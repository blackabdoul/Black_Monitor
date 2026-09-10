CREATE TABLE IF NOT EXISTS stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_percent REAL,
    ram_percent REAL,
    disk_percent REAL,
    disk_used_gb REAL,
    disk_total_gb REAL,
    net_sent_mb REAL,
    net_recv_mb REAL,
    net_sent_mbps REAL,
    net_recv_mbps REAL,
    battery_percent REAL,
    battery_plugged INTEGER,
    cpu_temp_c REAL
);