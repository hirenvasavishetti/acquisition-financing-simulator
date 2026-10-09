"""Construct historical inputs only from gated facts and explicit future choices."""

from copy import deepcopy
from .config import validate


def historical_config(case, evidence):
    if evidence["blocked"]:
        raise ValueError("Historical evidence gate blocked")
    values = {
        r["key"]: r["value"]
        for r in evidence["rows"]
        if r["classification"] in ("verified fact", "explicit modelling assumption")
    }

    def fact(key):
        if key not in values:
            raise ValueError(f"Missing historical model mapping: {key}")
        return deepcopy(values[key])

    op = fact("assumption.operating_forecast")
    finance = fact("assumption.financing_terms_and_fees")
    thresholds = fact("assumption.analytical_thresholds")
    allocation = fact("assumption.capital_allocation")
    bridge = fact("assumption.closing_bridge")
    companies = []
    for index, role in enumerate(("acquirer", "target")):
        c = deepcopy(op["companies"][index])
        c["name"] = "DICK'S Sporting Goods" if index == 0 else "Foot Locker"
        c["revenue"] = fact(f"{role}.FY2024.revenue")
        c["cash"] = fact(f"{role}.opening.unrestricted_cash")
        da = fact(f"{role}.FY2024.depreciation_amortisation")
        c["da_ratio"] = da / c["revenue"]
        ebitda = fact(f"{role}.FY2024.operating_profit") + da
        lease = fact(f"{role}.FY2024.lease_reconciliation")
        c["rent"] = lease["rent_expense"]
        c["rent_cash_factor"] = lease["rent_cash"] / c["rent"]
        c["operating_lease_liability"] = lease["operating_lease_liability"]
        c["fixed_opex"] = (
            c["revenue"] * (c["gross_margin"] - c["variable_opex"]) - c["rent"] - ebitda
        )
        c["debts"] = fact(f"{role}.debt.instrument_inventory")
        c["cash_bridge"] = bridge["companies"][index]
        if (
            abs(
                sum((d["principal"] for d in c["debts"]))
                - fact(f"{role}.opening.debt_principal")
            )
            > 1e-05
        ):
            raise ValueError(
                f"{role} debt instruments do not reconcile to verified opening principal"
            )
        cost = c["revenue"] * (1 - c["gross_margin"])
        c["dio"] = fact(f"{role}.FY2024.inventory") / cost * 365
        c["dso"] = fact(f"{role}.FY2024.receivables") / c["revenue"] * 365
        c["dpo"] = fact(f"{role}.FY2024.payables") / cost * 365
        companies.append(c)
    shares = fact("transaction.share_and_award_treatment")
    transaction = {
        **finance["transaction"],
        **shares,
        "cash_price": fact("transaction.cash_price"),
        "exchange_ratio": fact("transaction.exchange_ratio"),
    }
    for source_key, target_key in (
        ("transaction.equity_value", "headline_equity"),
        ("transaction.enterprise_value", "headline_ev"),
    ):
        if source_key in values:
            transaction[target_key] = values[source_key]
    if transaction["allow_target_cash"]:
        raise ValueError(
            "Historical target-cash availability requires a separately reviewed legal release mapping; not implemented"
        )
    if op["quarterly"]["enabled"]:
        raise ValueError(
            "Historical quarterly analysis needs verified pre-close quarter seeds; use separately labelled synthetic quarterly mode"
        )
    revolver = {
        **fact("acquirer.debt.revolver_commitments"),
        **fact("acquirer.debt.borrowing_base_and_letters_of_credit"),
        **fact("acquirer.debt.covenants_and_restricted_payments")[
            "modelled_revolver_constraints"
        ],
    }
    config = dict(
        schema_version=2,
        mode="historical",
        label="DICK'S / Foot Locker - pre-cutoff inputs",
        closing_date=bridge["closing_date"],
        currency="USD millions",
        companies=companies,
        transaction=transaction,
        new_debt=finance["new_debt"],
        revolver=revolver,
        policy={**thresholds, **allocation, **finance["policy"]},
        synergies=fact("assumption.synergy_delivery_and_costs"),
        quarterly=op["quarterly"],
    )
    return validate(config)


# Preserved implementation notes
# Cost decomposition is explicitly a forecast assumption calibrated to
# sourced standalone EBITDA, not a claimed historical gross-margin fact.
# Baseline days must reproduce verified balance sheet balances.
# No automatic target-cash release is inferred from an unrestricted accounting label.
