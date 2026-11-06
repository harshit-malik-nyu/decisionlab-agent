# Research card — v0.3

DecisionLab studies auditable business investigations using bounded tools, explicit assumptions, re-executable evidence and deterministic data-quality stopping rules. It is a research prototype, not a novel algorithm or independent benchmark result.

## Preserved measurements

Six authored development cases, one observed run per model configuration, seed 17, maximum 12 tool actions, Ollama CPU inference, temperature 0. Exact runtime/model digests, code commits, prompt/source hashes, token counts and per-case latency are committed in `evaluation/`.

| Configuration | Correct cases |
|---|---:|
| Qwen2.5 1.5B | 0/6 |
| Qwen2.5 3B | 3/6 |
| Qwen2.5 3B with invalid-data stopping policy | 6/6 |

The guarded result contains three model-origin pilot proposals and three runtime-origin holds. The stopping policy examines tool-returned data validation, not evaluator labels. Model inference selects tools and assumptions for valid investigations; the runtime owns permissions, validation and invalid-data termination. Budget exhaustion earns no correctness credit.

The evaluator judges the largest-decline segment and evidence-backed holds under this task's defined objective. It does not establish that this is the globally optimal business investment. Scenario lift, contribution margin and persistence are assumptions, not causal estimates. A pilot proposal is not automatic spending authorization.

## Important negative evidence

The small model failed all six tasks. The unguarded larger model looped on invalid data. All failures are retained. The adaptive rules reference already achieves 6/6, so these results do not show the model outperforms a deterministic policy. Temperature zero does not guarantee bitwise repeatability across runtimes or hardware.

The model did not retrieve the malicious document in the injection case. That run tests behavior with the document present but unexposed; it provides no evidence of resistance after exposure. Revised evidence is a fresh investigation with a changed dataset hash, not durable-memory invalidation.

## What remains unproven

- Unseen schema and domain generalization.
- Prompt-injection resistance after actual document exposure.
- Independent evaluation, repeated trials and statistical precision.
- Real causal effects, business impact or employer demand.
- Superiority over strong workflows or other agent architectures.
- Safe ingestion of arbitrary external datasets and production deployment.

## Next research protocol

Freeze the source and prompt; introduce independently authored tasks with new schemas and metric ambiguity; keep oracle labels out of the agent's context; compare strong deterministic workflows against model-only and guarded-model conditions. Force and record document exposure for injection tests. Repeat matched tasks and publish all failures, token use, latency and uncertainty across independent task instances. Do not treat repeated seeds that only permute IDs as independent business problems.

## Verification boundary

`python -m decisionlab.verify trace.json` regenerates the synthetic fixture and re-executes recorded tools. It detects edited results even if hashes are recomputed. It trusts the installed code and fixture generator; hashes do not authenticate real-world sources. Early ephemeral experiments lost during an interruption are excluded from measured claims.
