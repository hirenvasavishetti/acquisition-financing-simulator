"""Formatting must preserve formula caches, types and evidence restrictions."""

import tempfile
import unittest
from pathlib import Path

from financing.portable_excel import write_xlsx


class WorkbookPresentationTest(unittest.TestCase):
    def test_styles_preserve_values_and_formula_cache(self):
        import openpyxl

        plan = [
            dict(
                name="Schedule",
                header_row=4,
                widths=[35, 30, 30],
                rows=[
                    ["Schedule", None, None],
                    ["Python snapshots", None, None],
                    ["Period", "Rate", "Evidence"],
                    [1, 0.05, "missing evidence"],
                    [2, 0, None],
                ],
                formulas=[dict(cell="B6", formula="=B5*2", value=0.1)],
                number_formats=[dict(column=1, format="0.00%")],
            ),
            dict(
                name="Summary",
                header_row=0,
                widths=[44, 100],
                rows=[
                    ["Acquisition financing simulator", ""],
                    [
                        "Recommendation status",
                        "Blocked — insufficient verified evidence.",
                    ],
                ],
                formulas=[],
            ),
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.xlsx"
            write_xlsx(plan, path)
            book = openpyxl.load_workbook(path)
            cached = openpyxl.load_workbook(path, data_only=True)
            sheet = book["Schedule"]
            self.assertEqual(sheet["B6"].value, "=B5*2")
            self.assertEqual(cached["Schedule"]["B6"].value, 0.1)
            self.assertEqual(sheet["B6"].number_format, "0.00%")
            self.assertIsNone(sheet["C6"].value)
            self.assertEqual(sheet["A6"].value, 2)
            self.assertEqual(sheet.freeze_panes, "B5")
            self.assertIsNone(sheet.auto_filter.ref)
            self.assertEqual(sheet["A4"].fill.fgColor.rgb, "FF3C5658")
            self.assertTrue(sheet["A4"].font.italic)
            self.assertEqual(
                book["Summary"]["B3"].value, "Blocked — insufficient verified evidence."
            )
            self.assertTrue(book["Summary"].conditional_formatting)
