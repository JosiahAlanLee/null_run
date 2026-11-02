# SPRITE ROLES — bake table for the pitch-aware pipeline

**Status: PROPOSAL.** Consolidated production table for the three new sheets. It assumes the pipeline that
was proven on the Applicant (`shared/codex/nullrun-sprites-20261101/`): 5 elevation bands (−45, −20, 0,
+20, +45°) × 8 yaws = **40 views per sample**, 768 px square, one world-origin pivot per band, no
per-pose re-centring, `FORCEXYBILLBOARD` + zero-roll `ROLLSPRITE`, `gl_spriteclip 0`, and a generated
`sprite-catalog.zs` so dynamic `GetSpriteIndex` names resolve.

## 1. One bank, not one per body

The three Circuit bodies are the same anatomy, so they share **one** bank and three actors use it. The hub's
split tether root does not need a second bank: both tethers are engine geometry and can leave the same root
collar. The sheet's `tether root` view is satisfied by the two tubes, not by the sprite.

The tether itself is **not bakeable**. A 12 m tether cannot be billboarded with the bodies; it must be
engine-side geometry (a tube or segment chain) drawn between actors. This is a new renderer/AI cost that the
Applicant proof does not cover, and it is the first question in `OPEN-QUESTIONS.md`.

## 2. Framing, span and pivot per actor

The pipeline's proven bake uses an **8 m span** and 96 px/m. That is right for the Applicant (3.4 m) and
wrong for two of these three. Span must be chosen per actor by the **largest pose extent from the pivot**,
because a sprite frame contains the pose, not the world displacement:

| Actor | Largest pose extent from pivot | Span proposed | px/m | Body on canvas | Pivot z | Band-0 grAb y |
| --- | --- | --- | --- | --- | --- | --- |
| Circuit body | ~1.0 m (whiskers forward) | **2.0 m** | 384 | 0.9 m ≈ 346 px | 0.45 m | 557 |
| Underprint | ~2.6 m (swipe reach) | **5.5 m** | 140 | 2.2 m ≈ 308 px | 1.30 m | 566 |
| Hem | ~3.0 m (snare reach) | **6.8 m** | 113 | 1.7 m ≈ 192 px | 1.05 m | 503 |

`grAb = (384, round(384 + pivotZ × cos(elevation) × pxPerMetre))`, constant across frames and yaws within a
band. The 8 m span would put the Circuit body at 86 px and lose the whiskers — the detail the encounter is
built on. A **per-actor span** is therefore a required change to the packer and to the actor's scale, and it
needs its own native check before any of this is baked at scale.

**Hem trade-off (Josiah's call):** 6.8 m span keeps the full 3.0 m snare and costs body resolution
(192 px). A 5.0 m span with a shortened 2.2 m snare gives 261 px for the body. The snare's reach is also an
encounter number, so this is a design decision, not only an art one.

## 3. Role and sample table

| Creature | Actor letter | Roles (letter: samples × ticks) | Samples | PNGs |
| --- | --- | --- | --- | --- |
| Circuit | `C` | I 4×7, W 4×7, N 3×7, K 2×6, L 3×7, B 4×8, E 3×9, Q 4×10, H 2×4, D 4×5, X 1 | **34** | 1,360 |
| Underprint | `P` | I 4×8, W 3×9, N 3×6, D 4×11, B 3×9, F 3×10, S 3×5, G 5×16, E 3×7, M 3×31, H 2×5, X 3×11, C 1 | **40** | 1,600 |
| Hem | `M` | I 6×10, N 3×8, V 5×9, G 4×8, K 4×4, S 4×5 + 3×14, L 2×11, H 2×5, A 2×8, D 5×7, X 1 | **41** | 1,640 |
| **Total** | | | **115** | **4,600** |

Role letters are proposals and collide with nothing in the Applicant's set (`I N C T L R H D X`); the
Applicant's actor namespace is `N`. Naming follows `[actor][band][role][variant]` + standard frame letter
+ rotation, e.g. `C2KA1`. **Check every name against `package_grid.py`'s manifest before baking** — a
4-character sprite name with 5 bands × 11 roles × 3 actors is a small namespace, and a silent collision
produces an invisible or wrong-band sprite.

## 4. Memory and pack cost

Measured from the Applicant delivery: one 768² PNG is 2.25 MiB resident uncompressed, and the 1,280-PNG pack
was ~68 MiB (≈53 KiB per PNG compressed).

| | Samples | PNGs | Pack (est.) | Resident (est.) | At 512 px resident |
| --- | --- | --- | --- | --- | --- |
| Full set, 768 | 115 | 4,600 | ~238 MiB | **~10.1 GiB** | ~4.5 GiB |
| First-proof gate, 768 | 40 | 1,600 | ~83 MiB | ~3.5 GiB | ~1.6 GiB |

**Recommendation: bake the first gate at 512 px.** 1,600 PNGs at 512 is ~1.6 GiB resident, which is the
only version I would put in a level before streaming/precache behaviour is measured. The Applicant's
2.81 GiB for one creature was already flagged as a production risk; three creatures at full bank is
roughly the whole budget.

## 5. First-proof gate (per creature, ~13 samples)

| Creature | Gate roles | Samples | PNGs |
| --- | --- | --- | --- |
| Circuit | I 2, W 2, N 2, L 2, E 1, H 1, D 2, X 1 | 13 | 520 |
| Underprint | I 2, W 2, N 2, D 2, E 2, H 1, X 2, C 1 | 14 | 560 |
| Hem | I 2, N 2, V 2, S 2, K 1, H 1, D 2, X 1 | 13 | 520 |
| **Total** | | **40** | **1,600** |

The gate exists to prove legibility in the real camera: pose silhouette, ground contact, pivot, band
transitions, and the one tell each encounter depends on (taut tether, pattern break, open palm). It is not a
finished bank, and it should not be presented as one.

## 6. Bake-specific notes

- **Circuit.** Ground contact is on pads, not hooves: the pad must sit at z = 0 in every band and every yaw,
  including the trip brace (body low, pads planted). The whiskers are 0.3–0.5 m long and 1–2 px wide at
  192 px/m — check they survive at gameplay distance before approval; if they vanish, the encounter's
  sensing tell is invisible and the design fails, not just the art.
- **Underprint.** The detach and shed frames must include the **wallpaper behind the body** as part of the
  pose? No: the wallpaper is level geometry. The sprite must read as a body-shaped gap only where the level
  provides one. Do not paint wallpaper into the sprite. Death and corpse lift all vertices above the floor,
  as the Applicant rig did.
- **Hem.** The ordinary loop must be indistinguishable from a civilian NPC at 8 m. The civil-NPC comparison
  belongs in the review sheet. The +45 band correctly hides the limbs under the skirt; the snare must still
  read from above as limbs beyond the hem. Seated poses leave headroom under one fixed pivot — do not
  re-centre them.
- **All three.** Neutral lighting, no painted cast shadows, no per-pose scale changes. Death poses must not
  clip the canvas at ±45°; check every death frame's alpha bounds before packaging.
