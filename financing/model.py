"""Small anonymous numerical model for gate integration, not historical analysis."""

import math

FIELDS = (
    "purchase",
    "fees",
    "cash",
    "reserve",
    "existing_debt",
    "existing_coupon",
    "new_rate",
    "ebitda",
    "pre_interest_cash_flow",
)


def calculate(inputs):
    for key in FIELDS:
        value = inputs.get(key)
        if (
            isinstance(value, bool)
            or not isinstance(value, (float, int))
            or (not math.isfinite(value))
        ):
            raise ValueError(f"Missing/invalid numerical input: {key}")
        if key != "pre_interest_cash_flow" and value < 0:
            raise ValueError(f"Negative input: {key}")
    p = inputs
    outputs = []
    for name, stock in (
        ("Cash-first", 0),
        ("Liquidity-first", 0),
        ("Mixed consideration", 0.5),
    ):
        uses = p["purchase"] * (1 - stock) + p["fees"]
        contribution = (
            0
            if name == "Liquidity-first"
            else min(uses, max(0, p["cash"] - p["reserve"]))
        )
        new, old, cash = (
            uses - contribution,
            p["existing_debt"],
            p["cash"] - contribution,
        )
        opening = {
            "cash_uses": uses,
            "cash_contribution": contribution,
            "new_borrowing": new,
            "noncash_consideration": p["purchase"] * stock,
            "opening_cash": cash,
            "opening_debt": old + new,
        }
        years = []
        for year in range(1, 6):
            begin_cash, begin_debt = (cash, old + new)
            interest = old * p["existing_coupon"] + new * p["new_rate"]
            cash += p["pre_interest_cash_flow"] - interest
            available = max(0, cash - p["reserve"])
            repay_new = min(new, available)
            repay_old = min(old, available - repay_new)
            new, old = (new - repay_new, old - repay_old)
            repayment = repay_new + repay_old
            cash -= repayment
            gap = old + new if year == 5 else 0
            years.append(
                {
                    "year": year,
                    "opening_cash": begin_cash,
                    "opening_debt": begin_debt,
                    "interest": interest,
                    "repayment": repayment,
                    "closing_cash": cash,
                    "closing_debt": old + new,
                    "maturity_gap": gap,
                    "liquidity_shortfall": max(0, p["reserve"] - cash),
                    "net_leverage": (
                        (old + new - cash) / p["ebitda"] if p["ebitda"] > 0 else None
                    ),
                    "coverage": (
                        p["ebitda"] / interest
                        if interest > 0 and p["ebitda"] > 0
                        else None
                    ),
                }
            )
        outputs.append({"structure": name, **opening, "years": years})
    return outputs
