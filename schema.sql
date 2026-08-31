-- schema.sql
-- The storage layer. Two tables: the roster, and the firehose.

-- Drop on re-run so this file is safe to apply repeatedly during development.
DROP TABLE IF EXISTS telemetry;
DROP TABLE IF EXISTS devices;

-- The ROSTER. One row per physical device. Changes rarely.
CREATE TABLE devices (
    -- A stable string id like 'DEV-000042'. We assign it ourselves so the
    -- simulator and queries can talk about a device without a DB round-trip.
    id            TEXT PRIMARY KEY,
    -- Where the device physically is. Used for per-region health rollups.
    region        TEXT NOT NULL,
    -- Which hardware generation, e.g. 'v1', 'v2'. Older revs degrade more.
    hardware_rev  TEXT NOT NULL,
    -- When the device came online for the first time. Defaults to "now".
    registered_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- The TELEMETRY stream. One row per device per tick. Grows forever.
CREATE TABLE telemetry (
    -- A surrogate auto-incrementing id. We never assign it; Postgres does.
    id              BIGSERIAL PRIMARY KEY,
    -- Which device reported. REFERENCES ties it back to the roster so you
    -- can never insert telemetry for a device that doesn't exist.
    device_id       TEXT NOT NULL REFERENCES devices(id),
    -- The instant this reading describes. The "time" axis of the time-series.
    ts              TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- The device's reported state. We constrain it to three known values so a
    -- typo like 'onlin' is rejected at write time instead of corrupting queries.
    status          TEXT NOT NULL CHECK (status IN ('online', 'offline', 'degraded')),
    -- Radio signal quality in dB. Higher is better. Offline devices report 0.
    signal_strength DOUBLE PRECISION NOT NULL,
    -- Data flowing through the device, in megabits/sec.
    throughput      DOUBLE PRECISION NOT NULL,
    -- Operating temperature in Celsius. Runs hot when degraded.
    temp            DOUBLE PRECISION NOT NULL,
    -- Seconds the device has been continuously up. Resets to 0 after an outage.
    uptime          INTEGER NOT NULL
);
