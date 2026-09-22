from __future__ import annotations

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[3]
PROSPECTOR_DIR = Path(os.getenv("PROSPECTOR_DIR", BASE_DIR / "prospector"))
DATA_DIR = PROSPECTOR_DIR / "data"
DB_PATH = DATA_DIR / "prospector.db"
LEADS_PATH = DATA_DIR / "leads.csv"

os.makedirs(DATA_DIR, exist_ok=True)

API_TITLE = "Prospector API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "API para gestão de prospecção comercial e leads."
