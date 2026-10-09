"""One workbook layout shared by the bundled renderer and portable exporter.

Python model outputs are labelled snapshots. Familiar Excel formulas show useful
operating and cash/debt rollforwards; they do not pretend to rerun the solver.
"""

import json


def scalar(value):
    return (
        json.dumps(value, ensure_ascii=False)
        if isinstance(value, (dict, list))
        else value
    )


def flatten(value, prefix=""):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from flatten(child, f"{prefix}.{key}" if prefix else key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from flatten(child, f"{prefix}[{i}]")
    else:
        yield [prefix, value]


def make_plan(r, case):
    partial = any(
        (
            x["status"] == "Supported"
            for x in r.get("supported_historical_calculations", [])
        )
    )
    summary = [
        ["Acquisition financing simulator", ""],
        ["Recommendation status", r["recommendation_status"]],
        ["Preferred actual-company structure", r.get("preferred_structure") or "None"],
        [
            "Historical-analysis completion",
            (
                "Complete with qualifications"
                if r["historical_analysis_complete"]
                else "Incomplete"
            ),
        ],
        ["Numerical results", r["illustrative_label"]],
        [
            "Refresh",
            "Model snapshots. Rerun Python after input/source changes; only displayed formulas recalculate in Excel.",
        ],
        ["Analysis limitation", r["analysis_limitation"]],
        [
            "Historical results",
            "Available" if r["historical_results"] else "Unavailable",
        ],
        ["Information cutoff", r["evidence"]["cutoff"]],
        ["Input ID", r.get("config_id", r["evidence"]["case_id"])],
    ]
    sheets = [
        dict(name="Summary", rows=summary, header_row=0, widths=[44, 100], formulas=[])
    ]
    if partial and (not r.get("illustrative_results")):
        summary[4] = [
            "Numerical results",
            "Bounded historical calculations and explicit hypothetical sensitivities; no synthetic company inputs.",
        ]
        summary[7] = [
            "Historical results",
            "Full funding analysis unavailable; supported calculations are on Historical calculations.",
        ]

    def sheet(name, heads, rows, formula_fn=None, widths=None):
        title = (
            (r.get("model", {}).get("config", {}).get("label") or "Evidence review")
            + " | "
            + name
        )
        data = [
            [title],
            [
                "USD millions unless stated. Python snapshots; formula calculations are explicitly shown."
            ],
            heads,
        ] + rows
        data = [row + [None] * (len(heads) - len(row)) for row in data]
        formulas = []
        if formula_fn:
            for i, row in enumerate(rows, 5):
                formulas.extend(formula_fn(i, row))
        sheets.append(
            dict(
                name=name,
                rows=data,
                header_row=4,
                widths=widths or [30] + [18] * (len(heads) - 1),
                formulas=formulas,
            )
        )

    m = r.get("model")
    if m:
        summary.extend(
            [
                ["Engineering", r["engineering_status"]],
                ["Illustrative assessment", m["recommendation"]["narrative"]],
                ["Model code ID", m["code_id"]],
                ["Run ID", r.get("run_id", "Not persisted")],
            ]
        )
        sheet(
            "Assumptions",
            ["Input / future choice", "Value"],
            list(flatten(m["config"])),
            widths=[65, 75],
        )
        opening = []
        for s in m["base"]:
            for key, val in s["opening"].items():
                if key not in ("bridges", "retained_instruments", "structure"):
                    opening.append([s["structure"], key.replace("_", " "), scalar(val)])
        sheet(
            "Sources Uses",
            ["Structure", "Bridge item", "Value"],
            opening,
            widths=[28, 48, 25],
        )
        bridge = []
        for s in m["base"]:
            for b in s["opening"]["bridges"]:
                bridge.append(
                    [
                        s["structure"],
                        b["company"],
                        b["latest_cash"],
                        b["operating"],
                        b["capex"],
                        b["dividends"],
                        b["buybacks"],
                        b["preclose_debt_repayment"],
                        b["closing_cash"],
                        b["latest_debt"],
                        b["closing_debt"],
                    ]
                )
        sheet(
            "Opening Bridge",
            [
                "Structure",
                "Company",
                "Latest cash",
                "Operating cash",
                "Capex",
                "Dividends",
                "Buybacks",
                "Debt repayment",
                "Closing cash",
                "Latest debt",
                "Closing debt",
            ],
            bridge,
            lambda n, row: [
                dict(
                    cell=f"I{n}",
                    formula=f"=C{n}+D{n}-E{n}-F{n}-G{n}-H{n}",
                    value=row[8],
                ),
                dict(cell=f"K{n}", formula=f"=J{n}-H{n}", value=row[10]),
            ],
        )
        ops = []
        for s in m["base"]:
            for a in s["company_forecasts"]:
                ops.append(
                    [
                        s["structure"],
                        a["company"],
                        a["year"],
                        a["revenue"],
                        a["cogs"],
                        a["variable_opex"],
                        a["fixed_opex"],
                        a["rent"],
                        a["ebitda"],
                        a["da"],
                        a["ebit"],
                        a["capex"],
                        a["inventory"],
                        a["receivables"],
                        a["payables"],
                        a["nwc"],
                    ]
                )
        sheet(
            "Operations",
            [
                "Structure",
                "Company",
                "Year",
                "Revenue",
                "COGS",
                "Variable cost",
                "Fixed cost",
                "Rent expense",
                "EBITDA",
                "D&A",
                "EBIT",
                "Capex",
                "Inventory",
                "Receivables",
                "Payables",
                "Net working capital",
            ],
            ops,
            lambda n, row: [
                dict(cell=f"I{n}", formula=f"=D{n}-E{n}-F{n}-G{n}-H{n}", value=row[8]),
                dict(cell=f"K{n}", formula=f"=I{n}-J{n}", value=row[10]),
                dict(cell=f"P{n}", formula=f"=M{n}+N{n}-O{n}", value=row[15]),
            ],
        )
        liquidity = []
        for s in m["base"]:
            for a in s["years"]:
                liquidity.append(
                    [
                        s["structure"],
                        a["year"],
                        a["opening_cash"],
                        a["ebitda"],
                        a["tax"],
                        a["delta_nwc"],
                        a["integration"],
                        a["rent_cash"] - a["rent"],
                        a["capex"],
                        a["interest"],
                        a["dividends"],
                        a["buybacks"],
                        a["refinancing_fees"],
                        a["revolver_draw"],
                        a["mandatory_paid"],
                        a["optional_paid"],
                        a["closing_cash"],
                        a["opening_debt"],
                        a["closing_debt"],
                        a["net_leverage"],
                        a["coverage"],
                        a["rent_inclusive_coverage"],
                        a["maturity_gap"],
                    ]
                )
        sheet(
            "Liquidity",
            [
                "Structure",
                "Year",
                "Opening cash",
                "EBITDA",
                "Tax",
                "Change NWC",
                "Integration",
                "Rent cash adjustment",
                "Capex",
                "Interest",
                "Dividends",
                "Buybacks",
                "Refinancing fees",
                "Revolver draw",
                "Mandatory paid",
                "Optional paid",
                "Closing cash",
                "Opening debt",
                "Closing debt",
                "Net leverage",
                "Interest coverage",
                "Rent coverage",
                "Funding gap",
            ],
            liquidity,
            lambda n, row: [
                dict(
                    cell=f"Q{n}",
                    formula=f"=C{n}+D{n}-E{n}-F{n}-G{n}-H{n}-I{n}-J{n}-K{n}-L{n}-M{n}+N{n}-O{n}-P{n}",
                    value=row[16],
                ),
                dict(cell=f"S{n}", formula=f"=R{n}+N{n}-O{n}-P{n}", value=row[18]),
                dict(
                    cell=f"T{n}",
                    formula=f'=IF(D{n}<=0,"n.a.",(S{n}-Q{n})/D{n})',
                    value=row[19] if row[19] is not None else "n.a.",
                ),
                dict(
                    cell=f"U{n}",
                    formula=f'=IF(D{n}<=0,"n.a.",IF(J{n}=0,"n.a.",D{n}/J{n}))',
                    value=row[20] if row[20] is not None else "n.a.",
                ),
            ],
        )
        debt = []
        for s in m["comparisons"]:
            for a in s["debt_schedule"]:
                debt.append(
                    [
                        s["structure"],
                        s["scenario"],
                        a["instrument"],
                        a["period"],
                        a["opening_principal"],
                        a["rate"],
                        a["interest"],
                        a["mandatory_due"],
                        a["mandatory_paid"],
                        a["optional_paid"],
                        a["draw"],
                        a["refinanced"],
                        a["closing_principal"],
                    ]
                )
        sheet(
            "Debt Schedule",
            [
                "Structure",
                "Scenario",
                "Instrument",
                "Period",
                "Opening principal",
                "Rate (fraction)",
                "Interest",
                "Mandatory due",
                "Mandatory paid",
                "Optional paid",
                "New borrowing",
                "Refinanced old debt",
                "Closing principal",
            ],
            debt,
            lambda n, row: [
                dict(cell=f"M{n}", formula=f"=E{n}+K{n}-I{n}-J{n}-L{n}", value=row[12])
            ],
            widths=[25, 28, 45] + [18] * 10,
        )
        sheet(
            "Scenarios",
            [
                "Structure",
                "Scenario",
                "Year",
                "EBITDA",
                "Interest",
                "Closing cash",
                "Closing debt",
                "Leverage",
                "Coverage",
                "Maturity gap",
                "Scenario feasible",
            ],
            [
                [
                    s["structure"],
                    s["scenario"],
                    a["year"],
                    a["ebitda"],
                    a["interest"],
                    a["closing_cash"],
                    a["closing_debt"],
                    a["net_leverage"],
                    a["coverage"],
                    a["maturity_gap"],
                    s["feasible"],
                ]
                for s in m["comparisons"]
                for a in s["years"]
            ],
        )
        sheet(
            "Quarterly",
            [
                "Structure",
                "Year",
                "Quarter",
                "Revenue",
                "EBITDA",
                "Inventory",
                "Change NWC",
                "Interest",
                "Tax",
                "Cash",
                "Debt",
                "TTM coverage",
                "Funding gap",
            ],
            [
                [
                    s["structure"],
                    a["year"],
                    a["quarter"],
                    a["revenue"],
                    a["ebitda"],
                    a["inventory"],
                    a["delta_nwc"],
                    a["interest"],
                    a["tax"],
                    a["closing_cash"],
                    a["closing_debt"],
                    a["coverage"],
                    a["maturity_gap"],
                ]
                for s in m["quarterly"]
                for a in s["periods"]
                if a["year"] <= 2
            ],
        )
        sheet(
            "Capacity",
            [
                "Structure",
                "Maximum acquisition debt",
                "Residual analytical equity",
                "Eligible uses",
                "Funding limited",
                "Limiting constraint/period",
                "Boundary resolution",
                "Feasible ranges",
            ],
            [
                [
                    s,
                    x["maximum_acquisition_borrowing"],
                    x["residual_analytical_equity"],
                    x["eligible_acquisition_uses"],
                    x["funding_limited"],
                    scalar(x["limiting_constraint"]),
                    x["boundary_resolution"],
                    scalar(x["feasible_ranges"]),
                ]
                for s, x in m["capacity"].items()
            ],
            widths=[28, 25, 25, 20, 18, 70, 22, 35],
        )
        sheet(
            "Capacity Grid",
            ["Structure", "Acquisition borrowing", "Feasible", "First breach"],
            [
                [s, x["borrowing"], x["feasible"], scalar(x["first_breach"])]
                for s, c in m["capacity"].items()
                for x in c["grid"]
            ],
            widths=[30, 25, 18, 80],
        )
        sheet(
            "Sensitivity",
            ["Cash-first case", "Capacity", "Residual equity", "Limiting constraint"],
            [
                [
                    x["label"],
                    x["maximum_acquisition_borrowing"],
                    x["residual_analytical_equity"],
                    scalar(x["limiting_constraint"]),
                ]
                for x in m["sensitivities"]
            ],
            widths=[35, 25, 25, 75],
        )
        sheet(
            "Reverse Stress",
            [
                "Structure",
                "Status",
                "Revenue decline (fraction)",
                "Resolution",
                "Failing constraint/period",
            ],
            [
                [
                    s,
                    x["status"],
                    x.get("revenue_decline"),
                    x["resolution"],
                    scalar(x.get("failing")),
                ]
                for s, x in m["reverse_stress"].items()
            ],
            widths=[28, 45, 28, 18, 75],
        )
        sheet(
            "Checks",
            [
                "Structure",
                "Year",
                "Sources/uses difference",
                "Cash rollforward difference",
                "Debt rollforward difference",
                "Maximum debt ledger difference",
            ],
            [
                [
                    s["structure"],
                    a["year"],
                    s["opening"]["sources_uses_difference"],
                    a["cash_check"],
                    a["debt_check"],
                    max(
                        (
                            abs(
                                d["closing_principal"]
                                - d["opening_principal"]
                                - d["draw"]
                                + d["mandatory_paid"]
                                + d["optional_paid"]
                                + d["refinanced"]
                            )
                            for d in s["debt_schedule"]
                            if d["year"] == a["year"]
                        )
                    ),
                ]
                for s in m["base"]
                for a in s["years"]
            ],
            widths=[28, 15, 30, 30, 30, 35],
        )
    else:
        sheet(
            "Scenarios",
            [
                "Structure",
                "Year",
                "Closing cash",
                "Closing debt",
                "Interest",
                "Maturity gap",
            ],
            [
                [
                    s["structure"],
                    a["year"],
                    a["closing_cash"],
                    a["closing_debt"],
                    a["interest"],
                    a["maturity_gap"],
                ]
                for s in r["illustrative_results"]
                for a in s["years"]
            ],
        )
        sheets[-1]["rows"][0][0] = r["illustrative_label"]
        if partial and (not r["illustrative_results"]):
            sheets[-1]["rows"][0][
                0
            ] = "Historical financing scenarios unavailable: insufficient verified evidence"
    sheet(
        "Evidence",
        [
            "Input",
            "Value",
            "Classification",
            "Blocks recommendation",
            "Reason",
            "Affected calculations",
            "Materiality",
            "Resolution",
        ],
        [
            [
                x["key"],
                scalar(x.get("value")),
                x["classification"],
                x.get("recommendation_blocking", True),
                x["reason"],
                x["affected_calculations"],
                x.get("materiality_reason", ""),
                x["resolution"],
            ]
            for x in r["evidence"]["rows"]
        ],
        widths=[54, 35, 30, 22, 60, 60, 70, 70],
    )
    sheet(
        "Sources",
        [
            "Source ID",
            "Document",
            "Published",
            "Retrieved",
            "URL",
            "Archive type",
            "Section",
        ],
        [
            [
                s["id"],
                s["document_id"],
                s["published"],
                s["retrieved"],
                s["url"],
                s.get("archive_type", "Original file"),
                s.get("section", "See reviewed claim register"),
            ]
            for s in case.get("sources", [])
        ],
        widths=[25, 38, 20, 28, 80, 55, 60],
    )
    if partial:
        sheet(
            "Historical calculations",
            [
                "Calculation",
                "Status",
                "Value",
                "Units",
                "Formula",
                "Dependencies",
                "Limitation",
            ],
            [
                [
                    x["calculation"],
                    x["status"],
                    x["value"],
                    x["units"],
                    x["formula"],
                    scalar(x["dependencies"]),
                    x["limitation"],
                ]
                for x in r["supported_historical_calculations"]
            ],
            widths=[48, 20, 22, 22, 65, 70, 80],
        )
        sheet(
            "Historical gap review",
            [
                "Input",
                "Status",
                "Classification",
                "Type",
                "Materiality",
                "Current evidence",
                "Exact missing information",
                "Applicability",
                "Primary source",
                "Resolution",
            ],
            [
                [
                    g[k]
                    for k in (
                        "key",
                        "status",
                        "classification",
                        "nature",
                        "materiality",
                        "current_evidence",
                        "missing_information",
                        "applicability",
                        "primary_source",
                        "proposed_resolution",
                    )
                ]
                for g in r["historical_gap_register"]
            ],
            widths=[55, 20, 28, 35, 70, 85, 90, 90, 80, 90],
        )
        sheet(
            "Historical sensitivities",
            [
                "Study",
                "Company",
                "Year",
                "Annual growth",
                "Margin shift",
                "Revenue",
                "EBITDA",
                "Limitations",
            ],
            [
                [
                    x[k]
                    for k in (
                        "study",
                        "company",
                        "year",
                        "annual_growth",
                        "margin_shift",
                        "revenue",
                        "ebitda",
                        "limitation",
                    )
                ]
                for x in r["historical_operating_sensitivities"]
            ],
            widths=[65, 22, 15, 22, 22, 22, 22, 90],
        )
        sheet(
            "Historical assumptions",
            ["Future choice", "Value", "Rationale"],
            [
                [o["key"], scalar(o["value"]), o["rationale"]]
                for o in case.get("observations", [])
                if o.get("kind") == "assumption"
            ],
            widths=[55, 110, 110],
        )
        sheet(
            "Funding unit sensitivities",
            ["Study", "Assumptions", "Value", "Units", "Limitation"],
            [
                [x[k] for k in ("study", "assumptions", "value", "units", "limitation")]
                for x in r["historical_financing_sensitivities"]
            ],
            widths=[60, 70, 22, 30, 90],
        )
    if r.get("public_information"):
        from .public_exports import tables, narrative

        p = r["public_information"]
        if not m:
            summary[4] = [
                "Numerical results",
                "Verified historical calculations and dependency-gated conditional public projections; no synthetic company inputs.",
            ]
        summary.extend(
            [
                ["Public-information case", p["scope"]],
                ["Conditional conclusion", p["conclusion"]],
                [
                    "Public-case refresh",
                    "Python snapshots connected to evaluated source dependencies. Rerun with --public-information; Excel formulas explain rollforwards but do not rerun scenarios or solver.",
                ],
            ]
        )
        summary[7] = [
            "Historical results",
            "Supported historical calculations and separate conditional public projections; strict recommendation blocked.",
        ]
        start = len(sheets)
        for name, heads, rows in tables(p):
            fn = None
            if name == "Projected closing bridge":
                fn = lambda n, row: [
                    dict(
                        cell=f"H{n}",
                        formula=f"=B{n}+C{n}-D{n}-E{n}-F{n}-G{n}",
                        value=row[7],
                    ),
                    dict(cell=f"I{n}", formula=f"=MAX(0,H{n})*J{n}", value=row[8]),
                ]
            if name == "Public cash and debt":
                fn = lambda n, row: [
                    dict(
                        cell=f"M{n}",
                        formula=f"=C{n}+D{n}-E{n}-F{n}-G{n}-H{n}-I{n}+J{n}-K{n}-L{n}",
                        value=row[12],
                    ),
                    dict(cell=f"O{n}", formula=f"=N{n}+J{n}-K{n}-L{n}", value=row[14]),
                ]
            if name == "Public instruments":
                fn = lambda n, row: [
                    dict(
                        cell=f"L{n}",
                        formula=f"=D{n}+J{n}-H{n}-I{n}-K{n}",
                        value=row[11],
                    )
                ]
            sheet(
                name,
                heads,
                rows,
                fn,
                widths=(
                    [52, 36, 95, 90]
                    if name in ("Public output policy", "Public gap assessment")
                    else (
                        [48, 80]
                        if name == "Public assumptions"
                        else [40] + [23] * (len(heads) - 1)
                    )
                ),
            )
            sheets[-1]["rows"][0][0] = "PUBLIC INFORMATION | " + name
            sheets[-1]["rows"][1][
                0
            ] = "Conditional model snapshots; strict recommendation remains blocked. USD millions unless stated."
            if name == "Public sources and uses":
                sheets[-1]["widths"] = [35, 55, 90]
            if name == "Public capacity and stress":
                sheets[-1]["widths"] = [50, 28, 28, 28, 65, 22]
            if name == "Public comparisons":
                sheets[-1]["widths"] = [55, 28, 23, 23, 23, 23, 23, 65, 90]
        sheet(
            "Public conventions",
            ["Convention / limitation"],
            [[t] for t in narrative(p)]
            + [[k + ": " + v] for k, v in p.get("field_definitions", {}).items()],
            widths=[150],
        )
        sheets = sheets[:1] + sheets[start:] + sheets[1:start]
    for spec in sheets:
        spec["number_formats"] = []
        if not spec["header_row"]:
            continue
        heads = spec["rows"][2]
        for j, head in enumerate(heads):
            fmt = None
            if head in ("Year", "Quarter", "Period"):
                fmt = "0"
            if head in ("Rate (fraction)", "Revenue decline (fraction)") or (
                spec["name"] == "Reverse Stress" and head == "Resolution"
            ):
                fmt = "0.00%"
            if head in ("Annual growth", "Margin shift"):
                fmt = "0.00%"
            if head in ("Cash access fraction", "Common dilution fraction"):
                fmt = "0.00%"
            if fmt:
                spec["number_formats"].append(dict(column=j, format=fmt))
        if spec["name"] == "Assumptions":
            spec["number_formats"].append(dict(column=1, format="0.0000"))
        if spec["name"] == "Public assumptions":
            spec["number_formats"].append(dict(column=1, format="0.0000"))
        if spec["name"] == "Public capacity and stress":
            spec["number_formats"].append(dict(column=5, format="0.00"))
        if spec["name"] == "Sources Uses":
            spec["number_formats"].append(dict(column=2, format="#,##0.0000"))
        if spec["name"] == "Historical calculations":
            spec["number_formats"].append(dict(column=2, format="#,##0.000000"))
    from .portfolio_workbook import augment

    return augment(sheets, r)


# Preserved implementation notes
# Keep the original regression's positions and semantics intact.
# Public outputs precede preserved strict evidence sheets; synthetic sheets retain their labels.
