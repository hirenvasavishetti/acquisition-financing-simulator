"""Editable future assumptions. This module cannot modify source observations."""

from copy import deepcopy
import json
import math
from pathlib import Path


def public_assumptions(overrides=None):
    defaults = json.loads(Path(__file__).with_name("public_defaults.json").read_text())
    changes = overrides or {}
    unknown = set(changes) - set(defaults)
    if unknown:
        raise ValueError("Unknown public assumptions: " + ", ".join(sorted(unknown)))
    values = {**defaults, **deepcopy(changes)}
    if values["closing_date"] != "2025-11-01":
        raise ValueError(
            "Closing date requires a reviewed seasonal/call-date remapping"
        )

    def numbers(x):
        if isinstance(x, list):
            for item in x:
                yield from numbers(item)
        elif isinstance(x, (int, float)):
            yield x

    if any((not math.isfinite(x) for x in numbers(list(values.values())))):
        raise ValueError("All assumptions must be finite")
    for key in (
        "cash_access",
        "operating_cash_access",
        "award_fraction",
        "mixed_stock_fraction",
        "tax_rate",
        "fee",
    ):
        if not 0 <= values[key] <= 1 or (key == "fee" and values[key] == 1):
            raise ValueError("Invalid fraction: " + key)
    pairs = (
        "bridge_cfo_factors",
        "gross_annual_capex",
        "variable_cost_share",
        "closing_inventory_multiplier",
        "closing_receivables_multiplier",
        "closing_payables_multiplier",
        "maintenance_capex",
        "linked_growth_penalty",
    )
    for key in pairs:
        x = values[key]
        if (
            not isinstance(x, list)
            or len(x) != 2
            or any((not isinstance(v, (int, float)) or v < 0 for v in x))
        ):
            raise ValueError(key + " requires two nonnegative company values")
    if any((x > 1 for x in values["variable_cost_share"])):
        raise ValueError("Variable cost share must be 0–1")
    if values["closing_receivables_multiplier"][1] != 1:
        raise ValueError(
            "FL closing receivables held constant: cash-flow split unavailable"
        )
    if len(values["growth"]) != 2:
        raise ValueError("Growth requires two five-year arrays")
    for series in values["growth"]:
        if (
            not isinstance(series, list)
            or len(series) != 5
            or any((not -1 < x <= 1 for x in series))
        ):
            raise ValueError("Growth requires five values in (-1,1]")
    for key in (
        "cash_floor",
        "max_leverage",
        "min_coverage",
        "benchmark",
        "spread",
        "transaction_fees",
        "dividend_factor",
        "extra_abl_payoff",
        "other_liability_reserve",
        "purchase_commitment_reserve",
        "lease_rate",
        "lease_tail_cash",
        "synergy",
        "integration_multiplier",
    ):
        if not isinstance(values[key], (int, float)) or values[key] < 0:
            raise ValueError("Invalid assumption " + key)
    for key in (
        "lc_collateral_factor",
        "fixed_cost_growth",
        "new_debt_maturity",
        "new_debt_amortisation",
        "refinance_limit",
        "refinance_tenor",
        "reference_share_price",
    ):
        if not isinstance(values[key], (int, float)) or values[key] < 0:
            raise ValueError("Invalid assumption " + key)
    for key in ("synergy_ramp", "integration_costs"):
        if (
            not isinstance(values[key], list)
            or len(values[key]) != 5
            or any(not isinstance(x, (int, float)) or x < 0 for x in values[key])
        ):
            raise ValueError(key + " requires five nonnegative values")
    if values["new_debt_amortisation"] > 1 or any(
        x > 1 for x in values["synergy_ramp"]
    ):
        raise ValueError("Amortisation and synergy ramp must be fractions")
    if not isinstance(values["refinance"], bool):
        raise ValueError("Refinance must be true or false")
    if values["fee_convention"] not in ("fixed_budget", "issued_debt"):
        raise ValueError("Invalid fee convention")
    return values


def form_overrides(query):
    """Small explicit UI allow-list; facts and filenames cannot be submitted."""
    result = {}
    for key in (
        "cash_floor",
        "max_leverage",
        "min_coverage",
        "cash_access",
        "operating_cash_access",
        "dividend_factor",
        "synergy",
        "benchmark",
        "spread",
    ):
        if key in query:
            result[key] = float(query[key][0])
    for key in ("gross_annual_capex", "variable_cost_share"):
        if key + "_dks" in query or key + "_fl" in query:
            original = public_assumptions()[key]
            result[key] = [
                float(query.get(key + suffix, [original[i]])[0])
                for i, suffix in enumerate(("_dks", "_fl"))
            ]
    if "growth_dks" in query or "growth_fl" in query:
        original = public_assumptions()["growth"]
        result["growth"] = [
            (
                (lambda xs: xs * 5 if len(xs) == 1 else xs)(
                    [float(x.strip()) for x in query["growth" + suffix][0].split(",")]
                )
                if "growth" + suffix in query
                else original[i]
            )
            for i, suffix in enumerate(("_dks", "_fl"))
        ]
    if "refinance" in query:
        result["refinance"] = query["refinance"][0] == "true"
    if "fee_convention" in query:
        result["fee_convention"] = query["fee_convention"][0]
    return result
