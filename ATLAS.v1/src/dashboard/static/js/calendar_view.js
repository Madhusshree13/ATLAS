/* calendar_view.js — Monthly calendar grid */

(function () {
  const MONTHS = ['January','February','March','April','May','June',
                  'July','August','September','October','November','December'];
  const DAYS   = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

  let _year, _month, _events = [];

  window.calInit = function () {
    const now = new Date();
    _year  = now.getFullYear();
    _month = now.getMonth() + 1;
    loadCal();
  };

  window.calPrev = function () {
    _month--;
    if (_month < 1) { _month = 12; _year--; }
    loadCal();
  };

  window.calNext = function () {
    _month++;
    if (_month > 12) { _month = 1; _year++; }
    loadCal();
  };

  async function loadCal() {
    document.getElementById('cal-month-label').textContent = `${MONTHS[_month-1]} ${_year}`;
    document.getElementById('cal-grid').innerHTML =
      '<div class="loading"><div class="spinner"></div>Loading…</div>';
    try {
      _events = await fetch(`/api/calendar?year=${_year}&month=${_month}`).then(r => r.json());
      if (_events.error) { _events = []; }
    } catch (_) { _events = []; }
    renderGrid();
  }

  function renderGrid() {
    const firstDay = new Date(_year, _month - 1, 1).getDay();
    const daysInMonth = new Date(_year, _month, 0).getDate();
    const today = new Date();
    const isCurrentMonth = today.getFullYear() === _year && today.getMonth() + 1 === _month;

    // Build event map: day → [events]
    const evMap = {};
    (_events || []).forEach(ev => {
      if (!ev.start) return;
      const d = new Date(ev.start);
      const key = d.getDate();
      if (!evMap[key]) evMap[key] = [];
      evMap[key].push(ev);
    });

    const grid = document.getElementById('cal-grid');
    let html = '<div class="cal-grid">';

    // Day headers
    DAYS.forEach(d => { html += `<div class="cal-day-hdr">${d}</div>`; });

    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) html += '<div class="cal-cell cal-empty"></div>';

    // Day cells
    for (let d = 1; d <= daysInMonth; d++) {
      const isToday = isCurrentMonth && d === today.getDate();
      const evs = evMap[d] || [];
      const dots = evs.slice(0, 3).map(() => '<div class="cal-dot"></div>').join('');
      const more = evs.length > 3 ? `<div class="cal-more">+${evs.length - 3}</div>` : '';
      html += `
        <div class="cal-cell${isToday ? ' cal-today' : ''}${evs.length ? ' cal-has-events' : ''}"
             onclick="showDayEvents(${d})">
          <div class="cal-num">${d}</div>
          <div class="cal-dots">${dots}${more}</div>
        </div>`;
    }
    html += '</div>';
    grid.innerHTML = html;
  }

  window.showDayEvents = function (day) {
    const evs = (_events || []).filter(ev => {
      if (!ev.start) return false;
      return new Date(ev.start).getDate() === day;
    });
    const card  = document.getElementById('cal-events-card');
    const title = document.getElementById('cal-events-title');
    const list  = document.getElementById('cal-events-list');

    title.textContent = `${MONTHS[_month-1]} ${day}`;
    if (!evs.length) {
      list.innerHTML = '<div style="color:var(--text-dim);font-size:13px;padding:8px 0">No events this day.</div>';
    } else {
      list.innerHTML = evs.map(ev => {
        const start = ev.start ? new Date(ev.start).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) : '';
        const end   = ev.end   ? new Date(ev.end  ).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) : '';
        return `<div class="cal-event-item">
          <div class="cal-event-time">${start}${end ? ' – '+end : ''}</div>
          <div class="cal-event-title">${ev.title || 'Event'}</div>
        </div>`;
      }).join('');
    }
    card.style.display = 'block';
  };
})();
