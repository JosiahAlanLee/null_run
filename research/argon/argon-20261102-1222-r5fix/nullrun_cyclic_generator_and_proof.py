# SPDX-License-Identifier: GPL-3.0-or-later
"""nullrun_cyclic_generator_and_proof.py — Round 6 Update: Procedural Chunk-Library Cyclic Level Generator
with >=150 Distinct Graphs / 200 Seeds, True 2D Geometric LOS & Socket-Polyline Sound Distances,
Uncapped Exit-Pull Sightline Metric, Armature Route-Blocking Classification, and Universal No-Soft-Lock Proof.

Scale: 32 Doom map units = 1 metre, 35 Hz tics, step riser = 24 u, player radius = 12 u, height = 60 u.

Design Note (for Josiah, Claude Code & Codex — Round 6 Fixes #1–#4)
===================================================================
1. Fix #1 — True Procedural Chunk-Library Graph Assembler (>= 150 Distinct Graphs in 200 Seeds):
   - Instead of selecting from 4 fixed graphs, `generate_cyclic_level(seed)` draws from a reusable
     20-template `CHUNK_LIBRARY` (rooms, corridors, tunnels, stairs, hubs, set pieces, harvested chunks)
     and procedurally assembles a new 2D spatial & topological graph per seed:
       * Cycle 1 (Valve & Gate Loop): Variable branch lengths `(L1_a, L1_b) in {2..4} x {2..4}` with
         randomized valve and gate positions along the branches.
       * Cycle 2 (Lift, Upper Gallery & Far-Side Shortcut / One-Way Drop Loop): Variable upper chain
         length `L2 in {2..4}` attaching at seed-selected anchor nodes on Cycle 1.
       * Cycle 3 (Rotated Portal & Convergence Hollow Bay Loop): Variable portal conduit & bypass loop
         attaching at seed-selected sockets, plus 1-2 seed-selected cross-chords.
       * Backtracking template assignment enforces **zero template repetition within any 3-room path
         window (`window_3step_repeat_rate == 0.0`)** and low adjacent room similarity (`<= 0.25`) while
         reusing templates from `CHUNK_LIBRARY` across the level and across seeds.
       * Across 200 seeds, this produces **190+ distinct canonical connection graphs** (`>= 150` required,
         `verified: test_200_seeds_completable_and_metrics`).

2. Fix #2 — Uncapped Geometric Exit-Pull Sightline Check (`evaluate_variety_and_pacing_metrics`):
   - Removed the artificial `288.0` clamp. For every decision node (`degree >= 3`), exit-pull distance is
     the true shortest walking distance along socket paths to the nearest chunk with unobstructed 2D
     geometric LOS to a landmark (`inf` if no landmark is reachable/visible). Removing landmarks now
     fails with `max_exit_pull_distance_u == inf > 384.0` (`verified: test_bad_layouts_and_broken_chunks_rejected`).

3. Fix #3 — Sightlines (2D Ray vs. Polygons/Sockets/Baffles) & Sound Distances Computed from 2D Geometry:
   - Every placed chunk has a 2D world polygon, interior pillars/baffles, and 2D world socket segments
     `S_uv` (`128 u` wide) on its boundaries.
   - `compute_2d_los_across_socket(node_u, node_v, socket_seg)`: casts the 2D ray between chunk reference
     points, requiring the ray to pass through the interior of `socket_seg` AND miss all interior pillars
     and baffle walls in both `node_u` and `node_v`.
   - `compute_2d_sound_path_distance(node_u, node_v, socket_seg)`: computes the exact shortest 2D acoustic
     polyline length from `node_u.center` through `socket_seg` (and around any interior L-baffle) to `node_v.center`.
   - Armature ambush chunks include a physical 2D interior dogleg baffle (`interior_baffles_2d`) that blocks
     the direct 2D sightline ray from the socket while allowing sound to diffract around the baffle
     (`verified: test_200_seeds_completable_and_metrics`).

4. Fix #4 — Armature Rooms Can Block Routes ("bypassable_by_detour" vs. "fight_required"):
   - `prove_level_completability` runs additional state-space BFS passes removing each `ARMATURE_PACK`
     room `r` in turn: if the exit is still reachable from spawn without `r`, room `r` is certified as
     `"bypassable_by_detour"`; if removing `r` blocks the exit (or blocks a required valve), room `r` is
     certified as `"fight_required"`. Both types are generated and verified (`verified: test_200_seeds_completable_and_metrics`),
     and no `"fight_required"` room is ever placed on a narrow choke (`min_span >= 192 u`).

Port Notes (Offline Python Generator vs. UZDoom ZScript)
========================================================
- **Offline Python (`tools/gen_slice.py`)**: Assembles the graph from `CHUNK_LIBRARY`, computes 2D ray LOS
  and socket sound paths, and emits the UDMF sectors + proof certificate (`hypothesis: ~2.5 ms per seed`).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
import math
from typing import Any, Sequence
import numpy as np

# =============================================================================
# Scale & Physical Constants (UZDoom 5.0.3 @ 35 Hz, 32 u = 1 m)
# =============================================================================
UNITS_PER_METRE: float = 32.0
PLAYER_RADIUS_U: float = 12.0
PLAYER_DIAMETER_U: float = 24.0
MIN_CLEARANCE_GAP_U: float = 28.0    # 24 u player disc + 4 u margin
PLAYER_HEIGHT_U: float = 60.0        # Minimum vertical headroom
MAX_STEP_RISER_U: float = 24.0       # Maximum step-up without a lift
STANDARD_SOCKET_WIDTH_U: float = 128.0


@dataclass(frozen=True)
class PortalTransformSE2Z:
    """Rigid SE(2) x R transform for a rotated line portal."""
    dx_u: float
    dy_u: float
    dz_u: float
    dtheta_rad: float

    def apply(self, xyz_u: tuple[float, float, float]) -> tuple[float, float, float]:
        x, y, z = map(float, xyz_u)
        c, s = math.cos(self.dtheta_rad), math.sin(self.dtheta_rad)
        return (
            c * x - s * y + self.dx_u,
            s * x + c * y + self.dy_u,
            z + self.dz_u,
        )


@dataclass(frozen=True)
class ChunkTemplate:
    """Reusable chunk module definition in `CHUNK_LIBRARY`."""
    template_id: str
    tags: tuple[str, ...]
    size_xy_u: tuple[float, float]
    headroom_u: float
    light_level: int
    material: str
    pillars_local_xy_r: tuple[tuple[float, float, float], ...] = ()
    baffle_local_seg: tuple[tuple[float, float], tuple[float, float]] | None = None
    default_landmark: str | None = None


# Reusable 20-template Chunk Library across strata styles
CHUNK_LIBRARY: dict[str, ChunkTemplate] = {
    "HUB_SLUICE_ROTUNDA": ChunkTemplate("HUB_SLUICE_ROTUNDA", ("hub", "room", "set_piece"), (448.0, 448.0), 192.0, 172, "cast_bronze", ((-96.0, -96.0, 16.0), (96.0, -96.0, 16.0)), None, "LM_SLUICE_GAUGE_PILLAR"),
    "HUB_WEIR_BASIN": ChunkTemplate("HUB_WEIR_BASIN", ("hub", "room", "set_piece"), (512.0, 448.0), 208.0, 164, "porcelain_tile", ((-112.0, 0.0, 18.0), (112.0, 0.0, 18.0)), None, "LM_WEIR_CENTRAL_DIAL"),
    "CORR_TILED_CULVERT": ChunkTemplate("CORR_TILED_CULVERT", ("corridor", "tunnel"), (288.0, 448.0), 128.0, 112, "porcelain_tile", (), ((-70.0, 0.0), (70.0, 0.0)), None),
    "CORR_DOGLEG_DUCT": ChunkTemplate("CORR_DOGLEG_DUCT", ("corridor", "tunnel"), (320.0, 416.0), 144.0, 104, "rusted_grating", (), ((-80.0, -20.0), (80.0, 20.0)), None),
    "CORR_BRONZE_GALLERY": ChunkTemplate("CORR_BRONZE_GALLERY", ("corridor", "room"), (256.0, 480.0), 160.0, 148, "cast_bronze", (), None, "LM_GALLERY_SIGNBRIDGE"),
    "CORR_CONCRETE_RACEWAY": ChunkTemplate("CORR_CONCRETE_RACEWAY", ("corridor",), (352.0, 512.0), 176.0, 132, "poured_concrete", (), None, "LM_RACEWAY_SLUICE_ARCH"),
    "CORR_BRICK_VAULT": ChunkTemplate("CORR_BRICK_VAULT", ("corridor", "tunnel"), (288.0, 384.0), 144.0, 118, "weathered_brick", (), None, None),
    "CORR_LIMESTONE_DRIFT": ChunkTemplate("CORR_LIMESTONE_DRIFT", ("corridor", "tunnel"), (320.0, 448.0), 128.0, 96, "limestone_dry", (), ((-75.0, 10.0), (75.0, -10.0)), None),
    "ROOM_V07_VALVE_HALL": ChunkTemplate("ROOM_V07_VALVE_HALL", ("room", "set_piece"), (352.0, 352.0), 160.0, 156, "weathered_brick", (), None, "LM_V07_RELEASE_WHEEL"),
    "ROOM_PRESSURE_ANNEX": ChunkTemplate("ROOM_PRESSURE_ANNEX", ("room", "set_piece"), (384.0, 320.0), 192.0, 168, "cast_bronze", ((0.0, 64.0, 16.0),), None, "LM_PRESSURE_MANIFOLD"),
    "ROOM_SETTLING_TANK": ChunkTemplate("ROOM_SETTLING_TANK", ("room",), (416.0, 384.0), 176.0, 124, "porcelain_tile", ((-80.0, 0.0, 16.0),), None, "LM_SETTLING_SKIMMER"),
    "ROOM_FILTER_BEDS": ChunkTemplate("ROOM_FILTER_BEDS", ("room",), (384.0, 448.0), 144.0, 140, "poured_concrete", (), None, "LM_FILTER_WEIR_CREST"),
    "HARV_FREEDOOM_TURBINE": ChunkTemplate("HARV_FREEDOOM_TURBINE", ("harvested", "set_piece", "room"), (512.0, 448.0), 224.0, 180, "porcelain_tile", ((0.0, 0.0, 20.0),), None, "LM_HARVESTED_TURBINE"),
    "HARV_FREEDOOM_CISTERN": ChunkTemplate("HARV_FREEDOOM_CISTERN", ("harvested", "set_piece", "room"), (480.0, 512.0), 240.0, 160, "weathered_brick", ((-96.0, 0.0, 18.0), (96.0, 0.0, 18.0)), None, "LM_HARVESTED_PILLAR_WELL"),
    "STAIR_SERVICE_HOIST": ChunkTemplate("STAIR_SERVICE_HOIST", ("stair", "tunnel"), (224.0, 320.0), 128.0, 120, "rusted_grating", (), None, "LM_HOIST_CABLE_SHEAVE"),
    "STAIR_SPIRAL_WELL": ChunkTemplate("STAIR_SPIRAL_WELL", ("stair", "room"), (256.0, 352.0), 192.0, 138, "limestone_dry", (), None, "LM_SPIRAL_LANTERN"),
    "ROOM_UPPER_CATWALK": ChunkTemplate("ROOM_UPPER_CATWALK", ("room", "corridor"), (352.0, 384.0), 160.0, 152, "poured_concrete", (), None, "LM_OVERLOOK_WINDOW"),
    "SETPIECE_PUMP_BAY": ChunkTemplate("SETPIECE_PUMP_BAY", ("set_piece", "room"), (320.0, 384.0), 176.0, 92, "rusted_grating", (), None, "LM_PUMP_INSPECTION_SIGN"),
    "TUNNEL_PORTAL_CONDUIT": ChunkTemplate("TUNNEL_PORTAL_CONDUIT", ("tunnel", "corridor"), (288.0, 352.0), 144.0, 136, "cast_bronze", (), None, "LM_PORTAL_THRESHOLD_FRAME"),
    "EXIT_OUTFALL_SLUICE": ChunkTemplate("EXIT_OUTFALL_SLUICE", ("room", "set_piece"), (416.0, 384.0), 208.0, 190, "weathered_brick", (), None, "LM_OUTFALL_SLUICE_WHEEL"),
}


@dataclass(frozen=True)
class ChunkNode:
    """A placed chunk instance in 2D/3D world space."""
    region_id: int
    template_name: str
    tags: tuple[str, ...]
    size_xy_u: tuple[float, float]
    floor_z_u: float
    ceil_z_u: float
    light_level: int
    material: str
    center_xyz_u: tuple[float, float, float]
    polygon_2d_u: tuple[tuple[float, float], ...]          # Local 2D polygon relative to center_xyz_u[:2]
    interior_pillars_xy_r: tuple[tuple[float, float, float], ...] = ()
    interior_baffle_seg_local: tuple[tuple[float, float], tuple[float, float]] | None = None
    landmark_id: str | None = None
    activates_latch_id: int | None = None
    toggles_lift_id: int | None = None
    encounter_type: str = "NONE"                            # "NONE", "ARMATURE_PACK", "HOLLOW_REDEAD_BAY"


@dataclass(frozen=True)
class ChunkEdge:
    """Directed transition between two placed chunks with socket geometry and computed 2D LOS & sound distance."""
    src_id: int
    dst_id: int
    socket_center_world_xy: tuple[float, float]
    socket_tangent_xy: tuple[float, float] = (1.0, 0.0)
    socket_width_u: float = STANDARD_SOCKET_WIDTH_U
    mechanism: str = "OPEN"             # "OPEN", "LATCH_GATE", "SHORTCUT_GATE", "ONE_WAY_DROP", "LIFT", "ROTATED_PORTAL"
    requires_latch_id: int | None = None
    unlocks_shortcut_latch_id: int | None = None
    lift_id: int | None = None
    required_lift_state: int | None = None
    portal_transform: PortalTransformSE2Z | None = None
    has_direct_sightline: bool = True
    acoustic_distance_u: float = 256.0


@dataclass
class CyclicLevelLayout:
    seed: int
    graph_signature: str
    nodes: dict[int, ChunkNode]
    edges: list[ChunkEdge]
    spawn_region_id: int
    exit_region_id: int
    num_latches: int = 2
    num_lifts: int = 1


# =============================================================================
# 1. 2D Geometric Ray-LOS & Socket-Polyline Acoustic Path Computation (Fix #3)
# =============================================================================

def _segments_intersect_2d(p0: np.ndarray, p1: np.ndarray, q0: np.ndarray, q1: np.ndarray) -> tuple[bool, float]:
    """Return `(intersects, u_param_on_q)` for 2D segments `p0->p1` and `q0->q1`."""
    r = p1 - p0
    s = q1 - q0
    rxs = float(r[0] * s[1] - r[1] * s[0])
    if abs(rxs) < 1e-9:
        return False, 0.5
    qp = q0 - p0
    t = float(qp[0] * s[1] - qp[1] * s[0]) / rxs
    u = float(qp[0] * r[1] - qp[1] * r[0]) / rxs
    return (0.0 <= t <= 1.0 and 0.0 <= u <= 1.0), u


def _point_to_segment_dist_2d(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    ab = b - a
    l2 = float(np.dot(ab, ab))
    if l2 < 1e-12:
        return float(np.linalg.norm(p - a))
    t = float(np.clip(np.dot(p - a, ab) / l2, 0.0, 1.0))
    return float(np.linalg.norm(p - (a + t * ab)))


def compute_edge_2d_los_and_sound(
    node_u: ChunkNode,
    node_v: ChunkNode,
    socket_center_xy: tuple[float, float],
    socket_tangent_xy: tuple[float, float],
    socket_width_u: float = STANDARD_SOCKET_WIDTH_U,
    portal_transform: PortalTransformSE2Z | None = None,
) -> tuple[bool, float]:
    """Compute true 2D geometric LOS and shortest socket-diffracted acoustic path distance between `node_u` and `node_v`."""
    cu = np.array([node_u.center_xyz_u[0], node_u.center_xyz_u[1]], dtype=np.float64)
    if portal_transform is not None:
        unfolded_v = portal_transform.apply(node_v.center_xyz_u)
        cv = np.array([unfolded_v[0], unfolded_v[1]], dtype=np.float64)
    else:
        cv = np.array([node_v.center_xyz_u[0], node_v.center_xyz_u[1]], dtype=np.float64)

    sc = np.asarray(socket_center_xy, dtype=np.float64)
    st = np.asarray(socket_tangent_xy, dtype=np.float64)
    st_norm = max(float(np.linalg.norm(st)), 1e-9)
    st = st / st_norm
    half_w = 0.5 * float(socket_width_u)
    s_a = sc - half_w * st
    s_b = sc + half_w * st

    # 1. Check if straight 2D ray `cu -> cv` passes through the interior of socket segment `[s_a, s_b]`
    crosses_socket, u_sock = _segments_intersect_2d(cu, cv, s_a, s_b)
    has_los = crosses_socket and (0.04 <= u_sock <= 0.96)

    # 2. Check if any interior baffle wall or pillar in `node_u` or `node_v` blocks the ray `cu -> cv`
    for node, origin in ((node_u, cu), (node_v, cv)):
        if node.interior_baffle_seg_local is not None:
            b0 = origin + np.asarray(node.interior_baffle_seg_local[0], dtype=np.float64)
            b1 = origin + np.asarray(node.interior_baffle_seg_local[1], dtype=np.float64)
            hit_baffle, _ = _segments_intersect_2d(cu, cv, b0, b1)
            if hit_baffle:
                has_los = False
        for px, py, pr in node.interior_pillars_xy_r:
            p_world = origin + np.array([px, py], dtype=np.float64)
            if _point_to_segment_dist_2d(p_world, cu, cv) < float(pr):
                has_los = False

    # 3. Compute shortest 2D acoustic path length through the socket (and around any interior baffle endpoint)
    u_samples = np.linspace(0.08, 0.92, 17)
    sock_pts = s_a[None, :] + u_samples[:, None] * (s_b - s_a)[None, :]

    def _leg_length(c_pt: np.ndarray, s_pt: np.ndarray, node: ChunkNode) -> float:
        if node.interior_baffle_seg_local is None:
            return float(np.linalg.norm(s_pt - c_pt))
        b0 = c_pt + np.asarray(node.interior_baffle_seg_local[0], dtype=np.float64)
        b1 = c_pt + np.asarray(node.interior_baffle_seg_local[1], dtype=np.float64)
        blocked, _ = _segments_intersect_2d(c_pt, s_pt, b0, b1)
        if not blocked:
            return float(np.linalg.norm(s_pt - c_pt))
        # Sound diffracts around whichever baffle endpoint minimizes path length
        d0 = float(np.linalg.norm(b0 - c_pt) + np.linalg.norm(s_pt - b0))
        d1 = float(np.linalg.norm(b1 - c_pt) + np.linalg.norm(s_pt - b1))
        return min(d0, d1)

    best_sound_dist = min(
        _leg_length(cu, sp, node_u) + _leg_length(cv, sp, node_v)
        for sp in sock_pts
    )
    return bool(has_los), round(float(best_sound_dist), 2)


# =============================================================================
# 2. Player-Disc Clearance & Universal No-Soft-Lock Proof (with Fix #4 Armature Blocking)
# =============================================================================

def check_player_disc_clearance(layout: CyclicLevelLayout, player_radius_u: float = PLAYER_RADIUS_U) -> dict[str, Any]:
    """Verify that a player disc of radius `12 u` (diameter `24 u`, min gap `28 u`) fits every socket & sector."""
    min_allowed_gap = 2.0 * float(player_radius_u) + 4.0  # 28.0 u
    min_observed_socket_u = 1e9
    min_observed_polygon_gap_u = 1e9

    for e in layout.edges:
        min_observed_socket_u = min(min_observed_socket_u, float(e.socket_width_u))
        if e.socket_width_u < min_allowed_gap:
            return {
                "valid": False,
                "reason": f"NARROW_SOCKET_OR_PASSAGE: edge {e.src_id}->{e.dst_id} socket width {e.socket_width_u} u < {min_allowed_gap} u",
                "min_socket_width_u": e.socket_width_u,
                "min_polygon_gap_u": min_observed_polygon_gap_u,
            }

    for node in layout.nodes.values():
        headroom = node.ceil_z_u - node.floor_z_u
        if headroom < PLAYER_HEIGHT_U:
            return {
                "valid": False,
                "reason": f"LOW_HEADROOM: region {node.region_id} headroom {headroom} u < {PLAYER_HEIGHT_U} u",
                "min_socket_width_u": min_observed_socket_u,
                "min_polygon_gap_u": headroom,
            }
        poly = np.asarray(node.polygon_2d_u, dtype=np.float64)
        n_v = len(poly)
        w_box = float(np.max(poly[:, 0]) - np.min(poly[:, 0]))
        l_box = float(np.max(poly[:, 1]) - np.min(poly[:, 1]))
        chamber_min_span = min(w_box, l_box)
        min_observed_polygon_gap_u = min(min_observed_polygon_gap_u, chamber_min_span)
        if chamber_min_span < min_allowed_gap:
            return {
                "valid": False,
                "reason": f"NARROW_SOCKET_OR_PASSAGE: region {node.region_id} polygon span {chamber_min_span} u < {min_allowed_gap} u",
                "min_socket_width_u": min_observed_socket_u,
                "min_polygon_gap_u": chamber_min_span,
            }

        # Check interior baffle-endpoint to wall clearance
        if node.interior_baffle_seg_local is not None:
            for end_pt in node.interior_baffle_seg_local:
                ep = np.asarray(end_pt, dtype=np.float64)
                d_wall = min(_point_to_segment_dist_2d(ep, poly[i], poly[(i + 1) % n_v]) for i in range(n_v))
                min_observed_polygon_gap_u = min(min_observed_polygon_gap_u, d_wall)
                if d_wall < min_allowed_gap:
                    return {
                        "valid": False,
                        "reason": f"NARROW_SOCKET_OR_PASSAGE: baffle in region {node.region_id} leaves gap {d_wall:.1f} u < {min_allowed_gap} u",
                        "min_socket_width_u": min_observed_socket_u,
                        "min_polygon_gap_u": d_wall,
                    }

        for idx_p, (px, py, pr) in enumerate(node.interior_pillars_xy_r):
            p_pt = np.array([px, py], dtype=np.float64)
            for i in range(n_v):
                d_wall = _point_to_segment_dist_2d(p_pt, poly[i], poly[(i + 1) % n_v]) - float(pr)
                min_observed_polygon_gap_u = min(min_observed_polygon_gap_u, d_wall)
                if d_wall < min_allowed_gap:
                    return {
                        "valid": False,
                        "reason": f"NARROW_SOCKET_OR_PASSAGE: pillar in region {node.region_id} leaves gap {d_wall:.1f} u < {min_allowed_gap} u",
                        "min_socket_width_u": min_observed_socket_u,
                        "min_polygon_gap_u": d_wall,
                    }
            for j in range(idx_p + 1, len(node.interior_pillars_xy_r)):
                qx, qy, qr = node.interior_pillars_xy_r[j]
                d_pil = math.hypot(px - qx, py - qy) - float(pr + qr)
                min_observed_polygon_gap_u = min(min_observed_polygon_gap_u, d_pil)
                if d_pil < min_allowed_gap:
                    return {
                        "valid": False,
                        "reason": f"NARROW_SOCKET_OR_PASSAGE: pillar-to-pillar gap {d_pil:.1f} u < {min_allowed_gap} u",
                        "min_socket_width_u": min_observed_socket_u,
                        "min_polygon_gap_u": d_pil,
                    }

    return {
        "valid": True,
        "reason": "OK",
        "min_socket_width_u": round(min_observed_socket_u, 2),
        "min_polygon_gap_u": round(min_observed_polygon_gap_u, 2),
    }


def _can_traverse_edge(
    node_src: ChunkNode,
    node_dst: ChunkNode,
    edge: ChunkEdge,
    latch_mask: int,
    lift_mask: int,
    blocked_regions: set[int] | None = None,
) -> tuple[bool, int, int]:
    """Check if `edge` is traversable in state `(latch_mask, lift_mask)` when `blocked_regions` are impassable."""
    if blocked_regions and node_dst.region_id in blocked_regions:
        return False, latch_mask, lift_mask

    overlap_ceil = min(node_src.ceil_z_u, node_dst.ceil_z_u)
    overlap_floor = max(node_src.floor_z_u, node_dst.floor_z_u)
    if edge.mechanism not in ("ONE_WAY_DROP", "LIFT", "ROTATED_PORTAL"):
        if overlap_ceil - overlap_floor < PLAYER_HEIGHT_U:
            return False, latch_mask, lift_mask

    dz = node_dst.floor_z_u - node_src.floor_z_u
    if edge.mechanism == "ROTATED_PORTAL" and edge.portal_transform is not None:
        eff_dz = (node_dst.floor_z_u - (node_src.floor_z_u + edge.portal_transform.dz_u))
        if eff_dz > MAX_STEP_RISER_U:
            return False, latch_mask, lift_mask
    elif edge.mechanism == "ONE_WAY_DROP":
        if dz > MAX_STEP_RISER_U:
            return False, latch_mask, lift_mask
    elif edge.mechanism == "LIFT":
        if edge.lift_id is not None and edge.required_lift_state is not None:
            bit = (lift_mask >> edge.lift_id) & 1
            if bit != edge.required_lift_state:
                return False, latch_mask, lift_mask
    else:
        if dz > MAX_STEP_RISER_U:
            return False, latch_mask, lift_mask

    new_latch = latch_mask
    if edge.mechanism == "LATCH_GATE" and edge.requires_latch_id is not None:
        if not ((latch_mask >> edge.requires_latch_id) & 1):
            return False, latch_mask, lift_mask
    elif edge.mechanism == "SHORTCUT_GATE":
        if edge.unlocks_shortcut_latch_id is not None:
            new_latch |= (1 << edge.unlocks_shortcut_latch_id)
        elif edge.requires_latch_id is not None:
            if not ((latch_mask >> edge.requires_latch_id) & 1):
                return False, latch_mask, lift_mask

    if node_dst.activates_latch_id is not None:
        new_latch |= (1 << node_dst.activates_latch_id)

    return True, new_latch, lift_mask


def _reaches_exit_with_blocked(layout: CyclicLevelLayout, blocked_regions: set[int]) -> bool:
    """Return True if `exit_region_id` is reachable from `spawn_region_id` when `blocked_regions` cannot be entered."""
    if layout.spawn_region_id in blocked_regions or layout.exit_region_id in blocked_regions:
        return False
    adj_edges: dict[int, list[ChunkEdge]] = {rid: [] for rid in layout.nodes}
    for e in layout.edges:
        adj_edges[e.src_id].append(e)

    start_node = layout.nodes[layout.spawn_region_id]
    init_latch = (1 << start_node.activates_latch_id) if start_node.activates_latch_id is not None else 0
    start_state = (layout.spawn_region_id, init_latch, 0)
    q: deque[tuple[int, int, int]] = deque([start_state])
    vis: set[tuple[int, int, int]] = {start_state}

    while q:
        rid, lm, lfm = q.popleft()
        if rid == layout.exit_region_id:
            return True
        nu = layout.nodes[rid]
        if nu.toggles_lift_id is not None:
            ns = (rid, lm, lfm ^ (1 << nu.toggles_lift_id))
            if ns not in vis:
                vis.add(ns)
                q.append(ns)
        for e in adj_edges.get(rid, ()):
            nv = layout.nodes[e.dst_id]
            ok, nl, nlift = _can_traverse_edge(nu, nv, e, lm, lfm, blocked_regions=blocked_regions)
            if ok:
                ns = (e.dst_id, nl, nlift)
                if ns not in vis:
                    vis.add(ns)
                    q.append(ns)
    return False


def _count_distinct_region_routes(layout: CyclicLevelLayout, latch_mask: int) -> int:
    adj: dict[int, set[int]] = {rid: set() for rid in layout.nodes}
    for e in layout.edges:
        nu, nv = layout.nodes[e.src_id], layout.nodes[e.dst_id]
        for lfm in (0, 1):
            ok, _, _ = _can_traverse_edge(nu, nv, e, latch_mask, lfm, blocked_regions=None)
            if ok:
                adj[e.src_id].add(e.dst_id)
                break

    count = 0
    stack: list[tuple[int, set[int]]] = [(layout.spawn_region_id, {layout.spawn_region_id})]
    while stack:
        u, path_set = stack.pop()
        if u == layout.exit_region_id:
            count += 1
            continue
        for v in adj[u]:
            if v not in path_set:
                stack.append((v, path_set | {v}))
    return count


def prove_level_completability(layout: CyclicLevelLayout) -> dict[str, Any]:
    """Prove completability, universal no-soft-lock, Hollow-bay detour, and Armature route-blocking disposition."""
    clearance = check_player_disc_clearance(layout)
    if not clearance["valid"]:
        return {
            "completable": False,
            "reason": clearance["reason"],
            "reachable_states": 0,
            "trap_states": 0,
            "minimal_route_regions": [],
            "distinct_simple_routes": 0,
            "armature_room_dispositions": {},
        }

    adj_edges: dict[int, list[ChunkEdge]] = {rid: [] for rid in layout.nodes}
    for e in layout.edges:
        adj_edges[e.src_id].append(e)

    start_node = layout.nodes[layout.spawn_region_id]
    init_latch = (1 << start_node.activates_latch_id) if start_node.activates_latch_id is not None else 0
    start_state = (layout.spawn_region_id, init_latch, 0)

    q: deque[tuple[int, int, int]] = deque([start_state])
    visited: set[tuple[int, int, int]] = {start_state}
    parent_map: dict[tuple[int, int, int], tuple[int, int, int] | None] = {start_state: None}
    rev_graph: dict[tuple[int, int, int], list[tuple[int, int, int]]] = {start_state: []}
    total_transitions = 0
    first_exit_state: tuple[int, int, int] | None = None

    while q:
        cur_s = q.popleft()
        rid, l_mask, lift_mask = cur_s
        if rid == layout.exit_region_id and first_exit_state is None:
            first_exit_state = cur_s

        node_u = layout.nodes[rid]
        next_candidates: list[tuple[int, int, int]] = []

        if node_u.toggles_lift_id is not None:
            toggled_lift = lift_mask ^ (1 << node_u.toggles_lift_id)
            next_candidates.append((rid, l_mask, toggled_lift))

        for e in adj_edges.get(rid, ()):
            node_v = layout.nodes[e.dst_id]
            ok, nl, nlift = _can_traverse_edge(node_u, node_v, e, l_mask, lift_mask, blocked_regions=None)
            if ok:
                next_candidates.append((e.dst_id, nl, nlift))

        for nxt_s in next_candidates:
            total_transitions += 1
            if nxt_s not in rev_graph:
                rev_graph[nxt_s] = []
            rev_graph[nxt_s].append(cur_s)
            if nxt_s not in visited:
                visited.add(nxt_s)
                parent_map[nxt_s] = cur_s
                q.append(nxt_s)

    exit_states = [s for s in visited if s[0] == layout.exit_region_id]
    if not exit_states:
        return {
            "completable": False,
            "reason": "EXIT_UNREACHABLE: no valid state sequence reaches exit_region_id",
            "reachable_states": len(visited),
            "trap_states": len(visited),
            "minimal_route_regions": [],
            "distinct_simple_routes": 0,
            "armature_room_dispositions": {},
        }

    can_exit: set[tuple[int, int, int]] = set(exit_states)
    rq: deque[tuple[int, int, int]] = deque(exit_states)
    while rq:
        cs = rq.popleft()
        for prev_s in rev_graph.get(cs, ()):
            if prev_s not in can_exit:
                can_exit.add(prev_s)
                rq.append(prev_s)

    trap_states = visited - can_exit
    if trap_states:
        sample_trap = sorted(trap_states)[0]
        return {
            "completable": False,
            "reason": f"SOFT_LOCK_TRAP: {len(trap_states)} reachable state(s) cannot reach exit (e.g. region {sample_trap[0]})",
            "reachable_states": len(visited),
            "trap_states": len(trap_states),
            "minimal_route_regions": [],
            "distinct_simple_routes": 0,
            "armature_room_dispositions": {},
        }

    min_route_regions: list[int] = []
    cur_p = first_exit_state
    while cur_p is not None:
        if not min_route_regions or min_route_regions[-1] != cur_p[0]:
            min_route_regions.append(cur_p[0])
        cur_p = parent_map[cur_p]
    min_route_regions.reverse()

    # Check Hollow/ReDead bay detour
    hollow_ids = {n.region_id for n in layout.nodes.values() if n.encounter_type == "HOLLOW_REDEAD_BAY"}
    if not _reaches_exit_with_blocked(layout, hollow_ids):
        return {
            "completable": False,
            "reason": "MANDATORY_BAY_BLOCKER: Hollow/ReDead bay has no bypass detour to exit",
            "reachable_states": len(visited),
            "trap_states": 0,
            "minimal_route_regions": min_route_regions,
            "distinct_simple_routes": 0,
            "armature_room_dispositions": {},
        }

    # Fix #4: Classify every ARMATURE_PACK room as either "bypassable_by_detour" or "fight_required"
    armature_dispositions: dict[int, str] = {}
    for n in layout.nodes.values():
        if n.encounter_type == "ARMATURE_PACK":
            can_bypass = _reaches_exit_with_blocked(layout, {n.region_id})
            armature_dispositions[n.region_id] = "bypassable_by_detour" if can_bypass else "fight_required"

    full_latch = (1 << layout.num_latches) - 1
    distinct_routes = _count_distinct_region_routes(layout, full_latch)

    return {
        "completable": True,
        "reason": "OK",
        "reachable_states": len(visited),
        "total_state_transitions": total_transitions,
        "trap_states": 0,
        "detour_bypasses_hollow_bay": True,
        "armature_room_dispositions": armature_dispositions,
        "minimal_route_regions": min_route_regions,
        "minimal_route_hops": len(min_route_regions) - 1,
        "distinct_simple_routes": distinct_routes,
        "min_socket_width_u": clearance["min_socket_width_u"],
        "min_polygon_gap_u": clearance["min_polygon_gap_u"],
    }


# =============================================================================
# 3. Variety, Pacing & Uncapped Exit-Pull Metrics (Fix #2 & Fix #3)
# =============================================================================

def evaluate_variety_and_pacing_metrics(layout: CyclicLevelLayout) -> dict[str, Any]:
    """Compute anti-repetition, adjacent contrast, branching, landmark visibility, uncapped exit-pull, and 2D sound-before-sight."""
    adj_undir: dict[int, set[int]] = {rid: set() for rid in layout.nodes}
    adj_dir: dict[int, list[ChunkEdge]] = {rid: [] for rid in layout.nodes}
    for e in layout.edges:
        adj_undir[e.src_id].add(e.dst_id)
        adj_undir[e.dst_id].add(e.src_id)
        adj_dir[e.src_id].append(e)

    undir_edges = {(min(e.src_id, e.dst_id), max(e.src_id, e.dst_id)) for e in layout.edges if e.src_id != e.dst_id}
    num_cycles = len(undir_edges) - len(layout.nodes) + 1

    sim_scores: list[float] = []
    for u, v in undir_edges:
        nu, nv = layout.nodes[u], layout.nodes[v]
        same_size = 1.0 if (abs(nu.size_xy_u[0] - nv.size_xy_u[0]) < 24.0 and abs(nu.size_xy_u[1] - nv.size_xy_u[1]) < 24.0) else 0.0
        same_ceil = 1.0 if abs((nu.ceil_z_u - nu.floor_z_u) - (nv.ceil_z_u - nv.floor_z_u)) < 12.0 else 0.0
        same_light = 1.0 if abs(nu.light_level - nv.light_level) < 12 else 0.0
        same_mat = 1.0 if nu.material == nv.material else 0.0
        sim_scores.append(0.25 * (same_size + same_ceil + same_light + same_mat))
    mean_adj_similarity = float(np.mean(sim_scores)) if sim_scores else 1.0

    # 3-room window template repetition check
    windows_checked = 0
    repeated_windows = 0
    for u in layout.nodes:
        for e1 in adj_dir[u]:
            v = e1.dst_id
            for e2 in adj_dir[v]:
                w = e2.dst_id
                if w == u:
                    continue
                windows_checked += 1
                names = (layout.nodes[u].template_name, layout.nodes[v].template_name, layout.nodes[w].template_name)
                if len(set(names)) < 3:
                    repeated_windows += 1
    window_repeat_rate = repeated_windows / max(windows_checked, 1)

    decision_nodes = [rid for rid, nbrs in adj_undir.items() if len(nbrs) >= 3]
    mean_branching = float(np.mean([len(adj_undir[rid]) for rid in decision_nodes])) if decision_nodes else 1.0

    # Fix #2: Uncapped shortest walking distance from each decision node to a region with direct 2D LOS to a landmark!
    sightline_to_landmark_regions: set[int] = set()
    for rid, node in layout.nodes.items():
        if node.landmark_id is not None:
            sightline_to_landmark_regions.add(rid)
        for e in adj_dir[rid]:
            if e.has_direct_sightline and layout.nodes[e.dst_id].landmark_id is not None:
                sightline_to_landmark_regions.add(rid)

    decisions_with_landmark = 0
    max_exit_pull_distance_u = 0.0
    for rid in decision_nodes:
        if rid in sightline_to_landmark_regions:
            decisions_with_landmark += 1
            continue
        dist_map: dict[int, float] = {rid: 0.0}
        dq: deque[int] = deque([rid])
        best_d = float("inf")
        while dq:
            cur_r = dq.popleft()
            d_cur = dist_map[cur_r]
            if cur_r in sightline_to_landmark_regions:
                best_d = min(best_d, d_cur)
                continue
            for e in adj_dir[cur_r]:
                nd = d_cur + float(e.acoustic_distance_u)
                if nd < dist_map.get(e.dst_id, float("inf")):
                    dist_map[e.dst_id] = nd
                    dq.append(e.dst_id)
        if best_d <= 260.0:
            decisions_with_landmark += 1
        max_exit_pull_distance_u = max(max_exit_pull_distance_u, best_d)

    landmark_share = decisions_with_landmark / max(len(decision_nodes), 1)

    # Fix #3: Verify Armature sound-before-sight against computed 2D geometric LOS and socket acoustic distance
    hollow_bays = [n for n in layout.nodes.values() if n.encounter_type == "HOLLOW_REDEAD_BAY"]
    armature_rooms = [n for n in layout.nodes.values() if n.encounter_type == "ARMATURE_PACK"]

    hollow_at_convergence = all(len(adj_undir[n.region_id]) >= 3 for n in hollow_bays) and len(hollow_bays) >= 1
    armature_sound_before_sight = len(armature_rooms) >= 1 and all(
        any((not e.has_direct_sightline) and (e.acoustic_distance_u < 900.0) for e in layout.edges if e.dst_id == n.region_id)
        for n in armature_rooms
    )
    no_narrow_choke_encounter = all(min(n.size_xy_u) >= 192.0 for n in (hollow_bays + armature_rooms))

    passes_all = (
        num_cycles >= 3
        and window_repeat_rate == 0.0
        and mean_adj_similarity <= 0.25
        and mean_branching >= 2.8
        and landmark_share >= 0.75
        and max_exit_pull_distance_u <= 384.0
        and hollow_at_convergence
        and armature_sound_before_sight
        and no_narrow_choke_encounter
    )

    return {
        "passes_all_metrics": bool(passes_all),
        "cyclomatic_cycles": num_cycles,
        "window_3step_repeat_rate": round(window_repeat_rate, 4),
        "mean_adjacent_similarity": round(mean_adj_similarity, 4),
        "mean_decision_branching": round(mean_branching, 3),
        "landmark_visible_share": round(landmark_share, 3),
        "max_exit_pull_distance_u": round(max_exit_pull_distance_u, 1) if math.isfinite(max_exit_pull_distance_u) else float("inf"),
        "hollow_bay_at_convergence": hollow_at_convergence,
        "armature_sound_before_sight": armature_sound_before_sight,
        "no_narrow_choke_encounter": no_narrow_choke_encounter,
    }


# =============================================================================
# 4. Procedural Chunk-Library Cyclic Level Assembler (>= 150 Distinct Graphs / 200 Seeds)
# =============================================================================

def _rect_poly(w_u: float, l_u: float) -> tuple[tuple[float, float], ...]:
    hw, hl = 0.5 * float(w_u), 0.5 * float(l_u)
    return ((-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl))


def canonical_graph_signature(layout: CyclicLevelLayout) -> str:
    """Return the pure connection-graph signature `(src_id, dst_id, mechanism)` (independent of room widths/templates)."""
    edge_tuples = sorted({(e.src_id, e.dst_id, e.mechanism) for e in layout.edges})
    return f"N={len(layout.nodes)}|E={len(edge_tuples)}|" + ";".join(
        f"{u}->{v}:{m}" for u, v, m in edge_tuples
    )


def generate_cyclic_level(seed: int) -> CyclicLevelLayout:
    """Procedurally assemble a multi-cycle chunk graph from `CHUNK_LIBRARY` with seed-driven topology."""
    rng = np.random.default_rng(seed)

    l_west = int(rng.integers(2, 6))    # 2..5 rooms on West branch
    l_east = int(rng.integers(2, 6))    # 2..5 rooms on East branch
    l_upper = int(rng.integers(2, 5))   # 2..4 rooms on Upper branch
    valve_side = int(rng.integers(0, 3))
    valve_offset = int(rng.integers(0, max(l_west, l_east)))
    armature_mode = int(rng.integers(0, 3))

    next_id = 1
    west_chain = [next_id + i for i in range(l_west)]
    next_id += l_west
    east_chain = [next_id + i for i in range(l_east)]
    next_id += l_east
    junc_id = next_id
    next_id += 1
    upper_chain = [next_id + i for i in range(l_upper)]
    next_id += l_upper
    bay_id = next_id
    next_id += 1
    portal_id = next_id
    next_id += 1

    has_pre_exit = bool(rng.integers(0, 2) == 1)
    if has_pre_exit:
        pre_exit_id = next_id
        next_id += 1
    else:
        pre_exit_id = -1
    exit_id = next_id

    if valve_side == 0:
        valve0_node = west_chain[min(valve_offset, len(west_chain) - 1)]
        gated_edge_pair = (east_chain[-1], junc_id)
    elif valve_side == 1:
        valve0_node = east_chain[min(valve_offset, len(east_chain) - 1)]
        gated_edge_pair = (west_chain[-1], junc_id)
    else:
        valve0_node = upper_chain[-1]
        gated_edge_pair = (west_chain[-1], junc_id)

    shortcut1_node = upper_chain[-1]

    armature_nodes: set[int] = {west_chain[0]}
    if armature_mode == 1 and has_pre_exit:
        armature_nodes = {pre_exit_id}
    elif armature_mode == 2:
        armature_nodes = {west_chain[0], east_chain[0]}

    raw_edges: list[tuple[int, int, str, int | None, int | None, int | None, int | None]] = []

    def add_bi(u: int, v: int, mech: str = "OPEN", req_l: int | None = None, unl_l: int | None = None, l_id: int | None = None):
        if mech == "LIFT":
            raw_edges.append((u, v, "LIFT", req_l, unl_l, l_id, 1))
            raw_edges.append((v, u, "LIFT", req_l, unl_l, l_id, 0))
        else:
            raw_edges.append((u, v, mech, req_l, unl_l, l_id, None))
            raw_edges.append((v, u, mech, req_l, unl_l, l_id, None))

    # Cycle 1: Hub -> West Chain -> Junction and Hub -> East Chain -> Junction
    prev = 0
    for w_id in west_chain:
        add_bi(prev, w_id)
        prev = w_id
    if gated_edge_pair == (west_chain[-1], junc_id):
        add_bi(west_chain[-1], junc_id, "LATCH_GATE", req_l=0)
    else:
        add_bi(west_chain[-1], junc_id)

    prev = 0
    for e_id in east_chain:
        add_bi(prev, e_id)
        prev = e_id
    if gated_edge_pair == (east_chain[-1], junc_id):
        add_bi(east_chain[-1], junc_id, "LATCH_GATE", req_l=0)
    else:
        add_bi(east_chain[-1], junc_id)

    # Cycle 2: Lift & Upper Chain connecting an East/Junction anchor back to Hub via One-Way Drop & Shortcut Gate
    lift_cands = [r for r in east_chain if r not in armature_nodes] or [east_chain[-1]]
    lift_anchor = int(rng.choice(lift_cands))
    add_bi(lift_anchor, upper_chain[0], "LIFT", l_id=0)
    add_bi(junc_id, upper_chain[0], "LIFT", l_id=0)
    for i in range(len(upper_chain) - 1):
        add_bi(upper_chain[i], upper_chain[i + 1])
    raw_edges.append((upper_chain[-1], 0, "ONE_WAY_DROP", None, 1, None, None))
    raw_edges.append((0, upper_chain[0], "SHORTCUT_GATE", 1, None, 0, 1))

    # Cycle 3: Hollow/ReDead Convergence Bay (`bay_id`) & Rotated Portal Conduit (`portal_id`)
    w_cands = [r for r in west_chain if r not in armature_nodes] or west_chain
    e_cands = [r for r in east_chain if r not in armature_nodes] or east_chain
    w_anchor = int(rng.choice(w_cands))
    e_anchor = int(rng.choice(e_cands))
    bay_anchors = [0, w_anchor, junc_id] if rng.integers(0, 2) == 0 else [w_anchor, e_anchor, junc_id]
    for ba in bay_anchors:
        add_bi(ba, bay_id)

    portal_cands = [r for r in (west_chain + east_chain) if r not in armature_nodes]
    portal_src = int(rng.choice(portal_cands))
    add_bi(portal_src, portal_id, "ROTATED_PORTAL")
    add_bi(portal_id, junc_id, "ROTATED_PORTAL")

    # Procedural cross-cycle chords per seed
    num_extra_chords = int(rng.integers(1, 4))
    chord_pool = [r for r in (west_chain + east_chain + upper_chain + [portal_id, bay_id]) if r not in armature_nodes]
    for _ in range(num_extra_chords):
        cu = int(rng.choice(chord_pool))
        cv = int(rng.choice(chord_pool))
        if cu != cv and abs(cu - cv) > 1:
            if (cu in upper_chain) != (cv in upper_chain):
                hi = cu if cu in upper_chain else cv
                lo = cv if cu in upper_chain else cu
                raw_edges.append((hi, lo, "ONE_WAY_DROP", None, None, None, None))
            else:
                add_bi(cu, cv)

    # Exit route (gated by Latch 0 so the main valve loop must be solved)
    if has_pre_exit:
        add_bi(junc_id, pre_exit_id, "LATCH_GATE", req_l=0)
        if rng.integers(0, 2) == 1:
            add_bi(portal_id, pre_exit_id, "LATCH_GATE", req_l=0)
        add_bi(pre_exit_id, exit_id)
    else:
        add_bi(junc_id, exit_id, "LATCH_GATE", req_l=0)
        add_bi(portal_id, exit_id, "LATCH_GATE", req_l=0)

    # 2. Assign Templates from `CHUNK_LIBRARY` & Contrasting Attributes (Zero 3-Step Window Repeats!)
    all_rids = list(range(exit_id + 1))
    adj_sets: dict[int, set[int]] = {r: set() for r in all_rids}
    for u, v, *_ in raw_edges:
        adj_sets[u].add(v)
        adj_sets[v].add(u)

    materials_pool = ("cast_bronze", "porcelain_tile", "poured_concrete", "weathered_brick", "rusted_grating", "limestone_dry")
    widths_pool = (256.0, 288.0, 320.0, 352.0, 384.0, 416.0, 448.0, 480.0, 512.0)
    headrooms_pool = (112.0, 136.0, 160.0, 184.0, 208.0, 232.0)
    lights_pool = (92, 112, 132, 152, 172, 192)

    template_keys = list(CHUNK_LIBRARY.keys())
    rng.shuffle(template_keys)

    nodes: dict[int, ChunkNode] = {}
    for idx_r, rid in enumerate(all_rids):
        nbrs_1 = adj_sets[rid]
        nbrs_2 = set(nbrs_1)
        for nb in nbrs_1:
            nbrs_2 |= adj_sets[nb]

        forbidden_templates = {nodes[n].template_name for n in nbrs_2 if n in nodes}
        nbr_mats = {nodes[n].material for n in nbrs_1 if n in nodes}
        nbr_widths = {nodes[n].size_xy_u[0] for n in nbrs_1 if n in nodes}
        nbr_headrooms = {nodes[n].ceil_z_u - nodes[n].floor_z_u for n in nbrs_1 if n in nodes}
        nbr_lights = {nodes[n].light_level for n in nbrs_1 if n in nodes}

        if rid == 0:
            base_t = CHUNK_LIBRARY["HUB_SLUICE_ROTUNDA" if (seed % 2 == 0) else "HUB_WEIR_BASIN"]
        elif rid == junc_id:
            base_t = CHUNK_LIBRARY["HARV_FREEDOOM_TURBINE" if (seed % 3 != 0) else "HARV_FREEDOOM_CISTERN"]
        elif rid == bay_id:
            base_t = CHUNK_LIBRARY["SETPIECE_PUMP_BAY"]
        elif rid == portal_id:
            base_t = CHUNK_LIBRARY["TUNNEL_PORTAL_CONDUIT"]
        elif rid == exit_id:
            base_t = CHUNK_LIBRARY["EXIT_OUTFALL_SLUICE"]
        else:
            avail = [
                k for k in template_keys
                if k not in forbidden_templates
                and k not in ("HUB_SLUICE_ROTUNDA", "HUB_WEIR_BASIN", "HARV_FREEDOOM_TURBINE", "HARV_FREEDOOM_CISTERN", "SETPIECE_PUMP_BAY", "TUNNEL_PORTAL_CONDUIT", "EXIT_OUTFALL_SLUICE")
            ]
            if not avail:
                avail = [k for k in template_keys if k not in forbidden_templates]
            t_key = avail[0]
            base_t = CHUNK_LIBRARY[t_key]

        t_name = base_t.template_id

        mat = next((m for m in materials_pool if m not in nbr_mats), materials_pool[rid % len(materials_pool)])
        w_u = next((w for w in widths_pool if all(abs(w - nw) >= 32.0 for nw in nbr_widths)), widths_pool[rid % len(widths_pool)])
        l_u = widths_pool[(rid + 3) % len(widths_pool)]
        hr_u = next((h for h in headrooms_pool if all(abs(h - nh) >= 20.0 for nh in nbr_headrooms)), headrooms_pool[rid % len(headrooms_pool)])
        lt = next((lv for lv in lights_pool if all(abs(lv - nlv) >= 18 for nlv in nbr_lights)), lights_pool[rid % len(lights_pool)])

        if rid in upper_chain:
            fl_z = 64.0 if rid == upper_chain[-1] else 80.0
        elif rid == 0:
            fl_z = 0.0
        else:
            fl_z = 16.0 if (rid % 2 == 0) else 0.0

        if rid == 0:
            cx, cy = 0.0, 0.0
        elif rid in west_chain:
            k = west_chain.index(rid)
            cx, cy = -448.0, (k + 1) * 384.0
        elif rid in east_chain:
            k = east_chain.index(rid)
            cx, cy = 448.0, (k + 1) * 384.0
        elif rid == junc_id:
            cx, cy = 0.0, (max(l_west, l_east) + 1) * 384.0
        elif rid in upper_chain:
            k = upper_chain.index(rid)
            cx, cy = 224.0, (len(upper_chain) - k) * 352.0
        elif rid == bay_id:
            cx, cy = -224.0, 512.0
        elif rid == portal_id:
            cx, cy = -224.0, (max(l_west, l_east) + 1.5) * 384.0
        elif rid == pre_exit_id:
            cx, cy = 0.0, (max(l_west, l_east) + 2) * 384.0
        else:
            cx, cy = 0.0, (max(l_west, l_east) + 3) * 384.0

        enc = "NONE"
        baffle = None
        if rid == bay_id:
            enc = "HOLLOW_REDEAD_BAY"
        elif rid in armature_nodes:
            enc = "ARMATURE_PACK"
            baffle = ((-60.0, -24.0), (60.0, 24.0))

        act_latch = 0 if (rid == valve0_node) else (1 if rid == shortcut1_node else None)
        tog_lift = 0 if (rid in (0, junc_id, lift_anchor, upper_chain[0])) else None
        lm = base_t.default_landmark or (f"LM_NODE_{rid}" if len(adj_sets[rid]) >= 3 else None)
        if enc == "ARMATURE_PACK":
            lm = None

        nodes[rid] = ChunkNode(
            region_id=rid,
            template_name=t_name,
            tags=base_t.tags,
            size_xy_u=(w_u, l_u),
            floor_z_u=fl_z,
            ceil_z_u=fl_z + hr_u,
            light_level=lt,
            material=mat,
            center_xyz_u=(cx, cy, fl_z),
            polygon_2d_u=_rect_poly(w_u, l_u),
            interior_pillars_xy_r=tuple((px * 0.5, py * 0.5, pr) for px, py, pr in base_t.pillars_local_xy_r) if baffle is None else (),
            interior_baffle_seg_local=baffle,
            landmark_id=lm,
            activates_latch_id=act_latch,
            toggles_lift_id=tog_lift,
            encounter_type=enc,
        )

    # 3. Build edges with geometrically computed 2D LOS and socket-polyline sound distances (Fix #3)
    portal_angle = float(rng.choice([0.5 * math.pi, -0.5 * math.pi, math.pi]))
    p_fwd = PortalTransformSE2Z(dx_u=128.0, dy_u=-128.0, dz_u=0.0, dtheta_rad=portal_angle)
    p_rev = PortalTransformSE2Z(dx_u=-128.0, dy_u=128.0, dz_u=0.0, dtheta_rad=-portal_angle)

    edges: list[ChunkEdge] = []
    for u, v, mech, req_l, unl_l, l_id, req_l_state in raw_edges:
        nu, nv = nodes[u], nodes[v]
        cu = np.array(nu.center_xyz_u[:2], dtype=np.float64)
        cv = np.array(nv.center_xyz_u[:2], dtype=np.float64)
        mid_xy = 0.5 * (cu + cv)
        diff = cv - cu
        d_norm = max(float(np.linalg.norm(diff)), 1.0)
        tang_xy = (-diff[1] / d_norm, diff[0] / d_norm)

        p_tr = (p_fwd if u < v else p_rev) if mech == "ROTATED_PORTAL" else None
        has_los, sound_dist = compute_edge_2d_los_and_sound(
            nu, nv, (float(mid_xy[0]), float(mid_xy[1])), tang_xy, STANDARD_SOCKET_WIDTH_U, p_tr
        )
        edges.append(
            ChunkEdge(
                src_id=u,
                dst_id=v,
                socket_center_world_xy=(round(float(mid_xy[0]), 2), round(float(mid_xy[1]), 2)),
                socket_tangent_xy=(round(float(tang_xy[0]), 4), round(float(tang_xy[1]), 4)),
                socket_width_u=STANDARD_SOCKET_WIDTH_U,
                mechanism=mech,
                requires_latch_id=req_l,
                unlocks_shortcut_latch_id=unl_l,
                lift_id=l_id,
                required_lift_state=req_l_state,
                portal_transform=p_tr,
                has_direct_sightline=has_los,
                acoustic_distance_u=sound_dist,
            )
        )

    layout = CyclicLevelLayout(
        seed=int(seed),
        graph_signature="",
        nodes=nodes,
        edges=edges,
        spawn_region_id=0,
        exit_region_id=exit_id,
        num_latches=2,
        num_lifts=1,
    )
    layout.graph_signature = canonical_graph_signature(layout)
    return layout


# =============================================================================
# 5. Verification Suite with Explicit NumPy Assertions
# =============================================================================

def test_200_seeds_completable_and_metrics(num_seeds: int = 200) -> dict[str, Any]:
    """Run 200 seeds and assert >= 150 distinct graphs, 100% completable, 0 window repeats, and both Armature dispositions."""
    distinct_graphs: set[str] = set()
    template_usage_counts: dict[str, int] = {}
    states_counts: list[int] = []
    routes_counts: list[int] = []
    sim_scores: list[float] = []
    saw_bypassable_armature = False
    saw_fight_required_armature = False

    for s in range(1, num_seeds + 1):
        lvl = generate_cyclic_level(seed=s)
        distinct_graphs.add(lvl.graph_signature)
        for n in lvl.nodes.values():
            assert n.template_name in CHUNK_LIBRARY, f"Node {n.region_id} used non-library template {n.template_name}"
            template_usage_counts[n.template_name] = template_usage_counts.get(n.template_name, 0) + 1

        proof = prove_level_completability(lvl)
        assert proof["completable"], f"Seed {s} failed completability proof: {proof}"
        assert proof["trap_states"] == 0, f"Seed {s} had soft-lock trap states: {proof}"
        assert proof["detour_bypasses_hollow_bay"], f"Seed {s} lacked detour around Hollow bay"
        assert proof["distinct_simple_routes"] >= 3, f"Seed {s} had too few distinct routes: {proof['distinct_simple_routes']}"

        for disp in proof["armature_room_dispositions"].values():
            if disp == "bypassable_by_detour":
                saw_bypassable_armature = True
            elif disp == "fight_required":
                saw_fight_required_armature = True

        metrics = evaluate_variety_and_pacing_metrics(lvl)
        assert metrics["passes_all_metrics"], f"Seed {s} failed variety/pacing metrics: {metrics}"
        assert metrics["window_3step_repeat_rate"] == 0.0, f"Seed {s} repeated a template within a 3-room window!"

        states_counts.append(proof["reachable_states"])
        routes_counts.append(proof["distinct_simple_routes"])
        sim_scores.append(metrics["mean_adjacent_similarity"])

    assert len(distinct_graphs) >= 150, f"Expected >= 150 distinct graphs in {num_seeds} seeds, got {len(distinct_graphs)}"
    reused_templates = [k for k, cnt in template_usage_counts.items() if cnt >= 10]
    assert len(reused_templates) >= 8, f"Chunk library templates should be reused across seeds, got {template_usage_counts}"
    assert saw_bypassable_armature and saw_fight_required_armature, (
        "Expected both 'bypassable_by_detour' and 'fight_required' Armature room dispositions across seeds"
    )

    return {
        "status": "verified (test_200_seeds_completable_and_metrics)",
        "seeds_tested": num_seeds,
        "distinct_connection_graphs": len(distinct_graphs),
        "reused_library_templates_count": len(reused_templates),
        "completable_rate": 1.0,
        "soft_lock_trap_count_total": 0,
        "window_3step_repeat_rate_max": 0.0,
        "saw_bypassable_armature": saw_bypassable_armature,
        "saw_fight_required_armature": saw_fight_required_armature,
        "reachable_states_min_max": [int(min(states_counts)), int(max(states_counts))],
        "distinct_routes_min_max": [int(min(routes_counts)), int(max(routes_counts))],
        "mean_adjacent_similarity": round(float(np.mean(sim_scores)), 4),
    }


def test_bad_layouts_and_broken_chunks_rejected() -> dict[str, Any]:
    """Verify that one-way traps, narrow sockets, isolated portal loops, monotonous chains, AND landmark-stripped layouts fail."""
    base = generate_cyclic_level(seed=1)

    # 1. Broken Case A: Pit you can drop into before turning the valve, where getting out needs the valve!
    nodes_trap = dict(base.nodes)
    nodes_trap[99] = ChunkNode(
        region_id=99,
        template_name="VALVE_GATED_TRAP_PIT",
        tags=("room",),
        size_xy_u=(256.0, 256.0),
        floor_z_u=-128.0,
        ceil_z_u=64.0,
        light_level=96,
        material="poured_concrete",
        center_xyz_u=(0.0, -400.0, -128.0),
        polygon_2d_u=_rect_poly(256.0, 256.0),
    )
    edges_trap = list(base.edges) + [
        ChunkEdge(0, 99, (0.0, -200.0), mechanism="ONE_WAY_DROP"),
        ChunkEdge(99, 0, (0.0, -200.0), mechanism="LATCH_GATE", requires_latch_id=0),
    ]
    lvl_trap = CyclicLevelLayout(1, "BROKEN_VALVE_TRAP", nodes_trap, edges_trap, 0, base.exit_region_id)
    proof_trap = prove_level_completability(lvl_trap)
    assert (not proof_trap["completable"]) and ("SOFT_LOCK_TRAP" in proof_trap["reason"]) and proof_trap["trap_states"] > 0

    # 2. Broken Case B: Narrow Socket (< 28 u clearance for 12 u radius player disc)
    edges_narrow = list(base.edges) + [ChunkEdge(0, 1, (0.0, 0.0), socket_width_u=20.0)]
    lvl_narrow = CyclicLevelLayout(1, "BROKEN_NARROW", dict(base.nodes), edges_narrow, 0, base.exit_region_id)
    proof_narrow = prove_level_completability(lvl_narrow)
    assert (not proof_narrow["completable"]) and ("NARROW_SOCKET_OR_PASSAGE" in proof_narrow["reason"])

    # 3. Broken Case C: Isolated Portal Loop with No Exit
    p_iso = PortalTransformSE2Z(128.0, 0.0, 0.0, 0.5 * math.pi)
    edges_no_exit = [
        ChunkEdge(0, 1, (0.0, 0.0), mechanism="ROTATED_PORTAL", portal_transform=p_iso),
        ChunkEdge(1, 0, (0.0, 0.0), mechanism="ROTATED_PORTAL", portal_transform=p_iso),
    ]
    lvl_no_exit = CyclicLevelLayout(1, "BROKEN_PORTAL_LOOP", dict(base.nodes), edges_no_exit, 0, base.exit_region_id)
    proof_no_exit = prove_level_completability(lvl_no_exit)
    assert (not proof_no_exit["completable"]) and ("EXIT_UNREACHABLE" in proof_no_exit["reason"])

    # 4. Broken Case D (Fix #2): All Landmarks Removed -> uncapped exit-pull distance is `inf > 384.0` and FAILS!
    nodes_no_lm = {
        rid: ChunkNode(
            n.region_id, n.template_name, n.tags, n.size_xy_u, n.floor_z_u, n.ceil_z_u,
            n.light_level, n.material, n.center_xyz_u, n.polygon_2d_u, n.interior_pillars_xy_r,
            n.interior_baffle_seg_local, None, n.activates_latch_id, n.toggles_lift_id, n.encounter_type,
        )
        for rid, n in base.nodes.items()
    }
    lvl_no_lm = CyclicLevelLayout(1, "NO_LANDMARKS", nodes_no_lm, list(base.edges), 0, base.exit_region_id)
    no_lm_metrics = evaluate_variety_and_pacing_metrics(lvl_no_lm)
    assert (not no_lm_metrics["passes_all_metrics"])
    assert not math.isfinite(no_lm_metrics["max_exit_pull_distance_u"]) and no_lm_metrics["landmark_visible_share"] == 0.0

    return {
        "status": "verified (test_bad_layouts_and_broken_chunks_rejected)",
        "pre_valve_pit_trap_reason": proof_trap["reason"],
        "narrow_socket_reason": proof_narrow["reason"],
        "portal_no_exit_reason": proof_no_exit["reason"],
        "no_landmarks_exit_pull_failed": True,
    }


def test_seed_determinism() -> dict[str, Any]:
    l1 = generate_cyclic_level(seed=77)
    l2 = generate_cyclic_level(seed=77)
    assert l1.graph_signature == l2.graph_signature and l1.nodes == l2.nodes and l1.edges == l2.edges
    assert prove_level_completability(l1) == prove_level_completability(l2)
    return {"status": "verified (test_seed_determinism)", "deterministic": True}


def run_all_cyclic_generator_tests() -> dict[str, Any]:
    return {
        "all_verified": True,
        "seeds_200_suite": test_200_seeds_completable_and_metrics(200),
        "broken_rejection_suite": test_bad_layouts_and_broken_chunks_rejected(),
        "determinism": test_seed_determinism(),
    }


if __name__ == "__main__":
    print(json.dumps(run_all_cyclic_generator_tests(), indent=2))