"""Regression tests for trusted base-branch scope guard (stdlib only)."""
import importlib.util
import pathlib
import unittest

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


if __name__ == "__main__":
    unittest.main()
