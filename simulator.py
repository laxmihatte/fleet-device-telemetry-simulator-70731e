# simulator.py (extended) — now it can WRITE a tick, not just generate it.
import argparse
import random
from datetime import datetime, timezone
from db import get_connection

# ... reading_for(), all_device_ids(), and tick() from the previous step
# remain unchanged above this point. We add the insert path below.

# The columns we write, in order. Kept in one place so the COPY and the tuple
# shape from reading_for() can never drift apart.
TELEMETRY_COLUMNS = ("device_id", "ts", "status", "signal_strength", "throughput", "temp", "uptime")


def insert_tick(conn, readings):
    """Bulk-load a list of telemetry tuples using Postgres COPY.

    Why COPY and not a loop of INSERTs? Inserting one row at a time means one
    network round trip and one statement parse PER ROW. For 5,000 devices every
    few seconds that's thousands of round trips — your simulator would fall
    behind the clock. COPY streams ALL the rows to Postgres in a single bulk
    operation: dramatically less overhead, often 10-100x faster.
    """
    with conn.cursor() as cur:
        # cursor.copy() opens a high-speed bulk channel. We name the target
        # table and columns, then write each row tuple into the stream.
        with cur.copy(
            "COPY telemetry (device_id, ts, status, signal_strength, throughput, temp, uptime) FROM STDIN"
        ) as copy:
            for row in readings:
                copy.write_row(row)
    # Commit once for the whole tick. Committing per row would add a disk flush
    # for every single insert, throwing away most of COPY's speed advantage.
    conn.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="emit one tick")
    parser.add_argument("--write", action="store_true", help="write the tick to Postgres")
    args = parser.parse_args()
    if args.once:
        readings = tick()
        if args.write:
            with get_connection() as conn:
                insert_tick(conn, readings)
            print(f"Wrote {len(readings)} readings to Postgres.")
        else:
            print(f"Generated {len(readings)} readings. Sample: {readings[0]}")
