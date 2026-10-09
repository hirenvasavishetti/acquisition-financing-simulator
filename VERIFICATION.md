# Verification record - 20 September 2026

## Render hosting — 9 October 2026

- Deployed the existing dashboard at https://acquisition-financing-simulator.onrender.com/ on Render Free, Python 3.12.12 and Waitress 3.0.2. Source deployment: `c3dcf1e85229762fc4309be3e77a5c5bb3b13f07`.
- GitHub Actions run `38000963747` passed 81 tests (one optional Node exporter test skipped), production-server HTTP smoke tests, export/pipeline checks and evidence-gate checks on Ubuntu / Python 3.11. Local full suite passed 80 tests before the additional port-selection test, which also passed in the seven-test hosting suite.
- Public HTTPS smoke tests passed: default synthetic dashboard; changed cash reserve and quarterly calculation; independent subsequent request; conditional public assumptions; strict block in every mode; public and strict HTML pages; invalid input and unexposed-file rejection. Health responded in 0.33 seconds while calculation work was active.
- Browser inspection confirmed the redesigned page and working navigation. Invalid cash reserve displayed the validation message without clearing stale-state protection. An initial concurrent smoke request received the expected busy 503; rerunning after the browser's initial calculation completed passed.
- Each request uses an isolated process with a 120-second termination limit, one active calculation, finite bounded inputs and no shared output/database writes. Web history is not persisted. CLI Excel/PDF/SQLite features remain available locally. Free cold starts and limited concurrent calculation are documented.
- No financial or evidence logic was changed. A deployed application does not establish historical completeness or executable financing capacity.

Engineering is complete within the documented educational scope. Historical clearance is incomplete and the strict evidence gate remains blocked. The project was published to GitHub on 9 October 2026. See the publication record below; earlier verification entries describe their status at the time.

## Local checks performed

- Reproduced the original 65-test baseline and nine review findings. Final suite: all 74 tests passed (19.385 seconds; no skips), including the independent Decimal financing-fee example, annual/quarterly capacity regression, working-capital continuity, alternative cost behaviour, maturity timing, live assumption propagation and output-level evidence removal.
- Created a fresh Windows Python 3.12 virtual environment, built and installed version 0.3.0 with declared export/test dependencies, and verified imports from its site-packages outside the repository. `pip check` passed. Installation used `--no-cache-dir` after the restricted global pip cache caused an initial failure.
- Generated the synthetic demonstration (48 comparisons), conditional public case (36 scenarios / 108 comparisons) and strict historical assessment. Historical/public CLI exit code 2 is expected because strict recommendation status remains blocked; synthetic exit code is 0.
- Installed portable public exports reproduce the delivered public model exactly. Output scripts check financial values, workbook cached/formula values, no Excel error cells, PDF page counts, SQLite and evidence status. The synthetic pipeline also verifies live threshold recalculation and HTTP 422 rejection of invalid `nan` input.
- Independently reproduced annual cash-first capacity $948m, its quarterly reserve shortfall $24.268m, and quarterly capacity $928m with $929m failing. Identical economic assumptions use different settlement timing; numerical interest equality is not imposed.
- Live browser checks: quarterly recalculation; public cash reserve, capex and dividend edits reaching the engine; stale-result warning; unchanged strict block. Under reserve $500m, capex $900m/$240m and no dividends, the conditional mixed structure passes the analytical screens. This is not an overall recommendation.
- Desktop 1280px and narrow 390px layouts inspected. Current README screenshot was captured from the live application, not a mock-up. Charts, comparison cards and responsive layout inspected.
- Delivered workbooks contain 25 synthetic, 28 public and 10 strict sheets. All 47 distinct/relevant workbook views and all six memo pages were rendered and inspected; corrected low-contrast assumption headers, verbose constraint cells and redundant itemised-use dictionaries. Memos are two pages each.
- Financial reconciliations and provenance remain shared across JSON, dashboard, workbook, memo and SQLite. Output SHA256 manifests are regenerated and checked; the delivery archive excludes local environments, node_modules, build folders and inspection logs.

The final presentation patch was rebuilt offline with the bundled setuptools backend and installed into the same clean environment; installed exports and HTTP checks passed again. A network-isolated build-isolation retry could not reach PyPI, so it was not counted as a successful installation. The earlier fresh dependency installation remains the clean-install check.

## Verification limits

Artifact Tool workbook export succeeds. Its separate Windows preview process writes all expected PNGs but returns teardown code 3221226505. The rendered images were inspected and saved XLSX values were independently checked; this preview-process issue is not silently reported as a clean exit. Portable XlsxWriter exports were also checked from the installed package. Native Microsoft Excel execution was not tested.

GitHub-hosted Linux CI is configured but has not run. Local success is Windows Python 3.12 only. No human-independent source review, lender verification or transaction-execution opinion is claimed. Hashes establish integrity rather than truth. Passing tests does not resolve the 23 strict material evidence gaps.

The model is reproducible by source, assumption, input and code identifiers. PDF/XLSX packaging timestamps and SQLite run history need not be byte-identical. Historical public projections remain annual; no unsupported quarterly seasonality is silently inferred.

## Reproduce

From the repository root after activating a Python environment:

```sh
python -m pip install ".[exports,test]" --no-cache-dir
python -m unittest discover -s tests -v
python -m financing data/historical.json --demo --output full-output --excel --pdf
python scripts/verify_pipeline.py full-output data/historical.json
python -m financing data/historical.json --public-information --output public-output --database public-output/model.sqlite --excel --pdf
# Expected exit 2: strict recommendation remains blocked.
python scripts/verify_public.py public-output
python -m pip check
```

See REQUIREMENTS.md for implementation coverage and IMPROVEMENT_LOG.md for the before/after findings. Earlier verification records remain under legacy/2026-09-16.


## Dashboard redesign - 9 October 2026

Presentation-only redesign: charcoal/olive sidebar, lime actions, lavender charts, eight navigation sections, global scenario/structure selection and a scoped insight panel. Financial engine, assumptions and evidence policy were not changed.

- All 74 existing tests passed in 43.360 seconds. The initial run failed because the managed Windows temporary directory was unwritable; using a writable project temporary directory resolved those environmental errors.
- Recomputed all three modes and compared model base/scenario/capacity/stress outputs, public projections, evidence, recommendation status and supported historical calculations with saved pre-edit baselines. All values are unchanged; only presentation code provenance differs. Saved JSON reports/workbooks/memos remain the original numerical snapshots; new HTML embeds those reports exactly.
- Browser checked every navigation section, three modes, selected severe-revenue scenario, quarterly recalculation (annual cash-first 948 versus quarterly 928), public reserve edit to 500, stale-result/export blocking, invalid negative reserve rejection and restore. Downloaded JSON matches baseline financial arrays and evidence exactly.
- Strict assessment disables unsupported timing/recalculation and hides unavailable charts. Public mode retains annual-only timing and strict recommendation block. Responsive desktop 1440x1000 and mobile 390x844 inspected; mobile sidebar opens/closes, hidden navigation is inert, and wide tables scroll inside their panels without page overflow.
- Current screenshot captured from the live application. Browser error log was empty at the final overview check.
- All three saved dashboards regenerated with self-contained CSS/JavaScript. Embedded payload equality and file-mode disabling were checked in code; a separate file-protocol browser execution was not performed. Saved scenarios remain local; live model edits require the server.
- Wheel rebuilt and installed with CSS/JS assets included; installed renderer verified. Build needed a short clean staging path after Windows temporary-path and stale build-directory errors. No new dependencies added. GitHub publication is unchanged: not published.
- Export button downloads the currently displayed JSON report. XLSX/PDF generation remains through the documented CLI, with no nonfunctional browser export buttons.

## GitHub publication — 9 October 2026

Published at https://github.com/hirenvasavishetti/acquisition-financing-simulator. All 136 initial publishing files were checked against their Git blob fingerprints before the branch was updated. The exact publishing copy passed 74 local tests (one optional Node exporter test skipped); the working source had previously passed all 74 with Node configured. GitHub-hosted Ubuntu / Python 3.11 CI passed for publication commit f2af9352fed6682f6e02aa75274fd66d8b34f31c (Actions run 37988727343): installation, unit tests, synthetic exports, pipeline checks, public-information exports and strict-block exit-code checks all succeeded. Generated SQLite files and local environments are excluded; the CLI recreates the databases. Source-extract bytes are preserved through `.gitattributes` to protect evidence integrity hashes. Publication does not resolve historical evidence gaps or host the live Python application.
