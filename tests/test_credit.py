import unittest
from copy import deepcopy
from financing.config import demo_config
from financing.credit import stress_grid
from financing.engine import run, STRUCTURES


class JointStressTests(unittest.TestCase):
    def test_base_cells_reconcile_and_inputs_are_not_mutated(self):
        config = demo_config()
        before = deepcopy(config)
        grid = stress_grid(config)
        self.assertEqual(config, before)
        self.assertEqual(len(grid["cells"]), 27)
        for structure in STRUCTURES:
            base = run(config, structure)
            cell = next(
                c
                for c in grid["cells"]
                if c["structure"] == structure and c["rate_bp"] == c["margin_bp"] == 0
            )
            self.assertEqual(cell["feasible"], base["feasible"])
            self.assertEqual(
                cell["cash_headroom"], base["min_cash"] - config["policy"]["cash_floor"]
            )
            self.assertEqual(cell["total_interest"], base["total_interest"])

    def test_quarterly_grid_retains_timing_and_exposes_joint_downside(self):
        config = demo_config()
        config["frequency"] = 4
        cells = stress_grid(config)["cells"]
        base = next(
            c
            for c in cells
            if c["structure"] == "Cash-first" and c["rate_bp"] == c["margin_bp"] == 0
        )
        self.assertEqual(
            base["min_cash"], run(config, "Cash-first", frequency=4)["min_cash"]
        )
        downside = next(
            c
            for c in cells
            if c["structure"] == "Cash-first"
            and c["rate_bp"] == 200
            and c["margin_bp"] == -200
        )
        self.assertLess(downside["cash_headroom"], base["cash_headroom"])
