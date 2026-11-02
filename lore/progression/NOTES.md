# NOTES — risks, open questions, prototype order

**Status: notes only.** Nothing here is settled.

## 1. Risks and the guards I built against them

1. **Grind — the heap as a vending machine.** The lore pack already flags this (ARMATURE NOTES §9): the
   common mob must not become a farm. Guards: kill-method gating (the valuable yield requires the risky
   surgical kill), harvest noise (12 m wake, and kills already wake packs within 15 m), encumbrance (you
   cannot carry a farm), the one-node-per-stratum craft pace, and the offerings as a non-grind source of
   rare materials. Watch for the case where the player farms free Armatures in a room with a safe corner;
   the noise rules exist to make that corner unsafe.
2. **Power creep.** Guards: Integrity 20 (hard cap of 10 nodes), taxes that do not wash out (pain 7+
   is real; 20 kg is real), maintenance decay on upgrades, per-run reset with no stat carry-over, and the
   refusal line that stops mono-builds at seven. If a node's tax is cheaper than its benefit in play,
   raise the tax, not the cost — the taxes are the character.
3. **A dominant tree.** Guards: slot-level opposition (each slot offers both answers), five cross-tree
   synergies that reward mixing, different problem sets (upgrades fight weight and noise; mutations fight
   drift and oddities), and the endings: pure builds win power and lose the exit. The file must warn the
   player before the seventh node, or the lock-out reads as a trap.
4. **Photosensitivity.** Every oddity is a slow cue, a false sound or a ≤ 0.5 Hz glint; no flash, no
   strobe, no whole-frame jump (PILLARS §5). The Crest Filaments' outline and the Works Body's ending
   states must be reviewed against the safety rules before implementation.
5. **Pain as a resource.** Pain is a meter of wear (tremor, desaturation, slower raise), never reward
   imagery, never a bar to optimise for its own sake. The offering "give pain for a core" is the closest
   the design gets to self-harm-as-currency; if that reads wrong, swap it for drift. (For Josiah.)
6. **Drift and dignity.** Drift must not mock the inhabitants — no "you become a monster" comedy; the
   resident ending is quiet and observational. No harvest from former humans, ever, including the
   Applicant's face plate (photograph of a person; yield comes from the torso laminate). The
   Colony's Rhythm (creatures hesitate) must not trivialise the panic spike; it buys 1.5 s, not immunity,
   and controlled Armatures check you twice.
7. **Rejection readability.** Same-limb −25% is deterministic and warned, not rolled; a random failed
   craft would read as the game eating materials. If the −25% penalty is invisible in play, the rule
   becomes flavour; if it is too visible, mixing feels punished. Tune the symptom (tremor, seepage, noise)
   to be the visible half.
8. **The two endings as "losses".** If the works-body and resident endings are read as fail states,
   players will never take them and the tree ends become dead content. They should be filed endings with
   their own unlock lines (see RUN-STRUCTURE §3.2), presented as what they are: the discipline completed,
   and the exit closed.

## 2. Open questions for Josiah

1. **Integrity 20, 2 per node** — right cap for a 5-stratum run? At one node per stratum the cap is only
   felt by completionists; that is intentional.
2. **Same-limb mixing:** deterministic −25% + symptom (recommended), or hard refusal like same-slot?
3. **Dry-stratum penalty** on Woven Repair and the damp rooting bonus — keep, or make mutations
   stratum-neutral for simplicity?
4. **The climb back.** Should the run end at the still pool (recommended for now), or should the player
   climb back out through the five strata, with the turnstile as the true exit? The Purgatorio argues for
   the climb; it costs five more floors of game.
5. **Offerings:** once each per run (recommended) or re-rollable per stratum?
6. **The stores case:** can the player lose it by dying in a room they left it in, or does it return to
   the stratum landing (recommended: it stays where you left it; the map marks it)?
7. **The Applicant's face plate:** confirm no face harvest (recommended).
8. **Seed entry:** allow typing a case number at the desk, or only the last three on the board?
9. **The Works Body's Spindle-as-host twist:** colony cores can lodge in you. This is the strongest
   mechanical consequence in the doc — keep it, soften it, or cut it?
10. **Kill-method harvest on creatures beyond the Armature** (Spindle, Applicant, Erratum): the doc
    assumes any-kill yields; should surgical vs brutal apply to all of them, or stay Armature-only
    (recommended: Armature-only first)?
11. **Drift threshold 8 locking the workbench:** if the player has upgrades that need maintenance at
    drift 8, they decay with no repair. Intended (the cost of drifting) — confirm.
12. **The Hollow's fibre** is listed but its sheet has not reached this machine; the yield line is a
    placeholder until the sheet arrives.

## 3. Prototype first

1. **The Armature kill-method table** (MATERIALS §1): one creature, two kill outcomes, the kneel-harvest
   action with its 12 m noise. This is the core loop; everything else hangs on it.
2. **One slot pair — HANDS:** Wrist Tensioners vs Grip Fibres, one bench and one tray on stratum 0.
   Validates the budget, the stations, the install/rooting asymmetry, and the taxes.
3. **Encumbrance thresholds** (MATERIALS §2) on the existing movement: satchel + case, three thresholds.
   Cheapest way to prove the physicality pillar in-engine.
4. **The waiting-room FILE** as a paper prototype: endings, node diagrams, start options, case numbers.
   The meta-game must read before any of it is built.
5. **One stratum's fork structure:** two routes, one station each, one offering, one gate — to feel the
   "four decisions" pacing before committing to five strata of it.
