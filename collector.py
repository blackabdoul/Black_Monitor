import sqlite3
import psutil
import time
from datetime import datetime

DB_PATH = "stats.db"
COLLECTION_INTERVAL_SECONDS = 15


def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def get_battery():
    """Returns (percent, plugged) or (None, None) if no battery present."""
    battery = psutil.sensors_battery()
    if battery is None:
        return None, None
    return round(battery.percent, 1), int(battery.power_plugged)


def get_cpu_temp():
    """Returns CPU temp in Celsius, or None if unavailable."""
    try:
        temps = psutil.sensors_temperatures()
    except AttributeError:
        return None

    if not temps:
        return None

    # Different systems label the CPU sensor differently — try common names
    for label in ("coretemp", "cpu_thermal", "acpitz"):
        if label in temps and temps[label]:
            return round(temps[label][0].current, 1)

    # Fallback: just grab the first sensor found
    first_key = next(iter(temps))
    if temps[first_key]:
        return round(temps[first_key][0].current, 1)

    return None


def collect_stats(prev_net, prev_time):
    """Read current system stats. Needs the previous network reading
    to calculate throughput rates."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    now = time.time()

    elapsed = now - prev_time
    sent_rate = round(((net.bytes_sent - prev_net.bytes_sent) / (1024 ** 2)) / elapsed, 3)
    recv_rate = round(((net.bytes_recv - prev_net.bytes_recv) / (1024 ** 2)) / elapsed, 3)

    battery_percent, battery_plugged = get_battery()
    cpu_temp = get_cpu_temp()

    stats = {
        "cpu_percent": cpu,
        "ram_percent": ram.percent,
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024 ** 3), 2),
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "net_sent_mb": round(net.bytes_sent / (1024 ** 2), 2),
        "net_recv_mb": round(net.bytes_recv / (1024 ** 2), 2),
        "net_sent_mbps": sent_rate,
        "net_recv_mbps": recv_rate,
        "battery_percent": battery_percent,
        "battery_plugged": battery_plugged,
        "cpu_temp_c": cpu_temp,
    }

    return stats, net, now


def save_stats(stats):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO stats (
            cpu_percent, ram_percent, disk_percent,
            disk_used_gb, disk_total_gb, net_sent_mb, net_recv_mb,
            net_sent_mbps, net_recv_mbps,
            battery_percent, battery_plugged, cpu_temp_c
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            stats["cpu_percent"], stats["ram_percent"], stats["disk_percent"],
            stats["disk_used_gb"], stats["disk_total_gb"],
            stats["net_sent_mb"], stats["net_recv_mb"],
            stats["net_sent_mbps"], stats["net_recv_mbps"],
            stats["battery_percent"], stats["battery_plugged"], stats["cpu_temp_c"],
        ),
    )
    conn.commit()
    conn.close()


def main():
    init_db()
    print(f"[{datetime.now()}] Collector started — logging every {COLLECTION_INTERVAL_SECONDS}s")

    # Prime the network baseline before the loop starts
    prev_net = psutil.net_io_counters()
    prev_time = time.time()

    while True:
        stats, prev_net, prev_time = collect_stats(prev_net, prev_time)
        save_stats(stats)
        print(f"[{datetime.now()}] CPU: {stats['cpu_percent']}%  "
              f"RAM: {stats['ram_percent']}%  "
              f"Net: ↑{stats['net_sent_mbps']} ↓{stats['net_recv_mbps']} MB/s")
        time.sleep(COLLECTION_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()