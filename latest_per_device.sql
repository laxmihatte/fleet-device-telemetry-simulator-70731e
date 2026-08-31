-- latest_per_device.sql
-- The query the dashboard's device LIST needs: one row per device, showing its
-- single most recent reading. This is the most-run query in the whole system,
-- so it needs an index.

-- The index. We order by device_id, then ts DESCENDING. With this, Postgres can
-- walk straight to each device's newest row instead of scanning all of history.
-- A composite index on (device_id, ts DESC) is the exact shape DISTINCT ON wants.
CREATE INDEX IF NOT EXISTS idx_telemetry_device_ts
    ON telemetry (device_id, ts DESC);

-- DISTINCT ON (device_id) keeps the FIRST row for each device_id, and the
-- ORDER BY decides which row is "first" — here, the newest ts. So we get each
-- device's latest reading in one clean pass.
SELECT DISTINCT ON (device_id)
       device_id,
       ts,
       status,
       signal_strength,
       throughput,
       temp,
       uptime
FROM telemetry
ORDER BY device_id, ts DESC;

-- Want proof the index is used? Prefix the query with EXPLAIN:
--   EXPLAIN SELECT DISTINCT ON (device_id) ... ;
-- and look for "Index Scan using idx_telemetry_device_ts" instead of a
-- "Seq Scan" (a full-table scan) in the output.
