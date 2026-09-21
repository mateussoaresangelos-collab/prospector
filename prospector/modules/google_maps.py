"""Google Maps-style lead discovery based on open APIs."""

from __future__ import annotations

import re
from typing import Any

import requests

from prospector.models.lead import Lead
from prospector.modules.categories import Category, get_category_by_name


class GoogleMapsSearcher:
    """Search for potential leads using open geocoding and map data APIs."""

    def __init__(self, timeout: int = 15) -> None:
        """Initialize the searcher with a request timeout."""
        self.timeout = timeout
        self.session = requests.Session()

    def search(self, category: str, city: str, limit: int = 10) -> list[Lead]:
        """Return a list of leads for the given category and city."""
        if not category.strip() or not city.strip():
            return []

        coordinates = self._geocode_city(city)
        if coordinates is None:
            return []

        category_obj = get_category_by_name(category)
        tag_sets = self._resolve_tag_sets(category_obj)
        if not tag_sets:
            return []

        elements = self._collect_elements(tag_sets, coordinates, limit)
        if not elements:
            return []

        leads: list[Lead] = []
        exact_category = category_obj is not None

        for item in elements[:limit]:
            tags_data = item.get("tags", {})
            name = tags_data.get("name")
            if not name:
                continue

            lname = name.lower()
            if category_obj:
                if category_obj.accept:
                    if not any(tok.lower() in lname for tok in category_obj.accept):
                        continue
                if category_obj.ignore:
                    if any(tok.lower() in lname for tok in category_obj.ignore):
                        continue

            lead = Lead(
                name=name,
                category=category,
                city=tags_data.get("addr:city") or city,
                address=self._build_address(tags_data),
                phone=tags_data.get("phone") or tags_data.get("contact:phone", ""),
                website=tags_data.get("website") or tags_data.get("contact:website", ""),
                has_website=bool(
                    tags_data.get("website") or tags_data.get("contact:website", "")
                ),
            )

            score = 0
            if lead.website:
                score += 40
            if lead.phone:
                score += 20
            if lead.email:
                score += 20
            if lead.instagram:
                score += 10
            if exact_category:
                score += 10
            lead.score = min(score, 100)

            leads.append(lead)

        return leads

    def _geocode_city(self, city: str) -> tuple[float, float] | None:
        """Geocode a city name using Nominatim."""
        try:
            response = self.session.get(
                "https://nominatim.openstreetmap.org/search",
                params={"format": "jsonv2", "limit": 1, "q": city},
                timeout=self.timeout,
                headers={"User-Agent": "prospector/1.0"},
            )
            response.raise_for_status()
        except requests.RequestException:
            return None

        try:
            payload = response.json()
        except ValueError:
            return None

        if not payload:
            return None

        first_result = payload[0]
        return float(first_result["lat"]), float(first_result["lon"])

    def _collect_elements(
        self,
        tag_sets: list[list[tuple[str, str]]],
        coordinates: tuple[float, float],
        limit: int,
    ) -> list[dict[str, Any]]:
        """Try several tag combinations until a valid result set is found."""
        best_elements: list[dict[str, Any]] = []
        for tag_set in tag_sets:
            try:
                response = self.session.post(
                    "https://overpass-api.de/api/interpreter",
                    data=self._build_query(tag_set, coordinates, limit),
                    timeout=self.timeout,
                    headers={"User-Agent": "prospector/1.0"},
                )
                response.raise_for_status()
            except requests.RequestException:
                continue

            try:
                payload = response.json()
            except ValueError:
                continue

            elements = payload.get("elements", [])
            if not elements:
                continue

            # prefer the first non-empty result set for precision,
            # but keep the best set if it returns more than the current best.
            if len(elements) >= limit:
                return elements
            if len(elements) > len(best_elements):
                best_elements = elements

        return best_elements

    def _resolve_tag_sets(self, category_obj: Category | None) -> list[list[tuple[str, str]]]:
        """Build an ordered list of tag sets for the requested category."""
        if category_obj:
            return category_obj.tag_sets()
        return []

    def _build_query(
        self, tags: list[tuple[str, str]], coordinates: tuple[float, float], limit: int
    ) -> str:
        """Build an Overpass query for the specified tags near coordinates."""
        latitude, longitude = coordinates
        tag_clauses = []
        for key, value in tags:
            tag_clauses.append(f'node["{key}"="{value}"](around:5000,{latitude},{longitude});')
            tag_clauses.append(f'way["{key}"="{value}"](around:5000,{latitude},{longitude});')
            tag_clauses.append(f'relation["{key}"="{value}"](around:5000,{latitude},{longitude});')

        query = """[out:json][timeout:25];
(
"""
        query += "\n".join(tag_clauses)
        query += """
);
out center;
"""
        return query

    def _build_address(self, tags_data: dict[str, Any]) -> str:
        """Build a readable address from OSM tags."""
        parts = []
        if tags_data.get("addr:street"):
            parts.append(tags_data["addr:street"])
        if tags_data.get("addr:housenumber"):
            parts.append(tags_data["addr:housenumber"])
        if tags_data.get("addr:city"):
            parts.append(tags_data["addr:city"])
        return ", ".join(parts)
