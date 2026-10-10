"""Shared analysis pipeline used by dashboard, CLI, database and workbook."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from .engine import run, STRUCTURES
from .scenarios import Shock, scenarios
from .solver import capacity, reverse_stress, sensitivities


def code_id():
    return sha256(
        b"".join(
            (
                p.name.encode() + p.read_bytes()
                for p in sorted(Path(__file__).parent.glob("*.py"))
            )
        )
    ).hexdigest()


def compare_recommendation(base, stress, mode):
    eligible = [r for r in base if r["feasible"]]
    tradeoffs = [
        dict(
            structure=r["structure"],
            feasible=r["feasible"],
            minimum_cash=r["min_cash"],
            interest=r["total_interest"],
            dilution=r["opening"]["ownership_dilution"],
            refinanced=r["total_refinancing"],
            max_leverage=r["max_leverage"],
            min_coverage=r["min_coverage"],
            stress_cases_passed=sum(
                (s["feasible"] for s in stress if s["structure"] == r["structure"])
            ),
        )
        for r in base
    ]
    preferred = eligible[0]["structure"] if len(eligible) == 1 else None
    if not eligible:
        narrative = "No fully funded structure passes all analytical constraints. Review capacity and residual equity before selecting a structure."
    elif preferred:
        narrative = f"{preferred} is the only base structure passing all period constraints. It is conditional on accepting its dilution, cash policy and downside outcomes; severe stress may still fail."
    else:
        narrative = "Multiple base structures pass. There is no automatic preference: compare liquidity, costs, dilution, stress resilience and refinancing dependence."
    return dict(
        scope=(
            "Illustrative synthetic recommendation"
            if mode == "synthetic"
            else "Qualified historical model comparison"
        ),
        preferred_structure=preferred,
        narrative=narrative,
        tradeoffs=tradeoffs,
    )


def analyse(config, full=True):
    frequency = config.get("frequency", 1)
    base = [run(config, s, frequency=frequency) for s in STRUCTURES]
    comparisons = (
        [
            run(config, s, shock, frequency=frequency)
            for shock in scenarios()
            for s in STRUCTURES
        ]
        if full
        else base
    )
    refinance = deepcopy(config)
    refinance["policy"]["refinance"] = True
    refi = [
        run(refinance, s, Shock(name="Assumed refinancing"), frequency=frequency)
        for s in STRUCTURES
    ]
    quarterly = (
        [run(config, s, frequency=4) for s in STRUCTURES]
        if config["quarterly"]["enabled"]
        else []
    )
    timing_capacity = {
        str(f): {s: capacity(config, s, frequency=f) for s in STRUCTURES}
        for f in (1, 4)
        if f == 1 or config["quarterly"]["enabled"]
    }
    return dict(
        frequency=frequency,
        timing_basis="Quarterly" if frequency == 4 else "Annual",
        capacity_by_frequency=timing_capacity,
        analysis_scope="full" if full else "preview",
        config=config,
        base=base,
        comparisons=comparisons + refi,
        refinancing=refi,
        quarterly=quarterly,
        capacity=timing_capacity[str(frequency)],
        reverse_stress={
            s: reverse_stress(config, s, frequency=frequency) for s in STRUCTURES
        },
        sensitivities=(
            sensitivities(config, "Cash-first", frequency=frequency) if full else []
        ),
        recommendation=compare_recommendation(base, comparisons, config["mode"]),
        code_id=code_id(),
    )


# Preserved implementation notes
# A unique feasible candidate is conditional, never inferred merely from low debt.
