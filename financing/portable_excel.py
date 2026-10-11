"""Presentation for the shared workbook plan; calculations stay in the model.

Cell addresses and Python-validated formula caches are preserved. Styling is
shared by every export, including the evidence-only historical assessment.
"""

import textwrap

TEAL = "#3C5658"
ORANGE = "#F15A29"
NUMBER = '#,##0.0;(#,##0.0);"-"'


def row_height(values, widths, *, size=11, minimum=24):
    """Allow wrapped prose to expand without enlarging every row."""
    lines = 1
    for value, width in zip(values, widths):
        if not isinstance(value, str):
            continue
        capacity = max(8, int((width - 2) * 11 / size))
        count = sum(
            max(1, len(textwrap.wrap(part, capacity))) for part in value.split("\n")
        )
        lines = max(lines, count)
    return min(409, max(minimum, lines * (size + 4) + 10))


def write_xlsx(plan, path):
    import xlsxwriter
    from xlsxwriter.utility import xl_cell_to_rowcol, xl_rowcol_to_cell

    book = xlsxwriter.Workbook(
        str(path), {"strings_to_formulas": False, "strings_to_urls": False}
    )
    common = dict(
        font_name="Arial",
        font_size=11,
        font_color="#25282D",
        valign="vcenter",
        text_wrap=True,
    )
    styles = {}

    def style(**properties):
        key = tuple(sorted(properties.items()))
        if key not in styles:
            styles[key] = book.add_format({**common, **properties})
        return styles[key]

    title = style(font_name="Georgia", font_size=22, font_color=ORANGE)
    context = style(
        font_size=10, italic=True, font_color="#536567", bottom=1, bottom_color=ORANGE
    )
    header = style(
        bold=True,
        italic=True,
        bg_color=TEAL,
        font_color="#FFFFFF",
        align="center",
        border=1,
        border_color="#C4CECE",
    )
    statuses = {
        "verified fact": ("#DFECD9", "#285232"),
        "Supported": ("#DFECD9", "#285232"),
        "explicit modelling assumption": ("#FFF0C2", "#765408"),
        "missing evidence": ("#FBE1DC", "#9D3028"),
        "conflicting evidence": ("#FBE1DC", "#9D3028"),
    }
    status_formats = {
        text: style(bg_color=fill, font_color=ink)
        for text, (fill, ink) in statuses.items()
    }
    bad = style(bg_color="#FBE1DC", font_color="#9D3028", bold=True)

    for spec in plan:
        sh = book.add_worksheet(spec["name"])
        sh.hide_gridlines(2)
        sh.set_zoom(90)
        sh.set_tab_color(ORANGE if spec["name"] in ("Contents", "Summary") else TEAL)
        widths = spec["widths"]
        last_col = len(widths) - 1
        formats = {f["column"]: f["format"] for f in spec.get("number_formats", [])}
        formulas = {xl_cell_to_rowcol(f["cell"]): f for f in spec["formulas"]}
        sh.set_row(0, 9)
        for j, width in enumerate(widths):
            sh.set_column(j, j, width)

        for i, row in enumerate(spec["rows"], 1):
            is_header = i + 1 == spec["header_row"]
            sh.set_row(i, row_height(row, widths, minimum=34 if is_header else 24))
            # Emphasise supplied totals; never infer new financial outcomes.
            total = any(
                str(v).lower()
                in (
                    "total uses",
                    "total sources",
                    "cash uses",
                    "sources less uses",
                    "sources_uses_difference",
                )
                for v in row[:2]
            )
            for j, value in enumerate(row):
                numeric = isinstance(value, (int, float)) and not isinstance(
                    value, bool
                )
                props = dict(
                    bg_color="#F3F6F5" if i % 2 else "#FFFFFF",
                    border=1,
                    border_color="#D5DEDD",
                    align="right" if numeric else "left",
                )
                if j == 0:
                    props.update(left=2, left_color=ORANGE)
                if total:
                    props.update(bold=True, top=2, top_color=TEAL)
                if numeric or (i, j) in formulas:
                    props.update(num_format=formats.get(j, NUMBER), align="right")
                fmt = header if is_header else style(**props)
                if i in (1, 2) and spec["header_row"] and j >= min(len(widths), 6):
                    fmt = style(bg_color="#FFFFFF")
                if i == 1 and not spec["header_row"] and j > 0:
                    fmt = style(bg_color="#FFFFFF")
                if (i, j) in formulas:
                    f = formulas[i, j]
                    sh.write_formula(i, j, f["formula"], fmt, f["value"])
                elif value is not None:
                    sh.write(i, j, value, fmt)
                else:
                    sh.write_blank(i, j, None, fmt)
                if not is_header and isinstance(value, str) and value in statuses:
                    cell = xl_rowcol_to_cell(i, j)
                    sh.conditional_format(
                        cell,
                        dict(
                            type="cell",
                            criteria="==",
                            value='"' + value + '"',
                            format=status_formats[value],
                        ),
                    )

        if spec["header_row"]:
            sh.freeze_panes(spec["header_row"], 1)
            last = min(len(widths), 6) - 1
            for index, fmt in ((1, title), (2, context)):
                value = spec["rows"][index - 1][0]
                if last > 0:
                    sh.merge_range(index, 0, index, last, value, fmt)
                else:
                    sh.write(index, 0, value, fmt)
                sh.set_row(
                    index,
                    row_height(
                        [value],
                        [sum(widths[: last + 1])],
                        size=22 if index == 1 else 10,
                        minimum=42 if index == 1 else 30,
                    ),
                )
            # Do not encourage sorting positional formula rollforwards.
            if not spec["formulas"]:
                sh.autofilter(spec["header_row"] - 1, 0, len(spec["rows"]), last_col)
            sh.repeat_rows(0, spec["header_row"] - 1)
        else:
            sh.write(1, 0, spec["rows"][0][0], title)
            sh.set_row(
                1, row_height([spec["rows"][0][0]], [widths[0]], size=22, minimum=52)
            )
        if spec["name"] == "Summary":
            sh.conditional_format(
                "B3",
                dict(type="text", criteria="containing", value="Blocked", format=bad),
            )
        sh.set_landscape()
        sh.set_paper(9)
        sh.set_margins(0.3, 0.3, 0.4, 0.4)
        # Wide evidence schedules print across pages at readable scale.
        sh.set_print_scale(85)
        sh.print_area(0, 0, len(spec["rows"]), last_col)
        sh.set_footer("&L" + spec["name"] + "&RPage &P of &N")
    book.close()
