"""Connected transaction, instrument debt and liquidity model in USD millions."""

from copy import deepcopy
from .config import validate
from .operating import operating_periods, trailing
from .scenarios import Shock
from .funding import FundingUses, replace_acquisition_debt

STRUCTURES = ("Cash-first", "Liquidity-first", "Mixed consideration")
EPS = 1e-07


def transaction(config, structure):
    if structure not in STRUCTURES:
        raise ValueError("Unknown financing structure")
    t, p = (config["transaction"], config["policy"])
    bridges = []
    retained = []
    required = 0.0
    for c in config["companies"]:
        b = c["cash_bridge"]
        prepay = sum((d["preclose_repayment"] for d in c["debts"]))
        close_cash = (
            c["cash"]
            + b["operating"]
            - b["capex"]
            - b["dividends"]
            - b["buybacks"]
            - prepay
        )
        bridges.append(
            dict(
                company=c["name"],
                latest_cash=c["cash"],
                **b,
                preclose_debt_repayment=prepay,
                closing_cash=close_cash,
                latest_debt=sum((d["principal"] for d in c["debts"])),
                closing_debt=sum((d["principal"] for d in c["debts"])) - prepay,
            )
        )
        for original in c["debts"]:
            d = deepcopy(original)
            d["principal"] -= d["preclose_repayment"]
            d["original_principal"] = d["principal"]
            d["new"] = False
            if d["repay_at_close"]:
                required += d["principal"]
            else:
                retained.append(d)
    shares = t["target_shares"] + t["award_shares"]
    election = (
        t.get("mixed_stock_fraction", 0.5)
        if structure == "Mixed consideration"
        else 0.0
    )
    cash_purchase = shares * t["cash_price"] * (1 - election)
    stock_shares = shares * election * t["exchange_ratio"]
    noncash = stock_shares * t["acquirer_reference_price"]
    acquirer_cash = bridges[0]["closing_cash"]
    target_cash = bridges[1]["closing_cash"] if t["allow_target_cash"] else 0.0
    if t["allow_target_cash"] and (not t["target_cash_rationale"].strip()):
        raise ValueError("Target cash eligibility requires explicit justification")
    eligible = acquirer_cash + target_cash
    uses = FundingUses(
        cash_purchase, required, t["transaction_fees"], **t.get("additional_uses", {})
    )
    preliminary = uses.total
    contribution = (
        0.0
        if structure == "Liquidity-first"
        else min(preliminary, max(0, eligible - p["cash_floor"]))
    )
    new = (preliminary - contribution) / (1 - t["financing_fee_rate"])
    fee = new * t["financing_fee_rate"]
    cash_uses = preliminary + fee
    acq = max(0, cash_purchase - contribution)
    other = new - acq
    target_debt = bridges[1]["closing_debt"]
    equity = shares * t["cash_price"]
    ev = equity + target_debt - bridges[1]["closing_cash"] + t["ev_other"]
    return dict(
        structure=structure,
        bridges=bridges,
        retained_instruments=retained,
        itemised_uses={**uses.rows(), "financing_fees": fee},
        fee_convention=t.get("fee_convention", "fixed_budget"),
        equity_consideration=equity,
        enterprise_value=ev,
        equity_headline_difference=(
            equity - t["headline_equity"] if "headline_equity" in t else None
        ),
        ev_headline_difference=ev - t["headline_ev"] if "headline_ev" in t else None,
        cash_purchase=cash_purchase,
        noncash_consideration=noncash,
        stock_issued=stock_shares,
        ownership_dilution=stock_shares / (t["acquirer_shares"] + stock_shares),
        required_debt_repayment=required,
        transaction_fees=t["transaction_fees"],
        financing_fees=fee,
        cash_uses=cash_uses,
        cash_contribution=contribution,
        acquisition_borrowing=acq,
        borrowing_for_refinancing_and_fees=other,
        total_new_borrowing=new,
        retained_debt=sum((d["principal"] for d in retained)),
        opening_cash=eligible - contribution,
        unavailable_target_cash=(
            0.0 if t["allow_target_cash"] else bridges[1]["closing_cash"]
        ),
        opening_debt=sum((d["principal"] for d in retained)) + new,
        analytical_equity=0.0,
        sources_uses_difference=contribution + new - cash_uses,
    )


def instrument_rate(d, config, shock, year):
    if d["kind"] == "fixed":
        return d["rate"]
    return (
        max(0, config["new_debt"]["benchmark"][year - 1] + shock.benchmark)
        + d["spread"]
        + (shock.spread if d.get("new") else 0)
    )


def constraints(row, config):
    p = config["policy"]
    return dict(
        cash=row["closing_cash"] - p["cash_floor"],
        leverage=(
            p["max_leverage"] - row["net_leverage"]
            if row["net_leverage"] is not None
            else None
        ),
        coverage=(
            row["coverage"] - p["min_coverage"]
            if row["coverage"] is not None
            else None if row["ttm_ebitda"] <= 0 else 1000000000000.0
        ),
        maturity=-row["maturity_gap"],
    )


def run(
    config, structure="Cash-first", shock=None, acquisition_borrowing=None, frequency=1
):
    c = validate(config)
    shock = shock or Shock()
    if not -1 < shock.revenue <= 1 or frequency not in (1, 4):
        raise ValueError("Invalid shock/frequency")
    opening = transaction(c, structure)
    if acquisition_borrowing is not None:
        if not -EPS <= acquisition_borrowing <= opening["acquisition_borrowing"] + EPS:
            raise ValueError("Capacity borrowing exceeds eligible acquisition uses")
        replace_acquisition_debt(
            opening,
            acquisition_borrowing,
            c["transaction"]["financing_fee_rate"],
            c["transaction"].get("fee_convention", "fixed_budget"),
        )
    debts = deepcopy(opening["retained_instruments"])
    n = c["new_debt"]
    debts.append(
        dict(
            id="Acquisition term",
            principal=opening["total_new_borrowing"],
            original_principal=opening["total_new_borrowing"],
            kind=n["kind"],
            rate=n["fixed_benchmark"] + shock.benchmark + n["spread"] + shock.spread,
            spread=n["spread"],
            maturity=n["maturity"],
            amortisation=n["amortisation"],
            optional=True,
            new=True,
        )
    )
    rv = c["revolver"]
    revolver = dict(
        id="Committed revolver",
        principal=0.0,
        original_principal=0.0,
        kind="floating",
        rate=0.0,
        spread=rv["spread"],
        maturity=rv["maturity"],
        amortisation=0.0,
        optional=True,
        new=False,
    )
    debts.append(revolver)
    company_rows, ops = operating_periods(c, shock, frequency)
    initial_ebitda = sum((trailing(x)["ebitda"] for x in c["companies"]))
    ebitda_history = (
        [
            sum(
                (
                    trailing(x)["revenue"]
                    * x["seasonality"][q]
                    * (x["gross_margin"] - x["variable_opex"])
                    - (x["fixed_opex"] + x["rent"]) / 4
                    for x in c["companies"]
                )
            )
            for q in range(4)
        ]
        if frequency == 4
        else []
    )
    initial_interest = sum(
        (d["principal"] * instrument_rate(d, c, shock, 1) for d in debts)
    )
    interest_history = [initial_interest / 4] * 4 if frequency == 4 else []
    cash = opening["opening_cash"]
    policy = c["policy"]
    refinance_remaining = policy["refinance_limit"]
    rows = []
    ledger = []
    breaches = []
    opening_row = dict(
        period=0,
        year=0,
        closing_cash=cash,
        net_leverage=(
            (opening["opening_debt"] - cash) / initial_ebitda
            if initial_ebitda > 0
            else None
        ),
        coverage=(
            initial_ebitda / initial_interest
            if initial_interest > 0 and initial_ebitda > 0
            else None
        ),
        ttm_ebitda=initial_ebitda,
        maturity_gap=0.0,
    )
    opening_row["headroom"] = constraints(opening_row, c)
    for key, val in opening_row["headroom"].items():
        if val is None or val < -EPS:
            breaches.append(dict(period=0, year=0, constraint=key, headroom=val))
    for op in ops:
        year = op["year"]
        time = op["time"]
        beginning = cash
        begin_debt = sum((d["principal"] for d in debts))
        period_ledger = []
        interest = 0.0
        for d in list(debts):
            rate = instrument_rate(d, c, shock, year)
            charge = d["principal"] * rate / frequency
            interest += charge
            period_ledger.append(
                dict(
                    instrument=d["id"],
                    period=op["period"],
                    year=year,
                    opening_principal=d["principal"],
                    rate=rate,
                    interest=charge,
                    mandatory_due=0.0,
                    mandatory_paid=0.0,
                    optional_paid=0.0,
                    draw=0.0,
                    refinanced=0.0,
                    maturity=d["maturity"],
                )
            )
        by_id = {x["instrument"]: x for x in period_ledger}
        deductible = min(
            interest, max(0, op["ebit"]) * policy["interest_deduction_limit"]
        )
        tax = max(0, op["ebit"] - deductible) * policy["tax_rate"]
        dividend = policy["dividends"][year - 1] / frequency
        buyback = policy["buybacks"][year - 1] / frequency
        cash_flow = (
            op["ebitda"]
            - tax
            - op["delta_nwc"]
            - op["integration"]
            - (op["rent_cash"] - op["rent"])
        )
        access = policy.get("operating_cash_access_fraction", 1.0)
        if not 0 <= access <= 1:
            raise ValueError("Operating cash access must be a fraction")
        cash_flow = min(0, cash_flow) + max(0, cash_flow) * access
        cash += cash_flow - op["capex"] - interest - dividend - buyback
        refinancing = 0.0
        refi_fee = 0.0
        due_list = []
        for d in list(debts):
            matured = (
                d["maturity_date"] <= op["period_end"]
                if d.get("maturity_date")
                else d["maturity"] <= time + EPS
            )
            due = (
                d["principal"]
                if matured
                else min(
                    d["principal"],
                    d["original_principal"] * d["amortisation"] / frequency,
                )
            )
            if "cash_payment_schedule" in d and (not matured):
                due = min(
                    d["principal"],
                    max(
                        0,
                        d["cash_payment_schedule"][year - 1] / frequency
                        - by_id[d["id"]]["interest"],
                    ),
                )
            by_id[d["id"]]["mandatory_due"] = due
            if (
                due > EPS
                and matured
                and (d is not revolver)
                and (not d.get("finance_lease"))
                and policy["refinance"]
            ):
                amount = min(due, refinance_remaining)
                if amount > 0:
                    refinance_remaining -= amount
                    refinancing += amount
                    d["principal"] -= amount
                    due -= amount
                    by_id[d["id"]]["refinanced"] = amount
                    new_id = f"Refinance {d['id']} at {op['period']}"
                    new = dict(
                        id=new_id,
                        principal=amount,
                        original_principal=amount,
                        kind=n["kind"],
                        rate=n["fixed_benchmark"]
                        + shock.benchmark
                        + n["spread"]
                        + shock.spread,
                        spread=n["spread"],
                        maturity=time + policy["refinance_tenor"],
                        amortisation=n["amortisation"],
                        optional=True,
                        new=True,
                    )
                    debts.append(new)
                    entry = dict(
                        instrument=new_id,
                        period=op["period"],
                        year=year,
                        opening_principal=0.0,
                        rate=instrument_rate(new, c, shock, year),
                        interest=0.0,
                        mandatory_due=0.0,
                        mandatory_paid=0.0,
                        optional_paid=0.0,
                        draw=amount,
                        refinanced=0.0,
                        maturity=new["maturity"],
                    )
                    period_ledger.append(entry)
                    by_id[new_id] = entry
                    refi_fee += amount * policy["refinance_fee"]
            due_list.append((d, due))
        cash -= refi_fee
        total_due = sum((due for _, due in due_list))
        gross = sum((d["principal"] for d in debts))
        full_ebitda = (
            sum(ebitda_history[-3:]) + op["ebitda"] if frequency == 4 else op["ebitda"]
        )
        available = max(
            0,
            min(rv["commitment"], rv["borrowing_base"])
            - rv["letters_of_credit"]
            - revolver["principal"],
        )
        leverage_cap = max(0, rv["max_gross_leverage"] * max(0, full_ebitda) - gross)
        available = min(available, leverage_cap) if time < rv["maturity"] - EPS else 0.0
        draw = min(available, max(0, total_due + policy["cash_floor"] - cash))
        revolver["principal"] += draw
        cash += draw
        by_id[revolver["id"]]["draw"] += draw
        mandatory_paid = 0.0
        gap = 0.0
        for d, due in due_list:
            paid = min(due, max(0, cash))
            cash -= paid
            d["principal"] -= paid
            mandatory_paid += paid
            gap += due - paid
            by_id[d["id"]]["mandatory_paid"] = paid
        sweep = max(0, cash - policy["cash_floor"]) * policy["sweep_fraction"]
        optional = 0.0
        order = sorted(
            debts,
            key=lambda d: (d is revolver, instrument_rate(d, c, shock, year)),
            reverse=True,
        )
        for d in order:
            amount = min(d["principal"], sweep) if d["optional"] else 0.0
            d["principal"] -= amount
            cash -= amount
            sweep -= amount
            optional += amount
            by_id[d["id"]]["optional_paid"] = amount
        for d in debts:
            by_id[d["id"]]["closing_principal"] = d["principal"]
        ledger.extend(period_ledger)
        total = sum((d["principal"] for d in debts))
        ebitda_history.append(op["ebitda"])
        interest_history.append(interest)
        ttm = (
            sum(ebitda_history[-frequency:])
            if frequency == 1
            else sum(ebitda_history[-4:])
        )
        ttm_interest = (
            sum(interest_history[-frequency:])
            if frequency == 1
            else sum(interest_history[-4:])
        )
        coverage = ttm / ttm_interest if ttm > 0 and ttm_interest > EPS else None
        leverage = (total - cash) / ttm if ttm > 0 else None
        row = {
            **op,
            "opening_cash": beginning,
            "opening_debt": begin_debt,
            "interest": interest,
            "tax": tax,
            "operating_cash_flow": cash_flow,
            "dividends": dividend,
            "buybacks": buyback,
            "refinancing": refinancing,
            "refinancing_fees": refi_fee,
            "revolver_draw": draw,
            "mandatory_paid": mandatory_paid,
            "optional_paid": optional,
            "repayment": mandatory_paid + optional,
            "closing_cash": cash,
            "closing_debt": total,
            "maturity_gap": gap,
            "liquidity_shortfall": max(0, policy["cash_floor"] - cash),
            "ttm_ebitda": ttm,
            "ttm_interest": ttm_interest,
            "net_leverage": leverage,
            "coverage": coverage,
            "revolver_outstanding": revolver["principal"],
            "available_revolver": max(0, available - draw),
            "cash_check": cash
            - (
                beginning
                + cash_flow
                - op["capex"]
                - interest
                - dividend
                - buyback
                - refi_fee
                + draw
                - mandatory_paid
                - optional
            ),
            "debt_check": total - (begin_debt + draw - mandatory_paid - optional),
        }
        row["headroom"] = constraints(row, c)
        for key, val in row["headroom"].items():
            if val is None or val < -EPS:
                breaches.append(
                    dict(period=op["period"], year=year, constraint=key, headroom=val)
                )
        rows.append(row)
    annual = []
    flow_keys = (
        "revenue",
        "cogs",
        "variable_opex",
        "fixed_opex",
        "rent",
        "rent_cash",
        "ebitda",
        "ebit",
        "da",
        "capex",
        "delta_nwc",
        "synergy",
        "integration",
        "interest",
        "tax",
        "operating_cash_flow",
        "dividends",
        "buybacks",
        "refinancing",
        "refinancing_fees",
        "revolver_draw",
        "mandatory_paid",
        "optional_paid",
        "repayment",
    )
    for year in range(1, 6):
        group = [r for r in rows if r["year"] == year]
        a = dict(group[-1])
        a.update({k: sum((r[k] for r in group)) for k in flow_keys})
        a["opening_cash"] = group[0]["opening_cash"]
        a["opening_debt"] = group[0]["opening_debt"]
        a["maturity_gap"] = max((r["maturity_gap"] for r in group))
        a["min_cash"] = min((r["closing_cash"] for r in group))
        a["coverage"] = (
            a["ebitda"] / a["interest"]
            if a["ebitda"] > 0 and a["interest"] > EPS
            else None
        )
        a["net_leverage"] = (
            (a["closing_debt"] - a["closing_cash"]) / a["ebitda"]
            if a["ebitda"] > 0
            else None
        )
        a["rent_inclusive_coverage"] = (
            (a["ebitda"] + a["rent"]) / (a["interest"] + a["rent_cash"])
            if a["ebitda"] > 0 and a["interest"] + a["rent_cash"] > EPS
            else None
        )
        annual.append(a)
    return dict(
        structure=structure,
        scenario=shock.name,
        shock=shock.to_dict(),
        frequency=frequency,
        timing_basis="Quarterly" if frequency == 4 else "Annual",
        post_breach_policy="Continues mechanically after breach; later values are diagnostic, not an executable financing path.",
        opening=opening,
        company_forecasts=company_rows,
        years=annual,
        periods=rows,
        debt_schedule=ledger,
        opening_checks=opening_row,
        feasible=not breaches,
        breaches=breaches,
        min_cash=min([opening["opening_cash"]] + [r["closing_cash"] for r in rows]),
        total_interest=sum((r["interest"] for r in rows)),
        total_refinancing=sum((r["refinancing"] for r in rows)),
        max_leverage=max(
            (r["net_leverage"] for r in rows if r["net_leverage"] is not None),
            default=None,
        ),
        min_coverage=min(
            (r["coverage"] for r in rows if r["coverage"] is not None), default=None
        ),
        **{
            k: opening[k]
            for k in (
                "opening_cash",
                "opening_debt",
                "cash_uses",
                "cash_contribution",
                "noncash_consideration",
            )
        },
    )


# Preserved implementation notes
# Synthetic pre-close standalone quarters seed the trailing window, not future quarters.
# Public sensitivity can exclude positive cash while retaining all cash losses.
# Aggregate finance-lease projection: cash includes estimated interest.
# Existing synthetic instruments do not use this optional convention.
# A facility must still be committed and borrowing-eligible when drawn.
# Repay drawn revolver first, then highest current interest cost.
# Annual rent-inclusive ratios are recomputed on annual sums below.
