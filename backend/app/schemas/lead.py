from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class LeadBase(BaseModel):
    name: str = ""
    category: str = ""
    city: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    instagram: str = ""
    linkedin: str = ""
    facebook: str = ""
    whatsapp: str = ""
    has_website: bool = False
    has_email: bool = False
    has_instagram: bool = False
    score: int = 0
    status: str = "Novo"
    favorite: bool = False
    notes: str = ""
    ai_message: str = ""


class LeadRead(LeadBase):
    id: int | None = None
    search_id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LeadUpdate(BaseModel):
    status: str | None = None
    favorite: bool | None = None
    notes: str | None = None
