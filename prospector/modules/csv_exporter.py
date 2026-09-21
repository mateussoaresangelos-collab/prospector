"""CSV export module."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from prospector.config import LEADS_FILE
from prospector.models.lead import Lead


class CSVExporter:
    """Export leads to a CSV file."""

    def export(self, leads: list[Lead], path: str | Path | None = None) -> Path:
        """Export a list of leads to CSV."""
        # TODO: implement CSV export logic.
        target_path = Path(path or LEADS_FILE)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if leads:
            with target_path.open("w", newline="", encoding="utf-8") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=list(leads[0].to_dict().keys()))
                writer.writeheader()
                writer.writerows([lead.to_dict() for lead in leads])
        else:
            target_path.write_text("", encoding="utf-8")

        return target_path
