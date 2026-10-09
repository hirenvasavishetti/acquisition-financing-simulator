"""Verify installed-package outputs and the live HTTP calculation boundary."""

import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from financing.policy import BLOCKED


def main():
    output = Path(sys.argv[1])
    case = Path(sys.argv[2]).resolve()
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["recommendation_status"] == BLOCKED
    assert report["historical_results"] == [] and report["preferred_structure"] is None
    assert len(report["model"]["comparisons"]) == 48
    assert len(report["model"]["base"]) == 3 and len(report["model"]["quarterly"]) == 3
    assert len(report["model"]["sensitivities"]) == 8
    import openpyxl
    from pypdf import PdfReader

    wb = openpyxl.load_workbook(output / "evidence-review.xlsx", data_only=True)
    expected_sheets = (
        25
        if any(
            x["status"] == "Supported"
            for x in report.get("supported_historical_calculations", [])
        )
        else 20
    )
    assert (
        len(wb.sheetnames) == expected_sheets and wb["Summary"]["B3"].value == BLOCKED
    )
    for sheet in wb:
        for row in sheet:
            assert not any(c.data_type == "e" for c in row), sheet.title
    assert abs(wb["Operations"]["I5"].value - 1247.4) < 1e-6
    assert (
        abs(
            wb["Liquidity"]["Q5"].value
            - report["model"]["base"][0]["years"][0]["closing_cash"]
        )
        < 1e-6
    )
    wb.close()
    assert len(PdfReader(output / "financing-memo.pdf").pages) == 2
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    proc = subprocess.Popen(
        [sys.executable, "-m", "financing", str(case), "--demo", "--serve", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        for _ in range(50):
            try:
                with urlopen(
                    url + "/api/report?cash_floor=500", timeout=30
                ) as response:
                    data = json.load(response)
                break
            except URLError:
                if proc.poll() is not None:
                    raise RuntimeError("Dashboard process exited")
                time.sleep(0.1)
        else:
            raise RuntimeError("Dashboard failed to start")
        assert data["model"]["config"]["policy"]["cash_floor"] == 500
        assert data["model"]["base"][0]["feasible"]
        assert (
            data["recommendation_status"] == BLOCKED
            and data["preferred_structure"] is None
        )
        try:
            urlopen(url + "/api/report?cash_floor=nan", timeout=30)
        except HTTPError as exc:
            assert (
                exc.code == 422 and json.load(exc)["recommendation_status"] == BLOCKED
            )
        else:
            raise AssertionError("Invalid input did not fail closed")
    finally:
        proc.terminate()
        proc.wait(timeout=10)
    result = subprocess.run(
        [sys.executable, "-m", "financing", str(case)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert (
        result.returncode == 2 and json.loads(result.stdout)["historical_results"] == []
    )
    print(
        f"PASS: installed pipeline, 48 comparisons, {expected_sheets} sheets, two-page PDF, live recalculation, invalid-input block, historical exit 2"
    )


if __name__ == "__main__":
    main()
