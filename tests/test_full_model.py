import json
from pathlib import Path
import tempfile
import unittest
from copy import deepcopy
from financing.config import demo_config
from financing.engine import run, transaction, STRUCTURES
from financing.scenarios import Shock, scenarios
from financing.solver import capacity, reverse_stress, feasible_ranges
from financing.operating import forecast
from financing import database as dbm
from financing.ingestion import companyfacts_candidates, standalone_quarter, fetch
from financing.evidence import check_evidence
from test_evidence import reviewed_fixture


def benchmark():
    c = demo_config()
    for i, comp in enumerate(c["companies"]):
        comp.update(
            revenue=500.0,
            gross_margin=0.4,
            variable_opex=0.1,
            fixed_opex=40.0,
            rent=10.0,
            cash=300.0 if i == 0 else 50.0,
            growth=[0.0] * 5,
            fixed_growth=0.0,
            da_ratio=0.0,
            capex_ratio=0.0,
            dio=0.0,
            dso=0.0,
            dpo=0.0,
            cash_bridge=dict(operating=0.0, capex=0.0, dividends=0.0, buybacks=0.0),
        )
        d = deepcopy(comp["debts"][0])
        d.update(
            principal=100.0,
            carrying_value=100.0,
            rate=0.04 if i == 0 else 0.05,
            maturity=5.0 if i == 0 else 3.0,
            amortisation=0.1 if i == 0 else 0.0,
            optional=i == 0,
            repay_at_close=False,
        )
        comp["debts"] = [d]
    c["transaction"].update(
        target_shares=50.0,
        award_shares=0.0,
        cash_price=10.0,
        transaction_fees=10.0,
        financing_fee_rate=0.0,
    )
    c["new_debt"].update(
        kind="fixed", fixed_benchmark=0.04, spread=0.02, amortisation=0.1
    )
    c["policy"].update(cash_floor=100.0, tax_rate=0.0, dividends=[0.0] * 5)
    c["synergies"].update(run_rate=0.0, integration=[0.0] * 5)
    return c


class FullModelTests(unittest.TestCase):
    def test_independent_full_model_benchmark(self):
        expected = json.loads(
            Path(__file__).with_name("full_benchmark.json").read_text()
        )
        r = run(benchmark())
        for key in (
            "cash_uses",
            "cash_contribution",
            "total_new_borrowing",
            "opening_debt",
            "opening_cash",
        ):
            self.assertAlmostEqual(r["opening"][key], expected[key], places=8)
        for key in (
            "ebitda",
            "interest",
            "mandatory_paid",
            "optional_paid",
            "closing_debt",
            "closing_cash",
        ):
            self.assertAlmostEqual(r["years"][0][key], expected[key], places=8)

    def test_sources_uses_and_instrument_cash_rollforwards_across_stress(self):
        c = demo_config()
        for shock in scenarios():
            for structure in STRUCTURES:
                r = run(c, structure, shock)
                self.assertAlmostEqual(r["opening"]["sources_uses_difference"], 0)
                for p in r["periods"]:
                    self.assertAlmostEqual(p["cash_check"], 0, places=6)
                    self.assertAlmostEqual(p["debt_check"], 0, places=6)
                for d in r["debt_schedule"]:
                    self.assertGreaterEqual(d["closing_principal"], -1e-7)
                    self.assertAlmostEqual(
                        d["closing_principal"],
                        d["opening_principal"]
                        + d["draw"]
                        - d["mandatory_paid"]
                        - d["optional_paid"]
                        - d["refinanced"],
                        places=6,
                    )

    def test_cash_not_spent_twice_target_excluded_and_coc_repaid(self):
        c = demo_config()
        r = transaction(c, "Cash-first")
        self.assertEqual(r["required_debt_repayment"], 100.0)
        self.assertEqual(r["unavailable_target_cash"], 340.0)
        self.assertEqual(
            r["opening_cash"] + r["cash_contribution"], r["bridges"][0]["closing_cash"]
        )
        self.assertNotIn(
            "Beacon CoC loan", [d["id"] for d in r["retained_instruments"]]
        )

    def test_fixed_coupons_unchanged_and_floaters_reset(self):
        c = demo_config()
        a = run(c)
        b = run(c, shock=Shock(benchmark=0.02, spread=0.02))
        self.assertEqual(a["debt_schedule"][0]["rate"], b["debt_schedule"][0]["rate"])
        ta = next(
            d for d in a["debt_schedule"] if d["instrument"] == "Acquisition term"
        )
        tb = next(
            d for d in b["debt_schedule"] if d["instrument"] == "Acquisition term"
        )
        self.assertAlmostEqual(tb["rate"] - ta["rate"], 0.04)

    def test_facility_limit_and_overdue_gap(self):
        c = demo_config()
        c["revolver"].update(
            commitment=50.0, borrowing_base=40.0, letters_of_credit=10.0
        )
        r = run(c, shock=Shock(revenue=-0.5))
        self.assertTrue(
            any(
                p["maturity_gap"] > 0 or p["liquidity_shortfall"] > 0
                for p in r["periods"]
            )
        )
        self.assertTrue(
            all(p["revolver_outstanding"] <= 30.0 + 1e-7 for p in r["periods"])
        )

    def test_explicit_refinancing_creates_new_instruments_and_respects_limit(self):
        c = demo_config()
        c["policy"].update(refinance=True, refinance_limit=150.0)
        r = run(c)
        self.assertGreater(r["total_refinancing"], 0)
        self.assertLessEqual(r["total_refinancing"], 150.0 + 1e-6)
        self.assertTrue(
            any(d["instrument"].startswith("Refinance ") for d in r["debt_schedule"])
        )
        self.assertGreater(sum(p["refinancing_fees"] for p in r["periods"]), 0)
        self.assertEqual(run(demo_config())["total_refinancing"], 0)

    def test_operating_shock_is_level_and_no_double_ebitda_haircut(self):
        c = demo_config()
        a = forecast(c, Shock())
        b = forecast(c, Shock(revenue=-0.1))
        for x, y in zip(a, b):
            self.assertAlmostEqual(y["revenue"] / x["revenue"], 0.9)
            self.assertAlmostEqual(
                y["ebitda"],
                y["revenue"]
                - y["cogs"]
                - y["variable_opex"]
                - y["fixed_opex"]
                - y["rent"],
            )

    def test_stock_dilution_and_cash_funding_separate(self):
        r = transaction(demo_config(), "Mixed consideration")
        self.assertAlmostEqual(r["stock_issued"], 5.1)
        self.assertAlmostEqual(r["ownership_dilution"], 5.1 / 85.1)
        self.assertGreater(r["noncash_consideration"], 0)
        self.assertAlmostEqual(
            r["cash_uses"],
            r["cash_purchase"]
            + r["required_debt_repayment"]
            + r["transaction_fees"]
            + r["financing_fees"],
        )

    def test_quarterly_operating_totals_and_cash_reconcile(self):
        c = demo_config()
        annual = run(c)
        quarterly = run(c, frequency=4)
        self.assertEqual(len(quarterly["periods"]), 20)
        for a, b in zip(annual["years"], quarterly["years"]):
            for key in (
                "revenue",
                "ebitda",
                "delta_nwc",
                "capex",
                "synergy",
                "integration",
            ):
                self.assertAlmostEqual(a[key], b[key], places=6)
            q = [r for r in quarterly["periods"] if r["year"] == a["year"]]
            for key in ("interest", "tax", "repayment", "revolver_draw"):
                self.assertAlmostEqual(b[key], sum(x[key] for x in q), places=6)
            self.assertEqual(b["closing_cash"], q[-1]["closing_cash"])
        self.assertTrue(all(abs(r["cash_check"]) < 1e-6 for r in quarterly["periods"]))

    def test_lease_cash_adjustment_not_full_double_deduction(self):
        c = benchmark()
        a = run(c)
        c["companies"][0]["rent_cash_factor"] = 1.2
        b = run(c)
        self.assertAlmostEqual(
            a["years"][0]["operating_cash_flow"] - b["years"][0]["operating_cash_flow"],
            2.0,
        )
        self.assertAlmostEqual(b["years"][0]["ebitda"], a["years"][0]["ebitda"])

    def test_capacity_holds_uses_cash_fixed_and_substitutes_equity(self):
        c = demo_config()
        full = run(c)
        less = run(c, acquisition_borrowing=100.0)
        for key in (
            "cash_uses",
            "cash_contribution",
            "opening_cash",
            "borrowing_for_refinancing_and_fees",
        ):
            self.assertAlmostEqual(full["opening"][key], less["opening"][key])
        self.assertGreater(less["opening"]["analytical_equity"], 0)
        with self.assertRaises(ValueError):
            run(c, acquisition_borrowing=999999.0)
        solved = capacity(c, "Cash-first")
        if solved["maximum_acquisition_borrowing"] is not None:
            self.assertTrue(
                run(c, acquisition_borrowing=solved["maximum_acquisition_borrowing"])[
                    "feasible"
                ]
            )
        self.assertEqual(
            feasible_ranges([(0, True), (10, False), (20, True)]), [[0, 0], [20, 20]]
        )

    def test_solver_infeasible_and_funding_limited_cases(self):
        c = benchmark()
        c["policy"]["min_coverage"] = 100000.0
        self.assertIsNone(capacity(c, "Cash-first")["maximum_acquisition_borrowing"])
        c = benchmark()
        c["transaction"]["cash_price"] = 1.0
        self.assertTrue(capacity(c, "Mixed consideration")["funding_limited"])

    def test_reverse_already_failing_and_no_breach(self):
        c = demo_config()
        c["policy"]["min_coverage"] = 100000.0
        self.assertEqual(
            reverse_stress(c, "Cash-first")["status"],
            "Already failing at starting point",
        )
        c = benchmark()
        c["transaction"]["cash_price"] = 1.0
        self.assertEqual(
            reverse_stress(c, "Mixed consideration", max_decline=0)["status"],
            "No breach within the tested range",
        )

    def test_old_trend_data_remains_missing_without_blocking_explicit_growth(self):
        with tempfile.TemporaryDirectory() as t:
            case = reviewed_fixture(Path(t))
            source = next(
                s for s in case["sources"] if "FY2022.revenue" in s["claims"][0]["key"]
            )
            (Path(t) / source["path"]).unlink()
            self.assertFalse(check_evidence(case, t)["blocked"])
            self.assertTrue(
                check_evidence(case, t, {"historical_trend_calibration": True})[
                    "blocked"
                ]
            )

    def test_sql_related_storage_roundtrip_and_queries(self):
        with tempfile.TemporaryDirectory() as t:
            db = dbm.connect(Path(t) / "model.sqlite")
            c = demo_config()
            cid = dbm.store_config(db, c)
            self.assertEqual(dbm.load_config(db, cid), c)
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM companies").fetchone()[0], 2
            )
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM debt_instruments").fetchone()[0], 4
            )
            self.assertGreater(
                db.execute("SELECT COUNT(*) FROM financial_observations").fetchone()[0],
                0,
            )
            db.close()

    def test_companyfacts_cutoff_excludes_later_restatements(self):
        entries = [
            dict(
                val=100,
                accn="a",
                filed="2025-03-01",
                start="2024-01-01",
                end="2024-12-31",
                form="10-K",
            ),
            dict(
                val=999,
                accn="b",
                filed="2026-03-01",
                start="2024-01-01",
                end="2024-12-31",
                form="10-K",
            ),
        ]
        rows = companyfacts_candidates(
            {"facts": {"us-gaap": {"Revenues": {"units": {"USD": entries}}}}},
            ["Revenues"],
        )
        self.assertEqual([r["value"] for r in rows], [100])
        self.assertEqual(rows[0]["period_basis"], "annual")

    def test_quarterly_cumulative_subtraction_validates_periods(self):
        first = dict(
            period_start="2024-01-01", period_end="2024-03-31", units="USD", value=20
        )
        second = {**first, "period_end": "2024-06-30", "value": 50}
        self.assertEqual(standalone_quarter(second, first), 30)
        with self.assertRaises(ValueError):
            standalone_quarter(first, second)

    def test_sec_access_requires_truthful_contact(self):
        with self.assertRaises(ValueError):
            fetch(
                "https://data.sec.gov/api/xbrl/companyfacts/CIK0001089063.json",
                "unused",
                "no contact",
            )


if __name__ == "__main__":
    unittest.main()
