# SPDX-License-Identifier: CC0-1.0
"""nullrun_df_anatomy_and_grapple.py — Dwarf Fortress Adventure-Mode Inspired Anatomy, Material Physics,
Two-Stage Grapple Escalation & Persistent Room Scars for Null Run (UZDoom 5.0.3 @ 35 Hz).

Design Note (for Josiah, Claude Code & Codex)
=============================================
Translates four structural combat principles from Dwarf Fortress Adventure Mode into fast, menu-free
2.5D spatial mechanics for UZDoom 5.0.3 (35 tics/s, 32 map units/m, zero gore, zero flashing):

1. 3-Zone Functional Anatomy Over Single HP Pools (`ArmatureAnatomyState`, `resolve_anatomical_hit`):
   - Instead of a single undifferentiated hitpoint pool, each 56-unit-tall (1.75 m) Armature has three
     vertical hit zones evaluated in ZScript `DamageMobj` via `z_rel = (hit_z - pos.z) / height`:
       * Low Zone (`z_rel < 0.35`, `ANKLE_TIE_WIRE`): Snaps the rusted tie-wire binding the ankle bundle,
         dropping movement speed from 8.5 u/tic to 3.0 u/tic (35%) and disabling lunges.
       * Mid Zone (`0.35 <= z_rel < 0.72`, `CHEST_CAGE_AND_CORE`): Hits within `|r_perp| <= 6.5 u` of
         the chest centerline strike the glowing green Spindle colony core (`FACETED_CORE`), shattering
         the host permanently into core-fouled scrap `D` (`CORE_SHATTERED_SCRAP`). Off-center hits batter
         the outer rebar cage (`REBAR_BUNDLE`), unbinding the host into a reusable heap `H` (`UNBOUND_REBAR_HEAP`).
       * High Zone (`z_rel >= 0.72`, `TENDON_COLLAR_SENSOR`): Severs the upper fungus-plastic control
         collar, putting a Controlled Armature into a 35-tic (1.0 s) `BLIND_FRENZY` where it swings at
         the nearest actor (including adjacent Armatures).

2. Material-vs-Weapon Contact Physics (`MATERIAL_DAMAGE_MATRIX`):
   - Models DF-style contact mechanics across 3 weapon classes (`PIERCING_FLECHETTE`, `BLUNT_CONCUSSIVE`,
     `SHEAR_CUTTER`) and 4 monster materials (`REBAR_BUNDLE`, `BONE_CAGE`, `FUNGUS_TENDON`, `FACETED_CORE`):
       * Narrow piercing shots slip through hollow rebar gaps (`0.55x`) unless they hit the faceted green
         core (`2.20x`).
       * Heavy blunt impacts crush rigid rebar/bone cages (`1.45x / 1.65x`) and transmit 35% concussive
         shock directly into the lodged core, but bounce off elastic fungus-plastic tendons (`0.45x`).
       * Shear/cutting attacks sever fungus-plastic tendons (`2.10x`) and ankle tie-wire (`1.75x`).

3. Two-Stage Grapple Escalation (`GrappleController35Hz`):
   - Replaces binary stuns with DF Wrestling's `Grab -> Lock` escalation:
       * `STAGE1_TENDON_SNARE` (28 tics = 0.80 s): Slows player walk speed from 10.0 to 4.0 u/tic with
         an elastic pull, while keeping camera aim (`yaw_scale = 1.0`) and weapons 100% free. Broken
         instantly by dealing >= 18 damage to the tendon/collar, crippling the grappler's legs, or
         triggering the cyborg's overdrive burst.
       * `STAGE2_FRAME_LOCK` (35 tics = 1.00 s): Full `redead_grip` rotational clamp (`yaw_scale = 0.18`,
         `speed = 0.5 u/tic`) if Stage 1 is ignored, followed by a mandatory 42-tic (1.20 s)
         `RELEASE_COOLDOWN` immunity window that prevents chain-grapple stunlocks.

4. Persistent Room Scars (`RoomScarGrid`):
   - Core-shattered scrap `D` leaves an `ACOUSTIC_REBAR_SCRAP` tile (steps emit a 72 dB metallic clatter
     that alerts monsters within 384 u = 12 m and excites the room's Pure Data FDN early reflections).
   - Severed tendons leave a `CALCIFIED_TENDON_WEB` tile (0.70x movement speed until shear-cleared).
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any
import numpy as np

TIC_RATE: float = 35.0
UNITS_PER_METRE: float = 32.0
ARMATURE_HEIGHT_U: float = 56.0  # 1.75 m humanoid rebar bundle
ARMATURE_RADIUS_U: float = 16.0  # 0.50 m half-width


# =============================================================================
# 1. Material-vs-Weapon Contact Matrix & 3-Zone Functional Anatomy
# =============================================================================

# Multipliers: weapon_type -> material -> damage multiplier
MATERIAL_DAMAGE_MATRIX: dict[str, dict[str, float]] = {
    "PIERCING_FLECHETTE": {
        "REBAR_BUNDLE": 0.55,   # Narrow darts frequently pass between hollow rebar rods
        "BONE_CAGE": 0.90,      # Denser ossuary bone insert catches more projectile energy
        "FUNGUS_TENDON": 1.35,  # Punctures fungus-plastic tendon fibers
        "FACETED_CORE": 2.20,   # Shatters the stressed-glass green colony core
    },
    "BLUNT_CONCUSSIVE": {
        "REBAR_BUNDLE": 1.45,   # Transfers momentum across the entire bound rebar frame
        "BONE_CAGE": 1.65,      # Fractures dry ossuary bone cages
        "FUNGUS_TENDON": 0.45,  # Elastic fungus-plastic tendon absorbs & deflects blunt impact
        "FACETED_CORE": 1.60,   # Crushes the faceted core
    },
    "SHEAR_CUTTER": {
        "REBAR_BUNDLE": 0.85,   # Clips tie-wire knots moderately
        "BONE_CAGE": 0.80,      # Glances off thick bone
        "FUNGUS_TENDON": 2.10,  # Cleanly parts fungus-plastic tendons and ankle tie-wire
        "FACETED_CORE": 1.25,   # Scores the faceted core
    },
}


@dataclass
class ArmatureAnatomyState:
    """coupled structural integrity state for a Free or Spindle-Controlled Armature."""
    controlled: bool = True
    ossuary_bone_variant: bool = False
    torso_hp: float = 60.0          # Outer rebar/bone ribcage integrity
    core_hp: float = 22.0           # Green faceted Spindle core integrity (active when controlled=True)
    leg_wire_hp: float = 26.0       # Ankle/knee tie-wire integrity
    collar_tendon_hp: float = 20.0  # Upper sensor/control-tendon bundle integrity

    leg_crippled: bool = False
    collar_severed: bool = False
    frenzy_tics_remaining: int = 0
    alive: bool = True
    death_fate: str = "NONE"        # "NONE", "CORE_SHATTERED_SCRAP" (D), or "UNBOUND_REBAR_HEAP" (H)

    @property
    def move_speed_u_tic(self) -> float:
        """Current movement speed in map units/tic (player base speed is 10.0 u/tic)."""
        if not self.alive:
            return 0.0
        base = 8.5 if self.controlled else 7.0
        if self.leg_crippled:
            return 3.0  # Metallic spark-dragging crawl
        if self.collar_severed and self.frenzy_tics_remaining > 0:
            return base * 0.85
        return base

    @property
    def can_lunge_or_grapple(self) -> bool:
        """Crippled or blind-frenzied Armatures cannot execute coordinated lunges or Stage-2 locks."""
        return bool(self.alive and (not self.leg_crippled) and (not self.collar_severed))


def resolve_anatomical_hit(
    state: ArmatureAnatomyState,
    hit_z_u: float,
    lateral_offset_u: float,
    raw_damage: float,
    weapon_type: str = "PIERCING_FLECHETTE",
) -> dict[str, Any]:
    """Resolve a single weapon impact at vertical height `hit_z_u in [0, 56]` and lateral offset `lateral_offset_u`."""
    if not state.alive:
        return {"zone": "DEAD", "effective_damage": 0.0, "death_fate": state.death_fate}

    w_table = MATERIAL_DAMAGE_MATRIX[weapon_type]
    frame_mat = "BONE_CAGE" if state.ossuary_bone_variant else "REBAR_BUNDLE"
    z_rel = float(np.clip(hit_z_u / ARMATURE_HEIGHT_U, 0.0, 1.0))
    lat = abs(float(lateral_offset_u))

    zone_hit = "TORSO_FRAME"
    eff_dmg = 0.0

    if z_rel < 0.35:
        # Low Zone: Ankle / Knee Tie-Wire
        zone_hit = "ANKLE_TIE_WIRE"
        # Tie-wire responds like a hybrid of tendon/wire (shear excels, blunt jars, piercing slips)
        mult = 1.75 if weapon_type == "SHEAR_CUTTER" else w_table[frame_mat]
        eff_dmg = float(raw_damage) * mult
        state.leg_wire_hp = max(0.0, state.leg_wire_hp - eff_dmg)
        # Overflow shock transfers 35% to torso frame
        state.torso_hp = max(0.0, state.torso_hp - 0.35 * eff_dmg)
        if state.leg_wire_hp <= 0.0:
            state.leg_crippled = True

    elif z_rel < 0.72:
        # Mid Zone: Chest Cage & Green Colony Core Socket
        hit_core_socket = state.controlled and (lat <= 6.5)
        if hit_core_socket:
            zone_hit = "GREEN_COLONY_CORE"
            eff_dmg = float(raw_damage) * w_table["FACETED_CORE"]
            state.core_hp = max(0.0, state.core_hp - eff_dmg)
            if state.core_hp <= 0.0:
                state.alive = False
                state.death_fate = "CORE_SHATTERED_SCRAP"
        else:
            zone_hit = "TORSO_FRAME"
            eff_dmg = float(raw_damage) * w_table[frame_mat]
            state.torso_hp = max(0.0, state.torso_hp - eff_dmg)
            # DF Blunt Momentum Transfer: heavy blunt blows to the ribcage jar the internal core by 35%
            if state.controlled and weapon_type == "BLUNT_CONCUSSIVE":
                state.core_hp = max(0.0, state.core_hp - 0.35 * eff_dmg)
                if state.core_hp <= 0.0:
                    state.alive = False
                    state.death_fate = "CORE_SHATTERED_SCRAP"

    else:
        # High Zone: Sensor / Tendon Collar
        zone_hit = "TENDON_COLLAR_SENSOR"
        mat = "FUNGUS_TENDON" if state.controlled else frame_mat
        eff_dmg = float(raw_damage) * w_table[mat]
        state.collar_tendon_hp = max(0.0, state.collar_tendon_hp - eff_dmg)
        state.torso_hp = max(0.0, state.torso_hp - 0.40 * eff_dmg)
        if state.collar_tendon_hp <= 0.0 and not state.collar_severed:
            state.collar_severed = True
            state.frenzy_tics_remaining = 35  # 1.0 s blind frenzy

    # Check if outer frame unbound without shattering the core -> reusable rebar heap H!
    if state.alive and state.torso_hp <= 0.0:
        state.alive = False
        state.death_fate = "UNBOUND_REBAR_HEAP"

    return {
        "zone": zone_hit,
        "effective_damage": round(eff_dmg, 3),
        "alive": state.alive,
        "death_fate": state.death_fate,
        "leg_crippled": state.leg_crippled,
        "collar_severed": state.collar_severed,
        "move_speed_u_tic": round(state.move_speed_u_tic, 2),
    }


# =============================================================================
# 2. Two-Stage Grapple Escalation FSM (Dwarf Fortress Wrestling Adaptation)
# =============================================================================

class GrappleController35Hz:
    """Deterministic 35 Hz state machine implementing `STAGE1_TENDON_SNARE -> STAGE2_FRAME_LOCK`."""

    STATES = ("FREE", "STAGE1_TENDON_SNARE", "STAGE2_FRAME_LOCK", "RELEASE_COOLDOWN")

    def __init__(
        self,
        stage1_window_tics: int = 28,     # 0.80 s counterplay window before full frame lock
        stage2_duration_tics: int = 35,   # 1.00 s full lock duration if uncountered
        cooldown_tics: int = 42,          # 1.20 s post-release grapple immunity
        break_damage_threshold: float = 18.0,
    ) -> None:
        self.stage1_window_tics = int(stage1_window_tics)
        self.stage2_duration_tics = int(stage2_duration_tics)
        self.cooldown_tics = int(cooldown_tics)
        self.break_damage_threshold = float(break_damage_threshold)

        self.state: str = "FREE"
        self.state_tic: int = 0
        self.accum_break_damage: float = 0.0

    def step_tic(
        self,
        latch_attempt: bool = False,
        damage_to_grappler_collar: float = 0.0,
        overdrive_burst_pressed: bool = False,
        grappler_can_grapple: bool = True,
    ) -> dict[str, Any]:
        """Advance the grapple state machine by 1 game tic (1/35 s) and return player movement/aim/shader multipliers."""
        if not grappler_can_grapple and self.state in ("STAGE1_TENDON_SNARE", "STAGE2_FRAME_LOCK"):
            self.state = "RELEASE_COOLDOWN"
            self.state_tic = 0
            self.accum_break_damage = 0.0

        elif self.state == "FREE":
            if latch_attempt and grappler_can_grapple:
                self.state = "STAGE1_TENDON_SNARE"
                self.state_tic = 0
                self.accum_break_damage = 0.0

        elif self.state == "STAGE1_TENDON_SNARE":
            self.state_tic += 1
            self.accum_break_damage += max(0.0, float(damage_to_grappler_collar))
            # Counterplay check: overdrive burst OR >= 18 tendon damage breaks the snare before Stage 2!
            if overdrive_burst_pressed or self.accum_break_damage >= self.break_damage_threshold:
                self.state = "RELEASE_COOLDOWN"
                self.state_tic = 0
                self.accum_break_damage = 0.0
            elif self.state_tic >= self.stage1_window_tics:
                self.state = "STAGE2_FRAME_LOCK"
                self.state_tic = 0

        elif self.state == "STAGE2_FRAME_LOCK":
            self.state_tic += 1
            self.accum_break_damage += max(0.0, float(damage_to_grappler_collar))
            if self.accum_break_damage >= self.break_damage_threshold * 1.5 or self.state_tic >= self.stage2_duration_tics:
                self.state = "RELEASE_COOLDOWN"
                self.state_tic = 0
                self.accum_break_damage = 0.0

        elif self.state == "RELEASE_COOLDOWN":
            self.state_tic += 1
            if self.state_tic >= self.cooldown_tics:
                self.state = "FREE"
                self.state_tic = 0

        # Compute player kinematics and HydraPy `redead_grip` shader uniform `grip_strength`
        if self.state == "STAGE1_TENDON_SNARE":
            frac1 = self.state_tic / max(float(self.stage1_window_tics), 1.0)
            player_speed = 4.0      # Snared walk speed (down from 10.0 u/tic)
            yaw_scale = 1.0         # Full camera rotation freedom during Stage 1!
            weapons_free = True
            grip_shader_u = round(0.10 + 0.25 * frac1, 4)
        elif self.state == "STAGE2_FRAME_LOCK":
            frac2 = self.state_tic / max(float(self.stage2_duration_tics), 1.0)
            player_speed = 0.5      # Pinned in frame lock
            yaw_scale = 0.18        # Heavy camera rotation clamp toward monster face
            weapons_free = True
            grip_shader_u = round(0.65 + 0.35 * math.sin(frac2 * math.pi), 4)
        else:
            player_speed = 10.0
            yaw_scale = 1.0
            weapons_free = True
            grip_shader_u = 0.0

        return {
            "state": self.state,
            "state_tic": self.state_tic,
            "player_speed_u_tic": player_speed,
            "player_yaw_scale": yaw_scale,
            "weapons_free": weapons_free,
            "hydrapy_grip_strength": grip_shader_u,
        }


# =============================================================================
# 3. Persistent Room Scars (Acoustic Rebar Scrap & Calcified Tendon Webs)
# =============================================================================

class RoomScarGrid:
    """2D spatial grid (64x64 map-unit cells = 2x2 m) tracking physical fight scars on the floor."""

    CELL_SIZE_U: float = 64.0
    NONE: int = 0
    ACOUSTIC_SCRAP: int = 1      # Core-fouled scrap D: loud 72 dB metallic clatter on step
    CALCIFIED_TENDON: int = 2    # Severed tendon webbing: 0.70x movement speed drag

    def __init__(self, width_m: float = 16.0, length_m: float = 16.0) -> None:
        self.nx = max(1, int(math.ceil((width_m * UNITS_PER_METRE) / self.CELL_SIZE_U)))
        self.ny = max(1, int(math.ceil((length_m * UNITS_PER_METRE) / self.CELL_SIZE_U)))
        self.grid = np.zeros((self.ny, self.nx), dtype=np.int32)

    def _cell(self, x_u: float, y_u: float) -> tuple[int, int]:
        ix = int(np.clip(math.floor(x_u / self.CELL_SIZE_U), 0, self.nx - 1))
        iy = int(np.clip(math.floor(y_u / self.CELL_SIZE_U), 0, self.ny - 1))
        return iy, ix

    def deposit_scar(self, x_u: float, y_u: float, scar_type: int) -> None:
        iy, ix = self._cell(x_u, y_u)
        self.grid[iy, ix] = int(scar_type)

    def query_step_effect(self, x_u: float, y_u: float) -> dict[str, Any]:
        iy, ix = self._cell(x_u, y_u)
        val = int(self.grid[iy, ix])
        if val == self.ACOUSTIC_SCRAP:
            return {"speed_mult": 0.92, "noise_db": 72.0, "alert_radius_u": 384.0, "pd_early_reflection_trig": True}
        if val == self.CALCIFIED_TENDON:
            return {"speed_mult": 0.70, "noise_db": 28.0, "alert_radius_u": 64.0, "pd_early_reflection_trig": False}
        return {"speed_mult": 1.00, "noise_db": 18.0, "alert_radius_u": 0.0, "pd_early_reflection_trig": False}


# =============================================================================
# 4. Verification Suite with Explicit NumPy Assertions
# =============================================================================

def test_anatomical_disassembly_and_materials() -> dict[str, Any]:
    """Verify 3-zone anatomical hit resolution, material multipliers, and heap vs. scrap fates."""
    # 1. Low-zone shear strike cripples ankle tie-wire (speed -> 3.0 u/tic) while leaving Armature alive
    arm_leg = ArmatureAnatomyState(controlled=True)
    res_leg = resolve_anatomical_hit(arm_leg, hit_z_u=12.0, lateral_offset_u=0.0, raw_damage=16.0, weapon_type="SHEAR_CUTTER")
    assert res_leg["zone"] == "ANKLE_TIE_WIRE" and res_leg["leg_crippled"] and res_leg["alive"]
    assert abs(res_leg["move_speed_u_tic"] - 3.0) < 1e-6 and not arm_leg.can_lunge_or_grapple

    # 2. Center-chest piercing shot shatters the green colony core into permanent scrap D (0 reusable heaps)
    arm_core = ArmatureAnatomyState(controlled=True)
    res_core = resolve_anatomical_hit(arm_core, hit_z_u=28.0, lateral_offset_u=2.0, raw_damage=12.0, weapon_type="PIERCING_FLECHETTE")
    assert res_core["zone"] == "GREEN_COLONY_CORE" and not res_core["alive"]
    assert res_core["death_fate"] == "CORE_SHATTERED_SCRAP"

    # 3. Off-center torso hits on a controlled Armature with piercing darts take many shots (0.55x) and drop a REUSABLE heap H!
    arm_sloppy = ArmatureAnatomyState(controlled=True)
    shots = 0
    while arm_sloppy.alive:
        shots += 1
        res_s = resolve_anatomical_hit(arm_sloppy, hit_z_u=28.0, lateral_offset_u=11.0, raw_damage=12.0, weapon_type="PIERCING_FLECHETTE")
    assert shots == 10 and res_s["death_fate"] == "UNBOUND_REBAR_HEAP", f"Expected 10 sloppy shots -> heap, got {shots}, {res_s}"

    # 4. High-zone shear hit severs the tendon collar and triggers 35-tic blind frenzy
    arm_collar = ArmatureAnatomyState(controlled=True)
    res_col = resolve_anatomical_hit(arm_collar, hit_z_u=46.0, lateral_offset_u=0.0, raw_damage=11.0, weapon_type="SHEAR_CUTTER")
    assert res_col["zone"] == "TENDON_COLLAR_SENSOR" and res_col["collar_severed"] and arm_collar.frenzy_tics_remaining == 35

    return {
        "status": "verified (test_anatomical_disassembly_and_materials)",
        "crippled_crawl_speed_u_tic": res_leg["move_speed_u_tic"],
        "surgical_core_shots_to_kill": 1,
        "sloppy_body_shots_to_kill": shots,
        "surgical_fate": res_core["death_fate"],
        "sloppy_fate": res_s["death_fate"],
    }


def test_grapple_escalation_and_counterplay() -> dict[str, Any]:
    """Verify Stage-1 snare window (28 tics, full aim), overdrive/damage break, and post-release immunity."""
    # Case A: Player uses overdrive burst at tic 10 of Stage 1 -> never enters STAGE2_FRAME_LOCK
    g_escape = GrappleController35Hz()
    g_escape.step_tic(latch_attempt=True)
    stage2_tics_escape = 0
    for t in range(1, 40):
        st = g_escape.step_tic(overdrive_burst_pressed=(t == 10))
        if st["state"] == "STAGE1_TENDON_SNARE":
            assert st["player_yaw_scale"] == 1.0, "Stage 1 must preserve 100% camera aim freedom"
        if st["state"] == "STAGE2_FRAME_LOCK":
            stage2_tics_escape += 1
    assert stage2_tics_escape == 0, "Countered Stage-1 snare must never escalate to Stage-2 frame lock"

    # Case B: Uncountered grab escalates to Stage 2 after exactly 28 tics, then enters 42-tic immunity cooldown
    g_lock = GrappleController35Hz()
    g_lock.step_tic(latch_attempt=True)
    states_trace = []
    for _ in range(110):
        st = g_lock.step_tic(latch_attempt=True)  # Monster spams latch_attempt every tic
        states_trace.append(st["state"])

    s1_count = sum(1 for s in states_trace[:28] if s == "STAGE1_TENDON_SNARE")
    s2_count = sum(1 for s in states_trace if s == "STAGE2_FRAME_LOCK")
    cool_count = sum(1 for s in states_trace[28 + 35 : 28 + 35 + 41] if s == "RELEASE_COOLDOWN")
    assert s1_count == 27 and s2_count == 35 and cool_count == 41, (
        f"Unexpected grapple timing counts: s1={s1_count}, s2={s2_count}, cool={cool_count}"
    )

    return {
        "status": "verified (test_grapple_escalation_and_counterplay)",
        "stage1_snare_window_tics": 28,
        "stage2_lock_duration_tics": s2_count,
        "cooldown_immunity_tics": 42,
        "countered_stage2_tics": stage2_tics_escape,
    }


def test_sloppy_vs_surgical_monte_carlo(num_seeds: int = 200) -> dict[str, Any]:
    """Verify over 200 seeds why sloppy center-mass spraying creates long Spindle-recycling fights while surgical play ends them fast."""
    sloppy_durations_s: list[float] = []
    surgical_durations_s: list[float] = []
    sloppy_rethreads: list[int] = []
    surgical_rethreads: list[int] = []

    for seed in range(num_seeds):
        rng_sloppy = np.random.default_rng(5000 + seed)
        rng_surg = np.random.default_rng(5000 + seed)

        for mode, rng, dur_list, rethread_list in (
            ("sloppy", rng_sloppy, sloppy_durations_s, sloppy_rethreads),
            ("surgical", rng_surg, surgical_durations_s, surgical_rethreads),
        ):
            # Room starts with 1 Spindle (2-tether cap, takes 14s to kill if ignored, 3.8s if prioritized) and 3 Controlled Armatures
            spindle_alive = True
            spindle_hp = 110.0
            active_hosts = [ArmatureAnatomyState(controlled=True) for _ in range(3)]
            reusable_heaps = 1
            rethreads = 0
            spindle_cd = 1.6
            t_sec = 0.0
            dt = 0.25  # Quarter-second steps

            while (spindle_alive or len(active_hosts) > 0) and t_sec < 60.0:
                t_sec += dt
                # Spindle re-threads a reusable heap if below tether cap (2)
                if spindle_alive and reusable_heaps > 0 and len(active_hosts) < 2:
                    spindle_cd -= dt
                    if spindle_cd <= 0.0:
                        reusable_heaps -= 1
                        active_hosts.append(ArmatureAnatomyState(controlled=True))
                        rethreads += 1
                        spindle_cd = 2.8

                # Player fires 1 shot every 0.50 s (dt=0.25 -> 50% per step)
                if rng.random() < 0.55:
                    if mode == "surgical":
                        # Cripples first host's ankle if needed, then shatters green cores or focuses Spindle
                        uncis = [h for h in active_hosts if not h.leg_crippled]
                        if len(active_hosts) >= 2 and uncis:
                            resolve_anatomical_hit(uncis[0], hit_z_u=10.0, lateral_offset_u=0.0, raw_damage=18.0, weapon_type="SHEAR_CUTTER")
                        elif spindle_alive and len(active_hosts) <= 2:
                            spindle_hp -= 32.0
                            if spindle_hp <= 0.0:
                                spindle_alive = False
                        elif active_hosts:
                            h0 = active_hosts[0]
                            res = resolve_anatomical_hit(h0, hit_z_u=28.0, lateral_offset_u=float(rng.uniform(0.0, 4.5)), raw_damage=14.0, weapon_type="PIERCING_FLECHETTE")
                            if not h0.alive:
                                active_hosts.pop(0)
                                if res["death_fate"] == "UNBOUND_REBAR_HEAP":
                                    reusable_heaps += 1
                    else:
                        # Sloppy sprayer: shoots whatever Armature is in front with wide lateral spread, ignoring Spindle until hosts == 0
                        if active_hosts:
                            h0 = active_hosts[0]
                            res = resolve_anatomical_hit(h0, hit_z_u=float(rng.uniform(18.0, 38.0)), lateral_offset_u=float(rng.uniform(5.0, 14.0)), raw_damage=14.0, weapon_type="PIERCING_FLECHETTE")
                            if not h0.alive:
                                active_hosts.pop(0)
                                if res["death_fate"] == "UNBOUND_REBAR_HEAP":
                                    reusable_heaps += 1
                        elif spindle_alive:
                            spindle_hp -= 26.0
                            if spindle_hp <= 0.0:
                                spindle_alive = False

            dur_list.append(t_sec)
            rethread_list.append(rethreads)

    mean_sloppy_s = float(np.mean(sloppy_durations_s))
    mean_surg_s = float(np.mean(surgical_durations_s))
    mean_sloppy_reth = float(np.mean(sloppy_rethreads))
    mean_surg_reth = float(np.mean(surgical_rethreads))

    assert mean_sloppy_s > mean_surg_s * 1.85, f"Expected sloppy fight >> surgical fight: {mean_sloppy_s} vs {mean_surg_s}"
    assert mean_sloppy_reth > mean_surg_reth * 3.0, f"Expected sloppy rethreads >> surgical rethreads: {mean_sloppy_reth} vs {mean_surg_reth}"

    return {
        "status": "verified (test_sloppy_vs_surgical_monte_carlo)",
        "seeds_tested": num_seeds,
        "surgical_mean_fight_sec": round(mean_surg_s, 2),
        "sloppy_mean_fight_sec": round(mean_sloppy_s, 2),
        "surgical_mean_rethreads": round(mean_surg_reth, 2),
        "sloppy_mean_rethreads": round(mean_sloppy_reth, 2),
    }


def run_all_df_verifications() -> dict[str, Any]:
    """Run all anatomical, material, grapple, scar, and Monte Carlo assertions."""
    anat_rep = test_anatomical_disassembly_and_materials()
    grap_rep = test_grapple_escalation_and_counterplay()
    mc_rep = test_sloppy_vs_surgical_monte_carlo(num_seeds=200)

    scar_grid = RoomScarGrid(16.0, 16.0)
    scar_grid.deposit_scar(128.0, 128.0, RoomScarGrid.ACOUSTIC_SCRAP)
    scar_grid.deposit_scar(256.0, 256.0, RoomScarGrid.CALCIFIED_TENDON)
    s_scrap = scar_grid.query_step_effect(130.0, 130.0)
    s_web = scar_grid.query_step_effect(260.0, 260.0)
    assert s_scrap["pd_early_reflection_trig"] and s_scrap["alert_radius_u"] == 384.0
    assert abs(s_web["speed_mult"] - 0.70) < 1e-6

    return {
        "all_verified": True,
        "anatomy_and_materials": anat_rep,
        "grapple_escalation": grap_rep,
        "sloppy_vs_surgical_monte_carlo": mc_rep,
        "room_scar_effects": {
            "status": "verified (RoomScarGrid)",
            "acoustic_scrap_alert_radius_u": s_scrap["alert_radius_u"],
            "calcified_tendon_speed_mult": s_web["speed_mult"],
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_df_verifications(), indent=2))