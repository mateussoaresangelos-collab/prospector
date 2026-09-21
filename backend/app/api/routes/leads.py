from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.lead import LeadRead, LeadUpdate
from app.services.prospecting_service import ProspectingService

router = APIRouter(prefix="/leads", tags=["leads"])
service = ProspectingService()


@router.get("", response_model=list[LeadRead])
def list_leads():
    searches = service.list_searches()
    if not searches:
        return []
    latest = searches[0]
    return [
        {
            "id": lead.id,
            "search_id": lead.search_id,
            "name": lead.name,
            "category": lead.category,
            "city": lead.city,
            "address": lead.address,
            "phone": lead.phone,
            "email": lead.email,
            "website": lead.website,
            "instagram": lead.instagram,
            "linkedin": lead.linkedin,
            "facebook": lead.facebook,
            "whatsapp": lead.whatsapp,
            "has_website": lead.has_website,
            "score": lead.score,
            "status": lead.status,
            "favorite": lead.favorite,
            "notes": lead.notes,
            "ai_message": lead.ai_message,
            "created_at": lead.created_at,
            "updated_at": lead.updated_at,
            "metadata": lead.metadata,
        }
        for lead in service.get_leads_for_search(latest["id"])
    ]


@router.patch("/{lead_id}", response_model=LeadRead)
def update_lead(lead_id: int, data: LeadUpdate):
    updated = service.update_lead(lead_id, data.model_dump(exclude_none=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="Lead não encontrado.")
    return {
        "id": updated.id,
        "search_id": updated.search_id,
        "name": updated.name,
        "category": updated.category,
        "city": updated.city,
        "address": updated.address,
        "phone": updated.phone,
        "email": updated.email,
        "website": updated.website,
        "instagram": updated.instagram,
        "linkedin": updated.linkedin,
        "facebook": updated.facebook,
        "whatsapp": updated.whatsapp,
        "has_website": updated.has_website,
        "score": updated.score,
        "status": updated.status,
        "favorite": updated.favorite,
        "notes": updated.notes,
        "ai_message": updated.ai_message,
        "created_at": updated.created_at,
        "updated_at": updated.updated_at,
        "metadata": updated.metadata,
    }
