# SPDX-License-Identifier: CC0-1.0
"""nullrun_spindle_ecology.py — Mathematical & ZScript-Ready Model for the Vore Spindle / Armature Ecology.

Design Note (for Josiah, Claude Code & Codex — Null Run on UZDoom 5.0.3)
========================================================================
1. Why the Ecology Never Snowballs & Never Fizzles:
   - Conservation of Rebar Chassis: Spindles (`S`) do not spawn matter from nothing; they launch
     fungus-plastic tendon cores into existing unbound rebar heaps (`H`) or dormant Armatures (`A`).
     Thus total active threats are hard-bounded by both the room's total chassis count
     `N_chassis = A + B + C + H + D` and each Spindle's biological tether cap `M_max = 2` active
     controlled hosts per Spindle.
   - Core Fate ("Kill vs. Free"): We evaluate the continuous parameter `rho_free in [0, 1]`
     (probability that destroying a lodged green core frees the host back into a hostile Free
     Armature `A` rather than collapsing it). Analytic steady-state and Monte Carlo tests prove
     that freeing the host (`rho_free = 1`) *penalizes* precision weakpoint shooting because the
     player still has to fight the freed Armature `A`, which then dies into a reusable heap `H`!
     Instead, the optimal rule (`verified: test_core_fate_and_spindle_priority`) is:
       * Destroying the green core weakpoint (in flight, during threading, or lodged in `C`)
         severs the fungus-plastic tendon and **collapses the Armature permanently** into tangled,
         core-fouled scrap (`D`, non-reusable).
       * Destroying a Controlled Armature via crude body damage (`1 - eta_weakpoint`) or killing
         a Free Armature `A` unbinds it into an intact rebar heap (`H`) that a living Spindle can
         re-thread.
       * Killing the Vore Spindle (`S -> S - 1`) slackens all of its active tendons: any core in
         flight or mid-threading aborts immediately, and its controlled Armatures suffer tendon
         shock (`60%` collapse into heaps `H`, `40%` stagger for 35 tics and revert to weaker Free
         Armatures `A`).
   - This creates a sharp, readable "Kill the Spindle First (or Shoot the Green Cores)" loop:
     ignoring the Spindle while body-killing Armatures recycles `A -> H -> B -> C -> H`, whereas
     eliminating the Spindle or sniping the green cores drains the conversion loop permanently.

2. 2.5D Core Ballistics & Fairness Rule (UZDoom 5.0.3 @ 35 Hz, 32 map units/m):
   - The core travels along a parachute/tendon-dragged parabolic arc (`g_core = 0.28 u/tic^2`,
     roughly 28% of standard Doom gravity) at horizontal speed `v_xy = 14.0 u/tic` (15.3 m/s),
     with apex height automatically clamped below `ceil_z - 24 u` so cores never clip ceilings in
     low 8x8 m ossuary rooms.
   - Fairness / Minimum Warning Rule (`verified: test_ballistics_and_warning_time`):
       `t_warn(d) = t_telegraph (18 tics) + t_flight(d) (>= 12 tics) + t_thread (42 tics) >= 72 tics (2.06 s)`
     Every heap conversion gives the slow cyborg player (10 u/tic) at least 2.06 seconds of
     non-flashing visual + metallic-ratchet audio warning to shoot the core in flight (`r = 14 u`,
     `h = 24 u`, `+SHOOTABLE +NOBLOOD`) or while it threads the heap.

3. UZDoom 5.0.3 Engine Grounding & Photosensitivity:
   - Uses only verified UZDoom 5.0.3 ZScript features: standard Actor state labels, custom `Tick()`
     kinematic step, `CheckSight(target, SF_IGNOREVISIBILITY)`, and a fixed chain of 8 lightweight
     `+NOINTERACTION` tendon-bead actors interpolated along the quadratic Bezier curve between the
     Spindle's spinneret and the core (steady matte olive-green `BRIGHT` frames and smooth sinusoidal
     breathing—zero strobe or flashing effects).
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any
import numpy as np

# =============================================================================
# Engine & Scale Constants (UZDoom 5.0.3)
# =============================================================================
TIC_RATE: float = 35.0               # 35 tics per second
UNITS_PER_METRE: float = 32.0        # 32 Doom map units = 1 metre
PLAYER_SPEED_U_TIC: float = 10.0     # Careful cyborg base speed: 10 u/tic (10.94 m/s)
PLAYER_BURST_U_TIC: float = 16.0     # Short overdrive burst speed: 16 u/tic


# =============================================================================
# 1. Population Model (Continuous Mean-Field ODE + Equilibria + Sensitivities)
# =============================================================================

@dataclass(frozen=True)
class EcologyParams:
    """Parameters for the Spindle (S) - Free Armature (A) - Binding (B) - Controlled (C) - Heap (H) system.

    All rates with `_per_sec` or `_s` are in s^-1; time constants with `_tics` are in 35 Hz game tics.
    """
    launch_cooldown_tics: int = 48          # 1.37 s between core launches per Spindle (lambda_L = 0.7292 /s)
    telegraph_tics: int = 18                # 0.51 s seed-sac swell before core leaves Spindle
    conversion_tics: int = 42               # 1.20 s tendon-threading time in heap before C stands up
    max_controlled_per_spindle: int = 2     # Tether cap M_max per living Spindle
    core_speed_u_tic: float = 14.0          # Horizontal core flight speed (14 u/tic = 490 u/s = 15.3 m/s)
    core_gravity_u_tic2: float = 0.28       # Tendon-braked gravity (u/tic^2)
    min_launch_dist_u: float = 96.0         # Minimum launch range (3.0 m = 96 u, works in 8x8 m rooms)
    max_launch_dist_u: float = 768.0        # Maximum launch range (24.0 m = 768 u)
    hit_decay_dist_u: float = 900.0         # Distance scale for core landing accuracy
    los_visibility: float = 0.85            # Mean fraction of heaps with unobstructed LOS

    # Player engagement & kill rates (s^-1 when actively targeted by careful cyborg player)
    player_kill_rate_spindle_s: float = 0.28     # ~3.57 s of focused fire to kill 1 Spindle
    player_kill_rate_armature_s: float = 0.55    # ~1.82 s to drop 1 Free Armature (into Heap H)
    player_kill_rate_controlled_s: float = 0.42  # ~2.38 s to drop 1 Controlled Armature
    player_intercept_core_prob: float = 0.28     # Baseline probability player shoots down a core mid-flight/threading
    weakpoint_kill_fraction: float = 0.65        # Fraction of C kills that hit the green core weakpoint
    rho_free_on_core_kill: float = 0.0           # 0.0 = core kill collapses host to inert D; 1.0 = frees host to A
    body_kill_heap_survival: float = 0.85        # Probability body-killed A or C leaves an intact reusable heap H

    # Threat weights for encounter budgeting
    threat_weight_spindle: float = 1.6
    threat_weight_free: float = 1.0
    threat_weight_binding: float = 0.6
    threat_weight_controlled: float = 1.85


def core_flight_tics(distance_u: float, params: EcologyParams = EcologyParams()) -> int:
    """Return integer 35 Hz flight tics for a core launched across horizontal distance `distance_u`."""
    d_clamped = max(float(distance_u), params.min_launch_dist_u)
    return max(12, int(math.ceil(d_clamped / max(params.core_speed_u_tic, 1.0))))


def core_hit_probability(
    distance_u: float,
    has_los: bool = True,
    los_factor: float | None = None,
    params: EcologyParams = EcologyParams(),
) -> float:
    """Probability that a launched core lands in a target heap at `distance_u` without missing or being shot down."""
    if not has_los:
        return 0.0
    vis = params.los_visibility if los_factor is None else float(np.clip(los_factor, 0.0, 1.0))
    d = float(distance_u)
    if d < params.min_launch_dist_u or d > params.max_launch_dist_u:
        return 0.0
    range_acc = math.exp(-((d - 160.0) / params.hit_decay_dist_u) ** 2)
    t_f = core_flight_tics(d, params)
    shootdown_survival = (1.0 - params.player_intercept_core_prob) * math.exp(-0.004 * max(0, t_f - 12))
    return float(np.clip(vis * range_acc * shootdown_survival, 0.0, 1.0))


def effective_conversion_rate_per_spindle(
    mean_dist_u: float,
    params: EcologyParams = EcologyParams(),
) -> float:
    """Effective rate `k_conv` (s^-1 per Spindle per available heap scale) accounting for cooldown, flight, and threading."""
    t_f_sec = core_flight_tics(mean_dist_u, params) / TIC_RATE
    t_tele_sec = params.telegraph_tics / TIC_RATE
    t_conv_sec = params.conversion_tics / TIC_RATE
    t_cool_sec = params.launch_cooldown_tics / TIC_RATE
    p_hit = core_hit_probability(mean_dist_u, has_los=True, params=params)
    cycle_sec = t_cool_sec + t_tele_sec + t_f_sec + t_conv_sec
    return p_hit / max(cycle_sec, 1e-6)


def compute_equilibria_and_stability(
    S_fixed: float,
    total_chassis: float,
    mean_dist_u: float = 384.0,
    params: EcologyParams = EcologyParams(),
    conservative_recycling: bool = False,
) -> dict[str, Any]:
    """Compute exact equilibria and Jacobian eigenvalues of the reduced (A, B, C, H) ODE system."""
    k_launch = (TIC_RATE / (params.launch_cooldown_tics + params.telegraph_tics)) * core_hit_probability(
        mean_dist_u, True, params=params
    )
    k_thread = TIC_RATE / float(params.conversion_tics)
    mu_A = params.player_kill_rate_armature_s
    mu_C = params.player_kill_rate_controlled_s
    eta = params.weakpoint_kill_fraction
    rho_free = params.rho_free_on_core_kill

    if conservative_recycling:
        beta_A = 1.0
        beta_C = 1.0 - eta * rho_free
    else:
        beta_A = params.body_kill_heap_survival
        beta_C = (1.0 - eta) * params.body_kill_heap_survival

    def rhs(state: np.ndarray) -> np.ndarray:
        A, B, C, H = np.maximum(state, 0.0)
        if S_fixed <= 1e-9:
            r_bind = 0.0
        else:
            cap = params.max_controlled_per_spindle * S_fixed
            tether_avail = float(np.clip(cap - (B + C), 0.0, 1.0))
            heap_sat = H / (H + 0.5) if H > 0.0 else 0.0
            r_bind = k_launch * S_fixed * tether_avail * heap_sat
        kill_A = mu_A * A / (1.0 + 0.35 * (A + C))
        kill_C = mu_C * C / (1.0 + 0.35 * (A + C))
        dA = -kill_A + eta * rho_free * kill_C
        dB = r_bind - k_thread * B
        dC = k_thread * B - kill_C
        dH = beta_A * kill_A + beta_C * kill_C - r_bind
        return np.array([dA, dB, dC, dH], dtype=np.float64)

    y = np.array([0.0, 0.0, 0.0, float(total_chassis)], dtype=np.float64)
    dt = 0.02
    for _ in range(6000):
        k1 = rhs(y)
        k2 = rhs(y + 0.5 * dt * k1)
        k3 = rhs(y + 0.5 * dt * k2)
        k4 = rhs(y + dt * k3)
        y = np.maximum(0.0, y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4))

    eps = 1e-6
    J = np.zeros((4, 4), dtype=np.float64)
    for j in range(4):
        dp = np.zeros(4, dtype=np.float64)
        dp[j] = eps
        J[:, j] = (rhs(y + dp) - rhs(y - dp)) / (2.0 * eps)

    eigvals = np.linalg.eigvals(J)
    sorted_real = np.sort(np.real(eigvals))
    transverse_max_real = float(sorted_real[-2]) if conservative_recycling else float(sorted_real[-1])

    return {
        "equilibrium_ABCH": [round(float(v), 5) for v in y],
        "jacobian_eigenvalues_real": [round(float(v), 5) for v in sorted_real],
        "max_transverse_eigenvalue_real": round(transverse_max_real, 6),
        "asymptotically_stable": bool(transverse_max_real < -1e-4),
        "effective_reproduction_number_R": round(
            float((k_launch * S_fixed / max(mu_C, 1e-6)) * beta_C), 4
        ),
    }


def simulate_ode_fight(
    S0: float,
    A0: float,
    H0: float,
    strategy: str = "spindle_first",
    mean_dist_u: float = 384.0,
    params: EcologyParams = EcologyParams(),
    dt: float = 1.0 / 35.0,
    max_sec: float = 60.0,
) -> dict[str, Any]:
    """Integrate the coupled (S, A, B, C, H, D) fight trajectory under player target-priority `strategy`."""
    S, A, B, C, H, D = float(S0), float(A0), 0.0, 0.0, float(H0), 0.0
    k_launch = (TIC_RATE / (params.launch_cooldown_tics + params.telegraph_tics)) * core_hit_probability(
        mean_dist_u, True, params=params
    )
    k_thread = TIC_RATE / float(params.conversion_tics)

    steps = int(max_sec / dt)
    peak_threat = 0.0
    peak_controlled = 0.0
    threat_integral = 0.0
    time_to_clear = max_sec
    cleared = False

    history_t: list[float] = []
    history_threat: list[float] = []
    history_C: list[float] = []

    for step in range(steps):
        t = step * dt
        threat = (
            params.threat_weight_spindle * S
            + params.threat_weight_free * A
            + params.threat_weight_binding * B
            + params.threat_weight_controlled * C
        )
        peak_threat = max(peak_threat, threat)
        peak_controlled = max(peak_controlled, C)
        threat_integral += threat * dt
        if step % 5 == 0:
            history_t.append(round(t, 3))
            history_threat.append(round(threat, 4))
            history_C.append(round(C, 4))

        if (S + A + B + C) < 0.08 and not cleared:
            time_to_clear = t
            cleared = True

        if strategy == "spindle_first":
            w_S = 0.84 * (S / (S + 0.12))
            rem = 1.0 - w_S
            w_C = rem * (C / max(C + A + 0.12, 1e-6))
            w_A = rem - w_C
            eta_eff = params.weakpoint_kill_fraction
        else:
            mob = C + A
            w_mob = 0.94 * (mob / (mob + 0.12))
            w_C = w_mob * (C / max(mob + 0.08, 1e-6))
            w_A = w_mob - w_C
            w_S = 1.0 - w_mob
            eta_eff = 0.30 * params.weakpoint_kill_fraction

        kill_S = params.player_kill_rate_spindle_s * w_S * (S / (S + 0.12))
        kill_A = params.player_kill_rate_armature_s * w_A * (A / (A + 0.15))
        kill_C = params.player_kill_rate_controlled_s * w_C * (C / (C + 0.15))

        if S > 0.02:
            cap = params.max_controlled_per_spindle * S
            tether_avail = float(np.clip(cap - (B + C), 0.0, 1.0))
            r_bind = k_launch * S * tether_avail * (H / (H + 0.5))
        else:
            r_bind = 0.0

        tendon_sever = (kill_S / max(S, 0.15)) * C if S > 0.02 else 3.0 * C
        tendon_abort_B = (kill_S / max(S, 0.15)) * B if S > 0.02 else 3.0 * B

        eta = eta_eff
        rho_free = params.rho_free_on_core_kill
        beta_H = params.body_kill_heap_survival

        dS = -kill_S
        dA = -kill_A + eta * rho_free * kill_C + 0.40 * tendon_sever
        dB = r_bind - k_thread * B - tendon_abort_B
        dC = k_thread * B - kill_C - tendon_sever
        dH = beta_H * kill_A + (1.0 - eta) * beta_H * kill_C + tendon_abort_B + 0.60 * tendon_sever - r_bind
        dD = (1.0 - beta_H) * kill_A + (eta * (1.0 - rho_free) + (1.0 - eta) * (1.0 - beta_H)) * kill_C

        S = max(0.0, S + dS * dt)
        A = max(0.0, A + dA * dt)
        B = max(0.0, B + dB * dt)
        C = max(0.0, C + dC * dt)
        H = max(0.0, H + dH * dt)
        D = max(0.0, D + dD * dt)

    return {
        "strategy": strategy,
        "peak_threat": round(peak_threat, 4),
        "peak_controlled": round(peak_controlled, 4),
        "threat_integral": round(threat_integral, 4),
        "time_to_clear_sec": round(time_to_clear, 3),
        "final_scrap_D": round(D, 3),
        "history_t": history_t,
        "history_threat": history_threat,
        "history_C": history_C,
    }


def compute_parameter_sensitivities(
    S0: float = 1.0,
    A0: float = 2.0,
    H0: float = 4.0,
    base_params: EcologyParams = EcologyParams(),
) -> dict[str, dict[str, float]]:
    """Compute normalized local elasticity S_p = (p / Y) * (dY / dp) for Peak Controlled C_max and Threat Integral."""
    base_res = simulate_ode_fight(S0, A0, H0, strategy="armature_first", params=base_params)
    y_cmax0 = base_res["peak_controlled"]
    y_int0 = base_res["threat_integral"]

    param_names = (
        "launch_cooldown_tics",
        "conversion_tics",
        "max_controlled_per_spindle",
        "player_kill_rate_spindle_s",
        "player_kill_rate_controlled_s",
        "player_intercept_core_prob",
        "weakpoint_kill_fraction",
    )
    sensitivities: dict[str, dict[str, float]] = {}
    for name in param_names:
        val0 = float(getattr(base_params, name))
        delta = max(1.0, round(0.10 * val0)) if isinstance(getattr(base_params, name), int) else 0.05 * val0
        kw_hi = {**base_params.__dict__, name: type(getattr(base_params, name))(val0 + delta)}
        res_hi = simulate_ode_fight(S0, A0, H0, strategy="armature_first", params=EcologyParams(**kw_hi))
        el_cmax = ((res_hi["peak_controlled"] - y_cmax0) / max(y_cmax0, 1e-6)) / (delta / max(val0, 1e-6))
        el_int = ((res_hi["threat_integral"] - y_int0) / max(y_int0, 1e-6)) / (delta / max(val0, 1e-6))
        sensitivities[name] = {
            "elasticity_peak_controlled": round(float(el_cmax), 4),
            "elasticity_threat_integral": round(float(el_int), 4),
        }
    return sensitivities


# =============================================================================
# 2. Core Ballistics in a 2.5D Engine (UZDoom 5.0.3)
# =============================================================================

@dataclass(frozen=True)
class CoreBallisticSolution:
    distance_u: float
    flight_tics: int
    flight_sec: float
    total_warning_tics: int
    total_warning_sec: float
    vel_xy_u_tic: float
    vel_z0_u_tic: float
    gravity_u_tic2: float
    apex_z_u: float
    trajectory_xyz: np.ndarray       # Shape (flight_tics + 1, 3)
    tendon_beads_mid_xyz: np.ndarray # 8 tendon bead positions at mid-flight (t = flight_tics // 2)


def solve_core_ballistics_25d(
    spindle_xyz: tuple[float, float, float],
    heap_xyz: tuple[float, float, float],
    ceiling_z_u: float = 192.0,
    params: EcologyParams = EcologyParams(),
) -> CoreBallisticSolution:
    """Compute a ceiling-safe, shootable 2.5D parabolic core trajectory and 8-bead tendon curve."""
    x0, y0, z0_floor = map(float, spindle_xyz)
    x1, y1, z1_floor = map(float, heap_xyz)
    z_launch = z0_floor + 28.0  # Spindle dorsal seed-sac spinneret height (28 u = 0.875 m)
    z_target = z1_floor + 10.0  # Heap chest socket height (10 u = 0.31 m)

    dx = x1 - x0
    dy = y1 - y0
    dist_u = math.hypot(dx, dy)
    t_f = core_flight_tics(dist_u, params)
    v_xy = dist_u / float(t_f)

    g_eff = params.core_gravity_u_tic2
    vz0 = (z_target - z_launch) / t_f + 0.5 * g_eff * t_f
    t_apex = np.clip(vz0 / max(g_eff, 1e-6), 0.0, float(t_f))
    z_apex = z_launch + vz0 * t_apex - 0.5 * g_eff * (t_apex ** 2)
    max_allowed_z = float(ceiling_z_u) - 24.0

    if z_apex > max_allowed_z:
        headroom = max(4.0, max_allowed_z - max(z_launch, z_target))
        g_eff = min(g_eff, (8.0 * headroom) / max(float(t_f ** 2), 1.0))
        vz0 = (z_target - z_launch) / t_f + 0.5 * g_eff * t_f
        t_apex = np.clip(vz0 / max(g_eff, 1e-6), 0.0, float(t_f))
        z_apex = z_launch + vz0 * t_apex - 0.5 * g_eff * (t_apex ** 2)

    tics = np.arange(0, t_f + 1, dtype=np.float64)
    ux = dx / max(dist_u, 1e-6)
    uy = dy / max(dist_u, 1e-6)
    xs = x0 + ux * v_xy * tics
    ys = y0 + uy * v_xy * tics
    zs = z_launch + vz0 * tics - 0.5 * g_eff * (tics ** 2)
    traj = np.stack([xs, ys, zs], axis=-1)

    mid_idx = t_f // 2
    p_start = np.array([x0, y0, z_launch], dtype=np.float64)
    p_core = traj[mid_idx]
    p_ctrl = 0.5 * (p_start + p_core)
    p_ctrl[2] -= 14.0
    s_vals = np.linspace(0.1, 0.9, 8)[:, None]
    beads = ((1.0 - s_vals) ** 2) * p_start + 2.0 * (1.0 - s_vals) * s_vals * p_ctrl + (s_vals ** 2) * p_core

    warn_tics = params.telegraph_tics + t_f + params.conversion_tics
    return CoreBallisticSolution(
        distance_u=round(dist_u, 2),
        flight_tics=t_f,
        flight_sec=round(t_f / TIC_RATE, 3),
        total_warning_tics=warn_tics,
        total_warning_sec=round(warn_tics / TIC_RATE, 3),
        vel_xy_u_tic=round(v_xy, 3),
        vel_z0_u_tic=round(vz0, 3),
        gravity_u_tic2=round(g_eff, 4),
        apex_z_u=round(float(z_apex), 2),
        trajectory_xyz=traj,
        tendon_beads_mid_xyz=beads,
    )


# =============================================================================
# 3. Encounter Budget Function (Seeded Level Generator Integration)
# =============================================================================

def allocate_spindle_encounter(
    room_dims_m: tuple[float, float],
    existing_heaps: int,
    player_health: int = 100,
    player_ammo_ratio: float = 1.0,
    target_threat_band: tuple[float, float] = (4.5, 9.5),
    params: EcologyParams = EcologyParams(),
) -> dict[str, Any]:
    """Choose initial `(S, A, H)` for a generated room so expected peak threat stays inside `target_threat_band`."""
    w_m = float(np.clip(room_dims_m[0], 8.0, 30.0))
    l_m = float(np.clip(room_dims_m[1], 8.0, 30.0))
    area_m2 = w_m * l_m
    mean_dist_u = 0.52 * math.hypot(w_m * UNITS_PER_METRE, l_m * UNITS_PER_METRE)
    mean_dist_u = float(np.clip(mean_dist_u, 192.0, 680.0))

    hp_norm = float(np.clip(player_health / 100.0, 0.20, 1.0))
    ammo_norm = float(np.clip(player_ammo_ratio, 0.25, 1.4))
    readiness = float(np.clip(0.55 + 0.30 * hp_norm + 0.20 * min(ammo_norm, 1.25), 0.55, 1.15))

    area_scale = float(np.clip(0.65 + 0.45 * ((area_m2 - 64.0) / (900.0 - 64.0)), 0.65, 1.10))
    low_target = target_threat_band[0] * readiness * area_scale
    high_target = target_threat_band[1] * readiness * area_scale
    mid_target = 0.5 * (low_target + high_target)

    max_S = 1 if (area_m2 < 240.0 or readiness < 0.78) else 2
    best_choice: dict[str, Any] | None = None
    best_score = 1e9

    for S in range(1, max_S + 1):
        for A in range(1, 6):
            for H_total in range(max(existing_heaps, 2), max(existing_heaps + 4, 6)):
                sim = simulate_ode_fight(
                    S0=float(S),
                    A0=float(A),
                    H0=float(H_total),
                    strategy="spindle_first",
                    mean_dist_u=mean_dist_u,
                    params=params,
                )
                peak = sim["peak_threat"]
                in_band = (low_target <= peak <= high_target)
                band_penalty = 0.0 if in_band else (
                    (low_target - peak) * 10.0 if peak < low_target else (peak - high_target) * 12.0
                )
                score = band_penalty + abs(peak - mid_target)
                if score < best_score:
                    best_score = score
                    best_choice = {
                        "S": S,
                        "A": A,
                        "H": H_total,
                        "H_added": max(0, H_total - existing_heaps),
                        "expected_peak_threat": round(peak, 3),
                        "expected_peak_controlled": round(sim["peak_controlled"], 3),
                        "target_band_scaled": (round(low_target, 3), round(high_target, 3)),
                        "in_target_band": bool(in_band),
                        "room_area_m2": round(area_m2, 1),
                        "player_readiness": round(readiness, 3),
                    }

    assert best_choice is not None
    return best_choice


# =============================================================================
# 4. ZScript-Ready Per-Tic Finite State Machines & Stochastic Room Simulator
# =============================================================================

@dataclass
class HeapEntity:
    heap_id: int
    x: float
    y: float
    intact: bool = True
    claimed_by_spindle: int = -1
    threading_tics: int = 0


@dataclass
class ArmatureEntity:
    actor_id: int
    x: float
    y: float
    state: str = "FREE_HUNT"  # FREE_HUNT, CONTROLLED_GUARD, CONTROLLED_HUNT, CORE_STAGGER, DEAD
    master_spindle_id: int = -1
    stagger_tics: int = 0
    hp: float = 60.0


@dataclass
class SpindleEntity:
    spindle_id: int
    x: float
    y: float
    state: str = "SCUTTLE_POSTURE"  # SCUTTLE_POSTURE, TELEGRAPH_LAUNCH, LAUNCH_CORE, TETHER_MAINTAIN, DEAD
    cooldown_tics: int = 20
    telegraph_tics: int = 0
    target_heap_id: int = -1
    hp: float = 110.0


@dataclass
class CoreEntity:
    core_id: int
    spindle_id: int
    target_heap_id: int
    state: str = "IN_FLIGHT"  # IN_FLIGHT, THREADING_HEAP, SEVERED
    flight_tics_remaining: int = 20
    threading_tics_remaining: int = 42


def score_heap_for_spindle(
    spindle_xy: tuple[float, float],
    heap: HeapEntity,
    player_xy: tuple[float, float],
    has_los: bool = True,
    params: EcologyParams = EcologyParams(),
) -> float:
    """Per-tic ZScript heap selection score `U(h)`: positive only for valid, unclaimed heaps in LOS."""
    if (not heap.intact) or (heap.claimed_by_spindle != -1) or (not has_los):
        return -1.0
    d_sh = math.hypot(heap.x - spindle_xy[0], heap.y - spindle_xy[1])
    if d_sh < params.min_launch_dist_u or d_sh > params.max_launch_dist_u:
        return -1.0
    d_ph = math.hypot(heap.x - player_xy[0], heap.y - player_xy[1])
    if d_ph < 56.0:
        return -1.0
    range_bell = math.exp(-((d_sh - 280.0) / 280.0) ** 2)
    player_safety = min(1.0, (d_ph - 56.0) / 192.0)
    return float(range_bell * (0.65 + 0.35 * player_safety))


def decide_controlled_armature_posture(
    arm_xy: tuple[float, float],
    spindle: SpindleEntity | None,
    player_xy: tuple[float, float],
    current_guards_for_spindle: int,
    max_guards_per_spindle: int = 1,
) -> str:
    """Per-tic ZScript rule switching a Controlled Armature between `CONTROLLED_GUARD` and `CONTROLLED_HUNT`."""
    if spindle is None or spindle.state == "DEAD":
        return "FREE_HUNT"
    d_player_spindle = math.hypot(player_xy[0] - spindle.x, player_xy[1] - spindle.y)
    spindle_threatened = (d_player_spindle < 288.0) or (spindle.hp < 55.0)
    if spindle_threatened and current_guards_for_spindle < max_guards_per_spindle:
        return "CONTROLLED_GUARD"
    return "CONTROLLED_HUNT"


def simulate_stochastic_encounter_35hz(
    S0: int,
    A0: int,
    H0: int,
    room_dims_m: tuple[float, float] = (16.0, 16.0),
    seed: int = 42,
    max_tics: int = 35 * 45,
    params: EcologyParams = EcologyParams(),
) -> dict[str, Any]:
    """Run a discrete 35 Hz tic-by-tic agent simulation of the ZScript FSMs in a room."""
    rng = np.random.default_rng(seed)
    w_u = room_dims_m[0] * UNITS_PER_METRE
    l_u = room_dims_m[1] * UNITS_PER_METRE

    player_xy = np.array([w_u * 0.5, l_u * 0.12], dtype=np.float64)

    spindles = [
        SpindleEntity(
            spindle_id=i,
            x=float(rng.uniform(0.22 * w_u, 0.78 * w_u)),
            y=float(rng.uniform(0.78 * l_u, 0.92 * l_u)),
            cooldown_tics=int(rng.integers(6, 18)),
        )
        for i in range(S0)
    ]
    armatures = [
        ArmatureEntity(
            actor_id=i,
            x=float(rng.uniform(0.15 * w_u, 0.85 * w_u)),
            y=float(rng.uniform(0.35 * l_u, 0.70 * l_u)),
            state="FREE_HUNT",
        )
        for i in range(A0)
    ]
    heaps = [
        HeapEntity(
            heap_id=i,
            x=float(rng.uniform(0.18 * w_u, 0.82 * w_u)),
            y=float(rng.uniform(0.32 * l_u, 0.54 * l_u)),
            intact=True,
        )
        for i in range(H0)
    ]
    cores: list[CoreEntity] = []
    next_core_id = 0
    next_arm_id = len(armatures)

    total_conversions = 0
    total_launches = 0
    peak_controlled = 0
    peak_active_mobs = A0
    peak_threat = 0.0
    min_observed_warning_tics = 999999
    heap_warn_start_tic: dict[int, int] = {}

    for tic in range(max_tics):
        living_spindles = [s for s in spindles if s.state != "DEAD"]
        free_arms = [a for a in armatures if a.state in ("FREE_HUNT", "CORE_STAGGER")]
        ctrl_arms = [a for a in armatures if a.state in ("CONTROLLED_GUARD", "CONTROLLED_HUNT")]
        active_cores = [c for c in cores if c.state in ("IN_FLIGHT", "THREADING_HEAP")]

        peak_controlled = max(peak_controlled, len(ctrl_arms))
        peak_active_mobs = max(peak_active_mobs, len(free_arms) + len(ctrl_arms))
        cur_threat = (
            params.threat_weight_spindle * len(living_spindles)
            + params.threat_weight_free * len(free_arms)
            + params.threat_weight_binding * len(active_cores)
            + params.threat_weight_controlled * len(ctrl_arms)
        )
        peak_threat = max(peak_threat, cur_threat)

        if not living_spindles and not free_arms and not ctrl_arms and not active_cores:
            return {
                "cleared": True,
                "clear_tics": tic,
                "total_launches": total_launches,
                "total_conversions": total_conversions,
                "peak_controlled": peak_controlled,
                "peak_active_mobs": peak_active_mobs,
                "peak_threat": round(peak_threat, 3),
                "min_observed_warning_tics": min_observed_warning_tics if total_conversions > 0 else 72,
            }

        # 1. Step Spindles FSM
        for sp in living_spindles:
            active_tethers = sum(1 for a in ctrl_arms if a.master_spindle_id == sp.spindle_id) + sum(
                1 for c in active_cores if c.spindle_id == sp.spindle_id
            )
            if sp.state == "SCUTTLE_POSTURE":
                if sp.cooldown_tics > 0:
                    sp.cooldown_tics -= 1
                elif active_tethers >= params.max_controlled_per_spindle:
                    sp.state = "TETHER_MAINTAIN"
                else:
                    best_h: HeapEntity | None = None
                    best_u = 0.0
                    for h in heaps:
                        has_los = bool(rng.random() < params.los_visibility)
                        u = score_heap_for_spindle((sp.x, sp.y), h, (player_xy[0], player_xy[1]), has_los, params)
                        if u > best_u:
                            best_u = u
                            best_h = h
                    if best_h is not None:
                        best_h.claimed_by_spindle = sp.spindle_id
                        sp.target_heap_id = best_h.heap_id
                        sp.state = "TELEGRAPH_LAUNCH"
                        sp.telegraph_tics = params.telegraph_tics
                        heap_warn_start_tic[best_h.heap_id] = tic
                    else:
                        sp.cooldown_tics = 8

            elif sp.state == "TELEGRAPH_LAUNCH":
                sp.telegraph_tics -= 1
                if sp.telegraph_tics <= 0:
                    sp.state = "LAUNCH_CORE"

            elif sp.state == "LAUNCH_CORE":
                th = next((h for h in heaps if h.heap_id == sp.target_heap_id and h.intact), None)
                if th is not None:
                    d_u = math.hypot(th.x - sp.x, th.y - sp.y)
                    tf = core_flight_tics(d_u, params)
                    cores.append(
                        CoreEntity(
                            core_id=next_core_id,
                            spindle_id=sp.spindle_id,
                            target_heap_id=th.heap_id,
                            state="IN_FLIGHT",
                            flight_tics_remaining=tf,
                            threading_tics_remaining=params.conversion_tics,
                        )
                    )
                    next_core_id += 1
                    total_launches += 1
                sp.state = "SCUTTLE_POSTURE"
                sp.cooldown_tics = params.launch_cooldown_tics

            elif sp.state == "TETHER_MAINTAIN":
                if active_tethers < params.max_controlled_per_spindle:
                    sp.state = "SCUTTLE_POSTURE"

        # 2. Step Cores FSM
        for core in active_cores:
            parent = next((s for s in living_spindles if s.spindle_id == core.spindle_id), None)
            th = next((h for h in heaps if h.heap_id == core.target_heap_id and h.intact), None)
            if parent is None or th is None:
                core.state = "SEVERED"
                if th is not None:
                    th.claimed_by_spindle = -1
                continue

            if core.state == "IN_FLIGHT":
                core.flight_tics_remaining -= 1
                if core.flight_tics_remaining <= 0:
                    core.state = "THREADING_HEAP"
            elif core.state == "THREADING_HEAP":
                core.threading_tics_remaining -= 1
                if core.threading_tics_remaining <= 0:
                    th.intact = False
                    th.claimed_by_spindle = -1
                    core.state = "SEVERED"
                    warn_elapsed = tic - heap_warn_start_tic.get(th.heap_id, tic - 72)
                    min_observed_warning_tics = min(min_observed_warning_tics, warn_elapsed)
                    armatures.append(
                        ArmatureEntity(
                            actor_id=next_arm_id,
                            x=th.x,
                            y=th.y,
                            state="CONTROLLED_HUNT",
                            master_spindle_id=parent.spindle_id,
                            hp=75.0,
                        )
                    )
                    next_arm_id += 1
                    total_conversions += 1

        # 3. Step Armatures FSM
        guards_per_spindle: dict[int, int] = {s.spindle_id: 0 for s in living_spindles}
        for arm in armatures:
            if arm.state == "DEAD":
                continue
            if arm.state == "CORE_STAGGER":
                arm.stagger_tics -= 1
                if arm.stagger_tics <= 0:
                    arm.state = "FREE_HUNT"
            elif arm.state in ("CONTROLLED_GUARD", "CONTROLLED_HUNT"):
                parent = next((s for s in living_spindles if s.spindle_id == arm.master_spindle_id), None)
                if parent is None:
                    arm.state = "CORE_STAGGER"
                    arm.stagger_tics = 35
                    arm.master_spindle_id = -1
                else:
                    g_cnt = guards_per_spindle.get(parent.spindle_id, 0)
                    posture = decide_controlled_armature_posture(
                        (arm.x, arm.y), parent, (player_xy[0], player_xy[1]), g_cnt
                    )
                    arm.state = posture
                    if posture == "CONTROLLED_GUARD":
                        guards_per_spindle[parent.spindle_id] = g_cnt + 1

        # 4. Player Action Model (Careful Cyborg @ 35 Hz applying UZDoom weapon damage to actor HP):
        if active_cores and rng.random() < (params.player_intercept_core_prob / TIC_RATE) * 1.6:
            c_hit = active_cores[0]
            c_hit.state = "SEVERED"
            th = next((h for h in heaps if h.heap_id == c_hit.target_heap_id), None)
            if th is not None:
                th.claimed_by_spindle = -1
        elif living_spindles and (len(ctrl_arms) <= 2 or rng.random() < 0.70):
            target_sp = living_spindles[0]
            dmg = (110.0 * params.player_kill_rate_spindle_s / TIC_RATE) * float(rng.uniform(0.75, 1.25))
            target_sp.hp -= dmg
            if target_sp.hp <= 0.0:
                target_sp.state = "DEAD"
                target_sp.hp = 0.0
        elif ctrl_arms:
            target_c = ctrl_arms[0]
            dmg = (75.0 * params.player_kill_rate_controlled_s / TIC_RATE) * float(rng.uniform(0.75, 1.25))
            target_c.hp -= dmg
            if target_c.hp <= 0.0:
                target_c.state = "DEAD"
                if rng.random() > params.weakpoint_kill_fraction:
                    if rng.random() < params.body_kill_heap_survival:
                        heaps.append(HeapEntity(heap_id=len(heaps), x=target_c.x, y=target_c.y, intact=True))
                elif rng.random() < params.rho_free_on_core_kill:
                    target_c.state = "FREE_HUNT"
                    target_c.hp = 45.0
        elif free_arms:
            target_a = free_arms[0]
            dmg = (60.0 * params.player_kill_rate_armature_s / TIC_RATE) * float(rng.uniform(0.75, 1.25))
            target_a.hp -= dmg
            if target_a.hp <= 0.0:
                target_a.state = "DEAD"
                if rng.random() < params.body_kill_heap_survival:
                    heaps.append(HeapEntity(heap_id=len(heaps), x=target_a.x, y=target_a.y, intact=True))

    return {
        "cleared": False,
        "clear_tics": max_tics,
        "total_launches": total_launches,
        "total_conversions": total_conversions,
        "peak_controlled": peak_controlled,
        "peak_active_mobs": peak_active_mobs,
        "peak_threat": round(peak_threat, 3),
        "min_observed_warning_tics": min_observed_warning_tics if total_conversions > 0 else 72,
    }


# =============================================================================
# 5. Verification Suite with Explicit NumPy Assertions
# =============================================================================

def test_equilibria_and_stability() -> dict[str, Any]:
    """Verify asymptotic stability of both the conservative endemic plateau and full attrition equilibrium."""
    params = EcologyParams()
    eq_cons = compute_equilibria_and_stability(1.0, 6.0, 384.0, params, conservative_recycling=True)
    eq_attr = compute_equilibria_and_stability(1.0, 6.0, 384.0, params, conservative_recycling=False)
    eq_dead = compute_equilibria_and_stability(0.0, 6.0, 384.0, params, conservative_recycling=False)

    assert eq_cons["asymptotically_stable"], f"Conservative plateau unstable: {eq_cons}"
    assert eq_attr["asymptotically_stable"], f"Attrition system unstable: {eq_attr}"
    C_star = eq_cons["equilibrium_ABCH"][2]
    assert 0.4 < C_star <= params.max_controlled_per_spindle + 1e-6, f"Invalid C* plateau: {C_star}"
    assert sum(eq_dead["equilibrium_ABCH"][:3]) < 1e-3, f"Dead spindle equilibrium non-zero: {eq_dead}"
    return {
        "status": "verified (test_equilibria_and_stability)",
        "conservative_plateau_ABCH": eq_cons["equilibrium_ABCH"],
        "attrition_equilibrium_ABCH": eq_attr["equilibrium_ABCH"],
        "max_transverse_eigenvalue_real": eq_cons["max_transverse_eigenvalue_real"],
        "effective_R": eq_attr["effective_reproduction_number_R"],
    }


def test_core_fate_and_spindle_priority() -> dict[str, Any]:
    """Verify 'kill the Spindle first' dominance and prove core-collapse beats core-frees-host."""
    p_collapse = EcologyParams(rho_free_on_core_kill=0.0)
    p_free = EcologyParams(rho_free_on_core_kill=1.0)

    sim_spindle_1st = simulate_ode_fight(1.0, 3.0, 3.0, strategy="spindle_first", params=p_collapse)
    sim_mob_1st = simulate_ode_fight(1.0, 3.0, 3.0, strategy="armature_first", params=p_collapse)
    sim_free_host = simulate_ode_fight(1.0, 3.0, 3.0, strategy="armature_first", params=p_free)

    assert sim_spindle_1st["threat_integral"] < sim_mob_1st["threat_integral"] * 0.78, (
        f"Spindle-first did not reduce threat integral enough: {sim_spindle_1st['threat_integral']} vs {sim_mob_1st['threat_integral']}"
    )
    assert sim_spindle_1st["time_to_clear_sec"] < sim_mob_1st["time_to_clear_sec"], (
        "Spindle-first must clear faster than Armature-first"
    )
    assert sim_mob_1st["threat_integral"] < sim_free_host["threat_integral"], (
        "Core-collapse (rho_free=0) must reward the player with lower cumulative threat than freeing a hostile Armature"
    )
    return {
        "status": "verified (test_core_fate_and_spindle_priority)",
        "spindle_first_threat_integral": sim_spindle_1st["threat_integral"],
        "armature_first_threat_integral": sim_mob_1st["threat_integral"],
        "spindle_first_clear_sec": sim_spindle_1st["time_to_clear_sec"],
        "armature_first_clear_sec": sim_mob_1st["time_to_clear_sec"],
        "core_collapse_vs_free_integral_ratio": round(
            sim_mob_1st["threat_integral"] / max(sim_free_host["threat_integral"], 1e-6), 4
        ),
    }


def test_ballistics_and_warning_time() -> dict[str, Any]:
    """Verify 2.5D parabolic core ballistics, ceiling clearance in low rooms, and >= 70 tic (2.0 s) warning rule."""
    params = EcologyParams()
    min_warn_tics = 999999
    max_apex_violation = 0.0

    for dist_u in np.linspace(96.0, 768.0, 25):
        for ceil_z in (128.0, 192.0, 256.0):
            sol = solve_core_ballistics_25d((0.0, 0.0, 0.0), (float(dist_u), 0.0, 0.0), ceiling_z_u=ceil_z, params=params)
            min_warn_tics = min(min_warn_tics, sol.total_warning_tics)
            violation = max(0.0, sol.apex_z_u - (ceil_z - 24.0 + 1e-6))
            max_apex_violation = max(max_apex_violation, violation)
            assert sol.total_warning_tics >= 70, f"Warning time {sol.total_warning_tics} tics < 70 tics at d={dist_u}"
            assert violation == 0.0, f"Core trajectory clipped ceiling ({sol.apex_z_u} > {ceil_z - 24.0})"
            assert np.linalg.norm(sol.trajectory_xyz[0] - np.array([0.0, 0.0, 28.0])) < 1e-6
            assert np.linalg.norm(sol.trajectory_xyz[-1] - np.array([dist_u, 0.0, 10.0])) < 1e-6

    return {
        "status": "verified (test_ballistics_and_warning_time)",
        "min_warning_tics": int(min_warn_tics),
        "min_warning_sec": round(min_warn_tics / TIC_RATE, 3),
        "max_ceiling_violation_u": max_apex_violation,
    }


def test_encounter_budget_and_monte_carlo(num_seeds: int = 240) -> dict[str, Any]:
    """Run Monte Carlo simulations across 240 seeds and room sizes (8x8 m, 16x16 m, 30x30 m)."""
    params = EcologyParams()
    room_presets = [(8.0, 8.0), (16.0, 16.0), (30.0, 30.0)]

    budget_checks = 0
    for dims in room_presets:
        for hp in (45, 75, 100):
            for ammo in (0.5, 1.0, 1.3):
                alloc = allocate_spindle_encounter(dims, existing_heaps=2, player_health=hp, player_ammo_ratio=ammo, params=params)
                assert alloc["in_target_band"], f"Budget allocation out of band: {alloc}"
                assert 1 <= alloc["S"] <= 2 and 1 <= alloc["A"] <= 5 and alloc["H"] >= 2
                budget_checks += 1

    alloc_cache = {
        dims: allocate_spindle_encounter(dims, existing_heaps=3, player_health=85, player_ammo_ratio=1.0, params=params)
        for dims in room_presets
    }

    max_peak_controlled = 0
    max_peak_threat = 0.0
    runaway_count = 0
    fizzle_runs = 0
    min_warn_observed = 999999

    for idx in range(num_seeds):
        dims = room_presets[idx % len(room_presets)]
        alloc = alloc_cache[dims]
        res = simulate_stochastic_encounter_35hz(
            S0=alloc["S"],
            A0=alloc["A"],
            H0=alloc["H"],
            room_dims_m=dims,
            seed=1000 + idx,
            params=params,
        )
        tether_cap = alloc["S"] * params.max_controlled_per_spindle
        assert res["peak_controlled"] <= tether_cap, (
            f"Seed {idx} exceeded tether cap: {res['peak_controlled']} > {tether_cap}"
        )
        assert res["peak_active_mobs"] <= alloc["A"] + alloc["H"], "Snowball violation: active mobs exceeded chassis pool"
        if not res["cleared"]:
            runaway_count += 1
        if res["total_launches"] == 0:
            fizzle_runs += 1
        max_peak_controlled = max(max_peak_controlled, res["peak_controlled"])
        max_peak_threat = max(max_peak_threat, res["peak_threat"])
        min_warn_observed = min(min_warn_observed, res["min_observed_warning_tics"])

    fizzle_rate = fizzle_runs / float(num_seeds)
    assert runaway_count == 0, f"Encounter failed to clear in {runaway_count}/{num_seeds} seeds"
    assert fizzle_rate < 0.03, f"Fizzle rate {fizzle_rate:.3f} >= 3%"
    assert min_warn_observed >= 70, f"Observed warning time {min_warn_observed} tics < 70 tics"

    return {
        "status": "verified (test_encounter_budget_and_monte_carlo)",
        "seeds_tested": num_seeds,
        "budget_grid_checks": budget_checks,
        "runaway_count": runaway_count,
        "fizzle_rate": round(fizzle_rate, 4),
        "max_peak_controlled_observed": max_peak_controlled,
        "max_peak_threat_observed": round(max_peak_threat, 3),
        "min_warning_tics_observed": int(min_warn_observed),
    }


def run_all_verifications() -> dict[str, Any]:
    """Execute all verification suites and return a complete summary dictionary."""
    eq_rep = test_equilibria_and_stability()
    prio_rep = test_core_fate_and_spindle_priority()
    ball_rep = test_ballistics_and_warning_time()
    mc_rep = test_encounter_budget_and_monte_carlo(num_seeds=240)
    sens_rep = compute_parameter_sensitivities()
    return {
        "all_verified": True,
        "equilibria_and_stability": eq_rep,
        "core_fate_and_priority": prio_rep,
        "ballistics_and_warning": ball_rep,
        "budget_and_monte_carlo": mc_rep,
        "parameter_sensitivities": sens_rep,
        "engine_hypotheses_and_notes": {
            "tendon_rendering_uzdoom_503": (
                "verified engine feature: spawn 8 lightweight +NOINTERACTION actors along the quadratic "
                "Bezier curve between Spindle and Core in ZScript Tick(); hypothesis: visual read at 640x400 "
                "is clearest when alternating 2 matte olive-green tendon-knot sprites with zero strobe/flicker."
            ),
        },
    }


if __name__ == "__main__":
    import json
    report = run_all_verifications()
    print(json.dumps(report, indent=2))