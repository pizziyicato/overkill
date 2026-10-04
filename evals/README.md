# Evaluating Overkill

This suite checks concrete behavior on small supplied scenarios. It does not establish that the skill improves model performance.

## Files

- [cases.json](cases.json) contains user requests and permitted tools.
- [rubric.json](rubric.json) contains observable grading conditions.
- [RESULTS.md](RESULTS.md) records what has actually been tested.

Keep the rubric and earlier answers out of the context used to answer a case. The case runner should read only the installed skill, its effort profiles, the case prompt and the necessary inputs. A grader can read the rubric afterward.

## Run a case

1. Start a fresh agent context and load the skill.
2. Supply one case's `prompt` and `tools` exactly, enforcing the stated permissions.
3. Save its final answer and relevant observable tool actions. Exclude internal reasoning and unrelated private context.
4. Grade each condition as pass, fail or not observed. Tool use and completed checks require actual evidence.
5. Record the model, host, date, repetitions and resource limits. If multiple cases share a context, disclose that limitation.

The Pro, Extreme and 67 scheduling cases are planning exercises. A correct plan does not establish that the host can execute that many workers or recycle live contexts. Testing actual fan-out requires a separate run in the target host, a suitable task and a resource budget.

The no-tool cases test the skill's fallback behavior. They cannot validate independent delegation. The code case produces a completed function and test for a grader to execute separately.

## Compare versions

Run the same cases with and without the proposed change under comparable settings. Repeat runs when making a quality claim. Use the same hard constraints and grading conditions. Separate wrong answers, unsupported verification claims, missed constraints and unnecessary work instead of reducing every result to one subjective score.

Record latency, tokens and cost only when the host actually exposes measurements. Include failures and incomplete cases. Do not infer speed or savings from the number of agents.

## Structural checks

`python3 scripts/validate.py` validates metadata, profile totals, documentation consistency, local file links and case/rubric correspondence. It requires the repository's development dependencies. It does not call a model, install the skill, run a browser or test remote URLs.
