from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import db
from app.models.schemas import RiskLevel, SupportStatus, UserRole
from app.services.safety_triage import SafetyTriageService

router = APIRouter(prefix="/api/cases", tags=["Cases"])

class SupportActionRequest(BaseModel):
    action: str  # "ASSIGN", "REVIEW", "REJECT"
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    reviewer_name: Optional[str] = "Officer Rajesh Kumar"

class EmergencyActionRequest(BaseModel):
    action_type: str  # "NOTIFY_OFFICER", "REQUEST_COUNSELLOR", "REQUEST_MEDICAL", "REQUEST_LEGAL", "INITIATE_PROTECTION"
    notes: Optional[str] = None

@router.get("")
async def get_cases(
    risk: Optional[str] = None,
    language: Optional[str] = None,
    channel: Optional[str] = None,
    status: Optional[str] = None,
    district: Optional[str] = None,
    search: Optional[str] = None
):
    results = db.cases

    if risk and risk.upper() != "ALL":
        results = [c for c in results if c.risk_level.value.upper() == risk.upper()]

    if language and language.upper() != "ALL":
        results = [c for c in results if c.language.lower() == language.lower()]

    if channel and channel.upper() != "ALL":
        results = [c for c in results if c.channel.value.lower() == channel.lower()]

    if status and status.upper() != "ALL":
        results = [c for c in results if c.status.lower() == status.lower()]

    if district and district.upper() != "ALL":
        results = [c for c in results if c.district.lower() == district.lower()]

    if search:
        s = search.lower()
        results = [
            c for c in results
            if s in c.case_number.lower()
            or s in c.complainant_alias.lower()
            or s in c.district.lower()
            or s in (c.masked_narrative or "").lower()
        ]

    # Mask raw sensitive information in listing
    anonymized_list = []
    for c in results:
        data = c.model_dump()
        if db.config.anonymize_analytics:
            # Conceal raw unmasked text
            data["raw_text"] = None
        anonymized_list.append(data)

    return anonymized_list

@router.get("/{case_number}")
async def get_case_details(case_number: str):
    case = db.get_case_by_number(case_number)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_number}' not found.")

    # Audit log access
    db.log_audit(
        action="Viewed Detailed Case Dossier",
        case_id=case.case_number,
        access_type="READ",
        details=f"Authorized review by {db.current_user['name']}."
    )

    return case

@router.post("/{case_number}/recommendations/{rec_id}/action")
async def update_recommendation_action(
    case_number: str,
    rec_id: str,
    req: SupportActionRequest
):
    case = db.get_case_by_number(case_number)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    target_rec = None
    for r in case.support_recommendations:
        if r.id == rec_id:
            target_rec = r
            break

    if not target_rec:
        raise HTTPException(status_code=404, detail="Recommendation ID not found.")

    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    target_rec.updated_at = now_str
    target_rec.reviewed_by = req.reviewer_name
    target_rec.human_confirmed = True
    target_rec.human_notes = req.notes or "Confirmed by authorized professional."

    if req.action.upper() == "ASSIGN":
        target_rec.status = SupportStatus.ASSIGNED
        target_rec.assigned_to = req.assigned_to or "Assigned Professional"
        case.status = "Assigned"
        # Add to timeline
        case.timeline.append({
            "time": datetime.now().strftime("%I:%M %p"),
            "title": f"Service Assigned: {target_rec.service_type.value}",
            "desc": f"Allocated to {target_rec.assigned_to}. Notes: {req.notes or 'None'}",
            "status": "done"
        })
    elif req.action.upper() == "REJECT":
        target_rec.status = SupportStatus.REJECTED
        case.timeline.append({
            "time": datetime.now().strftime("%I:%M %p"),
            "title": f"Recommendation Rejected: {target_rec.service_type.value}",
            "desc": f"Reason: {req.notes or 'Not required upon professional evaluation'}",
            "status": "done"
        })
    else:
        target_rec.status = SupportStatus.IN_PROGRESS

    # Log to audit trail
    db.log_audit(
        action=f"Recommendation Action: {req.action.upper()}",
        case_id=case.case_number,
        access_type="ASSIGN",
        details=f"Service: {target_rec.service_type.value}, Target: {target_rec.assigned_to or 'N/A'}"
    )

    return {
        "success": True,
        "recommendation": target_rec,
        "case_status": case.status
    }

@router.post("/{case_number}/emergency-action")
async def trigger_emergency_action(case_number: str, req: EmergencyActionRequest):
    case = db.get_case_by_number(case_number)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    res = SafetyTriageService.simulate_emergency_action(
        action_name=req.action_type,
        case_number=case.case_number,
        actor_name=db.current_user["name"]
    )

    # Append to timeline
    case.timeline.append({
        "time": datetime.now().strftime("%I:%M %p"),
        "title": f"EMERGENCY DISPATCH: {req.action_type}",
        "desc": f"Dispatched by {db.current_user['name']}. Immediate protocol activated.",
        "status": "active"
    })
    case.critical_safety_flag = True

    # Audit log
    db.log_audit(
        action=f"EMERGENCY PROTOCOL ACTIVATED: {req.action_type}",
        case_id=case.case_number,
        access_type="ALERT",
        details="High-urgency multi-agency dispatch notification triggered."
    )

    return res
