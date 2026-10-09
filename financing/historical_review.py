"""Dependency-gated partial history. No full funding preference or synthetic data."""

from .policy import REQUIREMENTS

ORIGINAL_GAPS = tuple(
    (
        r.key
        for r in REQUIREMENTS
        if r.key.startswith("assumption.")
        or r.key == "transaction.share_and_award_treatment"
        or ".debt." in r.key
        or (".opening." in r.key and (not r.key.endswith("debt_carrying_value")))
        or (
            ".FY2024." in r.key
            and r.key.rsplit(".", 1)[-1]
            in (
                "dividends_buybacks_commitments",
                "ebitda_reconciliation",
                "lease_reconciliation",
            )
        )
        or (r.key == "target.FY2024.receivables")
    )
)


def gap_register(case, evidence):
    lookup = {r["key"]: r for r in evidence["rows"]}
    result = []
    for key in ORIGINAL_GAPS:
        r = lookup[key]
        role = key.split(".")[0]
        metric = key.rsplit(".", 1)[-1]
        source = "review_dks" if role == "acquirer" else "review_fl"
        nature = "historical fact"
        app = "Required for all complete funding structures."
        current = ""
        missing = ""
        resolution = ""
        if metric in ("unrestricted_cash", "cash_restrictions"):
            current = "Feb 1 cash and equivalents: DKS 1689.940; FL 401, with separately restricted 29. Accounting balances are verified separately."
            missing = "Entity-level encumbrances, trapped/repatriable cash, minimum operating balances, and legally available cash at the selected closing date."
            resolution = "Treasury cash-by-entity/restriction schedule, credit security documents and counsel review; prospective cash bridge must remain a forecast."
            app = "Cash-first consumes availability. A zero contribution removes acquisition use, but group liquidity still cannot count restricted or inaccessible balances. No waiver applied."
        elif metric == "debt_principal":
            current = "DKS notes 750+750; FL notes 400 and finance-lease liability 50. Carrying amounts are separate."
            missing = (
                "DKS complete principal-to-balance-sheet reconciliation including any finance leases; no zero inferred from zero annual finance-lease payment."
                if role == "acquirer"
                else ""
            )
            resolution = "Debt Note 9 / Note 13 and lease liability ledger; exclude operating leases from financial-debt principal."
        elif metric == "ebitda_reconciliation":
            current = "Computed from verified FY2024 operating profit plus disclosed cash-flow D&A. No exceptional-item addbacks."
            resolution = "Code-owned sum with dependency checks. This resolves simple operating EBITDA, not covenant EBITDAR."
        elif metric == "receivables":
            current = (
                "FL Note 8 p54: net receivables 156 at Feb 1, 2025; 160 comparative."
            )
            resolution = "Exact units/date reviewed; feeds selected operating NWC, not all current assets."
        elif metric == "lease_reconciliation":
            current = "Rent cost components, fixed lease cash, operating liabilities, uncommenced commitments and FL finance cash are separately archived."
            missing = "Cash timing for variable/short-term rent, subleases and complete instrument finance-lease interest/principal schedules; reconcile held-for-sale treatment."
            resolution = "Lease Note 7 (DKS) / 16 (FL), lease payment ledger and explicit future rent assumptions. FL liability includes 5 held for sale outside main table."
        elif metric == "dividends_buybacks_commitments":
            current = "Cash-flow historical distributions and lease commitments disclosed; future discretionary distributions set to zero only as a scenario assumption."
            if role == "acquirer":
                current += " MD&A p36 discloses approximately 180 of non-cancellable purchase commitments, but not their annual cash timing."
            missing = "Reconciliation of declared/unpaid distributions and binding capex, purchase and lease commitments affecting the closing bridge and forecast."
            resolution = "Annual cash-flow statement, commitments notes, pre-cutoff dividend declarations, treasury payable and capital-commitment schedules."
        elif metric == "share_and_award_treatment":
            source = "merger"
            current = "May 12 common shares 95,560,582; options/RSUs/PSUs/DSUs counts and different settlement rules archived."
            missing = "Individual option strikes, director versus employee RSU split, PSU performance/award agreement settlement and award tax/withholding cash. Weighted-average strike cannot prove all options out of money."
            resolution = "Merger Sections 3.4/4.2; omitted Company Disclosure Letter 4.2 and equity-administration ledger. April 10 proxy is an earlier, incomplete employee population; later merger proxy excluded."
        elif ".debt." in key:
            nature = "conditionally applicable requirement"
            if metric == "revolver_commitments":
                current = "DKS unsecured 1600, Jan 14 2027; FL secured 600, June 20 2029. Both zero drawn at fiscal year-end. Uncommitted accordions excluded."
                resolution = "Annual debt notes verify contractual size and dates; does not resolve borrowing eligibility."
            elif metric == "borrowing_base_and_letters_of_credit":
                current = "DKS LC 19.9 against unsecured 1600; FL LC 7 against 600 commitment, subject to eligible inventory/reserves."
                missing = (
                    ""
                    if role == "acquirer"
                    else "Latest certified eligible collateral, reserves and LC replacement/cash-collateral terms."
                )
                resolution = "DKS Note 9; FL ABL borrowing-base certificate under agreement reporting provisions, held by Wells Fargo/borrower treasury."
                app = "Target ABL is terminated under merger 7.16(a); no post-close availability counted. Certificate matters for interim liquidity; funded payoff and LC replacement still matter for closing uses. No blanket waiver."
            elif metric == "covenants_and_restricted_payments":
                source = "dks_credit" if role == "acquirer" else "fl_credit"
                current = "DKS lease-adjusted maximum 3.75x; conditional acquisition election 4.25x. FL springing FCCR 1.00x plus restricted-payment conditions."
                missing = "Contractual numerator/denominator reconciliation, permitted debt and lien baskets, payment-condition capacity and post-acquisition eligibility."
                resolution = "Executed agreements and latest compliance certificates; counsel interpretation. Generic net-debt/EBITDA engine thresholds do not implement these covenants."
            elif metric == "instrument_inventory":
                current = "Bond series and aggregate lease liabilities disclosed; supplemental disclosures are not a complete executable instrument inventory."
                missing = "Complete lease/other borrowing register with principal, maturity, coupon, repayment and close treatment reconciled to debt notes."
                resolution = "Annual debt and lease notes, treasury debt ledger and all material financing leases."
            elif metric == "maturity_and_amortisation_schedule":
                current = "DKS bullets Jan 15 2032/2052; FL note Oct 1 2029; annual aggregate lease payments disclosed."
                missing = "Finance-lease principal versus interest allocation and instrument-level remaining payment dates; relative model maturity must use assumed closing date."
                resolution = "Original indentures plus lease amortisation ledger. Aggregate future minimum payments are not all principal."
            elif metric == "coupons_and_resets":
                current = "Fixed note coupons 3.15%/4.10% DKS and 4% FL; DKS SOFR margin 112.5bp at year-end, FL term-SOFR grid 150-200bp."
                missing = "Instrument lease effective interest schedules, applicable future facility pricing-grid/rating assumptions and resets."
                resolution = "Indentures and credit agreements plus lease ledger. Weighted-average lease discount rate is not each instrument coupon."
            elif metric == "change_of_control":
                source = "merger"
                current = "FL ABL termination required at closing. FL note offer 101% requires control AND ratings event. DKS purchase of target does not itself establish DKS control change."
                missing = "Facility and lease consent/default application, notes ratings-event assessment and exact retained versus redeemed treatment."
                resolution = "Merger 7.16, indenture definitions/4.10, ABL 8.01 and lease contracts; scenario-specific legal review."
            elif metric == "refinancing_and_repricing":
                source = "dks_indent" if role == "acquirer" else "fl_indent"
                current = "DKS pre-par make-whole; FL redemption 102% before Oct 1 2025, 101% until Oct 1 2026, then par, plus accrued interest."
                missing = "Scenario treatment for each instrument, accrued interest, notice timing and any lease termination/consent costs; actual future refinancing is not guaranteed."
                resolution = "Original indenture redemption sections and prospective quote sensitivities. Retained DKS notes with no optional redemption do not require a make-whole quote."
                app = "Retain versus redeem changes required calculations. Refinancing coupon/fees are future assumptions; existing call premium/consent rights remain historical facts. No waiver applied."
        elif key.startswith("assumption."):
            nature = "future modelling assumption"
            source = "Analyst assumption register"
            current = next(
                (o["rationale"] for o in case["observations"] if o["key"] == key),
                "No choice recorded",
            )
            resolution = "Explicit prospective choice; test uncertainty. Does not replace missing historical balance, rights or obligations."
            app = "Required when running the full prospective model. Partial studies disclose only the assumptions they consume."
        resolved = r["classification"] in (
            "verified fact",
            "explicit modelling assumption",
        )
        if resolved:
            missing = "None for this narrowly defined input; related financing dependencies remain separate."
        urls = [s["url"] for s in case.get("sources", []) if s["id"] == source]
        result.append(
            dict(
                key=key,
                classification=r["classification"],
                nature=nature,
                status="Resolved" if resolved else "Remaining",
                affected_calculation=r["affected_calculations"],
                materiality=r["materiality_reason"],
                current_evidence=current,
                missing_information=missing,
                primary_source="; ".join(urls) or source,
                proposed_resolution=resolution,
                applicability=app,
            )
        )
    return result


def supported_calculations(evidence):
    rows = {r["key"]: r for r in evidence["rows"]}
    out = []

    def calc(label, deps, fn, formula, limitation, units="USD millions"):
        missing = [
            d
            for d in deps
            if d not in rows or rows[d]["classification"] != "verified fact"
        ]
        out.append(
            dict(
                calculation=label,
                status="Unavailable" if missing else "Supported",
                value=None if missing else fn(*[rows[d]["value"] for d in deps]),
                units=units,
                formula=formula,
                dependencies=deps,
                missing_dependencies=missing,
                limitation=limitation,
            )
        )

    for role in ("acquirer", "target"):
        p = f"{role}.FY2024."
        calc(
            role + " FY2024 simple operating EBITDA",
            [p + "operating_profit", p + "depreciation_amortisation"],
            lambda a, b: a + b,
            "Operating profit + cash-flow D&A",
            "Not adjusted EBITDA or covenant EBITDAR; no addbacks.",
        )
        calc(
            role + " FY2024 CFO less gross capex",
            [p + "operating_cash_flow", p + "capex"],
            lambda a, b: a - b,
            "CFO - gross cash capital expenditures",
            "Historical residual, not forecast cash available for debt service; CFO includes interest/taxes and lease payments.",
        )
        calc(
            role + " FY2024 selected operating NWC",
            [p + "inventory", p + "receivables", p + "payables"],
            lambda a, b, c: a + b - c,
            "Inventory + receivables - payables",
            "Selected working capital only, not total current assets minus liabilities.",
        )
        calc(
            role + " Q4 CFO less gross capex",
            [p + "operating_cash_flow", p + "capex", f"detail.{role}.ytd_cash_flow"],
            lambda a, b, c: a - c["cfo"] - (b - c["capex"]),
            "(FY CFO - 39wk CFO) - (FY capex - 39wk capex)",
            "Derived 13 weeks Nov 3 2024-Feb 1 2025; demonstrates seasonality, not a forecast seed.",
        )
    calc(
        "FL cash reconciliation",
        ["detail.target.cash", "detail.target.restricted_cash"],
        lambda a, b: a + b["current"] + b["noncurrent"] - b["cash_flow_total"],
        "401 + 4 + 25 - 430 = 0",
        "Accounting reconciliation; no legal cash-release conclusion.",
    )
    calc(
        "FL financial debt principal",
        ["detail.target.notes_principal", "detail.target.finance_lease"],
        lambda a, b: a + b,
        "Notes principal + finance-lease liability",
        "Operating lease liabilities excluded; not complete instrument-level payment schedule.",
    )
    calc(
        "FL finance-lease rollforward check",
        ["detail.target.leases", "detail.target.finance_lease"],
        lambda a, b: a["finance_opening"]
        + a["finance_additions"]
        - (a["finance_cash"] - a["finance_interest"])
        - b,
        "Opening + additions - (cash paid - interest) - closing",
        "Aggregate liability check; cannot infer each future instrument principal payment.",
    )
    cap = "detail.transaction.capitalization"
    calc(
        "Common shares all-cash consideration",
        [cap, "transaction.cash_price"],
        lambda c, p: c["target_common"] * p / 1000000.0,
        "May 12 outstanding common shares x $24 / 1e6",
        "Common shares only: excludes awards, fees, debt, closing share changes and fractional-share payments.",
    )
    calc(
        "Common shares all-stock issuance",
        [cap, "transaction.exchange_ratio"],
        lambda c, x: c["target_common"] * x / 1000000.0,
        "May 12 outstanding common shares x 0.1168 / 1e6",
        "Election endpoint only, not predicted elections; excludes awards and fractional-share cash.",
        "million DKS shares",
    )
    calc(
        "DKS note annual coupon obligation",
        ["detail.acquirer.notes", "detail.acquirer.notes_outstanding"],
        lambda n, p: sum((a * b for a, b in zip(p, n["coupons"]))),
        "750 x 3.15% + 750 x 4.10%",
        "Original fixed notes only; no revolver, lease interest or refinancing.",
    )
    calc(
        "FL note annual coupon obligation",
        ["detail.target.notes_principal", "detail.target.notes_terms"],
        lambda p, n: p * n["coupon"],
        "400 x 4%",
        "Retained-note contractual coupon only; not total cash interest.",
    )
    return out


def financing_sensitivities(evidence):
    v = {
        r["key"]: r["value"]
        for r in evidence["rows"]
        if r["classification"] == "explicit modelling assumption"
    }
    out = []
    f = v.get("assumption.financing_terms_and_fees")
    if (
        isinstance(f, dict)
        and isinstance(f.get("new_debt"), dict)
        and isinstance(f["new_debt"].get("benchmark"), list)
        and f["new_debt"]["benchmark"]
        and isinstance(f["new_debt"].get("spread"), (int, float))
    ):
        for rate_shift in (-0.02, 0.0, 0.02):
            for spread_shift in (0.0, 0.01, 0.02):
                rate = (
                    max(0.0, f["new_debt"]["benchmark"][0] + rate_shift)
                    + f["new_debt"]["spread"]
                    + spread_shift
                )
                out.append(
                    dict(
                        study="Annual coupon per hypothetical 1000 new debt",
                        assumptions=f"Benchmark shift {rate_shift:+.2%}; spread shift {spread_shift:+.2%}",
                        value=1000 * rate,
                        units="USD millions/year",
                        limitation="Unit sensitivity, not actual debt size, quote, debt capacity or fixed legacy-note repricing.",
                    )
                )
        for fee in (0.01, 0.02, 0.03):
            out.append(
                dict(
                    study="Gross borrowing to net hypothetical 1000 proceeds",
                    assumptions=f"Upfront fee {fee:.0%}",
                    value=1000 / (1 - fee),
                    units="USD millions",
                    limitation="1000 is a unit scenario, not historical acquisition funding.",
                )
            )
    sy = v.get("assumption.synergy_delivery_and_costs")
    if (
        isinstance(sy, dict)
        and isinstance(sy.get("ramp"), list)
        and (len(sy["ramp"]) == 5)
        and isinstance(sy.get("integration"), list)
        and (len(sy["integration"]) == 5)
    ):
        for run_rate in (0.0, 100.0, 125.0):
            for delay in (0, 1):
                for cost_factor in (1.0, 2.0):
                    savings = sum(
                        (
                            run_rate * (sy["ramp"][y - delay] if y >= delay else 0.0)
                            for y in range(5)
                        )
                    )
                    out.append(
                        dict(
                            study="Five-year cumulative synergy less integration costs",
                            assumptions=f"Run rate {run_rate}; delay {delay}yr; cost multiplier {cost_factor}",
                            value=savings - sum(sy["integration"]) * cost_factor,
                            units="USD millions, pre-tax",
                            limitation="Hypothetical delivery and costs; no discounting/tax, financing or working-capital effects.",
                        )
                    )
    return out


def partial_sensitivities(evidence):
    """Bounded studies using historical anchors; deliberately no debt capacity."""
    v = {
        r["key"]: r["value"]
        for r in evidence["rows"]
        if r["classification"] == "verified fact"
    }
    out = []
    for role in ("acquirer", "target"):
        deps = [f"{role}.FY2024.{m}" for m in ("revenue", "ebitda_reconciliation")]
        if not all((d in v for d in deps)):
            continue
        revenue, ebitda = [v[d] for d in deps]
        for growth in (0.0, -0.05, -0.1):
            for margin_shift in (0.0, -0.01, -0.02):
                for year in range(1, 6):
                    projected = revenue * (1 + growth) ** year
                    out.append(
                        dict(
                            study="Hypothetical operating sensitivity; not actual company forecast or capacity",
                            company=role,
                            year=year,
                            annual_growth=growth,
                            margin_shift=margin_shift,
                            revenue=projected,
                            ebitda=projected * (ebitda / revenue + margin_shift),
                            dependencies=deps,
                            limitation="Constant stressed EBITDA margin; excludes synergies, integration, capex, taxes, rent cash and financing. No preferred structure.",
                        )
                    )
    return out
