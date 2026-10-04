# Installing Overkill

The installed package is the `skills/overkill` folder. The CLI installer requires Python 3.10 or newer and uses only the standard library. Manual installation does not require Python.

Clone the repository, or download and extract its source archive.

```sh
git clone https://github.com/pizziyicato/overkill.git
cd overkill
```

Run the commands below from the repository root. On Windows, use `python` if `python3` is unavailable.

## Personal installation

```sh
python3 scripts/install.py --target both
```

Use `--target claude` or `--target codex` to install for one host.

| Host | Personal destination | Project destination | Invocation |
| --- | --- | --- | --- |
| Claude Code | `~/.claude/skills/overkill/` | `.claude/skills/overkill/` | `/overkill Pro your task` |
| Codex | `~/.agents/skills/overkill/` | `.agents/skills/overkill/` | `$overkill Pro your task` |

For the hosts' loading rules, see the [Claude Code skills documentation](https://code.claude.com/docs/en/skills) and [Codex skills documentation](https://learn.chatgpt.com/docs/build-skills). Open a fresh session and check its skill list. Installation copies files locally and does not upload the skill to a cloud account.

The [installer checks](../evals/RESULTS.md) verify local file operations. Discovery and invocation in either client have not yet been tested.

## Project installation

Name an existing project directory to install there instead of your home directory.

```sh
python3 scripts/install.py --target both --project /path/to/project
```

Project installation writes to that project's `.claude/skills/` and `.agents/skills/` folders. Review the files before adding them to version control.

## Preview and update

```sh
# Preview without writing files
python3 scripts/install.py --target both --dry-run

# Back up and replace an existing, different copy
python3 scripts/install.py --target both --replace
```

An identical installation is left alone. A different existing copy stops installation unless `--replace` is supplied. To preview replacement of a different copy, combine `--replace` with `--dry-run`.

Backups live outside the active skills directory, under `.claude/skill-backups/` or `.agents/skill-backups/` beneath the same home or project directory. The installer prints each backup path. It refuses symlinked source contents and destination paths. Review linked installations manually.

## Use a different invocation name

Skill names are local invocation names, not globally reserved package identities. If another skill uses `overkill`, install this one with an alias.

```sh
python3 scripts/install.py --target both --name my-overkill
```

Invoke the installed alias as `/my-overkill Pro ...` in Claude Code or `$my-overkill Pro ...` in Codex.

The installer changes the installed directory name, the `SKILL.md` name field and the Codex default invocation prompt. The repository source and Overkill branding stay the same. Names must contain 1 to 64 lowercase letters, digits or hyphens, with no leading, trailing or consecutive hyphens.

The installer checks only its selected destinations. It does not find or resolve duplicate names in other projects, personal directories or plugins. Each host controls how it handles those duplicates. A distinct alias makes your intended invocation easier to identify.

## Manual installation

Copy the entire `skills/overkill` folder into the destination for your host. Keep `LICENSE`, `references/` and `agents/` with `SKILL.md`. Review an existing copy before replacing it.

## Other hosts

Overkill follows the [Agent Skills format](https://agentskills.io/specification). Its core instructions do not depend on Claude-only or Codex-only tool names, hooks or model settings. The `agents/openai.yaml` file provides optional Codex UI metadata.

Other compatible hosts may load the same folder through their own installation process. Invocation syntax, permissions and tools vary, and those hosts have not been tested here.

Delegation requires a host that exposes and permits delegation tools. A limit on concurrent workers calls for batches. When delegation is unavailable, Overkill uses explicitly labelled same-context alternatives. Sharing a file format does not guarantee identical behavior or support for every effort profile.
