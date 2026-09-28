# Repository controls (maintainer action)

Governance files alone do not protect main. The GitHub connector used for bootstrap cannot write repository rulesets or branch protection, so configure these in GitHub settings.

1. Configure a main-branch ruleset requiring PRs; block force pushes and deletion.
2. Require the relevant CI checks: Scope guard / scope and Quality / quality. Confirm exact names in Actions after first runs. Verify both checks actually gate the PR head; scope uses pull_request_target and should be tested with a harmless PR before treating it as enforcement.
3. Do not enable automerge. CODEOWNERS routes review but the solo maintainer cannot approve their own PR; use a deliberate manual merge decision rather than an impossible approval requirement.
4. Minimize bypass allowances. Keep Actions permissions read-only unless a future scoped issue requires more.
5. Governance changes need separate review. Scope guard runs base-branch code through pull_request_target and never checks out or executes PR files. Quality runs PR code with read-only permissions and no repository secrets.
6. Do not configure Cloudflare deployment or production credentials in M0. Add deployment only after explicit approval.
7. If merge queue is later enabled, required application checks must run on merge_group (the quality workflow already declares it).

Path scope does not guarantee semantic correctness, non-overlapping ownership or legitimacy of an issue. If the trusted scope check cannot be required for this repository, do not describe the policy as enforced until another reliable gate is configured.
