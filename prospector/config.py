"""Configuration values for the prospector project."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
LEADS_FILE = DATA_DIR / "leads.csv"
DB_FILE = DATA_DIR / "prospector.db"


def ensure_directories() -> None:
    """Create required directories if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


ensure_directories()
