from fastapi import APIRouter
from app.database import db

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("")
async def get_analytics_data():
    return db.get_analytics()
