$('mode').onchange = () => {
  if (live) location.href = '?mode=' + $('mode').value;
  else location.href = '../' + ({
    synthetic: 'full-output',
    public: 'public-output',
    strict: 'historical-output'
  } [$('mode').value]) + '/dashboard.html';
};
$('structure').onchange = selected;
$('scenario').onchange = selected;
$('filter').oninput = evidence;
$('controls').oninput = markStale;
$('restore').onclick = render;
$('controls').onsubmit = async e => {
  e.preventDefault();
  if (!live || !M) return;
  showView('assumptions');
  $('topRecalculate').disabled = true;
  document.body.classList.add('dirty');
  $('stale').classList.remove('hidden');
  $('recalculate').disabled = true;
  try {
    let q = new URLSearchParams(new FormData($('controls')));
    q.set('mode', mode);
    let response = await fetch('/api/report?' + q, {
        cache: 'no-store'
      }),
      data = await response.json();
    if (!response.ok || data.error) throw Error(data.error || 'Recalculation failed');
    R = data;
    render();
  } catch (e) {
    $('error').textContent = e.message;
  } finally {
    $('recalculate').disabled = !live || !M;
    $('topRecalculate').disabled = !live || !M
  }
};
render();
