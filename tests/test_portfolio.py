"""Independent arithmetic and economically material integration regressions."""

from copy import deepcopy
from decimal import Decimal as D
import json
from pathlib import Path
import unittest

from financing.config import demo_config, validate
from financing.engine import run
from financing.evidence import check_evidence
from financing.funding import replace_acquisition_debt
from financing.operating import trailing, forecast
from financing.public_case import construct, assumptions
from financing.public_inputs import public_assumptions, form_overrides
from financing.report import build_report
from financing.scenarios import Shock
from financing.solver import capacity, reverse_stress

ROOT = Path(__file__).resolve().parents[1]


class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads(
            (ROOT / "data/historical.json").read_text(encoding="utf-8")
        )
        e = check_evidence(cls.case, ROOT / "data")
        cls.facts = {
            r["key"]: r["value"]
            for r in e["rows"]
            if r["classification"] == "verified fact"
        }

    def test_annual_capacity_does_not_establish_quarterly_liquidity(self):
        c = demo_config()
        annual = capacity(c, "Cash-first", frequency=1)
        self.assertEqual(annual["maximum_acquisition_borrowing"], 948.0)
        quarterly_at_annual = run(
            c, "Cash-first", acquisition_borrowing=948.0, frequency=4
        )
        self.assertAlmostEqual(quarterly_at_annual["min_cash"], 725.7318217456881)
        q = capacity(c, "Cash-first", frequency=4)
        self.assertEqual(q["frequency"], 4)
        self.assertEqual(q["maximum_acquisition_borrowing"], 928.0)
        self.assertTrue(
            run(c, "Cash-first", acquisition_borrowing=928.0, frequency=4)["feasible"]
        )
        self.assertFalse(
            run(c, "Cash-first", acquisition_borrowing=929.0, frequency=4)["feasible"]
        )

    def test_reverse_stress_uses_selected_periods(self):
        c = demo_config()
        s = reverse_stress(c, "Mixed consideration", frequency=4, step=0.01)
        self.assertEqual(s["frequency"], 4)
        if s["revenue_decline"] is not None:
            self.assertFalse(
                run(
                    c,
                    "Mixed consideration",
                    Shock(revenue=-s["revenue_decline"]),
                    frequency=4,
                )["feasible"]
            )

    def test_independent_debt_dependent_fee_example(self):
        # Nonfinancing uses 1,000, cash 200, acquisition principal budget 600.
        # Replace 300 acquisition principal with equity. Other uses funded by debt=200.
        old_fee = 800 / 0.98 * 0.02
        opening = dict(
            acquisition_borrowing=600.0,
            cash_uses=1000.0 + old_fee,
            financing_fees=old_fee,
            cash_contribution=200.0,
            retained_debt=100.0,
            borrowing_for_refinancing_and_fees=800 / 0.98 - 600.0,
            itemised_uses=dict(
                cash_consideration=800.0,
                transaction_expenses=200.0,
                financing_fees=old_fee,
            ),
        )
        fixed = deepcopy(opening)
        replace_acquisition_debt(opening, 300.0, 0.02, "issued_debt")
        expected_debt = (D("300") + D("200")) / (1 - D(".02"))
        self.assertAlmostEqual(opening["total_new_borrowing"], float(expected_debt))
        self.assertAlmostEqual(
            opening["financing_fees"], float(expected_debt * D(".02"))
        )
        self.assertEqual(opening["analytical_equity"], 300.0)
        self.assertAlmostEqual(opening["sources_uses_difference"], 0.0)
        replace_acquisition_debt(fixed, 300.0, 0.02, "fixed_budget")
        self.assertAlmostEqual(fixed["financing_fees"], old_fee)
        self.assertGreater(fixed["total_new_borrowing"], opening["total_new_borrowing"])

    def test_itemised_uses_reconcile_all_structures(self):
        c, _, _ = construct(self.facts, assumptions())
        for s in ("Cash-first", "Liquidity-first", "Mixed consideration"):
            o = run(c, s)["opening"]
            self.assertEqual(o["transaction_fees"], 75.0)
            self.assertAlmostEqual(sum(o["itemised_uses"].values()), o["cash_uses"])
            self.assertAlmostEqual(o["itemised_uses"]["redemption_premium"], 4.0)
            self.assertAlmostEqual(o["sources_uses_difference"], 0.0)

    def test_closing_working_capital_continuity(self):
        c, b, _ = construct(self.facts, assumptions())
        r = run(c)
        opening = sum(
            x["closing_working_capital"]["inventory"]
            + x["closing_working_capital"]["receivables"]
            - x["closing_working_capital"]["payables"]
            for x in b
        )
        self.assertAlmostEqual(
            r["years"][0]["delta_nwc"], r["years"][0]["nwc"] - opening
        )
        self.assertAlmostEqual(
            sum(y["delta_nwc"] for y in r["years"]), r["years"][-1]["nwc"] - opening
        )
        for x in b:
            self.assertAlmostEqual(
                x["projected_cfo"],
                x["pre_working_capital_cfo"] - x["projected_nwc_change"],
            )
        # Independently worked DKS closing bridge, not generated by production code.
        nwc = (
            D("3349.83") * D(".18") + D("214.25") * D(".05") - D("1497.743") * D(".15")
        )
        cfo = D("680.307") - (-D("877.115") - D("25.055") + D("404.685")) - nwc
        closing = (
            D("1689.940")
            + cfo
            - D("1200") * D("565.569") / D("802.565")
            - D("1.2125") * D("80.046011") * 3
            - D("5")
        )
        self.assertAlmostEqual(b[0]["projected_cash"], float(closing))

    def test_cost_behaviour_preserves_baseline_but_changes_downside(self):
        low = assumptions({"variable_cost_share": [0.65, 0.65]})
        high = assumptions({"variable_cost_share": [0.95, 0.95]})
        lc, _, _ = construct(self.facts, low)
        hc, _, _ = construct(self.facts, high)
        for a, b in zip(lc["companies"], hc["companies"]):
            self.assertAlmostEqual(trailing(a)["ebitda"], trailing(b)["ebitda"])
        lr = forecast(lc, Shock(revenue=-0.1))
        hr = forecast(hc, Shock(revenue=-0.1))
        self.assertLess(sum(x["ebitda"] for x in lr), sum(x["ebitda"] for x in hr))
        self.assertEqual([x["inventory"] for x in lr], [x["inventory"] for x in hr])

    def test_public_ui_changes_reach_engine_without_changing_facts(self):
        changes = form_overrides(
            {
                "cash_floor": ["1000"],
                "growth_fl": ["-0.05,0,0.02,0.02,0.02"],
                "spread": ["0.04"],
            }
        )
        r = build_report(
            self.case,
            ROOT / "data",
            full=False,
            public_information=True,
            public_overrides=changes,
        )
        self.assertEqual(
            r["public_information"]["config"]["policy"]["cash_floor"], 1000.0
        )
        self.assertEqual(r["public_information"]["config"]["new_debt"]["spread"], 0.04)
        self.assertEqual(r["evidence"], check_evidence(self.case, ROOT / "data"))
        with self.assertRaises(ValueError):
            public_assumptions({"transaction.cash_price": 1})
        with self.assertRaises(ValueError):
            public_assumptions({"growth": [[0.1], [0.1]]})

    def test_maturity_settles_first_period_end_after_date(self):
        c = demo_config()
        c["companies"][0]["debts"][0]["maturity_date"] = "2026-01-15"
        r = run(c, frequency=4)
        line = next(
            x
            for x in r["debt_schedule"]
            if x["instrument"] == "Atlas notes" and x["period"] == 1
        )
        self.assertEqual(r["periods"][0]["period_end"], "2026-02-01")
        self.assertEqual(line["mandatory_due"], 900.0)
        self.assertAlmostEqual(line["interest"], 900 * 0.038 / 4)

    def test_validation_rejects_invalid_units_and_seasonality(self):
        for field, value in [
            ("currency", "USD"),
            ("frequency", 12),
            ("closing_date", "not-a-date"),
        ]:
            c = demo_config()
            c[field] = value
            with self.assertRaises(ValueError):
                validate(c)
        c = demo_config()
        c["companies"][0]["inventory_seasonality"] = [1.0]
        with self.assertRaises(ValueError):
            validate(c)
