/* View code consumes Python results. No second financial engine in the browser. */
function setupRiskViews(results) {
  const credit = document.createElement('section');
  credit.id = 'creditView';
  credit.innerHTML =
    `<div class="risk-intro"><div><span class="section-tag">Credit research</span><h2>Where does the funding break?</h2><p>Test a weaker operating margin and higher base rates together. Read the cash cushion alongside the first failed screen.</p></div><div class="risk-rule">3 structures<br>9 joint stresses each<br>One connected cash model</div></div><div class="panel"><h3>Margin × benchmark rate</h3><p id="creditScope" class="minor"></p><div id="creditGrid" class="stress-grid"></div><p class="minor">Each tile shows the minimum cash cushion against the reserve, including closing. “Pass” means every analytical screen passes. Leverage, coverage and maturity tests can fail even with positive cash. This grid holds the selected structure's base assumptions fixed; it does not apply the saved scenario selector.</p></div>`;
  const market = document.createElement('section');
  market.id = 'marketsView';
  market.innerHTML =
    `<div class="risk-intro"><div><span class="section-tag">Fixed income</span><h2>Translate yield moves into P&amp;L.</h2><p>A hypothetical bullet bond connects price, duration, convexity and hedge sizing. This lab is separate from the acquisition model in every analysis mode.</p></div><div class="risk-rule">No live quotes<br>No company security<br>Coupon-date settlement</div></div><div class="panel"><h3>Instrument assumptions</h3><form id="bondForm"><div id="bondInputs" class="inputs"></div><button class="primary" type="submit" id="bondCalculate">Calculate bond risk</button></form><p id="bondError" role="alert" class="bad"></p><p id="bondStale" class="minor" role="status"></p></div><div id="bondResults"><div id="bondMetrics" class="risk-metrics"></div><div class="panel"><h3>Exact repricing versus duration + convexity</h3><div id="bondScenarios" class="scroll"></div></div><div class="panel"><h3>DV01 hedge sizing</h3><p id="bondHedge"></p><p id="bondLimits" class="minor"></p><button id="bondExport">Download bond analysis JSON</button></div></div>`;
  results.append(credit, market);
  const fields = [
    ['notional', 'Notional · USD', 100000000, 1, 10000000000, 1],
    ['years', 'Maturity · whole years', 5, 1, 30, 1],
    ['coupon', 'Coupon · fraction', .06, 0, .25, .001],
    ['benchmark', 'Benchmark yield · fraction', .04, 0, .2, .001],
    ['spread', 'Credit spread · fraction', .02, 0, .2, .001],
    ['hedge_dv01', 'Hypothetical hedge DV01 · USD / bp', 80, 1, 10000, 1]
  ];
  fields.forEach(([key, title, value, min, max, step]) => {
    const label = document.createElement('label');
    label.textContent = title;
    const input = document.createElement('input');
    Object.assign(input, {
      name: key,
      type: 'number',
      value,
      min,
      max,
      step,
      required: true
    });
    label.append(input);
    $('bondInputs').append(label);
  });
  const label = document.createElement('label');
  label.textContent = 'Coupon payments per year';
  const select = document.createElement('select');
  select.name = 'frequency';
  [1, 2, 4].forEach(value => {
    const option = new Option(String(value), String(value));
    option.selected = value === 2;
    select.append(option)
  });
  label.append(select);
  $('bondInputs').append(label);
  $('bondForm').oninput = () => {
    $('bondStale').textContent = 'Inputs changed. Recalculate before using these results.';
    $('bondResults').classList.add('bond-stale');
    $('bondExport').disabled = true;
  };
  $('bondForm').onsubmit = async event => {
    event.preventDefault();
    $('bondError').textContent = '';
    $('bondCalculate').disabled = true;
    try {
      const response = await fetch('/api/bond-risk?' + new URLSearchParams(new FormData($(
        'bondForm'))));
      const result = await response.json();
      if (!response.ok) throw new Error(result.error);
      renderBond(result);
    } catch (error) {
      $('bondError').textContent = error.message || 'Bond calculation unavailable.';
    } finally {
      $('bondCalculate').disabled = !live;
    }
  };
  $('bondCalculate').disabled = !live;
}

function renderCreditGrid() {
  if (!$('creditGrid')) return;
  const grid = M?.joint_stress;
  $('creditScope').textContent = grid ? grid.scope + ' · ' + $('structure').value :
    'No supported full financing model is available for this assessment.';
  $('creditGrid').replaceChildren();
  if (!grid) return;
  grid.cells.filter(cell => cell.structure === $('structure').value).forEach(cell => {
    const tile = document.createElement('div');
    tile.className = 'stress-cell ' + (cell.feasible ? 'stress-pass' : 'stress-fail');
    const title = document.createElement('h4');
    title.textContent = `Margin ${cell.margin_bp} bp / rate +${cell.rate_bp} bp`;
    const number = document.createElement('strong');
    number.textContent = `$${money(cell.cash_headroom)}m`;
    const state = document.createElement('p');
    state.textContent = cell.feasible ? 'Pass · all analytical screens' : breach(cell
      .first_breach);
    tile.append(title, number, state);
    $('creditGrid').append(tile);
  });
}

function renderBond(result) {
  if (!result) return;
  Object.entries(result.inputs).forEach(([key, value]) => {
    const input = $('bondForm').elements.namedItem(key);
    if (input) input.value = value;
  });
  $('bondMetrics').replaceChildren();
  [
    ['Price / 100', money(result.price)],
    ['Modified duration · years', result.modified_duration.toFixed(2)],
    ['DV01 · USD / bp', money(result.dv01)],
    ['Convexity', money(result.convexity)]
  ].forEach(([label, value]) => {
    const item = document.createElement('div'),
      name = document.createElement('span'),
      number = document.createElement('strong');
    name.textContent = label;
    number.textContent = value;
    item.append(name, number);
    $('bondMetrics').append(item);
  });
  table('bondScenarios', ['Rate Δ · bp', 'Spread Δ · bp', 'Price / 100', 'Exact P&L · USD',
    'Duration + convexity · USD'
  ], result.scenarios.map(s => [s.rate_bp, s.spread_bp, money(s.price), money(s.pnl), money(s
    .duration_convexity_pnl)]));
  $('bondHedge').textContent =
    `Short approximately ${result.hedge_short_contracts.toLocaleString()} hypothetical contracts at $${money(result.inputs.hedge_dv01)} DV01 each to offset the long bond's benchmark exposure. Residual DV01 after rounding: $${money(result.residual_dv01)} per bp. Credit-spread exposure remains: CS01 $${money(result.cs01)} per bp.`;
  $('bondLimits').textContent = result.limitations;
  $('bondStale').textContent = live ?
    'Rates are decimal fractions: 0.04 = 4%. Bond outputs use USD, while acquisition outputs use USD millions.' :
    'Saved illustrative results. Recalculation requires the live server.';
  $('bondResults').classList.remove('bond-stale');
  $('bondExport').disabled = false;
  $('bondExport').onclick = () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(result, null, 2)], {
      type: 'application/json'
    }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'illustrative-bond-risk.json';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
}

function renderRiskViews() {
  renderCreditGrid();
  renderBond(R.bond_lab);
}
