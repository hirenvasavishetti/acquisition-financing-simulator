# Acquisition Financing & Debt Capacity Simulator

Five-year acquisition funding, instrument debt schedules, liquidity, stress and
conditional debt capacity, with an independently enforced historical evidence gate.
All financial amounts are USD millions unless indicated.

**Engineering:** complete offline synthetic implementation, with validation recorded
in [VERIFICATION.md](VERIFICATION.md). **Historical analysis:** blocked — insufficient
verified evidence for the strict assessment. A separately scoped **public-information case** supports conditional projections and comparisons; see [review and limitations](PUBLIC_CASE_REVIEW.md). **GitHub:** prepared locally; not published.

## Public-information case

The [scope amendment](PUBLIC_INFORMATION_POLICY.md) preserves the gate and distinguishes verified history, conditional forecasts and blocked execution/compliance claims. All 23 remaining gaps are reviewed individually. Five additional factual disclosures support the projected closing bridge and aggregate lease/reserve treatments. No synthetic inputs enter this case.

```sh
python scripts/public_source_supplement.py
python -m financing data/historical.json --public-information --output public-output --database public-output/model.sqlite --excel --pdf
# Exit 2 is expected: the strict recommendation remains blocked.
python scripts/verify_public.py public-output
python -m financing --database public-output/model.sqlite --query public
python -m financing data/historical.json --public-information --serve 8502
```

`public-output/` contains a 20-sheet workbook, two-page memo, dashboard, full JSON results and 23-item applicability review. Under the stated public-information assumptions and analytical thresholds, the model indicates no passing base structure. Mixed consideration passes one lower-reinvestment/no-dividend counterfactual and fails without its assumed synergies. Unbounded private consent/settlement costs prevent an overall financing preference. These are conditional model results, not confirmed borrowing capacity or executable financing.

The public dashboard shows evaluated schedules and comparisons. Rerun Python to change its assumptions in `public_case.assumptions()`; the synthetic dashboard's live threshold form does not alter the public case. JSON exports retain all assumptions, model configuration and provenance. Excel rollforward formulas explain the model snapshot; they do not rerun the capacity solver.

## Run

Python 3.11 or newer. Run these commands from this repository directory:

```sh
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install ".[exports,test]"
python -m financing data/historical.json --demo --output generated --excel --pdf
python -m unittest discover -s tests -v
python -m financing data/historical.json --demo --serve 8501
```

Open http://127.0.0.1:8501. Select a structure and stress case; the live threshold
form recalculates the actual Python model. Exported `dashboard.html` supports
scenario selection offline; live recomputation requires the server. No CDN,
Streamlit or browser package installation is required. The preferred stack was
adapted to standard-library HTTP/SQLite and native HTML/SVG for a smaller offline
installation. Tests use unittest and are also discoverable by pytest.

```sh
python -m financing --database generated/model.sqlite --query summary
python -m financing --database generated/model.sqlite --query observations
python -m financing data/historical.json --output historical-review
```

Historical mode returns exit **2** when blocked and does not calculate fictional
historical results. `--demo` returns 0 when engineering succeeds even if historical
evidence is blocked; add `--require-historical` to require historical clearance.
`--quick` is a partial preview that omits the full stress/sensitivity suite.

To change assumptions, save `financing.config.demo_config()` as JSON and pass it
using `--illustrative-inputs config.json`. Keep `mode: synthetic`. Future historical
assumptions belong in the explicit assumption register, not in this demo file.

## Delivered outputs

`full-output/` contains an intentional demonstration snapshot: interactive HTML,
21-sheet Excel workbook, two-page PDF memo, detailed evidence memo, JSON report
and SQLite database. The public workbook writer uses XlsxWriter with cached
formula results. In the bundled environment, Artifact Tool renders/recalculates
and exports the same shared plan. No proprietary package is needed to install.
Workbook formulas reconcile displayed operations and cash/debt schedules; scenario
and solver cells are clearly labelled Python snapshots. Rerun after input changes.

![Dashboard demonstration](docs/dashboard.png)

![Cash plot](docs/dashboard-charts.png)

## Illustrative findings — fictional Atlas / Beacon only

| Structure | Minimum annual cash | Five-year interest | Base constraints | Acquisition capacity | Residual analytical equity |
|---|---:|---:|---|---:|---:|
| Cash-first | 472.3 | 476.1 | Fails Y5 cash floor | 948 | 222 |
| Liquidity-first | 405.1 | 548.1 | Fails Y5 cash floor | 1,764 | 276 |
| Mixed consideration | 750.0 | 169.7 | Passes | 150 | 0 |

Mixed is the sole base-feasible demonstration structure, conditional on roughly
5.99% dilution. It still fails combined stress; its first reverse revenue breach
is at an 8.5% decline on the 0.5-point scan. Cash-first and liquidity-first already
fail at zero revenue shock. Quarterly cash minima can be lower than annual minima.
Capacity substitutes acquisition debt for separate hypothetical equity while
holding uses and cash contribution fixed. It does not alter stock elections or
represent lender appetite. See [methodology](METHODOLOGY.md) for conventions.

## Historical evidence

The cutoff is 15 May 2025. The source register has 83 reviewed factual observations
from twelve distinct primary documents (16 extract archives), plus six explicit
future assumption groups. Three code-owned derivations use verified dependencies.
Of the original 36 gaps, 13 are resolved (seven facts/derivations and six future
choices) and 23 remain. `historical-output/` contains a nine-sheet workbook,
two-page historical memo, full 36-item gap register, dashboard and SQLite review.
Local archives are factual extracts, not original
filing bytes; hashes and attributed review claims track integrity and provenance.
No human source sign-off is claimed. Material cash, debt, contract and transaction
gaps keep historical recommendations blocked in every output. All 109 checks retain classification,
conditional applicability, materiality, affected calculations and gap resolution.

See [historical review](HISTORICAL_REVIEW.md), [requirement map](REQUIREMENTS.md)
and [learning guide](LEARNING.md). Facts with missing sources remain missing facts.
No illustrative values enter historical mode. Original SEC candidate refresh:

```sh
# Set SEC_USER_AGENT to your truthful organization and contact email first.
python -m financing --sec-facts acquirer --cache generated/cache
python -m financing --sec-facts target --cache generated/cache
```

Downloads use caching, hashes, bounded retries, timeouts and rate limits. SEC
candidates retain original accession, filing and period dates; later restatements
are excluded. Candidates require review before becoming evidence. No SEC contact
was supplied, so automated SEC retrieval was not executed. Restricted OAS data
are excluded; issuer spread assumptions are not market quotes.

## Architecture

`config → database → operating/engine → scenarios/solver → analysis/report → UI/exports`.
`evidence/policy` separately controls historical eligibility; `historical` maps only
cleared facts and explicit future choices. SQLite stores canonical configurations,
companies, source documents, observations, instruments, rates, assumptions, runs,
annual results and breaches. Run IDs include config, evidence, code and scope.

Limitations: annual/quarterly period-end timing, simplified taxes and lease cash
adjustment, no daily solvency, unused commitment fees or detailed lease accounting.
Capacity can miss feasible islands narrower than its initial grid. Historical
quarterly seeding and target cash release require further verified mapping.

## Publish when ready

No Git repository or existing history was found here. No commits or uploads were
made. Review the public-file set and choose a code licence before publishing:

```sh
git init -b main
git add .
git status --short
git commit -m "Add acquisition financing simulator"
gh repo create acquisition-financing-simulator --public --source=. --remote=origin --push
```

Ignore rules exclude credentials, caches, databases, environments and build files.
`full-output` documents the intentional demo; the SQLite snapshot is excluded from
Git but provided in the delivery archive and recreated by the demo command.

Source extracts have not received independent human sign-off.
