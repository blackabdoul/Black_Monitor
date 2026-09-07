# Phase 1 — Data Collector

## Goal
Build the first real component of HabaMonitor: a Python script that
reads live system statistics from the server and stores them in a
database, laying the foundation for everything the dashboard will
later display.

## Setup

### Python Virtual Environment

Created an isolated Python environment so project dependencies stay
separate from system-wide packages:

```bash
sudo apt install python3-venv python3-pip -y
python3 -m venv venv
source venv/bin/activate
pip install psutil
```

**Issue encountered:** the initial `venv` creation failed with
`ensurepip is not available`. Ubuntu Server's minimal install doesn't
include every Python component by default. Resolved by explicitly
installing `python3-venv` before recreating the virtual environment.
This is a good example of why Server edition trims are worth knowing
about — smaller footprint, but occasionally a component needs to be
added manually that a Desktop install would have included already.

### Dependencies

`requirements.txt` at this stage:

psutil
flask

(`flask` isn't used yet — added in preparation for Phase 2.)

## Database Schema

Defined in `schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_percent REAL,
    ram_percent REAL,
    disk_percent REAL,
    disk_used_gb REAL,
    disk_total_gb REAL,
    net_sent_mb REAL,
    net_recv_mb REAL
);
```

Each row represents one snapshot in time. `id` and `timestamp` are
populated automatically by SQLite — the collector only ever supplies
the six actual metric values.

## The Collector Script (`collector.py`)

Three core functions:

- **`init_db()`** — runs `schema.sql` against the database on startup,
  using `CREATE TABLE IF NOT EXISTS` so it's always safe to re-run.
- **`collect_stats()`** — uses `psutil` to read CPU (`cpu_percent`),
  RAM (`virtual_memory`), disk (`disk_usage`), and network
  (`net_io_counters`), converting raw bytes into human-readable GB/MB,
  and returns everything as a dictionary.
- **`save_stats(stats)`** — inserts one row into the `stats` table
  using a parameterized SQL query (`?` placeholders), which safely
  handles the values without manually building SQL strings.

`main()` ties it together in an infinite loop: collect → save → print
a status line → sleep 15 seconds → repeat.

## Verification

Ran the collector directly:
```bash
python3 collector.py
```

Output confirmed readings were being taken every 15 seconds:

[2026-09-02 19:01:25] Collector started — logging every 15s
[2026-09-02 19:01:27] CPU: 1.0% RAM: 16.8% Disk: 1.0%
[2026-09-02 19:01:43] CPU: 0.3% RAM: 16.7% Disk: 1.0%
[2026-09-02 19:01:59] CPU: 0.5% RAM: 16.8% Disk: 1.0%


Stopped the script (`Ctrl+C`) and confirmed the data was actually
persisted by querying the database directly:
```bash
sqlite3 stats.db "SELECT * FROM stats;"
```

1|2026-09-02 19:01:26|1.0|16.8|1.0|8.84|914.78|54.47|589.57
2|2026-09-02 19:01:43|0.3|16.7|1.0|8.84|914.78|54.48|589.59
3|2026-09-02 19:01:59|0.5|16.8|1.0|8.84|914.78|54.5|589.61


Every row matches what was printed live, confirming the full
collect → store pipeline works end to end.

## Outcome

The server now has a working, repeatable process for capturing its
own vital statistics over time, persisted in a lightweight database
file (`stats.db`) that will power the dashboard in later phases.