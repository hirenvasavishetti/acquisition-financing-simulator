# Scope and conventions recorded before implementation

## Full simulator conventions (version 2, adopted before implementation)

The full simulator supersedes the foundation's limited numerical demo below.
All synthetic amounts are USD millions; share counts are millions of shares.
Periods are five full post-close model years starting at the illustrative
2025-11-01 close, not labelled company fiscal years. Original fiscal periods are
preserved in evidence records. Annual cash flows occur at year end; a separate
quarterly run uses four period-end settlements per model year and reports its
own annual aggregates. Differences between annual and quarterly financing costs
are timing effects, not forced reconciliation plugs.

- Equity = cash price times diluted eligible target shares and awards. Mixed
  election issues target shares times election fraction times exchange ratio;
  noncash value uses the explicit acquirer reference price. EV = equity plus
  target financial-debt principal less target cash plus explicit other EV items.
  Headline discrepancies are reported, never forced to zero. Debt carrying-value
  differences are reconciliations, not repayable principal.
- Closing bridges show latest balances, pre-close operating cash, capex,
  dividends, buybacks and instrument-specific pre-close debt repayment. Target
  cash is excluded from available liquidity unless the model explicitly documents
  availability; unavailable target cash is tracked separately, never spent.
- Existing financial debt includes finance leases, excludes operating lease
  liabilities, and retains each original coupon and maturity. Change-of-control
  repayment is an explicit instrument flag requiring evidence in historical mode.
  New acquisition debt and debt for refinancing/fees are reported separately.
- Financing fees are grossed up in the full-funding sources-and-uses calculation.
  Capacity keeps those uses and the cash contribution FIXED, treats the resulting
  financing fee as a fixed conservative budget, and substitutes acquisition debt
  for separately labelled analytical equity. Analytical equity is unrelated to
  transaction stock elections. No borrowing beyond eligible cash consideration.
- Company forecasts use level revenue shocks versus the base, gross margin
  before rent, variable costs, fixed costs, cash rent and depreciation. EBITDA is
  after rent and before D&A. No duplicate EBITDA haircut. Inventory/receivables/
  payables use days and COGS/revenue; rising net working capital is a cash outflow.
- Recurring synergy ramp and one-time cash integration costs are separate.
  Rent-inclusive coverage = (EBITDA + cash rent expense) / (cash interest + rent
  cash paid). EBITDA already deducts rent; cash flow adjusts only lease cash minus
  rent expense, preventing a second full rent deduction.
- Cash taxes = rate * max(0, EBIT - deductible interest). The configurable
  deduction limit is a proportion of positive EBIT; no loss carryforwards or
  jurisdiction-level tax modelling. It is an analyst simplification, not tax law.
- Interest uses opening instrument principal and opening benchmark plus spread;
  period-end draws start accruing next period. Existing fixed coupons resist
  rate/spread shocks. Existing floaters receive benchmark shocks only; new or
  refinanced instruments receive new-spread shocks. No circular interest sweep.
- Period cash first pays mandatory principal, drawing only eligible committed
  revolver capacity if needed. Unpaid mandatory amounts remain overdue debt and
  are reported as a funding gap. Optional sweeps use only cash above the reserve,
  pay the revolver first, and never exceed outstanding principal. Negative cash
  is an explicit unfunded cash deficit, not implicit borrowing.
- Assumed refinancing rolls only due principal up to an explicit total limit,
  creates a new instrument with stated tenor and pricing, and charges fees. It
  is never included in committed availability. No-refinancing mode creates none.
- Net leverage = (financial debt - unrestricted cash) / EBITDA. Cash-interest
  coverage = EBITDA / cash interest. Nonpositive EBITDA produces unavailable
  ratios and fails analytical ratio checks; zero interest with positive EBITDA
  is displayed as unavailable (no interest due) and does not fail coverage.
- Opening leverage uses combined standalone trailing EBITDA; year-end tests use
  corresponding full forecast-year EBITDA/interest. Quarterly checks use the
  trailing four quarters, seeded with explicitly synthetic pre-close quarters in
  demo mode. Annual checks do not establish intra-year solvency.
- Capacity enumerates a $10m grid including endpoints, detects disconnected
  ranges, then refines every change in feasibility to $1m without assuming global
  monotonicity. Reverse stress scans revenue losses from 0 to 60% in 0.5-point
  increments and reports the first breach, including an already-failing base.
- Initial $750m cash, 3.0x leverage and 4.0x coverage limits are analyst-selected;
  thresholds, new-debt pricing and refinancing assumptions are sensitivity inputs.
  Neither analytical capacity nor scenario feasibility is lender appetite.

## Evidence and implementation limits

The 109 code-owned requirements remain visible. `policy.materiality` determines
conditional applicability and gives a reason for every check. Missing older trend
data do not block explicit future growth; choosing historical trend calibration
reactivates them. Headline values and carrying amounts are reconciliations, not
cash funding inputs. Current cash, debt principal and contracts remain material.
Only six groups of future choices may be analyst assumptions. A missing fact
cannot be relabelled as an assumption. Source hashes demonstrate integrity, not
truth; exact-value review claims and their attributed reviewer are still required.
The curated historical extracts were machine-assisted reviews, not human sign-off.

Historical configuration is built only after the gate passes and financial mapping
reconciles. Unsupported target cash release and historical quarterly seeding are
explicit mapping errors. Synthetic configuration is never a historical fallback.
Every live request rechecks evidence. Saved outputs are snapshots to regenerate.

The model uses simplified annual/quarterly opening-balance cash interest, not daily
day-count accrual, SOFR compounding or commitment-fee calculations. Upfront and
refinancing fees are explicit. Unused revolver commitment fees are excluded from
this educational convention; use an expanded contract mapping before real credit
advice. Quarterly initial interest is seeded with opening pro-forma annual cash
interest divided by four, expressly synthetic. Revolver draw tests use current
trailing earnings, not future annual earnings. Operating lease liabilities are
reported separately and not amortised as a complete lease accounting model.

## Independent hand-worked benchmark

`tests/full_benchmark.json` stores predetermined answers independent of engine
calculations. Two companies each have revenue 500, gross profit 200, variable
costs 50, fixed costs 40 and rent 10: combined EBITDA is 200. There are no taxes,
working-capital changes, capex or dividends in this deliberately small example.
Cash purchase 500 + transaction fees 10 = uses 510. Eligible acquirer cash 300
less reserve 100 contributes 200; new debt is 310. Retained debt 100 + 100 gives
opening debt 510; target cash 50 is unavailable. Interest is 100*4% + 100*5% +
310*6% = 27.6. Mandatory repayment is 100*10% + 310*10% = 41. Cash before optional
repayment is 100 + 200 - 27.6 - 41 = 231.4. Sweep 131.4 leaves cash 100 and debt
510 - 41 - 131.4 = 337.6. Tests compare these stored answers to the full engine.

`model.py` and `data/illustrative.json` preserve the earlier small evidence-gate
regression; `--demo` always selects the full v2 engine.
