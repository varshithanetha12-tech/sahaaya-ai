from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from app.models.schemas import CaseCreateRequest, SVIResult, RiskLevel
from app.database import db
from app.services.speech_analyzer import SpeechAnalyzerService
from app.services.nlp_analyzer import NLPAnalyzerService
from app.services.svi_engine import SVIEngineService

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

@router.post("/analyze-interactive")
async def analyze_interactive(req: CaseCreateRequest):
    """
    Real-time assessment calculation endpoint for the victim chat / helpline interface.
    Performs Multilingual NLP, Speech Analysis, Emotion Detection, and SVI calculation.
    """
    if not req.consent_given:
        raise HTTPException(
            status_code=400,
            detail="Consent is required before AI stress and trauma assessment can proceed."
        )

    # NLP and Emotion Analysis
    nlp, emotion = NLPAnalyzerService.analyze_text(
        text=req.raw_text or "",
        specified_language=req.language
    )

    # Speech Analysis if audio channel or simulation
    speech = None
    has_audio = req.audio_present or req.channel in ["Voice Helpline", "Voice Recording Upload", "IVRS"]
    if has_audio:
        speech = SpeechAnalyzerService.analyze_audio(
            text_content=req.raw_text,
            duration_sec=req.audio_duration_sec or 28.0,
            is_high_distress_hint=(nlp.fear_score > 50 or nlp.threat_intimidation_score > 50)
        )

    # Compute SVI & Explainable Factors
    svi_res = SVIEngineService.calculate_svi(
        nlp=nlp,
        emotion=emotion,
        speech=speech,
        config=db.config
    )

    return {
        "svi": svi_res,
        "speech_metrics": speech,
        "nlp_metrics": nlp,
        "emotion_metrics": emotion,
        "detected_language": nlp.detected_language
    }

@router.post("/submit-case")
async def submit_case(req: CaseCreateRequest):
    """
    Creates a formal triage case record from the victim interaction.
    """
    if not req.consent_given:
        raise HTTPException(
            status_code=400,
            detail="Consent must be formally registered to create an authorized triage record."
        )

    new_case = db.create_case_from_interaction(req)
    return {
        "success": True,
        "case": new_case,
        "message": f"Case {new_case.case_number} registered successfully and routed for professional review."
    }
