# Contributing to Overkill

Overkill is maintained under Skill Issue Labs. The goal is to help an agent choose a sound approach and complete the user's task. Changes should improve observable behavior on a realistic example.

## Start with a failure

Include the request, relevant inputs, tool limits, observed failure and the smallest proposed correction. Remove private data. A reproducible case gives reviewers something to check.

Keep the installed skill self-contained and put contributor material in the repository documentation. If a change affects worker allocations or scheduling, update the effort profiles, README and relevant evaluation cases together. Preserve the original copyright notice in both copies of `LICENSE`.

## Run the local checks

Use Python 3.10 or newer in a development environment.

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate.py
python3 scripts/test_install.py
```

The validator checks package structure, metadata, local links and evaluation records. Installer tests use isolated temporary destinations. Neither check calls a model or proves that a host discovers the installed skill.

## Check behavior

1. Select relevant cases from [evals/cases.json](evals/cases.json), or add a case that exposes the failure.
2. Give the skill and case to a fresh evaluation context without the grading rubric or earlier answers.
3. Grade the resulting artifact and observable tool activity using [evals/rubric.json](evals/rubric.json). Mark each condition pass, fail or not observed.
4. Record the model and host when known, date, permitted tools, repetitions and material limitations.

See the [evaluation guide](evals/README.md) for the full process. A correct scheduling plan does not prove that the host executed those workers. A claim that a test ran needs evidence of that execution.

## Describe the change

Explain the concrete failure, the resulting behavior and the checks you performed. State any relevant checks you could not run. Keep simple tasks inexpensive and avoid adding instructions that only restate existing guidance.

Performance claims need repeated comparisons against the same tasks without the skill, using the same model, resources and evaluation method. Include failures and measured cost or latency where available. A favorable example or one judge's opinion is insufficient.

Do not commit account configuration, credentials, private prompts or raw internal reasoning. Public evidence should contain task inputs, observable outputs, tool actions and concise grading notes.
