# Argon's engine-fork maths (2026-11-02): Claude's review
Files: ~/dev/shared/inputs/nullrun/argon-20261102-0207/ (read-only; GPL-3.0-or-later headers). Each test suite was run in isolation with python -I.

## Volumetric fog and shafts (wishlist #1 and #7)
- The analytic height-plus-distance optical depth is correct. Its own test FAILS (tau error 6.5e-6 against a 1e-6 tolerance) because the 1024-step midpoint reference is inaccurate. Claude refined the reference: error 1.0e-7 at 8192 steps and 1.6e-9 at 65536, falling as 1/N². Fix the test, not the maths.
- The curl flow is analytically divergence-free (curl of a stream function); the numerical check passes.
- Cone-clipped shafts with 6–8 IGN-jittered steps plus HG phase: sensible.
- The temporal clamp bounds the FOG LAYER's frame-to-frame luminance change (8%), not the scene. That matches Josiah's effect-contribution rule.
- The GPU cost is labelled a hypothesis (0.68 ms full-res, 0.24 ms half-res at N=6). Measure it in the fork.
- Use: hand to the fork's fog shader (job 20261102-014346, follow-up chained).

## Per-pixel sprite lighting (wishlist #5 and #4)
- All tests pass. Useful result: using the live view basis on baked camera-space normals has a worst-case normal error of 25.7° at 8 yaws × 5 bands, and 16.8° at 16 yaws. That's another argument for 16-yaw rebakes.
- The ±4° normal crossfade removes LIGHTING pops (a 520× reduction in its test), but not silhouette or albedo pops. Blending normals from two different frames at the same texel mixes different body parts where the silhouettes differ; it's acceptable inside a narrow window, but it isn't geometrically exact.

## Pixel-accurate hitboxes (wishlist #3 and #16)
- All tests pass: 100% core recall on visible core texels; rays pass through the gaps in the rebar.
- Overclaim: the "ray-aligned virtual plane reduces oblique parallax error to identically 0". It still inherits yaw quantisation (±22.5° at 8 yaws), so it isn't zero. Player shots come from the camera, so they're unaffected; it matters for infighting and turrets.
- Good port design: a 4-bit alpha-plus-region mask per frame on the CPU (about 512 bytes per frame), an MF9 flag, and the hit region and UV passed to DamageMobj. The region masks come from a Blender object-index or cryptomatte pass in our bake.

## Portal audio and early reflections (wishlist #2 and #11)
- The early reflections match a brute-force box image-source lattice to 1e-9. The parallel-wall flutter taps are present.
- Its spatial-audio test FAILS on its own example: the "diffracted" emitter's detour is 16.7 u against an asserted >20 u. That's a test geometry slip; the unfolding maths checks out (a manual unfold reproduced (0, 384, 32)).
- The diffraction curve is labelled "Maekawa-Kirchhoff", but (1+6.6N)^-1/2 is NOT Maekawa: it gives about 4 dB at N=1, where Maekawa gives about 13 dB. Treat it as a tunable curve, or replace it with Maekawa's 10·log10(3+20N).
- "Under 4 µs per room" is unmeasured.

Overall: Argon's best batch so far. The maths is right everywhere we checked; the failures are in its tests, and there are two overclaims.

# Batch 2 (2026-11-02): probes, refraction, wet PBR, debris, wall-walk
Files: ~/dev/shared/inputs/nullrun/argon-20261102-0218/ (plus PORT-NOTES.md).

## #6 L1 SH light probes
- Tests pass. Gating by one-sided walls gives zero leak in its test; the naive interpolation leaks badly (mean 6.28 against 0.06).
- STORAGE MISCOUNT: L1 RGB needs 12 coefficients (c0, cx, cy, cz × 3 channels), plus occlusion. "Two RGBA16F 3D textures" hold only 8 channels, so it needs three textures (or a luminance-only directional term). Fix in the port.
- The 2/3 band factor is a convention for unnormalised coefficients. Keep the bake and the evaluation consistent.

## #8 Depth-gated refraction (the Condensate, the Omission)
- Tests pass: the foreground pillar is never overwritten, and no bleed of its colour into the refraction. Standard, correct technique. It depends on wishlist #1 (depth) and #8 (an opaque-scene copy before the translucent pass).

## #18 Wet concrete PBR
- Tests pass: monotonic darkening (to 66% of dry albedo), and grazing Fresnel about 12× steep.
- Sector_SetPlaneReflection is a real existing UZDoom feature (QUICK WIN: try reflective puddle sectors natively now). But a material shader can't modulate the engine's planar reflection per pixel (a puddle mask plus Fresnel); that part needs fork work: expose the reflection texture to the floor material, or a per-pixel reflectivity channel.

## #17 Debris settle and clatter
- Its OWN TEST FAILS, and this time it's a real bug, not a test slip. Resting-contact jitter: gravity re-applies every tic, the floor contact re-bounces with vz around 0.26 u/tic forever, and the prop never reaches the sleep threshold (verified: velocity still 0.259 at tic 199). Fix: treat a sub-threshold normal speed (below about 1.5 × the gravity step) as resting contact (vz = 0) before the sleep check.
- Clatter dB and alert-radius mapping: reasonable, tunable.
- Port note: "unlink from ThinkerList[STAT_ACTORMOVER]" is the wrong statnum (that list is for ActorMover). A dedicated sleeping statnum, or ChangeStatNum, would do it; wake on overlap through the sector's thing lists.

## #19 Per-zone gravity and wall-walk (E10 the Crosswise Hall)
- The SO(3) maths passes (orthonormal to 2e-16, under 7.5° per tic, no gimbal lock at 85° pitch).
- The PORT NOTE IS NOT FEASIBLE AS WRITTEN: Doom collision is 2.5D. Walls are vertical linedefs and floors are sector heights, so rotating velocity into "local gravity space" can't make a wall into a walkable floor; the map data has no such surface.
- Feasible alternative, natively, without engine gravity: build E10 as a NORMAL room in map space, with the "wall" parquet as the actual floor and the furniture placed rotated, then ROLL THE CAMERA 90° while the player is inside (UZDoom supports view roll), easing in and out at the doorway with Argon's geodesic frame. The player walks on what looks like a wall; gravity never changes. Sideways-falling props get rotated gravity in ZScript only. The tea pouring sideways becomes, in map space, tea pouring down.

---

# Round 4 (argon-20261102-0440): reviewed by Claude, 2026-11-02 04:50 CST
Files: nullrun_fork_debris_and_wallwalk_v2.py, nullrun_cyborg_locomotion_and_pain.py, nullrun_fork_fog_reprojection.py. Run isolated (`python -I`) in the scratchpad; probe script at scratchpad/argon4-probe/probe.py.

## Debris v2: PASS (its own test)
- The resting-contact fix is right. A dropped piece bounces twice, clatters at 73.8 dB, then sleeps at tic 36 (the docstring says 31). A prop already resting sleeps at tic 6, and a kick wakes it and it clatters again.
- PORT CAUTION: gravity is skipped while the prop is "resting". In the engine, recompute resting against the actual sector floor (floorz) every tic. Otherwise a prop on a lowering floor, or one knocked off a ledge, will hover, which breaks the physicality pillar.
- The custom statnum is now correct.

## Fog reprojection: the core idea works, but its own test FAILS (an approximation bug) and the static-identity claim is false
- VERIFIED (its motion test passes; numbers from my run):
  - a 180°/s yaw turn: trailing error 0.103 → 0.018 (5.7× less);
  - a 4 m/s strafe: none 0.0301, surface depth 0.0176, optical centroid 0.0062. The centroid is 2.8× better than plain surface depth.
- The centroid formula g(τ) = 1/τ − 1/(e^τ − 1) is correct (I derived it independently).
- BUG: the polynomial "Padé" approximation g(a) = 0.5 − 0.165a − 0.085a² is poor. Max error is 0.15 (at τ = 10), and 0.06 even inside its claimed range of a ≤ 0.95 (it claims under 0.009). The module's own assertion (< 0.012) fails.
  - FIX: the exact closed form in opacity, g(a) = −1/ln(1−a) − (1−a)/a. That's one log in GLSL; it matched to 1e-13 in my run. Use the series 0.5 − a/12 for a < 1e-3 and clamp to [0.05, 0.5].
- The static-identity test FAILS: a static camera differs by 4.4e-8, not bit-for-bit. That's harmless in size, but the claim is false. Port: skip reprojection when the current and previous view-projection matrices are equal.
- The limiter here is whole-frame only. KEEP the fork's existing per-pixel 8% bound, applied against the reprojected history. Argon's whole-frame scaling may be added on top, but must not replace it.
- The portal test only exercises the limiter; it never checks the matrix unfolding. M_prev · T⁻¹ is conceptually right; the fork job must test it on a real rotated portal.
- The 0.03 ms cost is an estimate (hypothesis), not measured. Port notes say "4-tap cross" but the reference uses 3×3.

## Cyborg locomotion and pain: good architecture; its own test FAILS (tolerance only); two real design issues
- VERIFIED (it passes):
  - injuries and treatment: monotone, never self-heal;
  - limp cadence: step intervals 8/15 tics;
  - frustration floor at worst case: 1.97 m/s walking, lift 0.92 s, grapple escape 33 tics;
  - deterministic.
  The architecture is right: weight lives in the body and the weapon spring, and mouse look is never touched. The "verified" mouse-latency check is tautological; the real guarantee is architectural (weapon code never writes Angle or Pitch).
- Its own test FAILS on overdrive speed: 4.875 against 4.93 m/s after one second, a ramp-time tolerance slip. The model is fine.
- REAL ISSUE 1: heavy blows can never kill.
  - apply_heavy_impact floors HP at 8 (from 65 HP or more) and at 1 otherwise.
  - A player at 2 HP survives a 150-damage blow, and ten rebar blows in a row leave you at 1 HP.
  - That contradicts the pillar "lethality both ways". FIX: keep the one-blow survival only from high HP; at low HP a heavy blow kills.
- REAL ISSUE 2: cadence and bob.
  - At 3.65 m/s it takes 3.94 steps/s (9-tic intervals), a jogging cadence; the docstring claims at most 2.25 Hz.
  - The view bob runs once per two steps, so it isn't dipping at the footfalls.
  - Syncing the bob to each step would exceed its own 3 Hz comfort limit at this speed.
  - Underlying point: 3.65 m/s is not a walk. A careful walk at about 2.5 steps/s and 0.9 m steps is about 2.2–2.5 m/s, with 3.65 as a hurried stride (louder footsteps). That's JOSIAH'S CALL.
- Overdrive locks out after 67 tics (1.9 s) of burn, so it's a burst. Treat that as a tuning knob.
- Inconsistent docstring numbers: it says 100→22 HP for 88 damage, but the code gives 40.2.

## Disposition
No implementation jobs launched; per the playtest-first rule, nothing is queued until the cistern slice is fun.
- Fog reprojection: the fork's next fog step after the slice (with the exact centroid, the per-pixel bound kept, and a real-portal test).
- Locomotion: feeds the slice's movement retune after Josiah's first slice playtest, once he decides walk speed (about 2.4 versus 3.65 m/s) and lethality.
- Debris: Tier 3, later.

## Round 5 (2026-11-02 10:43, inputs/nullrun/argon-20261102-1043): cyclic generator plus steering
Ran both isolated (`python -I`, nice 19); probes are in the session scratchpad (argon5/probe). Both pass their own tests: generator 0.26 s, steering 9.9 s.

**Generator (nullrun_cyclic_generator_and_proof.py)**
- KEEP: the proof. BFS over (region, latch mask, lift mask), then reverse BFS from the exit states. Any reachable state that can't reach the exit is a soft-lock. It handles directed one-way drops, two-state lifts, gates and the Hollow-bay detour. My own probe (a pit you can drop into before the valve, with its exit needing the valve) was correctly rejected as SOFT_LOCK_TRAP. That's the piece to port to gen_slice.py.
- NOT A GENERATOR YET: 200 seeds give only 4 distinct connection graphs (4 hand-written variants); the seeds only vary room widths (195 width combinations). "Window repetition = 0" is true by construction, since every node has a unique template name.
- VACUOUS CHECK: exit pull is capped at 288 u in code against a threshold of 384, so it can never fail. With every landmark removed it still reports 288 and passes that check.
- HAND-SET, NOT COMPUTED: sightlines and acoustic distances are booleans and numbers typed into the edges, so "sound before sight" is asserted, not measured. Disc clearance compares socket numbers and rectangle bounding boxes, not real polygon gaps. Portal transforms only feed the step-height check. Armature rooms are never treated as blocking; only the Hollow bay is.

**Steering (nullrun_creature_steering.py)**
- The 500-run "no stall" test treats creatures as points: a 14 u disc overlaps walls in about 5% of agent-tics (it cuts door jambs). The design note says the grid is "eroded by creature radius", but the code doesn't erode.
- Re-test with engine-like collision (a 14 u disc, slide along walls), 100 runs:
  - as shipped: 4% of runs stall over 1 s at its 7.5 u/tic; 30% stall at a walking 2.5 u/tic (max 342 tics; only 37% of packs reach the player).
  - with the promised one-cell erosion added: 0% stall at 7.5 u/tic (99/100 reach). At 2.5 u/tic, 10%: nine are packs pinned against a wall 2–3 m from the player by pack-mates, and one is a real 9 s stall 14 m out.
- Its chase speed of 7.5 u/tic is 8.2 m/s (a sprint), and runs last only 75 tics (2 s), so the test is easy to pass.
- The portal flow vector is hard-coded to (0, 1). The flanking "spread" uses max − min angle, which a ±179° pair passes. "< 1.5 µs per creature in ZScript" is unmeasured (hypothesis).
- KEEP: the flow field (grid Dijkstra plus portal links), the right-hand vortex separation, and the rolling-window stuck detector with a sidestep. The design is right; it needs erosion, disc collision, a walking speed and longer runs.

## Round 5 fixes (2026-11-02 12:20 via Downloads, inputs/nullrun/argon-20261102-1222-r5fix)
Ran both isolated; probes are in the session scratchpad (argon5b/probe). Both pass their own tests: generator 1.4 s, steering 65 s.

**Steering: PASS. Keep it; it's port-ready as the general (non-cistern) nav.**
- It now models a 14 u disc with engine-style AABB push-out and slide, Minkowski-eroded walkability, 2.5 u/tic, 360-tic runs with a moving player, crowd-pinned members taking flank slots, a portal-derived flow, and the largest-gap spread metric.
- My independent per-tic re-measure (200 runs, 252,000 agent-tics):
  - min wall clearance 14.00 u; 0 overlaps;
  - ALL pack members within 3 m of the player in 200/200 runs (its own metric only needed one member);
  - the worst far-from-player slowdown: under 0.5 m moved over 1 s, lasting 1 s + 8 tics; no episode reached 2 s.
- Caveats: the test map is its own 24×24 grid, not the cistern; the "ops per tic" figure is not a ZScript timing. Codex's v7 already has a cistern-specific version (longest stall 18 tics in-engine).

**Generator: the proof still sound, but the layouts are not buildable.**
- Better: a 20-template library, 200 distinct graphs in 200 seeds (also distinct up to renumbering, by a WL hash), an uncapped exit pull that fails with no landmarks, Armature rooms classed as bypassable or fight-required, and LOS and sound computed from geometry.
- NOT BUILDABLE: rooms sit at fixed grid spots with random sizes, so rooms at the same height overlap in 200/200 seeds (2,921 overlapping pairs). Doors are placed at the midpoint between room centres: 7,482 of 8,287 non-portal doors are not on both rooms' walls, and 1,411 lie inside a third room.
- LOS is therefore mostly by construction: the centre-to-centre ray always crosses its own midpoint door, so the computed LOS is false only where a baffle was deliberately placed (the Armature rooms).
- REPETITION: a median of 16 rooms use 10 templates; the most-repeated template appears 3 times (median), up to 5. The picker takes the first allowed template from a shuffled list, which is literally Josiah's "same chamber repeated five times".
- "Exit pull" measures distance to the nearest landmark, not to the next goal.

## Round 6 (2026-11-02, first DIRECT job via agy: shared/argon/20261102-122648-argon-r6-generator-embedding/)
- VERIFIED independently (Claude's probe, 200 seeds): 0 overlapping rooms at the same height; 0 of 4,515 non-portal doors off a room wall; the proof intact; repetition limits and weighted template choice hold.
- FAILS the brief's intent:
  - (1) One macro plan: the exit is WEST of the hub in 200/200 seeds, and the plots show the same skeleton every seed. The generator uses an integer cell grid, with cycle 1 from 3 configs via (seed-1)%3. 150 distinct lattice occupancies are stretched variants of one plan.
  - (2) Rectangles butting directly against each other on a grid, with almost no corridors or tunnels: the "tiled boxes" Josiah rejected on 11-01.
  - (3) The exit-pull threshold was raised to 1,920 u, just above the observed 1,898 u maximum (test tuned to the data).
- Round 7 sent (same conversation): free-form socket growth from DeepSeek's real 32-template library; a randomized plan; at least 40% connector links; doglegs for Armature approaches; vertical layers; thresholds stated first (exit octant ≤25%, same-plan IoU >0.6 for ≤5% of pairs, exit pull ≤768 u); export_level_json for UDMF.

## Round 7 (2026-11-02, shared/argon/20261102-132334-argon-r7-freeform-generator/): PASS. Port to gen_slice.py.
- Free-form socket snapping from DeepSeek's 32-template library, polygon overlap and slab checks, export_level_json, thresholds stated first, 18 negative tests.
- Claude's independent check (60 seeds, my own transform of the library footprints, an 8 u raster overlap test, door-to-wall distances):
  - my transforms match Argon's polygons in every room;
  - 0 same-band overlaps;
  - 0 of 1,164 doors off a wall;
  - exit octants spread {10,4,8,9,7,6,6,10} (max 16.7%).
- The seed 1–12 plots show genuinely different plans, connectors and doglegs before Armature rooms, and z-layers.
- Open:
  - 7 legacy socket ids disagree with normal_deg (key on normal_deg);
  - some long dead-end corridors (visual QA);
  - exit pull max 752 u under a pre-stated 768 u.
