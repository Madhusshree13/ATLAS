/* ═══════════════════════════════════════════════════════════
   world.js  —  Atlas Dashboard logic + analytics
═══════════════════════════════════════════════════════════ */

// ── Clock ──────────────────────────────────────────────────
function tickClock() {
  const el = document.getElementById('world-clock');
  if (!el) return;
  const now = new Date();
  el.textContent =
    now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) +
    '  ·  ' +
    now.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
}
setInterval(tickClock, 1000);
tickClock();

// ── Tab switching ──────────────────────────────────────────
const _loaded = {};

document.getElementById('nav-tabs').addEventListener('click', (e) => {
  const btn = e.target.closest('.nav-tab');
  if (!btn) return;
  const tab = btn.dataset.tab;

  document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));

  btn.classList.add('active');
  document.getElementById('panel-' + tab).classList.add('active');

  if (!_loaded[tab]) {
    _loaded[tab] = true;
    if (tab === 'tasks')      loadTasks();
    if (tab === 'meetings')   loadMeetings();
    if (tab === 'health')     loadHealth();
    if (tab === 'habits')     loadHabits();
    if (tab === 'calendar')   calInit();
    if (tab === 'journal')    journalInit();
    if (tab === 'finance')    loadFinance();
    if (tab === 'sysmon')     sysmonInit();
    if (tab === 'notes')      loadNotes();
    if (tab === 'whiteboard') initWhiteboard();
  }
  // stop sysmon polling when leaving that tab
  if (tab !== 'sysmon' && typeof sysmonStop === 'function') sysmonStop();
});

loadEmails();
_loaded['email'] = true;

// ── Helpers ────────────────────────────────────────────────
async function apiFetch(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

function fmt12(isoStr) {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  if (isNaN(d)) return isoStr;
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function minsAgo(isoStr) {
  if (!isoStr) return '';
  const diff = Date.now() - new Date(isoStr).getTime();
  if (diff < 0) return '';
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  if (h > 23) return new Date(isoStr).toLocaleDateString([], { month: 'short', day: 'numeric' });
  if (h > 0) return `${h}h ${m}m ago`;
  if (m > 0) return `${m}m ago`;
  return 'just now';
}

function fmtMins(m) {
  m = Math.round(m);
  if (m <= 0) return '0m';
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60), rem = m % 60;
  return rem > 0 ? `${h}h ${rem}m` : `${h}h`;
}

function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return isNaN(d) ? '' : d.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function esc(str) {
  return String(str || '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ══════════════════════════════════════════════════════════
// EMAIL
// ══════════════════════════════════════════════════════════
async function loadEmails(force = false) {
  if (force) await fetch('/api/cache/clear', { method: 'POST' });
  const el = document.getElementById('email-list');
  el.innerHTML = '<div class="loading"><div class="spinner"></div>Loading emails…</div>';

  try {
    const emails = await apiFetch('/api/emails');
    const cnt = document.getElementById('email-count');

    if (!emails.length) {
      el.innerHTML = '<div class="empty-state"><div class="empty-icon">📭</div>No emails today. Inbox is clear.</div>';
      cnt.style.display = 'none';
      return;
    }

    cnt.textContent = emails.length;
    cnt.style.display = 'inline-flex';

    renderEmailAnalytics(emails);

    el.innerHTML = emails.map(em => {
      const initials = (em.sender || '?').replace(/<.*>/, '').trim().split(' ')
        .slice(0, 2).map(s => s[0] || '').join('').toUpperCase() || '?';
      return `
        <div class="email-item">
          <div class="email-avatar">${esc(initials)}</div>
          <div class="email-body">
            <div class="email-sender">${esc((em.sender || '').replace(/<.*>/, '').trim())}</div>
            <div class="email-subject">${esc(em.subject)}</div>
          </div>
          <div class="email-time">${minsAgo(em.date || '')}</div>
        </div>`;
    }).join('');
  } catch (err) {
    document.getElementById('email-list').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div>Could not load emails.<br><small>${err.message}</small></div>`;
  }
}

function renderEmailAnalytics(emails) {
  // Sender frequency map
  const senderCounts = {};
  emails.forEach(em => {
    const name = (em.sender || 'Unknown').replace(/<[^>]+>/g, '').trim() || 'Unknown';
    senderCounts[name] = (senderCounts[name] || 0) + 1;
  });
  const uniqueSenders = Object.keys(senderCounts).length;

  // Most recent email
  const validDates = emails.map(em => em.date ? new Date(em.date) : null).filter(Boolean);
  const latestLabel = validDates.length
    ? minsAgo(validDates.sort((a, b) => b - a)[0].toISOString())
    : '—';

  // Stats card
  document.getElementById('estat-total').textContent   = emails.length;
  document.getElementById('estat-senders').textContent = uniqueSenders;
  document.getElementById('estat-latest').textContent  = latestLabel;
  document.getElementById('email-stats-card').style.display = 'block';

  // Top senders bar chart
  const top = Object.entries(senderCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const maxCount = top[0]?.[1] || 1;

  document.getElementById('email-senders-list').innerHTML = top.map(([name, count]) => {
    const shortName = name.split(' ').slice(0, 2).join(' ');
    const barPct = ((count / maxCount) * 100).toFixed(0);
    return `
      <div class="sender-row">
        <div class="sender-name">${esc(shortName)}</div>
        <div class="sender-bar-wrap"><div class="sender-bar" style="width:${barPct}%"></div></div>
        <div class="sender-count">${count}</div>
      </div>`;
  }).join('');
  document.getElementById('email-senders-card').style.display = 'block';
}

// ══════════════════════════════════════════════════════════
// MEETINGS
// ══════════════════════════════════════════════════════════
async function loadMeetings(force = false) {
  if (force) await fetch('/api/cache/clear', { method: 'POST' });
  const el = document.getElementById('meetings-list');
  el.innerHTML = '<div class="loading"><div class="spinner"></div>Loading schedule…</div>';

  try {
    const events = await apiFetch('/api/meetings');

    if (!events.length) {
      el.innerHTML = '<div class="empty-state"><div class="empty-icon">📅</div>No meetings scheduled for today.</div>';
      return;
    }

    renderMeetingsAnalytics(events);

    el.innerHTML = events.map((ev, i) => {
      const start = fmt12(ev.start);
      const end   = fmt12(ev.end);
      let dur = '';
      if (ev.start && ev.end) {
        const mins = Math.round((new Date(ev.end) - new Date(ev.start)) / 60000);
        dur = fmtMins(mins);
      }
      return `
        <div class="meeting-block">
          <div class="meeting-time">${esc(start)}</div>
          <div class="meeting-axis">
            <div class="meeting-dot"></div>
            ${i < events.length - 1 ? '<div class="meeting-line"></div>' : ''}
          </div>
          <div class="meeting-body">
            <div class="meeting-card">
              <div class="meeting-title">${esc(ev.title || 'Busy')}</div>
              <div class="meeting-meta">${esc(start)} – ${esc(end)}${dur ? ' · ' + dur : ''}</div>
            </div>
          </div>
        </div>`;
    }).join('');
  } catch (err) {
    el.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div>Could not load meetings.<br><small>${err.message}</small></div>`;
  }
}

function renderMeetingsAnalytics(events) {
  // Total blocked minutes
  let totalMins = 0;
  events.forEach(ev => {
    if (ev.start && ev.end)
      totalMins += Math.max(0, (new Date(ev.end) - new Date(ev.start)) / 60000);
  });

  // Working day 9 AM – 6 PM = 540 min
  const now       = new Date();
  const workStart = new Date(); workStart.setHours(9,  0, 0, 0);
  const workEnd   = new Date(); workEnd.setHours(18, 0, 0, 0);
  const freeMins  = Math.max(0, 540 - totalMins);

  document.getElementById('mstat-count').textContent = events.length;
  document.getElementById('mstat-time').textContent  = fmtMins(totalMins);
  document.getElementById('mstat-free').textContent  = freeMins > 0 ? fmtMins(freeMins) : 'None';

  // Next upcoming meeting countdown
  const upcoming = events.filter(ev => ev.start && new Date(ev.start) > now);
  if (upcoming.length > 0) {
    const minsUntil = Math.round((new Date(upcoming[0].start) - now) / 60000);
    document.getElementById('mstat-next').textContent =
      minsUntil <= 0 ? 'Starting now' : `in ${fmtMins(minsUntil)}`;
    document.getElementById('mstat-next-box').style.display = 'block';
  }
  document.getElementById('meetings-stats-card').style.display = 'block';

  // Day utilization timeline bar
  const totalMs = workEnd - workStart;
  if (totalMs > 0) {
    const blocks = events
      .filter(ev => ev.start && ev.end)
      .map(ev => {
        const s = new Date(ev.start), e = new Date(ev.end);
        const left  = Math.max(0,   (s - workStart) / totalMs * 100);
        const right = Math.min(100, (e - workStart) / totalMs * 100);
        return { left, width: Math.max(0, right - left), title: ev.title || 'Meeting' };
      })
      .filter(b => b.width > 0 && b.left < 100);

    const nowPct  = ((now - workStart) / totalMs * 100).toFixed(1);
    const showNow = now >= workStart && now <= workEnd;

    document.getElementById('day-utilization').innerHTML = `
      <div class="day-bar-wrap">
        <div class="day-bar">
          ${blocks.map(b =>
            `<div class="day-block" style="left:${b.left.toFixed(1)}%;width:${b.width.toFixed(1)}%" title="${esc(b.title)}"></div>`
          ).join('')}
          ${showNow ? `<div class="day-now" style="left:${nowPct}%"></div>` : ''}
        </div>
        <div class="day-bar-labels">
          <span>9 AM</span><span>12 PM</span><span>3 PM</span><span>6 PM</span>
        </div>
      </div>`;
  }
}

// ══════════════════════════════════════════════════════════
// HEALTH
// ══════════════════════════════════════════════════════════
const RING_CIRC = 2 * Math.PI * 45;

function makeRing(id, value, maxVal, color, label, displayVal, unit) {
  const pct    = maxVal > 0 ? Math.min(1, value / maxVal) : 0;
  const offset = RING_CIRC * (1 - pct);
  return `
    <div class="ring-widget">
      <div class="ring-wrap">
        <svg class="ring-svg" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="45" class="ring-track"/>
          <circle cx="50" cy="50" r="45" class="ring-fill"
            style="stroke:${color};stroke-dasharray:${RING_CIRC.toFixed(1)};stroke-dashoffset:${RING_CIRC.toFixed(1)}"
            id="ring-${id}"/>
        </svg>
        <div class="ring-center">
          <div class="ring-value">${esc(displayVal)}</div>
          <div class="ring-unit">${esc(unit)}</div>
        </div>
      </div>
      <div class="ring-label">${esc(label)}</div>
    </div>`;
}

function animateRing(id, value, maxVal) {
  const el = document.getElementById('ring-' + id);
  if (!el) return;
  const pct = maxVal > 0 ? Math.min(1, value / maxVal) : 0;
  setTimeout(() => { el.style.strokeDashoffset = (RING_CIRC * (1 - pct)).toFixed(1); }, 100);
}

async function loadHealth(force = false) {
  if (force) await fetch('/api/cache/clear', { method: 'POST' });
  const ringsEl = document.getElementById('health-rings');
  ringsEl.innerHTML = '<div class="loading"><div class="spinner"></div>Loading health data…</div>';

  try {
    const data     = await apiFetch('/api/health');
    const today    = data.today    || {};
    const analytics = data.analytics || {};
    const patterns  = data.patterns  || [];

    const steps   = today.steps           || 0;
    const waterMl = today.water_ml        || 0;
    const sleepH  = today.sleep_hours     || 0;
    const hrAvg   = today.heart_rate_avg;
    const spo2    = today.spo2;
    const mood    = today.mood;
    const workout = today.workout;

    const hasData = steps || waterMl || sleepH || hrAvg || spo2;

    if (!hasData) {
      ringsEl.innerHTML = '<div class="empty-state"><div class="empty-icon">💪</div>No health data logged today yet.<br>Tell Atlas: "I walked 8,000 steps and drank 2 litres of water"</div>';
    } else {
      ringsEl.innerHTML =
        makeRing('steps', steps,   10000, '#3b82f6', 'Steps',      steps.toLocaleString(),       'steps') +
        makeRing('water', waterMl, 2500,  '#06b6d4', 'Water',      (waterMl/1000).toFixed(1),    'L')     +
        makeRing('sleep', sleepH,  8,     '#8b5cf6', 'Sleep',      sleepH.toFixed(1),            'hrs')   +
        (hrAvg  ? makeRing('hr',   hrAvg, 200, '#ef4444', 'Heart Rate', hrAvg, 'bpm') : '') +
        (spo2   ? makeRing('spo2', spo2,  100, '#22c55e', 'SpO₂',       spo2,  '%')   : '');

      animateRing('steps', steps,   10000);
      animateRing('water', waterMl, 2500);
      animateRing('sleep', sleepH,  8);
      if (hrAvg) animateRing('hr',   hrAvg, 200);
      if (spo2)  animateRing('spo2', spo2,  100);

      // Mood / workout badges
      if (mood || workout) {
        const badges = [];
        if (mood) {
          const moodLabels = { 1:'😔 Low', 2:'😕 Meh', 3:'😐 Okay', 4:'🙂 Good', 5:'😄 Great' };
          badges.push(`<span class="health-badge">${moodLabels[mood] || 'Mood: '+mood}</span>`);
        }
        if (workout) {
          const wType = today.workout_type || 'Workout';
          const wMins = today.workout_minutes ? ` · ${today.workout_minutes} min` : '';
          badges.push(`<span class="health-badge health-badge-green">🏋️ ${esc(wType)}${wMins}</span>`);
        }
        ringsEl.insertAdjacentHTML('afterend',
          `<div class="health-badges">${badges.join('')}</div>`);
      }
    }

    // 7-day averages grid
    const anaEl   = document.getElementById('analytics-grid');
    const anaCard = document.getElementById('analytics-card');
    if (Object.keys(analytics).length > 0) {
      const labels = {
        avg_steps: 'Avg Steps', avg_water_ml: 'Avg Water',
        avg_sleep_hours: 'Avg Sleep', avg_heart_rate: 'Avg HR',
        avg_spo2: 'Avg SpO₂', workout_frequency: 'Workouts',
        steps_trend: 'Steps', sleep_trend: 'Sleep', water_trend: 'Water',
      };
      anaEl.innerHTML = Object.entries(analytics)
        .filter(([k]) => labels[k])
        .map(([k, v]) => {
          let display = v, trendClass = '', sub = '';
          if (k === 'avg_water_ml' && typeof v === 'number') display = (v/1000).toFixed(1) + ' L';
          else if (typeof v === 'number') display = v % 1 !== 0 ? v.toFixed(1) : v.toLocaleString();
          if (typeof v === 'string') {
            if (v === 'improving') { display = '↑'; sub = 'Improving'; trendClass = 'trend-up'; }
            else if (v === 'declining') { display = '↓'; sub = 'Declining'; trendClass = 'trend-down'; }
            else if (v === 'stable')    { display = '→'; sub = 'Stable';    trendClass = 'trend-flat'; }
          }
          return `<div class="analytics-item">
            <div class="a-key">${esc(labels[k])}</div>
            <div class="a-val ${esc(trendClass)}">${esc(String(display))}${sub ? `<span class="a-trend">${esc(sub)}</span>` : ''}</div>
          </div>`;
        }).join('');
      anaCard.style.display = 'block';
    }

    // 7-day sparkline history
    loadHealthHistory();

    // Patterns
    const patEl   = document.getElementById('patterns-list');
    const patCard = document.getElementById('patterns-card');
    if (patterns.length > 0) {
      patEl.innerHTML = patterns.map(p =>
        `<div class="pattern-item"><div class="pattern-icon">⚡</div><span>${esc(p)}</span></div>`
      ).join('');
      patCard.style.display = 'block';
    }

  } catch (err) {
    document.getElementById('health-rings').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div>Could not load health data.<br><small>${err.message}</small></div>`;
  }
}

async function loadHealthHistory() {
  try {
    const raw = await apiFetch('/api/health/history');
    if (!raw || !raw.length) return;

    // API returns DESC; reverse to get oldest→newest for the chart
    const history = [...raw].reverse();

    const metrics = [
      { key: 'steps',       label: 'Steps',      max: 10000, color: '#3b82f6',
        fmt: v => v >= 1000 ? `${(v/1000).toFixed(1)}k` : String(v) },
      { key: 'sleep_hours', label: 'Sleep (h)',   max: 10,    color: '#8b5cf6',
        fmt: v => v.toFixed(1) },
      { key: 'water_ml',    label: 'Water (L)',   max: 3000,  color: '#06b6d4',
        fmt: v => (v/1000).toFixed(1) },
    ].filter(m => history.some(d => d[m.key]));

    if (!metrics.length) return;

    const card = document.getElementById('health-history-card');
    const el   = document.getElementById('health-history-bars');

    el.innerHTML = metrics.map(m => {
      const cols = history.map(d => {
        const val  = parseFloat(d[m.key]) || 0;
        const pct  = m.max > 0 ? Math.min(100, val / m.max * 100) : 0;
        const day  = d.record_date
          ? new Date(d.record_date + 'T00:00:00').toLocaleDateString([], { weekday: 'short' }).slice(0, 2)
          : '';
        const tip  = `${d.record_date}: ${m.fmt(val)}`;
        return `
          <div class="spark-col" title="${esc(tip)}">
            <div class="spark-val">${esc(m.fmt(val))}</div>
            <div class="spark-bar-outer">
              <div class="spark-bar-inner" style="height:${pct.toFixed(0)}%;background:${m.color}"></div>
            </div>
            <div class="spark-day">${esc(day)}</div>
          </div>`;
      }).join('');
      return `
        <div class="sparkline-row">
          <div class="spark-label">${esc(m.label)}</div>
          <div class="spark-bars">${cols}</div>
        </div>`;
    }).join('');

    card.style.display = 'block';
  } catch (e) {
    console.error('Health history error:', e);
  }
}

// ══════════════════════════════════════════════════════════
// NOTES
// ══════════════════════════════════════════════════════════
let _notes      = [];
let _activeNote = null;
let _activeColor = '#fff9c4';

async function loadNotes() {
  try {
    _notes = await apiFetch('/api/notes');
    renderNotesList();
    renderNotesStats(_notes);
    if (_notes.length > 0) openNote(_notes[0]);
  } catch (err) {
    document.getElementById('notes-list').innerHTML =
      `<div style="color:var(--text-dim);font-size:12px;padding:10px">Error loading notes: ${err.message}</div>`;
  }
}

function renderNotesStats(notes) {
  const el = document.getElementById('notes-stats');
  if (!el) return;
  if (!notes.length) { el.innerHTML = ''; return; }

  const totalWords = notes.reduce((acc, n) =>
    acc + ((n.content || '').trim().split(/\s+/).filter(w => w.length > 0).length), 0);

  const colorMap = {};
  notes.forEach(n => {
    const c = n.color || '#fff9c4';
    colorMap[c] = (colorMap[c] || 0) + 1;
  });

  // Most recently edited note
  const lastEdit = notes[0]?.updated_at
    ? new Date(notes[0].updated_at).toLocaleDateString([], { month: 'short', day: 'numeric' })
    : null;

  el.innerHTML = `
    <div class="notes-stat-strip">
      <span class="nstat-bold">${notes.length}</span> note${notes.length !== 1 ? 's' : ''}
      &nbsp;·&nbsp;
      <span class="nstat-bold">${totalWords.toLocaleString()}</span> words
    </div>
    <div class="notes-color-row">
      ${Object.entries(colorMap).map(([color, count]) =>
        `<div class="notes-color-chip" style="background:${esc(color)}" title="${count} note${count>1?'s':''}">${count}</div>`
      ).join('')}
    </div>
    ${lastEdit ? `<div class="notes-last-edit">Last edited ${esc(lastEdit)}</div>` : ''}`;
}

function renderNotesList() {
  const el = document.getElementById('notes-list');
  if (!_notes.length) {
    el.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:8px;text-align:center">No notes yet</div>';
    return;
  }
  el.innerHTML = _notes.map(n => `
    <div class="note-card${_activeNote && _activeNote.id === n.id ? ' active' : ''}"
         data-id="${n.id}" onclick="openNote(${n.id})"
         style="border-left:3px solid ${esc(n.color || '#fff9c4')}">
      <button class="note-del-btn" onclick="deleteNote(event,${n.id})" title="Delete">✕</button>
      <div class="note-card-title">${esc(n.title || 'Untitled')}</div>
      <div class="note-card-preview">${esc((n.content || '').substring(0, 100))}</div>
      <div class="note-card-date">${fmtDate(n.updated_at)}</div>
    </div>`).join('');
}

function openNote(noteOrId) {
  const n = typeof noteOrId === 'number' ? _notes.find(x => x.id === noteOrId) : noteOrId;
  if (!n) return;
  _activeNote  = n;
  _activeColor = n.color || '#fff9c4';
  document.getElementById('note-title').value   = n.title   || '';
  document.getElementById('note-content').value = n.content || '';
  document.getElementById('note-content').style.background = _activeColor;
  document.querySelectorAll('.color-dot').forEach(d =>
    d.classList.toggle('active', d.dataset.color === _activeColor));
  renderNotesList();
}

function newNote() {
  _activeNote = null;
  document.getElementById('note-title').value   = '';
  document.getElementById('note-content').value = '';
  document.getElementById('note-content').style.background = _activeColor;
  document.querySelectorAll('.note-card').forEach(c => c.classList.remove('active'));
}

async function saveNote() {
  const title   = document.getElementById('note-title').value.trim() || 'Untitled';
  const content = document.getElementById('note-content').value.trim();
  try {
    const res = await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: _activeNote?.id || null, title, content, color: _activeColor }),
    });
    if (!res.ok) {
      const err = await res.text();
      showToast('Save failed: ' + err, 'error');
      return;
    }
    const { id } = await res.json();
    await loadNotes();
    openNote(id);
    showToast('Note saved ✓');
  } catch (err) {
    showToast('Save failed: ' + err.message, 'error');
  }
}

async function deleteNote(e, id) {
  e.stopPropagation();
  if (!confirm('Delete this note?')) return;
  try {
    await fetch('/api/notes/' + id, { method: 'DELETE' });
    if (_activeNote && _activeNote.id === id) newNote();
    await loadNotes();
  } catch (err) {
    alert('Failed to delete: ' + err.message);
  }
}

document.querySelectorAll('.color-dot').forEach(dot => {
  dot.addEventListener('click', () => {
    _activeColor = dot.dataset.color;
    document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
    dot.classList.add('active');
    document.getElementById('note-content').style.background = _activeColor;
  });
});

document.getElementById('new-note-btn').addEventListener('click', newNote);
document.getElementById('save-note-btn').addEventListener('click', saveNote);

document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    if (document.getElementById('panel-notes')?.classList.contains('active')) saveNote();
    if (document.getElementById('panel-journal')?.classList.contains('active') &&
        typeof window._journalSave === 'function') window._journalSave();
  }
});

// ══════════════════════════════════════════════════════════
// TASKS
// ══════════════════════════════════════════════════════════
async function loadTasks() {
  document.getElementById('task-pending-list').innerHTML =
    '<div class="loading"><div class="spinner"></div>Loading tasks…</div>';
  try {
    const tasks   = await apiFetch('/api/tasks');
    const pending = tasks.filter(t => !t.done);
    const done    = tasks.filter(t =>  t.done);

    // Stats
    const todayStr  = new Date().toDateString();
    const doneToday = done.filter(t =>
      t.completed_at && new Date(t.completed_at).toDateString() === todayStr
    ).length;
    const pct = tasks.length > 0 ? Math.round(done.length / tasks.length * 100) : 0;

    if (tasks.length > 0) {
      document.getElementById('tstat-pending').textContent = pending.length;
      document.getElementById('tstat-done').textContent    = done.length;
      document.getElementById('tstat-pct').textContent     = doneToday + ' today';
      document.getElementById('task-stats-card').style.display = 'block';
    }

    // Pending badge
    const badge = document.getElementById('task-pending-count');
    if (pending.length > 0) { badge.textContent = pending.length; badge.style.display = 'inline-flex'; }
    else badge.style.display = 'none';

    // Pending list
    const pendEl = document.getElementById('task-pending-list');
    if (!pending.length) {
      pendEl.innerHTML = '<div class="empty-state"><div class="empty-icon">✅</div>All caught up! No pending tasks.</div>';
    } else {
      pendEl.innerHTML = pending.map(t => taskRow(t, false)).join('');
    }

    // Done list
    const doneCard = document.getElementById('task-done-card');
    const doneEl   = document.getElementById('task-done-list');
    if (done.length > 0) {
      doneEl.innerHTML = done.map(t => taskRow(t, true)).join('');
      doneCard.style.display = 'block';
    } else {
      doneCard.style.display = 'none';
    }
  } catch (err) {
    document.getElementById('task-pending-list').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div>Could not load tasks.<br><small>${err.message}</small></div>`;
  }
}

function taskRow(t, isDone) {
  const due = t.due_date
    ? `<span class="task-due">${esc(t.due_date)}</span>`
    : '';
  return `
    <div class="task-row${isDone ? ' task-done' : ''}" data-id="${t.id}">
      <button class="task-check" onclick="toggleTask(${t.id},${isDone ? 1 : 0})" title="${isDone ? 'Undo' : 'Mark done'}">
        ${isDone ? '✓' : ''}
      </button>
      <div class="task-body">
        <div class="task-title">${esc(t.title)}</div>
        ${due}
      </div>
      <button class="task-del" onclick="deleteTaskUI(${t.id})" title="Delete">✕</button>
    </div>`;
}

async function toggleTask(id, isDone) {
  if (isDone) {
    // undo — just delete the done flag by re-adding? No, just delete for simplicity
    await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
  } else {
    await fetch(`/api/tasks/${id}/complete`, { method: 'POST' });
  }
  loadTasks();
}

async function deleteTaskUI(id) {
  await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
  loadTasks();
}

async function addTaskFromUI() {
  const title = document.getElementById('task-input').value.trim();
  if (!title) return;
  const due = document.getElementById('task-due').value.trim() || null;
  await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, due_date: due }),
  });
  document.getElementById('task-input').value = '';
  document.getElementById('task-due').value   = '';
  loadTasks();
}

function toggleDoneList() {
  const el  = document.getElementById('task-done-list');
  const ch  = document.getElementById('task-done-chevron');
  const vis = el.style.display !== 'none';
  el.style.display = vis ? 'none' : 'block';
  ch.textContent   = vis ? '▸' : '▾';
}

// Enter key submits task
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && document.activeElement.id === 'task-input') {
    addTaskFromUI();
  }
});

// ── Whiteboard init trigger ───────────────────────────────
function initWhiteboard() {
  if (window._wbInit) window._wbInit();
}
