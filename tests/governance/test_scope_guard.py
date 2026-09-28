"""Regression tests for trusted base-branch scope guard (stdlib only)."""
import importlib.util
import pathlib
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "scope_guard.py"
SPEC = importlib.util.spec_from_file_location("scope_guard", SCRIPT)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


class ScopeGuardTests(unittest.TestCase):
    def test_issue_reference(self):
        self.assertEqual(guard.issue_from_body("Verified.\nCloses #12\n"), 12)
        for text in ("", "Related to #1", "Closes #1\nFixes #2", "Closes #1\nCloses #1"):
            with self.subTest(text=text):
                with self.assertRaises(guard.ScopeError):
                    guard.issue_from_body(text)

    def test_exact_and_subtree(self):
        rules = guard.parse_scope("# comment\nsrc/**\npackage.json\n\n")
        self.assertTrue(guard.is_allowed("src/main.ts", rules))
        self.assertTrue(guard.is_allowed("src/deep/game.ts", rules))
        self.assertTrue(guard.is_allowed("package.json", rules))
        self.assertFalse(guard.is_allowed("src-other/main.ts", rules))
        self.assertFalse(guard.is_allowed("package-lock.json", rules))
        self.assertFalse(guard.is_allowed("src", rules))

    def test_malformed_and_empty_fail_closed(self):
        for value in ("", "# only comment", "../src/**", "/src/**", "src/*",
                      "src/**/game.ts", "src//game.ts", r"src\game.ts",
                      "src/[abc]", "src/./game.ts", "src/**\nsrc/**"):
            with self.subTest(value=value):
                with self.assertRaises(guard.ScopeError):
                    guard.parse_scope(value)

    def test_rename_checks_both_paths(self):
        paths = guard.changed_paths(b"R100\0src/old.ts\0other/new.ts\0")
        self.assertEqual(paths, ["src/old.ts", "other/new.ts"])
        self.assertEqual(guard.evaluate(paths, ["src/**"]), ["other/new.ts"])

    def test_deletion_addition_and_modification(self):
        paths = guard.changed_paths(b"D\0src/old.ts\0A\0src/new.ts\0M\0AGENTS.md\0")
        self.assertEqual(guard.evaluate(paths, ["src/**"]), ["AGENTS.md"])

    def test_missing_rename_target_fails(self):
        with self.assertRaises(guard.ScopeError):
            guard.changed_paths(b"R100\0src/old.ts\0")

    def test_guard_and_scope_files_are_not_self_authorizing(self):
        self.assertEqual(
            guard.evaluate(["scripts/scope_guard.py", "tasks/1.scope"],
                           ["src/**", "package.json"]),
            ["scripts/scope_guard.py", "tasks/1.scope"],
        )


    def test_issue_metadata_must_be_open_and_match(self):
        guard.validate_issue_payload(1, {"number": 1, "state": "open"})
        for payload in (
            {"number": 1, "state": "closed"},
            {"number": 2, "state": "open"},
            {"number": 1, "state": "open", "pull_request": {}},
            {"number": 1},
            None,
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(guard.ScopeError):
                    guard.validate_issue_payload(1, payload)

    def test_issue_api_errors_fail_closed(self):
        with self.assertRaises(guard.ScopeError):
            guard.require_open_issue(1, "bad repository", "https://api.github.com", "token")
        with self.assertRaises(guard.ScopeError):
            guard.require_open_issue(1, "owner/repo", "http://api.github.com", "token")
        with mock.patch.object(guard.urllib.request, "urlopen",
                               side_effect=guard.urllib.error.URLError("offline")):
            with self.assertRaises(guard.ScopeError):
                guard.require_open_issue(1, "owner/repo", "https://api.github.com", "token")

    def test_removing_tests_needs_exact_scope_not_subtree(self):
        diff = b"D\0tests/game/swing.test.ts\0R100\0tests/game/old.test.ts\0tests/game/new.test.ts\0"
        self.assertEqual(
            guard.unauthorized_test_removals(diff, ["tests/game/**"]),
            ["tests/game/old.test.ts", "tests/game/swing.test.ts"],
        )
        self.assertEqual(
            guard.unauthorized_test_removals(
                diff, ["tests/game/**", "tests/game/old.test.ts", "tests/game/swing.test.ts"]
            ), [],
        )

if __name__ == "__main__":
    unittest.main()
