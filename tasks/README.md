# Task scopes

Each task's base-branch file `tasks/<issue-number>.scope` is a line-oriented allowlist. The PR body must contain exactly one `Closes #N`, `Fixes #N` or `Resolves #N` reference.

Allowed forms: an exact repository-relative path, or a directory prefix ending in `/**`. No other glob syntax, traversal or absolute paths. Blank lines and `#` comments are ignored. A rename needs BOTH paths to match. Changes to task scopes or the guard itself need their own maintainer-approved governance task and are never self-authorizing.

This controls changed files only, not semantic correctness or parallel ownership. A change in allowed path still requires tests and review.
