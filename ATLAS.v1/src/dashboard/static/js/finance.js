/* finance.js — Finance tracker logic */

let _finType = 'expense';
let _finCats = { expense: [], income: [] };

async function loadFinance() {
  document.getElementById('fin-list').innerHTML =
    '<div class="loading"><div class="spinner"></div>Loading…</div>';
  try {
    const now  = new Date();
    const data = await fetch(`/api/finance?year=${now.getFullYear()}&month=${now.getMonth()+1}`)
      .then(r => r.json());

    _finCats.expense = data.expense_cats || [];
    _finCats.income  = data.income_cats  || [];
    updateFinCategorySelect();

    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    document.getElementById('fin-month-label').textContent =
      `— ${months[now.getMonth()]} ${now.getFullYear()}`;

    renderFinSummary(data.summary || {});
    renderFinCategories(data.summary?.by_category || {});
    renderFinList(data.transactions || []);
  } catch (e) {
    document.getElementById('fin-list').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div>${e.message}</div>`;
  }
}

function renderFinSummary(s) {
  if (!s.income && !s.expense) return;
  const fmt = n => '₹' + Number(n || 0).toLocaleString('en-IN', {maximumFractionDigits: 0});
  document.getElementById('fstat-income').textContent  = fmt(s.income);
  document.getElementById('fstat-expense').textContent = fmt(s.expense);
  const bal = document.getElementById('fstat-balance');
  bal.textContent  = fmt(s.balance);
  bal.className    = 'stat-num ' + ((s.balance || 0) >= 0 ? 'trend-up' : 'trend-down');
  document.getElementById('fin-summary-card').style.display = 'block';
}

function renderFinCategories(byCat) {
  const cats = Object.entries(byCat);
  if (!cats.length) return;
  const max = cats[0]?.[1] || 1;
  const el  = document.getElementById('fin-cats-list');
  el.innerHTML = cats.map(([cat, amt]) => `
    <div class="sender-row">
      <div class="sender-name">${esc(cat)}</div>
      <div class="sender-bar-wrap">
        <div class="sender-bar" style="width:${(amt/max*100).toFixed(0)}%;background:var(--danger)"></div>
      </div>
      <div class="sender-count">₹${Number(amt).toLocaleString('en-IN', {maximumFractionDigits:0})}</div>
    </div>`).join('');
  document.getElementById('fin-cats-card').style.display = 'block';
}

function renderFinList(txs) {
  const el = document.getElementById('fin-list');
  if (!txs.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">💰</div>No transactions this month.</div>';
    return;
  }
  el.innerHTML = txs.map(t => {
    const sign  = t.type === 'income' ? '+' : '−';
    const color = t.type === 'income' ? 'var(--success)' : 'var(--danger)';
    const fmt   = n => '₹' + Number(n).toLocaleString('en-IN', {maximumFractionDigits: 0});
    return `
      <div class="fin-row">
        <div class="fin-row-left">
          <div class="fin-cat-badge">${esc(t.category || '—')}</div>
          <div>
            <div class="fin-desc">${esc(t.description || t.category)}</div>
            <div class="fin-date">${esc(t.tx_date)}</div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:12px">
          <div class="fin-amount" style="color:${color}">${sign} ${fmt(t.amount)}</div>
          <button class="task-del" style="opacity:1" onclick="deleteFinUI(${t.id})" title="Delete">✕</button>
        </div>
      </div>`;
  }).join('');
}

function setFinType(type, btn) {
  _finType = type;
  document.querySelectorAll('.fin-type-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  updateFinCategorySelect();
}

function updateFinCategorySelect() {
  const sel = document.getElementById('fin-category');
  const cats = _finCats[_finType] || [];
  sel.innerHTML = cats.map(c => `<option value="${esc(c)}">${esc(c)}</option>`).join('');
}

async function addFinanceUI() {
  const amount = parseFloat(document.getElementById('fin-amount').value);
  if (!amount || isNaN(amount)) return;
  const category = document.getElementById('fin-category').value;
  const desc     = document.getElementById('fin-desc').value.trim();
  await fetch('/api/finance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: _finType, amount, category, description: desc }),
  });
  document.getElementById('fin-amount').value = '';
  document.getElementById('fin-desc').value   = '';
  loadFinance();
}

async function deleteFinUI(id) {
  await fetch(`/api/finance/${id}`, { method: 'DELETE' });
  loadFinance();
}

document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.activeElement.id === 'fin-amount') addFinanceUI();
});

function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
