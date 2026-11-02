# Maths, licences and engine references

The new shader implementations are AGPL-3.0-or-later. Their full editable GLSL and ZScript are supplied beside the PK3 and inside it. HydraPy's LICENSE identifies its derivative Hydra operators as AGPL-3.0-or-later; this output preserves that licence rather than implying the ports are permissively licensed. Hydra: Olivia Jack and contributors. HydraPy: the local project and contributors. See `AGPL-3.0.txt`. The copied game's existing GPL code and asset provenance remain in the package; this private build is not an asset redistribution approval.

All maths was read in Josiah's READ-ONLY `/home/echevarian/dev/hydrapy` checkout. No HydraPy file was modified or imported for rendering. The ports use bounded expressions, not HydraPy running inside Doom.

| Shader | HydraPy source actually read | Relationship and changes |
|---|---|---|
| sludge.fp | `hydrapy/ops.py`, `modulate` and `osc` | Coordinate displacement by two periodic fields, followed by interference modulation. Centred warp, tiny amplitudes, slow time. This is analytic domain warp, not reaction-diffusion or simplex noise. |
| water.fp | `hydrapy/ops.py`, `modulate`, `osc` | Two travelling coordinate waves and high-power interference peaks. Analytic caustic approximation, not physical photon caustics. |
| cracks.fp | `hydrapy/ops_paint.py`, `_np_crackle`, `crackle` | Retains nearest/second-nearest distances over nine sites. Replaces simplex warp and taper with slow sines; bounded width makes cracks breathe rather than permanently grow. |
| quasi.fp | `hydrapy/ops_quasicrystal.py`, `_np_quasifield`, `quasifield` | Five plane-wave projections at pi*k/5, normalized sum and narrow contour threshold. It is a quasiperiodic interference pattern, not a discrete Penrose tiling. |
| drift.fp | `hydrapy/signals.py`, `EntropyLock`, and `ops.py` modulate | Recurring 16-step deterministic hash stream with smooth interpolation. A Seq/EntropyLock-inspired approximation; it does not reproduce Fx reseeding or maintain a framebuffer feedback state. |
| emulsion.fp | `hydrapy/ops.py`, `grain`, `vignette`, `rings`; `ops_glitch.py` inspected for tracking effects | Pixel/time hash grain, radial mask and decaying radial displacement. Fringe, two-tap halation approximation, gate drift and crop marks are original bounded additions. There is no full-frame luminance pulse. |
| normal generation | `hydrapy/ops_material.py`, `normalMap` | Early proof used central differences of authored pack height. Final imported-asset normals/AO are Blender UV bakes; sprite maps are camera-space shading-normal emission passes. |

Version-specific primary sources downloaded locally under `upstream/UZDoom-5.0.3/`:

- [UZDoom 5.0.3 GLDEFS parser](https://github.com/UZDoom/UZDoom/blob/5.0.3/src/r_data/gldefs.cpp): material sprite support, normal/specular and complete PBR bindings, custom timer materials, PPShader declarations.
- [UZDoom 5.0.3 postprocess implementation](https://github.com/UZDoom/UZDoom/blob/5.0.3/src/common/rendering/hwrenderer/postprocessing/hw_postprocess.cpp): `PPCustomShaderInstance` supplies InputTexture and LastInputTexture, plus explicit resource textures; it does not bind scene depth to custom postprocessing. Internal SSAO DOES access scene depth; that is a separate path.
- [UZDoom 5.0.3 map loader](https://github.com/UZDoom/UZDoom/blob/5.0.3/src/maploader/maploader.cpp): `LoadLightmap`, experimental `-enablelightmaps`, version-zero ZLIB lightmap payload. This source inspection changed the initial hypothesis; lightmap support must not be dismissed based on older GZDoom advice.
- [ZDRay](https://github.com/Talon1024/ZDRay): built unmodified from the recorded local clone, CPU bake. `zdray/README.md` documents the actual fields used. Its source and COPYING are retained locally.

The user's held melt-shear and Poincare cathedral scenes were not read or reused.

## Copied sigil integration

`delivery-fx-caster.zs`, glyph data and NSG ribbon/pen sprites come from the completed private `shared/codex/nullrun-sigils-20261101/pass2/` proof. Its separate laboratory handler/maps are excluded. Local changes preserve placed position, call the emulsion handler only at successful cast completion, and replace the interruption lamp's alternation with monotonic fading. This is integration of the existing module, not new authorship of its glyph artwork. Original provenance remains with that source output.
