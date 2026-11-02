# ROOMS — acoustic profiles per stratum and room type

**Status: PROPOSAL.** Values are targets for tuning, not shipped constants. Unit notes come first; the
strata follow in descent order; a master table and implementation notes close the file. Companion rules
live in MIX.md (tell audibility, tail discipline) and SFX-LIST.md (which sounds exist and how wet they
are rendered).

## 1. The acoustic idea of the descent

The descent is a dive into a wetter, older, more resonant building. Light falls as you descend
(stratum 0 fluorescent, stratum 4 near-dark); **reverb rises**: each stratum adds water, hard shell or
void to the room's answer, until the root cathedral is a breathing ribcage and the settling basin is an
indoor horizon that barely answers at all. Two rules run through every profile:

1. **Water damps the lows.** Standing water, mud and sludge couple low-frequency energy into the water
   body instead of returning it: the low tail is short everywhere below the level line. What the
   player hears in the cistern is the *bright* tail — glazed porcelain keeps 1–8 kHz ringing while the
   floor swallows the bottom. (This is the cistern's signature and the reason its DecayHF ratio is >1.)
2. **Hard shells flutter.** Parallel hard walls (tiled cistern halls, painted transit corridors, lift
   shafts) give discrete slap echoes — EAX's EchoTime/EchoDepth — on top of the diffuse tail. The
   flutter is a location cue: you can hear the room's width. Irregular rooms (grown cathedral, dusted
   ossuary alcoves) diffuse instead of fluttering.

The descent is also a story in **room feel**: transit is dry and close (you are processed), the ossuary
is dry and old (the dryness is the point — "stone that stays dry keeps the name legible"), the
scriptorium rings like a bell that is reading you, the cistern answers everything twice, the basin
swallows sound, and the cathedral leans in.

## 2. Vocabulary and units

The brief's parameter set maps onto the ZDoom/UZDoom REVERBS lump and OpenAL-soft EFX like this:

| Brief term | REVERBS lump name | EFX name | Meaning | Units / range |
|---|---|---|---|---|
| decay time | `DecayTime` | `DecayTime` | late-reverb decay time (RT60-ish) | seconds |
| HF ratio | `DecayHFRatio` | `DecayHFRatio` | decay-time multiplier above `HFReference` | ratio; <1 dark, 1 flat, >1 bright |
| reflections level | `Reflections` | `ReflectionsGain` | early-reflection gain | **mB** (millibels); 100 mB = 1 dB, 0 mB = unity |
| reflections delay | `ReflectionsDelay` | `ReflectionsDelay` | first reflection delay | seconds |
| reverb level | `Reverb` | `LateReverbGain` | late-field gain | mB |
| reverb delay | `ReverbDelay` | `LateReverbDelay` | late-field onset | seconds |
| diffusion | `EnvironmentDiffusion` | `Diffusion` | echo-density of the tail (high = smooth wash, low = discrete echoes) | 0–100 % |
| density | `EnvironmentSize` | (`Density`, derived) | room size; large size = packed tail. EFX Density is derived by the backend from size; small rooms read as sparse | metres (this file gives both: size in m, density %) |
| room / roomHF | `Room`, `RoomHF` (from the base EAX preset) | `Gain`, `GainHF` | overall wet gain and its HF shelf | mB |

Also used, where a room needs them: `DecayLFRatio` (where the fork's lump supports EAX3 fields — the
"water damps the lows" mechanism), `EchoTime`/`EchoDepth` (flutter between parallel walls),
`AirAbsorptionHF` (mB per metre at HFReference; humid rooms), `ModulationTime`/`ModulationDepth`
(the cathedral "breathes"), and `DecayHFLimit` — which must be **TRUE** for the cistern and
scriptorium, otherwise the backend clamps the HF tail to the LF tail and the bright rooms go grey.

Defaults assumed: `HFReference` 5000 Hz, 20 °C-ish air. **100 mB = 1 dB** everywhere in this file.

## 3. Global rules (all strata)

- **Zones sit at doors.** Every profile boundary should be authored inside a doorframe, so the acoustic
  change is masked by the door sound. Never put a seam in the middle of a combat room (MIX.md,
  "two-room fight" rule).
- **Reverb placement:** one reverb thing per room, radius = room extent, overlapping neighbours by
  1–2 m. The engine blends zones by the listener's position; if this fork snaps instead of blending,
  keep seams at doors only and script a 0.3 s crossfade. (Verify against the fork — see §6.)
- **Underwater / wade variant.** While the camera is in water, crossfade to the shared wet profile:
  Decay 0.9 s, DecayHFRatio 0.12, Reflections −400 mB / 0.006 s, Reverb +400 mB / 0.010 s,
  Diffusion 20 %, EnvSize 1.8 m, Room −1000, RoomHF −800. Near-instant, dark, smeared — the classic
  underwater read. Only while the head is in water; wading with the head out uses the room's own profile.
- **The boss arena is neutral ground.** One shared profile (Decay 2.0 s, HF 0.7, Refl −900 mB /
  0.012 s, Rev −550 mB / 0.020 s, Diff 80 %, EnvSize 16 m, Room −1000, RoomHF −250) so boss tells
  read identically on every floor. Fairness over flavour.
- **Send discipline** (details in SFX-LIST.md): gameplay sounds are rendered dry and the zone wets
  them; tells and key cues carry baked early reflections, never baked tails over 0.4 s; only decor and
  deaths get long tails.

## 4. The strata

### 4.0 Stratum 0 — Institutional Transit ("the top station")

Materials: painted concrete, lino tile, acoustic ceiling panels in offices, glass, steel, dark
institutional wood benches, rubber door seals. Light 195–235. The driest, closest stratum on purpose:
everything below it sounds wetter because this one sounds dry.

| Room type | Volume | Decay s | HF ratio | Refl mB / delay | Reverb mB / delay | Diff % | Size m (density %) | Room / RoomHF mB | Flutter EchoTime / Depth |
|---|---|---|---|---|---|---|---|---|---|
| **Bay** (waiting bay, platform bay) | 150–600 m³ | 1.0 | 0.75 | −1500 / 0.008 | −1200 / 0.014 | 70 | 6 (60) | −1000 / −200 | 0.045 / 0.25 |
| **Corridor** (service corridor, riser) | 20–150 m³ | 0.7 | 0.60 | −1200 / 0.005 | −1500 / 0.011 | 60 | 3 (40) | −1000 / −400 | 0.035 / 0.30 |
| **Shaft** (lift shaft) | 50–500 m³ | 2.2 | 0.50 | −900 / 0.010 | −700 / 0.025 | 50 | 8 (70) | −1000 / −600 | 0.160 / 0.55 |

- **Bay — reason:** benches, lino and ceiling tile eat the highs; glass and lino keep the first
  reflection tight (8 ms). Small volume, fast decay, subtle slap between the facing walls.
  **Feel:** held close and overheard; the room is dry because you are *waiting*, and waiting is dry.
- **Corridor — reason:** parallel painted walls give a fast close slapback (EchoTime 0.035 s ≈ 6 m
  width); acoustic tile and rubber seals pull the tail down hard. **Feel:** compressed; you are being
  routed, and your footsteps are countable.
- **Shaft — reason:** hard parallel walls over a long vertical extent: the flutter is long (0.16 s ≈
  27 m), the late field starts late, and energy escapes past the floor openings, so the reverb level
  stays moderate. **Feel:** vertigo; the building's throat.

### 4.1 Stratum 1 — Limestone Ossuary ("the dry galleries")

Materials: cut limestone, dusted shelf stone, slate, dry mortar. Light 115–165. The shelf lattice and
the dust are the acoustics: hard enough to ring, dusty enough to stay dark and old.

| Room type | Volume | Decay s | HF ratio | Refl mB / delay | Reverb mB / delay | Diff % | Size m (density %) | Room / RoomHF mB | Flutter EchoTime / Depth |
|---|---|---|---|---|---|---|---|---|---|
| **Bay** (gallery, alcove row) | 300–1000 m³ | 2.1 | 0.55 | −900 / 0.010 | −450 / 0.018 | 85 | 13 (90) | −1000 / −300 | 0.070 / 0.30 |
| **Corridor** (shelf corridor) | 30–120 m³ | 1.4 | 0.50 | −1100 / 0.007 | −800 / 0.014 | 75 | 5 (60) | −1000 / −500 | 0.060 / 0.30 |
| **Vault** (chapel vault) | 600–2000 m³ | 2.9 | 0.45 | −800 / 0.014 | −400 / 0.024 | 80 | 20 (95) | −1000 / −450 | — |
| **Shaft** (dry chasm) | open | 3.2 | 0.35 | −700 / 0.020 | −1400 / 0.045 | 40 | 35 (50) | −1000 / −700 | — |

- **Bay — reason:** limestone keeps a long tail, but the shelf dust and the alcove lattice diffuse the
  highs away (HF 0.55) and scatter early energy (diffusion 85 — the shelves are a diffuser wall).
  **Feel:** watched by shelves; dry and old. The dryness *is* the atmosphere.
- **Corridor — reason:** a narrow dusty stone slot; flutter between the shelf walls, highs dulled by
  dust. **Feel:** close; someone was just ahead of you.
- **Vault — reason:** the ossuary's one singing room — a real dry vault, long dark tail, no water
  brightness anywhere. **Feel:** small-sacred; the chapel remembers hymns.
- **Shaft (dry chasm) — reason:** the floor is gone; energy falls into the void and what returns is
  late, sparse and dark (reverb level −1400 mB despite the long decay). The Span's clack is the only
  landmark in it. **Feel:** the building is missing a piece.

### 4.2 Stratum 2 — Bronze Scriptorium ("the bronze margins")

Materials: bronze lattice and inscription channels, overstruck bronze plates, paper, wooden desks, and
— at the current water level — water over the desks. Light 135–180. Bronze is the acoustic: it rings,
and the overstruck plates are literal bells.

| Room type | Volume | Decay s | HF ratio | Refl mB / delay | Reverb mB / delay | Diff % | Size m (density %) | Room / RoomHF mB | Flutter EchoTime / Depth |
|---|---|---|---|---|---|---|---|---|---|
| **Bay** (reading floor, wet) | 500–2000 m³ | 2.5 | 0.95 | −700 / 0.009 | −550 / 0.017 | 90 | 15 (95) | −1000 / −100 | 0.070 / 0.30 |
| **Corridor** (stacks) | 40–150 m³ | 1.6 | 0.80 | −900 / 0.007 | −700 / 0.014 | 85 | 6 (70) | −1000 / −250 | — |
| **Vault** (bronze vault) | 800–3000 m³ | 3.3 | 1.10 | −650 / 0.013 | −500 / 0.022 | 80 | 24 (100) | −1000 / 0 | 0.090 / 0.40 |

- **Bay — reason:** the bronze lattice keeps the HF tail alive (0.95, nearly bright); the wet floor
  adds a strong early floor reflection and damps the lows (half-drowned: short low tail); paper and
  the dense overstruck plates diffuse. Set `DecayHFLimit` TRUE. **Feel:** overheard by the record;
  everything you do here is filed.
- **Corridor — reason:** paper eats the edges; the stacks are the softest rooms above the cistern.
  **Feel:** muffled, close; the paper is listening quietly.
- **Vault — reason:** the one room that rings brighter than the cistern (HF ratio 1.1): bronze is a
  resonator and the overstrikes are bells, so the tail shimmers slightly instead of smearing. RoomHF
  held at 0 so the shimmer survives. **Feel:** the margin is singing; the room reads you back.

### 4.3 Stratum 3 — Flooded Cistern ("the level line")

Materials: vaulted porcelain tile halls, brick cores, cast grates and pipes, gauges, standing water
with a level line, mud where the floor is open. Light 85–135. **This is the game's signature acoustic
and the combat-readability problem — see MIX.md §5.**

| Room type | Volume | Decay s | HF ratio | Refl mB / delay | Reverb mB / delay | Diff % | Size m (density %) | Room / RoomHF mB | Flutter EchoTime / Depth |
|---|---|---|---|---|---|---|---|---|---|
| **Vault** (tile hall, standing water) | 2000–8000 m³ | 4.2 | 1.20 | −800 / 0.014 | −400 / 0.028 | 95 | 30 (100) | −800 / −100 | 0.120 / 0.50 |
| **Bay** (tank bay, pump room) | 300–1500 m³ | 2.4 | 0.85 | −900 / 0.010 | −600 / 0.018 | 80 | 14 (90) | −1000 / −200 | 0.080 / 0.35 |
| **Corridor** (pipe gallery) | 20–200 m³ | 2.0 | 0.80 | −1000 / 0.006 | −700 / 0.013 | 70 | 7 (80) | −1000 / −300 | 0.050 / 0.45 |
| **Shaft** (drain / vent shaft) | 100–800 m³ | 3.0 | 0.60 | −800 / 0.012 | −600 / 0.030 | 60 | 10 (80) | −1000 / −500 | 0.140 / 0.50 |

- **Vault — reason, the flagship.** Parallel glazed tile walls 20–30 m apart: flutter at 0.12 s
  (2 × width ÷ 345 m/s) with real depth. Porcelain preserves the highs, so the tail is *bright*
  (HF ratio 1.2, `DecayHFLimit` TRUE, RoomHF held high at −100). Standing water and mud couple the
  low end into the water body instead of returning it — the low tail is damped (RoomLF −300, or
  DecayLFRatio ≈ 0.5 where the lump supports it; humid air takes a little of the extreme top,
  AirAbsorptionHF ≈ −10 mB/m). The late field starts at 28 ms, deliberately late, so attack transients
  stay clear inside the long tail. **Feel:** drowned cathedral. The room answers everything you do,
  twice, and returns it wet; a footstep here is a conversation. Combat here is the game's hardest
  mixing problem — solved by asset discipline, not by making the room dead (MIX.md).
- **Bay — reason:** pumps, pipe banks and brick cores break the flutter and eat the highs; the wet
  floor keeps the lows damped. The machines are louder than the reverb. **Feel:** a working room —
  the pump is the room's pulse, and the reverb is its breath.
- **Corridor — reason:** rows of cast pipes make a strong close slap (EchoTime 0.05 s); low ceiling,
  hard floor, fast reflections. **Feel:** squeezed between the pipes; something is always dripping
  behind you.
- **Shaft — reason:** long vertical flutter (0.14 s ≈ 24 m), late onset, highs dulled by the wet
  walls; energy escapes up and down, so the level stays moderate. **Feel:** the building inhales; up
  is as far as down.

### 4.4 Stratum 3b — Settling Basin ("the marsh")

Materials: open tank volumes, sludge flats, stained concrete walkways, algae-crusted brick, ochre
painted steel, scattered filter works. Light: sickly. The basin is a quasi-exterior: it barely answers,
and when it does it answers late.

| Room type | Volume | Decay s | HF ratio | Refl mB / delay | Reverb mB / delay | Diff % | Size m (density %) | Room / RoomHF mB | Flutter EchoTime / Depth |
|---|---|---|---|---|---|---|---|---|---|
| **Open basin** (sludge flats, filter beds) | 5000–20000 m³ | 2.2 | 0.40 | −600 / 0.040 | −1200 / 0.090 | 30 | 70 (100) | −1000 / −600 | 0.300 / 0.60 (one slap) |
| **Corridor** (walkway, screen) | 30–150 m³ | 1.3 | 0.50 | −1100 / 0.006 | −900 / 0.012 | 60 | 5 (60) | −1000 / −500 | 0.045 / 0.35 |

- **Open basin — reason:** the space is huge, so the tail is really two or three far discrete slaps
  off the tank walls (diffusion 30, first return at 40 ms, a single echo at 0.3 s) — the rest of the
  energy is gone into the sky of the room. Sludge and growth absorb both ends (HF 0.4, lows damped).
  **Feel:** agoraphobic indoors. The marsh swallows sound, and the far walls answer late. The Ravel's
  shards and the Bloom's spikes are the only things here that ring.
- **Corridor — reason:** metal walkway over wet: close, clangy, quickly dead; the wet is one slip
  away. **Feel:** precarious; keep to the grating.

### 4.5 Stratum 4 — Root Cathedral ("the grown layer")

Materials: cable-and-rebar roots grown through masonry, rib vaults that are ribs, moss, damp stone,
the still pool, occasional standing water in damp bays. Light 70–125. The room is irregular and alive:
maximum diffusion, no flutter, a slow breathing modulation, and a faint cable shimmer at the very top.

| Room type | Volume | Decay s | HF ratio | Refl mB / delay | Reverb mB / delay | Diff % | Size m (density %) | Room / RoomHF mB | Mod time / depth |
|---|---|---|---|---|---|---|---|---|---|
| **Bay** (grown bay) | 400–1500 m³ | 3.0 | 0.70 | −850 / 0.012 | −500 / 0.020 | 100 | 18 (100) | −1000 / −350 | 0.8 / 0.10 |
| **Vault** (rib vault) | 2000–6000 m³ | 4.4 | 0.65 | −750 / 0.016 | −450 / 0.026 | 100 | 42 (100) | −1000 / −450 | 0.8 / 0.12 |
| **Corridor** (root tunnel) | 20–150 m³ | 1.9 | 0.60 | −1000 / 0.008 | −650 / 0.015 | 85 | 8 (85) | −1000 / −500 | — |
| **Shaft** (the void, west void) | open | 4.0 | 0.40 | −600 / 0.022 | −1400 / 0.050 | 40 | 50 (50) | −1000 / −700 | — |
| **Open basin** (still pool chamber) | 1000–3000 m³ | 3.2 | 0.75 | −700 / 0.010 | −500 / 0.020 | 90 | 24 (100) | −1000 / −300 | — |

- **Bay — reason:** growth and moss eat the highs; the irregular ribs kill all flutter (diffusion
  100); the slow modulation (0.8 s cycle, depth 0.10) is the room breathing — audible only when the
  bed is quiet, and worth keeping subtle. **Feel:** inside something. The walls lean in when you are
  not looking.
- **Vault — reason:** the grown ceiling is a ribcage, not an arch: a long warm tail (4.4 s, HF 0.65),
  no flutter, and the cable tendons add a faint metallic shimmer at the very top — that is why RoomHF
  is kept at −450 rather than buried. **Feel:** the cathedral is breathing; you are inside the
  descent remembering itself.
- **Corridor — reason:** root tunnels are close and womblike; short decay, fast reflections, no
  flutter (the walls are never parallel for long). **Feel:** it closes behind you.
- **Shaft — reason:** near-open void: long, sparse, dark (reverb level −1400 mB); the Span's clacks
  are the only landmarks. **Feel:** the floor has been renegotiated.
- **Open basin (still pool) — reason:** the water surface gives a strong early floor reflection and
  damps the lows; the chamber is the Unaddressed's — keep the reverb *under* the plate taps (the
  puzzle is the voice; MIX.md tell rules). **Feel:** held breath; the still water is the room's ear.

## 5. Master reference table

| Zone | Decay s | HF | Refl mB / del | Reverb mB / del | Diff % | Size m | Room / RoomHF mB | Flutter |
|---|---|---|---|---|---|---|---|---|
| T0 bay | 1.0 | 0.75 | −1500 / 0.008 | −1200 / 0.014 | 70 | 6 | −1000 / −200 | 0.045 / 0.25 |
| T0 corridor | 0.7 | 0.60 | −1200 / 0.005 | −1500 / 0.011 | 60 | 3 | −1000 / −400 | 0.035 / 0.30 |
| T0 shaft | 2.2 | 0.50 | −900 / 0.010 | −700 / 0.025 | 50 | 8 | −1000 / −600 | 0.160 / 0.55 |
| O1 bay | 2.1 | 0.55 | −900 / 0.010 | −450 / 0.018 | 85 | 13 | −1000 / −300 | 0.070 / 0.30 |
| O1 corridor | 1.4 | 0.50 | −1100 / 0.007 | −800 / 0.014 | 75 | 5 | −1000 / −500 | 0.060 / 0.30 |
| O1 vault | 2.9 | 0.45 | −800 / 0.014 | −400 / 0.024 | 80 | 20 | −1000 / −450 | — |
| O1 chasm | 3.2 | 0.35 | −700 / 0.020 | −1400 / 0.045 | 40 | 35 | −1000 / −700 | — |
| S2 bay | 2.5 | 0.95 | −700 / 0.009 | −550 / 0.017 | 90 | 15 | −1000 / −100 | 0.070 / 0.30 |
| S2 corridor | 1.6 | 0.80 | −900 / 0.007 | −700 / 0.014 | 85 | 6 | −1000 / −250 | — |
| S2 vault | 3.3 | 1.10 | −650 / 0.013 | −500 / 0.022 | 80 | 24 | −1000 / 0 | 0.090 / 0.40 |
| C3 vault | 4.2 | 1.20 | −800 / 0.014 | −400 / 0.028 | 95 | 30 | −800 / −100 | 0.120 / 0.50 |
| C3 bay | 2.4 | 0.85 | −900 / 0.010 | −600 / 0.018 | 80 | 14 | −1000 / −200 | 0.080 / 0.35 |
| C3 corridor | 2.0 | 0.80 | −1000 / 0.006 | −700 / 0.013 | 70 | 7 | −1000 / −300 | 0.050 / 0.45 |
| C3 shaft | 3.0 | 0.60 | −800 / 0.012 | −600 / 0.030 | 60 | 10 | −1000 / −500 | 0.140 / 0.50 |
| B3 open basin | 2.2 | 0.40 | −600 / 0.040 | −1200 / 0.090 | 30 | 70 | −1000 / −600 | 0.300 / 0.60 |
| B3 corridor | 1.3 | 0.50 | −1100 / 0.006 | −900 / 0.012 | 60 | 5 | −1000 / −500 | 0.045 / 0.35 |
| R4 bay | 3.0 | 0.70 | −850 / 0.012 | −500 / 0.020 | 100 | 18 | −1000 / −350 | mod 0.8 / 0.10 |
| R4 vault | 4.4 | 0.65 | −750 / 0.016 | −450 / 0.026 | 100 | 42 | −1000 / −450 | mod 0.8 / 0.12 |
| R4 corridor | 1.9 | 0.60 | −1000 / 0.008 | −650 / 0.015 | 85 | 8 | −1000 / −500 | — |
| R4 void | 4.0 | 0.40 | −600 / 0.022 | −1400 / 0.050 | 40 | 50 | −1000 / −700 | — |
| R4 still pool | 3.2 | 0.75 | −700 / 0.010 | −500 / 0.020 | 90 | 24 | −1000 / −300 | — |
| Boss arena | 2.0 | 0.70 | −900 / 0.012 | −550 / 0.020 | 80 | 16 | −1000 / −250 | — |
| Underwater | 0.9 | 0.12 | −400 / 0.006 | +400 / 0.010 | 20 | 1.8 | −1000 / −800 | — |

## 6. Implementation notes

- **Lump shape.** The ZDoom-family REVERBS lump defines one environment per block: a name, the
  editor number used for the in-map reverb thing, a base EAX preset (from which Room/RoomHF derive),
  then parameter lines (DecayTime/DecayHFRatio/Reflections/ReflectionsDelay/Reverb/ReverbDelay;
  EchoTime/EchoDepth/ModulationTime/ModulationDepth/AirAbsorptionHF/HFReference;
  EnvironmentSize/EnvironmentDiffusion/DecayHFLimit where the fork supports EAX3 fields). **Verify
  the exact line order against this fork's reverb loader before authoring** — forks differ, and I
  could not read the engine source on this machine. The values above are the design targets; the
  lump is the syntax.
- **mB arithmetic.** 100 mB = 1 dB. The tables' Room values around −1000 mB (−10 dB) match the
  engine's built-in presets; the interesting numbers are the HF ratios, the reflection/reverb delay
  pairs, the flutter pairs and the RoomHF shelf.
- **`DecayHFLimit`.** Set TRUE for S2 vault, S2 bay and C3 vault (HF ratio > 1 must be allowed) or
  those rooms lose their bright tails and the cistern reads grey.
- **Tuning order.** Author the four C3 zones first (they are the brief's focus), then walk a fight
  through the C3 vault with a tell playing (MIX.md §5 checklist) before committing any other zone.
- **Zone radius vs room size.** The reverb thing's radius should reach the zone's doors, not the
  room's centre; overlapping radii at doors blend (or mask the snap) per §3.
