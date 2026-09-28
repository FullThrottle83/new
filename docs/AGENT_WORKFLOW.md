# Agent workflow

## Source of truth and entry

`AGENTS.md` is shared policy; `CLAUDE.md` and `GEMINI.md` only point to it. Issues define the requested behavior, while `tasks/N.scope` on the protected base branch grants path-level edit permission. Docs describe intent but never override task scope.

Before dispatch, the maintainer creates a scoped issue and checks active ownership. Each agent works on its own branch with one issue per PR and writes `Closes #N` in its PR body. An agent may open a PR, but must not merge, deploy, change policy or request new paid services unless that task explicitly authorizes it.

## Serialized foundation

M0 and M1 are sequential. Use a core integrator for movement and grapple physics. Other executors join only when they can work on independent modules. Do not assign multiple agents to the same hot files, even if separate branches are available.

Hot paths: package manifest/lockfile, bootstrap and scene registry, input mapping, physics core, game-feel config, shared asset registries, tests infrastructure, CI and deployment config. Prefer per-scene assets and module-local data; minimize central edit points.

Scope guard checks that the referenced issue is open, but **open issue state does not prove the PR is assigned to that issue**. The maintainer must verify the issue-to-PR relationship, especially for broad scopes, and avoid simultaneous PRs claiming the same task. Do not reopen an old task without reviewing its stale scope. Scope guard is a **diff policy, not a lock**. Task ownership is recorded in the issue/PR workflow and reviewed before dispatch. If overlaps occur, finish/integrate the earlier task or explicitly resequence; do not ask the agents to race.

## Acceptance

A PR needs an authorized scope, green checks, a relevant deterministic test for behavior changes, and actual browser verification when visual/gameplay behavior changed. A passing CI check never establishes that art direction or game feel is good; the maintainer makes that call.

Do not run automatic merge during foundation. One designated integrator handles rebase/conflict resolution after each accepted PR. Merge queue is deferred until enough concurrent PRs justify it.

## Handoffs

Report changed files, exact executed commands/results, what could not be tested, blockers and next action. Label PRs by executing agent once labels exist; after enough merged PRs compare accepted work, reruns and integration effort, not produced line count.
