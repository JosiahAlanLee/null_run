# THE ARMATURE — ecology: the Spindle colony

**Status: PROPOSAL throughout.** Follow-up to `ARMATURE.md`. Three new sheets: **Armature, bone / torso
damage**, **Armature, Spindle control**, and **Vore Spindle, rebar / bone**. I have not seen the images; §1
is Claude's descriptions, quoted. The established rules hold: never human; no flesh, no gore; the material
becoming aware. The organic edge is fungal and plastic, not meat: tendons are a fibrous, slightly glossy,
semi-translucent growth halfway between fungus and plastic; cores are faceted crystal; bone is dry and
clean; the Spindle's sac is a seed-like membrane. The wetter look on the Spindle-control sheet is fine.

## 1. What the three descriptions establish

| Sheet | Description detail | What it is |
| --- | --- | --- |
| Armature, bone / torso damage | Dry bone — ribs, a forearm bone, a scapula — bound into the rebar cage with tie wire; broken rebar ribs | The Armature takes in rigid material at hand. In the ossuary, that material is bone. The broken ribs are structural, not a wound. |
| Armature, Spindle control | Reddish control tendons threaded through the body; green faceted Vore Spindle colony cores, a large one at the chest; poses dormant, walk, strike | The core is the organ; the tendons are a semi-translucent growth threaded through the cage; the Armature is the body the colony is wearing. |
| Vore Spindle, rebar / bone | Crab-like body of bundled rebar legs with hooked feet; dark seed-like sac; bone plates and tusks; green faceted cores; poses walk, brace, LAUNCH (fires a colony core trailing a tendon), hit | A Spindle adapted to dry rebar and bone. It is a colony-bearer: the core is both its child and its projectile. |

Three facts: **the core is the link**, **the tendon is the leash**, **the bone is the local material**. The
ecology is not a new creature; it is a relationship between two existing ones. The controlled Armature is
still an Armature, and the Spindle is still a Spindle. Nothing here gives either one a voice, a face or a
grudge.

## 2. The infection loop

### 2.1 Stages

| Stage | Ticks | What happens | What it means |
| --- | --- | --- | --- |
| BRACE | 3 × 8 = 24 | The Spindle plants its rebar legs, the bone plates lift, the rib cage opens, the large core brightens; a rising glass hum. | The tell. The Spindle is choosing a host. |
| LAUNCH | 3 × 4 = 12 | The ribs peel open; the core leaves with a ratchet-zing and a soft stretch, trailing a tendon. | The colony is in the air. The launch is loud; the core is quiet. |
| FLIGHT | 30–42 ticks | The core arcs slowly, a green point at the end of a pale line; it does not home. | It can be shot. It is aimed at a host, not at the player. |
| LODGE | 3 × 5 = 15 | The core strikes a dormant Armature's chest or a rebar heap; it catches in the cage, not in flesh; the tendon goes taut. | The host is chosen. A miss leaves the core on the floor, still on the tendon. |
| ROOT | 4 × 6 = 24 | Pale, semi-translucent tendons run from the core into the bars; the heap shivers; the core hum rises; a few bars lift. | The colony is wiring the body. This is the last chance to shoot the core before it has a body. |
| RISE | 5 × 8 = 40 | The heap stands up: bars find their places, the torso cage closes around the core, the head is last, the tendon retracts to the Spindle and goes taut. | The unbind in reverse. The signature scene. |
| LINK | 2 × 6 = 12 | The new Armature settles; the core hum steadies; the Spindle settles or walks. | The pair is live. The Spindle is anchored while the link holds; it cannot launch again until the link is broken. |

### 2.2 What can be infected

- **A dormant Armature** — one in STAND, not one in NOTICE, WALK, WINDUP or STRIKE. The core needs a still
  cage. The host keeps its 40 HP and its full body; if the core is later destroyed, it reverts to a free
  Armature. A dormant host does not rise: it stiffens, the core lights, and the tendons thread through the
  cage over 24 ticks. The **heap** host is the one that stands up.
- **A rebar heap** — a corpse heap or a rebar pile prop. The heap has no free body to return to, so the rise
  is a reassembly, not a possession. The host is a jumble: mismatched bars, bent ends, a lower stance
  (about 1.7 m), an asymmetrical head. HP 30. If the core is destroyed, it collapses.
- **Not a moving Armature.** The core cannot catch a cage in motion; a fighting Armature is safe from
  infection until it is killed, and then its heap is a host. This is deliberate: the player can prevent
  infection by keeping the pack awake, but a woken pack is already a fight.
- **Not a person, a Circuit, a Span or a Spindle.** The core needs a rebar cage with gaps. A body of flesh
  has no gaps; a cable network is the wrong structure; the Span is a load path rather than a standing cage,
  and a later set-piece could try it (see `NOTES.md`), but not in this build.
- **A bone heap** works if there is rebar in it. In the ossuary, every heap has both.

### 2.3 The rise is the horror

The heap stands up. That is the scene the ecology exists for: the player has learned that a heap is dead,
and then the dead thing reassembles around a green light. The bars do not fly; they lift, find their
places, and settle, the way a bundle is tied. The head is last. The first sound the new body makes is not a
creak; it is the core's hum. The free Armature's silence is replaced by a continuous tone, and that tone is
the tell that this one is not free.

Show the rise once per run, at a distance, with no other enemies in the room. The player should be able to
watch it or interrupt it, and should learn the green core before being asked to shoot one. After that, the
loop can happen off-screen: the player finds a controlled Armature and follows the tendon back to the
Spindle. The inference is cheaper and creepier than the animation.

### 2.4 The tether

The tendon is a growth halfway between fungus and plastic: fibrous, slightly glossy, semi-translucent, 12 m
at full extension. It is the control link and the leash at once.

- **Taut:** the controlled Armature can move anywhere within 12 m of the Spindle. At the limit, the tendon
  tautens, the Armature stops, and the Spindle can reel it in. The pair cannot leave the room together.
- **Visible:** in light, the tendon is a pale, glossy line with a faint green shimmer; in the dark, only the
  core's green glint shows where it runs. It sags, catches on corners and runs over the floor; it is not a
  laser.
- **Cuttable:** the tendon is engine geometry, not a sprite. It has a thin hitbox and 20 HP. Cutting it
  frees the host (collapse or reversion, §4) and releases the Spindle from the anchor — but the colony core
  is lost with the host, so the Spindle is spent and will retreat, not re-launch. This is an advanced
  counterplay: the core is the obvious target, the tendon is the quiet one.
- **The tether is a map.** The player can follow it from a controlled Armature back to the Spindle. In a
  dark room, the green shimmer on the tendon is the trail. The Spindle knows this, in the sense that it
  prefers to anchor behind cover; it does not hide the line, because it cannot.

## 3. Controlled versus free

The controlled Armature is not a new creature. It is a free Armature with a colony in its chest: the same
bars, the same creak, the same unbind. The differences are purpose, coordination and the core. The free one
is deliberately underwhelming; the controlled one is the panic spike (§8).

| | Free Armature | Controlled Armature |
| --- | --- | --- |
| Idle | Stands anywhere, still, no continuous sound. | Dormant or on guard: upright, head down, core humming; stands between the Spindle and the player, facing out. |
| Notice | Head turns to the last sound or light; the wake passes one to the next, but it is not a plan. | Does not listen to the player. The **Spindle** is the sensor; when it notices, its core pulses and the Armature turns. Kill the Spindle and the Armature is blind. |
| Approach | Walks to the last disturbance; stops when the sound stops; does not coordinate. Each one arrives on its own, often from the same direction; they crowd the same line and get in each other's way. | Patrols a 6–8 m cordon around the Spindle; interposes; does not chase beyond the tether. It moves with purpose, not with curiosity. |
| Windup | One arm; 32 ticks sweep / 24 jab; the creak rises. | **Both arms**; 40 ticks; the chest opens, the core brightens, the hum rises with the creak; the strike is a two-arm slam. |
| Attack | Sweep 9 in a 1.9 m arc, or jab 12 in a 2.2 m line. | Two-arm slam **16** in a 2.2 m arc; one attack, then a long recovery. No jab; the colony does not do precision. |
| Hit reaction | A clang, a wire snaps, the body re-settles. | The core flickers; the tendons jerk; the body does not re-settle as freely. The Spindle feels the hit as a tug on the tendon. |
| Death | Unbind; heap. | Core destroyed: collapse (heap host) or reversion (dormant host). Spindle destroyed: the tendon goes slack; the same two outcomes, but the Armature stands confused for 1 s first. |
| Pack | No squad. One creak wakes the next, but they do not flank, synchronise or cut off; they arrive one at a time and often collide. | Coordinated patterns: synchronised windups, pincer, cut-off, converge on light (§8). At most **two** controlled Armatures per Spindle; they move on the Spindle's pulse, not on each other's creak. |

The controlled Armature is not faster. Speed is the same 150/230; the lope is still there. What changes is
that it knows where it is going. It guards, it interposes, it commits to the two-arm slam. The free one
tests the load; the controlled one protects the colony. That is the whole behavioural difference, and it is
enough to make a familiar body read as wrong.

## 4. The weak point and the two outcomes

### 4.1 The green core

The colony core sits at the centre of the chest, inside the rib cage: a faceted green crystal about 0.25 m
across, the only saturated colour on the body and the only continuous light in a dark room. It is the weak
point, the tell and the leash anchor.

- **Hitbox:** a small sphere at the sternum, visible from the front and the sides; the back is shielded by
  the spine bundle. The rib bars cover it partially; a shot through the ribs does **1.0×**, a shot in the
  open **2.0×**. The chest opens during the two-arm windup, which is the clean window.
- **HP:** 20. It is not a second health bar; it is a prop with its own hit points. Destroying it triggers the
  outcome immediately.
- **Read:** the core is the only part of a controlled Armature that glows. A free Armature has no light.
  The player learns: green chest = controlled; no green = free; green at the end of a line = a Spindle.
- **The core does not speak, blink or look.** It pulses at about 0.5 Hz, a signal, not a heartbeat. It has
  facets, not an iris. Never give it a pupil or a face.

### 4.2 Outcome 1 — the heap host collapses

A heap that stood up has no free body to return to. The core is the only thing holding the reassembled
bundle in a body shape. Destroy it and the Armature **unbinds on the spot**: the control tendons snap, the
bars let go, the green light goes out, the core falls out and rolls, dark. The heap stays, now with a dead
core in it. This is the clean kill, and it is the one the player will see most often in the cistern, where
heaps are the usual host.

The collapse uses the free Armature's DEATH state with a different first beat: the core cracks before the
wires snap. No new bank is needed if the core is a prop; the prop pops, the bank plays the unbind.

### 4.3 Outcome 2 — the dormant host reverts

A dormant Armature was a free one before the core lodged. Destroy the core and the control is removed, not
the body: the tendons snap, the green light goes out, the Armature drops to a knee for 1 s (STUN), then
stands as a **free Armature**. It is not grateful and it is not an ally. It tests the nearest load, which
may be the player, the Spindle, or both. A reverted Armature will attack the Spindle if the Spindle is the
nearest large load; that is a legitimate tactic, but it is not reliable, and the player should not be told
it is.

The reversion is the more interesting outcome because it turns the ecology against itself. It is also the
more expensive one: the player has to survive a free Armature after spending shots on the core.

### 4.4 If the Spindle dies first

The Spindle is the will. Kill it and every tendon goes slack at once.

- Heap hosts **collapse** where they stand; the green lights go out one after another, in the order the
  cores were linked. The room darkens in sequence. This is the "all clear" beat and the clean solution to
  the encounter.
- Dormant hosts **revert**: they stand confused for 1 s, then behave as free Armatures. The player still has
  a fight, but it is the familiar one.
- The Spindle's own core goes dark last. If the player is counting green lights, the last one is the hub.

Killing the Spindle first is the recommended counterplay, and the level should make it possible: the
Spindle must be reachable, not parked behind an unkillable barrier. If the geometry forces the player to
fight the controlled Armature first, the encounter is a tax, not a puzzle.

### 4.5 If the tendon is cut

Cutting the tendon is the quiet solution. The host is freed (collapse or reversion, same as above), but the
colony core is still lodged in it, dead or stranded. The Spindle has lost its large core and cannot launch
another; it is spent and will retreat, not re-arm. The player can also cut the tendon after the core is
destroyed, but there is no reason to.

The tendon is thin and hard to hit; it should not be easier than the core. It is the expert route, not the
default.

### 4.6 Counterplay

- **Kill the Spindle first.** It is the sensor and the will. Without it the controlled Armatures are blind
  and lose their link; heap hosts collapse and dormant hosts revert. The Spindle is a support creature, not
  a boss — around 80 HP, with its own green core at 2× — and the level must make it reachable. If the
  geometry forces the player to fight the cordon first, the encounter is a tax.
- **Shoot the cores in flight.** The colony core is slow, aimed and does not home; it is a green point at
  the end of a pale line. A flying core is fragile (10 HP, one clean hit); the lodged core is tougher (20
  HP). The player can also shoot a core that missed and is lying on the floor, still on the tendon.
- **Deny the heaps.** A heap is a host. Destroy rebar piles and corpse heaps before the Spindle launches —
  or after a kill, before the next launch — and the Spindle has nowhere to put a core. This costs ammo,
  time and noise, and it removes the heap's warning value; it is a trade, not a free action. The authored
  infection markers (see `NOTES.md` §4) are the props that can be destroyed.
- **Cut the tendon.** The expert route: 20 HP, thin hitbox, no green core to aim at. It frees the host and
  strands the colony core; the Spindle is spent and retreats. Do not make the tendon easier to hit than the
  core; it is the quiet solution, not the obvious one.
- **Use the reversion.** Shoot the core on a dormant host and step back. The freed Armature is not an ally,
  but it tests the nearest load, and the nearest load may be the Spindle. Do not promise this in the UI; let
  the player discover it.

## 5. The bone variant

### 5.1 What the sheet establishes

Dry bone — ribs, a forearm bone, a scapula — bound into the rebar cage with tie wire, and broken rebar ribs.
The sheet reads two ways at once: a **damage state** (the cage is broken, the ribs are snapped) and an
**ossuary variant** (rebar that has taken in shelved remains). Both readings are useful, and the design
should keep both.

### 5.2 The rule: local material

The Armature incorporates rigid material at hand. In the transit it is rebar and scaffold tube; in the
ossuary it is bone. The bone is not a person and not a relic with a name; it is material, like the bars.
The tie wire binds a scapula the same way it binds a bundle. The office's record would call it
**reinforcement (ossuary grade)** or "reinforcement with incorporated shelf material"; the trade word is
still **standers**.

The bones are dry, clean and empty: no flesh, no marrow, no blood, no hair, no cloth. A bone that still had
a name attached would turn the creature into a ghost story and break the premise. The ossuary's bones are
shelf material; the Armature does not know what a shelf is.

### 5.3 It is a place variant, not a damage state

The broken ribs and the bones look like wounds. They are not. The bone variant has the same 40 HP as a free
Armature; the player's first read ("this one is damaged") is wrong. That misread is the point, and it must
be quiet, not comic: no limp, no whimper, no "wounded animal" behaviour. It walks and strikes exactly like
a rust Armature.

Mechanically:
- Bone parts **1.25×** (brittle); rebar joints **1.25×**; torso cage **0.7×**. The bone is a small
  vulnerability, not a new fight.
- Speed is unchanged; the bone is lighter but the cage is the same.
- The death scatters bones out of the heap; the heap prop has a bone variant. The bones in the heap are a
  warning and a resource for the Spindle.
- The bone variant is a **skin plus attachments**, not a new bank: the same skeleton, with bone props bound
  into the cage and a paler atlas. The broken-rib silhouette must read at gameplay distance; if it does not,
  the variant is just a recolour.

### 5.4 Bone in the ossuary

The ossuary is the bone variant's home. Put it in the repair scaffolding, the closed galleries and the
works store, never in the shelf galleries (the ReDead owns those). The bone variant is the default Armature
skin in the ossuary; the rust variant appears only in the newer repair work.

The bone variant is also the ossuary's infection host. The rebar/bone Spindle lives in the same closed
galleries, and its controlled Armature is a bone cage with a green core. The visual is strong: a pale bone
lattice, a green jewel at the chest, a pale, glossy tendon running back to a crab of rebar and bone. Use the
bone-controlled **scene** once per ossuary, not as a random spawn; the bone **skin** itself is the default
in the ossuary.

### 5.5 The bone heap

A bone Armature leaves a heap of bars and bones. The heap prop needs a bone variant: a low tangle with a
scapula or a rib ends, a few wire ends, no skull (never a skull — a skull reads as a person). The Spindle
can infect it; the bone-controlled Armature rises from it. The player can destroy the heap to deny the
host, the same as any rebar heap.

## 6. Sound and lighting for the core

### 6.1 Sound

The core has the only continuous tone in the Armature's palette. The free Armature is silence and creaks;
the controlled one hums. That is the cleanest audio tell in the ecology.

- **The core hum:** a faint glass hum, high and pure, dry — a finger on a wet glass rim, but without the
  wet. It is steady, with a slow amplitude pulse at about 0.5 Hz; it is a signal, not a heartbeat. It carries
  about 10 m and is directional; it is a clue, not a beacon across the level. Each core has a small pitch
  offset (±2 semitones) so the player can count them.
- **The windup:** the hum rises with the creak. A controlled windup is two sounds at once — the Armature's
  rising rebar creak and the core's rising glass hum — and that doubling is the controlled tell. The free
  Armature never doubles.
- **The tendon:** a soft creak, like stretched plastic or mycelium, under the metal creak; a low elastic
  twang when it goes taut; a slack thrum when it is cut. The launch is a soft stretching sound as the tendon
  unspools, with the Spindle's ratchet-zing under it; the core in flight is quiet. The launch carries
  further than the core, as the Spindle's launch always does.
- **The core hit:** a glass crack, a bright shatter, a thin pop; the hum stops; the green light goes out.
  No wet sound. The shards are dry and fall like glass.
- **The rise:** the unbind in reverse — bars lifting and settling, a wire tightening, the hum starting at
  the chest and steadying. The last sound is the tendon retracting with a long soft zing.
- **The Spindle:** the rebar/bone variant's brace is a bone-and-rebar scrape; its launch is a ratchet plus a
  glass chime; its own large core hums at the hub. The controlled cores answer it at the same pitch, so the
  room sounds like a small chord. When the Spindle dies, the chord loses its root and the satellites go out
  one by one.
- **The bone variant:** a dry bone tick, a hollow knock, a single clatter when a bone shifts; no rattle, no
  chatter. The bone is a different pitch, not a different creature.

**Mix rule:** the core hum is a P4/P5 source, not a tell; the windup is the tell (P6). The pack of cores
should not eat the tell budget: cap the hum at two concurrent voices per room, and let the nearest core
dominate. The player should be able to hear how many controlled Armatures are near, not a wall of hum.

### 6.2 Lighting

The green core is the only light the creature carries. In a dark room, the green glint is the first thing
the player sees — often the only light in the scene apart from their own — and it is a **point**, not a
wash.

- **The glint:** a small, faceted green spark at the chest, with a hard specular and a short falloff (1–2 m).
  It lights the inside of the rib cage, so the player sees a green cage before a silhouette: first the
  point, then the bars, then the shape. The core is visible before the Armature. That is the dark-room
  notice tell.
- **No green fog, no green room light.** The core is not a lamp; it does not illuminate the floor or the
  walls beyond the body. The player still needs their own light to cross the room. The green is the only
  saturated colour in the scene; use it sparingly or it becomes a genre cliché.
- **The tendon:** a pale, glossy line with a faint green shimmer where the core's light catches it. In the
  dark, the tendon is the trail back to the Spindle: a green point, a pale line, a second green point. The
  player can follow it.
- **The bone variant:** pale bone catches the green; the cage becomes a green-lit lattice, brighter than the
  rust variant. The bone is the backlit silhouette in the ossuary; the core is the jewel in it.
- **The two deaths:** when a core is destroyed, the green goes out and the room goes dark; the collapse is
  heard, not seen, unless the player is lighting it. When the Spindle dies, the cores dim in sequence, one
  after another; the room darkens in order, and the player can count the lights going out. Do not add a
  flash or a green explosion; the light simply stops.
- **The rise:** light the core, not the body. The green point hangs in the dark, the bars lift into the
  edge of its light, and the shape assembles around it. If the player's light is on the heap, the rise is a
  silhouette; if not, it is a green point and a sound. Both work; prefer the green point.

## 7. Strata, frequency, and the first infection

The ecology needs two things: a Spindle and a supply of rebar cages or heaps. The classic Spindle is a
cistern/basin organism; the rebar/bone variant extends it into dry strata. The bone variant is the
ossuary's local skin of the Armature, and the rebar/bone Spindle is the ossuary's local Spindle.

| Stratum | Spindle variant | Host skin | Frequency | Notes |
| --- | --- | --- | --- | --- |
| 3 flooded cistern / settling basin | classic Spindle (pale chitin, membrane) | rust Armature; heaps | **primary**: one Spindle per 4 free Armatures; one infection site per 3 rooms | the ecology's home; the first infection is here |
| 4 root cathedral | rebar/bone Spindle | rust Armature; some bone | **secondary**: one Spindle per 5 Armatures; one site per 4 rooms | damp rebar thickets; the tendon disappears into the roots |
| 1 limestone ossuary | rebar/bone Spindle | **bone Armature**; bone heaps | **secondary**: one Spindle per 6 Armatures; one site per 5 rooms | closed galleries and repair scaffolding only; never the shelf galleries |
| 2 bronze scriptorium | rebar/bone Spindle | rust Armature | **rare**: one Spindle, 1–2 Armatures; one site per 6 rooms | only the flooded reading floor; the bronze is the wrong material |
| 0 institutional transit | none | — | **absent** | too dry and too new; the Armature here is always free |
| boss arenas | none | — | **absent** | bosses do not share |

**Frequency rules.**
- The ecology is a **set-piece**, not the default. Most Armature encounters are free packs. The player must
  meet free Armatures first, or the controlled one has no baseline.
- Never in the first room of a stratum. The first infection is a scripted scene, shown at a distance, with
  no other enemies. After that, the loop can happen off-screen.
- At most **one Spindle per room** and at most **two controlled Armatures per Spindle**. A third is a
  crowd; the cordon stops reading.
- A Spindle room has the Spindle, one or two controlled Armatures, and one or two **dormant** Armatures
  (the next hosts). It does not also have a free patrol pack. A dormant host is not a patrol: it stands
  still, and it can be killed before it is infected. The stratum-wide ratio (one Spindle per 4/5/6
  Armatures) is a density guide, not a per-room count.
- Never a free patrol pack and a controlled cordon in the same room, unless the scene is "the Spindle takes
  the pack" — a scripted set-piece in which the player watches a dormant pack get infected one by one. Use
  once per run at most.
- The Spindle must be reachable. If the geometry puts it behind an unkillable barrier, the encounter is a
  tax; the player must be able to kill it first, or the whole counterplay collapses.
- The bone variant is the default in the ossuary, not a rare spawn. The rust variant is the default
  everywhere else. The two skins should not mix in one pack except at a repair seam between strata, or in
  the cathedral's bone thickets.
- The green core is rare enough to stay special. If every third Armature glows, the dark rooms lose their
  darkness and the core becomes a lamp.

## 8. Panic: the tick and the coordinated attack

`shared/inputs/nullrun/PILLARS.md` §5 is explicit: the Armature is the game's panic spike, and the first
impression must be harmless.
A free Armature is stiff, slow, uncoordinated, easy to underestimate. The player kills two or three and
learns the creak. Then the tick starts, and the same bodies become a squad. The horror is not a new monster;
it is the same monster, suddenly organised.

### 8.1 Two reads

| | Free Armature | Controlled Armature |
| --- | --- | --- |
| Silhouette | rust bars; no light; no tendon | the same body with a green core, reddish glossy tendons and a pale tendon running away into the dark |
| Sound | metal creak, wire tick, rebar chink; irregular; silence between | the same, plus the core's glass hum and the Spindle's ceramic tick; the creaks synchronise |
| Movement | stop-start; each one walks to the last sound on its own; they crowd the same line, arrive late | still, then a cordon; they move on the Spindle's pulse; they guard, flank and cut off |
| Threat | a slow nuisance; dangerous only if cornered | a machine; the room is the attack |
| Player read | "I can handle these" | "I have to leave, or kill the thing making the tick" |

The free one is deliberately underwhelming. It is stiff; its knee catches; it stops halfway through a step;
it arrives after the fight is over. That is the setup. The controlled one is the same silhouette with a
green heart and a plan. Make the free one slow and clumsy, not comic: the player's overconfidence is the
joke, not the creature.

### 8.2 The tick

The tick is the Spindle's ceramic claws on the floor. It is not the Armature's sound; it is a new source,
and it is the panic trigger and the fair warning at once. It is the sound of the Spindle arriving; the cores
lighting is the sound of it taking control.

- **Source.** The Spindle walks on ceramic/porcelain claw tips — the classic Spindle's pale chitin, the
  rebar/bone variant's hooked feet. The tick is small, hard and regular. It comes from the dark at the edge
  of the room: a side passage, a vent, a stair, behind a column. It is at floor level and it circles; it
  does not come from the Armature.
- **Build.** One tick. A pause — the player is not sure. Then tick-tick. Then tick tick tick, the interval
  shortening from about 1.2 s to 0.4 s. The rhythm is the clock. Then a pause, and the green cores light one
  by one with the soft hum. The walking tick stops when the Spindle settles; the hum continues, and the
  Spindle taps its claws in place. The pause before the cores is the "oh no" beat.
- **The count-in.** Once the cores are lit, the tapping becomes the metronome for the controlled windups. The
  Armatures draw back on the tick; the creaks and hums align. The player can use the tick to time a dodge, a
  shot or a retreat. It is not a sting; it is a countdown the player can hear.
- **Surfaces.**
  - *Tile:* sharp, high, hard, with a short ring; the ceramic edge chirps; it carries across a room.
  - *Limestone:* duller, chalky, no ring; a compact tok with a gritty tail; it dies quickly, so the player
    hears the rhythm better than the direction.
  - *Water:* a wet tok and a small suck as the claw lifts; the sharp edge is gone, the splash carries further
    than the tick, and the rhythm smears. The Spindle sounds closer than it is, or farther; the player cannot
    place it.
  - *Concrete and rebar:* between tile and limestone; on rebar, a ceramic-on-metal ring that the Armature's
    own creak can mask.
- **Three layers.** Metal = Armature (creak, chink, wire tick); ceramic = Spindle (tick); glass = control
  (hum). The player can hear which layer is present before seeing anything.
- **The first time.** The tick must arrive before the Spindle is visible. The player has time to run, to kill
  the Spindle, or to prepare. If they ignore it, the cores light and the squad forms. The tick is the fair
  warning; the panic is what the player does with it.

### 8.3 The coordinated patterns

Controlled Armatures only. Free ones never do any of this.

- **Synchronised windup.** Two or three draw back on the same tick; the creaks and hums align into one sound.
  The player cannot interrupt all of them. Counter: break line of sight, use a pillar, or kill one core to
  break the timing.
- **Pincer (the flank).** One on each side, closing; the Spindle holds the centre. The player must break
  through one side, not back away. Counter: pick the weaker side (the heap host, 30 HP) and push through; do
  not get caught between.
- **Cut off the retreat.** One moves to the door or behind the player, not to attack but to block; it stands
  in the exit and waits. Counter: kill the blocker's core (the heap host collapses), or bait it to the tether
  limit and slip past; it cannot leave 12 m.
- **Converge on the light.** All controlled Armatures turn toward the player's beam; they walk to the light,
  not to the player. Counter: sweep the beam to draw them one way, kill the light, and move; they lose the
  fix. If the player holds the light, they are the centre of the room.

**Fairness.** Every pattern has a tell on the tick, a gap at the tether limit, and a weak side. The player can
always break it by killing the Spindle, shooting a core, or leaving the room. If a pattern has no gap, it is
not a panic spike; it is a kill box. Do not build a kill box.

**Damage note.** The panic is not bought with damage. `PILLARS.md` §3 says a rebar strike is nearly a
one-shot for a normal human; the 9/12 numbers in `ARMATURE.md` are the earlier "moderate" tier. Flagged in
`NOTES.md` §14. The coordination, not a damage spike, is what sells the panic; the strike's lethality is a
separate balance pass.

## 9. Spawn pairing: the Hollow and the Stone ReDead

`PILLARS.md` §5 makes this a generator constraint: the Hollow and the Stone ReDead **always** spawn
together. The
Hollow is tree-like and still until it moves; alone, the player just shoots the tree. The ReDead keeps the
player busy while the Hollow comes alive. The Hollow's sheet has not reached the PC; keep it vague — no
anatomy, no attack names, no origin.

**The ReDead, as established.** NR-077-D, ossuary resident, north gallery, alcove 44: gaunt humanoid;
cracked limestone mask over the upper face; dry sinew; slate cloth; long grasping hands. It remains in or
near alcove 44 unless disturbed; follows at a walk and reaches rather than runs; the grip is close and hard
to break; a stagger follows if it is made to release. When the mask is lifted it shrieks and prepares to
seize. It does not answer its shelf-name. The player is told: do not lift the mask; do not read the name
aloud.

**The pairing.** The ReDead is the hand; the Hollow is the clock. The ReDead walks the aisle and reaches; it
is slow, but the grip pins. The Hollow is the tree-like shape at the edge of the light — a column, a root, a
shrine — and it is still until it moves. The ReDead keeps the player's attention and the player's feet; the
Hollow moves when the player is held or looking away. The ReDead's shriek — if the mask is lifted — can
cover the Hollow's first movement.

**Sketch: the north gallery, alcove 44.** The player enters a dry gallery. The ReDead is in the aisle between
the player and the exit, walking and reaching. At the edge of the light, a tree-like shape stands among the
columns; it reads as furniture. The player's instinct is to shoot the tree; the ReDead is already close, and
the grip is the pin. If the player focuses on the ReDead, the tree moves. The counter: keep both in the
light, break the grip, use the ReDead's slow walk to create distance, and do not let it hold the player in
the Hollow's reach. The ReDead is the distraction; the Hollow is the threat. Do not put the Hollow between
the player and the only exit; the ReDead can hold the player there.

**Generator rules.** Always together; never the Hollow alone (the player shoots the tree); never the ReDead
alone in this pairing (a slow chase, not a panic spike). Place the ReDead near a shelf or alcove (its lore),
the Hollow at the edge of the light (its stillness). The room needs two exits or a breakable grip; the player
must be able to leave. The Hollow's first move is the tell; the ReDead's grip is the lock. Keep the Hollow
vague until its sheet arrives; do not design its attack here.

## 10. Name resolution

The clash: `ARMATURE.md` and this file use **THE ARMATURE** for the creature; `UNDERPRINT.md` (line 20) uses
"armature" for the Underprint's internal twine frame, and the sound cue `cr/paperedroom/armature` uses the
same word. The word is doing two jobs: a technical term for a frame, and a proper name for a creature.

**Recommendation: keep THE ARMATURE for the creature and rename the Underprint's term.** The creature name
is the stronger of the two, "armature" is the correct trade word for a rebar cage, and the rename is cheap:
one prose line and one cue. Alternatives for the Underprint's term, in order:

1. **Twine frame** — accurate (the Underprint's frame is twine and scrim), plain, and it reads as a thing,
   not a name. The cue becomes `cr/paperedroom/frame`. **Recommended.**
2. **Scrim frame** — accurate to the material, slightly more technical; the cue becomes
   `cr/paperedroom/scrim`.
3. **The frame** — the simplest; it loses the material specificity but is unambiguous in context.

If Josiah prefers to keep "armature" for the Underprint, the creature needs a new name. Alternatives, in
order:

1. **THE STANDER** — already the trade word in the record; short, human-scale, and it describes the one
   verb.
2. **THE CAGE** — good silhouette, but generic, and it collides with "rib cage" in the descriptions.
3. **THE BUNDLE** — material-first and cold, but it undersells the humanoid shape.

Keep **standing reinforcement** as the office's species name either way. The actor letter is **`R`**
(reinforcement) under either name; do not use `T`, which is already the turn role in the bank. Check `R`
against `package_grid.py` before baking.

## 11. Production cost (short)

- **Controlled Armature:** a skin (reddish glossy tendons, green core at the chest) plus a compact variant
  bank — dormant, walk, two-arm windup, two-arm slam, hit, collapse/revert — about 16–18 samples, not a full
  second bank. The core is a prop with a hitbox and an emissive material; the tendon is engine geometry
  (a segment chain or tube), like the Circuit's tether. The green light is a small dynamic light or an
  emissive plus a point light; budget one per controlled Armature, not per core shard.
- **Bone variant:** a skin plus bone attachments; reuse the free bank. The bone heap is a prop variant. No
  new actor.
- **Rebar/bone Spindle:** a skin plus the sheet's brace and LAUNCH poses; reuse the classic Spindle's bank
  where the poses match. The colony core in flight is a small prop with a trail; the tendon is the same
  engine geometry as the link.
- **Heap infection:** the heap prop needs an "infectable" flag and a rise animation, or the infection is
  authored at fixed heap markers. The second is cheaper and more controllable; the first is the emergent
  version. This is the largest new cost and it is flagged in `NOTES.md`.

## 12. What this file does not do

No image was opened (I cannot see the three sheets), and no model, rig, sprite, bake, map, engine, AI,
collision, audio or balance work was done. The numbers are prototype starting values. Open questions are in
`NOTES.md` §14; collisions and production costs are in §13.
