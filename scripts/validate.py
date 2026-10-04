#!/usr/bin/env python3
"""Validate this repository's packaging, not the quality of model answers."""

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    raise SystemExit("Install the development dependencies from requirements-dev.txt.")

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ["Lite", "Medium", "Pro", "Max", "Ultra", "Extreme", "67"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def profile_rows(document):
    # The first level table holds numeric allocations. Later tables describe roles.
    rows = {}
    for line in document.splitlines():
        cells = [cell.strip().strip("*") for cell in line.strip().strip("|").split("|")]
        if cells[0] in LEVELS and all(value.isdigit() for value in cells[1:]) and len(cells) > 1:
            require(cells[0] not in rows, f"Duplicate level {cells[0]}")
            rows[cells[0]] = [int(value) for value in cells[1:]]
    return rows


def validate():
    text = read("skills/overkill/SKILL.md")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    require(match is not None, "SKILL.md needs YAML frontmatter and a Markdown body")
    metadata = yaml.safe_load(match.group(1))
    require(isinstance(metadata, dict), "Frontmatter must be a mapping")
    require(metadata.get("name") == "overkill", 'Skill name must be the string "overkill"')
    description = metadata.get("description")
    require(isinstance(description, str) and 0 < len(description) <= 1024,
            "Description must be a nonempty string of at most 1024 characters")
    require(metadata.get("license") == "MIT", "Expected MIT license declaration")
    details = metadata.get("metadata")
    require(isinstance(details, dict) and isinstance(details.get("version"), str),
            "Metadata needs a string version")
    require(re.fullmatch(r"\d+\.\d+\.\d+", details["version"]), "Use a semantic version")
    require(match.group(2).strip(), "Skill body is empty")

    agent_metadata = yaml.safe_load(read("skills/overkill/agents/openai.yaml"))
    require(isinstance(agent_metadata, dict), "Codex UI metadata must be a mapping")
    ui = agent_metadata.get("interface")
    require(isinstance(ui, dict), "Codex UI interface must be a mapping")
    for key in ["display_name", "short_description", "default_prompt"]:
        require(isinstance(ui.get(key), str) and ui[key].strip(), f"Invalid UI field {key}")
    require(25 <= len(ui["short_description"]) <= 64, "UI description needs 25 to 64 characters")
    require("$overkill" in ui["default_prompt"], "UI prompt must invoke $overkill")

    license_text = read("LICENSE")
    require(license_text == read("skills/overkill/LICENSE"), "Installed skill must preserve full license")
    require("Copyright (c) 2026 Jake Schincariol" in license_text, "Missing upstream attribution")

    profiles = profile_rows(read("skills/overkill/references/effort-levels.md"))
    summary = profile_rows(read("README.md"))
    require(list(profiles) == LEVELS and list(summary) == LEVELS, "Seven effort levels must be in order")
    previous = 0
    for level, counts in profiles.items():
        require(len(counts) == 5 and all(value >= 0 for value in counts), f"Invalid allocation for {level}")
        require(sum(counts[:3]) == counts[3], f"Worker total is wrong for {level}")
        require(counts[3] > previous, "Worker allocations must increase by level")
        require(summary[level] == counts[:4], f"README disagrees with profile {level}")
        previous = counts[3]

    cases = json.loads(read("evals/cases.json"))
    rubric = json.loads(read("evals/rubric.json"))
    require(isinstance(cases, list) and cases, "Evaluation cases must be a nonempty array")
    ids = []
    for case in cases:
        require(isinstance(case, dict), "Each evaluation case must be an object")
        require(all(isinstance(case.get(key), str) and case[key].strip()
                    for key in ["id", "prompt", "tools"]), "Cases need id, prompt and tools")
        ids.append(case["id"])
    require(len(ids) == len(set(ids)), "Duplicate evaluation case IDs")
    require(isinstance(rubric, dict) and set(ids) == set(rubric), "Cases and rubric IDs differ")
    require(all(isinstance(items, list) and items and all(isinstance(s, str) and s.strip() for s in items)
                for items in rubric.values()), "Rubrics need nonempty observable conditions")

    # BaseLoader avoids YAML 1.1 interpreting the GitHub Actions key 'on' as True.
    workflow = yaml.load(read(".github/workflows/validate.yml"), Loader=yaml.BaseLoader)
    require(set(workflow["on"]) == {"push", "pull_request", "workflow_dispatch"}, "Unexpected CI triggers")
    require(workflow.get("permissions") == {"contents": "read"}, "CI should need read-only access")

    markdown = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in {".git", ".venv", "__pycache__"} for part in relative.parts):
            continue
        require(not path.is_symlink(), f"Package contains symlink {relative}")
        if path.is_file() and path.suffix == ".md":
            markdown.append(path)
    for path in markdown:
        # Repository docs use inline links. Check local file targets, not remote sites or anchors.
        for target in re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            require(destination.is_relative_to(ROOT), f"Link escapes repo in {path.relative_to(ROOT)}")
            require(destination.exists(), f"Broken local link in {path.relative_to(ROOT)} to {target}")

    print(f"PASS package metadata, seven profiles, {len(cases)} evaluation cases and {len(markdown)} Markdown files")
    print("Structural validation only. Model behavior, remote links and live client discovery are not tested.")


if __name__ == "__main__":
    try:
        validate()
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        sys.exit(1)
