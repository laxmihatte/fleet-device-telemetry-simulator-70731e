# run_live.py
# Keep the data ALIVE. Instead of one tick, emit a tick every `interval`
# seconds forever, so the database always reflects a fleet reporting in real
# time. This is what makes the eventual dashboard feel live.
import argparse
import time
from datetime import datetime, timezone
from db import get_connection
from simulator import tick, insert_tick


def run_live(interval_seconds):
    """Emit and store one tick every `interval_seconds`, forever."""
    print(f"Starting live simulation. A tick every {interval_seconds}s. Ctrl+C to stop.")
    # One connection, reused across every tick — opening a fresh connection each
    # loop would waste time and connection slots.
    with get_connection() as conn:
        while True:
            started = time.monotonic()      # a steady clock for measuring work
            readings = tick()               # generate a reading per device
            insert_tick(conn, readings)     # bulk-load them (COPY + one commit)
            now = datetime.now(timezone.utc).strftime("%H:%M:%S")
            print(f"[{now}] wrote {len(readings)} readings")
            # Sleep for the remainder of the interval, subtracting the time the
            # tick already took, so ticks land on a steady cadence.
            elapsed = time.monotonic() - started
            time.sleep(max(0, interval_seconds - elapsed))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=10, help="seconds between ticks")
    args = parser.parse_args()
    try:
        run_live(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
