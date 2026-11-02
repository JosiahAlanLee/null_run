# THE SPAN — the bridge that is still an animal

**Status: PROPOSAL throughout.** Sheet 11. I have not seen the image; §1 is Claude's description, quoted.
Origin proposed **never human**: a slab-and-rebar span that learned to hold a gap. This is the batch's
traversal creature, and the one with the largest engine cost. Read §4.5 before approving the sheet.

## 1. What the description establishes

| Description detail | What it is |
| --- | --- |
| Long arched body of stacked limestone or concrete paving slabs | The body is made of **deck**: slabs, kerbs, paving, the material of a crossing. |
| Wrapped in rusted rebar cage and cable | The cage is the tendons; the cable is the tension. The body is pre-stressed. |
| Many thin jointed rebar legs with hooked feet | The legs are scaffolding that learned to stand. The hooks grip ledges. |
| Pale eyeless head with whisker-like cables | The head is at one end, hanging over the void; the cables are its only sense. |
| READY: arched, standing | On a ledge, over a gap, waiting to be needed. |
| ACTION: lies across a chasm between two concrete ledges, over pipes, as a bridge, while a small worker in a hard hat walks across its back | **It is infrastructure.** The worker is not a victim; the worker is the institution using it. |

The description gives three facts: **it is made of a road**, **it spans gaps**, and **people already cross
it**. The encounter is not "fight the bridge". The encounter is "the bridge is alive, and you have to
decide what that means".

## 2. Institutional record

**NRRO INTAKE NR-204-S — STRUCTURE (ANIMATE)**
- Subject no.: NR-204-S. Received ██.██.19██. Class: STRUCTURE. Station: stratum 4, root cathedral, the
  west void and the bridge decks; also stratum 1, ossuary, the dry chasm between the north and east
  galleries. Bridge number 4. Load rating: two persons or one cart.
- Description: long arched body, 7.5 m at full span, 1.2 m across the deck; stacked limestone and concrete
  paving slabs; rusted rebar cage and cable; many thin jointed rebar legs with hooked feet; pale eyeless
  head at the west end with whisker-like cables. In the standing state the legs are folded under the arch.
  In the spanning state the body lies across the gap and the slabs lock into a deck.
- Behaviour: spans. The subject extends for a crossing when it detects a load at the ledge, and holds
  until the load leaves. It does not pursue, bite or call. It shudders when struck, overloaded, or when a
  cable is cut; the shudder is a drop, not an attack. A worker (Works & Descent, bridge maintenance) has
  crossed it daily for ██ years. The worker pats the head. The head permits this.
- Origin: a collapsed bridge over the cathedral void, rebuilt by the growth in the only material available.
  The collapse is in the Works record. The rebuild is not. UNRESOLVED.
- Notes: do not cut the cables to "test" the load. The bridge remembers a cut cable and will not extend for
  the person who cut it. The worker's route is the safe route. Do not strike the head; the head is the
  parapet.
- Disposition: IN SERVICE. Bridge 4 is open.

## 3. Lore proposals

### 3.1 Origin (never human — proposal)

It grew where a bridge fell. The cathedral's growth had slabs, rebar and cable, and it had a gap that
wanted to be crossed; the two facts met. The Span is not a bridge that became an animal, and it is not an
animal that became a bridge. It is **a load path that learned it was alive** — the shape of holding a gap,
practised until it could stand up and choose the gap.

That distinction matters for tone. It has no memory of the collapse as an event. It has the **habit of the
span**: it prefers a gap with two good ledges, it tests a ledge before it commits, and it will not cross
water. The worker's daily crossing is, to the Span, the same thing as weather.

### 3.2 What it wants (proposal)

To be loaded correctly. It extends for a crossing the way a hand extends for a tool: because the shape
fits. It is not helpful and it is not servile; it is **used**, and it has no concept of use. The worker
pats it because the worker is a person and the Span is a bridge, and people pat bridges.

The office's word for the species is **the crossing**. Bridge 4 has a maintenance card, a load rating and a
paint mark. The card does not have a species field, so the species is filed under Works.

### 3.3 Strata and room tags (proposal)

**Primary: stratum 4, root cathedral.** Tags: `west void`, `bridge deck`, `chasm`, `pipe crossing`,
`ledge`, `arch`, `gallery`, `nave`. It is at the gaps, always.

**Secondary: stratum 1, limestone ossuary.** Tags: `dry chasm`, `north gallery`, `east gallery`,
`collapsed floor`. The ossuary's gaps are smaller; the Span there is younger and shorter.

**Absent from:** the transit (no gap it respects; the platforms are too regular), the scriptorium (the
bronze lattice is a conductor, not a ledge), the cistern (water; the Span will not span a flooded gap —
the cable would short, and the body knows it). The cistern is the one place a player can be sure the
bridge is not a Span.

### 3.4 Relationships

- **Erratum** — both structural. The Erratum rams a route that was removed; the Span **is** a route that
  was removed and replaced. They meet at a bricked doorway with a gap behind it: the Erratum breaks the
  infill, the Span extends through it. Authored set-piece, not simulated.
- **Circuit** — both cable and rebar. The Circuit's cables are signal; the Span's are tension. A Circuit
  trio can route along the Span's cage; the Span does not notice, and the Circuit does not cut a loaded
  cable. A cut cable on the Span is a **Ravel** mark, not a Circuit one.
- **Unaddressed** — the Unaddressed uses the Span to cross the void and has never thanked it, because
  thanks is not a load. The Span does not expect thanks. If the Unaddressed's plates are on the far ledge,
  the Span is the way to reach them.
- **White Bloom** — the Bloom makes wet floor; the Span will not span wet ground. In the basin the Span is
  absent and the Bloom is not.
- **The worker** — a Works & Descent maintenance worker in a hard hat, a one-off neutral NPC. The worker
  crosses the Span, pats the head, and writes on the card. The worker is not a combatant and should not be
  killable without consequence (see `NOTES.md`, item 4).

## 4. Encounter design

### 4.1 Stat block (starting values)

| | |
| --- | --- |
| HP | **380** (structure-class; the fight is optional and expensive). Slabs **0.3×**; cables 1.25×; head 1.5×; legs 0.75×. |
| Size | 7.5 m long spanning; 1.2 m wide deck; 2.2 m arch; legs 2.5 m |
| Speed | walk 100 u/s on ledges; unfold 2.5 s; bridge hold indefinite; shudder 0.5 s |
| Attacks | rebar leg lash 18 (3.2 m, one leg); shudder/buck (fall damage 20–40, or drop to a lower ledge); no bite, no ranged attack |
| Fairness caps | it never attacks first; it bucks only if struck, overloaded, or a cable is cut; one lash per 6 s; the head is never in the walking path; the bridge is safe while the cables are taut |

### 4.2 Behaviour

| State | Ticks | What it does | What it means |
| --- | --- | --- | --- |
| ARCHED (idle loop) | 3 × 10 = 30 | Arched on the ledge, legs folded under, slabs breathing slightly; the head hangs over the void, whisker cables drifting. | Waiting to be needed. |
| NOTICE | 3 × 8 = 24 | The head turns (eyeless) toward footsteps; the rebar legs tap the ledge in sequence, testing; the arch deepens. | It has heard a load. |
| UNFOLD | 4 × 22 = 88 | It stands leg by leg, the slabs separating, the cage tightening; it walks to the gap edge. | The invitation. |
| SPAN | 4 × 12 = 48 | It lies across the gap; the slabs lock with a concrete-on-concrete clack; the whisker cables go taut and point across. | **The bridge.** The pose is the encounter. |
| LOCK | 3 × 6 = 18 | A final settle; the deck stops moving; the head lowers. | Cross now. |
| SHUDDER | 4 × 5 = 20 | The arch drops 0.5 m; slabs separate; dust; a cable twangs. | The buck. The player must run back or drop. |
| LASH | 3 × 6 = 18 | One rebar leg swings in a low arc; the hooked foot catches the light. | Only if attacked. |
| RE-ARCH | 4 × 10 = 40 | It withdraws from the gap, re-stacks the slabs, and re-arches on the ledge. | Cooldown. It will not extend again for 30 s. |
| WALK | 4 × 8 = 32 | Many-legged walk along a ledge, slabs shifting, head low. | It relocates to another gap. |
| HURT | 2 × 6 = 12 | A slab cracks; dust; it braces. | It does not flinch away; it flinches **down**. |
| DEATH | 5 × 9 = 45 | The arch collapses from the middle; slabs fall into the void; the head goes last. | The bridge is gone. |
| CORPSE | 1 | A rubble pile on both ledges; one whisker cable still hanging. | The gap is now a gap. |

The sheet's named poses map as: `ready` = ARCHED, `action` = SPAN. LOCK and SHUDDER are the two states the
encounter is built on.

### 4.3 The telegraph

**The arch deepens and the slabs clack.** Before it extends: the legs tap the ledge in sequence, the arch
rises, the whisker cables go taut and point across the gap. Before a **shudder**: the slabs lift a finger's
width, the cables snap straight, and fine dust falls from the deck. The shudder telegraph is 0.5 s; the
player must already be moving. The bridge has no wind-up for the first crossing — extending is not an
attack, and treating it as one would make the traversal unreadable.

### 4.4 Counterplay

- **Cross when LOCK.** The deck is stable only in LOCK; in SPAN it is still settling. The worker waits for
  LOCK. So should you.
- **Keep to the centre line.** The deck is 1.2 m wide; the edges are slab lips. A jump loads one slab and
  can trigger a shudder. Walk.
- **Do not cut cables.** A cut cable drops a slab permanently, and the Span remembers: it will not extend
  for the player who cut it. This is a **soft-block** for that crossing and must have a backup route (4.5).
- **Do not overload it.** The load rating is two persons or one cart. Carrying a heavy item (the Pleat's
  block, a full fuel can, a body) counts as two. Set it down, cross, come back. The Span shudders once as
  a warning before it bucks.
- **Do not strike the head.** The head is the parapet; a hit makes it withdraw and re-arch, and the bridge
  is gone for 30 s. If you must fight it, fight the legs, not the head.
- **If it shudders,** run back to the near ledge or drop to the lower ledge (authored catch ledges, not a
  death pit). The drop costs 20–40, not the run. There is no instant death from the Span; the void is
  below the lower ledge, not below the deck.

### 4.5 Traversal contract (engine handling — read this)

The Span is a **living bridge**, and a billboard sprite cannot be walked on. The proposal is a hybrid, and
the hybrid is the condition of approval:

1. **The collider is a level mesh, not the actor.** A 7.5 m × 1.2 m bridge deck brush (or a moving sector)
   is authored across the gap. The Span actor is drawn over it. The deck must exist before the Span is
   spawned; the actor's SPAN state enables it and its RE-ARCH state disables it.
2. **The actor's path is authored, not simulated.** The Span walks from its ledge to the gap edge on a
   fixed path, then lies down on a fixed deck line. No procedural IK, no physics. The sprite's slab line
   and the deck brush must be built from the same numbers; a 0.1 m mismatch reads as a floating animal.
3. **The player is parented to the deck.** Walking on it is ordinary floor movement; the deck has a
   `blockplayer`/`walkable` flag, a 1.2 m width, and a lip that stops a fall. The camera does not ride the
   actor; the actor is visual. If the deck moves during SPAN/LOCK, the player moves with the sector.
4. **The shudder is a scripted drop, not a physics event.** SHUDDER lowers the deck brush by 0.5 m over
   20 ticks, plays the sprite's shudder, and raises it again. If the player is on the deck, they ride the
   drop; if they are at the edge, they slide. No ragdoll, no random fall.
5. **The fall is authored.** If the player leaves the deck, they land on the lower ledge (a catch brush at
   −2.5 m) and take 20–40. The void below the catch ledge is the death pit, and the catch ledge is the
   reason the encounter is fair. Do not rely on the engine's default falling.
6. **The cut cable is a persistent level state.** Cutting a cable sets a flag on the bridge's line; the
   Span refuses to extend for 60 s and the missing slab is a visible hole. The backup route (a lower
   service walk, a pipe crossing, or a one-way drop) must be authored **before** the bridge, per the
   softlock rule.
7. **The worker is a path, not an AI.** The worker crosses on a fixed spline at a fixed speed, pauses at
   the head, pats it, and writes on the card. If the worker is a full NPC, the path is still fixed. The
   worker's route is the tutorial for the crossing: the player sees the centre line, the LOCK pause, and
   the pat before they are asked to do it.
8. **The bridge pose needs a non-billboard option.** A 7.5 m sprite at 8 bands will be either tiny or a
   very long canvas. The recommendation is a **three-part hybrid**: a low-poly slab-and-rebar deck mesh
   (always present, 1,200–1,800 tris), the Span's **head and forelegs** as a normal billboard actor at the
   near ledge, and the **hind legs** as a second billboard at the far ledge. The middle is mesh. This
   keeps the animal readable at both ends, keeps the deck walkable, and avoids a 7.5 m billboard.
   Cost: one bespoke mesh, one two-ended actor rig, one authored path. It is still cheaper than a
   full skeletal bridge.

**Softlock rule:** the Span must never be the only way back. Every gap it spans needs a return route that
does not depend on the Span being alive, willing, or unprovoked. If the player kills it, the level must
still be completable. This is a hard requirement, not a preference.

### 4.6 Non-lethal / puzzle route — THE CROSSING

The default encounter is not a fight. It is a traversal with three readable states:

- **Follow the worker.** The worker crosses first; the player crosses behind at 3 m. The Span holds for
  both. This is the tutorial and the intended first crossing.
- **Cross alone.** Approach the ledge; the Span notices, unfolds, spans, locks. Wait for LOCK; walk the
  centre line; do not jump. It holds until you leave.
- **Ask it to span the other gap.** At a junction with two gaps, the Span can only take one. The worker's
  card marks which one is inspected. Lure it with a load (a heavy item set on the far ledge) or show it a
  lantern at the second gap; it walks and spans. The first gap is then closed, and the player must choose.
  This is the puzzle: the bridge is a resource, not a fixture. Both gaps must be forward branches from
  the same ledge; never let the lure strand the player on the far side of the only way back.
- **Repair a broken span.** A missing slab can be spliced with rebar and cable from the environment (a
  short interaction, no skill check). The repair is temporary: the Span holds for one crossing, then
  withdraws. It is a temporary way to cross after a cut cable; the backup route is still the guarantee.
- **The worker's pat.** If the player pats the head (interact at the head, no weapon), the Span lowers its
  head and the next crossing is 20% faster to LOCK. It is not a trick; it is the same gesture the worker
  makes. It is also the only "friendship" mechanic in the batch, and it should be quiet.

## 5. Sound cues (in words)

- **Idle:** concrete breathing — a slow, gritty settle; cable humming in a draft; the head's whiskers
  ticking against the ledge.
- **Notice:** rebar tapping stone, one leg at a time, like a surveyor's staff; a deep stone groan.
- **Unfold:** slabs sliding apart, rebar creaking, cable tightening with a high thin note.
- **Span:** a long concrete-on-concrete clack, then a wash of small settles; the deck finding its line.
- **LOCK:** one clean knock, then nothing. The nothing is the cue.
- **Shudder:** a cable twang, a slab crack, dust falling on stone; no roar.
- **Lash:** rebar whistling through air; the hooked foot biting a wall.
- **Death:** the arch failing from the middle, slabs hitting the lower ledge one after another, the head
  last; a long cable sigh.
- **The worker:** boots on slabs, a pencil on a card, a pat on stone. No dialogue.

## 6. Sprite roles (3D artist)

The full bridge is **not** a single billboard (see 4.5). Bake the actor in two ends plus a deck mesh.

| Part | Role | Samples × ticks | Notes |
| --- | --- | --- | --- |
| Head/near | I arched / idle | 3 × 10 | Head over the void, whiskers drifting. |
| Head/near | N notice | 3 × 8 | Head turn, leg tap. |
| Head/near | U unfold | 4 × 22 | Stand, walk to the edge, first slab down. |
| Head/near | P span / bridge (near half) | 4 × 12 | The near 3.5 m of deck and the head; the deck mesh takes over at the cut. |
| Head/near | K lock | 3 × 6 | Final settle, head lower. |
| Head/near | Q shudder | 4 × 5 | Drop, dust, cable twang. |
| Head/near | L lash | 3 × 6 | One leg, low arc. |
| Head/near | R re-arch | 4 × 10 | Withdraw, re-stack, re-arch. |
| Head/near | H hurt | 2 × 6 | Slab crack, brace. |
| Head/near | D death | 5 × 9 | Collapse from the middle; the head last. |
| Head/near | X corpse | 1 | Rubble, one whisker. |
| Hind/far | P2 span / bridge (far half) | 4 × 12 | The far 3.5 m and the hind legs; mirrors the near half's settle. |
| Hind/far | W walk | 4 × 8 | Many-legged walk along a ledge. |
| Hind/far | D2 death | 4 × 8 | The far half collapses a half-beat later. |

**Total: 48 samples, 1,920 PNGs**, plus a 1,200–1,800-tri deck mesh (shared by all Span instances) and one
authored path. First-proof gate: I 2, N 1, U 1, P 2, K 1, Q 1, D 2, X 1 on the near half, P2 1 and D2 1 on the far half = 13 samples. Span framing: near/far half each ~3.8 m pose extent; **8.0 m span at 768 px = 96 px/m** is
adequate for the ends (the proven span), and the deck mesh carries the middle at full resolution. Do not
try to bake a 7.5 m body at 768 px; it will be 720 px long and 30 px tall.

## 7. Found text

> **BRIDGE INSPECTION CARD 4.** LOAD: TWO PERSONS OR ONE CART. LAST INSPECTION: ██. CONDITION:
> ATTENTIVE. Cross at the lock, not at the clack. Do not jump. Do not cut the cables to test the load; it
> remembers. The worker is authorised to pat the head. The head is the parapet. *(Pencil, bottom margin:)*
> It held for the cart. It did not hold for the cart and the two persons. We have revised the card.
