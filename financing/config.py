"""Deterministic fictional case. No real-company financial values."""

from copy import deepcopy
import math


def demo_config():

    def company(name, revenue, margin, fixed, rent, cash, debt):
        return dict(
            name=name,
            revenue=revenue,
            gross_margin=margin,
            variable_opex=0.1,
            fixed_opex=fixed,
            rent=rent,
            da_ratio=0.025,
            capex_ratio=0.035,
            dio=75.0,
            dso=5.0,
            dpo=40.0,
            growth=[0.025] * 5,
            fixed_growth=0.02,
            cash=cash,
            rent_cash_factor=1.0,
            operating_lease_liability=rent * 4,
            cash_bridge=dict(operating=120.0, capex=80.0, dividends=20.0, buybacks=0.0),
            debts=debt,
            seasonality=[0.22, 0.23, 0.24, 0.31],
            inventory_seasonality=[1.04, 1.08, 1.18, 1.0],
        )

    def debt(id, principal, rate, maturity, kind="fixed", amort=0.0, **kw):
        return dict(
            id=id,
            principal=principal,
            carrying_value=principal - 2.0,
            rate=rate,
            kind=kind,
            spread=0.018,
            maturity=maturity,
            amortisation=amort,
            optional=True,
            repay_at_close="CoC" in id,
            preclose_repayment=0.0,
            **kw,
        )

    return dict(
        schema_version=2,
        mode="synthetic",
        label="Fictional Atlas / Beacon - illustrative only",
        closing_date="2025-11-01",
        currency="USD millions",
        companies=[
            company(
                "Atlas",
                11000.0,
                0.34,
                1150.0,
                280.0,
                1600.0,
                [
                    debt("Atlas notes", 900.0, 0.038, 4.0),
                    debt(
                        "Atlas finance lease",
                        80.0,
                        0.05,
                        5.0,
                        amort=0.2,
                        finance_lease=True,
                    ),
                ],
            ),
            company(
                "Beacon",
                5400.0,
                0.32,
                670.0,
                220.0,
                320.0,
                [
                    debt("Beacon notes", 350.0, 0.0475, 3.0),
                    debt("Beacon CoC loan", 100.0, 0.0, 2.0, kind="floating"),
                ],
            ),
        ],
        transaction=dict(
            target_shares=100.0,
            award_shares=2.0,
            cash_price=20.0,
            exchange_ratio=0.1,
            acquirer_shares=80.0,
            acquirer_reference_price=200.0,
            transaction_fees=50.0,
            financing_fee_rate=0.015,
            headline_equity=2040.0,
            headline_ev=2170.0,
            ev_other=0.0,
            allow_target_cash=False,
            target_cash_rationale="Unavailable in all demo structures",
        ),
        new_debt=dict(
            kind="floating",
            benchmark=[0.04, 0.0375, 0.035, 0.035, 0.035],
            spread=0.025,
            fixed_benchmark=0.04,
            maturity=5.0,
            amortisation=0.02,
        ),
        revolver=dict(
            commitment=800.0,
            borrowing_base=700.0,
            letters_of_credit=70.0,
            spread=0.0225,
            maturity=5.0,
            max_gross_leverage=4.5,
        ),
        policy=dict(
            cash_floor=750.0,
            max_leverage=3.0,
            min_coverage=4.0,
            tax_rate=0.25,
            interest_deduction_limit=1.0,
            dividends=[180.0] * 5,
            buybacks=[0.0] * 5,
            sweep_fraction=1.0,
            refinance=False,
            refinance_limit=2000.0,
            refinance_tenor=5.0,
            refinance_fee=0.015,
        ),
        synergies=dict(
            run_rate=100.0,
            ramp=[0.2, 0.6, 1.0, 1.0, 1.0],
            integration=[80.0, 60.0, 20.0, 0.0, 0.0],
        ),
        quarterly=dict(
            enabled=True,
            label="Illustrative seasonality and pre-close trailing quarters",
        ),
    )


def validate(config):
    if config.get("schema_version") != 2 or config.get("mode") not in (
        "synthetic",
        "historical",
    ):
        raise ValueError("Expected v2 synthetic or historical model configuration")

    def walk(value, path="config"):
        if value is None:
            raise ValueError(f"Missing input: {path}")
        if isinstance(value, float) and (not math.isfinite(value)):
            raise ValueError(f"Nonfinite input: {path}")
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, f"{path}.{key}")
        if isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f"{path}[{i}]")

    walk(config)
    if len(config["companies"]) != 2:
        raise ValueError("Exactly two companies required")
    from datetime import date

    date.fromisoformat(config["closing_date"])
    if config.get("frequency", 1) not in (1, 4):
        raise ValueError("Frequency must be 1 or 4")
    if config.get("currency") != "USD millions":
        raise ValueError("Model units must be USD millions")
    p, t = (config["policy"], config["transaction"])
    if t.get("fee_convention", "fixed_budget") not in ("fixed_budget", "issued_debt"):
        raise ValueError("Invalid fee convention")
    if any((v < 0 for v in t.get("additional_uses", {}).values())):
        raise ValueError("Closing uses cannot be negative")
    for k in (
        "cash_floor",
        "max_leverage",
        "min_coverage",
        "refinance_limit",
        "refinance_tenor",
    ):
        if p[k] < 0:
            raise ValueError(f"Negative policy {k}")
    for k in ("tax_rate", "sweep_fraction", "interest_deduction_limit"):
        if not 0 <= p[k] <= 1:
            raise ValueError(f"Invalid fraction {k}")
    if not 0 <= t.get("mixed_stock_fraction", 0.5) <= 1:
        raise ValueError("Invalid mixed stock election fraction")
    if not 0 <= t["financing_fee_rate"] < 1:
        raise ValueError("Invalid financing fee rate")
    ids = []
    for company in config["companies"]:
        for k in (
            "revenue",
            "cash",
            "rent",
            "fixed_opex",
            "capex_ratio",
            "da_ratio",
            "dio",
            "dso",
            "dpo",
        ):
            if company[k] < 0:
                raise ValueError(f"Negative company input {k}")
        if len(company["growth"]) != 5 or len(company["seasonality"]) != 4:
            raise ValueError("Invalid forecast horizon")
        if abs(sum(company["seasonality"]) - 1) > 1e-09:
            raise ValueError("Seasonality must sum to one")
        if any((not -1 < g <= 1 for g in company["growth"])):
            raise ValueError("Growth outside (-1,1]")
        if (
            not 0 <= company["gross_margin"] <= 1
            or not 0 <= company["variable_opex"] <= 1
        ):
            raise ValueError("Invalid cost fractions")
        if len(company["inventory_seasonality"]) != 4 or any(
            (x < 0 for x in company["inventory_seasonality"] + company["seasonality"])
        ):
            raise ValueError("Invalid seasonal weights")
        if any((v < 0 for v in company.get("closing_working_capital", {}).values())):
            raise ValueError("Negative closing working capital balance")
        for d in company["debts"]:
            if d.get("maturity_date"):
                date.fromisoformat(d["maturity_date"])
            if d["maturity"] <= 0 or d["rate"] < 0 or d["spread"] < 0:
                raise ValueError("Invalid debt timing/rate")
            if "cash_payment_schedule" in d and (
                len(d["cash_payment_schedule"]) != 5
                or any((x < 0 for x in d["cash_payment_schedule"]))
            ):
                raise ValueError("Invalid lease cash schedule")
            ids.append(d["id"])
            if (
                d["kind"] not in ("fixed", "floating")
                or not 0 <= d["amortisation"] <= 1
                or d["principal"] < 0
            ):
                raise ValueError("Invalid debt instrument")
            if not 0 <= d["preclose_repayment"] <= d["principal"]:
                raise ValueError("Invalid preclose repayment")
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate instrument id")
    for series in (
        p["dividends"],
        p["buybacks"],
        config["synergies"]["ramp"],
        config["synergies"]["integration"],
        config["new_debt"]["benchmark"],
    ):
        if len(series) != 5:
            raise ValueError("Five forecast years required")
    return deepcopy(config)
