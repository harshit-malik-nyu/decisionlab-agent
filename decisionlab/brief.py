"""Reproducible reviewer brief from the clean synthetic fixture."""
from pathlib import Path
from .engine import Investigation

def build():
    lab=Investigation('clean',max_steps=40)
    try:
        comparison=lab.step('compare')['result']
        segment=comparison['priority'];g=comparison['segments'][segment]
        lines=['# Decision brief: retention recovery','',
               '**Synthetic work sample. No customer impact or causal lift is claimed.**','',
               '## Decision requested','',
               'Authorize experiment design and measurement review, not rollout or spending. The selected cohort shows a descriptive decline; the intervention and its effect are still hypotheses.','',
               '## Evidence','',
               f"The {segment} cohort contains {g['after']['n']} accounts. Retention moved from {g['before']['retention']:.1%} to {g['after']['retention']:.1%} ({g['change_pp']:+.1f} percentage points).",
               f"Support cost per account moved from ${g['before']['support_per_account']:.2f} to ${g['after']['support_per_account']:.2f}. These concurrent changes do not show that support cost caused churn.",'',
               '## Business sensitivity','',
               'Contribution assumes 75% margin and six months of persistence, before intervention cost. Each lift is an absolute percentage-point assumption, not a measured treatment effect. Support-cost savings are excluded to avoid inventing benefits.','',
               '| Assumed lift | Intervention cost | Conditional net contribution | Break-even lift |',
               '|---:|---:|---:|---:|']
        for lift in (.01,.03,.05,.10):
            for cost in (1000,2000,5000):
                r=lab.step('scenario',{'segment':segment,'lift':lift,'cost':cost})['result']
                lines.append(f"| {lift*100:.1f} pp | ${cost:,.0f} | ${r['net_scenario']:,.2f} | {r['break_even_lift']*100:.2f} pp |")
        lines+=['','At the reference $2,000 cost, break-even is about 2.78 percentage points. A 1-point lift loses $1,280; a 5-point lift yields $1,600 under the stated assumptions. This spread is the reason to test rather than promise ROI.','',
        '## Product experiment specification','',
        '- Hypothesis: a specified onboarding or support intervention improves account retention; select one intervention before testing.',
        '- Unit: account. Freeze eligibility before assignment, randomize accounts to treatment/control, and analyze intent-to-treat. Avoid mixing multiple users from one account across arms.',
        '- Primary metric: retained eligible accounts / all eligible randomized accounts at a prespecified renewal horizon. Define renewal, cancellation, missing outcomes and late events before launch.',
        '- Guardrails: support cost per assigned account, complaints, and revenue per assigned account. Set business-approved deterioration limits before exposure.',
        '- Measurement contract: immutable account ID, assignment ID, timestamp, eligibility version, treatment exposure, renewal outcome and observation cutoff. Check duplicate assignments, sample-ratio mismatch and missingness by arm.',
        '- Power gate: choose a minimum worthwhile effect, error rates and observation horizon; calculate required sample size before launch. The 80 synthetic accounts do not establish that a powered experiment is feasible.',
        '- Decision rule: prespecify the analysis and confidence interval; ship only when the evidence meets the minimum worthwhile effect and guardrails. Otherwise hold or redesign. No repeated peeking followed by selective stopping.',
        '- Scope: a causal analysis requires randomized prospective observations; these paired descriptive snapshots cannot estimate intervention lift.','',
        '## Ownership and acceptance','',
        '| Workstream | Deliverable | Acceptance criterion |',
        '|---|---|---|',
        '| Data | Validated account-period panel | No duplicate keys, missing outcomes, invalid values or changing segments |',
        '| Business | Sensitivity and budget decision | Explicit cost, margin, horizon and break-even assumptions; human budget approval |',
        '| Product | Preregistered experiment and event contract | Named intervention, eligibility, metrics, power calculation and stopping rule agreed before launch |',
        '| Engineering | Auditable agent trace | Bounded read-only tools; replayed evidence; runtime holds attributed separately from model reasoning |','',
        '## Known limits','',
        'This memo is generated from one authored synthetic case. It does not demonstrate employer adoption, actual revenue impact, statistical significance, or model generalization. Historical model results and the 600 generated engine checks answer different questions and must not be combined into one AI success rate.','',
        'Reproduce with `python -m decisionlab.brief`.']
        return '\n'.join(lines)+'\n'
    finally:lab.close()

if __name__=='__main__':
    Path('docs/DECISION_BRIEF.md').write_text(build())
    print('Generated decision brief from executable scenario evidence.')
