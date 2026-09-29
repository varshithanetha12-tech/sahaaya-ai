from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from app.models.schemas import CaseCreateRequest, SVIResult, RiskLevel, ConversationTurnRequest
from app.database import db
from app.services.speech_analyzer import SpeechAnalyzerService
from app.services.nlp_analyzer import NLPAnalyzerService
from app.services.svi_engine import SVIEngineService
from app.services.conversational_agent import ConversationalAgentService

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

@router.post("/conversation/start")
async def start_conversation_session(language: str = "Telugu", channel: str = "Voice Assessment"):
    """
    Start a new AI-guided conversational assessment session.
    Returns a session_id and the first AI greeting message.
    """
    session_data = ConversationalAgentService.start_session(language=language, channel=channel)
    db.log_audit(
        action="Conversational Assessment Session Started",
        case_id=None,
        access_type="WRITE",
        details=f"Language: {language}, Channel: {channel}, Session: {session_data['session_id']}"
    )
    return session_data

@router.post("/conversation/turn")
async def process_conversation_turn(req: ConversationTurnRequest):
    """
    Process one turn of the AI conversational assessment.
    Analyzes the user's response and returns the next AI question plus live indicators.
    """
    response = ConversationalAgentService.process_turn(
        session_id=req.session_id,
        turn_index=req.turn_index,
        user_message=req.user_message,
        language=req.language,
        channel=req.channel,
        audio_present=req.audio_present,
        audio_duration_sec=req.audio_duration_sec
    )

    # If assessment is complete, create a case record
    if response.is_complete and response.final_assessment:
        session = ConversationalAgentService.sessions.get(req.session_id)
        if session and not session.get("case_number"):
            case_req = CaseCreateRequest(
                channel="Chatbot",
                language=req.language,
                raw_text=session.get("cumulative_text", req.user_message),
                audio_present=req.audio_present,
                audio_duration_sec=req.audio_duration_sec,
                consent_given=True
            )
            new_case = db.create_case_from_interaction(case_req)
            session["case_number"] = new_case.case_number
            response.case_number = new_case.case_number

    return response
