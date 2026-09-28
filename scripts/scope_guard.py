#!/usr/bin/env python3
"""Validate PR paths against an issue scope stored on the trusted base branch.

Run this script from a base-branch checkout. It reads Git objects and event JSON;
it never checks out or executes PR-supplied code.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
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


def changed_paths(name_status: bytes) -> list[str]:
    """Parse git diff --name-status -z; check BOTH old and new rename/copy paths."""
    chunks = name_status.decode("utf-8", errors="strict").split("\0")
    if chunks and chunks[-1] == "":
        chunks.pop()
    paths: list[str] = []
    cursor = 0
    while cursor < len(chunks):
        status = chunks[cursor]
        cursor += 1
        count = 2 if status.startswith(("R", "C")) else 1
        if not status or status[0] not in "ACDMRTUXB" or cursor + count > len(chunks):
            raise ScopeError(f"Malformed git diff status: {status!r}")
        paths.extend(chunks[cursor:cursor + count])
        cursor += count
    return paths


def evaluate(paths: list[str], rules: list[str]) -> list[str]:
    return sorted(set(path for path in paths if not is_allowed(path, rules)))


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
