from fastapi import APIRouter
from pydantic import BaseModel
from app.models.schemas import UserRole
from app.database import db

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class RoleSwitchRequest(BaseModel):
    role: UserRole

ROLE_PROFILES = {
    UserRole.OFFICER: {
        "name": "Officer Rajesh Kumar",
        "role": UserRole.OFFICER,
        "department": "District Atrocity Protection Unit, Rangareddy",
        "email": "rajesh.kumar@telangana.gov.in"
    },
    UserRole.COUNSELLOR: {
        "name": "Dr. S. Anuradha",
        "role": UserRole.COUNSELLOR,
        "department": "Tele-MANAS Trauma Triage Unit",
        "email": "s.anuradha@telemanas.gov.in"
    },
    UserRole.LEGAL: {
        "name": "Adv. K. Venkatesh",
        "role": UserRole.LEGAL,
        "department": "State Legal Services Authority (SLSA)",
        "email": "k.venkatesh@tslsa.nic.in"
    },
    UserRole.ADMIN: {
        "name": "Admin Suresh Varma",
        "role": UserRole.ADMIN,
        "department": "National Portal IT & System Administration",
        "email": "admin.varma@sahaaya.gov.in"
    },
    UserRole.VICTIM: {
        "name": "Complainant (Citizen Portal)",
        "role": UserRole.VICTIM,
        "department": "Public Grievance Interface",
        "email": "citizen.anonymous@user.in"
    }
}

@router.get("/me")
async def get_current_user():
    return db.current_user

@router.post("/switch-role")
async def switch_role(req: RoleSwitchRequest):
    if req.role in ROLE_PROFILES:
        db.current_user = ROLE_PROFILES[req.role]
        db.log_audit(
            action=f"Switched Session Role to {req.role.value}",
            case_id=None,
            access_type="WRITE",
            details=f"Demo fast-switch performed for {db.current_user['name']}."
        )
    return {"success": True, "user": db.current_user}

@router.get("/notifications")
async def get_notifications():
    return db.notifications

@router.post("/notifications/mark-all-read")
async def mark_notifications_read():
    for n in db.notifications:
        n.read = True
    return {"success": True}
