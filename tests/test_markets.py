"""Independent closed-form benchmarks, risk identities and HTTP validation."""

import unittest
from financing.markets import bond_risk
from financing.web import Application
from test_web import request


class BondRiskTests(unittest.TestCase):
    def test_par_and_zero_coupon_closed_form(self):
        self.assertAlmostEqual(bond_risk()["price"], 100, places=10)
        r = bond_risk(coupon=0, years=10, benchmark=0.04, spread=0, frequency=1)
        self.assertAlmostEqual(r["price"], 100 / 1.04**10, places=10)
        self.assertAlmostEqual(r["modified_duration"], 10 / 1.04, places=10)
        self.assertAlmostEqual(r["convexity"], 110 / 1.04**2, places=10)

    def test_dv01_matches_central_difference_and_hedge_rounding(self):
        r = bond_risk()
        down, up = bond_risk(benchmark=0.039999), bond_risk(benchmark=0.040001)
        fd = (down["market_value"] - up["market_value"]) / 2e-6 * 0.0001
        self.assertAlmostEqual(r["dv01"], fd, places=4)
        self.assertLessEqual(abs(r["residual_dv01"]), 40)
        self.assertGreater(r["scenarios"][0]["pnl"], 0)
        self.assertLess(r["scenarios"][2]["pnl"], 0)
        self.assertAlmostEqual(r["scenarios"][3]["pnl"], r["scenarios"][4]["pnl"])

    def test_endpoint_is_bounded_and_independent_of_company_model(self):
        app = Application(
            {}, runner=lambda *a: self.fail("Bond lab must not run company model")
        )
        self.assertEqual(request(app, path="/api/bond-risk")["status"], 200)
        for q in (
            "years=30.5",
            "years=100000",
            "notional=nan",
            "frequency=3",
            "coupon=-1",
            "spread=inf",
            "case=source.json",
            "coupon=",
            "coupon=0&coupon=1",
        ):
            self.assertEqual(request(app, q, path="/api/bond-risk")["status"], 422, q)
