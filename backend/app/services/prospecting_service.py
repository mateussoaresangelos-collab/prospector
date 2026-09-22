from __future__ import annotations

import time
from typing import Any

from prospector.config import LEADS_FILE
from prospector.models.lead import Lead
from prospector.modules.ai_generator import AIGenerator
from prospector.modules.csv_exporter import CSVExporter
from prospector.modules.db import DBClient
from prospector.modules.email_finder import EmailFinder
from prospector.modules.google_maps import GoogleMapsSearcher
from prospector.modules.instagram import InstagramFinder
from prospector.modules.website_checker import WebsiteChecker


class ProspectingService:
    """Wraps the current prospecting pipeline for API use."""

    def __init__(self) -> None:
        self.db = DBClient()

    def run(self, city: str, category: str, force_refresh: bool = False) -> list[Lead]:
        city = city.strip()
        category = category.strip()
        if not city or not category:
            raise ValueError("Cidade e categoria são obrigatórias.")

        cached = self.db.get_last_search(city=city, category=category)
        if not force_refresh and cached is not None:
            return cached[1]

        searcher = GoogleMapsSearcher()
        checker = WebsiteChecker()
        instagram_finder = InstagramFinder()
        ai_generator = AIGenerator()
        email_finder = EmailFinder()

        start_ts = time.monotonic()
        leads = searcher.search(category=category, city=city, limit=12)
        processed: list[Lead] = []

        for lead in leads:
            try:
                lead.city = lead.city or city
                lead.category = lead.category or category
                lead.has_website = checker.has_website(lead)

                if lead.has_website:
                    lead = email_finder.find_email(lead)

                lead.instagram = instagram_finder.find_profile(lead)

                if lead.has_website and lead.email:
                    lead.ai_message = ai_generator.generate_message(lead)

                lead.status = lead.status or "Novo"
                lead.favorite = False
                lead.notes = lead.notes or ""
                lead.metadata["last_run"] = city
                processed.append(lead)
            except Exception as exc:  # pragma: no cover
                lead.metadata["status"] = "Erro"
                lead.metadata["error"] = str(exc)
                processed.append(lead)

        duration_seconds = time.monotonic() - start_ts
        self.db.save_search(city=city, category=category, leads=processed, duration_seconds=duration_seconds)
        exporter = CSVExporter()
        exporter.export(processed, LEADS_FILE)
        return processed

    def list_searches(self) -> list[dict[str, Any]]:
        return self.db.get_searches()

    def get_last_search(self, city: str, category: str) -> list[Lead]:
        cached = self.db.get_last_search(city=city, category=category)
        return cached[1] if cached else []

    def get_search_by_id(self, search_id: int) -> dict[str, Any] | None:
        return self.db.get_search_by_id(search_id)

    def get_leads_for_search(self, search_id: int) -> list[Lead]:
        return self.db.get_leads_for_search(search_id)

    def update_lead(self, lead_id: int, data: dict[str, Any]) -> Lead | None:
        leads = self.db.filter_leads(search_id=None)
        target = next((lead for lead in leads if lead.id == lead_id), None)
        if target is None:
            return None
        if "status" in data and data["status"] is not None:
            target.status = data["status"]
        if "favorite" in data and data["favorite"] is not None:
            target.favorite = bool(data["favorite"])
        if "notes" in data and data["notes"] is not None:
            target.notes = data["notes"]
        self.db.update_lead(target)
        return target
