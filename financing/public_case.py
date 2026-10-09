"""Output-level public-information case. Never clears the strict evidence gate."""

from copy import deepcopy
from itertools import product
from .engine import run, STRUCTURES
from .solver import capacity, reverse_stress
from .scenarios import Shock
from .evidence import fingerprint

PREFIX = "Under the stated public-information assumptions and analytical thresholds, the model indicates "
BRIDGE_DEPS = [
    "detail.acquirer.cash",
    "detail.target.cash",
    "detail.acquirer.ytd_cash_flow",
    "detail.target.ytd_cash_flow",
    "acquirer.FY2024.capex",
    "target.FY2024.capex",
    "detail.acquirer.planning_disclosures",
    "detail.acquirer.distributions",
    "detail.target.finance_maturities",
    "detail.transaction.capitalization",
    "detail.acquirer.ytd_wc_cash",
    "detail.target.ytd_wc_cash",
] + [
    f"{role}.FY2024.{metric}"
    for role in ("acquirer", "target")
    for metric in ("inventory", "receivables", "payables")
]
CONTRACT_DEPS = [
    "detail.acquirer.notes",
    "detail.acquirer.notes_outstanding",
    "detail.target.notes_principal",
    "detail.target.notes_terms",
    "detail.transaction.debt_treatment",
    "transaction.cash_price",
    "transaction.exchange_ratio",
    "target.debt.revolver_commitments",
    "detail.target.abl",
    "detail.target.letters_of_credit",
]
OPERATING_DEPS = [
    f"{role}.FY2024.{metric}"
    for role in ("acquirer", "target")
    for metric in (
        "revenue",
        "operating_profit",
        "depreciation_amortisation",
        "ebitda_reconciliation",
        "inventory",
        "receivables",
        "payables",
    )
] + [
    "detail.acquirer.leases",
    "detail.target.leases",
    "detail.acquirer.purchase_commitments",
    "detail.acquirer.other_liabilities",
    "detail.acquirer.cost_classification",
    "detail.target.cost_classification",
]


def assumptions(overrides=None):
    from .public_inputs import public_assumptions

    return public_assumptions(overrides)


def classify_gaps(gaps):
    result = []
    for g in gaps:
        if g["status"] != "Remaining":
            continue
        key = g["key"]
        m = key.rsplit(".", 1)[-1]
        if m in ("unrestricted_cash", "cash_restrictions"):
            category = "Private or unavailable information that may be bounded"
            effect = "Use verified accounting cash, project closing movements, then test 0-100% cash access. Do not assert the accessible fraction is a historical fact or legal availability."
        elif m in (
            "borrowing_base_and_letters_of_credit",
            "covenants_and_restricted_payments",
            "revolver_commitments",
        ):
            category = "Specific financing route or compliance claim"
            effect = "No post-close facility draws. ABL termination/LC treatment is a closing use. Borrowing-base/compliance certificates do not gate no-facility analytical capacity; actual compliance and availability remain blocked."
        elif m == "share_and_award_treatment":
            category = "Private or unavailable information that may be bounded"
            effect = "Known options have cash payoff between zero and 24 per option; director RSUs between zero and all disclosed RSUs; DSUs use disclosed count. Separate converted employee awards from common consideration. Unknown consent/withholding costs are not claimed bounded."
        elif m == "dividends_buybacks_commitments":
            category = "Private or unavailable information that may be bounded"
            effect = "Known declarations and accrued payments remain essential facts. Project future distributions at declared per-share rate; test zero/doubled future distributions. DKS disclosed 180 purchase commitments support a full-amount incremental stress, not a bound on all undisclosed FL obligations. Complete exceptional commitments remain unbounded."
        elif m in ("debt_principal", "instrument_inventory"):
            category = "Essential historical facts or contractual provisions"
            effect = "Model publicly disclosed note principal and FL aggregate finance-lease liability, not unsupported private instrument identities. Test the disclosed DKS other-liability envelope as a conservative extra cash reserve. Completeness of unreported debt is not asserted."
        elif m in (
            "lease_reconciliation",
            "maturity_and_amortisation_schedule",
            "coupons_and_resets",
        ):
            category = "Private or unavailable information that may be bounded"
            effect = "Use fixed-note contracts and aggregate disclosed lease cash maturities. Project lease principal using an explicit aggregate interest allocation; vary rate and tail timing. Instrument-level lease schedule and undisclosed early-termination/consent costs remain blocked."
        elif m == "change_of_control":
            category = "Essential historical facts or contractual provisions"
            effect = "Apply public merger ABL termination and elective note redemption provisions; do not require a future ratings event to be historical. Private lease consent obligations are not bounded, so no comprehensive actual-company preference."
        else:
            category = "Future modelling assumptions"
            effect = "Retain DKS notes without optional redemption; redeem FL notes under the published call grid. New rates/refinancing are explicit future scenarios, never committed liquidity. DKS make-whole quotes apply only if those notes are called."
        result.append(
            dict(
                **{k: v for k, v in g.items() if k != "classification"},
                classification=category,
                explanation=effect,
                strict_status=g["classification"],
                strict_materiality=g["materiality"],
            )
        )
    return result


def bridge(v, a):
    cap = v["detail.transaction.capitalization"]
    shares = (cap["acquirer_common"] + cap["acquirer_class_b"]) / 1000000.0
    quarterly = (
        v["detail.acquirer.planning_disclosures"][
            "declared_quarterly_dividend_per_share"
        ]
        * shares
    )
    result = []
    for i, role in enumerate(("acquirer", "target")):
        ytd = v[f"detail.{role}.ytd_cash_flow"]
        seasonal = ytd["capex"] / v[f"{role}.FY2024.capex"]
        wc = {
            m: v[f"{role}.FY2024.{m}"] for m in ("inventory", "receivables", "payables")
        }
        closing_wc = {m: wc[m] * a[f"closing_{m}_multiplier"][i] for m in wc}
        nwc_change = (
            closing_wc["inventory"]
            + closing_wc["receivables"]
            - closing_wc["payables"]
            - (wc["inventory"] + wc["receivables"] - wc["payables"])
        )
        reference_wc_cash = sum(v[f"detail.{role}.ytd_wc_cash"].values())
        pre_wc_cfo = (ytd["cfo"] - reference_wc_cash) * a["bridge_cfo_factors"][i]
        cfo = pre_wc_cfo - nwc_change
        capex = a["gross_annual_capex"][i] * seasonal
        dividends = quarterly * 3 * a["dividend_factor"] if i == 0 else 0.0
        buybacks = (
            v["detail.acquirer.distributions"]["accrued_buybacks"] if i == 0 else 0.0
        )
        fl = v["detail.target.finance_maturities"]
        lease_principal = (
            max(
                0,
                fl["annual_cash"][0] * 0.75 - fl["liability"] * a["lease_rate"] * 0.75,
            )
            if i == 1
            else 0.0
        )
        opening = v[f"detail.{role}.cash"]
        closing = opening + cfo - capex - dividends - buybacks - lease_principal
        result.append(
            dict(
                company=role,
                reported_working_capital=wc,
                closing_working_capital=closing_wc,
                projected_nwc_change=nwc_change,
                reference_wc_cash=reference_wc_cash,
                pre_working_capital_cfo=pre_wc_cfo,
                reported_cash=opening,
                projected_cfo=cfo,
                projected_gross_capex=capex,
                projected_dividends=dividends,
                accrued_buybacks_paid=buybacks,
                projected_lease_principal=lease_principal,
                projected_cash=closing,
                usable_cash=max(0, closing) * a["cash_access"] if i == 0 else 0.0,
                cash_availability_fraction=a["cash_access"] if i == 0 else 0.0,
                seasonal_capex_share=seasonal,
                bridge_check=closing
                - (opening + cfo - capex - dividends - buybacks - lease_principal),
                basis="Prior-year CFO removes separately disclosed trade-WC cash movements before forecast WC is deducted once. FL AR is not separately disclosed: held constant, other operating CF remains a proxy. This is a connected trade-WC bridge, not a full balance sheet.",
            )
        )
    return result


def construct(v, a):
    if a["closing_date"] != "2025-11-01":
        raise ValueError(
            "Public case currently supports November 1 close only; remap seasonal periods and call/accrual dates before changing it"
        )
    b = bridge(v, a)
    cap = v["detail.transaction.capitalization"]
    price = v["transaction.cash_price"]
    lower = cap["dsus"] * price / 1000000.0
    upper = (cap["dsus"] + cap["options"] + cap["rsus"]) * price / 1000000.0
    award = lower + (upper - lower) * a["award_fraction"]
    common = cap["target_common"] / 1000000.0
    fl = v["detail.target.finance_maturities"]
    coupon = v["detail.target.notes_terms"]["coupon"]
    principal = v["detail.target.notes_principal"]
    call = v["detail.target.notes_terms"]["redemption_oct2025"]
    premium = principal * (call - 1)
    accrued = principal * coupon / 12
    lc = v["detail.target.letters_of_credit"] * a["lc_collateral_factor"]
    other = v["detail.acquirer.other_liabilities"]
    extra_reserve = sum(other.values()) * a["other_liability_reserve"]
    purchase = (
        v["detail.acquirer.purchase_commitments"] * a["purchase_commitment_reserve"]
    )
    companies = []

    def debt(name, p, rate, maturity, **kw):
        return dict(
            id=name,
            principal=p,
            carrying_value=p,
            kind="fixed",
            rate=rate,
            spread=0.0,
            maturity=maturity,
            amortisation=0.0,
            optional=False,
            repay_at_close=False,
            preclose_repayment=0.0,
            **kw,
        )

    for i, role in enumerate(("acquirer", "target")):
        revenue = v[f"{role}.FY2024.revenue"]
        ebitda = v[f"{role}.FY2024.ebitda_reconciliation"]
        lease = v[f"detail.{role}.leases"]
        rent = (
            lease["operating_cost"]
            + lease["variable"]
            + lease["short_term"]
            - lease.get("sublease_income", 0)
        )
        rentcash = (
            lease["fixed_cash"]
            + lease["variable"]
            + lease["short_term"]
            - lease.get("sublease_income", 0)
        )
        reported = v[f"detail.{role}.cost_classification"]
        cash_cost_pool = revenue - ebitda - rent
        margin = 1 - cash_cost_pool * a["variable_cost_share"][i] / revenue
        variable = 0.0
        cogs = reported["cost_of_sales"]
        debts = []
        if i == 0:
            notes = v["detail.acquirer.notes"]
            for j, p in enumerate(v["detail.acquirer.notes_outstanding"]):
                debts.append(
                    debt(
                        "DKS notes " + str(2032 if j == 0 else 2052),
                        p,
                        notes["coupons"][j],
                        7.0 if j == 0 else 27.0,
                        maturity_date=notes["maturities"][j],
                    )
                )
        else:
            d = debt("FL notes redeemed", principal, coupon, 4.0)
            d["repay_at_close"] = True
            debts.append(d)
            cash = fl["annual_cash"]
            schedule = [cash[y] * 0.25 + cash[y + 1] * 0.75 for y in range(4)] + [
                a["lease_tail_cash"]
            ]
            d = debt(
                "FL aggregate finance leases",
                fl["liability"] - b[1]["projected_lease_principal"],
                a["lease_rate"],
                99.0,
                finance_lease=True,
                cash_payment_schedule=schedule,
            )
            debts.append(d)
        companies.append(
            dict(
                closing_working_capital=b[i]["closing_working_capital"],
                working_capital_cost_ratio=cogs / revenue,
                cost_reconciliation=dict(
                    reported=reported,
                    da_addback=v[f"{role}.FY2024.depreciation_amortisation"],
                    starting_ebitda=ebitda,
                    separate_lease_cost=rent,
                    nonrent_cash_cost_pool=cash_cost_pool,
                    assumed_variable_share=a["variable_cost_share"][i],
                ),
                name="DICK'S Sporting Goods" if i == 0 else "Foot Locker",
                revenue=revenue,
                gross_margin=margin,
                variable_opex=variable,
                fixed_opex=revenue * (margin - variable) - rent - ebitda,
                rent=rent,
                rent_cash_factor=rentcash / rent,
                operating_lease_liability=lease.get(
                    "liability",
                    lease.get("liability_ex_hfs", 0) + lease.get("hfs_liability", 0),
                ),
                da_ratio=v[f"{role}.FY2024.depreciation_amortisation"] / revenue,
                capex_ratio=a["gross_annual_capex"][i] / revenue,
                dio=v[f"{role}.FY2024.inventory"] / cogs * 365,
                dso=v[f"{role}.FY2024.receivables"] / revenue * 365,
                dpo=v[f"{role}.FY2024.payables"] / cogs * 365,
                growth=[a["growth"][i]] * 5,
                fixed_growth=a["fixed_cost_growth"],
                cash=b[i]["usable_cash"],
                cash_bridge=dict(operating=0.0, capex=0.0, dividends=0.0, buybacks=0.0),
                debts=debts,
                seasonality=[0.25] * 4,
                inventory_seasonality=[1.0] * 4,
            )
        )
    annualdiv = (
        v["detail.acquirer.planning_disclosures"][
            "declared_quarterly_dividend_per_share"
        ]
        * (cap["acquirer_common"] + cap["acquirer_class_b"])
        / 1000000.0
        * 4
        * a["dividend_factor"]
    )
    extra = (
        award
        + premium
        + accrued
        + lc
        + extra_reserve
        + purchase
        + a["extra_abl_payoff"]
        + max(0, -b[1]["projected_cash"])
        + max(0, -b[0]["projected_cash"])
    )
    c = dict(
        schema_version=2,
        mode="historical",
        label="PUBLIC INFORMATION — conditional projected case, not execution advice",
        closing_date=a["closing_date"],
        currency="USD millions",
        companies=companies,
        transaction=dict(
            target_shares=common,
            award_shares=0.0,
            cash_price=price,
            exchange_ratio=v["transaction.exchange_ratio"],
            acquirer_shares=(cap["acquirer_common"] + cap["acquirer_class_b"])
            / 1000000.0,
            mixed_stock_fraction=a["mixed_stock_fraction"],
            acquirer_reference_price=a["reference_share_price"],
            ev_other=0.0,
            transaction_fees=a["transaction_fees"],
            additional_uses=dict(
                award_settlement_reserve=award,
                redemption_premium=premium,
                accrued_interest=accrued,
                lc_collateral_reserve=lc,
                other_closing_uses=extra_reserve
                + purchase
                + a["extra_abl_payoff"]
                + max(0, -b[1]["projected_cash"])
                + max(0, -b[0]["projected_cash"]),
            ),
            fee_convention=a["fee_convention"],
            financing_fee_rate=a["fee"],
            allow_target_cash=False,
            target_cash_rationale="No target opening cash credited in public-case acquisition funding",
        ),
        new_debt=dict(
            kind="floating",
            benchmark=[a["benchmark"]] * 5,
            spread=a["spread"],
            fixed_benchmark=a["benchmark"],
            maturity=a["new_debt_maturity"],
            amortisation=a["new_debt_amortisation"],
        ),
        revolver=dict(
            commitment=0.0,
            borrowing_base=0.0,
            letters_of_credit=0.0,
            spread=0.0,
            maturity=5.0,
            max_gross_leverage=0.0,
        ),
        policy=dict(
            cash_floor=a["cash_floor"],
            max_leverage=a["max_leverage"],
            min_coverage=a["min_coverage"],
            tax_rate=a["tax_rate"],
            interest_deduction_limit=1.0,
            dividends=[annualdiv] * 5,
            buybacks=[0.0] * 5,
            sweep_fraction=1.0,
            refinance=a["refinance"],
            refinance_limit=a["refinance_limit"] if a["refinance"] else 0.0,
            refinance_tenor=a["refinance_tenor"],
            refinance_fee=a["fee"],
            operating_cash_access_fraction=a["operating_cash_access"],
        ),
        synergies=dict(
            run_rate=a["synergy"],
            ramp=a["synergy_ramp"],
            integration=[
                x * a["integration_multiplier"] for x in a["integration_costs"]
            ],
        ),
        quarterly=dict(
            enabled=False,
            label="Annual public-case projection; no claim of quarterly liquidity sufficiency",
        ),
    )
    for i, company in enumerate(c["companies"]):
        company["growth"] = (
            list(a["growth"][i])
            if isinstance(a["growth"][i], list)
            else [a["growth"][i]] * 5
        )
    uses = dict(
        known_award_cash_lower=lower,
        known_award_cash_upper=upper,
        projected_award_cash_reserve=award,
        fl_note_principal=principal,
        fl_note_premium=premium,
        fl_note_accrued_interest=accrued,
        lc_cash_collateral_reserve=lc,
        transaction_fees=a["transaction_fees"],
        other_liability_reserve=extra_reserve,
        purchase_commitment_reserve=purchase,
        projected_abl_payoff=a["extra_abl_payoff"],
        projected_preclose_cash_deficit_funding=max(0, -b[1]["projected_cash"])
        + max(0, -b[0]["projected_cash"]),
        total_fixed_closing_uses=a["transaction_fees"] + extra,
    )
    return (c, b, uses)


def analyse_public(evidence, gaps, full=True, overrides=None):
    v = {
        r["key"]: r["value"]
        for r in evidence["rows"]
        if r["classification"] == "verified fact"
    }
    missing = lambda deps: [d for d in deps if d not in v]
    deps = list(dict.fromkeys(BRIDGE_DEPS + CONTRACT_DEPS + OPERATING_DEPS))
    a = assumptions(overrides)
    result = dict(
        scope="Public-information conditional analysis; strict gate unchanged",
        assumptions=a,
        assumptions_id=fingerprint(a),
        gap_assessment=classify_gaps(gaps),
        output_policy=[],
        base=[],
        comparisons=[],
        capacity={},
        reverse_stress={},
        scenario_results=[],
        preferred_structure=None,
        unbounded_material_items=[
            "Undisclosed lease consent/change-of-control payments: public aggregate maturities do not cap these charges.",
            "Award tax/withholding, exceptional commitments and future changes in capitalization are not completely bounded by announcement-date aggregate counts.",
        ],
        conclusion=PREFIX
        + "only scoped scenario results; no overall financing preference is issued because material omitted private obligations are not bounded.",
        historical_complete=False,
    )
    for name, ds in [
        ("Projected closing bridge", BRIDGE_DEPS),
        ("Connected financing schedules", deps),
        ("Analytical debt capacity", deps),
    ]:
        result["output_policy"].append(
            dict(
                output=name,
                status="Blocked" if missing(ds) else "Conditional projection",
                missing_dependencies=missing(ds),
                dependencies=ds,
                limitation="Conditional on scope and assumptions; excludes unbounded consent/exceptional costs. No actual covenants or facility availability asserted.",
            )
        )
    for name in (
        "Actual covenant compliance",
        "Confirmed borrowing availability / lender appetite",
        "Executable financing / complete actual transaction uses",
        "Overall company-specific financing preference",
    ):
        result["output_policy"].append(
            dict(
                output=name,
                status="Blocked",
                missing_dependencies=[],
                dependencies=[],
                limitation="Outside analytical scope or unbounded material obligations; numerical feasibility cannot establish this claim.",
            )
        )
    if not missing(BRIDGE_DEPS):
        result["projected_bridge"] = bridge(v, a)
    if missing(deps):
        return result
    c, b, uses = construct(v, a)
    result.update(
        config=c,
        projected_bridge=b,
        uses_detail=uses,
        timing_basis="Annual; quarterly historical liquidity unsupported",
        cost_reconciliation=[x["cost_reconciliation"] for x in c["companies"]],
    )
    result["base"] = [run(c, s, Shock(margin=a["margin_shock"])) for s in STRUCTURES]
    for s in STRUCTURES:
        result["capacity"][s] = capacity(
            c, s, Shock(margin=a["margin_shock"]), grid=25.0, refinement=5.0
        )
        result["reverse_stress"][s] = reverse_stress(
            c, s, Shock(margin=a["margin_shock"]), step=0.01
        )
    scenarios = scenario_definitions(v, a, full)
    result["capacity_by_policy"] = {}
    result["scenario_context"] = {}
    result["investment_split"] = [
        dict(
            company=c["companies"][i]["name"],
            gross=a["gross_annual_capex"][i],
            assumed_maintenance=min(
                a["maintenance_capex"][i], a["gross_annual_capex"][i]
            ),
            residual_growth=max(
                0, a["gross_annual_capex"][i] - a["maintenance_capex"][i]
            ),
        )
        for i in range(2)
    ]
    for label, changes in scenarios:
        aa = {**a, **deepcopy(changes)}
        cc, bb, uu = construct(v, aa)
        rr = [
            run(cc, s, Shock(name=label, margin=aa["margin_shock"])) for s in STRUCTURES
        ]
        result["scenario_results"].extend(rr)
        result["scenario_context"][label] = dict(
            config=cc,
            projected_bridge=bb,
            investment_split=[
                dict(
                    company=cc["companies"][i]["name"],
                    gross=aa["gross_annual_capex"][i],
                    assumed_maintenance=min(
                        aa["maintenance_capex"][i], aa["gross_annual_capex"][i]
                    ),
                    residual_growth=max(
                        0, aa["gross_annual_capex"][i] - aa["maintenance_capex"][i]
                    ),
                )
                for i in range(2)
            ],
            cost_reconciliation=[x["cost_reconciliation"] for x in cc["companies"]],
        )
        result["comparisons"].append(
            dict(
                scenario=label,
                assumption_changes=changes,
                structures=[
                    dict(
                        structure=r["structure"],
                        feasible=r["feasible"],
                        new_debt=r["opening"]["total_new_borrowing"],
                        minimum_cash=r["min_cash"],
                        interest=r["total_interest"],
                        common_share_dilution=r["opening"]["ownership_dilution"],
                        first_breach=r["breaches"][0] if r["breaches"] else None,
                    )
                    for r in rr
                ],
                passing_structures=[r["structure"] for r in rr if r["feasible"]],
            )
        )
        if label in (
            "Lower reinvestment and dividends suspended",
            "No discretionary dividends",
            "Assumed term refinancing",
            "More fixed cost behaviour",
            "More variable cost behaviour",
            "Linked lower investment - mild",
            "Linked lower investment - stronger",
            "Fixed financing fee budget",
            "Central cost downside",
        ):
            result["capacity_by_policy"][label] = {
                s: capacity(
                    cc, s, Shock(margin=aa["margin_shock"]), grid=25.0, refinement=5.0
                )
                for s in STRUCTURES
            }
    for r in result["base"] + result["scenario_results"]:
        r["opening"]["enterprise_value"] = None
        r["opening"][
            "unsupported_enterprise_value_reason"
        ] = "Complete transaction EV reconciliation is outside the bounded common-share funding scope."
    result["field_definitions"] = {
        "transaction_fees": "Transaction expenses only. Award, redemption, collateral and other uses are separate itemised_uses fields.",
        "ownership_dilution": "Common-share issuance only, excluding converted awards; not complete diluted ownership.",
        "feasible": "Passes analytical cash/leverage/coverage/maturity screens only, not legal compliance.",
        "cash": "Model-accessible cash after an explicit assumption, not verified legal availability.",
        "capacity_none": "No borrowing point, including zero acquisition debt, passes all model constraints under the fixed operating/funding assumptions; not a claim of zero standalone lending capacity.",
    }
    result["comparison_summary"] = dict(
        tested_cases=len(scenarios),
        passes={
            s: sum((s in x["passing_structures"] for x in result["comparisons"]))
            for s in STRUCTURES
        },
        interpretation=PREFIX
        + "trade-offs between cash preservation, debt service and stock dilution within the specified scope. The tests are a finite scenario set, not proof over all continuous ranges; no universal preference follows.",
    )
    result["comparison_summary"]["conditions_with_a_passing_structure"] = [
        {"scenario": x["scenario"], "passing_structures": x["passing_structures"]}
        for x in result["comparisons"]
        if x["passing_structures"]
    ]
    return result


# Preserved implementation notes
# Nov 1 is 30 days after Oct 1 under the explicit 30/360 projection convention.
# 105% is an assumed cash-collateral reserve, not a verified release term.


def scenario_definitions(v, a, full):
    """Explicit stress assumptions; these do not alter any historical fact."""
    scenarios = [("Base", {})]
    if full:
        for cash, award, ops in product((0.0, 1.0), (0.0, 1.0), (0.0, 1.0)):
            scenarios.append(
                (
                    f"Envelope cash {cash:.0%}, awards {award:.0%}, CFO access {ops:.0%}",
                    dict(
                        cash_access=cash,
                        award_fraction=award,
                        operating_cash_access=ops,
                    ),
                )
            )
        scenarios += [
            (
                "Operating downside",
                dict(
                    growth=[-0.05, -0.1],
                    margin_shock=-0.01,
                    synergy=0.0,
                    integration_multiplier=2.0,
                ),
            ),
            ("No discretionary dividends", dict(dividend_factor=0.0)),
            ("Double distributions", dict(dividend_factor=2.0)),
            ("High rates/spreads", dict(benchmark=0.065, spread=0.045)),
            ("Low rates", dict(benchmark=0.025)),
            ("Financing fees 3%", dict(fee=0.03)),
            ("Preclose CFO downside", dict(bridge_cfo_factors=[0.5, 0.0])),
            (
                "Full ABL payoff stress",
                dict(
                    extra_abl_payoff=v["target.debt.revolver_commitments"]["commitment"]
                ),
            ),
            ("Disclosed other liabilities reserved", dict(other_liability_reserve=1.0)),
            (
                "Purchase commitments incremental stress",
                dict(purchase_commitment_reserve=1.0),
            ),
            ("Lease tail frontloaded", dict(lease_tail_cash=41.0, lease_rate=0.064)),
            ("Assumed term refinancing", dict(refinance=True)),
            ("Cash floor 500", dict(cash_floor=500.0)),
            ("Cash floor 1000", dict(cash_floor=1000.0)),
            ("Tighter leverage and coverage", dict(max_leverage=2.0, min_coverage=5.0)),
            ("Lower reinvestment", dict(gross_annual_capex=[900.0, 240.0])),
            ("High reinvestment", dict(gross_annual_capex=[1500.0, 400.0])),
        ]
    if full:
        scenarios += [
            (
                "Lower reinvestment and dividends suspended",
                dict(gross_annual_capex=[900.0, 240.0], dividend_factor=0.0),
            ),
            (
                "Lower reinvestment, no dividends, delayed synergies",
                dict(
                    gross_annual_capex=[900.0, 240.0], dividend_factor=0.0, synergy=0.0
                ),
            ),
        ]
    if full:
        scenarios += [
            ("Central cost downside", dict(growth=[-0.05, -0.1])),
            (
                "More fixed cost behaviour",
                dict(variable_cost_share=[0.65, 0.65], growth=[-0.05, -0.1]),
            ),
            (
                "More variable cost behaviour",
                dict(variable_cost_share=[0.95, 0.95], growth=[-0.05, -0.1]),
            ),
            (
                "Linked lower investment - mild",
                dict(
                    gross_annual_capex=[900.0, 240.0],
                    dividend_factor=0.0,
                    growth=[
                        [g - a["linked_growth_penalty"][0] for g in a["growth"][0]],
                        [g - a["linked_growth_penalty"][0] for g in a["growth"][1]],
                    ],
                ),
            ),
            (
                "Linked lower investment - stronger",
                dict(
                    gross_annual_capex=[900.0, 240.0],
                    dividend_factor=0.0,
                    growth=[
                        [g - a["linked_growth_penalty"][1] for g in a["growth"][0]],
                        [g - a["linked_growth_penalty"][1] for g in a["growth"][1]],
                    ],
                ),
            ),
            ("Fixed financing fee budget", dict(fee_convention="fixed_budget")),
        ]
    if full:
        scenarios += [
            (
                "High closing working capital",
                dict(
                    closing_inventory_multiplier=[1.28, 1.25],
                    closing_payables_multiplier=[1.05, 1.05],
                ),
            ),
            (
                "Low closing working capital",
                dict(
                    closing_inventory_multiplier=[1.08, 1.05],
                    closing_payables_multiplier=[1.25, 1.25],
                ),
            ),
        ]
    return scenarios
