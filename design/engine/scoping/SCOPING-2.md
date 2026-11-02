# UZDoom fork: feasibility scoping, round 2 — wishlist items 22–27

Scope: read-only research against `~/dev/uzdoom-nullrun` at commit `17480c8`
("Import UZDoom 5.0.3 source release", GPL-3). Items 22–27 are the new
candidates at `~/dev/shared/claude/engine/ENGINE-WISHLIST.md:80-103`. Nothing
was built, run or modified. Every file, function and line below was read in
this tree. **Unconfirmed** marks what I could not settle from source.

Format follows `~/dev/shared/deepseek/uzdoom-fork-scoping-20261102/SCOPING.md`.
"HW" means GL, GLES and Vulkan; the GL and Vulkan backends share all scene code
in `src/rendering/hwrenderer/`. Line numbers are this commit's.

Two structural facts drive almost everything below, so they come first:

1. **Sprites and geometry are lit by two different paths.** Sprites are lit on
   the CPU (`HWDrawInfo::GetDynSpriteLight`, `src/rendering/hwrenderer/scene/
   hw_spritelight.cpp:100-207`) using the CPU shadow test
   (`IShadowMap::ShadowTest`, `src/common/rendering/hwrenderer/data/
   hw_shadowmap.cpp:84-90`). Models, walls and flats are lit on the GPU from the
   uploaded light buffer (`hw_sprites.cpp:599-607` → `hw_GetDynModelLight`,
   `hw_spritelight.cpp:225-278` → `lightContribution`,
   `wadsrc/static/shaders/glsl/material_normal.fp:18-52`). Anything that changes
   per-light colour or shadowing has to be added **twice**, and cookies/actor
   shadows cannot affect sprites at all without moving sprite lighting to the
   GPU (a larger job, not scoped here).
2. **The shadow map is a 1D, z-less distance map.** It is one 1024×1024 R32F
   texture; one row per light, split into four 256-texel directions
   (`hw_shadowmap.cpp:25-51`), built by ray-testing **2D** line segments
   (`shadowmap.fp:113-156`, `LevelAABBTree::RayTest`,
   `src/common/rendering/hwrenderer/data/hw_aabbtree.cpp:51-96` — note
   `.XY()` throughout). Z is never part of the test, so a light under a floor
   already lights through it. Any actor occlusion added to this map is
   necessarily an infinite vertical column.

---

## Native coverage (no fork needed, or worth knowing before writing code)

| Item | Already native | Where |
|---|---|---|
| 22 | A flattened ground blob shadow under actors, cross-renderer, per-actor flags and cvars | `r_actorspriteshadow*` cvars `src/rendering/r_utility.cpp:103-128`; gate `R_ShouldDrawSpriteShadow` `r_utility.cpp:1268-1301`; draw `hw_bsp.cpp:592-601,625-633`; flattening `hw_sprites.cpp:948-951,1097,1397-1407`; flags `RF_CASTSPRITESHADOW`/`RF_NOSPRITESHADOW` `src/playsim/actor.h:486-488`, scriptable `src/scripting/thingdef_data.cpp:366-367`; software renderer too `src/rendering/swrenderer/scene/r_opaque_pass.cpp:961` |
| 23 | Spot lights with inner/outer angles, yaw/pitch, GLDEFS and ZScript control — everything except a texture | GLDEFS keyword `gldefs.cpp:181,520-527`; ZScript `DynamicLight.SpotInnerAngle/SpotOuterAngle/spot` `wadsrc/static/zscript/actors/shared/dynlights.zs:22-38`; `FDynamicLight::IsSpot` `src/playsim/a_dynlight.h:249`; direction upload `src/rendering/hwrenderer/hw_dynlightdata.cpp:121-133`; cone attenuation `main.fp:602-606` |
| 24 | Nothing. Skyboxes reserve a 16× convention for fog distances only | `hw_portal.cpp:735-737`; no scale in `FLinePortal` (`src/playsim/portal.h:201-225`) |
| 25 | Translucent planes; plane-reflection mirror (a second scene render); swimmable 3D floors and `SECMF_UNDERWATER`; `FF_FOG` fog brushes; normal maps on any texture; `timer` in custom shaders; full-screen custom postprocess shaders with the scene texture | `Sector_SetTranslucent` `p_lnspec.cpp:2252-2267`; `Sector_SetPlaneReflection` `p_lnspec.cpp:3420-3434` + `hw_sky.cpp:181-190`; `waterlevel` `p_mobj.cpp:5384-5405`, `actor.h:1279`; `SECMF_UNDERWATER` `src/gamedata/r_defs.h:490-492`; `FF_FOG` `hw_flats.cpp:457-478`, `hw_walls.cpp:1773-1790`, `fogboundary.fp:31-52`; `materials/normalmaps/` `src/common/textures/gametexture.cpp:145-155`; `timer` `gl_shader.cpp:421`; `hardwareshader postprocess` `gldefs.cpp:1572-1620`, `hw_postprocess.cpp:1022-1090` |
| 26 | Circle resize at runtime (`A_SetSize`); nothing for orientation. `CanCollideWith` cannot help — it is called *after* the radius test rejects the pair | `A_SetSize` `src/playsim/p_actionfunctions.cpp:4988-5024`; call order `p_map.cpp:1379-1381,1472-1475` |
| 27 | `ML_SOUNDBLOCK` is already parsed and counted during the wake-up flood; area sounds already move their perceived origin to the nearest wall; the underwater direct lowpass filter already exists | `p_enemy.cpp:120-213` (soundblocks 197-207); `CalcSectorSoundOrg` `s_doomsound.cpp:950-989`; `EnvFilters` `oalsound.cpp:866-888`, applied `1480-1495`, water `1789-1860` |

---

## The one projection system (items 22b and 23)

**Yes.** A cookie and an actor silhouette are the same operation: project a
world position into a light's view and sample a texture. The only differences
are where the texture comes from and what the sample means.

The light record already carries everything a spot-light projection needs:
position, radius, colour, a shadow index, the forward vector, a "is spot" flag,
and the inner/outer cosines — 16 floats, of which the last two are unused
(`hw_dynlightdata.cpp:135-151`; `data[8..10]` forward, `data[11]` type,
`data[12..13]` cosines, `data[14..15]` zero). The shader reads them as
`lightpos`, `lightspot1`, `lightspot2` (`material_normal.fp:20-23`).

A shared GLSL helper would build the basis from the forward vector and world up
(shader world is `(x, z, y)`, so up is `(0,1,0)`; the basis degenerates for a
straight-up/down spot and needs a fallback axis):

```
vec3 LightProject(vec4 lightpos, vec4 lightspot1, vec4 lightspot2, vec3 p,
                  out vec2 uv, out float dist)
{
    vec3 v   = p - lightpos.xyz;
    vec3 fwd = lightspot1.xyz;
    vec3 up  = abs(fwd.y) > 0.99 ? vec3(0,0,1) : vec3(0,1,0);
    vec3 right = normalize(cross(fwd, up));
    vec3 up2   = cross(right, fwd);
    float z    = dot(v, fwd);
    // call only when lightspot1.w == 1.0 (spot), lightspot2.y = cos(outer)
    float t    = tan(acos(lightspot2.y));      // outer cone half-angle
    uv  = vec2(dot(v, right), dot(v, up2)) / (z * t) * 0.5 + 0.5;
    dist = z;
}
```

- **Cookie (23):** `attenuation *= texture(CookieAtlas, uv).rgb` (or `.a`).
  The texture is authored, static (animatable by changing the TextureID, not by
  scrolling UVs unless you also pass a time uniform).
- **Actor silhouette (22b):** the same `uv` and `dist` sample a depth atlas
  rendered from the same basis: `lit = dist <= texture(ShadowAtlas, uv).r + bias`.
  The depth compare is what prevents self-shadowing: the caster's front surface
  is at the stored depth and passes; anything behind it fails.

So one basis, one projection function, two textures and two tests. Deliver them
as one "light projection" feature: `LightProject` in `main.fp`, called from
`lightContribution` in `material_normal.fp:18-52`, from the inline loops in
`material_pbr.fp:81-186` and from `material_specular.fp:18-45` (three files,
eight loops). Add the cookie/depth sample after the cone attenuation and before
the existing `shadowAttenuation` call, and pass the light's new index floats
through.

Texture delivery, in increasing cost:

1. **Atlas (recommended v1).** One RGBA8 atlas of 16 256² cookies and one
   R32F atlas of 4 512² tiles for dynamic actor shadows (R32F matches the
   existing shadow map, `gl_renderbuffers.cpp:638`). One extra sampler,
   one index in `data[14]` (0 = none) and a shadow-atlas tile in `data[15]`
   (0 = none), no light-record layout change. Cookie
   images are uploaded once at level start; the shadow atlas is re-rendered per
   frame only for participating lights.
2. **Texture array (v2).** Cleaner filtering and no atlas bleeding, but needs a
   new array resource in both backends (`FGLRenderBuffers` has only
   `Create2DTexture`, `gl_renderbuffers.cpp:627-650`; Vulkan's
   `VkTextureManager` has only `Shadowmap`/`Lightmap`,
   `src/common/rendering/vulkan/textures/vk_texture.h:47-60`).
3. **Per-light cube/dual-paraboloid (not recommended).** Needed only for
   non-spot lights; out of scope for the uses in the wishlist (door shafts,
   window bars, fan blades), all of which are spots.

Scope limit to state in the PR: **spot lights only** in v1. Point lights keep
the existing 1D shadow map plus (optionally) the cheap actor columns below.

### How the existing 2D shadow map could include actors cheaply (22a)

The map stores, per angular texel, the squared horizontal distance to the
nearest wall; a fragment is lit when its own distance is not greater
(`sampleShadowmap`, `main.fp:490-522`; PCF variant 523-561). A 2D circle can be
folded into exactly that value by taking the **far** ray/circle intersection and
storing `min(wall_t, actor_far_t)`. The far intersection is the trick that makes
it self-shadow-safe: a fragment on the caster's own surface is *inside* the
circle, nearer than the far exit, so it stays lit; a fragment on a wall behind
the actor is farther than the far exit and is shadowed. It costs one
ray/circle test per texel, and it is a column (no z), which matches the rest of
the map's 2D behaviour.

The same list must be consulted in **both** consumers: the CPU `RayTest`
(`hw_aabbtree.cpp:51-96`, used by `ShadowTest` for sprites) and the GPU
`shadowmap.fp` (used for geometry and models). The list can be built in
`CollectLights` (`hw_entrypoint.cpp:60-84`) with `BSPWalkCircle`
(`src/r_data/models.h:105-112`, the pattern used at `hw_spritelight.cpp:242`),
capped at 32 casters nearest the camera, uploaded as one more SSBO
(binding 7 is free; existing nodes/lines/lights are 4/5/6,
`src/common/rendering/hwrenderer/data/shaderuniforms.h:25-31`). With the cvar
off, count = 0 and the shader loop does nothing.

---

## Item 22 — Creature shadows ("see the shadow before the creature")

### Current behaviour
- Lights only get a shadow-map row if `FDynamicLight::shadowmapped` is true,
  which is set when the light is in front of a one-sided line's back face
  (`src/playsim/a_dynlight.cpp:512-527`, assigned 613, cleared 671). `CollectLights`
  then writes at most 1024 lights into the map (`hw_entrypoint.cpp:60-84`), and
  only if `gl_light_shadowmap` (default **false**, `hw_shadowmap.cpp:57`), SSBO
  support and `!LEVEL3_NOSHADOWMAP` all hold (`hw_entrypoint.cpp:103-118`).
- The tree contains only **one-sided** lines: `if (!maplines[i].backsector)`
  (`src/rendering/hwrenderer/doom_aabbtree.cpp:79-95`); polyobject lines go into
  the dynamic subtree (83-93). Two-sided walls never occlude, and nothing
  vertical exists at all.
- Shadows are applied per fragment to geometry and models
  (`main.fp:562-580`, called at `material_normal.fp:43-47`,
  `material_pbr.fp:125,165`, `material_specular.fp:39`) and per sprite on the
  CPU (`hw_spritelight.cpp:171`). Sprites and models never *cast*.
- The native blob shadow draws a black stencil sprite flattened to the floor
  under monsters/players (`r_actorspriteshadow`, default 1, `r_utility.cpp:
  103-128`; geometry at `hw_sprites.cpp:948-951,1097,1187,1397-1407`; drawn at
  `hw_bsp.cpp:592-601,625-633`). It is a straight-down blob: no light direction,
  no wall projection, no silhouette, and models are explicitly skipped
  (`hw_sprites.cpp:962-963`).

### Touch points
- 22a: `DoomLevelAABBTree` (`doom_aabbtree.h:24-39`) / `LevelAABBTree::RayTest`
  (`hw_aabbtree.cpp:51-96`) / `IShadowMap::ShadowTest` (`hw_shadowmap.cpp:84-90`);
  `shadowmap.fp:113-156,158-205`; `CollectLights` (`hw_entrypoint.cpp:60-84`);
  `IShadowMap::UploadLights`/`UploadAABBTree` (`hw_shadowmap.cpp:110-141`).
- 22b: `lightContribution` (`material_normal.fp:18-52`), PBR loops
  (`material_pbr.fp:81-186`), specular (`material_specular.fp:18-45`),
  `main.fp:562-580`; a new offscreen pass and target (GL `gl_framebuffer.cpp:
  426-451` as the model for a per-frame pass; Vulkan `vk_postprocess.cpp:
  343-356`); sprite quad/vertex construction for the caster pass
  (`hw_sprites.cpp:623-637`); `CollectLights`.

### Design (opt-in, zero cost when unused)
- **22a, S.** Cvar `gl_shadowmap_actors` (default 0). `CollectLights` gathers up
  to 32 actors flagged `RF_CASTSPRITESHADOW` (or monsters/players, matching
  `R_ShouldDrawSpriteShadow`'s mode 2, `r_utility.cpp:1280-1284`) within a radius
  around the camera (the camera is already captured by the lambda at
  `hw_entrypoint.cpp:106-108`, so pass its position in) via `BSPWalkCircle`,
  deduped by `validcount`. Upload
  `vec4(x, y, radius, 0)` per actor. CPU `RayTest` and `shadowmap.fp` each take
  the far ray/circle exit and `min()` it with the wall hit. Cost when off: one
  uniform and a zero-iteration loop.
- **22b, L.** `gl_shadowmap_sprites` (default 0). For each participating spot
  light (cap 4 per frame), render the flagged actors' sprite quads into one tile
  of an R32F atlas, oriented to the light rather than the camera, with the
  sprite texture, alpha test and normal depth test. Bind the atlas at a new
  sampler; in `LightProject`, compare `dist` against `data[15]`'s tile. Only
  actors inside the light radius are drawn. Cost when off: no pass,
  `data[15] == 0`, and one uniform branch per light in the shader.
- Reuse `RF_CASTSPRITESHADOW` rather than inventing a flag; it already means
  "this actor may cast a sprite shadow".

### OpenGL vs Vulkan
- 22a is the easy one: the shadow map and its shader are already duplicated in
  both backends (`gl_framebuffer.cpp:426-451`, `vk_postprocess.cpp:343-356`,
  `vk_texture.cpp:163-179`) and both bind the same three SSBOs
  (`vk_descriptorset.cpp:218-224`). Adding a fourth buffer is one binding in
  each. GL needs SSBO (already required by the shadow path).
- 22b needs a **new offscreen geometry pass**, which neither backend has:
  `hw_postprocess`'s `PPRenderState::Draw()` only draws a full-screen quad
  (`src/common/rendering/hwrenderer/postprocessing/hw_postprocess.h:118-135`);
  the existing `CopyToTexture` (`vk_pprenderstate.cpp:100`) is a blit, not
  geometry. GL: an FBO with the atlas tile. Vulkan: a render pass, pipeline,
  descriptor set and `VkImageTransition` for the tile. This is the bulk of the
  effort and is written twice.
- Vulkan ray-traced shadows use `TopLevelAS` (`main.fp:380-452`,
  `vk_raytrace.cpp:49-55,140-160`) built **from the level mesh only**
  (`SetLevelMesh`), so the RT path also cannot see actors. Either add actors to
  the TLAS or accept that 22a/b only apply to the raster shadow path. Note this
  in the PR.

### Effort and risks
- 22a: **S** (half a day to a day, plus testing).
- 22b: **L** (a week+, mostly the two offscreen passes and the atlas plumbing).
- Risks: shadow acne on the caster pass (bias tuning); the 1D map's 256-texel
  angular resolution makes slight columns chunky (PCF hides some of it); perf
  of the per-texel circle loop (cap the list; distance-cull in the shader); the
  CPU sprite path becomes O(sprites × lights × actors), so keep a cheap
  radius early-out there;
  sprite lighting is CPU and cannot see 22b (models and geometry can); portals:
  the CPU shadow test uses raw `light->Pos` while the light list uses
  `PosRelative` (`hw_spritelight.cpp:134-147` vs `171`), so lights and sprites in
  different portal groups already disagree — 22 inherits that bug and should be
  fixed with #2 first. None of this touches the playsim, so no demo/save risk.

### Overlaps
- **#2 portal transforms: yes.** Light/surface positions across portal groups
  are displacement-only; actor shadows will be visibly wrong at portal
  boundaries until #2 lands.
- #1 depth: no. #8 scene copy: no. #11 reverb: no.

### Upstream-friendliness
22a: medium — small, gated, and fixes a long-standing gap in an old feature.
22b: low — a new rendering feature with new resources and a new pass; better
kept in the fork, with the projection helper offered upstream separately if 23
lands first.

---

## Item 23 — Projected-texture lights (cookies)

### Current behaviour
- Spot lights exist and are fully parameterised, but the light contributes a
  smooth cone only: `spotLightAttenuation` (`main.fp:602-606`), applied in
  `material_normal.fp:35-36`, `material_pbr.fp:119,159`,
  `material_specular.fp:31-32`. There is no light projection, projector, gobo
  or cookie anywhere: the shader prolog has `tex`, `ShadowMap`, `LightMap` and
  `texture2..12` only (`gl_shader.cpp:405-418`; Vulkan `vk_shader.cpp:
  184-185,268-279`), and the light record's last two floats are unused
  (`hw_dynlightdata.cpp:150-151`).
- Lights can be animated (colour/radius cycling, `a_dynlight.cpp:220-341`) and
  can track an actor's yaw/pitch (`UpdateLocation`, `a_dynlight.cpp:343-395`;
  spot angles from GLDEFS `gldefs.cpp:520-527` or ZScript
  `dynlights.zs:22-38`).

### Touch points
- `FLightDefaults`/`FDynamicLight` (`src/playsim/a_dynlight.h:74-172,231-305`);
  the pointer pattern used for spot angles (`AttachLight`,
  `src/playsim/a_dynlight.cpp:76-93`; `ApplyProperties`,
  `src/r_data/a_dynlightdata.cpp:111-145`).
- ZScript `DynamicLight` (`dynlights.zs:20-137`), name table
  (`src/namedef.h:660`), and `DObject::TextureIDVar` (`src/common/objects/
  dobject.h:438`) for reading a `TextureID` field.
- GLDEFS light parser: `LightTags[]` (`gldefs.cpp:160-188`) and the switch
  — **five copies** at `gldefs.cpp:523,628,736,843,947`.
- Upload: `AddLightToList` (`hw_dynlightdata.cpp:67-152`); record stride is a
  hard 4×vec4 (`hw_lightbuffer.cpp:22-23`) with `i += 4` loops in all three
  material shaders, so use the two free floats and **do not** grow the record
  in v1.
- Sampler: GL prolog (`gl_shader.cpp:405-418`) and unit assignment
  (`gl_shader.cpp:774-786`); Vulkan fixed set (`vk_shader.cpp:184-185`,
  `vk_descriptorset.cpp:267-286`) and pool sizes (288-302).
- Texture atlas creation: model on `PPCustomShaderInstance::SetTextures`,
  which already converts an `FGameTexture` to an RGBA8 `PPTexture`
  (`hw_postprocess.cpp:1041-1090`).

### Design (opt-in, zero cost when unused)
- v1: spot lights only. `light->cookieIndex = N` in `data[14]` (0 = none);
  `data[15]` is the actor-shadow tile (0 = none), shared with 22b. A cookie's
  aspect/scale is baked into its atlas tile, so no extra per-light float is
  needed. A new `CookieAtlas`
  (RGBA8, 16×256² tiles) bound once per frame. In `LightProject` (above), sample
  `uv` and multiply the cone attenuation by the texel. Because the atlas is
  indexed per light, two lights can use different cookies; changing one at
  runtime re-uploads only that tile.
- Declaration, two routes, both worth having:
  - ZScript: `TextureID Cookie;` on `DynamicLight` plus a `cookie` flag/scale.
    This is animatable per tic and works for actor-attached lights. Read it via
    `TextureIDVar(NAME_Cookie)` and cache the pointer like `pSpotInnerAngle`
    (`a_dynlight.cpp:80-81`).
  - GLDEFS: `cookie "TEXNAME"` in the light block. Add the tag once and to all
    five switch copies.
- Zero cost: maps without cookies upload nothing, every light has index 0, and
  the shader takes a uniform branch. If a strict-zero variant is wanted, compile
  a `#define COOKIE` material variant through the existing shader-defines path
  (`gl_shader.cpp:Compile`, around 830+), at the cost of doubling shader count.

### OpenGL vs Vulkan
- The shader-side work is shared (`main.fp` + three material files). GL needs one
  more sampler unit: units 0–14 are used by `tex` and the `texture2..15` slots,
  16 is `ShadowMap`, 17 is `LightMap` (`gl_shader.cpp:774-786`), so use 18. GL 3.3 only guarantees 16
  fragment texture units (`src/common/rendering/gl_load/gl_interface.cpp:
  133-135`); this engine already exceeds that with 16/17, so a capability query
  and a graceful "cookies off" is the honest fix, and GLES should be excluded.
- Vulkan: add a binding to the fixed set 0 (currently ShadowMap=0, LightMap=1,
  optional TLAS=2), update `CreateFixedSetLayout` (`vk_descriptorset.cpp:
  267-286`) and the pool sizes (288-302), and a combined-image-sampler write in
  every draw. This is small but touches every shader's descriptor set.
- An atlas avoids new array resources entirely (`Create2DTexture` exists in GL,
  `gl_renderbuffers.cpp:627-650`; Vulkan PP textures are 2D only,
  `hw_postprocess.h:59`).

### Effort and risks
- **M** (2–4 days) for v1 with the atlas, including the five GLDEFS parsers.
- Risks: sprite lighting is CPU (`hw_spritelight.cpp:100-207`) and cannot sample
  the cookie, so sprites will be lit by the bare cone — visible on the creature
  standing in a window-bar shaft, the exact use case. Options: accept it for
  v1, tint sprites by the cookie's average colour, or move sprite lighting to
  the GPU (not scoped). Basis degeneracy at vertical pitch; portal groups again
  (a light and its surface must be in the same group for the basis to make
  sense); atlas bleeding/filtering; texture-unit ceiling; the cookie must be
  unlit/sRGB-handled consistently with other light textures.

### Overlaps
- **#2: yes**, for lights/surfaces across portal groups (same issue as 22).
- #8: no — this samples a static texture, not the scene. #1: no. #11: no.
  #23 and 22b share 100% of the projection code; implement them together.

### Upstream-friendliness
Medium. A spot-only, GLDEFS/ZScript-declared cookie is a self-contained feature
that upstream could take; the dynamic actor-shadow atlas is fork-only.

---

## Item 24 — Scaled portals ("bigger on the inside")

### Current behaviour
- Line portals carry rotation and translation only: `FLinePortal` has
  `mDisplacement`, `mAngleDiff`, `mSinRot`, `mCosRot`, no scale
  (`src/playsim/portal.h:201-225`). Rotation is computed in
  `SetPortalRotation` (`src/playsim/portal.cpp:203-226`).
- Every consumer goes through four functions: `P_TranslatePortalXY`
  (`portal.cpp:441-467`), `P_TranslatePortalVXVY` (469-486),
  `P_TranslatePortalAngle` (488-501), `P_TranslatePortalZ` (503-524). Actor
  crossing is at `p_map.cpp:2561-2666` (translate position, velocity, angle,
  then `LinkToWorld`); identical calls in `P_TranslatePortal*` hit
  `PortalRelocate` for traces (`p_maputl.cpp:1612-1633`) and in
  `FTraceInfo::EnterLinePortal` (`src/playsim/p_trace.cpp:239-262`).
- Rendering translates the *viewpoint* and reuses the same projection:
  `HWLineToLinePortal::Setup` (`hw_portal.cpp:624-673`, translations at
  637-644) → `HWDrawInfo::SetupView`/`SetViewMatrix` (`hw_drawinfo.cpp:405-433`).
  The software renderer does the same (`r_portal.cpp:375-379`). Sprites behind a
  portal are translated individually (`hw_sprites.cpp:1786-1800`).
- Portal creation is from line args (`src/maploader/specials.cpp:90-128`);
  `Line_SetPortal` has four args (`src/playsim/actionspecials.h:169`); the
  loader reads arg0 (tag), arg2 (type) and arg3 (align), and arg1 is not read
  in this path (`specials.cpp:92-118`). Portals are saved as origin/destination/displacement/type/flags/
  align (`src/p_saveg.cpp:458-470`). Note `FLinePortal::Clear()` memsets the
  struct (`portal.h:221-224`), so any `mScale` field must be reset to **1.0**
  explicitly or every portal becomes a point.
- The only scale convention in the codebase is the skybox's 16× fog divisor
  (`hw_portal.cpp:735-737`); it is not a geometry scale.

### Design (opt-in, zero cost when unused)
Two milestones; be explicit in the PR that they are separate.

- **M1 — visual-only scale (M).**
  - `double mScale` on `FLinePortal`, set from a new `Line_SetPortal` arg (grow
    the special to 5 args in `actionspecials.h:169`, parse in
    `specials.cpp:90-128`) or a UDMF line key. Default 1.
  - `P_TranslatePortalXY` multiplies the portal-relative offset by `1/mScale`
    (one multiply, skipped when 1).
  - `HWLineToLinePortal::Setup` multiplies the view matrix on the **right** by a
    uniform scale-about-point matrix, so world coordinates are scaled before the
    view transform. `SetViewMatrix` already builds a scale into the matrix
    (`hw_drawinfo.cpp:405-421`, the `scale(-mult, planemult, 1)` line), so this
    is a parameter, not a rewrite. Scale the projection's near/far by the same
    factor; a uniform 3D similarity is then exactly representable.
  - `ClearClipper` (`hw_portal.cpp:419-449`) computes angles from world
    positions; it must apply the same scale or it will over/under-clip. Cheapest
    correct version: apply the scale to the line endpoints it uses.
  - Everything else (sprites, models, lights, flats) is drawn through the same
    view matrix and follows for free; fog distances and shadow tests are in
    destination-space and stay consistent.
  - **Caveat:** traces and hitscans still use unscaled geometry, so shooting at
    what you see through a scaled portal will miss. For a purely decorative
    window (e.g. the "near sky", E15–E16, or a doll-house view) that may be
    acceptable; if the portal is shootable, M1 needs the trace scale too.
- **M2 — traversal (XL).**
  - On crossing, the actor's world scale changes: `radius`/`Height`
    (`actor.h:1181`), `MaxStepHeight`/`MaxDropOffHeight` (1359-1360), `Speed`
    (1192), `Gravity` (1294), render `Scale` (1153), `player->viewheight`
    (`d_player.h:351,461-478`), plus projectile speed and damage ranges.
  - `Radius` is `native readonly` to ZScript (`actor.zs:226-228`, property 419),
    so this must be engine-side; `A_SetSize` (`p_actionfunctions.cpp:
    4988-5024`) exists but relinks the actor and is circle-only.
  - Keep a per-actor scale stack (portal → scale) and restore on the return
    crossing; a player who leaves via a different portal must not stay shrunk.
  - Everything that reads world distances must be audited: `P_CheckSight`
    (`p_sight.cpp:840-951`), `P_RecursiveSound` (`p_enemy.cpp:120-213`),
    `P_LineAttack` (`p_map.cpp:4648`), `P_RadiusAttack`, item pickup, use
    ranges, `CalcPosVel` (`s_doomsound.cpp:1023-1138`), AI melee/ranged ranges.
  - Saves must persist the scale; demos will desync unless the scale is a pure
    function of the portal geometry (it is, if recomputed), but movement
    physics will still differ from vanilla, so demos through scaled portals
    are effectively invalid.

### OpenGL vs Vulkan
No backend-specific work in M1: the view matrix is a uniform consumed by both
(`src/common/rendering/hwrenderer/data/hw_viewpointuniforms.h`), the clipper is
shared, and the portal setup is shared. M2 is playsim. If instead of a view
matrix you render the far side to a texture and composite (the "portal texture"
approach), that would become #8's scene-copy problem and would need both
backends — do not do that.

### Effort and risks
- M1: **M**. M2: **XL**.
- Risks: clipping; precision at large coordinates; billboard/particle sizes;
  lights (a scaled light radius is in world units — under a scaled view it
  scales visually for free, but the shadow map's light position is world-space
  and consistent); fog density (distance is scaled, so fog is wrong by the
  scale factor unless the density is divided by it — a one-line fix but easy to
  miss); portals within portals (the scale must compose); `mDisplacement`
  linked portals (no rotation today, scale would need a new path); z scaling
  must be uniform or floors stop matching; saves; demos; multiplayer.

### Overlaps
- **#2 portal transforms: yes, entirely** — the same four functions and the same
  consumers; do #2 first and add scale as the fifth field.
- #8 scene copy: only if you choose render-to-texture instead of a view matrix
  (not recommended).
- #1: no. #11: no.

### Upstream-friendliness
Low. It changes playsim-observable behaviour, breaks demo compatibility through
scaled portals, and has a large edge-case surface. Keep it in the fork; a
visual-only `portalscale` UDMF key could be proposed separately if M1 proves
stable.

---

## Item 25 — Water refraction and underwater fog

### Current behaviour
- A water surface is an ordinary flat. Animation comes from texture animation or
  the built-in warp shaders, which already have a time uniform
  (`func_warp1.fp:18-29`, `timer` declared `gl_shader.cpp:421`). Normal maps are
  supported for any texture via `materials/normalmaps/<name>` (
  `gametexture.cpp:145-155`) but are static.
- Translucency is native: `Sector_SetTranslucent` (`p_lnspec.cpp:2252-2267`)
  writes `planes[pos].alpha` (`r_defs.h:903-916`); flats with alpha go to the
  translucent list (`AddFlat`, `src/rendering/hwrenderer/scene/
  hw_drawlistadd.cpp:99-130`).
- Plane reflection is native: `Sector_SetPlaneReflection`
  (`p_lnspec.cpp:3420-3434`, `reflect[]` at `r_defs.h:1155`, gated by
  `gl_plane_reflection`, `src/common/rendering/hwrenderer/data/hw_cvars.cpp:
  51-54`) turns the plane into a **plane-mirror portal** — a second stencil-based
  scene render (`hw_sky.cpp:181-190`, `hw_portal.cpp:270-360`), with the flat
  drawn at `alpha = 1 - reflect` (`hw_flats.cpp:544,601`).
- Water state is native: `AActor::waterlevel` 0–3 and `waterdepth`
  (`p_mobj.cpp:5384-5405`, `actor.h:1279`), from `SECMF_UNDERWATER` or swimmable
  3D floors (5267-5315). The sound engine uses exactly `waterlevel == 3`
  (`s_doomsound.cpp:795`). **The hardware renderer ignores it entirely** — no
  underwater tint, fog or distortion (searched; only the software renderer and
  the audio code mention underwater).
- Fog is per sector through the colormap (`hw_lighting.cpp:159-200`) and
  `Sector_SetColor`/`Sector_SetFade` (`p_lnspec.cpp:2421-2445`). `FF_FOG` 3D
  floors render a fog boundary you can see into (`hw_flats.cpp:457-478`,
  `hw_walls.cpp:1773-1790`, `fogboundary.fp:31-52`) — a coarse native fog
  volume.
- No refraction anywhere; the scene copy is #8's job.

### Touch points
- Underwater fog: `main.fp` fog block (862-905) and `getLightColor`
  (714-786); `HWViewpointUniforms` for a water-plane uniform
  (`hw_viewpointuniforms.h`); the camera's water state at `p_mobj.cpp:5384`
  (read `players[consoleplayer].camera->waterlevel` in the scene setup);
  `hw_setcolor.cpp:94-150` where fog density is chosen per sector.
- Refraction: `AddFlat` (`hw_drawlistadd.cpp:99-130`) to move flagged water
  flats into the translucent pass; the draw-list execution order in
  `hw_drawlist.cpp`; the scene copy from #8 (`OpenGLFrameBuffer::
  RenderTextureView`, `gl_framebuffer.cpp:212`; Vulkan
  `VkPPRenderState::CopyToTexture`, `vk_pprenderstate.cpp:100`); a material
  layer / extra sampler in `SetMaterialProps` (`main.fp:671-695`) and
  `ApplyNormalMap` (`main.fp:635-668`).
- Animated normal: a custom material shader using `timer` — native today.

### Design (opt-in, zero cost when unused)
- **(a) Underwater fog, M.** Reuse `SECMF_UNDERWATER` (already set by maps) and
  the water surface plane, behind a cvar/UDMF key so existing maps are
  unchanged. Shader tests `pixelpos.y < plane` (or above, for
  a ceiling water plane) and applies extra fog with the water colour/density,
  blended over the existing fog. When the camera itself is `waterlevel == 3`,
  use the stronger "inside" density and a tint. Volume membership: v1 tests only
  the plane and the owning sector's section; proper volumes are item 21's height
  fog. Zero cost when no sector carries the flag (a uniform compare).
- **(b) Refraction, L (needs #8).** Draw flagged water flats in the translucent
  pass; at the opaque/translucent boundary, copy scene colour once (half-res);
  the water shader samples that copy with an offset derived from the animated
  normal and screen-space position, tinted by depth/fog. Self-visibility is
  handled by drawing water after the copy, which translucents already do.
- **(c) Animated surface, S/native.** Normal map via `materials/normalmaps/`
  plus a custom material shader that scrolls/two-samples the normal with
  `timer`. No engine change; do this first, it is most of the look.

### OpenGL vs Vulkan
- (a) is shader-only, both backends.
- (b) uses the postprocess copy path that both backends implement
  (`PPTexture`, `PPRenderState::CopyToTexture`, `gl_renderbuffers.cpp:875-940`,
  `vk_pprenderstate.cpp:100`). The copy itself is cross-backend; the per-pass
  binding and the water material shader are shared. The real risk is draw-order
  plumbing in `hw_drawlist`, not the API.

### Effort and risks
- (a) **M**; (b) **L**; (c) **S** or native.
- Risks: draw order and the copy cost (half-res, only when water is visible);
  MSAA resolve; portals and mirrors double-render, so the copy must happen per
  view; the waterline (camera straddling the plane) needs a smooth transition or
  a hard cut; depth precision; the underwater fog must not fight sector fog or
  `FF_FOG`; refraction of sprites drawn after the copy is impossible without a
  second copy.
- No playsim impact; demos safe.

### Overlaps
- **#8 scene copy: yes, a hard dependency for (b).**
- **#1 depth: yes for the volume version of (a)** (per-fragment depth is already
  available in `pixelpos.w`, but a true volume needs the depth buffer and item
  1's work).
- **#11 reverb: shares the underwater state** (`s_doomsound.cpp:795`); keep one
  definition of "underwater" for audio and video.
- #2: only insofar as water is seen through portals (no special handling).

### Upstream-friendliness
(a) medium — underwater fog is a long-standing GZDoom request and can be a
sector flag + shader block. (b) low–medium — a new material feature that needs
the scene copy; better as a fork feature until #8 exists upstream.

---

## Item 26 — Collision hulls for models

### Current behaviour
- All actor collision is a vertical cylinder: `radius` and `Height`
  (`actor.h:1181`), broadphase from `FBoundingBox(x, y, radius)`
  (`src/common/utility/m_bbox.h:55`), narrow phase is
  `blockdist = thing->radius + tm.thing->radius` plus an axis-aligned test
  (`PIT_CheckThing`, `p_map.cpp:1359-1381`), and lines are tested against the
  moving actor's AABB (`PIT_CheckLine`, `p_map.cpp:824-895`;
  `BoxOnLineSide`, `p_maputl.cpp:2030-2067`; floor/ceiling resolution in
  `P_CheckPosition`, `p_map.cpp:1770-1830`).
- Models are render-only. `FSpriteModelFrame` holds scale/offset/rotation per
  actor class and frame (`src/common/models/model.h:52-85`); `FModel` has no
  bounds at all (`model.h:103-160`). `AActor::Scale` is explicitly a rendering
  field (`actor.h:1153`); collision uses `radius`/`Height`.
- `CanCollideWith` is a ZScript virtual called from `PIT_CheckThing` only after
  the radius overlap test (`p_map.cpp:1472-1475`; `actor.zs:664-667`), so it
  can veto a collision but cannot create one where the circles do not overlap.
  It cannot implement hulls.
- Native stopgaps: `A_SetSize` (circle only), or a compound collider made of
  invisible solid actors (costs actors, ticks and blockmap entries).

### Touch points
- `PIT_CheckThing` (`p_map.cpp:1359-1500+`), `PIT_CheckLine` (824-895),
  `P_CheckPosition` (1770-1830), `FBoundingBox` (`m_bbox.h:39-100`),
  `AActor` fields (`actor.h:1153,1181`).
- Model data: `FModel`/`FSpriteModelFrame` (`model.h:52-85,103-160`), loaders
  `models_iqm.cpp`, `models_md3.cpp`; `MODELDEF` parsing in `src/r_data/`.
- Savegames and networking for any new actor state.

### Design (opt-in, zero cost when unused)
- `FCollisionHull`: a small array of 2D convex polygons with a z range (one
  polygon covers most props; two fit a train car). Declared in `MODELDEF` or
  ZScript; derived offline or at load from the model's **base-pose** vertices
  (not per animation frame — a hull that breathes with the idle animation is
  worse than a cylinder).
- Broadphase unchanged: use the circumscribed radius so the blockmap and
  `FBoundingBox` iteration stay as they are. Narrow phase:
  - hull vs hull: 2D SAT on the two polygons, plus z-range overlap;
  - hull vs cylinder: closest point on the polygon to the circle centre;
  - hull vs line: polygon edges against the line, still 2D, then reuse the
    existing slide/step logic.
- v1 applies hulls only to non-monster, non-player props; everything else keeps
  the cylinder. That keeps AI, pathing and demo risk bounded.
- Zero cost: `hull == nullptr` → the existing path, one pointer check per
  collision test. A cvar (`sv_collisionhulls`) for A/B testing.
- Debug: a cvar drawing hull outlines (renderer only) is worth the day it costs.

### OpenGL vs Vulkan
None: this is playsim. A debug draw would add a draw-list entry like a decal
(`hw_decal.cpp:38`), which both backends already handle.

### Effort and risks
- **L** for props against static geometry and other actors; **XL** for a
  complete system (monsters, pathing, saves, net, demos, polyobjects).
- Risks: demo compatibility (any collision change is observable); savegame
  format; `P_CheckPosition`/`PIT_CheckThing` are hot; actors spawning inside
  geometry when a hull is larger than the old circle; stepping/sliding
  behaviour; portals and 3D floors; model scale/offset versus hull units.

### Overlaps
None of #1, #2, #8, #11. Conceptually adjacent to #3 (per-pixel hit tests) and
#16 (hit position): together they would make the playsim geometry-aware.

### Upstream-friendliness
Low. It is a visible playsim change; an opt-in `MODELDEF` hull for decorative
props might be accepted upstream, but the full system is fork material.

---

## Item 27 — Path-based sound occlusion

### Current behaviour
- `P_RecursiveSound` floods sectors and records a `soundblocks` count from
  `ML_SOUNDBLOCK` lines (`src/playsim/p_enemy.cpp:120-213`; the mark is at
  197-207), but the count is only used to avoid re-flooding — it never reaches
  the mixer. The flood is for waking monsters (`P_NoiseAlert`,
  `p_enemy.cpp:228-245`).
- The sound engine performs **no** line-of-sight or occlusion test at all
  (searched all of `src/sound` and `src/common/audio`).
- Positions are displacement-only: `DoomSoundEngine::CalcPosVel`
  (`src/sound/s_doomsound.cpp:1023-1138`) repositions every source with
  `primaryLevel->Displacements.getOffset(...)` and no rotation or path. This is
  the same defect as item 2.
- Area sounds already do a miniature version of "sound comes from the doorway":
  when the listener is outside the sector, `CalcSectorSoundOrg` uses the nearest
  point on the sector's boundary as the perceived origin
  (`s_doomsound.cpp:950-989`, used from `CalcPosVel` at 1085-1095).
- OpenAL side: one global direct lowpass (`EnvFilters[0]`) and one auxiliary
  filter (`EnvFilters[1]`) are created once (`oalsound.cpp:866-888`), used for
  underwater (`1789-1860`), and applied per source at start in `StartSound3D`
  (`oalsound.cpp:1382`, filter block at 1480-1495). `UpdateSoundParams3D`
  (1709-1737) updates only position, velocity and manual rolloff, so occlusion
  has to add a filter update there. Per-source filters are therefore already
  possible; the code just always uses the same two.
- `SoundEngine::UpdateSounds` calls `CalcPosVel` and `UpdateSoundParams3D` for
  every 3D channel on every update (`src/common/audio/sound/s_sound.cpp:
  1259-1273`), so a per-source occlusion value can be refreshed each tic.

### Touch points
- Path: `P_RecursiveSound` (`p_enemy.cpp:120-213`) as the traversal model,
  `PORTF_SOUNDTRAVERSE` (`p_enemy.cpp:165-176`), `ML_SOUNDBLOCK` (195-205).
- Perceived origin: `CalcSectorSoundOrg` (`s_doomsound.cpp:950-989`) and
  `CalcPosVel` (1023-1138); portal translation would use `P_TranslatePortalXY`
  (`portal.cpp:441-467`).
- Mixer: `StartSound3D` (`oalsound.cpp:1382-1554`) and
  `UpdateSoundParams3D` (1709-1737), filter creation (866-888), a new
  `FSoundChan` field in `src/common/audio/sound/s_sound.h`.
- Cache keyed on (source sector, listener sector, portal path) with
  invalidation when either actor changes sector (`AActor::Sector`,
  `LinkToWorld`).

### Design (opt-in, zero cost when unused)
- Cvar `snd_occlusion` (default 0). On sound start, BFS from the source sector to
  the listener sector over sector adjacency and line portals, weighting each
  crossing: a normal two-sided opening 0, `ML_SOUNDBLOCK` +0.5, a closed sector
  portal +1, a line portal +0.25 (or 0 if `PORTF_SOUNDTRAVERSE` is absent and the
  path must go around). Clamp the accumulated occlusion.
- Map occlusion to a small pool of lowpass filters (e.g. 12 `AL_FILTER_LOWPASS`
  objects with `AL_LOWPASS_GAINHF` from 1.0 down to 0.125), multiplied by the
  underwater factor so the two features compose. Assign in
  `UpdateSoundParams3D`; when occlusion is 0, use `EnvFilters[0]` exactly as
  today.
- Direction: if the direct path is blocked, move the perceived origin to the
  first portal aperture or the mouth of the first doorway on the path (the
  `CalcSectorSoundOrg` idea, extended along the path), using
  `P_TranslatePortalXY` so rotation is honoured (needs #2).
- Cache the path per (source sector, listener sector); recompute only when
  either changes. Recompute occlusion for every 3D channel at most once per tic.
- Zero cost when off: no traversal, no filter selection, the channel flag is
  zero, and `UpdateSoundParams3D` takes the existing branch.

### OpenGL vs Vulkan
None: audio only, OpenAL/EFX filters. If the filter pool cannot be created, fall
back to the existing behaviour (the code already does this for EFX,
`oalsound.cpp:866-895`).

### Effort and risks
- **L** for the real version; **M** for a first pass that uses one
  `P_CheckSight` (or the existing `soundblocks` count) at sound start only and
  a 3-filter pool.
- Risks: cost per tic per channel (the cache is mandatory); portal paths through
  rotated portals need #2; `P_CheckSight` from the audio thread/main thread
  timing (sound updates run on the main thread, so this is safe, but keep it
  cheap); filter count and driver limits; reverb (#11) already owns the
  auxiliary send, so occlusion must use only the direct filter; sounds that
  move must re-evaluate; `CHANF_UI`/non-3D channels must be excluded.

### Overlaps
- **#2: yes** — portal paths and rotation are the same machinery, and #2 must
  land first for a correct result.
- **#11: yes** — both touch `EnvFilters`, the environment slot and the
  underwater state; design them together so occlusion multiplies rather than
  overwrites.
- #1, #8: no.

### Upstream-friendliness
Medium. OpenAL occlusion is a long-requested GZDoom feature; a path-based,
portal-aware implementation is novel and would need a cvar and a modest diff.
The first pass (sight test + filter pool) is a plausible upstream PR on its own.

---

## Recommended order

The wishlist's own order (22 and 23 together, then #2, then 24) is right, but
22a does not need 22b and is the cheapest win in this batch.

1. **22a** (S) — actor columns in the existing shadow map. Immediate "shadow
   before the creature" for point lights, no new resources.
2. **#2** (already scoped, L) — portal-correct sight, sound and light
   positions. 22b, 23 and 27 all depend on it for portal-heavy maps.
3. **23** (M) then **22b** (L) — one projection system, cookies first, then the
   dynamic actor depth atlas. They share all the shader code.
4. **25c** (S/native) — animated normal-mapped water; check the look before
   building anything.
5. **25a** (M) — underwater fog, using the existing `waterlevel` state.
6. **27** (L) — path-based occlusion, after #2.
7. **24 M1** (M) — visual scale on one or two decorative portals, as a
   showpiece; only then decide whether M2 (XL) is worth it.
8. **25b** (L) — refraction, when #8 has landed.
9. **26** (L/XL) — last; it is the only item here that can break demos.

## Summary table

| Item | Core work | Effort | #1 | #8 | #2 | #11 | Upstream |
|---|---|---|---|---|---|---|---|
| 22a actor columns | circle list, far-exit min, CPU+GPU | S | – | – | yes | – | medium |
| 22b sprite silhouette | light-space depth atlas + caster pass | L | – | – | yes | – | low |
| 23 cookies | projection helper + cookie atlas + GLDEFS/ZScript | M | – | – | yes | – | medium |
| 24 M1 visual scale | view matrix + clipper + portal field | M | – | (avoid) | yes | – | low |
| 24 M2 traversal | actor scale stack + trace/physics audit | XL | – | – | yes | – | low |
| 25a underwater fog | shader volume + water plane | M | partly | – | – | yes | medium |
| 25b refraction | scene copy + water pass | L | – | yes | – | – | low–medium |
| 25c animated normal | material shader + normal map | S | – | – | – | – | high |
| 26 hulls | new collision shape in playsim | L–XL | – | – | – | – | low |
| 27 occlusion | portal path + per-source lowpass | L | – | – | yes | yes | medium |

## Open questions for Josiah

- For 22, is the crude column shadow (22a) enough for the door-shaft moment, or
  is the sprite silhouette (22b) the actual requirement? 22a is a day; 22b is a
  week and a new pass in both backends.
- For 23, are the cookies always spot lights? If any use needs a point light
  (e.g. caustics on a cistern ceiling from an omni light), the design grows a
  cube/dual-paraboloid path and the effort goes up by one step.
- For 24, is traversable scaling needed, or is the "doll house / near sky" view
  enough? M1 alone is a contained feature; M2 is the largest single item in
  this batch and the only one that would invalidate demos.
- For 26, which props actually need hulls? If it is a handful of set pieces,
  hand-authored hulls in `MODELDEF` are much cheaper than deriving them from
  meshes, and keep the model loaders untouched.
- For 27, is the first-pass "sight test + filter pool" enough for the Armature
  tick, or is the portal-aware path required from day one? The latter needs #2.

## Things I could not confirm

- Whether GZDoom/UZDoom's sprite shadow cvars and flags are used by the current
  Null Run maps (could not check the maps; this is a content question).
- Exact OpenAL Soft behaviour when many `AL_DIRECT_FILTER` objects are switched
  per tic (not measurable without running).
- Whether the Vulkan RT path (`vk_raytrace`) is ever enabled in the fork's test
  setup; if it is, 22 needs a TLAS decision.
- The performance of a per-texel circle loop at 1024 lights on the target GPUs
  (needs a build; not run here).
