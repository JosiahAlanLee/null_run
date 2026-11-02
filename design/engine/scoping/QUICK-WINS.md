# UZDoom wishlist: quick wins (already possible, or a few lines of change)

Verified against `~/dev/uzdoom-nullrun` @ `17480c8`. Sorted by bang-for-buck.
"Zero native code" means pure ZScript/MAPINFO/GLDEFS/UDMF today.

---

## QW-1 (item 15): log-only debug channel — ZERO native code

`Console.PrintfEx(int printlevel, ...)` is already native
(`wadsrc/static/zscript/engine/base.zs:704`) and the flags
`PRINT_LOG` ("only to logfile") and `PRINT_NONOTIFY` (1024, "do not add to
notify buffer") are already exposed (`base.zs:153-168`; honoured in
`PrintString`, `src/common/console/c_console.cpp:434`).

```csharp
// prints to the logfile and console, never to the screen notification area
Console.PrintfEx(PRINT_LOG | PRINT_NONOTIFY, "nr_debug: %s\n", msg);
```

Requires a logfile to exist (`-logfile <path>` on the command line, or the
`logfile` console command). Null Run's `nr_debug` cvar wrapper becomes one
line of ZScript. Optional 10-line native: `Console.Log(fmt, ...)` doing
exactly the above.

## QW-2 (item 16): hit position already available in ZScript

`Actor.LineTrace(...)` returns `FLineTraceData` with `HitLocation`,
`HitDir`, `HitTexture`, `HitActor`, `Distance`
(`wadsrc/static/zscript/actors/actor.zs:61-87`). Any ZScript-issued trace
(including custom weapon code that bypasses `A_FireBullets`) can read the
exact hit point today. The native gap is only `P_LineAttack`'s built-in path
(weapon puffs → `P_DamageMobj`), which is the item 16 fix — small.

## QW-3 (item 18): wet reflective floors — turn on what exists

- `Sector_SetPlaneReflection(tag, floor, ceiling)` line special is native
  (`src/playsim/p_lnspec.cpp:3420-3432`), or UDMF
  `floor_reflect` / `ceiling_reflect` (`src/maploader/udmf.cpp:2004-2009`).
- The renderer draws a true mirror under a translucent floor:
  `PORTALTYPE_PLANEMIRROR` (`src/rendering/hwrenderer/scene/hw_sky.cpp:181-190`)
  with `alpha = 1 - reflect` (`hw_flats.cpp:544,601`), gated by
  `gl_plane_reflection` (`hw_cvars.cpp:51-54`, default true).
- Wet look: GLDEFS `material` on the floor flat with `specular` +
  `glossiness`/`specularlevel` (or full PBR `normal metallic roughness ao`),
  parsed in `ParseMaterial` (`src/r_data/gldefs.cpp:1267-1535`) and applied
  via `FMaterial` (`src/common/textures/hw_material.cpp:76-89`).

Caveats to test in the target frame: reflections are skipped on sloped
planes (`p_lnspec.cpp:3425-3426`); mirror creation goes through `SkyPlane`
(`hw_sky.cpp:128-190`) — verify normal textured floors mirror correctly;
each reflective plane costs an extra scene pass.

## QW-4 (item 5, partial): normal maps + specular/PBR already parse for sprites

GLDEFS `material sprite <name> { normal ... specular ... }` is accepted by
the parser (`gldefs.cpp:1287-1288` keywords, type `sprite` at 1301) and
promoted to the specular/PBR shader in `FMaterial::FMaterial`
(`hw_material.cpp:76-89`) — the same path models use. Because each sprite
*rotation frame* is its own `FGameTexture`, per-rotation baked normal maps
can be assigned per frame with no engine change. What you do NOT get without
item 5 is per-pixel *dynamic light* response (sprites still receive one flat
aggregate light colour, `GetDynSpriteLight`,
`src/rendering/hwrenderer/scene/hw_spritelight.cpp:105-278`); the normal map
only affects the specular term of the flat light.

## QW-5 (item 9, partial): in-game ZScript network commands already exist

`EventHandler.SendNetworkCommand(name, args...)` and
`NetworkBuffer`/`NetworkCommand` (`wadsrc/static/zscript/events.zs:56-66,
244-246`; native `src/events.cpp:395-499`; wire format `DEM_ZSC_CMD`,
`src/d_net.cpp:3126-3145`) give Null Run an in-engine vararg RPC already —
useful for multiplayer playtests and for structuring the later event bus.
It does NOT reach off-machine tools; that is the item 9 native work (local
UDP/OSC socket).

## QW-6 (item 12, partial): ZScript canvas textures for live images

`TexMan.GetCanvas(name, ...)` returns a drawable hardware texture
(`wadsrc/static/zscript/engine/base.zs:344`, `Canvas` class `base.zs:540`;
upload-on-dirty in `src/rendering/hwrenderer/hw_entrypoint.cpp:357-376`).
A ZScript-side renderer can already draw CPU-generated frames into a texture
and show it on world monitors via `Screen.DrawTexture` / `ReplaceTextures` /
PP shader `Textures` map. The only missing piece for HydraPy is the
shared-memory data source (item 12 proper): without it the ZScript side would
have to copy pixels through the event bus (slow for 1080p60).

## QW-7 (item 14, partial): most test-isolation switches exist

`-nosound -nomusic -nosfx` (`src/common/audio/sound/i_sound.cpp:50-52,247-280`,
`NullSoundRenderer`), `snd_backend null` (i_sound.cpp:63,259), batch mode with
`-logfile`/`batchout` (`src/d_main.cpp:4181-4192`), `screenshot` ccmd
(`src/m_misc.cpp:664`), custom net port `-port`
(`src/common/engine/i_net.cpp:98-100`). Missing: deterministic fixed-tic
headless capture-and-exit mode and a guarantee that nothing touches the audio
device (that is the item 14 native addition — small).

## QW-8 (item 4, partial): `SpriteRotation`/`SpriteAngle` exist

Per-actor sprite yaw offset without touching the sprite bank:
`SpriteRotation`/`SpriteAngle` properties + `MF7_SPRITEANGLE`
(`wadsrc/static/zscript/actors/actor.zs:455,545-546`;
`src/playsim/actor.h:385`). Not pitch bands (item 4a) and no crossfade
(item 4b), but it already removes one class of popping.

## QW-9 (item 6, partial): light probes already light sprites

With the map's lightmap lump and `-enablelightmaps`
(`src/maploader/maploader.cpp:3331-3346`, experimental flag), `FindLightProbe`
(`src/rendering/hwrenderer/scene/hw_spritelight.cpp:34-89`) already adds
baked probe light to sprites, decals and the weapon HUD sprite
(`hw_sprites.cpp:172,303`, `hw_decal.cpp:60`, `hw_weapon.cpp:859`). Models do
not sample probes yet (item 6's gap), and actors do not sample the lightmap
texture itself.

## QW-10 (item 17, partial): bounce + friction primitives exist

`BounceFlags`/`bouncecount` with wall/floor bounce handling
(`src/playsim/p_mobj.cpp:2090-2184`), `MF8_NOFRICTION`/
`MF8_NOFRICTIONBOUNCE` (`src/playsim/actor.h:402-403`), ZScript `Friction`
(`wadsrc/static/zscript/actors/actor.zs:525,929`). A ZScript debris actor
with bounce + friction + `A_SetSpriteRotation` gets most of the "tins that
roll" feel today; the native item 17 additions are the rest-damping jitter
fix and any settle behaviour.

## QW-11 (item 2, partial): renderer already draws rotated portals correctly

The *visual* side of rotated portals works (rotation applied via
`FLinePortal::mSinRot/mCosRot/mAngleDiff`, `src/playsim/portal.h:209-211`,
set in `portal.cpp:200-230`, consumed by the HW portal code). Only sight,
hitscan, sound propagation and spatial audio ignore the rotation (item 2
proper). Argon's ZScript unfolded-ray `CheckSight` override
(`Actor.CheckSight`, `actor.zs:918`) remains the gameplay workaround until
then.
