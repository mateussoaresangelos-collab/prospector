from __future__ import annotations

from pydantic import BaseModel


class SearchRequest(BaseModel):
    city: str
    category: str
    force_refresh: bool = False


class SearchResponse(BaseModel):
    city: str
    category: str
    lead_count: int
    duration_seconds: float
