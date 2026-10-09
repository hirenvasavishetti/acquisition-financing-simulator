"""Two-page memo connected to model outputs, with historical status separate."""

from pathlib import Path
from xml.sax.saxutils import escape


def write_pdf(report, path):
    if report.get("model") or report.get("public_information", {}).get("base"):
        from .portfolio_memo import write_pdf as portfolio_pdf

        return portfolio_pdf(report, path)
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Table,
        TableStyle,
        PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            spaceAfter=7,
            textColor=colors.HexColor("#172C43"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallHead",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=9,
            spaceAfter=7,
            textColor=colors.HexColor("#172C43"),
        )
    )
    story = []

    def p(text, style="BodySmall"):
        story.append(Paragraph(escape(str(text)), styles[style]))

    def table(heads, rows, widths):
        data = [
            [Paragraph(escape(str(x)), styles["BodySmall"]) for x in row]
            for row in [heads] + rows
        ]
        t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E7EEF5")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.HexColor("#203D5B")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t)

    def f(x):
        return "n.a." if x is None else f"{x:,.1f}"

    m = report.get("model")
    p("Acquisition Financing & Debt Capacity", "Title")
    public = report.get("public_information")
    p(
        (
            "Public-information financing memo"
            if public
            else "Illustrative financing memo" if m else "Historical evidence review"
        )
        + " | USD millions | cutoff May 15, 2025"
    )
    p(report["recommendation_status"])
    p(
        "Historical company preference: "
        + (
            report.get("preferred_structure")
            or "None. Material evidence remains incomplete."
        )
    )
    if public:
        from .public_exports import pdf_story

        pdf_story(public, p, table, story, PageBreak)
    elif not m:
        p(
            report.get(
                "historical_capacity_status", "No complete model inputs supplied."
            )
        )
        p("Supported historical calculations", "SmallHead")
        for x in report.get("supported_historical_calculations", []):
            if x["status"] == "Supported":
                p(
                    x["calculation"]
                    + ": "
                    + f(x["value"])
                    + " "
                    + x["units"]
                    + ". "
                    + x["formula"]
                )
        p(
            "These are bounded historical reconciliations, not a complete acquisition financing analysis. Common consideration excludes awards, fees and debt. Simple operating EBITDA is not covenant EBITDAR."
        )
        story.append(PageBreak())
        p("Evidence resolution", "Title")
        reviewed = report.get("historical_gap_register", [])
        p(
            f"Original material gaps: {len(reviewed)}; resolved {sum((g['status'] == 'Resolved' for g in reviewed))}; remaining {sum((g['status'] == 'Remaining' for g in reviewed))}. Resolved future assumptions are not verified historical facts."
        )
        p("Material uncertainty", "SmallHead")
        p(
            "Spendable cash and intervening commitments, complete award settlement, instrument lease schedules, and contractual borrowing capacity remain unresolved. Foot Locker ABL termination requires funded payoff and LC treatment. Original indentures establish call terms, not the future outcome of rating events or consents."
        )
        p("Sensitivities", "SmallHead")
        p(
            "Operating study varies annual growth 0/-5/-10% and EBITDA margins 0/-100/-200bp. New-debt unit study varies benchmark +/-200bp, spread +0/100/200bp and fees 1/2/3%. Synergies use 0/100/125, one-year delay and doubled integration costs. Full funding capacity and liquidity reverse stress are unavailable; no synthetic substitution."
        )
        p(
            "See memo.md and the workbook Historical gap review for all 36 items, exact missing information, applicability and source references. All archives are machine-reviewed extracts, not original filing bytes or human signoff."
        )
        gaps = [
            x
            for x in report["evidence"]["rows"]
            if x["classification"] in ("missing evidence", "conflicting evidence")
            and x.get("recommendation_blocking", True)
        ]
        for x in gaps[:4]:
            p(x["key"] + ": " + x["resolution"])
    else:
        p(m["config"]["label"], "SmallHead")
        p(m["recommendation"]["narrative"])
        p("Base structures and trade-offs", "SmallHead")
        table(
            ["Structure", "Min cash", "Interest", "Dilution", "Base result"],
            [
                [
                    s["structure"],
                    f(s["min_cash"]),
                    f(s["total_interest"]),
                    f(s["opening"]["ownership_dilution"] * 100) + "%",
                    (
                        "Pass"
                        if s["feasible"]
                        else s["breaches"][0]["constraint"]
                        + " / Y"
                        + str(s["breaches"][0]["year"])
                    ),
                ]
                for s in m["base"]
            ],
            [125, 72, 72, 65, 156],
        )
        p("Opening funding and conditional capacity", "SmallHead")
        table(
            ["Structure", "New debt", "Retained debt", "Capacity", "Residual equity"],
            [
                [
                    s["structure"],
                    f(s["opening"]["total_new_borrowing"]),
                    f(s["opening"]["retained_debt"]),
                    f(m["capacity"][s["structure"]]["maximum_acquisition_borrowing"]),
                    f(m["capacity"][s["structure"]]["residual_analytical_equity"]),
                ]
                for s in m["base"]
            ],
            [125, 91, 91, 91, 92],
        )
        p(
            "Capacity holds transaction uses and each structure's cash contribution fixed. Acquisition debt replaces separate hypothetical equity funding, unrelated to transaction stock elections. The $10m grid is refined to $1m at observed feasibility boundaries. This is conditional model capacity, not lender appetite."
        )
        p("Capital allocation and assumptions", "SmallHead")
        policy = m["config"]["policy"]
        p(
            f"Analyst limits: cash floor {f(policy['cash_floor'])}, net leverage {policy['max_leverage']:.1f}x, interest coverage {policy['min_coverage']:.1f}x, and no unresolved maturity gap. Dividends and buybacks are explicit cash outflows. Fixed coupons are retained until refinancing. Target cash is unavailable in the demo."
        )
        p(
            "Any illustrative preference applies only to the fictional companies. Feasibility, interest, cash headroom, dilution and downside performance are assessed together; low debt alone does not select a structure."
        )
        story.append(PageBreak())
        p("Stress, liquidity and evidence", "Title")

        def outcome(structure, name):
            case = next(
                (
                    x
                    for x in m["comparisons"]
                    if x["structure"] == structure and x["scenario"] == name
                ),
                None,
            )
            return (
                "Not run" if case is None else "Pass" if case["feasible"] else "Breach"
            )

        table(
            [
                "Structure",
                "Moderate combined",
                "Severe combined",
                "Reverse revenue breach",
            ],
            [
                [
                    s["structure"],
                    outcome(s["structure"], "Moderate combined"),
                    outcome(s["structure"], "Severe combined"),
                    (
                        f(m["reverse_stress"][s["structure"]]["revenue_decline"] * 100)
                        + "%"
                        if m["reverse_stress"][s["structure"]].get("revenue_decline")
                        is not None
                        else "No breach in range"
                    ),
                ]
                for s in m["base"]
            ],
            [125, 115, 115, 135],
        )
        p(
            "Moderate/severe shocks: revenue -5%/-10%, gross margin -100/-200bp, inventory days +10/+20, benchmark and new spreads +100/+200bp, and delayed half/no synergies. Individual shocks are also calculated. EBITDA is not haircut a second time. A 0% reverse breach means the starting structure already fails."
        )
        p("Refinancing and quarterly liquidity", "SmallHead")
        table(
            [
                "Structure",
                "Assumed refinanced",
                "Refinancing case",
                "Quarterly min cash",
            ],
            [
                [
                    s["structure"],
                    f(s["total_refinancing"]),
                    "Pass" if s["feasible"] else "Breach",
                    (
                        f(
                            next(
                                (
                                    q
                                    for q in m["quarterly"]
                                    if q["structure"] == s["structure"]
                                )
                            )["min_cash"]
                        )
                        if m["quarterly"]
                        else "Not run"
                    ),
                ]
                for s in m["refinancing"]
            ],
            [125, 115, 115, 135],
        )
        p(
            "Assumed refinancing is limited future borrowing, not committed liquidity. The first two years have illustrative quarterly schedules, aggregated into the quarterly run's annual statements. Annual and quarterly interest differ with repayment timing. Neither establishes daily solvency."
        )
        p("Historical evidence gate", "SmallHead")
        verified = sum(
            (x["classification"] == "verified fact" for x in report["evidence"]["rows"])
        )
        gaps = [
            x
            for x in report["evidence"]["rows"]
            if x.get("recommendation_blocking", True)
            and x["classification"] in ("missing evidence", "conflicting evidence")
        ]
        p(
            f"{verified} verified factual rows including derived values; {len(gaps)} unresolved recommendation-blocking inputs. Key gaps: eligible cash, complete instrument/lease schedules, contractual borrowing capacity, commitments and award settlement. Six future assumption groups are explicit choices, not historical facts. See the workbook gap register."
        )
        p("Sources and reproducibility", "SmallHead")
        p(
            "Historical context: DICK'S and Foot Locker FY2024 10-Ks filed 27 March 2025; acquisition announcement Exhibit 99.2 dated 15 May 2025. Local archives are reviewed factual extracts, not original filing bytes. No later outcomes or synthetic values enter historical results."
        )
        p(
            "Source URLs and review provenance: data/historical.json and workbook Sources. Input ID: "
            + report.get("config_id", "n.a.")[:24]
            + ". Code ID: "
            + m["code_id"][:24]
            + ". Reproduce with README commands. AI-assisted implementation and source extraction; no human review is claimed."
        )

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#526477"))
        canvas.drawString(
            40,
            24,
            (
                "Illustrative analysis; historical status shown separately"
                if m
                else "Historical evidence review; no company-specific financing preference"
            ),
        )
        canvas.drawRightString(550, 24, str(doc.page) if public else f"{doc.page} / 2")

    SimpleDocTemplate(
        str(path),
        pagesize=(595.28, 841.89),
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=40,
    ).build(story, onFirstPage=footer, onLaterPages=footer)
