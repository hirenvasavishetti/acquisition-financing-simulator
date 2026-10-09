"""Idempotent primary-source review supplement. Never fetches or fabricates facts.

Archives are reviewed factual extracts, not original filing bytes or human signoff.
Run after build_historical_register.py to reproduce the enhanced case.
"""

import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from financing.evidence import fingerprint


def main():
    path = ROOT / "data/historical.json"
    case = json.loads(path.read_text(encoding="utf-8"))
    docs = {
        "review_dks": (
            "https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm",
            "2025-03-27",
            "DKS FY2024 10-K",
        ),
        "review_fl": (
            "https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm",
            "2025-03-27",
            "FL FY2024 10-K",
        ),
        "merger": (
            "https://www.sec.gov/Archives/edgar/data/850209/000110465925049592/tm2515123d3_ex2-1.htm",
            "2025-05-15",
            "May 15 merger agreement, Exhibit 2.1; SEC acceptance 17:16:25",
        ),
        "dks_indent": (
            "https://www.sec.gov/Archives/edgar/data/1089063/000119312522009887/d285529dex42.htm",
            "2022-01-14",
            "DKS first supplemental indenture",
        ),
        "fl_indent": (
            "https://www.sec.gov/Archives/edgar/data/850209/000153949721001514/exh4-1_indenture.htm",
            "2021-10-05",
            "FL 2029 notes indenture",
        ),
        "dks_credit": (
            "https://www.sec.gov/Archives/edgar/data/1089063/000119312522009887/d285529dex101.htm",
            "2022-01-14",
            "DKS credit agreement",
        ),
        "fl_credit": (
            "https://www.sec.gov/Archives/edgar/data/850209/000143774924021177/ex_691205.htm",
            "2024-06-25",
            "FL amendment 4, executed June 20, 2024",
        ),
        "dks_q3": (
            "https://www.sec.gov/Archives/edgar/data/1089063/000108906324000121/dks-20241102.htm",
            "2024-11-27",
            "DKS Q3 2024 10-Q",
        ),
        "fl_q3": (
            "https://www.sec.gov/Archives/edgar/data/850209/000143774924037241/floc20241102_10q.htm",
            "2024-12-11",
            "FL Q3 2024 10-Q",
        ),
        "fl_prelim": (
            "https://www.sec.gov/Archives/edgar/data/850209/000110465925048852/tm2515123d1_ex99-1.htm",
            "2025-05-15",
            "FL preliminary Q1 2025 release",
        ),
    }
    docs["dks_prelim"] = (
        "https://www.sec.gov/Archives/edgar/data/1089063/000119312525120243/d830209dex991.htm",
        "2025-05-15",
        "DKS preliminary Q1 2025 release",
    )
    facts = {s: [] for s in docs}

    def add(
        s,
        key,
        value,
        section,
        start="2025-02-01",
        end="2025-02-01",
        units="USD millions",
    ):
        facts[s].append(
            dict(
                key=key,
                value=value,
                kind="fact",
                origin="reported",
                company=(
                    key.split(".")[1]
                    if key.startswith("detail.")
                    else key.split(".")[0]
                ),
                units=units,
                period_start=start,
                period_end=end,
                extraction_method="Machine-assisted primary-document review: "
                + section,
                section=section,
            )
        )

    add("review_fl", "target.FY2024.receivables", 156.0, "Note 8, p54: net receivables")
    add(
        "review_fl",
        "target.FY2023.receivables",
        160.0,
        "Note 8, p54: comparative net receivables",
        "2024-02-03",
        "2024-02-03",
    )
    add(
        "review_dks",
        "acquirer.debt.revolver_commitments",
        {
            "commitment": 1600.0,
            "drawn": 0.0,
            "maturity_date": "2027-01-14",
            "uncommitted_incremental_excluded": 500.0,
        },
        "Note 9, p62; commitment is not unconditional borrowing availability",
    )
    add(
        "review_dks",
        "acquirer.debt.borrowing_base_and_letters_of_credit",
        {
            "borrowing_base": 1600.0,
            "letters_of_credit": 19.9,
            "basis": "Unsecured commitment ceiling, subject to covenants; not an inventory borrowing base",
        },
        "Note 9, p62",
    )
    add(
        "review_fl",
        "target.debt.revolver_commitments",
        {
            "commitment": 600.0,
            "drawn": 0.0,
            "maturity_date": "2029-06-20",
            "uncommitted_total_ceiling_excluded": 750.0,
        },
        "Note 13, p57; availability subject to borrowing base",
    )
    add(
        "review_dks",
        "detail.acquirer.cash",
        1689.940,
        "Balance sheet p48, Note 1: cash and equivalents, NOT verified spendable acquisition cash",
    )
    add(
        "review_dks",
        "detail.acquirer.notes_outstanding",
        [750.0, 750.0],
        "Note 9: principal of 2032 and 2052 series at fiscal year-end",
    )
    add(
        "review_dks",
        "detail.acquirer.purchase_commitments",
        180.0,
        "MD&A p36 Contractual Obligations: approximate non-cancellable purchase commitments",
    )
    add(
        "review_fl",
        "detail.target.cash",
        401.0,
        "Balance sheet p36; excludes separately classified restricted cash",
    )
    add(
        "review_fl",
        "detail.target.restricted_cash",
        {"current": 4.0, "noncurrent": 25.0, "cash_flow_total": 430.0},
        "Note 1 pp43-44; primarily lease escrow and insurance cash trust",
    )
    add(
        "review_fl",
        "detail.target.notes_principal",
        400.0,
        "Note 13 p57: 4% notes; carrying 396 plus unamortized discount/costs 4",
    )
    add(
        "review_fl",
        "detail.target.finance_lease",
        50.0,
        "Notes 13 and 16: finance lease liability current 5 plus long-term 45; exclude operating leases",
    )
    add(
        "dks_indent",
        "detail.acquirer.notes",
        {
            "principal_each": 750.0,
            "coupons": [0.0315, 0.041],
            "maturities": ["2032-01-15", "2052-01-15"],
            "day_count": "30/360",
            "payment_months": [1, 7],
            "makewhole_spreads_bps": [25, 30],
        },
        "Sections 2.2-2.3; principal issuance corroborated by FY2024 Note 9",
        "2022-01-14",
        "2022-01-14",
        "USD millions; fractional annual coupons; dates",
    )
    add(
        "fl_indent",
        "detail.target.notes_terms",
        {
            "coupon": 0.04,
            "maturity": "2029-10-01",
            "redemption_oct2024": 1.02,
            "redemption_oct2025": 1.01,
            "redemption_oct2026": 1.0,
            "coc_offer": 1.01,
            "trigger": "Change of control AND ratings event; not signing alone",
        },
        "Definitions, Sections 3.07 and 4.10; note form",
        "2021-10-05",
        "2021-10-05",
        "fractions and contractual terms",
    )
    add(
        "merger",
        "detail.transaction.capitalization",
        {
            "target_common": 95560582,
            "target_treasury_excluded": 312977,
            "options": 1731169,
            "weighted_option_strike": 48.12,
            "rsus": 2635903,
            "psus_target": 1443467,
            "psus_max": 2749910,
            "dsus": 177680.622,
            "acquirer_common": 56475378,
            "acquirer_class_b": 23570633,
        },
        "Sections 4.2 and 5.2, capitalization date May 12; section 3.4 distinguishes award settlement",
        "2025-05-12",
        "2025-05-12",
        "shares; option strike USD/share",
    )
    add(
        "merger",
        "detail.transaction.debt_treatment",
        {
            "target_abl": "Terminate commitments, repay obligations and release liens at effective time; parent funds required",
            "notes": "Offers, consent solicitations, redemption or assumption routes; future outcome not established",
            "award_rule": "ITM options and DSUs cash; employee RSUs/PSUs adjusted parent awards; director RSUs cash",
        },
        "Sections 3.4 and 7.16(a)-(b); payoff letter due at least one business day before closing",
        "2025-05-15",
        "2025-05-15",
        "contractual terms",
    )
    add(
        "dks_credit",
        "detail.acquirer.covenant",
        {
            "maximum_lease_adjusted_leverage": 3.75,
            "acquisition_elected_limit": 4.25,
            "election_full_quarters": 4,
            "definition": "Borrowed debt plus operating lease liabilities / contractual EBITDAR; variable rental costs excluded from rental addback",
        },
        "Definitions and Section 6.12; election is conditional, not automatic",
        "2022-01-14",
        "2022-01-14",
        "multiples and contractual terms",
    )
    add(
        "fl_credit",
        "detail.target.abl",
        {
            "loan_cap": "Minimum of commitment and borrowing base",
            "springing_fccr": 1.0,
            "coc_voting_threshold": 0.4,
            "restriction": "Covenant Compliance Period trigger; restricted payments and collateral eligibility require full contract compliance",
        },
        "Definitions; Sections 7.06, financial covenant and 8.01(k); amendment annex",
        "2024-06-20",
        "2024-06-20",
        "multiples, fractions and contractual terms",
    )
    add(
        "review_dks",
        "detail.acquirer.leases",
        {
            "operating_cost": 636.744,
            "short_term": 26.186,
            "variable": 131.832,
            "sublease_income": 11.842,
            "fixed_cash": 708.988,
            "liability": 3003.543,
            "uncommenced_commitments": 352.1,
        },
        "Note 7 pp60-61; fixed liability cash excludes other rent categories",
    )
    add(
        "review_fl",
        "detail.target.leases",
        {
            "operating_cost": 643.0,
            "variable": 272.0,
            "short_term": 16.0,
            "fixed_cash": 723.0,
            "liability_ex_hfs": 2338.0,
            "hfs_liability": 5.0,
            "finance_cash": 8.0,
            "finance_interest": 2.0,
            "finance_opening": 52.0,
            "finance_additions": 4.0,
            "uncommenced_commitments": 41.0,
        },
        "Note 16 pp58-60; liabilities held for sale separately reported",
    )
    add(
        "dks_q3",
        "detail.acquirer.ytd_cash_flow",
        {"cfo": 680.307, "capex": 565.569},
        "Consolidated cash flows p7; thousands converted to millions",
        "2024-02-04",
        "2024-11-02",
    )
    add(
        "fl_q3",
        "detail.target.ytd_cash_flow",
        {"cfo": 98.0, "capex": 185.0},
        "Cash flows and liquidity free-cash-flow reconciliation",
        "2024-02-04",
        "2024-11-02",
    )
    add(
        "fl_prelim",
        "detail.target.preliminary_q1",
        {
            "comparable_sales_change": -0.026,
            "expected_net_loss": 363.0,
            "expected_non_gaap_net_loss": 6.0,
            "impairments": 276.0,
        },
        "Preliminary First Quarter Results; NOT full financial statements or EBITDA",
        "2025-02-02",
        "2025-05-03",
        "USD millions; fractional comparable sales change",
    )
    replaced = {o["key"] for group in facts.values() for o in group}
    add(
        "dks_prelim",
        "detail.acquirer.preliminary_q1",
        {
            "comparable_sales_growth": 0.045,
            "expected_eps": 3.24,
            "expected_non_gaap_eps": 3.37,
        },
        "Preliminary First Quarter Results; full results scheduled May 28, after cutoff",
        "2025-02-02",
        "2025-05-03",
        "fraction and USD/share",
    )
    replaced = {o["key"] for group in facts.values() for o in group}
    case["observations"] = [
        o
        for o in case["observations"]
        if o["key"] not in replaced and not o["key"].startswith("assumption.")
    ]
    case["sources"] = [s for s in case["sources"] if s["id"] not in docs]
    for sid, (url, published, title) in docs.items():
        archive = dict(
            archive_type="reviewed factual extraction, not original document bytes",
            url=url,
            published=published,
            document_id=title,
            reviewed_on="2026-09-14",
            facts=facts[sid],
        )
        ap = ROOT / "data/sources" / f"{sid}.json"
        ap.write_text(json.dumps(archive, indent=2), encoding="utf-8")
        source = dict(
            id=sid,
            url=url,
            published=published,
            document_id=title,
            retrieved="2026-09-14",
            path=f"sources/{sid}.json",
            sha256=sha256(ap.read_bytes()).hexdigest(),
            archive_type=archive["archive_type"],
            section="; ".join(sorted({o["section"] for o in facts[sid]})),
            claims=[],
        )
        for o in facts[sid]:
            source["claims"].append(
                dict(
                    key=o["key"],
                    payload_hash=fingerprint(
                        {
                            k: o[k]
                            for k in (
                                "key",
                                "value",
                                "company",
                                "units",
                                "period_start",
                                "period_end",
                            )
                        }
                    ),
                    section=o["section"],
                    reviewer="Codex machine-assisted review; not human signoff",
                    reviewed_at="2026-09-14",
                    review_note=o["extraction_method"],
                )
            )
            case["observations"].append(o)
        case["sources"].append(source)
    choices = {
        "analytical_thresholds": dict(
            cash_floor=750.0,
            max_leverage=3.0,
            min_coverage=4.0,
            tax_rate=0.25,
            interest_deduction_limit=1.0,
        ),
        "capital_allocation": dict(
            dividends=[0.0] * 5, buybacks=[0.0] * 5, sweep_fraction=0.0
        ),
        "synergy_delivery_and_costs": dict(
            run_rate=100.0,
            ramp=[0.0, 0.5, 1.0, 1.0, 1.0],
            integration=[100.0, 50.0, 25.0, 0.0, 0.0],
        ),
        "closing_bridge": dict(
            closing_date="2025-11-01",
            companies=[
                dict(operating=0.0, capex=0.0, dividends=0.0, buybacks=0.0)
                for _ in range(2)
            ],
        ),
        "operating_forecast": dict(
            companies=[
                dict(
                    gross_margin=0.35,
                    variable_opex=0.10,
                    capex_ratio=0.06,
                    growth=[0.0] * 5,
                    fixed_growth=0.02,
                    seasonality=[0.25] * 4,
                    inventory_seasonality=[1.0] * 4,
                ),
                dict(
                    gross_margin=0.30,
                    variable_opex=0.10,
                    capex_ratio=0.04,
                    growth=[-0.05, 0.0, 0.02, 0.02, 0.02],
                    fixed_growth=0.02,
                    seasonality=[0.25] * 4,
                    inventory_seasonality=[1.0] * 4,
                ),
            ],
            quarterly=dict(
                enabled=False, label="No assumed quarterly historical liquidity"
            ),
        ),
        "financing_terms_and_fees": dict(
            transaction=dict(
                transaction_fees=75.0,
                financing_fee_rate=0.02,
                ev_other=0.0,
                allow_target_cash=False,
                target_cash_rationale="Conservative future scenario choice; no upstream availability assumed",
                acquirer_reference_price=200.0,
            ),
            new_debt=dict(
                kind="floating",
                benchmark=[0.045] * 5,
                spread=0.025,
                fixed_benchmark=0.045,
                maturity=5.0,
                amortisation=0.02,
            ),
            policy=dict(
                refinance=False,
                refinance_limit=0.0,
                refinance_tenor=5.0,
                refinance_fee=0.02,
            ),
        ),
    }
    reasons = {
        "analytical_thresholds": "Analyst screening limits, not lender covenants or verified tax deductibility; test cash floors 500/750/1000 and leverage 2/3/4.",
        "capital_allocation": "Prospective suspension of discretionary distributions and optional repayments. Existing declared obligations remain separate missing facts, not zeroed.",
        "synergy_delivery_and_costs": "Future delivery/cost choices, not management cost guidance. Test run rates 0/100/125, one-year delay and doubled integration costs.",
        "closing_bridge": "Frozen-balance diagnostic at assumed November 1 close. Zero movements are NOT historical updates; no financing conclusion may rely on this diagnostic without opening-cash restrictions and intervening commitments.",
        "operating_forecast": "Explicit future cost decomposition and growth paths, not reported margins. Calibrate fixed expenses to verified operating EBITDA. Stress revenue and EBITDA margin; preliminary target Q1 deterioration makes flat extrapolation unreliable.",
        "financing_terms_and_fees": "Hypothetical future quote: 4.5% benchmark plus 250bp, 2% upfront, 75 transaction costs, stock reference 200. No claim these are committed financing or observed prices. Test rates +/-200bp, spreads +100/+200bp, fees 1/2/3%; historical redemption costs remain separate.",
    }
    for name, value in choices.items():
        case["observations"].append(
            dict(
                key="assumption." + name,
                value=value,
                kind="assumption",
                origin="analyst",
                rationale=reasons[name],
            )
        )
    case["note"] = (
        "Pre-cutoff primary evidence plus explicit prospective assumptions. Full financing remains blocked; bounded calculations exclude unsupported funding, awards and legal availability. No synthetic inputs."
    )
    path.write_text(json.dumps(case, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        "Enhanced historical case:",
        len(case["observations"]),
        "observations;",
        len(case["sources"]),
        "archives",
    )


if __name__ == "__main__":
    main()
