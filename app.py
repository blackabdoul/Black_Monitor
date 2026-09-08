from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)
DB_PATH = "stats.db"


def get_db_connection():
    """Open a connection that returns rows as dict-like objects."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    """Serve the dashboard page (placeholder for now, built in Phase 3)."""
    return render_template("index.html")


@app.route("/api/stats/latest")
def latest_stats():
    """Return the most recent stats reading as JSON."""
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM stats ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    print(row)

    if row is None:
        return jsonify({"error": "no data yet"}), 404

    return jsonify(dict(row))


@app.route("/api/stats/history")
def stats_history():
    """Return stats from the last hour, oldest first."""
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT * FROM stats
        WHERE timestamp >= datetime('now', '-1 hour')
        ORDER BY timestamp ASC
        """
    ).fetchall()
    print(rows)

    conn.close()

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)