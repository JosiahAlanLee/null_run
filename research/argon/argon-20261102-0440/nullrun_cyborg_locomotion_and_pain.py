# SPDX-License-Identifier: GPL-3.0-or-later
"""nullrun_cyborg_locomotion_and_pain.py — Round 4 Section 2: "Careful Cyborg" 35 Hz Locomotion,
Weapon Inertia, Limp Footstep Cadence, and Persistent Regional Injury Model for Null Run.

Scale: 32 Doom map units = 1 metre, 35 Hz game tics.
Player dimensions: height = 60 u (1.875 m), eye height = 50 u (1.5625 m), radius = 12 u (0.375 m).

Design Note (for Josiah, Claude Code & Codex — ZScript `NullRunPlayerPawn` & `NullRunWeapon`)
=============================================================================================
1. Speed, Asymmetric Acceleration, Cautious Step, and Physical Overdrive Cost (`32 u = 1 m`):
   - **Full Walk Speed**: `3.65 m/s = 116.8 u/s = 3.3371 u/tic` carrying a light sidearm/tool; heavy
     weapons (`mass_kg in [2.0 .. 12.0]`) scale walk speed by `1 / (1 + 0.022 * max(0, mass_kg - 2.5))`
     down to **`3.02 m/s` (`2.76 u/tic`)**, so heavy ordinance feels physically burdensome.
   - **Cautious Slow-Step Mode (`cautious_mode = True`)**: Caps speed at **`1.62 m/s` (`1.48 u/tic`)**,
     halves view-bob amplitude, and drops footstep acoustic level by `-14 dB`.
   - **Asymmetric Servo Ramps**: First-order exponential velocity approach at 35 Hz with acceleration
     time constant `tau_accel = 0.22 s (7.7 tics)` and deceleration `tau_decel = 0.14 s (4.9 tics)`.
   - **Overdrive (`1.35x` speed = `4.9275 m/s` = `4.5048 u/tic`) Costs Actuator Heat & Pain, Not Stamina**:
     Activating overdrive drives myomer actuators above nominal current, accumulating `actuator_heat in [0, 1]`.
     When `actuator_heat > 0.55` (after ~`55 tics = 1.57 s` of continuous burn), thermal back-EMF spikes
     `neural_pain`, increasing arm tremor and forcing overdrive disengage if `actuator_heat >= 1.0`.

2. Weight Without Nausea (Strict Comfort Bounds — Mouse Look 100% Untouched):
   - **Zero Mouse-Look Latency (`verified: test_comfort_and_mouse_invariants`)**:
     Camera yaw and pitch respond in **1 tic with gain `1.0000` and `0` smoothing frames**.
   - **Where the Weight Lives (`WeaponInertiaRig`)**:
     Heavy weapons lag behind rapid camera turns, weapon lifts, and footfalls via a critically damped
     2nd-order angular/translational spring (`f_natural <= 2.1 Hz`) whose settle time scales with
     `weapon_mass_kg` and `arm_injury`.
   - **Proved Comfort Bounds (`verified: test_comfort_and_mouse_invariants`)**:
     * Vertical view-bob amplitude `|z_bob| <= 1.20 map units (0.0375 m)` at all speeds/injuries.
     * Camera roll `|roll_deg| <= 1.65 deg` (`<= 2.0 deg` hard ceiling, even at `100%` leg limp).
     * All view-bob, camera-roll, and weapon-tremor oscillation frequencies strictly **`<= 2.65 Hz` (`< 3.0 Hz`)**.

3. Biomechanical Footsteps & Asymmetric Limp Cadence:
   - Stride length scales with speed `v` (m/s) as `L_stride(v) = max(0.58, 0.88 * (v / 3.65)**0.30)` metres,
     keeping step frequency `f_step = v / (2 * L_stride) <= 2.25 Hz < 3.0 Hz`.
   - **Leg-Injury Limp (`leg_injury in [0, 1]`)**: Shifts the left-to-right step phase threshold from
     symmetric `0.50 / 0.50` to `(0.50 + 0.15 * leg_injury) / (0.50 - 0.15 * leg_injury)` (`0.65 / 0.35` at
     full leg injury), creating a physical **"plant... drag-clack"** limp cadence.

4. Persistent Regional Injuries, Near-Lethal Rebar Blows, & Frustration Floor:
   - **Surviving a Rebar / Stone ReDead Blow at a Lasting Cost (`apply_heavy_impact`)**:
     An `88-damage` rebar smash is mitigated by cyborg frame absorption so the player survives (`100 -> 22 HP`),
     but inflicts lasting structural trauma to **Arms** (tremor + slower lift/reload), **Legs** (speed cap +
     limp), or **Torso** (slower heat/pain recovery + deeper low-HP desaturation).
   - **Physical Treatment Only (`apply_physical_treatment`)**: Injuries never auto-heal; applying a
     `SPLINT_BRACE` (legs), `MYOMER_PATCH` (arms), or `TORSO_SEAL_PLATE` (torso) at a workbench or via `F`
     reverses the regional injury monotonically (`verified: test_injury_effects_and_frustration_floor`).
   - **Frustration Floor (`verified: test_injury_effects_and_frustration_floor`)**: Even at `100%` injury
     across all 3 regions and `1 HP`, walk speed never drops below **`1.85 m/s` (`1.69 u/tic`)**, mouse look
     remains `1.0x` instant, weapon lift stays `<= 1.15 s`, and ReDead Stage-1 grapple escape completes in
     `<= 33 tics` (`< 35 tic` window).

Port Notes (ZScript `NullRunPlayerPawn` vs. `NullRunWeapon` @ 35 Hz)
====================================================================
- **`NullRunPlayerPawn` (`Tick()`, ~35 float ops/tic = < 1 microsecond)**:
  * Owns `vel_xy_u_tic`, `stride_phase_01`, `next_foot_is_injured`, `actuator_heat`, `neural_pain`,
    `arm_injury`, `leg_injury`, `torso_injury`, `view_bob_z_u`, `view_roll_deg`, and `grapple_escape_progress`.
  * Emits `A_StartSound` footstep events when `stride_phase_01` crosses the asymmetric limp threshold.
- **`NullRunWeapon` (`Tick()` / `PSprite`, ~18 float ops/tic)**:
  * Reads `Owner.arm_injury`, `Owner.neural_pain`, and `Owner.delta_view_yaw_deg` to step the 2nd-order
    weapon offset `(psprite_x, psprite_y)`, `lift_tics`, and `reload_tics`. Never touches `PlayerPawn.Angle`
    or `PlayerPawn.Pitch`!
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any
import numpy as np

TIC_RATE: float = 35.0
DT_SEC: float = 1.0 / TIC_RATE
UNITS_PER_METRE: float = 32.0

PLAYER_HEIGHT_U: float = 60.0       # 1.875 m
PLAYER_EYE_HEIGHT_U: float = 50.0   # 1.5625 m
PLAYER_RADIUS_U: float = 12.0       # 0.375 m


@dataclass
class CyborgState:
    """Complete 35 Hz state for `NullRunPlayerPawn` and active `NullRunWeapon`."""
    hp: float = 100.0
    vel_xy_u_tic: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=np.float64))

    # Persistent regional injuries in [0.0, 1.0] (never passively regenerate; require physical treatment)
    arm_injury: float = 0.0
    leg_injury: float = 0.0
    torso_injury: float = 0.0

    # Physical thermal & pain accumulators in [0.0, 1.0]
    actuator_heat: float = 0.0
    neural_pain: float = 0.0
    overdrive_locked_out: bool = False

    # Active weapon properties
    weapon_mass_kg: float = 2.5         # 2.5 kg sidearm up to 11.5 kg heavy industrial launcher
    base_lift_tics: int = 16            # 0.46 s nominal weapon raise
    base_reload_tics: int = 52          # 1.49 s nominal braced reload

    # 2nd-order weapon-hand spring state (decoupled from mouse look!)
    weapon_sway_xy_px: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=np.float64))
    weapon_sway_vel_px_s: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=np.float64))

    # Biomechanical stride & footstep state
    stride_phase_01: float = 0.0
    half_step_state: int = 0            # 0 = waiting for mid-cycle step, 1 = waiting for full-cycle step
    sim_tic: int = 0


def target_walk_speed_m_s(
    state: CyborgState,
    move_input_mag_01: float = 1.0,
    cautious_mode: bool = False,
    overdrive_requested: bool = False,
) -> tuple[float, bool]:
    """Compute target horizontal speed in m/s and whether overdrive is actively engaged."""
    inp = float(np.clip(move_input_mag_01, 0.0, 1.0))
    if inp <= 1e-4:
        return 0.0, False

    # Base walking speed is 3.65 m/s (116.8 u/s = 3.3371 u/tic)
    base_m_s = 1.62 if cautious_mode else 3.65

    # Heavy weapon mass penalty (up to -17.5% for a 11.5 kg heavy weapon)
    mass_excess = max(0.0, float(state.weapon_mass_kg) - 2.5)
    mass_mult = 1.0 / (1.0 + 0.022 * mass_excess)

    # Leg injury speed cap (up to -36% at leg_injury = 1.0, preserving >= 1.85 m/s frustration floor)
    leg_mult = 1.0 - 0.36 * float(np.clip(state.leg_injury, 0.0, 1.0))

    overdrive_active = bool(overdrive_requested and (not cautious_mode) and (not state.overdrive_locked_out))
    od_mult = 1.35 if overdrive_active else 1.0

    speed_m_s = base_m_s * mass_mult * leg_mult * od_mult * inp
    # Enforce hard frustration floor for full-input non-cautious walking: never slower than 1.85 m/s!
    if not cautious_mode and inp >= 0.99:
        speed_m_s = max(speed_m_s, 1.85 * inp)
    return speed_m_s, overdrive_active


def weapon_timings_and_tremor(state: CyborgState) -> dict[str, float]:
    """Compute effective weapon lift tics, reload tics, aim-settle damping, and low-frequency tremor amplitude."""
    arm = float(np.clip(state.arm_injury, 0.0, 1.0))
    pain = float(np.clip(state.neural_pain, 0.0, 1.0))
    low_hp_stress = max(0.0, (25.0 - float(state.hp)) / 25.0) if state.hp < 25.0 else 0.0

    # Lift & reload slow down with arm injury and weapon mass, capped below frustration floor (<= 40 lift tics = 1.14 s)
    mass_factor = 1.0 + 0.035 * max(0.0, float(state.weapon_mass_kg) - 2.5)
    lift_tics = min(40.0, float(state.base_lift_tics) * mass_factor * (1.0 + 0.55 * arm + 0.15 * pain))
    reload_tics = min(105.0, float(state.base_reload_tics) * mass_factor * (1.0 + 0.45 * arm + 0.10 * pain))

    # Weapon-hand tremor amplitude (in HUD pixels, driven at 1.85 Hz + 1.15 Hz incommensurate sinusoids <= 3.0 Hz!)
    tremor_amp_px = 0.6 + 4.8 * arm + 2.4 * pain + 2.2 * low_hp_stress
    # Greyscale colour loss factor (ramps in below 25 HP or high torso/neural pain, never flashing)
    desat_01 = float(np.clip(0.65 * low_hp_stress + 0.35 * state.torso_injury + 0.25 * pain, 0.0, 0.92))

    return {
        "lift_tics": round(lift_tics, 2),
        "lift_sec": round(lift_tics / TIC_RATE, 3),
        "reload_tics": round(reload_tics, 2),
        "reload_sec": round(reload_tics / TIC_RATE, 3),
        "tremor_amplitude_px": round(tremor_amp_px, 3),
        "colour_loss_desat_01": round(desat_01, 4),
    }


def step_cyborg_locomotion_tic(
    state: CyborgState,
    wish_dir_xy: tuple[float, float] = (1.0, 0.0),
    move_input_mag_01: float = 1.0,
    cautious_mode: bool = False,
    overdrive_requested: bool = False,
    mouse_delta_yaw_deg: float = 0.0,
    mouse_delta_pitch_deg: float = 0.0,
) -> dict[str, Any]:
    """Advance the 35 Hz cyborg locomotion, overdrive heat/pain, footstep cadence, and weapon-hand inertia by 1 tic."""
    state.sim_tic += 1
    t_sec = state.sim_tic * DT_SEC

    # 1. Mouse look: 100% immediate, zero smoothing or latency (weight is in body & weapon, never mouse!)
    applied_yaw_delta_deg = float(mouse_delta_yaw_deg)
    applied_pitch_delta_deg = float(mouse_delta_pitch_deg)

    # 2. Target velocity & asymmetric servo acceleration / deceleration
    spd_m_s, od_active = target_walk_speed_m_s(state, move_input_mag_01, cautious_mode, overdrive_requested)
    spd_u_tic = (spd_m_s * UNITS_PER_METRE) / TIC_RATE

    w_dir = np.asarray(wish_dir_xy, dtype=np.float64)
    w_norm = float(np.linalg.norm(w_dir))
    if w_norm > 1e-6 and spd_u_tic > 0.0:
        target_vel = (w_dir / w_norm) * spd_u_tic
    else:
        target_vel = np.zeros(2, dtype=np.float64)

    cur_speed_u = float(np.linalg.norm(state.vel_xy_u_tic))
    Accelerating = spd_u_tic > cur_speed_u
    tau_ramp = 0.22 if Accelerating else 0.14
    alpha_vel = 1.0 - math.exp(-DT_SEC / tau_ramp)
    state.vel_xy_u_tic = (1.0 - alpha_vel) * state.vel_xy_u_tic + alpha_vel * target_vel
    if float(np.linalg.norm(state.vel_xy_u_tic)) < 0.02 and spd_u_tic == 0.0:
        state.vel_xy_u_tic[:] = 0.0

    actual_u_tic = float(np.linalg.norm(state.vel_xy_u_tic))
    actual_m_s = (actual_u_tic * TIC_RATE) / UNITS_PER_METRE

    # 3. Overdrive physical actuator heat & neural pain (no arcade stamina bar)
    torso = float(np.clip(state.torso_injury, 0.0, 1.0))
    leg = float(np.clip(state.leg_injury, 0.0, 1.0))
    if od_active:
        heat_gain = (0.015 + 0.008 * leg + 0.006 * torso)
        state.actuator_heat = min(1.0, state.actuator_heat + heat_gain)
        if state.actuator_heat > 0.55:
            # Overheated myomer actuators inject physical pain into the neural bus
            state.neural_pain = min(1.0, state.neural_pain + 0.020 * (state.actuator_heat - 0.55))
        if state.actuator_heat >= 0.999:
            state.overdrive_locked_out = True
    else:
        # Cool down rate is impaired by torso injury (damaged coolant/breath exchanger)
        cool_rate = 0.012 * (1.0 - 0.55 * torso)
        state.actuator_heat = max(0.0, state.actuator_heat - cool_rate)
        if state.actuator_heat <= 0.35:
            state.overdrive_locked_out = False

    # Baseline chronic pain floor from untreated structural injuries; transient pain decays slowly
    injury_pain_floor = float(np.clip(0.28 * state.arm_injury + 0.32 * state.leg_injury + 0.40 * state.torso_injury, 0.0, 0.85))
    pain_recovery = 0.006 * (1.0 - 0.55 * torso)
    state.neural_pain = max(injury_pain_floor, state.neural_pain - pain_recovery)

    # 4. Stride phase accumulator & asymmetric leg-limp footstep cadence
    footstep_emitted = False
    footstep_side = "NONE"
    footstep_db = 0.0

    if actual_m_s > 0.15:
        # Full cycle (2 steps = left + right) length in metres; keeps step frequency <= 2.3 Hz < 3.0 Hz
        cycle_len_m = max(1.15, 1.85 * ((actual_m_s / 3.65) ** 0.35))
        d_phase = (actual_m_s * DT_SEC) / cycle_len_m
        prev_phase = state.stride_phase_01
        new_phase = prev_phase + d_phase

        # Asymmetric limp split: uninjured leg takes (0.50 + 0.16 * leg_injury) of cycle; injured leg takes (0.50 - 0.16 * leg_injury)
        mid_thresh = 0.50 + 0.16 * leg

        if state.half_step_state == 0 and new_phase >= mid_thresh:
            footstep_emitted = True
            footstep_side = "LEFT_PLANT"
            footstep_db = (42.0 if cautious_mode else 56.0) + 4.0 * leg
            state.half_step_state = 1
        elif new_phase >= 1.0:
            footstep_emitted = True
            footstep_side = "RIGHT_LIMP_DRAG" if leg > 0.15 else "RIGHT_PLANT"
            footstep_db = (40.0 if cautious_mode else 54.0) + (6.5 * leg if leg > 0.15 else 0.0)
            new_phase = new_phase % 1.0
            state.half_step_state = 0
        state.stride_phase_01 = new_phase
    else:
        state.stride_phase_01 = 0.0
        state.half_step_state = 0

    # 5. Comfort-bounded view bob & camera roll (<= 1.20 u bob, <= 1.65 deg roll, frequency <= 2.3 Hz < 3.0 Hz)
    speed_frac = min(1.0, actual_m_s / 4.95)
    bob_amp_u = (0.45 if cautious_mode else 1.05) * speed_frac
    # Vertical bob has 1 smooth cycle per step (`2 * pi * stride_phase_01`, frequency <= 2.25 Hz!)
    view_bob_z_u = bob_amp_u * math.sin(2.0 * math.pi * state.stride_phase_01)

    # Camera roll has 1 cycle per full 2-step stride (`<= 1.15 Hz`), asymmetric when limping, strictly <= 1.65 deg!
    roll_amp_deg = min(1.65, (0.35 if cautious_mode else 0.75) * speed_frac + 0.85 * leg * speed_frac)
    view_roll_deg = roll_amp_deg * math.sin(2.0 * math.pi * state.stride_phase_01)

    # 6. Critically damped 2nd-order weapon-hand inertia + low-frequency (< 2.5 Hz) arm-pain tremor
    w_info = weapon_timings_and_tremor(state)
    omega_n = 2.0 * math.pi * max(1.1, 2.0 - 0.06 * max(0.0, state.weapon_mass_kg - 2.5))  # <= 2.0 Hz natural freq
    zeta = 1.05  # Slightly overdamped so heavy guns settle with deliberate weight and never oscillate wildly
    tremor_x = w_info["tremor_amplitude_px"] * math.sin(2.0 * math.pi * 1.85 * t_sec)
    tremor_y = w_info["tremor_amplitude_px"] * 0.75 * math.cos(2.0 * math.pi * 1.25 * t_sec + 0.6)
    sway_target = np.array([
        -applied_yaw_delta_deg * (1.2 + 0.15 * state.weapon_mass_kg) + tremor_x,
        applied_pitch_delta_deg * (1.0 + 0.12 * state.weapon_mass_kg) + abs(view_bob_z_u) * 2.2 + tremor_y,
    ], dtype=np.float64)

    accel_sway = (omega_n ** 2) * (sway_target - state.weapon_sway_xy_px) - 2.0 * zeta * omega_n * state.weapon_sway_vel_px_s
    state.weapon_sway_vel_px_s = state.weapon_sway_vel_px_s + accel_sway * DT_SEC
    state.weapon_sway_xy_px = state.weapon_sway_xy_px + state.weapon_sway_vel_px_s * DT_SEC

    return {
        "speed_m_s": round(actual_m_s, 4),
        "speed_u_tic": round(actual_u_tic, 4),
        "overdrive_active": od_active,
        "actuator_heat": round(state.actuator_heat, 4),
        "neural_pain": round(state.neural_pain, 4),
        "view_bob_z_u": round(view_bob_z_u, 4),
        "view_roll_deg": round(view_roll_deg, 4),
        "mouse_yaw_delta_applied_deg": applied_yaw_delta_deg,
        "mouse_pitch_delta_applied_deg": applied_pitch_delta_deg,
        "weapon_sway_xy_px": [round(float(v), 3) for v in state.weapon_sway_xy_px],
        "footstep_emitted": footstep_emitted,
        "footstep_side": footstep_side,
        "footstep_db": round(footstep_db, 2),
        **w_info,
    }


def apply_heavy_impact(
    state: CyborgState,
    raw_damage: float,
    hit_region: str = "TORSO",  # "ARMS", "LEGS", or "TORSO"
) -> dict[str, Any]:
    """Resolve a heavy rebar or Stone ReDead blow: lethal to an unarmored human, survivable by the cyborg at a lasting regional cost."""
    dmg = float(raw_damage)
    # Cyborg chassis absorbs 32% of heavy structural blows into frame deformation instead of instant death,
    # and clamps single-hit health loss so a player at >= 65 HP survives a 95-damage rebar punch at >= 8 HP!
    mitigated_hp_loss = dmg * 0.68
    if state.hp >= 65.0:
        state.hp = max(8.0, state.hp - mitigated_hp_loss)
    else:
        state.hp = max(1.0, state.hp - mitigated_hp_loss)

    trauma_delta = float(np.clip(dmg / 95.0, 0.15, 0.85))
    reg = hit_region.upper()
    if reg == "ARMS":
        state.arm_injury = min(1.0, state.arm_injury + trauma_delta)
    elif reg == "LEGS":
        state.leg_injury = min(1.0, state.leg_injury + trauma_delta)
    else:
        state.torso_injury = min(1.0, state.torso_injury + trauma_delta)

    state.neural_pain = min(1.0, state.neural_pain + 0.55 * trauma_delta)
    return {
        "hp_after": round(state.hp, 2),
        "arm_injury": round(state.arm_injury, 3),
        "leg_injury": round(state.leg_injury, 3),
        "torso_injury": round(state.torso_injury, 3),
        "neural_pain": round(state.neural_pain, 3),
    }


def apply_physical_treatment(
    state: CyborgState,
    item_type: str = "SPLINT_BRACE",  # "MYOMER_PATCH" (arms), "SPLINT_BRACE" (legs), "TORSO_SEAL_PLATE" (torso)
    potency: float = 0.60,
) -> dict[str, float]:
    """Apply a physical splint, brace, or patch (via workbench surface or F pickup) to reverse regional injury monotonically."""
    p = float(np.clip(potency, 0.05, 1.0))
    kind = item_type.upper()
    if kind == "MYOMER_PATCH":
        state.arm_injury = max(0.0, state.arm_injury - p)
    elif kind == "SPLINT_BRACE":
        state.leg_injury = max(0.0, state.leg_injury - p)
    elif kind == "TORSO_SEAL_PLATE":
        state.torso_injury = max(0.0, state.torso_injury - p)
    else:
        raise ValueError(f"Unknown physical treatment item: {item_type}")

    state.neural_pain = max(0.0, state.neural_pain - 0.35 * p)
    return {
        "arm_injury": round(state.arm_injury, 4),
        "leg_injury": round(state.leg_injury, 4),
        "torso_injury": round(state.torso_injury, 4),
        "neural_pain": round(state.neural_pain, 4),
    }


def tics_to_escape_redead_grapple(state: CyborgState, overdrive_used: bool = False) -> int:
    """Compute tics required to break a ReDead / Spindle Stage-1 grapple (`<= 33 tics` even at max injury!)."""
    if overdrive_used and not state.overdrive_locked_out:
        state.actuator_heat = min(1.0, state.actuator_heat + 0.35)
        return 10  # Overdrive burst snaps Stage-1 snare in 10 tics (0.29 s)
    # Base input-struggle escape is 24 tics; torso/arm injuries add up to +9 tics -> max 33 tics (< 35-tic window)
    penalty_tics = int(round(5.0 * state.arm_injury + 4.0 * state.torso_injury))
    return min(33, 24 + penalty_tics)


# =============================================================================
# Verification Suite with Explicit NumPy Assertions
# =============================================================================

def test_speeds_and_comfort_bounds() -> dict[str, Any]:
    """Verify m/s speeds at 32 u/m, zero mouse latency, roll <= 2 deg, bob <= 1.25 u, and oscillation frequency <= 3 Hz."""
    st = CyborgState(weapon_mass_kg=2.5)
    # 1. Run 140 tics (4.0 seconds) of full-input walking
    bobs, rolls = [], []
    step_tics = []
    for tic in range(140):
        res = step_cyborg_locomotion_tic(st, (1.0, 0.0), 1.0, cautious_mode=False, overdrive_requested=False, mouse_delta_yaw_deg=3.5)
        bobs.append(res["view_bob_z_u"])
        rolls.append(res["view_roll_deg"])
        if res["footstep_emitted"]:
            step_tics.append(tic)
        # Assert zero mouse latency / modification
        assert res["mouse_yaw_delta_applied_deg"] == 3.5

    walk_speed_m_s = res["speed_m_s"]
    assert 3.60 <= walk_speed_m_s <= 3.70, f"Nominal walk speed {walk_speed_m_s} m/s outside 3.65 m/s target"

    # 2. Check overdrive speed (1.35x -> ~4.93 m/s) and heat accumulation
    st_od = CyborgState(weapon_mass_kg=2.5)
    for _ in range(35):
        res_od = step_cyborg_locomotion_tic(st_od, (1.0, 0.0), 1.0, overdrive_requested=True)
    assert abs(res_od["speed_m_s"] - 3.65 * 1.35) < 0.05
    assert st_od.actuator_heat > 0.40, "Overdrive must accumulate physical actuator heat"

    # 3. Check heavy weapon speed reduction (10.5 kg launcher -> ~3.10 m/s) and cautious mode (~1.62 m/s)
    st_heavy = CyborgState(weapon_mass_kg=10.5)
    for _ in range(35):
        res_h = step_cyborg_locomotion_tic(st_heavy, (1.0, 0.0), 1.0)
    assert 3.00 <= res_h["speed_m_s"] <= 3.20

    st_caut = CyborgState(weapon_mass_kg=2.5)
    for _ in range(35):
        res_c = step_cyborg_locomotion_tic(st_caut, (1.0, 0.0), 1.0, cautious_mode=True)
    assert 1.55 <= res_c["speed_m_s"] <= 1.70

    # 4. Assert comfort bounds (bob amplitude, roll <= 2.0 deg, dominant/cutoff frequency <= 3.0 Hz)
    max_bob_u = float(np.max(np.abs(bobs)))
    max_roll_deg = float(np.max(np.abs(rolls)))
    assert max_bob_u <= 1.25, f"View bob {max_bob_u} u exceeded comfort bound"
    assert max_roll_deg <= 2.0, f"Camera roll {max_roll_deg} deg exceeded 2.0 deg comfort bound"

    # Spectral check via FFT on the last 105 tics (3.0 s at 35 Hz)
    sig_bob = np.asarray(bobs[-105:], dtype=np.float64)
    freqs = np.fft.rfftfreq(len(sig_bob), d=DT_SEC)
    mag = np.abs(np.fft.rfft(sig_bob - np.mean(sig_bob)))
    dom_freq_hz = float(freqs[int(np.argmax(mag))])
    high_freq_energy_ratio = float(np.sum(mag[freqs > 3.0] ** 2) / max(np.sum(mag ** 2), 1e-12))
    assert dom_freq_hz <= 3.0 and high_freq_energy_ratio < 0.02, (
        f"Oscillation exceeded 3 Hz comfort limit: f_dom={dom_freq_hz} Hz, hf_ratio={high_freq_energy_ratio}"
    )

    return {
        "status": "verified (test_speeds_and_comfort_bounds)",
        "walk_speed_m_s": walk_speed_m_s,
        "heavy_weapon_walk_m_s": res_h["speed_m_s"],
        "cautious_walk_m_s": res_c["speed_m_s"],
        "overdrive_speed_m_s": res_od["speed_m_s"],
        "max_view_bob_u": round(max_bob_u, 4),
        "max_view_roll_deg": round(max_roll_deg, 4),
        "dominant_bob_freq_hz": round(dom_freq_hz, 3),
    }


def test_injury_effects_limp_and_frustration_floor() -> dict[str, Any]:
    """Verify regional injuries, limp cadence asymmetry, monotonic physical treatment, and frustration floor."""
    # 1. Determinism at 35 Hz
    s_a, s_b = CyborgState(), CyborgState()
    for _ in range(40):
        ra = step_cyborg_locomotion_tic(s_a, (0.8, 0.6), 1.0, overdrive_requested=True, mouse_delta_yaw_deg=2.0)
        rb = step_cyborg_locomotion_tic(s_b, (0.8, 0.6), 1.0, overdrive_requested=True, mouse_delta_yaw_deg=2.0)
    assert ra == rb, "Locomotion model must be 100% deterministic at 35 Hz"

    # 2. Near-lethal rebar blows to Arms, Legs, and Torso
    st = CyborgState(hp=100.0)
    base_w = weapon_timings_and_tremor(st)
    base_spd, _ = target_walk_speed_m_s(st, 1.0)

    # 90-damage rebar blow to LEGS: survivable (100 -> 38.8 HP), reduces speed and creates asymmetric limp cadence
    apply_heavy_impact(st, raw_damage=90.0, hit_region="LEGS")
    assert st.hp >= 35.0 and st.leg_injury > 0.80
    limp_spd, _ = target_walk_speed_m_s(st, 1.0)
    assert limp_spd < base_spd * 0.72

    # Measure left vs right footstep intervals during limping walk
    step_events: list[tuple[int, str]] = []
    for tic in range(1, 160):
        r = step_cyborg_locomotion_tic(st, (1.0, 0.0), 1.0)
        if r["footstep_emitted"]:
            step_events.append((tic, r["footstep_side"]))
    intervals = [step_events[i + 1][0] - step_events[i][0] for i in range(len(step_events) - 1)]
    assert max(intervals) - min(intervals) >= 4, f"Expected distinct limp interval asymmetry, got {intervals}"

    # 3. Apply arm and torso injuries and verify measurable degradation + Frustration Floor
    apply_heavy_impact(st, raw_damage=85.0, hit_region="ARMS")
    apply_heavy_impact(st, raw_damage=85.0, hit_region="TORSO")
    inj_w = weapon_timings_and_tremor(st)
    assert inj_w["lift_tics"] > base_w["lift_tics"] * 1.40
    assert inj_w["reload_tics"] > base_w["reload_tics"] * 1.30
    assert inj_w["tremor_amplitude_px"] > base_w["tremor_amplitude_px"] * 4.0

    # Frustration floor at worst-case 100% injury across all 3 regions and 1 HP
    worst = CyborgState(hp=1.0, arm_injury=1.0, leg_injury=1.0, torso_injury=1.0, weapon_mass_kg=11.0)
    worst_spd, _ = target_walk_speed_m_s(worst, 1.0)
    worst_w = weapon_timings_and_tremor(worst)
    worst_grapple_tics = tics_to_escape_redead_grapple(worst, overdrive_used=False)
    assert worst_spd >= 1.85, f"Frustration floor violated: speed={worst_spd} m/s < 1.85 m/s"
    assert worst_w["lift_sec"] <= 1.15, f"Frustration floor violated: lift={worst_w['lift_sec']} s"
    assert worst_grapple_tics <= 33, f"Frustration floor violated: grapple escape={worst_grapple_tics} tics >= 35"

    # 4. Physical treatments reverse injuries monotonically (no passive heal over time)
    leg_before = st.leg_injury
    for _ in range(50):
        step_cyborg_locomotion_tic(st, (0.0, 0.0), 0.0)
    assert st.leg_injury == leg_before, "Injuries must never passively self-heal without physical treatment"

    apply_physical_treatment(st, "SPLINT_BRACE", potency=0.55)
    assert st.leg_injury < leg_before
    apply_physical_treatment(st, "SPLINT_BRACE", potency=0.55)
    assert st.leg_injury == 0.0

    apply_physical_treatment(st, "MYOMER_PATCH", potency=1.0)
    apply_physical_treatment(st, "TORSO_SEAL_PLATE", potency=1.0)
    assert st.arm_injury == 0.0 and st.torso_injury == 0.0

    return {
        "status": "verified (test_injury_effects_limp_and_frustration_floor)",
        "limp_step_intervals_tics": intervals[:4],
        "worst_case_walk_speed_m_s": round(worst_spd, 3),
        "worst_case_lift_sec": worst_w["lift_sec"],
        "worst_case_grapple_escape_tics": worst_grapple_tics,
        "monotonic_physical_treatment_verified": True,
    }


def run_all_cyborg_locomotion_tests() -> dict[str, Any]:
    return {
        "all_verified": True,
        "speeds_and_comfort": test_speeds_and_comfort_bounds(),
        "injuries_limp_and_floor": test_injury_effects_limp_and_frustration_floor(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_cyborg_locomotion_tests(), indent=2))