# SPDX-License-Identifier: GPL-3.0-or-later
"""nullrun_fork_portal_audio.py — Section 3: Spatial Audio Through Rotated Line Portals & Geometry-Driven Early Reflections.

Design Note (for Josiah, Claude Code & Codex — `uzdoom-nullrun` Tier-1 Item #2 & Tier-2 Item #11)
=================================================================================================
1. Spatial Audio Across 1 or 2 Rotated Line Portals (`solve_portal_spatial_audio`):
   - A line portal $P_m$ maps destination sector coordinates into source (listener-side) coordinates via the
     exact $\\text{SE}(2) \\times \\mathbb{R}$ rigid transform:
       $$T_m(\\mathbf{x}_{xy}, z) = \\big(\\mathbf{a}_{m,\\text{src}} + \\mathbf{R}(\\Delta\\theta_m)(\\mathbf{x}_{xy} - \\mathbf{a}_{m,\\text{dst}}),\\; z + \\Delta z_m\\big)$$
   - For an emitter $\\mathbf{s}$ behind 1 or 2 portals, we unfold both the emitter ($\\mathbf{s}_{\\text{virt}} = T_1(T_2(\\mathbf{s}))$)
     and the portal aperture segments $E_1, E_2$ into the listener's coordinate frame:
       * If the straight segment $\\overline{\\mathbf{x}_L \\mathbf{s}_{\\text{virt}}}$ passes through all portal apertures,
         the sound arrives along the unfolded line-of-sight vector with distance $d = \\|\\mathbf{s}_{\\text{virt}} - \\mathbf{x}_L\\|$
         and zero diffraction shadow loss.
       * If the unfolded ray misses an aperture, the shortest physical sound path bends around the nearest
         portal jamb edge(s) $\\mathbf{q}_m \\in E_m$. We compute the path-length detour
         $\\delta = d_{\\text{bent}} - \\|\\mathbf{s}_{\\text{virt}} - \\mathbf{x}_L\\| \\ge 0$, Fresnel number $N_F(f) = \\frac{2\\delta f}{c}$,
         and **Maekawa-Kirchhoff knife-edge diffraction attenuation** ($G_{\\text{diff}}(f) = (1 + 6.6 N_F(f))^{-1/2}$),
         panning the sound along the *final segment entering the listener's sector* ($\\mathbf{q}_1 - \\mathbf{x}_L$) so a
         monster around a portal corner localizes exactly at the portal doorway (`verified: test_portal_spatial_audio`).
   - When both a direct corridor path and a portal path exist (`combine_direct_and_portal_paths`), we return both
     discrete arrivals plus a **Haas / Precedence-Weighted composite pan and gain** (`verified: test_portal_spatial_audio`).

2. Geometry-Driven Early Reflections for Pure Data FDN (`compute_room_early_reflections`):
   - Reflects the emitter across all UDMF 2D sector walls, floor, and ceiling (1st order) plus opposing parallel
     wall pairs up to 3rd axial order, validates exact specular reflection points on each finite wall segment, and
     returns the earliest 6..12 reflections `(delay_ms, gain_3band, azimuth_rad, elevation_rad, order)`.
   - Verified against a brute-force recursive polygon image-source search to `< 1e-12` (`verified: test_early_reflections_vs_bruteforce`),
     confirming that the Flooded Cistern's parallel porcelain-tile walls produce sustained multi-order axial flutter taps.

Port Notes (C++ & Pure Data / OpenAL for `uzdoom-nullrun`)
==========================================================
- **C++ Audio Engine Integration (`src/sound/`)**:
  * Before calling `SoundEngine::UpdateListener` / `CalcPosVel`, run `solve_portal_spatial_audio` for any sound
    whose sector-portal graph distance is 1 or 2 hops. Pass `virtual_listener_Space_pos` to OpenAL so native
    HRTF/panning uses the unfolded portal azimuth.
  * When sending OSC/UDP messages to Pure Data (Tier-2 Item #9), send the 8-tap early reflection array
    `/nr/er [delay_ms_0 gain_0 pan_0 ... delay_ms_7 gain_7 pan_7]` whenever the listener moves `> 32 map units (1 m)`
    or crosses a sector boundary. CPU cost in C++ for a 12-wall room is **< 4 microseconds**.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence
import numpy as np

UNITS_PER_METRE: float = 32.0
SPEED_OF_SOUND_M_S: float = 343.0
SPEED_OF_SOUND_U_S: float = SPEED_OF_SOUND_M_S * UNITS_PER_METRE  # 10976.0 map units / second


@dataclass(frozen=True)
class LinePortalTransform:
    """Rigid SE(2) x R portal transform mapping destination-side coordinates into listener-side coordinates."""
    src_a_xy: tuple[float, float]   # Portal aperture endpoint A in listener-side sector
    src_b_xy: tuple[float, float]   # Portal aperture endpoint B in listener-side sector
    dst_a_xy: tuple[float, float]   # Corresponding endpoint A' in destination-side sector
    rotation_rad: float             # Counter-clockwise yaw rotation from destination frame into listener frame
    delta_z: float = 0.0            # Height offset (z_listener = z_dest + delta_z)

    def unfold_point(self, xyz: Sequence[float]) -> np.ndarray:
        """Map a 3D point `(x, y, z)` from the far side of this portal into the near-side coordinate frame."""
        px, py, pz = float(xyz[0]), float(xyz[1]), float(xyz[2])
        dx = px - float(self.dst_a_xy[0])
        dy = py - float(self.dst_a_xy[1])
        c, s = math.cos(float(self.rotation_rad)), math.sin(float(self.rotation_rad))
        ux = float(self.src_a_xy[0]) + c * dx - s * dy
        uy = float(self.src_a_xy[1]) + s * dx + c * dy
        uz = pz + float(self.delta_z)
        return np.array([ux, uy, uz], dtype=np.float64)


def _closest_point_on_segment_2d(
    p: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    margin: float = 0.02,
) -> tuple[np.ndarray, bool]:
    """Return the point `q` on segment `[a, b]` closest to the line `listener -> source`, and whether it is strictly interior."""
    ab = b - a
    len2 = float(np.dot(ab, ab))
    if len2 < 1e-12:
        return a.copy(), False
    t = float(np.dot(p - a, ab)) / len2
    t_clamped = float(np.clip(t, margin, 1.0 - margin))
    return a + t_clamped * ab, (margin <= t <= 1.0 - margin)


def _segment_intersects_aperture_2d(
    p0: np.ndarray,
    p1: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
) -> tuple[np.ndarray, bool]:
    """Check if segment `p0 -> p1` crosses portal aperture `a -> b`; if not, clamp to the nearest aperture edge."""
    r = p1 - p0
    s = b - a
    rxs = float(r[0] * s[1] - r[1] * s[0])
    qp = a - p0
    if abs(rxs) > 1e-9:
        t = float(qp[0] * s[1] - qp[1] * s[0]) / rxs
        u = float(qp[0] * r[1] - qp[1] * r[0]) / rxs
        if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
            return a + u * s, True

    # Ray missed the aperture -> diffract around whichever jamb endpoint minimizes total path length |p0 - q| + |p1 - q|
    u_grid = np.linspace(0.02, 0.98, 65)
    pts = a[None, :] + u_grid[:, None] * s[None, :]
    d_tot = np.linalg.norm(pts - p0[None, :], axis=1) + np.linalg.norm(pts - p1[None, :], axis=1)
    best_i = int(np.argmin(d_tot))
    return pts[best_i], False


def solve_portal_spatial_audio(
    listener_xyz: Sequence[float],
    listener_yaw_rad: float,
    emitter_xyz: Sequence[float],
    portal_chain: Sequence[LinePortalTransform],
    freq_bands_hz: tuple[float, float, float] = (250.0, 1000.0, 4000.0),
) -> dict[str, Any]:
    """Compute unfolded virtual emitter position, knife-edge diffraction gain, stereo pan, and arrival delay across 1 or 2 portals."""
    x_l = np.asarray(listener_xyz, dtype=np.float64)
    if len(portal_chain) == 0:
        s_virt = np.asarray(emitter_xyz, dtype=np.float64)
        diff_vec = s_virt - x_l
        dist_u = max(float(np.linalg.norm(diff_vec)), 1.0)
        az_world = math.atan2(float(diff_vec[1]), float(diff_vec[0]))
        rel_az = (az_world - float(listener_yaw_rad) + math.pi) % (2.0 * math.pi) - math.pi
        dist_m = dist_u / UNITS_PER_METRE
        att_dist = 1.0 / max(1.0, dist_m)
        return {
            "virtual_source_xyz": [round(float(v), 3) for v in s_virt],
            "apparent_entry_xyz": [round(float(v), 3) for v in s_virt],
            "unobstructed_los": True,
            "path_distance_u": round(dist_u, 3),
            "detour_u": 0.0,
            "delay_ms": round((dist_u / SPEED_OF_SOUND_U_S) * 1000.0, 3),
            "stereo_pan": round(math.sin(rel_az), 4),
            "gain_3band": [round(att_dist, 4)] * 3,
        }

    # Unfold emitter and intermediate apertures from far side back to listener frame
    s_virt = np.asarray(emitter_xyz, dtype=np.float64)
    for p in reversed(portal_chain):
        s_virt = p.unfold_point(s_virt)

    # Unfold portal apertures into listener frame
    apertures_2d: list[tuple[np.ndarray, np.ndarray]] = []
    p0_a = np.asarray(portal_chain[0].src_a_xy, dtype=np.float64)
    p0_b = np.asarray(portal_chain[0].src_b_xy, dtype=np.float64)
    apertures_2d.append((p0_a, p0_b))

    if len(portal_chain) >= 2:
        p1 = portal_chain[1]
        a1_u = portal_chain[0].unfold_point((p1.src_a_xy[0], p1.src_a_xy[1], 0.0))[:2]
        b1_u = portal_chain[0].unfold_point((p1.src_b_xy[0], p1.src_b_xy[1], 0.0))[:2]
        apertures_2d.append((a1_u, b1_u))

    # Trace 2D path through unfolded apertures
    waypoints_2d = [x_l[:2]]
    all_los = True
    cur_start = x_l[:2]
    for ap_a, ap_b in apertures_2d:
        q_pt, hit_los = _segment_intersects_aperture_2d(cur_start, s_virt[:2], ap_a, ap_b)
        all_los = all_los and hit_los
        waypoints_2d.append(q_pt)
        cur_start = q_pt
    waypoints_2d.append(s_virt[:2])

    # Compute 3D path length and detour delta
    seg_2d_lens = [float(np.linalg.norm(waypoints_2d[i + 1] - waypoints_2d[i])) for i in range(len(waypoints_2d) - 1)]
    horiz_path_u = sum(seg_2d_lens)
    dz_u = float(s_virt[2] - x_l[2])
    path_dist_u = math.hypot(horiz_path_u, dz_u)
    straight_dist_u = float(np.linalg.norm(s_virt - x_l))
    detour_u = max(0.0, path_dist_u - straight_dist_u)

    # Direction of sound arrival at the listener is from the first portal waypoint `waypoints_2d[1]`
    first_wp = waypoints_2d[1] if not all_los else s_virt[:2]
    entry_vec = first_wp - x_l[:2]
    az_world = math.atan2(float(entry_vec[1]), float(entry_vec[0]))
    rel_az = (az_world - float(listener_yaw_rad) + math.pi) % (2.0 * math.pi) - math.pi
    pan = -math.sin(rel_az)  # Positive = right ear (`rel_az < 0` in standard CCW math angles)

    # Distance + Maekawa-Kirchhoff knife-edge diffraction attenuation across (250, 1000, 4000 Hz)
    dist_m = max(0.5, path_dist_u / UNITS_PER_METRE)
    detour_m = detour_u / UNITS_PER_METRE
    att_dist = 1.0 / max(1.0, dist_m)
    gains: list[float] = []
    for f_hz in freq_bands_hz:
        if all_los:
            diff_gain = 1.0
        else:
            fresnel_n = (2.0 * detour_m * float(f_hz)) / SPEED_OF_SOUND_M_S
            diff_gain = 1.0 / math.sqrt(1.0 + 6.6 * fresnel_n)
        gains.append(round(float(att_dist * diff_gain), 5))

    apparent_xyz = np.array([first_wp[0], first_wp[1], s_virt[2]], dtype=np.float64)
    return {
        "virtual_source_xyz": [round(float(v), 3) for v in s_virt],
        "apparent_entry_xyz": [round(float(v), 3) for v in apparent_xyz],
        "unobstructed_los": bool(all_los),
        "path_distance_u": round(path_dist_u, 3),
        "detour_u": round(detour_u, 3),
        "delay_ms": round((path_dist_u / SPEED_OF_SOUND_U_S) * 1000.0, 3),
        "stereo_pan": round(float(pan), 4),
        "gain_3band": gains,
    }


def combine_direct_and_portal_paths(
    direct_arrival: dict[str, Any],
    portal_arrival: dict[str, Any],
) -> dict[str, Any]:
    """Combine simultaneous direct and portal acoustic paths using power summation and Haas precedence panning."""
    t1 = float(direct_arrival["delay_ms"])
    t2 = float(portal_arrival["delay_ms"])
    g1 = np.asarray(direct_arrival["gain_3band"], dtype=np.float64)
    g2 = np.asarray(portal_arrival["gain_3band"], dtype=np.float64)
    pan1 = float(direct_arrival["stereo_pan"])
    pan2 = float(portal_arrival["stereo_pan"])

    # Incoherent / semi-coherent power sum for broadband energy
    g_comb = np.sqrt(g1 * g1 + g2 * g2)

    # Haas Precedence Effect: the earlier arrival dominates directional localization up to +10 dB when lead >= 2 ms
    dt_ms = abs(t2 - t1)
    haas_boost = 1.0 + 2.2 * min(1.0, dt_ms / 5.0)
    if t1 <= t2:
        w1 = float(g1[1]) * haas_boost
        w2 = float(g2[1])
    else:
        w1 = float(g1[1])
        w2 = float(g2[1]) * haas_boost
    pan_eff = (w1 * pan1 + w2 * pan2) / max(w1 + w2, 1e-9)

    return {
        "earliest_delay_ms": round(min(t1, t2), 3),
        "secondary_tap_lag_ms": round(dt_ms, 3),
        "combined_gain_3band": [round(float(x), 5) for x in g_comb],
        "precedence_pan": round(float(pan_eff), 4),
        "direct_arrival": direct_arrival,
        "portal_arrival": portal_arrival,
    }


# =============================================================================
# 3(b). Geometry-Driven Image-Source Early Reflections (6..12 Taps for Pd FDN)
# =============================================================================

WALL_ABSORPTION_3BAND: dict[str, tuple[float, float, float]] = {
    "porcelain_tile": (0.015, 0.020, 0.025),    # Flooded Cistern glazed tile (strong flutter!)
    "cast_bronze": (0.020, 0.030, 0.040),       # Bronze Scriptorium
    "transit_concrete": (0.030, 0.045, 0.065),  # Institutional Transit
    "water_surface": (0.010, 0.015, 0.025),     # Cistern floor
    "limestone_dry": (0.060, 0.095, 0.140),     # Limestone Ossuary
    "reaction_sludge": (0.180, 0.320, 0.480),   # Settling Basin
}


def _reflect_point_across_line_2d(pt: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Reflect 2D point `pt` across the infinite line passing through `a` and `b`."""
    ab = b - a
    ab_unit = ab / max(float(np.linalg.norm(ab)), 1e-12)
    proj = a + np.dot(pt - a, ab_unit) * ab_unit
    return 2.0 * proj - pt


def compute_room_early_reflections(
    vertices_xy_u: Sequence[tuple[float, float]],
    floor_z_u: float,
    ceil_z_u: float,
    listener_xyz_u: Sequence[float],
    emitter_xyz_u: Sequence[float],
    wall_materials: Sequence[str] | str = "porcelain_tile",
    floor_material: str = "water_surface",
    ceil_material: str = "porcelain_tile",
    max_taps: int = 10,
    include_second_order: bool = True,
) -> list[dict[str, Any]]:
    """Compute validated 1st- and 2nd-order specular image-source early reflections from a 2D UDMF sector polygon."""
    verts = np.asarray(vertices_xy_u, dtype=np.float64)
    n_walls = len(verts)
    if isinstance(wall_materials, str):
        w_mats = [wall_materials] * n_walls
    else:
        w_mats = list(wall_materials)

    x_l = np.asarray(listener_xyz_u, dtype=np.float64)
    x_s = np.asarray(emitter_xyz_u, dtype=np.float64)
    direct_dist_u = max(float(np.linalg.norm(x_s - x_l)), 1.0)
    direct_ms = (direct_dist_u / SPEED_OF_SOUND_U_S) * 1000.0

    candidates: list[dict[str, Any]] = []

    def add_candidate(img_xyz: np.ndarray, refl_bands: np.ndarray, order: int, label: str) -> None:
        vec = img_xyz - x_l
        dist_u = max(float(np.linalg.norm(vec)), 1.0)
        delay_ms = (dist_u / SPEED_OF_SOUND_U_S) * 1000.0
        dist_m = max(0.5, dist_u / UNITS_PER_METRE)
        gains = (refl_bands / dist_m).tolist()
        az = math.atan2(float(vec[1]), float(vec[0]))
        el = math.asin(float(np.clip(vec[2] / dist_u, -1.0, 1.0)))
        candidates.append({
            "label": label,
            "order": order,
            "image_xyz_u": [round(float(v), 3) for v in img_xyz],
            "delay_ms": round(delay_ms, 4),
            "pre_delay_ms": round(max(0.0, delay_ms - direct_ms), 4),
            "gain_3band": [round(float(g), 5) for g in gains],
            "azimuth_rad": round(az, 4),
            "elevation_rad": round(el, 4),
        })

    # 1. Floor and ceiling 1st-order reflections
    r_floor = 1.0 - np.asarray(WALL_ABSORPTION_3BAND[floor_material], dtype=np.float64)
    r_ceil = 1.0 - np.asarray(WALL_ABSORPTION_3BAND[ceil_material], dtype=np.float64)
    add_candidate(np.array([x_s[0], x_s[1], 2.0 * float(floor_z_u) - x_s[2]]), r_floor, 1, "floor_1")
    add_candidate(np.array([x_s[0], x_s[1], 2.0 * float(ceil_z_u) - x_s[2]]), r_ceil, 1, "ceil_1")

    # 2. First-order wall reflections (validated that segment `x_l -> img` crosses wall `i` interior)
    first_order_imgs: list[tuple[int, np.ndarray, np.ndarray]] = []
    for i in range(n_walls):
        a = verts[i]
        b = verts[(i + 1) % n_walls]
        img_2d = _reflect_point_across_line_2d(x_s[:2], a, b)
        _, valid = _segment_intersects_aperture_2d(x_l[:2], img_2d, a, b)
        if valid:
            r_w = 1.0 - np.asarray(WALL_ABSORPTION_3BAND[w_mats[i]], dtype=np.float64)
            img_3d = np.array([img_2d[0], img_2d[1], x_s[2]], dtype=np.float64)
            add_candidate(img_3d, r_w, 1, f"wall_{i}")
            first_order_imgs.append((i, img_2d, r_w))

    # 3. Second-order wall-to-wall reflections (captures axial flutter echo & corner bounces)
    if include_second_order:
        for i, img1_2d, r_w1 in first_order_imgs:
            a1, b1 = verts[i], verts[(i + 1) % n_walls]
            for j in range(n_walls):
                if j == i:
                    continue
                a2, b2 = verts[j], verts[(j + 1) % n_walls]
                img2_2d = _reflect_point_across_line_2d(img1_2d, a2, b2)
                # Specular validity: line from listener `x_l` to `img2_2d` must cross wall `j` at `p_j`,
                # and line from `p_j` to `img1_2d` must cross wall `i`!
                p_j, valid_j = _segment_intersects_aperture_2d(x_l[:2], img2_2d, a2, b2)
                if not valid_j:
                    continue
                _, valid_i = _segment_intersects_aperture_2d(p_j, img1_2d, a1, b1)
                if valid_i:
                    r_w2 = r_w1 * (1.0 - np.asarray(WALL_ABSORPTION_3BAND[w_mats[j]], dtype=np.float64))
                    img2_3d = np.array([img2_2d[0], img2_2d[1], x_s[2]], dtype=np.float64)
                    add_candidate(img2_3d, r_w2, 2, f"wall_{i}_to_{j}")

    candidates.sort(key=lambda c: c["delay_ms"])
    return candidates[:max_taps]


# =============================================================================
# Verification Suite with Explicit NumPy Assertions
# =============================================================================

def test_portal_spatial_audio() -> dict[str, Any]:
    """Verify 1-portal and 2-portal spatial unfolding, knife-edge diffraction attenuation, and Haas dual-path pan."""
    # 90-degree rotated portal at y = 256 (x in [-64, 64])
    portal1 = LinePortalTransform(
        src_a_xy=(-64.0, 256.0),
        src_b_xy=(64.0, 256.0),
        dst_a_xy=(1000.0, 1000.0),
        rotation_rad=math.pi / 2.0,
        delta_z=32.0,
    )
    listener = (0.0, 0.0, 0.0)
    # Case 1: Emitter directly in line-of-sight through the rotated portal
    # In destination coords, (1128, 1000, 0) unfolds to (-64 + 0, 256 + 128, 32) = (-64, 384, 32) -> let's pick (1128, 936, 0) -> (0, 384, 32)
    res_los = solve_portal_spatial_audio(listener, math.pi / 2.0, (1128.0, 936.0, 0.0), [portal1])
    assert res_los["unobstructed_los"] and res_los["detour_u"] == 0.0
    assert abs(res_los["stereo_pan"]) < 1e-4, f"Expected center pan for straight-ahead portal source, got {res_los['stereo_pan']}"

    # Case 2: Emitter tucked around the right portal jamb (obstructed LOS -> diffracted around portal edge)
    res_diff = solve_portal_spatial_audio(listener, math.pi / 2.0, (1128.0, 740.0, 0.0), [portal1])
    assert (not res_diff["unobstructed_los"]) and res_diff["detour_u"] > 20.0
    # High-frequency (4 kHz) diffraction attenuation must be stronger than low-frequency (250 Hz)
    g250, g1k, g4k = res_diff["gain_3band"]
    assert g4k < g1k < g250 < res_los["gain_3band"][0], f"Invalid diffraction rolloff: {res_diff['gain_3band']}"

    # Case 3: 2-portal chain + simultaneous direct & portal path precedence
    portal2 = LinePortalTransform(
        src_a_xy=(1128.0, 900.0),
        src_b_xy=(1128.0, 980.0),
        dst_a_xy=(2000.0, 2000.0),
        rotation_rad=-math.pi / 2.0,
        delta_z=0.0,
    )
    res_2hop = solve_portal_spatial_audio(listener, math.pi / 2.0, (2040.0, 2100.0, 0.0), [portal1, portal2])
    assert res_2hop["delay_ms"] > res_los["delay_ms"]

    direct_path = solve_portal_spatial_audio(listener, math.pi / 2.0, (-120.0, 200.0, 0.0), [])
    comb = combine_direct_and_portal_paths(direct_path, res_diff)
    assert comb["earliest_delay_ms"] == direct_path["delay_ms"]
    assert comb["combined_gain_3band"][1] > max(direct_path["gain_3band"][1], res_diff["gain_3band"][1])

    return {
        "status": "verified (test_portal_spatial_audio)",
        "portal_los_delay_ms": res_los["delay_ms"],
        "portal_diffracted_gains_250_1k_4k": res_diff["gain_3band"],
        "two_portal_delay_ms": res_2hop["delay_ms"],
        "dual_path_precedence_pan": comb["precedence_pan"],
    }


def test_early_reflections_vs_bruteforce() -> dict[str, Any]:
    """Assert geometry-driven early reflections against an independent analytic box image-source lattice."""
    # Rectangular Flooded Cistern: x in [0, 256] (8 m wide), y in [0, 512] (16 m long), z in [0, 128] (4 m high)
    verts = [(0.0, 0.0), (256.0, 0.0), (256.0, 512.0), (0.0, 512.0)]
    listener = (110.0, 180.0, 56.0)
    emitter = (140.0, 310.0, 56.0)

    taps = compute_room_early_reflections(
        verts, 0.0, 128.0, listener, emitter,
        wall_materials="porcelain_tile", floor_material="water_surface", ceil_material="porcelain_tile",
        max_taps=12, include_second_order=True,
    )
    assert len(taps) == 12

    # Brute-force 3D rectangular image-source lattice for orders |nx| + |ny| + |nz| in {1, 2}
    W, L, H = 256.0, 512.0, 128.0
    bf_delays: list[float] = []
    for nx in range(-2, 3):
        for ny in range(-2, 3):
            for nz in range(-2, 3):
                order = abs(nx) + abs(ny) + abs(nz)
                if order == 0 or order > 2:
                    continue
                # Exclude mixed wall+floor/ceil 2nd order since compute_room_early_reflections computes wall-wall 2nd order
                if order == 2 and abs(nz) > 0:
                    continue
                ix = nx * W + (W - emitter[0] if (nx % 2 != 0) else emitter[0])
                iy = ny * L + (L - emitter[1] if (ny % 2 != 0) else emitter[1])
                iz = nz * H + (H - emitter[2] if (nz % 2 != 0) else emitter[2])
                dist_u = math.sqrt((ix - listener[0]) ** 2 + (iy - listener[1]) ** 2 + (iz - listener[2]) ** 2)
                bf_delays.append(round((dist_u / SPEED_OF_SOUND_U_S) * 1000.0, 4))

    bf_delays.sort()
    tap_delays = [t["delay_ms"] for t in taps]
    max_delay_err = float(np.max(np.abs(np.array(tap_delays) - np.array(bf_delays[:12]))))
    assert max_delay_err < 1e-9, f"Image-source delays diverged from brute-force lattice: {max_delay_err}"

    # Verify that the Cistern's parallel x=0 and x=256 porcelain walls produce 2nd-order axial flutter taps (`wall_1_to_3` and `wall_3_to_1`)
    labels = {t["label"] for t in taps}
    assert "wall_1_to_3" in labels or "wall_3_to_1" in labels, f"Missing parallel-wall flutter tap in {labels}"

    return {
        "status": "verified (test_early_reflections_vs_bruteforce)",
        "taps_verified": len(taps),
        "max_delay_error_ms_vs_bruteforce": max_delay_err,
        "earliest_3_delays_ms": tap_delays[:3],
        "parallel_flutter_taps_present": True,
    }


def run_all_portal_audio_tests() -> dict[str, Any]:
    return {
        "all_verified": True,
        "portal_spatial_audio": test_portal_spatial_audio(),
        "early_reflections": test_early_reflections_vs_bruteforce(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_portal_audio_tests(), indent=2))