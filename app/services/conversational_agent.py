import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.schemas import (
    RiskLevel, SVIResult, ConversationTurnResponse, CaseRecord, ChannelType
)
from app.services.nlp_analyzer import NLPAnalyzerService
from app.services.speech_analyzer import SpeechAnalyzerService
from app.services.svi_engine import SVIEngineService

class ConversationalAgentService:
    """
    AI-Powered Conversational Distress & Trauma Assessment Agent.
    Conducts an empathetic, multi-turn dialogue with complainants in Telugu, English, or other Indian languages,
    continuously tracking emotional arousal, prosody, and trauma indicators across turns.
    """

    # In-memory store for active conversational assessment sessions
    sessions: Dict[str, Dict[str, Any]] = {}

    PROMPTS = {
        "Telugu": {
            "turn_1_greeting": "నమస్కారం. మీరు సురక్షితమైన మరియు గోప్యమైన స్థలంలో ఉన్నారు. మీకు ఏమి జరిగిందో, ప్రస్తుతం మీరు ఎలాంటి పరిస్థితిని ఎదుర్కొంటున్నారో మీ స్వంత మాటల్లో చెప్పండి.",
            "turn_2_threat": "ఇది ఎంత భయానకమైనదో నేను అర్థం చేసుకోగలను. ప్రస్తుతం మీపై లేదా మీ కుటుంబంపై ఎవరైనా బెదిరింపులకు పాల్పడుతున్నారా, మీరు సురక్షితమైన ప్రదేశంలో ఉన్నారా?",
            "turn_2_general": "చెప్పినందుకు ధన్యవాదాలు. ఈ సంఘటన వల్ల మీ నిద్ర, భయం లేదా రోజువారీ భద్రతపై ఎలాంటి ప్రభావం పడింది?",
            "turn_3_isolation": "ఈ కష్ట సమయంలో మీకు అండగా ఉండటానికి కుటుంబం లేదా స్థానిక వ్యక్తులు ఎవరైనా ఉన్నారా, లేదా ఊరి నుంచి వెలివేయడం వంటి ఒంటరితనాన్ని ఎదుర్కొంటున్నారా?",
            "turn_3_general": "ఈ సమయంలో మీకు ఎలాంటి తక్షణ సహాయం (కౌన్సిలింగ్, చట్టపరమైన రక్షణ, లేదా పోలీసు భద్రత) అత్యంత అవసరమని మీరు భావిస్తున్నారు?",
            "turn_4_conclusion": "వివరాలు పంచుకున్నందుకు ధన్యవాదాలు. మీ సంభాషణ ఆధారంగా ఒత్తిడి మరియు మానసిక క్షోభ సూచికల విశ్లేషణ పూర్తయింది. మీకు తగిన అధికారి మరియు కౌన్సెలర్ సహాయాన్ని కేటాయించడానికి ఫలితాలను సమీక్షించండి."
        },
        "English": {
            "turn_1_greeting": "Hello. You are in a safe, confidential space. Please tell us what happened in your own words, and what you are going through right now.",
            "turn_2_threat": "I hear how frightening and difficult this is. Are people continuing to threaten or intimidate you or your family right now, and are you in a secure location?",
            "turn_2_general": "Thank you for sharing. How has this impacted your sleep, feelings of fear, or daily sense of personal safety?",
            "turn_3_isolation": "Do you have any trusted family, community, or local support nearby, or are you feeling isolated and cut off from help?",
            "turn_3_general": "What immediate support (counselling, legal aid defense, or emergency protection) feels most urgent for you right now?",
            "turn_4_conclusion": "Thank you for placing your trust in us. Our AI decision-support engine has synthesized your distress and trauma indicators. Please review your personalized assessment and available human support pathways."
        }
    }

    @classmethod
    def start_session(cls, language: str = "Telugu", channel: str = "Voice Assessment") -> Dict[str, Any]:
        session_id = f"SESS-{uuid.uuid4().hex[:8].upper()}"
        lang_pack = cls.PROMPTS.get(language, cls.PROMPTS["English"])

        cls.sessions[session_id] = {
            "session_id": session_id,
            "language": language,
            "channel": channel,
            "turn_index": 1,
            "max_turns": 4,
            "conversation_history": [],
            "cumulative_text": "",
            "total_audio_sec": 0.0,
            "created_at": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
            "case_number": None
        }

        return {
            "session_id": session_id,
            "turn_index": 1,
            "max_turns": 4,
            "language": language,
            "ai_response": lang_pack["turn_1_greeting"]
        }

    @classmethod
    def process_turn(
        cls,
        session_id: str,
        turn_index: int,
        user_message: str,
        language: str = "Telugu",
        channel: str = "Voice Assessment",
        audio_present: bool = False,
        audio_duration_sec: Optional[float] = None
    ) -> ConversationTurnResponse:
        session = cls.sessions.get(session_id)
        if not session:
            # Recreate session if expired
            start_data = cls.start_session(language, channel)
            session = cls.sessions[start_data["session_id"]]
            session_id = start_data["session_id"]

        # Append turn
        session["conversation_history"].append({
            "turn": turn_index,
            "user_message": user_message,
            "audio_present": audio_present,
            "audio_duration_sec": audio_duration_sec or 0.0
        })
        session["cumulative_text"] += " " + user_message
        session["total_audio_sec"] += (audio_duration_sec or 20.0) if audio_present else 0.0

        lang = language or session.get("language", "Telugu")
        lang_pack = cls.PROMPTS.get(lang, cls.PROMPTS["English"])

        # Run real-time NLP and speech analysis on cumulative interaction
        nlp_metrics, emotion_metrics = NLPAnalyzerService.analyze_text(
            text=session["cumulative_text"],
            specified_language=lang
        )

        speech_metrics = None
        if audio_present or session["total_audio_sec"] > 0:
            speech_metrics = SpeechAnalyzerService.analyze_audio(
                text_content=session["cumulative_text"],
                duration_sec=session["total_audio_sec"],
                is_high_distress_hint=(nlp_metrics.fear_score > 50 or nlp_metrics.threat_intimidation_score > 50)
            )

        # Calculate running SVI, stress score, and trauma score
        svi_res = SVIEngineService.calculate_svi(
            nlp=nlp_metrics,
            emotion=emotion_metrics,
            speech=speech_metrics
        )

        progress_pct = min(100, int((turn_index / 4.0) * 100))
        is_complete = (turn_index >= 4)

        # Generate next dynamic AI conversational response
        ai_response = ""
        if turn_index == 1:
            if nlp_metrics.threat_intimidation_score > 40 or nlp_metrics.immediate_danger_detected:
                ai_response = lang_pack["turn_2_threat"]
            else:
                ai_response = lang_pack["turn_2_general"]
        elif turn_index == 2:
            if nlp_metrics.social_isolation_score > 35 or "boycott" in str(nlp_metrics.keywords_matched).lower():
                ai_response = lang_pack["turn_3_isolation"]
            else:
                ai_response = lang_pack["turn_3_general"]
        elif turn_index >= 3 or is_complete:
            ai_response = lang_pack["turn_4_conclusion"]
            is_complete = True
            progress_pct = 100

        detected_indicators = [f.factor for f in svi_res.explainability_factors]

        # Emotion dictionary for UI visualization
        detected_emotions = {
            "Fear": emotion_metrics.fear,
            "Distress": emotion_metrics.distress,
            "Anxiety": emotion_metrics.anxiety,
            "Sadness": emotion_metrics.sadness,
            "Anger": emotion_metrics.anger,
            "Confusion": emotion_metrics.confusion,
            "Calm": emotion_metrics.calm,
            "Neutral": emotion_metrics.neutral
        }

        case_number = session.get("case_number")
        final_assessment = svi_res if is_complete else None

        return ConversationTurnResponse(
            session_id=session_id,
            turn_index=turn_index + 1 if not is_complete else turn_index,
            max_turns=4,
            is_complete=is_complete,
            ai_response=ai_response,
            progress_pct=progress_pct,
            current_stress_score=svi_res.stress_score,
            current_trauma_score=svi_res.trauma_score,
            current_risk_level=svi_res.risk_level,
            emotional_state=svi_res.emotional_state,
            detected_emotions=detected_emotions,
            detected_indicators=detected_indicators,
            final_assessment=final_assessment,
            case_number=case_number
        )
