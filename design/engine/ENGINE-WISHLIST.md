# Null Run engine fork: wishlist (compiled by Claude from the 2026-10-31 to 11-02 sessions)

Fork: `~/dev/uzdoom-nullrun` (UZDoom 5.0.3 import on main). Each item lists the wall we hit, where the evidence lives, and what the fork would add. Ranked roughly by value to Null Run against effort. `[in progress]` means a job is already on it.

## Tier 1: directly blocks the look or the design

1. **Scene depth for custom post-process.** `[in progress: job 20261102-014346, branch codex/depth-postprocess]`
   - Wall: custom PPShaders can't read depth (nullrun-engine-20261101/SUMMARY.md, PATCH-IDEAS #3), so no true distance or height fog, and no depth-masked effects.
   - Unlocks: Silent Hill 2 fog, height fog, depth haze, the Omission's orb mask, the Condensate's refraction masking.
2. **Sight and sound through rotated line portals.**
   - Wall: CheckSight fails through rotated portals, and spatial audio across rotated connections is silent (nullrun-noneuclid-20261101/PORTALS.md). Argon's unfolded-ray maths fixes sight in ZScript (nullrun-argon-open-problems-20261101), but the engine's own LOS, hitscan targeting, sound propagation and monster wake-up still ignore the rotation.
   - Unlocks: creatures that see, hear and shoot through the impossible spaces natively (looping corridors, rotated junctions, the lightwell, the mirror room).
3. **Hitbox matches the picture: per-pixel sprite hit testing plus weak-point masks.**
   - Wall: hits resolve against a cylinder, but Null Run's anatomy system (an Armature's legs, core and collar; a weapon-versus-material table) needs to know WHERE on the sprite a shot landed. The core moves per frame and per angle and is hidden from behind.
   - Add: an opt-in per-actor mode where the hitscan or projectile trace tests the sprite's alpha at the hit point, plus a "region mask" texture channel per frame (core, legs, collar and so on), with the region ID and texel UV passed to DamageMobj / ZScript.
   - Unlocks: the DF-style anatomy with honest hitboxes; Monster Hunter-style part breaking.
4. **Smooth sprite rotation and pitch transitions.**
   - Wall: pre-rendered sprites pop between angles (Argon's SDF morph failed on real banks). We fake 5 pitch bands in ZScript.
   - Add: (a) native pitch-band frame selection (sprite frames indexed by yaw AND camera elevation, with hysteresis); (b) an optional short crossfade or dither between adjacent rotations or bands over a few frames, done in the sprite shader with two textures bound.
   - Unlocks: less popping without 3D models, and native support for our whole sprite pipeline.
5. **Per-pixel lighting on sprites (normal-mapped billboards).**
   - Wall: sprites get flat aggregate light; normal maps aren't applied to sprites (PATCH-IDEAS #4). We use a rim-light fallback.
   - Add: an opt-in per-pixel light list for sprites, using baked camera-space normals per rotation and band (we can bake these in Blender).
   - Unlocks: creatures lit by the door shaft in the Hollow target frame, pools of light that actually light the creature, the lighting-study styles applied to actors.

## Tier 2: big wins for atmosphere and sound

6. **Light probes or lightmap sampling for actors and models.**
   - Wall: the lightmap bake excludes models, and actors don't pick up baked light (nullrun-cycles-lightmaps, nullrun-upscale-gi).
   - Add: sample the baked lightmap or a probe grid at the actor's position for sprites and models.
   - Unlocks: creatures that match the room's baked light.
7. **Volumetric light shafts.**
   - Wall: faked with translucent geometry.
   - Add: with depth available (item 1), a screen-space or raymarched shaft pass for designated lights (the door daylight in the Hollow target frame).
8. **Scene-colour access for translucent sprites and models (refraction).**
   - Wall: a sprite can't sample the scene behind it, so the glass-clear Condensate is unsolved (Argon batch 2).
   - Add: an opaque-scene copy bound to opt-in translucent materials.
9. **A proper external event bus (OSC or UDP) instead of stdout scraping.**
   - Wall: the music and SFX bridge reads NRAUDIO/NRSTATE lines from engine stdout; fixed ports clashed with tests and blocked Josiah's launch.
   - Add: a small built-in, opt-in localhost event channel (game events out, beat and phase in), on per-run ports, exposed to ZScript as send and receive.
   - Unlocks: clean Pd and Rack integration (studio and distribution modes), and beat-locked sigils.
10. **A transport or beat clock service** (PATCH-IDEAS #2): an external beat and phase readable in ZScript and shaders, interpolated at render time. Pairs with item 9.
11. **Reverb that does what the zone asks.**
   - Wall: OpenAL accepts flutter and modulation parameters with no audible effect; SNDINFO `$environment` is unsupported (nullrun-sound-20261101/ENGINE-AUDIO.md).
   - Add: real early reflections and flutter, or a per-sound reverb send out to Pd (item 9) so the Pd FDN can take over.
12. **Live HydraPy texture over shared memory** (PATCH-IDEAS #1): HydraPy scenes running live on in-world monitors, the Omission's field, the sky.

## Tier 3: robustness, tooling, distribution

13. **ZIP64 or large-archive support**, or a documented multi-archive load order. We hit the ZIP size limits, ZIP64 failed natively, and the builds are split into 9 PK3s.
14. **Test-isolation flags:** never grab the audio device exclusively (`-noaudio`, or the default PulseAudio/PipeWire device), a deterministic headless capture and screenshot mode, and no fixed-port defaults, so automated tests can never block a human playtest.
15. **A separate debug log channel**: script prints that go to a log or console only, never to the screen notification area. We solved it with an nr_debug cvar; native would be cleaner.
16. **Hit position into DamageMobj**: pass the exact trace hit point and normal into ZScript damage handling (a subset of item 3, useful on its own).
17. **Lightweight physics for small props and debris**, for the physicality pillar: scrap that clatters, tins that roll, things that settle. Simple rigid bodies or a "settle" behaviour, not a full physics engine.
18. **Wet and reflective floors**: verify and improve UDMF reflective planes and PBR specular on floors, for the wet concrete in the target frame. (The target-frame job is testing what already works.)

## Tier 4: ambitious, maybe never

19. **Per-zone gravity direction** (Argon's port note isn't feasible in 2.5D collision; the native alternative is a normal room plus a 90° camera roll, see ARGON-FORK-MATH-REVIEW.md), for E10 the Crosswise Hall (walk on the wall). Currently faked with sideways furniture.
20. **A native navmesh or portal-aware nav graph** in the engine. Currently ZScript A* plus offline graphs.
21. **Height-fog and fog-volume sector properties** (if item 1 lands, these can be shader-side instead).

## Process
- Each feature on its own `codex/<feature>` (or `deepseek/<feature>`) branch, small diffs in upstream style, opt-in and zero-cost when unused, with an upstream-PR-ready description in FORK.md.
- Rebase onto upstream git history before publishing. GPL-3 throughout.

## Maths references (Argon, 2026-11-02, reviewed)
See ARGON-FORK-MATH-REVIEW.md and ~/dev/shared/inputs/nullrun/argon-20261102-0207/: volumetric fog and shafts (#1, #7), per-pixel sprite lighting (#4, #5), pixel hitboxes (#3, #16), portal audio and early reflections (#2, #11). Implementation jobs for those items start from these.
Batch 2 (argon-20261102-0218): probes #6, refraction #8, wet PBR #18 (Sector_SetPlaneReflection is a native quick win), debris #17 (resting-jitter bug to fix), wall-walk #19 (use the camera-roll alternative).
Round 4 (argon-20261102-0440): fog reprojection for #1 (use the exact centroid formula, not the polynomial), debris v2 for #17 (passes), careful-cyborg locomotion and pain (feeds the slice movement retune).

## DeepSeek scoping (2026-11-02, read-only; I spot-checked 4 citations and all held)
~/dev/shared/deepseek/uzdoom-fork-scoping-20261102/SCOPING.md and QUICK-WINS.md, with file and line touch points and S/M/L/XL effort for items 2–18. Corrections to this list:
- **#6:** native light probes already exist and light sprites and decals (FindLightProbe, hw_spritelight.cpp:39); only models miss out. Lightmaps are gated by `-enablelightmaps`. Item 6 shrinks to "models plus our bake pipeline".
- **#15:** native already: `Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY)`.
- **#16:** largely native: ZScript `FLineTraceData.HitLocation`.
- **#2:** the rotation exists in the renderer and in `P_TranslatePortal*`, but `P_CheckSight`, `P_RecursiveSound` and `CalcPosVel` use offset-only `PosRelative`, so the fix is well located.
Recommended order: quick wins 13, 14, 15, 16 and 18; then item 2.

## New candidates (2026-11-02, for the other strata; source facts checked in ~/dev/uzdoom-nullrun)
22. **Creature shadows: "see the shadow before the creature".**
   - Now: the dynamic-light shadow map is built from wall lines only (doom_aabbtree); sprites RECEIVE shadow tests (hw_spritelight.cpp:171) but never cast.
   - Add, for designated lights: (a) actors as occluders in the shadow map (cheap, crude); (b) the sprite's silhouette projected from the light onto walls and floors, so the Hollow's shadow stretches down the corridor from the door shaft.
   - Pillar 5 ("show less") in every stratum.
23. **Projected-texture lights (gobos or cookies), animatable.**
   - Now: there is no projector or cookie support in the renderer.
   - Uses: window bars; stained boneglass colour (the ossuary's boneglass conservatory); fan blades turning (E20, the dead boiler house); water caustics on the cistern ceiling; root shadows (the root cathedral).
   - Shares its projection code with 22(b).
24. **Scaled portals: "bigger on the inside".**
   - Now: line portals carry rotation and translation only (portal.h mAngleDiff and mSinRot; no scale).
   - Add: a scale factor; render through it scaled, and rescale the player (radius, height, speed, eye) on crossing.
   - Uses: the unshared room and the near sky (E15–E16), doll-house rooms, impossible interiors.
   - Ambitious: the collision and physics edge cases are the risk.
25. **Water you can see into.** An animated surface normal plus screen-space refraction of what's under the water (shares #8's scene copy), with an underwater fog volume (with #1's depth). Native has swimmable 3D floors, colormaps and plane reflections. For the cistern (drowned records) and the basin.
26. **Model collision hulls** (oriented boxes or convex hulls for MD3 and IQM props instead of cylinders): angled furniture you actually bump into (the Crosswise Hall), train cars (the transit switchyard chapel), and props that block properly.
27. **Path-based sound occlusion:** sounds through walls are low-passed, and sounds arriving around corners come from the doorway's direction ("sound before sight" for the Armature tick). This extends #2 and #11; Argon's portal-audio maths applies.

NATIVE NOW (no fork needed):
- **Canvas textures** (ZScript `TexMan.GetCanvas` plus `Canvas`, r_canvastexture.cpp): live-drawn in-world surfaces. Uses: ledgers that write themselves (the scriptorium), gauges and monitors that update, sigils drawn onto walls, signs that change state, a live view of the FILE.
- Camera roll (the Crosswise Hall, #19).
- Sector_SetPlaneReflection (wet floors, #18).

Recommended fork order after the quick wins: 22 and 23 together (one projection system, used everywhere); then #2 (portal sight and sound); 24 as the showpiece.

ROUND-2 SCOPING (DeepSeek, 2026-11-02; `~/dev/shared/deepseek/uzdoom-fork-scoping-2-20261102/SCOPING-2.md`; Claude spot-checked 5 citations: 4 hold, 1 wrong):
- Key constraint: sprites are lit on the CPU (hw_spritelight.cpp), geometry and models on the GPU. Light cookies and actor shadows reach walls, flats and models, but not sprites, unless sprite lighting moves to the GPU (not scoped).
- 22a (S): circle casters folded into the existing 2D shadow map (far-exit min, CPU RayTest plus shadowmap.fp). Native: r_actorspriteshadow blob shadows. 22b (L): a light-space depth atlas.
- 23 (M, spot only): the light record has 2 unused floats (hw_dynlightdata.cpp data[14..15]) for the cookie index.
- 24: M1 visual scale (M); M2 traversal (XL, breaks demos).
- 25: c (S, normal-mapped animated water); a (M, underwater fog); b (L, needs #8).
- 26: L–XL; last. CanCollideWith runs after the radius rejection, so it can't help.
- 27: L after #2. ML_SOUNDBLOCK and CalcSectorSoundOrg are native.
- CORRECTION: DeepSeek says SSBO binding 7 is free, but BONEBUF_BINDINGPOINT = 7 (shaderuniforms.h:31). Use 8.
- Revised order: 22a → #2 → 23 → 22b → 25c → 25a → 27 → 24 M1 → 25b → 26.

MODEL PATH (2026-11-02; Josiah approved a sprite-vs-IQM A/B and is "willing to update this engine until it feels native"):
- Native now: IQM skeletal models, MODELDEF and GLDEFS materials (normal and PBR), ZScript bone control (SetBoneRotation and Translation, GetBoneFramePose, named animations via GetAnimStartFrame). Models are GPU-lit per pixel and RECEIVE the shadow map; cookies (#23) would light them too.
- 28 (new): models CAST shadows (an actor depth pass into the light shadow map; reuses the 22b atlas, but with real mesh depth instead of sprite silhouettes).
- 29 (new): model LOD with a sprite fallback at fog distance ("show less"), switched on screen size.
- 30 (new): native bone-capsule hit tests (trace against per-frame bone capsules in C++; the ZScript version first).
- Codex's IQM job writes ENGINE-NEEDS.md with what the A/B actually exposes; fold that in here.

22a IMPLEMENTED (DeepSeek, 2026-11-02; branch deepseek/actor-shadow-columns in ~/dev/uzdoom-nullrun-deepseek, commit 84d8363; compiled clean, NOT run yet):
- 32 nearest-camera circle casters as an SSBO at binding 8 (GL and Vulkan); far-exit min in CPU RayTest and shadowmap.fp; cvar gl_light_shadowmap_actors (default off).
- Claude's review found a BUG: a light whose origin is inside a caster circle (the player's flashlight; a creature's own glow) gets clamped to the owner's radius, i.e. blacked out.
- FIXED in commit ca3d2f8 (turn 2): casters containing the light origin are skipped (both consumers); the camera is excluded by default (gl_light_shadowmap_actors_self); positions are interpolated; the physical radius is used (gl_light_shadowmap_actors_renderradius opts in); a search radius cvar gl_light_shadowmap_actorsdist (default 2048). Compiled clean. NEXT: Codex in-engine test plan (PATCH-NOTES.md, 15 items), then merge to the fork main. Cost 1.39 USD.

GORGON IN REVERSE (Josiah, 2026-11-02: "use the game assets in reverse with Gorgon eventually, parts of scenes, 3D environments"):
- #9 event bus and #10 beat clock: build them with GORGON as the reference client. OSC/UDP in, so tracker automation lanes drive camera rails, light and fog levels, sector moves and creature triggers; the engine FOLLOWS Gorgon's clock (Gorgon is always the master).
- 31 (new): a frame-output path (shared memory or a PipeWire video stream, building on the existing capture.so used by the slice launcher) into HydraPy External/FrameSource, so the engine render is one layer of a Gorgon scene (Program/Aux). Plus a performance mode: no HUD or weapon, an invisible player, cinematic camera actors on rails.
- 32 (new): exporters: creature sprite banks as atlases plus JSON (yaw, pitch, action, frame) for a HydraPy "puppet" layer; room plates with depth (the fork has depth) for 2.5D parallax and depth-keyed feedback; UDMF→glTF and IQM→glTF for Blender and Mac renders.
- Keep the living-surface and painterly GLSL as SHARED modules that run as both fork step shaders and HydraPy operators (they were ported from HydraPy; keep them two-way).
