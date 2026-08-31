# queries.py
# The query SEAM. Each fleet question is one function returning plain Python
# data (lists of dicts). The next rung's API imports these and serves them over
# HTTP — it never writes SQL itself. This file is the contract between layers.
from db import get_connection


def fleet_summary():
    """Return current status counts for the whole fleet, e.g.
    [{'status': 'online', 'count': 4503}, {'status': 'offline', 'count': 185}]."""
    sql = """
        WITH latest AS (
            SELECT device_id, MAX(ts) AS max_ts FROM telemetry GROUP BY device_id
        )
        SELECT t.status, COUNT(*) AS count
        FROM telemetry t
        JOIN latest l ON t.device_id = l.device_id AND t.ts = l.max_ts
        GROUP BY t.status ORDER BY count DESC
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return [{"status": r[0], "count": r[1]} for r in cur.fetchall()]


def region_breakdown():
    """Return per-region, per-status counts as a list of dicts."""
    sql = """
        WITH latest AS (
            SELECT device_id, MAX(ts) AS max_ts FROM telemetry GROUP BY device_id
        )
        SELECT d.region, t.status, COUNT(*) AS count
        FROM telemetry t
        JOIN latest l ON t.device_id = l.device_id AND t.ts = l.max_ts
        JOIN devices d ON d.id = t.device_id
        GROUP BY d.region, t.status ORDER BY d.region, t.status
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return [{"region": r[0], "status": r[1], "count": r[2]} for r in cur.fetchall()]


def stale_devices(minutes=5):
    """Return devices silent for longer than `minutes` — likely offline.

    Note %s is a SAFE parameter placeholder: psycopg escapes the value, so this
    can never be a SQL-injection hole even if `minutes` came from user input.
    """
    sql = """
        SELECT d.id, d.region, MAX(t.ts) AS last_seen
        FROM devices d JOIN telemetry t ON t.device_id = d.id
        GROUP BY d.id, d.region
        HAVING MAX(t.ts) < now() - (%s * INTERVAL '1 minute')
        ORDER BY last_seen ASC
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (minutes,))
            return [{"id": r[0], "region": r[1], "last_seen": r[2]} for r in cur.fetchall()]


def device_history(device_id, limit=50):
    """Return the recent telemetry readings for one device, newest first."""
    sql = """
        SELECT ts, status, signal_strength, throughput, temp, uptime
        FROM telemetry WHERE device_id = %s
        ORDER BY ts DESC LIMIT %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (device_id, limit))
            return [
                {"ts": r[0], "status": r[1], "signal_strength": r[2],
                 "throughput": r[3], "temp": r[4], "uptime": r[5]}
                for r in cur.fetchall()
            ]


if __name__ == "__main__":
    # A quick demo: print the fleet summary so you can see the module working.
    print("Fleet summary:", fleet_summary())
