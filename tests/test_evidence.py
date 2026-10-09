"""All purported sources here are artificial TEST FIXTURES, never historical evidence."""

import copy
from hashlib import sha256
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
import os

from financing.cli import main
from financing.evidence import check_evidence, fingerprint
from financing.exports import dashboard, memo, export_all
from financing.model import calculate
from financing.policy import REQUIREMENTS, BLOCKED, VERIFIED
from financing.report import build_report

ROOT = Path(__file__).resolve().parents[1]
ILLUSTRATIVE = json.loads((ROOT / "data/illustrative.json").read_text())


def reviewed_fixture(root):
    """Create a logically complete gate fixture; values are not company facts."""
    case = {"observations": [], "sources": []}
    for n, req in enumerate(REQUIREMENTS):
        if req.assumption_allowed:
            case["observations"].append(
                {
                    "key": req.key,
                    "value": "Future TEST choice",
                    "kind": "assumption",
                    "origin": "analyst",
                    "rationale": "Explicit test modelling choice",
                }
            )
            continue
        obs = {
            "key": req.key,
            "kind": "fact",
            "origin": "reported",
            "value": 1,
            "company": req.key.split(".")[0],
            "units": "USD millions (TEST)",
            "period_start": "2024-01-01",
            "period_end": "2024-12-31",
            "extraction_method": "TEST FIXTURE ONLY",
        }
        payload = {
            k: obs[k]
            for k in ("key", "value", "company", "units", "period_start", "period_end")
        }
        data = f"TEST FIXTURE ONLY, no historical content: {req.key}".encode()
        path = f"source-{n}.txt"
        (root / path).write_bytes(data)
        case["observations"].append(obs)
        case["sources"].append(
            {
                "id": f"s{n}",
                "document_id": "test-document",
                "url": "https://example.invalid/test-fixture",
                "published": "2025-03-01",
                "retrieved": "2026-09-11T00:00:00Z",
                "path": path,
                "sha256": sha256(data).hexdigest(),
                "claims": [
                    {
                        "key": req.key,
                        "payload_hash": fingerprint(payload),
                        "section": "Test section",
                        "reviewer": "TEST reviewer",
                        "reviewed_at": "2026-09-11",
                        "review_note": "Fixture simulates an exact observation review; not company evidence",
                    }
                ],
            }
        )
    return case


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.case = reviewed_fixture(self.root)

    def gate(self):
        return check_evidence(self.case, self.root)

    def first(self):
        return next(r for r in self.gate()["rows"] if r["key"] == REQUIREMENTS[0].key)

    def test_complete_review_fixture_clears_only_evidence_gate(self):
        self.assertEqual(self.gate()["status"], VERIFIED)
        report = build_report(self.case, self.root)
        self.assertIsNone(report["preferred_structure"])
        self.assertFalse(report["historical_analysis_complete"])

    def test_removing_required_source_blocks_even_when_model_calculates(self):
        before = build_report(self.case, self.root, ILLUSTRATIVE)
        self.assertFalse(before["evidence"]["blocked"])
        (self.root / self.case["sources"][0]["path"]).unlink()
        after = build_report(self.case, self.root, ILLUSTRATIVE)
        self.assertEqual(after["recommendation_status"], BLOCKED)
        self.assertEqual(after["illustrative_results"], before["illustrative_results"])
        self.assertEqual(len(after["illustrative_results"]), 3)
        self.assertIsNone(after["preferred_structure"])
        self.assertEqual(after["historical_results"], [])
        self.assertIn("Missing source", self.first()["reason"])
        self.assertTrue(self.first()["affected_calculations"])
        self.assertTrue(self.first()["resolution"])

    def test_deleting_source_register_record_blocks(self):
        self.case["sources"].pop(0)
        self.assertTrue(self.gate()["blocked"])

    def test_fact_cannot_become_assumption(self):
        self.case["observations"][0].update(
            kind="assumption", origin="analyst", rationale="Guess"
        )
        self.assertEqual(self.first()["classification"], "missing evidence")
        self.assertIn("cannot be relabelled", self.first()["reason"])

    def test_synthetic_fact_cannot_pass_even_with_matching_claim(self):
        self.case["observations"][0]["origin"] = "synthetic"
        self.assertTrue(self.gate()["blocked"])

    def test_removed_observation_stays_required(self):
        self.case["observations"].pop(0)
        self.assertEqual(len(self.gate()["rows"]), len(REQUIREMENTS))
        self.assertTrue(self.gate()["blocked"])

    def test_optional_flag_cannot_waive_policy(self):
        self.case["observations"][0].update(value=None, material=False, required=False)
        self.assertTrue(self.gate()["blocked"])

    def test_duplicate_observation_is_conflict(self):
        self.case["observations"].append(copy.deepcopy(self.case["observations"][0]))
        self.assertEqual(self.first()["classification"], "conflicting evidence")

    def test_differing_reviewed_claim_blocks(self):
        self.case["sources"][0]["claims"].append(
            {**self.case["sources"][0]["claims"][0], "payload_hash": "different"}
        )
        self.assertEqual(self.first()["classification"], "conflicting evidence")

    def test_explicit_unresolved_conflict_blocks(self):
        self.case["observations"][0]["conflict"] = "Unresolved footnote disagreement"
        self.assertEqual(self.first()["classification"], "conflicting evidence")

    def test_changing_value_requires_new_review(self):
        self.case["observations"][0]["value"] = 42
        self.assertTrue(self.gate()["blocked"])

    def test_changed_source_bytes_block(self):
        (self.root / self.case["sources"][0]["path"]).write_text("changed")
        self.assertIn("hash mismatch", self.first()["reason"])

    def test_post_cutoff_publication_blocks_but_later_retrieval_is_allowed(self):
        self.assertFalse(self.gate()["blocked"])
        self.case["sources"][0]["published"] = "2025-05-16"
        self.assertTrue(self.gate()["blocked"])

    def test_missing_review_blocks(self):
        del self.case["sources"][0]["claims"][0]["reviewer"]
        self.assertTrue(self.gate()["blocked"])

    def test_unknown_material_input_blocks(self):
        self.case["observations"].append(
            {"key": "new.unmapped", "kind": "assumption", "value": 1}
        )
        self.assertTrue(self.gate()["blocked"])

    def test_null_and_nan_are_missing_not_zero(self):
        for value in (None, float("nan"), "", {}):
            with self.subTest(value=value):
                self.case["observations"][0]["value"] = value
                if isinstance(value, float):
                    # Invalid JSON numeric values are rejected rather than serialized as valid evidence.
                    with self.assertRaises(ValueError):
                        self.gate()
                else:
                    self.assertEqual(self.first()["classification"], "missing evidence")

    def test_no_historical_synthetic_fallback(self):
        report = build_report({"observations": [], "sources": []}, self.root)
        self.assertEqual(report["illustrative_results"], [])
        self.assertEqual(report["historical_results"], [])
        self.assertEqual(report["recommendation_status"], BLOCKED)

    def test_output_propagation_and_no_cached_recommendation(self):
        self.case.update(
            preferred_structure="Cash-first", recommendation_status="Approved"
        )
        self.case["sources"].pop(0)
        report = build_report(self.case, self.root, ILLUSTRATIVE)
        export_all(report, self.case, self.root / "export")
        for name in ("report.json", "memo.md", "dashboard.html"):
            self.assertIn(
                BLOCKED, (self.root / "export" / name).read_text(encoding="utf-8")
            )
        self.assertIsNone(report["preferred_structure"])
        path = self.root / "case.json"
        path.write_text(json.dumps(self.case))
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([str(path)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out.getvalue())["recommendation_status"], BLOCKED)

    def test_dashboard_escapes_source_text(self):
        self.case["observations"][0]["conflict"] = True
        report = build_report(self.case, self.root)
        report["evidence"]["rows"][0]["reason"] = "<script>alert(1)</script>"
        self.assertNotIn("<script>alert(1)", dashboard(report))

    def test_malformed_case_overwrites_stale_reports_with_blocked_status(self):
        path = self.root / "case.json"
        path.write_text("{invalid json")
        output = self.root / "output"
        output.mkdir()
        (output / "memo.md").write_text("Old recommendation")
        with redirect_stdout(io.StringIO()):
            code = main([str(path), "--output", str(output)])
        self.assertEqual(code, 2)
        self.assertIn(BLOCKED, (output / "memo.md").read_text(encoding="utf-8"))

    def test_malformed_schema_is_rejected(self):
        for case in (
            [],
            {"sources": None},
            {"observations": [{}]},
            {"sources": [{"id": "s", "claims": [None]}]},
        ):
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    check_evidence(case, self.root)

    def test_every_required_category_blocks_on_source_removal(self):
        categories = {r.category for r in REQUIREMENTS if not r.assumption_allowed}
        for category in categories:
            with self.subTest(category=category):
                from financing.policy import materiality

                key = next(
                    r.key
                    for r in REQUIREMENTS
                    if r.category == category and materiality(r.key)[0]
                )
                source = next(
                    s for s in self.case["sources"] if s["claims"][0]["key"] == key
                )
                original = source["path"]
                source["path"] = "absent-source.txt"
                self.assertEqual(self.gate()["status"], BLOCKED)
                source["path"] = original

    @unittest.skipUnless(
        os.environ.get("FINANCING_NODE"), "Optional bundled Node/Excel integration"
    )
    def test_required_source_removal_reaches_saved_excel_and_cli_json(self):
        from openpyxl import load_workbook

        self.case["sources"].pop(0)
        case_path = self.root / "case.json"
        case_path.write_text(json.dumps(self.case))
        dest = self.root / "export"
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(
                [
                    str(case_path),
                    "--output",
                    str(dest),
                    "--excel",
                    "--illustrative-inputs",
                    str(ROOT / "data/illustrative.json"),
                ]
            )
        self.assertEqual(code, 2)
        self.assertEqual(
            json.loads(stdout.getvalue())["recommendation_status"], BLOCKED
        )
        book = load_workbook(dest / "evidence-review.xlsx", data_only=True)
        self.assertEqual(book["Summary"]["B3"].value, BLOCKED)
        self.assertEqual(book["Summary"]["B4"].value, "None")
        self.assertEqual(book["Summary"]["B9"].value, "Unavailable")
        self.assertIn("Illustrative", book["Scenarios"]["A2"].value)
        self.assertAlmostEqual(book["Scenarios"]["D5"].value, 717.2)
        book.close()


class ModelTests(unittest.TestCase):
    def test_independent_benchmark(self):
        expected = json.loads((ROOT / "tests/benchmark.json").read_text())
        first = calculate(ILLUSTRATIVE)[0]
        for key in (
            "cash_uses",
            "cash_contribution",
            "new_borrowing",
            "opening_cash",
            "opening_debt",
        ):
            self.assertAlmostEqual(first[key], expected[key])
        for key in ("interest", "repayment", "closing_cash", "closing_debt"):
            self.assertAlmostEqual(first["years"][0][key], expected[key])

    def test_deterministic_and_rollforwards(self):
        outputs = calculate(ILLUSTRATIVE)
        self.assertEqual(outputs, calculate(ILLUSTRATIVE))
        for case in outputs:
            self.assertAlmostEqual(
                case["cash_uses"], case["cash_contribution"] + case["new_borrowing"]
            )
            for year in case["years"]:
                self.assertAlmostEqual(
                    year["closing_debt"], year["opening_debt"] - year["repayment"]
                )
                self.assertAlmostEqual(
                    year["closing_cash"],
                    year["opening_cash"] + 150 - year["interest"] - year["repayment"],
                )
                self.assertLessEqual(year["repayment"], year["opening_debt"])

    def test_missing_model_input_raises_without_demo_substitution(self):
        p = dict(ILLUSTRATIVE)
        del p["cash"]
        with self.assertRaises(ValueError):
            calculate(p)

    def test_maturity_gap_and_unavailable_ratios(self):
        p = {**ILLUSTRATIVE, "pre_interest_cash_flow": 0, "ebitda": 0}
        year = calculate(p)[0]["years"][-1]
        self.assertGreater(year["maturity_gap"], 0)
        self.assertIsNone(year["coverage"])
        self.assertIsNone(year["net_leverage"])


if __name__ == "__main__":
    unittest.main()
