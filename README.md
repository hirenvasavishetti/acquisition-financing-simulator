# Acquisition Financing & Debt Capacity Simulator

**[Try the live simulator](https://acquisition-financing-simulator.onrender.com/)** · [Model methodology](docs/METHODOLOGY.md)

An acquisition can fit a leverage target and still run out of cash. This project tests that distinction with a connected five-year operating model, instrument-level debt schedules and period-by-period liquidity constraints. A separate fixed-income lab translates yield and spread shocks into bond P&L and hypothetical DV01 hedges.

Built with Python, SQLite and a responsive browser interface. No market-data subscription or API key is needed.

## Explore it in three minutes

1. **Compare funding.** Start with the fictional Atlas / Beacon acquisition. Cash-first, liquidity-first and mixed consideration expose the trade-off between borrowing, cash reserves and dilution.
2. **Find the constraint.** Open Debt Capacity, compare annual with quarterly timing, then use Credit Risk to combine margin compression and higher rates. A passing leverage ratio does not guarantee a funded cash path.
3. **Price the risk.** Open Rates Lab. Change the benchmark or spread and compare exact repricing with duration/convexity estimates. Inspect the residual DV01 after rounding the hypothetical hedge.
4. **Challenge the evidence.** Switch to the DICK’S / Foot Locker public-information case. Follow projected closing cash back to verified starting observations, then inspect the separate strict assessment and unresolved requirements.

The live site recalculates the Python model. JSON downloads are available in the browser; Excel, PDF and SQLite outputs are produced with the CLI. The bond lab has its own JSON export and uses USD, while acquisition schedules use USD millions.

## Results worth discussing

| Question | Reproducible result | Interpretation |
|---|---|---|
| Does timing change capacity? | Fictional cash-first capacity: $948m annual versus $928m quarterly. | At $948m borrowing, quarterly cash falls $24.3m below the $750m reserve. Timing matters even with the same annual operating totals. |
| Is projected cash the same as available funding? | Public case projected closing accounting cash: DICK’S $1,336.9m; Foot Locker $96.1m. | Cash accessibility and financing treatment remain separate assumptions and contractual checks. These are forecasts, not actual closing balances. |
| Is the public financing comparison robust? | All three base structures breach analytical screens. Mixed consideration passes the lower-investment/no-dividend case and a 1pp linked growth penalty, but fails a 2pp penalty. | The result depends on reinvestment and growth assumptions; it does not establish the actual transaction’s optimal structure. |
| What does a 100bp move cost? | A hypothetical $100m, 5-year, 6% semiannual bond at 6% yield has DV01 of about $42,651. A +100bp yield move loses about $4.16m. | Exact repricing differs from the linear duration estimate; a benchmark hedge leaves spread and basis risk. |

**Actual-company recommendation: Blocked — insufficient verified evidence.** The 23 unresolved material strict requirements are visible in the evidence register. Independently supported history and conditional projections remain available. No synthetic input fills a historical gap.

## Technical substance

- Connected sources and uses, projected opening balances, five-year operations, taxes, investment, working capital and instrument-level debt service.
- Annual and quarterly cash timing; cash sweeps, maturity shortfalls, assumed refinancing, coverage and leverage screens checked from closing onward.
- Debt-capacity search and reverse stress; separate rate, spread, operating, working-capital and synergy shocks; 27 joint margin/rate stress cases using the same engine.
- Normalised SQLite records for inputs, evidence and model runs, with reproducible fingerprints. Public hosting does not persist visitor history.
- An output-level evidence policy: verified history, explicit projections and unsupported conclusions are distinct. Tests remove required sources and prove that dependent results stay blocked even when the synthetic model calculates.
- Closed-form bond benchmarks and finite-difference checks for price, duration, convexity and DV01. The browser renders Python outputs rather than maintaining a second financial engine.
- Bounded HTTP inputs, isolated financing workers, calculation timeouts and read-only source evidence. Concurrent visitors cannot overwrite another visitor’s assumptions or reports.

## Run and verify

Python 3.11 or newer:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install ".[web,exports,test]"
.venv/Scripts/python -m financing data/historical.json --demo --serve 8765
```

Open **http://127.0.0.1:8765**. On macOS/Linux use `.venv/bin/python`. Core calculations use the standard library; public serving uses Waitress, Excel uses XlsxWriter and PDF uses ReportLab. Node is not required.

After activating the environment:

```powershell
python -m unittest discover -s tests -v
python scripts/smoke_hosting.py --local
python -m financing data/historical.json --demo --frequency 4 --output generated --excel --pdf
python scripts/verify_pipeline.py generated data/historical.json
python -m financing data/historical.json --public-information --public-assumptions data/public-assumptions.json --output public-generated --database public-generated/model.sqlite --excel --pdf
python scripts/verify_public.py public-generated
```

Public and strict runs intentionally return exit code **2** while the strict recommendation is blocked; supported exports are still written. Invalid input can also return 2: inspect the CLI `error` field. CI runs the model, export, evidence and hosting checks on every push.

## Repository guide

| Location | Purpose |
|---|---|
| `financing/` | Operating/debt engine, evidence policy, SQL persistence, risk analytics, HTTP boundary and dashboard |
| `data/` | Synthetic inputs, public assumptions and dated historical source extracts |
| `tests/` | Independent benchmarks, reconciliations, source-removal regressions and HTTP checks |
| `scripts/` | Traceable ingestion and reproducibility checks |
| `docs/` | [Financial methodology](docs/METHODOLOGY.md) |
| `full-output/`, `public-output/`, `historical-output/` | Saved reports for the three distinct scopes; regenerate after changes |
| `legacy/`, `example-output/` | Earlier audit material; not current findings |

The existing free HTTPS address works independently of a local computer; its first request after inactivity can be slow.

## Analytical boundaries

The historical information cutoff is **15 May 2025**. Public forecasts are conditional on cash access, seasonality, investment, cost behaviour and future financing assumptions. Analytical leverage/coverage screens are not actual covenants. No legal compliance, lender appetite or confirmed borrowing availability is asserted. Negative balances after a breach describe an unfunded path.

The rates lab is a hypothetical coupon-date, flat-yield, non-callable bond model, not a live quote or valuation of either company’s securities. Source extracts have not received independent human sign-off. Passing software tests does not establish historical completeness or executable financing.
