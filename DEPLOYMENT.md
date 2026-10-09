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
