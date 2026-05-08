/* habits.js — Habit tracker logic */

const HABIT_HISTORY_DAYS = 30;

async function loadHabits() {
  document.getElementById('habits-list').innerHTML =
    '<div class="loading"><div class="spinner"></div>Loading…</div>';
  try {
    const data = await fetch(`/api/habits?days=${HABIT_HISTORY_DAYS}`).then(r => r.json());
    renderHabitsToday(data.today, data.streaks);
    renderHabitsHistory(data.today, data.history, data.dates);
    renderHabitsStats(data.today, data.streaks);
  } catch (e) {
    document.getElementById('habits-list').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div>${e.message}</div>`;
  }
}

function renderHabitsStats(today, streaks) {
  const done  = today.filter(h => h.done).length;
  const total = today.length;
  const best  = Object.values(streaks).reduce((a, b) => Math.max(a, b), 0);
  document.getElementById('hstat-done').textContent  = `${done}/${total}`;
  document.getElementById('hstat-total').textContent = total;
  document.getElementById('hstat-best').textContent  = best ? `${best}d` : '—';
  document.getElementById('habits-stats-card').style.display = 'block';
}

function renderHabitsToday(today, streaks) {
  const el = document.getElementById('habits-list');
  if (!today.length) {
    el.innerHTML = '<div class="empty-state">No habits set up yet.</div>';
    return;
  }
  el.innerHTML = today.map(h => {
    const streak = streaks[h.id] || 0;
    const fire   = streak >= 3 ? ` <span class="streak-fire" title="${streak}-day streak">🔥 ${streak}</span>` : '';
    return `
      <div class="habit-row${h.done ? ' habit-done' : ''}" id="habit-row-${h.id}">
        <button class="habit-check${h.done ? ' checked' : ''}" onclick="toggleHabit(${h.id}, ${h.done})">
          ${h.done ? '✓' : ''}
        </button>
        <span class="habit-name">${esc(h.name)}${fire}</span>
        <button class="habit-del" onclick="deleteHabitUI(${h.id})" title="Remove">✕</button>
      </div>`;
  }).join('');
}

function renderHabitsHistory(today, history, dates) {
  const el = document.getElementById('habits-history');
  if (!today.length || !dates.length) { el.innerHTML = ''; return; }

  const todayStr = new Date().toISOString().slice(0, 10);

  // Build column header labels: show "MMM D" every 7 days, short weekday otherwise
  const colLabels = dates.map((d, i) => {
    const dt = new Date(d + 'T00:00:00');
    if (i === 0 || i % 7 === 0) {
      return dt.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
    return dt.toLocaleDateString([], { weekday: 'short' }).slice(0, 2);
  });

  // Dot cell HTML for a single day
  const dotCell = (done, date) => {
    const isToday = date === todayStr;
    const style   = isToday
      ? 'outline:2px solid var(--accent,#6c63ff);outline-offset:2px;border-radius:50%;'
      : '';
    return `<td style="padding:1px 2px;text-align:center">
      <div class="habit-dot${done ? ' done' : ''}" title="${date}" style="${style}"></div>
    </td>`;
  };

  el.innerHTML = `
    <div style="overflow-x:auto;padding-bottom:4px">
      <table style="border-collapse:collapse;white-space:nowrap;font-size:12px">
        <thead>
          <tr>
            <th style="text-align:left;padding-right:12px;min-width:80px;font-weight:500;color:var(--text-dim,#888)"></th>
            ${colLabels.map((lbl, i) => `
              <th title="${dates[i]}" style="padding:2px 2px 6px;font-weight:${dates[i]===todayStr?'700':'400'};
                color:${dates[i]===todayStr?'var(--accent,#6c63ff)':'var(--text-dim,#888)'};
                min-width:20px;text-align:center">${esc(lbl)}</th>
            `).join('')}
          </tr>
        </thead>
        <tbody>
          ${today.map(h => `
            <tr>
              <td style="padding-right:12px;padding-bottom:4px;color:var(--text,#ddd);white-space:nowrap">
                ${esc(h.name.replace(/\s[\S]*$/, ''))}
              </td>
              ${(history[String(h.id)] || []).map((done, i) => dotCell(done, dates[i])).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>`;
}

async function toggleHabit(id, isDone) {
  const method = isDone ? 'DELETE' : 'POST';
  await fetch(`/api/habits/${id}/log`, { method,
    headers: { 'Content-Type': 'application/json' }, body: '{}' });
  loadHabits();
}

async function deleteHabitUI(id) {
  if (!confirm('Remove this habit?')) return;
  await fetch(`/api/habits/${id}`, { method: 'DELETE' });
  loadHabits();
}

async function addHabitUI() {
  const name = document.getElementById('habit-input').value.trim();
  if (!name) return;
  await fetch('/api/habits', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  document.getElementById('habit-input').value = '';
  loadHabits();
}

document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.activeElement.id === 'habit-input') addHabitUI();
});

function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
