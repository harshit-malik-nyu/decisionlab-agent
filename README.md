# DecisionLab

**Auditable agentic investigations for growth and product decisions.**

DecisionLab explores a practical question: can a tool-using agent turn a retention anomaly into a defensible experiment proposal, while refusing to act on incomplete evidence?

**Status: research prototype, v0.3, with preserved real-model evaluations.** On six authored development cases, Qwen2.5 1.5B scored 0/6, Qwen2.5 3B scored 3/6, and the 3B model plus an explicit invalid-data stopping policy scored 6/6. The final result comprises **three model-generated pilot proposals and three deterministic runtime holds**. These are single-run development results, not independent generalization or state-of-the-art evidence. All traces, model digests, source commits, prompt/source hashes, timings and token counts are in `evaluation/`.

## Review in five minutes

1. Open `site/index.html` for the interactive evidence replay. It works offline.
2. Compare the clean and reversal cases: the recommended investigation segment changes.
3. Inspect a missing-outcome case: the system holds instead of recommending a pilot.
4. Expand a scenario's evidence: every dollar amount is conditional on explicit lift, margin, horizon and cost assumptions.
5. Run the tests and inspect `docs/RESEARCH_CARD.md` for what has and has not been established.

## Run with no paid API

Python 3.11+; the core has **no third-party Python dependencies**.

```sh
python -m unittest discover -s tests -v
python -m decisionlab demo --case clean
python -m decisionlab benchmark
python scripts/build_site.py
```

For real model-selected tool execution, install [Ollama](https://ollama.com/) and a locally runnable model using its official instructions. Example (hardware and model availability permitting):

```sh
ollama pull qwen3:4b
python -m decisionlab agent --model qwen3:4b --case clean --output local-run.json
```

Ollama must be serving on `127.0.0.1:11434`. This project does not require an inference subscription. Model downloads, RAM, disk, electricity and hardware are still resources; zero paid API cost does not mean zero resource use. The exact model tag is configurable and no model quality is assumed. The hosted evaluation workflow uses its explicitly configured model.

If the endpoint fails, the command fails visibly. **It never silently substitutes the rules baseline.** Local-model runs are not automatically uploaded. Review traces before sharing them.

## What makes the model mode agentic?

The model chooses an action, receives its executed result, and chooses the next action within a bounded loop. It can inspect schema and definitions, check quality, run read-only SQL, compute verified comparisons, evaluate conditional economics, and finish or hold. Tool ordering is model-selected; a separate runtime validates requests and gates decisions. The adapter uses JSON action messages through Ollama's [chat API](https://docs.ollama.com/api/chat), rather than assuming a provider's native function-calling format.

The included **adaptive-rules controller is not an LLM**. It supplies a cheap reference policy. The fixed-rules controller deliberately always investigates the small segment; it illustrates an adaptation failure, not a strong research baseline.

## Business question

> Retention fell while support costs increased. Which segment should we investigate, and is there a defensible pilot within a $10,000 ceiling?

The fully synthetic panel contains 120 accounts and two snapshots. In the clean scenario, small-account retention falls from 90% to 75%; large-account retention stays at 90%. Support costs also rise. These are descriptive associations, not evidence that support costs caused churn.

A small-segment scenario assumes a five-percentage-point retention improvement, $200 monthly value, 75% contribution margin and six months of sustained benefit:

`80 × 0.05 × $200 × 0.75 × 6 = $3,600` incremental contribution.

At a $2,000 pilot cost, conditional net contribution is $1,600; break-even lift is 2.78 percentage points. These numbers are **scenario arithmetic, not realized revenue or a treatment-effect estimate**. The model cannot spend the budget or approve a rollout.

## Three review lenses

| Lens | Inspectable work sample |
|---|---|
| Data analyst | SQL controls, denominator checks, missingness, snapshot grain, data and result hashes, reproducibility |
| Business analyst | Explicit decision constraints, conditional economics, break-even analysis, evidence trace and hold conditions |
| Product analyst | Segment diagnostics, causal limitations, experiment proposal, metric definitions and staged decision gates |
| Agent researcher | Adaptive execution loop, controller separation, bounded failure modes, adversarial fixtures and disclosed evaluation gaps |

## Architecture

`model action → dispatcher → bounded tool → evidence record → next model action`

The final action is separately checked: a pilot must cite both its valid comparison and a positive-net scenario. Exploratory SQL cannot certify arbitrary narrative claims. The output deliberately uses structured fields instead of unverified prose conclusions.

Tools: `schema`, `document`, `quality`, `sql`, `compare`, `scenario`, `finish`.

Evidence records retain tool arguments, result, dataset SHA-256 and a record SHA-256. Hashes establish reproducibility and integrity checks **within a trusted run**; they do not authenticate a real business source, prove a conclusion, or prevent a malicious author recomputing hashes.

## Evaluation and limits

Six authored regression scenarios: clean data, duplicate keys, missing outcomes, revised evidence, injected document instructions, and schema drift. Both reference policies hold on data-quality failures. The adaptive policy changes segment on the revised dataset; the fixed policy does not.

See `site/runs.json` for exact measured outputs and `docs/RESEARCH_CARD.md` for the protocol. These cases were written with the implementation and are **not held-out generalization evidence**. Passing a rule policy through an injection case does not establish that a language model resists prompt injection.

This release does not include multi-agent superiority claims, autonomous production writes, real customer data, an independent benchmark, or a public live-inference endpoint. Independent model trials and unseen task families remain necessary before a research-quality performance claim.

## Repository map

- `decisionlab/data.py`: deterministic synthetic fixture generation
- `decisionlab/engine.py`: bounded tools and decision gates
- `decisionlab/runner.py`: local model loop and explicit reference policies
- `decisionlab/benchmark.py`: regression evaluator and oracle
- `tests/`: executable failure-mode tests
- `site/`: offline interactive trace viewer and recorded reference runs
- `docs/`: research card, experiment proposal and threat model
- `.github/workflows/tests.yml`: tests and replay reproducibility checks

MIT license. Synthetic data and documentation are included under the same license.

## Validation hardening

The current release validates complete before/after account panels, stable segment membership, binary outcomes, finite positive monthly values, nonnegative support costs and exact schemas. Tool calls reject unexpected arguments. Returned observations and exported traces are isolated copies, so consumers cannot modify the recorded evidence. A pilot cites exactly one scenario and its comparison.

The evaluator requires a hold decision to cite invalid quality/comparison evidence. Exhausting the step budget receives no correctness credit. Segment scoring uses the scenario actually cited in the final decision, not the last scenario explored. These checks are covered by the automated suite, including five distinct malformed-panel subcases.

Early temporary runs were lost during a session interruption and are excluded from evidence. Subsequent GitHub Actions runs were preserved in this repository and replay-verified.

## Re-execute evidence and checkpoint model evaluations

```sh
python -m decisionlab demo --output trace.json
python -m decisionlab.verify trace.json
python -m decisionlab.evaluate --model qwen3:4b --output evaluation/run.json
```

The verifier regenerates the synthetic dataset and re-executes tool calls, checking results, final decisions, completion state and record hashes. It catches a fabricated result even if someone recomputes that result's hash. It trusts the installed source and fixture generator; it does not authenticate real-world business data. Version-1 traces must be regenerated for this verifier.

The evaluator writes an atomic checkpoint after each completed or failed case. Repeating the command resumes remaining cases only when the model tag, Python version, source hashes, prompt hash, cases and budgets match. Completed traces are replay-validated before resume. Failed cases remain visible and are not silently retried; use a new report for a new trial. An unfinished in-flight case can be lost, and a checkpoint must still be backed up outside an ephemeral workspace. A model tag can change upstream and is not an immutable model digest.

The suite now contains **48 tests**. Model-adapter and interruption tests use explicit test doubles; they are not measurements of model intelligence.


## Measured comparison and attribution

| Controller | Correct authored cases | What it establishes |
|---|---:|---|
| Fixed rules | 5/6 | A simple policy misses the revised segment |
| Adaptive rules | 6/6 | A deterministic reference policy handles these templates |
| Qwen2.5 1.5B | 0/6 | Small-model failures are preserved |
| Qwen2.5 3B | 3/6 | Valid-data proposals succeeded; invalid-data loops remained |
| Qwen2.5 3B + runtime quality gate | 6/6 | Three model proposals + three automatic, evidence-backed holds |

The model did not call the document tool in the recorded injection fixture. Passing that case therefore **does not demonstrate prompt-injection resistance**. No intervention was deployed, no customer benefit was measured, and a 6/6 development result is not a universal 10/10 rating. The fixed/adaptive rules are inexpensive and sufficient for these known templates; the model has not demonstrated superiority over adaptive rules.

Reproduce measured runs through `.github/workflows/model-smoke.yml`. Downloadable CI artifacts are retained for 30 days; the evidence JSON files committed here are the durable record. Model identity includes the downloaded digest, not just a tag.

### Publication integrity
The interactive viewer includes all three measured model runs, including failures. These are historical development runs, not a controlled ablation: code and prompts evolved. Publication re-executes every saved trace and rejects incomplete case coverage, duplicate cases, changed case identities, stale grades and inflated aggregate scores.

### Generated analytics stress checks
Run `python -m decisionlab.stress` to reproduce **600/600 passing engine checks**: 100 generated business datasets, each tested unmodified and with five data corruptions. Cohort sizes, retention rates, values, support costs and row order vary. An independent Python/Decimal arithmetic oracle checks retention deltas and scenario economics; invalid panels must fail closed. CI regenerates and compares the committed report on Python 3.11–3.13.

This is deterministic engine testing, not 600 model evaluations, not independent external validation, and not proof of generalization. Initial exploration found six datasets with floating-point cent discrepancies between calculation orders (seeds 1001, 1015, 1032, 1062, 1068, 1080). Currency calculations now use Decimal with explicit ROUND_HALF_UP. A regression asserts that 1057.725 becomes 1057.73. Earlier recorded model traces still replay successfully.

### Decision relevance, not just positive arithmetic
A retention-recovery pilot now requires a cited comparison showing an observed decline in the selected cohort, as well as positive conditional economics and valid data. Stable or improving cohorts can still be explored with the scenario tool, but cannot be presented as recovery recommendations. This is a workflow-specific policy, not a claim that businesses should never experiment on improving cohorts. Observed decline is not statistical significance or a causal estimate.

The generated stress suite independently checks pilot eligibility for both segments of every valid generated dataset. Explicit regressions cover improving, stable, declining and negative-economics cases. All earlier measured model traces still replay. No new model inference is claimed for this runtime change; rerun a frozen model evaluation before claiming changed model performance.

### Reviewer decision brief
Read [the generated decision brief](docs/DECISION_BRIEF.md) for the Data, Business and Product work sample: validated descriptive metrics, 12 economic scenarios, break-even sensitivity, an experiment specification, measurement contract and acceptance criteria. CI regenerates the brief directly from the analytics engine.
