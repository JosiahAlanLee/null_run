# OPEN-QUESTIONS — decisions only Josiah can settle

**Status: these are genuinely open; nothing here picks an answer.** Each item names the contradiction or choice, the two or more live options, and where my proposals stand.

## A. The institution

1. **Name and role.** I invented the *Null Run Receiving Office (NRRO)* and three departments (Works & Descent, Records Amended, Persons Awaiting Assessment). Is the office name right? Does the office still operate, or is it as dead as the layers below and merely the newest ghost? The handoff leaves "institution / annex / city / several incompatible things" open; my docs assume an office that keeps filing and never admits what it houses.
2. **Does the office predate the descent?** STRATA.md lets both readings stand: the office built the transit (its claim) or only occupies it (the Keepers' claim). A settled answer would change every intake record's authority.

## B. The strata

3. **Flood: accident or verdict?** The cistern flood is currently triple-authored (pressure accident / deliberate "read too slowly" / always was water). Fine to keep unresolved in-game, but the *gauge prop* must pick a visual: I propose painted-at-highest-mark with three lower crossed-out growth marks.
4. **Five strata vs seven floors.** The current native game has seven floors; these five strata are the depth themes. Which two floors are not strata (repeats, sublevels), or do we need two more strata? My documents only tag the five.
5. **Who built what, canonically.** STRATA.md's Shelf-Keepers / Bronze Margins / Descent Works are all proposals. Any one of them could be folded into the office's own history instead of being independent orders — that choice changes the tone from "contending congregations" to "one institution arguing with its own past".

## C. The bestiary

6. **Hollow is missing here.** The author index lists thirteen sheets; twelve local sheets exist, and Hollow's new sheet is a private library link this machine does not have. Its entry needs a decision: write it from the older description (split-tree, chest face, four limbs folding to crawl) or wait for the new sheet. I covered only the twelve supplied sheets, as the brief asked.
7. **Origin assignments for the pre-existing mobs** (book demons, Hollow, Stone ReDead, Surveyor, Vore Spindle, Ballast Husk, Threshold Mimic) are open in the handoff. My intake records log each subject's self-identification and mark origin UNRESOLVED. Do you want any of these settled per creature, or left permanently unresolved (my recommendation: permanent, it is the setting's engine)?
8. **Surveyor's third leg.** The tripod study is art direction, not recorded anatomy. My intake explicitly says so. If the tripod becomes canon, the intake line must change.

## D. Prose and placement

9. **Redaction convention.** I use `██` in the NRRO records. That's the SCP-family convention; it is also unreadable on some in-game fonts. If Null Run's institution should have its own mark (e.g. a wax-seal stamp or a struck-through line), say so and I'll re-run `tools/build_documents.py` with it.
10. **Document numbering.** `DOCUMENTS/` ids are arbitrary. If documents should also carry a seed-visible number (so a run's generator can reference them), the id scheme needs to change from `doc-001` to something like `NRRO-44-C-001`.
11. **Which apocrypha are corroborated.** The five fictional apocryphal documents (The Maintenance of Persons, A Catalogue of Rooms Which Have Never Existed, The Unfinished Reader, On the Biography of a Substitute, desligar_hub_FINAL_agora_v8.nfo) hover behind several entries — "awaiting assessment", the wall that corrects toward a drawing, the reader consortium, the two-signature transfer slips. Does Josiah want the apocrypha named in-game as bootleg texts, or left as invisible scaffolding? I left them unnamed.
12. **Tone mix.** Clinical restraint (NRRO) and ceremonial excess (orders) are both present. Per-room proportions are open: the handoff asks us not to give every room the same explanation.

## E. Items and generator

13. **Items presume future systems.** ITEMS.md is designed for perk drafts/shops that do not exist in the current build ("no perk drafts, persistent unlocks, shops or save slots in this first build"). Accept the items as a design target, or wait until those systems land?
14. **Generator bindings.** GENERATORS.md binds one story element per stratum to real props (door 44, alcove seal, room-6 plates, gauge, growth marks). Are those bindings allowed to touch vendor stock or seal states, or strictly cosmetic in v1? I propose strictly cosmetic in v1.
15. **Seed stability.** Should a retry of the same seed reproduce the same history? I propose yes, with a version string in the run manifest.

## F. What I could not settle alone

16. The *player's identity* and *why they descend* remain entirely open (as in the handoff) — none of my documents state it, and a few (the waiting-room slip, the uniform) flirt with it. They should be revised once Josiah decides.
17. Whether any ordinary human communities remain, or anyone stays voluntarily — untouched here, deliberately.
