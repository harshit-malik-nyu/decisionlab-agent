# DecisionLab

**Auditable agentic investigations for growth and product decisions.**

DecisionLab explores a practical question: can a tool-using agent turn a retention anomaly into a defensible experiment proposal, while refusing to act on incomplete evidence?

**Status: research prototype, v0.1.** The local-model action loop is implemented. Automated tests exercise it with test doubles. No real-model evaluation has been completed in the build environment: its local inference endpoint is unavailable. The included replay and scores are **deterministic rule-policy runs**, not AI-generated runs. There is no claim of state-of-the-art performance or demonstrated employer demand.

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

Ollama must be serving on `127.0.0.1:11434`. This project does not require an inference subscription. Model downloads, RAM, disk, electricity and hardware are still resources; zero paid API cost does not mean zero resource use. The exact model tag is configurable and no model quality is assumed.

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

This release does not include multi-agent superiority claims, autonomous production writes, real customer data, an independent benchmark, or a deployed live model. Independent model trials and unseen task families remain necessary before a research-quality performance claim.

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
