# Null Run — cistern found documents (job 20261102-125236)

DeepSeek worker for Claude Code, on Josiah's workstation. **Status: PROPOSAL.**
Text only; nothing rendered, built, imported, pushed or posted. All strings are original.

**Claim.** DeepSeek writes only `shared/deepseek/nullrun-cistern-documents-20261102/` for this job.
`shared/CLAIMS.md` was not edited because the job's write scope is this folder; the claim is recorded
here and should be added/removed by the requester.

## Files

| File | Contents | Counts |
| --- | --- | --- |
| `DOCUMENTS.md` | self-writing ledger, inspection tags, maintenance notices, pickup labels, gauge cards, manifest, continuity notes | 8 + 6 + 4 + 6 + 3 = 27 documents; 30 text blocks including both sides of the 3 gauge cards |
| `CHECKS.md` | the automated line-length, count and duplicate checks, with results | — |

## What was read

`shared/inputs/nullrun/PILLARS.md` (full) · `nullrun-cistern-text-20261102/CISTERN-TEXT.md` and
`WAYFINDING.md` (full) · `nullrun-lore-armature-20261101/ARMATURE.md`, `NOTES.md`, `ECOLOGY.md`
(the relevant sections on the standing figure, the wire tick, the Spindle's ceramic tick and the
free/controlled distinction) · `nullrun-progression-20261102/RUN-STRUCTURE.md`, `MATERIALS.md`,
`NOTES.md` · `nullrun-lore-20261101/DOCUMENTS/` (the cistern documents) and `STRATA.md` ·
`nullrun-text-20261101/INWORLD-TEXT.md`, `AMMO-PICKUPS.md`, `WEAPONS.md` ·
`nullrun-pack-cistern-20261101/manifest.json` and `REPORT.md` · `nullrun-sound-bible-20261101/ROOMS.md`
(cistern and pump-room acoustics). No credentials, firmware or OS images were opened; nothing outside
`shared/inputs/nullrun/PILLARS.md` and the named DeepSeek/Cistern files was read.

## Decisions made (for review)

1. **The self-writing ledger lives in the Gauge Gallery hub.** The hub is the only room the player
   reliably re-crosses, so one entry per return works. The ledger lags the player by one visit and never
   writes while watched; the last entry prints the run's registry number. A fallback placement is in
   `DOCUMENTS.md` §1 and §8.
2. **The registry number is a token, not a fixed name.** `NR-311-R` is the example used across the pack;
   the build substitutes the run's case number. The collision with the Armature's intake number in
   `ARMATURE.md` is flagged in §8.1 — it can be a deliberate horror beat or removed.
3. **The dead tree hint is T4/T5.** "No growth rings" and "moved 2 m since 112 — do not re-tag, observe."
   Neither tag says what the tree is. If the Hollow's sheet contradicts the detail, change the finding,
   not the form.
4. **The tick notice distinguishes one tick from kept time.** A free stander's tie wire ticks once; the
   Spindle's ceramic tick keeps time. N2 says this in the office's terms without naming the Spindle.
5. **The pickup labels use the established names.** Index Block, Seal Case, index strip, Cell Rack from
   `AMMO-PICKUPS.md`; the stores medical tin and the field splint kit from `PILLARS.md` §3.
6. **R.D.** appears once, in pencil, in the ledger's margin. It is a callback to `CISTERN-TEXT.md`;
   keep or cut together.
7. **Every in-world line is 38 characters or fewer.** The longest is 34. Each item states its placement
   and `Max line: 38`.

## Open (for Josiah / Claude Code)

- **The registry number.** `NR-311-R` is both the example run seed and the Armature intake number. If
  the collision is unwanted, substitute a neutral seed; the line is a token. If wanted, the office files
  the case and the creature under one number. Decide before the number is baked.
- **The ledger's home.** If the slice does not return to the Gauge Gallery after the basin gate, move
  the ledger to the Pump Inspection Bay exit, or add the duplicate L8 page on the stair landing.
- **The dead tree's behaviour when read.** T4/T5 assume the tree does not attack while read. If the
  Hollow moves when approached, the tags need to be readable from outside its reach; that is a layout
  decision.
- **The gauge card flip.** The cards assume the player can flip them after turning the valve. If that
  interaction is too costly, print both states on one card as two columns.
- **The one-text-per-room rule.** This pack uses "wall texts two per room, tags and labels on their
  fixtures". If the earlier pack's stricter rule is binding, move N1 to the bay door; see §8.6.
- **R.D.** keep or cut. If cut, drop the pencil note with it and do not replace it with another name.

## Not done

No art, texture, engine, audio, level geometry or git work. No file outside this folder was written.
No string was reused from `INWORLD-TEXT.md` or `CISTERN-TEXT.md`; the exact-line check in `CHECKS.md`
reports zero duplicates.
