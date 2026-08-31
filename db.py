# db.py
# A tiny helper so every other file gets a Postgres connection the same way.
import os
import psycopg  # the modern PostgreSQL driver for Python (psycopg 3)


def get_connection():
    """Open a connection to Postgres using the DATABASE_URL env var.

    DATABASE_URL looks like:
        postgresql://user:password@localhost:5432/fleet
    Keeping the credentials in an environment variable (not in code) means we
    never hardcode a password into a file that gets committed to git.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        # Fail with a clear message instead of a confusing driver error.
        raise RuntimeError(
            "DATABASE_URL is not set. Example:\n"
            "  export DATABASE_URL=postgresql://localhost:5432/fleet"
        )
    # psycopg.connect returns a live connection object. autocommit=False (the
    # default) means changes are batched until we call conn.commit() — important
    # for bulk inserts later, where committing once is far faster than per-row.
    return psycopg.connect(url)


if __name__ == "__main__":
    # Running `python db.py` directly does a quick smoke test: connect, ask
    # Postgres what tables exist, and print them. If this prints 'devices' and
    # 'telemetry', your schema is loaded and your connection works.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            tables = [row[0] for row in cur.fetchall()]
            print("Connected. Tables:", tables)
