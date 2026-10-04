# Effort levels

Use the profile the user selects. Medium is the default. Level names are case-insensitive. Recognize an explicit effort selection after the skill name or in a request such as "use the 67 tier". A number 67 appearing only in task data does not select the 67 tier.

## Allocation

| Level | Candidates | Reviewers | Verifiers | Worker roles | Additional correction rounds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Lite | 2 | 0 | 0 | 2 | 0 |
| Medium | 3 | 1 | 0 | 4 | 1 |
| Pro | 6 | 1 | 2 | 9 | 1 |
| Max | 12 | 2 | 4 | 18 | 2 |
| Ultra | 18 | 3 | 6 | 27 | 2 |
| Extreme | 24 | 4 | 8 | 36 | 3 |
| 67 | 48 | 7 | 12 | 67 | 4 |

Counts are target allocations and ceilings for delegated worker roles, excluding the coordinator. A role becomes a separately delegated task when the host permits it. The coordinator always integrates the result and checks final acceptance. Lite and Medium still verify evidence even though that work has no dedicated verification agents.

These profiles allocate work. They do not provision agents, change model reasoning effort or guarantee independent contexts. Report actual agent contexts, completed roles and any same-context fallback accurately. Do not claim 67 agents ran because the 67 tier was selected.

Corrections are optional targeted follow-ups after the initial review, not extra complete tournaments. A correction round addresses a remaining decisive gap, rechecks affected candidates and validates the revision. Stop earlier when the task is complete. Retries and substitute workers consume the same role allocation. Do not recursively give the full profile to each worker.

## How depth changes

- **Lite** explores two useful options. The coordinator checks the deciding claim, chooses and validates the result. Keep intermediate reports short.
- **Medium** develops three approaches and gives one reviewer the common brief and evidence. The coordinator resolves disputed facts and tests the selected result.
- **Pro** preserves the six-candidate idea. One reviewer compares the proposals. Two verifiers check decisive claims and likely failure cases, with work divided by the task.
- **Max** explores twelve approaches, ideally grouped into several strategy families. Two reviewers examine complementary criteria such as correctness and operational fit. Four verifiers divide factual checks, implementation behavior, edge cases and synthesis consistency where those concerns apply.
- **Ultra** develops eighteen approaches across relevant strategy families. Three reviewers cover the most important competing requirements. Six verifiers probe shared assumptions, adverse cases, integration and the final result. Reserve some verification work until a provisional solution exists.
- **Extreme** develops twenty-four approaches, four complementary reviews and eight verification assignments. Build a compact map of distinct strategies first. Include attempts to falsify assumptions shared by the leading candidates and checks of the combined result. Use the additional correction rounds only for unresolved gaps that can change the answer.

- **67** allocates forty-eight candidates, seven complementary reviewers and twelve verifiers. Organize the candidate pool into useful strategy families, such as six families of eight genuinely distinct approaches when the task supports that shape. Reviewers examine the feasible set through seven relevant concerns. Twelve verifiers divide evidence checks, adverse-case tests and final synthesis checks. Use at most four targeted correction rounds.

## Divide the roles

Use these as starting allocations and adapt the concerns to the domain while preserving the selected totals. A review compares proposals. A verification assignment checks evidence or an artifact. They are different jobs.

| Level | Candidate work | Review work | Verification work |
| --- | --- | --- | --- |
| Lite | 2 distinct options | Coordinator compares feasibility and tradeoffs | Coordinator checks the decisive claim and final answer |
| Medium | 3 distinct approaches | 1 reviewer checks the shared criteria | Coordinator resolves factual disputes and checks the result |
| Pro | 6 different approaches | 1 reviewer compares all feasible candidates | 1 checks decisive evidence, 1 checks failure cases and the final result |
| Max | 12 approaches across relevant families | 1 checks correctness, 1 checks practical fit | 1 factual check, 1 behavior check, 1 edge-case check, 1 synthesis check |
| Ultra | 18 approaches across relevant families | 1 checks correctness, 1 checks practical fit, 1 challenges shared assumptions | 2 evidence assignments, 2 adverse-case assignments, 2 final-result assignments |
| Extreme | 24 approaches across relevant families | 1 each for correctness, practical fit, shared assumptions and tradeoffs | 3 evidence assignments, 3 stress-case assignments, 2 final-result assignments |
| 67 | 48 approaches, with a compact strategy map | 1 each for constraints, correctness, evidence, complexity, resources, failure handling and synthesis coherence | 4 evidence assignments, 4 adverse-case assignments, 4 final-result assignments |

Do not turn this into a vote count. Reviewers' conclusions still need support, and the coordinator owns the final choice. In the highest tiers, final-result verifiers wait until a provisional synthesis exists.

Choose strategy families and review concerns for the task. A software project may vary architecture, migration path and failure handling. Research may vary explanation, identification strategy and source base. A writing task may vary argument and organization. Do not force software testing categories onto every domain.

## Schedule the work

1. Share the brief and assign materially different candidate strategies. Allocate reviewers and verifiers distinct responsibilities, with some final checks held until after integration.
2. Run candidates in batches within actual host limits. Keep their initial proposals separate where possible. Release finished workers if needed to free capacity.
3. Review the complete feasible set. Reviewers may work in parallel. Verifiers can check independent claims concurrently, but verification of a final synthesis must wait for that synthesis.
4. Resolve disagreements, integrate and perform the reserved final checks. Use only the permitted additional correction rounds.

For example, a host allowing four live agents including the coordinator has three worker slots. Pro's six candidates take two batches of three. The reviewer and two verification roles can use later slots as their inputs become ready. This is nine planned worker roles, not nine concurrent agents. If the host imposes a total-agent limit that cannot be freed, reduce or use clearly labelled same-context work within the available resources.

## When to adapt

An explicit small budget takes precedence over Extreme or 67. Reduce breadth first to preserve a decisive check and a finished result. Explain the change before large fan-out. If the budget cannot be measured exactly, treat it as a planning constraint and state that limitation.

Do not fill an allocation with cosmetic variants. First look for meaningful strategy differences or failure hypotheses. If the task has fewer useful avenues, say how many are worth exploring and reduce the allocation. A one-line calculation may use no worker at all. A demanding Extreme or 67 request with enough distinct work should receive the full planned allocation, subject to the stated limits.

When subagents are unavailable or prohibited, the profile describes a work plan for same-context passes. Scale it to the available budget and preserve honest process reporting. Never describe these passes as separate agents, independent trials or a context reset.
