"""Required coverage is code-owned; an input file cannot make facts optional."""

from dataclasses import dataclass

CUTOFF = "2025-05-15"
BLOCKED = "Blocked — insufficient verified evidence."
VERIFIED = "Evidence verified — financial-analysis review still required."
CLASSES = (
    "verified fact",
    "explicit modelling assumption",
    "missing evidence",
    "conflicting evidence",
)


@dataclass(frozen=True)
class Requirement:
    key: str
    category: str
    affects: str
    resolution: str
    assumption_allowed: bool = False


def requirements():
    rows = []

    def add(key, category, affects, resolution, assumption=False):
        rows.append(Requirement(key, category, affects, resolution, assumption))

    for metric in (
        "cash_price",
        "exchange_ratio",
        "equity_value",
        "enterprise_value",
        "share_and_award_treatment",
        "election_restrictions",
        "synergy_guidance",
    ):
        add(
            f"transaction.{metric}",
            "material transaction terms",
            "Consideration bridge, cash uses, stock issuance and synergy scenarios",
            "Review pre-cutoff announcement/merger agreement; record exact term and section.",
        )
    for company in ("acquirer", "target"):
        for metric in (
            "unrestricted_cash",
            "cash_restrictions",
            "debt_principal",
            "debt_carrying_value",
        ):
            add(
                f"{company}.opening.{metric}",
                "opening cash and debt",
                "Opening liquidity, retained debt, cash deployment and leverage",
                "Reconcile latest pre-cutoff balance sheet and notes, with balance date and units.",
            )
        for year in (2022, 2023, 2024):
            for metric in (
                "revenue",
                "operating_profit",
                "depreciation_amortisation",
                "ebitda_reconciliation",
                "operating_cash_flow",
                "capex",
                "taxes",
                "inventory",
                "receivables",
                "payables",
                "lease_reconciliation",
                "dividends_buybacks_commitments",
            ):
                add(
                    f"{company}.FY{year}.{metric}",
                    "operating financials",
                    "Operating forecast, EBITDA, working capital and debt-service cash flow",
                    "Review original pre-cutoff fiscal accounts; record exact fiscal dates, units and reconciliation.",
                )
        for metric, category, effect in (
            (
                "instrument_inventory",
                "debt maturities",
                "Completeness of instrument debt schedule",
            ),
            (
                "maturity_and_amortisation_schedule",
                "debt maturities",
                "Mandatory repayments and maturity gaps",
            ),
            (
                "coupons_and_resets",
                "financing provisions",
                "Cash interest and rate stress",
            ),
            (
                "change_of_control",
                "financing provisions",
                "Required repayment and retained debt",
            ),
            (
                "refinancing_and_repricing",
                "financing provisions",
                "Refinancing dependence and debt service",
            ),
            (
                "revolver_commitments",
                "borrowing restrictions",
                "Eligible committed liquidity",
            ),
            (
                "borrowing_base_and_letters_of_credit",
                "borrowing restrictions",
                "Revolver draw limits",
            ),
            (
                "covenants_and_restricted_payments",
                "borrowing restrictions",
                "Borrowing eligibility and capital allocation",
            ),
        ):
            add(
                f"{company}.debt.{metric}",
                category,
                effect,
                "Review debt notes and executed agreements for every instrument; reconcile totals, cite sections and document any non-applicability.",
            )
    for metric in (
        "closing_bridge",
        "operating_forecast",
        "synergy_delivery_and_costs",
        "financing_terms_and_fees",
        "analytical_thresholds",
        "capital_allocation",
    ):
        add(
            f"assumption.{metric}",
            "modelling choices",
            "Forecast, liquidity and scenario comparisons",
            "Record explicit future scenario choice and rationale separately from historical facts.",
            True,
        )
    return tuple(rows)


REQUIREMENTS = requirements()
SUPPLEMENTAL = {
    key: Requirement(
        key,
        "supporting historical disclosure",
        "Bounded historical calculation; not complete financing capacity",
        "Review exact pre-cutoff document, units and period.",
    )
    for key in (
        "detail.acquirer.cash",
        "detail.target.cash",
        "detail.target.restricted_cash",
        "detail.target.notes_principal",
        "detail.target.finance_lease",
        "detail.acquirer.notes",
        "detail.target.notes_terms",
        "detail.transaction.capitalization",
        "detail.transaction.debt_treatment",
        "detail.acquirer.covenant",
        "detail.target.abl",
        "detail.acquirer.leases",
        "detail.target.leases",
        "detail.acquirer.ytd_cash_flow",
        "detail.target.ytd_cash_flow",
        "detail.target.preliminary_q1",
        "detail.acquirer.preliminary_q1",
        "detail.acquirer.notes_outstanding",
        "detail.acquirer.purchase_commitments",
        "detail.target.finance_maturities",
        "detail.acquirer.distributions",
        "detail.acquirer.other_liabilities",
        "detail.acquirer.planning_disclosures",
        "detail.target.letters_of_credit",
        "detail.acquirer.cost_classification",
        "detail.target.cost_classification",
        "detail.acquirer.ytd_wc_cash",
        "detail.target.ytd_wc_cash",
    )
}


def materiality(key, context=None):
    """Code-owned dependency policy; missing trend evidence is never called verified.

    Context is selected by the model integration, not observation material flags.
    The v2 engine uses explicit future growth, not an historical trend regression.
    """
    context = context or {}
    if key in SUPPLEMENTAL:
        return (
            False,
            "Supplementary disclosure; each bounded calculation independently requires verified dependencies. Original financing requirements remain active.",
        )
    if ".FY2022." in key or ".FY2023." in key:
        return (
            bool(context.get("historical_trend_calibration")),
            "Prior-year trend/reconciliation context. Blocks only when historical trend calibration is used; explicit forecast growth does not consume it.",
        )
    if key.endswith("debt_carrying_value"):
        return (
            False,
            "Accounting reconciliation only; cash debt service uses verified principal, not carrying value. Missing reconciliation remains disclosed.",
        )
    if key in ("transaction.equity_value", "transaction.enterprise_value"):
        return (
            False,
            "Headline comparison only. Consideration is calculated from verified price, shares and award treatment; discrepancies remain disclosed.",
        )
    if key == "transaction.synergy_guidance" and context.get("zero_synergies", False):
        return (
            False,
            "Zero-synergy scenario consumes no management synergy guidance; zero remains an explicit future modelling choice.",
        )
    if key == "transaction.exchange_ratio" and context.get("cash_only", False):
        return (
            False,
            "No stock election is analysed. Any mixed-consideration comparison reactivates this requirement.",
        )
    if key.endswith("FY2024.dividends_buybacks_commitments"):
        return (
            True,
            "Contractual capital commitments can compete with debt service; discretionary future distributions are separate explicit assumptions.",
        )
    if ".FY2024." in key:
        return (
            True,
            "Latest standalone operating base drives forecast EBITDA, cash taxes, working capital and cash available for debt service.",
        )
    if ".opening." in key:
        return (
            True,
            "Opening liquidity and debt determine spendable cash, financing need and net leverage; a wrong balance can falsely imply funding.",
        )
    if ".debt." in key:
        return (
            True,
            "Instrument rights determine mandatory repayments, coupon resets and legally available borrowing; numerical solvency cannot replace contract evidence.",
        )
    if key.startswith("assumption."):
        return (
            True,
            "Future choice controls forecast or funding mechanics; explicit rationale is required, but it is not a historical fact.",
        )
    return (
        True,
        "Material transaction or unregistered model dependency: unsupported consideration or scope can change financing needs.",
    )


# Preserved implementation notes
# These extra disclosures cannot replace the original 109 financing requirements.
