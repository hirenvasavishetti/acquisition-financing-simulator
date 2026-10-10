"""Small joint-stress grid using the same debt, cash and operating engine."""

from .engine import run, STRUCTURES
from .scenarios import Shock


def stress_grid(config):
    cells = []
    for structure in STRUCTURES:
        for margin_bp in (0, -100, -200):
            for rate_bp in (0, 100, 200):
                result = run(
                    config,
                    structure,
                    Shock(
                        name="Joint margin / rate stress",
                        margin=margin_bp / 10000,
                        benchmark=rate_bp / 10000,
                    ),
                    frequency=config.get("frequency", 1),
                )
                cells.append(
                    dict(
                        structure=structure,
                        margin_bp=margin_bp,
                        rate_bp=rate_bp,
                        feasible=result["feasible"],
                        min_cash=result["min_cash"],
                        cash_headroom=result["min_cash"]
                        - config["policy"]["cash_floor"],
                        total_interest=result["total_interest"],
                        first_breach=(
                            result["breaches"][0] if result["breaches"] else None
                        ),
                    )
                )
    return dict(
        scope="Conditional analytical screens, not contractual covenants or committed financing",
        definition="Parallel benchmark increase and gross-margin reduction in every forecast period; all other assumptions held fixed. Cash headroom includes closing. A positive cash cushion alone does not establish feasibility.",
        cells=cells,
    )
