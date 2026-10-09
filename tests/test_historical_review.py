import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from financing.evidence import check_evidence
from financing.historical_review import ORIGINAL_GAPS
from financing.report import build_report
from financing.config import demo_config
from financing.policy import BLOCKED, REQUIREMENTS

DATA = Path(__file__).resolve().parents[1] / "data"


class HistoricalReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "data"
        shutil.copytree(DATA, self.root)
        self.case = json.loads(
            (self.root / "historical.json").read_text(encoding="utf-8")
        )

    def test_narrow_resolution_and_independent_arithmetic(self):
        r = build_report(self.case, self.root)
        self.assertEqual(len(REQUIREMENTS), 109)
        self.assertEqual(len(ORIGINAL_GAPS), 36)
        self.assertEqual(
            sum(g["status"] == "Resolved" for g in r["historical_gap_register"]), 13
        )
        self.assertEqual(r["recommendation_status"], BLOCKED)
        self.assertFalse(r["historical_analysis_complete"])
        self.assertEqual(r["historical_results"], [])
        v = {
            x["calculation"]: x["value"] for x in r["supported_historical_calculations"]
        }
        self.assertAlmostEqual(v["acquirer FY2024 simple operating EBITDA"], 1874.341)
        self.assertEqual(v["target FY2024 simple operating EBITDA"], 305)
        self.assertAlmostEqual(v["Common shares all-cash consideration"], 2293.453968)
        self.assertEqual(v["FL cash reconciliation"], 0)
        self.assertEqual(v["FL finance-lease rollforward check"], 0)
        self.assertAlmostEqual(v["DKS note annual coupon obligation"], 54.375)

    def test_required_source_removal_suppresses_derived_history_not_synthetic_model(
        self,
    ):
        before = build_report(self.case, self.root, demo_config(), full=False)
        (self.root / "sources/review_fl.json").unlink()
        after = build_report(self.case, self.root, demo_config(), full=False)
        self.assertEqual(before["model"]["base"], after["model"]["base"])
        self.assertEqual(after["recommendation_status"], BLOCKED)
        self.assertIsNone(after["preferred_structure"])
        affected = next(
            x
            for x in after["supported_historical_calculations"]
            if x["calculation"] == "FL financial debt principal"
        )
        self.assertEqual(affected["status"], "Unavailable")
        self.assertIsNone(affected["value"])
        gate = {x["key"]: x for x in after["evidence"]["rows"]}
        self.assertEqual(
            gate["target.opening.debt_principal"]["classification"], "missing evidence"
        )

    def test_filing_removal_suppresses_operating_sensitivity(self):
        (self.root / "sources/dks10k.json").unlink()
        r = build_report(self.case, self.root)
        self.assertFalse(
            any(
                x["company"] == "acquirer"
                for x in r["historical_operating_sensitivities"]
            )
        )

    def test_post_cutoff_source_and_conflicting_derivation_fail_closed(self):
        next(s for s in self.case["sources"] if s["id"] == "merger")[
            "published"
        ] = "2025-05-16"
        self.case["observations"].append(
            dict(
                key="target.FY2024.ebitda_reconciliation",
                value=999,
                kind="fact",
                conflict=True,
            )
        )
        r = build_report(self.case, self.root)
        gate = {x["key"]: x for x in r["evidence"]["rows"]}
        self.assertEqual(
            gate["target.FY2024.ebitda_reconciliation"]["classification"],
            "conflicting evidence",
        )
        x = next(
            x
            for x in r["supported_historical_calculations"]
            if x["calculation"] == "Common shares all-cash consideration"
        )
        self.assertEqual(x["status"], "Unavailable")

    def test_unknown_supplement_cannot_waive_policy(self):
        self.case["observations"].append(
            dict(
                key="detail.fake",
                value=42,
                kind="assumption",
                origin="analyst",
                rationale="waive",
            )
        )
        x = next(
            x
            for x in check_evidence(self.case, self.root)["rows"]
            if x["key"] == "detail.fake"
        )
        self.assertTrue(x["recommendation_blocking"])
        self.assertEqual(x["classification"], "missing evidence")


if __name__ == "__main__":
    unittest.main()
