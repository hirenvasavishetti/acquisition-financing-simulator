/* Presentation only. All financial values come from the canonical report. */
const viewNames = {
  overview: 'Overview',
  assumptions: 'Assumptions',
  funding: 'Sources & Uses',
  operating: 'Operating Forecast',
  liquidity: 'Debt & Liquidity',
  scenarios: 'Scenarios & Stress',
  capacityView: 'Debt Capacity',
  creditView: 'Credit Risk',
  marketsView: 'Rates Lab',
  sources: 'Evidence & Sources'
};
let activeView = 'overview';

function setupWorkspace() {
  const main = document.querySelector('main');
  const header = document.querySelector('header');
  const oldNav = document.querySelector('nav');
  const sidebar = document.createElement('aside');
  sidebar.className = 'sidebar';
  sidebar.id = 'sidebar';
  sidebar.innerHTML = `<button class="menu-close" id="closeMenu">Close navigation</button>
    <div class="brand"><span class="brand-mark" aria-hidden="true">A/F</span><span>Acquisition<span style="display:block;font-size:11px;font-weight:400;letter-spacing:.6px;color:#b6c2a5">Finance research</span></span></div>
    <div class="nav-caption">Research workspace</div>`;
  oldNav.replaceChildren();
  const icons = [
    '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    '<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="9" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="8" cy="18" r="2"/>',
    '<path d="M4 7h16m-4-4 4 4-4 4M20 17H4m4-4-4 4 4 4"/>',
    '<path d="M4 20V4m0 16h17M8 15l4-5 4 3 5-8"/>',
    '<path d="M4 19h16M7 15V9m5 6V4m5 11v-5"/>',
    '<path d="m3 17 5-7 5 4 8-10M3 7l5 7 5-4 8 10"/>',
    '<path d="M4 20h16M6 16V8h4v8m4 0V4h4v12"/>',
    '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6zM12 8v5m0 3h.01"/>',
    '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    '<path d="M5 3h10l4 4v14H5zM14 3v5h5M8 12h8m-8 4h6"/>'
  ];
  Object.entries(viewNames).forEach(([id, title], i) => {
    const button = document.createElement('button');
    button.dataset.view = id;
    button.innerHTML =
      `<span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${icons[i]}</svg></span><span>${title}</span>`;
    button.onclick = () => {
      showView(id);
      $("viewTitle").tabIndex = -1;
      $("viewTitle").focus({
        preventScroll: true
      });
    };
    oldNav.append(button);
  });
  sidebar.append(oldNav);
  const foot = document.createElement('div');
  foot.className = 'sidebar-foot';
  foot.innerHTML =
    '<strong>Follow the funding</strong>Funding → cash flow → credit risk.<br>Separate rates-risk laboratory.<br><br>Student research · USD millions';
  sidebar.append(foot);
  document.body.prepend(sidebar);
  const backdrop = document.createElement('button');
  backdrop.className = 'mobile-backdrop';
  backdrop.setAttribute('aria-label', 'Close navigation');
  backdrop.tabIndex = -1;
  backdrop.onclick = closeMenu;
  document.body.prepend(backdrop);

  header.innerHTML =
    `<div class="top-heading"><button id="menuToggle" aria-label="Open navigation" aria-controls="sidebar" aria-expanded="false">☰</button><div><div class="eyebrow">Corporate finance research</div><h1 id="viewTitle">Overview</h1><p id="cutoffLabel">Deterministic research workspace · USD millions</p></div></div>
    <div><div class="header-actions"><label class="timing-label">Model timing<select id="topTiming" aria-describedby="timingReason"><option value="1">Annual</option><option value="4">Quarterly</option></select></label><button id="topRecalculate" class="primary">Recalculate</button><button id="exportReport">↓ Export JSON</button></div><p id="exportHint">Download the displayed model report</p><p id="timingReason" class="minor"></p></div>`;
  $('menuToggle').onclick = () => {
    document.body.classList.toggle('sidebar-open');
    $('menuToggle').setAttribute('aria-expanded', document.body.classList.contains(
      'sidebar-open'));
    updateSidebarAccess();
    if (document.body.classList.contains('sidebar-open')) $('closeMenu').focus();
  };
  $('closeMenu').onclick = () => {
    closeMenu();
    $('menuToggle').focus();
  };
  matchMedia('(max-width:780px)').addEventListener('change', updateSidebarAccess);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && document.body.classList.contains('sidebar-open')) {
      closeMenu();
      $('menuToggle').focus();
    }
  });

  const results = $('results');
  setupRiskViews(results);
  // Split existing schedules into focused views; retain their original element IDs.
  const operating = document.createElement('section');
  operating.id = 'operating';
  operating.append($('operations').closest('.panel'));
  results.append(operating);
  const capacitySection = document.createElement('section');
  capacitySection.id = 'capacityView';
  capacitySection.append($('capacity').closest('.panel'));
  results.append(capacitySection);
  const scenarios = document.createElement('section');
  scenarios.id = 'scenarios';
  scenarios.append($('scenarioSummary').closest('.panel'));
  results.append(scenarios);
  const debtPanel = $('debt').closest('.panel');
  $('liquidity').append(debtPanel);
  const chartGrid = $('cashChart').closest('.grid');
  chartGrid.classList.add('overview-chart-grid');
  $('overview').insertBefore(chartGrid, $('finding').closest('.panel'));
  $('tradeoffChart').closest('.panel').classList.add('tradeoff-panel');
  const shortcut = $('selectedFinding').closest('.panel');
  shortcut.classList.add('research-shortcut');
  shortcut.querySelector('h3').textContent = 'Where does the plan break?';
  const shortcutCopy = document.createElement('p');
  shortcutCopy.textContent = 'Explore margin pressure and higher rates together in Credit Risk.';
  shortcut.append(shortcutCopy);
  const shortcutButton = document.createElement('button');
  shortcutButton.className = 'primary';
  shortcutButton.textContent = 'Explore Credit Risk';
  shortcutButton.onclick = () => showView('creditView');
  shortcut.append(shortcutButton);
  // Keep the three trend charts and funding comparison together on Overview.
  chartGrid.append($('tradeoffChart').closest('.panel'));
  for (const [chartId, label, hasThreshold] of [
      ['cashChart', 'Cash • USD m', true],
      ['debtChart', 'Debt • USD m', false],
      ['coverageChart', 'Coverage • times', true]
    ]) {
    const legend = document.createElement('div');
    legend.className = 'chart-note';
    legend.innerHTML =
      `<span>${label}</span>${hasThreshold?'<span class="threshold">Analytical threshold</span>':''}`;
    $(chartId).after(legend);
  }
  const selectionPanel = $('scenario').closest('.panel');
  selectionPanel.className = 'panel selection-bar';
  selectionPanel.prepend($('structure').closest('label'));
  selectionPanel.querySelector('p').textContent =
    'Selections change supporting schedules and charts. Overview structure cards always show the base case.';
  results.prepend(selectionPanel);
  const empty = document.createElement('p');
  empty.id = 'modelUnavailable';
  empty.className = 'empty-message hidden';
  empty.textContent =
    'Full financing schedules are unavailable in this assessment. Evidence & Sources shows independently supported historical calculations and the exact unresolved requirements.';
  results.prepend(empty);

  const workspace = document.createElement('div');
  workspace.className = 'workspace-grid';
  const centre = document.createElement('div');
  centre.className = 'workspace-main';
  while (main.firstChild) centre.append(main.firstChild);
  const insight = document.createElement('aside');
  insight.className = 'insights';
  insight.setAttribute('aria-label', 'Model insights');
  insight.innerHTML =
    `<div><h2>Model insights</h2><div class="insight-kicker">The context behind the numbers</div></div>
    <div class="insight-block"><h3>Selected analysis</h3><span class="chip" id="insightMode"></span><p id="insightSelection"></p><p id="insightBreach"></p></div>
    <div class="insight-block"><h3>Principal finding</h3><p id="insightFinding"></p><h3>Key assumptions</h3><p id="insightAssumptions"></p></div>
    <div class="insight-block"><h3>Evidence boundary</h3><p class="insight-limit" id="insightEvidence"></p><button class="subtle-button" id="reviewEvidence">Review evidence →</button></div>`;
  workspace.append(centre, insight);
  main.append(workspace);
  $('reviewEvidence').onclick = () => showView('sources');
  $('topTiming').onchange = () => {
    const input = $('controls').elements.namedItem('frequency');
    if (input) {
      input.value = $('topTiming').value;
      markStale();
    }
  };
  $('topRecalculate').onclick = () => {
    $('controls').requestSubmit();
  };
  $('exportReport').onclick = () => {
    if (document.body.classList.contains('dirty')) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(R, null, 2)], {
      type: 'application/json'
    }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `acquisition-financing-${mode}-report.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  // Only JSON is offered here: workbook/PDF generation remains the documented CLI path.
  showView(Object.hasOwn(viewNames, location.hash.slice(1)) ? location.hash.slice(1) : 'overview');
}

function closeMenu() {
  document.body.classList.remove('sidebar-open');
  $('menuToggle').setAttribute('aria-expanded', 'false');
  updateSidebarAccess();
}

function updateSidebarAccess() {
  const mobile = matchMedia('(max-width:780px)').matches;
  const opened = document.body.classList.contains('sidebar-open');
  $('sidebar').inert = mobile && !opened;
  document.querySelector('main').inert = mobile && opened;
  document.querySelector('header').inert = mobile && opened;
}

function showView(id) {
  activeView = id;
  document.body.classList.toggle("rates-view", id === "marketsView");
  $("scenario").disabled = id === "creditView" || !M;
  window.scrollTo({
    top: 0,
    behavior: "instant"
  });
  if (live) history.replaceState(null, '', '#' + id);
  Object.keys(viewNames).forEach(key => $(key).classList.toggle('hidden', key !== id));
  document.querySelectorAll('nav button').forEach(button => {
    const current = button.dataset.view === id;
    button.classList.toggle('active', current);
    if (current) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  });
  $('viewTitle').textContent = viewNames[id];
  closeMenu();
}

function markStale() {
  document.body.classList.add('dirty');
  $('stale').classList.remove('hidden');
  $('exportReport').disabled = true;
  const input = $('controls').elements.namedItem('frequency');
  if (input) $('topTiming').value = input.value;
}

function syncInsights() {
  if (!$('insightSelection')) return;
  const r = M?.comparisons.find(x => x.structure === $('structure').value && x.scenario === $(
    'scenario').value) || M?.base[0];
  $('insightMode').textContent = mode === 'synthetic' ? 'Fictional demonstration' : mode ===
    'public' ? 'Conditional public case' : 'Strict evidence assessment';
  $('insightSelection').textContent = r ? `${r.structure} · ${r.scenario} · ${r.timing_basis}` :
    'No full funding model';
  $('insightBreach').textContent = r ? breach(r.breaches[0]) :
    'Supported historical calculations remain available.';
  $('insightBreach').className = r && !r.feasible ? 'bad' : 'ok';
  $('insightFinding').textContent = $('finding').textContent;
  const cfg = P?.scenario_context?.[r?.scenario]?.config || M?.config;
  $('insightAssumptions').textContent = cfg ?
    `Cash reserve $${money(cfg.policy.cash_floor)}m. Maximum net leverage ${ratio(cfg.policy.max_leverage)}. Minimum coverage ${ratio(cfg.policy.min_coverage)}. Forecasts, cash access and refinancing remain explicit model choices.` :
    'No forecast assumptions can establish missing historical facts.';
  $('insightEvidence').textContent = R.evidence.blocked ?
    'Material evidence is incomplete, so no company-specific financing recommendation is available. Supported historical calculations and conditional projections remain available. See the evidence assessment for the unresolved requirements.' :
    R.recommendation_status + ' Analytical screens are not lender commitments or actual covenants.';
}

function render() {
  renderReport();
  $('historicalStatus').textContent = 'Company-specific recommendation: ' + (R.evidence.blocked ?
    'evidence incomplete' : R.preferred_structure ? 'qualified' : 'unavailable');
  $('historicalStatus').title = R.recommendation_status;
  $('scope').textContent = mode === 'synthetic' ?
    'How does the funding mix change liquidity, debt service and dilution? Fictional inputs only.' :
    mode === 'public' ?
    'Conditional annual projections from verified public starting information.' :
    'Verified history and unresolved evidence; no full financing recommendation.';
  $('cutoffLabel').textContent = mode === 'synthetic' ? 'Fictional case · USD millions' :
    'Information cutoff: 15 May 2025 · USD millions';
  $('topTiming').value = String(M?.frequency || 1);
  $('topTiming').disabled = mode !== 'synthetic' || !live;
  $('timingReason').textContent = mode === 'public' ?
    'Public projections support annual timing only.' : mode === 'strict' ?
    'Timing unavailable: no full historical model.' : !live ?
    'Saved timing; use the live server to recalculate.' : '';
  $('topRecalculate').disabled = !live || !M;
  $('topRecalculate').title = !live ? 'Recalculation requires the live server' : !M ?
    'No supported funding model' : 'Recalculate using the current assumption inputs';
  $('exportReport').disabled = false;
  $('scenario').disabled = $('structure').disabled = !M;
  $('modelUnavailable').classList.toggle('hidden', !!M);
  document.querySelector('.overview-chart-grid').classList.toggle('hidden', !M);
  document.querySelector('.selection-bar').classList.toggle('hidden', !M);
  if (!M) {
    $('runKind').textContent =
      'Evidence assessment: supported historical calculations are available in Evidence & Sources.';
    $('drivers').textContent =
      'Missing material evidence blocks the affected funding conclusions. It does not suppress independently verified historical calculations.';
  }
  if (!M) {
    options('structure', ['Unavailable']);
    options('scenario', ['Unavailable']);
  }
  syncInsights();
  renderRiskViews();
  showView(activeView);
}

function selected() {
  selectedReport();
  syncInsights();
  renderCreditGrid();
}
setupWorkspace();

// Charts display report values only; the threshold is drawn from model policy.
function chart(id, rows, key, floor, formatter = money) {
  const svg = $(id),
    ns = 'http://www.w3.org/2000/svg';
  svg.setAttribute('viewBox', '0 0 470 230');
  svg.replaceChildren();
  if (!rows.length) return;
  const values = rows.map(row => row[key]);
  const finite = values.filter(value => Number.isFinite(value));
  const low = Math.min(0, ...finite, Number.isFinite(floor) ? floor : 0);
  const high = Math.max(1, ...finite, Number.isFinite(floor) ? floor : 0);
  const y = value => 180 - (value - low) / (high - low) * 145;
  const x = index => 62 + index * 355 / Math.max(1, values.length - 1);

  function element(tag, attributes, text) {
    const node = document.createElementNS(ns, tag);
    Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
    if (text !== undefined) node.textContent = text;
    svg.append(node);
    return node;
  }
  for (let i = 0; i < 3; i++) {
    const value = low + (high - low) * i / 2;
    element('line', {
      x1: 62,
      x2: 417,
      y1: y(value),
      y2: y(value),
      stroke: '#eeedf2'
    });
    element('text', {
      x: 54,
      y: y(value) + 4,
      'text-anchor': 'end',
      'font-size': 10,
      fill: '#777381'
    }, formatter(value));
  }
  // Draw separate segments across missing observations, rather than connecting them.
  let segment = [];

  function draw() {
    if (!segment.length) return;
    const points = segment.map(([i, value]) => `${x(i)},${y(value)}`).join(' ');
    element('polygon', {
      points: `${x(segment[0][0])},180 ${points} ${x(segment.at(-1)[0])},180`,
      fill: '#dccbff',
      opacity: '.65'
    });
    element('polyline', {
      points,
      fill: 'none',
      stroke: '#7545f5',
      'stroke-width': 2.5,
      'stroke-linejoin': 'round'
    });
    segment = [];
  }
  values.forEach((value, i) => {
    if (Number.isFinite(value)) segment.push([i, value]);
    else draw();
  });
  draw();
  if (Number.isFinite(floor)) element('line', {
    x1: 62,
    x2: 417,
    y1: y(floor),
    y2: y(floor),
    stroke: '#647827',
    'stroke-dasharray': '5 4',
    'stroke-width': 1.5
  });
  [0, values.length - 1].forEach((i) => {
    if (Number.isFinite(values[i])) {
      element('circle', {
        cx: x(i),
        cy: y(values[i]),
        r: 3,
        fill: '#7545f5'
      });
      element('text', {
        x: x(i),
        y: Math.max(18, y(values[i]) - 12),
        'text-anchor': i ? 'end' : 'start',
        'font-size': 11,
        fill: '#6435d1'
      }, formatter(values[i]));
    }
    element('text', {
      x: x(i),
      y: 208,
      'text-anchor': i ? 'end' : 'start',
      'font-size': 10,
      fill: '#777381'
    }, rows[i].period_end);
  });
}
