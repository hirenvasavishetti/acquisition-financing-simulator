# Implementation and verification map

Engineering is implemented for the documented educational scope. Historical evidence completeness remains a separate, unfinished track. Source publication to GitHub is complete. Verification does not turn assumptions into historical facts.

| Major requirement | Implementation | Verification / status |
|---|---|---|
| Financial conventions and independent benchmark | METHODOLOGY.md; benchmark fixtures; engine.py; funding.py | Predetermined full-model benchmark and independent Decimal issued-debt fee example |
| Five-year operations, opening bridge, sources/uses, instrument debt and liquidity | operating.py, engine.py, funding.py | Cash/debt rollforwards, itemised balanced funding, interest, maturity, WC continuity and no double counting |
| Three funding structures | Existing engine.STRUCTURES | Cash-first, liquidity-first and mixed calculated with common operating assumptions |
| Rates, spreads, operating and refinancing scenarios | scenarios.py, analysis.py, public_case.py | 48 synthetic comparisons; 36 public cases / 108 comparisons; refinancing remains assumed |
| Capacity and reverse stress | solver.py, analysis.py | Closing and every selected period checked; annual $948m versus quarterly $928m regression; infeasible and boundary cases |
| Calendar timing and maturity treatment | engine.py and instrument dates | Calendar period ends, fixed coupons, maturity/refinancing gaps; public case deliberately annual |
| Traceable ingestion and meaningful SQLite | ingestion.py, database.py | Cutoff, cache, source integrity, linked observations, canonical inputs, review/results queries and roundtrip tests |
| Evidence gate and 109 input relevance | evidence.py, policy.py, INPUT_REVIEW.md | Required-source removal blocks dependent recommendations even when model calculates; strict 23 gaps retained |
| Public output-level policy | public_case.py; PUBLIC_INFORMATION_POLICY.md | Supported history/bridge survive unrelated contract removal; affected funding outputs remain blocked |
| Historical source collection | data/source_archive; scripts/portfolio_sources.py; public_source_supplement.py | 87 reported facts plus 3 traceable derivations; 20 archives from 12 primary documents; review notes and hashes |
| Operating reconciliation and uncertain behaviour | public_case.py; public_defaults.json | Reported COS/SG&A/D&A/lease bridge; cost shares 65/80/95% preserve opening EBITDA and change downside results |
| Connected projected closing balances | public_case.bridge | Historical pre-WC CFO calibration, explicit closing WC assumptions, forecast CFO and post-close continuity |
| Financing fee and uses mechanics | funding.py | Fixed-budget and actual-issued-debt fees; separate analytical equity and stock consideration; independent reconciliation |
| Reinvestment uncertainty | public scenario configuration | Mechanical lower capex; linked growth reductions; dividends and synergy dependence shown |
| Editable assumptions and validation | public_inputs.py; public_defaults.json; data/public-assumptions.json | Live edits reach engine; dates, ranges, units and instrument identity validated; facts remain separate |
| Maintainable lightweight architecture | Existing modules plus funding/public_inputs/portfolio presentation modules | Consistent Black formatting; validated financial boundaries; shared calculation results and provenance IDs |
| Dashboard | portfolio_dashboard.py, live CLI server | Three modes, status/structure cards, charts, saved scenarios and live edits; stale-result treatment; desktop/narrow inspection |
| Connected Excel | workbook_plan.py, portfolio_workbook.py, workbook.mjs, portable_excel.py | 25 synthetic, 28 public, 10 strict sheets; cached/formula checks; readable itemised schedules; Python snapshot scope explicit |
| Concise memo | portfolio_memo.py, pdf_memo.py | Three two-page PDFs generated from corresponding reports; six pages visually inspected |
| Documentation and learning | README, METHODOLOGY, LEARNING, IMPROVEMENT_LOG | Current screenshot, exact commands, source-to-output interview walkthrough and before/after findings |
| Tests, clean install and CI | tests; scripts/verify_pipeline.py; scripts/verify_public.py; workflow | 74 tests; installed package outside source tree; portable exports and live HTTP checks; GitHub-hosted Ubuntu / Python 3.11 CI passed on 9 October 2026 |
| Publishing preparation | pyproject.toml, ignore rules, delivery ZIP | Public repository published 9 October 2026; environments, dependency folders, inspection logs and generated databases excluded |

## Remaining historical and scope limits

Strict assessment retains 23 material gaps with individual applicability in the output gap registers. The public case supports verified historical calculations and explicitly conditional annual projections, not legal covenant compliance, committed borrowing availability or executable financing. Unbounded private obligations and essential restrictions prevent an overall actual-company funding preference. Terminated FL facilities contribute no post-close liquidity.

The public annual closing bridge uses prior seasonal cash-flow information and explicit future working-capital/access assumptions; it is not a verified closing balance or a quarterly liquidity forecast. Post-breach schedules continue mechanically and do not describe an executable funding path. Analytical thresholds are not contractual covenants. See VERIFICATION.md for what was actually checked and PUBLIC_CASE_REVIEW.md for financial limitations.
