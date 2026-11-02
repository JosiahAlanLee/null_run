[PLAYTEST.md](PLAYTEST.md)

Candidate v7 runs and the requested behavior changes are implemented. Promotion is withheld pending review of the inherited transition safety failure. No map/environment change is proposed in this build.

## Build and use

Run `candidate-v7/run.sh`. It launches the engine directly, without a bridge, service, job, Pd or port, at 1280x800 in a window, with music bank root set and arrow turning bound. It checks PLAYTEST-IN-PROGRESS before launching. `-` / `=` trim walking in 0.05 steps, 0.80–1.50, archived; F7 changes careful/brisk. Options → Null Run movement contains the slider with two-decimal display. Each change prints one Walking line, including changes made while the menu pauses gameplay.

Large unchanged files and the original cistern-v6.pk3 are symlinked. `cistern-v7.pk3` is a ~53 KB override containing only player/creature code, movement controls/menu, three small debris textures and two new creature sounds. `src/` and `pack.py` reproduce it. Rebuild with `python pack.py`, then `python audit.py`.

## Implemented

- Careful 2.65 and brisk 4.03 m/s; Shift, Alt, weight and injury scale from nr_walk_scale. Cadence capped at 35/16 = 2.1875 Hz with stride length increasing with speed; eye dip and native sound share every footfall phase. SPEED.md contains engine-tic results for both profiles at .8, 1, 1.1, 1.5.
- Armature Fall uses the exported scrap bank over 36 tics, sounds a metallic settle, and retains the final heap indefinitely. Generic deaths follow Fall too. Cripple and frenzy art remain distinct (frenzy takes priority when combined).
- Navigation samples engine collision at a 16-u grid using a 22-u probe (actual Armature radius 18 plus 4 clearance), cardinal BFS paths, real 1.9 u/tic chase / .45 cripple speeds, right-hand separation, rolling eight-tic detection, repeat sidestep/backoff, reachable flank targets and seven-tic re-path intervals. Pack milling/tick/coordination timings remain v6. This is a Cistern-specific native implementation, not a general rotated-portal nav system. Static nav samples are built once per coordinator; later topology changes outside the tested gallery are not certified.
- Hollow alternates its pounce with a rooted blow: 42-tic windup, reversed unfolding art, fixed committed direction, 112-u / 24-degree strike cone for 100 Heavy damage and 35-tic recovery. Pounce remains 80 Heavy. Lateral movement or retreat avoids the second blow. The exported hit bank plays for 12 tics.
- Hollow death retains the collapse for 35 tics then replaces the body with 12 bark/root/lattice fragments. Debris uses the reviewed v2 resting threshold, restitution .25, friction, six quiet tics to sleep, explicit native CheckPosition floor queries every tic, and overlap kicks to wake. Settles at ages 27–30 tics in the clip; wake/re-sleep logged. It continues ticking even asleep to recheck floors and overlap.

## Evidence and scope

See EVIDENCE.md, SPEED.md, steering-final-proof/stalls.json, ui-proof/, plain-launch.json and AUDIT.json. Final steering: four 700-tic staged placements, packs 3/4/3/3, real Cistern geometry, observer invulnerable; stationary maxima 8/6/18/7 tics, rolling low-progress maxima 4/3/11/4. Longest stationary episode ends at tic 1890, role 2, (789.851,580.303). Intentional windup/strike/recovery and completed strike slots are excluded from chase-stall measurement, not relabelled as movement.

AUDIT.json asserts symlink targets resolve to exactly v6's originals and confirms unchanged C5Enemy, C5Stone, C5Encounter and coordinator environmental/timing logic. Existing maps, geometry, textures, lights, fog, signs and sounds are untouched; newly named creature sounds do not replace old cues. All debug output is PRINT_LOG|PRINT_NONOTIFY.

No branch, commit, push, PR, external post, delegate, persistent memory update or changes outside shared/codex. A local claim was used because the explicit job write boundary excludes shared/CLAIMS.md. The final response is the handoff.
