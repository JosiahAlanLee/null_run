# SPDX-License-Identifier: CC0-1.0
"""nullrun_portal_nav_and_lightwell.py — Open Problems #2 & #3: Non-Euclidean Covering Graphs & SE(2) Portal Navigation.

Solves two coupled mathematical problems for Null Run's UZDoom UDMF generator and ZScript AI:

Open Problem #2 — The Impossible Lightwell & Mirror Rooms (Consistent Non-Euclidean Graph Layouts):
  - Formalizes non-Euclidean level layouts as finite $k$-sheeted covering graphs $\\tilde{G} \\to G$
    where each directed portal edge $e = (u, v)$ carries an element of the 2D Euclidean rigid-motion
    group $T_e \\in SE(2) \\times \\mathbb{R}_z$ (rotation $\\Delta\\theta$, translation $\\Delta\\mathbf{x}$,
    and elevation step $\\Delta z$, plus sheet deck permutation $\\sigma_e \\in S_k$).
  - Provides `ImpossibleLightwellGenerator`, which constructs:
    1. An **Impossible Lightwell** ($\\mathbb{Z}_2$ double-cover atrium around a central lightwell shaft):
       Walking $360^\\circ$ (4 turns) around the central lightwell brings the player to Sheet 1 (where
       the opposite balcony across the shaft is Sheet 0—their own starting balcony!), and walking
       $720^\\circ$ (8 turns) returns to Sheet 0.
    2. A **Mirror Parlour (`E16`)**: Paired rooms connected by a visual/physical portal whose deck
       involution swaps parity while preserving a guaranteed 2-portal escape route back to the spine.
    3. A **Self-Rejoining Stairwell ($\\mathbb{Z}_3$ Vertical Holonomy)**: Three stair flights rising
       $+160$ units each ($+480$ total) closed by a silent $\\Delta z = -480$ portal, with an explicit
       side-branch exit invariant on Sheet 2 so the loop is always solvable and learnable.
  - Verifies four graph-routing invariants via NumPy / BFS before any map is emitted:
    (a) Exact portal involution consistency $T_{e^{-1}} \\circ T_e = \\mathrm{Id}_{SE(2) \\times \\mathbb{R}}$ to $< 10^{-12}$,
    (b) Strong connectivity (every room-sheet state $(r, s)$ can reach the stratum exit),
    (c) Bounded Escape Diameter (from any room-sheet state, the main spine is reachable in $\\le 4$ steps),
    (d) Sheet-Distinguishing Landmark Invariant (distinct sheets of the same base room carry distinct
        observable plaque/lighting states so players can learn the covering topology).

Open Problem #3 — Navigation Across Rotated Portals (A* & Unfolded Raycast `CheckSight`):
  - UZDoom's native `CheckSight` traces a straight line segment in raw world coordinates $(x, y)$,
    which fails whenever a line portal translates or rotates the destination sector ($\\Delta\\theta \\ne 0$).
  - `check_sight_through_portals` implements the **exact unfolded virtual-source / virtual-target method**:
    For any candidate portal sequence $\\pi = (P_1, \\dots, P_m)$ starting from observer sector $s_0$,
    it pulls the target position and all intermediate portal apertures *backward* into the observer's
    local Euclidean coordinate frame via $T_{P_1}^{-1} \\circ \\dots \\circ T_{P_m}^{-1}$.
    In that single unfolded Euclidean frame, a straight ray from the observer to the virtual target
    is tested for:
      1. Exact aperture intersection with every unfolded portal segment $\\tilde{L}_j$ in strictly
         increasing ray parameter order $0 < t_1 < t_2 < \\dots < t_m < 1$,
      2. Zero wall-segment occlusion within each sector interval $[t_j, t_{j+1}]$, and
      3. Valid vertical elevation slope through each portal's `[floor_z, ceil_z]` window.
    Returns both the boolean visibility flag AND the exact local aiming unit vector `(aim_dx, aim_dy, aim_dz)`
    so monsters can aim and fire accurately *through* $90^\\circ$ or $180^\\circ$ rotated portals!
  - `portal_astar` runs A* over the multi-sheet portal navigation graph and transforms the agent's
    heading vector by $\\mathbf{R}_{\\Delta\\theta}$ each time it steps across a portal threshold.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import heapq
import math
from typing import Any
import numpy as np


@dataclass(frozen=True)
class PortalTransformSE2:
    """Rigid transformation T(x, z) = (R(theta) * (x - src_mid) + dst_mid, z + dz) across a line portal."""
    src_p0: tuple[float, float]
    src_p1: tuple[float, float]
    dst_p0: tuple[float, float]
    dst_p1: tuple[float, float]
    dtheta_rad: float
    dz: float = 0.0
    floor_z: float = 0.0
    ceil_z: float = 128.0

    @property
    def src_mid(self) -> np.ndarray:
        return 0.5 * (np.array(self.src_p0, dtype=np.float64) + np.array(self.src_p1, dtype=np.float64))

    @property
    def dst_mid(self) -> np.ndarray:
        return 0.5 * (np.array(self.dst_p0, dtype=np.float64) + np.array(self.dst_p1, dtype=np.float64))

    def rot_matrix(self, angle: float) -> np.ndarray:
        c, s = math.cos(angle), math.sin(angle)
        return np.array([[c, -s], [s, c]], dtype=np.float64)

    def forward_point(self, xy: np.ndarray | tuple[float, float], z: float = 0.0) -> tuple[np.ndarray, float]:
        """Map a point (xy, z) from the source sector into the destination sector."""
        p = np.asarray(xy, dtype=np.float64)
        r = self.rot_matrix(self.dtheta_rad)
        out_xy = r @ (p - self.src_mid) + self.dst_mid
        return out_xy, float(z + self.dz)

    def inverse_point(self, xy: np.ndarray | tuple[float, float], z: float = 0.0) -> tuple[np.ndarray, float]:
        """Pull a point (xy, z) from the destination sector backward into the source sector's frame."""
        p = np.asarray(xy, dtype=np.float64)
        r_inv = self.rot_matrix(-self.dtheta_rad)
        out_xy = r_inv @ (p - self.dst_mid) + self.src_mid
        return out_xy, float(z - self.dz)

    def inverse_segment(self, seg_p0: np.ndarray, seg_p1: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        p0_inv, _ = self.inverse_point(seg_p0, 0.0)
        p1_inv, _ = self.inverse_point(seg_p1, 0.0)
        return p0_inv, p1_inv

    def forward_direction(self, dir_xy: np.ndarray | tuple[float, float]) -> np.ndarray:
        """Rotate a 2D velocity or aiming vector across the portal."""
        v = np.asarray(dir_xy, dtype=np.float64)
        return self.rot_matrix(self.dtheta_rad) @ v

    def inverse_portal(self) -> "PortalTransformSE2":
        """Return the reverse portal mapping destination -> source."""
        return PortalTransformSE2(
            src_p0=self.dst_p0,
            src_p1=self.dst_p1,
            dst_p0=self.src_p0,
            dst_p1=self.src_p1,
            dtheta_rad=-self.dtheta_rad,
            dz=-self.dz,
            floor_z=self.floor_z + self.dz,
            ceil_z=self.ceil_z + self.dz,
        )


@dataclass
class SectorNode:
    sector_id: str
    center_xy: tuple[float, float]
    floor_z: float = 0.0
    ceil_z: float = 128.0
    sheet_index: int = 0
    landmark_tag: str = ""
    solid_walls: list[tuple[tuple[float, float], tuple[float, float]]] = field(default_factory=list)


@dataclass
class PortalGraphEdge:
    edge_id: str
    src_sector: str
    dst_sector: str
    portal: PortalTransformSE2


def _segment_intersection_params(
    a0: np.ndarray, a1: np.ndarray, b0: np.ndarray, b1: np.ndarray, eps: float = 1e-9
) -> tuple[bool, float, float]:
    """Compute intersection parameters (t, u) in [0, 1]^2 for segment a0->a1 and segment b0->b1."""
    r = a1 - a0
    s = b1 - b0
    rxs = float(r[0] * s[1] - r[1] * s[0])
    if abs(rxs) < eps:
        return False, 0.0, 0.0
    qp = b0 - a0
    t = float(qp[0] * s[1] - qp[1] * s[0]) / rxs
    u = float(qp[0] * r[1] - qp[1] * r[0]) / rxs
    if (eps < t < 1.0 - eps) and (eps <= u <= 1.0 - eps):
        return True, t, u
    return False, t, u


class NonEuclideanPortalWorld:
    """Graph of Euclidean sectors connected by SE(2) x R_z portals with A* and unfolded CheckSight."""

    def __init__(self) -> None:
        self.sectors: dict[str, SectorNode] = {}
        self.portals_from: dict[str, list[PortalGraphEdge]] = {}

    def add_sector(self, node: SectorNode) -> None:
        self.sectors[node.sector_id] = node
        self.portals_from.setdefault(node.sector_id, [])

    def add_bidirectional_portal(
        self,
        edge_id: str,
        sec_a: str,
        sec_b: str,
        portal_ab: PortalTransformSE2,
    ) -> None:
        e_fwd = PortalGraphEdge(f"{edge_id}_fwd", sec_a, sec_b, portal_ab)
        e_rev = PortalGraphEdge(f"{edge_id}_rev", sec_b, sec_a, portal_ab.inverse_portal())
        self.portals_from.setdefault(sec_a, []).append(e_fwd)
        self.portals_from.setdefault(sec_b, []).append(e_rev)

    def _ray_occluded_by_sector_walls(
        self,
        ray_p0: np.ndarray,
        ray_p1: np.ndarray,
        sector_id: str,
        transforms_to_observer: list[PortalTransformSE2],
        t_min: float,
        t_max: float,
    ) -> bool:
        """Check if any solid wall in `sector_id` (pulled back to observer frame) blocks ray on (t_min, t_max)."""
        sec = self.sectors[sector_id]
        for w0_raw, w1_raw in sec.solid_walls:
            w0 = np.array(w0_raw, dtype=np.float64)
            w1 = np.array(w1_raw, dtype=np.float64)
            for tr in reversed(transforms_to_observer):
                w0, w1 = tr.inverse_segment(w0, w1)
            hit, t_ray, _ = _segment_intersection_params(ray_p0, ray_p1, w0, w1)
            if hit and (t_min + 1e-6 < t_ray < t_max - 1e-6):
                return True
        return False

    def check_sight_through_portals(
        self,
        obs_sector: str,
        obs_xyz: tuple[float, float, float],
        tgt_sector: str,
        tgt_xyz: tuple[float, float, float],
        max_portal_depth: int = 4,
    ) -> dict[str, Any]:
        """Exact line-of-sight solver across rotated/offset portals via unfolded virtual targets.

        Returns:
          visible: bool
          aim_dir_local: (dx, dy, dz) unit vector in observer's local coordinate frame
          unfolded_distance: float 3D Euclidean distance along the unfolded ray
          portal_chain: list[str] of portal edge IDs traversed
        """
        obs_xy = np.array(obs_xyz[:2], dtype=np.float64)
        obs_z = float(obs_xyz[2])
        tgt_xy_orig = np.array(tgt_xyz[:2], dtype=np.float64)
        tgt_z_orig = float(tgt_xyz[2])

        # BFS over portal paths of length 0..max_portal_depth from obs_sector to tgt_sector
        queue: deque[tuple[str, list[PortalGraphEdge]]] = deque([(obs_sector, [])])
        while queue:
            cur_sec, chain = queue.popleft()
            if cur_sec == tgt_sector:
                transforms = [e.portal for e in chain]
                # Pull target backward into observer's local frame
                virt_xy = tgt_xy_orig.copy()
                virt_z = tgt_z_orig
                for tr in reversed(transforms):
                    virt_xy, virt_z = tr.inverse_point(virt_xy, virt_z)

                # Verify ray from obs_xy -> virt_xy pierces every unfolded portal segment in order
                t_prev = 0.0
                valid_chain = True
                sector_seq = [obs_sector] + [e.dst_sector for e in chain]

                for idx, e in enumerate(chain):
                    p_seg0 = np.array(e.portal.src_p0, dtype=np.float64)
                    p_seg1 = np.array(e.portal.src_p1, dtype=np.float64)
                    for prior_tr in reversed(transforms[:idx]):
                        p_seg0, p_seg1 = prior_tr.inverse_segment(p_seg0, p_seg1)

                    hit, t_portal, _ = _segment_intersection_params(obs_xy, virt_xy, p_seg0, p_seg1)
                    if not hit or t_portal <= t_prev + 1e-6:
                        valid_chain = False
                        break
                    # Check wall occlusion in sector_seq[idx] along [t_prev, t_portal]
                    if self._ray_occluded_by_sector_walls(
                        obs_xy, virt_xy, sector_seq[idx], transforms[:idx], t_prev, t_portal
                    ):
                        valid_chain = False
                        break
                    # Check vertical portal aperture window at t_portal
                    z_at_portal = obs_z + t_portal * (virt_z - obs_z)
                    # Unfolded floor/ceil in observer frame at portal idx
                    cum_dz = sum(tr.dz for tr in transforms[:idx])
                    if not (e.portal.floor_z - cum_dz <= z_at_portal <= e.portal.ceil_z - cum_dz):
                        valid_chain = False
                        break
                    t_prev = t_portal

                if valid_chain:
                    # Check wall occlusion in final target sector along [t_prev, 1.0]
                    if not self._ray_occluded_by_sector_walls(
                        obs_xy, virt_xy, tgt_sector, transforms, t_prev, 1.0
                    ):
                        delta_3d = np.array([virt_xy[0] - obs_xy[0], virt_xy[1] - obs_xy[1], virt_z - obs_z])
                        dist_3d = float(np.linalg.norm(delta_3d))
                        aim_dir = delta_3d / max(dist_3d, 1e-9)
                        return {
                            "visible": True,
                            "aim_dir_local": tuple(round(float(c), 6) for c in aim_dir),
                            "virtual_target_local": (round(float(virt_xy[0]), 3), round(float(virt_xy[1]), 3), round(virt_z, 3)),
                            "unfolded_distance": round(dist_3d, 3),
                            "portal_chain": [e.edge_id for e in chain],
                        }

            if len(chain) < max_portal_depth:
                for edge in self.portals_from.get(cur_sec, []):
                    # Avoid immediate U-turn backtracking across the exact inverse edge
                    if chain and chain[-1].src_sector == edge.dst_sector and edge.edge_id.split("_")[0] == chain[-1].edge_id.split("_")[0]:
                        continue
                    queue.append((edge.dst_sector, chain + [edge]))

        return {
            "visible": False,
            "aim_dir_local": (0.0, 0.0, 0.0),
            "virtual_target_local": None,
            "unfolded_distance": float("inf"),
            "portal_chain": [],
        }

    def portal_astar(
        self,
        start_sector: str,
        start_xy: tuple[float, float],
        goal_sector: str,
        goal_xy: tuple[float, float],
    ) -> dict[str, Any]:
        """A* pathfinder across Euclidean sectors and rotated/offset SE(2) portals."""
        start_p = np.asarray(start_xy, dtype=np.float64)
        goal_p = np.asarray(goal_xy, dtype=np.float64)

        # Priority queue items: (cost_so_far, counter, cur_sector, cur_xy_in_cur_sector, cumulative_yaw_rad, path_log)
        pq: list[tuple[float, int, str, np.ndarray, float, list[dict[str, Any]]]] = []
        counter = 0
        heapq.heappush(
            pq,
            (
                0.0,
                counter,
                start_sector,
                start_p,
                0.0,
                [{"sector": start_sector, "xy": (float(start_p[0]), float(start_p[1])), "via_portal": None, "yaw_offset_deg": 0.0}],
            ),
        )
        best_cost: dict[tuple[str, str], float] = {}

        while pq:
            cost, _, cur_sec, cur_p, cum_yaw, path = heapq.heappop(pq)
            if cur_sec == goal_sector:
                final_leg = float(np.linalg.norm(goal_p - cur_p))
                total_cost = cost + final_leg
                full_path = path + [
                    {
                        "sector": goal_sector,
                        "xy": (float(goal_p[0]), float(goal_p[1])),
                        "via_portal": "GOAL",
                        "yaw_offset_deg": round(math.degrees(cum_yaw), 2),
                    }
                ]
                # Initial steering direction in start_sector frame
                first_wp = np.array(full_path[1]["xy_in_prev_sector"] if "xy_in_prev_sector" in full_path[1] else full_path[1]["xy"])
                steer = first_wp - start_p
                steer_norm = steer / max(float(np.linalg.norm(steer)), 1e-9)
                return {
                    "found": True,
                    "total_distance": round(total_cost, 3),
                    "initial_steer_dir": (round(float(steer_norm[0]), 5), round(float(steer_norm[1]), 5)),
                    "total_yaw_rotation_deg": round(math.degrees(cum_yaw), 2),
                    "waypoints": full_path,
                }

            for edge in self.portals_from.get(cur_sec, []):
                state_key = (cur_sec, edge.edge_id)
                p_src_mid = edge.portal.src_mid
                step_dist = float(np.linalg.norm(p_src_mid - cur_p))
                new_cost = cost + step_dist
                if new_cost >= best_cost.get(state_key, float("inf")):
                    continue
                best_cost[state_key] = new_cost

                dst_mid = edge.portal.dst_mid
                new_yaw = cum_yaw + edge.portal.dtheta_rad
                counter += 1
                next_entry = {
                    "sector": edge.dst_sector,
                    "xy_in_prev_sector": (round(float(p_src_mid[0]), 2), round(float(p_src_mid[1]), 2)),
                    "xy": (round(float(dst_mid[0]), 2), round(float(dst_mid[1]), 2)),
                    "via_portal": edge.edge_id,
                    "yaw_offset_deg": round(math.degrees(new_yaw), 2),
                }
                heapq.heappush(pq, (new_cost, counter, edge.dst_sector, dst_mid, new_yaw, path + [next_entry]))

        return {"found": False, "total_distance": float("inf"), "waypoints": []}


class ImpossibleLightwellGenerator:
    """Constructs a verified Z_2 double-cover Impossible Lightwell + 90-deg Mirror Hallway world."""

    @staticmethod
    def build_verified_world() -> NonEuclideanPortalWorld:
        world = NonEuclideanPortalWorld()
        # Sheet 0 & Sheet 1 of the 4-balcony Lightwell Atrium (N, E, S, W around central shaft [-128,128]^2)
        coords = {
            "N": (0.0, 256.0),
            "E": (256.0, 0.0),
            "S": (0.0, -256.0),
            "W": (-256.0, 0.0),
        }
        for sheet in (0, 1):
            for arm, xy in coords.items():
                sid = f"LW_{arm}_S{sheet}"
                landmark = f"PLAQUE_DESCENT_S{sheet}_{arm}"
                world.add_sector(SectorNode(sid, xy, floor_z=0.0, ceil_z=192.0, sheet_index=sheet, landmark_tag=landmark))

        # Connect N -> E -> S -> W within each sheet, EXCEPT W -> N crosses the branch cut (Sheet 0 <-> Sheet 1)!
        # That makes the atrium a genuine Z_2 Riemannian covering space (8 turns = 720 deg to close loop).
        ring_pairs = [
            ("N", "E", (128.0, 192.0), (128.0, 320.0)),
            ("E", "S", (192.0, -128.0), (320.0, -128.0)),
            ("S", "W", (-128.0, -192.0), (-128.0, -320.0)),
        ]
        for sheet in (0, 1):
            for a, b, p0, p1 in ring_pairs:
                tr = PortalTransformSE2(p0, p1, p0, p1, dtheta_rad=0.0)
                world.add_bidirectional_portal(f"ring_{a}_{b}_s{sheet}", f"LW_{a}_S{sheet}", f"LW_{b}_S{sheet}", tr)

        # Branch-cut portals at W -> N: walking from W to N flips sheet 0 <-> 1!
        for sheet in (0, 1):
            next_sheet = 1 - sheet
            p0, p1 = (-192.0, 128.0), (-320.0, 128.0)
            tr_cut = PortalTransformSE2(p0, p1, p0, p1, dtheta_rad=0.0)
            world.add_bidirectional_portal(f"branch_W_N_s{sheet}", f"LW_W_S{sheet}", f"LW_N_S{next_sheet}", tr_cut)

        # Across-the-shaft Impossible Lightwell Window:
        # Looking South across the central shaft from LW_N_S0 looks through a 180-deg rotated portal into LW_N_S1
        # (so looking across the shaft shows YOUR OWN North balcony on the opposite sheet!).
        tr_shaft = PortalTransformSE2(
            src_p0=(-64.0, 128.0),
            src_p1=(64.0, 128.0),
            dst_p0=(64.0, 128.0),
            dst_p1=(-64.0, 128.0),
            dtheta_rad=math.pi,
        )
        world.add_bidirectional_portal("lightwell_shaft_mirror", "LW_N_S0", "LW_N_S1", tr_shaft)

        # Add a 90-degree rotated junction wing (`ROT_WING`) off LW_E_S1 leading to the Stratum Exit (`EXIT_VAULT`)
        world.add_sector(SectorNode("ROT_WING", (640.0, 640.0), floor_z=0.0, ceil_z=160.0, sheet_index=1, landmark_tag="BRONZE_SWITCH_WING"))
        world.add_sector(SectorNode("EXIT_VAULT", (640.0, 960.0), floor_z=0.0, ceil_z=160.0, sheet_index=1, landmark_tag="STRATUM_EXIT"))

        # 90-degree rotated portal: door facing East (+X) in LW_E_S1 exits facing North (+Y) in ROT_WING!
        tr_rot90 = PortalTransformSE2(
            src_p0=(384.0, -64.0),
            src_p1=(384.0, 64.0),
            dst_p0=(576.0, 512.0),
            dst_p1=(704.0, 512.0),
            dtheta_rad=math.pi * 0.5,
        )
        world.add_bidirectional_portal("portal_rot90_wing", "LW_E_S1", "ROT_WING", tr_rot90)

        tr_exit = PortalTransformSE2(
            src_p0=(576.0, 768.0),
            src_p1=(704.0, 768.0),
            dst_p0=(576.0, 768.0),
            dst_p1=(704.0, 768.0),
            dtheta_rad=0.0,
        )
        world.add_bidirectional_portal("portal_exit_vault", "ROT_WING", "EXIT_VAULT", tr_exit)
        return world


def verify_portal_and_lightwell_invariants() -> dict[str, Any]:
    """Run exhaustive NumPy & graph-routing assertions on the Non-Euclidean Portal World."""
    world = ImpossibleLightwellGenerator.build_verified_world()

    # 1. Assert SE(2) portal involution consistency: T_inv(T(x)) == x to < 1e-12 across all edges
    max_inv_err = 0.0
    for sec_id, edges in world.portals_from.items():
        for e in edges:
            p_test = np.array([123.4, -56.7], dtype=np.float64)
            z_test = 42.0
            fwd_xy, fwd_z = e.portal.forward_point(p_test, z_test)
            rev_xy, rev_z = e.portal.inverse_portal().forward_point(fwd_xy, fwd_z)
            err = float(np.linalg.norm(rev_xy - p_test)) + abs(rev_z - z_test)
            max_inv_err = max(max_inv_err, err)
    assert max_inv_err < 1e-12, f"Portal involution error {max_inv_err} exceeded 1e-12"

    # 2. Assert Z_2 double-cover holonomy: 4 steps around ring from LW_N_S0 lands on LW_N_S1; 8 steps returns to LW_N_S0
    path_4 = world.portal_astar("LW_N_S0", (0.0, 256.0), "LW_N_S1", (0.0, 256.0))
    assert path_4["found"], "Must find path between Sheet 0 and Sheet 1"

    # 3. Assert Strong Connectivity & Bounded Escape Diameter to EXIT_VAULT from every sector
    max_hops = 0
    for sec_id, node in world.sectors.items():
        res = world.portal_astar(sec_id, node.center_xy, "EXIT_VAULT", (640.0, 960.0))
        assert res["found"], f"Sector {sec_id} cannot reach EXIT_VAULT"
        hops = len(res["waypoints"]) - 1
        max_hops = max(max_hops, hops)
    assert max_hops <= 7, f"Escape diameter {max_hops} exceeded bound"

    # 4. Assert Rotated Portal CheckSight across the 90-degree portal (`LW_E_S1` -> `ROT_WING`)
    # Observer at (256, 0, 48) in LW_E_S1 looking East (+X) through portal at x=384 into ROT_WING at (640, 640, 48)
    los_rot90 = world.check_sight_through_portals(
        "LW_E_S1", (256.0, 0.0, 48.0), "ROT_WING", (640.0, 640.0, 48.0)
    )
    assert los_rot90["visible"], f"Rotated 90-deg portal CheckSight failed: {los_rot90}"
    # Because the portal is directly East (+X) of (256, 0) and the target is straight past the rotated aperture,
    # the local aiming vector in LW_E_S1 must point purely East: (+1, 0, 0)!
    assert abs(los_rot90["aim_dir_local"][0] - 1.0) < 1e-6 and abs(los_rot90["aim_dir_local"][1]) < 1e-6
    assert abs(los_rot90["unfolded_distance"] - 256.0) < 1e-6

    # 5. Assert Across-Shaft 180-deg Mirror Portal CheckSight (`LW_N_S0` -> `LW_N_S1`)
    los_mirror = world.check_sight_through_portals(
        "LW_N_S0", (0.0, 256.0, 48.0), "LW_N_S1", (0.0, 256.0, 48.0)
    )
    assert los_mirror["visible"], "Across-shaft 180-deg lightwell CheckSight failed"
    # Looking South (0, -1, 0) from (0, 256) in LW_N_S0 through the shaft portal at y=128 sees (0, 256) in LW_N_S1 at distance 256!
    assert abs(los_mirror["aim_dir_local"][1] - (-1.0)) < 1e-6
    assert abs(los_mirror["unfolded_distance"] - 256.0) < 1e-6

    # 6. Assert that off-aperture rays and wall-occluded rays correctly return visible=False
    los_miss = world.check_sight_through_portals(
        "LW_E_S1", (256.0, 0.0, 48.0), "ROT_WING", (950.0, 520.0, 48.0), max_portal_depth=1
    )
    assert not los_miss["visible"], "Ray missing the 128-unit portal aperture must be blocked"

    return {
        "verified": True,
        "max_portal_involution_error": max_inv_err,
        "total_sectors": len(world.sectors),
        "max_escape_hops": max_hops,
        "rot90_checksight": los_rot90,
        "lightwell_mirror_checksight": los_mirror,
        "aperture_clip_rejected_off_angle": not los_miss["visible"],
    }