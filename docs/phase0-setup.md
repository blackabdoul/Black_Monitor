# Phase 0 — Server Setup

## Goal
Prepare the hardware and operating system foundation for Black_Monitor —
a self-hosted server monitoring dashboard, built as a CS50 final project.

## Hardware

- **Machine:** HP 250 G8
- **CPU:** Intel i3, 10th generation
- **RAM:** 8GB DDR4
- **Storage:** 1TB HDD

## Why Ubuntu Server (not Desktop)

Ubuntu Server ships without a GUI or desktop environment, which matters
significantly on 8GB of RAM — a desktop environment alone can consume
1.5–2GB just idling, before any actual services run. Server edition
keeps nearly all available RAM free for the collector script, the
Flask app, and whatever other services eventually run on this machine.

Ubuntu specifically (over Debian, Fedora Server, etc.) was chosen for
its large community and documentation base, which matters for a first
self-hosted server build — most errors encountered have already been
asked and answered elsewhere.

## Installation Steps

1. Downloaded the Ubuntu Server 24.04 LTS ISO from ubuntu.com
2. Prepared a bootable USB using **Ventoy** — installed once, then the
   ISO was simply copied onto the drive (no reflashing needed for
   future ISOs)
3. Booted the HP 250 G8 from USB via the F9 boot-menu key
4. Ran through the Ubuntu Server installer:
   - Language: English
   - Keyboard layout: auto-detected
   - Network: connected via [Ethernet/WiFi — fill in which was used]
     and received an IP automatically via DHCP
   - Storage: used the entire 1TB HDD with the guided LVM setup
   - Created a user profile and set the server's hostname
   - **Enabled OpenSSH server during install** — this was the key
     step that avoids ever needing a monitor/keyboard on this machine
     again after setup
   - Skipped Ubuntu Pro and featured server snaps (Docker, etc. will
     be installed manually later, only if actually needed)
5. Rebooted, removed the USB drive
6. Confirmed successful boot into a text-based login prompt (expected
   — no GUI is correct behavior for a server install)

## Verification

Confirmed SSH was active on the server:
```bash
sudo systemctl status ssh
```

Found the server's local IP address:
```bash
ip addr show
```

Successfully connected from the main development machine:
```bash
ssh <username>@<server-ip>
```

## Outcome

The HP 250 G8 now boots headless into Ubuntu Server and is reachable
over SSH from any other device on the home network. No monitor or
keyboard is required going forward — all further development happens
remotely via SSH / VS Code Remote-SSH.