# Project conventions

- Keep financing calculations in the Python engine. Dashboard code renders reports; it must not introduce another financial model.
- Preserve the 15 May 2025 historical cutoff and output-level evidence dependencies. A calculation succeeding never clears the recommendation block.
- Do not alter archived source bytes to fix integrity failures. Diagnose the mismatch and document a fresh review when warranted.
- Keep the synthetic acquisition, conditional public case, strict assessment and hypothetical bond lab visibly separate. Never substitute demonstration values into historical calculations.
- Distinguish analytical thresholds from actual covenants and hypothetical hedges from executable trades.
- Tests: `python -m unittest discover -s tests -v`; hosting: `python scripts/smoke_hosting.py --local`. Export checks and their expected CLI exit codes are in README.md.
- New financial conventions need an independent benchmark or reconciliation. Formatting changes alone do not need new tests.
- Use small, descriptive commits. Keep source, tests and documentation together; regenerate saved reports after financial or evidence changes.
- Keep environments, credentials, generated databases and local inspection files out of Git. Deployment uses the existing Render Free service; do not create paid resources without approval.
