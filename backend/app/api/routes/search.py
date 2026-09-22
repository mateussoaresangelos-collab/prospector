from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.search import SearchRequest, SearchResponse
from app.services.prospecting_service import ProspectingService

router = APIRouter(prefix="/search", tags=["search"])
service = ProspectingService()


@router.post("", response_model=SearchResponse)
def run_search(payload: SearchRequest):
    try:
        leads = service.run(payload.city, payload.category, payload.force_refresh)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    saved_search = service.db.get_last_search(city=payload.city.strip(), category=payload.category.strip())
    duration_seconds = saved_search[0]["duration_seconds"] if saved_search else 0.0

    return {
        "city": payload.city,
        "category": payload.category,
        "lead_count": len(leads),
        "duration_seconds": duration_seconds,
    }


@router.get("/history")
def history():
    return service.list_searches()
