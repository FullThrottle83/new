# SÖM

Working title for an original atmospheric, side-scrolling puzzle adventure about repairing the connections between isolated settlements in a suspended industrial valley.

**Status:** pre-production. This repository currently defines the project contract; it does not yet contain a playable game. The first implementation task is [M0](https://github.com/FullThrottle83/new/issues/1).

## The game

Edda, a former cable-network engineer, hears three bells from a tower that has been silent for years. She leaves an isolated outpost and discovers that settlements cut off by a central safety system are still inhabited. Her mechanical grappling tool becomes the main movement and puzzle mechanic: swing, anchor, pull, tension and connect. The world is eerie and quiet, but not devoid of life or hope.

The story, title and visual treatment are working creative decisions, not an instruction to imitate another game's protected content. See [Game vision](docs/GAME_VISION.md).

## Development

- [Technical direction](docs/TECHNICAL_DIRECTION.md) — provisional stack, constraints and decisions still open.
- [Roadmap](docs/ROADMAP.md) — serial foundation and first playable vertical slice.
- [Quality gates](docs/QUALITY_GATES.md) — what must be true before a feature is accepted.
- [Agent workflow](docs/AGENT_WORKFLOW.md) and [AGENTS.md](AGENTS.md) — task scope, ownership, handoffs and safeguards.
- [Decision log](docs/DECISIONS.md) — explicit commitments and open questions.

This project is designed for a browser build hosted as Cloudflare Workers Static Assets. No runtime backend or deployment is part of the foundation task.

## Next action

Complete issue #1. It is deliberately limited to project scaffolding and one static test scene. Do not implement the player, grapple physics, multiple levels, accounts or a custom engine in that task.

No automatic merge or deployment is enabled by these documents.
