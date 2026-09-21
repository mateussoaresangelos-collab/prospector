"""Lead model for the prospector project."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Lead:
    """Represents a potential client lead."""

    id: int | None = None
    search_id: int | None = None
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
    score: int = 0
    status: str = "Novo"
    favorite: bool = False
    notes: str = ""
    ai_message: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the lead to a dictionary."""
        return {
            "id": self.id,
            "search_id": self.search_id,
            "name": self.name,
            "category": self.category,
            "city": self.city,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "instagram": self.instagram,
            "linkedin": self.linkedin,
            "facebook": self.facebook,
            "whatsapp": self.whatsapp,
            "has_website": self.has_website,
            "score": self.score,
            "status": self.status,
            "favorite": self.favorite,
            "notes": self.notes,
            "ai_message": self.ai_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row: Any) -> "Lead":
        """Create a Lead from a SQLite row."""
        return cls(
            id=row["id"],
            search_id=row["search_id"],
            name=row["name"] or "",
            category=row["category"] or "",
            city=row["city"] or "",
            address=row["address"] or "",
            phone=row["phone"] or "",
            email=row["email"] or "",
            website=row["website"] or "",
            instagram=row["instagram"] or "",
            linkedin=row["linkedin"] or "",
            facebook=row["facebook"] or "",
            whatsapp=row["whatsapp"] or "",
            has_website=bool(row["has_website"]),
            score=int(row["score"] or 0),
            status=row["status"] or "Novo",
            favorite=bool(row["favorite"]),
            notes=row["notes"] or "",
            ai_message=row["ai_message"] or "",
            created_at=row["created_at"] or "",
            updated_at=row["updated_at"] or "",
        )
