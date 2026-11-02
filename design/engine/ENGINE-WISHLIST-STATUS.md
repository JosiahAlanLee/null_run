# Null Run engine fork: wishlist status (2026-11-02, updated 9:20 am)

Fork: `~/dev/uzdoom-nullrun` (UZDoom 5.0.3, GPL-3). Feature work is on branch `codex/depth-postprocess`. Details for each item are in ENGINE-WISHLIST.md.

**Legend**
- ✅ done (working prototype in the fork)
- 🟢 already native (UZDoom can do it; no fork work needed)
- 🟡 partly done or partly native
- 📐 maths ready (Argon, reviewed and run by Claude)
- 🔍 scoped (DeepSeek found where it goes in the source)
- ⬜ not started

## Tier 1: directly blocks the look or the design
| # | Item | Status | Notes |
|---|---|---|---|
| 1 | Scene depth for post-process (Silent Hill 2-style fog) | ✅ | Depth fog plus height fog: 0.27 ms at half resolution on the 4090; passes the flash-safety audit. OpenGL only. Next: Argon's reprojection to stop smearing on fast turns (📐, using the exact formula, not its approximation). |
| 2 | Sight and sound through rotated portals | 📐 🔍 | Creatures can't see, hear or shoot through rotated portals. The fix is well located: sight, sound propagation and positional audio all ignore portal rotation. |
| 3 | Hitbox matches the picture (per-pixel hits, region masks) | ✅ (ZScript) | Done without the fork: the anatomy lab and slice v5 use per-frame region masks (legs, core, collar), checked at 120 poses and angles. A native version is only needed if it gets slow. |
| 4 | Smooth sprite rotation and pitch transitions | ⬜ | Still faked with pitch bands in ZScript. |
| 5 | Per-pixel lighting on sprites | 📐 | Argon's band-consistent lighting maths passes. |

## Tier 2: atmosphere and sound
| # | Item | Status | Notes |
|---|---|---|---|
| 6 | Light probes for actors | 🟡 🟢 📐 | Native probes already light sprites and decals; only models miss out. Argon's probe maths passes (it needs 3 textures, not 2). |
| 7 | Volumetric light shafts | ✅ | A door-shaft light runs in the fork's fog v2. There's no shadowing inside the shaft yet. |
| 8 | Refraction behind translucent sprites (the glass Condensate) | 📐 | Needs a copy of the opaque scene; depth from #1 is done. |
| 9 | External event bus (OSC/UDP) | 🔍 | The engine's own network-command system is the model to follow. |
| 10 | Beat clock | 📐 | Argon's drift-free 35 Hz beat clock maths exists. |
| 11 | Reverb that works | ⬜ 📐 | Argon's reverb and early-reflection maths exists, but used the wrong scale (64 u/m, not 32), so it needs a recheck. |
| 12 | Live HydraPy texture | ⬜ | Native canvas textures (below) cover scripted drawing, but not live frames streamed in from HydraPy. |

## Tier 3: robustness, tooling, physical world
| # | Item | Status | Notes |
|---|---|---|---|
| 13 | Large archives (ZIP64) | 🔍 | Quick win: ZIP64 is read, but entries over 2 GB are skipped. |
| 14 | Test-isolation flags | 🟡 | Worked around (per-run ports, private audio, the playtest lock). A native flag is a quick win. |
| 15 | Debug text never on screen | 🟢 ✅ | Native `Console.PrintfEx(PRINT_LOG\|PRINT_NONOTIFY)`. Already used in your cistern copy. |
| 16 | Hit position into damage | 🟢 | Native: line traces already report the hit location to scripts. |
| 17 | Debris that clatters and settles | 📐 | Argon v2 passes (it settles in about 1 s and wakes when kicked). |
| 18 | Wet and reflective floors | 🟡 🟢 | Native plane reflections work (tested in the target frame), but they're too smooth for puddles. A puddle mask and roughness need the fork. |

## Tier 4: ambitious
| # | Item | Status | Notes |
|---|---|---|---|
| 19 | Walk on the wall (E10, the Crosswise Hall) | 🟢 📐 | Solved without the fork: a normal room plus a 90° camera roll, using Argon's smooth-roll maths. Not built yet. |
| 20 | Creature navigation | ⬜ | Argon round 5 (stall-free steering) has been requested. |
| 21 | Height fog and fog volumes | ✅ | Covered by #1's fog shader. |

## New candidates (scoped by DeepSeek, round 2)
Effort: S about a day, M a few days, L about a week, XL more than that.
| # | Item | Status | Notes |
|---|---|---|---|
| 22 | **Creature shadows: see the shadow before the creature** | 🔍 | Two versions. **22a (S):** creatures block light as a solid column in the existing wall shadow map; a crude shape, but it works with point lights. **22b (L):** the true sprite silhouette, which needs a new rendering pass. Native today: a dark blob straight under each creature (no light direction). A catch for both: sprites are lit on the CPU, so a creature's shadow falls on walls and floors but not on other sprites. |
| 23 | **Lights that project an image** (bars, boneglass colour, fan blades, water ripples) | 🔍 | M, for spot lights only; one step more if a point light needs it (ceiling caustics). Shares all its code with 22b. Same catch: it lights walls, floors and models, not sprites. |
| 24 | **Bigger-on-the-inside portals** (scaled portals) | 🔍 | **M1 (M):** you see through it at a different scale (a doll's house, or a near sky). **M2 (XL):** you walk through and change size; it breaks demos. Build M1 first, then decide. |
| 25 | Water you can see into (cistern, basin) | 🔍 🟡 | **25c (S, mostly native):** animated normal-mapped water. Try this first. **25a (M):** fog under the water. **25b (L):** refraction, which needs #8. |
| 26 | Solid props (collision boxes for models) | 🔍 | L to XL, and last: the only item that can break demos. Hand-made boxes for a few set pieces are much cheaper. |
| 27 | Sound around corners (path-based occlusion) | 🔍 🟡 | L, after #2. Partly native: sound-blocking lines, and room sounds that come from the nearest wall. A cheaper first pass (a sight test plus muffling) is possible without #2. |

DeepSeek's citations check out, with one fix: shader buffer slot 7 is taken (by bones), so the shadow list needs slot 8.

## Native now, ready to use in the game
- 🟢 **Canvas textures:** surfaces drawn live by scripts. Ledgers that write themselves, updating gauges, sigils drawn onto walls, signs that change state.
- 🟢 **Camera roll** (#19).
- 🟢 **Plane reflections** (#18).
- 🟢 **Light probes for sprites** (#6).

## Suggested order
1. Quick wins: 13, 14, 16 and 18.
2. Fog reprojection (#1 follow-up).
3. 22a (creature shadows, the cheap version: about a day).
4. #2 (portal sight and sound); 22b, 23 and 27 depend on it in portal-heavy maps.
5. 23, then 22b (one projection system).
6. 25c (water look), then 24 M1 as the showpiece.

No fork building until you've played the cistern slice.
