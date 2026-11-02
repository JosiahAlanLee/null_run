# NOTES — collisions, costs and decisions

**Status: notes only.** Nothing here is settled. Items are ordered by how much they affect the proposal.

## 1. The name "Armature"

The Underprint's internal twine frame is called an "armature" in
`nullrun-newsheets-lore-20261101/UNDERPRINT.md` (line 20) and in the sound cue
`cr/paperedroom/armature` (`nullrun-sound-bible-20261101/SFX-LIST.md`, line 518). This creature is THE
ARMATURE. The resonance is not fatal — the Underprint's frame is a body's frame, this is a reinforcement
cage — but it will confuse the docs and the asset namespace.

**Resolution (follow-up, 2026-11-02): keep THE ARMATURE and rename the Underprint's term.** The creature
name is the stronger of the two, "armature" is the correct trade word for a rebar cage, and the rename is
cheap. Alternatives for the Underprint's term, in order: **twine frame** (recommended; cue
`cr/paperedroom/frame`), **scrim frame** (cue `cr/paperedroom/scrim`), **the frame** (simplest). If Josiah
prefers to keep "armature" for the Underprint, the creature alternatives are **THE STANDER** (recommended;
already the trade word; actor letter `T`), **THE CAGE**, and **THE BUNDLE**. Keep **standing reinforcement**
as the office's species name either way. The full argument is in `ECOLOGY.md` §10.

## 2. Rebar overlaps (non-duplication)

The setting already has four steel-and-wire creatures. The distinctions in `ARMATURE.md` §3.4 are
structural, not cosmetic. One line each:

| Creature | It is… | Never let it… |
| --- | --- | --- |
| Span | a bridge that holds a gap | stand up as a person, or test a load with an arm |
| Erratum | a route that rams an infill | become upright or human-shaped |
| Ballast Husk | a powered machine with a maw | creak patiently, or stand in a pack |
| Circuit | a signal network of three bodies | become one body, or speak in creaks |
| **Armature** | **a fence that stands up** | span, ram, hum or arc |

The Stone ReDead is the other humanoid common mob. Keep the Armature out of the shelf galleries; it belongs
to the repair scaffolding and the closed galleries. The ReDead has a face, a name and a grip; the Armature
has none of the three. Do not put them in the same room.

The **Vore Spindle** is the fifth material in this family: chitin, bone and rebar, a colony-bearer. The
controlled Armature is still an Armature, not a Spindle with a body; the Spindle is the will, the Armature
is the hand. Do not let the Spindle grow an Armature-shaped shell, and do not let the Armature grow a
Spindle's sac or lens. The link is the core and the tendon, nothing else.

## 3. Strata numbering

`STRATA.md` and the batch-C folder use strata **0–4** (transit, ossuary, scriptorium, cistern, root
cathedral). `nullrun-depths-layout-20261101/DESIGN.md` numbers the same five **1–5**. This file uses 0–4
for consistency with the lore packs. If the engine and docs settle on 1–5, every station line needs a
one-number shift. The settling basin is treated as a sub-area of stratum 3 (cistern), as in batch C; it is
not a sixth stratum. The text pack (`nullrun-text-20261101/NOTES.md`) notes that no creature is assigned
to the basin. This proposal puts one wet, rust-swollen Armature there; if the basin is meant to be empty,
remove that line.

## 4. The heap is a static prop, not a corpse actor

"The heap stays" is cheap only if it is not an actor. Recommendation: on death, remove the actor and spawn
a **heap prop** at the death point — four variants (fresh, settled, old, collapsed), no AI, no collision
beyond a low step, a footstep sound, and a decal. Do not keep the death actor's corpse frame in the world;
the most-spawned creature will otherwise leave hundreds of actors. If the engine cannot spawn props at
runtime, place fixed heap markers in rooms where a pack is expected and enable one on death. This is the
single largest integration cost in the proposal.

**Follow-up cost (Spindle ecology):** the heap is now also the Spindle's host. A static decal heap cannot
stand up. Two options: (a) the heap prop gets an "infectable" flag, a rise animation and a host state — the
emergent version, and the expensive one; (b) the infection is authored at fixed **heap markers** (specific
props placed by the level designer) and the prop is swapped for an actor during RISE — cheaper and easier
to keep fair. Recommend (b) for the first build; it also lets the designer choose which heaps can stand up,
so the player is never ambushed by a heap that looked like scenery. The free corpse heap stays a static
prop; only the authored markers are infectable.

## 5. The rebar prop set

The disguise fails if the level's rebar props do not match the creature. The Armature needs a **standing
prop family** built from the same kit: starter cage, column cage, scaffold bundle, bent bar bundle, and a
tied bundle leaning on a wall. Four to six props, 1.8–2.0 m tall, same bar gauge, same tie-wire spacing,
same rust palette. Without them, the player learns the silhouette in the first room and the creature is
never invisible again. This is a level and art cost, not a creature cost, and it is the one that makes the
encounter work.

## 6. The loper is a state, not an actor

One bank, one actor; the loper is a speed and HP variant with a state in the same bank (L). If the
loose-bundle texture variant does not survive at 512 px, drop the texture and keep the state. Do not build a
second bank for one variant.

## 7. Light: notice, not attraction

The brief says the pack moves when the player's light or footsteps are near. I have read that as **notice**,
not attraction: light is a load change the Armature turns toward, not a lure it is drawn to. It avoids lit
pools but will cross them if cornered. If Josiah wants light to be a hard lure (moth behaviour), the AI and
the lighting staging change: the pack would leave the dark to follow a beam, and the "safe dark route"
counterplay disappears. My recommendation is notice, not attraction, because it keeps the player's choice
meaningful.

## 8. Sound collisions

The Span already owns "rebar creak" (`cr/span/tell`; `cr/span/lash` is its rebar whistle), and the Pleat
owns metal ticks. The Armature's creak must be **higher, drier and more regular** than the Span's: the Span
is a big structure settling; the Armature is a small bundle tightening. Give the Armature a distinct pitch
band and a tighter rhythm. The sound bible's priority ladder puts tells at P6 with a two-concurrent limit;
the pack's idle creaks should be P4 or lower, or a stand of six will eat the tell budget. The death is a P5
event, not P8 (P8 is the player's death).

## 9. Does it drop anything?

Proposal: no. The heap is information, not loot. If the item system wants tie wire as a resource, the heap
becomes a harvest node, which turns the warning into a vending machine. If it must drop, make it a single
straightened bar with no use, or a wire coil that is only good for one scripted repair; do not make the
common mob a farm.

## 10. The false heap (optional, not core)

A rare idle variant: an Armature folded down into a heap shape, unfolding when the player steps over it. It
is a strong scare and it fits "indistinguishable until it moves", but it makes every heap suspect and can
feel unfair. If used: once per stratum, with a clear tell (a taut tie wire, no rust at the breaks, a slow
creak, the bars too organised), and never in a room where the player has already been taught that heaps are
safe. My recommendation is to leave it out of the first build; add it after the player has learned the heap
language.

## 11. Never human — the line to hold

The risk is that players read the Armature as a worker who died in the concrete: a skull in the cage, a
boot, a name tag. That would make it a ghost story and break premise 2. The record describes a bundle-built
body with no face; the death shows no remains; the heap contains only bars and wire. If a document needs a
human trace, put it *near* the cage (a site instruction, a boot print in the dust) and never *in* it.

## 12. Open questions for Josiah

1. **Name.** Keep THE ARMATURE and rename the Underprint's twine frame, or keep "armature" for the
   Underprint and rename this creature? (Recommend the former.)
2. **Fodder tier.** Is 40 HP with 9–12 damage right, or should it be softer (30 HP) because it arrives in
   threes?
3. **Pack cap.** Is six the right maximum, or does the engine or renderer prefer four?
4. **Heap persistence.** Static prop spawn (recommended), fixed markers, or no heap after a level reset?
   This is an engine decision.
5. **Light.** Notice (recommended) or hard attraction?
6. **Loper.** One in four, or one in six? Does the loose-bundle texture variant exist, or is it state only?
7. **Drops.** None (recommended), or a tie-wire resource?
8. **False heap.** Leave it out of the first build (recommended), or include once per stratum?
9. **The rebar prop family.** Who builds it, and does it ship with the creature or with the environment
   kit? The disguise depends on it.
10. **Sound.** Confirm the pitch band against the Span and the Pleat before recording; the Armature's creak
    must not read as a smaller Span.

## 13. The Spindle ecology — costs and collisions

1. **The controlled Armature is a variant, not a new actor.** One skin (reddish glossy tendons, green core at
   the chest) plus a compact bank: dormant, walk, two-arm windup, two-arm slam, hit, collapse/revert. About
   17 samples, 680 PNGs at 40 views; roughly 0.7 GiB at 512 px, 1.5 GiB at 768. The free bank cannot cover
   the two-arm slam; that is the one new strike role. The core is a prop with a hitbox and an emissive
   material, not a sprite.
2. **The tendon is engine geometry, not a bake.** It is a segment chain or tube from the Spindle to the
   core, like the Circuit's tether in `SPRITE-ROLES.md`. It needs a thin hitbox, a taut/slack state and a
   cut transition. A 12 m billboard is not an option.
3. **The core in flight is a projectile with a non-damage hit result.** It must be able to miss, land, lie
   on the floor, be shot, and lodge in a tagged host. That is a new projectile outcome (attach), not a
   damage type. The Spindle's existing homing spore is the wrong model: the colony core is a slow, aimed
   arc, not a homing shot. Keep the two projectiles distinct.
4. **The heap infection needs a host rule.** Authored heap markers (recommended) or an infectable heap prop;
   see §4. Do not make every corpse heap infectable in the first build. The player must be able to learn
   which heaps are dangerous; a random heap that stands up is a trap, not a lesson.
5. **The bone variant is a skin plus attachments.** Reuse the free bank; add bone props and a pale atlas;
   the bone heap is a prop variant. No new actor. The bone variant must be full HP; if it is a damage state,
   the player's read ("wounded") is correct and the ossuary loses its quiet misread.
6. **The rebar/bone Spindle is a skin plus the brace and LAUNCH poses.** Reuse the classic Spindle bank
   where the poses match; the new sheet's walk, brace and LAUNCH are the additions. About 12 samples, 480
   PNGs; roughly 0.5 GiB at 512 px.
7. **The green light is a budget.** One small dynamic light (or emissive plus a short-falloff point light)
   per controlled Armature; cap two per room. The core is a point, not a room wash; if the light bleeds, the
   dark-room staging dies. The control core's light should not be brighter than the player's flashlight.
8. **The ecology's AI is a sensor and a hand.** The Spindle is the sensor (notice, launch, pulse); the
   controlled Armature is the hand (guard, cordon, slam). That is cheaper than two independent hunters: one
   detection check, one distance constraint, one attack state. Do not give the controlled Armature the free
   pack's relay; it has a different controller, and that controller runs the patterns in `ECOLOGY.md` §8.3.
9. **Collisions with the other basin creatures.** The Ravel is a fixed ring of amber shards; the White Bloom
   is floor denial; the Spindle is one green core, a tendon and a host. Three different reads. Never give
   the Spindle a ring, the Ravel a host, or the Bloom a core. The Spindle's green is the only green in the
   basin; the Ravel's amber and the Bloom's pale stay theirs.
10. **Collisions with the Circuit and the Span.** The Circuit's tether is signal (three bodies); the
    Spindle's tendon is control (two). Do not route a Circuit along a live tendon, and do not let a cut
    tendon read as a Circuit mark. The Span is a rebar cage and a tempting host; keep it out of the first
    build (see §14).
11. **The first infection is a scripted set-piece.** One per run, shown at a distance, no other enemies. It
    is the tutorial for the green core. After that, the loop can happen off-screen; the player finds the
    controlled Armature and follows the tendon. Do not spend the rise animation on random spawns.
12. **The bone variant vs the Stone ReDead.** Both are bone in the ossuary; the ReDead is a resident with a
    mask and a name, the bone Armature is material with neither. Keep the bone Armature out of the shelf
    galleries. No skulls in the Armature's cage, ever; a skull would read as the ReDead's kin and break
    premise 2.
13. **The tick is surface-dependent.** It needs four short variants (tile, limestone, water, concrete/rebar)
    and a floor-material or room tag to choose one. If the engine has no surface tags, use one tick with an
    occlusion or lowpass filter per zone: the rhythm survives, the placeability does not. The tick is a new
    cue family, not a variant of the Spindle's chitin clicks; keep it distinct.

## 14. Open questions (ecology)

1. **Host rule.** Only dormant Armatures and heaps (recommended), or any Armature whose chest the core
   reaches? The former is fair and readable; the latter makes the core a combat disable.
2. **Reversion.** When a dormant host is freed, does it turn on the Spindle? Recommendation: it tests the
   nearest load, which may be the Spindle, but it is not guaranteed and the game does not promise it.
3. **Heap infection.** Authored markers (recommended) or emergent infectable heaps? The second is the
   better toy and the bigger cost.
4. **Spindle cores.** One large colony core (recommended) or several? If the core misses, can the Spindle
   reel it back and re-launch, or is it spent?
5. **Tendon.** Cuttable (recommended) or invulnerable? If cuttable, does the Spindle re-arm or retreat?
6. **Controlled cap.** Two per Spindle (recommended) or three? Three is a cordon; four is a crowd.
7. **Bone variant.** Skin (recommended) or separate actor? Full HP (recommended) or a genuine damage state?
8. **Spindle variant.** Skin plus brace/LAUNCH poses (recommended) or a new bank? The existing Spindle bank
   may not cover the rebar/bone silhouette.
9. **Green light.** Dynamic light or emissive-only? Budget one per controlled Armature; two per room.
10. **The Span as a host.** A later set-piece (recommended: no in the first build). A colony-controlled
    Span would be a boss, not a common encounter; it needs its own rules.
11. **Denying heaps.** Can the player destroy a heap (melee or shots)? If not, the "deny it heaps"
    counterplay is unavailable and the ecology is only "kill the Spindle or shoot the core".
12. **First infection.** Once per run (recommended) or once per stratum? The latter teaches the loop in each
    stratum and costs three set-pieces.
13. **Classic Spindle vs colony Spindle.** Does the pale cistern Spindle also launch colony cores, or is the
    infection ability only on the rebar/bone variant? This proposal gives the cistern the ecology. If the
    classic Spindle stays a pure homing-spore vermin, the primary stratum moves to the cathedral and
    ossuary, and the cistern gets the free Armature only. This is the one assumption that changes the
    ecology's home.
14. **Damage tier.** `PILLARS.md` §3 says a rebar strike is nearly a one-shot for a normal human; the
    current 9/12 is the earlier moderate tier. Recommendation: raise the free sweep/jab to 15/18 and the
    controlled slam to 20–24, then re-check the pack. If the numbers stay, the coordination must carry the
    panic alone. Decide before the damage pass.
15. **The tick's first appearance.** How early? Recommendation: after the player has killed at least two
    free packs in the stratum, so the contrast lands. The first tick is scripted, not random; it arrives
    before the Spindle is visible.
16. **Hollow / ReDead pairing.** The pairing is binding, but the Hollow's sheet is not on the PC. The sketch
    in `ECOLOGY.md` §9 is provisional. Does the Hollow need a "still until it moves" state that shooting can
    interrupt, or is the ReDead's pin the only thing that makes it move? Recommendation: the Hollow is still
    until the player is engaged or held; shooting the "tree" before it moves should work, which is why the
    ReDead must keep the player busy. Do not make the Hollow invulnerable while still.
17. **Tick vs the Spindle's existing cues.** The sound bible's Spindle cues are chitin clicks and water
    drips; the tick is a new ceramic-on-surface family. Confirm it does not read as the Armature's wire tick
    or the ReDead's sinew creak. On water, the tick may be masked by the cistern's drips; the launch thump
    is still the fallback.

## 15. What this package does not do

No image was opened (I cannot see it, or the three follow-up sheets), and no model, rig, sprite, bake, map,
engine, AI, collision, audio or balance work was done. No file outside
`shared/deepseek/nullrun-lore-armature-20261101/` was written. Nothing was pushed or posted. The claim line
is in `README.md` because the job restricts writes to this folder.
