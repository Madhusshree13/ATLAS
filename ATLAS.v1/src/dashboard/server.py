import os
import json
import queue
import time
import threading

from flask import Flask, Response, render_template, jsonify, request

_HERE = os.path.dirname(__file__)

app = Flask(
    __name__,
    template_folder=os.path.join(_HERE, "templates"),
    static_folder=os.path.join(_HERE, "static"),
)
app.config["SECRET_KEY"] = "atlas-local-dashboard"

_ctx   = {}
_cache = {}
_CACHE_TTL = 300

# SSE broadcast — one queue per connected tab
_listeners      = []
_listeners_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _cached(key, loader):
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < _CACHE_TTL:
        return entry["data"]
    try:
        data = loader()
    except Exception as exc:
        print(f"[Dashboard] cache error [{key}]: {exc}")
        data = [] if key != "health" else {"today": {}, "analytics": {}, "patterns": []}
    _cache[key] = {"data": data, "ts": time.time()}
    return data


def _safe_dict(d: dict) -> dict:
    out = {}
    for k, v in d.items():
        if isinstance(v, (str, int, float, bool, type(None))):
            out[k] = v
        else:
            out[k] = str(v)
    return out


def _broadcast(cmd: str):
    """Push a command string to every open dashboard tab."""
    with _listeners_lock:
        for q in list(_listeners):
            try:
                q.put_nowait(cmd)
            except queue.Full:
                pass


# ---------------------------------------------------------------------------
# Public API — called from main.py without HTTP
# ---------------------------------------------------------------------------

def send_command(cmd: str):
    """Called directly by the voice worker to push a command to the browser."""
    _broadcast(cmd)


def clear_section(key: str):
    """Invalidate one cache entry so the next API call re-fetches live data."""
    _cache.pop(key, None)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/world")
def world():
    return render_template("world.html")


# ---------------------------------------------------------------------------
# SSE  —  /api/events
# ---------------------------------------------------------------------------

@app.route("/api/events")
def sse_events():
    q = queue.Queue(maxsize=10)
    with _listeners_lock:
        _listeners.append(q)

    def stream():
        try:
            while True:
                try:
                    cmd = q.get(timeout=25)
                    yield f"data: {json.dumps({'cmd': cmd})}\n\n"
                    if cmd == "close":
                        break
                except queue.Empty:
                    yield "data: {\"cmd\":\"ping\"}\n\n"   # keep-alive
        finally:
            with _listeners_lock:
                if q in _listeners:
                    _listeners.remove(q)

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Data APIs
# ---------------------------------------------------------------------------

@app.route("/api/emails")
def api_emails():
    gmail = _ctx.get("gmail")
    if not gmail:
        return jsonify([])
    emails = _cached("emails", lambda: gmail.fetch_today_emails(max_count=20))
    return jsonify([_safe_dict(e) for e in emails])


@app.route("/api/meetings")
def api_meetings():
    gcal = _ctx.get("gcal")
    if not gcal:
        return jsonify([])
    events = _cached("meetings", lambda: gcal.get_today_events())
    return jsonify([_safe_dict(e) for e in events])


@app.route("/api/health")
def api_health():
    tracker = _ctx.get("health")
    if not tracker:
        return jsonify({"today": {}, "analytics": {}, "patterns": []})
    data = _cached("health", lambda: {
        "today":     _safe_dict(tracker.get_entry()),
        "analytics": tracker.compute_analytics(7),
        "patterns":  tracker.find_patterns(30),
    })
    return jsonify(data)


@app.route("/api/health/history")
def api_health_history():
    tracker = _ctx.get("health")
    if not tracker:
        return jsonify([])
    rows = tracker.get_range(days=7)
    return jsonify([_safe_dict(dict(r)) for r in rows])


# --- Tasks ---

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    tasks = _ctx.get("tasks")
    if not tasks:
        return jsonify([])
    return jsonify(tasks.get_all())


@app.route("/api/tasks", methods=["POST"])
def add_task():
    tasks = _ctx.get("tasks")
    if not tasks:
        return jsonify({"error": "tasks not initialised"}), 503
    body = request.json or {}
    task_id = tasks.add_task(
        body.get("title", "Untitled"),
        body.get("due_date"),
        body.get("priority", "normal"),
    )
    _broadcast("refresh:tasks")
    return jsonify({"id": task_id})


@app.route("/api/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    _ctx["tasks"].complete_task(task_id)
    _broadcast("refresh:tasks")
    return jsonify({"ok": True})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    _ctx["tasks"].delete_task(task_id)
    _broadcast("refresh:tasks")
    return jsonify({"ok": True})


# --- Notes ---

@app.route("/api/notes", methods=["GET"])
def get_notes():
    return jsonify(_ctx["notes"].get_all_notes())


@app.route("/api/notes", methods=["POST"])
def save_note():
    body = request.json or {}
    nid = _ctx["notes"].save_note(
        body.get("id"),
        body.get("title", "Untitled"),
        body.get("content", ""),
        body.get("color", "#fff9c4"),
    )
    return jsonify({"id": nid})


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    _ctx["notes"].delete_note(note_id)
    return jsonify({"ok": True})


# --- Whiteboards ---

@app.route("/api/whiteboards", methods=["GET"])
def list_whiteboards():
    return jsonify(_ctx["notes"].get_all_whiteboards())


@app.route("/api/whiteboards", methods=["POST"])
def create_whiteboard():
    body = request.json or {}
    board = _ctx["notes"].create_whiteboard(body.get("name", "Untitled Board"))
    return jsonify(board)


@app.route("/api/whiteboards/<int:board_id>", methods=["GET"])
def get_whiteboard(board_id):
    board = _ctx["notes"].get_whiteboard_canvas(board_id)
    if not board:
        return jsonify({"error": "not found"}), 404
    return jsonify(board)


@app.route("/api/whiteboards/<int:board_id>", methods=["POST"])
def save_whiteboard(board_id):
    body = request.json or {}
    _ctx["notes"].save_whiteboard_canvas(board_id, body.get("canvas", '{"objects":[]}'))
    return jsonify({"ok": True})


@app.route("/api/whiteboards/<int:board_id>/rename", methods=["POST"])
def rename_whiteboard(board_id):
    body = request.json or {}
    _ctx["notes"].rename_whiteboard(board_id, body.get("name", "Untitled Board"))
    return jsonify({"ok": True})


@app.route("/api/whiteboards/<int:board_id>", methods=["DELETE"])
def delete_whiteboard(board_id):
    _ctx["notes"].delete_whiteboard(board_id)
    return jsonify({"ok": True})


@app.route("/api/cache/clear", methods=["POST"])
def clear_cache():
    _cache.clear()
    return jsonify({"ok": True})


# --- Habits ---

@app.route("/api/habits", methods=["GET"])
def get_habits():
    habits = _ctx.get("habits")
    if not habits:
        return jsonify({"today": [], "streaks": {}, "history": {}, "dates": []})
    days    = request.args.get("days", 30, type=int)
    today   = habits.get_today()
    streaks = habits.get_streaks()
    hist, dates = habits.get_week_history(days)
    return jsonify({"today": today, "streaks": streaks, "history": hist, "dates": dates})


@app.route("/api/habits", methods=["POST"])
def add_habit():
    body = request.json or {}
    _ctx["habits"].add_habit(body.get("name", "New Habit"))
    return jsonify({"ok": True})


@app.route("/api/habits/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id):
    _ctx["habits"].delete_habit(habit_id)
    return jsonify({"ok": True})


@app.route("/api/habits/<int:habit_id>/log", methods=["POST"])
def log_habit(habit_id):
    body = request.json or {}
    _ctx["habits"].log(habit_id, body.get("date"))
    return jsonify({"ok": True})


@app.route("/api/habits/<int:habit_id>/log", methods=["DELETE"])
def unlog_habit(habit_id):
    body = request.json or {}
    _ctx["habits"].unlog(habit_id, body.get("date"))
    return jsonify({"ok": True})


# --- Finance ---

@app.route("/api/finance", methods=["GET"])
def get_finance():
    fin = _ctx.get("finance")
    if not fin:
        return jsonify({"transactions": [], "summary": {}})
    year  = request.args.get("year",  type=int)
    month = request.args.get("month", type=int)
    return jsonify({
        "transactions": fin.get_month(year, month),
        "summary":      fin.get_summary(year, month),
        "expense_cats": fin.EXPENSE_CATS,
        "income_cats":  fin.INCOME_CATS,
    })


@app.route("/api/finance", methods=["POST"])
def add_finance():
    body = request.json or {}
    tx_id = _ctx["finance"].add(
        body.get("type", "expense"),
        body.get("amount", 0),
        body.get("category", "Other"),
        body.get("description", ""),
        body.get("date"),
    )
    return jsonify({"id": tx_id})


@app.route("/api/finance/<int:tx_id>", methods=["DELETE"])
def delete_finance(tx_id):
    _ctx["finance"].delete(tx_id)
    return jsonify({"ok": True})


# --- Journal ---

@app.route("/api/journal", methods=["GET"])
def get_journal():
    jrn = _ctx.get("journal")
    if not jrn:
        return jsonify({"entry_date": "", "content": "", "mood": None})
    d = request.args.get("date")
    return jsonify(jrn.get(d))


@app.route("/api/journal", methods=["POST"])
def save_journal():
    body = request.json or {}
    _ctx["journal"].save(
        body.get("content", ""),
        body.get("mood"),
        body.get("date"),
    )
    return jsonify({"ok": True})


@app.route("/api/journal/recent", methods=["GET"])
def recent_journal():
    jrn = _ctx.get("journal")
    if not jrn:
        return jsonify([])
    return jsonify(jrn.recent(14))


@app.route("/api/journal/search", methods=["GET"])
def search_journal():
    q = request.args.get("q", "")
    if not q:
        return jsonify([])
    return jsonify(_ctx["journal"].search(q))


# --- System Monitor ---

@app.route("/api/system", methods=["GET"])
def get_system():
    try:
        import psutil
        cpu  = psutil.cpu_percent(interval=0.2)
        mem  = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net  = psutil.net_io_counters()
        return jsonify({
            "cpu_percent":    round(cpu, 1),
            "ram_percent":    round(mem.percent, 1),
            "ram_used_gb":    round(mem.used  / 1e9, 2),
            "ram_total_gb":   round(mem.total / 1e9, 2),
            "disk_percent":   round(disk.percent, 1),
            "disk_used_gb":   round(disk.used  / 1e9, 1),
            "disk_total_gb":  round(disk.total / 1e9, 1),
            "net_sent_mb":    round(net.bytes_sent / 1e6, 1),
            "net_recv_mb":    round(net.bytes_recv / 1e6, 1),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Calendar ---

@app.route("/api/calendar", methods=["GET"])
def get_calendar():
    gcal = _ctx.get("gcal")
    if not gcal:
        return jsonify([])
    import calendar as cal_mod
    from datetime import datetime
    now   = datetime.now()
    year  = request.args.get("year",  default=now.year,  type=int)
    month = request.args.get("month", default=now.month, type=int)
    last  = cal_mod.monthrange(year, month)[1]
    try:
        tz    = gcal._tz()
        start = datetime(year, month, 1,    0,  0,  0, tzinfo=tz)
        end   = datetime(year, month, last, 23, 59, 59, tzinfo=tz)
        events = gcal.get_events_in_range(start, end)
        return jsonify([_safe_dict(e) for e in events])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Start
# ---------------------------------------------------------------------------

def start_server(ctx_dict: dict, port: int = 7000):
    global _ctx
    _ctx = ctx_dict
    threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1", port=port,
            debug=False, use_reloader=False, threaded=True,
        ),
        daemon=True,
    ).start()
    print(f"[Atlas Dashboard] http://127.0.0.1:{port}")
