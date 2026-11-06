# Decision brief: retention recovery

**Synthetic work sample. No customer impact or causal lift is claimed.**

## Decision requested

Authorize experiment design and measurement review, not rollout or spending. The selected cohort shows a descriptive decline; the intervention and its effect are still hypotheses.

## Evidence

The small cohort contains 80 accounts. Retention moved from 90.0% to 75.0% (-15.0 percentage points).
Support cost per account moved from $30.00 to $90.00. These concurrent changes do not show that support cost caused churn.

## Business sensitivity

Contribution assumes 75% margin and six months of persistence, before intervention cost. Each lift is an absolute percentage-point assumption, not a measured treatment effect. Support-cost savings are excluded to avoid inventing benefits.

| Assumed lift | Intervention cost | Conditional net contribution | Break-even lift |
|---:|---:|---:|---:|
| 1.0 pp | $1,000 | $-280.00 | 1.39 pp |
| 1.0 pp | $2,000 | $-1,280.00 | 2.78 pp |
| 1.0 pp | $5,000 | $-4,280.00 | 6.94 pp |
| 3.0 pp | $1,000 | $1,160.00 | 1.39 pp |
| 3.0 pp | $2,000 | $160.00 | 2.78 pp |
| 3.0 pp | $5,000 | $-2,840.00 | 6.94 pp |
| 5.0 pp | $1,000 | $2,600.00 | 1.39 pp |
| 5.0 pp | $2,000 | $1,600.00 | 2.78 pp |
| 5.0 pp | $5,000 | $-1,400.00 | 6.94 pp |
| 10.0 pp | $1,000 | $6,200.00 | 1.39 pp |
| 10.0 pp | $2,000 | $5,200.00 | 2.78 pp |
| 10.0 pp | $5,000 | $2,200.00 | 6.94 pp |

At the reference $2,000 cost, break-even is about 2.78 percentage points. A 1-point lift loses $1,280; a 5-point lift yields $1,600 under the stated assumptions. This spread is the reason to test rather than promise ROI.

## Product experiment specification

- Hypothesis: a specified onboarding or support intervention improves account retention; select one intervention before testing.
- Unit: account. Freeze eligibility before assignment, randomize accounts to treatment/control, and analyze intent-to-treat. Avoid mixing multiple users from one account across arms.
- Primary metric: retained eligible accounts / all eligible randomized accounts at a prespecified renewal horizon. Define renewal, cancellation, missing outcomes and late events before launch.
- Guardrails: support cost per assigned account, complaints, and revenue per assigned account. Set business-approved deterioration limits before exposure.
- Measurement contract: immutable account ID, assignment ID, timestamp, eligibility version, treatment exposure, renewal outcome and observation cutoff. Check duplicate assignments, sample-ratio mismatch and missingness by arm.
- Power gate: choose a minimum worthwhile effect, error rates and observation horizon; calculate required sample size before launch. The 80 synthetic accounts do not establish that a powered experiment is feasible.
- Decision rule: prespecify the analysis and confidence interval; ship only when the evidence meets the minimum worthwhile effect and guardrails. Otherwise hold or redesign. No repeated peeking followed by selective stopping.
- Scope: a causal analysis requires randomized prospective observations; these paired descriptive snapshots cannot estimate intervention lift.

## Ownership and acceptance

| Workstream | Deliverable | Acceptance criterion |
|---|---|---|
| Data | Validated account-period panel | No duplicate keys, missing outcomes, invalid values or changing segments |
| Business | Sensitivity and budget decision | Explicit cost, margin, horizon and break-even assumptions; human budget approval |
| Product | Preregistered experiment and event contract | Named intervention, eligibility, metrics, power calculation and stopping rule agreed before launch |
| Engineering | Auditable agent trace | Bounded read-only tools; replayed evidence; runtime holds attributed separately from model reasoning |

## Known limits

This memo is generated from one authored synthetic case. It does not demonstrate employer adoption, actual revenue impact, statistical significance, or model generalization. Historical model results and the 600 generated engine checks answer different questions and must not be combined into one AI success rate.

Reproduce with `python -m decisionlab.brief`.
