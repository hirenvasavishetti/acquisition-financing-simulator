import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlparse, parse_qs
from .exports import dashboard, export_all
from .report import build_report


def read_case(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def evaluate(
    case_path,
    illustration_path=None,
    demo=False,
    database_path=None,
    full=True,
    overrides=None,
    public_information=False,
    public_overrides=None,
    frequency=1,
    fee_convention=None,
):
    if public_information and fee_convention:
        public_overrides = {
            **(public_overrides or {}),
            "fee_convention": fee_convention,
        }
    case = read_case(case_path) if case_path else {"observations": [], "sources": []}
    from .config import demo_config

    illustrative = (
        demo_config()
        if demo
        else read_case(illustration_path) if illustration_path else None
    )
    if illustrative:
        illustrative["frequency"] = frequency
        if fee_convention:
            illustrative["transaction"]["fee_convention"] = fee_convention
    if overrides:
        if not illustrative or illustrative.get("mode") != "synthetic":
            raise ValueError("Live overrides apply only to synthetic scenarios")
        for key, value in overrides.items():
            illustrative["policy"][key] = value
    return (
        case,
        build_report(
            case,
            Path(case_path).resolve().parent if case_path else Path.cwd(),
            illustrative,
            database_path,
            full,
            public_information,
            public_overrides,
        ),
    )


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Check evidence before any company recommendation"
    )
    parser.add_argument("case", type=Path, nargs="?")
    parser.add_argument(
        "--frequency",
        type=int,
        choices=(1, 4),
        default=1,
        help="Consistent model, capacity and reverse-stress periods per year; public case remains annual",
    )
    parser.add_argument(
        "--public-assumptions",
        type=Path,
        help="JSON future assumptions, never source facts",
    )
    parser.add_argument("--fee-convention", choices=("fixed_budget", "issued_debt"))
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the complete deterministic fictional simulator",
    )
    parser.add_argument(
        "--public-information",
        action="store_true",
        help="Add dependency-gated public-information projections without clearing the strict assessment",
    )
    parser.add_argument(
        "--database", type=Path, help="SQLite input store and run history"
    )
    parser.add_argument(
        "--query",
        choices=("summary", "gaps", "sources", "observations", "maturities", "public"),
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Base-only engineering preview; omit full stress/sensitivity work",
    )
    parser.add_argument(
        "--require-historical",
        action="store_true",
        help="Return exit 2 for historical blockers even in demo mode",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Export a two-page financing memo (requires reportlab)",
    )
    parser.add_argument(
        "--fetch-url", help="Download a source into --cache with bounded retries"
    )
    parser.add_argument("--cache", type=Path, default=Path("generated/cache"))
    parser.add_argument(
        "--sec-facts",
        choices=("acquirer", "target"),
        help="Retrieve pre-cutoff SEC Company Facts candidates",
    )
    parser.add_argument(
        "--illustrative-inputs",
        type=Path,
        help="Explicit separate anonymous scenario data; never fills historical gaps",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--excel", action="store_true")
    parser.add_argument("--serve", type=int, metavar="PORT")
    args = parser.parse_args(argv)
    if args.fetch_url or args.sec_facts:
        import os
        from .ingestion import fetch, companyfacts_candidates

        url = (
            args.fetch_url
            or f"https://data.sec.gov/api/xbrl/companyfacts/CIK{('0001089063' if args.sec_facts == 'acquirer' else '0000850209')}.json"
        )
        path, metadata = fetch(
            url,
            args.cache,
            os.environ.get("SEC_USER_AGENT", "AcquisitionFinancingSimulator research"),
        )
        output = {"path": str(path), **metadata}
        if args.sec_facts:
            output["candidates"] = companyfacts_candidates(
                json.loads(path.read_text()),
                [
                    "Revenues",
                    "RevenueFromContractWithCustomerExcludingAssessedTax",
                    "OperatingIncomeLoss",
                    "CashAndCashEquivalentsAtCarryingValue",
                    "NetCashProvidedByUsedInOperatingActivities",
                    "PaymentsToAcquirePropertyPlantAndEquipment",
                ],
            )
        print(json.dumps(output, indent=2))
        return 0
    if args.query:
        if not args.database:
            parser.error("--query requires --database")
        from .database import connect, QUERIES

        db = connect(args.database)
        print(json.dumps([dict(r) for r in db.execute(QUERIES[args.query])], indent=2))
        db.close()
        return 0
    if not args.case and (not args.demo):
        parser.error("Supply a historical case JSON or --demo")
    if (args.excel or args.pdf) and args.output is None:
        parser.error("--excel and --pdf require --output")
    if args.serve is not None:

        class Handler(BaseHTTPRequestHandler):

            def do_GET(self):
                try:
                    query = parse_qs(urlparse(self.path).query)
                    mode = query.get(
                        "mode",
                        [
                            (
                                "public"
                                if args.public_information
                                else "synthetic" if args.demo else "strict"
                            )
                        ],
                    )[0]
                    if mode not in ("public", "synthetic", "strict"):
                        raise ValueError("Unknown mode")
                    overrides = (
                        {
                            k: float(query[k][0])
                            for k in ("cash_floor", "max_leverage", "min_coverage")
                            if k in query
                        }
                        if mode == "synthetic"
                        else None
                    )
                    from .public_inputs import form_overrides

                    public_choices = (
                        read_case(args.public_assumptions)
                        if args.public_assumptions
                        else {}
                    )
                    if mode == "public":
                        public_choices.update(form_overrides(query))
                    frequency = int(query.get("frequency", [args.frequency])[0])
                    if mode == "public" and frequency != 1:
                        raise ValueError(
                            "Historical quarterly inputs insufficient: public case supports annual timing only"
                        )
                    _, report = evaluate(
                        args.case,
                        args.illustrative_inputs,
                        mode == "synthetic",
                        args.database,
                        not args.quick,
                        overrides,
                        mode == "public",
                        public_choices,
                        frequency,
                        query.get("fee_convention", [args.fee_convention])[0],
                    )
                    is_api = urlparse(self.path).path == "/api/report"
                    body = (
                        json.dumps(report, ensure_ascii=False)
                        if is_api
                        else dashboard(report)
                    ).encode("utf-8")
                    self.send_response(200)
                except (ValueError, KeyError, TypeError, OSError) as exc:
                    from .policy import BLOCKED
                    from html import escape

                    body = (
                        json.dumps(
                            {"recommendation_status": BLOCKED, "error": str(exc)}
                        )
                        if urlparse(self.path).path == "/api/report"
                        else f"<h1>{BLOCKED}</h1><p>Input validation failed: {escape(str(exc))}</p>"
                    ).encode("utf-8")
                    self.send_response(422)
                self.send_header(
                    "Content-Type",
                    (
                        "application/json; charset=utf-8"
                        if urlparse(self.path).path == "/api/report"
                        else "text/html; charset=utf-8"
                    ),
                )
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

        print(f"Live evidence dashboard: http://127.0.0.1:{args.serve}", flush=True)
        HTTPServer(("127.0.0.1", args.serve), Handler).serve_forever()
        return 0
    try:
        database = args.database or (
            args.output / "model.sqlite" if args.output and args.demo else None
        )
        if args.public_information and args.frequency != 1:
            raise ValueError("Public information supports annual timing only")
        case, report = evaluate(
            args.case,
            args.illustrative_inputs,
            args.demo,
            database,
            not args.quick,
            public_information=args.public_information,
            public_overrides=(
                read_case(args.public_assumptions) if args.public_assumptions else None
            ),
            frequency=args.frequency,
            fee_convention=args.fee_convention,
        )
        if args.output:
            export_all(report, case, args.output, args.excel)
            if args.pdf:
                from .pdf_memo import write_pdf

                write_pdf(report, args.output / "financing-memo.pdf")
        print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
        return (
            2
            if (report["evidence"]["blocked"] or report.get("historical_mapping_error"))
            and (not args.demo or args.require_historical)
            else 0
        )
    except (ValueError, KeyError, TypeError, OSError) as exc:
        from .policy import BLOCKED

        report = build_report(
            {"observations": [], "sources": []},
            args.case.parent if args.case else Path.cwd(),
        )
        report["error"] = f"Input validation failed: {exc}"
        report["analysis_limitation"] = report["error"]
        if args.output:
            export_all(report, {"sources": []}, args.output, args.excel)
        print(json.dumps(report, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())

# Preserved implementation notes
# Redirected Windows stdout must remain UTF-8 JSON, including blocked status.
# Replace stale snapshots with blocked outputs even when case JSON cannot load.
