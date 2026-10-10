# Portfolio improvement checklist and decisions

## Checklist
- [x] Reproduce baseline and review nine findings.
- [x] Align model, capacity and reverse stress timing; document maturity conventions.
- [x] Review cost disclosures and expose alternative cost behaviour.
- [x] Connect closing working capital without double-counting CFO.
- [x] Itemise uses and implement variable versus fixed-budget financing fees.
- [x] Separate mechanical reinvestment cuts from linked growth scenarios.
- [x] Add validated public assumption configuration and live controls.
- [x] Improve code readability and meaningful regression benchmarks.
- [x] Redesign scope/status, comparison and source views.
- [x] Refresh workbook, memo, README and interview walkthrough.
- [x] Verify installation, live recalculation, financial exports and responsive visuals.

## Review findings (before changes)
The initial source inspection confirms annual-only solver calls despite quarterly engine support; cost decomposition of 35%/30% margins and 10% variable expenses; closing cash projected without closing inventory/receivable/payable continuity; fixed financing-fee budgets under equity substitution; lower investment with unchanged growth; Python-only public assumption edits; reserves aggregated into transaction_fees; and ambiguous global dashboard status/raw dictionaries. Numerical reproduction and primary-source spot checks follow below.

## Decisions
- Preserve the existing engine, evidence registry, SQLite and export pipeline. Extend selected boundaries rather than replacing the project.
- Keep annual timing as the backward-compatible default; expose quarterly synthetic results and evaluate capacity/stress at the selected frequency. Public quarterly timing remains unsupported without explicit seasonal assumptions.
- Keep fixed-budget fees as an explicit historical comparison convention and add actual-issued-debt fees. Analytical equity remains separate from stock elections.
- Public cost behaviour and investment/growth links are analyst scenarios, never facts inferred from EBITDA matching.
- Preserve strict evidence status while presenting operational/conditional/blocked statuses separately.

## Verified before/after results
All nine review findings were confirmed against the preserved baseline. The original 65-test suite was reproduced before extending it; the final suite contains 74 tests.

| Finding | Correction and evidence |
|---|---|
| $948m annual cash-first capacity fails quarterly | Independently reproduced $24.268m quarterly reserve shortfall; quarterly capacity is $928m and $929m fails |
| Annual-only solver/stress | Explicit frequency now flows through model, capacity, reverse stress and live controls; both timing capacities exported |
| Assumed margins calibrated to EBITDA | Replaced with sourced income-statement reconciliation; 65%, 80%, 95% variable shares preserve starting EBITDA and expose downside uncertainty |
| Disconnected closing WC | Prior CFO WC contribution removed, forecast WC movement deducted once; post-close starts from projected closing balances |
| Fixed fees during debt substitution | Both fixed-budget and issued-debt conventions; independently worked Decimal fee example verifies the latter |
| Lower investment with unchanged growth | Retained as labelled mechanical sensitivity; added linked 1pp and 2pp growth reductions |
| Python-only public edits | Validated JSON configuration and live assumption controls with stale-result indicators |
| Aggregated transaction fees | Itemised consideration, awards, principal, premium, interest, expenses, financing fees and collateral reserves |
| Ambiguous status and dense presentation | Three distinct modes, comparison cards, readable constraints, charts, workbook navigation and concise model-derived memos |

The connected bridge changes projected DKS cash from $1,228.437m to $1,336.902m and FL cash from $215.150m to $96.100m. These are conditional forecasts, not closing facts. All public base structures still fail the analytical screens. Mixed passes three explicitly labelled policy scenarios, but this does not establish an overall financing preference. See PUBLIC_CASE_REVIEW.md for drivers and limitations.
