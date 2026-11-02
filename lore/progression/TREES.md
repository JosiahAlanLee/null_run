# TREES — UPGRADE (the office's way) and MUTATION (the building's way)

**Status: PROPOSAL.** Text only. Numbers are prototype starting values. All node costs are in Integrity
points (pool of 20) — see `BODY-BUDGET.md`. Stations are physical places; nothing is bought from a menu.

The opposition in one line: **the office replaces what you were; the building grows over it.** Both are
ways of paying for the descent, and both take from the same body.

## 1. Common rules

- Every node costs **2 Integrity** (10 nodes maximum) and occupies **one body slot** (12 slots; the table
  in §4). Each slot is a choice between the institutional node and the growth.
- **UPGRADE — the workbench.** A steel bench with a vice and a spares tray, stencilled `WORKS ONLY`, in
  service rooms (stratum 0 service corridors, stratum 1 works store, stratum 3 pump rooms, stratum 4 grown
  bays). Install: lay the materials on the bench (they rest there — physicality), then **8 s of working on
  yourself** — spanner, vice, swarf, small slow sparks (no strobe). The bench needs the room's light on.
  Install noise wakes packs within **12 m**. Effect is immediate. Costs: materials + pain + weight + noise/
  heat.
- **MUTATION — the nursery tray / spore bed.** A shallow tray of fibrous medium, per environment sheet E2
  (the drying nursery; also the basin edge and the cathedral's grown bays). Grow: kneel and bed the
  materials (**4 s**), then the node **roots over the rest of the stratum** and matures at the next landing
  — the cue is a slow ache and a smell, never a flash (photosensitivity-safe). While rooting, the growth is
  visible on the chosen slot. Costs: materials + drift + oddities. No weight. Damp rooms speed rooting by
  one room; the dry transit halves Woven Repair's rate.
- **Maintenance.** After each stratum, **one upgrade degrades** (effect −1/3) unless you pay spares (any
  one mechanical material) at a bench. Mutations need no upkeep; they need the damp instead.
- **Weapon mods** are bench crafts, slotted into one weapon each (one mod per weapon), adding weapon
  weight, lost with the weapon. They are not body nodes.

## 2. The taxes (three small meters, run-scoped)

| Meter | Scale | Gained by | What it does |
| --- | --- | --- | --- |
| **PAIN** | 0–8 | +1 per upgrade node; +1 temporary after each overdrive (until stratum end) | 4+: resting tremor (slight idle sway). 7+: desaturation below 50% HP; weapon raise +10%. Chosen, never removed mid-run (PILLARS §2, §4). |
| **NOISE** | 0–5 | upgrades and carried load; Quiet Soles subtracts while walking | Armature wake radius 8 m +1 m per point. The panic game is auditory; noise is a real tax. |
| **HEAT** | 0–5 | boiler plate, capacitor forearms, weapon mods; Coolant Sheath subtracts | Each point: sprinting > 4 s hisses (audible 10 m). 3+: you show as vapour in cold rooms. 5: overdrive ends with a stagger. |

**DRIFT** (mutations only) is not a tax meter; it is the other half of the body budget and lives in
`BODY-BUDGET.md` with its thresholds.

## 3. UPGRADE tree — twelve nodes, then the final

| # | Slot | Node | Effect (starting values) | Materials | Weight | Taxes |
| --- | --- | --- | --- | --- | --- | --- |
| U1 | SPINE | **Load Frame** | carry thresholds +16 kg | 4 rebar, 2 tie wire, 1 valve, 1 cable | +3 kg | pain +1, noise +1 (it creaks under load) |
| U2 | HANDS | **Wrist Tensioners** | Fathom Hook damage +25%, hook return 20% faster | 1 brass, 1 cable, 1 tie wire | +1.5 kg | pain +1 (the hands ache; at low HP the tremble shows) |
| U3 | TORSO | **Boiler-Plate Cladding** | −3 from BLUNT hits (flat, after armour) | 3 bronze plate, or 4 limestone; 2 tie wire | +8 kg | pain +1, heat +1 |
| U4 | LEGS | **Servo Knees** | step height 0.3 → 0.6 m; run 320 → 346 u/s | 2 valve, 3 cable, 1 brass | +5 kg | noise +1 (whine); sprint > 4 s costs pain |
| U5 | FOREARMS | **Capacitor Forearms** | overdrive lasts 3 s longer; Aethometer/Hymnodyne recharge 15% faster | 2 porcelain insulator, 3 cable, 1 lamp cell | +2 kg | heat +1, pain +1; the Ballast Husk arcs toward you from 2 m further (you read as a conductor) |
| U6 | HEAD | **Shoulder Lamp** | hands-free light while both hands hold a gun | 1 porcelain, 1 brass, 1 lamp cell | +1.5 kg | Armatures notice your light at 14 m instead of 12; fog blooms around the lamp |
| U7 | FEET | **Hydraulic Lock** | hold Use to plant: immune to stagger and knockback, melee +25% while planted, 3 s to unplant | 1 valve, 2 cable, 1 bronze plate | +4 kg | noise +2 during plant, pain +1 |
| U8 | SKIN | **Coolant Sheath** | heat −2; resonance weapons overheat 50% slower | 2 cable, 2 valve, 1 gauge brass | +2 kg | none (the rare free node) — but it needs the coat; it pipes under it |
| U9 | EARS | **Acoustic Attenuators** | Choraz pressure and Hymnodyne self-stagger halved | 2 felt wadding, 1 tube glass, 1 brass | +0.5 kg | **tell range −15%** (you hear the creak later — a real trade against the panic game) |
| U10 | EYES | **Beam-Proof Visor** | standing lamps and your own muzzle flash do not dazzle | 1 tube glass, 1 brass, 1 tie wire | +0.6 kg | fog and darkness fall 10% harder (the visor scatters) |
| U11 | GUT | **Belt Feed** | reloads 25% faster, one-handed | 2 cable, 1 brass | +2 kg | noise +1 (the belt clatters when you run) |
| U12 | VOICE | **Annunciator Relay** | shout (a Use key): inhabitants within a room turn toward the sound for 2 s | 1 bronze plate, 1 cable, 1 valve | +1 kg | Choraz now answers you (a proclamation follows you); Repetiel brings you one message per stratum |
| **UF** | — | **THE WORKS BODY** | requires 6 upgrades. See BODY-BUDGET §5. | the bench accepts it after the sixth node | — | — |

**Weapon mods (bench crafts, no body slot):**

| Mod | Weapon | Effect | Materials | Weight |
| --- | --- | --- | --- | --- |
| Counterweight | Comptroller | aim drift while firing −30% | 1 brass, 1 tie wire | +0.8 kg |
| Grip-Plate | Registrar | draw and aim −20% | 1 limestone, 1 tie wire | +0.4 kg |
| Heel-Plate | Transit-12 | recoil settle −25% | 1 rebar, 2 tie wire | +0.6 kg |
| Sight-Collar | Plumb Bombard | projectile drop −40% | 1 brass, 1 valve | +0.5 kg |
| Key-Bed Shim | Hymnodyne | discharge 15% faster; weapon heat +1 (hiss on the 3rd consecutive shot) | 1 bronze plate, 1 porcelain | +0.5 kg |
| Insulator Neck | Aethometer | every 4th cell is free | 2 porcelain, 1 cable | +0.4 kg |

## 4. MUTATION tree — twelve nodes, then the final

| # | Slot | Node | Effect (starting values) | Materials (bedded) | Drift |
| --- | --- | --- | --- | --- | --- |
| M1 | FEET | **Quiet Soles** | footsteps −40%, heap-clatter −40% (you stop waking packs by walking) | 2 basin residue, 1 Hollow fibre | 1 |
| M2 | EARS | **Tympanic Filaments** | hear the Spindle's tick 0.5 s earlier and 10 m further; hear a windup creak through one wall | 1 tendon, 1 chitin plate | 1 |
| M3 | EYES | **Fog Eyelids** | see 30% further through fog; darkness falls 10% less | 1 photoform emulsion, 1 spindle membrane | 1 |
| M4 | SKIN | **Woven Repair** | stand still 3 s → regenerate 1 HP per 2 s, up to 60 HP; the repair weeps pale resin and leaves a glistening patch (spores settle on it; a Spindle in the room drifts toward it) | 2 root growth, 1 Hollow fibre | 1 |
| M5 | GUT | **Basin Respiration** | breathe water 12 s; spore and fog damage −50% | 2 basin residue, 1 membrane | 1 |
| M6 | TORSO | **The Colony's Rhythm** | never-human organisms hesitate 1.5 s on first sight of you; dormant Armatures ignore your footsteps (light and weapons still wake them) | 1 colony glass, 2 root growth | 2 |
| M7 | HEAD | **Crest Filaments** | sense colony cores through thin cover within 10 m (a green glint outline; never through anything thicker than a door) | 1 colony glass, 1 chitin plate | 1 |
| M8 | HANDS | **Grip Fibres** | weapon raise 20% steadier (sway down); long-hold tremble halved; grown ladders and ledges never slip | 1 tendon, 1 Hollow fibre | 1 |
| M9 | SPINE | **Drift Marrow** | limb-injury penalties halve; bone Armatures no longer include you in load tests (you read as shelved material) | 2 bone, 1 basin residue | 2 |
| M10 | VOICE | **Root-Tongue** | one wrong reply per scripted exchange is forgiven and re-demonstrated; roots mark your map one room ahead | 1 louvre glass, 1 root growth | 2 |
| M11 | FOREARMS | **Tendon Lacing** | hook swings 15% faster; you can grip a ledge for 3 s | 2 tendon, 1 Hollow fibre | 1 |
| M12 | LEGS | **Splay Growth** | crouch 30% faster; crouch-walk 15% faster and silent | 1 root growth, 1 chitin plate | 1 |
| **MF** | — | **THE DRIFT** | requires 6 mutations. See BODY-BUDGET §5. | the bed accepts it after the sixth node | — |

**The oddities (photosensitivity-safe — every one is a slow cue, a false sound, or a low-frequency glint,**
**never a flash, strobe or jump; PILLARS §5):**

| Node | The oddity |
| --- | --- |
| Quiet Soles | you feel the floor's seams; stepping off the level line feels wrong (a soft wrongness cue) |
| Tympanic Filaments | the hour chimes for you when none sounds — low, far, rare |
| Fog Eyelids | in the cistern, the water line seems to rise slowly while you stare (cosmetic; no gameplay change) |
| Woven Repair | the first regen of each stratum itches like a wrong heartbeat (painless) |
| Basin Respiration | on dry floors you wheeze (noise +1) until you stand in damp for 3 s |
| Colony's Rhythm | office machines hesitate too: turnstiles take 1 s, doors need a second push; you hum the two keys, faintly, when idle |
| Crest Filaments | the glints pulse at your pulse rate |
| Grip Fibres | fibre prints on everything you touch; doors you touched stay slightly warm; the file notes "unidentified growth" |
| Drift Marrow | in the ossuary the alcoves feel like yours; the ReDead follows at a distance and does not attack |
| Root-Tongue | you answer before you think; the first time, your voice sounds like the room's |
| Tendon Lacing | your forearm twitches toward colony cores within 10 m (a pull, not a light) |
| Splay Growth | your knees bend a little further each stratum (cosmetic) |

## 5. The slot opposition (read this as the design's spine)

| Slot | UPGRADE (the office) | MUTATION (the building) |
| --- | --- | --- |
| SPINE | Load Frame — carry more | Drift Marrow — injure less |
| HANDS | Wrist Tensioners — hit harder | Grip Fibres — hold steadier |
| TORSO | Boiler-Plate — take the blow | Colony's Rhythm — not be attacked at all |
| LEGS | Servo Knees — move faster | Splay Growth — move quieter |
| FOREARMS | Capacitor Forearms — more power | Tendon Lacing — more grip and swing |
| HEAD | Shoulder Lamp — make light | Crest Filaments — see the green |
| FEET | Hydraulic Lock — stand and take it | Quiet Soles — not be heard |
| SKIN | Coolant Sheath — shed heat | Woven Repair — regrow |
| EARS | Attenuators — resist noise, hear less | Tympanic Filaments — hear everything earlier |
| EYES | Visor — no dazzle, less sight in fog | Fog Eyelids — see through the fog |
| GUT | Belt Feed — feed the gun faster | Basin Respiration — breathe the water |
| VOICE | Annunciator Relay — command attention | Root-Tongue — be answered |

Every slot is a fork between solving the problem with iron or with growth. The same panic spike is met two
ways: the upgrade player installs Attenuators and Hydraulic Lock and plants; the mutation player grows
Tympanic Filaments and Quiet Soles and is already gone. Both are valid; neither is both.
