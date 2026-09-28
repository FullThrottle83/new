#!/usr/bin/env python3
"""Validate PR paths against an issue scope stored on the trusted base branch.

Run this script from a base-branch checkout. It reads Git objects and event JSON;
it never checks out or executes PR-supplied code.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import PurePosixPath

CLOSING_REF = re.compile(r"\b(?:closes|fixes|resolves)\s+#([1-9]\d*)\b", re.IGNORECASE)


class ScopeError(ValueError):
    pass


def issue_from_body(body: str) -> int:
    matches = CLOSING_REF.findall(body or "")
    if len(matches) != 1:
        raise ScopeError("PR body must contain exactly one closing reference, e.g. Closes #1")
    return int(matches[0])


def parse_scope(source: str) -> list[str]:
    rules: list[str] = []
    for number, raw in enumerate(source.splitlines(), 1):
        rule = raw.strip()
        if not rule or rule.startswith("#"):
            continue
        is_subtree = rule.endswith("/**")
        stem = rule[:-3] if is_subtree else rule
        parts = stem.split("/")
        if (
            not stem
            or stem.startswith("/")
            or "\\" in stem
            or "*" in stem
            or "?" in stem
            or "[" in stem
            or "]" in stem
            or any(p in ("", ".", "..") for p in parts)
            or not all(re.fullmatch(r"[A-Za-z0-9._@+ -]+", p) for p in parts)
        ):
            raise ScopeError(f"Malformed scope rule on line {number}: {rule!r}")
        if rule in rules:
            raise ScopeError(f"Duplicate scope rule on line {number}: {rule!r}")
        rules.append(rule)
    if not rules:
        raise ScopeError("Empty scope is not allowed")
    return rules


def is_allowed(path: str, rules: list[str]) -> bool:
    if not path or path.startswith("/") or "\\" in path or ".." in PurePosixPath(path).parts:
        return False
    return any(
        path.startswith(rule[:-3] + "/") if rule.endswith("/**") else path == rule
        for rule in rules
    )


def changed_entries(name_status: bytes) -> list[tuple[str, list[str]]]:
    """Parse git diff --name-status -z without losing rename source paths."""
    chunks = name_status.decode("utf-8", errors="strict").split("\0")
    if chunks and chunks[-1] == "":
        chunks.pop()
    entries: list[tuple[str, list[str]]] = []
    cursor = 0
    while cursor < len(chunks):
        status = chunks[cursor]
        cursor += 1
        count = 2 if status.startswith(("R", "C")) else 1
        if not status or status[0] not in "ACDMRTUXB" or cursor + count > len(chunks):
            raise ScopeError(f"Malformed git diff status: {status!r}")
        entries.append((status, chunks[cursor:cursor + count]))
        cursor += count
    return entries


def changed_paths(name_status: bytes) -> list[str]:
    return [path for _, paths in changed_entries(name_status) for path in paths]


def unauthorized_test_removals(name_status: bytes, rules: list[str]) -> list[str]:
    """A subtree scope cannot silently retire existing tests.

    Deletions or renames of tests require an exact source-path rule on main.
    """
    removed: list[str] = []
    for status, paths in changed_entries(name_status):
        if status[0] in ("D", "R") and paths[0].startswith("tests/"):
            if paths[0] not in rules:
                removed.append(paths[0])
    return sorted(set(removed))


def evaluate(paths: list[str], rules: list[str]) -> list[str]:
    return sorted(set(path for path in paths if not is_allowed(path, rules)))


def validate_issue_payload(number: int, payload: object) -> None:
    if not isinstance(payload, dict) or payload.get("number") != number:
        raise ScopeError("Issue API returned missing or mismatched issue metadata")
    if "pull_request" in payload:
        raise ScopeError(f"#{number} is a pull request, not a task issue")
    if payload.get("state") != "open":
        raise ScopeError(f"Task issue #{number} is not open")


def require_open_issue(number: int, repository: str, api_url: str, token: str) -> None:
    """Fetch task state with a read-only token; fail closed on API errors."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ScopeError("Missing or invalid GITHUB_REPOSITORY")
    if not api_url.startswith("https://") or not token:
        raise ScopeError("Missing trusted GitHub API URL or read-only token")
    endpoint = f"{api_url.rstrip('/')}/repos/{repository}/issues/{number}"
    request = urllib.request.Request(endpoint, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except (urllib.error.URLError, ValueError, OSError) as exc:
        raise ScopeError(f"Could not verify task issue #{number} via GitHub API") from exc
    validate_issue_payload(number, payload)


def git(*args: str, text: bool = False):
    return subprocess.check_output(["git", *args], text=text, stderr=subprocess.PIPE)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, help="GITHUB_EVENT_PATH")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    args = parser.parse_args()

    try:
        with open(args.event, encoding="utf-8") as event_file:
            event = json.load(event_file)
        pr = event.get("pull_request") or {}
        issue = issue_from_body(pr.get("body") or "")
        require_open_issue(issue, os.getenv("GITHUB_REPOSITORY", ""),
                           os.getenv("GITHUB_API_URL", ""), os.getenv("GH_TOKEN", ""))
        path = f"tasks/{issue}.scope"
        try:
            source = git("show", f"{args.base_sha}:{path}", text=True)
        except subprocess.CalledProcessError as exc:
            raise ScopeError(f"Missing base-branch scope file: {path}") from exc
        rules = parse_scope(source)
        diff = git("diff", "--name-status", "-z", "--find-renames",
                   f"{args.base_sha}...{args.head_sha}")
        paths = changed_paths(diff)
        if not paths:
            raise ScopeError("PR has no changed files")
        removed_tests = unauthorized_test_removals(diff, rules)
        if removed_tests:
            raise ScopeError("Tests removed/renamed without exact base-branch scope:\n"
                             + "\n".join(f"  - {p}" for p in removed_tests))
        violations = evaluate(paths, rules)
        if violations:
            raise ScopeError("Changed paths outside base scope:\n" + "\n".join(
                f"  - {p}" for p in violations
            ))
        print(f"PASS: issue #{issue}, {len(paths)} changed path(s), {len(rules)} scope rule(s)")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError, UnicodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
