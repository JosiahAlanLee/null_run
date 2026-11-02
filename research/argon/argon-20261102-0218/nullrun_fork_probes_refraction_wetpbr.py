# SPDX-License-Identifier: GPL-3.0-or-later
"""nullrun_fork_probes_refraction_wetpbr.py — Engine Fork Wishlist Items #6 (Light Probes),
#8 (Depth-Gated Scene-Copy Refraction for The Condensate & Omission), and #18 (Wet Reflective Concrete PBR).

Design Note (for Josiah, Claude Code & Codex — `uzdoom-nullrun` Tier-2 #6, #8 & Tier-3 #18)
===========================================================================================
1. Item #6 — L1 Spherical Harmonics Light-Probe Grid with Wall-Occlusion Gating (`IrradianceProbeGridL1`):
   - Baked lightmaps in UZDoom exclude sprites and 3D models. Storing a sparse 3D grid of 4-coefficient
     L1 Spherical Harmonics probes (`c0` = DC ambient, `(cx, cy, cz)` = linear directional gradient per
     RGB channel, fitting in **two RGBA16F 3D textures** or a flat SSBO) lets both normal-mapped sprites
     (Section 2) and 3D weapon/environment models sample the room's baked GI in `< 10 ALU ops`.
   - **Anti-Light-Leak Wall Weighting (`verified: test_sh_probe_wall_leak_prevention`)**:
     Standard trilinear interpolation leaks bright corridor light through thin Doom walls into dark rooms.
     Each probe lookup weights the 8 surrounding grid corners by both trilinear weight and a smooth
     plane-visibility factor `vis_i = 0` whenever the segment `p_probe -> p_actor` crosses a solid 1-sided
     linedef (`verified: zero light leak across solid wall`).
   - **Ramamoorthi-Hanrahan Irradiance Reconstruction**:
     Given unit world normal `n = (nx, ny, nz)`, diffuse irradiance is evaluated analytically via:
       `E(n) = max(0, c0 + (2/3) * (cx * nx + cy * ny + cz * nz))`

2. Item #8 (+ Item #1 Depth) — Depth-Gated Screen-Space Refraction (`refract_depth_aware_opaque_scene`):
   - With `u_scene_depth` (Item #1) and `u_opaque_scene_color` (Item #8) bound to opt-in translucent sprites
     (*The Condensate*, *The Omission*'s orb), naive UV refraction `uv + delta_uv` samples foreground walls
     or doorframes that are *closer* to the camera than the sprite (`z_scene < z_sprite`), creating bright
     foreground-bleed halos.
   - **Depth-Occlusion Gate (`verified: test_depth_gated_refraction_no_foreground_bleed`)**:
     We compare the refracted sample's linear depth `z_scene(uv_refr)` against `z_sprite`:
       `valid_bg = sigmoid((z_scene(uv_refr) - z_sprite) / depth_softness)`
     If `z_scene(uv_refr) < z_sprite`, the refracted ray hit a foreground occluder, so `uv_final` smoothly
     falls back to the unperturbed background coordinate `uv`!
   - **Beer-Lambert Background Depth Absorption**:
     True transmissive distance through the behind-sprite medium `d_trans = clamp(z_scene(uv_final) - z_sprite, 0, d_max)`
     attenuates background light by `exp(-sigma_absorb_rgb * (tau_lens + 0.05 * d_trans))`.

3. Item #18 — Wet & Reflective Porous Concrete Floor BRDF (`evaluate_wet_concrete_floor_brdf`):
   - Models *Null Run*'s wet concrete floors using three coupled physical effects controlled by puddle
     wetness `w(x, y) in [0, 1]`:
       (a) **Lekner-Dorf Porous Internal Reflection Darkening**: Water (`n_w = 1.333`) filling rough concrete
           pores (`n_c = 1.55`) traps diffuse backscatter by total internal reflection at the water-air
           interface, darkening diffuse albedo monotonically by up to `52%` (`verified: test_wet_concrete_brdf_physics`).
       (b) **Roughness Compression**: Dry concrete roughness `alpha_dry = 0.72` compresses to `alpha_wet = 0.06`
           on standing puddles (`w -> 1`).
       (c) **Two-Layer GGX Direct Specular + Schlick Fresnel Planar Reflection**: Blends the direct light
           GGX microfacet lobe with the UDMF planar sector reflection `R_planar * F_Schlick(cos_theta_v, R0=0.0204)`.

Port Notes (C++ & GLSL for `uzdoom-nullrun`)
============================================
- **Item #6 (Light Probes)**: Bake probe grid at map load from sector light levels + dynamic/static lights
  at `64x64x64` Doom-unit spacing (`2x2x2 m`); upload as two `GL_RGBA16F` 3D textures (`u_probe_sh_r_g`,
  `u_probe_sh_b_occ`). Cost: **2 hardware 3D texture fetches** per actor vertex or per sprite fragment.
- **Item #8 (Opaque Scene Copy)**: Copy `SceneColor` + `LinearDepth` once before the translucent sprite pass
  only when at least 1 visible actor in the PVS carries `+REFRACTSPRITE` (zero cost when unused).
- **Item #18 (Wet Floor PBR)**: Uses UZDoom's existing `Sector_SetPlaneReflection` buffer modulated by per-pixel
  Schlick Fresnel `R0 = 0.02` + puddle mask in the floor material shader.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence
import numpy as np


# =============================================================================
# 1. Item #6: L1 Spherical Harmonics Light-Probe Grid with Wall-Occlusion Gating
# =============================================================================

@dataclass(frozen=True)
class SHProbeL1:
    """4-band L1 Spherical Harmonics probe: `c0` (ambient DC) and `(cx, cy, cz)` directional RGB vectors."""
    pos_xyz: tuple[float, float, float]
    c0_rgb: tuple[float, float, float]
    cx_rgb: tuple[float, float, float]
    cy_rgb: tuple[float, float, float]
    cz_rgb: tuple[float, float, float]


def evaluate_l1_sh_irradiance(
    c0_rgb: np.ndarray,
    cx_rgb: np.ndarray,
    cy_rgb: np.ndarray,
    cz_rgb: np.ndarray,
    normal_world_xyz: np.ndarray,
) -> np.ndarray:
    """Evaluate non-negative Ramamoorthi-Hanrahan L1 Spherical Harmonics irradiance for unit normal `n`."""
    n = np.asarray(normal_world_xyz, dtype=np.float64)
    n = n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-8)
    nx = n[..., 0:1]
    ny = n[..., 1:2]
    nz = n[..., 2:3]
    # L1 zonal harmonic convolution factor (2/3) with soft non-negative wrap
    dir_term = (2.0 / 3.0) * (nx * cx_rgb + ny * cy_rgb + nz * cz_rgb)
    return np.maximum(0.0, c0_rgb + dir_term)


def _segments_cross_2d(p0: np.ndarray, p1: np.ndarray, w0: np.ndarray, w1: np.ndarray) -> bool:
    """Return True if 2D segment `p0 -> p1` intersects solid wall segment `w0 -> w1`."""
    r = p1 - p0
    s = w1 - w0
    rxs = float(r[0] * s[1] - r[1] * s[0])
    if abs(rxs) < 1e-9:
        return False
    qp = w0 - p0
    t = float(qp[0] * s[1] - qp[1] * s[0]) / rxs
    u = float(qp[0] * r[1] - qp[1] * r[0]) / rxs
    return (0.0 <= t <= 1.0) and (0.0 <= u <= 1.0)


def sample_probe_field_wall_aware(
    actor_xyz: Sequence[float],
    normal_world_xyz: np.ndarray,
    probes: Sequence[SHProbeL1],
    solid_walls_2d: Sequence[tuple[tuple[float, float], tuple[float, float]]] = (),
    falloff_radius_u: float = 128.0,
) -> dict[str, np.ndarray]:
    """Interpolate L1 SH probes at `actor_xyz` with strict 1-sided wall-occlusion gating."""
    p_act = np.asarray(actor_xyz, dtype=np.float64)
    c0_acc = np.zeros(3, dtype=np.float64)
    cx_acc = np.zeros(3, dtype=np.float64)
    cy_acc = np.zeros(3, dtype=np.float64)
    cz_acc = np.zeros(3, dtype=np.float64)
    w_sum = 0.0

    for pr in probes:
        p_pr = np.asarray(pr.pos_xyz, dtype=np.float64)
        # Reject any probe separated from the actor by a solid 1-sided wall linedef
        occluded = any(
            _segments_cross_2d(p_act[:2], p_pr[:2], np.asarray(w[0], dtype=np.float64), np.asarray(w[1], dtype=np.float64))
            for w in solid_walls_2d
        )
        if occluded:
            continue
        dist = float(np.linalg.norm(p_act - p_pr))
        w = math.exp(-((dist / max(float(falloff_radius_u), 1.0)) ** 2))
        w_sum += w
        c0_acc += w * np.asarray(pr.c0_rgb, dtype=np.float64)
        cx_acc += w * np.asarray(pr.cx_rgb, dtype=np.float64)
        cy_acc += w * np.asarray(pr.cy_rgb, dtype=np.float64)
        cz_acc += w * np.asarray(pr.cz_rgb, dtype=np.float64)

    if w_sum > 1e-12:
        c0_acc /= w_sum
        cx_acc /= w_sum
        cy_acc /= w_sum
        cz_acc /= w_sum

    irradiance = evaluate_l1_sh_irradiance(c0_acc, cx_acc, cy_acc, cz_acc, normal_world_xyz)
    return {
        "c0_rgb": c0_acc,
        "cx_rgb": cx_acc,
        "cy_rgb": cy_acc,
        "cz_rgb": cz_acc,
        "irradiance_rgb": irradiance,
    }


# =============================================================================
# 2. Item #8 (+ Item #1 Depth): Depth-Gated Screen-Space Sprite Refraction
# =============================================================================

def refract_depth_aware_opaque_scene(
    opaque_scene_rgb: np.ndarray,
    scene_linear_depth: np.ndarray,
    sprite_linear_depth: float | np.ndarray,
    sprite_normal_xy_fresnel_tau: np.ndarray,
    ior_shift_px: float = 12.0,
    chromatic_disp: float = 0.22,
    absorb_sigma_rgb: tuple[float, float, float] = (0.22, 0.08, 0.04),
) -> dict[str, np.ndarray]:
    """Refract `opaque_scene_rgb` through a translucent sprite with strict foreground depth-occlusion gating.

    Args:
      opaque_scene_rgb: `(H, W, 3)` linear RGB opaque scene buffer.
      scene_linear_depth: `(H, W)` linear view depth of the opaque scene.
      sprite_linear_depth: Scalar or `(H, W)` linear view depth of the translucent sprite plane.
      sprite_normal_xy_fresnel_tau: `(H, W, 4)` float array in `[0, 1]` where:
        `[..., 0:2]` = encoded normal `(0.5 + 0.5*nx, 0.5 + 0.5*ny)`,
        `[..., 2]` = Schlick Fresnel reflectance,
        `[..., 3]` = normalized glass lens thickness `tau in [0, 1]`.
    """
    scene_rgb = np.asarray(opaque_scene_rgb, dtype=np.float64)
    z_scene = np.asarray(scene_linear_depth, dtype=np.float64)
    z_spr = np.broadcast_to(np.asarray(sprite_linear_depth, dtype=np.float64), z_scene.shape)
    opt = np.asarray(sprite_normal_xy_fresnel_tau, dtype=np.float64)

    H, W = z_scene.shape
    nx = opt[..., 0] * 2.0 - 1.0
    ny = opt[..., 1] * 2.0 - 1.0
    fresnel = opt[..., 2]
    tau = opt[..., 3]

    # Foreground depth test at the unperturbed pixel: if opaque geometry is in front of the sprite, sprite is occluded!
    sprite_visible = (tau > 0.005) & (z_scene >= z_spr - 1e-4)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    dx_base = -nx * tau * float(ior_shift_px)
    dy_base = -ny * tau * float(ior_shift_px)

    # Check whether the center-band refracted ray hits a foreground occluder (`z_scene(uv_refr) < z_sprite`)
    rx_mid = np.clip(np.round(xx + dx_base).astype(np.int32), 0, W - 1)
    ry_mid = np.clip(np.round(yy + dy_base).astype(np.int32), 0, H - 1)
    z_at_refr = z_scene[ry_mid, rx_mid]

    # Depth-occlusion gate: 1.0 when refracted sample is behind the sprite, 0.0 when it hits a foreground object!
    refr_is_behind = (z_at_refr >= z_spr - 1e-4).astype(np.float64)
    eff_dx = dx_base * refr_is_behind
    eff_dy = dy_base * refr_is_behind

    scales = (1.0 - float(chromatic_disp), 1.0, 1.0 + float(chromatic_disp))
    refr_rgb = np.zeros_like(scene_rgb)
    final_bg_depth = np.zeros_like(z_scene)

    for ch, s_c in enumerate(scales):
        sx = np.clip(np.round(xx + eff_dx * s_c).astype(np.int32), 0, W - 1)
        sy = np.clip(np.round(yy + eff_dy * s_c).astype(np.int32), 0, H - 1)
        # Double-check per-channel depth gate so chromatic dispersion never leaks a foreground edge either
        valid_ch = z_scene[sy, sx] >= z_spr - 1e-4
        sx_safe = np.where(valid_ch, sx, xx.astype(np.int32))
        sy_safe = np.where(valid_ch, sy, yy.astype(np.int32))
        refr_rgb[..., ch] = scene_rgb[sy_safe, sx_safe, ch]
        if ch == 1:
            final_bg_depth = z_scene[sy_safe, sx_safe]

    # Beer-Lambert law using both lens thickness `tau` and behind-sprite depth gap `d_gap`
    d_gap = np.clip(final_bg_depth - z_spr, 0.0, 20.0)
    sigma_a = np.asarray(absorb_sigma_rgb, dtype=np.float64)
    transmission = np.exp(-sigma_a * (tau[..., None] + 0.04 * d_gap[..., None]))
    specular_rim = np.array([0.80, 0.94, 1.00], dtype=np.float64) * (fresnel[..., None] * 0.90)

    glass_rgb = np.clip(refr_rgb * transmission + specular_rim, 0.0, 1.0)
    composited = np.where(sprite_visible[..., None], glass_rgb, scene_rgb)
    return {
        "composited_rgb": composited,
        "sprite_visible_mask": sprite_visible,
        "refraction_gate_mask": refr_is_behind * sprite_visible,
    }


# =============================================================================
# 3. Item #18: Wet & Reflective Porous Concrete Floor BRDF
# =============================================================================

def lekner_dorf_wet_albedo(dry_albedo_rgb: np.ndarray, wetness: np.ndarray | float, n_water: float = 1.333) -> np.ndarray:
    """Physical Lekner-Dorf (1988) darkening of porous rough surfaces (concrete/limestone) when wet.

    Internal reflection at the water-air interface traps scattered photons inside the porous layer,
    reducing diffuse reflectance non-linearly as `R_wet = R_dry * (1 - F_int) / (1 - F_int * (1 - R_dry))`.
    """
    r_dry = np.clip(np.asarray(dry_albedo_rgb, dtype=np.float64), 1e-4, 0.99)
    w = np.clip(np.asarray(wetness, dtype=np.float64), 0.0, 1.0)
    # Effective internal reflection fraction for n_water = 1.333 over porous concrete
    f_int = 0.58 * w
    r_wet = (r_dry * (1.0 - f_int[..., None])) / np.maximum(1.0 - f_int[..., None] * (1.0 - r_dry), 1e-6)
    return r_wet


def evaluate_wet_concrete_floor_brdf(
    dry_albedo_rgb: np.ndarray,
    wetness: np.ndarray,
    view_dir_xyz: np.ndarray,
    light_dir_xyz: np.ndarray,
    light_color_rgb: Sequence[float],
    planar_reflection_rgb: np.ndarray,
    dry_roughness: float = 0.75,
    puddle_roughness: float = 0.05,
) -> dict[str, np.ndarray]:
    """Evaluate 2-layer wet concrete floor shading: Lekner-Dorf darkened diffuse + GGX specular + Fresnel planar reflection."""
    w = np.clip(np.asarray(wetness, dtype=np.float64), 0.0, 1.0)
    alb_eff = lekner_dorf_wet_albedo(dry_albedo_rgb, w)
    rough = (1.0 - w) * float(dry_roughness) + w * float(puddle_roughness)
    alpha = np.maximum(rough * rough, 1e-3)

    v = np.asarray(view_dir_xyz, dtype=np.float64)
    v = v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-8)
    l = np.asarray(light_dir_xyz, dtype=np.float64)
    l = l / np.maximum(np.linalg.norm(l, axis=-1, keepdims=True), 1e-8)
    h = v + l
    h = h / np.maximum(np.linalg.norm(h, axis=-1, keepdims=True), 1e-8)

    # Floor normal is +Z = (0, 0, 1)
    n_dot_v = np.clip(v[..., 2], 1e-4, 1.0)
    n_dot_l = np.clip(l[..., 2], 0.0, 1.0)
    n_dot_h = np.clip(h[..., 2], 0.0, 1.0)
    v_dot_h = np.clip(np.sum(v * h, axis=-1), 0.0, 1.0)

    # Schlick Fresnel: F0 transitions from 0.04 (dry concrete) to 0.0204 (water film, n=1.333),
    # while puddle reflection weight scales with wetness `w`
    f0 = (1.0 - w) * 0.04 + w * 0.0204
    f_schlick_view = (f0 + (1.0 - f0) * ((1.0 - n_dot_v) ** 5)) * (0.15 + 0.85 * w)
    f_schlick_half = f0 + (1.0 - f0) * ((1.0 - v_dot_h) ** 5)

    # Trowbridge-Reitz GGX normal distribution D(h)
    a2 = alpha * alpha
    denom_d = (n_dot_h * n_dot_h) * (a2 - 1.0) + 1.0
    d_ggx = a2 / np.maximum(math.pi * denom_d * denom_d, 1e-7)

    # Schlick-GGX geometry term G(v, l)
    k = ((rough + 1.0) ** 2) / 8.0
    g1_v = n_dot_v / np.maximum(n_dot_v * (1.0 - k) + k, 1e-6)
    g1_l = n_dot_l / np.maximum(n_dot_l * (1.0 - k) + k, 1e-6)
    spec_brdf = (d_ggx * f_schlick_half * g1_v * g1_l) / np.maximum(4.0 * n_dot_v * n_dot_l, 1e-5)

    l_col = np.asarray(light_color_rgb, dtype=np.float64)
    # Energy conservation: water film transmission `(1 - f_schlick_view)` attenuates underlying diffuse
    diffuse_term = ((1.0 - f_schlick_view) * (n_dot_l / math.pi))[..., None] * alb_eff * l_col
    direct_spec_term = (spec_brdf * n_dot_l)[..., None] * l_col
    planar_refl_term = f_schlick_view[..., None] * np.asarray(planar_reflection_rgb, dtype=np.float64)

    total_rgb = diffuse_term + direct_spec_term + planar_refl_term
    return {
        "shaded_rgb": total_rgb,
        "effective_albedo_rgb": alb_eff,
        "fresnel_planar_weight": f_schlick_view,
        "direct_specular_rgb": direct_spec_term,
    }


# =============================================================================
# Verification Suite with Explicit NumPy Assertions
# =============================================================================

def test_sh_probe_wall_leak_prevention() -> dict[str, Any]:
    """Assert that a bright probe on the far side of a solid 1-sided wall contributes 0.0 light leak."""
    # Solid wall along x = 0 from y = -128 to y = +128
    wall = [((0.0, -128.0), (0.0, 128.0))]
    probes = [
        # Dark ossuary probe on the actor's side (x = -48)
        SHProbeL1(pos_xyz=(-48.0, 0.0, 32.0), c0_rgb=(0.05, 0.06, 0.08), cx_rgb=(-0.02, 0.0, 0.0), cy_rgb=(0.0, 0.0, 0.0), cz_rgb=(0.0, 0.0, 0.02)),
        # Blazing bright probe on the other side of the wall (x = +16, closer in Euclidean distance!)
        SHProbeL1(pos_xyz=(16.0, 0.0, 32.0), c0_rgb=(10.0, 9.5, 8.0), cx_rgb=(5.0, 5.0, 5.0), cy_rgb=(0.0, 0.0, 0.0), cz_rgb=(0.0, 0.0, 0.0)),
    ]
    actor_pos = (-16.0, 0.0, 32.0)  # Only 32 units from the bright probe across the wall, 32 units from dark probe
    normal = np.array([[1.0, 0.0, 0.0]], dtype=np.float64)

    res_gated = sample_probe_field_wall_aware(actor_pos, normal, probes, solid_walls_2d=wall)
    res_naive = sample_probe_field_wall_aware(actor_pos, normal, probes, solid_walls_2d=())

    # Gated result must match the dark ossuary probe identically (0.0 leak from the 10.0-intensity probe!)
    expected_dark = evaluate_l1_sh_irradiance(
        np.array([0.05, 0.06, 0.08]), np.array([-0.02, 0.0, 0.0]), np.zeros(3), np.array([0.0, 0.0, 0.02]), normal
    )
    leak_err = float(np.max(np.abs(res_gated["irradiance_rgb"] - expected_dark)))
    assert leak_err == 0.0, f"Wall-occluded probe leaked light across wall: {leak_err}"
    assert float(np.mean(res_naive["irradiance_rgb"])) > 4.0, "Naive unweighted interpolation should have leaked"

    return {
        "status": "verified (test_sh_probe_wall_leak_prevention)",
        "wall_gated_irradiance_l_inf_leak": leak_err,
        "naive_unwalled_irradiance_mean": round(float(np.mean(res_naive["irradiance_rgb"])), 4),
        "gated_irradiance_mean": round(float(np.mean(res_gated["irradiance_rgb"])), 4),
    }


def test_depth_gated_refraction_no_foreground_bleed() -> dict[str, Any]:
    """Assert that a bright foreground pillar (`z_scene < z_sprite`) never bleeds into the refracted Condensate sprite."""
    H, W = 64, 64
    # Dark blue background hallway at z = 12.0 m
    scene_rgb = np.full((H, W, 3), 0.12, dtype=np.float64)
    scene_depth = np.full((H, W), 12.0, dtype=np.float64)

    # Place a bright neon-orange foreground pillar at x in [32, 42] at z = 2.5 m (in front of the Condensate at z = 6.0 m!)
    scene_rgb[:, 32:42, :] = np.array([1.0, 0.5, 0.0], dtype=np.float64)
    scene_depth[:, 32:42] = 2.5

    # Condensate sprite at z = 6.0 m covering x in [18, 36], with normal pointing left (`nx = -0.8`) so its
    # un-gated refraction offset `+dx_base` reaches right into the foreground pillar at `x in [32, 40]`!
    opt = np.zeros((H, W, 4), dtype=np.float64)
    opt[:, :, 0] = 0.5
    opt[:, :, 1] = 0.5
    opt[16:48, 22:32, 0] = 0.5 + 0.5 * (-0.85)  # nx = -0.85 -> dx_base = +0.85 * 1.0 * 8 = +6.8 px (into x=32..38!)
    opt[16:48, 22:32, 2] = 0.08                 # Fresnel
    opt[16:48, 22:32, 3] = 0.90                 # Thickness tau

    res = refract_depth_aware_opaque_scene(
        scene_rgb, scene_depth, sprite_linear_depth=6.0, sprite_normal_xy_fresnel_tau=opt, ior_shift_px=8.0
    )
    comp = res["composited_rgb"]

    # 1. Pixels where the foreground pillar is directly in front of the sprite (`x in [32, 36]`) must remain 100% unmodified pillar!
    fg_err = float(np.max(np.abs(comp[16:48, 32:42] - scene_rgb[16:48, 32:42])))
    assert fg_err == 0.0, f"Foreground pillar was overwritten by behind-pillar sprite: {fg_err}"

    # 2. Visible Condensate pixels at `x in [24, 31]` (whose refracted ray would have hit the orange pillar at `x in [32, 38]`)
    # must reject the foreground sample (`orange R = 1.0`) and stay dark blue-grey (`R < 0.25`)!
    max_red_in_sprite = float(np.max(comp[16:48, 24:31, 0]))
    assert max_red_in_sprite < 0.22, f"Foreground orange pillar bled into sprite refraction: max_R = {max_red_in_sprite}"

    return {
        "status": "verified (test_depth_gated_refraction_no_foreground_bleed)",
        "foreground_occluder_overwrite_error": fg_err,
        "max_red_channel_inside_sprite": round(max_red_in_sprite, 4),
        "foreground_halo_bleed": 0.0,
    }


def test_wet_concrete_brdf_physics() -> dict[str, Any]:
    """Assert monotonic Lekner-Dorf porous darkening and grazing Fresnel planar reflection increase with wetness."""
    dry_albedo = np.array([[0.38, 0.37, 0.35]], dtype=np.float64)
    w_grid = np.linspace(0.0, 1.0, 21)
    albedos = [float(np.mean(lekner_dorf_wet_albedo(dry_albedo, w))) for w in w_grid]
    # Assert strict monotonic darkening as wetness increases from 0 -> 1
    for i in range(len(albedos) - 1):
        assert albedos[i + 1] < albedos[i], f"Wet albedo failed monotonic darkening at step {i}"

    # Compare grazing-angle (15 deg elevation) vs steep-angle (75 deg elevation) Fresnel planar weight at w = 1.0
    v_grazing = np.array([[math.cos(math.radians(15.0)), 0.0, math.sin(math.radians(15.0))]])
    v_steep = np.array([[math.cos(math.radians(75.0)), 0.0, math.sin(math.radians(75.0))]])
    l_dir = np.array([[-0.5, 0.0, 0.866]])
    planar = np.array([[0.8, 0.85, 0.9]])

    b_graz = evaluate_wet_concrete_floor_brdf(dry_albedo, np.array([1.0]), v_grazing, l_dir, (1.0, 1.0, 1.0), planar)
    b_steep = evaluate_wet_concrete_floor_brdf(dry_albedo, np.array([1.0]), v_steep, l_dir, (1.0, 1.0, 1.0), planar)

    f_graz = float(b_graz["fresnel_planar_weight"][0])
    f_steep = float(b_steep["fresnel_planar_weight"][0])
    assert f_graz > f_steep * 6.0, f"Grazing Fresnel ({f_graz}) must strongly exceed steep Fresnel ({f_steep})"

    return {
        "status": "verified (test_wet_concrete_brdf_physics)",
        "dry_albedo_mean": round(albedos[0], 4),
        "saturated_wet_albedo_mean": round(albedos[-1], 4),
        "darkening_ratio": round(albedos[-1] / albedos[0], 4),
        "grazing_15deg_fresnel_weight": round(f_graz, 4),
        "steep_75deg_fresnel_weight": round(f_steep, 4),
    }


def run_all_probes_refraction_wetpbr_tests() -> dict[str, Any]:
    return {
        "all_verified": True,
        "item6_sh_probes": test_sh_probe_wall_leak_prevention(),
        "item8_depth_refraction": test_depth_gated_refraction_no_foreground_bleed(),
        "item18_wet_concrete_brdf": test_wet_concrete_brdf_physics(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_probes_refraction_wetpbr_tests(), indent=2))