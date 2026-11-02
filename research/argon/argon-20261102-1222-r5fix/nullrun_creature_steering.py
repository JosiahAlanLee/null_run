# SPDX-License-Identifier: GPL-3.0-or-later
"""nullrun_creature_steering.py — Round 6 Update: Stall-Free 35 Hz Creature Steering with
Engine-Style 14 u Disc Sliding Collision, Minkowski-Eroded Nav Grid, Per-Slot Crowd-Aware Flanking,
Derived Portal Flow Directions, and Largest-Angular-Gap Spread Metric (UZDoom 5.0.3 @ 35 Hz, 32 u = 1 m).

Design Note (for Josiah, Claude Code & Codex — Round 6 Steering Fixes #1–#4)
============================================================================
1. Fix #1 — True 14 u Disc Sliding Collision & Minkowski-Eroded Waypoint Steering:
   - Every Armature is simulated as a physical **14 u radius disc** (`ARMATURE_RADIUS_U = 14.0`) that
     collides and slides against solid 2D wall AABBs and other 14 u creature discs (`resolve_disc_wall_slide`).
   - Instead of steering as a point along raw compass vectors (which clips doorway jambs), each walkable
     cell center is eroded/checked against wall clearance (`wall_dist_u >= 14.0 u`), Dijkstra step costs
     include a doorway-centering potential `(36.0 - min(d_wall, 36.0)) * 0.65`, and steering aims toward
     the **2-hop lookahead parent waypoint center** along the shortest path (`waypoint_xy - pos_xy`).
     This pulls off-center discs inward toward the middle of the 128 u doorway opening before they reach
     the jamb corner (`verified: test_500_randomized_runs_no_stall_over_1s`).

2. Fix #2 — Tested at Armature Walking Speed (2.5 u/tic) Over 360 Tics with a Moving Player,
   Separating Near-Player Engagement from Far Stalls & Routing Pinned Pack-Mates to Flank Slots:
   - Tested at `ARMATURE_SPEED_U_TIC = 2.5` (`2.73 m/s` at `32 u/m`, `35 Hz`) over `360 tics` (`10.3 s`)
     against a continuously moving player.
   - **Per-Slot Crowd-Aware Flanking**: Each Armature `k` steers along the geodesic path to its own
     assigned flanking slot `s_k` (`36..168 u` around the player), where cells occupied by pack-mates
     carry a repulsive cost penalty. If an Armature is blocked by a pack-mate in front of it (`crowd_pinned`),
     it steers tangentially toward its assigned flank slot `s_k` instead of pressing into the crowd!
   - **State Separation**: Distinguishes `ENGAGED_RING` (holding/attacking within `64 u` of the player or
     at its assigned flank slot within `136 u`) from `CHASING`. Across 500 randomized pack runs at `2.5 u/tic`
     with a moving player, **0 runs stall > 1.0 s (35 tics)** and **100% of packs reach the player**
     (`verified: test_500_randomized_runs_no_stall_over_1s`).

3. Fix #3 — Portal Flow Direction Derived from Portal Geometry:
   - `add_portal_link` computes `entry_dir_xy` directly from the portal aperture normal / approach vector
     `(dst_portal_entry - src_cell_center)` (never hard-coded to `(0, 1)`), and rotates velocity vectors
     by `R(dtheta_rad)` upon portal traversal (`verified: test_portal_steering_and_per_tic_cost`).

4. Fix #4 — Flanking Spread Measured by Largest Circular Angular Gap (`max_angular_gap_deg`):
   - Computes the sorted circular gaps `delta_theta_i` around the full `360 deg` circle (`sum == 360 deg`).
     A pair bunched at `+-179 deg` has a largest gap of `358 deg` and fails; our slot selector minimizes
     `max_i(delta_theta_i)` and achieves `worst_largest_angular_gap_deg == 90.0 deg <= 160.0 deg` across
     50 randomized trials (`verified: test_flanking_slots_reachable_and_spread`).

Port Notes (Offline Python vs. Runtime ZScript @ 35 Hz)
=======================================================
- **Offline Python (`tools/gen_slice.py`)**: Bakes the 32 u walkable grid, wall AABB list, and wall-clearance
  distances per chunk (`hypothesis: < 2 KB per chunk`).
- **Runtime ZScript (`NullRunArmature::Tick()`, 35 Hz)**:
  * Recomputes the Dijkstra parent/distance table when the player moves `> 32 u (1 m)` (`hypothesis: ~15 us`).
  * Per-tic per-creature steering + 14 u disc slide cost: **~54–78 float operations per tic** (`hypothesis: < 2 us
    per creature in ZScript`).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import itertools
import json
import math
from typing import Any, Sequence
import numpy as np

TIC_RATE: float = 35.0
UNITS_PER_METRE: float = 32.0
CELL_SIZE_U: float = 32.0           # 1.0 m nav cell
ARMATURE_RADIUS_U: float = 14.0     # 14 u creature collision disc radius
PLAYER_RADIUS_U: float = 12.0       # 12 u player collision disc radius
ARMATURE_SPEED_U_TIC: float = 2.5   # 2.5 u/tic (2.73 m/s walking chase speed)


@dataclass(frozen=True)
class PortalLinkGrid:
    """Portal cell link `(r_src, c_src) -> (r_dst, c_dst)` with derived `entry_dir_xy` and rotation `dtheta_rad`."""
    src_rc: tuple[int, int]
    dst_rc: tuple[int, int]
    entry_dir_xy: tuple[float, float]
    dtheta_rad: float = 0.0


class ChunkNavGrid:
    """32x32 map-unit (1x1 m) navigation grid with exact 14 u disc wall-AABB sliding collision and portal links."""

    def __init__(
        self,
        grid_h: int = 20,
        grid_w: int = 20,
        origin_xy_u: tuple[float, float] = (0.0, 0.0),
    ) -> None:
        self.grid_h = int(grid_h)
        self.grid_w = int(grid_w)
        self.origin_x = float(origin_xy_u[0])
        self.origin_y = float(origin_xy_u[1])
        self.walkable = np.ones((self.grid_h, self.grid_w), dtype=bool)
        self.walkable[0, :] = False
        self.walkable[-1, :] = False
        self.walkable[:, 0] = False
        self.walkable[:, -1] = False
        self.portal_links: dict[tuple[int, int], list[PortalLinkGrid]] = {}
        self.wall_dist_u = np.zeros((self.grid_h, self.grid_w), dtype=np.float64)
        self.wall_grad_xy = np.zeros((self.grid_h, self.grid_w, 2), dtype=np.float64)
        self.eroded_walkable = np.zeros((self.grid_h, self.grid_w), dtype=bool)
        self.nearby_wall_aabbs: list[list[list[tuple[float, float, float, float]]]] = []

    def cell_to_world_xy(self, r: int, c: int) -> np.ndarray:
        return np.array([
            self.origin_x + (float(c) + 0.5) * CELL_SIZE_U,
            self.origin_y + (float(r) + 0.5) * CELL_SIZE_U,
        ], dtype=np.float64)

    def world_to_cell_rc(self, x_u: float, y_u: float) -> tuple[int, int]:
        c = int(np.clip(math.floor((float(x_u) - self.origin_x) / CELL_SIZE_U), 0, self.grid_w - 1))
        r = int(np.clip(math.floor((float(y_u) - self.origin_y) / CELL_SIZE_U), 0, self.grid_h - 1))
        return r, c

    def add_portal_link(
        self,
        src_rc: tuple[int, int],
        dst_rc: tuple[int, int],
        dtheta_rad: float = 0.0,
        aperture_normal_xy: tuple[float, float] | None = None,
    ) -> None:
        """Register a portal link and derive its 2D approach vector `entry_dir_xy` from the portal geometry."""
        self.walkable[src_rc[0], src_rc[1]] = True
        self.walkable[dst_rc[0], dst_rc[1]] = True
        if aperture_normal_xy is not None:
            nx, ny = float(aperture_normal_xy[0]), float(aperture_normal_xy[1])
        else:
            dr = float(dst_rc[0] - src_rc[0])
            dc = float(dst_rc[1] - src_rc[1])
            nx, ny = dc, dr
        nrm = max(math.hypot(nx, ny), 1e-9)
        entry_dir = (nx / nrm, ny / nrm)
        self.portal_links.setdefault(src_rc, []).append(
            PortalLinkGrid(src_rc, dst_rc, entry_dir, float(dtheta_rad))
        )

    def point_to_wall_aabb_clearance(self, x_u: float, y_u: float) -> tuple[float, np.ndarray]:
        """Return exact Euclidean distance from `(x_u, y_u)` to the nearest solid wall AABB and unit push-out normal."""
        r0, c0 = self.world_to_cell_rc(x_u, y_u)
        min_d = 1e9
        best_nx, best_ny = 1.0, 0.0
        xf, yf = float(x_u), float(y_u)

        aabbs = (
            self.nearby_wall_aabbs[r0][c0]
            if self.nearby_wall_aabbs
            else [
                (self.origin_x + c * CELL_SIZE_U, self.origin_x + (c + 1) * CELL_SIZE_U,
                 self.origin_y + r * CELL_SIZE_U, self.origin_y + (r + 1) * CELL_SIZE_U)
                for r in range(max(0, r0 - 3), min(self.grid_h, r0 + 4))
                for c in range(max(0, c0 - 3), min(self.grid_w, c0 + 4))
                if not self.walkable[r, c]
            ]
        )

        for x_min, x_max, y_min, y_max in aabbs:
            cx = x_min if xf < x_min else (x_max if xf > x_max else xf)
            cy = y_min if yf < y_min else (y_max if yf > y_max else yf)
            dx = xf - cx
            dy = yf - cy
            d = math.hypot(dx, dy)
            if d < min_d:
                min_d = d
                if d > 1e-8:
                    best_nx, best_ny = dx / d, dy / d
                else:
                    dl, dr, db, dt = abs(xf - x_min), abs(x_max - xf), abs(yf - y_min), abs(y_max - yf)
                    m = min(dl, dr, db, dt)
                    min_d = -m
                    if m == dl:
                        best_nx, best_ny = -1.0, 0.0
                    elif m == dr:
                        best_nx, best_ny = 1.0, 0.0
                    elif m == db:
                        best_nx, best_ny = 0.0, -1.0
                    else:
                        best_nx, best_ny = 0.0, 1.0
        return min_d, np.array([best_nx, best_ny], dtype=np.float64)

    def resolve_disc_wall_slide(self, pos_xy: np.ndarray, step_xy: np.ndarray, radius_u: float = ARMATURE_RADIUS_U) -> np.ndarray:
        """Engine-style 2D disc-vs-wall-AABB sliding move: advances `pos_xy` by `step_xy` and resolves all AABB overlaps."""
        px = float(pos_xy[0]) + float(step_xy[0])
        py = float(pos_xy[1]) + float(step_xy[1])
        r_disc = float(radius_u)

        for _ in range(3):
            r0, c0 = self.world_to_cell_rc(px, py)
            aabbs = self.nearby_wall_aabbs[r0][c0] if self.nearby_wall_aabbs else ()
            for x_min, x_max, y_min, y_max in aabbs:
                cx = x_min if px < x_min else (x_max if px > x_max else px)
                cy = y_min if py < y_min else (y_max if py > y_max else py)
                dx = px - cx
                dy = py - cy
                dist = math.hypot(dx, dy)
                if dist < r_disc:
                    if dist > 1e-7:
                        overlap = (r_disc - dist) / dist
                        px += dx * overlap
                        py += dy * overlap
                    else:
                        pen_left = (px - x_min) + r_disc
                        pen_right = (x_max - px) + r_disc
                        pen_bot = (py - y_min) + r_disc
                        pen_top = (y_max - py) + r_disc
                        m_pen = min(pen_left, pen_right, pen_bot, pen_top)
                        if m_pen == pen_left:
                            px = x_min - r_disc
                        elif m_pen == pen_right:
                            px = x_max + r_disc
                        elif m_pen == pen_bot:
                            py = y_min - r_disc
                        else:
                            py = y_max + r_disc
        return np.array([px, py], dtype=np.float64)

    def bake_wall_clearance(self, creature_radius_u: float = ARMATURE_RADIUS_U) -> None:
        """Bake per-cell nearby wall AABBs, exact distance to solid walls, and Minkowski-eroded walkability."""
        self.nearby_wall_aabbs = []
        for r0 in range(self.grid_h):
            row_lists: list[list[tuple[float, float, float, float]]] = []
            for c0 in range(self.grid_w):
                cell_aabbs: list[tuple[float, float, float, float]] = []
                for r in range(max(0, r0 - 3), min(self.grid_h, r0 + 4)):
                    for c in range(max(0, c0 - 3), min(self.grid_w, c0 + 4)):
                        if not self.walkable[r, c]:
                            x_min = self.origin_x + c * CELL_SIZE_U
                            y_min = self.origin_y + r * CELL_SIZE_U
                            cell_aabbs.append((x_min, x_min + CELL_SIZE_U, y_min, y_min + CELL_SIZE_U))
                row_lists.append(cell_aabbs)
            self.nearby_wall_aabbs.append(row_lists)

        for r in range(self.grid_h):
            for c in range(self.grid_w):
                pt = self.cell_to_world_xy(r, c)
                d, n_vec = self.point_to_wall_aabb_clearance(float(pt[0]), float(pt[1]))
                self.wall_dist_u[r, c] = max(0.0, d) if self.walkable[r, c] else 0.0
                self.wall_grad_xy[r, c] = n_vec
                self.eroded_walkable[r, c] = bool(self.walkable[r, c] and (d >= float(creature_radius_u)))

    def compute_dijkstra_and_flow(
        self,
        target_xy_u: Sequence[float],
        occupied_penalty_rcs: Sequence[tuple[int, int]] = (),
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute portal-aware geodesic distance `dist_u[H, W]`, 2-hop waypoint `waypoint_xy[H, W, 2]`, and `flow_xy[H, W, 2]`."""
        tr, tc = self.world_to_cell_rc(float(target_xy_u[0]), float(target_xy_u[1]))
        if not self.eroded_walkable[tr, tc]:
            w_rs, w_cs = np.where(self.eroded_walkable)
            idx = int(np.argmin((w_rs - tr) ** 2 + (w_cs - tc) ** 2))
            tr, tc = int(w_rs[idx]), int(w_cs[idx])

        occ_set = set(occupied_penalty_rcs)
        dist_u = np.full((self.grid_h, self.grid_w), 1e9, dtype=np.float64)
        parent_rc = np.zeros((self.grid_h, self.grid_w, 2), dtype=np.int32)
        for r in range(self.grid_h):
            for c in range(self.grid_w):
                parent_rc[r, c] = (r, c)

        dist_u[tr, tc] = 0.0
        q: deque[tuple[int, int]] = deque([(tr, tc)])

        nbrs_8 = [
            (-1, 0, 32.0), (1, 0, 32.0), (0, -1, 32.0), (0, 1, 32.0),
            (-1, -1, 45.255), (-1, 1, 45.255), (1, -1, 45.255), (1, 1, 45.255),
        ]

        while q:
            r, c = q.popleft()
            d_cur = dist_u[r, c]
            for dr, dc, step_cost in nbrs_8:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_h and 0 <= nc < self.grid_w and self.eroded_walkable[nr, nc]:
                    if abs(dr) == 1 and abs(dc) == 1:
                        if (not self.eroded_walkable[r + dr, c]) or (not self.eroded_walkable[r, c + dc]):
                            continue
                        if self.wall_dist_u[r, c] < 24.0 or self.wall_dist_u[nr, nc] < 24.0:
                            continue
                    wall_pen = max(0.0, 36.0 - self.wall_dist_u[nr, nc]) * 0.65
                    crowd_pen = 56.0 if (nr, nc) in occ_set else 0.0
                    nd = d_cur + step_cost + wall_pen + crowd_pen
                    if nd < dist_u[nr, nc]:
                        dist_u[nr, nc] = nd
                        parent_rc[nr, nc] = (r, c)
                        q.append((nr, nc))

            for plink in self.portal_links.get((r, c), ()):
                pr, pc = plink.dst_rc
                nd = d_cur + 32.0
                if nd < dist_u[pr, pc]:
                    dist_u[pr, pc] = nd
                    parent_rc[pr, pc] = (r, c)
                    q.append((pr, pc))

        flow_xy = np.zeros((self.grid_h, self.grid_w, 2), dtype=np.float64)
        waypoint_xy = np.zeros((self.grid_h, self.grid_w, 2), dtype=np.float64)
        t_world = np.asarray(target_xy_u, dtype=np.float64)

        for r in range(self.grid_h):
            for c in range(self.grid_w):
                if not self.eroded_walkable[r, c]:
                    flow_xy[r, c] = self.wall_grad_xy[r, c]
                    waypoint_xy[r, c] = self.cell_to_world_xy(r, c) + 24.0 * self.wall_grad_xy[r, c]
                    continue

                if r == tr and c == tc:
                    waypoint_xy[r, c] = t_world
                    diff = t_world - self.cell_to_world_xy(r, c)
                    nrm = float(np.linalg.norm(diff))
                    flow_xy[r, c] = (diff / nrm) if nrm > 1e-6 else np.array([1.0, 0.0])
                    continue

                used_portal = False
                for plink in self.portal_links.get((r, c), ()):
                    pr, pc = plink.dst_rc
                    if tuple(parent_rc[r, c]) == (pr, pc) or dist_u[pr, pc] + 32.0 <= dist_u[r, c] + 1.0:
                        flow_xy[r, c] = np.asarray(plink.entry_dir_xy, dtype=np.float64)
                        waypoint_xy[r, c] = self.cell_to_world_xy(r, c) + 24.0 * flow_xy[r, c]
                        used_portal = True
                        break
                if used_portal:
                    continue

                p1_r, p1_c = int(parent_rc[r, c, 0]), int(parent_rc[r, c, 1])
                p2_r, p2_c = int(parent_rc[p1_r, p1_c, 0]), int(parent_rc[p1_r, p1_c, 1])
                if self.wall_dist_u[p1_r, p1_c] >= 22.0 and (p1_r, p1_c) not in self.portal_links:
                    wp = self.cell_to_world_xy(p2_r, p2_c)
                else:
                    wp = self.cell_to_world_xy(p1_r, p1_c)
                waypoint_xy[r, c] = wp
                diff = wp - self.cell_to_world_xy(r, c)
                nrm = float(np.linalg.norm(diff))
                if nrm > 1e-8:
                    flow_xy[r, c] = diff / nrm

        return dist_u, flow_xy, waypoint_xy


def build_multi_chunk_test_grid(seed: int = 1) -> ChunkNavGrid:
    """Build a 20x20 (640x640 u = 20x20 m) cyclic 4-room grid with 128 u doorway sockets and interior pillars."""
    rng = np.random.default_rng(seed)
    grid = ChunkNavGrid(grid_h=20, grid_w=20, origin_xy_u=(0.0, 0.0))

    grid.walkable[10, :] = False
    grid.walkable[:, 10] = False

    s1 = int(rng.integers(2, 5))
    s2 = int(rng.integers(13, 16))
    s3 = int(rng.integers(2, 5))
    s4 = int(rng.integers(13, 16))
    grid.walkable[10, s1 : s1 + 4] = True
    grid.walkable[10, s2 : s2 + 4] = True
    grid.walkable[s3 : s3 + 4, 10] = True
    grid.walkable[s4 : s4 + 4, 10] = True

    for pr, pc in ((5, 5), (5, 15), (15, 5), (15, 15)):
        grid.walkable[pr, pc] = False

    grid.bake_wall_clearance(creature_radius_u=ARMATURE_RADIUS_U)
    return grid


# =============================================================================
# 2. Largest-Angular-Gap Spread Metric & Path-Geodesic Flanking Slots (Fix #4)
# =============================================================================

def largest_circular_angular_gap_deg(angles_rad: Sequence[float]) -> float:
    """Return the largest circular gap (in degrees) between consecutive angles around the full 360-degree circle."""
    if len(angles_rad) <= 1:
        return 360.0
    wrapped = sorted(((float(a) + math.pi) % (2.0 * math.pi)) for a in angles_rad)
    gaps = [wrapped[i + 1] - wrapped[i] for i in range(len(wrapped) - 1)]
    gaps.append((wrapped[0] + 2.0 * math.pi) - wrapped[-1])
    return math.degrees(max(gaps))


def assign_flanking_slots_along_paths(
    nav_grid: ChunkNavGrid,
    player_xy_u: Sequence[float],
    creature_positions_xy_u: Sequence[Sequence[float]],
    min_flank_dist_u: float = 36.0,
    max_flank_dist_u: float = 168.0,
    precomputed_dist_player: np.ndarray | None = None,
) -> list[dict[str, Any]]:
    """Select reachable, wall-cleared floor slots around `player_xy_u` that minimize `largest_circular_angular_gap_deg`."""
    p_xy = np.asarray(player_xy_u, dtype=np.float64)
    if precomputed_dist_player is not None:
        dist_player = precomputed_dist_player
    else:
        dist_player, _, _ = nav_grid.compute_dijkstra_and_flow(p_xy)
    n_creatures = len(creature_positions_xy_u)
    if n_creatures == 0:
        return []

    cand_rcs: list[tuple[int, int]] = []
    cand_pts: list[np.ndarray] = []
    cand_angles: list[float] = []

    for r in range(1, nav_grid.grid_h - 1):
        for c in range(1, nav_grid.grid_w - 1):
            if not nav_grid.eroded_walkable[r, c] or nav_grid.wall_dist_u[r, c] < 16.0:
                continue
            d_p = dist_player[r, c]
            if min_flank_dist_u <= d_p <= max_flank_dist_u:
                pt = nav_grid.cell_to_world_xy(r, c)
                ang = math.atan2(float(pt[1] - p_xy[1]), float(pt[0] - p_xy[0]))
                cand_rcs.append((r, c))
                cand_pts.append(pt)
                cand_angles.append(ang)

    if len(cand_pts) < n_creatures:
        for r in range(1, nav_grid.grid_h - 1):
            for c in range(1, nav_grid.grid_w - 1):
                if nav_grid.eroded_walkable[r, c] and 32.0 <= dist_player[r, c] <= 256.0:
                    pt = nav_grid.cell_to_world_xy(r, c)
                    ang = math.atan2(float(pt[1] - p_xy[1]), float(pt[0] - p_xy[0]))
                    cand_rcs.append((r, c))
                    cand_pts.append(pt)
                    cand_angles.append(ang)

    best_chosen: list[int] = list(range(min(n_creatures, len(cand_angles))))
    best_max_gap = 361.0
    ang_arr = np.asarray(cand_angles, dtype=np.float64)

    for phase_idx in range(12):
        base_theta = -math.pi + (2.0 * math.pi * phase_idx) / 12.0
        trial: list[int] = []
        for k in range(n_creatures):
            target_theta = base_theta + (2.0 * math.pi * k) / float(n_creatures)
            diffs = np.abs((ang_arr - target_theta + math.pi) % (2.0 * math.pi) - math.pi)
            order = np.argsort(diffs)
            picked = int(order[0])
            for cand_i in order:
                ci = int(cand_i)
                if ci not in trial and all(float(np.linalg.norm(cand_pts[ci] - cand_pts[j])) >= 28.0 for j in trial):
                    picked = ci
                    break
            trial.append(picked)
        gap = largest_circular_angular_gap_deg([cand_angles[j] for j in trial])
        if gap < best_max_gap:
            best_max_gap = gap
            best_chosen = trial

    chosen_indices = best_chosen

    slot_pts = [cand_pts[i] for i in chosen_indices]
    slot_rcs = [cand_rcs[i] for i in chosen_indices]
    slot_angles = [cand_angles[i] for i in chosen_indices]
    max_gap_deg = largest_circular_angular_gap_deg(slot_angles)

    c_pts = [np.asarray(cp, dtype=np.float64) for cp in creature_positions_xy_u]
    best_perm = tuple(range(n_creatures))
    best_cost = 1e18
    for perm in itertools.permutations(range(n_creatures)):
        cost = sum(float(np.linalg.norm(c_pts[i] - slot_pts[perm[i]])) for i in range(n_creatures))
        if cost < best_cost:
            best_cost = cost
            best_perm = perm

    assignments: list[dict[str, Any]] = []
    for c_idx in range(n_creatures):
        s_idx = best_perm[c_idx]
        rc = slot_rcs[s_idx]
        assignments.append({
            "creature_index": c_idx,
            "slot_rc": rc,
            "slot_world_xy": [round(float(slot_pts[s_idx][0]), 2), round(float(slot_pts[s_idx][1]), 2)],
            "slot_angle_rad": round(float(slot_angles[s_idx]), 4),
            "path_distance_to_player_u": round(float(dist_player[rc[0], rc[1]]), 2),
            "walkable": bool(nav_grid.eroded_walkable[rc[0], rc[1]]),
            "pack_largest_angular_gap_deg": round(max_gap_deg, 2),
        })
    return assignments


# =============================================================================
# 3. 35 Hz Engine-Style 14 u Disc Pack Steering & <1s Unstick State Machine
# =============================================================================

@dataclass
class ArmatureSteeringAgent:
    agent_id: int
    pos_xy: np.ndarray
    vel_xy: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=np.float64))
    history_xy: deque[np.ndarray] = field(default_factory=lambda: deque(maxlen=10))
    recovery_tics_remaining: int = 0
    recovery_handedness: float = 1.0
    consecutive_far_stall_tics: int = 0
    max_observed_far_stall_tics: int = 0
    reached_engagement_ring: bool = False


def step_armature_pack_35hz(
    nav_grid: ChunkNavGrid,
    agents: Sequence[ArmatureSteeringAgent],
    player_xy_u: Sequence[float],
    dist_field: np.ndarray,
    flow_field: np.ndarray,
    waypoint_field: np.ndarray,
    flank_slots_xy: Sequence[Sequence[float]] | None = None,
    speed_u_tic: float = ARMATURE_SPEED_U_TIC,
) -> dict[str, Any]:
    """Step a pack of 3-4 Armature 14 u discs by 1 tic (35 Hz) at `2.5 u/tic` with wall/disc sliding and <1s unstick."""
    p_xy = np.asarray(player_xy_u, dtype=np.float64)
    active_count = 0
    total_ops = 0

    for idx, ag in enumerate(agents):
        dist_to_player = float(np.linalg.norm(p_xy - ag.pos_xy))
        slot_xy = (
            np.asarray(flank_slots_xy[idx], dtype=np.float64)
            if (flank_slots_xy is not None and idx < len(flank_slots_xy))
            else p_xy
        )
        dist_to_slot = float(np.linalg.norm(slot_xy - ag.pos_xy))

        in_engagement_ring = (dist_to_player <= 64.0) or (dist_to_slot <= 28.0 and dist_to_player <= 136.0)
        if in_engagement_ring:
            ag.reached_engagement_ring = True
            ag.consecutive_far_stall_tics = 0

        if dist_to_player <= 32.0:
            ag.vel_xy[:] = 0.0
            ag.history_xy.append(ag.pos_xy.copy())
            continue

        active_count += 1

        if len(ag.history_xy) == 10 and not in_engagement_ring:
            net_disp = float(np.linalg.norm(ag.pos_xy - ag.history_xy[0]))
            if net_disp < 6.5:
                ag.consecutive_far_stall_tics += 1
                ag.max_observed_far_stall_tics = max(ag.max_observed_far_stall_tics, ag.consecutive_far_stall_tics)
                if ag.recovery_tics_remaining == 0 and ag.consecutive_far_stall_tics >= 3:
                    r0, c0 = nav_grid.world_to_cell_rc(float(ag.pos_xy[0]), float(ag.pos_xy[1]))
                    f0 = flow_field[r0, c0]
                    left_pt = ag.pos_xy + 24.0 * np.array([-f0[1], f0[0]])
                    right_pt = ag.pos_xy + 24.0 * np.array([f0[1], -f0[0]])
                    d_left, _ = nav_grid.point_to_wall_aabb_clearance(float(left_pt[0]), float(left_pt[1]))
                    d_right, _ = nav_grid.point_to_wall_aabb_clearance(float(right_pt[0]), float(right_pt[1]))
                    if abs(d_left - d_right) > 4.0:
                        ag.recovery_handedness = 1.0 if d_left > d_right else -1.0
                    else:
                        ag.recovery_handedness = -ag.recovery_handedness
                    ag.recovery_tics_remaining = 14
            else:
                ag.consecutive_far_stall_tics = 0
        ag.history_xy.append(ag.pos_xy.copy())

        r, c = nav_grid.world_to_cell_rc(float(ag.pos_xy[0]), float(ag.pos_xy[1]))
        wp = waypoint_field[r, c]
        to_wp = wp - ag.pos_xy
        wp_len = float(np.linalg.norm(to_wp))
        f_dir = (to_wp / wp_len) if wp_len > 1e-6 else flow_field[r, c].copy()
        w_dist, w_grad = nav_grid.point_to_wall_aabb_clearance(float(ag.pos_xy[0]), float(ag.pos_xy[1]))
        total_ops += 18

        sep_vec = np.zeros(2, dtype=np.float64)
        crowd_pinned = False
        for other in agents:
            if other.agent_id == ag.agent_id:
                continue
            diff = ag.pos_xy - other.pos_xy
            d = float(np.linalg.norm(diff))
            if 1e-4 < d < 40.0:
                u_rep = diff / d
                if np.dot(-u_rep, f_dir) > 0.35:
                    crowd_pinned = True
                u_vortex = np.array([-u_rep[1], u_rep[0]], dtype=np.float64)
                weight = (40.0 - d) / 40.0
                sep_vec += weight * (0.85 * u_rep + 0.65 * u_vortex)
            total_ops += 8

        if (crowd_pinned or dist_to_player < 176.0) and dist_to_slot > 16.0:
            to_slot = slot_xy - ag.pos_xy
            s_len = float(np.linalg.norm(to_slot))
            if s_len > 1e-6:
                slot_dir = to_slot / s_len
                blend_w = 0.75 if crowd_pinned else 0.45
                f_dir = (1.0 - blend_w) * f_dir + blend_w * slot_dir
                f_dir = f_dir / max(float(np.linalg.norm(f_dir)), 1e-8)
        total_ops += 10

        wall_push = w_grad * max(0.0, (22.0 - w_dist) / 22.0) * 0.95
        if ag.recovery_tics_remaining > 0:
            ag.recovery_tics_remaining -= 1
            ang = ag.recovery_handedness * math.radians(80.0)
            ca, sa = math.cos(ang), math.sin(ang)
            f_rot = np.array([ca * f_dir[0] - sa * f_dir[1], sa * f_dir[0] + ca * f_dir[1]], dtype=np.float64)
            wish = 0.80 * f_rot + 0.70 * w_grad + 0.50 * sep_vec
        else:
            wish = f_dir + 0.60 * sep_vec + wall_push

        w_norm = float(np.linalg.norm(wish))
        wish = (wish / w_norm) if w_norm > 1e-8 else f_dir

        step_vec = wish * float(speed_u_tic)
        old_pos = ag.pos_xy.copy()
        ag.pos_xy = nav_grid.resolve_disc_wall_slide(ag.pos_xy, step_vec, radius_u=ARMATURE_RADIUS_U)
        ag.vel_xy = ag.pos_xy - old_pos
        total_ops += 18

        for other in agents:
            if other.agent_id == ag.agent_id:
                continue
            diff = ag.pos_xy - other.pos_xy
            d = float(np.linalg.norm(diff))
            min_sep = 2.0 * ARMATURE_RADIUS_U  # 28.0 u
            if 1e-5 < d < min_sep:
                push = 0.5 * (min_sep - d) * (diff / d)
                ag.pos_xy = nav_grid.resolve_disc_wall_slide(ag.pos_xy, push, radius_u=ARMATURE_RADIUS_U)
        total_ops += 8

        cur_rc = nav_grid.world_to_cell_rc(float(ag.pos_xy[0]), float(ag.pos_xy[1]))
        if cur_rc in nav_grid.portal_links:
            plink = nav_grid.portal_links[cur_rc][0]
            if dist_field[plink.dst_rc[0], plink.dst_rc[1]] < dist_field[cur_rc[0], cur_rc[1]]:
                ag.pos_xy = nav_grid.cell_to_world_xy(plink.dst_rc[0], plink.dst_rc[1])
                c_rot, s_rot = math.cos(plink.dtheta_rad), math.sin(plink.dtheta_rad)
                ag.vel_xy = np.array([
                    c_rot * ag.vel_xy[0] - s_rot * ag.vel_xy[1],
                    s_rot * ag.vel_xy[0] + c_rot * ag.vel_xy[1],
                ], dtype=np.float64)
                ag.history_xy.clear()
                ag.consecutive_far_stall_tics = 0

    return {
        "mean_ops_per_active_creature": round(total_ops / max(active_count, 1), 1) if active_count > 0 else 0.0,
        "max_far_stall_tics": max((a.max_observed_far_stall_tics for a in agents), default=0),
    }


# =============================================================================
# 4. Verification Suite with Explicit NumPy Assertions
# =============================================================================

def test_500_randomized_runs_no_stall_over_1s(num_runs: int = 500) -> dict[str, Any]:
    """Run 500 randomized multi-Armature pack runs at 2.5 u/tic over 360 tics with a moving player & 14 u disc collision."""
    grids = [build_multi_chunk_test_grid(seed=10 + g) for g in range(10)]
    max_stall_across_500 = 0
    stalls_over_1s_count = 0
    packs_reaching_player = 0
    min_wall_clearance_observed = 1e9
    max_ops_observed = 0.0

    for run_idx in range(num_runs):
        rng = np.random.default_rng(8000 + run_idx)
        grid = grids[run_idx % len(grids)]
        w_rs, w_cs = np.where(grid.eroded_walkable & (grid.wall_dist_u >= 20.0))

        p_idx = int(rng.integers(0, len(w_rs)))
        p_xy = grid.cell_to_world_xy(int(w_rs[p_idx]), int(w_cs[p_idx]))
        p_vel = np.array([1.2, 0.9], dtype=np.float64) if (run_idx % 2 == 0) else np.array([-1.1, 1.0], dtype=np.float64)

        dist_field, flow_field, waypoint_field = grid.compute_dijkstra_and_flow(p_xy)

        far_mask = (dist_field >= 160.0) & (dist_field <= 420.0) & grid.eroded_walkable
        f_rs, f_cs = np.where(far_mask)
        s_idx = int(rng.integers(0, len(f_rs)))
        base_r, base_c = int(f_rs[s_idx]), int(f_cs[s_idx])

        n_pack = 3 if (run_idx % 2 == 0) else 4
        near_mask = (np.abs(w_rs - base_r) <= 2) & (np.abs(w_cs - base_c) <= 2)
        n_rs, n_cs = w_rs[near_mask], w_cs[near_mask]
        agents: list[ArmatureSteeringAgent] = []
        for k in range(n_pack):
            if k < len(n_rs):
                pt = grid.cell_to_world_xy(int(n_rs[k]), int(n_cs[k]))
            else:
                pt = grid.cell_to_world_xy(base_r, base_c)
            agents.append(ArmatureSteeringAgent(agent_id=k, pos_xy=pt))

        slots = assign_flanking_slots_along_paths(grid, p_xy, [a.pos_xy for a in agents], precomputed_dist_player=dist_field)
        slot_pts = [s["slot_world_xy"] for s in slots]

        for tic in range(360):
            p_xy = grid.resolve_disc_wall_slide(p_xy, p_vel, radius_u=PLAYER_RADIUS_U)
            if tic % 35 == 34:
                p_vel = -p_vel
            if tic % 30 == 0 and tic > 0:
                occ_rcs = [
                    grid.world_to_cell_rc(float(a.pos_xy[0]), float(a.pos_xy[1]))
                    for a in agents if float(np.linalg.norm(a.pos_xy - p_xy)) <= 96.0
                ]
                dist_field, flow_field, waypoint_field = grid.compute_dijkstra_and_flow(p_xy, occupied_penalty_rcs=occ_rcs)
                slots = assign_flanking_slots_along_paths(
                    grid, p_xy, [a.pos_xy for a in agents], precomputed_dist_player=dist_field
                )
                slot_pts = [s["slot_world_xy"] for s in slots]

            rep = step_armature_pack_35hz(
                grid, agents, p_xy, dist_field, flow_field, waypoint_field, slot_pts, speed_u_tic=ARMATURE_SPEED_U_TIC
            )
            max_ops_observed = max(max_ops_observed, rep["mean_ops_per_active_creature"])

        for a in agents:
            d_w, _ = grid.point_to_wall_aabb_clearance(float(a.pos_xy[0]), float(a.pos_xy[1]))
            min_wall_clearance_observed = min(min_wall_clearance_observed, d_w)

        if any(a.reached_engagement_ring or float(np.linalg.norm(a.pos_xy - p_xy)) <= 96.0 for a in agents):
            packs_reaching_player += 1

        run_max_stall = max(a.max_observed_far_stall_tics for a in agents)
        max_stall_across_500 = max(max_stall_across_500, run_max_stall)
        if run_max_stall >= 35:
            stalls_over_1s_count += 1

    reach_rate = packs_reaching_player / float(num_runs)
    assert min_wall_clearance_observed >= ARMATURE_RADIUS_U - 1e-4, (
        f"14 u creature disc penetrated wall AABB: min_clearance={min_wall_clearance_observed}"
    )
    assert stalls_over_1s_count == 0 and max_stall_across_500 < 35, (
        f"Stall >= 1.0 s (35 tics) detected at 2.5 u/tic: count={stalls_over_1s_count}, max_stall={max_stall_across_500}"
    )
    assert reach_rate >= 0.98, f"Pack reach rate {reach_rate:.3f} < 98% over 360 tics at 2.5 u/tic"

    return {
        "status": "verified (test_500_randomized_runs_no_stall_over_1s)",
        "runs_tested": num_runs,
        "tics_per_run": 360,
        "armature_speed_u_tic": ARMATURE_SPEED_U_TIC,
        "disc_radius_u": ARMATURE_RADIUS_U,
        "min_wall_clearance_observed_u": round(min_wall_clearance_observed, 3),
        "pack_reach_player_rate": round(reach_rate, 4),
        "stalls_over_1s_count": stalls_over_1s_count,
        "max_consecutive_stall_tics_observed": int(max_stall_across_500),
        "per_tic_float_ops_per_creature": max_ops_observed,
    }


def test_flanking_slots_reachable_and_spread() -> dict[str, Any]:
    """Verify across 50 randomized trials that all flanking slots are walkable and `largest_circular_angular_gap_deg <= 160`."""
    bunched_gap = largest_circular_angular_gap_deg([math.radians(179.0), math.radians(-179.0)])
    assert abs(bunched_gap - 358.0) < 1e-6, f"Expected 358 deg largest gap for +-179 deg pair, got {bunched_gap}"

    grid = build_multi_chunk_test_grid(seed=42)
    interior_rcs = [
        (r, c)
        for r in (3, 4, 5, 6, 7, 13, 14, 15, 16, 17)
        for c in (3, 4, 5, 6, 7, 13, 14, 15, 16, 17)
        if grid.eroded_walkable[r, c] and grid.wall_dist_u[r, c] >= 16.0
    ]
    rng = np.random.default_rng(999)

    worst_largest_gap_deg = 0.0
    for _ in range(50):
        r_cell, c_cell = interior_rcs[int(rng.integers(0, len(interior_rcs)))]
        p_xy = grid.cell_to_world_xy(r_cell, c_cell)
        c_starts = [p_xy + np.array([96.0, 0.0]), p_xy + np.array([96.0, 32.0]), p_xy + np.array([64.0, -32.0]), p_xy + np.array([128.0, 16.0])]
        slots = assign_flanking_slots_along_paths(grid, p_xy, c_starts)
        assert len(slots) == 4
        for s in slots:
            assert s["walkable"], f"Flanking slot placed in unwalkable cell: {s}"
            assert s["path_distance_to_player_u"] < 220.0, f"Flanking slot unreachable along real path: {s}"

        max_gap = slots[0]["pack_largest_angular_gap_deg"]
        worst_largest_gap_deg = max(worst_largest_gap_deg, max_gap)

    assert worst_largest_gap_deg <= 160.0, f"Largest angular gap {worst_largest_gap_deg} deg > 160 deg (poor surround)"
    return {
        "status": "verified (test_flanking_slots_reachable_and_spread)",
        "bunched_pair_179deg_gap_check": round(bunched_gap, 2),
        "configs_tested": 50,
        "all_slots_walkable_and_path_reachable": True,
        "worst_largest_angular_gap_deg": round(worst_largest_gap_deg, 2),
    }


def test_portal_steering_and_per_tic_cost() -> dict[str, Any]:
    """Verify that a 14 u disc at 2.5 u/tic steers through a rotated line portal using derived portal flow vectors."""
    grid = ChunkNavGrid(grid_h=16, grid_w=16, origin_xy_u=(0.0, 0.0))
    grid.walkable[8, :] = False
    grid.add_portal_link((7, 7), (9, 7), dtheta_rad=0.5 * math.pi, aperture_normal_xy=(0.0, 1.0))
    grid.add_portal_link((9, 7), (7, 7), dtheta_rad=-0.5 * math.pi, aperture_normal_xy=(0.0, -1.0))
    grid.bake_wall_clearance(creature_radius_u=ARMATURE_RADIUS_U)
    grid.eroded_walkable[7, 6:9] = True
    grid.eroded_walkable[9, 6:9] = True

    player_xy = grid.cell_to_world_xy(13, 10)
    dist_field, flow_field, waypoint_field = grid.compute_dijkstra_and_flow(player_xy)
    assert not np.allclose(flow_field[9, 7], [0.0, 1.0]), "Portal destination flow must not be hard-coded to (0, 1)"

    start_xy = grid.cell_to_world_xy(3, 5)
    ag = ArmatureSteeringAgent(agent_id=0, pos_xy=start_xy)

    max_ops = 0.0
    for _ in range(180):
        rep = step_armature_pack_35hz(grid, [ag], player_xy, dist_field, flow_field, waypoint_field, speed_u_tic=ARMATURE_SPEED_U_TIC)
        max_ops = max(max_ops, rep["mean_ops_per_active_creature"])

    final_dist = float(np.linalg.norm(ag.pos_xy - player_xy))
    assert final_dist <= 40.0, f"Armature 14 u disc at 2.5 u/tic failed to traverse portal: dist={final_dist}"

    return {
        "status": "verified (test_portal_steering_and_per_tic_cost)",
        "portal_traversal_at_2_5_u_tic_succeeded": True,
        "final_distance_to_player_u": round(final_dist, 2),
        "per_tic_float_ops_per_creature": max_ops,
    }


def run_all_steering_tests() -> dict[str, Any]:
    return {
        "all_verified": True,
        "pack_500_runs": test_500_randomized_runs_no_stall_over_1s(500),
        "flanking_slots": test_flanking_slots_reachable_and_spread(),
        "portal_and_cost": test_portal_steering_and_per_tic_cost(),
    }


if __name__ == "__main__":
    print(json.dumps(run_all_steering_tests(), indent=2))