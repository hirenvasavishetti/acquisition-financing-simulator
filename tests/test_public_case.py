import json, shutil, tempfile, unittest
from pathlib import Path
from financing.report import build_report
from financing.public_case import construct, assumptions
from financing.evidence import check_evidence
from financing.engine import run
from financing.config import demo_config
from financing.policy import BLOCKED

DATA = Path(__file__).resolve().parents[1] / "data"


class PublicCaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "data"
        shutil.copytree(DATA, self.root)
        self.case = json.loads(
            (self.root / "historical.json").read_text(encoding="utf-8")
        )

    def report(self):
        return build_report(self.case, self.root, public_information=True, full=False)

    def test_connected_conditional_case_does_not_clear_strict_gate(self):
        r = self.report()
        p = r["public_information"]
        self.assertEqual(r["recommendation_status"], BLOCKED)
        self.assertEqual(r["historical_results"], [])
        self.assertIsNone(p["preferred_structure"])
        self.assertEqual(len(p["gap_assessment"]), 23)
        self.assertEqual(len(p["base"]), 3)
        self.assertEqual(p["config"]["revolver"]["commitment"], 0)
        self.assertNotEqual(
            p["projected_bridge"][0]["projected_cash"],
            p["projected_bridge"][0]["reported_cash"],
        )
        for b in p["base"]:
            self.assertAlmostEqual(b["opening"]["sources_uses_difference"], 0)
            for y in b["years"]:
                self.assertAlmostEqual(y["cash_check"], 0)
                self.assertAlmostEqual(y["debt_check"], 0)
                self.assertEqual(y["revolver_draw"], 0)

    def test_missing_contract_blocks_financing_but_not_bridge_or_history(self):
        (self.root / "sources/fl_indent.json").unlink()
        r = self.report()
        p = r["public_information"]
        self.assertIn("projected_bridge", p)
        self.assertEqual(p["base"], [])
        self.assertEqual(p["output_policy"][1]["status"], "Blocked")
        self.assertTrue(
            any(
                c["status"] == "Supported"
                for c in r["supported_historical_calculations"]
            )
        )
        from financing.exports import export_all
        from financing.workbook_plan import make_plan

        export_all(r, self.case, Path(self.tmp.name) / "blocked-export")
        self.assertTrue(make_plan(r, self.case))

    def test_missing_cash_source_blocks_bridge_and_funding(self):
        (self.root / "sources/review_dks.json").unlink()
        p = self.report()["public_information"]
        self.assertNotIn("projected_bridge", p)
        self.assertEqual(p["base"], [])

    def test_verified_public_envelopes_and_contractual_payoff(self):
        p = self.report()["public_information"]
        u = p["uses_detail"]
        self.assertAlmostEqual(u["fl_note_premium"], 4.0)
        self.assertAlmostEqual(u["fl_note_accrued_interest"], 400 * 0.04 / 12)
        self.assertAlmostEqual(u["lc_cash_collateral_reserve"], 7.35)
        self.assertGreater(u["known_award_cash_upper"], u["known_award_cash_lower"])
        for b in p["base"]:
            self.assertEqual(b["opening"]["required_debt_repayment"], 400)
            self.assertFalse(
                any(x["instrument"] == "FL notes redeemed" for x in b["debt_schedule"])
            )
            for x in b["debt_schedule"]:
                if x["instrument"] == "DKS notes 2032":
                    self.assertEqual(x["optional_paid"], 0)

    def test_feasible_counterfactual_still_cannot_unlock_preference(self):
        e = check_evidence(self.case, self.root)
        v = {
            r["key"]: r["value"]
            for r in e["rows"]
            if r["classification"] == "verified fact"
        }
        a = assumptions()
        a.update(gross_annual_capex=[900.0, 240.0], dividend_factor=0.0)
        c, _, _ = construct(v, a)
        self.assertTrue(run(c, "Mixed consideration")["feasible"])
        r = self.report()
        self.assertEqual(r["recommendation_status"], BLOCKED)
        self.assertIsNone(r["public_information"]["preferred_structure"])

    def test_synthetic_default_cash_access_and_debt_ledger_unchanged(self):
        c = demo_config()
        a = run(c)
        c["policy"]["operating_cash_access_fraction"] = 1.0
        self.assertEqual(a, run(c))

    def test_postcutoff_public_source_cannot_run_projections(self):
        next(s for s in self.case["sources"] if s["id"] == "public_fl")[
            "published"
        ] = "2025-05-16"
        self.assertEqual(self.report()["public_information"]["base"], [])

    def test_independently_checked_projected_bridge(self):
        from decimal import Decimal as D

        # Independent decimal benchmark, sourced FY2024 cash/flows and explicit forecasts.
        cash = (
            D("1689.940")
            + D("680.307")
            - D("1200") * D("565.569") / D("802.565")
            - D("1.2125") * D("80.046011") * 3
            - D("5")
        )
        # New bridge replaces historical trade-WC movement with explicit projected balances.
        cash += D("497.485") - (
            D("3349.83") * D(".18") + D("214.25") * D(".05") - D("1497.743") * D(".15")
        )
        p = self.report()["public_information"]
        self.assertAlmostEqual(p["projected_bridge"][0]["projected_cash"], float(cash))
        self.assertAlmostEqual(p["projected_bridge"][1]["projected_cash"], 96.10)
        self.assertAlmostEqual(p["base"][0]["opening"]["cash_purchase"], 2293.453968)

    def test_public_output_policy_and_database_propagation(self):
        from financing.exports import export_all
        from financing.workbook_plan import make_plan
        import sqlite3

        db = Path(self.tmp.name) / "model.sqlite"
        r = build_report(
            self.case, self.root, public_information=True, full=False, database_path=db
        )
        out = Path(self.tmp.name) / "out"
        export_all(r, self.case, out)
        for name in ("dashboard.html", "memo.md"):
            text = (out / name).read_text(encoding="utf-8")
            self.assertIn(BLOCKED, text)
            self.assertIn("Projected closing bridge", text)
            self.assertIn("Confirmed borrowing availability", text)
        self.assertEqual(
            json.loads((out / "public-information.json").read_text(encoding="utf-8")),
            r["public_information"],
        )
        plan = make_plan(r, self.case)
        bridge = next(s for s in plan if s["name"] == "Projected closing bridge")
        self.assertEqual(len(bridge["formulas"]), 4)
        with sqlite3.connect(db) as conn:
            saved = json.loads(
                conn.execute(
                    "SELECT payload FROM public_information_reviews"
                ).fetchone()[0]
            )
        conn.close()
        self.assertEqual(saved, r["public_information"])


if __name__ == "__main__":
    unittest.main()
