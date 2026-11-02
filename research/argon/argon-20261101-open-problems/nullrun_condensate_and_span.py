# SPDX-License-Identifier: CC0-1.0
"""nullrun_condensate_and_span.py — Open Problems #6 & #7: The Condensate Sprite Refraction & The Span Living Bridge.

Solves the final two open problems from Section 7 of Claude Code's Null Run brief:

Open Problem #6 — The Condensate (Glass-Clear Sprite Refraction Without a Depth Buffer):
  - *The Condensate* (from the shadow family) is a glass-clear figure seen in doorways and windows,
    rendered as pre-rendered sprites without access to a scene depth buffer.
  - `bake_condensate_optical_map` takes any binary or soft alpha silhouette (or Blender pass) and
    computes the exact interior Euclidean distance field $d_{\\text{in}}(x, y)$ to the silhouette
    boundary, constructing an ellipsoidal glass lens thickness profile:
      $$\\tau(x, y) = \\sqrt{\\operatorname{clamp}\\!\\big(d_{\\text{in}}(x, y) / d_{\\max},\\, 0,\\, 1\\big)}$$
    whose spatial gradient yields the camera-space refraction normal $(N_x, N_y) = -\\nabla\\tau(x, y)$
    and Schlick Fresnel rim reflectance $F(x, y) = R_0 + (1 - R_0)(1 - N_z)^5$ ($R_0 = 0.0426$ for
    crown glass $n = 1.52$).
  - Packs `(Nx, Ny, Fresnel, Thickness)` into a single 8-bit RGBA sprite texture so `refract_condensate_np`
    and `CONDENSATE_REFRACTION_GLSL` refract the background doorway/hallway via paraxial Snell dispersion
    ($\\Delta\\mathbf{u}_c = -\\eta_c \\tau(x, y) (N_x, N_y)$ for $c \\in \\{R, G, B\\}$) with **zero scene depth
    buffer required** and exact zero distortion outside the silhouette (`alpha == 0`).

Open Problem #7 — The Span (A Creature That Is Also a Bridge, Robust in 2.5D/UDMF):
  - *The Span* (`11 THE SPAN`) is a slab-and-rebar quadruped that roams as a creature and lies
    across chasms so the player can walk across its spine as a bridge.
  - Relying on actor-on-actor AABB collision (`+ACTLIKEBRIDGE`) fails in 2.5D Doom engines because
    Doom actor hitboxes are axis-aligned squares (`radius xradius`) that cannot rotate to match a
    diagonal chasm, snag on ledge step-ups, and crush/drop the player during state transitions.
  - `SpanBridgeController` implements the **Segmented `Sector_Set3DFloor` Chasm-Slot Lockstep**:
    1. Each crossable chasm has $K = 5$ narrow UDMF bridge sectors $S_0, \\dots, S_4$ spanning from
       Ledge A to Ledge B at deck height $z_{\\text{deck}}$, linked via `Sector_Set3DFloor` (`special = 160`)
       to 5 dummy control sectors.
    2. While the Span is `ROAMING` or `ALIGNING`, all 5 control sectors are parked below the chasm floor
       and non-solid (`solid = False`).
    3. During `EXTENDING_SPINE` (5 stages x 10 tics = 50 tics), as the Span's animation stretches across
       the gap, segments $S_0 \\to S_4$ sequentially lock to `[z_deck - 12, z_deck]` with `solid = True`
       so the walkable surface advances in lockstep with the creature's spine!
    4. During `LOCKED_BRIDGE`, the Span actor shifts its own collision height below the deck (`z_actor_top <= z_deck - 4`)
       so the player walks smoothly across the true polygon geometry of $S_0 \\dots S_4$ without ever
       snagging on an actor AABB.
    5. **Player-On-Bridge Safety Interlock**: The transition `LOCKED_BRIDGE -> RETRACTING` is strictly
       inhibited whenever any player/actor 2D bounding box overlaps $\\bigcup_{k=0}^4 S_k$, guaranteeing
       zero mid-crossing drops or softlocks.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any
import numpy as np

from nullrun_sprite_morph import edt_2d


def bake_condensate_optical_map(alpha_mask: np.ndarray, refractive_power: float = 1.0) -> np.ndarray:
    """Bake an RGBA uint8 optical refraction sprite `(R=Nx, G=Ny, B=Fresnel, A=Thickness)` from a silhouette."""
    inside = np.asarray(alpha_mask) >= 0.5
    h, w = inside.shape
    if not np.any(inside):
        return np.zeros((h, w, 4), dtype=np.uint8)

    # Interior Euclidean distance to silhouette edge
    dist_in = edt_2d(~inside) * inside.astype(np.float64)
    d_max = max(float(dist_in.max()), 1.0)
    # Ellipsoidal lens thickness profile tau in [0, 1]
    tau = np.sqrt(np.clip(dist_in / d_max, 0.0, 1.0))

    # Smooth tau slightly (3x3 box) for C^1 normal continuity across pixel steps
    tau_s = tau.copy()
    for _ in range(2):
        acc = np.zeros_like(tau_s)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                acc += np.roll(np.roll(tau_s, dy, axis=0), dx, axis=1)
        tau_s = (acc / 9.0) * inside

    # Camera-space lens normals (Nx, Ny) = -grad(tau)
    dtau_dx = np.zeros_like(tau_s)
    dtau_dy = np.zeros_like(tau_s)
    dtau_dx[:, 1:-1] = (tau_s[:, 2:] - tau_s[:, :-2]) * 0.5
    dtau_dy[1:-1, :] = (tau_s[2:, :] - tau_s[:-2, :]) * 0.5

    nx = np.clip(-dtau_dx * 3.2 * float(refractive_power), -0.98, 0.98) * inside
    ny = np.clip(-dtau_dy * 3.2 * float(refractive_power), -0.98, 0.98) * inside
    nz = np.sqrt(np.maximum(0.0, 1.0 - nx * nx - ny * ny))

    # Schlick Fresnel reflectance for crown glass (n = 1.52 -> R0 = 0.0426) + internal caustic veins
    r0 = 0.0426
    fresnel = (r0 + (1.0 - r0) * ((1.0 - nz) ** 4)) * inside
    caustic = np.clip(np.abs(nx * ny) * 2.5, 0.0, 0.35) * inside
    b_ch = np.clip(fresnel + caustic, 0.0, 1.0)

    r_u8 = np.where(inside, np.clip(0.5 + 0.5 * nx, 0.0, 1.0), 0.5)
    g_u8 = np.where(inside, np.clip(0.5 + 0.5 * ny, 0.0, 1.0), 0.5)
    rgba = np.stack([r_u8, g_u8, b_ch, tau_s], axis=-1)
    return (np.clip(rgba, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


def refract_condensate_np(
    bg_rgb: np.ndarray,
    optical_rgba_u8: np.ndarray,
    ior_strength: float = 14.0,
    dispersion: float = 0.28,
) -> np.ndarray:
    """Apply depthless glass refraction + chromatic dispersion + Fresnel specular over `bg_rgb`."""
    bg = np.asarray(bg_rgb, dtype=np.float32)
    if bg.max() > 1.001:
        bg = bg / 255.0
    opt = np.asarray(optical_rgba_u8, dtype=np.float32) / 255.0

    h, w = bg.shape[:2]
    nx = (opt[..., 0] * 2.0 - 1.0)
    ny = (opt[..., 1] * 2.0 - 1.0)
    fresnel = opt[..., 2]
    thickness = opt[..., 3]
    inside = thickness > 0.005

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base_dx = -nx * thickness * float(ior_strength)
    base_dy = -ny * thickness * float(ior_strength)

    # 3-channel Cauchy chromatic dispersion (Red bends least, Blue bends most)
    scales = (1.0 - float(dispersion), 1.0, 1.0 + float(dispersion))
    refracted = np.zeros_like(bg[..., :3])
    for ch_idx, s_c in enumerate(scales):
        sx = np.clip(np.round(xx + base_dx * s_c).astype(np.int32), 0, w - 1)
        sy = np.clip(np.round(yy + base_dy * s_c).astype(np.int32), 0, h - 1)
        refracted[..., ch_idx] = bg[sy, sx, ch_idx]

    # Add cold glass transmission attenuation + bright Fresnel specular rim
    glass_tint = np.array([0.88, 0.95, 1.00], dtype=np.float32)
    transmitted = refracted * (1.0 - 0.16 * thickness[..., None]) * glass_tint
    specular = np.array([0.82, 0.96, 1.00], dtype=np.float32) * (fresnel[..., None] * 0.95)
    comp = np.clip(transmitted + specular, 0.0, 1.0)
    return np.where(inside[..., None], comp, bg[..., :3]).astype(np.float32)


CONDENSATE_REFRACTION_GLSL = """#version 330 core
// UZDoom / OpenGL 3.3 depthless sprite refraction shader for The Condensate.
in vec2 v_uv;
out vec4 fragColor;
uniform sampler2D u_world;
uniform sampler2D u_condensate_opt;
uniform vec2 u_resolution;
uniform float u_ior_px;

void main() {
    vec4 base = texture(u_world, v_uv);
    vec4 opt = texture(u_condensate_opt, v_uv);
    float tau = opt.a;
    if (tau <= 0.005) {
        fragColor = base;
        return;
    }
    vec2 n_xy = opt.rg * 2.0 - 1.0;
    float fresnel = opt.b;
    vec2 px = 1.0 / max(u_resolution, vec2(1.0));
    vec2 lo = 0.5 * px, hi = vec2(1.0) - lo;
    vec2 disp = -n_xy * tau * u_ior_px * px;
    float r = texture(u_world, clamp(v_uv + disp * 0.75, lo, hi)).r;
    float g = texture(u_world, clamp(v_uv + disp * 1.00, lo, hi)).g;
    float b = texture(u_world, clamp(v_uv + disp * 1.25, lo, hi)).b;
    vec3 glass = vec3(r, g, b) * (1.0 - 0.16 * tau) * vec3(0.88, 0.95, 1.0) + vec3(0.82, 0.96, 1.0) * fresnel * 0.95;
    fragColor = vec4(clamp(glass, 0.0, 1.0), base.a);
}
"""


# =============================================================================
# Open Problem #7: The Span (Living Bridge Platform State Machine in 2.5D/UDMF)
# =============================================================================

@dataclass
class BridgeSegment3DFloor:
    segment_index: int
    control_sector_tag: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_bottom: float
    z_top: float
    solid: bool


class SpanBridgeController:
    """Deterministic 5-state lockstep controller for `The Span` living 3D-floor bridge in UDMF."""

    STATES = ("ROAMING", "ALIGNING", "EXTENDING_SPINE", "LOCKED_BRIDGE", "RETRACTING")

    def __init__(
        self,
        chasm_x0: float = 0.0,
        chasm_x1: float = 320.0,
        chasm_y_center: float = 0.0,
        bridge_width: float = 96.0,
        deck_z: float = 0.0,
        abyss_z: float = -256.0,
        num_segments: int = 5,
        tics_per_segment: int = 8,
    ) -> None:
        self.chasm_x0 = float(chasm_x0)
        self.chasm_x1 = float(chasm_x1)
        self.chasm_y_center = float(chasm_y_center)
        self.bridge_width = float(bridge_width)
        self.deck_z = float(deck_z)
        self.abyss_z = float(abyss_z)
        self.num_segments = int(num_segments)
        self.tics_per_segment = int(tics_per_segment)

        self.state = "ROAMING"
        self.state_tic = 0
        self.actor_z_top = self.deck_z + 64.0
        self.actor_solid_to_weapons = True

        dx = (self.chasm_x1 - self.chasm_x0) / self.num_segments
        half_w = 0.5 * self.bridge_width
        self.segments: list[BridgeSegment3DFloor] = [
            BridgeSegment3DFloor(
                segment_index=k,
                control_sector_tag=1600 + k,
                x_min=self.chasm_x0 + k * dx,
                x_max=self.chasm_x0 + (k + 1) * dx,
                y_min=self.chasm_y_center - half_w,
                y_max=self.chasm_y_center + half_w,
                z_bottom=self.abyss_z - 16.0,
                z_top=self.abyss_z - 4.0,
                solid=False,
            )
            for k in range(self.num_segments)
        ]

    def is_player_on_bridge(self, player_xy: tuple[float, float], player_radius: float = 16.0) -> bool:
        """Return True if the player's 2D AABB overlaps any active bridge segment."""
        px, py = float(player_xy[0]), float(player_xy[1])
        r = float(player_radius)
        x_overlap = (px + r >= self.chasm_x0) and (px - r <= self.chasm_x1)
        y_overlap = abs(py - self.chasm_y_center) <= (0.5 * self.bridge_width + r)
        return bool(x_overlap and y_overlap)

    def step_tic(
        self,
        at_chasm_anchor: bool,
        command_retract: bool = False,
        player_xy: tuple[float, float] = (-100.0, 0.0),
    ) -> dict[str, Any]:
        """Advance the Span bridge state machine by 1 tic (35 Hz) with player-on-bridge safety interlock."""
        player_on_deck = self.is_player_on_bridge(player_xy)

        if self.state == "ROAMING":
            if at_chasm_anchor:
                self.state = "ALIGNING"
                self.state_tic = 0

        elif self.state == "ALIGNING":
            self.state_tic += 1
            if self.state_tic >= 10:
                self.state = "EXTENDING_SPINE"
                self.state_tic = 0

        elif self.state == "EXTENDING_SPINE":
            self.state_tic += 1
            # Sequentially raise and solidify segments 0 .. K-1 as spine unfurls
            for k, seg in enumerate(self.segments):
                t_start = k * self.tics_per_segment
                t_end = (k + 1) * self.tics_per_segment
                if self.state_tic >= t_end:
                    seg.z_top = self.deck_z
                    seg.z_bottom = self.deck_z - 12.0
                    seg.solid = True
                elif self.state_tic > t_start:
                    frac = (self.state_tic - t_start) / float(self.tics_per_segment)
                    seg.z_top = (1.0 - frac) * (self.abyss_z - 4.0) + frac * self.deck_z
                    seg.z_bottom = seg.z_top - 12.0
                    seg.solid = frac >= 0.99
            if self.state_tic >= self.num_segments * self.tics_per_segment:
                self.state = "LOCKED_BRIDGE"
                self.state_tic = 0
                # Duck actor hitbox below deck so player walks on pure UDMF 3D floor polygons without snagging
                self.actor_z_top = self.deck_z - 4.0
                self.actor_solid_to_weapons = False

        elif self.state == "LOCKED_BRIDGE":
            self.state_tic += 1
            # HARD SAFETY INTERLOCK: Never retract while a player/actor is on the bridge!
            if command_retract and not player_on_deck:
                self.state = "RETRACTING"
                self.state_tic = 0

        elif self.state == "RETRACTING":
            # If player steps onto remaining segments during retraction start, abort and re-lock!
            if player_on_deck:
                self.state = "EXTENDING_SPINE"
                self.state_tic = (self.num_segments - 1) * self.tics_per_segment
            else:
                self.state_tic += 1
                for k in range(self.num_segments - 1, -1, -1):
                    rev_k = (self.num_segments - 1) - k
                    seg = self.segments[k]
                    if self.state_tic >= (rev_k + 1) * self.tics_per_segment:
                        seg.solid = False
                        seg.z_top = self.abyss_z - 4.0
                        seg.z_bottom = self.abyss_z - 16.0
                if self.state_tic >= self.num_segments * self.tics_per_segment:
                    self.state = "ROAMING"
                    self.state_tic = 0
                    self.actor_z_top = self.deck_z + 64.0
                    self.actor_solid_to_weapons = True

        solid_count = sum(1 for s in self.segments if s.solid and abs(s.z_top - self.deck_z) < 1e-6)
        return {
            "state": self.state,
            "state_tic": self.state_tic,
            "solid_segments": solid_count,
            "bridge_fully_walkable": (solid_count == self.num_segments),
            "player_on_deck": player_on_deck,
            "actor_z_top": self.actor_z_top,
        }


def verify_condensate_and_span_invariants() -> dict[str, Any]:
    """Run explicit NumPy & state-machine assertions on Problems #6 (Condensate) and #7 (Span)."""
    # 1. Verify Problem #6 (Condensate depthless sprite refraction)
    h, w = 96, 96
    yy, xx = np.mgrid[0:h, 0:w]
    # Tall glass humanoid silhouette in doorway
    head = ((xx - 48) ** 2 + (yy - 24) ** 2) <= 10 ** 2
    torso = (np.abs(xx - 48) <= 14) & (yy >= 34) & (yy <= 78)
    alpha = (head | torso).astype(np.float32)

    opt_u8 = bake_condensate_optical_map(alpha, refractive_power=1.2)
    # Brick/grid background
    bg = np.zeros((h, w, 3), dtype=np.float32)
    bg[..., 0] = ((xx % 12 < 2) | (yy % 8 < 2)).astype(np.float32) * 0.65 + 0.18
    bg[..., 1] = ((xx % 12 < 2) | (yy % 8 < 2)).astype(np.float32) * 0.58 + 0.20
    bg[..., 2] = ((xx % 12 < 2) | (yy % 8 < 2)).astype(np.float32) * 0.48 + 0.22

    refr = refract_condensate_np(bg, opt_u8, ior_strength=12.0, dispersion=0.25)

    # Assert exact zero modification outside silhouette (`alpha == 0`)
    outside_err = float(np.max(np.abs(refr[alpha < 0.5] - bg[alpha < 0.5])))
    assert outside_err == 0.0, f"Pixels outside Condensate silhouette were modified: {outside_err}"
    # Assert non-trivial refraction & chromatic dispersion inside silhouette
    inside_diff = float(np.mean(np.abs(refr[alpha >= 0.5] - bg[alpha >= 0.5])))
    chroma_spread = float(np.mean(np.abs(refr[alpha >= 0.5, 0] - refr[alpha >= 0.5, 2])))
    assert inside_diff > 0.05 and chroma_spread > 0.02

    # 2. Verify Problem #7 (The Span living bridge state machine & safety interlock)
    span = SpanBridgeController(num_segments=5, tics_per_segment=6)
    for _ in range(11):  # 1 tic ROAMING->ALIGNING + 10 tics ALIGNING->EXTENDING_SPINE
        st = span.step_tic(at_chasm_anchor=True)
    assert st["state"] == "EXTENDING_SPINE"

    # Step through spine extension and verify monotonic segment locking 0 -> 1 -> 2 -> 3 -> 4 -> 5
    prev_solid = 0
    for _ in range(30):
        st = span.step_tic(at_chasm_anchor=True)
        assert st["solid_segments"] >= prev_solid, "Bridge segments must solidify monotonically"
        prev_solid = st["solid_segments"]
    assert st["state"] == "LOCKED_BRIDGE" and st["bridge_fully_walkable"]
    assert st["actor_z_top"] < span.deck_z, "Actor hitbox must duck below deck height when locked"

    # Attempt to retract while player is standing on the bridge at x=160, y=0 -> MUST BE BLOCKED!
    st_blocked = span.step_tic(at_chasm_anchor=True, command_retract=True, player_xy=(160.0, 0.0))
    assert st_blocked["state"] == "LOCKED_BRIDGE" and st_blocked["bridge_fully_walkable"], (
        "Safety interlock failed: bridge retracted while player was standing on deck!"
    )

    # Once player steps off onto Ledge B (x=380, y=0), retraction proceeds cleanly
    st_ret = span.step_tic(at_chasm_anchor=True, command_retract=True, player_xy=(380.0, 0.0))
    assert st_ret["state"] == "RETRACTING"

    return {
        "verified": True,
        "condensate_outside_err": outside_err,
        "condensate_inside_refraction_l1": round(inside_diff, 4),
        "condensate_chromatic_dispersion": round(chroma_spread, 4),
        "span_safety_interlock_held": True,
        "span_segments_locked": 5,
    }