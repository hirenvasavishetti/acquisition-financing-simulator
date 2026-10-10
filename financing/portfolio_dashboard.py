"""Finance-facing views over the canonical report; no financial calculations here."""

import json
from pathlib import Path


def page(report):

    payload = (
        json.dumps(report, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )

    assets = Path(__file__).parent
    scripts = "\n".join(
        (assets / name).read_text(encoding="utf-8-sig")
        for name in (
            "dashboard_core.js",
            "risk_views.js",
            "dashboard_shell.js",
            "dashboard_bootstrap.js",
        )
    )
    return (
        TEMPLATE.replace("__SCRIPT__", scripts)
        .replace(
            "__STYLE__", (assets / "dashboard.css").read_text(encoding="utf-8-sig")
        )
        .replace("__REPORT__", payload)
    )


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">

<title>Acquisition finance | Research simulator</title><style>

__STYLE__
</style></head><body><header><div class="eyebrow">Corporate finance research · USD millions</div><h1>Acquisition financing &amp; debt capacity</h1><p>How do cash, borrowing and share consideration change liquidity and financing risk?</p></header><main>

<div class="mode"><div><strong id="caseTitle"></strong><div class="minor" id="scope"></div></div><label>Analysis mode<select id="mode"><option value="synthetic">Synthetic demonstration</option><option value="public">Public-information case</option><option value="strict">Strict historical assessment</option></select></label></div>

<div class="badges"><span id="operational" class="badge"></span><span id="timing" class="badge"></span><span id="historicalStatus" class="badge warning"></span></div>

<p id="runKind" class="minor"></p><p id="stale" class="statusline hidden" role="status">Assumptions changed. Displayed results are stale. Recalculate on the live server or restore the saved inputs.</p>

<nav aria-label="Analysis sections"><button data-view="overview" class="active">Overview</button><button data-view="assumptions">Assumptions</button><button data-view="funding">Funding &amp; debt</button><button data-view="liquidity">Liquidity &amp; stress</button><button data-view="sources">Sources &amp; methodology</button></nav>

<section id="assumptions" class="hidden"><div class="panel"><h2>Future assumptions</h2><p>Editable analyst choices are separate from verified facts. Rates and growth are decimal fractions: 0.045 = 4.5%. Submit changes to recalculate the actual Python model.</p><form id="controls"><div class="inputs" id="inputs"></div><button type="submit" class="primary" id="recalculate">Recalculate live model</button> <button type="button" id="restore">Restore current results' inputs</button></form><p id="error" class="bad" role="alert"></p></div></section>

<div id="results"><section id="overview"><div class="cards" id="comparison"></div><div class="panel"><h2>Principal findings</h2><p id="finding"></p><p id="drivers"></p><p class="minor">A passing screen is conditional model feasibility. It does not establish lender appetite, legal compliance or executable financing. Projections continue mechanically after a breach; later balances describe an unfunded path.</p></div><div class="panel"><h3>Financing trade-offs</h3><svg id="tradeoffChart" role="img" aria-label="New borrowing across financing structures"></svg><p class="minor">New borrowing (USD m); compare interest and dilution in the table.</p><div id="tradeoffs" class="scroll"></div></div></section>

<section id="funding" class="hidden"><div class="panel"><label>Structure<select id="structure"></select></label><h2>Itemised sources and uses</h2><div id="uses" class="scroll"></div><h2>Projected closing bridge</h2><div id="bridge" class="scroll"></div></div><div class="panel"><h2>Debt instruments</h2><div id="debt" class="scroll"></div></div><div class="panel"><h2>Operating forecast and cost reconciliation</h2><div id="costs" class="scroll"></div><h3>Initial annual investment budget</h3><p class="minor">Maintenance amounts are analyst allocations, not disclosed minimums. Residual spending is labelled growth investment; linked scenarios test 1–2 percentage-point growth reductions.</p><div id="investment" class="scroll"></div><div id="operations" class="scroll"></div></div></section>

<section id="liquidity" class="hidden"><div class="panel"><label>Saved scenario<select id="scenario"></select></label><p class="minor">Scenario selection reads already calculated results; it does not edit assumptions.</p></div><div class="grid"><div class="panel"><h3>Cash versus reserve</h3><svg id="cashChart" role="img" aria-label="Cash compared with reserve"></svg></div><div class="panel"><h3>Debt repayment</h3><svg id="debtChart" role="img" aria-label="Debt outstanding by period"></svg></div><div class="panel"><h3>Interest coverage</h3><svg id="coverageChart" role="img" aria-label="Interest coverage and analytical threshold"></svg></div><div class="panel"><h3>Selected scenario</h3><p id="selectedFinding"></p></div></div><div class="panel"><h2>Period liquidity</h2><div id="annual" class="scroll"></div></div><div class="panel"><h2>Capacity and reverse stress</h2><p>Capacity replaces acquisition borrowing with separate analytical equity while holding nonfinancing uses and cash contribution fixed. Narrow feasible regions can be missed by the grid.</p><div id="capacity" class="scroll"></div><div id="reverse" class="scroll"></div><p id="frequencyNote" class="minor"></p></div><div class="panel"><h2>Scenario drivers</h2><div id="scenarioSummary" class="scroll"></div></div></section>

<section id="sources" class="hidden"><div class="panel"><h2>Evidence boundaries</h2><p id="strictText"></p><div id="outputPolicy" class="scroll"></div><h3>Supported historical calculations</h3><div id="historical" class="scroll"></div><details><summary>Full evidence register</summary><label>Filter requirements<input id="filter" type="search"></label><div id="evidence" class="scroll"></div></details><details><summary>Source verification and modelling conventions</summary><p>Information cutoff: end of 15 May 2025. Primary-file extracts are machine-reviewed; hashes establish integrity, not factual accuracy. No independent human signoff is claimed. Costs classified in accounting statements do not establish economic cost behaviour. Public closing working capital is projected; Foot Locker receivables are held constant because their historical cash-flow movement is not separately disclosed.</p><p>Interest accrues on beginning-period principal. Payments, refinancing and maturity settlement occur at period end. A maturity inside a period is settled at that period end; this can defer a real cash need. Quarterly modelling reduces but does not eliminate that approximation.</p><pre id="metadata"></pre></details></div></section></div><footer>Student research project · No trading functionality · Forecasts and analytical thresholds are explicit assumptions.</footer></main>

<script id="data" type="application/json">__REPORT__</script><script>

__SCRIPT__
</script></body></html>"""
