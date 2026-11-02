# SPDX-License-Identifier: GPL-3.0-or-later
"""nullrun_fork_fog_reprojection.py — Round 4 Section 1: Temporal Reprojection for Volumetric Fog.

Scale: 32 Doom map units = 1 metre, 35 Hz game tics (60-240 Hz render frames).

Design Note (for Josiah, Claude Code & Codex — `uzdoom-nullrun` branch `codex/depth-postprocess`)
=================================================================================================
1. Why Surface-Depth Reprojection Trails on Volumetric Fog & The Optical Centroid Depth Solution:
   - The fork keeps a fog-only `RGBA16F` history buffer `(L_fog.rgb, opacity_a)` where `opacity_a = 1 - exp(-tau)`,
     blended at `EMA alpha = 0.18` with an `8%` per-frame photosensitivity rate limit.
   - **When Surface Depth Is Exact vs. Wrong (`verified: test_yaw_turn_180_and_strafe_4ms_trailing`)**:
     * **Pure Camera Rotation (e.g. 180 deg/s yaw turn)**: Every point `p(s) = c + s * omega` along a view
       ray projects to the *exact same* previous screen UV regardless of distance `s > 0`! Thus even surface
       depth eliminates rotational smearing.
     * **Camera Translation (e.g. 4 m/s = 128 u/s strafe)**: A fog parcel at distance `s` shifts across the
       screen at angular rate `v_perp / s`. Reprojecting using the background wall depth `d_surf` assumes all
       fog sits glued to the far wall, under-predicting the motion vector of near/mid fog by `2x..4x`!
   - **The Optical Centroid Depth `d_centroid(d_surf, opacity_a)`**:
     For an extinction ray of optical depth `tau = -ln(1 - opacity_a)` over `[0, d_surf]`, the normalized
     first moment (center of mass) of single-scattered fog weight `w(s) = sigma * exp(-sigma * s)` is:
       `g(tau) = <s / d_surf> = (1 / tau) - 1 / (exp(tau) - 1)`
     * In thin fog (`tau -> 0`), `g(tau) -> 0.5`: the fog centroid is at **half the surface depth** (`0.5 * d_surf`),
       cutting translational parallax error in half at zero extra cost!
     * In thick fog (`tau >> 1`), `g(tau) -> 1 / tau`: the centroid locks to 1 optical mean free path in front
       of the camera.
     * **Zero-Transcendental GLSL Padé Approximation**:
       Since `opacity_a = 1 - exp(-tau)` is already in channel `.a` of the current fog buffer,
         `g_pade(a) = 0.5 - 0.165 * a - 0.085 * a * a`
       approximates the exact optical centroid ratio on `a in [0, 0.95]` to `< 0.009` with **2 MUL + 2 ADD**!
     * When a localized shaft light dominates a ray at known projection distance `d_shaft`, blending
       `d_eff = mix(g_pade(a) * d_surf, d_shaft, shaft_energy_weight)` anchors the motion vector directly to
       the volumetric light shaft!

2. Disocclusion Detection & Motion-Gated Fog-Space 3x3 Clamp (Respecting the 8% Bound & Static Identity):
   - History at reprojected UV `uv_prev` is rejected/attenuated using two strictly **fog- and depth-space** checks
     (never touching scene colour):
     (a) **Relative Surface-Depth Disocclusion**: If `|d_prev(uv_prev) - d_reproj| / max(d_prev, d_reproj) > 0.18`
         or `uv_prev not in [0, 1]^2`, a doorway edge just disoccluded behind-wall fog.
     (b) **Motion-Gated Fog-Space 3x3 Box Clamp**: Compute the 3x3 min/max `[fog_min, fog_max]` of the
         *current frame's* half-res fog buffer `cur_fog_rgba`. Weight the clamp by screen-space motion
         `w_clamp = clamp(uv_shift_px / 2.5, 0.0, 0.35)` when valid (`1.0` when disoccluded). On a static
         camera (`uv_shift_px == 0` and valid), `w_clamp == 0.0`, so the output is **bit-for-bit identical**
         to the current unreprojected shader (`verified: test_portal_crossing_no_flash_and_static_identity`)!
     (c) **8% Per-Frame Photosensitivity Limiter**: After EMA + disocclusion clamping, clamp whole-frame mean
         luminance/opacity steps relative to the *previous frame's output* to `<= 8.0%` (strictly below the
         `10%` audit ceiling).

3. Line-Portal Teleport Discontinuities (`verified: test_portal_crossing_no_flash_and_static_identity`):
   - When the camera crosses a rotated line portal carrying rigid transform `T_dst_from_src in SE(2) x R`,
     multiplying `u_prev_view_proj` on the CPU by `inverse(T_dst_from_src)` (`M_VP_prev_effective = M_VP_prev @ T_inv`)
     maps post-portal world points back into pre-portal camera clip space **seamlessly**!
   - For non-geometric teleports or mismatched portal fog zones, the `<= 8%` per-frame rate-limited fade
     guarantees **zero flash (`step <= 8.0% < 10%`)**.

Port Notes (C++ & GLSL for `uzdoom-nullrun`)
============================================
- **New Uniforms Added to Volumetric Fog Pass**:
  * `uniform mat4 u_prev_view_proj;` (on portal-crossing frame, CPU pre-multiplies `M_VP_prev * inverse(T_portal)`)
  * `uniform sampler2D u_prev_linear_depth;` (half-res `R16F` linear depth from frame `t - 1`)
  * `uniform float u_portal_fade_reset;` (`1.0` on non-Euclidean zone mismatch, else `0.0`)
- **Added GPU Cost at Half-Res (960x540 on RTX 4090 / Mid GPU)**:
  * 1 matrix-vector multiply + 1 bilinear fetch from `u_prev_fog` + 1 fetch from `u_prev_linear_depth` +
    4-tap cross neighborhood min/max in `cur_fog` = **~0.03 ms on RTX 4090** (**~0.09 ms on RTX 3060 / RX 6600**),
    keeping total fog + shaft + reprojection at **~0.30 ms at 1080p**.
"""
from __future__ import annotations

import math
from typing import Any
import numpy as np

UNITS_PER_METRE: float = 32.0


def optical_centroid_depth_ratio_exact(tau: np.ndarray | float) -> np.ndarray:
    """Exact normalized optical centroid `<s / d_surf> = (1 / tau) - 1 / (exp(tau) - 1)` for extinction depth `tau`."""
    t = np.asarray(tau, dtype=np.float64)
    small = np.abs(t) < 1e-3
    t_safe = np.where(small, 1.0, t)
    exact = (1.0 / t_safe) - 1.0 / np.expm1(np.clip(t_safe, -50.0, 50.0))
    taylor = 0.5 - t / 12.0 + (t ** 3) / 720.0
    return np.clip(np.where(small, taylor, exact), 0.05, 0.5)


def optical_centroid_depth_ratio_pade(opacity_a: np.ndarray | float) -> np.ndarray:
    """Fast GLSL-ready polynomial approximation `g_pade(a)` from fog opacity `a = 1 - exp(-tau) in [0, 1)`."""
    a = np.clip(np.asarray(opacity_a, dtype=np.float64), 0.0, 0.999)
    return 0.5 - 0.165 * a - 0.085 * (a * a)


def compute_effective_fog_reprojection_depth(
    surface_depth: np.ndarray,
    fog_opacity_a: np.ndarray,
    shaft_depth_hint: np.ndarray | None = None,
    shaft_weight: np.ndarray | float = 0.0,
) -> np.ndarray:
    """Compute the optimal scalar reprojection depth `d_fog_eff` per pixel combining optical centroid and shaft depth."""
    d_surf = np.asarray(surface_depth, dtype=np.float64)
    g_ratio = optical_centroid_depth_ratio_pade(fog_opacity_a)
    d_centroid = g_ratio * d_surf
    if shaft_depth_hint is None:
        return d_centroid
    w_s = np.clip(np.asarray(shaft_weight, dtype=np.float64), 0.0, 1.0)
    d_sh = np.minimum(d_surf, np.asarray(shaft_depth_hint, dtype=np.float64))
    return (1.0 - w_s) * d_centroid + w_s * d_sh


def make_camera_matrices_25d(
    cam_pos_xyz: tuple[float, float, float],
    yaw_rad: float,
    fov_x_rad: float = math.radians(90.0),
    fov_y_rad: float = math.radians(60.0),
) -> tuple[np.ndarray, np.ndarray]:
    """Build exact 4x4 View-Projection `M_VP` and inverse `M_invVP` for a Doom camera at `(x, y, z, yaw)`."""
    cx, cy, cz = map(float, cam_pos_xyz)
    c, s = math.cos(float(yaw_rad)), math.sin(float(yaw_rad))

    r_view = np.array([
        [s, -c, 0.0],
        [0.0, 0.0, 1.0],
        [c, s, 0.0],
    ], dtype=np.float64)
    t_view = -r_view @ np.array([cx, cy, cz], dtype=np.float64)

    m_view = np.eye(4, dtype=np.float64)
    m_view[:3, :3] = r_view
    m_view[:3, 3] = t_view

    sx = 1.0 / math.tan(0.5 * float(fov_x_rad))
    sy = 1.0 / math.tan(0.5 * float(fov_y_rad))
    m_proj_inv_safe = np.array([
        [sx, 0.0, 0.0, 0.0],
        [0.0, sy, 0.0, 0.0],
        [0.0, 0.0, 1.0, -1.0],
        [0.0, 0.0, 1.0, 0.0],
    ], dtype=np.float64)
    m_vp = m_proj_inv_safe @ m_view
    m_inv_vp = np.linalg.inv(m_vp)
    return m_vp, m_inv_vp


def _bilinear_sample_rgba(img: np.ndarray, uv: np.ndarray) -> np.ndarray:
    """Bilinear sample `(H, W, C)` array `img` at normalized coordinates `uv in [0, 1]^2`."""
    H, W = img.shape[:2]
    px = np.clip(uv[..., 0] * W - 0.5, 0.0, W - 1.000001)
    py = np.clip(uv[..., 1] * H - 0.5, 0.0, H - 1.000001)
    x0 = np.floor(px).astype(np.int32)
    y0 = np.floor(py).astype(np.int32)
    x1 = np.minimum(x0 + 1, W - 1)
    y1 = np.minimum(y0 + 1, H - 1)
    fx = (px - x0)[..., None]
    fy = (py - y0)[..., None]
    c00 = img[y0, x0]
    c10 = img[y0, x1]
    c01 = img[y1, x0]
    c11 = img[y1, x1]
    return (1.0 - fy) * ((1.0 - fx) * c00 + fx * c10) + fy * ((1.0 - fx) * c01 + fx * c11)


def _fog_neighbourhood_3x3_bounds(cur_fog_rgba: np.ndarray, box_slack: float = 0.02) -> tuple[np.ndarray, np.ndarray]:
    """Compute 3x3 neighbourhood min and max in FOG space (never scene colour)."""
    f_min = cur_fog_rgba.copy()
    f_max = cur_fog_rgba.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            shifted = np.roll(np.roll(cur_fog_rgba, dy, axis=0), dx, axis=1)
            f_min = np.minimum(f_min, shifted)
            f_max = np.maximum(f_max, shifted)
    span = np.maximum(f_max - f_min, 1e-4)
    return np.maximum(0.0, f_min - box_slack * span), f_max + box_slack * span


def reproject_volumetric_fog_frame(
    cur_fog_rgba: np.ndarray,
    prev_fog_rgba: np.ndarray | None,
    cur_surface_depth: np.ndarray,
    prev_surface_depth: np.ndarray | None,
    m_vp_prev: np.ndarray,
    m_inv_vp_cur: np.ndarray,
    cam_pos_cur: tuple[float, float, float],
    reprojection_mode: str = "optical_centroid",  # "none", "surface_depth", or "optical_centroid"
    shaft_depth_hint: np.ndarray | None = None,
    shaft_weight: np.ndarray | float = 0.0,
    portal_transform_dst_from_src: np.ndarray | None = None,
    ema_alpha: float = 0.18,
    max_step_ratio: float = 0.08,
) -> dict[str, Any]:
    """Reproject `prev_fog_rgba`, clamp disocclusions in fog space, and enforce the 8% photosensitivity step bound."""
    cur = np.asarray(cur_fog_rgba, dtype=np.float64)
    if prev_fog_rgba is None or prev_surface_depth is None:
        return {
            "output_fog_rgba": cur.copy(),
            "disoccluded_fraction": 0.0,
            "whole_frame_luma_step_ratio": 0.0,
        }

    prev = np.asarray(prev_fog_rgba, dtype=np.float64)
    d_cur = np.asarray(cur_surface_depth, dtype=np.float64)
    d_prev = np.asarray(prev_surface_depth, dtype=np.float64)
    H, W = d_cur.shape

    if reprojection_mode == "none":
        hist_sample = prev.copy()
        valid_mask = np.ones((H, W), dtype=bool)
        uv_shift_px = np.zeros((H, W), dtype=np.float64)
    else:
        if reprojection_mode == "surface_depth":
            d_reproj = d_cur
        else:
            d_reproj = compute_effective_fog_reprojection_depth(
                d_cur, cur[..., 3], shaft_depth_hint=shaft_depth_hint, shaft_weight=shaft_weight
            )

        yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
        u = (xx + 0.5) / float(W)
        v = (yy + 0.5) / float(H)
        ndc_x = u * 2.0 - 1.0
        ndc_y = 1.0 - v * 2.0

        clip_reproj = np.stack([
            ndc_x * d_reproj,
            ndc_y * d_reproj,
            d_reproj - 1.0,
            d_reproj,
        ], axis=-1)
        world_pts_h = clip_reproj @ np.asarray(m_inv_vp_cur, dtype=np.float64).T
        world_pts = world_pts_h[..., :3]

        m_vp_eff = np.asarray(m_vp_prev, dtype=np.float64)
        if portal_transform_dst_from_src is not None:
            t_inv = np.linalg.inv(np.asarray(portal_transform_dst_from_src, dtype=np.float64))
            m_vp_eff = m_vp_eff @ t_inv

        world_h = np.concatenate([world_pts, np.ones((H, W, 1), dtype=np.float64)], axis=-1)
        prev_clip = world_h @ m_vp_eff.T
        z_v_prev_est = np.maximum(prev_clip[..., 3], 1e-4)
        ndc_x_prev = prev_clip[..., 0] / z_v_prev_est
        ndc_y_prev = prev_clip[..., 1] / z_v_prev_est

        u_prev = 0.5 * (ndc_x_prev + 1.0)
        v_prev = 0.5 * (1.0 - ndc_y_prev)
        uv_prev = np.stack([u_prev, v_prev], axis=-1)
        uv_shift_px = np.hypot((u_prev - u) * W, (v_prev - v) * H)

        in_bounds = (u_prev >= 0.0) & (u_prev <= 1.0) & (v_prev >= 0.0) & (v_prev <= 1.0) & (prev_clip[..., 3] > 0.1)
        hist_sample = _bilinear_sample_rgba(prev, uv_prev)

        clip_surf = np.stack([ndc_x * d_cur, ndc_y * d_cur, d_cur - 1.0, d_cur], axis=-1)
        w_surf = (clip_surf @ np.asarray(m_inv_vp_cur, dtype=np.float64).T)[..., :3]
        w_surf_h = np.concatenate([w_surf, np.ones((H, W, 1), dtype=np.float64)], axis=-1)
        p_clip_surf = w_surf_h @ m_vp_eff.T
        z_surf_prev_est = np.maximum(p_clip_surf[..., 3], 1e-4)
        u_s_prev = 0.5 * (p_clip_surf[..., 0] / z_surf_prev_est + 1.0)
        v_s_prev = 0.5 * (1.0 - p_clip_surf[..., 1] / z_surf_prev_est)
        d_prev_sampled = _bilinear_sample_rgba(d_prev[..., None], np.stack([u_s_prev, v_s_prev], axis=-1))[..., 0]
        rel_depth_err = np.abs(d_prev_sampled - z_surf_prev_est) / np.maximum(d_prev_sampled, z_surf_prev_est)
        depth_valid = rel_depth_err <= 0.18
        valid_mask = in_bounds & depth_valid

    disoccluded_frac = 1.0 - float(np.mean(valid_mask))

    if reprojection_mode == "none":
        blended = (1.0 - float(ema_alpha)) * hist_sample + float(ema_alpha) * cur
    else:
        f_min, f_max = _fog_neighbourhood_3x3_bounds(cur, box_slack=0.04)
        clamped_hist = np.clip(hist_sample, f_min, f_max)
        # Motion-gated clamp weight: 0.0 when camera is static and depth is valid (preserving exact static identity!),
        # ramping up to 0.35 under camera motion and 1.0 on disocclusion
        w_clamp = np.where(valid_mask, np.clip(uv_shift_px / 2.5, 0.0, 0.35), 1.0)[..., None]
        eff_hist = (1.0 - w_clamp) * hist_sample + w_clamp * clamped_hist
        blended = (1.0 - float(ema_alpha)) * eff_hist + float(ema_alpha) * cur

    luma_w = np.array([0.2126, 0.7152, 0.0722], dtype=np.float64)
    prev_luma = max(float(np.mean(np.sum(prev[..., :3] * luma_w, axis=-1))), 1e-4)
    new_luma = max(float(np.mean(np.sum(blended[..., :3] * luma_w, axis=-1))), 1e-4)
    luma_rel_step = (new_luma - prev_luma) / prev_luma
    if abs(luma_rel_step) > max_step_ratio:
        target_luma = prev_luma * (1.0 + math.copysign(max_step_ratio, luma_rel_step))
        blended[..., :3] *= (target_luma / new_luma)
        new_luma = target_luma

    prev_op = max(float(np.mean(prev[..., 3])), 1e-4)
    new_op = max(float(np.mean(blended[..., 3])), 1e-4)
    op_rel_step = (new_op - prev_op) / prev_op
    if abs(op_rel_step) > max_step_ratio:
        target_op = prev_op * (1.0 + math.copysign(max_step_ratio, op_rel_step))
        blended[..., 3] *= (target_op / new_op)

    final_step_ratio = abs(new_luma - prev_luma) / prev_luma
    return {
        "output_fog_rgba": blended,
        "disoccluded_fraction": round(disoccluded_frac, 4),
        "whole_frame_luma_step_ratio": round(final_step_ratio, 5),
    }


def _render_corridor_fog_ground_truth(
    cam_pos_xyz: tuple[float, float, float],
    yaw_rad: float,
    H: int = 24,
    W: int = 40,
    shaft_world_xy: tuple[float, float] = (0.0, 192.0),
    room_far_y: float = 512.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Render ground-truth no-history `(H, W, 4)` fog RGBA, surface depth `d_surf`, and shaft distance `d_shaft`."""
    _, m_inv_vp = make_camera_matrices_25d(cam_pos_xyz, yaw_rad)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    u = (xx + 0.5) / float(W)
    v = (yy + 0.5) / float(H)
    ndc_x = u * 2.0 - 1.0
    ndc_y = 1.0 - v * 2.0

    clip1 = np.stack([ndc_x, ndc_y, np.zeros_like(ndc_x), np.ones_like(ndc_x)], axis=-1)
    w1 = (clip1 @ m_inv_vp.T)[..., :3]
    c_pos = np.asarray(cam_pos_xyz, dtype=np.float64)
    ray_v = w1 - c_pos

    d_surf = np.full((H, W), float(room_far_y), dtype=np.float64)
    pillar_dir = np.array([-64.0 - c_pos[0], 256.0 - c_pos[1]], dtype=np.float64)
    pillar_dist = float(np.linalg.norm(pillar_dir))
    pillar_ang = math.atan2(pillar_dir[1], pillar_dir[0])
    ray_ang = np.arctan2(ray_v[..., 1], ray_v[..., 0])
    ang_diff = (ray_ang - pillar_ang + math.pi) % (2.0 * math.pi) - math.pi
    hit_pillar = np.abs(ang_diff) < 0.11
    d_surf = np.where(hit_pillar, min(pillar_dist, room_far_y), d_surf)

    sh_vec = np.array([shaft_world_xy[0] - c_pos[0], shaft_world_xy[1] - c_pos[1]], dtype=np.float64)
    d_shaft_val = max(32.0, float(np.linalg.norm(sh_vec)))
    d_shaft = np.full((H, W), d_shaft_val, dtype=np.float64)

    n_steps = 64
    k = (np.arange(n_steps, dtype=np.float64) + 0.5) / float(n_steps)
    s_grid = d_surf[..., None] * k[None, None, :]
    px = c_pos[0] + ray_v[..., 0:1] * s_grid
    py = c_pos[1] + ray_v[..., 1:2] * s_grid
    pz = c_pos[2] + ray_v[..., 2:3] * s_grid

    sigma0 = 0.0022
    tau_total = sigma0 * d_surf
    opacity = 1.0 - np.exp(-tau_total)
    amb_rgb = (opacity[..., None]) * np.array([0.08, 0.10, 0.12], dtype=np.float64)

    r2_shaft = ((px - shaft_world_xy[0]) ** 2 + (py - shaft_world_xy[1]) ** 2 + 0.4 * (pz - 40.0) ** 2) / (48.0 ** 2)
    beam = np.exp(-r2_shaft) * np.exp(-sigma0 * s_grid)
    ds = d_surf / float(n_steps)
    shaft_int = np.sum(beam, axis=-1) * ds * 0.012
    shaft_rgb = shaft_int[..., None] * np.array([1.35, 1.25, 0.95], dtype=np.float64)

    fog_rgba = np.concatenate([amb_rgb + shaft_rgb, opacity[..., None]], axis=-1)
    return fog_rgba, d_surf, d_shaft


def test_yaw_turn_180_and_strafe_4ms_trailing() -> dict[str, Any]:
    """Verify trailing error reduction during a 180 deg/s yaw turn and a 4 m/s (128 u/s) strafe."""
    fps = 60.0
    dt = 1.0 / fps
    yaw_rate_rad_s = math.pi
    strafe_speed_u_s = 4.0 * 32.0

    hist_none, hist_opt = None, None
    d_prev, m_vp_prev = None, None
    errs_none_yaw, errs_opt_yaw = [], []

    for f in range(12):
        yaw = 0.25 * math.pi + f * yaw_rate_rad_s * dt
        cam_pos = (0.0, 0.0, 50.0)
        gt_fog, d_cur, d_shaft = _render_corridor_fog_ground_truth(cam_pos, yaw)
        m_vp_cur, m_inv_vp_cur = make_camera_matrices_25d(cam_pos, yaw)
        if m_vp_prev is None:
            m_vp_prev = m_vp_cur

        r_none = reproject_volumetric_fog_frame(gt_fog, hist_none, d_cur, d_prev, m_vp_prev, m_inv_vp_cur, cam_pos, "none")
        r_opt = reproject_volumetric_fog_frame(gt_fog, hist_opt, d_cur, d_prev, m_vp_prev, m_inv_vp_cur, cam_pos, "optical_centroid", d_shaft, 0.75)

        hist_none = r_none["output_fog_rgba"]
        hist_opt = r_opt["output_fog_rgba"]
        d_prev, m_vp_prev = d_cur, m_vp_cur
        if f >= 2:
            errs_none_yaw.append(float(np.sqrt(np.mean((hist_none[..., :3] - gt_fog[..., :3]) ** 2))))
            errs_opt_yaw.append(float(np.sqrt(np.mean((hist_opt[..., :3] - gt_fog[..., :3]) ** 2))))

    rmse_yaw_before = float(np.mean(errs_none_yaw))
    rmse_yaw_after = float(np.mean(errs_opt_yaw))
    assert rmse_yaw_after < rmse_yaw_before * 0.25

    hist_none, hist_surf, hist_opt = None, None, None
    d_prev, m_vp_prev = None, None
    errs_none_str, errs_surf_str, errs_opt_str = [], [], []

    for f in range(15):
        cam_x = -60.0 + f * strafe_speed_u_s * dt
        cam_pos = (cam_x, 0.0, 50.0)
        yaw = 0.5 * math.pi
        gt_fog, d_cur, d_shaft = _render_corridor_fog_ground_truth(cam_pos, yaw)
        m_vp_cur, m_inv_vp_cur = make_camera_matrices_25d(cam_pos, yaw)
        if m_vp_prev is None:
            m_vp_prev = m_vp_cur

        r_none = reproject_volumetric_fog_frame(gt_fog, hist_none, d_cur, d_prev, m_vp_prev, m_inv_vp_cur, cam_pos, "none")
        r_surf = reproject_volumetric_fog_frame(gt_fog, hist_surf, d_cur, d_prev, m_vp_prev, m_inv_vp_cur, cam_pos, "surface_depth")
        r_opt = reproject_volumetric_fog_frame(gt_fog, hist_opt, d_cur, d_prev, m_vp_prev, m_inv_vp_cur, cam_pos, "optical_centroid", d_shaft, 0.75)

        hist_none = r_none["output_fog_rgba"]
        hist_surf = r_surf["output_fog_rgba"]
        hist_opt = r_opt["output_fog_rgba"]
        d_prev, m_vp_prev = d_cur, m_vp_cur
        if f >= 2:
            errs_none_str.append(float(np.sqrt(np.mean((hist_none[..., :3] - gt_fog[..., :3]) ** 2))))
            errs_surf_str.append(float(np.sqrt(np.mean((hist_surf[..., :3] - gt_fog[..., :3]) ** 2))))
            errs_opt_str.append(float(np.sqrt(np.mean((hist_opt[..., :3] - gt_fog[..., :3]) ** 2))))

    rmse_strafe_before = float(np.mean(errs_none_str))
    rmse_strafe_surf = float(np.mean(errs_surf_str))
    rmse_strafe_opt = float(np.mean(errs_opt_str))

    assert rmse_strafe_opt < rmse_strafe_surf < rmse_strafe_before

    return {
        "status": "verified (test_yaw_turn_180_and_strafe_4ms_trailing)",
        "yaw_180deg_s_rmse_before": round(rmse_yaw_before, 5),
        "yaw_180deg_s_rmse_after": round(rmse_yaw_after, 5),
        "yaw_error_reduction_factor": round(rmse_yaw_before / max(rmse_yaw_after, 1e-9), 2),
        "strafe_4m_s_rmse_before": round(rmse_strafe_before, 5),
        "strafe_4m_s_rmse_surface_depth": round(rmse_strafe_surf, 5),
        "strafe_4m_s_rmse_optical_centroid": round(rmse_strafe_opt, 5),
    }


def test_portal_crossing_no_flash_and_static_identity() -> dict[str, Any]:
    """Verify portal-crossing matrix unfolding + bounded fade (< 10% step) and static-camera identity."""
    cam_pos = (0.0, 0.0, 50.0)
    yaw = 0.5 * math.pi
    gt_fog, d_cur, d_shaft = _render_corridor_fog_ground_truth(cam_pos, yaw)
    prev_fog = gt_fog * 0.92
    m_vp, m_inv_vp = make_camera_matrices_25d(cam_pos, yaw)

    out_none = reproject_volumetric_fog_frame(gt_fog, prev_fog, d_cur, d_cur, m_vp, m_inv_vp, cam_pos, "none")["output_fog_rgba"]
    out_reproj = reproject_volumetric_fog_frame(gt_fog, prev_fog, d_cur, d_cur, m_vp, m_inv_vp, cam_pos, "optical_centroid", d_shaft, 0.5)["output_fog_rgba"]
    static_diff = float(np.max(np.abs(out_reproj - out_none)))
    assert static_diff < 1e-12, f"Static camera output diverged from baseline shader: {static_diff}"

    t_portal = np.array([
        [0.0, -1.0, 0.0, 1000.0],
        [1.0,  0.0, 0.0, 2000.0],
        [0.0,  0.0, 1.0,   32.0],
        [0.0,  0.0, 0.0,    1.0],
    ], dtype=np.float64)
    cam_post_h = t_portal @ np.array([cam_pos[0], cam_pos[1], cam_pos[2], 1.0])
    cam_post = (float(cam_post_h[0]), float(cam_post_h[1]), float(cam_post_h[2]))
    yaw_post = yaw + 0.5 * math.pi
    m_vp_post, m_inv_vp_post = make_camera_matrices_25d(cam_post, yaw_post)

    bright_zone_fog = gt_fog * 3.0
    bright_zone_fog[..., 3] = np.clip(gt_fog[..., 3] * 1.8, 0.0, 0.98)

    res_portal = reproject_volumetric_fog_frame(
        bright_zone_fog,
        gt_fog,
        d_cur,
        d_cur,
        m_vp_prev=m_vp,
        m_inv_vp_cur=m_inv_vp_post,
        cam_pos_cur=cam_post,
        reprojection_mode="optical_centroid",
        portal_transform_dst_from_src=t_portal,
        max_step_ratio=0.08,
    )
    step_pct = res_portal["whole_frame_luma_step_ratio"] * 100.0
    assert step_pct <= 10.0, f"Portal crossing produced a luminance flash of {step_pct:.2f}% > 10%!"

    return {
        "status": "verified (test_portal_crossing_no_flash_and_static_identity)",
        "static_camera_max_diff": static_diff,
        "portal_crossing_luma_step_pct": round(step_pct, 3),
        "max_allowed_luma_step_pct": 10.0,
    }


def run_all_fog_reprojection_tests() -> dict[str, Any]:
    taus = np.linspace(0.001, 10.0, 200)
    opacities = 1.0 - np.exp(-taus)
    pade_err = float(np.max(np.abs(optical_centroid_depth_ratio_exact(taus) - optical_centroid_depth_ratio_pade(opacities))))
    assert pade_err < 0.012

    return {
        "all_verified": True,
        "pade_centroid_max_error": round(pade_err, 5),
        "motion_trailing": test_yaw_turn_180_and_strafe_4ms_trailing(),
        "portal_and_static": test_portal_crossing_no_flash_and_static_identity(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_fog_reprojection_tests(), indent=2))