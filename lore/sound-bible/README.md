# NULL RUN — sound design bible (text only)

DeepSeek worker, job `20261101-130728-deepseek-null-run-sound-design-bible-text-only`,
delegated by Claude Code for Josiah. **Everything here is a PROPOSAL to accept or reject.**

- **ROOMS.md** — one acoustic profile per stratum and room type (bay, vault, corridor, shaft, open
  basin), in the ZDoom/UZDoom REVERBS (EAX/EFX-style) vocabulary: decay time and HF ratio, reflection
  level and delay, reverb level and delay, diffusion, density, room and roomHF levels. Reasons and
  intended player feeling for each.
- **SFX-LIST.md** — every sound the game needs: player, seven weapons, all 21 creatures plus the two
  optional bosses, world, UI. Per sound: duration, priority, loop flag, reverb send, and a synthesis
  recipe for numpy/scipy. No external recordings.
- **MIX.md** — loudness targets, ducking, tell-audibility rules, how to keep long cistern tails from
  smearing combat, and audio safety (the photosensitive-equivalent rules).

## What was read

`nullrun-text-20261101/WEAPONS.md` · `nullrun-lore-20261101/{BESTIARY,STRATA}.md` ·
`nullrun-lore-batch-c-20261101/{VISITOR,PLEAT,SPAN,REUNION,RAVEL,WHITE-BLOOM}.md` (full) and `NOTES.md`
(in part) · `nullrun-newsheets-lore-20261101/{CIRCUIT,UNDERPRINT,HEM,BOSSES,SPRITE-ROLES}.md` ·
`codex/nullrun-build-20261101b/REVIEW.md` · `nullrun-depths-layout-20261101/DESIGN.md` ·
`nullrun-adaptive-music-20261031/DESIGN.md` · the cistern/basin/transit/rootcathedral pack reports ·
the shipped `living-depths.pk3` SNDINFO (the build's only audio today: four `ld-*` loops).

## Authority and scale

Where a creature sheet describes a sound in words, the SFX recipes implement **that** sound; where it is
silent, the recipe is mine. Encounter timings are the sheets' prototype values at **35 Hz** (1 tick =
28.6 ms); SFX durations here are seconds and must be re-timed against shipped states. Creature "sound
cues" sections in the lore are treated as binding art direction.

## Not done

No audio rendered, no pk3 built, nothing pushed or posted. The REVERBS lump's exact line order should be
verified against this fork's loader before authoring the lump (see ROOMS.md, "Implementation notes") —
forks differ, and I could not read the engine source on this machine.

## Status

PROPOSAL. Nothing here is canon until Josiah accepts it.
