# The Uncollected Editions: second impression

A 212-page typeset volume: the sixteen records of the first impression, with an
apparatus of four annotating hands, sewn-in leaves, a seventeenth record held
closed, generated plates, and an appendix of cabinet and unplaced papers.
Work in progress; this commit records one iteration.

- `out/` the built PDF
- `src/` the records as machine-extracted from the first impression
- `raw/` the same after structural repair (`tools/fix_raw.py`)
- `notes/NN.txt` the apparatus per record: substitutions, footnotes, marginalia, thread arrows
- `front.typ`, `inter.typ`, `extra.typ`, `s17.typ`, `back.typ` the new writing
- `lib.typ` page furniture, hands, threads, blocks
- `art/gen_vector.py`, `art/gen_raster.py` the plates, drawn from fixed seeds
- `build/papers.typ` papers lifted verbatim from the lore bible by `tools/papers.py`
  (the bible itself is not in this repository; place it at `sources/LORE-BIBLE-20261124.md` to regenerate)

Build: `pip install typst numpy pillow contourpy`, install the fonts EB Garamond,
Old Standard, Junicode, TT2020, IBM Plex and Courier Prime, then

    python3 art/gen_vector.py && python3 art/gen_raster.py
    python3 tools/assemble.py && python3 tools/build.py

The build runs twice if needed so that the foot-of-page ledger ends on the last
page, and reports the page count; the binder's certificate requires 212.
