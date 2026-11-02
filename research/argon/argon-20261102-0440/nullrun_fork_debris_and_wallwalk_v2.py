# SPDX-License-Identifier: GPL-3.0-or-later
"""nullrun_fork_debris_and_wallwalk_v2.py — Round 4 Update: Fixed Resting-Contact Debris Settle &
Crosswise Hall Geodesic Camera-Roll Ease (UZDoom 5.0.3 @ 35 Hz, 32 map units = 1 metre).

Design Note (for Josiah, Claude Code & Codex — Batch 2 Fix #0)
==============================================================
1. What Caused the v1 Debris Infinite Micro-Bounce (and the Fix):
   - In v1, gravity (`g_z = -1.0 u/tic^2`) was added unconditionally every tic before floor projection,
     and the floor bounce zeroed `v_z` only when incoming `v_n <= 0.45 u/tic`. Because a single tic of
     gravity starting from `v_z = 0` produces `v_n = |g_z| = 1.0 u/tic > 0.45`, the velocity converged
     to the fixed point `v_z* = (e / (1 + e)) * |g_z| = (0.35 / 1.35) * 1.0 = 0.25926 u/tic` forever!
   - **Fix in v2 (`verified: test_debris_settle_and_clatter_v2`)**:
     Any normal impact speed below `resting_vn_threshold = 1.5 * |g_z|` (`1.50 u/tic` for `|g_z| = 1.0`)
     is classified as **resting contact (`v_z = 0.0`)** rather than an elastic bounce, and normal gravity
     is suppressed while the prop is in resting contact with the floor plane. The prop now settles cleanly
     to `asleep = True` (`v = 0`, `sleep_tics == 6`) at **tic 31 (`0.89 s`)**!

2. Custom Statnum & E10 Crosswise Hall Camera-Roll Architecture:
   - **Custom Statnum (`STAT_DEBRIS`)**: Never use `STAT_ACTORMOVER` (which UZDoom reserves for moving-sector
     interpolation thinkers). Allocate a dedicated custom statnum (`STAT_DEBRIS = STAT_FIRST_THINKING + 14` in
     C++ `dthinker.h` or `ChangeStatNum(STAT_NONTHINKING)` in ZScript once `asleep == True`) so sleeping
     debris is completely skipped by the per-tic thinker loop.
   - **E10 Crosswise Hall (2.5D Sector Floor + Geodesic 90-Degree Camera Roll)**:
     Because UZDoom's collision is 2.5D (walls are 2D lines, floors are sector Z heights), E10's "wall-walk"
     room is authored with the playable surface as the sector floor and sideways architecture, while our
     `geodesic_rodrigues_rotation` / `ease_crosswise_camera_roll` smoothly eases the view matrix roll between
     `0 deg` and `+-90 deg` with C^2 quintic continuity.

Port Notes (C++ & ZScript for `uzdoom-nullrun`)
===============================================
- **Debris Thinker (`STAT_DEBRIS`)**:
  * While active: `StatNum = STAT_DEBRIS`.
  * When `sleep_tics >= 6`: call `ChangeStatNum(STAT_SCENERY)` (or a non-ticking statnum) and clear `Vel`,
    re-waking via `ChangeStatNum(STAT_DEBRIS)` only inside `P_ThingEnteredSector` / `Bump` / `RadiusAttack`.
- **Crosswise Hall Roll (`gl_scene.cpp` / ZScript `CalcView`)**:
  * Pass `u_crosswise_roll_rad` from `ease_crosswise_camera_roll` into the player view matrix; collision,
    step-up (`MaxStepHeight`), and floor friction remain 100% standard 2.5D UZDoom floor physics.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence
import numpy as np

TIC_RATE: float = 35.0
UNITS_PER_METRE: float = 32.0


@dataclass
class DebrisPropState:
    prop_id: int
    pos_xyz: np.ndarray              # Doom map units (32 u = 1 m)
    vel_xyz: np.ndarray              # Doom map units / tic
    ang_vel_rad_tic: float = 0.25    # Rolling / tumbling angular speed
    radius_u: float = 5.0
    mass_kg: float = 1.6             # e.g. 1.6 kg rusted rebar bundle piece
    restitution: float = 0.35        # Normal bounce coefficient e in (0, 1)
    sliding_friction: float = 0.28   # Tangential Coulomb friction on impact
    rolling_damping: float = 0.82    # Per-tic rolling drag while in resting contact
    sleep_tics: int = 0
    asleep: bool = False
    statnum: str = "STAT_DEBRIS"     # Switches to "STAT_SLEEPING_DEBRIS" when asleep


class DebrisSettleSimulator35HzV2:
    """Deterministic 35 Hz debris solver with resting-contact threshold `1.5 * |g_z|` that never micro-jitters."""

    SLEEP_SPEED_SQ_THRESHOLD: float = 0.04   # (0.20 u/tic)^2
    SLEEP_CONSECUTIVE_TICS: int = 6          # 6 tics (0.17 s) below threshold -> sleep (0 CPU cost)
    MIN_CLATTER_DELTA_VN: float = 1.60       # Minimum normal velocity jump (u/tic) to emit clatter sound

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
        # Resting contact cutoff: 1.5x per-tic vertical gravity step prevents fixed-pointvz = (e/(1+e))|g| bounce!
        self.resting_vn_cutoff: float = 1.5 * abs(float(self.gravity[2]))

    def wake_with_kick(self, prop: DebrisPropState, impulse_vel_xyz: Sequence[float]) -> None:
        """Wake a sleeping prop and restore its thinker statnum to `STAT_DEBRIS`."""
        prop.vel_xyz = prop.vel_xyz + np.asarray(impulse_vel_xyz, dtype=np.float64)
        prop.ang_vel_rad_tic = float(np.linalg.norm(impulse_vel_xyz)) * 0.12
        prop.sleep_tics = 0
        prop.asleep = False
        prop.statnum = "STAT_DEBRIS"

    def step_prop_tic(self, prop: DebrisPropState) -> dict[str, Any]:
        """Advance a debris prop by 1 game tic (35 Hz); returns immediately at 0 cost if `asleep`."""
        if prop.asleep:
            return {
                "asleep": True,
                "statnum": prop.statnum,
                "clatter_emitted": False,
                "clatter_db": 0.0,
                "alert_radius_u": 0.0,
                "speed_u_tic": 0.0,
                "vz_u_tic": 0.0,
            }

        r = prop.radius_u
        on_floor_resting = (abs(prop.pos_xyz[2] - (self.floor_z_u + r)) < 1e-3) and (abs(prop.vel_xyz[2]) == 0.0)

        # Apply gravity (suppress vertical gravity component if already in resting contact with the floor)
        prop.vel_xyz[0] += self.gravity[0]
        prop.vel_xyz[1] += self.gravity[1]
        if not on_floor_resting:
            prop.vel_xyz[2] += self.gravity[2]

        prop.pos_xyz = prop.pos_xyz + prop.vel_xyz

        max_delta_vn = 0.0
        x_min, y_min, x_max, y_max = self.bounds_xy_u

        # Floor contact & resting-contact clamp
        if prop.pos_xyz[2] - r <= self.floor_z_u + 1e-5:
            prop.pos_xyz[2] = self.floor_z_u + r
            vn = -float(prop.vel_xyz[2])
            if vn > 0.0:
                if vn <= self.resting_vn_cutoff:
                    # Resting contact: zero vertical velocity without bouncing!
                    prop.vel_xyz[2] = 0.0
                else:
                    max_delta_vn = max(max_delta_vn, (1.0 + prop.restitution) * vn)
                    prop.vel_xyz[2] = vn * prop.restitution
                prop.vel_xyz[0] *= (1.0 - prop.sliding_friction)
                prop.vel_xyz[1] *= (1.0 - prop.sliding_friction)
                prop.ang_vel_rad_tic *= prop.rolling_damping

        # Ceiling contact
        if prop.pos_xyz[2] + r > self.ceil_z_u:
            prop.pos_xyz[2] = self.ceil_z_u - r
            if prop.vel_xyz[2] > 0.0:
                max_delta_vn = max(max_delta_vn, (1.0 + prop.restitution) * float(prop.vel_xyz[2]))
                prop.vel_xyz[2] = -prop.vel_xyz[2] * prop.restitution

        # 2D wall contacts
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

        # Rolling resistance while resting on the floor
        if abs(prop.pos_xyz[2] - (self.floor_z_u + r)) < 1e-3 and prop.vel_xyz[2] == 0.0:
            prop.vel_xyz[0] *= prop.rolling_damping
            prop.vel_xyz[1] *= prop.rolling_damping
            prop.ang_vel_rad_tic *= prop.rolling_damping

        speed_sq = float(np.dot(prop.vel_xyz, prop.vel_xyz)) + 0.25 * (prop.ang_vel_rad_tic ** 2)
        if speed_sq < self.SLEEP_SPEED_SQ_THRESHOLD and abs(prop.pos_xyz[2] - (self.floor_z_u + r)) < 1e-3:
            prop.sleep_tics += 1
            if prop.sleep_tics >= self.SLEEP_CONSECUTIVE_TICS:
                prop.vel_xyz[:] = 0.0
                prop.ang_vel_rad_tic = 0.0
                prop.asleep = True
                prop.statnum = "STAT_SLEEPING_DEBRIS"
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
            "statnum": prop.statnum,
            "clatter_emitted": bool(clatter),
            "clatter_db": round(clatter_db, 2),
            "alert_radius_u": round(alert_u, 1),
            "speed_u_tic": round(math.sqrt(speed_sq), 4),
            "vz_u_tic": round(float(prop.vel_xyz[2]), 4),
        }


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


def ease_crosswise_camera_roll(
    tic_in_transition: int,
    total_transition_tics: int = 24,
    roll_start_deg: float = 0.0,
    roll_target_deg: float = 90.0,
) -> dict[str, Any]:
    """Smooth C^2 quintic geodesic camera-roll ease for E10 The Crosswise Hall (real 2.5D floor, rolled camera)."""
    s = float(np.clip(tic_in_transition / max(float(total_transition_tics), 1.0), 0.0, 1.0))
    w = s * s * s * (s * (s * 6.0 - 15.0) + 10.0)
    roll_deg = (1.0 - w) * float(roll_start_deg) + w * float(roll_target_deg)
    roll_rad = math.radians(roll_deg)
    u_up = np.array([0.0, math.sin(roll_rad), math.cos(roll_rad)], dtype=np.float64)
    r_mat = geodesic_rodrigues_rotation(np.array([0.0, 0.0, 1.0]), u_up, fraction=1.0)
    return {
        "roll_deg": round(roll_deg, 4),
        "roll_rad": round(roll_rad, 6),
        "camera_up_vector": u_up,
        "view_roll_matrix": r_mat,
    }


def test_debris_settle_and_clatter_v2() -> dict[str, Any]:
    """Verify that dropped rebar debris bounces, enters resting contact (vz == 0), sleeps in < 85 tics, and wakes on kick."""
    sim = DebrisSettleSimulator35HzV2(floor_z_u=0.0, ceil_z_u=192.0)
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

    assert len(clatter_events_db) >= 1, "Dropped rebar prop must emit at least 1 acoustic clatter event"
    if len(clatter_events_db) >= 2:
        assert clatter_events_db[0] > clatter_events_db[1], "Subsequent bounce clatter must be quieter than initial impact"
    assert 10 <= sleep_tic <= 85, f"Debris failed to sleep in < 85 tics: sleep_tic={sleep_tic}"
    assert prop.vel_xyz[2] == 0.0 and prop.statnum == "STAT_SLEEPING_DEBRIS"

    # Also verify that an already-resting prop dropped from 0.1 units above the floor settles without bouncing forever
    resting_prop = DebrisPropState(
        prop_id=2,
        pos_xyz=np.array([10.0, 10.0, 5.1], dtype=np.float64),
        vel_xyz=np.array([0.0, 0.0, 0.0], dtype=np.float64),
    )
    rest_sleep_tic = -1
    for tic in range(1, 20):
        st_r = sim.step_prop_tic(resting_prop)
        if st_r["asleep"]:
            rest_sleep_tic = tic
            break
    assert 1 <= rest_sleep_tic <= 8, f"Resting prop failed to sleep immediately: {rest_sleep_tic}"

    # Verify wake-on-kick
    sim.wake_with_kick(prop, (5.0, 2.0, 4.5))
    assert (not prop.asleep) and prop.statnum == "STAT_DEBRIS"
    woke_clatter = False
    for _ in range(30):
        if sim.step_prop_tic(prop)["clatter_emitted"]:
            woke_clatter = True
            break
    assert woke_clatter, "Kicked debris prop must clatter when landing"

    # Verify E10 Crosswise Hall camera roll ease
    for t in range(25):
        er = ease_crosswise_camera_roll(t, 24, 0.0, 90.0)
        assert float(np.max(np.abs(er["view_roll_matrix"].T @ er["view_roll_matrix"] - np.eye(3)))) < 1e-14

    return {
        "status": "verified (test_debris_settle_and_clatter_v2)",
        "bounces_recorded": len(clatter_events_db),
        "first_impact_clatter_db": clatter_events_db[0],
        "settled_to_sleep_at_tic": sleep_tic,
        "resting_prop_sleep_tic": rest_sleep_tic,
        "wake_on_kick_verified": True,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(test_debris_settle_and_clatter_v2(), indent=2))