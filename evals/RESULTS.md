# Smoke-test results

Recorded 4 October 2026 for the standalone package, with follow-up checks for the 67 tier and installation aliases.

The initial two Codex evaluation agents received the skill and disjoint groups of four cases. A third evaluation agent later checked two additional cases for the 67 tier and numeric-tier disambiguation. Cases within each evaluator shared context. No evaluator was given the grading rubric or earlier case answers. The third evaluator disclosed that mandatory workspace setup exposed administrative project summaries. The coordinating agent graded observable answers afterward.

The exact model identifier and usage measurements were not recorded. There was one pass per case and no baseline run without the skill. This is a limited smoke test, not a performance benchmark or an independent third-party audit.

The first eight scenarios were exercised before the rename from 67 to Overkill. Their existing tier allocations were unchanged by the rename or the later addition of tier 67. Invocation names in the published cases were updated afterward. The two new scenarios exercised the final seven-tier instructions. The [recorded answers](observations.json) retain the wording each evaluator actually produced. Live client discovery has not been tested.

| Case | Result | Observed behavior |
| --- | --- | --- |
| elapsed-time | Pass | Recomputed A at 20% and B at 30%, corrected the false claim and selected B |
| no-feasible-option | Pass | Rejected both vendors without relaxing either mandatory constraint |
| extreme-tight-budget | Pass | Returned 25% in one line and made no agent calls |
| pro-scheduling | Pass | Planned 6 candidates, 1 reviewer and 2 verifiers in at most 3 worker slots |
| extreme-scheduling | Pass | Planned 36 worker roles, 6 candidate batches of 4, and at most 3 correction rounds |
| finish-implementation | Pass | Returned working code and a test that distinguishes the original ordering defect |
| shared-brief-correction | Pass | Applied the corrected production prices consistently and selected B |
| synthesis-conflict | Pass | Rejected the incompatible synthesis and retained immediate read correctness |
| 67-scheduling | Pass | Planned 48 candidates, 7 reviewers and 12 verifiers within 4 worker slots, with at most 4 correction rounds |
| numeric-data-not-tier | Pass | Kept Medium as the default when 67 appeared only as a price and selected the feasible option |

Every condition in [rubric.json](rubric.json) was satisfied in these observed answers. No scenario required live delegation. Scheduling cases were plans only, and all other cases prohibited delegation. The evaluators correctly did not claim executed tests or benchmarks.

The coordinator separately ran the generated code test plus empty-input and ordering/case checks. All passed. The generated test's expected output differs from the original defective function. This execution checks only the small supplied code case.

## Package and installer checks

The official skill validator and repository structural checks passed. Twenty-five isolated installer tests passed, including the original nine, fourteen alias-focused tests and two backup-preflight regression tests. Coverage includes complete copies, dry runs, idempotence, conflict preflight, backed-up replacement, symlink rejection, failed-swap rollback, personal destinations, coexistence under an alias, precise metadata updates, source preservation, invalid names and a CLI alias test against the shipped package.

The Skill Issue Labs release preparation also fixed backup-directory preflight across both hosts and made malformed Codex UI metadata fail with a validation message. The two new installer tests reproduced partial updates before the fix and passed afterward. The final local check used Python 3.14.6. GitHub Actions is configured for Python 3.10 and 3.12 on Ubuntu, macOS and Windows. Current hosted results are available in [GitHub Actions](https://github.com/pizziyicato/overkill/actions/workflows/validate.yml), separately from these recorded local checks.

The actual CLI was also exercised against a temporary project with both host targets. Both copies matched the source byte for byte. A repeated install reported both destinations unchanged. These checks validate file installation, not discovery or runtime execution by either client.

## Not established

- Actual execution of 9, 18, 27, 36 or 67 workers in a target host.
- Reliable lifecycle management, isolation or independent contexts in every client.
- Better accuracy, lower cost or faster completion than an unassisted baseline.
- Automatic discovery or invocation in Claude Code, Codex or another client.

## Current instruction fingerprints

These SHA-256 fingerprints identify the final seven-tier instructions. The two added cases were tested against this version. The eight earlier cases and their timing are described above.

- `skills/overkill/SKILL.md`
  `d3a822a8dec807c53b04c01bdc7071ea99b3fc717ffd6b8de47126a4094d2940`
- `skills/overkill/references/effort-levels.md`
  `ae8ac817ab55aef998f3ff6a3eff7c7dfc770dce366cc08ed8192e06799c1577`
