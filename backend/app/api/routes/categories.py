from __future__ import annotations

from fastapi import APIRouter

from prospector.modules.categories import get_all_category_names

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[str])
def list_categories() -> list[str]:
    return get_all_category_names()