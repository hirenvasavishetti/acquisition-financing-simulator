let R = JSON.parse(document.getElementById('data').textContent),
  M, P, mode;
const $ = id => document.getElementById(id),
  live = location.protocol !== 'file:';

const money = x => x === null || x === undefined ? 'Unavailable' : Number(x).toLocaleString(
  'en-US', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }),
  pct = x => x == null ? 'Unavailable' : (x * 100).toFixed(1) + '%',
  ratio = x => x == null ? 'Unavailable' : x.toFixed(2) + '×';

const human = x => x.replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase());

function breach(b, frequency = M?.frequency) {
  return !b ? 'Passes all model screens' : (b.constraint === 'cash' ? 'Cash reserve breached' :
    human(b.constraint) + ' screen breached') + ' at ' + (b.period === 0 ? 'closing' : 'Year ' + b
    .year + (frequency === 4 ? ', quarter ' + ((b.period - 1) % 4 + 1) : ''));
}

function table(id, heads, rows) {
  let t = document.createElement('table'),
    tr = t.createTHead().insertRow();
  heads.forEach(x => {
    let c = document.createElement('th');
    c.textContent = x;
    tr.append(c)
  });
  let body = t.createTBody();
  rows.forEach(row => {
    let tr = body.insertRow();
    row.forEach(x => {
      let td = tr.insertCell();
      td.textContent = x ?? 'Unavailable'
    })
  });
  $(id).replaceChildren(t)
}

function options(id, values) {
  $(id).replaceChildren();
  values.forEach(x => {
    let o = document.createElement('option');
    o.value = o.textContent = x;
    $(id).append(o)
  })
}

function chart(id, rows, key, floor, formatter = money) {
  let s = $(id),
    ns = 'http://www.w3.org/2000/svg';
  s.setAttribute('viewBox', '0 0 470 230');
  s.replaceChildren();
  let vals = rows.map(r => r[key]);
  let finite = vals.filter(x => x != null),
    lo = Math.min(0, ...finite),
    hi = Math.max(1, ...finite, floor || 0),
    y = v => 185 - (v - lo) / (hi - lo) * 155,
    x = i => 42 + i * 380 / Math.max(1, vals.length - 1);

  function el(tag, attrs, text) {
    let e = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
    if (text) e.textContent = text;
    s.append(e)
  }
  el('polyline', {
    points: vals.map((v, i) => v == null ? '' : `${x(i)},${y(v)}`).join(' '),
    fill: 'none',
    stroke: '#8050e6',
    'stroke-width': 3
  });
  if (floor !== undefined) el('line', {
    x1: 35,
    x2: 430,
    y1: y(floor),
    y2: y(floor),
    stroke: '#ae512a',
    'stroke-dasharray': '5'
  });
  [0, vals.length - 1].forEach(i => {
    if (vals[i] != null) el('text', {
      x: x(i) - 15,
      y: Math.max(20, y(vals[i]) - 10),
      'font-size': 12
    }, formatter(vals[i]));
    el('text', {
      x: x(i) - 15,
      y: 213,
      'font-size': 11
    }, rows[i]?.period_end || '')
  })
}

function addInput(key, label, value, type = 'number', choices) {
  let l = document.createElement('label');
  l.textContent = label;
  let e = document.createElement(choices ? 'select' : 'input');
  e.name = key;
  if (choices) choices.forEach(([v, t]) => {
    let o = document.createElement('option');
    o.value = v;
    o.textContent = t;
    e.append(o)
  });
  else {
    e.type = type;
    e.step = 'any';
  }
  e.value = value;
  l.append(e);
  $('inputs').append(l)
}

function controls() {
  $('inputs').replaceChildren();
  $('recalculate').disabled = !live || !M;
  if (!M) return;
  let a = P?.assumptions || M.config.policy;
  for (let [k, label] of [
      ['cash_floor', 'Cash reserve (USD m)'],
      ['max_leverage', 'Maximum net leverage (×)'],
      ['min_coverage', 'Minimum coverage (×)']
    ]) addInput(k, label, a[k]);
  addInput('fee_convention', 'Financing fee convention', M.config.transaction.fee_convention ||
    'fixed_budget', '', [
      ['fixed_budget', 'Fixed original fee budget'],
      ['issued_debt', 'Fees on actual issued debt']
    ]);
  if (mode === 'synthetic') addInput('frequency', 'Model / capacity timing', M.frequency || 1, '', [
    [1, 'Annual'],
    [4, 'Quarterly']
  ]);
  if (P) {
    for (let [k, label] of [
        ['cash_access', 'Accessible DKS closing cash (fraction)'],
        ['operating_cash_access', 'Positive operating cash access'],
        ['dividend_factor', 'Dividend multiplier'],
        ['synergy', 'Eventual synergies (USD m)'],
        ['benchmark', 'Benchmark rate (fraction)'],
        ['spread', 'New debt spread (fraction)']
      ]) addInput(k, label, a[k]);
    for (let [i, suffix] of [
        [0, 'dks'],
        [1, 'fl']
      ]) {
      addInput('gross_annual_capex_' + suffix, suffix.toUpperCase() + ' initial annual capex', a
        .gross_annual_capex[i]);
      addInput('variable_cost_share_' + suffix, suffix.toUpperCase() +
        ' variable share of nonrent costs', a.variable_cost_share[i]);
      addInput('growth_' + suffix, suffix.toUpperCase() + ' growth (5 comma-separated fractions)', a
        .growth[i].join(', '), 'text');
    }
    addInput('refinance', 'Assumed term refinancing', String(a.refinance), '', [
      ['false', 'Unavailable'],
      ['true', 'Assumed, not committed']
    ]);
  }
  $('recalculate').disabled = !live;
}

function renderReport() {
  P = R.public_information;
  mode = P ? 'public' : R.model ? 'synthetic' : 'strict';
  M = R.model;
  if (P && P.base.length) M = {
    base: P.base,
    comparisons: P.scenario_results || P.base,
    config: P.config,
    capacity: P.capacity,
    reverse_stress: P.reverse_stress,
    frequency: 1,
    recommendation: {
      narrative: P.conclusion
    }
  };
  $('mode').value = mode;
  $('caseTitle').textContent = mode === 'synthetic' ? 'Atlas / Beacon — fictional demonstration' :
    "DICK’S Sporting Goods / Foot Locker — 15 May 2025 information set";
  $('scope').textContent = mode === 'synthetic' ?
    'Deterministic synthetic inputs; no findings about actual companies' :
    'Conditional projections from verified public starting information';
  $('operational').textContent = M ? (P ? 'Public-information case: conditional' :
    'Synthetic demonstration: operational') : (P ? 'Public case: partial calculations' :
    'Strict historical assessment');
  $('timing').textContent = M ? (M.frequency === 4 ? 'Quarterly model, capacity and stress' :
    'Annual model, capacity and stress') : 'No full funding model';
  $('historicalStatus').textContent = 'Actual-company recommendation: ' + (R.preferred_structure ?
    'qualified' : 'blocked');
  $('runKind').textContent = live ? 'Live Python model. Submit future assumptions to recalculate.' :
    'Saved results. Scenario selection works offline; assumption edits require the live server or CLI.';
  $('strictText').textContent = R.recommendation_status +
    ' This applies to the strict recommendation, not independently supported calculations.';
  $('finding').textContent = M?.recommendation.narrative ||
    'Full historical financing conclusions remain blocked. See supported calculations and the evidence register.';
  $('drivers').textContent = P ?
    'Results depend on cost behaviour, investment, dividends, cash access and synergy delivery. Mechanical capex cuts hold growth fixed; linked scenarios reduce growth by an assumed range. Neither establishes an executable financing preference.' :
    'Annual feasibility does not establish quarterly liquidity sufficiency. Compare capacity at both frequencies under the same economic assumptions.';

  $('comparison').replaceChildren();
  if (!M) {
    for (let id of ['uses', 'bridge', 'debt', 'costs', 'operations', 'annual', 'capacity',
        'reverse', 'scenarioSummary', 'tradeoffs', 'investment', 'tradeoffChart', 'cashChart',
        'debtChart', 'coverageChart'
      ]) $(id).replaceChildren();
    $('selectedFinding').textContent = 'Unavailable: required dependencies missing';
    if (P?.projected_bridge) table('bridge', ['Company', 'Reported cash', 'Projected CFO', 'Capex',
      'Dividends', 'Projected accounting cash', 'Accessible cash'
    ], P.projected_bridge.map(b => [b.company, money(b.reported_cash), money(b.projected_cfo),
      money(b.projected_gross_capex), money(b.projected_dividends), money(b.projected_cash),
      money(b.usable_cash)
    ]));
  }
  if (M) {
    for (let r of M.base) {
      let d = document.createElement('article');
      d.className = 'card';
      let title = document.createElement('h3');
      title.textContent = r.structure;
      d.append(title);
      for (let [l, v] of [
          ['New borrowing · USD m', money(r.opening.total_new_borrowing)],
          ['Minimum cash · USD m', money(r.min_cash)],
          ['Common share dilution', pct(r.opening.ownership_dilution)]
        ]) {
        let p = document.createElement('div');
        p.className = 'minor';
        p.textContent = l;
        let n = document.createElement('div');
        n.className = 'metric';
        n.textContent = v;
        d.append(p, n)
      }
      let p = document.createElement('p');
      p.className = r.feasible ? 'ok' : 'bad';
      p.textContent = breach(r.breaches[0]);
      d.append(p);
      $('comparison').append(d)
    }
    tradeoffChart(M.base);
    options('structure', M.base.map(r => r.structure));
    options('scenario', [...new Set(M.comparisons.map(r => r.scenario))]);
    table('tradeoffs', ['Structure', 'Cash contribution', 'New debt', 'Five-year interest',
      'Dilution'
    ], M.base.map(r => [r.structure, money(r.opening.cash_contribution), money(r.opening
      .total_new_borrowing), money(r.total_interest), pct(r.opening.ownership_dilution)]));
    selected();
  }

  table('outputPolicy', ['Output', 'Status', 'Limitation'], (P?.output_policy || []).map(x => [x
    .output, x.status, x.limitation
  ]));
  table('historical', ['Calculation', 'Status', 'Value', 'Units'], (R
    .supported_historical_calculations || []).map(x => [x.calculation, x.status, x.value ==
    null ? 'Unavailable' : money(x.value), x.units
  ]));
  evidence();
  $('metadata').textContent = JSON.stringify(P?.provenance || {
    input: R.config_id,
    code: M?.code_id
  }, null, 2);
  controls();
  document.body.classList.remove('dirty');
  $('stale').classList.add('hidden');
  $('error').textContent = '';
}

function selectedReport() {
  if (!M) return;
  let r = M.comparisons.find(x => x.structure === $('structure').value && x.scenario === $(
      'scenario').value) || M.base[0],
    o = r.opening,
    C = P?.scenario_context?.[r.scenario] || P,
    cfg = C?.config || M.config;
  table('uses', ['Funding item', 'USD m'], [...Object.entries(o.itemised_uses || {}).map(([k,
      v]) => [human(k), money(v)]), ['Total cash uses', money(o.cash_uses)],
    ['Acquisition cash contribution', money(o.cash_contribution)],
    ['New borrowing', money(o.total_new_borrowing)],
    ['Analytical equity', money(o.analytical_equity)],
    ['Sources less uses', money(o.sources_uses_difference)]
  ]);
  table('bridge', ['Company', 'Reported cash', 'Projected CFO', 'Capex', 'Dividends',
    'Projected accounting cash', 'Accessible cash'
  ], P ? C.projected_bridge.map(b => [b.company, money(b.reported_cash), money(b.projected_cfo),
    money(b.projected_gross_capex), money(b.projected_dividends), money(b.projected_cash),
    money(b.usable_cash)
  ]) : o.bridges.map(b => [b.company, money(b.latest_cash), money(b.operating), money(b.capex),
    money(b.dividends), money(b.closing_cash), money(b.closing_cash)
  ]));
  table('debt', ['Instrument', 'Year', 'Opening debt', 'Rate', 'Interest', 'Mandatory paid',
    'Optional paid', 'Closing debt'
  ], r.debt_schedule.filter(x => x.instrument !== 'Committed revolver' || x.opening_principal ||
    x.draw).map(x => [x.instrument, x.year, money(x.opening_principal), pct(x.rate), money(x
    .interest), money(x.mandatory_paid), money(x.optional_paid), money(x.closing_principal)]));
  table('operations', ['Company', 'Year', 'Revenue', 'EBITDA', 'Capex', 'Inventory', 'Receivables',
    'Payables', 'Change WC'
  ], r.company_forecasts.map(x => [x.company, x.year, money(x.revenue), money(x.ebitda), money(x
      .capex), money(x.inventory), money(x.receivables), money(x.payables), money(x
    .delta_nwc)]));
  table('costs', ['Company', 'Reported operating profit', 'D&A add-back', 'Starting EBITDA',
    'Nonrent cost pool', 'Assumed variable share'
  ], (C?.cost_reconciliation || []).map((x, i) => [M.config.companies[i].name, money(x.reported
    .operating_profit), money(x.da_addback), money(x.starting_ebitda), money(x
    .nonrent_cash_cost_pool), pct(x.assumed_variable_share)]));
  table('investment', ['Company', 'Gross investment', 'Assumed maintenance', 'Residual growth'], (C
    ?.investment_split || []).map(x => [x.company, money(x.gross), money(x.assumed_maintenance),
    money(x.residual_growth)
  ]));
  let rows = r.periods;
  chart('cashChart', rows, 'closing_cash', cfg.policy.cash_floor);
  chart('debtChart', rows, 'closing_debt');
  chart('coverageChart', rows, 'coverage', cfg.policy.min_coverage, ratio);
  $('selectedFinding').textContent = r.structure + ' / ' + r.scenario + ': ' + breach(r.breaches[
    0]) + '. Timing: ' + r.timing_basis + '.';
  table('annual', ['Period end', 'Revenue', 'EBITDA', 'Interest', 'Cash', 'Debt', 'Net leverage',
    'Coverage', 'Maturity funding gap'
  ], rows.map(x => [x.period_end, money(x.revenue), money(x.ebitda), money(x.interest), money(x
    .closing_cash), money(x.closing_debt), ratio(x.net_leverage), ratio(x.coverage), money(x
    .maturity_gap)]));
  let caps = [];
  if (M.capacity_by_frequency) {
    for (let [f, cs] of Object.entries(M.capacity_by_frequency))
      for (let [s, c] of Object.entries(cs)) caps.push([s, +f === 4 ? 'Quarterly' : 'Annual', c
        .maximum_acquisition_borrowing == null ? 'No feasible solution' : money(c
          .maximum_acquisition_borrowing), money(c.residual_analytical_equity), breach(c
          .limiting_constraint, +f)
      ]);
  } else
    for (let [s, c] of Object.entries(M.capacity)) caps.push([s, 'Annual', c
      .maximum_acquisition_borrowing == null ? 'No feasible solution' : money(c
        .maximum_acquisition_borrowing), money(c.residual_analytical_equity), breach(c
        .limiting_constraint)
    ]);
  table('capacity', ['Structure', 'Timing', 'Maximum acquisition debt',
    'Residual analytical equity', 'Limiting screen'
  ], caps);
  table('reverse', ['Structure', 'Timing', 'First tested revenue decline', 'Result'], Object
    .entries(M.reverse_stress).map(([s, x]) => [s, x.timing_basis, pct(x.revenue_decline), x
      .status
    ]));
  $('frequencyNote').textContent = P ?
    'Public case remains annual: verified historical quarterly seeds are insufficient. Capacity uses a $25m grid / $5m boundary refinement.' :
    'Annual and quarterly use identical operating assumptions, with payments and interest settled at different period ends. Capacity uses a $10m grid / $1m boundary refinement.';
  table('scenarioSummary', ['Scenario', 'Structure', 'First breach', 'Minimum cash', 'Interest'], M
    .comparisons.map(x => [x.scenario, x.structure, breach(x.breaches[0]), money(x.min_cash),
      money(x.total_interest)
    ]));
}

function tradeoffChart(rows) {
  let svg = $('tradeoffChart'),
    ns = 'http://www.w3.org/2000/svg',
    max = Math.max(1, ...rows.map(r => r.opening.total_new_borrowing));
  svg.setAttribute('viewBox', '0 0 700 175');
  svg.replaceChildren();
  rows.forEach((r, i) => {
    let t = document.createElementNS(ns, 'text');
    t.setAttribute('x', 0);
    t.setAttribute('y', 30 + i * 50);
    t.setAttribute('font-size', 14);
    t.textContent = r.structure;
    svg.append(t);
    let b = document.createElementNS(ns, 'rect');
    b.setAttribute('x', 170);
    b.setAttribute('y', 12 + i * 50);
    b.setAttribute('height', 25);
    b.setAttribute('width', 400 * r.opening.total_new_borrowing / max);
    b.setAttribute('fill', ['#7543eb', '#b499ef', '#a8ce47'][i]);
    svg.append(b);
    let n = t.cloneNode();
    n.setAttribute('x', 590);
    n.textContent = money(r.opening.total_new_borrowing);
    svg.append(n)
  })
}

function evidence() {
  let needle = $('filter').value.toLowerCase();
  table('evidence', ['Requirement', 'Classification', 'Materiality', 'Resolution'], R.evidence.rows
    .filter(x => JSON.stringify(x).toLowerCase().includes(needle)).map(x => [x.key, x
      .classification, x.materiality_reason, x.resolution
    ]));
}
