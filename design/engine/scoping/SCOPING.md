# UZDoom fork: feasibility scoping of the engine wishlist, items 2–18

Scope: read-only research against `~/dev/uzdoom-nullrun` at commit `17480c8`
("Import UZDoom 5.0.3 source release", GPL-3). Item 1 (scene depth for custom
post-process) is being implemented by another agent and is skipped. All file,
function and line references are as of this source. Nothing here was compiled
or run. Things I could not confirm in the source are marked **unconfirmed**.

Renderers in this tree: OpenGL (`src/common/rendering/gl`), OpenGL ES
(`src/common/rendering/gles`, shares the GL code), Vulkan
(`src/common/rendering/vulkan`), and a software renderer
(`src/rendering/swrenderer`). "HW" below means GL+Vulkan (and GLES). Both
backends share the same scene code in `src/rendering/hwrenderer/`.

---

## Item 2 — Sight and sound through rotated line portals

### Touch points
- `P_CheckSight`: `src/playsim/p_sight.cpp:840-951`. Positions are transformed
  with `AActor::PosRelative()` (`src/playsim/actorinlines.h:26-43`), which adds
  **only the group displacement** (`Level->Displacements.getOffset(...)`).
- `SightCheck::PTR_SightTraverse` (`p_sight.cpp:210-384`) queues portal
  continuations in `portals` (`p_sight.cpp:281-292`) using
  `backsec->GetOppositePortalGroup()`; no angle is carried.
- The rotation data already exists: `FLinePortal::mAngleDiff/mSinRot/mCosRot`
  (`src/playsim/portal.h:209-211`) and the transform helpers
  `P_TranslatePortalXY/VXVY/Angle/Z` (`src/playsim/portal.cpp:443-520`), which
  are used only by actor movement (`p_mobj.cpp` TryMove path).
- Hitscans: `P_AimLineAttack` (`src/playsim/p_map.cpp:4523`),
  `AimTraverse`/`AimTarget` (`p_map.cpp:3846-3933`), `P_LineAttack`
  (`p_map.cpp:4649-4982`). Portal handling in the aim path uses
  `EnterSectorPortal` / `exitsec->GetOppositePortalGroup` (p_map.cpp around
  4250-4320); line-portal traversal carries displacement only.
- Sound propagation (wake-up): `P_RecursiveSound` (`src/playsim/p_enemy.cpp:145-213`),
  `P_NoiseAlert` (`p_enemy.cpp:228-245`). Line portals are honoured only as
  sector adjacency via `PORTF_SOUNDTRAVERSE` / `port->mDestination->frontsector`
  (p_enemy.cpp:168-176); the `maxdist` test uses `actor->Distance2D(emitter)`
  (p_enemy.cpp:133) in un-rotated world space.
- Spatial audio: `DoomSoundEngine::CalcPosVel` (`src/sound/s_doomsound.cpp:1022-1138`)
  repositions every source with `primaryLevel->Displacements.getOffset(...)`
  (lines 1050, 1069, 1088, 1113) — displacement only, no rotation. The renderer
  does rotate (see "existing support"), so sound directions/attenuation are
  wrong exactly where sight is wrong.

### Design
Reuse the existing portal-traversal machinery (`FPathTraverse`,
`src/playsim/p_maputl.h:394`, `FLinePortalTraverse`,
`src/playsim/portal.cpp:112`) the way the renderer already does: when a trace
crosses a linked portal, push a task that records the crossed `FLinePortal`;
on the far side, rotate the trace direction (and the source position around
the portal line) by `mSinRot/mCosRot` and add `mAngleDiff` to any carried
angle, exactly mirroring `P_TranslatePortalXY/VXVY/Angle`. For `P_CheckSight`
the rotated source point must be recomputed per continuation (`SightTask`
gains `double rot[4]` or the portal pointer).
For `P_RecursiveSound`, rotate the emitter's position per portal hop for the
`maxdist` check. For `CalcPosVel`, rotate the source position around the portal
chain before handing the final position to OpenAL (listener stays put; each
source is folded through its portal path once, cached per sound update).
Opt-in behaviour change? No: it is a correctness fix, gated by
`port->mAngleDiff != 0` so maps without rotated portals take the identical
old code path (zero cost).

### Effort and risks
- Effort: **L** (one correctness fix, three consumers, but subtle geometry).
- Risks: demo sync — all three consumers are playsim-deterministic, so a pure
  function of map data + positions stays demo-safe; the portal path a trace
  takes must remain stable (it already is, it is derived from geometry, not
  timing). Savegames: nothing new serialized if rotation is recomputed from
  `FLinePortal` each use. Multiplayer: no net protocol change. Performance:
  `P_CheckSight` is hot; the rotation math is 4 adds/muls per portal crossing,
  negligible.

### Already partly exists
- Yes. The renderer applies portal rotation correctly: `SetPortalRotation` /
  `mSinRot/mCosRot` use in `src/playsim/portal.cpp:200-230` and the GL/Vulkan
  portal code consumes `mAngleDiff` (portal transforms in
  `src/rendering/hwrenderer/scene/hw_portal.cpp`). Movement through portals is
  correct (`P_TranslatePortal*`). Argon's ZScript unfolded-ray maths is the
  workaround (`Actor.CheckSight`, `wadsrc/static/zscript/actors/actor.zs:918`).
  Only the engine's own LOS/hitscan/sound paths ignore rotation.

### Upstream-friendliness
High — this is a bug-completeness fix in GZDoom's own architecture; upstream
GZDoom has the same gap (portal rotation is renderer-only). The change is
local to three files and demonstrably correct with rotated-portal test maps.

---

## Item 3 — Per-pixel sprite hit testing + weak-point region masks

### Touch points
- Hitscan actor hit: `P_LineAttack` (`src/playsim/p_map.cpp:4649-4982`); the
  thing-hit branch is ~4868-4956, where `trace.HitPos` (from `FTraceResults`,
  `src/playsim/p_trace.h:56-81`) is known and `P_DamageMobj` is called
  (`p_map.cpp:4941`). `P_AimLineAttack` (`p_map.cpp:4523-4640`) picks the target
  first; the pixel test must not change *aiming* (target choice) but may change
  *damage resolution* — see risks.
- Victim data carrier: `FTranslatedLineTarget`
  (`src/playsim/actor.h:1822-1828`) — extended by item 16.
- Sprite frame lookup for UV computation: `spritedef_t::GetSpriteFrame`
  (`src/r_data/sprites.cpp:62-91`), `spriteframe_t` (`src/r_data/sprites.h:37-42`),
  `FTexture::GetBgraBitmap` / `Get8BitPixels`
  (`src/common/textures/textures.h:272-273`) for CPU-side texel reads.
- Damage entry: `P_DamageMobj` (`src/playsim/p_interaction.cpp:1584`), ZScript
  virtual `DamageMobj` (`wadsrc/static/zscript/actors/actor.zs:912`).

### Design
New opt-in actor flag (e.g. `+PIXELHITTEST` / MF9 bit) plus a GLDEFS/ZScript
way to name the region-mask texture per sprite frame (region ID stored in one
channel, e.g. red, of a mask texture mirroring the frame's layout; fallback:
alpha channel of the sprite itself). In `P_LineAttack`'s thing-hit branch, when
the victim has the flag: compute the local UV of `trace.HitPos` on the
billboard quad (project the hit point into the sprite's `x1/x2/y1/y2` quad as
`HWSprite::CalculateVertices` does, or reuse `FTranslatedLineTarget`'s new hit
data), fetch the texel from a lazily cached per-frame `FBitmap` (keyed by
`spritenum+frame+rot`, built once via `GetBgraBitmap`), and either reject the
hit (alpha below threshold) or attach `{regionID, texelUV}` to the damage call.
Region/UV ride item 16's new damage parameters into `P_DamageMobj` and the
ZScript `DamageMobj` virtual (optional named args, default behaviour identical
to today). Zero cost when the flag is off (one flag test).

### Effort and risks
- Effort: **M** (most logic is the UV math + bitmap cache; hook points are two).
- Risks: demo/multiplayer — deterministic (pure function of positions and
  static textures) so safe; but **must not alter aiming** (only post-hit
  resolution) or monster behaviour subtly changes in demos. Savegames: cache
  is rebuildable, nothing serialized. Performance: bitmap decode happens once
  per frame per sprite (lazy), hit-test reads are O(1); keep an LRU cap for
  mods with huge sprite sets.

### Already partly exists
- `WorldHitscanPreFired/WorldHitscanFired` events (`wadsrc/static/zscript/
  events.zs:189-190`, `EventManager::WorldHitscan*` in `src/events.cpp`) let
  ZScript observe hitscans but not veto or refine the hit cheaply.
- ZScript `LineTrace` already returns `HitLocation/HitActor/HitTexture`
  (`actor.zs:61-87`), so a ZScript-only version is possible today (slow, and
  it cannot feed the native weapon puffs).

### Upstream-friendliness
Medium-high. GZDoom upstream has rejected nothing like this, and the opt-in
flag + optional damage params fit house style; the weak-point "region mask"
idea is novel and should be proposed as a GLDEFS/MODELDEF-like optional
channel, not a default. Expect bikeshedding on the mask format.

---

## Item 4 — Smooth sprite rotation and pitch transitions

### Touch points
- Frame selection: `spritedef_t::GetSpriteFrame(int frame, int rot, DAngle ang,
  bool *mirror, bool flipagain)` (`src/r_data/sprites.cpp:62-91`) — 16 yaw
  buckets (`>> 28`), **no pitch dimension**.
- Sprite lump install: `R_InstallSpriteLump` (`src/r_data/sprites.cpp:99-175`)
  parses the frame/rotation characters ('0'-'9','A'-'F' = 16 yaw). Pitch bands
  need a format extension here or a parallel table.
- Data structures: `spriteframe_t { FVoxelDef*; FTextureID Texture[16];
  uint16_t Flip; }` (`src/r_data/sprites.h:37-42`), `spritedef_t`
  (`sprites.h:49+`, `sprites.cpp:40-48`). Not savegame-serialized (only
  `sprite`+`frame` ints on actors are), so format changes are save-safe.
- HW consumers: `HWSprite::Process` (`src/rendering/hwrenderer/scene/
  hw_sprites.cpp:797`), picnum override and normal path around 994-1045,
  `GetSpriteFrame` call at 1035; SW consumer
  `src/rendering/swrenderer/scene/r_opaque_pass.cpp:1110`.
- Crossfade geometry: `HWSprite::CreateVertices`
  (`hw_sprites.cpp:623-640`) writes 4 `FFlatVertex`; the vertex format already
  has a **second UV channel** `lu,lv` + `lindex`
  (`src/common/rendering/hwrenderer/data/flatvertices.h:35-62`) that sprites
  leave unused (`lindex = -1`).
- Shader: sprites use `wadsrc/static/shaders/glsl/main.fp` (via
  `hw_shaderpatcher.cpp:283-307`); materials are `FMaterial`
  (`src/common/textures/hw_material.{h,cpp}`), which already supports multiple
  texture layers (`AddTextureLayer`, `GetLayer`, hw_material.h:60-87).

### Design
(a) Pitch bands: extend the sprite data with an optional second dimension —
either a new lump namespace (e.g. a `PITCHES`-style per-frame table listing N
pitch band textures + the band's elevation range + hysteresis margin) or
extended frame names the loader recognises when `pitchbands` is present in the
sprite's GLDEFS/ZScript metadata. `GetSpriteFrame` gains a pitch argument;
camera-elevation angle feeds it from both `HWSprite::Process` and the SW
renderer, with hysteresis state kept per-sprite-definition (not per-actor, to
stay demo-safe). Default = current behaviour.
(b) Crossfade: an opt-in sprite flag; when on, the two adjacent yaw frames (or
pitch bands) are selected, the second texture bound as an extra material layer,
the second UV set written into `lu,lv`, and a per-vertex fade factor packed
into an unused component (or `lindex` when negative). A small `#define
SPRITE_FADE` block in main.fp does the mix (or ordered dither when alpha
blending is off). Zero cost when off: same single-texture draw.

### Effort and risks
- Effort: (a) **M** (data format + two consumers), (b) **M** (shader + vertex
  plumbing in both backends' vertex format users).
- Risks: savegames are safe (see above), but the sprite lump format change
  must version-gate (`sprites.cpp` uses `MAX_SPRITE_FRAMES`; new namespace is
  additive). Renderer parity: SW renderer needs (a) too (one call site); (b)
  can be HW-only. Demos: frame choice is renderer-side only — no playsim
  effect, no demo impact. Performance: (b) doubles sprite texture fetches only
  for flagged sprites.

### Already partly exists
- `SpriteRotation`/`SpriteAngle` actor properties and `MF7_SPRITEANGLE`
  (`wadsrc/static/zscript/actors/actor.zs:455,545-546`,
  `src/playsim/actor.h:385`) — yaw offset only. No pitch support anywhere
  (searched: nothing).

### Upstream-friendliness
Medium. Pitch bands are a long-requested GZDoom feature but touch a 30-year-old
lump convention; the additive-table design is the part to get upstream review
on early. The crossfade is self-contained and likely welcome behind an opt-in
flag.

---

## Item 5 — Per-pixel lighting on sprites (normal-mapped billboards)

### Touch points
- Sprite lighting entry: `HWDrawInfo::GetDynSpriteLight`
  (`src/rendering/hwrenderer/scene/hw_spritelight.cpp:105-278`) — collapses ALL
  dynamic lights + the light probe into **one flat RGB**; `hw_sprites.cpp:167-175`
  calls it and `state.SetDynLight(...)` sets the single uniform
  `muDynLightColor` (`src/common/rendering/gl/gl_renderstate.cpp:122`).
- Material layers already exist: `FMaterial` layer array
  (`src/common/textures/hw_material.h:60-87`); GLDEFS `material` parser accepts
  `sprite` + `normal/specular/metallic/roughness/ao` layers
  (`src/r_data/gldefs.cpp:1267-1535`, keywords at 1287-1288) and
  `FMaterial::FMaterial` promotes them to SHADER_Specular/SHADER_PBR
  (`src/common/textures/hw_material.cpp:76-89`).
- Shaders: `ApplyNormalMap` + `NORMALMAP` define
  (`wadsrc/static/shaders/glsl/main.fp:612-662`), specular/PBR shader table
  entries (`src/common/rendering/hwrenderer/data/hw_shaderpatcher.cpp:286-287`),
  dynlight data upload `screen->mLights->UploadLights`
  (`hw_sprites.cpp:604`, `src/common/rendering/hwrenderer/data/hw_lightbuffer.cpp`).
- Sprite rotation frames are separate `FGameTexture`s, so **per-rotation baked
  normal maps already slot in** by assigning a material per frame.

### Design
Two parts. (a) Normal maps: enable the existing normal/PBR material path for
sprites (it already runs for models); the billboard's `vWorldNormal` is the
quad normal and `ApplyNormalMap`'s cotangent frame works from UV derivatives,
so a camera-space normal map per rotation gives correct directional response.
(b) Per-pixel lights: add an opt-in sprite path that uploads the affected
light list (same `FDynLightData` as walls, `hw_lightbuffer.cpp`) and passes a
light-buffer index with the sprite draw instead of the single flat color; a
`#define SPRITE_LIGHTS` block in main.fp loops the light list per fragment
using `pixelpos` and the bumped normal. Keep `GetDynSpriteLight` as the
default path (zero cost when unused). The probe term (item 6) folds into the
same per-pixel loop as an ambient term.

### Effort and risks
- Effort: **M-L** (shader + renderstate plumbing in both GL and Vulkan
  backend bindings; the shared scene code is the small part).
- Risks: performance is the big one (sprites in a 30-light scene × per-pixel
  loop); mitigate with a light-count cap and distance culling. Renderer parity
  GL/Vulkan: light buffer already exists in both. Demos/multiplayer: pure
  renderer change, no risk. Savegames: none.

### Already partly exists
- Flat dynamic light + probes on sprites (`GetDynSpriteLight`), material-layer
  plumbing, normal-map shaders for models. What's missing is only the
  sprite-specific binding/loop.

### Upstream-friendliness
High for (a) (uses existing machinery), medium for (b) (shader cost concerns;
upstream would want a cvar default-off at first, like `gl_light_sprites`).

---

## Item 6 — Light probes / lightmap sampling for actors and models

### Touch points
- Probes: `LightProbe`/`LightProbeCell` (`src/gamedata/r_defs.h:1767-1780`),
  loaded from the map's `ML_LIGHTMAP` lump by `MapLoader::LoadLightmap`
  (`src/maploader/maploader.cpp:3331-3433`), **gated behind
  `-enablelightmaps`** ("still too early WIP", `maploader.cpp:3346`).
  Sampling: `FindLightProbe` (`hw_spritelight.cpp:34-89`) — nearest probe in a
  3×3 cell neighbourhood; used for sprites (`hw_sprites.cpp:172,303`), decals
  (`hw_decal.cpp:60`), weapon (`hw_weapon.cpp:859`).
- Lightmaps: `LightmapSurface` UVs on walls/flats
  (`src/rendering/hwrenderer/hw_vertexbuilder.cpp:195-269`,
  `hw_walls.cpp:1125-1128,1371-1377`), sampled in-shader when `vLightmap.z >= 0`
  (`wadsrc/static/shaders/glsl/main.fp:771-773`). Sprite vertices already carry
  `lu,lv,lindex` unused (`flatvertices.h:35-62`).
- Models: `gl_light_models` (`hw_models.cpp:36`), light list upload
  (`hw_sprites.cpp:604`), but **no probe or lightmap sampling for models**.

### Design
(a) Sprites: when the actor's sector has a lightmap, write the floor's
lightmap UV + texture index into the sprite's `lu/lv/lindex` (computed from the
actor's position via `subsector_t`/`LightmapSurface` lookup); the existing
shader path then adds the baked light automatically. Blend with the probe term
(cvar). (b) Models: compute the same probe/lightmap term per model draw and
pass it as the model's ambient (the `FWModelRenderer` already sets a light
index; extend with the same `lu/lv/lindex` or a small uniform). (c) Un-gate and
stabilise `-enablelightmaps` after a review of `LoadLightmap` (versioning,
bounds checks). Zero cost when no lightmap lump exists.

### Effort and risks
- Effort: **M** (the probe machinery exists; the work is the actor→lightmap UV
  lookup and the model ambient path).
- Risks: the lightmap lump is WIP (version 0, zlib) — stabilising it is the
  real work. Renderer parity: lightmaps exist in GL and Vulkan (shared
  vertex path); SW renderer does not use lightmaps (document as unsupported).
  Demos/savegames: renderer-only, no risk. Performance: one extra texture
  sample per sprite/model fragment.

### Already partly exists
- Yes — probe-grid sampling for sprites/decals/weapons exists (citations
  above). Missing: lightmap sampling for actors, probes for models, the
  experimental gate.

### Upstream-friendliness
High. UZDoom's lightmap+probe system is its own (UDB-baker) feature; finishing
it is clearly in upstream's direction.

---

## Item 7 — Volumetric light shafts

### Touch points
- Post-process pipeline: `hw_postprocess.cpp` pass classes (SSAO etc.,
  `src/common/rendering/hwrenderer/postprocessing/hw_postprocess.cpp:643-900`),
  scene depth/colour inputs `SetInputSceneDepth/SetInputSceneColor`
  (`hw_postprocess.cpp:795-796`), output `SetOutputSceneColor` (845).
- Custom PP shader infra: `PPCustomShaders` (`hw_postprocess.cpp:903-960`),
  `PostProcessShader {Target, ShaderLumpName, Uniforms, Textures}`
  (`hw_postprocessshader.h:52-71`), ZScript uniforms
  `PPShader.SetUniform*` (`wadsrc/static/zscript/engine/ppshader.zs:29-33`,
  natives `hw_postprocessshader.cpp:47-145`).
- GLDEFS-side definitions of custom shaders parse in `ParseMaterial` /
  `hardwareshader` (`src/r_data/gldefs.cpp:237`).
- Light position/shadow: shadow maps exist (`src/common/rendering/hwrenderer/
  data/hw_shadowmap.cpp`) — a future enhancement; basic shafts only need
  depth + light position + colour.

### Design
New `PPLightShafts` pass (or a custom PP shader shipped in the mod, no engine
change beyond item 1's depth) that: reads linearised scene depth (item 1
delivers it to PP), marches screen-space rays from a designated light's screen
position (one spotlight or sun per pass), accumulates scattering, and adds the
result onto scene colour before tonemap. Light list and parameters come from
ZScript uniforms (`PPShader.SetUniform3f/1f` each frame from a RenderOverlay
handler). Opt-in per map; zero cost when disabled.

### Effort and risks
- Effort: **M** (shader + one pass class) — **S** if shipped as a mod-side
  custom PP shader once item 1 lands.
- Risks: performance (ray march cost — cap steps, half-res), flicker with
  moving lights (temporal reprojection out of scope), Vulkan parity (PP
  pipeline is shared, but shader code is GLSL-compiled in both — fine).
  No gameplay impact at all.

### Already partly exists
- Nothing for shafts (searched: no volumetric/godray code). All the
  scaffolding (PP passes, depth input pending item 1, ZScript uniforms) does.

### Upstream-friendliness
High as a generic "PP light shafts" pass with cvars, mirroring the existing
SSAO/Bloom passes.

---

## Item 8 — Scene-colour access for translucent sprites and models (refraction)

### Touch points
- Scene-to-texture machinery: `OpenGLFrameBuffer::RenderTextureView`
  (`src/common/rendering/gl/gl_framebuffer.cpp:212`) renders the 3D scene into
  a texture; used for canvases and camera textures
  (`src/rendering/hwrenderer/hw_entrypoint.cpp:357-390`).
- Material layers: `FMaterial` (`hw_material.h:60-87`) + GLDEFS `texture`
  custom-shader bindings (`gldefs.cpp:1376-1403`, `CustomShaderTextures`).
- Translucent draw order: sprites/models draw after opaque geometry
  (`HWDrawInfo` / `hw_drawlist.cpp`); the scene copy must be made at the
  opaque/translucent boundary.
- ZScript texture access: `TexMan.GetCanvas` (`wadsrc/static/zscript/engine/
  base.zs:344`), camera textures per level
  (`Level->canvasTextureInfo`, hw_entrypoint.cpp:378-390).

### Design
New opt-in material keyword (GLDEFS `refraction` on a sprite/model skin, or a
`+REFRACT` actor flag): after the opaque pass, blit the scene colour to a
dedicated RGBA16F texture (reuse `RenderTextureView`/`CopyToTexture` machinery,
once per frame, only when at least one refracting material is visible); bind
that texture as an extra material layer (sampler slot like detail/brightmap)
with a `#define REFRACTION` main.fp block that offsets the UV by a
normal-map-derived or fixed bend amount and samples it, mixing by material
alpha. Zero cost when unused (the copy pass is skipped).

### Effort and risks
- Effort: **M** (one scene copy + layer binding + shader block).
- Risks: cost of the copy (mitigate: half-res, only-when-used); self-visibility
  (refracting objects must not appear in their own copy — draw after the copy,
  which translucents already do); portal-heavy scenes double-render (bounded
  by recursion caps); Vulkan parity (shared PP/state API covers both).
  No playsim impact.

### Already partly exists
- No refraction anywhere (searched: none). The scene-copy and layer plumbing
  are all in place.

### Upstream-friendliness
Medium-high — GZDoom has long wanted this; the proposal must reuse the
existing texture-view machinery rather than add a new framebuffer path.

---

## Item 9 — External event bus (OSC/UDP), ZScript send/receive

### Touch points
- In-engine net command plumbing (the model to copy): `NetworkCommand` /
  `NetworkBuffer` ZScript (`wadsrc/static/zscript/events.zs:56-66`),
  `EventHandler.SendNetworkCommand/SendNetworkBuffer` (events.zs:244-246),
  natives `EventManager::SendNetworkCommand/SendNetworkBuffer`
  (`src/events.cpp:395-499`, VM wrappers 1645-1661), packet handling
  `DEM_ZSC_CMD` (`src/d_net.cpp:3126-3145`) — vararg-encoded commands over UDP
  with registered handlers, already versioned.
- UDP transport code: `src/common/engine/i_net.cpp` (socket setup, `-port`
  default 5029 at i_net.cpp:98-100, `BindToLocalPort` 212).
- Game events to emit: `StaticEventHandler` world events
  (`events.zs:179-196`: WorldThingDied, WorldThingDamaged, WorldHitscanFired,
  WorldTick, PlayerDied, ...).
- Stdout today: `Printf` (`src/common/console/c_console.cpp:493-511`); Null Run
  scrapes `NRAUDIO/NRSTATE` lines from it.

### Design
A small native "external bus" module: one localhost UDP socket (default
127.0.0.1, per-run port from a cvar or `-nreventport` with an ephemeral
`0 = auto-assign` mode, printed to the log so tooling can discover it), OSC
1.1 packets or a simple JSON/varint envelope. ZScript API mirrors the existing
network API: `EventBus.Send(name, args...)` and an
`EventHandler.BusReceive(BusEvent e)` virtual (or a
`NetworkCommandProcess`-style handler), plus opt-in auto-emit of the standard
world events. Rate-limit and drop rather than block (never stall the playsim;
no data may leave by default — opt-in per mod). Native thread only for the
socket; delivery is polled once per tick for determinism.

### Effort and risks
- Effort: **M** (socket + encode + ZScript natives + event tap).
- Risks: never let the bus affect game state ordering (poll at tick
  boundaries; incoming events apply as queued level-local commands, like
  net commands — demo safety requires the queue to be part of the playsim
  state or explicitly non-deterministic and local-only). Fixed-port clashes:
  solve with auto-assign + log. Security: bind localhost only.
- Multiplayer: bus is local-only (each machine's own); document that.

### Already partly exists
- The entire in-engine pattern (`SendNetworkCommand`, handlers, event
  hierarchy) — the new part is only the external transport + opt-in taps.

### Upstream-friendliness
Medium. An OSC bus is a modding-infrastructure feature; propose it with
`-nreventport`-style flag, default-off, localhost-only, and upstream will
likely take it (or ask for it as a library-style module).

---

## Item 10 — Transport/beat clock readable in ZScript and shaders

### Touch points
- Tick time: `P_Ticker` (`src/p_tick.cpp:168`), `Level.maptime/time/totaltime`
  are tick integers (`wadsrc/static/zscript/doombase.zs:522-527`); no
  fractional/interpolated time in ZScript (unconfirmed absence of any
  `GetMusicPosition` native — searched, none).
- Render interpolation: `viewPoint.TicFrac = I_GetTimeFrac()`
  (`src/rendering/r_utility.cpp:946`), `cl_capfps`/`r_NoInterpolate` override
  (`hw_entrypoint.cpp:343`).
- Shader time: `muTimer` per material (`gl_renderstate.cpp:124`); PP uniforms
  come from ZScript (`PPShader.SetUniform*`).
- Input path: item 9's bus.

### Design
Native `BeatClock` service: the engine keeps a phase accumulator updated per
tick from an external beat stream (item 9) — `SetBeat(bpm, phase)` ZScript
calls also allowed for offline use. Expose to ZScript as
`Level.BeatTime`/`BeatPhase` (double, including fractional tick part computed
from `I_GetTimeFrac()`); expose to shaders as a per-frame uniform
(`uBeatPhase`, smoothed `uBeatFrac` for render-time interpolation, added to the
viewpoint/uniform buffers alongside `muTimer`). All consumers read; none
write (deterministic). Zero cost when no beat is set.

### Effort and risks
- Effort: **M** (mostly plumbing: 1 uniform, 1 ZScript struct field, 1
  accumulator).
- Risks: demo sync — the clock must derive from tick time + explicit phase,
  never wall-clock (except in a clearly-marked `BeatClock`-local mode).
  Savegames: phase is level state — serialize it or reset on load (decide and
  document).

### Already partly exists
- Nothing beat-specific. `Level.maptime` + `I_GetTimeFrac` + `muTimer` are the
  building blocks.

### Upstream-friendliness
Medium — generic "engine time service" is uncontroversial; the *beat* framing
should be kept mod-facing (upstream would prefer a generic
`Level.RenderTime`-style API plus the shader uniform).

---

## Item 11 — Reverb that does what the zone asks

### Touch points
- EFX application: `OpenALSoundRenderer::LoadReverb`
  (`src/common/audio/sound/oalsound.cpp:2032-2127`) — forwards
  `ModulationTime/ModulationDepth`, `EchoTime/Depth`, reflections etc. to
  `AL_EFFECT_EAXREVERB` (2086-2105).
- Parameter set: `REVERB_PROPERTIES` (`src/common/audio/sound/
  i_soundinternal.h:69-102`), `ReverbContainer` (116-125), zones
  `Level->Zones[ZoneNumber].Environment` (`src/sound/s_doomsound.cpp:796-797`),
  `S_FindEnvironment` (`s_environment.cpp:461-489`).
- SNDINFO: command table `s_advsound.cpp:202-232` has **no `$environment`**
  (confirmed); SNDSEQ has `environment` (`s_sndseq.cpp:249`).
- ZScript sound entry: `S_StartSound`/`S_StartSoundAt`
  (`wadsrc/static/zscript/doombase.zs:207-214`).

### Design
Two-pronged. (a) Engine-side: add `$environment <name>` to SNDINFO (per-sound
reverb override, parsed in `S_AddSNDINFO`), expose
`Sound.SetReverbEnvironment`/per-channel wet send to ZScript, and add a
software early-reflection engine behind the OpenAL effect for drivers that
ignore EAX modulation (or fix the modulation path where OpenAL Soft silently
drops it — **unconfirmed** which backend quirk Null Run hit; the parameters
ARE sent). (b) Bridge-side: with item 9, add an opt-in "reverb send" mode that
emits per-sound events (position, zone, volume, dry/wet) so Pd's FDN takes
over entirely; engine reverb becomes a fallback. Zero cost when unused.

### Effort and risks
- Effort: (a) **M-L** (depends how much DSP must be written), (b) **S-M**
  (piggybacks item 9).
- Risks: audio-only changes — no demo/savegame/net risk; performance of a
  software FDN must stay under the audio buffer budget.

### Already partly exists
- Zones, EFX parameter forwarding, underwater filters, SNDSEQ `environment`.
  Missing: SNDINFO `$environment`, ZScript per-sound reverb control, real
  flutter/early reflections (backend-dependent).

### Upstream-friendliness
High for the SNDINFO/ZScript parts (long-standing GZDoom requests); the Pd
send is Null Run-specific and belongs behind the item 9 bus as a mod hook.

---

## Item 12 — Live HydraPy textures over shared memory

### Touch points
- Texture seam: `FCanvasTexture` (`src/common/textures/textures.h:305-320`),
  `TexMan.GetCanvas` (`wadsrc/static/zscript/engine/base.zs:344`), `Canvas`
  ZScript (`base.zs:540-570`); canvas redraw upload
  (`hw_entrypoint.cpp:357-376`, `RenderTextureView`
  `gl_framebuffer.cpp:212`).
- Material/custom-shader textures (to feed the sky, PP shaders, world
  monitors): `PostProcessShader.Textures` (`hw_postprocessshader.h:52-71`),
  GLDEFS `texture` bindings (`gldefs.cpp:1376-1403`).
- Camera textures as the precedent for "live scene in a texture"
  (`hw_entrypoint.cpp:378-390`).

### Design
New native texture type `FSharedMemoryTexture` (or a native on
`FCanvasTexture`): ZScript creates it with `TexMan.GetSharedMemoryTexture
(name, shm_path, w, h)`; the engine mmaps a HydraPy-written ring buffer
(header: magic, width, height, format, frame counter, pixel data), and once
per rendered frame, if the frame counter changed, uploads the pixels to the
GPU texture (the canvas-texture dirty path already does exactly this dance).
The texture is then usable anywhere a texture is: `Screen.DrawTexture`,
wall/flat via `ReplaceTextures`, sky, GLDEFS custom-shader `texture`, or the
PP shader's texture map (item 8's scene-copy machinery is a sibling, not a
dependency). Zero cost when no shm textures exist.

### Effort and risks
- Effort: **M** (one texture subclass + upload hook + ZScript native; ~300
  lines).
- Risks: security (validate the shm header, never trust sizes; document that
  shm means a cooperating local process), GPU upload cost at 4K@60
  (mitigate: PBO/streaming like camera textures), determinism (renderer-only —
  none).

### Already partly exists
- Canvas textures + upload-on-dirty + all texture consumers. Missing: the shm
  data source (no mmap/shm code in-tree, searched).

### Upstream-friendliness
Low-medium as-is (upstream may prefer a generic "external texture provider"
interface; the proposal should frame it as one).

---

## Item 13 — ZIP64 / large-archive support

### Touch points
- Zip loader: `src/common/filesystem/source/file_zip.cpp` — EOCD scan
  `Zip_FindCentralDir` (47-91, handles the PK\x06\x06 ZIP64 locator), EOCD64
  read `FZipFile::Open` (152-170), per-entry ZIP64 extra-field parse
  (258-283).
- **The cap**: entries with compressed/uncompressed size > 0x7fffffff are
  deliberately skipped — "The file system is limited to 32 bit file sizes"
  (`file_zip.cpp:271-277`).
- Entry storage is already 64-bit: `FResourceEntry::Length` is `size_t`
  (`src/common/filesystem/include/resourcefile.h:120-130`), `uint64_t
  dirsize/DirectoryOffset` (file_zip.cpp:132).
- Also note `FileSize = (uint32_t)fin.GetLength()` (file_zip.cpp:55) — the
  EOCD scan truncates 4GB+ archive sizes (**unconfirmed** whether this breaks
  >4GB archives; the scan window is bounded by 0xffff anyway, so the main
  risk is entries beyond 4GB and the central-directory size).

### Design
Lift the 2GB entry cap in `file_zip.cpp` (keep a sanity ceiling, e.g. 16GB,
configurable), audit the decompression/read paths for remaining 32-bit size
arithmetic (`FCompressedBuffer`, `FileReader::Read` callers, WAD/texture load
paths that take `int` sizes), and keep multi-archive `-file` order as the
documented alternative (it already works: archives load in command-line
order).

### Effort and risks
- Effort: **M** (one loader change + an audit, then soak-testing with real
  >2GB entries).
- Risks: memory (a >2GB lump must stream or be explicitly capped by the
  consumers — textures/video are the real users); archive writer
  compatibility; no gameplay impact.

### Already partly exists
- ZIP64 EOCD and extra fields ARE parsed; only the 2GB entry cap remains.
  Multi-archive load order already works.

### Upstream-friendliness
High — upstream will want this; the 2GB cap is an explicit TODO-style limit.

---

## Item 14 — Test-isolation flags

### Touch points
- Audio: `-nosound/-nomusic/-nosfx` FARGs (`src/common/audio/sound/i_sound.cpp:50-52`),
  `I_InitSound` (`i_sound.cpp:247-280`) with `NullSoundRenderer`, and
  `snd_backend` cvar (`i_sound.cpp:63`, "null" backend at 259).
- Batch mode: `batchout`/`batchrun` + `-logfile`
  (`src/d_main.cpp:4181-4192`) sets `nosound = true`.
- Screenshot: `screenshot` CCMD → `M_ScreenShot` (`src/m_misc.cpp:664-700`).
- Net port: `-port` (`src/common/engine/i_net.cpp:98-100`, default 5029).

### Design
(a) `-noaudio` alias / make `snd_backend null` a first-class flag that also
skips device enumeration entirely (avoids exclusive device grabs — verify
OpenAL device open behaviour, **unconfirmed** where Null Run's clash was).
(b) Deterministic headless capture: `-headless N` or
`+captureframe <tic>` mode — render offscreen at a fixed resolution with
`vid_activeinbackground`, `cl_capfps` locked, `-nomusic -nosound`, take
`M_ScreenShot` at a fixed tic, exit; make it exit with a defined code.
(c) Per-run auto-assigned ports for any new local services (item 9), never
fixed defaults.

### Effort and risks
- Effort: **S-M** (mostly wiring existing pieces; the deterministic exit is
  the fiddly part — capture happens on the render thread).
- Risks: none for gameplay; headless mode must not touch the audio device at
  all.

### Already partly exists
- `-nosound`, `-nomusic`, `-nosfx`, `snd_backend null`, batch mode + logfile,
  `screenshot` ccmd. Missing: deterministic fixed-tic capture/exit and
  guarantees about device grabs.

### Upstream-friendliness
High — testability flags are uncontroversial; upstream CI would use them.

---

## Item 15 — Log-only debug channel

### Touch points
- `Printf`/`Printf(PrintFlag, ...)` (`src/common/console/c_console.cpp:493-511`);
  notification routing honours `PRINT_NONOTIFY`
  (`c_console.cpp:434`); print-level flags `PRINT_LOG / PRINT_NONOTIFY /
  PRINT_NOLOG / PRINT_NOCONSOLE` are **already exposed to ZScript** as
  `EPrintLevel` (`wadsrc/static/zscript/engine/base.zs:153-168`) and
  `Console.PrintfEx(int printlevel, string fmt, ...)` (`base.zs:700-706`).
- `A_Log` calls plain `Printf` (`src/playsim/p_actionfunctions.cpp:1339-1350`).
- Logfile: `-logfile` / `logfile` ccmd (`d_main.cpp:4181-4185`).

### Design
Essentially nothing to build: `Console.PrintfEx(PRINT_LOG | PRINT_NONOTIFY,
...)` from ZScript already writes only to the logfile and never to the
notification area. The only native addition worth making is a convenience
`Console.Log(fmt, ...)` native (PrintfEx with those flags) and a
`nr_debug`-style cvar pattern documented in FORK.md. See QUICK-WINS.

### Effort and risks
- Effort: **S** (a wrapper native is ~10 lines; or zero — use PrintfEx).
- Risks: none.

### Already partly exists
- Fully, modulo the wrapper (see above).

### Upstream-friendliness
Trivial — `Console.Log` would be accepted without debate.

---

## Item 16 — Hit position into DamageMobj

### Touch points
- Carrier: `FTranslatedLineTarget` (`src/playsim/actor.h:1822-1828`) — add
  `DVector3 HitPos; DVector3 HitVector;` (or a bool + values).
- Fill sites: `P_LineAttack` thing-hit branch (`p_map.cpp:4868-4956`, where
  `trace.HitPos`/`trace.HitVector` from `FTraceResults` (`p_trace.h:56-81`)
  are in scope); wall-hit branch similarly (`p_map.cpp` ~4800-4870).
- Consumer: `P_DamageMobj` (`src/playsim/p_interaction.cpp:1584`) — add
  optional parameters; VM `DamageMobj` virtual
  (`wadsrc/static/zscript/actors/actor.zs:912`) gains optional named args
  `Vector3 hitpos = (0,0,0), Vector3 hitnormal = (0,0,0)` (defaults preserve
  source compat).

### Design
Mechanical: extend the struct, fill from the trace, thread through
`P_DamageMobj` and the VM call (existing call sites pass defaults). ZScript
callers that use `LineTrace` already have `HitLocation/HitDir`
(`actor.zs:61-87`) and can pass them explicitly. Zero behaviour change with
defaults.

### Effort and risks
- Effort: **S** (one struct, two fill sites, one function signature, VM
  wrapper).
- Risks: none — no serialization, no net, no demo change.

### Already partly exists
- The data exists inside `FTraceResults`; ZScript `LineTrace` already exposes
  hit position; only the `P_LineAttack → DamageMobj` plumbing is missing.

### Upstream-friendliness
High — an obvious, small, backward-compatible extension.

---

## Item 17 — Lightweight physics for props and debris

### Touch points
- Existing movement/bounce machinery: bounce handling in
  `src/playsim/p_mobj.cpp:2090-2184` (`BounceFlags`, `bouncecount`, wall/floor
  bounce), friction flags `MF8_NOFRICTION`, `MF8_NOFRICTIONBOUNCE`
  (`src/playsim/actor.h:402-403`), ZScript `Friction` property and
  `GetFriction()` (`wadsrc/static/zscript/actors/actor.zs:525,929`).
- No rigid-body/angular dynamics anywhere (searched: none).
- Argon batch 2 flags a "resting-jitter bug" in the bounce path
  (**unconfirmed** in this tree — likely the bouncer re-bouncing without a
  damping/rest threshold around p_mobj.cpp:2130-2184).

### Design
Two levels. (a) Fix the resting-jitter: add a velocity rest threshold to the
bounce path (below it, zero the velocity and clear bouncecount) — a small
native fix. (b) A "settle" behaviour for props: opt-in actor flag; on spawn or
on level start, run a short native settle simulation (drop to floor with
friction, damp angular pose to the nearest stable rest via the existing
`Angles.Pitch/Roll` — unconfirmed whether roll/pitch are render-only or
playsim-real; they are renderer-applied, so a ZScript-side settle using
`Vel`/floor checks is possible without native changes). Keep it explicitly
NOT a physics engine: no stacking, no constraints; per-actor and cvar-capped.

### Effort and risks
- Effort: (a) **S**, (b) **S-M** (ZScript-first; native only for the rest
  threshold if (a) is in the bounce path).
- Risks: demo/multiplayer — any randomised settle must use the playsim RNG
  (deterministic) or be cvar-gated; performance trivial.

### Already partly exists
- Bounce/friction primitives, gravity, floor collision. Missing: rest
  damping, settle behaviour, angular response.

### Upstream-friendliness
High for the jitter fix (a bug fix). The settle behaviour is mod-side in
spirit; propose as a documented ZScript pattern before asking for native
support.

---

## Item 18 — Wet and reflective floors

### Touch points
- Native special: `Sector_SetPlaneReflection(tag, floor, ceiling)`
  (`src/playsim/p_lnspec.cpp:3420-3432`), UDMF `floor_reflect`/`ceiling_reflect`
  (`src/maploader/udmf.cpp:2004-2009`), storage `sector_t::reflect[2]`
  (`src/gamedata/r_defs.h:709`), cvar `gl_plane_reflection`
  (`src/common/rendering/hwrenderer/data/hw_cvars.cpp:51-54`),
  `GetReflect()` (`r_defs.h:1155`).
- Renderer: mirror portal `PORTALTYPE_PLANEMIRROR` + `HWPlaneMirrorPortal`
  (`src/rendering/hwrenderer/scene/hw_sky.cpp:181-190`,
  `hw_walls.cpp:704-720`), translucent floor over the mirror
  `alpha = 1.0f - GetReflect(floor)` (`hw_flats.cpp:544`, ceiling 601).
- PBR wet look: GLDEFS material `specular/glossiness` per flat
  (`src/r_data/gldefs.cpp:1267-1535`) → `SHADER_Specular`/`PBR`
  (`hw_material.cpp:76-89`).
- Savegame: `reflect` serialized (`src/p_saveg.cpp:327`).

### Design
Mostly a verification/use job (see QUICK-WINS): set `floor_reflect` in UDMF
(or the line special), give the floor a PBR material with high glossiness /
low roughness for the wet look, tune `gl_plane_reflection`. Improvement
candidates found in the source: (a) reflections are skipped on sloped planes
(`p_lnspec.cpp:3425-3426`, `maploader.cpp:3218-3219`) — wet ramps need that
lifted; (b) the mirror is drawn only where the plane would draw sky
(`SkyPlane`, hw_sky.cpp:128-190) — confirm interaction with regular textured
floors (the alpha path in hw_flats.cpp:544 suggests it works for normal
flats too, but the portal is created in the sky path — **verify with the
target frame**); (c) sprite/actor reflections depend on the mirror portal's
recursion settings.

### Effort and risks
- Effort: **S** (use what exists), **M** if sloped-plane reflection support is
  needed.
- Risks: render cost of the mirror pass (one extra scene render per
  reflective plane); portal recursion caps.

### Already partly exists
- Plane reflections and PBR floors are native. This item is 80% "turn it on
  correctly".

### Upstream-friendliness
High — fixes to the existing feature (slopes, recursion) are upstream-welcome.

---

## Recommended implementation order

Order chosen so each step unlocks or de-risks the next; pairs that touch the
same code are adjacent. Items marked (QW) are quick wins, detailed in
QUICK-WINS.md.

1. **Item 15 (QW)** — log-only channel: one wrapper native; unblocks clean
   instrumentation of every later item.
2. **Item 16 (QW)** — hit position into DamageMobj: tiny, and item 3's pixel
   test builds directly on it.
3. **Item 14 (QW)** — test-isolation flags: makes all later items testable
   without blocking a human playtest.
4. **Item 13 (QW/M)** — ZIP64 cap lift: self-contained, unblocks big build
   archives before the fork's other large assets land.
5. **Item 18 (QW)** — reflective/PBR floors: mostly turn-on; lands a visible
   pillar cheaply.
6. **Item 2** — rotated-portal sight/sound/hitscan: the deepest gameplay
   correctness fix; do it before the anatomy/pixel work because both touch
   `P_LineAttack`/portal traversal and the hitscan part of item 2 should land
   before item 3's hit-testing (which must be correct through portals).
7. **Item 3** — per-pixel hit testing + region masks: needs item 16, and
   benefits from item 2's portal-correct traces. Design the mask channel with
   item 4's band work in mind (masks are per-frame too).
8. **Item 4a then 4b** — pitch bands first (data format; the frame pipeline
   items 3/5 reference), then the crossfade (independent shader work).
9. **Item 5** — per-pixel sprite lighting: after 4a so per-band/per-rotation
   normal maps exist to light.
10. **Item 6** — lightmap/probe sampling for actors/models: shares the sprite
    light path with item 5 and the `lu/lv/lindex` channel with item 4b;
    sequence after them to avoid conflicts in `hw_sprites.cpp`.
11. **Item 8** — refraction scene copy: after the opaque/translucent boundary
    is stable (items 4-6 move sprite code); also shares the texture-view
    machinery with item 12.
12. **Item 9** — event bus: prerequisites for items 10 and 11.
13. **Item 10** — beat clock: needs item 9 for the external beat; the
    shader-uniform part can be done in parallel.
14. **Item 11** — reverb: SNDINFO/ZScript parts anytime; the Pd-send variant
    after item 9.
15. **Item 7** — volumetric shafts: after item 1 (depth) lands; the PP pass
    itself is self-contained.
16. **Item 12** — shared-memory textures: last renderer item; everything it
    displays (sky, monitors) exists by then.
17. **Item 17** — debris physics: gameplay-feel polish, independent of the
    renderer items; do whenever a designer needs it.

Items deliberately independent: 13, 14, 15, 18 can start immediately in
parallel with everything else.
