# THE RAVEL — the filter that hunts

**Status: PROPOSAL throughout.** Sheet 13. I have not seen the image; §1 is Claude's description, quoted.
Origin proposed **never human**: a filter-bed growth of sinew, amber fibre and fused glass grit. This is
the batch's projectile creature; the spray rules in §4.3 are the condition of approval.

## 1. What the description establishes

| Description detail | What it is |
| --- | --- |
| Quadruped of dark grey sinew | A lean, low animal: muscle without a hide. The sinew is the whole body, not an armature. |
| Wrapped in amber-orange fibre strands | The fibre is a wrap, a filter medium, a charge carrier. It is not fur and not flame. |
| Armoured with a crest of translucent, cracked glass-like shards | The crest is **caught grit**, fused and cracked: the filter's own sediment, worn as armour. |
| READY: low and stalking | It circles; it does not charge without the crest. |
| ACTION: the shards burst outward in a glowing amber explosion, flying off as projectiles | The crest is a **one-shot magazine**. It fires the shards and is left bare. |

The description gives three facts: **the crest is glass**, **the amber is a charge**, and **the burst
leaves it empty**. The encounter is built on the empty crest.

## 2. Institutional record

**NRRO INTAKE NR-198-A — FILTER (ACTIVE)**
- Subject no.: NR-198-A. Received ██.██.19██. Class: FILTER. Station: stratum 3, flooded cistern,
  settling basin, grit channel 3 and the filter beds; also the sludge margins and the pump-house outfall.
- Description: low quadruped, 1.4 m long, 0.9 m tall; dark grey sinew; amber-orange fibre strands wrapped
  around the body; crest of translucent, cracked glass-like shards along the spine, 0.7 m at full rise;
  no visible eyes; four feet with three forward toes; a short, wide jaw.
- Behaviour: stalks at 4–5 m, circles, and fires the crest in a fixed radial pattern. The crest rises and
  points before the burst; the amber fibre brightens from tail to crest; the burst leaves the crest bare
  and soft. The subject is spent for several seconds and uses the time to circle and re-ink the shards from
  the fibre. It does not fire at close range. It does not home. It does not fire through walls.
- Origin: the basin's filter media — resin, glass grit, fibre, and the sinew of things that grew in the
  filter and were not swept out. The filter is still running. UNRESOLVED.
- Notes: the shards are evidence. A shard in a wall is a Ravel mark; a shard in a cable is a severed
  Circuit tether. Do not sweep the channel alone. The grit survey has been reclassified as a blockage
  three times.
- Disposition: CONTAINED LOCALLY. Do not transport. Do not sweep.

## 3. Lore proposals

### 3.1 Origin (never human — proposal)

It grew in the filter bed. The basin's water carries resin, glass grit, fibre and sediment; the filter
catches them; something in the filter learned to **hold** the catch, and then to **aim** it. The amber
fibre is the charge the filter accumulated; the glass crest is the grit it could not pass. It is a body
made of the thing it was supposed to remove.

This gives it a place in the basin's ecology: it is **the filter's opinion**. The White Bloom filters the
water; the Ravel filters the grit and keeps it. The two are not enemies. They are two answers to the same
job, and one of them hunts.

### 3.2 What it wants (proposal)

To be charged. It stalks because movement builds the charge in the fibre; it fires because the crest cannot
hold more. The burst is not a hunting strategy; it is **the filter emptying itself**. It then has to
re-charge, which is why it circles rather than closes.

The office's word for the species is **grit**. The basin works has a grit survey, a grit channel and a
grit disposal procedure. The procedure is "do not sweep".

### 3.3 Strata and room tags (proposal)

**Primary: stratum 3, flooded cistern / settling basin.** Tags: `grit channel`, `filter bed`, `sludge
margin`, `pump-house outfall`, `settling tank`, `screen`. It is always near moving water and grit.

**Secondary: stratum 4, root cathedral (damp bays).** Tags: `damp bay`, `rubble slope`, `pipe crossing`.
It follows the grit down; it does not go into dry rooms.

**Absent from:** the transit (no grit, no charge), the ossuary (dry dust is not grit), the scriptorium
(no water). The dry strata are safe from it, and the player can learn that from the shards: they are only
in wet rooms.

### 3.4 Relationships

- **Vore Spindle** — the other basin projectile. The Spindle lobs **one** homing spore; the Ravel sprays a
  **fixed ring**. One is a pursuit, the other is a pattern. Never give the Ravel homing and never give the
  Spindle a ring; the two encounters must read differently at a glance.
- **White Bloom** — the other basin filter. The Bloom's spikes come from the floor; the Ravel's from the
  air. They share a room and ignore each other. The Bloom's wet floor is the Ravel's charge source; the
  Ravel will not leave it.
- **Unaddressed** — both amber and glass, and they must not blur. The Unaddressed's amber membranes are
  **sensory** (a fan that notices movement); the Ravel's amber fibre is **ordnance** (a charge that fires
  glass). The Unaddressed is in the cathedral; the Ravel is in the basin. Keep them apart.
- **Circuit** — a Ravel burst severs a Circuit tether. A severed tether with glass in the cut is a Ravel
  mark, not a Husk mark. The Circuit avoids the grit channels.
- **Pleat** — the Pleat's yellow fibre and the Ravel's amber fibre are both insulation-adjacent and must
  read differently: yellow is soft, matted, inert; amber is wet, glossy, charged.
- **Span** — the Span will not span wet ground; the Ravel makes wet ground no wetter. They do not meet.

## 4. Encounter design

### 4.1 Stat block (starting values)

| | |
| --- | --- |
| HP | **140**. Crest **60** (destroying it disables the burst); body 1.0×; spent crest/back **1.5×**; sinew 1.0×; feet 0.75×. |
| Size | 1.4 m long, 0.9 m tall; crest 0.7 m; burst radius 7 m |
| Speed | stalk 180 u/s; charge 300; flee 380; spent limp 120 |
| Attacks | shard burst: **8 shards, 7 damage each, 7 m, 4 gaps** in the ring; bite 9 (1.2 m); no melee combo |
| Fairness caps | 1.5 s telegraph; **minimum range 1.5 m** (it cannot fire at its feet); at most one burst per 3.5 s; fixed 8-shard ring with 4 gaps; no homing; no fire through walls; no burst while the crest is below 20 HP |

### 4.2 Behaviour

| State | Ticks | What it does | What it means |
| --- | --- | --- | --- |
| STALK (idle loop) | 4 × 8 = 32 | Low circling at 4–5 m, head low, crest shards clicking; the amber fibre pulses with a slow glow, tail to crest. | The charge is building. The glow is the meter. |
| NOTICE | 3 × 6 = 18 | The head stops; the crest shards rise and align; the fibre brightens. | It has chosen a firing line. |
| CHARGE | 4 × 13 = 52 | The shards lift off the crest and point outward; the amber goes white at the tips; all four feet plant. | **The telegraph.** 1.5 s to cover. |
| BURST | 3 × 4 = 12 | The crest snaps outward; eight shards fly in a ring; an amber flash; the crest deflates. | The attack. The gaps are fixed; the ring is readable. |
| SPENT | 3 × 7 = 21 | The crest is bare and soft; the fibre dulls; it circles away. | The damage window. 1.5× on the back. |
| RECOVER | 3 × 7 = 21 | It stops, lowers its head, and the fibre re-inks the shards from the base up. | It cannot burst until the crest is half-grown (2.5 s). |
| WALK | 4 × 6 = 24 | A low, fast trot; the crest folded back. | Repositioning. |
| BITE | 3 × 5 = 15 | A short lunge and a wide bite; no combo. | Close-range answer if you hug it. |
| HURT | 2 × 4 = 8 | A whole-body flinch; the crest rattles. | — |
| DEATH | 4 × 7 = 28 | The crest falls shard by shard; the fibre goes dark; the body folds. | The shards are lootable. |
| CORPSE | 1 | A grey sinew shape, a scatter of dull glass, a fading amber thread. | — |
| DOCILE | 4 × 8 = 32 | Follows at 2 m, crest folded, fibre glowing steadily; does not fire. | The lured state (4.5). |

The sheet's named poses map as: `ready` = STALK, `action` = BURST. CHARGE and SPENT are the two states the
encounter is built on.

### 4.3 The telegraph and the spray contract

**The shards rise and point.** Before every burst: the crest shards lift off the spine and align outward,
the amber fibre brightens from tail to crest, the tips go white, the feet plant, and a rising glass note
sounds. The telegraph is **1.5 s**; the burst is 12 ticks. The ring is **fixed**:

- 8 shards and 4 gaps at 30° spacing (12 slots), with the gaps at the cardinal points (0°, 90°, 180°, 270°). The gaps are
  always in the same places relative to the Ravel's facing. A player who reads the crest can stand in a
  gap; a player who runs perpendicular can outrun the ring.
- The shards travel 7 m at 420 u/s, are 0.25 m wide, and fade after 0.8 s. They do not home, bounce, pierce
  cover, or fire through walls. They embed in geometry with a glass impact decal and a brief amber light.
- **Minimum range 1.5 m.** Inside that, the crest cannot point; it bites instead. Hugging it is a real
  counter and the encounter's best punish.
- **One burst per 3.5 s.** The crest must be at least half-grown. The SPENT state is 21 ticks and the
  RECOVER is 21; a player who closes during CHARGE gets a full SPENT window.
- **No burst at below 20 crest HP.** Breaking the crest (60 HP) disables the burst permanently for that
  Ravel; it flees or fights with the bite. This is the non-lethal-adjacent route: a disarmed Ravel is a
  different animal.
- **Accessibility:** the amber flash is brief but bright. Cap the flash at <3 Hz, keep it under 0.2 s, and
  provide a reduced-flash option. The ring is the attack; the flash is not the information.

### 4.4 Counterplay

- **Close inside 1.5 m during CHARGE.** It cannot fire; it bites for 9. The charge is the safest time to
  close.
- **Read the gaps.** The four cardinal gaps are visible in the crest's alignment. Stand in one, or move
  perpendicular to the facing.
- **Use cover.** The shards stop at geometry. A pipe, a slab, a tank rim is a wall.
- **Punish SPENT.** 1.5× on the bare back for 21 ticks, then RECOVER for 21 more.
- **Break the crest.** 60 HP and the burst is gone. It is the cleanest disable in the batch and the one
  that makes the Ravel a resource rather than a threat.
- **Do not chase it into the water.** It is faster in the shallows; the player is not.

### 4.5 Non-lethal / puzzle route — THE LIVING KEY

The Ravel is a filter that keeps what it catches, and the basin has four uses for that:

1. **Lure it with resin.** A resin nodule, an amber lump, or a fuel can's residue can be offered at 2 m.
   The Ravel becomes DOCILE, follows at 2 m, and its fibre glows steadily — a walking lamp in the basin's
   dark. It does not fire while docile. It can be led to a grate, a hatch or a locked filter housing and
   left there; it will settle and charge on the grit behind the grate. This is the "borrow the monster"
   route and the most useful.
2. **Provoke it at a barrier.** A glass partition, a salt crust, a rusted grate, a stuck valve. Stand on
   the far side of the barrier and let it fire; the shards break the barrier. The Ravel is unharmed and
   the barrier is open. The player must be in a gap or behind cover. This is the puzzle version: the
   creature is a key, not a fight.
3. **Harvest the shards.** After a burst, the embedded shards cool into a dull glass grit that can be
   collected. The grit is an abrasive, a lens, a lockpick, or a trade item. The Ravel does not care; it
   re-inks new ones. A player who follows a Ravel through the basin can collect a trail of shards.
4. **Break the crest and leave.** A disarmed Ravel is a 140 HP animal with a 9-damage bite and no ranged
   attack. It flees to the water. Killing it is optional; the shards are the reward either way.

The fight is the default only if the player meets it in the open with no cover and no resin. The room
should offer at least one of the four.

### 4.6 What it does not do (deliberate limits)

No homing shards, no random 360° coverage without gaps, no firing through walls, no burst at close range,
no infinite crest, no climbing, no invisibility, no splitting, no infection. It is a filter animal with a
magazine. It is not a boss and should not be scaled to one without a new crest mechanic.

## 5. Sound cues (in words)

- **Idle:** a low, wet purr; glass shards clicking against each other as it walks; the fibre's papery
  rustle; water dripping off the body.
- **Notice:** the clicking stops. One shard rings like a struck wine glass.
- **Charge:** a rising glass-harmonica note, thin and clear; the fibre crackles like static in cloth; the
  feet plant with a wet thump.
- **Burst:** a single hard crack, then eight small whistles; glass tinkling into water; the crest deflating
  like a paper bag.
- **Spent:** the fibre hisses as it dulls; the body pants; the shards rattle loosely.
- **Recover:** a soft, repeating tick as the fibre re-inks the crest, like a clock winding.
- **Bite:** a wet snap, no growl.
- **Death:** the crest falls shard by shard, each one a different note; the fibre goes out with a sigh.
- **Docile:** the purr slows to a hum; the glow steadies; the shards fold flat.

## 6. Sprite roles (3D artist)

One actor, one bank, pivot at the body centre. The burst is engine-side; the sprite must not bake the
shards flying. Pose extent ~1.5 m (crest and forelimbs): **3.2 m span at 768 px = 240 px/m; body 1.4 m ≈
336 px**; pivot z = 0.55 m. The crest needs its own small mesh or a separate sprite layer if the shards
are to be animated individually; the recommendation is an 8-shard engine-side projectile set and a crest
that changes silhouette (full → pointing → bare).

| Role | Name | Samples × ticks | Notes |
| --- | --- | --- | --- |
| I | stalk / idle | 4 × 8 | Low circle; the fibre glow is a material/emissive animation, not frames. |
| N | notice | 3 × 6 | Head stop; shards rise. |
| C | charge | 4 × 13 | Shards point outward; feet plant; the key telegraph. |
| B | burst | 3 × 4 | Crest snaps; body recoils; the shards are engine-side. |
| S | spent | 3 × 7 | Bare crest; soft back; the damage window. |
| R | recover | 3 × 7 | Re-inking; shards growing from the base. |
| W | walk / trot | 4 × 6 | Crest folded back. |
| T | bite | 3 × 5 | Short lunge, wide jaw. |
| H | hurt | 2 × 4 | Flinch, crest rattle. |
| D | death | 4 × 7 | Crest falls shard by shard. |
| X | corpse | 1 | Grey shape, dull glass, one amber thread. |
| F | docile / follow | 4 × 8 | Crest folded; steady glow; no fire. |

**Total: 38 samples, 1,520 PNGs.** First-proof gate: I 2, C 2, B 2, S 2, R 1, D 2, X 1 = 12 samples. The
CHARGE and SPENT silhouettes are the encounter; if they do not read at 8 m, the fight is unfair.

## 7. Found text

> **GRIT SURVEY, CHANNEL 3.** Sample: glass, amber, sinew. The sample moved. Reclassified as a channel
> blockage. Do not sweep. The blockage has been observed to sweep back. *(Pencil, same hand:)* The survey
> team is now a survey team of one. The one has been issued a second clipboard and no second surveyor.
