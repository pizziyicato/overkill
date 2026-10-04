#!/usr/bin/env python3
"""Install the portable skill into local Claude Code and/or Codex directories."""

import argparse
import hashlib
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

SOURCE = Path(__file__).resolve().parents[1] / "skills" / "overkill"
DEFAULT_NAME = "overkill"


def skill_name(value):
    """Accept a single Agent Skills directory name, never a path."""
    if not 1 <= len(value) <= 64 or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value) is None:
        raise ValueError("Skill name must be 1-64 lowercase letters, digits or hyphens, "
                         "without leading, trailing or consecutive hyphens")
    return value


def alias_metadata(source, name):
    """Rewrite only supported metadata fields in the installed copy.

    This is deliberately not a YAML parser. Aliasing requires the package's
    simple name scalar and single-line quoted Codex prompt; unfamiliar forms
    fail before any destination changes instead of producing a partial alias.
    """
    if name == DEFAULT_NAME:
        return {}
    skill = (source / "SKILL.md").read_bytes()
    frontmatter = re.match(rb"\A---\r?\n(?P<body>.*?)\r?\n---(?:\r?\n|\Z)", skill, re.DOTALL)
    if frontmatter is None:
        raise ValueError("Cannot alias SKILL.md: expected YAML frontmatter")
    body = frontmatter.group("body")
    # Accept exactly the shipped top-level name form, with optional quoting.
    names = list(re.finditer(rb"(?m)^name:[ \t]*(?:overkill|\"overkill\"|'overkill')[ \t]*\r?$", body))
    name_keys = re.findall(rb"(?m)^[ \t]*(?:name|'name'|\"name\")[ \t]*:", body)
    if len(names) != 1 or len(name_keys) != 1:
        raise ValueError("Cannot alias SKILL.md: expected one simple top-level name: overkill field")
    field = names[0]
    start = frontmatter.start("body") + field.start()
    end = frontmatter.start("body") + field.end()
    newline = b"\r" if field.group().endswith(b"\r") else b""
    overrides = {"SKILL.md": skill[:start] + b'name: "' + name.encode("ascii") + b'"' + newline + skill[end:]}

    agent_file = source / "agents" / "openai.yaml"
    if agent_file.exists():
        metadata = agent_file.read_bytes()
        # Restrict edits to a direct child of the unquoted interface mapping.
        interfaces = list(re.finditer(rb"(?m)^interface:[ \t]*\r?$", metadata))
        interface_keys = re.findall(rb"(?m)^(?:interface|'interface'|\"interface\")[ \t]*:", metadata)
        if len(interfaces) != 1 or len(interface_keys) != 1:
            raise ValueError("Cannot alias agents/openai.yaml: expected one simple interface mapping")
        interface = interfaces[0]
        following = metadata[interface.end():]
        next_mapping = re.search(rb"(?m)^[^ \t\r\n#]", following)
        interface_end = interface.end() + next_mapping.start() if next_mapping else len(metadata)
        section = metadata[interface.end():interface_end]
        prompts = list(re.finditer(rb'''(?m)^  default_prompt:[ \t]*(?P<quote>["'])(?P<value>[^\r\n]*)(?P=quote)[ \t]*\r?$''', section))
        prompt_keys = re.findall(rb"(?m)^[ \t]*(?:default_prompt|'default_prompt'|\"default_prompt\")[ \t]*:", metadata)
        if len(prompts) != 1 or len(prompt_keys) != 1:
            raise ValueError("Cannot alias agents/openai.yaml: expected one single-line quoted interface.default_prompt")
        prompt = prompts[0]
        value = prompt.group("value")
        quote = prompt.group("quote")
        # Escapes and embedded quotes need a YAML parser; refuse them explicitly.
        if b"\\" in value or quote in value:
            raise ValueError("Cannot alias agents/openai.yaml: escaped or embedded quotes are unsupported")
        rewritten, count = re.subn(rb"\$overkill(?![a-zA-Z0-9_-])", b"$" + name.encode("ascii"), value)
        if count == 0:
            raise ValueError("Cannot alias agents/openai.yaml: default_prompt does not invoke $overkill")
        start = interface.end() + prompt.start("value")
        end = interface.end() + prompt.end("value")
        overrides["agents/openai.yaml"] = metadata[:start] + rewritten + metadata[end:]
    return overrides


def snapshot(folder):
    """Compare regular files without following symlinks."""
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError(f"Expected a regular directory at {folder}")
    result = {}
    for path in folder.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Refusing a symlink at {path}")
        if path.is_file():
            result[path.relative_to(folder).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise ValueError(f"Unsupported file type at {path}")
    return result


def destinations(target, project=None, home=None, name=DEFAULT_NAME):
    skill_name(name)
    base = Path(project).absolute() if project is not None else (home or Path.home())
    names = ["claude", "codex"] if target == "both" else [target]
    return [base / (".claude" if host == "claude" else ".agents") / "skills" / name
            for host in names]


def backup_directory(target):
    """Keep replacements outside skill discovery and refuse linked backups."""
    folder = target.parent.parent / "skill-backups"
    if folder.is_symlink():
        raise ValueError(f"Refusing linked backup directory {folder}")
    if folder.exists() and not folder.is_dir():
        raise ValueError(f"Expected a backup directory at {folder}")
    return folder


def preflight(source, targets, replace, expected=None):
    expected = snapshot(source) if expected is None else expected
    if "SKILL.md" not in expected or "LICENSE" not in expected:
        raise ValueError("Source package is missing SKILL.md or LICENSE")
    plans = []
    for target in targets:
        # Avoid modifying the source or following linked destination directories.
        if target.resolve().is_relative_to(source.resolve()) or source.resolve().is_relative_to(target.resolve()):
            raise ValueError(f"Source and destination overlap at {target}")
        for part in [target, *target.parents]:
            if part.is_symlink():
                raise ValueError(f"Refusing a symlink in the destination path at {part}")
            if part.exists() and not part.is_dir():
                raise ValueError(f"Destination path is not a directory at {part}")
        exists = target.exists()
        identical = exists and snapshot(target) == expected
        if exists and not identical and not replace:
            raise ValueError(f"Different installation exists at {target}. Review it, then use --replace to back it up and replace it.")
        if exists and not identical:
            backup_directory(target)
        plans.append((target, "unchanged" if identical else "replace" if exists else "install"))
    return plans


def install(source, targets, replace=False, dry_run=False, name=DEFAULT_NAME):
    skill_name(name)
    if any(target.name != name for target in targets):
        raise ValueError("Destination directory must match the requested skill name")
    expected = snapshot(source)
    if "SKILL.md" not in expected or "LICENSE" not in expected:
        raise ValueError("Source package is missing SKILL.md or LICENSE")
    overrides = alias_metadata(source, name)
    expected.update({path: hashlib.sha256(data).hexdigest() for path, data in overrides.items()})
    # Check all targets before changing any of them.
    plans = preflight(source, targets, replace, expected)
    completed = []
    try:
        for target, action in plans:
            if dry_run or action == "unchanged":
                print(f"{'Would ' if dry_run else ''}{action} {target}")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Stage on the same filesystem, then rename the complete directory.
            with tempfile.TemporaryDirectory(prefix=f".{name}-install-", dir=target.parent) as stage:
                prepared = Path(stage) / name
                shutil.copytree(source, prepared)
                for path, data in overrides.items():
                    (prepared / path).write_bytes(data)
                backup = None
                if target.exists():
                    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                    backup = backup_directory(target) / f"{name}-{stamp}-{uuid4().hex[:8]}"
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    target.rename(backup)
                try:
                    prepared.rename(target)
                except OSError:
                    if backup is not None:
                        backup.rename(target)
                    raise
            completed.append(target)
            print(f"Installed {target}")
            if backup is not None:
                print(f"Previous version saved at {backup}")
    except (OSError, ValueError) as error:
        if completed:
            print("Completed before the error: " + ", ".join(map(str, completed)), file=sys.stderr)
        raise error
    return plans


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=["claude", "codex", "both"])
    parser.add_argument("--project", type=Path, help="Install for this existing project instead of your user account")
    parser.add_argument("--name", type=skill_name, default=DEFAULT_NAME,
                        help="Local skill name, e.g. my-overkill, to coexist with another installation (default: overkill)")
    parser.add_argument("--dry-run", action="store_true", help="Show the plan without writing files")
    parser.add_argument("--replace", action="store_true", help="Back up a different existing version before replacing it")
    args = parser.parse_args()
    if args.project is not None and not args.project.is_dir():
        parser.error("--project must name an existing directory")
    try:
        install(SOURCE, destinations(args.target, args.project, name=args.name), args.replace, args.dry_run, args.name)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Installation stopped: {error}\n")


if __name__ == "__main__":
    main()
