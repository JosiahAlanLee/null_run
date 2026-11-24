# The Uncollected Editions: fourth impression (collated)

A merge of two earlier iterations, 180 pages:

- the **text of the sixteen records** is lifted from the third impression
  (`../third-impression/`), which cut the early narrators' explanations and
  added physical evidence in their place;
- the **page design, plates, four-hand apparatus, sewn leaves and schedules**
  are the second impression's (`../second-impression/`).

Changes against the second impression: notes anchored to cut passages were
re-anchored or withdrawn; the appendix is reduced from 66 papers to the 28 that
a record or note cites; the binder's certificate, the "pages on no leaf" and
the foot-of-page ledger are computed from the real page count instead of being
fixed at 212.

`tools/collate/` holds the scripts that lifted the record text from the third
impression's PDF (`ex3.py`, `ex3b.py`), merged it with the second impression's
document blocks (`merge.py`) and repaired the result (`postfix.py`). They were
run from a scratch directory and their paths are absolute; treat them as a
record of the method. Everything else builds as described in
`../second-impression/README.md`.
