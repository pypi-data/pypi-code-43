import os

TPTP_ROOT = os.environ.get("TPTP_ROOT", "")

DBMS = os.environ.get("GAVEL_DBMS", "postgresql")

DB_CONNECTION = dict(
    user=os.environ.get("GAVEL_DB_USER", "postgres"),
    password=os.environ.get("GAVEL_DB_PASSWORD", "postgres"),
    host=os.environ.get("GAVEL_DB_HOST", "localhost"),
    port=os.environ.get("GABEL_DB_PORT", "5432"),
    database=os.environ.get("GAVEL_DB_NAME", "gavel"),
)

HETS_HOST = os.environ.get("HETS_HOST", "localhost")
HETS_PORT = os.environ.get("HETS_PORT", 8000)
