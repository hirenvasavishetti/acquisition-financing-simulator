"""Primary-source spot checks recorded 19 September 2026; all filings pre-cutoff."""

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
            "cost_dks",
            "review_dks",
            "detail.acquirer.cost_classification",
            dict(
                revenue=13442.849,
                cost_of_sales=8617.153,
                sga=3294.272,
                other_operating=57.492,
                operating_profit=1473.932,
            ),
            "FY2024 income statement p46; MD&A p32 and Note 1 p55: cost of sales includes occupancy and depreciation; not all variable.",
        ),
        (
            "cost_fl",
            "review_fl",
            "detail.target.cost_classification",
            dict(
                revenue=7988.0,
                cost_of_sales=5666.0,
                sga=1920.0,
                separate_da=202.0,
                other_operating=97.0,
                operating_profit=103.0,
                merchandise_cost=4674.0,
                occupancy_buyers=992.0,
            ),
            "FY2024 operations p36; MD&A p26; Note 16: store lease costs in cost of sales, non-store in SG&A. No impairment add-back.",
        ),
        (
            "wc_dks",
            "dks_q3",
            "detail.acquirer.ytd_wc_cash",
            dict(inventory=-877.115, receivables=-25.055, payables=404.685),
            "39-week cash flow statement p8: signed CFO contributions; thousands converted to USD millions.",
        ),
        (
            "wc_fl",
            "fl_q3",
            "detail.target.ytd_wc_cash",
            dict(inventory=-243.0, payables=137.0),
            "39-week cash flow statement p5: signed CFO contributions. Receivables are not separately disclosed; retain other cash-flow proxy and hold closing AR constant.",
        ),
    ]
    for sid, parent, key, value, section in specs:
        base = next(s for s in case["sources"] if s["id"] == parent)
        end = "2024-11-02" if sid.startswith("wc") else "2025-02-01"
        observation = dict(
            key=key,
            value=value,
            kind="fact",
            origin="reported",
            company=key.split(".")[1],
            units="USD millions",
            period_start="2024-02-04",
            period_end=end,
            section=section,
            extraction_method="Machine-assisted primary filing spot check; no independent human review",
        )
        archive = dict(
            url=base["url"],
            published=base["published"],
            reviewed_on="2026-09-19",
            archive_type="reviewed factual extraction, not original document bytes",
            facts=[observation],
        )
        local = ROOT / "data/sources" / f"{sid}.json"
        local.write_text(json.dumps(archive, indent=2), encoding="utf-8")
        source = {
            **base,
            "id": sid,
            "path": f"sources/{sid}.json",
            "retrieved": "2026-09-19",
            "section": section,
            "sha256": sha256(local.read_bytes()).hexdigest(),
            "claims": [
                dict(
                    key=key,
                    payload_hash=fingerprint(
                        {
                            k: observation[k]
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
                    section=section,
                    reviewer="Codex machine-assisted review; no human signoff",
                    reviewed_at="2026-09-19",
                    review_note=section,
                )
            ],
        }
        case["observations"] = [o for o in case["observations"] if o["key"] != key] + [
            observation
        ]
        case["sources"] = [s for s in case["sources"] if s["id"] != sid] + [source]
    path.write_text(json.dumps(case, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
