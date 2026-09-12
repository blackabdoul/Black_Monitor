# Phase 5 — Code Review & Cleanup

## Goal
Rather than adding new features, this phase was a deliberate pass
back through every existing file — `collector.py`, `app.py`,
`script.js`, `style.css`, `index.html` — checking for
inconsistencies, dead code, and unfinished scaffolding left behind
across four fast-moving phases of feature work.

## Scope Decision — No Production Infrastructure

Gunicorn (a production WSGI server), `systemd` service files, and
basic authentication were all prototyped during this phase, then
deliberately removed. This project is a CS50 final project intended
to demonstrate understanding of a full data pipeline — collection,
storage, an API, and a live frontend — not a system meant to be
exposed to real traffic or accessed by untrusted users. Keeping
production-grade scaffolding in place without it serving any real
purpose here would misrepresent the project's actual scope. The app
runs via Flask's built-in development server, started manually
alongside the collector script — simple, transparent, and honestly
scoped to what the project actually is.

## Issues Found and Fixed

### `style.css` — Duplicate and Dead Rules

- `.chart-container` was defined twice, with conflicting `height`
  values (350px, then 280px). CSS resolves this by letting the later
  rule in the file win, meaning the first definition was inert dead
  code. Removed.
- `.donut-card` was similarly defined in two separate places (layout
  properties in one, `position: relative` in another). Not
  conflicting, just poorly organized — merged into a single rule.
- `.stat-cards`, `.card`, `.card h2`, `.value`, and `.subvalue` were
  leftover from the original Phase 3 layout, fully replaced by the
  donut-based design in the dashboard upgrade. None of these class
  names appear anywhere in the current `index.html`. Removed
  entirely.

### `script.js` — Unfinished Feature Completed

A `.status-warning` CSS rule existed from early planning around
color-coded usage thresholds, but was never actually applied by any
JavaScript. Implemented it: `updateLatest()` now checks the current
CPU percentage against a named threshold constant
(`CPU_WARNING_THRESHOLD = 80`) on every refresh, adding or removing
the `status-warning` class on the CPU donut's center label
accordingly — via `classList.add()`/`classList.remove()`, so the
warning state clears itself automatically once usage drops back
below the threshold, rather than staying stuck on.

### Naming Consistency

The project is named **Black_Monitor** throughout the code
(`<title>`, page header, `localStorage` key) — confirmed consistent
across all files during this review.

### Confirmed Intentional (Not a Bug)

`/api/stats/history` filters to the last **10 minutes**
(`datetime('now', '-10 minutes')`), a deliberate tightening from the
original 1-hour window, paired with the frontend's history refresh
interval also being tightened to match the collector's 15-second
cadence. This keeps the chart's visible window tightly synced to
genuinely fresh data rather than accumulating an hour of history the
dashboard doesn't otherwise emphasize.

## Verification

Reloaded the dashboard after all CSS/JS changes and confirmed:
- Layout renders identically to before the cleanup — confirming the
  removed CSS was truly unused, not silently load-bearing
- Manually generated CPU load on the server and confirmed the CPU
  donut's label turns amber at the threshold and clears once load
  drops, without needing a page refresh

## Outcome

The codebase is smaller and more internally consistent than before
this phase, with no functional changes to what the dashboard actually
does — every remaining line of CSS and JavaScript now corresponds to
something real and currently in use.
