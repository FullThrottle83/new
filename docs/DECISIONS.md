# Decision log

Decisions are explicit and reversible. Changes to shared architecture require a scoped issue and supporting evidence.

| ID | State | Decision | Rationale / revisit |
| --- | --- | --- | --- |
| D-001 | Accepted | Original IP and working title SÖM | Preserve atmospheric inspiration, not protected characters, levels or assets. |
| D-002 | Accepted | Vertical slice before full game | Test movement and grapple before content multiplication. |
| D-003 | Accepted | GitHub main is integration source; one task per PR | Avoid agent workspace drift. No automatic merge. |
| D-004 | Accepted | Deploy target is static Cloudflare assets, not a game backend | Browser executes the game. No deploy in M0. |
| D-005 | Provisional | Phaser + TypeScript + Vite | Validate dependency versions during M0. |
| D-006 | Open | Matter.js versus Rapier 2D | Choose after M1 grapple and tunneling tests. |
| D-007 | Open | Commercial release, final title, controls, save format and asset pipeline | Do not assume decisions or buy assets. |
