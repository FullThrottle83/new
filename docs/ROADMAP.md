# Roadmap

Build the smallest evidence-producing slice; do not start a second workstream merely because additional agent quota is available.

| Gate | Work | Owner model | Exit evidence |
| --- | --- | --- | --- |
| M0 | Repository governance and static project skeleton | Maintainer, then one executor | Builds, renders one static test scene, no gameplay |
| M0.5 | CI and tick-test harness following M0 | One executor | Scope checks plus executable checks run reliably |
| M1a | Player movement and collision | One core owner | Deterministic ground, air, edge and restart tests |
| M1b | Grapple physics spike and engine decision | Same core owner | Swing/reel/release/re-attach, high-speed collision and replay tests; decision recorded |
| M2 | First authored playable route and checkpoints | Separate owners only after interfaces stabilize | Complete reachable route without debug bypasses |
| M3 | Atmosphere, animation, sound and browser QA | Independent art/audio and QA scopes | Coherent visuals, playable camera, audio controls, real browser evidence |
| M4 | 15–20-minute vertical slice | Integrator | A new player can finish workshop -> grapple -> chasm without assistance |

**Serial first:** M0 -> M0.5 -> M1a -> M1b. Do not parallelize overlapping core work. Later, at most two simultaneous gameplay PRs unless disjoint scopes and ownership are explicit.

The next active implementation issue is [#1](https://github.com/FullThrottle83/new/issues/1). Do not generate the entire campaign, a level editor, a bespoke engine or a server during this phase.
