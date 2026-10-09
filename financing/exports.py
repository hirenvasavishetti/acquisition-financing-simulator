"""Snapshot exports. Regenerate after changing sources; HTML server is live."""

import html
import json
import os
from pathlib import Path
import subprocess


def evidence_memo(report):
    lines = [
        "# Acquisition financing evidence review",
        "",
        report["recommendation_status"],
        "",
        "No preferred financing structure is named for DICK'S Sporting Goods / Foot Locker.",
        "",
        report["analysis_limitation"],
        "",
        "## Evidence gaps and resolutions",
        "",
    ]
    lines += [
        "## Supported historical calculations",
        "",
        report.get("historical_capacity_status", ""),
        "",
    ]
    for x in report.get("supported_historical_calculations", []):
        lines.append(
            f"- **{x['calculation']}**: {(x['value'] if x['status'] == 'Supported' else 'Unavailable')} {x['units']}. {x['formula']}. {x['limitation']} Dependencies: {', '.join(x['dependencies'])}."
        )
    lines += ["", "## Review of the original 36 material gaps", ""]
    lines += [
        "The six future choices are analyst assumptions, not additional verified historical facts. Operating sensitivities test annual growth 0/-5/-10% and EBITDA margin changes 0/-100/-200bp over five years. Unit financing and synergy sensitivities follow; complete debt capacity and liquidity reverse stress remain unavailable.",
        "",
    ]
    for x in report.get("historical_financing_sensitivities", []):
        lines.append(
            f"- {x['study']}: {x['assumptions']} => {x['value']:.3f} {x['units']}. {x['limitation']}"
        )
    for g in report.get("historical_gap_register", []):
        lines += [
            f"### {g['key']} — {g['status']}",
            f"{g['nature']}; {g['classification']}. Affects: {g['affected_calculation']}. Material because: {g['materiality']}",
            f"Current evidence: {g['current_evidence']}",
            f"Missing: {g['missing_information']}",
            f"Applicability: {g['applicability']}",
            f"Resolve: {g['proposed_resolution']} Primary source: {g['primary_source']}",
            "",
        ]
    for row in report["evidence"]["rows"]:
        if row["classification"] in ("missing evidence", "conflicting evidence"):
            lines.extend(
                [
                    f"- **{row['key']} — {row['classification']}**: {row['reason']}. Affected calculations: {row['affected_calculations']}. Resolution: {row['resolution']}"
                ]
            )
    lines += ["", "## Illustrative scenarios", "", report["illustrative_label"], ""]
    for case in report["illustrative_results"]:
        lines.append(
            f"- {case['structure']}: opening cash {case['opening_cash']:.2f}; opening debt {case['opening_debt']:.2f} (USD millions)."
        )
    if "model" in report:
        lines += [
            "",
            "## Conditional illustrative assessment",
            "",
            report["model"]["recommendation"]["narrative"],
            "",
            "The separate financing-memo.pdf is the two-page illustrative financing memo. The full workbook and JSON contain schedules, capacity, sensitivities and stress results.",
        ]
    lines += [
        "",
        "This detailed evidence register supplements the financing memo; it is not an actual-company recommendation.",
        "Snapshot: rerun after changing inputs or sources.",
        f"Input ID: {report['evidence']['case_id']}",
        "",
    ]
    if report.get("public_information"):
        from .public_exports import markdown

        lines.insert(5, markdown(report["public_information"]))
        lines.append(
            "The strict assessment above concerns complete historical financing; the separate public case reports scoped conditional capacity and schedules."
        )
    return "\n".join(lines)


def memo(report):
    from .portfolio_memo import markdown

    return markdown(report)


def dashboard(report):
    from .portfolio_dashboard import page

    return page(report)


def export_all(report, case, destination, excel=False):
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "evidence-review.xlsx").unlink(missing_ok=True)
    (dest / "financing-memo.pdf").unlink(missing_ok=True)
    (dest / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    (dest / "evidence-detail.md").write_text(evidence_memo(report), encoding="utf-8")
    (dest / "memo.md").write_text(memo(report), encoding="utf-8")
    (dest / "dashboard.html").write_text(dashboard(report), encoding="utf-8")
    (dest / "gap-register.json").write_text(
        json.dumps(
            report.get("historical_gap_register", []), indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )
    (dest / "source-register.json").write_text(
        json.dumps(case.get("sources", []), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    for name, key in [
        ("public-information.json", None),
        ("public-gap-assessment.json", "gap_assessment"),
    ]:
        if report.get("public_information"):
            payload = (
                report["public_information"]
                if key is None
                else report["public_information"][key]
            )
            (dest / name).write_text(
                json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False),
                encoding="utf-8",
            )
        else:
            (dest / name).unlink(missing_ok=True)
    if excel:
        from .workbook_plan import make_plan

        plan = make_plan(report, case)
        builder = Path(__file__).with_name("workbook.mjs")
        target = dest / "evidence-review.xlsx"
        payload = json.dumps(
            {"report": report, "case": case, "plan": plan}, allow_nan=False
        )
        try:
            result = subprocess.run(
                [os.environ.get("FINANCING_NODE", "node"), str(builder), str(target)],
                input=payload,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=True,
                env={
                    k: v for k, v in os.environ.items() if k != "FINANCING_PREVIEW_DIR"
                },
            )
        except FileNotFoundError:
            from .portable_excel import write_xlsx

            write_xlsx(plan, target)
        except subprocess.CalledProcessError as exc:
            if "ERR_MODULE_NOT_FOUND" not in (exc.stderr or ""):
                raise
            from .portable_excel import write_xlsx

            write_xlsx(plan, target)


def historical_html(report):
    e = html.escape

    def table(heads, rows):
        return (
            '<div style="overflow:auto;max-height:550px"><table><tr>'
            + "".join(("<th>" + e(h) + "</th>" for h in heads))
            + "</tr>"
            + "".join(
                (
                    "<tr>"
                    + "".join(("<td>" + e(str(c)) + "</td>" for c in row))
                    + "</tr>"
                    for row in rows
                )
            )
            + "</table></div>"
        )

    calcs = report.get("supported_historical_calculations", [])
    gaps = report.get("historical_gap_register", [])
    sensitivity = (
        "<h2>Explicit assumption sensitivities</h2><p>Operating study: annual growth 0/-5/-10%, EBITDA margin shifts 0/-100/-200bp, five years. These are hypothetical studies anchored to annual facts, not full forecasts or financing preferences.</p>"
        + table(
            ["Study", "Assumptions", "Value", "Units", "Limitations"],
            [
                [x[k] for k in ("study", "assumptions", "value", "units", "limitation")]
                for x in report.get("historical_financing_sensitivities", [])
            ],
        )
    )
    public = ""
    if report.get("public_information"):
        from .public_exports import dashboard

        public = dashboard(report["public_information"])
    return (
        public
        + "<h2>Supported historical calculations</h2><p>"
        + e(report.get("historical_capacity_status", ""))
        + "</p>"
        + table(
            ["Calculation", "Status", "Value", "Formula", "Limitations"],
            [
                [
                    x["calculation"],
                    x["status"],
                    x["value"],
                    x["formula"],
                    x["limitation"],
                ]
                for x in calcs
            ],
        )
        + sensitivity
        + "<h2>Original 36 material gaps</h2>"
        + table(
            [
                "Input",
                "Status / type",
                "Current evidence",
                "Missing information",
                "Applicability",
                "Primary source / resolution",
            ],
            [
                [
                    g["key"],
                    g["status"] + " / " + g["nature"],
                    g["current_evidence"],
                    g["missing_information"],
                    g["applicability"],
                    g["primary_source"] + " " + g["proposed_resolution"],
                ]
                for g in gaps
            ],
        )
    )


# Preserved implementation notes
# Never leave an old workbook beside freshly evaluated outputs when Excel was
# omitted or its new export fails. This path is an owned generated artifact.
