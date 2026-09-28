# Quality gates

A feature is done only when its relevant user action produces a verified state transition and can survive death/restart where applicable.

## Policy gate

The PR body contains exactly one closing reference such as `Closes #1`. The base branch contains `tasks/1.scope`. Every added, modified, deleted and renamed path must be allowed; for renames, both old and new paths are checked. Missing or malformed scope fails closed. Protected policy is evaluated from the base branch, not from the PR. Configure the scope check as required after bootstrap; a workflow file alone cannot enforce branch protection.

## Executable gate

Run available narrow tests, typecheck and build. M0 establishes the scripts; workflow starts running them once package.json exists. No skipping or weakening checks to get green. Gameplay tests must control simulation ticks and validate state, rather than depend on real-time keypress duration.

## Gameplay gate

No decorative substitutes for required mechanics. Check input -> state -> physics -> collision -> feedback -> progression; camera and audio do not conceal gameplay errors. Test fast collisions, moving anchors, restarts, no-softlock puzzle states and missing assets. Record limitations honestly.

## Browser and accessibility gate

Check actual Chrome gameplay for changes touching visuals or input. UI/menus must be keyboard-operable with visible focus. Respect reduced-motion and reduced-intensity audio preferences where relevant; do not promise a universal ADHD experience. Visual comparisons require stable capture settings and tolerance.

## Release gate

There is no automatic deployment. Publish only after explicit maintainer approval, licensing/provenance checks, playable progression evidence and production-build review.
