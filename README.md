# Black_Monitor

#### Video Demo:  <URL HERE>

#### Description:

A self-hosted server monitoring dashboard, built from scratch as a
CS50 final project — running on a repurposed HP 250 G8 laptop turned
into a home server.

![dashboard screenshot](/static/Screenshot%202026-09-13%20140854.png)
![dashboard screenshot](/static/Screenshot%202026-09-13%20140942.png)

## What It Does

Black_Monitor watches its own host machine in real time: CPU, RAM,
disk, network throughput, battery, and CPU temperature — all
collected every 15 seconds and served to a live browser dashboard
reachable from any device on the same network.

- Live CPU / RAM / Disk usage, shown as donut charts with the
  percentage rendered directly in the center
- Historical CPU and RAM usage over the last 10 minutes, as area
  charts
- Real network throughput (MB/s up/down) — calculated from raw
  cumulative byte counters, not just totals
- Uptime, battery charge, and CPU temperature
- A live-updating table of the top 8 processes by CPU usage
- Dark/light theme toggle, remembered across visits

## Why I Built This

The idea of building a hardware health-monitoring software emanated from the love I have for both hardware components and cloud infrastructures. Also I've always wanted to repurpose my former idle laptop into a self-hosted server for media, then I said why not use this long-awaited project as my cs50 final project.

## Architecture

Collector (Python, psutil) → SQLite → Flask API → Browser dashboard
(HTML/CSS/JS + Chart.js)

Two independent processes run continuously on the server:
- `collector.py` — reads system stats every 15 seconds, writes to
  `stats.db`
- `app.py` — a Flask app serving both the dashboard page and a small
  JSON API that the frontend polls

## Tech Stack

- **Backend:** Python, Flask, `psutil`
- **Database:** SQLite
- **Frontend:** HTML, CSS, vanilla JavaScript, Chart.js
- **OS:** Ubuntu Server 24.04 LTS

## Running It Yourself

```bash
git clone https://github.com/yourusername/black-monitor.git
cd black-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# In one terminal:
python3 collector.py

# In another terminal:
python3 app.py
```

Then visit `http://localhost:5000` (or `http://<your-ip>:5000` from
another device on the same network).

## Project Scope

This runs on Flask's built-in development server, without
authentication or process management (systemd, gunicorn, etc.).
That's a deliberate choice — see [`docs/phase5-review.md`](docs/phase5-review.md)
for the reasoning — since this project is meant to demonstrate the
full pipeline clearly, not serve as a production-hardened system.

## Build Log

This project was built in five documented phases:

- [Phase 0 — Server Setup](docs/phase0-setup.md)
- [Phase 1 — Data Collector](docs/phase1-collector.md)
- [Phase 2 — Flask API](docs/phase2-api.md)
- [Phase 3 — Dashboard](docs/phase3-dashboard.md)
- [Phase 4 — Dashboard Upgrade](docs/phase4-dashboard-upgrade.md)
- [Phase 5 — Code Review & Cleanup](docs/phase5-review.md)

## Hardware

- HP 250 G8, Intel i3-10th gen, 8GB RAM, 1TB HDD
- Repurposed from Windows to a headless Ubuntu Server install
