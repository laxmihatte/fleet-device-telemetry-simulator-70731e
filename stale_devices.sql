-- stale_devices.sql
-- A device that reports 'offline' told you it's down. But the scarier case is
-- a device that says NOTHING AT ALL — its last reading is minutes old and then
-- silence. That's a "stale" device, and stale usually means truly down (power
-- cut, network lost) — it can't even send an 'offline' packet.

-- Find every device whose most recent reading is older than 5 minutes.
SELECT d.id,
       d.region,
       MAX(t.ts) AS last_seen,
       now() - MAX(t.ts) AS silent_for
FROM devices d
JOIN telemetry t ON t.device_id = d.id
GROUP BY d.id, d.region
-- HAVING filters the GROUPED rows: keep only devices whose newest reading is
-- more than 5 minutes ago. INTERVAL '5 minutes' is real Postgres time math.
HAVING MAX(t.ts) < now() - INTERVAL '5 minutes'
ORDER BY last_seen ASC;  -- the most-silent devices first
-- last_seen is each device's freshest timestamp; silent_for is how long it has
-- been quiet. An ops console would flag every row here as "needs attention."
