# Technical direction

**Status: provisional until M1 physics spike.** This is a decision boundary, not a package manifest.

## Constraints

- Desktop browser first; keyboard + pointer, with an accessible route through menus and independently adjustable audio channels.
- A real game application may use client JavaScript. Do not apply zero-JS website rules to game simulation.
- TypeScript, Vite and a mainstream browser-oriented 2D rendering/game framework are the planned foundation. Phaser is the initial rendering/scenes candidate.
- **Physics engine undecided.** Compare integrated Matter.js against Rapier 2D on the grapple prototype. Do not couple all gameplay data to a candidate before the spike.
- Fixed simulation ticks independent of render refresh. Avoid relying on wall-clock Playwright key timings for physics assertions.
- Separate simulation/state, level data, camera/rendering, audio and checkpoint serialization. Resist premature plugin architecture and custom editor work.
- Authored levels should be data driven, but their puzzle relationships must be actually implemented and testable.
- Production deployment target: Cloudflare Workers Static Assets serving a built static directory. No Worker runtime/backend, R2, D1 or KV by default.
- No external runtime assets or APIs required for basic play. Assets must be original or licensed; keep provenance when assets are introduced.

## Grapple spike is the architectural gate

Validate attachment selection and collision, cable length and tension, pendulum behavior, reeling, release momentum, midair reattachment, moving anchors and fast thin-wall contact. Record Matter/Rapier choice with measured tests and an ADR before building many levels. CCD/tunneling is an explicit case, not a detail to ignore.

## Test strategy

- Node-side physics and puzzle tests at controlled ticks where feasible.
- Development-only test bridge: explicit `step(ticks, inputs)` and read-only state snapshots. The production build must not expose it.
- Playwright for actual loading, input integration and progression; no wall-clock-only simulation assertions.
- Canvas screenshot comparisons only in a pinned, controlled renderer with tolerance. Do not substitute screenshots for functional assertions.
- Checkpoint restoration covers affected bodies, triggers, hazards and enemy state, not just player coordinates.

## Game-feel ownership

Keep tuneable values in one gameplay config once implemented: acceleration, maximum speed, jump, air control, gravity, grapple speed/length, damping, camera smoothing and audio intensity. A small dev-only adjustment UI may be added in M1; no extra library required initially.

## Open decisions

Final engine and physics backend; control scheme and accessibility alternatives; saved progress format; exact visual production pipeline; hosting URL; final title and commercial release status. Do not silently treat these as settled.
