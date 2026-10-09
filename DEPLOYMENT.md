# Live portfolio hosting

Live service: https://acquisition-financing-simulator.onrender.com/

Deployed and verified on 9 October 2026 using the Free web service plan. The
existing service was created through the public Git repository form with the
same settings as `render.yaml`; it is not managed by a Blueprint. Avoid creating a
second service when updating this deployment. The Render settings show the `main`
branch and On Commit auto-deploy; manual deployment is also available in Render.

## Render setup

Connect this GitHub repository through Render's **New → Blueprint** flow and use
the root `render.yaml`. Review that the web service plan is **Free** before deploying.
No database, disk, paid service or custom domain is required. Alternatively create
a Python Web Service with the same build/start commands, Python version and health
path as the Blueprint. The root directory is the repository root.

The build installs `.[web]` (Waitress 3.0.2); the runtime is Python 3.12.12.
Render supplies `PORT`, and the listener binds to `0.0.0.0`. The service starts in
synthetic mode. `/healthz` checks HTTP availability without running the financial
model; it is not a claim that historical evidence is complete. Smoke-test the
actual calculation endpoints after every deployment.

Run `python scripts/smoke_hosting.py https://acquisition-financing-simulator.onrender.com`
to check the public endpoint, or `python scripts/smoke_hosting.py --local` to start,
test and stop a local Waitress server. Run smoke tests while no other visitor is
recalculating; a busy 503 response is an intentional capacity limit, not a saved result.

Local startup still works with `python -m financing data/historical.json --demo
--serve 8765` on `127.0.0.1`. Install `.[web]` to use the same Waitress server
locally. Without that optional dependency, only loopback development hosting is
allowed. With `PORT` set, bare `--serve` reads that port and defaults to public
binding; `--host 127.0.0.1` explicitly restores a local-only listener.

## Isolation and limits

Only `/`, `/api/report` and `/healthz` are served. No filesystem browser, upload,
database, arbitrary file path or source-editing endpoint exists. GET/HEAD only;
request bodies are rejected, query strings are limited to 4096 bytes / 24 fields,
and duplicate/unknown fields, nonfinite numbers and out-of-range values fail
before calculation. Strict mode does not accept forecast overrides.

Each calculation starts a fresh process, reads the bundled case and source files,
and passes no database or output path. Only one calculation runs at a time;
concurrent calculations receive 503 and can be retried. Health checks remain
available. Work exceeding 120 seconds is terminated. Waitress caps connections at
32, request headers at 16 KiB and request bodies at 4 KiB before application checks.
Errors do not expose local paths or traces. This small portfolio deployment is not
intended for high-volume service or guaranteed availability.

The hosted input ranges are operational limits, not evidence-based confidence
intervals: cash reserve 0–10,000 USD m; leverage 0–20; coverage 0–50; cash-access and
variable-cost fractions 0–1; dividends 0–3; synergy 0–2,000 USD m; benchmark/spread
0–30%; annual capex per company 0–5,000 USD m; annual growth -50% to +50% (one or five
values). Synthetic timing is annual or quarterly; public timing remains annual.
Use the offline CLI for wider legitimate scenario exploration.

## Outputs and persistence

The browser downloads the currently displayed JSON report. Excel and PDF exports
remain available through the CLI (`.[exports]`), not through a website button.
Recalculation and mode changes use fresh model results. Assumptions are not saved
as an account/session; refreshing or changing mode restores defaults. Synthetic,
conditional public-information and strict historical modes remain distinct.

Render's free filesystem is temporary. The web app does not write SQLite history,
change the bundled evidence or persist visitors' reports. Waitress may spool large
responses to temporary files; those are transport buffers, not saved model runs.
Generate lasting SQLite history locally with the CLI. Free services sleep after
15 minutes without inbound traffic and restart on the next visit, causing a cold
start delay. No keep-alive workaround is configured. Your laptop may be off.

Publication or a green health check does not clear the historical evidence gate.
The 15 May 2025 information cutoff and all financial/evidence logic are unchanged.

## Verification and official references

Run `python -m unittest discover -s tests -v`. Hosting regressions include invalid
requests, concurrency, worker timeout/recovery, visitor isolation and the strict
block. After deployment verify all three modes, changed assumptions and error
responses using the public HTTPS URL. Add a live README link only after that check.

- https://render.com/docs/blueprint-spec
- https://render.com/docs/web-services
- https://render.com/docs/python-version
- https://render.com/docs/free
- https://docs.pylonsproject.org/projects/waitress/en/stable/arguments.html
