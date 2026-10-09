/* Presentation only. All financial values come from the canonical report. */
const viewNames = {
  overview: 'Overview', assumptions: 'Assumptions', funding: 'Sources & Uses',
  operating: 'Operating Forecast', liquidity: 'Debt & Liquidity',
  scenarios: 'Scenarios & Stress', capacityView: 'Debt Capacity', sources: 'Evidence & Sources'
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
    <div class="brand"><span class="brand-mark" aria-hidden="true">↗</span><span>Acquisition<span style="display:block;font-size:11px;font-weight:400;letter-spacing:.6px;color:#b6c2a5">FINANCE SIMULATOR</span></span></div>
    <div class="nav-caption">Research workspace</div>`;
  oldNav.replaceChildren();
  const icons = ['◫','≡','⇄','▥','◷','⌁','▤','◇'];
  Object.entries(viewNames).forEach(([id,title],i) => {
    const button = document.createElement('button');
    button.dataset.view = id;
    button.innerHTML = `<span class="nav-icon" aria-hidden="true">${icons[i]}</span><span>${title}</span>`;
    button.onclick = () => showView(id);
    oldNav.append(button);
  });
  sidebar.append(oldNav);
  const foot = document.createElement('div');
  foot.className = 'sidebar-foot';
  foot.innerHTML = '<strong>Built for financial inquiry</strong>Three funding structures.<br>One traceable model.<br><br>Student research · USD millions';
  sidebar.append(foot);
  document.body.prepend(sidebar);
  const backdrop = document.createElement('button');
  backdrop.className = 'mobile-backdrop';
  backdrop.setAttribute('aria-label','Close navigation');
  backdrop.tabIndex = -1;
  backdrop.onclick = closeMenu;
  document.body.prepend(backdrop);

  header.innerHTML = `<div class="top-heading"><button id="menuToggle" aria-label="Open navigation" aria-controls="sidebar" aria-expanded="false">☰</button><div><div class="eyebrow">Corporate finance research</div><h1 id="viewTitle">Overview</h1><p id="cutoffLabel">Deterministic research workspace · USD millions</p></div></div>
    <div><div class="header-actions"><label class="timing-label">Model timing<select id="topTiming" aria-describedby="timingReason"><option value="1">Annual</option><option value="4">Quarterly</option></select></label><button id="topRecalculate" class="primary">Recalculate</button><button id="exportReport">↓ Export JSON</button></div><p id="exportHint">Download the displayed model report</p><p id="timingReason" class="minor"></p></div>`;
  $('menuToggle').onclick = () => {
    document.body.classList.toggle('sidebar-open');
    $('menuToggle').setAttribute('aria-expanded',document.body.classList.contains('sidebar-open'));
    updateSidebarAccess();
    if(document.body.classList.contains('sidebar-open')) $('closeMenu').focus();
  };
  $('closeMenu').onclick = () => {closeMenu();$('menuToggle').focus();};
  matchMedia('(max-width:780px)').addEventListener('change',updateSidebarAccess);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.body.classList.contains('sidebar-open')){closeMenu();$('menuToggle').focus();}});

  const results = $('results');
  // Split existing schedules into focused views; retain their original element IDs.
  const operating = document.createElement('section'); operating.id='operating';
  operating.append($('operations').closest('.panel')); results.append(operating);
  const capacitySection = document.createElement('section'); capacitySection.id='capacityView';
  capacitySection.append($('capacity').closest('.panel')); results.append(capacitySection);
  const scenarios = document.createElement('section'); scenarios.id='scenarios';
  scenarios.append($('scenarioSummary').closest('.panel')); results.append(scenarios);
  const debtPanel = $('debt').closest('.panel'); $('liquidity').append(debtPanel);
  const chartGrid = $('cashChart').closest('.grid');
  chartGrid.classList.add('overview-chart-grid');
  $('overview').insertBefore(chartGrid,$('finding').closest('.panel'));
  $('tradeoffChart').closest('.panel').classList.add('tradeoff-panel');
  // Keep the three trend charts and funding comparison together on Overview.
  chartGrid.append($('tradeoffChart').closest('.panel'));
  for(const [chartId,label,hasThreshold] of [['cashChart','Cash • USD m',true],['debtChart','Debt • USD m',false],['coverageChart','Coverage • times',true]]) {
    const legend=document.createElement('div'); legend.className='chart-note';
    legend.innerHTML=`<span>${label}</span>${hasThreshold?'<span class="threshold">Analytical threshold</span>':''}`;
    $(chartId).after(legend);
  }
  const selectionPanel = $('scenario').closest('.panel');
  selectionPanel.className='panel selection-bar';
  selectionPanel.prepend($('structure').closest('label'));
  selectionPanel.querySelector('p').textContent='Selections change supporting schedules and charts. Overview structure cards always show the base case.';
  results.prepend(selectionPanel);
  const empty = document.createElement('p'); empty.id='modelUnavailable'; empty.className='empty-message hidden';
  empty.textContent='Full financing schedules are unavailable in this assessment. Evidence & Sources shows independently supported historical calculations and the exact unresolved requirements.';
  results.prepend(empty);

  const workspace = document.createElement('div'); workspace.className='workspace-grid';
  const centre = document.createElement('div'); centre.className='workspace-main';
  while(main.firstChild) centre.append(main.firstChild);
  const insight = document.createElement('aside'); insight.className='insights'; insight.setAttribute('aria-label','Model insights');
  insight.innerHTML=`<div><h2>Model insights</h2><div class="insight-kicker">The context behind the numbers</div></div>
    <div class="insight-block"><h3>Selected analysis</h3><span class="chip" id="insightMode"></span><p id="insightSelection"></p><p id="insightBreach"></p></div>
    <div class="insight-block"><h3>Principal finding</h3><p id="insightFinding"></p><h3>Key assumptions</h3><p id="insightAssumptions"></p></div>
    <div class="insight-block"><h3>Evidence boundary</h3><p class="insight-limit" id="insightEvidence"></p><button class="subtle-button" id="reviewEvidence">Review evidence →</button></div>`;
  workspace.append(centre,insight); main.append(workspace);
  $('reviewEvidence').onclick=()=>showView('sources');
  $('topTiming').onchange=()=>{
    const input=$('controls').elements.namedItem('frequency');
    if(input){input.value=$('topTiming').value;markStale();}
  };
  $('topRecalculate').onclick=()=>{$('controls').requestSubmit();};
  $('exportReport').onclick=()=>{
    if(document.body.classList.contains('dirty'))return;
    const url=URL.createObjectURL(new Blob([JSON.stringify(R,null,2)],{type:'application/json'}));
    const link=document.createElement('a');link.href=url;link.download=`acquisition-financing-${mode}-report.json`;link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  // Only JSON is offered here: workbook/PDF generation remains the documented CLI path.
  showView('overview');
}
function closeMenu(){
  document.body.classList.remove('sidebar-open');
  $('menuToggle').setAttribute('aria-expanded','false');
  updateSidebarAccess();
}
function updateSidebarAccess(){
  $('sidebar').inert=matchMedia('(max-width:780px)').matches&&!document.body.classList.contains('sidebar-open');
}
function showView(id){
  activeView=id;
  Object.keys(viewNames).forEach(key=>$(key).classList.toggle('hidden',key!==id));
  document.querySelectorAll('nav button').forEach(button=>{
    const current=button.dataset.view===id;button.classList.toggle('active',current);
    if(current)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');
  });
  $('viewTitle').textContent=viewNames[id];
  closeMenu();
}
function markStale(){
  document.body.classList.add('dirty');$('stale').classList.remove('hidden');$('exportReport').disabled=true;
  const input=$('controls').elements.namedItem('frequency');if(input)$('topTiming').value=input.value;
}
function syncInsights(){
  if(!$('insightSelection'))return;
  const r=M?.comparisons.find(x=>x.structure===$('structure').value&&x.scenario===$('scenario').value)||M?.base[0];
  $('insightMode').textContent=mode==='synthetic'?'Fictional demonstration':mode==='public'?'Conditional public case':'Strict evidence assessment';
  $('insightSelection').textContent=r?`${r.structure} · ${r.scenario} · ${r.timing_basis}`:'No full funding model';
  $('insightBreach').textContent=r?breach(r.breaches[0]):'Supported historical calculations remain available.';
  $('insightBreach').className=r&&!r.feasible?'bad':'ok';
  $('insightFinding').textContent=$('finding').textContent;
  const cfg=P?.scenario_context?.[r?.scenario]?.config||M?.config;
  $('insightAssumptions').textContent=cfg?`Cash reserve $${money(cfg.policy.cash_floor)}m. Maximum net leverage ${ratio(cfg.policy.max_leverage)}. Minimum coverage ${ratio(cfg.policy.min_coverage)}. Forecasts, cash access and refinancing remain explicit model choices.`:'No forecast assumptions can establish missing historical facts.';
  $('insightEvidence').textContent=R.evidence.blocked?'Material evidence is incomplete, so no company-specific financing recommendation is available. Supported historical calculations and conditional projections remain available. See the evidence assessment for the unresolved requirements.':R.recommendation_status+' Analytical screens are not lender commitments or actual covenants.';
}
function render(){
  renderReport();
  $('historicalStatus').textContent='Company-specific recommendation: '+(R.evidence.blocked?'evidence incomplete':R.preferred_structure?'qualified':'unavailable');
  $('historicalStatus').title=R.recommendation_status;
  $('scope').textContent=mode==='synthetic'?'How does the funding mix change liquidity, debt service and dilution? Fictional inputs only.':mode==='public'?'Conditional annual projections from verified public starting information.':'Verified history and unresolved evidence; no full financing recommendation.';
  $('cutoffLabel').textContent=mode==='synthetic'?'Fictional case · USD millions':'Information cutoff: 15 May 2025 · USD millions';
  $('topTiming').value=String(M?.frequency||1);
  $('topTiming').disabled=mode!=='synthetic'||!live;
  $('timingReason').textContent=mode==='public'?'Public projections support annual timing only.':mode==='strict'?'Timing unavailable: no full historical model.':!live?'Saved timing; use the live server to recalculate.':'';
  $('topRecalculate').disabled=!live||!M;
  $('topRecalculate').title=!live?'Recalculation requires the live server':!M?'No supported funding model':'Recalculate using the current assumption inputs';
  $('exportReport').disabled=false;
  $('scenario').disabled=$('structure').disabled=!M;
  $('modelUnavailable').classList.toggle('hidden',!!M);
  document.querySelector('.overview-chart-grid').classList.toggle('hidden',!M);
  document.querySelector('.selection-bar').classList.toggle('hidden',!M);
  if(!M){
    $('runKind').textContent='Evidence assessment: supported historical calculations are available in Evidence & Sources.';
    $('drivers').textContent='Missing material evidence blocks the affected funding conclusions. It does not suppress independently verified historical calculations.';
  }
  if(!M){options('structure',['Unavailable']);options('scenario',['Unavailable']);}
  syncInsights();
  showView(activeView);
}
function selected(){selectedReport();syncInsights();}
setupWorkspace();

// Charts display report values only; the threshold is drawn from model policy.
function chart(id, rows, key, floor, formatter=money) {
  const svg=$(id), ns='http://www.w3.org/2000/svg';
  svg.setAttribute('viewBox','0 0 470 230'); svg.replaceChildren();
  if(!rows.length)return;
  const values=rows.map(row=>row[key]);
  const finite=values.filter(value=>Number.isFinite(value));
  const low=Math.min(0,...finite,Number.isFinite(floor)?floor:0);
  const high=Math.max(1,...finite,Number.isFinite(floor)?floor:0);
  const y=value=>180-(value-low)/(high-low)*145;
  const x=index=>62+index*355/Math.max(1,values.length-1);
  function element(tag,attributes,text){
    const node=document.createElementNS(ns,tag);
    Object.entries(attributes).forEach(([key,value])=>node.setAttribute(key,value));
    if(text!==undefined)node.textContent=text;svg.append(node);return node;
  }
  for(let i=0;i<3;i++){
    const value=low+(high-low)*i/2;
    element('line',{x1:62,x2:417,y1:y(value),y2:y(value),stroke:'#eeedf2'});
    element('text',{x:54,y:y(value)+4,'text-anchor':'end','font-size':10,fill:'#777381'},formatter(value));
  }
  // Draw separate segments across missing observations, rather than connecting them.
  let segment=[];
  function draw(){
    if(!segment.length)return;
    const points=segment.map(([i,value])=>`${x(i)},${y(value)}`).join(' ');
    element('polygon',{points:`${x(segment[0][0])},180 ${points} ${x(segment.at(-1)[0])},180`,fill:'#a784ee',opacity:'.18'});
    element('polyline',{points,fill:'none',stroke:'#8050e6','stroke-width':2.5,'stroke-linejoin':'round'});
    segment=[];
  }
  values.forEach((value,i)=>{if(Number.isFinite(value))segment.push([i,value]);else draw();});draw();
  if(Number.isFinite(floor))element('line',{x1:62,x2:417,y1:y(floor),y2:y(floor),stroke:'#a35c2e','stroke-dasharray':'5 4','stroke-width':1.5});
  [0,values.length-1].forEach((i)=>{
    if(Number.isFinite(values[i])){
      element('circle',{cx:x(i),cy:y(values[i]),r:3,fill:'#8050e6'});
      element('text',{x:x(i),y:Math.max(18,y(values[i])-12),'text-anchor':i?'end':'start','font-size':11,fill:'#5930a5'},formatter(values[i]));
    }
    element('text',{x:x(i),y:208,'text-anchor':i?'end':'start','font-size':10,fill:'#777381'},rows[i].period_end);
  });
}
