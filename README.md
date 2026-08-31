# Fleet Device Telemetry Simulator

Real device-fleet operators (think Starlink-style ground terminals) manage thousands of units that each emit a steady stream of status and telemetry — signal strength, throughput, temperature, uptime — every few seconds. Before anyone can build an ops dashboard, that data has to be generated, persisted, and made queryable. In this project you build a Python simulator that spins up thousands of devices across regions and emits realistic telemetry ticks, then bulk-load that telemetry into PostgreSQL using efficient insert techniques instead of one-row-at-a-time. You then write the real fleet-health queries an ops team lives on: how many devices are online right now, a per-region rollup, which devices have gone stale (stopped reporting), and the latest reading per device that a dashboard list needs. By the end you have a continuously running data substrate — the exact storage-and-query layer that the next rung's ops-console API will read from and the capstone React dashboard will render.

Built step-by-step with [KhwajaLabs Build](https://khwajalabs.com).

## Stack
- Python
- PostgreSQL
- psycopg
- SQL
