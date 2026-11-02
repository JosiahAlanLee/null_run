# SFX-LIST — every sound the game needs

**Status: PROPOSAL.** The shipped build currently contains exactly four audio loops
(`ld/app`, `ld/rep`, `ld/tell`, `ld/calm` in `living-depths.pk3`); everything else on this list is
greenfield. All sounds are synthesized with numpy/scipy — no external recordings. Creature recipes
implement the "Sound cues (in words)" sections of the lore sheets, which are treated as binding art
direction; timings are the sheets' prototype states at 35 Hz (1 tick = 28.6 ms) and must be re-timed
against shipped animation.

## 1. Conventions

**Columns.** `dur` = duration in seconds (round to whole ticks at integration; 0.086 s ≈ 3 ticks).
`prio` = priority class P1–P8 (P8 never culled, P1 first to go under channel pressure). `loop` =
looping asset or one-shot. `send` = reverb treatment (below). `recipe` = synthesis prescription in
toolkit terms (§2).

**Priority ladder.**

| Prio | Class | Budget (channels) |
|---|---|---|
| P8 | UI confirm, hurt-critical, death, sigil completion | 6 |
| P7 | Player feedback (footsteps, weapon fire) | 16 |
| P6 | **Tells** (attack telegraphs) and traversal cues (Span LOCK) | 8 |
| P5 | Creature attacks, creature signatures, doors | 24 |
| P4 | Creature idle/notice, voice, pickups | 16 |
| P3 | Ambience beds per stratum | 8 |
| P2 | Decor (drips, distant pipes, far creatures) | 12 |
| P1 | Cullable decor (distant random one-shots) | 8 |

SNDINFO carries `$limit` per logical group, `$random` for variants, `$volume` and `$attenuation`
(NORM world sounds; IDLE for decor; NONE for UI). Tells get their own group limit (2 concurrent —
MIX.md rule 4).

**Reverb send.** The engine wets everything by zone, so assets are authored dry and the zone does the
work. The `send` column therefore says what *extra* baked treatment the asset carries, so it reads
correctly inside the wet rooms (C3 vault is the test case):

- **DRY** — no baked wetness; UI and sounds that must never smear (Applicant shutter, Span LOCK).
- **NEAR** — baked early reflections only (first 80 ms, tuned to the zone's reflection delay); for
  tells and key cues that must cut through a long tail. No baked tail over 0.4 s.
- **MID** — dry + baked early reflections + short tail ≤ 0.6 s; for attacks and impacts that should
  read big but stay intelligible.
- **WET** — dry asset only; the zone's tail is the sound's tail (default for body sounds, footsteps
  in wet rooms).
- **WET-BAKE** — the tail is baked in (decor with signature tails: drips in shafts, the chime).
  Reads identically in every zone.
- **UW** — underwater variant; also hard-lowpassed.

**Logical names** use `pl/`, `wp/`, `cr/`, `wx/`, `ui/` namespaces and are the SNDINFO names.

**Timing rule.** A sound that must accompany a state should start on the state's first tick; tell
sounds start on tick 1 of the tell state and put their transient inside the first 50 ms (MIX.md).

## 2. Synthesis toolkit (numpy / scipy primitives)

Small recipes a programmer can lift. `sr` = 44100 (or 48000) throughout.

```python
import numpy as np
import scipy.signal as sg

def noise_band(dur, sr, lo, hi, q=1.0):
    """White noise through a 2nd-order bandpass, peak-normalised to q."""
    n = np.random.default_rng().standard_normal(int(dur * sr))
    y = sg.sosfilt(sg.butter(2, [lo, hi], 'bandpass', fs=sr, output='sos'), n)
    return y * (q / (np.max(np.abs(y)) + 1e-9))

def modal(sr, modes, dur=2.0):
    """Bank of exponentially decaying sinusoids (bells, glass, bronze, porcelain).
    modes = list of (freq Hz, tau s, amp)."""
    t = np.arange(int(dur * sr)) / sr
    y = np.zeros_like(t)
    for f, tau, a in modes:
        y += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * t)
    return y / (np.max(np.abs(y)) + 1e-9)

def granular(dur, sr, rate=80, band=(2e3, 6e3), grain=(0.002, 0.012), jitter=0.6, seed=0):
    """Sparse overlapping grains -> paper, fibre, dust, flakes, wool, scuffs.
    Raise rate for rustle, lower for sparse ticks."""
    rng = np.random.default_rng(seed)
    out = np.zeros(int(dur * sr)); t = 0.0
    while t < dur:
        g = rng.uniform(*grain); i = int(t * sr)
        y = noise_band(g, sr, *band) * np.hanning(int(g * sr))
        out[i:i + len(y)] += y[:max(0, len(out) - i)]
        t += g + rng.exponential(1.0 / rate) * jitter
    return out / (np.max(np.abs(out)) + 1e-9)

def impact(dur, sr, f0, fend, q=2.0):
    """Filtered impact: noise through a resonant lowpass whose centre sweeps
    f0 -> fend. Thumps, footsteps, bodyfalls; lower Q = duller material."""
    t = np.arange(int(dur * sr)) / sr
    f = f0 * (fend / f0) ** (t / dur)                      # exponential pitch drop
    x = noise_band(dur, sr, 40, max(6000, f0 * 4)) * np.exp(-t / (dur / 3))
    y = np.zeros_like(x); buf = np.zeros(2)
    for i in range(len(x)):                                # state-variable sweep
        k = np.tan(np.pi * f[i] / sr); a0 = 1 + k / q + k * k
        buf[0] += k * (x[i] - buf[1] - (1 + k / q) * buf[0]) / a0
        buf[1] += k * buf[0]
        y[i] = buf[1]
    return y / (np.max(np.abs(y)) + 1e-9)

def pitch_env(dur, sr, f0, f1, curve='exp', shape='sine', amp=0.5):
    """Exponential/linear glide on a tone. Squeaks, cable creaks, whines, windups.
    Replace the oscillator with a filtered noise band for 'hiss ramps'."""
    t = np.arange(int(dur * sr)) / sr
    f = f0 * (f1 / f0) ** (t / dur) if curve == 'exp' else np.linspace(f0, f1, len(t))
    return amp * np.sin(2 * np.pi * np.cumsum(f) / sr)

def formant(dur, sr, f0, f0end, f1, f2, f3, bws=(90, 120, 160), breath=0.7):
    """Whispered/voiced syllable: pulse source at f0 (gliding to f0end) through three
    formant resonators, plus a breathy noise layer. The only 'voice' the game needs."""
    t = np.arange(int(dur * sr)) / sr
    f = f0 * (f0end / f0) ** (t / dur)
    src = sg.square(2 * np.pi * np.cumsum(f) / sr, duty=0.2) * 0.5 + 0.5
    src = sg.sosfilt(sg.butter(2, 800, 'low', fs=sr, output='sos'), src)
    y = np.zeros_like(t)
    for fi, bw in zip((f1, f2, f3), bws):
        y += sg.sosfilt(sg.butter(2, [fi - bw, fi + bw], 'bandpass', fs=sr, output='sos'), src)
    y += breath * noise_band(dur, sr, 2e3, 8e3, q=0.3)
    return y / (np.max(np.abs(y)) + 1e-9)

def underwater(x, sr, lp=1200, down=0.97):
    """Steep lowpass + slight pitch-down for UW sends."""
    y = sg.sosfilt(sg.butter(4, lp, 'low', fs=sr, output='sos'), x)
    idx = np.linspace(0, len(y) - 1, int(len(y) * down))
    y = np.interp(idx, np.arange(len(y)), y)
    return y / max(1.0, np.max(np.abs(y)) + 1e-9)          # filter can overshoot

def freeverb_tail(x, sr, wet=0.33, damp=0.35, size=0.83, fb_gain=0.84):
    """Schroeder reverb (8 combs, 4 allpasses) for baking NEAR/MID/WET-BAKE layers.
    Classic Freeverb tunings, mono; `size` scales room size, `damp` dulls the tail."""
    cl = [0.0297, 0.0371, 0.0411, 0.0437, 0.0313, 0.0397, 0.0431, 0.0473]
    cb = [np.zeros(int(sr * d * size)) for d in cl]; store = [0.0] * 8
    ap = [(int(sr * d * size), np.zeros(int(sr * d * size)))
          for d in (0.0050, 0.0017, 0.0125, 0.0075)]
    out = np.zeros_like(x)
    for i in range(len(x)):
        acc = 0.0
        for k in range(8):
            j = i % len(cb[k])
            o = cb[k][j]
            lp = o * (1 - damp) + store[k] * damp      # one-pole damping in the loop
            cb[k][j] = x[i] + lp * fb_gain
            store[k] = lp
            acc += lp
        y = acc / 8
        for d, buf in ap:
            j = i % d
            tmp = buf[j]
            buf[j] = y + tmp * 0.5
            y = tmp - buf[j] * 0.5
        out[i] = x[i] * (1 - wet) + y * wet
    return out / max(1.0, np.max(np.abs(out)) + 1e-9)      # comb feedback can overshoot
```

Where a recipe says "`freeverb_tail(x, wet=…)`", bake with `damp` per material
(0.15 bright porcelain, 0.6 wet wool).

## 3. Player

Footsteps: 4 variants per material, grouped under `$random`, `$limit 2`, pitch jitter ±5 %.
Each step = impact + material click + scuff; step interval is the walk cycle (48 tics per the
Applicant walk standard, but the player's own cycle governs).

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| step — dry tile | `pl/step/tile1..4` | 0.18 | P7 | — | NEAR | `impact(0.18, f0=900→300, q=3)` + porcelain click `modal((2400, 0.02, 0.4))` + 8 ms `granular` scuff at 2–5 kHz |
| step — limestone | `pl/step/limestone1..4` | 0.20 | P7 | — | WET | `impact(0.20, f0=500→200, q=1.5)` + `modal((1100, 0.03, 0.3))` + stone grit `granular(rate=40, band=(3e3,7e3))` |
| step — wood (benches, planks) | `pl/step/wood1..4` | 0.22 | P7 | — | NEAR | `impact(0.22, f0=350→150, q=1)` + variant 3 adds a creak `pitch_env(0.06, f0=400, f1=250)` |
| step — wet stone | `pl/step/wetstone1..4` | 0.22 | P7 | — | NEAR | `impact(0.22, f0=600→250, q=1.5)` + 30 ms splash band 1–3 kHz + short wet `granular(rate=30)` |
| step — shallow water | `pl/step/water1..4` | 0.35 | P7 | — | WET | two-layer: 40 ms splash `noise_band(0.04, 800, 4e3)` + droplet tail `granular(0.3, rate=50, band=(1e3,5e3))`; lows damped per ROOMS |
| wade loop | `pl/wade` | 2.0 | P7 | yes | WET | rolling `noise_band(2.0, 300, 900)` with 0.7 Hz amplitude LFO + sparse droplet ticks |
| step — grating | `pl/step/grating1..4` | 0.15 | P7 | — | MID | `modal((1800, 0.04, 0.5), (2600, 0.03, 0.3))` + low clang `impact(0.15, f0=250→180, q=4)` |
| step — mud | `pl/step/mud1..4` | 0.25 | P7 | — | NEAR | `impact(0.25, f0=200→80, q=0.8)` + squelch `noise_band(0.06, 400, 900)` |
| landing (hard / soft) | `pl/land1..2` | 0.30 | P7 | — | MID | `impact(0.3, f0=250→90, q=1)` + boot scuff; soft variant −6 dB, lowpassed |
| splash (deep step / fall into water) | `pl/splash` | 0.8 | P7 | — | WET | 60 ms `noise_band(300, 2e3)` burst + falling droplet tail `granular(0.7, rate=60, band=(800,4e3))` |
| hurt | `pl/hurt1..2` | 0.35 | P8 | — | DRY | `formant(0.35, f0=160→110, f1=500, f2=1100, f3=2200, breath=0.4)` + cloth; variant 2 pitched up 2 st |
| death | `pl/death` | 1.8 | P8 | — | MID | exhale `formant(0.9, f0=130→70, breath=0.8)` + bodyfall `impact(0.5, f0=180→60)` + settle `granular(0.6, rate=15, band=(300,1e3))`, then room tone only |

## 4. Weapons

All seven, from WEAPONS.md (institutional mechanisms: punch dies, counting wheels, bellows, reels).
Shared: `wp/pickup` (0.5 s, P4, NEAR — paper tag rustle `granular(rate=90, band=(1e3,4e3))` +
metal clink `modal((3200, 0.05, 0.3))`), `wp/switch` (0.2 s, P4, DRY — small clunk
`impact(0.2, f0=600→300, q=3)`). Firing sounds are P7, mono-centre, `$limit` per weapon.

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| **Fathom Hook** raise | `wp/fathom/raise` | 0.5 | P4 | — | NEAR | cable rattle `granular(0.3, rate=80, band=(2e3,5e3))` + reel click `modal((1500, 0.02, 0.5))` ×2 |
| — swing | `wp/fathom/swing` | 0.35 | P7 | — | WET | cable whoosh `pitch_env(0.3, f0=900, f1=300)` on band noise + hook whirr `noise_band(0.3, 600, 2e3)` |
| — hit (flesh/stone) | `wp/fathom/hit1..2` | 0.25 | P7 | — | NEAR | porcelain/limestone crack `modal((1800, 0.05, 0.6), (3200, 0.02, 0.4))` + cable snap `impact(0.1, f0=800→300, q=5)` |
| — reel (chainsaw-mode run loop) | `wp/fathom/reel` | 1.0 | P7 | yes | WET | geared ratchet loop: `granular(1.0, rate=120, band=(1e3,4e3))` + motor-ish 110 Hz hum, 6 Hz flutter |
| **Registrar** raise | `wp/registrar/raise` | 0.4 | P4 | — | NEAR | punch-handle ratchet ×2 (`modal((2200, 0.03, 0.4))` ticks) + slide dry clack |
| — fire | `wp/registrar/fire` | 0.25 | P7 | — | DRY | 5 ms click + die strike `modal((3200, 0.04, 0.7))` + paper-punch thump `impact(0.2, f0=400→150, q=2)`; short and dry — a stapler, not a gun |
| — mechanism | `wp/registrar/mech` | 0.3 | P4 | — | NEAR | slide return clack + counter wheel tick `modal((2800, 0.015, 0.4))` |
| — empty | `wp/registrar/empty` | 0.15 | P4 | — | DRY | dry pin click `modal((3400, 0.01, 0.5))`, quieter than fire |
| — reload | `wp/registrar/reload` | 0.9 | P4 | — | NEAR | brass pin clip `granular(0.6, rate=70, band=(2e3,6e3))` + spring seat `pitch_env(0.2, f0=700, f1=400)` |
| **Transit-12** raise | `wp/transit/raise` | 0.5 | P4 | — | NEAR | break-action clunk `impact(0.3, f0=500→200, q=2)` + wax crumb rattle `granular(0.3, rate=60, band=(3e3,6e3))` |
| — fire (single) | `wp/transit/fire` | 0.5 | P7 | — | MID | seal driver: deep bang `impact(0.4, f0=110→50, q=1)` + lead slug whack `modal((700, 0.08, 0.5))` + 2 kHz crack layer; the room answers (let the zone do it) |
| — fire (double / SSG) | `wp/transit/firedbl` | 0.7 | P7 | — | MID | two `fire` bangs 40 ms apart + hinge foregrip rattle |
| — mechanism | `wp/transit/mech` | 0.4 | P4 | — | NEAR | spent cartridge jingle (the habit: `modal((2600, 0.05, 0.3))` + tinny roll) |
| — empty | `wp/transit/empty` | 0.2 | P4 | — | DRY | hammer on the jammed spent cartridge — dull tick, no bang |
| — reload | `wp/transit/reload` | 1.1 | P4 | — | NEAR | two cartridges ratchet in + hinge squeak `pitch_env(0.15, f0=500, f1=300)` |
| **Comptroller** raise | `wp/comptroller/raise` | 0.5 | P4 | — | NEAR | carrier clunk `impact(0.3, f0=350→150, q=2)` + gate-plate rattle |
| — fire | `wp/comptroller/fire` | 0.15 | P7 | — | MID | punch-head bang `impact(0.15, f0=120→70, q=1.5)` + die click 2.8 kHz; played at 9/s by the fire loop |
| — mechanism (carrier loop while firing) | `wp/comptroller/mech` | 1.0 | P7 | yes | WET | six-head carrier ratchet `granular(1.0, rate=140, band=(1e3,4e3))` + counting-wheel ticks accelerating |
| — empty | `wp/comptroller/empty` | 0.6 | P4 | — | NEAR | carrier spins free: whirr down `pitch_env(0.6, f0=600, f1=150)` on band noise |
| — reload | `wp/comptroller/reload` | 1.2 | P4 | — | NEAR | token-strip feed: paper tear `granular(0.2, rate=90, band=(1e3,3e3))` + tin lid clang + ratchet ×3 + wheels tick |
| **Plumb Bombard** raise | `wp/bombard/raise` | 0.6 | P4 | — | NEAR | tube clunk + spirit-level slosh `noise_band(0.3, 400, 1e3)` |
| — fire | `wp/bombard/fire` | 1.4 | P7 | — | MID | deep mortar thump `impact(0.8, f0=60→35, q=0.8)` + line whistle `pitch_env(0.7, f0=400, f1=3e3)` + drum unwind `granular(0.6, rate=110, band=(2e3,5e3))` |
| — mechanism | `wp/bombard/mech` | 0.5 | P4 | — | NEAR | measuring-drum ratchet + counter wheel tick |
| — empty | `wp/bombard/empty` | 0.25 | P4 | — | DRY | breech clang, hollow |
| — reload | `wp/bombard/reload` | 1.4 | P4 | — | NEAR | breech clack + charge seated (heavy) + line-drum wind ×3 |
| **Aethometer** raise | `wp/aethometer/raise` | 0.5 | P4 | — | NEAR | insulator stack slide (porcelain on porcelain `granular(0.2, rate=50, band=(3e3,6e3))`) + cable loom |
| — fire | `wp/aethometer/fire` | 0.45 | P7 | — | DRY | arc: 30 ms buzz `noise_band(0.03, 3e3, 6e3)` with `pitch_env` down + paper strip advance tick ×1 (`modal((1200, 0.03, 0.4))`); the arc is light, not lightning |
| — mechanism | `wp/aethometer/mech` | 1.0 | P4 | yes | WET | belt-battery hum loop (120 Hz + 240 Hz, very quiet, 2 Hz beat) |
| — empty | `wp/aethometer/empty` | 0.15 | P4 | — | DRY | weak click, no arc |
| — reload | `wp/aethometer/reload` | 0.8 | P4 | — | NEAR | glass cell seated `modal((4200, 0.1, 0.3))` + fabric tape pull |
| **Hymnodyne** raise | `wp/hymnodyne/raise` | 0.8 | P4 | — | NEAR | bellows wheeze `noise_band(0.6, 200, 800)` + keybed clatter |
| — fire | `wp/hymnodyne/fire` | 2.8 | P7 | — | WET | **the hour**: bronze chord `modal((174.6, 1.5, 1.0), (220, 1.2, 0.7), (261.6, 1.0, 0.5), (349.2, 0.7, 0.4))` + bellows blast `impact(1.0, f0=45→30, q=0.6)` + nine key strikes on the attack; the room always agrees |
| — mechanism (bellows loop) | `wp/hymnodyne/mech` | 1.5 | P4 | yes | WET | stitched-hide bellows pump: 0.8 Hz swell of `noise_band(1.5, 150, 600)` |
| — empty | `wp/hymnodyne/empty` | 0.2 | P4 | — | DRY | dry key: brass tick, no voice |
| — reload | `wp/hymnodyne/reload` | 1.6 | P4 | — | NEAR | forty cells: `granular(1.2, rate=80, band=(2e3,5e3))` glass clink loop + tuning-slide scrape |

## 5. Creatures

Every creature gets the six core states (idle, notice, tell, attack, hurt, death) plus its specials,
in the material terms of the lore sheets ("porcelain scrape, cable creak, paper rustle, concrete
grind"). Names under `cr/<id>/`. **Tell = P6, NEAR, mono, ≤0.4 s tail** unless noted — the audibility
rules live in MIX.md §4. Idles are P3/P4 loops. Deaths are MID/WET and may tail 2–4 s.

### 5.1 Bestiary (nullrun-lore-20261101)

**Calmor — restraint attendant (felt, hide, needles, latches).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (breathing + needlework) | `cr/calmor/idle` | 4.0 | P3 | yes | WET | slow felt-and-hide breath `noise_band(4, 150, 400)` with 0.25 Hz swell + sparse needle ticks `modal((3000, 0.015, 0.25))` + one latch click |
| notice (heavy step + strap creak) | `cr/calmor/notice` | 0.8 | P5 | — | WET | heavy footfall `impact(0.5, f0=180→70, q=1)` + leather creak `pitch_env(0.12, f0=300, f1=180)` on band noise |
| tell (buckle ratchets) | `cr/calmor/tell` | 0.7 | P6 | — | NEAR | buckle ratchet ×3 accelerating `granular(0.7, rate=40→90, band=(2e3,4e3))` |
| attack (restrain) | `cr/calmor/attack` | 0.9 | P5 | — | MID | cuff snap `impact(0.3, f0=200→100, q=2)` + whoosh `pitch_env(0.5, f0=700, f1=250)` |
| hurt | `cr/calmor/hurt` | 0.4 | P5 | — | WET | padded thump + low grunt `formant(0.35, f0=110→90, f1=400, f2=900, breath=0.3)` |
| death | `cr/calmor/death` | 2.2 | P5 | — | WET | long exhale `formant(1.4, f0=100→60, breath=0.9)` + felt settle `granular(1.0, rate=20, band=(200,600))` |

**Repetiel — double-faced courier (ivory shell, laryngeal tube, paper).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (two breaths) | `cr/repetiel/idle` | 4.0 | P3 | yes | WET | two overlapping soft breaths, 1.02× detune `noise_band(4, 250, 900)` ×2 panned apart + light footfalls |
| notice (ivory clack) | `cr/repetiel/notice` | 0.3 | P5 | — | NEAR | ivory shell clack `modal((2800, 0.04, 0.4))` |
| tell (second mouth) | `cr/repetiel/tell` | 0.8 | P6 | — | NEAR | the other mouth speaks: half-second breathy whisper `formant(0.8, f0=150, f1=500, f2=1400, breath=0.8)` slightly detuned, mid-word cut |
| attack (paper-rush lunge) | `cr/repetiel/attack` | 0.6 | P5 | — | WET | fast paper rustle `granular(0.4, rate=140, band=(1e3,4e3))` + tube wheeze `pitch_env(0.3, f0=800, f1=400)` |
| hurt | `cr/repetiel/hurt` | 0.5 | P5 | — | WET | breathy cry ×2, 40 ms apart (two formants, detuned) |
| death | `cr/repetiel/death` | 2.0 | P5 | — | WET | both mouths exhale, one after the other + paper drift `granular(1.0, rate=25, band=(1e3,3e3))` |

**Scriptorax — six-armed archivist (sleeves, paper, numbered strips).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (paper handled) | `cr/scriptorax/idle` | 5.0 | P3 | yes | WET | sparse paper `granular(5, rate=15, band=(1e3,4e3))` + sleeve cloth rustle |
| notice (many fingers) | `cr/scriptorax/notice` | 0.5 | P5 | — | NEAR | dense paper burst `granular(0.5, rate=180, band=(2e3,5e3))` |
| tell (sleeves rearranging) | `cr/scriptorax/tell` | 0.9 | P6 | — | NEAR | cloth sweep `noise_band(0.6, 400, 1e3)` + strip-number click `modal((1600, 0.03, 0.4))` |
| attack (six-arm grab) | `cr/scriptorax/attack` | 0.7 | P5 | — | MID | rush of sleeves `granular(0.5, rate=150, band=(800,2e3))` + paper slap `impact(0.2, f0=500→200, q=1)` |
| hurt | `cr/scriptorax/hurt` | 0.4 | P5 | — | WET | papery cry `formant(0.35, f0=200→150, f1=600, f2=1600, breath=0.7)` |
| death | `cr/scriptorax/death` | 2.5 | P5 | — | WET | coat of sleeves collapsing + strips falling like rain `granular(2.0, rate=40, band=(1e3,4e3))` |

**Choraz — sixteen-horn herald (brass, helmet, proclamation).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (horns settle) | `cr/choraz/idle` | 4.0 | P3 | yes | WET | brass settling `modal((500, 0.4, 0.2))` slow + breathing through metal `noise_band(4, 300, 600)` |
| notice (helmet + horn clink) | `cr/choraz/notice` | 0.4 | P5 | — | NEAR | leather turn + horn clink `modal((1800, 0.06, 0.35))` |
| tell (the inhale) | `cr/choraz/tell` | 1.0 | P6 | — | NEAR | long breath through sixteen bells: resonant noise sweep up 200→800 Hz + rising brass edge `pitch_env(1.0, f0=400, f1=900)` |
| attack (proclamation) | `cr/choraz/attack` | 1.2 | P5 | — | MID | formant blast + brass chord `modal((233, 0.8, 0.6), (311, 0.6, 0.4), (466, 0.4, 0.3))`; **each repeat +2 dB, onset 100 ms sooner, cap +6 dB** (the sheet's rule) |
| hurt | `cr/choraz/hurt` | 0.5 | P5 | — | WET | brass dent: inharmonic `modal((600, 0.3, 0.5), (900, 0.2, 0.4), (1300, 0.15, 0.3))` |
| death | `cr/choraz/death` | 3.0 | P5 | — | WET | sixteen horns going out of tune one by one: descending detuned modal cascade, last one alone |

**Stone ReDead — ossuary resident (limestone mask, slate, dry sinew).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (sinew + slate) | `cr/redead/idle` | 4.0 | P3 | yes | WET | dry sinew creak `pitch_env(0.3, f0=350, f1=200)` sparse + slate shuffle `granular(4, rate=10, band=(2e3,5e3))` |
| notice (stone scrape) | `cr/redead/notice` | 0.6 | P5 | — | WET | limestone scrape `noise_band(0.6, 1e3, 3e3)` with slow pitch-down |
| tell (the shriek) | `cr/redead/tell` | 0.9 | P6 | — | NEAR | **only when the mask is lifted**: formant scream `formant(0.8, f0=500→900, f1=1100, f2=2200, f3=3000, breath=0.2)` + limestone grind underneath |
| attack (grasp) | `cr/redead/attack` | 0.8 | P5 | — | MID | long fingers: joint pops ×4 `granular(0.4, rate=30, band=(1e3,3e3))` + slate drag `noise_band(0.5, 800, 2e3)` |
| hurt | `cr/redead/hurt` | 0.4 | P5 | — | WET | stone crack `modal((1200, 0.08, 0.5), (2400, 0.04, 0.4))` |
| death | `cr/redead/death` | 2.0 | P5 | — | WET | mask settling on the shelf: one hollow limestone knock `impact(0.6, f0=300→120, q=2)` + dust |

**Surveyor — the line (instrument body, gimbal, degree rings).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (gimbal whirr) | `cr/surveyor/idle` | 4.0 | P3 | yes | WET | gimbal loop `noise_band(4, 400, 800)` with 2 Hz flutter + degree-ring ticks `modal((2400, 0.02, 0.25))` sparse |
| notice (gimbal brakes) | `cr/surveyor/notice` | 0.5 | P5 | — | NEAR | whirr braking `pitch_env(0.5, f0=900, f1=500)` on band noise |
| tell (gimbal settles) | `cr/surveyor/tell` | 0.5 | P6 | — | DRY | one clean metallic click `modal((2000, 0.03, 0.5))` + one chalk strike `impact(0.2, f0=900→400, q=4)` — leave the line |
| attack (the line) | `cr/surveyor/attack` | 0.5 | P5 | — | MID | thin fast whine `pitch_env(0.15, f0=1e3, f1=6e3)` + cable twang `modal((300, 0.2, 0.5))` |
| hurt | `cr/surveyor/hurt` | 0.4 | P5 | — | WET | instrument rattle `granular(0.3, rate=90, band=(2e3,5e3))` |
| death | `cr/surveyor/death` | 2.5 | P5 | — | WET | gimbal spin-down: long pitch fall 3 kHz→200 Hz over 2 s, then a single degree-ring tick |

**Vore Spindle — spore-bearer (chitin, launch ribs, membrane).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (chitin + wet) | `cr/spindle/idle` | 4.0 | P3 | yes | WET | chitin clicks `modal((3500, 0.04, 0.25))` sparse + water drips |
| notice (ribs creak) | `cr/spindle/notice` | 0.5 | P5 | — | WET | launch ribs creaking open `pitch_env(0.5, f0=400, f1=800)` on band noise |
| tell (launch) | `cr/spindle/tell` | 0.6 | P6 | — | NEAR | **the launch sound carries further than the spore does** (sheet rule): low wet thump `impact(0.25, f0=80→50, q=1)` + membrane stretch `pitch_env(0.4, f0=300, f1=700)`; author with long rolloff, audible at 2× spore range while the spore itself is quiet |
| attack (spore out) | `cr/spindle/attack` | 0.3 | P5 | — | WET | pop + the homing spore's own faint whine (projectile loop, P2, very quiet `pitch_env(0.5, f0=900, f1=1400)`) |
| hurt | `cr/spindle/hurt` | 0.4 | P5 | — | WET | chitin shatter `modal((2800, 0.05, 0.5), (4200, 0.03, 0.4))` |
| death | `cr/spindle/death` | 1.5 | P5 | — | WET | abdomen settling in water: soft splash + one last membrane sigh |

**Ballast Husk — wire shambler (cable muscle, porcelain contacts, maw).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (the hum) | `cr/husk/idle` | 5.0 | P3 | yes | WET | **it hums in two keys** (sheet): `modal((82.4, 5.0, 0.5), (246.9, 4.0, 0.3))` — low E and something above it, very quiet + rare porcelain contact tick; never tune it |
| notice (ballast clunk) | `cr/husk/notice` | 0.6 | P5 | — | WET | ballast core clunk ×2 `impact(0.3, f0=120→60, q=1.5)` |
| tell (arc builds) | `cr/husk/tell` | 0.9 | P6 | — | NEAR | maw arcs building: rising buzz `noise_band(0.9, 2e3, 4e3)` with level ramp + cable creak `pitch_env(0.5, f0=500, f1=900)` |
| attack (the charge) | `cr/husk/attack` | 1.4 | P5 | — | MID | loud grinding run `granular(1.0, rate=160, band=(500,2e3))` + rumble `impact(1.0, f0=90→60, q=0.7)` + arc crack (white burst 1–6 kHz, 150 ms, capped per MIX safety) |
| hurt | `cr/husk/hurt` | 0.4 | P5 | — | WET | porcelain crack + wire snap `modal((2600, 0.04, 0.5))` |
| death | `cr/husk/death` | 3.0 | P5 | — | WET | **the hum drops to ONE key and stops** (the sheet's beat): the upper note dies first, the low E holds alone for 1.5 s, then silence |

**Threshold Mimic — the false exit (door, rubber seals, concrete teeth).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (a door) | `cr/mimic/idle` | 4.0 | P1 | yes | WET | nothing, mostly: a faint rubber-seal settle every ~12 s. The sound of a door is its absence |
| notice (seal flex) | `cr/mimic/notice` | 0.4 | P5 | — | NEAR | rubber seal flex `pitch_env(0.3, f0=300, f1=180)` |
| tell (teeth grind) | `cr/mimic/tell` | 0.5 | P6 | — | NEAR | concrete teeth grinding inside the frame `noise_band(0.5, 200, 600)` with pitch-down |
| attack (the bite) | `cr/mimic/attack` | 0.8 | P5 | — | MID | door slam `impact(0.4, f0=100→45, q=1)` + concrete grind + seal slap `noise_band(0.2, 600, 2e3)` |
| hurt | `cr/mimic/hurt` | 0.4 | P5 | — | WET | hollow door knock `modal((900, 0.1, 0.5))` |
| death | `cr/mimic/death` | 2.0 | P5 | — | WET | the frame settling shut + one long hinge groan `pitch_env(1.2, f0=250, f1=90)` |

**The Applicant — photoform colony (emulsion, laminate, felt fibre, shutter).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (felt breathing) | `cr/applicant/idle` | 4.0 | P3 | yes | WET | felt-fibre breath `noise_band(4, 200, 500)` slow + laminate creak sparse |
| notice (aligns) | `cr/applicant/notice` | 0.5 | P5 | — | NEAR | fibre tick `modal((2200, 0.02, 0.3))` + emulsion-paper slide `granular(0.3, rate=60, band=(1e3,3e3))` |
| tell (the shutter) | `cr/applicant/tell` | 0.2 | P6 | — | DRY | **move after the shutter sound** (sheet): precise two-stage shutter — mirror tick `modal((2500, 0.01, 0.6))` then leaf click `modal((3500, 0.015, 0.7))`, 60 ms apart, perfectly dry |
| attack (lunge) | `cr/applicant/attack` | 0.8 | P5 | — | MID | opposed knee hinges re-stack: two sharp clicks + air whoosh `pitch_env(0.4, f0=600, f1=200)` |
| hurt | `cr/applicant/hurt` | 0.4 | P5 | — | WET | paper slap + fibre tear `granular(0.3, rate=100, band=(2e3,5e3))` |
| death | `cr/applicant/death` | 2.5 | P5 | — | WET | the photograph developing out: slow papery exhale `granular(2.0, rate=20, band=(500,2e3))` + one laminate settle |

**The Erratum — rejected-stair organism (mortar, steel fibre, treads, feelers).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (mortar breathing) | `cr/erratum/idle` | 4.0 | P3 | yes | WET | mortar breath `noise_band(4, 60, 200)` at 0.2 Hz + tread dust ticks |
| notice (feelers scrape) | `cr/erratum/notice` | 0.6 | P5 | — | WET | handrail feelers tracing `granular(0.6, rate=70, band=(1e3,4e3))` |
| tell (the line-trace) | `cr/erratum/tell` | 1.1 | P6 | — | NEAR | head lowers, feelers trace ~1 s: sustained chalk-like scrape `noise_band(1.1, 1e3, 3e3)` with falling pitch — the 1-second warning |
| attack (the ram) | `cr/erratum/attack` | 1.2 | P5 | — | MID | steel-fibre rush + tread clatter `granular(0.8, rate=150, band=(600,3e3))` + brick crunch `impact(0.5, f0=250→90, q=1)` |
| hurt | `cr/erratum/hurt` | 0.4 | P5 | — | WET | mortar crunch `noise_band(0.3, 300, 1e3)` |
| death | `cr/erratum/death` | 2.5 | P5 | — | WET | the stair coming apart: tread vertebrae settling one by one, descending ticks `modal((1600, 0.1, 0.4))` ×8, slowing |

**The Unaddressed — reader consortium (glass louvres, amber membrane, plaster, floor plates).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (louvre sway) | `cr/unaddressed/idle` | 5.0 | P3 | yes | WET | glass louvre fan sway `modal((1200, 0.5, 0.15))` at 0.2 Hz + plaster settling ticks |
| notice (membrane rustle) | `cr/unaddressed/notice` | 0.5 | P5 | — | NEAR | amber membrane rustle `granular(0.5, rate=60, band=(1e3,3e3))` |
| tell (the contract) | `cr/unaddressed/tell` | 0.9 | P6 | — | NEAR | it contracts first and shows where the strike lands: drawn-out glass drag `noise_band(0.8, 3e3, 5e3)` pitch rising + pressure-pad hiss |
| attack (sweep) | `cr/unaddressed/attack` | 0.8 | P5 | — | MID | front-limb sweep: glass scrape + mortar thump `impact(0.4, f0=200→80, q=1)` along the strip |
| the voice (plate taps) | `cr/unaddressed/plate1..3` | 0.3 | P4 | — | WET | the three grooved plates, pitched and readable (the puzzle is the voice): `modal((900, 0.3, 0.5))`, `(1100, 0.3, 0.5)`, `(1400, 0.3, 0.5)` — keep them clear in the still-pool chamber |
| hurt | `cr/unaddressed/hurt` | 0.4 | P5 | — | WET | glass shiver `modal((3800, 0.06, 0.4))` |
| death | `cr/unaddressed/death` | 2.5 | P5 | — | WET | louvres falling: descending glass arpeggio, each shard a different note |

### 5.2 Batch C (nullrun-lore-batch-c-20261101)

**The Visitor — the man who is still waiting (tweed, shoes, lino, the cough).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (waiting) | `cr/visitor/idle` | 6.0 | P3 | yes | WET | slow regular shoe scuff on concrete `granular(0.3, rate=30, band=(600,2e3))` every ~4 s + tweed seam creak `pitch_env(0.1, f0=500, f1=300)` + a faint dry cough into the cuff, rarely; the fluorescent hum does the rest |
| notice (palm on floor) | `cr/visitor/notice` | 0.5 | P5 | — | WET | palm sliding on the floor `noise_band(0.4, 600, 1200)` + one knuckle crack `modal((1600, 0.03, 0.4))` |
| tell (the cough + sleeve) | `cr/visitor/tell` | 0.7 | P6 | — | NEAR | **he coughs before every reach** (sheet): small dry cough `formant(0.15, f0=160, f1=800, f2=1500, breath=0.9)` + the sleeve falling back, a soft heavy cloth `noise_band(0.4, 300, 700)`. No growl, ever |
| attack (the reach) | `cr/visitor/attack` | 0.4 | P5 | — | WET | a dry fast scrape, like a chair leg pulled across lino `noise_band(0.25, 1e3, 3e3)` — no breath |
| hurt | `cr/visitor/hurt` | 0.5 | P5 | — | WET | whole-body flinch + an embarrassed breath `formant(0.3, f0=150, f1=600, breath=0.8)` |
| death | `cr/visitor/death` | 2.5 | P5 | — | WET | the jacket folding `granular(1.5, rate=15, band=(200,600))` + ONE shoe tap (single tick `modal((900, 0.05, 0.4))`) as the leg lets go; then the room tone. **The room gets quieter** |
| voice ("after you" / "sorry") | `cr/visitor/voice1..2` | 0.5 | P4 | — | DRY | a worn whisper, mostly air: `formant(0.5, f0=120, f1=500, f2=1100, breath=0.95)`; "sorry" ends on a fall |
| the hand taken | `cr/visitor/hand` | 3.0 | P4 | yes | WET | **no sting, no chord** (sheet): a single low cello note `modal((130.8, 1.5, 0.4), (261.6, 1.0, 0.15))` with a slow attack, held while he leads, stopping the instant he lets go |

**The Pleat — the lagging that holds (slate plates, yellow fibre, concrete block, bellows).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (bellows breath) | `cr/pleat/idle` | 4.0 | P3 | yes | WET | slow wet bellows `noise_band(4, 100, 400)` at 0.4 Hz + cooling-metal ticks `modal((2400, 0.03, 0.2))` sparse + fibre settling like sand in a bag |
| notice (beak click) | `cr/pleat/notice` | 0.4 | P5 | — | NEAR | beak click ×2, like a stapler (15 ms apart) + seam parting with a dry book-opening crack `modal((1800, 0.05, 0.5))` |
| tell (OPEN) | `cr/pleat/tell` | 1.3 | P6 | — | NEAR | long inhale through cloth `noise_band(1.2, 200, 800)` rising + plates unfolding like a fan of heavy card `granular(1.2, rate=60→140, band=(1e3,3e3))` + the fitting's pressure whine `pitch_env(1.2, f0=500, f1=900)` |
| attack (the slam) | `cr/pleat/attack` | 0.4 | P5 | — | NEAR | single low thump with **no echo** — a mattress hitting a floor `impact(0.12, f0=70→40, q=0.8)` baked NEAR so the zone cannot smear it + dust `granular(0.3, rate=40, band=(2e3,6e3))` |
| fold (recover) | `cr/pleat/fold` | 1.2 | P4 | — | WET | the fan closing, slower: plate clatter decelerating + a wheeze |
| swap (concrete) | `cr/pleat/swap` | 1.0 | P4 | — | NEAR | concrete on concrete, one clean knock `impact(0.3, f0=300→150, q=2)` + hook testing (scrape) + a second knock |
| hurt | `cr/pleat/hurt` | 0.4 | P5 | — | WET | plate crack `modal((2200, 0.05, 0.5))` + fibre puff |
| death | `cr/pleat/death` | 3.0 | P5 | — | WET | the fan opens all the way and stops: fibre sigh `granular(2.0, rate=25, band=(400,1e3))` + water starting to move below (distant drain swallow) + the block rolling free (one concrete roll) |

**The Span — the bridge that is still an animal (slabs, rebar, cable, the LOCK).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (concrete breathing) | `cr/span/idle` | 5.0 | P3 | yes | WET | slow gritty settle `granular(5, rate=8, band=(100,600))` + cable hum in a draft `modal((120, 3, 0.2))` with 0.5 Hz beating + whisker ticks against the ledge |
| notice (legs tap) | `cr/span/notice` | 1.0 | P5 | — | WET | rebar tapping stone, one leg at a time, like a surveyor's staff `modal((1400, 0.08, 0.4))` ×4 + a deep stone groan `pitch_env(0.8, f0=120, f1=80)` |
| tell (unfold) | `cr/span/tell` | 2.6 | P6 | — | NEAR | slabs sliding apart `granular(2.0, rate=30, band=(300,1e3))` + rebar creak + cable tightening, a high thin note `pitch_env(2.4, f0=1e3, f1=2.4e3)` |
| span (the clack) | `cr/span/span` | 1.0 | P5 | — | MID | long concrete-on-concrete clack `impact(0.3, f0=300→120, q=1.5)` + a wash of small settles |
| LOCK (the knock, then nothing) | `cr/span/lock` | 0.3 | P6 | — | DRY | ONE clean knock `modal((700, 0.1, 0.5))`, then nothing. **The nothing is the cue** — MIX.md ducks the bed 6 dB for 0.5 s after it |
| shudder | `cr/span/shudder` | 1.0 | P6 | — | MID | cable twang `modal((300, 0.8, 0.6))` + slab crack + dust falling `granular(0.6, rate=50, band=(2e3,5e3))`. No roar |
| lash | `cr/span/lash` | 0.5 | P5 | — | MID | rebar whistle `noise_band(0.2, 2e3, 5e3)` pitch-down + hooked foot biting wall (clang) |
| hurt | `cr/span/hurt` | 0.5 | P5 | — | WET | slab crack + dust |
| death | `cr/span/death` | 4.0 | P5 | — | WET | the arch failing from the middle: slabs hitting the lower ledge one after another (4–5 descending thumps) + the head last + a long cable sigh |
| the worker | `cr/span/worker` | 2.0 | P2 | — | WET | boots on slabs + a pencil on a card + a pat on stone. No dialogue |

**The Reunion — two people, one application (harness, stitches, two voices).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (out-of-phase steps) | `cr/reunion/idle` | 5.0 | P3 | yes | WET | two footstep sets out of phase, scuffing the same floor + leather harness creak + an occasional soft stitch pop `modal((1300, 0.02, 0.3))` |
| notice (both turn) | `cr/reunion/notice` | 0.5 | P5 | — | NEAR | one cloth rustle (both heads turn at once) + harness creak `pitch_env(0.25, f0=400, f1=250)` |
| tell (wishbone wind) | `cr/reunion/tell` | 0.7 | P6 | — | NEAR | **stitches popping in a row, like a seam giving** (sheet): 6–8 pops accelerating `granular(0.7, rate=30→90, band=(1e3,2e3))` + a shared inhale + leather groan `pitch_env(0.5, f0=250, f1=150)` |
| attack (the wishbone) | `cr/reunion/attack` | 0.7 | P5 | — | MID | two arms cutting air in opposite directions (two whooshes, panned apart) + harness snapping taut, a low thrum `modal((90, 0.4, 0.6))` + one grunt from each (two formants, a third apart) |
| tangle (recover) | `cr/reunion/tangle` | 1.0 | P4 | — | WET | a stumble + two apologies at different times (two whispers) |
| talk (disagree) | `cr/reunion/talk` | 3.0 | P4 | — | WET | two low overlapping voices, unintelligible, not shouting: two `formant` streams (f0 130 / 170 Hz) with overlapping envelopes |
| hurt | `cr/reunion/hurt` | 0.5 | P5 | — | WET | one flinches; the other is pulled by the harness and complains (short voiced exhale) |
| death | `cr/reunion/death` | 2.5 | P5 | — | WET | one body down, then the other a half-beat later + harness settling + the case tag ticking against the floor `modal((1500, 0.05, 0.25))` ×3 |
| the notice read | `cr/reunion/notice_read` | 2.0 | P4 | — | NEAR | paper unfolding `granular(0.4, rate=40, band=(1e3,3e3))` + two people reading at different speeds (two quiet breaths, offset) + one says "oh" (`formant(0.3, f0=170, f1=600, f2=1000)`); the other says nothing |

**The Ravel — the filter that hunts (glass shards, amber fibre, sinew).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (wet purr) | `cr/ravel/idle` | 4.0 | P3 | yes | WET | low wet purr `noise_band(4, 60, 180)` + glass shards clicking as it walks `modal((3e3, 0.05, 0.2))` sparse + fibre papery rustle + water dripping off the body |
| notice (the clicking stops) | `cr/ravel/notice` | 0.4 | P5 | — | NEAR | **the clicking stops** (drop the idle) + one shard ringing like a struck wine glass `modal((3800, 0.8, 0.4))` |
| tell (CHARGE) | `cr/ravel/tell` | 1.5 | P6 | — | NEAR | rising glass-harmonica note, thin and clear `pitch_env(1.5, f0=2e3, f1=5e3)` sine-based + fibre crackle like static in cloth `granular(1.5, rate=90, band=(3e3,6e3))` + feet plant (wet thump) |
| attack (BURST) | `cr/ravel/attack` | 0.7 | P5 | — | MID | single hard crack `noise_band(0.1, 1e3, 6e3)` + eight small whistles panned in the ring `pitch_env(0.3, f0=3e3, f1=1e3)` ×8 + glass tinkling into water + crest deflating like a paper bag `granular(0.3, rate=60, band=(800,1500))` |
| spent | `cr/ravel/spent` | 0.8 | P4 | — | WET | fibre hisses as it dulls + panting + shards rattling loosely |
| recover (re-ink) | `cr/ravel/recover` | 0.8 | P4 | — | WET | a soft repeating tick like a clock winding, accelerating `modal((2200, 0.03, 0.3))` |
| bite | `cr/ravel/bite` | 0.2 | P5 | — | WET | a wet snap, no growl |
| hurt | `cr/ravel/hurt` | 0.4 | P5 | — | WET | whole-body flinch + crest rattle |
| death | `cr/ravel/death` | 2.5 | P5 | — | WET | the crest falls shard by shard, each a different note (descending glass arpeggio, τ increasing) + the fibre going out with a sigh |
| docile | `cr/ravel/docile` | 4.0 | P3 | yes | WET | the purr slows to a hum + shards folded flat (no clicks) |

**The White Bloom — the filter that stands up (sponges, bone, water, the hiss).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (filtering) | `cr/bloom/idle` | 5.0 | P3 | yes | WET | water dripping through sponges + a slow wet pulse + pores crackling softly `granular(5, rate=8, band=(2e3,5e3))` + mandibles clicking like a filter grate |
| notice (the dripping stops) | `cr/bloom/notice` | 0.5 | P5 | — | NEAR | **the dripping stops** + one deep bubble `impact(0.3, f0=120→60, q=0.8)` + pores opening like a sponge squeezed underwater `noise_band(0.4, 800, 2e3)` |
| tell (DRAW) | `cr/bloom/tell` | 1.2 | P6 | — | NEAR | a kettle hiss rising `noise_band(1.1, 2e3, 6e3)` with level ramp + water sucking into the feet (low glug) + a low wet rumble under the floor |
| attack (BLOOM) | `cr/bloom/attack` | 0.9 | P5 | — | MID | hard wet crack + a dozen white tips punching through water (12 small impacts panned in the ring, 100 ms apart, pitch descending) + grit falling + the bloom flaring with a papery rush |
| settle (recover) | `cr/bloom/settle` | 1.2 | P4 | — | WET | spikes crumbling one after another, like sugar (decelerating granular ticks) + pores closing + a long exhale |
| snap | `cr/bloom/snap` | 0.2 | P5 | — | NEAR | bone on bone, a clean click `modal((2600, 0.03, 0.5))`. No growl |
| hurt | `cr/bloom/hurt` | 0.4 | P5 | — | WET | bloom shudder + a puff of white dust |
| death | `cr/bloom/death` | 3.0 | P5 | — | WET | the bloom collapsing inward + water spreading + legs folding + ONE last bubble |
| wilt | `cr/bloom/wilt` | 1.5 | P4 | — | WET | a dry papery shrink + feet hardening + the wet ring receding |

### 5.3 New sheets (nullrun-newsheets-lore-20261101)

**The Circuit — three bodies, one memory (porcelain ribs, cable, brass whiskers, tether).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (wire hum) | `cr/circuit/idle` | 5.0 | P3 | yes | WET | the wire's own hum `modal((120, 4, 0.2))` very quiet + whisker sweep ticks (brass on floor, sparse `modal((3e3, 0.02, 0.2))`). No voice, no mouth — ever |
| notice (whiskers snap) | `cr/circuit/notice` | 0.4 | P6 | — | NEAR | whiskers snap forward, a crisp fan-click `modal((2.8e3, 0.02, 0.5))` + **all three tethers snap taut**: low cable twang `modal((110, 0.5, 0.6))` ×3, 60 ms apart — the group-wide alarm |
| tell (trip wind) | `cr/circuit/tell` | 0.7 | P6 | — | NEAR | the tether lifts to 0.25 m and vibrates: rising cable whine `pitch_env(0.7, f0=200, f1=900)` + red bands flare (soft hiss) |
| attack (lunge / trip) | `cr/circuit/attack` | 0.5 | P5 | — | MID | lunge whoosh + cable snap; trip sweep = cable whistle `pitch_env(0.4, f0=600, f1=2e3)` |
| contact (the test) | `cr/circuit/contact` | 0.15 | P5 | — | NEAR | whiskers bend + a copper spark at the tips: tiny electric tick `modal((4e3, 0.02, 0.4))` — a tick, not a zap (the zap is the Husk's) |
| sever reaction | `cr/circuit/sever` | 0.8 | P5 | — | WET | the body touches the cut copper to the floor repeatedly: dry copper taps `modal((2.6e3, 0.03, 0.4))` ×3 + a faint arc tick each tap |
| hurt (isolated only) | `cr/circuit/hurt` | 0.3 | P5 | — | WET | flinch + pads skid |
| death | `cr/circuit/death` | 1.5 | P5 | — | WET | ribs fold inward + the tether end curls + ONE last spark; corpse: one lit whisker tip fading (a 4 kHz tone decaying over 3 s, extremely quiet) |

**The Underprint — the wall that has been leaned on (plaster, scrim, wallpaper, flakes).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (flat: a wall) | `cr/underprint/idle` | 6.0 | P2 | yes | WET | almost nothing: faint plaster micro-settling `granular(6, rate=4, band=(3e3,6e3))`. The pattern-break is visual; the sound is the absence |
| notice (crack + faces) | `cr/underprint/notice` | 0.5 | P5 | — | NEAR | a fine crack opens along one shoulder (two-stage dry click `modal((1.2e3, 0.03, 0.5), (2.4e3, 0.02, 0.4))`) + faces turning, a dry scrape like a page dragged over plaster |
| tell (DETACH) | `cr/underprint/tell` | 0.7 | P6 | — | NEAR | the wallpaper bubbles outward: wet paper stretch `noise_band(0.6, 300, 900)` rising + flakes starting |
| attack (burst / swipe) | `cr/underprint/attack` | 0.6 | P5 | — | MID | scattering flakes `granular(0.4, rate=180, band=(2e3,6e3))` + swipe whoosh |
| press (the big one) | `cr/underprint/press` | 1.4 | P5 | — | MID | the arm plates CRACK AND SHED before the blow (loud stone crack 0.5 s before impact — its own mini-tell) + heavy air + thump |
| shed | `cr/underprint/shed` | 0.5 | P5 | — | NEAR | a plate layer bursting outward: crunch + dust `granular(0.4, rate=120, band=(2e3,6e3))` |
| re-plaster | `cr/underprint/replaster` | 1.2 | P4 | — | WET | paint running toward it: wet slurp `noise_band(1.0, 400, 1e3)` |
| hurt | `cr/underprint/hurt` | 0.4 | P5 | — | WET | flinch + flake loss |
| death | `cr/underprint/death` | 2.0 | P5 | — | WET | the frame folds + the last plate sliding off the shoulder (one slow scrape) + a heap of flakes settling |

**The Hem — the woman on the bench (wool, sewing, the hem, the limbs).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| idle (sewing) | `cr/hem/idle` | 6.0 | P3 | yes | WET | **indistinguishable from a civilian**: needle through wool (soft tick `modal((1500, 0.02, 0.3))` every ~2 s) + cloth settle + a person's breathing |
| notice (sewing put down) | `cr/hem/notice` | 0.6 | P5 | — | NEAR | soft wood/wool set-down + **the hem shifts once, on its own, and settles** (sheet): a low cloth move `noise_band(0.4, 200, 500)` pitch-down — the first honest tell |
| tell (REVEAL) | `cr/hem/tell` | 1.3 | P6 | — | NEAR | she grips the skirt (cloth fist) + limbs unfolding one at a time: 6–8 soft joint pops accelerating, like a fan of bone knitting open `modal((900, 0.04, 0.3))` — not interruptible, so the sound must mark the free-damage window |
| attack (strike) | `cr/hem/attack` | 0.6 | P5 | — | MID | root bunching under the skirt (cloth creak) + the fixed three-beat flurry: three whooshes in rhythm |
| snare | `cr/hem/snare` | 1.6 | P5 | — | MID | palm opens flat (soft) + the limb lays itself out along the floor (slow scrape, 1 s) then SHOOTS (fast whoosh) |
| limb recoil | `cr/hem/recoil` | 0.6 | P4 | — | WET | the struck limb snaps back + weight shifting |
| hurt | `cr/hem/hurt` | 0.3 | P5 | — | WET | a person's flinch — a sharp breath. She does not scream |
| death | `cr/hem/death` | 2.5 | P5 | — | WET | limbs withdrawing under the skirt one at a time (descending clicks) + she folds down and comes to rest seated; corpse is seated. No scream, no monstrous voice |
| voice ("sit down" / "wait") | `cr/hem/voice1..2` | 0.6 | P4 | — | DRY | a normal woman's voice, quiet and calm: `formant(0.6, f0=190, f1=700, f2=1200, f3=2400, breath=0.2)`. The only fully intelligible voice in the game |

### 5.4 Optional bosses (nullrun-newsheets-lore-20261101/BOSSES.md)

**Continuity — Post 3 (the Circuit at boss scale).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| core hum | `cr/continuity/idle` | 5.0 | P3 | yes | WET | the switchboard core: `modal((60, 4, 0.3), (240, 3, 0.2))` + relay ticks |
| arc charge (tell) | `cr/continuity/tell` | 0.8 | P6 | — | NEAR | the core's ribs brighten for 20 ticks: coil whine `pitch_env(0.8, f0=1e3, f1=4e3)` + a rising 60 Hz swell |
| arc (attack) | `cr/continuity/attack` | 0.5 | P5 | — | MID | the species' one electrical discharge: massive crack (white burst, capped per MIX) + the core's hum flinching |
| sever | `cr/continuity/sever` | 1.0 | P5 | — | WET | tether twang + a terminal body's copper taps |
| lights out (×3) | `cr/continuity/lightout` | 0.5 | P4 | — | NEAR | the arena lights going out a pair at a time, in the order the pairs died: one click + that pair's hum stopping — the room gets quieter each time |
| death | `cr/continuity/death` | 3.0 | P5 | — | WET | the core opening like a panel: porcelain clack + the whole room's hum letting go |

**The Papered Room (the Underprint at room scale).**

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| the room watches | `cr/paperedroom/idle` | 8.0 | P2 | yes | WET | four walls of almost-nothing: one offset petal's rustle when you are not looking at it |
| four walls shed | `cr/paperedroom/shed` | 1.5 | P6 | — | MID | all four walls bursting at once: huge flake burst (four `granular` layers panned) + the giant's first foot |
| the giant | `cr/paperedroom/step` | 0.8 | P5 | — | WET | bass-heavy plaster crunch, pitched below the ordinary Underprint |
| plates taken | `cr/paperedroom/take` | 0.7 | P4 | — | WET | a distant crunch behind you — the wall you are not facing |
| armature exposed | `cr/paperedroom/armature` | 2.0 | P5 | — | WET | when the last wall is bare: the twine frame creaking, sustained |

## 6. World

Doors and gates follow the live game's conventions (threshold sector + NRGate 16500 + 'G' meta; boss
'B' meta seals). Door sounds are P4–P5, MID, and must land on the door's move ticks so the acoustic
zone change at the threshold is masked (ROOMS.md §3).

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| door — heavy leaf open | `wx/door/open` | 0.6 | P5 | — | MID | latch clack + metal leaf `impact(0.4, f0=300→120, q=2)` + dry runner |
| door — close | `wx/door/close` | 0.4 | P5 | — | MID | thud `impact(0.3, f0=180→70, q=1)` + rubber seal `noise_band(0.1, 400, 900)` |
| door — locked / denied | `wx/door/deny` | 0.3 | P4 | — | DRY | handle rattle `granular(0.2, rate=90, band=(1e3,3e3))` |
| door — seal driven (the Transit-12's job) | `wx/door/seal` | 0.7 | P5 | — | MID | lead seal driven: whack `impact(0.3, f0=400→180, q=2)` + lead slug thud + wax crumble |
| gate — NRGate hum | `wx/gate/hum` | 4.0 | P3 | yes | WET | low institutional hum `modal((100, 2, 0.2))` + 0.5 Hz shimmer |
| gate — open | `wx/gate/open` | 0.8 | P5 | — | MID | grind + clank `granular(0.5, rate=100, band=(800,3e3))` + `impact(0.3, f0=250→100, q=2)` |
| sigil — drawing (loop) | `wx/sigil/draw` | 2.0 | P5 | yes | NEAR | chalk/ink sweep `granular(2.0, rate=40→90, band=(1e3,4e3))`, pitch rising with progress |
| sigil — completion | `wx/sigil/done` | 1.5 | P8 | — | WET | the seal takes: low chime `modal((196, 1.2, 0.6), (392, 0.9, 0.4))` + the room answers (stratum bed swell +2 dB for 1 s) |
| sigil — fail | `wx/sigil/fail` | 0.3 | P4 | — | DRY | one dry tick |
| ghost feedback (the sigil's ghost) | `wx/sigil/ghost` | 2.0 | P2 | yes | WET | spectral tone layer `pitch_env(2.0, f0=1.2e3, f1=900)` at the visual's 0.30 cap — quiet, half-heard |
| lever | `wx/lever` | 0.3 | P4 | — | NEAR | clunk `impact(0.3, f0=400→150, q=2)` + catch click |
| lift — motor loop | `wx/lift/run` | 4.0 | P3 | yes | WET | motor + cable `noise_band(4, 150, 600)` + 2 Hz rumble |
| lift — arrival | `wx/lift/stop` | 0.5 | P4 | — | MID | clank + cable settle |
| pickup — Index (ammo cards) | `wx/pickup/index` | 0.4 | P4 | — | NEAR | paper stack tap `impact(0.2, f0=500→250, q=1)` + `granular(0.2, rate=70, band=(1e3,3e3))` |
| pickup — Seal cartridges | `wx/pickup/seal` | 0.4 | P4 | — | NEAR | brass cartridge clink ×2 `modal((2.6e3, 0.05, 0.4))` |
| pickup — Plumb charge | `wx/pickup/plumb` | 0.5 | P4 | — | NEAR | heavy lead thud `impact(0.4, f0=120→60, q=0.8)` |
| pickup — Lamp cells | `wx/pickup/cell` | 0.5 | P4 | — | NEAR | glass clink + faint hum `modal((4.2e3, 0.1, 0.3))` + `modal((120, 1, 0.1))` |
| pickup — supplies / mending kit | `wx/pickup/supply` | 0.4 | P4 | — | NEAR | cloth + paper `granular(0.3, rate=50, band=(500,2e3))` |
| pickup — key / tag | `wx/pickup/key` | 0.4 | P4 | — | DRY | brass on waxed string `modal((3e3, 0.08, 0.4))` + paper tag |
| vendor | `wx/vendor` | 0.4 | P4 | — | DRY | institutional click (dry, mechanical, not a cash register) `modal((2.2e3, 0.02, 0.4))` ×2 |

### 6.1 Ambience beds (one per stratum, P3, WET, loop, 60–90 s seamless)

| Bed | Name | Recipe |
|---|---|---|
| transit | `wx/amb/t0` | fluorescent hum `modal((120, 2, 0.3))` + 240 Hz buzz very quiet + sparse tube-flicker ticks (the 'L' meta sectors should each add a flicker tick) + distant platform thrum; **the hum is the stratum's voice** |
| ossuary | `wx/amb/o1` | dust settling `granular(60, rate=2, band=(3e3,6e3))` + very distant stone groans + the occasional far shelf knock; no hum |
| scriptorium | `wx/amb/s2` | distant water lap + bronze settling (rare `modal((700, 2, 0.1))`) + paper drift + a faint metallic shimmer |
| cistern | `wx/amb/c3` | the star bed: multi-distance drips (2–4 `modal((2.4e3, 0.4, 0.2))` + splash per loop, panned far) + water lapping + pipe groans `pitch_env(2, f0=90, f1=60)` + a distant pump every ~20 s |
| settling basin | `wx/amb/b3` | marsh: slow bubbles + sludge pops `impact(0.3, f0=150→80, q=0.7)` sparse + drips from height (long fall, late splash) + no insects |
| root cathedral | `wx/amb/r4` | deep groans + cable hum `modal((60, 4, 0.2))` + distant settles + near-silence in the still-pool chamber (a 6 dB quieter variant) |

### 6.2 Decor one-shots (P2/P1, WET-BAKE where the tail is the point)

| Sound | Name | dur | prio | loop | send | Recipe |
|---|---|---|---|---|---|---|
| drip (near) | `wx/drip/near` | 0.5 | P2 | — | WET-BAKE | droplet `modal((2.4e3, 0.3, 0.3))` + splash; the shaft version bakes the 0.14 s flutter (ROOMS C3 shaft) |
| drip (far) | `wx/drip/far` | 1.2 | P1 | — | WET-BAKE | same, lowpassed, with the zone's reflection delay baked long |
| pipe knock | `wx/pipe/knock` | 0.4 | P2 | — | MID | cast pipe `modal((900, 0.4, 0.5))` + ring |
| distant door | `wx/distant/door` | 0.8 | P1 | — | WET-BAKE | door close, lowpassed, tail baked |
| distant proclamation | `wx/distant/choraz` | 3.0 | P1 | — | WET-BAKE | a muffled Choraz attack, far, in the transit shaft |
| the hour (landmark) | `wx/hour` | 6.0 | P2 | — | WET-BAKE | the Hymnodyne's own chord, played far away once per level visit (scripted): the one sound the whole building agreed on |
| counterweight settle | `wx/weight` | 0.6 | P2 | — | MID | heavy counterweight drop `impact(0.5, f0=90→50, q=0.8)` + cable |

## 7. UI (P8, DRY, `$attenuation NONE`, never reverbed)

| Sound | Name | dur | loop | Recipe |
|---|---|---|---|---|
| menu move | `ui/move` | 0.05 | — | soft tick `modal((1800, 0.01, 0.4))` |
| menu confirm | `ui/confirm` | 0.12 | — | papery click `modal((2.4e3, 0.02, 0.5))` + low tap |
| menu back / cancel | `ui/back` | 0.1 | — | quieter, lower tick |
| pause | `ui/pause` | 0.25 | — | two ticks (in, out) |
| pickup log entry | `ui/log` | 0.2 | — | paper stamp `impact(0.2, f0=700→300, q=3)` |
| sigil progress tick | `ui/sigil` | 0.08 | — | ink tick, pitch per progress |
| hurt vignette | `ui/hurt` | 0.15 | — | low filtered knock, very short — keep it subtle |
| damage direction sting | `ui/dmgdir` | 0.12 | — | short band-limited pip panned to the hit direction, P5 (it is a tell for the player) |
| death sting / victory | — | — | — | owned by the adaptive music director (`player_death` / `run_victory`); no UI duplicate |

## 8. Notes and gaps

- **Boss roster.** The live roster rotates Repetiel, Calmor, Probator and Jurisiel; Probator and
  Jurisiel have no sheets on this machine, so they have no rows here. Give each a full six-state pass
  in their own material terms when their sheets arrive (same template as §5).
- **The four shipped loops** (`ld/app`, `ld/rep`, `ld/tell`, `ld/calm`) map naturally onto the
  Applicant's idle/attack/tell/calm set; keep or replace them, but do not reuse `ld/` for another
  creature — names are the API.
- **SNDINFO sketch** (one example per feature):
  ```
  $random pl/step/tile { pl/step/tile1 pl/step/tile2 pl/step/tile3 pl/step/tile4 }
  pl/step/tile1  sounds/pl/step/tile1.wav
  $volume   pl/step/tile1 0.8
  $limit    pl/step/tile 2
  $pitchshift pl/step/tile1 0.95 1.05
  $attenuation NONE ui/confirm
  cr/span/idle  sounds/cr/span/idle.wav    // looping flag set in the actor's A_PlaySound loop
  ```
- **Tick alignment.** 1 tick = 28.6 ms; round every duration to whole ticks at integration, and start
  tell sounds on the tell state's first tick (the sheets' state durations are authoritative for when
  sounds end).
- **Dignity rule carries into audio.** The Visitor, Reunion, Hem and Stone ReDead never get growls,
  roars or monster-voice treatments (their sheets forbid them); their deaths are quiet. The Hem's
  voice is ordinary; the Visitor whispers; the Reunion's two voices never shout.
