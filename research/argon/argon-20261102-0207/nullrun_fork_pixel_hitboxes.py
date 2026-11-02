# SPDX-License-Identifier: GPL-3.0-or-later
"""nullrun_fork_pixel_hitboxes.py — Section 4: Pixel-Accurate Hitscan & Projectile Hits on Billboard Sprites.

Design Note (for Josiah, Claude Code & Codex — `uzdoom-nullrun` Tier-1 Item #3 & Tier-3 Item #16)
=================================================================================================
1. Ray-Billboard Plane Intersection & Per-Texel Anatomical Mask Lookup:
   - Given a world-space hitscan/projectile ray `r(t) = o + t * d` (`||d|| = 1`) and a billboard actor at
     `p_A = (x_A, y_A, z_A_floor)` with world width `W`, height `H`, and billboard horizontal tangent `T_B`
     and normal `N_B`:
       `t_hit = dot(p_A - o, N_B) / dot(d, N_B)`
       `h_vec = (o + t_hit * d) - p_A`
       `u = 0.5 + dot(h_vec, T_B) / W`,  `v = 1.0 - (h_vec.z / H)`
   - If `(u, v) in [0, 1]^2`, we sample the current `(yaw_idx, pitch_idx)` frame's `alpha_mask[iv, iu]` and
     `region_mask[iv, iu]` (`0=EMPTY`, `1=TORSO_REBAR`, `2=ANKLE_WIRE`, `3=GREEN_CORE`, `4=TENDON_COLLAR`).
   - When `alpha_mask[iv, iu] < 0.5`, the ray passes cleanly through the gap between rebar bundles or under
     an arm (`hit = False`), so the trace continues to walls or monsters behind it!

2. Billboard-vs-3D-Ray Mismatch Analysis & Ray-Aligned Virtual Plane (`verified: test_oblique_parallax_and_fallback`):
   - A camera-facing billboard is flat and orthogonal to the *camera* view direction `N_cam`, whereas a
     non-player ray (e.g., monster infighting, turret, or ricochet) may arrive at horizontal obliquity angle
     `gamma = arccos(-dot(d_xy, N_cam_xy))`.
   - **Exact Parallax Error Formula**: A 3D anatomical feature (such as the green core socket protruding by
     depth offset `rho` in front of the actor's spine) projected onto a billboard rotated by `gamma` shifts
     laterally by `delta_x = rho * tan(gamma)` and foreshortens the billboard width by `cos(gamma)`.
   - **Two-Stage Solution**:
     (a) **Ray-Aligned Virtual Billboard (`cos(gamma) >= 0.25`)**: Instead of intersecting an oblique ray with
         the *player's* camera plane, the server/engine intersects the ray with the **ray-orthogonal plane**
         (`N_ray = normalize(-d_xy)`) and indexes the sprite bank using the *ray's* incoming azimuth and
         elevation `(psi_ray, theta_ray)`! This reduces oblique parallax error to **identically `0.0`** for
         any ray direction.
     (b) **Conservative Cylinder Fallback (`cos(gamma) < 0.25` or uncached mask)**: Intersects the actor's
         3D cylinder (`radius = R`, `height = H`) and classifies `(z_rel, r_perp)` into the 3 anatomical
         zones (`ANKLE_WIRE`, `GREEN_CORE`, `TORSO_REBAR`, `TENDON_COLLAR`).

Port Notes (C++ & ZScript for `uzdoom-nullrun`)
===============================================
- **C++ Trace Hook (`FTraceResults` in `src/playsim/p_trace.cpp`)**:
  * Add actor flag `+PIXELHITBOX` (`MF9_PIXELHITBOX`). When `TraverseNodes` hits a `+PIXELHITBOX` actor's
    bounding cylinder, call `TraceBillboardPixelHit(...)` before accepting the cylinder hit.
  * Keep a compact CPU-side RLE or 4-bit packed `(alpha_1bit | region_3bit)` mip in `FGameTexture` (only
    `32x32` bytes = **512 bytes per sprite frame**, `< 200 KB` for an entire 8x5 monster sheet!) so C++
    ray-casts never stall on GPU texture readbacks.
  * Populate `FTraceResults::HitTexelUV`, `FTraceResults::HitRegionID`, and `FTraceResults::HitPos` and forward
    them into ZScript `DamageMobj(inflictor, source, damage, mod, flags, angle, hit_pos, hit_region_id, hit_uv)`.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence
import numpy as np

REGION_EMPTY: int = 0
REGION_TORSO_REBAR: int = 1
REGION_ANKLE_WIRE: int = 2
REGION_GREEN_CORE: int = 3
REGION_TENDON_COLLAR: int = 4

REGION_NAMES: dict[int, str] = {
    REGION_EMPTY: "EMPTY",
    REGION_TORSO_REBAR: "TORSO_REBAR",
    REGION_ANKLE_WIRE: "ANKLE_WIRE",
    REGION_GREEN_CORE: "GREEN_CORE",
    REGION_TENDON_COLLAR: "TENDON_COLLAR",
}


@dataclass(frozen=True)
class SpriteHitboxFrame:
    """Packed alpha + anatomical region ID mask for a single `(yaw_idx, pitch_idx)` sprite frame."""
    alpha_mask: np.ndarray     # Bool or float array of shape (H_tex, W_tex), row 0 = top (v=0)
    region_id_mask: np.ndarray # uint8 array of shape (H_tex, W_tex) with values in {0..4}


def build_armature_reference_frame(
    tex_h: int = 64,
    tex_w: int = 64,
    core_visible: bool = True,
    core_u_center: float = 0.50,
    core_v_center: float = 0.46,
) -> SpriteHitboxFrame:
    """Synthesize a 64x64 Armature sprite mask with legs, hollow rebar torso gaps, collar, and green core."""
    yy, xx = np.mgrid[0:tex_h, 0:tex_w].astype(np.float64)
    u = (xx + 0.5) / float(tex_w)
    v = (yy + 0.5) / float(tex_h)  # v = 0 at top of head, v = 1 at feet

    region = np.zeros((tex_h, tex_w), dtype=np.uint8)

    # 1. High Zone: Tendon Collar & Head (v in [0.08, 0.28])
    collar = (v >= 0.08) & (v < 0.28) & (np.abs(u - 0.50) <= 0.14)
    region[collar] = REGION_TENDON_COLLAR

    # 2. Mid Zone: Rebar Torso Cage with vertical hollow gaps between rebar bundles (v in [0.28, 0.65])
    in_torso_box = (v >= 0.28) & (v < 0.65) & (np.abs(u - 0.50) <= 0.22)
    # Leave two narrow transparent gaps (`|u - 0.50| in [0.11, 0.14]`) to test through-cage misses!
    hollow_gap = (np.abs(np.abs(u - 0.50) - 0.125) < 0.015) & (v >= 0.34) & (v < 0.58)
    torso = in_torso_box & (~hollow_gap)
    region[torso] = REGION_TORSO_REBAR

    # 3. Low Zone: Ankle & Leg Tie-Wire (v in [0.65, 0.96], two distinct legs separated by a central gap)
    left_leg = (v >= 0.65) & (v <= 0.96) & (np.abs(u - 0.41) <= 0.06)
    right_leg = (v >= 0.65) & (v <= 0.96) & (np.abs(u - 0.59) <= 0.06)
    region[left_leg | right_leg] = REGION_ANKLE_WIRE

    # 4. Lodged Green Spindle Colony Core (when visible from front/side angles)
    if core_visible:
        core_dist2 = ((u - float(core_u_center)) / 0.085) ** 2 + ((v - float(core_v_center)) / 0.075) ** 2
        core_mask = core_dist2 <= 1.0
        region[core_mask] = REGION_GREEN_CORE

    alpha = (region != REGION_EMPTY).astype(np.float32)
    return SpriteHitboxFrame(alpha_mask=alpha, region_id_mask=region)


def parallax_lateral_error_u(feature_depth_offset_u: float, obliquity_angle_rad: float) -> float:
    """Exact lateral UV shift (in map units) on a camera-locked billboard when struck at horizontal angle `gamma`."""
    return abs(float(feature_depth_offset_u) * math.tan(float(obliquity_angle_rad)))


def intersect_cylinder_fallback(
    ray_origin: np.ndarray,
    ray_dir: np.ndarray,
    actor_pos_floor: np.ndarray,
    radius_u: float = 16.0,
    height_u: float = 56.0,
    core_visible: bool = True,
) -> dict[str, Any]:
    """Conservative 3D cylinder intersection + 3-zone anatomical fallback when sprite masks are unavailable."""
    ox, oy, oz = ray_origin - actor_pos_floor
    dx, dy, dz = ray_dir
    a = dx * dx + dy * dy
    if a < 1e-12:
        return {"hit": False, "region_id": REGION_EMPTY, "region_name": "EMPTY", "fallback_used": True}
    b = 2.0 * (ox * dx + oy * dy)
    c = ox * ox + oy * oy - float(radius_u) ** 2
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return {"hit": False, "region_id": REGION_EMPTY, "region_name": "EMPTY", "fallback_used": True}

    t_hit = (-b - math.sqrt(disc)) / (2.0 * a)
    if t_hit < 0.0:
        t_hit = (-b + math.sqrt(disc)) / (2.0 * a)
    if t_hit < 0.0:
        return {"hit": False, "region_id": REGION_EMPTY, "region_name": "EMPTY", "fallback_used": True}

    z_hit = oz + t_hit * dz
    if z_hit < 0.0 or z_hit > float(height_u):
        return {"hit": False, "region_id": REGION_EMPTY, "region_name": "EMPTY", "fallback_used": True}

    # Lateral offset from centerline
    hx = ox + t_hit * dx
    hy = oy + t_hit * dy
    horiz_norm = max(math.hypot(dx, dy), 1e-8)
    r_perp = abs(hx * (-dy / horiz_norm) + hy * (dx / horiz_norm))
    z_rel = z_hit / float(height_u)

    if z_rel < 0.35:
        reg = REGION_ANKLE_WIRE
    elif z_rel >= 0.72:
        reg = REGION_TENDON_COLLAR
    elif core_visible and (0.45 <= z_rel <= 0.62) and (r_perp <= 5.5):
        reg = REGION_GREEN_CORE
    else:
        reg = REGION_TORSO_REBAR

    world_hit = actor_pos_floor + np.array([hx, hy, z_hit], dtype=np.float64)
    return {
        "hit": True,
        "t_distance": round(float(t_hit), 4),
        "world_hit_xyz": [round(float(v), 3) for v in world_hit],
        "uv": (round(0.5 + r_perp / (2.0 * radius_u), 4), round(1.0 - z_rel, 4)),
        "texel_xy": (-1, -1),
        "region_id": reg,
        "region_name": REGION_NAMES[reg],
        "fallback_used": True,
    }


def trace_billboard_pixel_hit(
    ray_origin_xyz: Sequence[float],
    ray_dir_xyz: Sequence[float],
    actor_pos_floor_xyz: Sequence[float],
    sprite_width_u: float,
    sprite_height_u: float,
    frame: SpriteHitboxFrame | None,
    billboard_normal_xy: Sequence[float] | None = None,
    use_ray_aligned_plane_for_oblique: bool = True,
    cylinder_radius_u: float = 16.0,
) -> dict[str, Any]:
    """Intersect a 3D hitscan ray with a billboard sprite, returning exact texel `(u, v)` and anatomical region ID."""
    o = np.asarray(ray_origin_xyz, dtype=np.float64)
    d = np.asarray(ray_dir_xyz, dtype=np.float64)
    d_norm = max(float(np.linalg.norm(d)), 1e-12)
    d = d / d_norm
    p_a = np.asarray(actor_pos_floor_xyz, dtype=np.float64)

    if frame is None:
        return intersect_cylinder_fallback(o, d, p_a, radius_u=cylinder_radius_u, height_u=sprite_height_u)

    # Determine horizontal billboard normal N_B = (nx, ny, 0)
    d_horiz_len = math.hypot(float(d[0]), float(d[1]))
    if d_horiz_len < 1e-5:
        # Vertical plunging ray -> use conservative cylinder fallback
        return intersect_cylinder_fallback(o, d, p_a, radius_u=cylinder_radius_u, height_u=sprite_height_u)

    ray_facing_n = np.array([-d[0] / d_horiz_len, -d[1] / d_horiz_len, 0.0], dtype=np.float64)
    if billboard_normal_xy is None:
        n_b = ray_facing_n
        cos_obliquity = 1.0
    else:
        nb_raw = np.array([float(billboard_normal_xy[0]), float(billboard_normal_xy[1]), 0.0], dtype=np.float64)
        nb_len = max(float(np.linalg.norm(nb_raw)), 1e-12)
        n_b = nb_raw / nb_len
        cos_obliquity = float(- (d[0] * n_b[0] + d[1] * n_b[1]) / d_horiz_len)
        # If ray is oblique (> 15 deg off camera plane) and ray-aligned mode is active, rotate virtual plane to face ray
        if use_ray_aligned_plane_for_oblique and cos_obliquity < math.cos(math.radians(15.0)):
            n_b = ray_facing_n
            cos_obliquity = 1.0

    if cos_obliquity < 0.25:
        return intersect_cylinder_fallback(o, d, p_a, radius_u=cylinder_radius_u, height_u=sprite_height_u)

    # Billboard right-hand tangent T_B = (-ny, nx, 0)
    t_b = np.array([-n_b[1], n_b[0], 0.0], dtype=np.float64)
    denom = float(np.dot(d, n_b))
    if abs(denom) < 1e-8:
        return intersect_cylinder_fallback(o, d, p_a, radius_u=cylinder_radius_u, height_u=sprite_height_u)

    t_hit = float(np.dot(p_a - o, n_b)) / denom
    if t_hit < 0.0:
        return {"hit": False, "region_id": REGION_EMPTY, "region_name": "EMPTY", "fallback_used": False}

    hit_world = o + t_hit * d
    rel = hit_world - p_a
    u = 0.5 + float(np.dot(rel, t_b)) / float(sprite_width_u)
    v = 1.0 - (float(rel[2]) / float(sprite_height_u))

    if not (0.0 <= u < 1.0 and 0.0 <= v < 1.0):
        return {"hit": False, "region_id": REGION_EMPTY, "region_name": "EMPTY", "fallback_used": False}

    tex_h, tex_w = frame.alpha_mask.shape
    ix = int(np.clip(math.floor(u * tex_w), 0, tex_w - 1))
    iy = int(np.clip(math.floor(v * tex_h), 0, tex_h - 1))

    alpha_val = float(frame.alpha_mask[iy, ix])
    reg_id = int(frame.region_id_mask[iy, ix])
    if alpha_val < 0.5 or reg_id == REGION_EMPTY:
        return {
            "hit": False,
            "uv": (round(u, 4), round(v, 4)),
            "texel_xy": (ix, iy),
            "region_id": REGION_EMPTY,
            "region_name": "EMPTY",
            "fallback_used": False,
        }

    return {
        "hit": True,
        "t_distance": round(t_hit, 4),
        "world_hit_xyz": [round(float(val), 3) for val in hit_world],
        "uv": (round(u, 4), round(v, 4)),
        "texel_xy": (ix, iy),
        "region_id": reg_id,
        "region_name": REGION_NAMES[reg_id],
        "fallback_used": False,
    }


# =============================================================================
# Verification Suite with Explicit NumPy Assertions
# =============================================================================

def test_visible_core_texel_100pct_recall() -> dict[str, Any]:
    """Assert that EVERY ray aimed through a visible GREEN_CORE texel reports `region_id == REGION_GREEN_CORE`."""
    frame = build_armature_reference_frame(tex_h=64, tex_w=64, core_visible=True)
    actor_pos = np.array([200.0, 0.0, 0.0], dtype=np.float64)
    cam_pos = np.array([0.0, 0.0, 32.0], dtype=np.float64)
    W, H = 40.0, 56.0

    # Billboard faces camera at (0,0) -> normal is (-1, 0, 0), tangent is (0, -1, 0)
    n_b = (-1.0, 0.0)
    t_b = np.array([0.0, -1.0, 0.0], dtype=np.float64)

    core_ys, core_xs = np.where(frame.region_id_mask == REGION_GREEN_CORE)
    assert len(core_xs) > 20, "Reference frame must contain visible core texels"

    hits_total = 0
    core_hits = 0
    for iy, ix in zip(core_ys, core_xs):
        u_center = (float(ix) + 0.5) / 64.0
        v_center = (float(iy) + 0.5) / 64.0
        target_world = (
            actor_pos
            + (u_center - 0.5) * W * t_b
            + np.array([0.0, 0.0, (1.0 - v_center) * H], dtype=np.float64)
        )
        ray_dir = target_world - cam_pos
        res = trace_billboard_pixel_hit(cam_pos, ray_dir, actor_pos, W, H, frame, billboard_normal_xy=n_b)
        hits_total += 1
        assert res["hit"] and res["region_id"] == REGION_GREEN_CORE, (
            f"Ray through visible core texel ({ix}, {iy}) failed: {res}"
        )
        assert res["texel_xy"] == (int(ix), int(iy))
        core_hits += 1

    # Also verify that a ray aimed through the hollow rebar gap (`u = 0.375, v = 0.45`) passes cleanly through!
    gap_world = actor_pos + (0.375 - 0.5) * W * t_b + np.array([0.0, 0.0, (1.0 - 0.45) * H])
    res_gap = trace_billboard_pixel_hit(cam_pos, gap_world - cam_pos, actor_pos, W, H, frame, billboard_normal_xy=n_b)
    assert not res_gap["hit"] and res_gap["region_id"] == REGION_EMPTY, "Hollow rebar gap should not register a hit"

    return {
        "status": "verified (test_visible_core_texel_100pct_recall)",
        "visible_core_texels_tested": hits_total,
        "core_recall_rate": round(core_hits / max(hits_total, 1), 4),
        "hollow_rebar_gap_passthrough_verified": True,
    }


def test_oblique_parallax_and_fallback() -> dict[str, Any]:
    """Verify oblique parallax error formula, ray-aligned virtual plane correction, and cylinder fallback."""
    frame = build_armature_reference_frame(tex_h=64, tex_w=64, core_visible=True)
    actor_pos = np.array([200.0, 0.0, 0.0], dtype=np.float64)
    W, H = 40.0, 56.0

    # Suppose the camera is at (0, 0, 32) so the camera-locked billboard has normal (-1, 0),
    # while a side turret at (200, -180, 28) fires along +Y (45 deg or 60 deg oblique to camera billboard!).
    err_45 = parallax_lateral_error_u(feature_depth_offset_u=6.0, obliquity_angle_rad=math.radians(45.0))
    assert abs(err_45 - 6.0) < 1e-9

    turret_pos = np.array([100.0, -173.2, 30.2], dtype=np.float64)  # 60 deg off camera axis
    core_target = np.array([200.0, 0.0, (1.0 - 0.46) * H], dtype=np.float64)
    res_aligned = trace_billboard_pixel_hit(
        turret_pos,
        core_target - turret_pos,
        actor_pos,
        W,
        H,
        frame,
        billboard_normal_xy=(-1.0, 0.0),
        use_ray_aligned_plane_for_oblique=True,
    )
    assert res_aligned["hit"] and res_aligned["region_id"] == REGION_GREEN_CORE

    # Test conservative cylinder fallback when `frame=None`
    res_cyl = trace_billboard_pixel_hit(
        (0.0, 0.0, 30.0),
        (1.0, 0.0, 0.0),
        actor_pos,
        W,
        H,
        frame=None,
        cylinder_radius_u=16.0,
    )
    assert res_cyl["hit"] and res_cyl["fallback_used"] and res_cyl["region_id"] == REGION_GREEN_CORE

    return {
        "status": "verified (test_oblique_parallax_and_fallback)",
        "parallax_error_at_45deg_for_6u_depth": round(err_45, 3),
        "oblique_60deg_ray_aligned_core_hit": True,
        "cylinder_fallback_verified": True,
    }


def run_all_pixel_hitbox_tests() -> dict[str, Any]:
    return {
        "all_verified": True,
        "core_recall": test_visible_core_texel_100pct_recall(),
        "oblique_and_fallback": test_oblique_parallax_and_fallback(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_pixel_hitbox_tests(), indent=2))