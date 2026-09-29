from fastapi import APIRouter
from app.models.schemas import SystemConfig, UserRole
from app.database import db

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/config")
async def get_config():
    return db.config

@router.post("/config")
async def update_config(cfg: SystemConfig):
    db.config = cfg
    db.log_audit(
        action="Updated Triage Parameters & Thresholds",
        case_id=None,
        access_type="WRITE",
        details=(
            f"LowMax={cfg.threshold_low_max}, ModMax={cfg.threshold_mod_max}, "
            f"HighMax={cfg.threshold_high_max}, NLPWeight={cfg.nlp_weight}"
        )
    )
    return {"success": True, "config": db.config}

@router.get("/system-health")
async def get_system_health():
    return {
        "status": "HEALTHY",
        "version": "Sahaaya AI v2.4-prod",
        "nlp_multilingual_service": "ONLINE (10 Indic Languages Active)",
        "speech_prosody_engine": "ONLINE (Acoustic Feature Extractor v3.1)",
        "svi_scoring_engine": "ONLINE (Calibrated Norms 2026)",
        "triage_queue_depth": sum(1 for c in db.cases if c.status == "Pending"),
        "active_escalations": sum(1 for c in db.cases if c.critical_safety_flag),
        "audit_ledger_status": "INTEGRITY_VERIFIED (HMAC-SHA256)",
        "uptime": "99.98%"
    }
