-- fleet_health.sql
-- The questions an ops team asks all day, expressed as SQL.

-- Q1: How many devices are in each status RIGHT NOW?
-- We only care about each device's MOST RECENT reading, so we first find, per
-- device, its latest timestamp, then join back to grab that row's status.
WITH latest AS (
    SELECT device_id, MAX(ts) AS max_ts
    FROM telemetry
    GROUP BY device_id
)
SELECT t.status, COUNT(*) AS device_count
FROM telemetry t
JOIN latest l
  ON t.device_id = l.device_id AND t.ts = l.max_ts
GROUP BY t.status
ORDER BY device_count DESC;
-- Reading the result: GROUP BY t.status collapses all the latest rows into one
-- row per status value, and COUNT(*) counts how many fell into each bucket.
-- You get exactly: online | 4503, degraded | 312, offline | 185.

-- Q2: Per-region health rollup. The same idea, but we also slice by region,
-- which lives on the devices table — so we join telemetry to devices.
WITH latest AS (
    SELECT device_id, MAX(ts) AS max_ts
    FROM telemetry
    GROUP BY device_id
)
SELECT d.region,
       t.status,
       COUNT(*) AS device_count
FROM telemetry t
JOIN latest l ON t.device_id = l.device_id AND t.ts = l.max_ts
JOIN devices d ON d.id = t.device_id
GROUP BY d.region, t.status
ORDER BY d.region, t.status;
-- Now GROUP BY has TWO columns, so you get one row per (region, status) pair:
-- us-west | online | 902, us-west | degraded | 61, ... per region.
