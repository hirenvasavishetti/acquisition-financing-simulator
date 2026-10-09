"""Reproduce reviewed numerical extracts, not a download or automatic fact verifier.

These small factual archives were checked against the cited primary filings via
the browser on 2026-09-11/14. They are not original filing-byte archives. Re-review
the cited sections before editing or expanding this curated dataset.
"""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from financing.evidence import fingerprint


def main():
    directory = ROOT / "data/sources"
    directory.mkdir(parents=True, exist_ok=True)
    periods = {
        2024: ("2024-02-04", "2025-02-01"),
        2023: ("2023-01-29", "2024-02-03"),
        2022: ("2022-01-30", "2023-01-28"),
    }
    documents = {
        "announcement": dict(
            url="https://www.sec.gov/Archives/edgar/data/1089063/000119312525120243/d830209dex992.htm",
            published="2025-05-15",
            document_id="0001193125-25-120243 Exhibit 99.2",
            section="Additional Transaction Details; operating efficiencies",
        ),
        "dks10k": dict(
            url="https://www.sec.gov/Archives/edgar/data/1089063/000108906325000012/dks-20250201.htm",
            published="2025-03-27",
            document_id="0001089063-25-000012",
            section="Statements pp.46,48,50; Note 9",
        ),
        "fl10k": dict(
            url="https://www.sec.gov/Archives/edgar/data/850209/000143774925009620/floc20241213_10k.htm",
            published="2025-03-27",
            document_id="0001437749-25-009620",
            section="Statements pp.36,38,40; Notes 13,14",
        ),
    }
    observations = []
    by_source = {k: [] for k in documents}

    def add(
        source,
        key,
        value,
        start,
        end,
        units="USD millions",
        basis="Reported financial statement amount",
    ):
        obs = dict(
            key=key,
            value=value,
            kind="fact",
            origin=(
                "management_guidance"
                if key == "transaction.synergy_guidance"
                else "reported"
            ),
            company=key.split(".")[0],
            units=units,
            period_start=start,
            period_end=end,
            extraction_method="Reviewed numerical browser extraction; " + basis,
        )
        observations.append(obs)
        by_source[source].append(obs)

    for key, value, units in [
        ("cash_price", 24.0, "USD per share"),
        ("exchange_ratio", 0.1168, "acquirer shares per target share"),
        ("equity_value", 2400.0, "USD millions, approximate"),
        ("enterprise_value", 2500.0, "USD millions, approximate"),
        (
            "synergy_guidance",
            [100.0, 125.0],
            "USD millions, medium-term management guidance",
        ),
        (
            "election_restrictions",
            "No minimum or maximum cash/stock election amount",
            "contractual announcement term",
        ),
    ]:
        add(
            "announcement",
            "transaction." + key,
            value,
            "2025-05-15",
            "2025-05-15",
            units,
        )
    financial = {
        "acquirer": dict(
            revenue=[13442.849, 12984.399, 12368.198],
            operating_profit=[1473.932, 1282.365, 1463.019],
            depreciation_amortisation=[400.409, 393.933, 365.475],
            operating_cash_flow=[1311.835, 1527.335, 921.881],
            capex=[802.565, 587.426, 364.075],
            taxes=[399.467, 243.244, 306.612],
        ),
        "target": dict(
            revenue=[7988.0, 8168.0, 8759.0],
            operating_profit=[103.0, 142.0, 581.0],
            depreciation_amortisation=[202.0, 199.0, 208.0],
            operating_cash_flow=[345.0, 91.0, 173.0],
            capex=[240.0, 242.0, 285.0],
            taxes=[76.0, 97.0, 153.0],
        ),
    }
    for role, metrics in financial.items():
        source = "dks10k" if role == "acquirer" else "fl10k"
        for metric, values in metrics.items():
            for year, value in zip((2024, 2023, 2022), values):
                basis = (
                    "Cash income taxes paid, not provision"
                    if metric == "taxes"
                    else (
                        "Gross cash capital expenditures; positive outflow"
                        if metric == "capex"
                        else (
                            "Total revenue including licensing"
                            if metric == "revenue" and role == "target"
                            else (
                                "Cash-flow D&A line; DKS FY2022/23 includes disclosed impairments"
                                if metric == "depreciation_amortisation"
                                else "Statement amount; DKS thousands converted to millions"
                            )
                        )
                    )
                )
                add(
                    source,
                    f"{role}.FY{year}.{metric}",
                    value,
                    *periods[year],
                    basis=basis,
                )
    for role, values in [
        (
            "acquirer",
            {
                "inventory": [3349.830, 2848.797],
                "receivables": [214.250, 114.877],
                "payables": [1497.743, 1288.728],
            },
        ),
        ("target", {"inventory": [1525.0, 1509.0], "payables": [378.0, 366.0]}),
    ]:
        for metric, pair in values.items():
            for year, value in zip((2024, 2023), pair):
                end = periods[year][1]
                add(
                    "dks10k" if role == "acquirer" else "fl10k",
                    f"{role}.FY{year}.{metric}",
                    value,
                    end,
                    end,
                )
    # Facts about particular disclosed instruments are retained as documentary
    # context; complete instrument inventories/contract restrictions remain gaps.
    for source, role, value in [
        ("dks10k", "acquirer", 1484.217),
        ("fl10k", "target", 446.0),
    ]:
        add(
            source,
            f"{role}.opening.debt_carrying_value",
            value,
            "2025-02-01",
            "2025-02-01",
            basis="DKS senior-note carrying amount; FL notes plus finance-lease carrying amount. Not principal.",
        )
    sources = []
    for sid, doc in documents.items():
        archive = {
            "archive_type": "reviewed factual extraction, not original document bytes",
            **doc,
            "reviewed_on": "2026-09-14",
            "facts": by_source[sid],
        }
        path = directory / f"{sid}.json"
        path.write_text(
            json.dumps(archive, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        source = {
            **doc,
            "id": sid,
            "retrieved": "2026-09-14",
            "retrieval_precision": "day",
            "retrieval_basis": "Browser extraction reviewed 2026-09-11 and 2026-09-14; timestamp records archive review date",
            "archive_type": archive["archive_type"],
            "path": f"sources/{sid}.json",
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "claims": [],
        }
        for obs in by_source[sid]:
            payload = {
                k: obs[k]
                for k in (
                    "key",
                    "value",
                    "company",
                    "units",
                    "period_start",
                    "period_end",
                )
            }
            source["claims"].append(
                dict(
                    key=obs["key"],
                    payload_hash=fingerprint(payload),
                    section=doc["section"],
                    reviewer="Codex - machine-assisted primary-source review; not human sign-off",
                    reviewed_at="2026-09-14",
                    review_note=obs["extraction_method"],
                )
            )
        sources.append(source)
    case = dict(
        case="DICK'S Sporting Goods / Foot Locker",
        mode="historical",
        observations=observations,
        sources=sources,
        note="Partial reviewed source integration. No synthetic inputs or unsupported unrestricted-cash assumption. Contract terms, share/award bridge and forecast mappings remain blocked.",
    )
    (ROOT / "data/historical.json").write_text(
        json.dumps(case, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"{len(observations)} reviewed factual observations; {len(sources)} factual-extraction archives"
    )


if __name__ == "__main__":
    main()
