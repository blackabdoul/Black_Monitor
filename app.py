from flask import Flask, jsonify, render_template
import sqlite3
import psutil
import time

app = Flask(__name__)
DB_PATH = "stats.db"

# Keeps Process objects alive between requests so cpu_percent()
# can measure real deltas instead of always returning 0.0
_process_objects = {}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def format_uptime(seconds):
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{days}d {hours}h {minutes}m"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats/latest")
def latest_stats():
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM stats ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "no data yet"}), 404

    data = dict(row)
    uptime_seconds = time.time() - psutil.boot_time()
    data["uptime_seconds"] = uptime_seconds
    data["uptime_formatted"] = format_uptime(uptime_seconds)

    return jsonify(data)


@app.route("/api/stats/history")
def stats_history():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT * FROM stats
        WHERE timestamp >= datetime('now', '-10 minutes')
        ORDER BY timestamp ASC
        """
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/processes")
def processes():
    current_pids = set()

    for proc in psutil.process_iter(["pid"]):
        pid = proc.info["pid"]
        current_pids.add(pid)
        if pid not in _process_objects:
            try:
                p = psutil.Process(pid)
                p.cpu_percent(interval=None)  # prime — first call is always 0.0
                _process_objects[pid] = p
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    # Drop tracked processes that no longer exist
    for pid in list(_process_objects.keys()):
        if pid not in current_pids:
            del _process_objects[pid]

    results = []
    for pid, p in _process_objects.items():
        try:
            results.append({
                "pid": pid,
                "name": p.name(),
                "cpu_percent": round(p.cpu_percent(interval=None), 1),
                "memory_percent": round(p.memory_percent(), 1),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    results.sort(key=lambda x: x["cpu_percent"], reverse=True)
    return jsonify(results[:8])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)