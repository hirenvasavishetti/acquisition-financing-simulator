# Historical evidence review — information cutoff 15 May 2025

Recommendation status: **Blocked — insufficient verified evidence.** No actual-company financing preference is issued. Engineering remains separate and working. This review does not claim historical completion.

The original 36 material gaps are now **13 resolved, 23 remaining**. Seven resolutions are historical facts or deterministic derivations: Foot Locker receivables; both revolver commitments; DICK'S unsecured commitment/LC ceiling; both simple operating EBITDA reconciliations; and Foot Locker financial-debt principal. Six resolutions are explicitly documented future modelling choices, **not six additional facts**. The original 109 requirements remain intact; 19 named supplementary disclosures support narrowly scoped calculations. Unregistered fields still block.

The executable gap register is in `historical-output/gap-register.json`; the readable register, all 36 materiality explanations, exact missing information, primary sources and applicability decisions are in `historical-output/memo.md` and the workbook. A requirement containing several facts stays unresolved if only part is verified.

## Supported results

USD millions, FY2024 ending 1 February 2025 unless stated:

| Calculation | DICK'S | Foot Locker | Limitation |
|---|---:|---:|---|
| Operating profit plus disclosed cash-flow D&A | 1,874.341 | 305.000 | Simple operating EBITDA; not covenant EBITDAR or adjusted EBITDA |
| Operating cash flow less gross capex | 509.270 | 105.000 | Historical residual; not forecast debt-service capacity |
| Inventory + receivables - payables | 2,066.337 | 1,303.000 | Selected operating working capital |
| Derived Q4 CFO less gross capex | 394.532 | 192.000 | FY minus 39 weeks; illustrates seasonality |
| Original fixed-note annual coupons | 54.375 | 16.000 | Excludes revolver, lease and refinancing interest |

Foot Locker's cash-flow cash reconciles: 401 cash/equivalents + 4 current restricted + 25 noncurrent restricted = 430. This does not prove acquisition availability. Financial debt is 400 note principal + 50 finance-lease liability = 450; operating lease liabilities are excluded. Its aggregate finance-lease rollforward also reconciles.

At the agreement's 12 May capitalization date, common shares alone imply **2,293.453968** cash consideration or **11.1614759776 million DICK'S shares** at the all-stock election endpoint. These are alternative endpoints, not election forecasts. Awards, closing share changes, fractional-share cash, fees and debt treatment remain outside this bounded calculation. Do not reconcile headline transaction enterprise value by plugging synthetic adjustments.

## Primary evidence collected

Fourteen integrity-checked factual-extract archives represent twelve distinct primary documents. Eleven archives were added to the prior three, including two supplements to already reviewed annual filings. Each factual observation binds value, unit, period and company to a reviewed document section and payload hash. The archives contain reviewed extracts, **not original filing bytes**, and have not received independent human sign-off. An accessible URL alone does not pass the gate.

| Publication | Primary document | Used for |
|---|---|---|
| 27 Mar 2025 | [DICK'S FY2024 10-K](https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm) | Financial statements, cash, notes, revolver, leases, non-cancellable purchase commitments |
| 27 Mar 2025 | [Foot Locker FY2024 10-K](https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm) | Financial statements, receivables, restricted cash, debt, leases |
| 27 Nov 2024 | [DICK'S Q3 10-Q](https://www.sec.gov/Archives/edgar/data/1089063/000108906324000121/dks-20241102.htm) | 39-week cash flows; derived fiscal Q4 |
| 11 Dec 2024 | [Foot Locker Q3 10-Q](https://www.sec.gov/Archives/edgar/data/850209/000143774924037241/floc20241102_10q.htm) | 39-week cash flows; derived fiscal Q4 |
| 14 Jan 2022 | [DICK'S credit agreement](https://www.sec.gov/Archives/edgar/data/1089063/000119312522009887/d285529dex101.htm) | Lease-adjusted covenant and conditional acquisition election |
| 25 Jun 2024 | [Foot Locker ABL amendment 4](https://www.sec.gov/Archives/edgar/data/850209/000143774924021177/ex_691205.htm) | June 20 executed amendment; collateral, springing covenant, control provisions |
| 14 Jan 2022 | [DICK'S supplemental indenture](https://www.sec.gov/Archives/edgar/data/1089063/000119312522009887/d285529dex42.htm) | Coupons, bullets, 30/360 and make-whole provisions |
| 5 Oct 2021 | [Foot Locker indenture](https://www.sec.gov/Archives/edgar/data/850209/000153949721001514/exh4-1_indenture.htm) | Coupon, 2029 maturity, redemption grid, control AND ratings trigger |
| 15 May 2025 | [Acquisition announcement](https://www.sec.gov/Archives/edgar/data/1089063/000119312525120243/d830209dex992.htm) | Price, election terms, headline values, management synergy guidance |
| 15 May 2025 | [Merger agreement](https://www.sec.gov/Archives/edgar/data/850209/000110465925049592/tm2515123d3_ex2-1.htm) | Sections 3.4, 4.2, 5.2, 7.16: awards, capitalization and debt treatment |
| 15 May 2025 | [DICK'S preliminary Q1 release](https://www.sec.gov/Archives/edgar/data/1089063/000119312525120243/d830209dex991.htm) | +4.5% comps; preliminary EPS, not complete closing balances |
| 15 May 2025 | [Foot Locker preliminary Q1 release](https://www.sec.gov/Archives/edgar/data/850209/000110465925048852/tm2515123d1_ex99-1.htm) | -2.6% comps; preliminary losses/impairments, not EBITDA |

The merger [filing index](https://www.sec.gov/Archives/edgar/data/850209/000110465925049592/0001104659-25-049592-index.html) records acceptance on 15 May at 17:16:25. This project uses an end-of-day cutoff, not an announcement-time cutoff. Full Q1 releases scheduled 28 May (DKS) and 29 May (FL), later 10-Qs, June S-4, July merger proxy, later notes exchanges and actual closing results are excluded from historical inputs.

## Access and applicability decisions

* **Awards:** the public agreement provides aggregate counts and legal treatment. The omitted Company Disclosure Letter, section 4.2, and equity-administration ledger are needed for individual strikes, director/employee RSU allocation and PSU settlement. The [April 10 annual proxy](https://www.sec.gov/Archives/edgar/data/850209/000110465925033769/tm2425908-3_def14a.htm) was found, but direct browser extraction returned an internal error on repeated attempts. Its earlier named-executive population would not alone resolve all employee awards. No claim from that inaccessible body was marked verified.
* **Target ABL:** merger section 7.16(a) calls for termination at closing. Retaining its 600 commitment as post-close liquidity is not an admissible default. A borrowing-base certificate is needed for interim borrowing availability, but not to assume post-close draws of zero. A funded payoff, LC replacement/cash collateral and collateral release remain material closing uses. The payoff letter is due shortly before future closing; its realized amount is unknowable at cutoff. Forecast an amount only from verified latest obligations and explicit sensitivities, never assert it existed.
* **Retained DICK'S notes:** no discretionary redemption means no redemption-date Treasury quote is needed for those notes. Refinancing them requires the contractual make-whole calculation, notices and assumed future rates. Neither debt principal nor coupon evidence becomes optional.
* **Target notes:** acquisition signing alone does not trigger the 101% offer. The indenture requires control and a ratings event. Optional redemption is 102% before 1 October 2025, 101% for the following year, then par, plus accrued interest. Retain/redemption routes must be modelled separately; no future consent is presumed.
* **Lease schedules and covenants:** aggregate lease cash payments do not supply instrument principal amortisation. DICK'S contractual lease-adjusted debt/EBITDAR cannot be substituted with the simulator's analytical net-debt/EBITDA screen. Compliance certificates, full lease schedules, covenant calculations and scenario-specific legal review remain needed. These include mapping limitations as well as evidence gaps; software completion of the synthetic engine does not establish them.
* **Cash and commitments:** treasury cash-by-entity schedules, encumbrances/repatriation rights and binding payment timing are needed. The DICK'S 10-K discloses about 180 of non-cancellable purchase commitments, but does not give enough timing to allocate all cash obligations. Future zero discretionary distributions do not cancel declared obligations.
* **Official market data:** the [New York Fed SOFR page](https://www.newyorkfed.org/markets/reference-rates/sofr) and its date-filtered API were examined; the API was unavailable through the browser tool. [FRED's current SOFR table](https://fred.stlouisfed.org/data/SOFR) shows 4.29% for 14 May 2025, but a cutoff-vintage observation was not established. It is retained here as an unverified historical-vintage candidate, not fed to the gate/model. May 15 effective SOFR would ordinarily publish after cutoff. A timestamped NY Fed release or ALFRED vintage as of May 15 would resolve this. Hypothetical future benchmark scenarios need no claim that a historical market quote was verified.

No original blocking requirement was marked not applicable merely to obtain a recommendation. Conditional dependencies are documented above and per row. No unresolved contradictory disclosures were converted into a selected fact; presentation differences such as debt carrying value versus principal, or lease liabilities excluding held-for-sale amounts, are reconciled rather than called conflicts.

## Assumptions, sensitivity and remaining work

The six assumption groups are stored independently in the historical case. They include future operating paths, a projected seasonal closing bridge (superseding the initial frozen diagnostic), zero discretionary distributions, screening thresholds, hypothetical financing/fees and synergy timing/costs. None is claimed as realized history. The strict mapping remains blocked; the separate public case uses the projected bridge, distribution policy and cash-access assumptions documented in PUBLIC_CASE_REVIEW.md.

The partial studies calculate 90 operating points (two companies, three growth paths, three margin shifts, five years) and 24 funding-unit/synergy cases. Growth is 0/-5/-10% annually and EBITDA margin shifts are 0/-100/-200bp. New debt is a hypothetical 1000 unit, benchmark 4.5% +/-200bp, spread 250bp plus 0/100/200bp, fees 1/2/3%. Synergy run rates 0/100/125 vary delay by one year and integration costs by 1x/2x. These are sensitivity illustrations, not forecasts calibrated to preliminary comps or actual financing findings.

Full company-specific sources/uses, five-year debt/liquidity projections, debt capacity and liquidity reverse stress **remain unavailable** because their material dependencies are unresolved. They are not reported as zero and no synthetic values fill them. The synthetic model's full scenario/solver/stress suite remains independent.

Reproduce from the original review using `python scripts/build_historical_register.py` followed by `python scripts/resolve_historical.py`. Run `python -m financing data/historical.json --output historical-output --database historical-output/model.sqlite --excel --pdf`; expected exit is 2 while blocked. Regenerate demo outputs separately using `--demo`. SQLite stores the review even when no complete historical model runs.

Engineering and regression verification are reported in VERIFICATION.md. GitHub publication remains **not performed**.

## Subsequent public-information amendment

The original strict review above is preserved as the earlier assessment. Five additional disclosures bring the register to 83 reported facts and 24 supporting disclosure keys, in 16 extract archives from twelve primary documents. PUBLIC_CASE_REVIEW.md and public-output/public-gap-assessment.json document all 23 remaining requirements. Public conditional schedules and analytical capacity now exist; complete transaction uses, legal compliance and an overall company-specific financing preference remain blocked. Earlier statements of unavailable full financing refer to the strict assessment.
