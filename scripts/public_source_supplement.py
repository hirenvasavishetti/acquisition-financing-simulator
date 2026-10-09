"""Reviewed additions for the public-information case, without changing strict gaps."""

import json, sys
from pathlib import Path
from hashlib import sha256

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from financing.evidence import fingerprint


def main():
    path = ROOT / "data/historical.json"
    case = json.loads(path.read_text(encoding="utf-8"))
    specs = [
        (
            "public_fl",
            "review_fl",
            [
                (
                    "detail.target.finance_maturities",
                    {
                        "annual_cash": [7.0, 6.0, 5.0, 4.0, 4.0],
                        "thereafter_cash": 40.0,
                        "total_cash": 66.0,
                        "unearned_interest": 16.0,
                        "liability": 50.0,
                        "weighted_discount_rate": 0.044,
                    },
                    "Note 16 pp59-60; FY2025-2029 and thereafter, not calendar years; discount rate is aggregate",
                )
            ],
        ),
        (
            "public_dks",
            "review_dks",
            [
                (
                    "detail.acquirer.distributions",
                    {
                        "dividends": 361.727,
                        "cash_buybacks": 263.021,
                        "accrued_buybacks": 5.0,
                    },
                    "FY2024 cash flows p50 and supplemental noncash information",
                ),
                (
                    "detail.acquirer.other_liabilities",
                    {
                        "accrued_expenses": 653.324,
                        "current_other": 82.696,
                        "long_term_other": 42.137,
                    },
                    "Balance sheet p48 and Deferred revenue and other liabilities table; excludes gift cards, loyalty and deferred compensation",
                ),
                (
                    "detail.acquirer.planning_disclosures",
                    {
                        "fy2025_net_capex_guidance": 1000.0,
                        "declared_quarterly_dividend_per_share": 1.2125,
                        "declaration_date": "2025-03-10",
                        "payment_date": "2025-04-11",
                    },
                    "MD&A pp34-35 Capital Expenditures and Dividends; net capex is management guidance, dividend is a declaration",
                ),
            ],
        ),
    ]
    for sid, old, items in specs:
        if sid == "public_fl":
            items.append(
                (
                    "detail.target.letters_of_credit",
                    7.0,
                    "Note 13 p57: outstanding letters of credit at February 1, 2025",
                )
            )
        source0 = next(s for s in case["sources"] if s["id"] == old)
        observations = []
        for key, value, section in items:
            date = (
                "2025-03-27" if key.endswith("planning_disclosures") else "2025-02-01"
            )
            units = "USD millions"
            if key.endswith("finance_maturities"):
                units += "; weighted discount rate fraction"
            if key.endswith("planning_disclosures"):
                units += "; dividend USD/share; dates ISO 8601"
            start = "2024-02-04" if key.endswith("distributions") else date
            observations.append(
                dict(
                    key=key,
                    value=value,
                    kind="fact",
                    origin="reported",
                    company=key.split(".")[1],
                    units=units,
                    period_start=start,
                    period_end=date,
                    extraction_method="Machine-assisted review of primary filing: "
                    + section,
                    section=section,
                )
            )
        archive = {
            "archive_type": "reviewed factual extraction, not original document bytes",
            "url": source0["url"],
            "published": source0["published"],
            "reviewed_on": "2026-09-15",
            "facts": observations,
        }
        target = ROOT / "data/sources" / f"{sid}.json"
        target.write_text(json.dumps(archive, indent=2), encoding="utf-8")
        source = {
            **source0,
            "id": sid,
            "path": f"sources/{sid}.json",
            "retrieved": "2026-09-15",
            "sha256": sha256(target.read_bytes()).hexdigest(),
            "section": "; ".join(x[2] for x in items),
            "claims": [],
        }
        for o in observations:
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
                    reviewer="Codex machine-assisted primary-source review; no human signoff",
                    reviewed_at="2026-09-15",
                    review_note=o["extraction_method"],
                )
            )
        keys = {o["key"] for o in observations}
        case["observations"] = [
            o for o in case["observations"] if o["key"] not in keys
        ] + observations
        case["sources"] = [s for s in case["sources"] if s["id"] != sid] + [source]
    from financing.evidence import check_evidence
    from financing.public_case import bridge, assumptions

    e = check_evidence(case, ROOT / "data")
    values = {
        r["key"]: r["value"]
        for r in e["rows"]
        if r["classification"] == "verified fact"
    }
    projected = bridge(values, assumptions())
    choice = next(
        o for o in case["observations"] if o["key"] == "assumption.closing_bridge"
    )
    choice["value"] = {
        "closing_date": "2025-11-01",
        "companies": [
            dict(
                operating=b["projected_cfo"],
                capex=b["projected_gross_capex"],
                dividends=b["projected_dividends"],
                buybacks=b["accrued_buybacks_paid"],
                projected_lease_principal=b["projected_lease_principal"],
            )
            for b in projected
        ],
    }
    choice["rationale"] = (
        "Projected 39-week bridge removes separately disclosed prior-year trade-WC movements before applying explicit closing-WC forecasts once; capex uses verified FY2024 seasonal calibration; not actual FY2025 interim balances. Lease principal must also map to the debt inventory. Public case applies separate cash-access assumptions. Supersedes frozen-balance diagnostic."
    )
    path.write_text(json.dumps(case, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
