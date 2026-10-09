"""End-to-end boundaries: evidence, calculation, storage and portable outputs."""

import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from financing.config import demo_config
from financing.engine import run
from financing.report import build_report
from financing.exports import export_all
from financing.ingestion import fetch
from financing.policy import BLOCKED
from financing.solver import capacity
from test_evidence import reviewed_fixture


class IntegrationTests(unittest.TestCase):
    def test_recheck_removes_stale_pdf_when_pdf_not_regenerated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "financing-memo.pdf").write_bytes(b"stale recommendation")
            case = {"sources": [], "observations": []}
            export_all(build_report(case, root), case, root)
            self.assertFalse((root / "financing-memo.pdf").exists())

    def test_required_source_removal_blocks_full_model_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = reviewed_fixture(root)
            before = build_report(case, root, demo_config(), full=False)
            self.assertFalse(before["evidence"]["blocked"])
            (root / case["sources"][0]["path"]).unlink()
            after = build_report(case, root, demo_config(), full=False)
            self.assertEqual(after["recommendation_status"], BLOCKED)
            self.assertEqual(after["model"]["base"], before["model"]["base"])
            self.assertIsNone(after["preferred_structure"])
            self.assertEqual(after["historical_results"], [])
            export_all(after, case, root / "out")
            for name in ("report.json", "memo.md", "dashboard.html"):
                self.assertIn(
                    BLOCKED, (root / "out" / name).read_text(encoding="utf-8")
                )

    def test_capacity_next_dollar_fails_and_results_reproduce(self):
        c = demo_config()
        s = capacity(c, "Cash-first")
        best = s["maximum_acquisition_borrowing"]
        self.assertTrue(run(c, acquisition_borrowing=best)["feasible"])
        self.assertFalse(run(c, acquisition_borrowing=best + 1)["feasible"])
        self.assertEqual(run(c), run(c))

    def test_download_retry_cache_and_integrity(self):
        calls = []
        sleeps = []

        def opener(request, timeout):
            calls.append(request.full_url)
            if len(calls) == 1:
                raise HTTPError(
                    request.full_url, 429, "limited", {"Retry-After": "999"}, None
                )
            return io.BytesIO(b"reviewable source")

        with tempfile.TemporaryDirectory() as tmp:
            path, meta = fetch(
                "https://example.invalid/fact",
                tmp,
                "test",
                opener=opener,
                sleeper=sleeps.append,
            )
            self.assertEqual(len(calls), 2)
            self.assertIn(10, sleeps)
            self.assertEqual(
                fetch("https://example.invalid/fact", tmp, "test", opener=opener)[1],
                meta,
            )
            self.assertEqual(len(calls), 2)
            path.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                fetch("https://example.invalid/fact", tmp, "test", opener=opener)

    def test_forbidden_download_is_not_retried(self):
        calls = []

        def opener(request, timeout):
            calls.append(1)
            raise HTTPError(request.full_url, 403, "forbidden", {}, None)

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(HTTPError):
                fetch(
                    "https://example.invalid/fact",
                    tmp,
                    "test",
                    opener=opener,
                    sleeper=lambda _: None,
                )
        self.assertEqual(len(calls), 1)

    def test_portable_excel_and_two_page_memo(self):
        try:
            import openpyxl
            import xlsxwriter
            import reportlab
            from pypdf import PdfReader
        except ImportError:
            self.skipTest("Install .[exports,test] for artifact integration")
        from financing.pdf_memo import write_pdf

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = {"sources": [], "observations": []}
            report = build_report(case, root, demo_config(), full=False)
            with patch.dict(os.environ, {"FINANCING_NODE": str(root / "no-node")}):
                export_all(report, case, root, excel=True)
            wb = openpyxl.load_workbook(root / "evidence-review.xlsx", data_only=True)
            self.assertEqual(len(wb.sheetnames), 20)
            self.assertEqual(wb["Summary"]["B3"].value, BLOCKED)
            self.assertAlmostEqual(
                wb["Liquidity"]["Q5"].value,
                report["model"]["base"][0]["years"][0]["closing_cash"],
            )
            for sheet in wb:
                for row in sheet:
                    self.assertFalse(
                        any(cell.data_type == "e" for cell in row), sheet.title
                    )
            wb.close()
            write_pdf(report, root / "memo.pdf")
            pdf = PdfReader(root / "memo.pdf")
            self.assertEqual(len(pdf.pages), 2)
            self.assertIn("insufficient verified evidence", pdf.pages[0].extract_text())


if __name__ == "__main__":
    unittest.main()
