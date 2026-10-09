# Verification record — 16 September 2026

Engineering is complete for the deterministic synthetic simulator under the
documented educational conventions. Historical analysis remains blocked. GitHub
publication and GitHub-hosted CI execution have not occurred.

## Public-information case extension

- Scope amendment preceded implementation. The original 109 requirements and strict block remain. All 23 gaps have an individual public-route assessment; five additional source-backed facts are archived in two new extracts. Public supported output is not historical completeness.
- 65 tests passed in the dedicated isolated export environment, using the installed wheel from outside the repository. A new dependency-free virtual environment passed its 63 applicable tests, with two optional export tests skipped. Both environments passed `pip check`. Nine added tests cover source/contract removal, post-cutoff evidence, independent decimal closing arithmetic, contractual treatment, no facility draws, propagation to exports/SQLite and a numerically feasible counterfactual that cannot unlock preference.
- Public model: 15 supported historical calculations, three five-year structures, 28 cases / 84 comparisons, scoped capacity sweeps and reverse stresses. All source/use, cash and debt checks reconcile. No base structure passes; one mixed counterfactual passes and loses feasibility without synergies. No overall preference is issued.
- Saved public workbook has 20 sheets, correctly cached closing-bridge and annual cash/debt formulas, no error cells and persistent strict status. The public memo has two pages. All twelve new/revised workbook preview views and both memo pages were visually inspected; rate/access formatting and long constraint text were corrected during review.
- Installed portable public CLI exports reproduced the delivered public model exactly. Existing live HTTP synthetic threshold recalculation, validation rejection and blocked exit-code pipeline passed. Public SQLite records the full evaluated bundle with source-state, assumption and code provenance; the public query exposes its comparative summary.
- Exact regression comparison found all original synthetic base, 48 scenario comparisons, capacity, reverse stress, sensitivities and quarterly results unchanged. Preserved strict historical/demo outputs retain 9/21 sheets and two-page PDFs.
- Artifact Tool export succeeds. Its separate Windows preview process still returns teardown code 3221226505 after writing all twelve PNGs. Saved workbook formulas and portable exports pass independently; this preview teardown issue is disclosed rather than treated as a financial-model failure.
- CI now includes public exports and `scripts/verify_public.py`, but GitHub-hosted execution and publication have not occurred. Packaging includes fresh output SHA256 manifests. Educational approximations and unbounded private obligations are documented in PUBLIC_CASE_REVIEW.md; tests do not resolve them.

Reproduce after installing `.[exports,test]`:

```sh
python -m financing data/historical.json --public-information --output public-output --database public-output/model.sqlite --excel --pdf
# Expected exit code 2: strict evidence remains blocked.
python scripts/verify_public.py public-output
```

## Earlier historical review extension (preserved baseline)

- Original 109 requirements preserved, with 19 separately registered supporting disclosures. Original 36 gaps: seven resolved facts/derivations, six explicit future choices, 23 still unresolved. These counts measure evidence coverage, not historical completion.
- Five new regression tests check independent historical arithmetic, removal of a required source, suppression of dependent operating sensitivities, post-cutoff/conflicting evidence and rejection of unregistered supplements. Existing evidence-gate tests remain intact.
- Isolated installed-package verification: all 56 tests passed; import was from `work/clean-v2/Lib/site-packages`, outside the source tree. Rebuilt wheel installed offline; `pip check` passed. Bundled Python ran 55 tests successfully with one optional export integration skipped; exported artifacts were independently checked with bundled Artifact Tool.
- Exact comparison against the previous saved report found synthetic base, 48 comparisons, capacity, reverse stress, sensitivities and quarterly results unchanged.
- Historical output: 15 supported bounded calculations, 90 operating sensitivity points and 24 hypothetical funding-unit/synergy cases. Full historical funding, capacity and liquidity reverse stress remain unavailable. Historical CLI exit 2, no historical model-result array and no actual-company preference.
- Nine-sheet historical and 21-sheet combined workbooks: status/value checks passed and no Excel error cells. Both PDFs have two pages. Historical pages and all six new/revised workbook view previews were visually inspected. A summary label was corrected to distinguish supported history from anonymous synthetic results.
- Installed live HTTP pipeline: threshold recomputation, invalid-input rejection and blocked historical CLI passed. SQLite persists blocked historical review and sources without a synthetic configuration in the historical database.
- Artifact Tool workbook export exited 0. Its separate Windows preview process wrote all six PNGs, then returned code 3221226505 during teardown; images were inspected. This known preview-only issue did not affect workbook exports or cached-value validation.

## Earlier engineering checks (preserved baseline)

- Windows, Python 3.12.14: all 51 tests passed using the bundled Node exporter.
- Fresh isolated virtual environment: built and installed the 0.2.0 wheel with
  declared public export/test dependencies. Confirmed import came from that
  environment's site-packages, outside the source tree; `pip check` passed.
- Public portable path: 50 tests passed, one bundled-Node-specific test skipped.
  A separate portable workbook/PDF integration test passed in that suite.
- Full installed pipeline: 48 structure/scenario combinations, eight threshold/
  spread sensitivity sweeps, three capacity/reverse-stress runs and three quarterly
  runs. Strict JSON contains no NaN/Infinity. Historical result array is empty.
- Predetermined full-model benchmark reconciles sources/uses, opening cash/debt,
  interest, mandatory/optional repayments and closing balances. Stress tests check
  cash and instrument debt rollforwards, limits and no over-repayment.
- Required source removal blocks the historical recommendation while the full
  model calculates identically. Output propagation is tested in HTML, JSON,
  Markdown and Excel. The PDF repeats the status and evidence limitations.
- Installed HTTP server: cash floor 500 recalculates cash-first to feasible;
  historical block remains. Invalid `nan` input returns HTTP 422 and blocked JSON.
  Historical-only CLI returns 2. Windows redirected stdout is explicitly UTF-8.
- Browser: structure selector changes base feasibility; threshold form performs
  live Python recalculation. Screenshots show the actual interface and cash plot.
- Delivered workbook: 16 sheets; formula error scan found zero matches; read-only
  cached-value checks found no error cells. Operating EBITDA and cash formulas
  reconcile to Python. All sheet previews were rendered and inspected; rate/
  fraction precision and header wrapping were corrected after inspection.
- PDF: exactly two pages; both rendered pages visually inspected. All numbers
  are labelled fictional; no actual-company preferred structure appears.

## Environment observations

The first pip build encountered a restricted global cache directory; installation
succeeded using `--no-cache-dir`. Build isolation supplies setuptools; do not use
`--no-build-isolation` in a fresh environment without a build backend installed.
The native workbook preview process returned Windows termination code 3221226505
after writing all 16 PNGs. The generated images were inspected and workbook export
itself exited 0; portable clean-install export also passed. This is a preview-process
teardown issue, not a suppressed workbook calculation error. Preview helpers and
large inspection logs are excluded from the delivery archive.

Python 3.11 Linux CI is configured but has not run on GitHub. The locally verified
environment is Windows Python 3.12.14; no cross-platform success is fabricated.
The model is deterministic by configuration/code/evidence hash; XLSX/PDF archive
metadata and SQLite run-history bytes need not be byte-for-byte identical.

## Reproduce verification

```sh
python -m pip install ".[exports,test]"
python -m unittest discover -s tests -v
python -m financing data/historical.json --demo --output generated --excel --pdf
python scripts/verify_pipeline.py generated data/historical.json
python -m pip check
```

See REQUIREMENTS.md for the complete implementation map and INPUT_REVIEW.md for
all 109 input decisions. Historical blocks are economic/evidence limitations,
not numerical test failures. Data collection and contract mapping remain partial.
