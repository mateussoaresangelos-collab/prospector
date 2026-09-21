from __future__ import annotations

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[3]
PROJECT_ROOT = BASE_DIR
DATA_DIR = PROJECT_ROOT / "prospector" / "data"
DB_PATH = DATA_DIR / "prospector.db"
LEADS_PATH = DATA_DIR / "leads.csv"

os.makedirs(DATA_DIR, exist_ok=True)

API_TITLE = "Prospector API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "API para gestão de prospecção comercial e leads."
