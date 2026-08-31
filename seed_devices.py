# seed_devices.py
# Generate the roster: N devices spread across regions, then insert them.
import sys
import random
from db import get_connection

# The regions our fleet covers. A real Starlink-style fleet would have many
# more, but a handful is enough to make per-region rollups interesting.
REGIONS = ["us-west", "us-east", "eu-central", "apac", "latam"]
# Two hardware generations. v1 is older and (we'll pretend) degrades more.
HARDWARE_REVS = ["v1", "v2"]


def build_roster(n):
    """Return a list of (id, region, hardware_rev) tuples for n devices."""
    roster = []
    for i in range(n):
        # Zero-padded id like 'DEV-000042' — sorts nicely and is easy to read.
        device_id = f"DEV-{i:06d}"
        # random.choice picks one region/hardware at random for each device,
        # giving us a realistic spread across the fleet.
        region = random.choice(REGIONS)
        hardware = random.choice(HARDWARE_REVS)
        roster.append((device_id, region, hardware))
    return roster


def seed(n):
    roster = build_roster(n)
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Wipe any previous roster so re-running is clean. Deleting telemetry
            # first respects the foreign key (you can't delete a device that
            # telemetry still points at).
            cur.execute("DELETE FROM telemetry")
            cur.execute("DELETE FROM devices")
            # executemany runs the INSERT once per tuple, but in a single round
            # trip-friendly batch — far better than a Python loop of execute().
            cur.executemany(
                "INSERT INTO devices (id, region, hardware_rev) VALUES (%s, %s, %s)",
                roster,
            )
        conn.commit()  # make the inserts permanent
    print(f"Seeded {n} devices across {len(REGIONS)} regions.")


if __name__ == "__main__":
    # Read the count from the command line, defaulting to 1000.
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    seed(count)
