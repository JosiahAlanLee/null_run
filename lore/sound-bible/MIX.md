# MIX — loudness, ducking, tell audibility, tail discipline, safety

**Status: PROPOSAL.** This file is the contract between the three documents: ROOMS.md makes the
building resonate, SFX-LIST.md makes the sounds, and this file keeps the resonating building from
burying the sounds. The design centre is one sentence: **the horror of Null Run is quiet — the mix's
job is to keep the quiet honest and the tells audible.**

## 1. Loudness targets

Reference: a calibrated in-game master at 80 %, per-class values in dBFS (RMS for sustained content,
peak for transients). Relative ladder matters more than absolutes — everything is quoted against the
**combat mean** (the average level of a one-creature fight with one weapon firing).

| Class | RMS | Peak | Notes |
|---|---|---|---|
| Ambience beds (`wx/amb/*`) | −34 to −28 | −24 | the fluorescent hum sits at −34; cistern bed at −28 (it is the star) |
| Decor one-shots | −30 | −22 | far drips quieter (−36) |
| Player footsteps | −22 | −14 | per-step peak; the step must beat the bed by ≥ 8 dB in its room |
| Weapon fire | −16 | −6 | the loudest regular event; Hymnodyne fire may touch −5 peak for its 2.8 s |
| Creature attacks | −18 | −8 | Ballast Husk charge and Pleat slam at the top of this band |
| **Tells** | −20 | −14 | +2 dB above the creature norm, band-carved (§4); never louder than weapon fire |
| Creature idle / voice | −26 | −18 | voice sits at −24 |
| UI | −24 | −12 | DRY, no reverb |
| Music (adaptive system) | — | — | owned by the music director; SFX contract: the music bus leaves the tell band free (§6) |

Hard ceilings (the safety layer, §5): master true-peak **−1 dBTP**; no single onset more than
**+12 dB** above its class mean; no one-shot above **−3 dBFS** peak. The composer's "sting voice,
explicitly budgeted" convention is mirrored here: the **tell bus** is explicitly budgeted and nothing
else may use it.

## 2. Bus architecture

```
master  ── safety limiter (−1 dBTP, 40 ms release, soft knee)
  ├─ sfx
  │   ├─ player      (P7/P8 player)      limiter −6 dBFS
  │   ├─ weapon      (P7 weapons)        limiter −4 dBFS
  │   ├─ creature    (P4/P5)             limiter −6 dBFS
  │   ├─ tell        (P6, exempt)        limiter −12 dBFS  ← nothing ducks this
  │   ├─ world       (P3–P5 world)       limiter −8 dBFS
  │   └─ ui          (P8, DRY)           limiter −10 dBFS
  └─ music           (adaptive director's bus; §6)
```

Rules: the **tell bus is exempt from all ducking** and from the creature limiter — it has its own.
The tail group (all baked tails > 0.6 s and all WET-BAKE decor) gets a **tail bus** inside `world` so
it can sidechain (§3, §5). UI is `$attenuation NONE` and never touches a zone reverb.

## 3. Ducking

| Who ducks | What ducks | Amount | Attack / release | When |
|---|---|---|---|---|
| Tells | ambience beds | −6 to −8 dB | 50 ms / 400 ms | for the tell's duration, local (within the tell's room) |
| Tells | creature idle & voice | −4 dB | 20 ms / 300 ms | same |
| Tells | music lanes 2–4 | −3 to −6 dB | 1/8 note / 2 beats | proposed new cue (see §6) |
| Weapon fire | ambience beds | −4 dB | 10 ms / 300 ms | while any player weapon is firing |
| Combat state (music director `combat_start`) | world decor (P2/P1) | −3 dB | 100 ms / 500 ms | for the combat dwell |
| Tail bus | weapon fire + tells | −6 dB | 20 ms / 400 ms | the long-tail decor pulls back exactly when combat needs clarity (§5) |
| Damage burst | music lanes 2–4 | existing | per director | the director already does this — do not double-duck on the SFX side |

**Never duck:** the tell bus, UI, footsteps (they are the player's only constant self-feedback), and
the Sigil completion sting. **Duck, never mute:** the deepest duck is −8 dB; cutting a bed entirely
reads as a bug, not a mix decision.

## 4. Attack-telegraph audibility rules

The tell is the game's fairness contract (every sheet encodes one: the Visitor's cough, the
Applicant's shutter, the Span's LOCK, the Bloom's hiss). These rules are binding:

1. **Dry + NEAR rendering.** Every tell renders with its dry attack and baked early reflections
   only — no baked tail over 0.4 s (SFX-LIST `send` = NEAR or DRY). In a wet room the zone may smear
   anything; the tell's own asset must not add to the smear.
2. **Transient in 50 ms.** The tell's first 50 ms must contain a transient ≥ 3 dB above the local
   bed. Where a tell is inherently soft (the Hem's cloth shift), precede it with its hard element
   (the sewing being put down).
3. **One band per tell.** Each tell owns a frequency band; competing creature/world content ducks
   3 dB in that band for the tell's duration. Band map (from SFX-LIST recipes):

| Creature | Tell | Band |
|---|---|---|
| Visitor | the cough + sleeve | 400 Hz – 1.5 kHz |
| Pleat | inhale + fitting whine | 200 Hz – 1 kHz |
| Reunion | stitches popping | 1 – 2 kHz |
| Span | unfold (cable note) | 200 Hz – 2.4 kHz |
| Span | **LOCK** | silence: duck the bed 6 dB for 0.5 s |
| Ravel | glass-harmonica charge | 2 – 5 kHz |
| White Bloom | kettle hiss | 2 – 6 kHz |
| Circuit | tether snap + whisker click | 80 – 150 Hz and 3 – 4 kHz |
| Applicant | the shutter | 2.5 – 4 kHz |
| Erratum | feeler trace | 1 – 4 kHz |
| Underprint | wallpaper bubble + crack | 300 Hz – 2.4 kHz |
| Hem | the hem shifting | 200 – 500 Hz |
| Ballast Husk | arc ramp | 2 – 4 kHz |
| Vore Spindle | launch thump | 60 – 120 Hz (authored long-rolloff — it must carry **further than the spore**) |
| Threshold Mimic | teeth grind | 200 – 600 Hz |
| Unaddressed | glass drag | 3 – 5 kHz |
| Surveyor | gimbal click | 1 – 3 kHz |
| Stone ReDead | the shriek | 1 – 3 kHz (broad) |
| Choraz | the inhale | 200 – 800 Hz |
| Calmor | buckle ratchets | 2 – 4 kHz |
| Repetiel | second mouth | 800 Hz – 2.5 kHz |
| Continuity boss | coil whine | 1 – 4 kHz |

4. **Two tells max.** At most two concurrent tells (SFX `$limit` 8 on the group, logic-cap 2); a
   third is queued and delayed up to 200 ms until one ends. Fairness over realism.
5. **Mono-centre.** Tells play mono-centre even in wide rooms; the player must not have to localise
   a warning, only act on it.
6. **Tell beats bed by ≥ 10 dB.** In the C3 vault (bed −28, tell −20 RMS/−14 peak) a tell must clear
   the local bed by 10 dB at onset; if a room bed is louder than target, the bed ducks, never the tell.
7. **Voice is a tell too.** The Hem's "sit down" and the Visitor's "sorry" get the same NEAR/band
   treatment; the Unaddressed's plate taps are puzzle+voice — keep them pitched, clear and consistent
   (they are the only tells the player must *answer*).

## 5. Keeping long cistern tails from smearing combat

The C3 vault decays 4.2 s with a 0.12 s flutter. Five countermeasures, in order of importance:

1. **Zone design does half the work.** The vault profile already biases early reflections (−800 mB at
   14 ms) and delays the late field to 28 ms (ROOMS.md 4.3): transients stay clear because the smear
   starts late. Do not "fix" combat by deadening the room — the room is the game.
2. **Pre-delay discipline in assets.** Gameplay sounds keep their attack inside 30 ms; the baked NEAR
   layer's first reflection lands at 14–18 ms, matching the vault, so dry attack + early reflections
   carry the information and the tail carries only mood.
3. **Tail budget.** No gameplay sound gets a baked tail over 1.5 s; only decor, deaths and the
   Hymnodyne may tail 2–4 s. A footstep in the C3 vault should return *once* (the flutter), not
   twenty times.
4. **Tail sidechain.** The tail bus (baked tails > 0.6 s and WET-BAKE decor) ducks 6 dB under weapon
   fire and tells (20 ms attack / 400 ms release). The moment combat needs clarity the long tails
   recede; the moment it ends they bloom back — which also *reads* as the fight ending.
5. **Zone seams at doors** (ROOMS.md §3) and the **two-room fight rule**: no combat may span two
   zones whose decay differs by more than 1.5 s. If a fight must cross, re-measure the room or move
   the seam — the ear localises across reverb changes the way the eye fails across light levels.

## 6. Music integration (contract with the adaptive director)

The director owns music state (`exploration → threat → combat → quiet → boss → victory`) and already
ducks lanes 2–4 on damage bursts. SFX asks for three additions, all proposals for Josiah/host work:

- **`tell` cue** (priority 65, between damage_burst 60 and floor_change 50): on any tell start, duck
  lanes 2–4 by 3–6 dB for two beats, 1-bar cooldown — mirrors the existing damage-burst treatment, so
  it is a two-line change in the director.
- **Quiet state ambience boost:** during `quiet`, ambience beds may rise +3 dB (the game's reward for
  silence); during `combat`, decor ducks per §3.
- **Victory/quiet and the tail bus:** after `combat_end`, release the tail sidechain over ~1 s — the
  reverb blooming back is the acoustic "all clear".

The composer's sting voice is already budgeted; the SFX side never adds musical content to UI or
beds, so the two systems cannot fight for the same band.

## 7. Audio safety (photosensitive-equivalent)

The visual rules (flash caps, luminance steps, reduced-flash options) get audio equivalents:

- **No sudden extreme loud spikes.** Master true-peak −1 dBTP; onset step cap +12 dB above class
  mean; no one-shot over −3 dBFS. The game's scares are quiet by design — **no jumpscare stings are
  authorised anywhere**, including the Mimic and the Underprint (their tells are their only warning).
- **The contrast rule.** If the mix has been quieter than −30 dB RMS for 30 s, the next loud event
  ramps in over 80 ms (anti-startle), except tells (which need their 50 ms transient — the exception
  that keeps the game fair).
- **Flash-equivalent caps.** The Ravel's burst crack is capped at +1.5 dB above the combat mean and
  ≤ 0.2 s (matching the sheet's <3 Hz / <0.2 s amber-flash cap); the Continuity boss's arc crack is
  capped at +3 dB above combat mean, once per 1.5 s cooldown.
- **Sustained exposure.** Beds are band-limited and sit at −34 to −28 dB RMS — hours-long safe; the
  fluorescent hum must include the music director's quiet-state dip so the 120 Hz drone never runs
  unrelieved for a whole floor.
- **Low-frequency discipline.** Sub-40 Hz content rolls off with a soft knee at 45 Hz. The two
  biggest LF events (Pleat slam, Plumb Bombard) are high-passed and limited to one per 2 s; the
  Hymnodyne's bellows blast gets a 45 Hz shelf, not a sub drop.
- **Accessibility option: "reduced spikes".** −6 dB on all P5+ one-shots and tails, a one-toggle
  mirror of reduced flash; the tell band and UI are untouched (fairness is not optional).
- **First-run safe start.** Master at 70 % on first launch until the player opens the audio menu.

## 8. Verification checklist (run these in the C3 vault first)

1. Stand still in the C3 vault: the bed sits at −28, the drips answer the room, the flutter is
   audible but not tonal. Walk ten steps: each step returns once, wet, never a smear.
2. Play every tell against the full stack (bed + music at default + one other creature): all 21
   creature tells (and the boss's) must clear by 10 dB and keep their transient inside 50 ms. The
   Applicant shutter is the reference — if it blurs, the vault profile or the send is wrong.
3. Fire the Transit-12 into the vault with two creatures active: attacks stay localisable, tails
   duck within 20 ms, the flutter does not overlap the next shot.
4. Cross the T0–O1 door: the zone change is masked by the door sound (no snap, no click).
5. Span LOCK in the west void: the knock reads, then 0.5 s of ducked bed — the silence is the cue.
6. Kill the Ballast Husk in the cistern: the hum drops to one key, then nothing. The room answers.
7. Reduced-spikes toggle on: the Pleat slam and the Ravel burst drop 6 dB, the Visitor's cough does
   not change. Master limiter never trips (−1 dBTP).
8. Thirty seconds of quiet, then the hour (the far Hymnodyne): it ramps over 80 ms per the contrast
   rule and does not startle.
