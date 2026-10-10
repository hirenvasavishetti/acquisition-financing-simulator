"""Coupon-date valuation of a hypothetical, non-callable bullet bond.

Flat nominal yield, periodic compounding and no accrued interest. This is a
separate teaching model: it never consumes or verifies company evidence.
"""

import math
from urllib.parse import parse_qs

DEFAULTS = dict(
    notional=100_000_000,
    years=5,
    coupon=0.06,
    benchmark=0.04,
    spread=0.02,
    frequency=2,
    hedge_dv01=80,
)
LIMITS = dict(
    notional=(1, 1e10),
    years=(1, 30),
    coupon=(0, 0.25),
    benchmark=(0, 0.20),
    spread=(0, 0.20),
    hedge_dv01=(1, 10000),
)


def bond_risk(**inputs):
    if inputs.keys() - DEFAULTS.keys():
        raise ValueError("Unsupported bond input")
    p = DEFAULTS | inputs
    for key, (low, high) in LIMITS.items():
        if (
            isinstance(p[key], bool)
            or not isinstance(p[key], (float, int))
            or not math.isfinite(p[key])
            or not low <= p[key] <= high
        ):
            raise ValueError(f"{key} must be finite and between {low:g} and {high:g}")
    if (
        p["years"] != int(p["years"])
        or p["frequency"] not in (1, 2, 4)
        or isinstance(p["frequency"], bool)
    ):
        raise ValueError("Use whole years and a frequency of 1, 2 or 4")
    f, n = int(p["frequency"]), int(p["years"] * p["frequency"])
    y = p["benchmark"] + p["spread"]
    cashflows = [100 * p["coupon"] / f] * n
    cashflows[-1] += 100

    def price(yield_rate):
        return sum(cf / (1 + yield_rate / f) ** k for k, cf in enumerate(cashflows, 1))

    clean = price(y)
    base = 1 + y / f
    first = sum(-k / f * cf / base ** (k + 1) for k, cf in enumerate(cashflows, 1))
    second = sum(
        k * (k + 1) / f**2 * cf / base ** (k + 2) for k, cf in enumerate(cashflows, 1)
    )
    value = clean / 100 * p["notional"]
    dv01 = -first * 0.0001 * p["notional"] / 100
    scenarios = []
    for rate_bp, spread_bp in (
        (-100, 0),
        (-50, 0),
        (50, 0),
        (100, 0),
        (0, 100),
        (100, 100),
    ):
        dy = (rate_bp + spread_bp) / 10000
        scenarios.append(
            dict(
                rate_bp=rate_bp,
                spread_bp=spread_bp,
                price=price(y + dy),
                pnl=(price(y + dy) - clean) / 100 * p["notional"],
                duration_convexity_pnl=(first * dy + 0.5 * second * dy**2)
                / 100
                * p["notional"],
            )
        )
    contracts = round(dv01 / p["hedge_dv01"])
    return dict(
        scope="Standalone illustrative bond; not an actual-company security or market quote",
        inputs=p,
        yield_rate=y,
        price=clean,
        market_value=value,
        modified_duration=-first / clean,
        convexity=second / clean,
        dv01=dv01,
        cs01=dv01,
        hedge_short_contracts=contracts,
        residual_dv01=dv01 - contracts * p["hedge_dv01"],
        scenarios=scenarios,
        limitations="Coupon-date settlement; flat yield; no accrued interest, default, optionality or liquidity premium model. Equal DV01 and CS01 reflect the additive flat-yield assumption. Hedge DV01 is hypothetical; benchmark hedging does not remove credit-spread or basis risk.",
    )


def from_query(raw):
    q = parse_qs(raw, keep_blank_values=True, max_num_fields=8)
    if any(len(v) != 1 or not v[0] for v in q.values()):
        raise ValueError("Each bond input needs one value")
    return bond_risk(**{key: float(value[0]) for key, value in q.items()})
