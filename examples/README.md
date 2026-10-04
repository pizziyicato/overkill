# Overkill examples

These examples show the intended behavior. They are illustrative outcomes, not recorded model runs or performance evidence. Use `$overkill` in Codex and `/overkill` in Claude Code. Medium applies when no effort level is named.

## Choose a feasible design

### Request

```text
Use $overkill to choose a search design for a help center that must work offline.
The documents fit in memory. Exact product names matter more than paraphrases.
Compare substring matching, a local inverted index and a hosted semantic API.
I only need advice. Do not implement anything.
```

### Expected result

Start with local substring matching if the collection is small and latency is acceptable. Measure representative queries before taking on an index. A local inverted index becomes attractive if scanning misses the latency target or ranked token matching matters. The hosted API fails the offline requirement and is excluded.

The deciding check is latency and retrieval quality on the actual corpus. Until those measurements are available, the recommendation remains conditional. The agent should not claim that it measured this dataset.

## Check the claim that changes the winner

### Request

```text
Use $overkill to compare two proposals using only these supplied facts.
The current job takes 40 seconds. Proposal A takes 32 seconds and costs nothing.
Proposal B takes 28 seconds and costs $200 per month. B is within our budget.
We require at least 25% less elapsed time. The current summary says A is 40% faster.
Pick an option and explain the arithmetic. No web or agents.
```

### Expected result

Choose B. A reduces elapsed time by `(40 - 32) / 40 = 20%` and misses the requirement. B reduces it by `(40 - 28) / 40 = 30%` and meets the requirement within budget. A's claimed 40% improvement is incorrect.

These are calculations from supplied values, not a benchmark the agent ran. The comparison uses same-context alternatives because delegation is prohibited.

## Skip an unnecessary panel

### Request

```text
Use $overkill to tell me the percentage decrease from 80 to 60. Keep it to one line.
```

### Expected result

The decrease is 25%, calculated as `(80 - 60) / 80`.

A calculation with one determined answer does not need competing proposals.

For recorded behavior and its limits, see the [smoke-test results](../evals/RESULTS.md).
