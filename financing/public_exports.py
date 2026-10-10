"""Shared public-case views; every surface reads the same evaluated bundle."""

import html
import json


def value(x):
    return json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x


def breach(x):
    return (
        "None"
        if not x
        else (
            f"{x['constraint']} / year {x['year']}; headroom {x['headroom']:,.2f}"
            if x.get("headroom") is not None
            else f"{x['constraint']} / year {x['year']}; unavailable ratio"
        )
    )


def tables(p):
    out = []

    def add(name, heads, rows):
        out.append((name, heads, rows))

    add(
        "Public output policy",
        ["Output", "Status", "Limitation", "Missing dependencies"],
        [
            [
                x["output"],
                x["status"],
                x["limitation"],
                value(x["missing_dependencies"]),
            ]
            for x in p["output_policy"]
        ],
    )
    add(
        "Public assumptions",
        ["Future assumption", "Value"],
        [[k, value(v)] for k, v in p["assumptions"].items()],
    )
    add(
        "Projected closing bridge",
        [
            "Company",
            "Reported cash",
            "Projected CFO",
            "Projected capex",
            "Projected dividends",
            "Accrued buybacks paid",
            "Projected lease principal",
            "Projected cash",
            "Usable cash",
            "Cash access fraction",
        ],
        [
            [
                b[k]
                for k in (
                    "company",
                    "reported_cash",
                    "projected_cfo",
                    "projected_gross_capex",
                    "projected_dividends",
                    "accrued_buybacks_paid",
                    "projected_lease_principal",
                    "projected_cash",
                    "usable_cash",
                    "cash_availability_fraction",
                )
            ]
            for b in p.get("projected_bridge", [])
        ],
    )
    add(
        "Public sources and uses",
        ["Structure / scope", "Item", "Value"],
        [
            [r["structure"], k, value(v)]
            for r in p["base"]
            for k, v in r["opening"].items()
            if k not in ("bridges", "retained_instruments", "structure")
        ]
        + [["All structures", k, v] for k, v in p.get("uses_detail", {}).items()],
    )
    add(
        "Public operations",
        [
            "Structure",
            "Company",
            "Year",
            "Revenue",
            "COGS",
            "Variable cost",
            "Fixed cost",
            "Rent",
            "EBITDA",
            "D&A",
            "EBIT",
            "Capex",
            "Inventory",
            "Receivables",
            "Payables",
            "NWC",
        ],
        [
            [r["structure"]]
            + [
                y[k]
                for k in (
                    "company",
                    "year",
                    "revenue",
                    "cogs",
                    "variable_opex",
                    "fixed_opex",
                    "rent",
                    "ebitda",
                    "da",
                    "ebit",
                    "capex",
                    "inventory",
                    "receivables",
                    "payables",
                    "nwc",
                )
            ]
            for r in p["base"]
            for y in r["company_forecasts"]
        ],
    )
    add(
        "Public cash and debt",
        [
            "Structure",
            "Year",
            "Opening cash",
            "Accessible operating CF",
            "Capex",
            "Interest",
            "Dividends",
            "Buybacks",
            "Refinance fees",
            "Facility draw",
            "Mandatory paid",
            "Optional paid",
            "Closing cash",
            "Opening debt",
            "Closing debt",
            "Net leverage",
            "Coverage",
            "Maturity gap",
        ],
        [
            [r["structure"]]
            + [
                y[k]
                for k in (
                    "year",
                    "opening_cash",
                    "operating_cash_flow",
                    "capex",
                    "interest",
                    "dividends",
                    "buybacks",
                    "refinancing_fees",
                    "revolver_draw",
                    "mandatory_paid",
                    "optional_paid",
                    "closing_cash",
                    "opening_debt",
                    "closing_debt",
                    "net_leverage",
                    "coverage",
                    "maturity_gap",
                )
            ]
            for r in p["base"]
            for y in r["years"]
        ],
    )
    add(
        "Public instruments",
        [
            "Structure",
            "Instrument",
            "Year",
            "Opening principal",
            "Rate (fraction)",
            "Interest",
            "Mandatory due",
            "Mandatory paid",
            "Optional paid",
            "Draw",
            "Refinanced",
            "Closing principal",
        ],
        [
            [r["structure"]]
            + [
                y[k]
                for k in (
                    "instrument",
                    "year",
                    "opening_principal",
                    "rate",
                    "interest",
                    "mandatory_due",
                    "mandatory_paid",
                    "optional_paid",
                    "draw",
                    "refinanced",
                    "closing_principal",
                )
            ]
            for r in p["base"]
            for y in r["debt_schedule"]
        ],
    )
    policies = {"Base": p["capacity"], **p.get("capacity_by_policy", {})}
    add(
        "Public capacity and stress",
        [
            "Policy / study",
            "Structure",
            "Maximum acquisition debt / decline",
            "Residual analytical equity",
            "Constraint / status",
            "Resolution",
        ],
        [
            [
                label,
                s,
                c["maximum_acquisition_borrowing"],
                c["residual_analytical_equity"],
                breach(c["limiting_constraint"]),
                c["boundary_resolution"],
            ]
            for label, cc in policies.items()
            for s, c in cc.items()
        ]
        + [
            [
                "Reverse revenue decline (fraction)",
                s,
                c.get("revenue_decline"),
                None,
                c["status"] + "; " + breach(c.get("failing")),
                c["resolution"],
            ]
            for s, c in p["reverse_stress"].items()
        ],
    )
    add(
        "Public comparisons",
        [
            "Scenario",
            "Structure",
            "Passes analytical screens",
            "New debt",
            "Minimum cash",
            "Five-year interest",
            "Common dilution fraction",
            "First breach",
            "Assumption changes",
        ],
        [
            [
                c["scenario"],
                s["structure"],
                s["feasible"],
                s["new_debt"],
                s["minimum_cash"],
                s["interest"],
                s["common_share_dilution"],
                value(s["first_breach"]),
                value(c["assumption_changes"]),
            ]
            for c in p["comparisons"]
            for s in c["structures"]
        ],
    )
    add(
        "Public gap assessment",
        [
            "Required input",
            "Classification",
            "Effect / applicability",
            "Strict materiality",
        ],
        [
            [
                g[k]
                for k in ("key", "classification", "explanation", "strict_materiality")
            ]
            for g in p["gap_assessment"]
        ],
    )
    for name, heads, rows in out:
        if name == "Public instruments":
            for row in rows:
                if row[1] == "Committed revolver":
                    row[1] = "No facility (zero placeholder)"
    return out


def narrative(p):
    text = [
        p["conclusion"],
        (
            "The base case has no structure passing all analytical screens. A blank capacity means no tested acquisition borrowing, including zero, passes the fixed operating and distribution policy; it does not establish zero standalone lending capacity."
            if p["base"] and (not any((r["feasible"] for r in p["base"])))
            else "Only outputs with supported dependencies are shown."
        ),
    ]
    if p.get("comparison_summary"):
        text.append(p["comparison_summary"]["interpretation"])
        passing = p["comparison_summary"]["conditions_with_a_passing_structure"]
        text.append(
            "Passing scenario conditions: "
            + (
                "; ".join(
                    (
                        x["scenario"] + " — " + ", ".join(x["passing_structures"])
                        for x in passing
                    )
                )
                or "None in the tested set"
            )
            + "."
        )
    text += [
        "Public-case amounts are USD millions. Projected close: 1 November 2025; annual years 1–5 follow closing. No target opening cash or terminated ABL is counted as available liquidity. Negative cash is an unfunded deficit, not permitted borrowing.",
        "Capacity uses a $25m grid with $5m boundary refinement; narrow feasible regions can be missed. Reverse revenue stress uses one percentage-point steps. Analytical cash/leverage/coverage thresholds are not contractual covenants.",
        "Known-award cash bounds exclude unknown taxes and consent costs. Common-share dilution excludes converted awards. Enterprise value remains unavailable. The $200 reference share value is an illustrative future valuation assumption, not a verified market price.",
        "Forecast limitations: prior-year seasonal cash-flow calibration is imperfect; no actual interim cash rollforward, daily liquidity or legal cash availability is asserted. Base cash access is an assumption. See source-register.json for source references.",
    ]
    return text + ["Unbounded: " + s for s in p["unbounded_material_items"]]


def markdown(p):
    lines = ["## Public-information conditional case", ""] + narrative(p) + [""]
    for name, heads, rows in tables(p):
        lines += [
            "### " + name,
            "",
            " | ".join(heads),
            " | ".join(["---"] * len(heads)),
        ]
        lines += [
            " | ".join(
                (str(value(c)).replace("|", "/").replace("\n", " ") for c in row)
            )
            for row in rows
        ]
        lines.append("")
    return "\n".join(lines)


def dashboard(p):
    e = html.escape
    result = (
        '<section id="public-case"><h2>Public-information conditional case</h2>'
        + "".join(("<p>" + e(t) + "</p>" for t in narrative(p)))
    )
    for name, heads, rows in tables(p):
        result += (
            "<details open><summary>"
            + e(name)
            + '</summary><div style="overflow:auto;max-height:520px"><table><tr>'
            + "".join(("<th>" + e(h) + "</th>" for h in heads))
            + "</tr>"
        )
        result += (
            "".join(
                (
                    "<tr>"
                    + "".join(
                        (
                            "<td>"
                            + e(f"{c:,.3f}" if isinstance(c, float) else str(c))
                            + "</td>"
                            for c in row
                        )
                    )
                    + "</tr>"
                    for row in rows
                )
            )
            + "</table></div></details>"
        )
    return result + "</section>"


def pdf_story(p, paragraph, table, story, pagebreak):
    paragraph("Public-information conditional case", "SmallHead")
    paragraph(p["conclusion"])
    paragraph("Projected closing bridge - 1 November 2025", "SmallHead")
    f = lambda x: "n.a." if x is None else f"{x:,.1f}"
    table(
        ["Company", "Reported cash", "Projected cash", "Usable cash"],
        [
            [
                b["company"],
                f(b["reported_cash"]),
                f(b["projected_cash"]),
                f(b["usable_cash"]),
            ]
            for b in p.get("projected_bridge", [])
        ],
        [130, 120, 120, 120],
    )
    if not p["base"]:
        paragraph(
            "Financing projections are unavailable because essential verified dependencies are missing. No prior scenario results are carried forward."
        )
        for x in p["output_policy"]:
            paragraph(
                x["output"]
                + ": "
                + x["status"]
                + ". "
                + x["limitation"]
                + " Missing: "
                + ", ".join(x["missing_dependencies"])
            )
        return
    paragraph(
        "Projected from FY2024 39-week cash flows, prospective capex and distributions. DKS usable cash is 75% of projected cash; target opening cash is excluded. These are assumptions, not verified spendable closing balances."
    )
    table(
        ["Structure", "New borrowing", "Minimum cash", "Analytical result"],
        [
            [
                r["structure"],
                f(r["opening"]["total_new_borrowing"]),
                f(r["min_cash"]),
                "Pass" if r["feasible"] else "Fails " + r["breaches"][0]["constraint"],
            ]
            for r in p["base"]
        ],
        [125, 115, 115, 135],
    )
    paragraph(
        "Retain DKS fixed notes; redeem FL notes at projected 101% plus accrued interest; terminate FL ABL. Existing facility availability is zero. Aggregate finance-lease cash maturities are projected with an approximate interest allocation."
    )
    paragraph(
        "Base thresholds: $750m cash floor, 3x net leverage, 4x interest coverage. These are analytical screens. Under base capex/dividends, no tested borrowing point, including zero acquisition borrowing, passes. This is not confirmed borrowing capacity."
    )
    story.append(pagebreak())
    paragraph("Conditions, uncertainty and evidence", "Title")
    paragraph(
        "Under the stated public-information assumptions and analytical thresholds, the model indicates that the tested liquidity result depends materially on reinvestment, distributions and synergies."
    )
    for t in narrative(p)[2:4]:
        paragraph(t)
    paragraph(
        "The lower-reinvestment/no-dividend case assumes annual initial gross capex of $900m/$240m for DKS/FL. It is a counterfactual policy, not management guidance. Removing its $100m eventual synergies causes the passing mixed structure to fail again."
    )
    paragraph(
        "Rate/spread, preclose CFO, cash access 0–100%, awards, lease timing, additional payoff/reserves, refinancing and analytical thresholds are tested. This finite set does not bound undisclosed lease consent or exceptional settlement costs."
    )
    paragraph("Outputs that remain blocked", "SmallHead")
    for x in p["output_policy"]:
        if x["status"] == "Blocked":
            paragraph(
                x["output"]
                + ": "
                + x["limitation"]
                + (
                    " Missing: " + ", ".join(x["missing_dependencies"])
                    if x["missing_dependencies"]
                    else ""
                )
            )
    paragraph(
        "Sources: DKS and FL FY2024 Forms 10-K filed 27 March 2025, 2024 third-quarter filings, merger agreement Sections 3.4/7.16 filed 15 May 2025 and original note/credit agreements. Reviewed extracts and exact claim references are in the source register; no later publications or private records were used."
    )
    paragraph(
        "See workbook Public output policy and Public gap assessment, and memo.md. The strict 23-gap assessment is preserved; public projections do not establish historical completeness."
    )
