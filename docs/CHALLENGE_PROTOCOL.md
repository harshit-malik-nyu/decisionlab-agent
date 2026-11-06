# Prospective challenge protocol v1

This protocol is committed before inference. Six new authored cases test whether the existing prompt and agent can reject a misleading premise and distinguish descriptive evidence from assumed economics. No prompt tuning, model change or retries selected for a better score are allowed within this run.

| Case | Expected decision | Evidence required |
|---|---|---|
| Improving retention | Hold | Valid comparison with no declining segment |
| Flat retention and support cost | Hold | Valid comparison with no declining segment |
| Support-cost spike without retention decline | Hold | Valid comparison with no declining segment |
| Equally declining cohorts | Pilot | Either declining segment, positive scenario and its cited comparison |
| Missing account-period observation | Hold | Invalid panel evidence |
| Account changes segments | Hold | Invalid panel evidence |

The original question asserts retention fell. Three fixtures contradict that premise. The correct response should follow tool evidence, not accept the question's assertion. A hold without relevant cited evidence or from budget exhaustion earns no credit.

Model: Qwen2.5 3B through pinned Ollama 0.40.14, temperature 0, 12 tool steps, same existing SYSTEM and QUESTION for all cases. Save model digest, source hashes, prompt hash, code commit, per-case traces, token metadata and timing. Preserve failures. The reference is a deterministic comparison/quality/scenario policy, not an LLM.

Report per-case model and reference outcomes separately; do not pool these results with engine stress tests or earlier development scores. One run per case is a limited measurement. The same project author created these tasks and knows their intended answers: this is prospective authored challenge testing, **not independent held-out validation or proof of generalization**. A changed implementation or prompt requires a new named protocol and retention of the old result.

Reproduce on a local Ollama installation with `decisionlab.challenge.evaluate(LocalModel('qwen2.5:3b'), 'new-output.json')`, or use the `Prospective challenge evaluation` GitHub workflow. Output paths must be new: the evaluator refuses to overwrite prior evidence.
