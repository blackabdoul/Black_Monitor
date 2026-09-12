# Phase 2 — Flask API

## Goal
Expose the data collected in Phase 1 over HTTP, so it can be consumed
by a browser-based dashboard (built in Phase 3) or any other client
on the network.

## Structure Added

Black_Monitor/<br>
├── app.py<br>
└── templates/<br>
  └── index.html

Flask's convention of looking for HTML files inside a `templates/`
folder (relative to `app.py`) is used as-is — no custom configuration
needed.

## `app.py` — Design

### Database Access

A shared `get_db_connection()` helper opens a SQLite connection and
sets `row_factory = sqlite3.Row`, which allows query results to be
accessed by column name (`row["cpu_percent"]`) rather than only by
tuple position. This is what allows a clean `dict(row)` conversion
into JSON-ready data in each route.

### Routes

- **`GET /`** — renders `templates/index.html`, currently a
  placeholder page confirming the server and API are reachable.
- **`GET /api/stats/latest`** — returns the single most recent row
  from the `stats` table as JSON (`ORDER BY id DESC LIMIT 1`).
  Returns a `404` with an error message if the table is empty.
- **`GET /api/stats/history`** — returns every row from the last hour
  (`WHERE timestamp >= datetime('now', '-10 minutes')`), ordered oldest
  to newest, as a JSON array — the shape a future chart will consume.

### Networking

The dev server is started with `host="0.0.0.0"`, allowing connections
from any device on the local network rather than only the server
itself — required to view the dashboard from a phone or another
computer. `debug=True` is used during development for auto-reload and
detailed error pages; this will be disabled for the production setup
in Phase 4.

## Verification

Ran both the collector and Flask app simultaneously, in separate
terminal sessions:
```bash
python3 collector.py     # terminal 1
python3 app.py           # terminal 2
```

Tested the API directly from the server:
```bash
curl http://localhost:5000/api/stats/latest
```
Returned a live JSON object matching the most recent database row.

Tested from a separate device (phone) on the same WiFi network:

http://<server-ip>:5000/
http://<server-ip>:5000/api/stats/history

Both loaded successfully, confirming the server is reachable across
the local network, not just from itself.

## Outcome

The server now exposes its collected stats over HTTP as JSON, via two
endpoints suited to a live dashboard: one for "right now," one for
recent history. This is the data layer the frontend will build on.
