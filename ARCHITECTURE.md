# Device-Fleet Telemetry — Architecture

## The problem

Imagine you operate thousands of internet terminals scattered across the globe
(Starlink-style dishes). Each one is a "device." Every few seconds each device
phones home with a small packet of numbers describing how it's doing right now:

  - is it online, offline, or degraded?
  - how strong is its signal?
  - how much data is flowing through it (throughput)?
  - how hot is it running (temperature)?
  - how long has it been up (uptime)?

That stream of numbers is called **telemetry**: machine-reported measurements
of a system's state over time. A fleet of 5,000 devices reporting every 10
seconds produces ~43 million telemetry rows a day. That's a firehose.

## Why we simulate instead of using real hardware

We don't have 5,000 real dishes. But the *shape* of the problem — high volume,
many devices, status that drifts over time — is identical whether the numbers
come from real radios or from a Python function. So we **simulate**: a program
generates believable telemetry. This lets us build and test the entire storage
and query layer before any hardware exists. (Real fleets do this too, for load
testing.)

## The three layers you build in this rung

  1. SIMULATOR (simulator.py) — creates N devices and emits a "tick" of
     telemetry per device. Most devices are online; a few degrade or drop.

  2. STORAGE (schema.sql + Postgres) — two tables. `devices` is the roster
     (who exists). `telemetry` is the time-series (what each device reported,
     when). Telemetry grows forever; devices barely changes.

  3. QUERIES (queries.py) — the questions an ops team asks: how many online,
     per-region health, which devices went dark, what each device last said.

## Where this sits in the ladder

This is rung 1 of 3. It is the DATA FOUNDATION.

  - Rung 1 (here): generate + store + query telemetry.
  - Rung 2: an ops-console API that serves these queries over HTTP.
  - Rung 3 (capstone): a React fleet-management dashboard on top of that API.

The query functions you write in `queries.py` are the exact seam the API rung
imports. Build them clean and the next rung is mostly plumbing.
