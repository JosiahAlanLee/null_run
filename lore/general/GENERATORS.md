# GENERATORS — per-run history rules

**Status: PROPOSAL for Josiah to accept or reject.** Rules for a generator that writes a slightly different history for every seed, Dwarf-Fortress-style: who sealed which door, which department flooded the cistern, whose account survives. The output is text records a run can scatter (terminal entries, plaques, chits) plus one binding per floor that changes a door, a vendor, or a sign.

## 1. Safety rules (the generator must never break these)

- Never emit a single universal cause, transformation event or responsible institution.
- Never have a former-human inhabitant recognise that they stopped being people. They may notice a cuff, a voice, a doorway — never the whole pattern.
- Never give the Applicant, Erratum or Unaddressed a human origin or a hidden human mind.
- Every generated fact must appear in at least two records, and at least two of those records must contradict each other about it.
- The seed selects *who*, *what* and *why*; it never selects *the truth*. Keep one blank in every account ("awaiting assessment").

## 2. Seed discipline

- Use the run seed (the one the floors are already built from). Split it with a different salt per table: `rng = SplitMix64(seed ^ 0x9E3779B97F4A7C15 * table_id)`.
- Roll order: actors first, then events, then contradictions. Cache per seed so every record in the run agrees with itself.
- All rolls are d6/d12 unless noted. Rerolling a table must never invalidate an already-written record.

## 3. Actor tables (who is credited or blamed)

**Table A — departments and offices (d12).**
| d12 | actor |
| --- | --- |
| 1 | Works & Descent (drains and stairs) |
| 2 | Records Amended (the filing of the filed) |
| 3 | Persons Awaiting Assessment (never meets anyone) |
| 4 | Stores (issues what was never ordered) |
| 5 | Lighting & Fluorescent Fittings |
| 6 | Descent Works, Predecessor (absorbed, resentful) |
| 7 | The Shelf-Keepers' Order (funerary) |
| 8 | The Bronze Margins (copying and precedent) |
| 9 | The Photographic Section (portraits, cropped) |
| 10 | The Gauge & Sounding Office (read, not believed) |
| 11 | No department; the paperwork names nobody |
| 12 | Two departments; the handwriting disagrees |

**Table B — non-institutional actors (d6), used for order records and organism records.**
| d6 | actor |
| --- | --- |
| 1 | a keeper who no longer keeps |
| 2 | a copyist who copied ahead of the original |
| 3 | a mourner who sat facing the stair |
| 4 | a boatman with borrowed oars |
| 5 | a colony that reads pressure (growth, never a person) |
| 6 | the building itself, correcting toward a drawing |

## 4. Event tables (one roll per stratum per run)

**Stratum 0 — institutional transit.**
- (d6) Door 44's history: 1 installed, never ordered; 2 ordered twice, installed once; 3 installed backwards and never noticed; 4 listed as window in one schedule; 5 removed on paper, present in the wall; 6 the schedule is the door.
- (d6) Who moved desk 3 to face the stairs: Table A roll. The memo blames the other department.

**Stratum 1 — limestone ossuary.**
- (d6) Who sealed alcove 44: 1 the Keepers, to stop the reading aloud; 2 Works & Descent, "structural"; 3 the occupant, from the inside; 4 nobody — the mortar grew over the name on its own; 5 Records Amended, to correct the shelf-mark; 6 it was never sealed; the seal is the shelf.
- (d6) What the seal keeps in or out: roll once, contradict it in the second record.

**Stratum 2 — bronze scriptorium.**
- (d6) Who re-numbered Room 6: 1 the Margins (twice); 2 a copyist copying ahead; 3 Works & Descent, for wayfinding; 4 the room itself, between visits; 5 the numbering never changed — the visitors did; 6 unknown; the ledger is overdue.
- (d6) The precedent that binds this run: 1 the handle keeps them; 2 the error is part of the correction; 3 do not read aloud after the third hour; 4 both readings are precedents; 5 the margin is full; 6 case adjourned, awaiting assessment.

**Stratum 3 — flooded cistern.**
- (d6) Which department flooded the cistern: 1 Works & Descent (pressure, an accident); 2 Descent Works, Predecessor (deliberate, "read too slowly"); 3 nobody — the water was always there, the rooms were lowered into it; 4 the Margins, by overstriking a drainage plan; 5 the Photographic Section, developing; 6 the records conflict; the water does not take sides.
- (d6) What the water covered: 1 the reading floor; 2 the old stair sockets; 3 the door schedule for the lower works; 4 a finished intake form; 5 nothing — the level line is the record; 6 the second plate (the one of thanks).

**Stratum 4 — root cathedral.**
- (d6) What the growth is currently reading: 1 the level line; 2 the chair's creaks; 3 the groove plates; 4 the grate punctuation; 5 the descent's own stairs; 6 the player's route through the upper floors (observable as cable following the path you took).
- (d6) How the growth answers: 1 by opening a gap in advance; 2 by closing one behind; 3 by pressing the plates in your rhythm; 4 by growing toward your last save of armour; 5 by stopping at the line like a paragraph; 6 not at all — it is still deciding what counts as a reply.

## 5. The three recorders

Every generated fact is written three times, once per recorder. Each recorder has a voice template; the generator fills in the seed's actors and events.

**Institutional record (NRRO)** — dry, redacted, blames a department, ends "AWAITING ASSESSMENT".
> Template: `MEMO — {dept}. Re: {event}. Cause: {cause}. Personnel are reminded that {denial}. File under {dept}. AWAITING ASSESSMENT.`

**Order record (Keeper or Margin)** — ceremonial or legal, attributes intent, never doubts itself.
> Template: `And so {actor} {event}, which is our word for {meaning}. Do not {prohibition}. The {object} will be kept {condition} for as long as {oath}.`

**Organism record (growth/pattern)** — no subjects, no blame; pressure, water, grooves, creaks; never a mind with a name.
> Template: `{material} records: {pattern}. {material} waits. {material} repeats. The {threshold} is not yet {state}.`

Contradiction rule: roll (d3) which two recorders disagree and about what — the who, the why, or whether the event happened at all. The third recorder's version is the one the level geometry most supports (see binding rule).

## 6. Binding rule (make the history touch the run)

Each stratum's event must bind to one real game element so the seed's story is visible without a single word being read:

- Transit: door 44's state (locked/unlocked/open one way) follows the schedule roll.
- Ossuary: the seal of alcove 44 shows the sealing actor's tool marks (mortar, crowbar, fingerprints, or growth).
- Scriptorium: Room 6's door plate carries the re-numbering roll (two plates, one worn).
- Cistern: the dedication plate above/below the water follows the flood roll; the gauge paint follows the actor.
- Cathedral: the gap/closing/plates/line from the growth roll is actually placed on the player's route.

Documents: the 40 files in `DOCUMENTS/` are pre-tagged by stratum and room type; a run scatters 2 per stratum (one institutional, one found-text) chosen by seed, and the generator may *not* rewrite them — it can only choose which survive.

## 7. Worked example — seed 20261101

Rolls: Table A=6 (Descent Works, Predecessor). Stratum 3 flood: roll 2 (deliberate, "read too slowly"). Water covered: roll 4 (a finished intake form). Contradiction d3=1: the institutional record and the order record disagree about *whether it was deliberate*.

- **Institutional record:** `MEMO — WORKS & DESCENT. Re: the cistern level. Cause: an accident of pressure; the claim of intent is a forgery by a wet hand. Personnel are reminded that gauges are read, not believed. File under Works. AWAITING ASSESSMENT.` (Placed in the pump room.)
- **Order record:** `And so Descent Works watered the reading floor, which is our word for being read too slowly. Do not read the water aloud. The plate of thanks will be kept above the line for as long as the names stay dry.` (Placed on the causeway, bronze.)
- **Organism record:** `Water records: a form, finished, face down, still legible. Water waits. Water repeats the signature once, softer. The line is not yet a paragraph.` (Scratched near the level line.)

Binding: the gauge in the cistern is painted at the highest mark, and the growth's three crossed-out marks sit below it — visible before any text is read.

## 8. Implementation notes

- One module (`history.py`) with the tables as data; no prose is generated at runtime beyond template fills, so every sentence is reviewable.
- Output: `history.json` per run (seed, rolls, three records per stratum, bindings) plus the chosen `DOCUMENTS/` ids.
- The generator is lore-only in the first version: it must not change collision, spawns or balance. Bindings are authored props chosen from the existing asset packs, not new geometry.
- Keep a fixed algorithm version string; histories are not expected to be stable across versions (a retry of the same seed should reproduce the same history, and a change of version should say so in the run manifest).
