/* journal.js — Daily journal editor */

(function () {
  let _currentDate = todayStr();
  let _mood = null;
  let _saveTimer = null;

  function todayStr() {
    return new Date().toISOString().slice(0, 10);
  }

  function fmtDateLabel(iso) {
    const d = new Date(iso + 'T00:00:00');
    return d.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  }

  window.journalInit = function () {
    updateDateLabel();
    loadEntry();
    loadRecent();
    setupMoodPicker();
    setupSearch();
    setupNav();

    document.getElementById('journal-save-btn').addEventListener('click', () => saveEntry(true));
    document.getElementById('journal-content').addEventListener('input', scheduleSave);
  };

  function updateDateLabel() {
    document.getElementById('journal-date-label').textContent = fmtDateLabel(_currentDate);
  }

  async function loadEntry() {
    const data = await fetch(`/api/journal?date=${_currentDate}`).then(r => r.json());
    document.getElementById('journal-content').value = data.content || '';
    setMood(data.mood);
  }

  async function loadRecent() {
    const entries = await fetch('/api/journal/recent').then(r => r.json());
    const el = document.getElementById('journal-recent');
    if (!entries.length) {
      el.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:10px 6px">No entries yet.</div>';
      return;
    }
    el.innerHTML = entries.map(e => {
      const preview = (e.content || '').slice(0, 60).replace(/\n/g, ' ');
      const active  = e.entry_date === _currentDate ? ' active' : '';
      const moodEmoji = e.mood ? ['','😔','😕','😐','🙂','😄'][e.mood] : '';
      return `<div class="journal-entry-card${active}" onclick="jumpToDate('${e.entry_date}')">
        <div class="jcard-date">${e.entry_date} ${moodEmoji}</div>
        <div class="jcard-preview">${esc(preview) || '<em style="opacity:0.5">Empty</em>'}</div>
      </div>`;
    }).join('');
  }

  window.jumpToDate = function (d) {
    _currentDate = d;
    updateDateLabel();
    loadEntry();
    // Disable future navigation
    document.getElementById('jnav-next').disabled = d >= todayStr();
  };

  function setupNav() {
    document.getElementById('jnav-prev').addEventListener('click', () => {
      const d = new Date(_currentDate + 'T00:00:00');
      d.setDate(d.getDate() - 1);
      _currentDate = d.toISOString().slice(0, 10);
      updateDateLabel();
      loadEntry();
      document.getElementById('jnav-next').disabled = false;
    });
    document.getElementById('jnav-next').addEventListener('click', () => {
      if (_currentDate >= todayStr()) return;
      const d = new Date(_currentDate + 'T00:00:00');
      d.setDate(d.getDate() + 1);
      _currentDate = d.toISOString().slice(0, 10);
      updateDateLabel();
      loadEntry();
      document.getElementById('jnav-next').disabled = _currentDate >= todayStr();
    });
    document.getElementById('jnav-next').disabled = true;
  }

  function setupMoodPicker() {
    document.querySelectorAll('.mood-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const m = parseInt(btn.dataset.mood);
        setMood(_mood === m ? null : m);
        scheduleSave();
      });
    });
  }

  function setMood(m) {
    _mood = m;
    document.querySelectorAll('.mood-btn').forEach(btn => {
      btn.classList.toggle('active', parseInt(btn.dataset.mood) === _mood);
    });
  }

  function scheduleSave() {
    clearTimeout(_saveTimer);
    _saveTimer = setTimeout(() => saveEntry(false), 1500);
  }

  async function saveEntry(showFeedback = false) {
    clearTimeout(_saveTimer);
    const content = document.getElementById('journal-content').value;
    try {
      const res = await fetch('/api/journal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, mood: _mood, date: _currentDate }),
      });
      if (!res.ok) {
        const err = await res.text();
        if (typeof showToast === 'function') showToast('Save failed: ' + err, 'error');
        return;
      }
      if (showFeedback && typeof showToast === 'function') showToast('Journal saved ✓');
      loadRecent();
    } catch (err) {
      if (typeof showToast === 'function') showToast('Save failed: ' + err.message, 'error');
    }
  }

  // Exposed so world.js Ctrl+S can call it with feedback
  window._journalSave = () => saveEntry(true);

  function setupSearch() {
    let searchTimer;
    document.getElementById('journal-search').addEventListener('input', e => {
      clearTimeout(searchTimer);
      const q = e.target.value.trim();
      if (!q) { loadRecent(); return; }
      searchTimer = setTimeout(async () => {
        const results = await fetch(`/api/journal/search?q=${encodeURIComponent(q)}`).then(r => r.json());
        const el = document.getElementById('journal-recent');
        if (!results.length) {
          el.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:10px">No matches.</div>';
          return;
        }
        el.innerHTML = results.map(e => {
          const preview = (e.content || '').slice(0, 80);
          return `<div class="journal-entry-card" onclick="jumpToDate('${e.entry_date}')">
            <div class="jcard-date">${e.entry_date}</div>
            <div class="jcard-preview">${esc(preview)}</div>
          </div>`;
        }).join('');
      }, 300);
    });
  }

  function esc(s) {
    return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }
})();
