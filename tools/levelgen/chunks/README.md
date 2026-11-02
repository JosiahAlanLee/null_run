# nullrun-cistern-chunks-20261102 — CHUNK LIBRARY for the CISTERN stratum

DeepSeek worker job 20261102-125236 for Claude Code. Everything in this folder is
a PROPOSAL; nothing was pushed, posted or merged.

## Files

| File | Contents |
| --- | --- |
| `chunk_library.json` | 32 chunk templates: 22 real slice rooms, the harvested Freedoom chunk, 9 new templates. Argon-compatible field names plus the brief's richer fields (footprint polygon, sockets with normals, light bands, mechanisms, encounter suitability, rarity weights, landmark text). |
| `validate_library.py` | Validator: sockets on boundary with outward normals, widths >= 128 u, headroom >= 60 u, risers <= 24 u, simple polygons, pillar/baffle placement, encounter and mechanism consistency, per-tag census. Standard library only. |
| `NOTES.md` | Purgatorio terrace logic, panic rules, approximations from the real map, decisions, open questions. |
| `validation-run.txt` | The validator's actual output. |
| `build_library.py` | Reproduces `chunk_library.json` from the slice geometry (self-checking). |
| `derive_slice.py` | Derivation of module footprints/interfaces from `geometry_v5.py` cells (provenance). |
| `geometry_v5.py`, `routing.py`, `udmf.py`, `import_chunk.py`, `harvest.py`, `harvest-source/` | Read-only copies of the slice's geometry sources, used for derivation. |

## Run

```
python3 validate_library.py        # validates chunk_library.json
python3 build_library.py           # rebuilds the JSON and re-validates
```

## Conventions (see `meta` in the JSON)

UZDoom map coordinates (+x east, +y south). Socket normal degrees: 0 = east,
90 = south, 180 = west, 270 = north, always outward. Socket width >= 128 u,
step riser <= 24 u (slice risers are 8 u), headroom >= 60 u. `tags` is a JSON
list; pass `tuple(tags)` to Argon's `ChunkTemplate`.
