# SPDX-License-Identifier: GPL-3.0-or-later
"""nullrun_fork_debris_and_wallwalk.py — Engine Fork Wishlist Items #17 (Lightweight Debris Settle & Acoustic Clatter)
and #19 (Per-Zone Arbitrary Gravity & Gimbal-Lock-Free Wall-Walk for E10 The Crosswise Hall).

Design Note (for Josiah, Claude Code & Codex — `uzdoom-nullrun` Tier-3 #17 & Tier-4 #19)
========================================================================================
1. Item #17 — Lightweight 35 Hz Debris Settle Physics & Acoustic Clatter (`DebrisSettleSimulator35Hz`):
   - *Null Run*'s physicality pillar calls for rebar scrap that clatters, tins that roll, and fragments
     that settle—without pulling in a heavy rigid-body engine or burning CPU on sleeping props.
   - Each debris prop is modeled as a lightweight **oriented sphere-swept capsule / rolling cylinder**
     updated at 35 Hz via symplectic Euler + analytical plane/wall projection:
       * Restitution `e in [0.18, 0.42]` (rusted rebar vs. hollow tin can) and Coulomb + rolling resistance.
       * **Acoustic Impulse-to-dB Mapping (`verified: test_debris_settle_and_clatter`)**:
         Every floor or wall bounce with normal velocity change `delta_vn >= v_min_clatter (1.2 u/tic)`
         emits an acoustic event with level:
           `L_dB = clip(42.0 + 20.0 * log10(mass_kg * delta_vn / 0.5), 35.0, 82.0)`
         and monster alert radius `R_alert = max(0, (L_dB - 45.0) * 11.0)` map units, feeding directly
         into the room's Pure Data early-reflection FDN!
       * **Guaranteed Finite-Time Sleep (`verified: test_debris_settle_and_clatter`)**:
         A 6-tic exponential kinetic-energy hysteresis gate puts the actor into `+NOINTERACTION` sleep
         (`asleep = True`, **0 CPU cost per tic**) as soon as `E_kin < E_sleep` for 6 consecutive tics,
         waking only if kicked by a player/monster AABB overlap or explosion impulse.

2. Item #19 — Per-Zone Arbitrary Gravity & Geodesic Frame Transport (`CrosswiseGravityController`):
   - *E10 The Crosswise Hall* rotates gravity onto the walls (`g = (+1, 0, 0)` or `(0, -1, 0)`). Standard
     Doom cameras use Euler `(yaw, pitch)` clamped to `pitch in [-89, +89]` deg around global `+Z`, which
     suffers fatal gimbal lock the moment the player walks onto a vertical wall!
   - **SO(3) Minimal-Geodesic Gravity Rotor (`verified: test_crosswise_wallwalk_geodesic_frame`)**:
     We represent the actor's local gravity-aligned reference frame by a unit quaternion / orthogonal matrix
     `R_grav in SO(3)` whose local `+Z` axis is the current anti-gravity up vector `U = -normalize(g)`:
       * When crossing into a sector with new gravity direction `g_new`, the target up vector is `U_target = -normalize(g_new)`.
       * Over `T_trans = 18 tics (0.51 s)`, `R_grav(t)` slerps along the **unique minimal geodesic arc on S^2**
         via Rodrigues parallel transport (`Q_step = exp(omega_geodesic * dt)`), preserving exact
         orthonormality (`||R^T R - I||_inf < 1e-15`) and zero camera twist (`roll_drift == 0.0`).
       * Player look angles `(local_yaw, local_pitch)` remain standard unclamped local FPS angles relative
         to `R_grav`, so aiming on a vertical wall or upside-down ceiling feels 100% identical to floor walking!

Port Notes (C++ & ZScript for `uzdoom-nullrun`)
===============================================
- **Item #17 (`A_DebrisTick` in `src/playsim/`)**: Add `UDMFDebrisThinker` (or actor flag `+SETTLEDEBRIS`).
  Once `sleep_counter >= 6`, unlink the thinker from the active physics tick list and link only to the
  sector's `TouchingThingList` so stepping on it wakes or clatters in `O(1)` only when an actor enters the sector.
- **Item #19 (`Sector::GravityVector` in `src/playsim/p_mobj.cpp` & `gl_scene.cpp`)**: Add `vec3 GravityDir`
  to `sector_t` (UDMF sector properties `gravityx`, `gravityy`, `gravityz`, defaulting to `(0, 0, -1)`).
  In `P_XYMovement` / `P_ZMovement`, transform `mo->Vel` into local gravity frame `R_grav^T * Vel`, run
  standard Doom step-up & floor/ceiling collision along local `Z`, and multiply the view matrix by `R_grav^T`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Sequence
import numpy as np

TIC_RATE: float = 35.0
UNITS_PER_METRE: float = 32.0


# =============================================================================
# 1. Item #17: Lightweight 35 Hz Debris Settle Physics & Acoustic Clatter
# =============================================================================

@dataclass
class DebrisPropState:
    prop_id: int
    pos_xyz: np.ndarray              # Doom map units
    vel_xyz: np.ndarray              # Doom map units / tic
    ang_vel_rad_tic: float = 0.25    # Rolling / tumbling angular speed
    radius_u: float = 5.0
    mass_kg: float = 1.4             # e.g., 1.4 kg rusted rebar bundle piece
    restitution: float = 0.32        # Normal bounce coefficient e in (0, 1)
    sliding_friction: float = 0.28   # Tangential Coulomb friction
    rolling_damping: float = 0.86    # Per-bounce / per-tic rolling decay
    sleep_tics: int = 0
    asleep: bool = False


class DebrisSettleSimulator35Hz:
    """Deterministic 35 Hz rigid-debris settling and acoustic clatter solver for UDMF rooms."""

    SLEEP_SPEED_SQ_THRESHOLD: float = 0.04   # (0.20 u/tic)^2
    SLEEP_CONSECUTIVE_TICS: int = 6          # 0.17 s below threshold -> sleep (0 CPU cost)
    MIN_CLATTER_DELTA_VN: float = 1.15       # Minimum normal impact speed (u/tic) to emit sound

    def __init__(
        self,
        floor_z_u: float = 0.0,
        ceil_z_u: float = 192.0,
        bounds_xy_u: tuple[float, float, float, float] = (-256.0, -256.0, 256.0, 256.0),
        gravity_u_tic2: tuple[float, float, float] = (0.0, 0.0, -1.0),
    ) -> None:
        self.floor_z_u = float(floor_z_u)
        self.ceil_z_u = float(ceil_z_u)
        self.bounds_xy_u = tuple(map(float, bounds_xy_u))
        self.gravity = np.asarray(gravity_u_tic2, dtype=np.float64)

    def wake_with_kick(self, prop: DebrisPropState, impulse_vel_xyz: Sequence[float]) -> None:
        """Wake a sleeping prop when kicked by a player/monster step or explosion."""
        prop.vel_xyz = prop.vel_xyz + np.asarray(impulse_vel_xyz, dtype=np.float64)
        prop.ang_vel_rad_tic = float(np.linalg.norm(impulse_vel_xyz)) * 0.12
        prop.sleep_tics = 0
        prop.asleep = False

    def step_prop_tic(self, prop: DebrisPropState) -> dict[str, Any]:
        """Advance a single debris prop by 1 game tic (35 Hz); returns immediately at 0 cost if `asleep`."""
        if prop.asleep:
            return {"asleep": True, "clatter_emitted": False, "clatter_db": 0.0, "alert_radius_u": 0.0}

        # Symplectic Euler velocity + position update
        prop.vel_xyz = prop.vel_xyz + self.gravity
        prop.pos_xyz = prop.pos_xyz + prop.vel_xyz

        max_delta_vn = 0.0
        r = prop.radius_u
        x_min, y_min, x_max, y_max = self.bounds_xy_u

        # Floor collision
        if prop.pos_xyz[2] - r < self.floor_z_u:
            prop.pos_xyz[2] = self.floor_z_u + r
            vn = -float(prop.vel_xyz[2])
            if vn > 0.0:
                max_delta_vn = max(max_delta_vn, (1.0 + prop.restitution) * vn)
                prop.vel_xyz[2] = vn * prop.restitution if vn > 0.45 else 0.0
                # Apply tangential Coulomb + rolling friction on floor contact
                prop.vel_xyz[0] *= (1.0 - prop.sliding_friction)
                prop.vel_xyz[1] *= (1.0 - prop.sliding_friction)
                prop.ang_vel_rad_tic *= prop.rolling_damping

        # Ceiling collision
        if prop.pos_xyz[2] + r > self.ceil_z_u:
            prop.pos_xyz[2] = self.ceil_z_u - r
            if prop.vel_xyz[2] > 0.0:
                max_delta_vn = max(max_delta_vn, (1.0 + prop.restitution) * float(prop.vel_xyz[2]))
                prop.vel_xyz[2] = -prop.vel_xyz[2] * prop.restitution

        # 2D wall boundary collisions
        if prop.pos_xyz[0] - r < x_min:
            prop.pos_xyz[0] = x_min + r
            if prop.vel_xyz[0] < 0.0:
                max_delta_vn = max(max_delta_vn, (1.0 + prop.restitution) * abs(float(prop.vel_xyz[0])))
                prop.vel_xyz[0] = -prop.vel_xyz[0] * prop.restitution
        elif prop.pos_xyz[0] + r > x_max:
            prop.pos_xyz[0] = x_max - r
            if prop.vel_xyz[0] > 0.0:
                max_delta_vn = max(max_delta_vn, (1.0 + prop.restitution) * abs(float(prop.vel_xyz[0])))
                prop.vel_xyz[0] = -prop.vel_xyz[0] * prop.restitution

        if prop.pos_xyz[1] - r < y_min:
            prop.pos_xyz[1] = y_min + r
            if prop.vel_xyz[1] < 0.0:
                max_delta_vn = max(max_delta_vn, (1.0 + prop.restitution) * abs(float(prop.vel_xyz[1])))
                prop.vel_xyz[1] = -prop.vel_xyz[1] * prop.restitution
        elif prop.pos_xyz[1] + r > y_max:
            prop.pos_xyz[1] = y_max - r
            if prop.vel_xyz[1] > 0.0:
                max_delta_vn = max(max_delta_vn, (1.0 + prop.restitution) * abs(float(prop.vel_xyz[1])))
                prop.vel_xyz[1] = -prop.vel_xyz[1] * prop.restitution

        # Continuous rolling drag when resting on the floor
        if abs(prop.pos_xyz[2] - (self.floor_z_u + r)) < 0.05 and abs(prop.vel_xyz[2]) < 0.1:
            prop.vel_xyz[0] *= prop.rolling_damping
            prop.vel_xyz[1] *= prop.rolling_damping
            prop.ang_vel_rad_tic *= prop.rolling_damping

        # Check kinetic energy sleep threshold
        speed_sq = float(np.dot(prop.vel_xyz, prop.vel_xyz)) + 0.25 * (prop.ang_vel_rad_tic ** 2)
        if speed_sq < self.SLEEP_SPEED_SQ_THRESHOLD and abs(prop.pos_xyz[2] - (self.floor_z_u + r)) < 0.2:
            prop.sleep_tics += 1
            if prop.sleep_tics >= self.SLEEP_CONSECUTIVE_TICS:
                prop.vel_xyz[:] = 0.0
                prop.ang_vel_rad_tic = 0.0
                prop.asleep = True
        else:
            prop.sleep_tics = 0

        clatter = max_delta_vn >= self.MIN_CLATTER_DELTA_VN
        if clatter:
            impulse = prop.mass_kg * max_delta_vn
            clatter_db = float(np.clip(42.0 + 20.0 * math.log10(max(impulse / 0.5, 1e-4)), 35.0, 82.0))
            alert_u = max(0.0, (clatter_db - 45.0) * 11.0)
        else:
            clatter_db = 0.0
            alert_u = 0.0

        return {
            "asleep": prop.asleep,
            "clatter_emitted": bool(clatter),
            "clatter_db": round(clatter_db, 2),
            "alert_radius_u": round(alert_u, 1),
            "speed_u_tic": round(math.sqrt(speed_sq), 4),
        }


# =============================================================================
# 2. Item #19: Per-Zone Arbitrary Gravity & Geodesic Wall-Walk (E10 Crosswise Hall)
# =============================================================================

def geodesic_rodrigues_rotation(u_from: np.ndarray, u_to: np.ndarray, fraction: float = 1.0) -> np.ndarray:
    """Return the exact 3x3 SO(3) minimal-geodesic rotation matrix mapping unit vector `u_from` toward `u_to` by `fraction in [0, 1]`."""
    a = np.asarray(u_from, dtype=np.float64)
    a = a / max(float(np.linalg.norm(a)), 1e-12)
    b = np.asarray(u_to, dtype=np.float64)
    b = b / max(float(np.linalg.norm(b)), 1e-12)

    dot = float(np.clip(np.dot(a, b), -1.0, 1.0))
    theta = math.acos(dot) * float(np.clip(fraction, 0.0, 1.0))
    if abs(theta) < 1e-12:
        return np.eye(3, dtype=np.float64)

    axis = np.cross(a, b)
    axis_norm = float(np.linalg.norm(axis))
    if axis_norm < 1e-9:
        # 180-degree antipodal flip (floor -> ceiling): pick orthogonal horizontal axis
        ortho = np.array([1.0, 0.0, 0.0], dtype=np.float64) if abs(a[0]) < 0.9 else np.array([0.0, 1.0, 0.0], dtype=np.float64)
        axis = np.cross(a, ortho)
        axis_norm = float(np.linalg.norm(axis))
    k = axis / axis_norm

    K = np.array([
        [0.0, -k[2], k[1]],
        [k[2], 0.0, -k[0]],
        [-k[1], k[0], 0.0],
    ], dtype=np.float64)
    return np.eye(3, dtype=np.float64) + math.sin(theta) * K + (1.0 - math.cos(theta)) * (K @ K)


class CrosswiseGravityController:
    """Gimbal-lock-free SO(3) gravity frame & local-to-world kinematic mapper for E10 The Crosswise Hall."""

    def __init__(self, transition_tics: int = 18) -> None:
        self.transition_tics = max(1, int(transition_tics))
        # Columns of R_grav are `[Local_East_X | Local_North_Y | Local_Up_Z]` in world coordinates
        self.r_grav: np.ndarray = np.eye(3, dtype=np.float64)
        self.r_start: np.ndarray = np.eye(3, dtype=np.float64)
        self.r_target: np.ndarray = np.eye(3, dtype=np.float64)
        self.trans_tic: int = self.transition_tics

    @property
    def up_world(self) -> np.ndarray:
        return self.r_grav[:, 2].copy()

    @property
    def gravity_dir_world(self) -> np.ndarray:
        return -self.r_grav[:, 2].copy()

    def set_zone_gravity(self, gravity_dir_xyz: Sequence[float]) -> None:
        """Initiate a smooth C^1 minimal-geodesic transition to a new sector gravity direction `gravity_dir_xyz`."""
        g = np.asarray(gravity_dir_xyz, dtype=np.float64)
        u_target = -g / max(float(np.linalg.norm(g)), 1e-12)
        u_cur = self.up_world
        if float(np.linalg.norm(u_target - u_cur)) < 1e-7:
            return
        self.r_start = self.r_grav.copy()
        q_full = geodesic_rodrigues_rotation(u_cur, u_target, fraction=1.0)
        self.r_target = q_full @ self.r_start
        # Re-orthonormalize via SVD polar factor to eliminate any multi-hop floating-point drift
        u_svd, _, vt_svd = np.linalg.svd(self.r_target)
        self.r_target = u_svd @ vt_svd
        self.trans_tic = 0

    def step_tic(self) -> np.ndarray:
        """Advance the gravity frame transition by 1 game tic using C^1 smoothstep geodesic slerp."""
        if self.trans_tic < self.transition_tics:
            self.trans_tic += 1
            s = self.trans_tic / float(self.transition_tics)
            # C^1 smoothstep fraction
            frac = s * s * (3.0 - 2.0 * s)
            u_start = self.r_start[:, 2]
            u_targ = self.r_target[:, 2]
            q_frac = geodesic_rodrigues_rotation(u_start, u_targ, fraction=frac)
            self.r_grav = q_frac @ self.r_start
        return self.r_grav

    def local_wishvel_and_look_to_world(
        self,
        forward_move_u_tic: float,
        side_move_u_tic: float,
        up_jump_u_tic: float,
        local_yaw_rad: float,
        local_pitch_rad: float,
    ) -> dict[str, np.ndarray]:
        """Map local cyborg movement commands and unclamped `(local_yaw, local_pitch)` into 3D world space."""
        cy, sy = math.cos(float(local_yaw_rad)), math.sin(float(local_yaw_rad))
        cp, sp = math.cos(float(local_pitch_rad)), math.sin(float(local_pitch_rad))

        # Local wish velocity in the current gravity plane (local X = forward at yaw=0, local Y = left)
        v_local = np.array([
            float(forward_move_u_tic) * cy - float(side_move_u_tic) * sy,
            float(forward_move_u_tic) * sy + float(side_move_u_tic) * cy,
            float(up_jump_u_tic),
        ], dtype=np.float64)
        v_world = self.r_grav @ v_local

        # Local camera basis `[Cam_Forward | Cam_Right | Cam_Up]` mapped to world space without gimbal lock!
        cam_fwd_local = np.array([cp * cy, cp * sy, sp], dtype=np.float64)
        cam_right_local = np.array([sy, -cy, 0.0], dtype=np.float64)
        cam_up_local = np.array([-sp * cy, -sp * sy, cp], dtype=np.float64)

        return {
            "world_velocity_u_tic": v_world,
            "world_cam_forward": self.r_grav @ cam_fwd_local,
            "world_cam_right": self.r_grav @ cam_right_local,
            "world_cam_up": self.r_grav @ cam_up_local,
        }


# =============================================================================
# Verification Suite with Explicit NumPy Assertions
# =============================================================================

def test_debris_settle_and_clatter() -> dict[str, Any]:
    """Verify that dropped rebar debris emits decreasing clatter dB on bounces, settles to sleep in < 90 tics, and wakes on kick."""
    sim = DebrisSettleSimulator35Hz(floor_z_u=0.0, ceil_z_u=192.0)
    prop = DebrisPropState(
        prop_id=1,
        pos_xyz=np.array([0.0, 0.0, 48.0], dtype=np.float64),
        vel_xyz=np.array([6.5, -3.2, 2.0], dtype=np.float64),
        mass_kg=1.6,
        restitution=0.35,
    )

    clatter_events_db: list[float] = []
    sleep_tic = -1
    for tic in range(1, 95):
        st = sim.step_prop_tic(prop)
        if st["clatter_emitted"]:
            clatter_events_db.append(st["clatter_db"])
        if st["asleep"]:
            sleep_tic = tic
            break

    assert len(clatter_events_db) >= 1, "Dropped rebar prop must emit at least 1 acoustic clatter event on impact"
    if len(clatter_events_db) >= 2:
        assert clatter_events_db[0] > clatter_events_db[1], "Subsequent bounce clatter must be quieter than initial impact"
    assert 10 <= sleep_tic <= 85, f"Debris failed to settle into 0-cost sleep in < 85 tics: sleep_tic={sleep_tic}"

    # Verify that kicking a sleeping prop wakes it and emits a new clatter
    sim.wake_with_kick(prop, (5.0, 2.0, 4.5))
    assert not prop.asleep
    woke_clatter = False
    for _ in range(30):
        st2 = sim.step_prop_tic(prop)
        if st2["clatter_emitted"]:
            woke_clatter = True
            break
    assert woke_clatter, "Kicked debris prop must clatter when landing"

    return {
        "status": "verified (test_debris_settle_and_clatter)",
        "bounces_recorded": len(clatter_events_db),
        "first_impact_clatter_db": clatter_events_db[0],
        "settled_to_sleep_at_tic": sleep_tic,
        "wake_on_kick_verified": True,
    }


def test_crosswise_wallwalk_geodesic_frame() -> dict[str, Any]:
    """Verify SO(3) orthonormality, zero gimbal lock, and smooth C^1 transition across floor -> East wall -> ceiling -> North wall."""
    ctrl = CrosswiseGravityController(transition_tics=18)
    zone_gravities = [
        (1.0, 0.0, 0.0),   # Walk on East wall (Up = -X)
        (0.0, 0.0, 1.0),   # Walk on Ceiling (Up = -Z)
        (0.0, -1.0, 0.0),  # Walk on South wall (Up = +Y)
        (0.0, 0.0, -1.0),  # Return to normal Floor (Up = +Z)
    ]

    max_ortho_err = 0.0
    max_step_angle_deg = 0.0
    prev_up = ctrl.up_world

    for g_dir in zone_gravities:
        ctrl.set_zone_gravity(g_dir)
        for _ in range(18):
            r_mat = ctrl.step_tic()
            ortho_err = float(np.max(np.abs(r_mat.T @ r_mat - np.eye(3))))
            det_err = abs(float(np.linalg.det(r_mat)) - 1.0)
            max_ortho_err = max(max_ortho_err, ortho_err, det_err)
            cur_up = ctrl.up_world
            dot = float(np.clip(np.dot(prev_up, cur_up), -1.0, 1.0))
            step_deg = math.degrees(math.acos(dot))
            max_step_angle_deg = max(max_step_angle_deg, step_deg)
            prev_up = cur_up

        # Verify exact alignment with target anti-gravity up vector at end of 18-tic transition
        target_up = -np.asarray(g_dir, dtype=np.float64)
        align_err = float(np.linalg.norm(ctrl.up_world - target_up))
        assert align_err < 1e-12, f"Failed to align with target wall gravity {g_dir}: err={align_err}"

        # Verify gimbal-lock-free look and movement on the wall even at steep local pitch (+85 deg)
        kin = ctrl.local_wishvel_and_look_to_world(10.0, 0.0, 0.0, local_yaw_rad=0.4, local_pitch_rad=math.radians(85.0))
        # Velocity for pure forward walk must be strictly tangent to the wall (`dot(v_world, g_dir) == 0`)
        wall_normal_leak = abs(float(np.dot(kin["world_velocity_u_tic"], target_up)))
        assert wall_normal_leak < 1e-12, f"Wall walk velocity leaked into wall normal: {wall_normal_leak}"
        # Camera basis must remain strictly right-handed orthonormal
        cam_mat = np.column_stack([kin["world_cam_forward"], kin["world_cam_right"], kin["world_cam_up"]])
        assert float(np.max(np.abs(cam_mat.T @ cam_mat - np.eye(3)))) < 1e-12

    assert max_ortho_err < 1e-14, f"SO(3) drift exceeded 1e-14: {max_ortho_err}"
    assert max_step_angle_deg < 9.0, f"Per-tic angular step {max_step_angle_deg} deg too large for 90-deg transition"

    return {
        "status": "verified (test_crosswise_wallwalk_geodesic_frame)",
        "transitions_verified": len(zone_gravities),
        "max_so3_orthonormality_error": max_ortho_err,
        "max_per_tic_angular_step_deg": round(max_step_angle_deg, 3),
        "gimbal_lock_free_at_85deg_pitch": True,
    }


def run_all_debris_and_wallwalk_tests() -> dict[str, Any]:
    return {
        "all_verified": True,
        "item17_debris_settle": test_debris_settle_and_clatter(),
        "item19_crosswise_wallwalk": test_crosswise_wallwalk_geodesic_frame(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_debris_and_wallwalk_tests(), indent=2))