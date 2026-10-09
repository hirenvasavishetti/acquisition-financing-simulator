# Acquisition financing evidence review

Blocked — insufficient verified evidence.

No preferred financing structure is named for DICK'S Sporting Goods / Foot Locker.

Historical forecasts and preferences require verified material evidence and a reconciled historical model mapping. Synthetic engineering is independent.

## Evidence gaps and resolutions

## Supported historical calculations

Unavailable: complete funding uses, eligible cash, instrument schedules and contractual borrowing capacity remain unresolved.

- **acquirer FY2024 simple operating EBITDA**: 1874.341 USD millions. Operating profit + cash-flow D&A. Not adjusted EBITDA or covenant EBITDAR; no addbacks. Dependencies: acquirer.FY2024.operating_profit, acquirer.FY2024.depreciation_amortisation.
- **acquirer FY2024 CFO less gross capex**: 509.27 USD millions. CFO - gross cash capital expenditures. Historical residual, not forecast cash available for debt service; CFO includes interest/taxes and lease payments. Dependencies: acquirer.FY2024.operating_cash_flow, acquirer.FY2024.capex.
- **acquirer FY2024 selected operating NWC**: 2066.337 USD millions. Inventory + receivables - payables. Selected working capital only, not total current assets minus liabilities. Dependencies: acquirer.FY2024.inventory, acquirer.FY2024.receivables, acquirer.FY2024.payables.
- **acquirer Q4 CFO less gross capex**: 394.5319999999999 USD millions. (FY CFO - 39wk CFO) - (FY capex - 39wk capex). Derived 13 weeks Nov 3 2024-Feb 1 2025; demonstrates seasonality, not a forecast seed. Dependencies: acquirer.FY2024.operating_cash_flow, acquirer.FY2024.capex, detail.acquirer.ytd_cash_flow.
- **target FY2024 simple operating EBITDA**: 305.0 USD millions. Operating profit + cash-flow D&A. Not adjusted EBITDA or covenant EBITDAR; no addbacks. Dependencies: target.FY2024.operating_profit, target.FY2024.depreciation_amortisation.
- **target FY2024 CFO less gross capex**: 105.0 USD millions. CFO - gross cash capital expenditures. Historical residual, not forecast cash available for debt service; CFO includes interest/taxes and lease payments. Dependencies: target.FY2024.operating_cash_flow, target.FY2024.capex.
- **target FY2024 selected operating NWC**: 1303.0 USD millions. Inventory + receivables - payables. Selected working capital only, not total current assets minus liabilities. Dependencies: target.FY2024.inventory, target.FY2024.receivables, target.FY2024.payables.
- **target Q4 CFO less gross capex**: 192.0 USD millions. (FY CFO - 39wk CFO) - (FY capex - 39wk capex). Derived 13 weeks Nov 3 2024-Feb 1 2025; demonstrates seasonality, not a forecast seed. Dependencies: target.FY2024.operating_cash_flow, target.FY2024.capex, detail.target.ytd_cash_flow.
- **FL cash reconciliation**: 0.0 USD millions. 401 + 4 + 25 - 430 = 0. Accounting reconciliation; no legal cash-release conclusion. Dependencies: detail.target.cash, detail.target.restricted_cash.
- **FL financial debt principal**: 450.0 USD millions. Notes principal + finance-lease liability. Operating lease liabilities excluded; not complete instrument-level payment schedule. Dependencies: detail.target.notes_principal, detail.target.finance_lease.
- **FL finance-lease rollforward check**: 0.0 USD millions. Opening + additions - (cash paid - interest) - closing. Aggregate liability check; cannot infer each future instrument principal payment. Dependencies: detail.target.leases, detail.target.finance_lease.
- **Common shares all-cash consideration**: 2293.453968 USD millions. May 12 outstanding common shares x $24 / 1e6. Common shares only: excludes awards, fees, debt, closing share changes and fractional-share payments. Dependencies: detail.transaction.capitalization, transaction.cash_price.
- **Common shares all-stock issuance**: 11.1614759776 million DKS shares. May 12 outstanding common shares x 0.1168 / 1e6. Election endpoint only, not predicted elections; excludes awards and fractional-share cash. Dependencies: detail.transaction.capitalization, transaction.exchange_ratio.
- **DKS note annual coupon obligation**: 54.375 USD millions. 750 x 3.15% + 750 x 4.10%. Original fixed notes only; no revolver, lease interest or refinancing. Dependencies: detail.acquirer.notes, detail.acquirer.notes_outstanding.
- **FL note annual coupon obligation**: 16.0 USD millions. 400 x 4%. Retained-note contractual coupon only; not total cash interest. Dependencies: detail.target.notes_principal, detail.target.notes_terms.

## Review of the original 36 material gaps

The six future choices are analyst assumptions, not additional verified historical facts. Operating sensitivities test annual growth 0/-5/-10% and EBITDA margin changes 0/-100/-200bp over five years. Unit financing and synergy sensitivities follow; complete debt capacity and liquidity reverse stress remain unavailable.

- Annual coupon per hypothetical 1000 new debt: Benchmark shift -2.00%; spread shift +0.00% => 50.000 USD millions/year. Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.
- Annual coupon per hypothetical 1000 new debt: Benchmark shift -2.00%; spread shift +1.00% => 60.000 USD millions/year. Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.
- Annual coupon per hypothetical 1000 new debt: Benchmark shift -2.00%; spread shift +2.00% => 70.000 USD millions/year. Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.
- Annual coupon per hypothetical 1000 new debt: Benchmark shift +0.00%; spread shift +0.00% => 70.000 USD millions/year. Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.
- Annual coupon per hypothetical 1000 new debt: Benchmark shift +0.00%; spread shift +1.00% => 80.000 USD millions/year. Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.
- Annual coupon per hypothetical 1000 new debt: Benchmark shift +0.00%; spread shift +2.00% => 90.000 USD millions/year. Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.
- Annual coupon per hypothetical 1000 new debt: Benchmark shift +2.00%; spread shift +0.00% => 90.000 USD millions/year. Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.
- Annual coupon per hypothetical 1000 new debt: Benchmark shift +2.00%; spread shift +1.00% => 100.000 USD millions/year. Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.
- Annual coupon per hypothetical 1000 new debt: Benchmark shift +2.00%; spread shift +2.00% => 110.000 USD millions/year. Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.
- Gross borrowing to net hypothetical 1000 proceeds: Upfront fee 1% => 1010.101 USD millions. 1000 is a unit scenario, not historical acquisition funding.
- Gross borrowing to net hypothetical 1000 proceeds: Upfront fee 2% => 1020.408 USD millions. 1000 is a unit scenario, not historical acquisition funding.
- Gross borrowing to net hypothetical 1000 proceeds: Upfront fee 3% => 1030.928 USD millions. 1000 is a unit scenario, not historical acquisition funding.
- Five-year cumulative synergy less integration costs: Run rate 0.0; delay 0yr; cost multiplier 1.0 => -175.000 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 0.0; delay 0yr; cost multiplier 2.0 => -350.000 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 0.0; delay 1yr; cost multiplier 1.0 => -175.000 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 0.0; delay 1yr; cost multiplier 2.0 => -350.000 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 100.0; delay 0yr; cost multiplier 1.0 => 175.000 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 100.0; delay 0yr; cost multiplier 2.0 => 0.000 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 100.0; delay 1yr; cost multiplier 1.0 => 75.000 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 100.0; delay 1yr; cost multiplier 2.0 => -100.000 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 125.0; delay 0yr; cost multiplier 1.0 => 262.500 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 125.0; delay 0yr; cost multiplier 2.0 => 87.500 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 125.0; delay 1yr; cost multiplier 1.0 => 137.500 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
- Five-year cumulative synergy less integration costs: Run rate 125.0; delay 1yr; cost multiplier 2.0 => -37.500 USD millions, pre-tax. Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.
### transaction.share_and_award_treatment — Remaining
historical fact; missing evidence. Affects: Consideration bridge, cash uses, stock issuance and synergy scenarios. Material because: Material transaction or unregistered model dependency: unsupported consideration or scope can change financing needs.
Current evidence: May 12 common shares 95,560,582; options/RSUs/PSUs/DSUs counts and different settlement rules archived.
Missing: Individual option strikes, director versus employee RSU split, PSU performance/award agreement settlement and award tax/withholding cash. Weighted-average strike cannot prove all options out of money.
Applicability: Required for all complete funding structures.
Resolve: Merger Sections 3.4/4.2; omitted Company Disclosure Letter 4.2 and equity-administration ledger. April 10 proxy is an earlier, incomplete employee population; later merger proxy excluded. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000110465925049592/tm2515123d3_ex2-1.htm

### acquirer.opening.unrestricted_cash — Remaining
historical fact; missing evidence. Affects: Opening liquidity, retained debt, cash deployment and leverage. Material because: Opening liquidity and debt determine spendable cash, financing need and net leverage; a wrong balance can falsely imply funding.
Current evidence: Feb 1 cash and equivalents: DKS 1689.940; FL 401, with separately restricted 29. Accounting balances are verified separately.
Missing: Entity-level encumbrances, trapped/repatriable cash, minimum operating balances, and legally available cash at the selected closing date.
Applicability: Cash-first consumes availability. A zero contribution removes acquisition use, but group liquidity still cannot count restricted or inaccessible balances. No waiver applied.
Resolve: Treasury cash-by-entity/restriction schedule, credit security documents and counsel review; prospective cash bridge must remain a forecast. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.opening.cash_restrictions — Remaining
historical fact; missing evidence. Affects: Opening liquidity, retained debt, cash deployment and leverage. Material because: Opening liquidity and debt determine spendable cash, financing need and net leverage; a wrong balance can falsely imply funding.
Current evidence: Feb 1 cash and equivalents: DKS 1689.940; FL 401, with separately restricted 29. Accounting balances are verified separately.
Missing: Entity-level encumbrances, trapped/repatriable cash, minimum operating balances, and legally available cash at the selected closing date.
Applicability: Cash-first consumes availability. A zero contribution removes acquisition use, but group liquidity still cannot count restricted or inaccessible balances. No waiver applied.
Resolve: Treasury cash-by-entity/restriction schedule, credit security documents and counsel review; prospective cash bridge must remain a forecast. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.opening.debt_principal — Remaining
historical fact; missing evidence. Affects: Opening liquidity, retained debt, cash deployment and leverage. Material because: Opening liquidity and debt determine spendable cash, financing need and net leverage; a wrong balance can falsely imply funding.
Current evidence: DKS notes 750+750; FL notes 400 and finance-lease liability 50. Carrying amounts are separate.
Missing: DKS complete principal-to-balance-sheet reconciliation including any finance leases; no zero inferred from zero annual finance-lease payment.
Applicability: Required for all complete funding structures.
Resolve: Debt Note 9 / Note 13 and lease liability ledger; exclude operating leases from financial-debt principal. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.FY2024.ebitda_reconciliation — Resolved
historical fact; verified fact. Affects: Operating forecast, EBITDA, working capital and debt-service cash flow. Material because: Latest standalone operating base drives forecast EBITDA, cash taxes, working capital and cash available for debt service.
Current evidence: Computed from verified FY2024 operating profit plus disclosed cash-flow D&A. No exceptional-item addbacks.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required for all complete funding structures.
Resolve: Code-owned sum with dependency checks. This resolves simple operating EBITDA, not covenant EBITDAR. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.FY2024.lease_reconciliation — Remaining
historical fact; missing evidence. Affects: Operating forecast, EBITDA, working capital and debt-service cash flow. Material because: Latest standalone operating base drives forecast EBITDA, cash taxes, working capital and cash available for debt service.
Current evidence: Rent cost components, fixed lease cash, operating liabilities, uncommenced commitments and FL finance cash are separately archived.
Missing: Cash timing for variable/short-term rent, subleases and complete instrument finance-lease interest/principal schedules; reconcile held-for-sale treatment.
Applicability: Required for all complete funding structures.
Resolve: Lease Note 7 (DKS) / 16 (FL), lease payment ledger and explicit future rent assumptions. FL liability includes 5 held for sale outside main table. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.FY2024.dividends_buybacks_commitments — Remaining
historical fact; missing evidence. Affects: Operating forecast, EBITDA, working capital and debt-service cash flow. Material because: Contractual capital commitments can compete with debt service; discretionary future distributions are separate explicit assumptions.
Current evidence: Cash-flow historical distributions and lease commitments disclosed; future discretionary distributions set to zero only as a scenario assumption. MD&A p36 discloses approximately 180 of non-cancellable purchase commitments, but not their annual cash timing.
Missing: Reconciliation of declared/unpaid distributions and binding capex, purchase and lease commitments affecting the closing bridge and forecast.
Applicability: Required for all complete funding structures.
Resolve: Annual cash-flow statement, commitments notes, pre-cutoff dividend declarations, treasury payable and capital-commitment schedules. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.debt.instrument_inventory — Remaining
conditionally applicable requirement; missing evidence. Affects: Completeness of instrument debt schedule. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: Bond series and aggregate lease liabilities disclosed; supplemental disclosures are not a complete executable instrument inventory.
Missing: Complete lease/other borrowing register with principal, maturity, coupon, repayment and close treatment reconciled to debt notes.
Applicability: Required for all complete funding structures.
Resolve: Annual debt and lease notes, treasury debt ledger and all material financing leases. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.debt.maturity_and_amortisation_schedule — Remaining
conditionally applicable requirement; missing evidence. Affects: Mandatory repayments and maturity gaps. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS bullets Jan 15 2032/2052; FL note Oct 1 2029; annual aggregate lease payments disclosed.
Missing: Finance-lease principal versus interest allocation and instrument-level remaining payment dates; relative model maturity must use assumed closing date.
Applicability: Required for all complete funding structures.
Resolve: Original indentures plus lease amortisation ledger. Aggregate future minimum payments are not all principal. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.debt.coupons_and_resets — Remaining
conditionally applicable requirement; missing evidence. Affects: Cash interest and rate stress. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: Fixed note coupons 3.15%/4.10% DKS and 4% FL; DKS SOFR margin 112.5bp at year-end, FL term-SOFR grid 150-200bp.
Missing: Instrument lease effective interest schedules, applicable future facility pricing-grid/rating assumptions and resets.
Applicability: Required for all complete funding structures.
Resolve: Indentures and credit agreements plus lease ledger. Weighted-average lease discount rate is not each instrument coupon. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.debt.change_of_control — Remaining
conditionally applicable requirement; missing evidence. Affects: Required repayment and retained debt. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: FL ABL termination required at closing. FL note offer 101% requires control AND ratings event. DKS purchase of target does not itself establish DKS control change.
Missing: Facility and lease consent/default application, notes ratings-event assessment and exact retained versus redeemed treatment.
Applicability: Required for all complete funding structures.
Resolve: Merger 7.16, indenture definitions/4.10, ABL 8.01 and lease contracts; scenario-specific legal review. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000110465925049592/tm2515123d3_ex2-1.htm

### acquirer.debt.refinancing_and_repricing — Remaining
conditionally applicable requirement; missing evidence. Affects: Refinancing dependence and debt service. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS pre-par make-whole; FL redemption 102% before Oct 1 2025, 101% until Oct 1 2026, then par, plus accrued interest.
Missing: Scenario treatment for each instrument, accrued interest, notice timing and any lease termination/consent costs; actual future refinancing is not guaranteed.
Applicability: Retain versus redeem changes required calculations. Refinancing coupon/fees are future assumptions; existing call premium/consent rights remain historical facts. No waiver applied.
Resolve: Original indenture redemption sections and prospective quote sensitivities. Retained DKS notes with no optional redemption do not require a make-whole quote. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000119312522009887/d285529dex42.htm

### acquirer.debt.revolver_commitments — Resolved
conditionally applicable requirement; verified fact. Affects: Eligible committed liquidity. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS unsecured 1600, Jan 14 2027; FL secured 600, June 20 2029. Both zero drawn at fiscal year-end. Uncommitted accordions excluded.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required for all complete funding structures.
Resolve: Annual debt notes verify contractual size and dates; does not resolve borrowing eligibility. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.debt.borrowing_base_and_letters_of_credit — Resolved
conditionally applicable requirement; verified fact. Affects: Revolver draw limits. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS LC 19.9 against unsecured 1600; FL LC 7 against 600 commitment, subject to eligible inventory/reserves.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Target ABL is terminated under merger 7.16(a); no post-close availability counted. Certificate matters for interim liquidity; funded payoff and LC replacement still matter for closing uses. No blanket waiver.
Resolve: DKS Note 9; FL ABL borrowing-base certificate under agreement reporting provisions, held by Wells Fargo/borrower treasury. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm

### acquirer.debt.covenants_and_restricted_payments — Remaining
conditionally applicable requirement; missing evidence. Affects: Borrowing eligibility and capital allocation. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS lease-adjusted maximum 3.75x; conditional acquisition election 4.25x. FL springing FCCR 1.00x plus restricted-payment conditions.
Missing: Contractual numerator/denominator reconciliation, permitted debt and lien baskets, payment-condition capacity and post-acquisition eligibility.
Applicability: Required for all complete funding structures.
Resolve: Executed agreements and latest compliance certificates; counsel interpretation. Generic net-debt/EBITDA engine thresholds do not implement these covenants. Primary source: https://www.sec.gov/Archives/edgar/data/1089063/000119312522009887/d285529dex101.htm

### target.opening.unrestricted_cash — Remaining
historical fact; missing evidence. Affects: Opening liquidity, retained debt, cash deployment and leverage. Material because: Opening liquidity and debt determine spendable cash, financing need and net leverage; a wrong balance can falsely imply funding.
Current evidence: Feb 1 cash and equivalents: DKS 1689.940; FL 401, with separately restricted 29. Accounting balances are verified separately.
Missing: Entity-level encumbrances, trapped/repatriable cash, minimum operating balances, and legally available cash at the selected closing date.
Applicability: Cash-first consumes availability. A zero contribution removes acquisition use, but group liquidity still cannot count restricted or inaccessible balances. No waiver applied.
Resolve: Treasury cash-by-entity/restriction schedule, credit security documents and counsel review; prospective cash bridge must remain a forecast. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.opening.cash_restrictions — Remaining
historical fact; missing evidence. Affects: Opening liquidity, retained debt, cash deployment and leverage. Material because: Opening liquidity and debt determine spendable cash, financing need and net leverage; a wrong balance can falsely imply funding.
Current evidence: Feb 1 cash and equivalents: DKS 1689.940; FL 401, with separately restricted 29. Accounting balances are verified separately.
Missing: Entity-level encumbrances, trapped/repatriable cash, minimum operating balances, and legally available cash at the selected closing date.
Applicability: Cash-first consumes availability. A zero contribution removes acquisition use, but group liquidity still cannot count restricted or inaccessible balances. No waiver applied.
Resolve: Treasury cash-by-entity/restriction schedule, credit security documents and counsel review; prospective cash bridge must remain a forecast. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.opening.debt_principal — Resolved
historical fact; verified fact. Affects: Opening liquidity, retained debt, cash deployment and leverage. Material because: Opening liquidity and debt determine spendable cash, financing need and net leverage; a wrong balance can falsely imply funding.
Current evidence: DKS notes 750+750; FL notes 400 and finance-lease liability 50. Carrying amounts are separate.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required for all complete funding structures.
Resolve: Debt Note 9 / Note 13 and lease liability ledger; exclude operating leases from financial-debt principal. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.FY2024.ebitda_reconciliation — Resolved
historical fact; verified fact. Affects: Operating forecast, EBITDA, working capital and debt-service cash flow. Material because: Latest standalone operating base drives forecast EBITDA, cash taxes, working capital and cash available for debt service.
Current evidence: Computed from verified FY2024 operating profit plus disclosed cash-flow D&A. No exceptional-item addbacks.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required for all complete funding structures.
Resolve: Code-owned sum with dependency checks. This resolves simple operating EBITDA, not covenant EBITDAR. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.FY2024.receivables — Resolved
historical fact; verified fact. Affects: Operating forecast, EBITDA, working capital and debt-service cash flow. Material because: Latest standalone operating base drives forecast EBITDA, cash taxes, working capital and cash available for debt service.
Current evidence: FL Note 8 p54: net receivables 156 at Feb 1, 2025; 160 comparative.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required for all complete funding structures.
Resolve: Exact units/date reviewed; feeds selected operating NWC, not all current assets. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.FY2024.lease_reconciliation — Remaining
historical fact; missing evidence. Affects: Operating forecast, EBITDA, working capital and debt-service cash flow. Material because: Latest standalone operating base drives forecast EBITDA, cash taxes, working capital and cash available for debt service.
Current evidence: Rent cost components, fixed lease cash, operating liabilities, uncommenced commitments and FL finance cash are separately archived.
Missing: Cash timing for variable/short-term rent, subleases and complete instrument finance-lease interest/principal schedules; reconcile held-for-sale treatment.
Applicability: Required for all complete funding structures.
Resolve: Lease Note 7 (DKS) / 16 (FL), lease payment ledger and explicit future rent assumptions. FL liability includes 5 held for sale outside main table. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.FY2024.dividends_buybacks_commitments — Remaining
historical fact; missing evidence. Affects: Operating forecast, EBITDA, working capital and debt-service cash flow. Material because: Contractual capital commitments can compete with debt service; discretionary future distributions are separate explicit assumptions.
Current evidence: Cash-flow historical distributions and lease commitments disclosed; future discretionary distributions set to zero only as a scenario assumption.
Missing: Reconciliation of declared/unpaid distributions and binding capex, purchase and lease commitments affecting the closing bridge and forecast.
Applicability: Required for all complete funding structures.
Resolve: Annual cash-flow statement, commitments notes, pre-cutoff dividend declarations, treasury payable and capital-commitment schedules. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.debt.instrument_inventory — Remaining
conditionally applicable requirement; missing evidence. Affects: Completeness of instrument debt schedule. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: Bond series and aggregate lease liabilities disclosed; supplemental disclosures are not a complete executable instrument inventory.
Missing: Complete lease/other borrowing register with principal, maturity, coupon, repayment and close treatment reconciled to debt notes.
Applicability: Required for all complete funding structures.
Resolve: Annual debt and lease notes, treasury debt ledger and all material financing leases. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.debt.maturity_and_amortisation_schedule — Remaining
conditionally applicable requirement; missing evidence. Affects: Mandatory repayments and maturity gaps. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS bullets Jan 15 2032/2052; FL note Oct 1 2029; annual aggregate lease payments disclosed.
Missing: Finance-lease principal versus interest allocation and instrument-level remaining payment dates; relative model maturity must use assumed closing date.
Applicability: Required for all complete funding structures.
Resolve: Original indentures plus lease amortisation ledger. Aggregate future minimum payments are not all principal. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.debt.coupons_and_resets — Remaining
conditionally applicable requirement; missing evidence. Affects: Cash interest and rate stress. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: Fixed note coupons 3.15%/4.10% DKS and 4% FL; DKS SOFR margin 112.5bp at year-end, FL term-SOFR grid 150-200bp.
Missing: Instrument lease effective interest schedules, applicable future facility pricing-grid/rating assumptions and resets.
Applicability: Required for all complete funding structures.
Resolve: Indentures and credit agreements plus lease ledger. Weighted-average lease discount rate is not each instrument coupon. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.debt.change_of_control — Remaining
conditionally applicable requirement; missing evidence. Affects: Required repayment and retained debt. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: FL ABL termination required at closing. FL note offer 101% requires control AND ratings event. DKS purchase of target does not itself establish DKS control change.
Missing: Facility and lease consent/default application, notes ratings-event assessment and exact retained versus redeemed treatment.
Applicability: Required for all complete funding structures.
Resolve: Merger 7.16, indenture definitions/4.10, ABL 8.01 and lease contracts; scenario-specific legal review. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000110465925049592/tm2515123d3_ex2-1.htm

### target.debt.refinancing_and_repricing — Remaining
conditionally applicable requirement; missing evidence. Affects: Refinancing dependence and debt service. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS pre-par make-whole; FL redemption 102% before Oct 1 2025, 101% until Oct 1 2026, then par, plus accrued interest.
Missing: Scenario treatment for each instrument, accrued interest, notice timing and any lease termination/consent costs; actual future refinancing is not guaranteed.
Applicability: Retain versus redeem changes required calculations. Refinancing coupon/fees are future assumptions; existing call premium/consent rights remain historical facts. No waiver applied.
Resolve: Original indenture redemption sections and prospective quote sensitivities. Retained DKS notes with no optional redemption do not require a make-whole quote. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000153949721001514/exh4-1_indenture.htm

### target.debt.revolver_commitments — Resolved
conditionally applicable requirement; verified fact. Affects: Eligible committed liquidity. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS unsecured 1600, Jan 14 2027; FL secured 600, June 20 2029. Both zero drawn at fiscal year-end. Uncommitted accordions excluded.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required for all complete funding structures.
Resolve: Annual debt notes verify contractual size and dates; does not resolve borrowing eligibility. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.debt.borrowing_base_and_letters_of_credit — Remaining
conditionally applicable requirement; missing evidence. Affects: Revolver draw limits. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS LC 19.9 against unsecured 1600; FL LC 7 against 600 commitment, subject to eligible inventory/reserves.
Missing: Latest certified eligible collateral, reserves and LC replacement/cash-collateral terms.
Applicability: Target ABL is terminated under merger 7.16(a); no post-close availability counted. Certificate matters for interim liquidity; funded payoff and LC replacement still matter for closing uses. No blanket waiver.
Resolve: DKS Note 9; FL ABL borrowing-base certificate under agreement reporting provisions, held by Wells Fargo/borrower treasury. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm

### target.debt.covenants_and_restricted_payments — Remaining
conditionally applicable requirement; missing evidence. Affects: Borrowing eligibility and capital allocation. Material because: Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.
Current evidence: DKS lease-adjusted maximum 3.75x; conditional acquisition election 4.25x. FL springing FCCR 1.00x plus restricted-payment conditions.
Missing: Contractual numerator/denominator reconciliation, permitted debt and lien baskets, payment-condition capacity and post-acquisition eligibility.
Applicability: Required for all complete funding structures.
Resolve: Executed agreements and latest compliance certificates; counsel interpretation. Generic net-debt/EBITDA engine thresholds do not implement these covenants. Primary source: https://www.sec.gov/Archives/edgar/data/850209/000143774924021177/ex_691205.htm

### assumption.closing_bridge — Resolved
future modelling assumption; explicit modelling assumption. Affects: Forecast, liquidity and scenario comparisons. Material because: Future choice controls forecast or funding mechanics; explicit rationale is required, but it is not a historical fact.
Current evidence: Projected 39-week closing bridge calibrated to verified FY2024 seasonality; not actual FY2025 interim balances. Lease principal must also map to the debt inventory. Public case applies separate cash-access assumptions. Supersedes frozen-balance diagnostic.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required when running the full prospective model. Partial studies disclose only the assumptions they consume.
Resolve: Explicit prospective choice; test uncertainty. Does not replace missing historical balance, rights or obligations. Primary source: Analyst assumption register

### assumption.operating_forecast — Resolved
future modelling assumption; explicit modelling assumption. Affects: Forecast, liquidity and scenario comparisons. Material because: Future choice controls forecast or funding mechanics; explicit rationale is required, but it is not a historical fact.
Current evidence: Explicit future cost decomposition and growth paths, not reported margins. Calibrate fixed expenses to verified operating EBITDA. Stress revenue and EBITDA margin; preliminary target Q1 deterioration makes flat extrapolation unreliable.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required when running the full prospective model. Partial studies disclose only the assumptions they consume.
Resolve: Explicit prospective choice; test uncertainty. Does not replace missing historical balance, rights or obligations. Primary source: Analyst assumption register

### assumption.synergy_delivery_and_costs — Resolved
future modelling assumption; explicit modelling assumption. Affects: Forecast, liquidity and scenario comparisons. Material because: Future choice controls forecast or funding mechanics; explicit rationale is required, but it is not a historical fact.
Current evidence: Future delivery/cost choices, not management cost guidance. Test run rates 0/100/125, one-year delay and doubled integration costs.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required when running the full prospective model. Partial studies disclose only the assumptions they consume.
Resolve: Explicit prospective choice; test uncertainty. Does not replace missing historical balance, rights or obligations. Primary source: Analyst assumption register

### assumption.financing_terms_and_fees — Resolved
future modelling assumption; explicit modelling assumption. Affects: Forecast, liquidity and scenario comparisons. Material because: Future choice controls forecast or funding mechanics; explicit rationale is required, but it is not a historical fact.
Current evidence: Hypothetical future quote: 4.5% benchmark plus 250bp, 2% upfront, 75 transaction costs, stock reference 200. No claim these are committed financing or observed prices. Test rates +/-200bp, spreads +100/+200bp, fees 1/2/3%; historical redemption costs remain separate.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required when running the full prospective model. Partial studies disclose only the assumptions they consume.
Resolve: Explicit prospective choice; test uncertainty. Does not replace missing historical balance, rights or obligations. Primary source: Analyst assumption register

### assumption.analytical_thresholds — Resolved
future modelling assumption; explicit modelling assumption. Affects: Forecast, liquidity and scenario comparisons. Material because: Future choice controls forecast or funding mechanics; explicit rationale is required, but it is not a historical fact.
Current evidence: Analyst screening limits, not lender covenants or verified tax deductibility; test cash floors 500/750/1000 and leverage 2/3/4.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required when running the full prospective model. Partial studies disclose only the assumptions they consume.
Resolve: Explicit prospective choice; test uncertainty. Does not replace missing historical balance, rights or obligations. Primary source: Analyst assumption register

### assumption.capital_allocation — Resolved
future modelling assumption; explicit modelling assumption. Affects: Forecast, liquidity and scenario comparisons. Material because: Future choice controls forecast or funding mechanics; explicit rationale is required, but it is not a historical fact.
Current evidence: Prospective suspension of discretionary distributions and optional repayments. Existing declared obligations remain separate missing facts, not zeroed.
Missing: None for this narrowly defined input; related financing dependencies remain separate.
Applicability: Required when running the full prospective model. Partial studies disclose only the assumptions they consume.
Resolve: Explicit prospective choice; test uncertainty. Does not replace missing historical balance, rights or obligations. Primary source: Analyst assumption register

- **acquirer.FY2022.dividends_buybacks_commitments — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2022.ebitda_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2022.inventory — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2022.lease_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2022.payables — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2022.receivables — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2023.dividends_buybacks_commitments — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2023.ebitda_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2023.lease_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2024.dividends_buybacks_commitments — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.FY2024.lease_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **acquirer.debt.change_of_control — missing evidence**: Required observation absent. Affected calculations: Required repayment and retained debt. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **acquirer.debt.coupons_and_resets — missing evidence**: Required observation absent. Affected calculations: Cash interest and rate stress. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **acquirer.debt.covenants_and_restricted_payments — missing evidence**: Required observation absent. Affected calculations: Borrowing eligibility and capital allocation. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **acquirer.debt.instrument_inventory — missing evidence**: Required observation absent. Affected calculations: Completeness of instrument debt schedule. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **acquirer.debt.maturity_and_amortisation_schedule — missing evidence**: Required observation absent. Affected calculations: Mandatory repayments and maturity gaps. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **acquirer.debt.refinancing_and_repricing — missing evidence**: Required observation absent. Affected calculations: Refinancing dependence and debt service. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **acquirer.opening.cash_restrictions — missing evidence**: Required observation absent. Affected calculations: Opening liquidity, retained debt, cash deployment and leverage. Resolution: Reconcile latest pre-cutoff balance sheet and notes, with balance date and units.
- **acquirer.opening.debt_principal — missing evidence**: Required observation absent. Affected calculations: Opening liquidity, retained debt, cash deployment and leverage. Resolution: Reconcile latest pre-cutoff balance sheet and notes, with balance date and units.
- **acquirer.opening.unrestricted_cash — missing evidence**: Required observation absent. Affected calculations: Opening liquidity, retained debt, cash deployment and leverage. Resolution: Reconcile latest pre-cutoff balance sheet and notes, with balance date and units.
- **target.FY2022.dividends_buybacks_commitments — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2022.ebitda_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2022.inventory — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2022.lease_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2022.payables — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2022.receivables — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2023.dividends_buybacks_commitments — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2023.ebitda_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2023.lease_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2024.dividends_buybacks_commitments — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.FY2024.lease_reconciliation — missing evidence**: Required observation absent. Affected calculations: Operating forecast, EBITDA, working capital and debt-service cash flow. Resolution: Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.
- **target.debt.borrowing_base_and_letters_of_credit — missing evidence**: Required observation absent. Affected calculations: Revolver draw limits. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **target.debt.change_of_control — missing evidence**: Required observation absent. Affected calculations: Required repayment and retained debt. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **target.debt.coupons_and_resets — missing evidence**: Required observation absent. Affected calculations: Cash interest and rate stress. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **target.debt.covenants_and_restricted_payments — missing evidence**: Required observation absent. Affected calculations: Borrowing eligibility and capital allocation. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **target.debt.instrument_inventory — missing evidence**: Required observation absent. Affected calculations: Completeness of instrument debt schedule. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **target.debt.maturity_and_amortisation_schedule — missing evidence**: Required observation absent. Affected calculations: Mandatory repayments and maturity gaps. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **target.debt.refinancing_and_repricing — missing evidence**: Required observation absent. Affected calculations: Refinancing dependence and debt service. Resolution: Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.
- **target.opening.cash_restrictions — missing evidence**: Required observation absent. Affected calculations: Opening liquidity, retained debt, cash deployment and leverage. Resolution: Reconcile latest pre-cutoff balance sheet and notes, with balance date and units.
- **target.opening.unrestricted_cash — missing evidence**: Required observation absent. Affected calculations: Opening liquidity, retained debt, cash deployment and leverage. Resolution: Reconcile latest pre-cutoff balance sheet and notes, with balance date and units.
- **transaction.share_and_award_treatment — missing evidence**: Required observation absent. Affected calculations: Consideration bridge, cash uses, stock issuance and synergy scenarios. Resolution: Review pre-cutoff announcement/merger agreement; record exact term and section.

## Illustrative scenarios

Illustrative scenario analysis — anonymous synthetic companies; not historical results.

- Cash-first: opening cash 750.00; opening debt 2670.10 (USD millions).
- Liquidity-first: opening cash 1620.00; opening debt 3553.35 (USD millions).
- Mixed consideration: opening cash 750.00; opening debt 1634.57 (USD millions).

## Conditional illustrative assessment

Mixed consideration is the only base structure passing all period constraints. It is conditional on accepting its dilution, cash policy and downside outcomes; severe stress may still fail.

The separate financing-memo.pdf is the two-page illustrative financing memo. The full workbook and JSON contain schedules, capacity, sensitivities and stress results.

This detailed evidence register supplements the financing memo; it is not an actual-company recommendation.
Snapshot: rerun after changing inputs or sources.
Input ID: 840bf1b8e85f7cb2618a20df2dc7295cde691a62416eef7c004df696fe056fe7
