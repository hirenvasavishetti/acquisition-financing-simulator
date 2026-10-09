"""Verify exported public-case dependencies, model identities and saved artifacts."""

import json, sqlite3, sys
from pathlib import Path
from financing.policy import BLOCKED


def main():
    out = Path(sys.argv[1])
    r = json.loads((out / "report.json").read_text(encoding="utf-8"))
    p = r["public_information"]
    assert (
        r["recommendation_status"] == BLOCKED and not r["historical_analysis_complete"]
    )
    assert (
        not r["historical_results"]
        and not r["illustrative_results"]
        and "model" not in r
    )
    assert p["preferred_structure"] is None and len(p["gap_assessment"]) == 23
    assert len(p["comparisons"]) >= 34 and all(
        len(x["structures"]) == 3 for x in p["comparisons"]
    )
    assert {"More fixed cost behaviour", "Linked lower investment - stronger"} <= {
        x["scenario"] for x in p["comparisons"]
    }
    for b in p["base"]:
        assert abs(b["opening"]["sources_uses_difference"]) < 1e-6
        assert b["opening"]["enterprise_value"] is None
        assert p["capacity"][b["structure"]]["maximum_acquisition_borrowing"] is None
        assert p["reverse_stress"][b["structure"]]["revenue_decline"] == 0
        for y in b["years"]:
            assert abs(y["cash_check"]) < 1e-6 and abs(y["debt_check"]) < 1e-6
            assert y["revolver_draw"] == y["available_revolver"] == 0
    import openpyxl
    from pypdf import PdfReader

    w = openpyxl.load_workbook(out / "evidence-review.xlsx", data_only=True)
    assert len(w.sheetnames) == 28 and w["Summary"]["B3"].value == BLOCKED
    assert (
        abs(
            w["Projected closing bridge"]["H5"].value
            - p["projected_bridge"][0]["projected_cash"]
        )
        < 1e-6
    )
    for i, b in enumerate(p["base"]):
        for j, y in enumerate(b["years"]):
            n = 5 + i * 5 + j
            assert (
                abs(w["Public cash and debt"][f"M{n}"].value - y["closing_cash"]) < 1e-6
            )
            assert (
                abs(w["Public cash and debt"][f"O{n}"].value - y["closing_debt"]) < 1e-6
            )
    for s in w:
        for row in s:
            assert not any(c.data_type == "e" for c in row), s.title
    w.close()
    pdf = PdfReader(out / "financing-memo.pdf")
    assert len(pdf.pages) == 2
    text = " ".join(page.extract_text() for page in pdf.pages)
    assert (
        "Public-information" in text
        and "Blocked" in text
        and "Under the stated public-information assumptions" in text
    )
    for name in ("dashboard.html", "memo.md"):
        text = (out / name).read_text(encoding="utf-8")
        assert BLOCKED in text and "Projected closing bridge" in text
    conn = sqlite3.connect(out / "model.sqlite")
    try:
        assert any(
            json.loads(row[0]) == p
            for row in conn.execute("SELECT payload FROM public_information_reviews")
        )
    finally:
        conn.close()
    print(
        "Public outputs verified: scenario identities, 28 sheets, two-page memo; strict block preserved."
    )


if __name__ == "__main__":
    main()
