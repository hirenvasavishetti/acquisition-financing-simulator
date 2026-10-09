# Requirement and verification map

Engineering completion means the deterministic educational implementation works
under the documented conventions. Historical clearance and public publication
are separate. Test evidence and environment are recorded in VERIFICATION.md.

| Requirement | Implementation | Engineering verification | Historical status |
|---|---|---|---|
| Financial conventions; independent benchmark | METHODOLOGY.md; full_benchmark.json; engine.py | Predetermined funding, interest, repayment and closing answers | Actual bridge unreconciled; no forced headline match |
| Source register, cutoff and four classifications | evidence.py, policy.py, data/historical.json | Removal, modified bytes/value, duplicate/conflict, post-cutoff, synthetic-origin and assumption tests | 83 factual observations, 3 verified derivations, 6 explicit future choices; 23 material gaps remain |
| 109 inputs; relevance and materiality | policy.materiality; INPUT_REVIEW.md; all output Evidence rows | Old trend checks activate conditionally; current-source removal blocks | Explicit growth does not require old trend history; current facts/contracts remain required |
| Equity/EV; awards; cash/noncash sources/uses | engine.transaction | Balanced uses, target cash excluded, CoC repayment, dilution, capped eligible uses | Share/award inventory and opening cash/debt incomplete |
| Opening cash/debt bridge | engine.transaction | Cash not double spent; principal and carrying values separate | Pre-close bridge assumptions and restrictions unresolved |
| Separate five-year operations | operating.py, engine.py | Level shocks, EBITDA identity, WC signs, cash/debt rollforwards across all stress runs | Latest EBITDA, rent and some operating reconciliation gaps |
| Instruments, leases and liquidity | engine.py | Fixed coupon invariance, amortisation, maturity gaps, revolver limits, refinancing caps, lease cash adjustment | Executed instrument/borrowing/CoC provisions not fully mapped |
| Capital allocation and synergies | config.py, operating.py | Explicit cash distributions, integration costs and synergy shocks | Future policy choices still need rationale |
| Cash-first, liquidity-first, mixed | engine.STRUCTURES | Same operations; funding rules and dilution checks | No actual-company preference issued |
| Individual/combined stress, rates, spread/refi | scenarios.py, analysis.py | 45 operating/pricing comparisons plus 3 assumed-refinancing runs | Benchmark source context reviewed; issuer quotes/OAS not inferred |
| Conditional capacity | solver.capacity | Fixed uses/cash, separate analytical equity, feasible and next-dollar failure, disconnected sample ranges | Remains illustrative |
| Reverse stress and sensitivities | solver.py | Starting-failure and no-breach tests; eight policy/pricing sweeps | Remains illustrative |
| Quarterly extension | operating.py, engine.py | 20 quarters; first eight exported; annual operating and quarterly cash aggregates reconcile | Pre-cutoff quarterly seeds not verified; labelled synthetic |
| SQLite | database.py | Canonical input roundtrip, linked observations/instruments, run and analytical queries | Verified extracts stored separately from synthetic data |
| Traceable ingestion | ingestion.py, CLI | Cache/integrity, bounded429 retry, no403 retry, cumulative periods, cutoff, SEC contact checks | Automated SEC request awaits truthful contact identity |
| Dashboard | dashboard.py, live CLI server | Browser structure selection and threshold recomputation; API validation | Blocked status persistent |
| Excel | workbook_plan.py, workbook.mjs, portable_excel.py | 21 demo sheets / 9 historical sheets, cached/formula reconciliation, error-cell scan and rendered previews | Blocked status in Summary and evidence details |
| Two-page memo | pdf_memo.py | Two-page count; both pages visually inspected | Explicitly illustrative; historical gaps stated |
| Learning and documentation | README, LEARNING, METHODOLOGY, DECISIONS | Input-to-SQL/model/UI trace; solver explanation; five exercises; interview questions | AI-assisted source-review attribution explicit |
| CI and clean install | pyproject.toml, workflow, verify_pipeline.py | Fresh environment installs wheel; model/tests/artifacts/HTTP checks | GitHub-hosted CI not executed until publication |
| GitHub preparation | ignore rules, README publication commands | Existing Git/history inspected; archive inventory checked | Not published; no fabricated commits |

External/scope limits: source completeness and historical modelling choices remain
unresolved; no authenticated SEC automated request without contact identity; OAS
permission not established. Detailed lease accounting, daily interest/solvency and
unused commitment fees are documented educational simplifications. These are not
silently interpreted as actual-company contractual terms.

## Public-information amendment: implementation and verification

This extends the original engineering map above; its historical column describes the strict assessment.

| Requirement | Implementation | Verification / supported scope |
|---|---|---|
| Scope before implementation | PUBLIC_INFORMATION_POLICY.md | Written before the public-case module; strict 109-check policy preserved |
| Individual review of 23 gaps | public_case.classify_gaps; public-gap-assessment.json | 23 entries retaining source, missing information, materiality and route applicability |
| Primary facts and traceable bounds | public_source_supplement.py; public_dks/public_fl archives | Five reviewed factual groups; claim, archive hash and cutoff checks; no URL-only verification |
| Forecast closing balances | public_case.bridge | Independent decimal benchmark; 39-week calibration, dividends, lease principal and cash-access fractions |
| Output-level evidence policy | public_case.analyse_public | Missing contract suppresses financing while retaining supported bridge/history; missing cash suppresses bridge |
| Connected uses, operations, debt and cash | public_case.construct; existing engine | Three five-year structures; zero existing facility draws; source/use, cash and debt reconciliation |
| Contractual route | Retain DKS notes; redeem FL notes; terminate FL ABL | Coupon, call premium, accrued interest, LC reserve and absent FL-note postclose ledger tests; lease allocation labelled approximate |
| Analytical capacity and reverse stress | Existing solver with public configuration | $25m/$5m capacity grid, 1pp reverse stress; base already fails; selected policy capacity recomputed |
| Structure uncertainty | 28 cases / 84 comparisons | Mixed passes only lower-reinvestment/no-dividend case; fails without synergies; no overall preference unlocked |
| SQLite and reproducibility | public_information_reviews; CLI query public | Full public bundle stored with source-state, code and assumptions fingerprints; export equality test |
| Dashboard, Excel, memo | public_exports; shared workbook plan; PDF branch | 20-sheet public workbook, two-page memo, HTML/JSON/status and cached-formula checks; synthetic outputs separate |
| Clean install and CI | Wheel, existing pipeline plus verify_public.py | Core installed in fresh environment; optional exports checked in dedicated environment; GitHub CI configured, not run |
| Unsupported claims | Always-blocked public output policy | Actual covenants, confirmed availability, complete uses and overall preference remain blocked; historical completeness false |

Engineering is implemented and verified. The public case supports scoped conditional calculations, not complete historical financing clearance. GitHub publication has not occurred.
