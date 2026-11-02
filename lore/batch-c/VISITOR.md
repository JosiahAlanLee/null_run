# THE VISITOR — the man who is still waiting

**Status: PROPOSAL throughout.** Sheet 9. I have not seen the image; §1 is Claude's description, quoted.
The origin is proposed **formerly human** and should stay open in the game (see `NOTES.md`, item 1).

## 1. What the description establishes

| Description detail | What it is |
| --- | --- |
| A gaunt middle-aged man | Not a creature wearing a man; a man, in a body that has changed. Age is visible and specific. |
| Patched, stitched blue-grey tweed jacket; brown trousers; polished shoes | He is dressed for an appointment. The repairs are careful, not comic. The shoes are the one thing kept clean. |
| Moves on all fours, long arms, oversized knuckle-walking hands | The waiting-room floor has become his posture. The hands are too large because they are what he stands on now. |
| READY: crouched, staring with mild, sad politeness | The default is attention, not menace. He is waiting to be addressed. |
| ACTION: a low lunge, one long hand reaching across the floor | The threat is a **reach**, not a bite: an offer of help that cannot stop itself. |

The description gives three facts that drive everything: **he is still dressed for an appointment**, **he
stands on his hands**, and **his first move is to reach toward you, not at you**.

## 2. Institutional record

**NRRO INTAKE NR-183-V — VISITOR (UNSCHEDULED)**
- Subject no.: NR-183-V. Received ██.██.19██. Class: VISITOR. Station: stratum 0, institutional transit,
  waiting room 3 and the lost-property bench; also stratum 1, ossuary landing, the bench that faces the stair.
- Description: one adult male, middle-aged, gaunt; patched blue-grey tweed jacket, brown trousers, polished
  shoes; ambulates on four limbs with long arms and oversized knuckle-walking hands; carries the torso low
  but upright enough to face a seated person. Garment maintained; shoes maintained; hands clean.
- Behaviour: waits. Approaches on all fours, rises as far as the body allows, and offers one hand palm up.
  The offer is repeated at intervals. If not taken, subject withdraws the hand and apologises. Subject
  follows at a walk if a visitor moves toward the stair, and reaches when the visitor does not stop.
  Subject has never been observed to leave a waiting area voluntarily.
- Origin: subject states he is waiting to be seen. The appointment book for waiting room 3 has no entry
  under his description. UNRESOLVED. Do not resolve on site.
- Notes: do not step on the hand. Do not offer a chair; he will try to use it and be embarrassed. The
  subject's queue ticket is in his jacket pocket and is older than the room.
- Disposition: AWAITING ASSESSMENT. Do not call his number.

## 3. Lore proposals

### 3.1 Origin (formerly human — proposal, open)

He came to be assessed. He was given a ticket and asked to wait. The building's waiting is not a metaphor:
the room kept him, and the room's furniture slowly stopped being the right shape for him. He adapted, as
people do, and he has not been told that adapting was the assessment. He believes he is still early.

The alternative — a never-human organism that assembled a man out of a jacket and a pair of shoes — is
available and I do not recommend it. It would make him the fourth impression-organism in the bestiary, and
it would lose the only thing the sheet is about: **a person who is still a person, in a body the office
would file as a chair.**

His dignity is the design constraint. He is not a dog, not a crawler, not a joke about waiting rooms. He is
a man in a good jacket who has been sitting in the same place for a very long time and has learned to get
about. The camera stays at his eye level. The documents never call him an animal. The one comic note
allowed is bureaucratic: the office has a form for him and the form is wrong.

### 3.2 What he wants (proposal)

To be seen. Not assessed — seen, which is a smaller and older request. He offers his hand because that is
what a man does when a stranger is standing and he is not. He reaches because he cannot stand up to be
introduced. He follows you toward the stair because the stair is where people are seen, and he would like
to come.

He is not hostile. He is **lonely in a way that has become a physical reach**. The fight, if there is one,
is about whether you let him take your hand and what happens when you pull away.

The office has no species word for him. The room schedule says VISITOR; the cleaning rota says "the
gentleman on the bench"; the intake form says FURNITURE, which is the only entry anyone has ever tried to
correct.

### 3.3 Strata and room tags (proposal)

**Primary: stratum 0, institutional transit.** Room tags: `waiting room`, `lost property`, `bench`,
`enquiry window`, `platform 3`, `stair landing`. He is at home in the furniture that faces a queue.

**Secondary: stratum 1, limestone ossuary.** Room tags: `chapel`, `north gallery`, `bench facing the
stair`, `alcove 44`. He waits with the shelves because the bench is there and the light is better.

**Absent from:** the cistern (he keeps his shoes polished and will not wade), the scriptorium (no waiting
room; the desks face the walls and he cannot find a seat), the root cathedral (no bench, no light, and the
stair he is watching does not go there). These absences are usable: the wet strata are where he cannot
follow, and the player can learn that from his shoes.

### 3.4 Relationships

- **Hem** — the only person who straightens his collar. She calls him "sir". He calls her "madam" and does
  not know she is the reason the bench is warm. They sit together without speaking; it is the least lonely
  room in the descent.
- **Applicant** — it photographed him once, at the portrait station, and now points at the place where he
  was sitting. He has moved. It misses. He is too polite to mention it.
- **Calmor** — tried to measure him. He stood as tall as he could, which was not tall, and was measured
  anyway. Calmor filed the measurement under "seated".
- **Stone ReDead** — he waits by alcove 44 and has never read the name aloud. He dusts it when the Keepers
  are late. He does not ask the occupant to move.
- **Reunion** — they knew each other before. He does not remember from where, and they do not remind him.

## 4. Encounter design

### 4.1 Stat block (starting values)

| | |
| --- | --- |
| HP | **110** (person-class; between zombieman 20 and demon 150). Head/torso 1.0×; jacket 0.8× (padded tweed); **hands 1.5×** (the organ); exposed wrist 1.25×. |
| Size | 1.75 m if he stood; 1.15 m at the shoulder on all fours; reach 2.4 m |
| Speed | crawl 110 u/s; follow 170; lunge hand 420 for 8 ticks (≈2.4 m); no run |
| Attacks | offered hand 0 damage, 0.6 s slow if taken and pulled; reach 8 + 0.4 m pull; defensive backhand 12 (1.4 m) only if attacked from the side |
| Fairness caps | one reach per 4 s; never from behind; never while the player is held; he coughs before every reach |

### 4.2 Behaviour

| State | Ticks | What he does | What it means |
| --- | --- | --- | --- |
| WAITING (idle loop) | 4 × 10 = 40 | Crouched on his knuckles, hands folded, shoes together; head tracks the player with mild interest. Every ~8 s he straightens his jacket with one hand and nearly loses his balance. | Not hostile. The jacket is the tell that he is a person. |
| SEATED (alternate idle) | 4 × 12 = 48 | On the bench, feet on the floor, hands on his knees, as if the body still remembered the chair. | The version of him the room was built for. Use in the first room, before he stands. |
| NOTICE | 3 × 7 = 21 | He rises to a crouch, wipes one palm on his trousers, and looks up. | The only warning. He is about to be polite. |
| OFFER | 4 × 10 = 40 | One hand comes out, palm up, at floor level; the fingers spread; the jacket sleeve falls back. He waits. | **The telegraph.** The hand arrives before the body. |
| REACH | 4 × 6 = 24 | The hand shoots across the floor; the body follows slowly, dragging the jacket. | The low lunge. It is a reach, not a strike. |
| WITHDRAW | 3 × 7 = 21 | He pulls the hand back, apologises, resets the cuff, and tries again after a pause. | The recovery window. He is not guarding. |
| FOLLOW | 4 × 7 = 28 | A four-limbed walk, jacket dragging, shoes scuffing; he keeps 1.5 m and does not close. | He follows you to the stair. He is not chasing. |
| BLOCK | 3 × 8 = 24 | He stands in the doorway on three limbs and holds the frame with the fourth. | Non-hostile obstacle. He will not move until addressed. |
| HURT | 2 × 5 = 10 | A whole-body flinch; he covers his head with both hands and then remembers his shoes. | Pain reads as embarrassment. |
| DEATH | 5 × 7 = 35 | He folds down, straightens his jacket once with the last movement, and is still. | No scream. The room gets quieter. |
| CORPSE | 1 | A patched jacket over a folded shape; the shoes are still polished and still together. | The office will file him as furniture. |

The sheet's named poses map as: `ready` = WAITING, `action` = REACH. OFFER is the state between them and
the one the encounter is built on.

### 4.3 The telegraph

**The palm turns up.** Before any reach: the hand comes out palm up, the fingers spread, the sleeve falls
back from the wrist, and he gives a small dry cough. The cough is the audio cue; the palm is the visual.
There is a 1.1 s hold in OFFER before REACH. A player who steps back in that hold is safe, and he
withdraws without resentment.

### 4.4 Counterplay

- **Step over the arm.** The reach is low and flat. A normal jump or a step onto a 0.4 m ledge clears it.
- **Do not stand on the hand.** If you do, he flinches (HURT) and then stops being polite: the next reach
  is a backhand.
- **Stairs.** He cannot climb quickly on three limbs. He will follow to the bottom and wait. Do not make
  this a joke; make it the sad limit of the body the room gave him.
- **Doorways.** He blocks, but he does not grab. Walk around him or address him. Shooting him is a choice,
  not a solution.
- **Distance.** At 2.4 m he cannot reach. At 1.5 m he offers. At 0.6 m he has stopped treating you as a
  visitor and will follow you to the stair.

### 4.5 Non-lethal route — TAKE THE HAND

The encounter has a complete non-combat shape, and it is the recommended one.

- **Take the hand.** Crouch and press the interact key at the offered palm. The player is held for 3 s (the
  camera stays at his eye level; no struggle prompt). He is gentle. He leads the player to the bench, or
  to the enquiry window, or to a door he has been keeping shut, and then lets go. The player receives one
  of: a queue ticket with a number that opens the waiting-room gate; a lost-property tag for an item in the
  room; or the location of the second exit, which he has been sitting in front of for years.
- **The second meeting.** He remembers. He offers the hand first, and does not reach. He will not block the
  door again.
- **Show him a form.** A completed intake form (from the scriptorium or the waiting room) makes him sit
  back down and wait, satisfied that someone is being seen. He does not read it. The form is the shape of
  the thing he wants.
- **Tell him his name.** If the player has found his name in a record (the queue book, the lost-property
  ledger, the Hem's mending tag) and says it, he is still for 5 s, then sits down. He does not speak. The
  room's light does not change. It is the quietest resolution in the game and should not be scored.
- **Pull away.** If the player takes the hand and then pulls away, he holds for 1 s — the only grab in the
  encounter — and then apologises. He does not chase.

The fight exists for players who cannot accept a hand, and it should be winnable and sad. It is not the
default.

### 4.6 What he does not do (deliberate limits)

No biting, no grappling beyond the 1 s hold, no speech beyond "after you" and "sorry" in a worn whisper,
no chase up stairs, no blocking the only exit permanently (the BLOCK state releases after 8 s or one
interaction), no spawning, no mimicry of the Hem, no "pet" prompts, no fetch, no barking, no animal
sounds. He is a man. The encounter fails if the player can read him as a dog.

## 5. Sound cues (in words)

- **Idle:** a shoe scuff on concrete, slow and regular; the dry creak of a tweed seam; a faint cough into a
  cuff; the building's fluorescent hum doing most of the work.
- **Notice:** a palm sliding on the floor; a jacket settling; one knuckle cracking.
- **Offer:** the sleeve falling back — a soft, heavy cloth sound; a breath held a half-second too long.
- **Reach:** a dry, fast scrape, like a chair leg pulled across lino; no growl, no breath.
- **Withdraw:** the same scrape, slower; a quiet "sorry" that is mostly air.
- **Death:** the jacket folding; one shoe tapping the floor once as the leg lets go; then the room tone.
- **The hand taken:** no sting, no chord. A single low cello note that stops when he lets go.

## 6. Sprite roles (3D artist)

One actor, one bank, one pivot at the body centre. The reach is 2.4 m, so the framing span must cover it:
**5.2 m at 768 px = 148 px/m; body ~1.6 m ≈ 237 px**; pivot z = 0.55 m. A tighter 4.4 m span with a
2.0 m reach gives 175 px/m and a 280 px body — a design trade (reach vs resolution), flagged in `NOTES.md`.

| Role | Name | Samples × ticks | Notes |
| --- | --- | --- | --- |
| I | idle / WAITING | 4 × 10 | Knuckles down, hands folded, shoes together. The jacket must read as tweed at 237 px. |
| S | seated / SEATED | 4 × 12 | The first-room pose. Feet on the floor, hands on knees. He should look like a man on a bench, not a crouching animal. |
| N | notice / rise | 3 × 7 | The palm wipe on the trousers is the key frame. |
| O | offer / OFFER | 4 × 10 | Palm up, fingers spread, sleeve back. **The most important pose in the bank.** Must read at ±45° and at −45°. |
| L | reach / REACH | 4 × 6 | Wind, extension, full stretch, miss. The body lags the hand. |
| W | withdraw / apology | 3 × 7 | Hand back, cuff reset, head down. |
| F | follow / walk | 4 × 7 | Four-limbed gait; the jacket drags; one shoulder lower than the other. |
| B | block / doorway | 3 × 8 | Three limbs down, one hand on the frame. |
| T | hand taken / held | 3 × 6 | The player's hand is not drawn; the pose is his hand closed gently around nothing, head up. Use with an engine-side hand prop if needed. |
| H | hurt | 2 × 5 | Flinch, hands over the head, then the shoes. |
| D | death | 5 × 7 | Fold, jacket straighten, still. No collapse. |
| X | corpse | 1 | Jacket over a folded shape; shoes together. |

**Total: 40 samples, 1,600 PNGs** at 5 bands × 8 yaws. The OFFER and REACH frames are the first-proof
gate: if the palm does not read as an offer at gameplay distance, the non-lethal route is invisible and
the encounter becomes a generic crawler.

## 7. Found text

> **QUEUE TICKET 44.** You are number 44. Please wait to be seen. Do not leave the waiting area; leaving
> the waiting area may affect your assessment. *(On the back, in pencil, in a careful hand:)* I have been
> seen. I am waiting to be told.
