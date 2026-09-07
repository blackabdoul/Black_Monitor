import sqlite3
import psutil
import time
from datetime import datetime

DB_PATH = "stats.db"
COLLECTION_INTERVAL_SECONDS = 15


def init_db():
    """Create the stats table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def collect_stats():
    """Read current system stats and return them as a dict."""
    cpu = psutil.cpu_percent(interval=1)  # blocks for 1 sec to measure accurately
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()

    return {
        "cpu_percent": cpu,
        "ram_percent": ram.percent,
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024 ** 3), 2),
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "net_sent_mb": round(net.bytes_sent / (1024 ** 2), 2),
        "net_recv_mb": round(net.bytes_recv / (1024 ** 2), 2),
    }


def save_stats(stats):
    """Insert one row of stats into the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO stats (cpu_percent, ram_percent, disk_percent,
                            disk_used_gb, disk_total_gb, net_sent_mb, net_recv_mb)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            stats["cpu_percent"],
            stats["ram_percent"],
            stats["disk_percent"],
            stats["disk_used_gb"],
            stats["disk_total_gb"],
            stats["net_sent_mb"],
            stats["net_recv_mb"],
        ),
    )
    conn.commit()
    conn.close()


def main():
    init_db()
    print(f"[{datetime.now()}] Collector started — logging every {COLLECTION_INTERVAL_SECONDS}s")

    while True:
        stats = collect_stats()
        save_stats(stats)
        print(f"[{datetime.now()}] CPU: {stats['cpu_percent']}%  "
              f"RAM: {stats['ram_percent']}%  "
              f"Disk: {stats['disk_percent']}%")
        time.sleep(COLLECTION_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()