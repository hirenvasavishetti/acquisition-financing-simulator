"""Concise model-derived memo; detailed source review stays in the register."""

from pathlib import Path
from xml.sax.saxutils import escape


def content(report):
    public = report.get("public_information")
    model = public or report.get("model")
    if not model or not model.get("base"):
        return None
    base = model["base"]
    conclusion = (
        public["conclusion"] if public else model["recommendation"]["narrative"]
    )
    timing = "Annual public projection" if public else model["timing_basis"]
    drivers = []
    if public:
        names = (
            "Lower reinvestment and dividends suspended",
            "Lower reinvestment, no dividends, delayed synergies",
            "Linked lower investment - mild",
            "Linked lower investment - stronger",
            "Central cost downside",
            "More fixed cost behaviour",
            "More variable cost behaviour",
        )
        for s in public["comparisons"]:
            if s["scenario"] in names:
                drivers.append(
                    (s["scenario"], ", ".join(s["passing_structures"]) or "None")
                )
    else:
        for name in ("Moderate combined", "Severe combined", "Assumed refinancing"):
            passing = [
                r["structure"]
                for r in model["comparisons"]
                if r["scenario"] == name and r["feasible"]
            ]
            drivers.append((name, ", ".join(passing) or "None"))
    return public, model, base, conclusion, timing, drivers


def markdown(report):
    c = content(report)
    if c is None:
        return (
            "# Strict historical assessment\n\n"
            + report["recommendation_status"]
            + "\n\nSee evidence-detail.md and the workbook for supported calculations and unresolved requirements.\n"
        )
    public, model, base, conclusion, timing, drivers = c
    lines = [
        "# Acquisition financing comparison",
        "",
        "How do cash, borrowing and share consideration change liquidity and financing risk?",
        "",
        ("Public-information conditional case" if public else "Synthetic demonstration")
        + " — "
        + timing
        + ". USD millions.",
        "Strict actual-company recommendation: " + report["recommendation_status"],
        "",
        conclusion,
        "",
        "| Structure | New borrowing | Minimum cash | Five-year interest | Passes screens |",
        "|---|---:|---:|---:|---|",
    ]
    for r in base:
        lines.append(
            f"| {r['structure']} | {r['opening']['total_new_borrowing']:.1f} | {r['min_cash']:.1f} | {r['total_interest']:.1f} | {r['feasible']} |"
        )
    lines += ["", "## Drivers of feasibility", ""] + [
        f"- {name}: passing structures — {result}." for name, result in drivers
    ]
    lines += [
        "",
        "## Projected closing bridge",
        (
            "Trade working-capital balances feed postclose changes. Historical separately disclosed WC cash movements are removed before forecast movements are deducted once. FL receivables are held constant; other operating cash remains a proxy. No complete balance-sheet forecast is claimed."
            if public
            else "Fictional cash movements and opening working capital are explicit synthetic inputs."
        ),
        "",
        "## Funding and timing",
        "Itemised uses separate consideration, awards, principal, premiums, accrued interest, expenses, fees and collateral. Fee convention: "
        + model["config"]["transaction"].get("fee_convention", "fixed_budget")
        + ". Analytical equity is separate from transaction stock elections.",
        "Interest uses beginning principal; maturity and refinancing cash settles at the containing period end. Annual and quarterly results can differ. Post-breach projections continue mechanically and are not executable paths.",
        "",
        "## Material assumptions and limits",
        "Public variable cost shares preserve starting EBITDA but change downside behaviour. The 65–95% range is an assumption, not an estimate proven by financial statement classification. Mechanical capex cuts hold operations fixed; linked cases reduce annual growth by an assumed 1–2 percentage points.",
        "Confirmed borrowing availability / lender appetite and actual covenant compliance are unsupported. Private consent and exceptional settlement costs remain unbounded. Numerical feasibility does not clear the evidence gate.",
        "",
        "Sources and detailed applicability: source-register.json, gap-register.json, evidence-detail.md and Sources in the workbook. Information cutoff: 15 May 2025. No independent human verification is claimed.",
    ]
    return "\n".join(lines) + "\n"


def write_pdf(report, path):
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Table,
        TableStyle,
        PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    c = content(report)
    public, model, base, conclusion, timing, drivers = c
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="FinanceBody",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            spaceAfter=7,
        )
    )
    story = []

    def p(text, style="FinanceBody"):
        story.append(Paragraph(escape(str(text)), styles[style]))

    def table(heads, rows, widths):
        data = [
            [Paragraph(escape(str(x)), styles["FinanceBody"]) for x in row]
            for row in [heads] + rows
        ]
        t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eff5")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t)

    f = lambda x: "No feasible solution" if x is None else f"{x:,.1f}"
    p("Acquisition financing comparison", "Title")
    p(
        ("Public-information conditional case" if public else "Synthetic demonstration")
        + " | "
        + timing
        + " | USD millions"
    )
    p(
        "Question: how do cash, borrowing and share consideration affect liquidity, debt service and dilution?"
    )
    p("Strict actual-company recommendation: " + report["recommendation_status"])
    p(conclusion)
    table(
        ["Structure", "New debt", "Min cash", "Interest", "Screens"],
        [
            [
                r["structure"],
                f(r["opening"]["total_new_borrowing"]),
                f(r["min_cash"]),
                f(r["total_interest"]),
                "Pass" if r["feasible"] else "Breach",
            ]
            for r in base
        ],
        [125, 90, 90, 90, 100],
    )
    p("Capacity and funding", "Heading2")
    table(
        ["Structure", "Acquisition debt capacity", "Residual analytical equity"],
        [
            [
                s,
                f(x["maximum_acquisition_borrowing"]),
                f(x["residual_analytical_equity"]),
            ]
            for s, x in model["capacity"].items()
        ],
        [165, 165, 165],
    )
    p(
        "A missing feasible point includes the zero-acquisition-debt test under this operating policy; it is not proof of zero standalone lending capacity. The grid can miss narrow feasible regions. Fee convention: "
        + model["config"]["transaction"].get("fee_convention", "fixed_budget")
        + "."
    )
    p("Cash, working capital and uses", "Heading2")
    if public:
        p(
            "Projected closing cash: "
            + ", ".join(
                b["company"]
                + " "
                + f(b["projected_cash"])
                + " (accessible "
                + f(b["usable_cash"])
                + ")"
                for b in public.get("projected_bridge", [])
            )
            + ". Trade working capital feeds postclose cash changes; FL receivables remain constant and other operating cash is a proxy."
        )
    else:
        p(
            "Cash contribution is separate from retained cash. Synthetic seasonal inventory and payment timing can make quarterly capacity lower than annual capacity."
        )
    p(
        "Uses separately identify purchase consideration, award reserves, debt repayment, call premiums, accrued interest, transaction expenses, financing fees and collateral."
        + (" No terminated FL facility contributes liquidity." if public else "")
    )
    story.append(PageBreak())
    p("What drives the result?", "Title")
    table(["Scenario", "Structures passing the model screens"], drivers, [260, 235])
    p("Operating uncertainty", "Heading2")
    p(
        "Public accounting costs are reconciled to operating profit and the stated D&A add-back. The assumed 65–95% variable share of nonrent operating costs preserves the same starting EBITDA. Matching that baseline does not validate operating leverage. Impairment costs are not silently normalised away."
        if public
        else "Fictional company growth, margins, inventory seasonality and fixed costs are explicit demonstration inputs. Revenue and margin stresses test their consequences."
    )
    p(
        "Lower spending with unchanged growth is a mechanical sensitivity. Linked cases apply assumed 1–2 percentage-point growth penalties; no precise capex-to-growth elasticity is claimed. Maintenance/growth spending splits are analyst choices. Compare dividend suspension, synergy delivery and refinancing separately."
        if public
        else "Compare revenue, margin, inventory, rates, synergy delivery and assumed refinancing. No annual pass establishes quarterly liquidity sufficiency."
    )
    p("Timing and execution limits", "Heading2")
    p(
        "All selected-frequency periods, including closing, enter capacity and reverse stress. Beginning-principal interest and period-end payments approximate intra-period maturities. Quarterly tests reduce timing aggregation but do not establish daily liquidity. Public forecasts remain annual because historical quarterly inputs are incomplete."
    )
    p(
        "Post-breach balances continue mechanically to identify funding needs; they are not an executable path. Refinancing is an assumption, not a commitment. Analytical leverage and coverage screens are not legal covenants. Private consent and exceptional settlement obligations prevent a complete company-specific financing preference."
    )
    p("Source trail", "Heading2")
    p(
        "DKS and FL FY2024 Forms 10-K (27 March 2025), Q3 2024 cash-flow statements, merger agreement (15 May 2025), and original indentures. Exact extracted claims, units and dates are in Sources and source-register.json. Hashes establish integrity, not accuracy. Machine-assisted review; no independent human signoff."
        if public
        else "Synthetic facts are fictional and deterministic. See tests/full_benchmark.json, the independent Decimal financing-fee test, and docs/METHODOLOGY.md. The separate strict assessment uses the 15 May 2025 information cutoff."
    )

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.drawString(
            40, 24, "Conditional educational analysis | cutoff 15 May 2025"
        )
        canvas.drawRightString(550, 24, str(doc.page))

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(path),
        pagesize=(595.28, 841.89),
        leftMargin=40,
        rightMargin=40,
        topMargin=32,
        bottomMargin=40,
    ).build(story, onFirstPage=footer, onLaterPages=footer)
