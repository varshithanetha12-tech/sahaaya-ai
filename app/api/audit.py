from fastapi import APIRouter, Query
from typing import Optional
from app.database import db

router = APIRouter(prefix="/api/audit", tags=["Audit"])

@router.get("")
async def get_audit_logs(
    search: Optional[str] = None,
    access_type: Optional[str] = None,
    case_id: Optional[str] = None
):
    results = db.audit_logs

    if access_type and access_type.upper() != "ALL":
        results = [l for l in results if l.access_type.upper() == access_type.upper()]

    if case_id:
        results = [l for l in results if l.case_id and case_id.lower() in l.case_id.lower()]

    if search:
        s = search.lower()
        results = [
            l for l in results
            if s in l.user_name.lower()
            or s in l.action.lower()
            or s in l.details.lower()
            or (l.case_id and s in l.case_id.lower())
        ]

    return results
