"""Portable fallback for installations without the bundled Artifact Tool.

The same workbook plan contains formulas and Python-validated cached results.
No financial calculation is reimplemented in this writer.
"""


def write_xlsx(plan, path):
    import xlsxwriter

    book = xlsxwriter.Workbook(
        str(path), {"strings_to_formulas": False, "strings_to_urls": False}
    )
    base = book.add_format(
        {
            "font_name": "Arial",
            "font_size": 11,
            "font_color": "#172C43",
            "valign": "vcenter",
            "text_wrap": True,
        }
    )
    number = book.add_format(
        {
            "font_name": "Arial",
            "font_size": 11,
            "num_format": '#,##0.0;(#,##0.0);"-"',
            "valign": "vcenter",
        }
    )
    header = book.add_format(
        {
            "font_name": "Arial",
            "bold": True,
            "bg_color": "#203D5B",
            "font_color": "#FFFFFF",
            "text_wrap": True,
            "valign": "vcenter",
        }
    )
    bad = book.add_format({"bg_color": "#FFF1EE", "font_color": "#B42318"})
    for spec in plan:
        sh = book.add_worksheet(spec["name"])
        sh.hide_gridlines(2)
        formats = {
            f["column"]: book.add_format(
                {
                    "font_name": "Arial",
                    "font_size": 11,
                    "num_format": f["format"],
                    "valign": "vcenter",
                }
            )
            for f in spec.get("number_formats", [])
        }
        for j, width in enumerate(spec["widths"]):
            sh.set_column(j, j, width)
        for i, row in enumerate(spec["rows"], 1):
            sh.set_row(
                i,
                (
                    150
                    if spec["name"] == "Historical gap review"
                    else (
                        210
                        if spec["name"] == "Historical assumptions"
                        else (
                            80
                            if spec["name"].startswith("Historical")
                            or spec["name"] == "Funding unit sensitivities"
                            else (
                                75
                                if spec["name"] == "Evidence"
                                else 45 if spec["name"] == "Summary" else 30
                            )
                        )
                    )
                ),
            )
            if spec["name"].startswith("Public"):
                sh.set_row(
                    i,
                    (
                        130
                        if spec["name"] == "Public gap assessment"
                        else (
                            100
                            if spec["name"]
                            in ("Public output policy", "Public conventions")
                            else 60
                        )
                    ),
                )
            for j, value in enumerate(row):
                fmt = (
                    header
                    if i + 1 == spec["header_row"]
                    else (
                        formats.get(j, number)
                        if isinstance(value, (int, float))
                        and (not isinstance(value, bool))
                        else base
                    )
                )
                if value is not None:
                    sh.write(i, j, value, fmt)
        if spec["header_row"]:
            sh.freeze_panes(spec["header_row"], 1)
            last = min(len(spec["widths"]), 6) - 1
            for index in (1, 2):
                if last > 0:
                    sh.merge_range(
                        index, 0, index, last, spec["rows"][index - 1][0], base
                    )
                sh.set_row(index, 36)
        for f in spec["formulas"]:
            sh.write_formula(f["cell"], f["formula"], number, f["value"])
        if spec["name"] == "Summary":
            sh.conditional_format(
                "B3",
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "Blocked",
                    "format": bad,
                },
            )
    book.close()
