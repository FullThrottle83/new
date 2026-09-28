# Task scopes

Each task's base-branch file `tasks/<issue-number>.scope` is a line-oriented allowlist. The PR body must contain exactly one `Closes #N`, `Fixes #N` or `Resolves #N` reference.

Allowed forms: an exact repository-relative path, or a directory prefix ending in `/**`. No other glob syntax, traversal or absolute paths. Blank lines and `#` comments are ignored. A rename needs BOTH paths to match. The issue must still be OPEN according to the GitHub API. A closed issue cannot lend its old scope to a new PR; reopening requires maintainer review of the scope. Open state alone does not establish that the PR is legitimately assigned to the issue, so verify the issue-to-PR relationship during review. Deletion/rename of existing test files requires an exact old-path rule, not merely tests/**. Changes to task scopes or the guard itself need their own maintainer-approved governance task and are never self-authorizing.

This controls changed files only, not semantic correctness or parallel ownership. A change in allowed path still requires tests and review.
