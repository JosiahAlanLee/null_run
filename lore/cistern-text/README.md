# Null Run — cistern text layer (job 20261102-002329)

DeepSeek worker for Claude Code, on Josiah's workstation. **Status: PROPOSAL.**
Text only; nothing rendered, built, pushed or posted. All strings are original; no real
place, person or organisation is named.

**Claim.** DeepSeek writes only `shared/deepseek/nullrun-cistern-text-20261102/` for
this job. `shared/CLAIMS.md` was not edited because the job's write scope is this
folder; the claim is recorded here and should be added/removed by the requester.

## Files

| File | Contents | Counts |
| --- | --- | --- |
| `WAYFINDING.md` | Descent Works sign system: four schemes, six sign types, reading order, 17 generator rules, generator contract, 40 tagged sign strings, one worked room | 40 strings: exit 7, hub 6, shortcut 7, dead end 6, optional 6, danger 4, water depth 4 |
| `CISTERN-TEXT.md` | plaques, gauge labels, maintenance notices; ledgers; graffiti; object vignettes | 25 (10 plaques + 8 gauges + 7 notices), 10 ledgers, 6 graffiti, 3 vignettes |
| `SOUND-CUES.md` | audible pulls with the bearing each serves, staging notes, direction table, cue sheet by route | 14 cues incl. the silence cue; 7 routes |

## What was read

`shared/deepseek/nullrun-text-20261101/INWORLD-TEXT.md` (full) ·
`shared/deepseek/nullrun-lore-20261101/STRATA.md` (full) and `GENERATORS.md` (rules and
cistern tables) · `nullrun-sound-bible-20261101/ROOMS.md` (cistern and basin acoustics,
§4.3–4.4) and `SFX-LIST.md` (priority ladder) · `nullrun-depths-layout-20261101/DESIGN.md`
(room templates, door and exit conventions) · `nullrun-pack-cistern-20261101/REPORT.md`
(piece and vignette inventory). No inputs, credentials, firmware or OS images were
opened.

## Decisions made (for review)

1. **Works Zero = the sill of Sluice 1**, not the cistern floor. Gives the three gauge
   marks, the floor depth and the sump a single consistent datum across all three files.
   Water is at `+1.95`; high water `+2.40`; old line `+1.60`.
2. **Route letters are works letters, not compass.** G/L/S/P/D/W/B with the mapping in
   `WAYFINDING.md` §2.2. Loop suffix `a`/`b` per the brief's example rule.
3. **Basin Stair `B1` is present but sealed** in this slice, consistent with the
   settling basin's placement below the cistern in the prior pack. Its far transom is
   lit; the near face is unlit, so it works as a promise rather than a route.
4. **"Unopened Tin / Private Mirror style"** was not documented anywhere I could read.
   Interpreted as self-contained object vignettes: one object, one short piece of
   writing, no explanation, no interaction beyond reading. Confirmed against the
   Unopened Tin name by treating the tin as never openable.
5. **R.D.** is a recurring set of initials in four records. It is not a person and is
   never explained.

## Open (for Josiah / Claude Code)

- Whether the gauge datum in decision 1 is the level's actual geometry. If the floor or
  water height changes, the three marks and the depth tags move with it; the strings are
  the cheap part to regenerate.
- Whether the sealed `B1` route should exist in this slice at all. If not, strings 7,
  18 and 25 and the basin entries in `SOUND-CUES.md` should be dropped together.
- Whether the second bell's early answer (the one allowed lie) is acceptable as a
  per-seed fixed anomaly. It is flagged in `SOUND-CUES.md` §2 and §3.4.
- Whether sign materials/colours are art-directed yet. This pack proposes ochre/black
  (Descent Works), oxide red/white (Works & Descent), bare bronze (Margins reuse) and
  green/cream enamel (pace plates); no textures exist.
- The requester should add the claim to `shared/CLAIMS.md` if the delegation rule
  requires it there rather than here.

## Not done

No art, no audio, no level geometry, no engine work, no git operations. No string was
reused from `INWORLD-TEXT.md`; that was checked by exact match.
