from fastapi import APIRouter, Query
from typing import Optional, List
from app.models.schemas import SupportResource
from app.services.resource_matcher import ResourceMatcherService

router = APIRouter(prefix="/api/resources", tags=["Resources"])

@router.get("")
async def search_resources(
    state: Optional[str] = None,
    district: Optional[str] = None,
    category: Optional[str] = None,
    language: Optional[str] = None,
    available_24x7: Optional[bool] = None
):
    return ResourceMatcherService.search_resources(
        state=state,
        district=district,
        category=category,
        language=language,
        available_24x7=available_24x7
    )
