# Live portfolio hosting

Live service: https://acquisition-financing-simulator.onrender.com/

Deployed and verified on 9 October 2026 using the Free web service plan. The
existing service was created through the public Git repository form with the
same settings as `render.yaml`; it is not managed by a Blueprint. Avoid creating a
second service when updating this deployment. The Render settings show the `main`
branch and On Commit auto-deploy; manual deployment is also available in Render.

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

## Runtime and public boundaries

The public service runs `pip install ".[web]"` followed by
`python -m financing data/historical.json --demo --host 0.0.0.0 --serve $PORT`.
`render.yaml` records the free-plan configuration and pinned Python runtime.
The existing Render service has automatic deployments from `main`.

- `/healthz`: process health without running the financial model.
- `/api/report?mode=synthetic`: acquisition report; `public` and `strict` retain their separate evidence policies.
- `/api/bond-risk`: bounded standalone illustrative bond calculation; no company evidence is consumed.
- `/`: dashboard, defaulting to the synthetic demonstration.

Only GET/HEAD are accepted. Queries are limited to 4 KiB with allowlisted,
finite inputs. Request bodies and file-serving routes are rejected. Financing
calculations run in a disposable process with a 120-second limit; one runs at a
time, and concurrent calculation requests receive HTTP 503 with Retry-After.
Waitress has four threads, 32 connections and bounded request headers/bodies.
The bond lab is limited to 30 years and quarterly payments (120 cash flows).
It remains available while a financing worker is busy.

Visitor assumptions stay in the request and response. The server does not write
SQLite, exports or source files. Render's filesystem is temporary: there is no
persistent visitor history, account or saved workspace. Download JSON before
leaving. Generate Excel, PDF and SQLite locally with the documented CLI commands.

Render Free services [spin down after 15 minutes without inbound traffic](https://render.com/docs/free).
The next request can take about a minute to wake the service, followed by the
model calculation. This is a portfolio demonstration, not a low-latency trading
service. The descriptive `onrender.com` address provides HTTPS without buying a
domain. A custom domain or paid instance requires an explicit ownership/budget
decision; neither is necessary to use this deployment.
