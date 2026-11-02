# NOTES — cistern chunk library (job 20261102-125236-deepseek-cistern-chunk-library)

Companion to `chunk_library.json` (32 templates) and `validate_library.py` (the
check that proves the geometry claims below; see `validation-run.txt`).
Everything here is a PROPOSAL for Claude Code and Josiah to review.

## 1. What is in the library

- **22 slice rooms** as templates, derived from `geometry_v5.py` / the v7 mapdata:
  the tidal hub, intake with its three stores plinths, east service corridor with the
  native service door, east stair, gallery, upper pipe run (the slice's W3 weir walk),
  pump inspection bay, west throat, sump, culvert, drain stair, pump landing,
  shortcut gate/foot/return stair/head, the two vestibules, optional ward, outfall
  exit gate and room, and the Hollow/ReDead pair bay.
- **1 harvested chunk**: the real Freedoom E2M5 cluster (sectors 87/137/139/140/141/
  142/350), footprint re-derived from the source UDMF union (18 vertices, two 8x8
  pillar holes become r5 pillars).
- **9 new templates** in the same vocabulary: V-07 valve hall, tidal lightwell,
  weir walk set piece, stores alcove (the Unopened Tin), dogleg duct, spiral
  stairwell, dry lift shaft, flume one-way drop, and the sealed basin stair.

Field names keep Argon's `ChunkTemplate` contract (`template_id, tags, size_xy_u,
headroom_u, light_level, material, pillars_local_xy_r, baffle_local_seg,
default_landmark`) and add `footprint_local_u`, `sockets`, `floor_z_u`,
`ceiling_z_u`, `light_band`, `mechanisms`, `encounter`, `rarity_weight` and
`landmark_text`. Conventions are stated in `meta`: UZDoom map coordinates (+y
south), socket normal 0=east(+x) / 90=south(+y) / 180=west / 270=north(-y),
socket width >= 128 u, step riser <= 24 u (slice risers are 8 u), headroom >= 60 u.

## 2. How the templates encode the Purgatorio terrace logic (PILLARS 4)

The cistern's terrace discipline is **maintenance and measurement**: the
inhabitants keep the records and the water keeps disagreeing with them, and nobody
notices the change. The templates carry that discipline as data, so a generated
level cannot accidentally explain it:

- **The gauge contradiction is the point.** The hub carries the staff gauge
  (+2.40 painted by hand; +1.95 / +1.60 scratched and crossed out, labelled, never
  painted over) and notice 51 ("report the water"). No template carries a string
  that resolves which recorder is right, and none explains the flood.
- **R.D. is initials, not a person.** Four records across four templates (level
  log, personnel transfer, gallery roster, the dry coat's laundry mark); never a
  name, never explained.
- **The inhabitants do not know they stopped being people.** Graffiti is placed on
  one template each (gallery roster pressed harder, culvert cuff, pump beam) and is
  tagged as graffiti, never as signage — the generator must not promote it to a
  route cue (W15).
- **One wrong detail, seed-fixed.** The hub's painted plan is wrong in exactly one
  way per run (W14). The library declares the plan; the generator picks the lie.
- **The one allowed lie.** The second bell answering first on flagged seeds (H2) is
  the generator's, not the templates' — the lightwell and basin templates only
  carry the cue letters.
- **Suffering as the price of ascent, chosen.** Descent is physical and voluntary:
  the flume drop is "chosen, not sprung"; the culvert forces a crouch (80 u); the
  drain stair is wet below and dry above (W cue: "a wet shaft is a dead end below
  it"). Ascent is signed and earned: every vertical socket carries a `+2 LEVEL`
  chevron relative to Works Zero and a landing gauge at the top (W7).
- **Physicality (PILLARS 1).** Nothing floats: pickups sit on the intake plinths
  (three solid 32x32 pedestals, kept as pillars in the footprint), the stores
  alcove's tin rests on a shelf between brackets, the pump's mirror is bolted to a
  pipe. Pillars and baffles are solid geometry the generator's LOS/sound rays
  respect.
- **The text layer is the furniture of the discipline.** One text per room, per the
  placement rules: plaques/gauges/notices on their own walls, vignettes as a room's
  only readable object (dry coat in the gallery, mirror in the pump, tin in the
  alcove). `landmark_text` carries exactly one of each kind per template.

## 3. How the templates encode the panic rules (PILLARS 5)

- **Calm first impression.** The hub and intake are `suitability: calm`; the
  ninety-second tutorial of the sign system happens before any creature. Encounters
  escalate abruptly; the calm rooms are part of the threat.
- **The Hollow and the Stone ReDead always spawn together.** The two
  `hollow_redead_bay` templates (the slice's pair bay, and the new tidal lightwell
  as a per-seed alternative home) declare `convergence: true` and have 3 sockets;
  `validate_library.py` fails any bay that does not sit at a convergence. The bay
  notes carry the pair behaviour measured in the slice: the ReDead walks, reaches
  and grips (snare releases 4 ticks after it catches); the Hollow begins crawling
  ~3 s after alert; there is room to retreat. The lightwell's surge (L cue) masks
  the Hollow's crawl, and the surge/bell coincidence is the set piece's downbeat —
  no music.
- **The Armature: sound before sight, tick before coordination.** The two
  `armature_ambush` templates (dogleg duct, V-07 valve hall) carry an interior
  baffle (`baffle_local_seg`) that blocks the socket-to-socket sightline while
  letting the ceramic tick diffract around the bend; the validator rejects an
  ambush template without a baffle. The gallery (`armature_pack`) relies on
  distance and haze — the slice's warning-led Armatures were glints in fog until
  the tick. Free Armatures read stiff and slow; the tick is the panic trigger and
  the fair warning at once.
- **No fight_required room on a narrow choke.** The east service corridor is
  128 u wide and says so: the generator must never place a `fight_required`
  Armature room there (Argon Fix #4, min_span >= 192 u).
- **Light and fog are panic tools.** Encounter rooms use the slice's `silhouette`
  and `underwater` styles and low `light_band`s; the bay and lightwell notes
  require slow fades and fog ramps (never strobe faster than ~2 Hz, no whole-frame
  jumps). The library gives each template a light band (the slice's +/-8 u
  jitter), not a single value, so the generator keeps rooms alive without flashing.
- **Show less.** Silhouette style on the pump and valve hall, underwater on the
  bay, fog in the gallery: creatures are glints and sounds until close. Set design
  and the cue set (SOUND-CUES.md letters on each template) carry the fear.
- **Fairness is data.** Every socket has a transom state (steady / flicker /
  dark_clean / dark_dust) per WAYFINDING W1-W17: exits are lit, dead ends are not,
  shortcuts are plated on both faces and lit on one (W4/W17). The validator's
  encounter checks make the panic rules fail closed at generation time.

## 4. What is approximated from the real map

- **Rooms are flattened to axis-aligned orthogonal polygons.** The blockout's
  32 u cell grid is exact; the hub's diamond is the exact clipped-diamond octagon
  of the cell union (not the stair-stepped cell boundary).
- **Stair chunks carry their sockets at the neighbour floors.** In the slice the
  first stair cell is already at z 8 (the 0 -> 8 riser sits at the threshold), so
  each stair template lists socket floors 0 and 64 with 8 risers of 8 u, and
  per-socket ceilings follow the run (`ceiling_z_u` on each socket). The slice's
  headrooms (144/128/112) are kept.
- **The pair bay mouth is widened 96 -> 128 u.** The slice's real opening to the
  pump is 96 u; the bay template extends 32 u north (its north wall then meets the
  upper pipe run, true to the slice's room layout) so the mouth carries a true
  128 u socket. The bay's north and east sockets are declared for the generator,
  not present in the slice.
- **Solid plinths and pillar holes become pillars.** The intake's three 32x32
  pedestals (z 26..96) are r16 pillars; the harvested chunk's two 8x8 pillar
  sectors are r5 pillars. LOS and sound treat them as solid.
- **The harvested chunk.** Footprint is the real union of its seven sectors;
  ceilings are approximated at 192 u (the provenance records floors and bounds,
  not source ceilings); the slice attaches it at +64 u with cold-strip textures.
  Its two 128 u sockets are the real seam sockets; the <128 u candidates are
  deliberately excluded.
- **Water is a datum, not 3D water.** `water_z_u` 16 (0.55 m at the +1.95 line
  over the +1.40 floor, per CISTERN-TEXT) marks sump/culvert/flume; the slice
  renders it as a floor texture and the generator should treat it as slow wading.
- **Mechanisms map to the slice's real actors**: V-07 valve unlocks the sluice
  latch (exit gate), the shortcut foot unlocks the shortcut latch, the service
  door is a native Door_Raise (a gate hint, never a latch), the outfall handle is
  the level exit. The lift, drop and portal anchor exist only as templates for the
  generator; the harvest vestibule is offered as the rotated-portal anchor
  (Cycle 3) because the harvested room genuinely does not line up with the works'
  numbering.
- **Sockets on wide walls are single 128 u openings placed on the real interface
  line** (the gallery's two west and two east doors, the pump's four mouths). A
  1024 u interface (upper pipe/gallery wall) carries one socket, not eight.

## 5. Decisions made (for review)

1. Socket normal convention: 0 = +x east, 90 = +y south, 180 = -x west,
   270 = -y north, in UZDoom map coordinates (+y south). Argon's generator must
   flip y if it treats +y as north.
2. The tidal lightwell is a second `hollow_redead_bay` home so the pair can sit at
   a convergence on seeds that never build the pump bay; one bay per seed.
3. The sealed basin stair is a real dead-end template (the B1 of the sign system),
   so the W4/W17 shortcut promise has a home even when the return stair is not in
   the graph.
4. `LIFT_DRY_SHAFT` uses the `stair` tag as its vertical tag (the brief's tag list
   has no `lift`); the mechanism field says lift.
5. Rarity weights: hubs/set pieces 1.0-1.2 (one per level), corridors 2.0-2.5
   (recur, but never twice in a 3-room window), optionals/dead ends 1.5.

## 6. Open questions for Josiah / Claude Code

- The bay widening (96 -> 128 u) changes the slice's real mouth; confirm the
  32 u extension north is acceptable, or supply the 128 u mouth some other way.
- Whether the lightwell's surge/bell coincidence may double as the pair bay's
  downbeat (SOUND-CUES.md already flags H2's allowed lie).
- Whether the harvest vestibule should really anchor the rotated portal, or
  whether Argon wants a dedicated portal template instead.
