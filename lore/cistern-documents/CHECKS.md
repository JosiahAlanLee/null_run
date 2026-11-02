# Checks — DOCUMENTS.md

Run 2026-11-02 by the DeepSeek worker, locally, with Python 3. No network, no engine.

## Line length

- 30 fenced code blocks: 8 ledger entries (3 lines each), 6 inspection tags (3), 4 notices (4),
  6 pickup labels (3), 6 gauge-card sides (3).
- **0 lines over 38 characters.**
- Longest line: 34 characters — `IF IT KEEPS TIME, IT IS NOT ALONE.`

## Counts

- 27 documents: 8 ledger + 6 tags + 4 notices + 6 labels + 3 gauge cards.
- 27 `Max line: 38` statements (one per document; a gauge card's two sides share one statement).
- 27 rows in the placement manifest (§6).
- Last ledger block:
  - `CISTERN CLOSED — BALANCE`
  - `CARRIED FORWARD`
  - `REGISTRY NR-311-R — PRESENT`

## Duplicate check

Compared every in-world line (normalised to uppercase, punctuation stripped) against:

- `../nullrun-cistern-text-20261102/*.md`
- `../nullrun-text-20261101/*.md`
- `../nullrun-lore-20261101/DOCUMENTS/*.md`
- `../nullrun-progression-20261102/*.md`

**0 exact duplicate lines** longer than 8 characters. This is an exact-line check; it does not catch
paraphrase or shared motifs, which are deliberate (the water datum, the stander, R.D.).

## Not checked

No visual, texture-size, font-metric or engine test was run. The 38-character limit is a text
constraint, not a proof that the line reads at a given distance on a given canvas.
