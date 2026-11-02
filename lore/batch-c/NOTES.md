# NOTES — problems, costs and decisions

**Status: notes only.** Nothing here is settled. The four items the brief asked me to flag come first;
the rest are collisions and costs I found while writing. Each item says what would need to change if
Josiah picks a side.

## 1. The Visitor and the Reunion: dignity is a design constraint (brief item)

### 1.1 The Visitor

The risk is not that he is too frightening; it is that he becomes **funny or pitiable**, which would lose the unsettling part as well. A man on all fours in
a good jacket is one bad camera angle away from a dog joke, and one bad document away from a joke about
disability. Rules I used, and would make binding:

- **Camera at his eye level.** Never look down on him except when the player is standing, and then let the
  player feel the height. The −45° band exists for the reach, not for condescension.
- **No animal prompts.** No "pet", "feed", "fetch", "heel", no barking, no growl, no tail. The sound set is
  shoes, tweed, a cough and a palm on concrete.
- **He is dressed for an appointment.** The jacket and shoes are maintained. The repairs are careful. He is
  not ragged, not feral, not dirty.
- **His politeness is real, not a lure.** The OFFER state is not a trap. If the player takes the hand, he
  is gentle. The only grab is the 1 s hold when the player pulls away, and it reads as loneliness, not
  predation.
- **The documents are dry, not cruel.** The intake record says "do not offer a chair; he will try to use it
  and be embarrassed". That is the tone limit: bureaucratic, not mocking.
- **No "cure".** The player cannot make him stand. The good ending is that he is seen, not fixed.

**Open (Josiah):** should he be killable? My recommendation is yes mechanically, but with no score, no
drop and no achievement, and with the non-lethal route flagged in the room. The alternative — he retreats
at low HP and cannot be killed — is cleaner ethically and cheaper to defend. This is a decision, not an
art note.

### 1.2 The Reunion

The risk is larger because the image is two people joined at the hip, and the internet has a hundred ways
to make that a joke. Rules I used, and would make binding:

- **Two people, not one creature.** The record names both; the death state names both; the corpse is two
  people. The camera does not frame the join as a spectacle.
- **The relationship is redacted.** Not coyness: the moment the game says "husband and wife" or "brother
  and sister", it invites a joke about marriage or incest. Keep the application's relationship field
  `██`. They are two adults who are fond of each other and cannot agree.
- **The harness is institutional equipment.** Leather, trouser fabric, stitching, a case tag. Not bondage
  gear, not medical horror, not a circus costume. It should look issued by a depot.
- **No comedy of disagreement.** They are not a sitcom couple. The argument is quiet, repetitive and worn
  smooth. The player should feel they are intruding.
- **No cure, no separation.** The player cannot cut them apart. The good ending is that they walk away
  together, still disagreeing, which is what they asked for.
- **The "lie to one" option is allowed and is worse.** It is not punished mechanically; one of them is
  silent afterwards. Do not turn it into a joke either.

**Open (Josiah):** the two-actor rig. Option A (two actors, one hip constraint) solves the opposite-facing
problem and costs a shared state machine; Option B (one billboard, front/back split) is cheaper and reads
wrong at every yaw but 0. I recommend A. If A is not possible in the current actor system, the creature
should wait rather than ship as a billboard that turns one person into a back.

## 2. The Span: carrying the player needs special engine handling (brief item)

This is the largest integration cost in the batch, and the sheet cannot be approved as a normal actor.
The full contract is in `SPAN.md` §4.5; the short version:

1. **A billboard cannot be walked on.** The deck must be a level mesh (a 7.5 m × 1.2 m brush or moving
   sector), authored before the Span spawns; the actor is drawn over it. The actor's SPAN state enables
   the deck; RE-ARCH disables it.
2. **The path is authored, not simulated.** Fixed walk to the gap, fixed deck line. The sprite's slab line
   and the deck brush must share numbers; a 0.1 m mismatch reads as a floating animal.
3. **The shudder is a scripted drop, not physics.** 0.5 m over 20 ticks; the player rides the sector; no
   ragdoll, no random fall.
4. **A catch ledge at −2.5 m.** Falling off costs 20–40 and lands on a lower ledge; the void below that is
   the death pit. Without the catch ledge the encounter is unfair.
5. **The cut cable is a persistent level state.** A cut drops a slab, the Span refuses to extend for 60 s,
   and the hole is visible. The backup route must exist **before** the bridge (softlock rule).
6. **The worker is a fixed spline, not an AI.** The worker crosses, pauses, pats the head, writes on the
   card. That path is the tutorial for the crossing.
7. **Render as three parts.** A low-poly deck mesh (1,200–1,800 tris) plus the head/forelegs as a
   billboard at the near ledge and the hind legs as a second billboard at the far ledge. A 7.5 m billboard
   at 768 px is either tiny or a very long canvas; the hybrid is cheaper and readable.
8. **Load rating vs inventory.** "Two persons or one cart" is a lore rule; if it becomes a mechanic, it
   needs a carry-weight check. The Reunion is two persons in one body — does it count as two? (A nice
   authored joke, but do not settle it in code until the Reunion exists.)

**Hard requirement:** the Span must never be the only way back. Every gap it spans needs a return route
that does not depend on it being alive, willing or unprovoked.

## 3. The Ravel: projectile spray (brief item)

The burst is a fixed 8-shard ring with 4 cardinal gaps, 7 m range, 1.5 s telegraph, 1.5 m minimum range,
no homing, no fire through walls, one burst per 3.5 s. Full rules in `RAVEL.md` §4.3. The risks:

- **Flash.** The amber flash is brief and bright. Cap it under 0.2 s and <3 Hz, and offer a reduced-flash
  option. The ring, not the flash, carries the information.
- **Cover.** The shards must stop at geometry and leave a decal. If they pass through railings or grates,
  the room's cover is a lie.
- **Performance.** 8 shards × up to 6 bursts = 48 projectiles per fight; fine for the engine, but the
  impact decals and lights need a budget.
- **The barrier puzzle.** If the "provoke it at a barrier" route uses a barrier the player can also shoot
  open, the puzzle is trivial. Make the barrier a material only the shards break (a resin seal, a salt
  crust, a glass partition), or gate the player's weapons in that room. Do not rely on the player not
  trying.
- **Loot.** The cooled shards are a resource only if the item system exists. Do not build the Ravel around
  a resource that does not exist; the disable-the-crest route works without loot.

## 4. The Pleat: the fan geometry and the block

- **The fan read.** The slam hits everything within 2.2 m of the open 4.4 m fan; beyond that is safe. The
  counter-intuitive part is the fold: the open fan is the damage window, the closed plates are nearly
  immune. Teach it with the first slam in a room with no other threat. If the read fails, the fight is a
  coin flip.
- **The plates at 0.4×.** Closed plates are nearly immune; the fight is a waiting game for the fold. That
  is intentional (the creature is a gasket, not a duelist), but it can become a slog. If playtests hate it,
  raise the plate multiplier to 0.6× and shorten the fold to 24 ticks.
- **The block swap needs a weight system or a scripted "heavy item" check.** If neither exists, the puzzle
  becomes a single scripted interaction at the fitting; still works, less interesting.
- **The fibre puff is an accuracy penalty.** If accuracy penalties are not native, make it a 25-tick
  screen haze or drop it. Do not make it damage; the Pleat already has a slam.
- **Asbestos-adjacent.** The yellow fibre is lagging. Do not make a joke about breathing it. The horror is
  bureaucratic ("serviceable"), not medical.

## 5. The White Bloom: floor spikes are level geometry

- **Spikes are not sprites.** They need per-spike spawn markers, a collision volume, a 4 s lifetime, a
  crumble animation and a grit decal. The body sprite only plays the DRAW/BLOOM/SETTLE poses.
- **The wet/dry read must be explicit.** A wet sheen, a waterline, a dry dust edge. Do not rely on a subtle
  material change; the whole fight depends on the player seeing where the floor is wet.
- **The impale is a 2 s movement lock, not damage-over-time.** If movement locks are not native, use a 2 s
  slow and 12 damage.
- **The dry safe zone must exist in every room.** If a Bloom is placed in a room with no dry ledge, no
  drain and no decoy, it is an unfair tax. The default room has a dry path around the wet ring.
- **The bloom is indifferent, not evil.** Do not give it a roar, a chase or a grudge. The horror is that it
  is doing its job.

## 6. Cross-creature collisions (keep these apart)

| Pair | Risk | Ruling |
| --- | --- | --- |
| Visitor / Hem | Both formerly human, polite, non-hostile, seated-adjacent. | Hem waits for a child and blocks a stair; the Visitor waits to be seen and offers a hand. Different need, different posture, different failure. Do not give the Visitor a bench loop that reads as her. |
| Visitor / Applicant | Both in the waiting room; both about being seen. | The Applicant records a position; the Visitor offers a hand. The Applicant's shutter is not the Visitor's cough. Keep the Visitor out of the Applicant's encounter room. |
| Reunion / Calmor | Both restraint and alteration. | Calmor restrains others as a duty; the Reunion is restrained together by the office, and does not want adjusting. Calmor must not be allowed to "fix" the harness. |
| Span / Erratum | Both structural. | The Erratum rams a removed route; the Span is a route. Never give the Span a ram. |
| Pleat / Underprint | Both layered plates. | Plaster that leans vs lagging that braces. Different material, different want, different silhouette (biped vs crab/fan). |
| Ravel / Unaddressed | Both amber and glass. | The Unaddressed's amber is sensory; the Ravel's is ordnance. Basin vs cathedral. Keep them apart. |
| White Bloom / Unaddressed | Both pale, porous, growth-like. | The Bloom is a filter; the Unaddressed's baffles are ears. Do not put a large Bloom in the Unaddressed's chamber. |
| White Bloom / Vore Spindle | Both basin organisms. | Spindle = one homing projectile; Bloom = floor denial. Different reads at a glance. |
| Ravel / Vore Spindle | Both basin projectiles. | Ring vs homing. Never give the Ravel homing. |

## 7. Naming and data collisions

- **Actor letters** proposed: `V` Visitor, `L` Pleat, `S` Span, `J` Reunion, `A` Ravel, `B` White Bloom.
  Existing actors: `N` Applicant, `C` Circuit, `P` Underprint, `M` Hem. Every name must be checked
  against `package_grid.py`'s 4-character namespace before baking; a collision produces an invisible or
  wrong-band sprite.
- **"Visitor"** is a common word. `INWORLD-TEXT.md` has a line "VISITORS — none. Signatures: eleven."
  The office class VISITOR is deliberately the same word; if that is too much resonance, the class can be
  `ATTENDEE` or `CALLER` without changing the creature's name.
- **"Reunion"** is also the name of the desk (`reunification desk`). That is intentional; the room and the
  creature share the office's word. Do not rename the desk.
- **Settling basin.** The five-strata model (transit, ossuary, scriptorium, cistern, root cathedral) does
  not include the basin; earlier `nullrun-text-20261101/NOTES.md` flagged this. I placed the Ravel and the
  White Bloom under **stratum 3, cistern / settling basin** as a sub-area of the cistern, not a sixth
  stratum. If the basin is a sixth stratum below the cistern, both files' station lines need a one-word
  change and the "water is a wall to the Circuit" boundary needs a second look.

## 8. Sprite budget (this is a whole bestiary, not a batch)

From the per-creature tables:

| Creature | Samples | PNGs (40 views) |
| --- | --- | --- |
| Visitor | 40 | 1,600 |
| Pleat | 36 | 1,440 |
| Span | 48 | 1,920 |
| Reunion (two actors) | 78 | 3,120 |
| Ravel | 38 | 1,520 |
| White Bloom | 39 | 1,560 |
| **Total** | **279** | **11,160** |

At the Applicant's measured 2.25 MiB per 768² PNG resident, that is **~24.5 GiB resident** and **~578 MiB**
packed. At 512 px it is **~6.1 GiB resident**. The earlier three-creature batch was already ~10.1 GiB at
768; the two together are ~34.6 GiB. That is not a budget; it is a warning.

**Recommendation:** bake only a **first-proof gate at 512 px** — 12–14 samples for each single-actor
creature and about 22 for the Reunion pair, roughly 80 samples and 3,200 PNGs (~1.8 GiB resident) — and
choose the first proof by what it tests, not by which creature is coolest.

## 9. Recommended first proofs (and order)

1. **The Visitor** — one actor, one bank, no new engine system, and it tests the hardest thing in the
   batch: whether the OFFER pose reads as an offer at gameplay distance. If it does not, the non-lethal
   route is invisible and the creature is a generic crawler.
2. **The White Bloom** — tests the wet/dry floor read and the spike geometry. The body is slow and the
   bank is small; the level cost is the spike set, which is reusable.
3. **The Ravel** — tests the ring/gap projectile pattern and the crest-as-magazine. Reusable projectile
   code.
4. **The Pleat** — tests the fan/ring read. The body is compact; the block puzzle can be scripted.
5. **The Reunion** — only after the two-actor hip constraint exists; otherwise it ships as a billboard that
   turns one person into a back.
6. **The Span** — last, with a bespoke level, the hybrid mesh, and the catch ledge. Do not start here.

## 10. Open questions for Josiah

1. **Visitor and Reunion origins.** I propose formerly human for both, open in-game. Confirm, or make one
   or both never-human. (The Visitor as a never-human impression-organism is available and I do not
   recommend it.)
2. **Killability of the two former humans.** Recommendation: killable, no reward, non-lethal route flagged;
   or the Visitor retreats and cannot be killed. Decide before the encounter is built.
3. **The Reunion's relationship.** Keep it redacted? I recommend yes, permanently.
4. **The Reunion's rig.** Two actors + hip constraint (recommended) or one billboard (cheap, reads wrong)?
5. **The worker on the Span.** Is there a neutral human NPC class? If not, the worker is a scripted
   silhouette or a one-off; the Span loses its best image without them.
6. **The Span's load rating vs the Reunion.** Two persons or one cart — does the Reunion count as two? If
   yes, the Span will not take them, which is a good scene. If no, it is a plot hole.
7. **May water/lighting drive AI?** The White Bloom's drain and the Circuit's lamp decoy both assume level
   state can change behaviour. The earlier generator proposal kept bindings cosmetic; these are gameplay
   bindings.
8. **Is the Pleat's block an inventory item?** If yes, it is a 0.5 m cube with a carry weight; if no, the
   swap is a scripted interaction.
9. **Are the Ravel's shards a resource?** Only if the item system exists; otherwise the crest disable is
   the route.
10. **The settling basin.** Sixth stratum, or a sub-area of the cistern? My files assume the latter.
11. **Sound palette.** The cues here are words. Check the Visitor's cello note, the Reunion's two voices,
    the Span's post-lock silence and the Bloom's kettle hiss against the existing cues (Applicant shutter,
    Circuit spark, Hem sewing) before recording.
12. **Documents.** Each file has one found text and one record entry. A full document set (three per
    creature, as in the earlier batch) is a follow-up, not part of this job.
13. **Names.** The Visitor's name and the Reunion's two names are deliberately not given. If the
    "tell him his name" or the case-tag resolution is built, choose ordinary names and keep them on the
    tags and the corpse. Do not make the names a puzzle.
14. **Ticket 44.** The Visitor's queue ticket is 44, echoing door 44, alcove 44 and Case 44. If 44 is not
    a deliberate recurrence, change the ticket number before it becomes a theory.

## 11. What this package does not do

No images were opened (I cannot see them), no model, rig, sprite, bake, map, engine, AI, collision, audio
or balance work. No file outside `shared/deepseek/nullrun-lore-batch-c-20261101/` was written. Nothing was
pushed, posted or committed (the shared folder is not a git repository). The claim line is in `README.md`
because the job restricts writes to this folder.
