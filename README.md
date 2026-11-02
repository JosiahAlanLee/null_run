# Null Run

An original survival-horror roguelike built on [UZDoom](https://github.com/UZDoom/UZDoom) and Freedoom.
"Rogue + Doom + Quake + Minecraft + generative art + a grimoire": Doom from someone who read the Purgatorio at 14.

This repository holds the game's source, tools and design, made by Josiah Alan-Lee with a team of AI
agents (Claude Code, Codex, DeepSeek and Argon/Gemini) working under his direction. It is meant to be
read, taken apart and reused.

## What is here

| Folder | Contents |
|---|---|
| `design/` | The design pillars, the engine-fork wishlist and status, scoping reports, and maths reviews. |
| `game/cistern/` | The CISTERN vertical slice: ZScript gameplay (`src/`), the UDMF map and the build scripts that generate it, and the v7 review and playtest notes. |
| `tools/levelgen/` | The cyclic level generator with its completability proof (no soft-locks), and the 32-template cistern chunk library with its validator. |
| `research/argon/` | Maths and simulation studies (fog reprojection, debris, locomotion, steering, generators), each with tests. |
| `shaders/hydrapy-derived/` | GLSL material and post-process shaders adapted from [HydraPy](https://github.com/JosiahAlanLee/hydrapy) (AGPL-3.0). |
| `lore/` | In-world text: signage, found documents, the self-writing ledger, creature lore, the sound bible. |

## Not here (yet)

Creature art (sprites, sprite banks, models) is unfinished and is not in this repository. Game binaries
and the Freedoom IWAD are not included: get Freedoom from <https://freedoom.github.io/>, and UZDoom
from its project. The engine fork lives in its own repository.

## Licence

Josiah's original code and text: GPL-3.0 (see `LICENSE`). Third-party parts keep their own licences;
see `THIRD_PARTY.md`.
