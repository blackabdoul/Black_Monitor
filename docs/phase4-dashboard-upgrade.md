# Phase 4 — Dashboard Upgrade

## Goal
Extend the working Phase 3 pipeline from a single combined chart into
a genuinely useful monitoring dashboard: richer system metrics, a
per-process breakdown, and a more considered visual design.

## Schema Changes

`schema.sql` gained five columns to support the new metrics:

```sql
net_sent_mbps REAL,
net_recv_mbps REAL,
battery_percent REAL,
battery_plugged INTEGER,
cpu_temp_c REAL
```

The existing `stats.db` was deleted and allowed to regenerate, since
no meaningful historical data existed yet worth migrating.

## Collector Changes (`collector.py`)

### Network Throughput

`psutil.net_io_counters()` only reports cumulative bytes sent/received
since boot, not a rate. Throughput is computed manually:

rate (MB/s) = (bytes_now - bytes_previous) / 1024² / seconds_elapsed


This required restructuring `collect_stats()` to accept and return
the previous network reading and timestamp, so each loop iteration
can calculate a delta against the one before it. The very first
reading, taken before the main loop starts, serves as the initial
baseline.

### Battery and Temperature

- `get_battery()` wraps `psutil.sensors_battery()`, returning
  `(None, None)` on hardware without a battery rather than raising an
  error.
- `get_cpu_temp()` wraps `psutil.sensors_temperatures()`, checking a
  few common sensor label names (`coretemp`, `cpu_thermal`, `acpitz`)
  before falling back to whatever sensor group is available. Wrapped
  in error handling since this function doesn't exist at all on some
  operating systems.

Required installing `lm-sensors` on the server for temperature
readings to be available at all.

## API Changes (`app.py`)

### Uptime

Computed live on every request to `/api/stats/latest` — not stored in
the database, since it's only ever meaningful as of "right now":

```python
uptime_seconds = time.time() - psutil.boot_time()
```

A small helper, `format_uptime()`, converts raw seconds into a
readable "Xd Yh Zm" string using floor division and modulo.

### Per-Process Endpoint (`/api/processes`)

Returns the top 8 processes by CPU usage. The key implementation
detail: `psutil`'s per-process `cpu_percent()` always returns `0.0`
on its first call for a given process, since it needs two readings
over time to compute a meaningful delta. Solved by keeping a
module-level dictionary of `psutil.Process` objects that persists
between requests — each process is "primed" once when first seen,
and every subsequent request reads a real value from the same
tracked object. Processes that exit are removed from this dictionary
to avoid an unbounded memory leak over time.

## Frontend Changes

### Layout

Replaced the single combined line chart with:
- A status strip (uptime, battery, temperature)
- Three doughnut charts (CPU/RAM/Disk) showing the current value,
  with the percentage rendered as an absolutely-positioned HTML label
  over the canvas center — avoids relying on hover/tap tooltips
- Two separate area charts (CPU history, RAM history) — kept apart
  since combining them with future metrics on one axis would get
  visually cluttered
- A network throughput chart (upload/download MB/s)
- A live-updating table of the top processes by CPU usage

### Theme Toggle

A button in the header switches a `data-theme` attribute on the
`<html>` element between `"dark"` and `"light"`, with matching CSS
variable sets for each. The chosen theme is saved via
`localStorage`, so it persists across page reloads and future visits
rather than resetting every time.

## Verification

- Confirmed network throughput values reflect actual activity by
  generating traffic (a large file download) and watching the
  upload/download chart respond
- Confirmed the per-process table shows real, non-zero CPU
  percentages after the first refresh cycle
- Toggled the theme, reloaded the page, and confirmed the previously
  selected theme persisted
- Verified battery and temperature show "N/A" gracefully rather than
  breaking, useful for confirming the fallback logic without needing
  to fake missing hardware

## Outcome

The dashboard now reports not just whether the server is busy, but
what's causing it, alongside laptop-specific context (battery,
temperature) that reflects the actual repurposed hardware this
project runs on.
