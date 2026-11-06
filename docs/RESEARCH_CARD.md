# Research card — v0.1

## Claim boundary

This is an auditable investigation **prototype**, not a published novel agent algorithm. The useful hypothesis is that typed evidence gates can reduce unsupported business decisions at the cost of greater abstention. This release demonstrates the gates and supplies a testable harness; it has not established that hypothesis statistically for real models.

## Measured configuration

- Standard-library Python, SQLite in-memory data.
- 120 synthetic accounts, two observations each before perturbation.
- Six authored scenario families, seed 17. Seed permutes identifiers only; different seeds are **not independent business problems**.
- Fixed rules vs adaptive rules; same tools and gate policy.
- Correctness: hold for invalid data, otherwise propose a pilot for the oracle's largest-decline segment.
- Additional recorded metrics: calls and tool errors.
- Fixture authors know the oracle. This is regression testing, not blind testing.

## Expected and actual results

The generated replay contains the actual outcomes. Fixed rules should pass five of six cases and adaptive rules six of six. This narrow distinction only tests segment adaptation. A six-case result cannot be represented as a real-world success rate or confidence bound on generalization.

No real-model accuracy, token usage, latency comparison, injection-resistance rate or cost reduction has been measured. A local endpoint connection attempt failed in the build environment. Mock-model tests establish orchestration behavior only.

## Next experiment required before stronger claims

1. Freeze this implementation and prompt by commit hash.
2. Have a separate evaluator author new schemas, metric definitions and causal-confounding tasks; keep labels outside agent context.
3. Compare a strong deterministic workflow, one model with tools, and the same model with evidence gates disabled in a disposable evaluation harness.
4. Use matched task instances and fixed tool budgets. Report all failures and abstentions, not only successful traces.
5. Record model digest, runtime version, hardware, prompt, dataset hashes, per-call latency, prompt/output tokens and random seeds.
6. Evaluate numeric correctness, decision correctness, citation entailment, appropriate abstention, harmful-action attempts and prompt-injection success separately.
7. Report paired differences with uncertainty over independent task instances. Repeated runs of one template do not create independent evidence.
8. Test memory or specialist agents only after the single-agent baseline is stable. More agents are not evidence of better reasoning.

## Failure modes left open

- A model can choose an economically positive but weakly justified lift assumption.
- Evidence gates certify arithmetic and prerequisites, not the truth of the assumed effect.
- A model can waste its budget, abstain unnecessarily or select a suboptimal segment.
- The schema-drift case fails closed instead of repairing arbitrary schemas.
- Revised evidence is evaluated as a fresh run with a new data hash; this release does not implement mid-run state migration or durable memory invalidation.
- SQL is constrained but this is not a complete hostile-code sandbox.
- Synthetic data cannot demonstrate external business impact or hiring demand.

## Research context

- Anthropic, [Building effective agents](https://www.anthropic.com/research/building-effective-agents): distinguishes workflows from agents and motivates simple evaluated architectures.
- [DABstep](https://arxiv.org/abs/2506.23719): an example of the difficulty of evaluating realistic data-analysis agents. DecisionLab does not claim results on DABstep.
- [Ollama chat API](https://docs.ollama.com/api/chat): interface used by the optional local model adapter.
