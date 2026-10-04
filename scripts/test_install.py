#!/usr/bin/env python3
"""Exercise installation in temporary folders, never the user's skill locations."""

import argparse
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import install

TEMP_ROOT = None


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=TEMP_ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text(
            '---\nname: "overkill"\ndescription: Compare approaches with Overkill\n---\n'
            '# Overkill\nKeep the prose $overkill and https://example.com/overkill intact.\n')
        (self.source / "LICENSE").write_text("license")
        (self.source / "agents").mkdir()
        (self.source / "agents" / "openai.yaml").write_text(
            'interface:\n  display_name: "overkill"\n'
            '  default_prompt: "Use $overkill Pro. Keep $overkill-tools separate."\n')
        (self.source / "references").mkdir()
        (self.source / "references" / "effort.md").write_text("effort profiles")
        self.targets = install.destinations("both", project=self.root / "project")

    def run_install(self, targets=None, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return install.install(self.source, self.targets if targets is None else targets, **kwargs)

    def run_alias(self, **kwargs):
        targets = install.destinations("both", project=self.root / "project", name="my-overkill")
        return self.run_install(targets=targets, name="my-overkill", **kwargs)

    def test_both_hosts_receive_complete_package(self):
        self.run_install()
        for target in self.targets:
            self.assertEqual(install.snapshot(target), install.snapshot(self.source))

    def test_dry_run_has_no_filesystem_effect(self):
        self.run_install(dry_run=True)
        self.assertFalse((self.root / "project").exists())

    def test_same_install_is_unchanged(self):
        self.run_install()
        self.assertEqual([action for _, action in self.run_install()], ["unchanged", "unchanged"])
        self.assertFalse(list(self.root.rglob("skill-backups")))

    def test_conflict_preflight_prevents_partial_install(self):
        conflicting = self.targets[1]
        conflicting.mkdir(parents=True)
        (conflicting / "SKILL.md").write_text("local edits")
        with self.assertRaises(ValueError):
            self.run_install()
        self.assertFalse(self.targets[0].exists())
        self.assertEqual((conflicting / "SKILL.md").read_text(), "local edits")

    def test_replace_preserves_previous_version_outside_discovery(self):
        self.run_install()
        (self.targets[0] / "SKILL.md").write_text("local edits")
        self.run_install(replace=True)
        backups = list((self.targets[0].parent.parent / "skill-backups").glob("overkill-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "SKILL.md").read_text(), "local edits")
        self.assertEqual(install.snapshot(self.targets[0]), install.snapshot(self.source))
        self.assertFalse(backups[0].is_relative_to(self.targets[0].parent))

    def test_backup_file_conflict_prevents_either_host_from_changing(self):
        self.run_install()
        for target in self.targets:
            (target / "SKILL.md").write_text("local edits")
        before = [install.snapshot(target) for target in self.targets]
        backup_dir = self.targets[1].parent.parent / "skill-backups"
        backup_dir.write_text("unrelated file")
        with self.assertRaisesRegex(ValueError, "backup directory"):
            self.run_install(replace=True)
        self.assertEqual([install.snapshot(target) for target in self.targets], before)
        self.assertFalse((self.targets[0].parent.parent / "skill-backups").exists())
        self.assertEqual(backup_dir.read_text(), "unrelated file")

    def test_linked_backup_directory_prevents_either_host_from_changing(self):
        self.run_install()
        for target in self.targets:
            (target / "SKILL.md").write_text("local edits")
        before = [install.snapshot(target) for target in self.targets]
        outside = self.root / "outside"
        outside.mkdir()
        backup_dir = self.targets[1].parent.parent / "skill-backups"
        backup_dir.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "backup directory"):
            self.run_install(replace=True)
        self.assertEqual([install.snapshot(target) for target in self.targets], before)
        self.assertFalse((self.targets[0].parent.parent / "skill-backups").exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlink_destination_is_refused(self):
        self.targets[0].parent.mkdir(parents=True)
        self.targets[0].symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.run_install(replace=True)

    def test_symlink_source_is_refused(self):
        (self.source / "linked").symlink_to(self.source / "SKILL.md")
        with self.assertRaises(ValueError):
            self.run_install()

    def test_failed_swap_restores_previous_version(self):
        self.run_install()
        (self.targets[0] / "SKILL.md").write_text("local edits")
        actual_rename = Path.rename

        def fail_prepared(path, target):
            if path.parent.name.startswith(".overkill-install-"):
                raise OSError("simulated filesystem failure")
            return actual_rename(path, target)

        with patch.object(Path, "rename", fail_prepared):
            with self.assertRaises(OSError):
                self.run_install(replace=True)
        self.assertEqual((self.targets[0] / "SKILL.md").read_text(), "local edits")

    def test_personal_paths_without_touching_home(self):
        home = self.root / "pretend-home"
        self.assertEqual(install.destinations("codex", home=home), [home / ".agents/skills/overkill"])
        self.assertEqual(install.destinations("claude", home=home), [home / ".claude/skills/overkill"])

    def test_alias_coexists_with_a_different_overkill(self):
        for target in self.targets:
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("Someone else's Overkill")
        before = [install.snapshot(target) for target in self.targets]
        plans = self.run_alias()
        self.assertEqual([action for _, action in plans], ["install", "install"])
        self.assertEqual([install.snapshot(target) for target in self.targets], before)
        self.assertTrue(all(target.name == "my-overkill" for target, _ in plans))
        self.assertFalse(list(self.root.rglob("skill-backups")))

    def test_alias_changes_only_internal_name_and_exact_prompt_invocation(self):
        before = install.snapshot(self.source)
        for target, _ in self.run_alias():
            skill = (target / "SKILL.md").read_bytes()
            self.assertEqual(skill, (self.source / "SKILL.md").read_bytes().replace(
                b'name: "overkill"', b'name: "my-overkill"', 1))
            metadata = (target / "agents" / "openai.yaml").read_bytes()
            self.assertEqual(metadata, (self.source / "agents" / "openai.yaml").read_bytes().replace(
                b'Use $overkill Pro', b'Use $my-overkill Pro', 1))
            self.assertEqual((target / "LICENSE").read_bytes(), (self.source / "LICENSE").read_bytes())
            self.assertEqual((target / "references" / "effort.md").read_bytes(),
                             (self.source / "references" / "effort.md").read_bytes())
        self.assertEqual(install.snapshot(self.source), before)

    def test_repeated_alias_is_unchanged(self):
        self.run_alias()
        plans = self.run_alias()
        self.assertEqual([action for _, action in plans], ["unchanged", "unchanged"])
        self.assertFalse(list(self.root.rglob("skill-backups")))

    def test_alias_dry_run_has_no_filesystem_effect(self):
        before = install.snapshot(self.source)
        plans = self.run_alias(dry_run=True)
        self.assertEqual([action for _, action in plans], ["install", "install"])
        self.assertFalse((self.root / "project").exists())
        self.assertEqual(install.snapshot(self.source), before)

    def test_alias_conflict_is_checked_before_either_host_changes(self):
        targets = install.destinations("both", project=self.root / "project", name="my-overkill")
        targets[1].mkdir(parents=True)
        (targets[1] / "SKILL.md").write_text("Local alias edits")
        with self.assertRaises(ValueError):
            self.run_alias()
        self.assertFalse(targets[0].exists())
        self.assertEqual((targets[1] / "SKILL.md").read_text(), "Local alias edits")

    def test_alias_replacement_uses_alias_backup_outside_discovery(self):
        targets = [target for target, _ in self.run_alias()]
        (targets[0] / "SKILL.md").write_text("Local alias edits")
        self.run_alias(replace=True)
        backups = list((targets[0].parent.parent / "skill-backups").glob("my-overkill-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "SKILL.md").read_text(), "Local alias edits")
        self.assertFalse(backups[0].is_relative_to(targets[0].parent))
        self.assertEqual(install.snapshot(targets[0]), install.snapshot(targets[1]))
        self.assertEqual([action for _, action in self.run_alias()], ["unchanged", "unchanged"])

    def test_invalid_and_traversal_names_are_rejected_before_writing(self):
        invalid = ["", ".", "..", "../overkill", "my/overkill", "my\\overkill", "/overkill",
                   "-overkill", "overkill-", "my--overkill", "Overkill", "my_overkill",
                   "my overkill", "overkill\n", "a" * 65, "überkill"]
        for name in invalid:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    install.destinations("both", project=self.root / "project", name=name)
                with self.assertRaises(ValueError):
                    self.run_install(name=name)
        self.assertFalse((self.root / "project").exists())

    def test_valid_names_include_single_character_and_maximum_length(self):
        for name in ["a", "1", "a-1", "a" * 64]:
            with self.subTest(name=name):
                targets = install.destinations("both", project=self.root / "project", name=name)
                plans = self.run_install(targets=targets, name=name)
                self.assertTrue(all(target.name == name for target, _ in plans))
                self.assertIn(f'name: "{name}"', (targets[0] / "SKILL.md").read_text())

    def test_mismatched_destination_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must match"):
            self.run_install(name="my-overkill")
        self.assertFalse((self.root / "project").exists())

    def test_unsupported_skill_metadata_is_rejected_before_writing(self):
        fixtures = ["No frontmatter", "---\nname: other\n---\n",
                    "---\nname: overkill\nname: overkill\n---\n",
                    '---\nname: overkill\n"name": other\n---\n',
                    "---\nname: >-\n  overkill\n---\n"]
        for metadata in fixtures:
            with self.subTest(metadata=metadata):
                (self.source / "SKILL.md").write_text(metadata)
                with self.assertRaisesRegex(ValueError, "Cannot alias SKILL.md"):
                    self.run_alias()
                self.assertFalse((self.root / "project").exists())

    def test_unsupported_codex_metadata_is_rejected_before_writing(self):
        fixtures = ['interface:\n  default_prompt: >-\n    Use $overkill Pro.\n',
                    'interface:\n  default_prompt: "No skill invocation"\n',
                    'interface:\n  default_prompt: "Use $overkill-tools only"\n',
                    'interface:\n  display_name: "overkill"\n',
                    'interface:\n  default_prompt: "Use $overkill"\n  default_prompt: "Use $other"\n',
                    'interface:\n  default_prompt: "Use $overkill"\ninterface: {}\n',
                    'interface:\n  default_prompt: "Use $overkill \\"Pro\\""\n']
        for metadata in fixtures:
            with self.subTest(metadata=metadata):
                (self.source / "agents" / "openai.yaml").write_text(metadata)
                with self.assertRaisesRegex(ValueError, "Cannot alias agents/openai.yaml"):
                    self.run_alias()
                self.assertFalse((self.root / "project").exists())

    def test_alias_without_optional_codex_metadata(self):
        (self.source / "agents" / "openai.yaml").unlink()
        for target, _ in self.run_alias():
            self.assertIn('name: "my-overkill"', (target / "SKILL.md").read_text())
            self.assertFalse((target / "agents" / "openai.yaml").exists())

    def test_alias_preserves_crlf_and_supports_simple_name_quotes(self):
        for original_name in [b"overkill", b"'overkill'", b'"overkill"']:
            with self.subTest(original_name=original_name):
                (self.source / "SKILL.md").write_bytes(b"---\r\nname: " + original_name + b"\r\n---\r\n# Overkill\r\n")
                (self.source / "agents" / "openai.yaml").write_bytes(
                    b"interface:\r\n  display_name: 'overkill'\r\n  default_prompt: 'Use $overkill Pro'\r\n")
                for target, _ in self.run_alias(replace=True):
                    self.assertEqual((target / "SKILL.md").read_bytes(),
                                     b'---\r\nname: "my-overkill"\r\n---\r\n# Overkill\r\n')
                    self.assertIn(b"'Use $my-overkill Pro'\r\n", (target / "agents" / "openai.yaml").read_bytes())

    def test_cli_name_installs_shipped_package_with_consistent_metadata(self):
        project = self.root / "cli-project"
        project.mkdir()
        source_before = install.snapshot(install.SOURCE)
        argv = ["install.py", "--target", "both", "--project", str(project), "--name", "my-overkill"]
        with patch("sys.argv", argv), contextlib.redirect_stdout(io.StringIO()):
            install.main()
        for target in install.destinations("both", project=project, name="my-overkill"):
            self.assertIn('name: "my-overkill"', (target / "SKILL.md").read_text())
            self.assertIn("Use $my-overkill Pro", (target / "agents" / "openai.yaml").read_text())
        self.assertEqual(install.snapshot(install.SOURCE), source_before)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--temp-root", type=Path)
    args, remaining = parser.parse_known_args()
    if args.temp_root is not None:
        args.temp_root.mkdir(parents=True, exist_ok=True)
        TEMP_ROOT = str(args.temp_root.resolve())
    unittest.main(argv=[__file__, *remaining])
