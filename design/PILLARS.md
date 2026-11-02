# NULL RUN: design pillars (Josiah, 2026-11-02). Every job reads this.

> "This is no longer Doom. Things do not float as power-ups; everything should feel physical unless it has a lore reason. The guns and hands especially need to feel like they hurt to move and are heavy to lift. A cyborg is someone that lives with a lot of pain, generally speaking. If something made of rebar punches you it's nearly a one-shot, and probably would be for a normal human. The technology extended both your capacity and your capacity to suffer. This is Doom from someone who read the Purgatorio at 14."

Also standing: Rogue + Doom + Quake + Minecraft + Josiah's generative art + his grimoire. Influences (tone only): Shadowrun, SCP, Control, The X-Files, Dark Souls, Bloodborne, Backrooms, Dwarf Fortress, Slay the Spire, the Purgatorio. Careful cyborg, not charging space marine. Not gory. Materials at the edge of organic; tendons are halfway between fungus and plastic.

## 1. Physicality. Nothing floats without a lore reason
- No bobbing, spinning or hovering pickups. Items REST on surfaces with contact shadows: on shelves, tables and floors, in lockers, drawers, crates and stores cages, on heaps and bodies.
- Taking an item is a physical act: walk to it and use it (F), or pick it up with a short reach, never a vacuum-on-touch. Ammo comes in tins, strips and cells that look like what WEAPONS.md says they are.
- Exceptions need lore: sigil residue, Omission artefacts and the Photoform emulsion may float or drift because they are wrong.
- Props have mass. Heavy things don't slide, small things can be knocked about, debris settles.

## 2. Weight and pain in the body
- Weapons are heavy. Raising and lowering is slow and effortful; switching takes real time; heavy weapons slow movement. Sway lags with mass; recoil is big and settles slowly; aim drifts and must be held.
- Hands and arms visibly strain: knuckles whiten, the arm trembles on long holds and at low health, a slight shake after recoil, the servo whine and a breath under exertion. Reloads look like work, not choreography.
- The cyborg endures. Pain is the cost of capacity: overdrive hurts, and so do heavy lifts and long sprints, with a pain state that shows in sound, sway and vision. Never as flashing; desaturation, vignette and tremor are fine within the photosensitivity rules.

## 3. Lethality, both ways
- Enemies hit like what they are made of. A rebar Armature's strike is nearly a one-shot for a normal human; for the cyborg it's devastating but survivable, with consequences.
- So combat is about reading tells, positioning, cover (props now block), timing and avoidance. Few enemies at once; every one of them matters.
- Damage persists. Injuries carry a cost beyond the number: a limp, an unsteady aim, a lost overdrive. Healing is slow, physical and maybe painful (a field repair, a splint, a stores medical tin, with an animation). No floating medikits.
- The player's weapons are lethal too: things die properly when hit properly.

## 4. Purgatorio
- Suffering is the price of ascent, and chosen, not merely punishment: the player keeps going and bears it. Strata as terraces, each with its own discipline. The inhabitants "don't realize they stopped being people", like souls on the terraces. Treat this as tone and structure, not quotation; nothing derivative.

## 5. Designing for player panic (Josiah, 2026-11-02)
- Encounters escalate abruptly. A calm first impression is part of the threat. Sound arrives before sight.
- SPAWN PAIRING RULES are generator constraints, not suggestions:
  - **The Hollow and the Stone ReDead ALWAYS spawn together.** The Hollow is tree-like and still until it moves; alone, the player just shoots the tree before it moves. The ReDead (it walks and reaches, grips hard, shrieks when its mask is lifted) keeps the player busy while the Hollow comes alive. (The Hollow's author sheet has not reached the PC yet.)
- THE ARMATURE: at first it should seem fairly harmless. Free Armatures are stiff, slow, uncoordinated, easy to underestimate. Then a "tick tick tick" of ceramic claws, and they suddenly COORDINATE: synchronised windups, flanking, cutting off the retreat, converging. That tick is the panic trigger and the fair warning at once. In the ecology it's the Vore Spindle's arrival or control. Free versus controlled must read completely differently.
- Fairness still holds: every panic spike has an audible tell first, and lethality (section 3) makes the tell matter.
- LIGHTING AND FOG ARE PANIC TOOLS (Josiah): lights that fail one by one as a threat approaches (slow fades and dying tubes, never strobe or flicker faster than about 2 Hz, no whole-frame jumps over the safety limit), fog that thickens or rolls in (sector fade colour and density ramps), a lamp the player relies on going out, and darkness that hides the coordinated Armatures until the tick. Use native UZDoom sector light and fade ramps (Light_Fade, Sector_SetFade and similar) plus dynamic-light toggles, all driven by encounter state.
- SHOW LESS (Josiah: "You can get a long way with sprites and good fog and set design. Hell, no one really saw the monsters in The Fog."). Creatures are mostly silhouettes, glints, sounds and shapes in haze until they're close; full detail is the payoff, not the default. Fog and darkness are also how the sprite pipeline's limits (angle pops, flat lighting, distance detail) stop mattering. Set design and atmosphere carry the fear.
