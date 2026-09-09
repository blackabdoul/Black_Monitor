# Phase 3 — Dashboard

## Goal
Build the actual browser-facing dashboard: live stat cards and a
history chart, consuming the two API endpoints built in Phase 2.

## Structure Added

habamonitor/
├── templates/
│ └── index.html (updated — real dashboard markup)
└── static/
    ├── style.css (new)
    └── script.js (new)


Flask serves anything under `static/` automatically at `/static/...`,
the same convention already relied on for `templates/`.

## Frontend Stack

Plain HTML/CSS/JS plus Chart.js, loaded from a CDN. No frontend
framework or build step — deliberate choice, since the dashboard's
job is simple: poll two endpoints, update some text, redraw one
chart. A framework like React would add tooling overhead with no
real benefit at this scale.

## `index.html`

Three stat cards (CPU, RAM, Disk — each with a distinct `id` so
JavaScript can update them independently) and a `<canvas>` element
that Chart.js draws onto. Includes the standard mobile viewport meta
tag so the dashboard scales correctly on a phone screen, not just a
desktop browser.

## `style.css`

Reuses the same dark color palette (via CSS custom properties) as the
HabaTech homepage project. Cards are laid out with `flexbox`
(`display: flex`, `flex: 1` on each card) so they share space equally
and wrap onto a second row automatically on narrow screens.

## `script.js`

Two async functions, each polling one API endpoint:

- **`updateLatest()`** — fetches `/api/stats/latest`, parses the JSON
  response, and writes the values directly into the stat cards via
  `document.getElementById(...).textContent`. Wrapped in a
  `try/catch` so a lost connection shows "Connection lost" instead of
  silently breaking.
- **`updateHistory()`** — fetches `/api/stats/history`, transforms
  the returned rows into parallel arrays (timestamps, CPU values, RAM
  values) using `.map()`, and either creates a new Chart.js line
  chart (first run) or updates an existing one in place (subsequent
  runs, tracked via a module-level `historyChart` variable).

Both functions run once immediately on page load, then repeat via
`setInterval` — `updateLatest` every 5 seconds, `updateHistory` every
30.

## Design Note — Polling Interval vs. Collection Interval

The collector writes a new row every 15 seconds, while the dashboard
polls `/api/stats/latest` every 5 seconds. This means the same value
is displayed for roughly 3 consecutive polls before new data arrives
— an expected consequence of polling faster than the underlying data
changes, not a bug. Left as-is for this phase: the extra requests are
inexpensive, and the behavior doesn't produce incorrect output, only
occasionally-unchanged output. Worth revisiting if this project were
extended toward a production system with tighter resource constraints
or many simultaneous viewers.

## Verification

Ran the collector and Flask app simultaneously and loaded the
dashboard from a phone browser on the same home network:

- Stat cards displayed live values, updating every 5 seconds
- The line chart rendered CPU and RAM history, redrawing every 30
  seconds with newly available data points
- Disabling the Flask process confirmed the "Connection lost" status
  message appears correctly rather than the page breaking silently

## Outcome

The project now has a complete, working pipeline end to end: system
stats are collected, stored, served over HTTP, and displayed live in
a browser — reachable from any device on the home network.
