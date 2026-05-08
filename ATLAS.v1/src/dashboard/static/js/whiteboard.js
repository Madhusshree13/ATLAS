/* ═══════════════════════════════════════════════════════════
   whiteboard.js  —  Multi-board Fabric.js whiteboard
   Sidebar lists all boards; click to open, double-click to rename.
═══════════════════════════════════════════════════════════ */

(function () {
  if (typeof fabric === 'undefined') return;

  // ── State ──────────────────────────────────────────────
  let canvas       = null;
  let currentTool  = 'select';
  let currentColor = '#1a1a1a';
  let activeBoardId = null;
  let _boards      = [];
  let _history     = [];
  let _saveTimer   = null;

  // ── Entry point called when the Whiteboard tab is first shown ──
  window._wbInit = function () {
    if (canvas) return;
    buildCanvas();
    loadBoardsList();
  };

  // ════════════════════════════════════════════════════════
  // CANVAS SETUP
  // ════════════════════════════════════════════════════════
  function buildCanvas() {
    const wrap = document.getElementById('wb-canvas-wrap');
    const el   = document.getElementById('wb-canvas');
    el.width   = wrap.clientWidth;
    el.height  = wrap.clientHeight;

    canvas = new fabric.Canvas('wb-canvas', {
      isDrawingMode: false,
      selection: true,
      backgroundColor: '#ffffff',
    });

    canvas.freeDrawingBrush.color = currentColor;
    canvas.freeDrawingBrush.width = 4;

    canvas.on('mouse:down',      onMouseDown);
    canvas.on('object:added',    snapshot);
    canvas.on('object:modified', snapshot);
    canvas.on('object:removed',  snapshot);

    new ResizeObserver(() => {
      canvas.setWidth(wrap.clientWidth);
      canvas.setHeight(wrap.clientHeight);
      canvas.renderAll();
    }).observe(wrap);

    // Toolbar buttons
    document.querySelectorAll('[data-tool]').forEach(btn =>
      btn.addEventListener('click', () => setTool(btn.dataset.tool))
    );
    document.querySelectorAll('.wb-color').forEach(dot =>
      dot.addEventListener('click', () => setColor(dot.dataset.color, dot))
    );
    document.querySelector('.wb-color')?.classList.add('active');

    document.getElementById('wb-brush-size').addEventListener('change', e => {
      canvas.freeDrawingBrush.width = parseInt(e.target.value);
    });
    document.getElementById('wb-undo').addEventListener('click', undo);
    document.getElementById('wb-clear').addEventListener('click', () => {
      if (confirm('Clear this board?')) {
        canvas.clear();
        canvas.backgroundColor = '#ffffff';
        canvas.renderAll();
        saveCurrentBoard(true);
      }
    });
    document.getElementById('wb-save').addEventListener('click', () => saveCurrentBoard(true));
    document.getElementById('wb-new-board-btn').addEventListener('click', createBoard);

    // Board name double-click → inline rename
    document.getElementById('wb-board-name').addEventListener('dblclick', () => {
      if (activeBoardId !== null) startRenameBoard(activeBoardId);
    });

    document.addEventListener('keydown', onKey);
  }

  // ════════════════════════════════════════════════════════
  // BOARDS SIDEBAR
  // ════════════════════════════════════════════════════════
  async function loadBoardsList(selectId = null) {
    try {
      _boards = await fetch('/api/whiteboards').then(r => r.json());
      renderBoardsList();

      if (_boards.length === 0) {
        // Auto-create first board
        const board = await fetch('/api/whiteboards', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: 'Board 1' }),
        }).then(r => r.json());
        _boards = [{ id: board.id, name: board.name, updated_at: '' }];
        renderBoardsList();
        openBoard(board.id);
      } else {
        const target = selectId ?? _boards[0].id;
        openBoard(target);
      }
    } catch (err) {
      console.error('Failed to load boards:', err);
    }
  }

  function renderBoardsList() {
    const el = document.getElementById('wb-boards-list');
    if (!_boards.length) { el.innerHTML = ''; renderWbStats([]); return; }
    el.innerHTML = _boards.map(b => `
      <div class="wb-board-card${b.id === activeBoardId ? ' active' : ''}"
           data-id="${b.id}" onclick="window._wbOpenBoard(${b.id})">
        <button class="wb-board-del" onclick="window._wbDeleteBoard(event,${b.id})" title="Delete">✕</button>
        <div class="wb-board-name">${esc(b.name)}</div>
        <div class="wb-board-date">${fmtDate(b.updated_at)}</div>
      </div>
    `).join('');
    renderWbStats(_boards);
  }

  function renderWbStats(boards) {
    const el = document.getElementById('wb-stats');
    if (!el) return;
    if (!boards.length) { el.innerHTML = ''; return; }
    const lastDate = boards[0]?.updated_at
      ? new Date(boards[0].updated_at).toLocaleDateString([], { month: 'short', day: 'numeric' })
      : null;
    el.innerHTML = `
      <div class="wb-stat-strip">
        <span class="wb-stat-count">${boards.length}</span>
        board${boards.length !== 1 ? 's' : ''}
        ${lastDate ? `<div class="wb-stat-dim">Last edited ${lastDate}</div>` : ''}
      </div>`;
  }

  // Expose to inline onclick handlers
  window._wbOpenBoard   = (id) => openBoard(id);
  window._wbDeleteBoard = (e, id) => deleteBoard(e, id);

  async function openBoard(id) {
    if (id === activeBoardId) return;
    // Auto-save current board before switching
    if (activeBoardId !== null) await saveCurrentBoard(false);

    try {
      const data = await fetch(`/api/whiteboards/${id}`).then(r => r.json());
      if (!data.id) return;

      activeBoardId = id;
      document.getElementById('wb-board-name').textContent = data.name;

      canvas.clear();
      canvas.backgroundColor = '#ffffff';

      if (data.canvas_json && data.canvas_json !== '{"objects":[]}') {
        canvas.loadFromJSON(data.canvas_json, () => {
          canvas.backgroundColor = '#ffffff';
          canvas.renderAll();
          _history = [data.canvas_json];
        });
      } else {
        canvas.renderAll();
        _history = [];
      }

      renderBoardsList();
    } catch (err) {
      console.error('Failed to open board:', err);
    }
  }

  async function createBoard() {
    const name = prompt('Board name:', 'Untitled Board');
    if (!name) return;
    try {
      const board = await fetch('/api/whiteboards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      }).then(r => r.json());
      _boards.unshift({ id: board.id, name: board.name, updated_at: new Date().toISOString() });
      renderBoardsList();
      openBoard(board.id);
    } catch (err) {
      console.error('Failed to create board:', err);
    }
  }

  async function deleteBoard(e, id) {
    e.stopPropagation();
    const board = _boards.find(b => b.id === id);
    if (!confirm(`Delete "${board?.name || 'this board'}"?`)) return;
    try {
      await fetch(`/api/whiteboards/${id}`, { method: 'DELETE' });
      _boards = _boards.filter(b => b.id !== id);
      if (activeBoardId === id) {
        activeBoardId = null;
        canvas.clear();
        canvas.backgroundColor = '#ffffff';
        canvas.renderAll();
        document.getElementById('wb-board-name').textContent = '';
      }
      renderBoardsList();
      if (_boards.length > 0 && activeBoardId === null) openBoard(_boards[0].id);
    } catch (err) {
      console.error('Failed to delete board:', err);
    }
  }

  function startRenameBoard(id) {
    const card = document.querySelector(`.wb-board-card[data-id="${id}"] .wb-board-name`);
    const board = _boards.find(b => b.id === id);
    if (!card || !board) return;

    const input = document.createElement('input');
    input.className = 'wb-board-rename';
    input.value = board.name;
    card.replaceWith(input);
    input.focus();
    input.select();

    const commit = async () => {
      const newName = input.value.trim() || board.name;
      board.name = newName;
      if (activeBoardId === id) document.getElementById('wb-board-name').textContent = newName;
      renderBoardsList();
      try {
        await fetch(`/api/whiteboards/${id}/rename`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: newName }),
        });
      } catch (_) {}
    };

    input.addEventListener('blur', commit);
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); input.blur(); }
      if (e.key === 'Escape') { input.value = board.name; input.blur(); }
    });
  }

  // ════════════════════════════════════════════════════════
  // TOOLS
  // ════════════════════════════════════════════════════════
  function setTool(tool) {
    currentTool = tool;
    document.querySelectorAll('[data-tool]').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-tool="${tool}"]`)?.classList.add('active');
    canvas.isDrawingMode = (tool === 'draw');
    canvas.selection     = (tool === 'select');
    canvas.defaultCursor = tool === 'eraser' ? 'not-allowed' : 'default';
  }

  function setColor(color, dot) {
    currentColor = color;
    canvas.freeDrawingBrush.color = color;
    document.querySelectorAll('.wb-color').forEach(d => d.classList.remove('active'));
    dot?.classList.add('active');
  }

  function onMouseDown(opts) {
    const ptr = canvas.getPointer(opts.e);

    if (currentTool === 'eraser') {
      const obj = canvas.findTarget(opts.e);
      if (obj) { canvas.remove(obj); canvas.renderAll(); }
      return;
    }
    if (currentTool === 'text') {
      const tb = new fabric.Textbox('Type here…', {
        left: ptr.x, top: ptr.y,
        fontSize: 18, fontFamily: 'Inter, sans-serif',
        fill: currentColor, width: 200, editable: true,
      });
      canvas.add(tb);
      canvas.setActiveObject(tb);
      tb.enterEditing();
      canvas.renderAll();
      setTool('select');
    }
    if (currentTool === 'sticky') {
      addStickyNote(ptr.x, ptr.y);
      setTool('select');
    }
  }

  const STICKY_COLORS = ['#fff9c4', '#e3f2fd', '#e8f5e9', '#fce4ec', '#fff3e0'];
  let _stickyIdx = 0;

  function addStickyNote(x, y) {
    const fill = STICKY_COLORS[_stickyIdx++ % STICKY_COLORS.length];
    const rect = new fabric.Rect({ width: 180, height: 150, fill, rx: 6, ry: 6,
      shadow: 'rgba(0,0,0,0.12) 2px 4px 8px' });
    const text = new fabric.Textbox('Click to edit…', {
      left: 10, top: 10, width: 160, fontSize: 13,
      fontFamily: 'Inter, sans-serif', fill: '#333', editable: true });
    const group = new fabric.Group([rect, text], { left: x, top: y, subTargetCheck: true });
    group.on('mousedblclick', e => {
      if (e.subTargets?.[0] instanceof fabric.Textbox) {
        canvas.setActiveObject(e.subTargets[0]);
        e.subTargets[0].enterEditing();
      }
    });
    canvas.add(group);
    canvas.setActiveObject(group);
    canvas.renderAll();
  }

  // ════════════════════════════════════════════════════════
  // UNDO / SAVE
  // ════════════════════════════════════════════════════════
  function snapshot() {
    _history.push(JSON.stringify(canvas.toJSON()));
    if (_history.length > 50) _history.shift();
    if (activeBoardId !== null) scheduleSave();
  }

  function undo() {
    if (_history.length < 2) return;
    _history.pop();
    canvas.loadFromJSON(_history[_history.length - 1], () => {
      canvas.backgroundColor = '#ffffff';
      canvas.renderAll();
    });
  }

  function scheduleSave() {
    clearTimeout(_saveTimer);
    _saveTimer = setTimeout(() => saveCurrentBoard(false), 2000);
  }

  async function saveCurrentBoard(manual = false) {
    if (activeBoardId === null) return;
    try {
      const json = JSON.stringify(canvas.toJSON());
      await fetch(`/api/whiteboards/${activeBoardId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ canvas: json }),
      });
      // Update local updated_at
      const b = _boards.find(b => b.id === activeBoardId);
      if (b) b.updated_at = new Date().toISOString();
      renderBoardsList();

      if (manual) {
        const el = document.getElementById('wb-save-status');
        el.textContent = 'Saved ✓';
        setTimeout(() => { el.textContent = ''; }, 2000);
      }
    } catch (err) {
      console.error('Save failed:', err);
    }
  }

  // ════════════════════════════════════════════════════════
  // KEYBOARD
  // ════════════════════════════════════════════════════════
  function onKey(e) {
    if (!document.getElementById('panel-whiteboard').classList.contains('active')) return;
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

    if ((e.key === 'Delete' || e.key === 'Backspace') && !canvas.isDrawingMode) {
      e.preventDefault();
      const sel = canvas.getActiveObjects();
      if (sel.length) { canvas.remove(...sel); canvas.discardActiveObject(); canvas.renderAll(); }
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.key === 'z') { e.preventDefault(); undo(); return; }
    if ((e.ctrlKey || e.metaKey) && e.key === 's') { e.preventDefault(); saveCurrentBoard(true); return; }
    if (e.key === 'v' || e.key === 'V') setTool('select');
    if (e.key === 'd' || e.key === 'D') setTool('draw');
    if (e.key === 't' || e.key === 'T') setTool('text');
    if (e.key === 's' && !e.ctrlKey && !e.metaKey) setTool('sticky');
  }

  // ── Helpers ──────────────────────────────────────────
  function esc(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function fmtDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return isNaN(d) ? '' : d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  }

})();
