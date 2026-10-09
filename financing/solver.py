"""Enumerated capacity and reverse stress; no monotonicity assumption."""

from dataclasses import replace
from copy import deepcopy
from .engine import run, transaction
from .scenarios import Shock


def feasible_ranges(points):
    ranges = []
    start = None
    last = None
    for x, feasible in sorted(points):
        if feasible:
            if start is None:
                start = x
            last = x
        elif start is not None:
            ranges.append([start, last])
            start = None
    if start is not None:
        ranges.append([start, last])
    return ranges


def capacity(config, structure, shock=None, grid=10.0, refinement=1.0, frequency=1):
    if grid <= 0 or refinement <= 0 or refinement > grid:
        raise ValueError("Invalid solver resolution")
    cap = transaction(config, structure)["acquisition_borrowing"]
    tests = {}

    def evaluate(x):
        x = round(x, 8)
        if x not in tests:
            tests[x] = run(config, structure, shock, x, frequency=frequency)
        return tests[x]

    points = [min(cap, i * grid) for i in range(int(cap / grid) + 1)] + [cap]
    for x in points:
        evaluate(x)
    coarse = sorted(tests)
    for a, b in zip(coarse, coarse[1:]):
        if tests[a]["feasible"] != tests[b]["feasible"]:
            for step in range(1, int((b - a) / refinement) + 1):
                evaluate(min(b, a + step * refinement))
    good = [x for x, r in tests.items() if r["feasible"]]
    best = max(good) if good else None
    ranges = feasible_ranges([(x, r["feasible"]) for x, r in tests.items()])
    next_bad = min((x for x in tests if best is not None and x > best), default=None)
    limiting = (
        tests[next_bad]["breaches"][0]
        if next_bad is not None
        else tests[min(tests)]["breaches"][0] if best is None else None
    )
    chosen = tests[best] if best is not None else None
    return dict(
        frequency=frequency,
        timing_basis="Quarterly" if frequency == 4 else "Annual",
        fee_convention=config["transaction"].get("fee_convention", "fixed_budget"),
        maximum_acquisition_borrowing=best,
        residual_analytical_equity=cap - best if best is not None else None,
        eligible_acquisition_uses=cap,
        funding_limited=best is not None and abs(best - cap) < 1e-06,
        limiting_constraint=limiting,
        feasible_ranges=ranges,
        disconnected=len(ranges) > 1,
        grid_resolution=grid,
        boundary_resolution=refinement,
        pricing="Constant spread for each sweep; sensitivity runs vary spread",
        headroom=(
            [{"period": 0, **chosen["opening_checks"]["headroom"]}]
            + [{"period": r["period"], **r["headroom"]} for r in chosen["periods"]]
            if chosen
            else []
        ),
        grid=[
            dict(
                borrowing=x,
                feasible=tests[x]["feasible"],
                first_breach=tests[x]["breaches"][0] if tests[x]["breaches"] else None,
            )
            for x in sorted(tests)
        ],
        caveat="Conditional model capacity; not lender appetite. Narrow feasible islands below the grid resolution can be missed.",
    )


def reverse_stress(
    config, structure, shock=None, max_decline=0.6, step=0.005, frequency=1
):
    if step <= 0 or not 0 <= max_decline < 1:
        raise ValueError("Invalid reverse stress range")
    baseline = shock or Shock()
    points = sorted(
        set(
            [min(max_decline, i * step) for i in range(int(max_decline / step) + 1)]
            + [max_decline]
        )
    )
    for decline in points:
        r = run(
            config,
            structure,
            replace(baseline, revenue=-decline, name="Reverse revenue stress"),
            frequency=frequency,
        )
        if not r["feasible"]:
            return dict(
                frequency=frequency,
                timing_basis="Quarterly" if frequency == 4 else "Annual",
                status=(
                    "Already failing at starting point"
                    if decline == 0
                    else "First breach found"
                ),
                revenue_decline=decline,
                previous_tested_decline=max(0, decline - step),
                failing=r["breaches"][0],
                resolution=step,
                explanation="Revenue loss reduces gross profit while fixed costs persist; working-capital release partly offsets cash pressure.",
            )
    return dict(
        frequency=frequency,
        timing_basis="Quarterly" if frequency == 4 else "Annual",
        status="No breach within the tested range",
        revenue_decline=None,
        tested_maximum=max_decline,
        resolution=step,
    )


def sensitivities(config, structure, frequency=1):
    rows = []
    for label, key, value in [
        ("Cash floor 500", "cash_floor", 500.0),
        ("Cash floor 1000", "cash_floor", 1000.0),
        ("Leverage 2.5x", "max_leverage", 2.5),
        ("Leverage 3.5x", "max_leverage", 3.5),
        ("Coverage 5x", "min_coverage", 5.0),
        ("Coverage 3x", "min_coverage", 3.0),
    ]:
        c = deepcopy(config)
        c["policy"][key] = value
        rows.append(dict(label=label, **capacity(c, structure, frequency=frequency)))
    for spread in (0.01, 0.02):
        rows.append(
            dict(
                label=f"New spread +{spread * 10000:.0f}bp",
                **capacity(
                    config, structure, Shock(spread=spread), frequency=frequency
                ),
            )
        )
    return rows
