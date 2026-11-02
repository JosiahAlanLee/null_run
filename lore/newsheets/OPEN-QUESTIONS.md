# OPEN QUESTIONS — decisions only Josiah can make

**Status: nothing here picks an answer.** Each item gives the choice, the live options, and where my
proposal stands, so the proposal can be rejected without rewriting the rest.

## A. Origins and lore

1. **The Hem's origin.** I propose formerly human (premise 1 in its plainest form) and keep it open in the
   documents. Option B is a never-human mending organism in a coat. B would give the set three
   impression-organisms and spend the best thing on the sheet — that the woman is a person. **My
   recommendation: A, and never settle it in-game.**
2. **Underprint vs Applicant.** I propose no shared origin and the split "photograph vs palimpsest". Confirm
   or reject. If you want them related, the cheapest version is that the Underprint is what a photograph
   becomes after forty years of being painted over — I do *not* recommend it; it merges two good ideas.
3. **The Circuit's indifference.** It is not hostile until its wiring is disturbed. That is a lore choice
   with an engine consequence: the current roster may be hostile-only. Confirm whether a neutral/investigative
   state is allowed, or whether the encounter must be authored as aggression from the first frame.
4. **"Coils".** The works department's word for the Circuit, used in the documents. Keep, or give the office
   a different trade word? (Also: is there a works department at all, or only Works & Descent?)
5. **The child's coat.** If the player returns it, what happens? Options: she leaves; she takes her own coat
   off (and is then assessable); she stops waiting and sits down; nothing visible changes and the bench is
   empty next time. **I refuse to settle this**; whatever it is, it should be quiet.

## B. Encounter and systems

6. **Three-body AI.** The Circuit needs three actors, one group controller, a shared route/target table and
   an engine-side tether. Is that within the current NRMonster architecture, or does it need a new actor
   class? This gates the whole species, and it is the largest integration question in this package.
7. **Underprint regeneration.** It re-plasters at walls (90 ticks, one 60-point layer). Is regeneration
   acceptable in a Doom fight, or should the three shed windows be the only route and the repair be cut? My
   proposal keeps it because it makes the wall matter; cutting it is trivial if playtests hate it.
8. **The Hem's non-combat resolutions** (sit 30 s, talk, return the coat) assume interaction and dialogue
   that may not exist. If they do not, she is a non-hostile actor who blocks nothing and fights when
   provoked — still workable, but the best version is unavailable.
9. **The mending kit** is an undefined item. Do not build it until the item system does.
10. **The Circuit's lamp decoy and junction lever** change AI by shooting level lighting. The earlier
    generator proposal kept bindings strictly cosmetic in v1; this is a gameplay binding, not cosmetic.
    Decide whether lighting may drive AI at all.
11. **The trip attack** assumes a 0.25 m tether sweep and a 0.5 s stumble, no hold. If stumbling is not a
    native state, the trip becomes damage-only and loses its point.
12. **Dust obscuration** (Underprint shed, 25 ticks) is a screen effect. If that is an accessibility
    problem, it can become a 25-tick accuracy penalty or be removed; the shed's damage window does not
    depend on it.

## C. Sprite pipeline

13. **Per-actor span.** The proven bake is 8 m / 96 px per metre. The Circuit body needs ~2.0 m and the
    Underprint ~5.5 m; the Hem needs ~6.8 m unless her snare shortens to 2.2 m (which costs body resolution
    the other way). This needs a packer change and a native proof. **Decide the Hem's trade-off first** — it
    is a design number, not an art number.
14. **Resolution.** Full banks for the three come to ~4,600 PNGs and ~10.1 GiB resident at 768 px. I
    recommend a 512 px first-proof gate (~1.6 GiB). Confirm, or set a different budget.
15. **Naming.** Proposed actor letters C / P / M and the role letters in `SPRITE-ROLES.md` must be checked
    against `package_grid.py`'s 4-character namespace before baking.

## D. Placement and production

16. **Strata.** Circuit: 0 + 2 + the risers. Underprint: 0 + 1 (dry, repaired). Hem: 0 + 1 + 2 (seated,
    dry). The cistern is closed to the Circuit and the Hem; the cathedral is closed to the Underprint.
    Confirm these absences, since they are load-bearing for each species' identity.
17. **Which encounter gets the first proof?** My recommendation: **the Circuit trio in a service corridor**,
    because it tests the group AI, the tether renderer and the neutral state in one room. The Hem is the
    cheapest single-actor proof and would be my second. The Underprint is the most expensive per room.
18. **Boss.** A (`CONTINUITY — POST 3`) is recommended once the ordinary Circuit works; B (`THE PAPERED
    ROOM`) is a later set-piece. Also: the existing boss titles are personal names (Repetiel, Calmor,
    Probator, Jurisiel). A boss titled by *post*, with a vacancy in the personnel file, is a deliberate
    break in that pattern. Keep it or not?
19. **Scale confirmation.** All numbers assume 40 units = 1 m and a 320 u/s player run, inferred from the
    depth layouts and the Applicant's 3.4 m / 136 units. If the live build differs, every speed in this
    package rescales.

## E. What I could not settle alone

- Whether any of this belongs in the current build at all, or stays a design bank until the apocrypha
  encounters (Applicant, Erratum, Unaddressed) have their first native proofs.
- Whether the three creatures should know about each other in play (the Erratum dislodging an Underprint,
  a Husk severing a tether) or only in documents. I propose: documents first, one authored meeting later.
