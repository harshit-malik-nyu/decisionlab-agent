# Retention pilot — a decision artifact, not a completed experiment

## Decision

Investigate the segment with the largest observed retention decline, after passing source-quality checks. The clean fixture prioritizes small accounts. Do not infer that rising support costs caused churn.

## Hypothesis

A specific onboarding intervention may improve account retention. The intervention has not been implemented or tested. A five-point improvement is a planning assumption only.

## Design

- Unit: account; randomize account IDs, never individual events.
- Population: eligible accounts at renewal, specified before assignment.
- Primary metric: retained accounts / all assigned eligible accounts at the prespecified renewal horizon (intention-to-treat).
- Guardrails: support cost per assigned account, gross margin, complaint rate.
- Record assignment, exposure, eligibility, outcome timestamp and missing-outcome reason.
- Check sample-ratio mismatch and differential missingness before interpretation.
- Specify exclusions before randomization. Do not exclude users because they failed to engage after assignment.
- Use a fixed horizon with no unplanned significance peeking; report confidence intervals, absolute differences and commercial implications.

## Feasibility caveat

The 80 small accounts in this fixture are not enough to establish a five-point lift reliably. A conventional two-sided 5% test with 80% power comparing 75% and 80% retention needs roughly 1,100 accounts per arm (normal approximation; exact design depends on attrition and analysis choice). The sample-size estimate must be recalculated for the real population. If sufficient volume is unavailable, treat a small pilot as a feasibility study, not an efficacy test.

## Economics and stop/go

A $2,000 planning cost against $3,600 conditional six-month contribution is an initial screen. Margin, incremental operating costs, persistence of benefit and cannibalization require validation. Do not scale based solely on the optimistic scenario.

Advance only after measurement integrity, adequate precision, guardrail performance and conservative incremental economics are acceptable. Otherwise hold, extend the prespecified study where justified, or reject the intervention. An inconclusive result is not evidence of no effect.
