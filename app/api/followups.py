from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from app.database import db
from app.models.schemas import FollowUpItem, SupportServiceType

router = APIRouter(prefix="/api/followups", tags=["Follow-ups"])

class FollowUpCreateRequest(BaseModel):
    case_number: str
    category: SupportServiceType
    scheduled_date: str
    scheduled_time: str
    assigned_to: str
    notes: Optional[str] = None

@router.get("")
async def get_followups(status: Optional[str] = None):
    results = db.followups
    if status and status.upper() != "ALL":
        results = [f for f in results if f.status.lower() == status.lower()]
    return results

@router.post("")
async def create_followup(req: FollowUpCreateRequest):
    case = db.get_case_by_number(req.case_number)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    new_item = FollowUpItem(
        id=f"FOL-{uuid.uuid4().hex[:4].upper()}",
        case_id=case.id,
        case_number=case.case_number,
        category=req.category,
        scheduled_date=req.scheduled_date,
        scheduled_time=req.scheduled_time,
        assigned_to=req.assigned_to,
        status="Upcoming",
        notes=req.notes or "Scheduled follow-up assessment",
        historical_svi=[
            {"stage": "Baseline Contact", "date": case.created_at, "svi": case.svi_score}
        ]
    )
    db.followups.insert(0, new_item)

    # Timeline note
    case.timeline.append({
        "time": datetime.now().strftime("%I:%M %p"),
        "title": f"Follow-up Scheduled: {req.category.value}",
        "desc": f"Date: {req.scheduled_date} at {req.scheduled_time}. Assigned to {req.assigned_to}.",
        "status": "active"
    })

    db.log_audit(
        action="Scheduled Follow-up",
        case_id=case.case_number,
        access_type="WRITE",
        details=f"Category: {req.category.value}, Date: {req.scheduled_date}"
    )

    return {"success": True, "followup": new_item}

@router.put("/{followup_id}/status")
async def update_followup_status(followup_id: str, new_status: str):
    target = None
    for f in db.followups:
        if f.id == followup_id:
            target = f
            break

    if not target:
        raise HTTPException(status_code=404, detail="Follow-up not found.")

    target.status = new_status
    db.log_audit(
        action=f"Follow-up Marked as {new_status}",
        case_id=target.case_number,
        access_type="WRITE",
        details=f"ID: {target.id}"
    )
    return {"success": True, "followup": target}
