"""Additional finance-facing schedules over the shared Python results."""

import json


def augment(sheets, report):
    public = report.get("public_information")
    model = report.get("model") or public
    extras = []

    def add(name, heads, rows, widths=None, formulas=None):
        columns = len(heads)
        extras.append(
            dict(
                name=name,
                rows=[
                    [name] + [None] * (columns - 1),
                    [
                        "USD millions. Python snapshots; rerun Python to change assumptions."
                    ]
                    + [None] * (columns - 1),
                    heads,
                ]
                + rows,
                header_row=4,
                widths=widths or [35] + [23] * (columns - 1),
                formulas=formulas or [],
                number_formats=[],
            )
        )

    if model:
        add(
            "Itemised funding",
            ["Structure", "Use / source", "USD millions"],
            [
                [r["structure"], k.replace("_", " ").capitalize(), v]
                for r in model["base"]
                for k, v in r["opening"]["itemised_uses"].items()
            ]
            + [
                [r["structure"], k.replace("_", " ").capitalize(), r["opening"][k]]
                for r in model["base"]
                for k in (
                    "cash_uses",
                    "cash_contribution",
                    "total_new_borrowing",
                    "analytical_equity",
                    "sources_uses_difference",
                )
            ],
            [30, 52, 25],
        )
        timing = report.get("model", {}).get(
            "capacity_by_frequency", {"1": model["capacity"]}
        )
        add(
            "Timing and capacity",
            [
                "Timing",
                "Structure",
                "Acquisition debt",
                "Residual equity",
                "Fee convention",
                "Constraint",
            ],
            [
                [
                    "Quarterly" if f == "4" else "Annual",
                    s,
                    (
                        c["maximum_acquisition_borrowing"]
                        if c["maximum_acquisition_borrowing"] is not None
                        else "No feasible solution"
                    ),
                    c["residual_analytical_equity"],
                    c.get("fee_convention", "fixed_budget"),
                    constraint(c["limiting_constraint"]),
                ]
                for f, cs in timing.items()
                for s, c in cs.items()
            ],
            [22, 30, 28, 24, 25, 65],
        )
        add(
            "Model checks",
            [
                "Structure",
                "Period end",
                "Sources less uses",
                "Cash rollforward",
                "Debt rollforward",
                "Timing",
            ],
            [
                [
                    r["structure"],
                    y["period_end"],
                    r["opening"]["sources_uses_difference"],
                    y["cash_check"],
                    y["debt_check"],
                    r["timing_basis"],
                ]
                for r in model["base"]
                for y in r["periods"]
            ],
        )
    if public and public.get("base"):
        rows = []
        for b in public["projected_bridge"]:
            for metric in ("inventory", "receivables", "payables"):
                rows.append(
                    [
                        b["company"],
                        metric,
                        b["reported_working_capital"][metric],
                        b["closing_working_capital"][metric],
                        b["closing_working_capital"][metric]
                        - b["reported_working_capital"][metric],
                    ]
                )
        add(
            "Closing working capital",
            ["Company", "Balance", "Reported", "Projected closing", "Movement"],
            rows,
            formulas=[
                dict(cell=f"E{n}", formula=f"=D{n}-C{n}", value=row[4])
                for n, row in enumerate(rows, 5)
            ],
        )
        add(
            "CFO bridge",
            [
                "Company",
                "Prior WC cash contribution",
                "Projected pre-WC CFO",
                "Projected change NWC",
                "Projected CFO",
                "Projected cash",
                "Accessible cash",
                "Excluded accounting cash",
            ],
            [
                [
                    b["company"],
                    b["reference_wc_cash"],
                    b["pre_working_capital_cfo"],
                    b["projected_nwc_change"],
                    b["projected_cfo"],
                    b["projected_cash"],
                    b["usable_cash"],
                    b["projected_cash"] - b["usable_cash"],
                ]
                for b in public["projected_bridge"]
            ],
            formulas=[
                dict(cell=f"E{n}", formula=f"=C{n}-D{n}", value=b["projected_cfo"])
                for n, b in enumerate(public["projected_bridge"], 5)
            ],
        )
        add(
            "Cost reconciliation",
            [
                "Company",
                "Reported revenue",
                "Reported COS",
                "Reported SG&A",
                "Other operating cost",
                "Separately presented D&A",
                "Operating profit",
                "D&A add-back",
                "Starting EBITDA",
                "Separate lease cost",
                "Nonrent cost pool",
                "Assumed variable share",
            ],
            [
                [
                    public["config"]["companies"][i]["name"],
                    c["reported"]["revenue"],
                    c["reported"]["cost_of_sales"],
                    c["reported"]["sga"],
                    c["reported"]["other_operating"],
                    c["reported"].get("separate_da", 0),
                    c["reported"]["operating_profit"],
                    c["da_addback"],
                    c["starting_ebitda"],
                    c["separate_lease_cost"],
                    c["nonrent_cash_cost_pool"],
                    c["assumed_variable_share"],
                ]
                for i, c in enumerate(public["cost_reconciliation"])
            ],
        )
        extras[-1]["number_formats"] = [dict(column=11, format="0.0%")]
    if public and public.get("base"):
        add(
            "Investment assumptions",
            [
                "Company",
                "Initial gross budget",
                "Assumed maintenance",
                "Residual growth budget",
            ],
            [
                [
                    x["company"],
                    x["gross"],
                    x["assumed_maintenance"],
                    x["residual_growth"],
                ]
                for x in public["investment_split"]
            ],
        )
    if model and model.get("joint_stress"):
        add(
            "Joint credit stress",
            [
                "Structure",
                "Margin bp",
                "Rate bp",
                "Cash cushion USD m",
                "All screens pass",
                "First breach",
            ],
            [
                [
                    c["structure"],
                    c["margin_bp"],
                    c["rate_bp"],
                    c["cash_headroom"],
                    c["feasible"],
                    constraint(c["first_breach"]),
                ]
                for c in model["joint_stress"]["cells"]
            ],
        )
    bond = report.get("bond_lab")
    if bond:
        add(
            "Illustrative bond risk",
            ["Metric", "Value"],
            [
                ["Scope", bond["scope"]],
                ["Notional USD", bond["inputs"]["notional"]],
                ["Price per 100", bond["price"]],
                ["Modified duration", bond["modified_duration"]],
                ["Convexity", bond["convexity"]],
                ["DV01 USD per bp", bond["dv01"]],
                ["CS01 USD per bp", bond["cs01"]],
                ["Hypothetical short contracts", bond["hedge_short_contracts"]],
                ["Residual DV01 USD per bp", bond["residual_dv01"]],
                ["Limitations", bond["limitations"]],
            ],
        )
        extras[-1]["rows"][1][
            0
        ] = "Standalone hypothetical bond. Dollar risks are USD, not USD millions."
    # Keep established sheets, positions within each sheet and useful historic material.
    for spec in sheets:
        if spec["name"] == "Summary":
            spec["rows"] += [
                [
                    "Calculation status",
                    (
                        "Conditional public case available"
                        if public and public.get("base")
                        else (
                            "Synthetic demonstration operational"
                            if report.get("model")
                            else "Strict historical assessment only"
                        )
                    ),
                ],
                [
                    "Selected timing",
                    model.get("timing_basis", "Annual") if model else "Unavailable",
                ],
            ]
        if spec["name"] == "Public operations":
            spec["rows"][2][4] = "Model variable costs"
            spec["rows"][2][5] = "Other variable costs"
        if spec["name"] in ("Sources Uses", "Public sources and uses"):
            spec["rows"] = [
                row
                for row in spec["rows"]
                if len(row) < 2 or row[1] not in ("itemised_uses", "itemised uses")
            ]
        if spec["name"] == "Public capacity and stress":
            for row in spec["rows"][3:]:
                if not row[0].startswith("Reverse"):
                    for column in (2, 3):
                        if row[column] is None:
                            row[column] = "No feasible solution"
        constraint_column = {
            "Capacity": 5,
            "Capacity Grid": 3,
            "Reverse Stress": 4,
            "Sensitivity": 3,
        }.get(spec["name"])
        if constraint_column is not None:
            for row in spec["rows"][3:]:
                raw = row[constraint_column]
                if isinstance(raw, str) and raw.startswith("{"):
                    row[constraint_column] = constraint(json.loads(raw))
    result = sheets[:1] + extras + sheets[1:]
    contents = dict(
        name="Contents",
        rows=[
            [
                "Acquisition financing research | "
                + (
                    "Public conditional analysis"
                    if public
                    else (
                        "Synthetic demonstration"
                        if report.get("model")
                        else "Strict evidence assessment"
                    )
                )
            ],
            ["Python snapshots: edit assumptions with the CLI or live dashboard."],
            [
                "Refresh",
                "Only displayed formulas recalculate. All forecasts, scenarios and capacity are Python snapshots.",
            ],
            ["Worksheet", "Purpose / navigation"],
        ]
        + [
            [
                x["name"],
                "Open the named worksheet tab. "
                + (
                    "Primary result and status"
                    if x["name"] == "Summary"
                    else "Supporting schedule / evidence"
                ),
            ]
            for x in result
        ],
        header_row=5,
        widths=[38, 105],
        formulas=[],
        number_formats=[],
    )
    return [contents] + result


def constraint(breach):
    if not breach:
        return "No limiting breach at tested funding bound"
    return (
        breach["constraint"].capitalize()
        + " at "
        + (
            "closing"
            if breach["period"] == 0
            else f"year {breach['year']}, period {breach['period']}"
        )
    )
