# Learning walkthrough

## Follow one input

In `data/historical.json`, find `acquirer.FY2024.revenue`: 13,442.849 USD million.
Its exact-value claim points to the DICK'S FY2024 10-K archive, original filing URL,
statement section and conversion from reported thousands. `check_evidence` checks
the period, cutoff, hash and review payload. `store_evidence` writes the observation
with its source foreign key. Run `--query observations` to inspect it. It appears
in the dashboard evidence table and workbook, but cannot seed an actual-company
forecast while other material inputs are missing. This is intentional.

For a complete numerical trace, fictional Atlas revenue is 11,000 in `demo_config`.
`store_config` saves it; `load_config` reloads the canonical JSON used by the engine.
With 2.5% growth, first-year revenue is 11,275. Gross profit is 11,275*34%=3,833.5;
variable costs 1,127.5, fixed costs 1,173 and rent 285.6 give EBITDA 1,247.4.
`operating.forecast` returns that row, `engine.run` combines Beacon and synergy,
`analysis` runs structures, and the dashboard Operations table displays those same
objects. Excel Operations I5 reproduces the Atlas EBITDA formula. The configuration
hash and code hash connect the output to its inputs. Historical and fictional
company IDs are distinct SQL records.

## Capacity worked example

For cash-first, full funding needs 1,170 of acquisition borrowing, plus separately
fixed refinancing/fee borrowing. Evaluate 0,10,...,1,170 while hypothetical equity
fills the difference. Every candidate runs all five years and opening checks.
The demo changes feasibility between 940 and 950, so the solver tests each dollar
inside that interval. At 948 it passes; 949 fails. Required analytical equity is
1,170-948=222. Read the reported limiting period/headroom rather than inferring
which ratio binds. A different spread or cash floor reruns the entire sweep.
Disconnected sampled feasible ranges are retained. A narrow island inside an
untested ten-dollar interval can still be missed; this is a numerical limitation.

## Five exercises

1. Raise the cash floor to 1,000: eligible opening cash contribution falls and
   cash headroom tightens. Full-funding borrowing generally rises; feasible capacity
   need not move monotonically because contributions also change.
2. Increase only the new-debt spread by 100bp: new/refinancing interest rises;
   existing fixed coupons remain unchanged. Capacity tends to fall.
3. Add ten inventory days: more inventory consumes cash and can induce revolver
   draws; do not separately haircut EBITDA for this working-capital change.
4. Remove synergies: EBITDA and cash available to repay debt fall; keep integration
   spending explicit rather than automatically removing it too.
5. Enable capped refinancing: maturity gaps may disappear but debt survives beyond
   the old maturity and incurs new pricing/fees. It is assumed, not committed liquidity.

For each, save a new JSON config, run the CLI and compare SQL `summary` and the
Capacity/Checks workbook sheets. Explain any result contrary to your expectation.

## Interview questions

- Why can a profitable acquirer still miss a maturity? Distinguish EBITDA, cash
  conversion, distributions and the timing of principal payments.
- Why does EV not equal cash purchase funding? Explain debt/cash adjustments,
  noncash shares, awards, fees and retained versus repaid debt.
- Why opening-principal interest? It prevents cash-sweep circularity, but delays
  interest on period-end draws; shorter periods reduce this timing approximation.
- What does the cash floor represent? An analyst threshold until a covenant is verified.
- Why no automatic minimum-debt recommendation? Dilution, liquidity, price and
  stress resilience are economic trade-offs.
- How does a source hash differ from verification? A hash catches modification;
  review must establish that a source actually supports the fact.
- Can a missing historical cash balance be an assumption? No. Use a separately
  labelled fictional scenario and block the actual-company conclusion.
- Why not bisection? Non-monotonic feasibility is possible; inspect the grid first.
- Why do quarterly ratios use trailing sums? Annualising one seasonal quarter or
  averaging ratios can materially misstate debt service capacity.
- Which change would be needed for real credit underwriting? Verified contracts,
  source-reconciled opening liquidity, daily/contractual interest and fee conventions,
  and defensible operating, tax, lease and refinancing assumptions.

## Public-information walkthrough

1. Run the README public-case command. Exit 2 is expected even though three financial schedules calculate: inspect strict status and the separate public output policy.
2. Trace DKS reported cash through prior-year CFO calibration, forecast capex/dividends and the 75% cash-access assumption. Compare projected cash to usable cash; neither is an actual closing disclosure.
3. Follow Foot Locker's $400m note redemption and ABL termination into uses. Find zero postclose facility availability and the retained aggregate lease cash schedule.
4. Compare the base and lower-reinvestment/no-dividend scenario, then remove synergies. Explain why the one passing structure is a conditional result and does not establish an optimal financing choice.
5. In a temporary copy, remove the FL indenture extract and rerun. Financing and capacity should become unavailable while independently supported historical calculations and the closing bridge remain. Restore the source before further work.

A missing historical balance cannot become a forecast assumption. A future balance can be projected from verified starting information. A numerical sensitivity cannot substitute for an essential missing contract.
