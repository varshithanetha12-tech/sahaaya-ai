from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models.schemas import (
    CaseRecord, RiskLevel, ChannelType, SpeechMetrics, NLPMetrics, EmotionMetrics,
    ExplainabilityFactor, SupportRecommendation, SupportServiceType, SupportStatus,
    FollowUpItem, NotificationItem, AuditLogItem, UserRole
)

def build_demo_cases() -> List[CaseRecord]:
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    two_days_ago = (now - timedelta(days=2)).strftime("%Y-%m-%d")

    # Case 003: THE MAIN SPECIFIED DEMO SCENARIO (NHAA-1024)
    # Telugu Voice Helpline - Land Threat & Boycott
    case_nhaa_1024 = CaseRecord(
        id="CASE-1024",
        case_number="NHAA-1024",
        created_at=f"{today_str} 09:42 AM",
        complainant_alias="Complainant-TL-4819",
        channel=ChannelType.VOICE,
        language="Telugu",
        raw_text=(
            "నమస్కారం... మమ్మల్ని ఊరి నుంచి వెలివేశారు... పొలం లాక్కుంటామని కొట్టారు... "
            "రాత్రిళ్ళు ఇంటి చుట్టూ తిరుగుతూ చంపేస్తామని బెదిరిస్తున్నారు... ఎవరూ సహాయం చేయడం లేదు... "
            "పిల్లలతో కలిసి ఇంట్లో దాక్కున్నాం... చాలా భయంగా ఉంది... ఏం చేయాలో దిక్కులేదు..."
        ),
        masked_narrative=(
            "Complainant reports forced social boycott in village, physical assault regarding land dispute, "
            "night intimidation around residence with death threats. Family sheltering indoors in acute distress."
        ),
        district="Rangareddy",
        state="Telangana",
        consent_recorded=True,
        svi_score=82,
        risk_level=RiskLevel.HIGH,
        confidence=0.89,
        status="Under Review",
        assigned_officer="Officer Rajesh Kumar (SP-Cell)",
        speech_metrics=SpeechMetrics(
            speech_rate_wpm=82.0,
            pause_count=6,
            avg_pause_duration_sec=3.2,
            pitch_variance_hz=48.5,
            voice_instability_index=0.74,
            hesitation_score=68.0,
            speech_intensity_db=71.2,
            tremor_detected=True,
            distress_indicators=[
                "High pitch variance (acoustic tremor)",
                "Extended silence gaps (> 2.8s) during narrative",
                "Elevated hesitation and syllable repetition rate"
            ]
        ),
        nlp_metrics=NLPMetrics(
            detected_language="Telugu",
            fear_score=86.0,
            anxiety_score=84.0,
            threat_intimidation_score=88.0,
            severe_distress_score=79.0,
            hopelessness_score=72.0,
            social_isolation_score=85.0,
            emotional_shock_score=76.0,
            vulnerability_score=84.0,
            self_harm_ideation=False,
            immediate_danger_detected=True,
            keywords_matched=["చంపేస్తామని", "బెదిరిస్తున్నారు", "వెలివేశారు", "భయంగా", "దిక్కులేదు"]
        ),
        emotion_metrics=EmotionMetrics(
            fear=0.86,
            sadness=0.62,
            anger=0.45,
            distress=0.79,
            anxiety=0.84,
            confusion=0.38,
            neutral=0.04,
            calm=0.06,
            dominant_emotion="Fear",
            confidence=0.89
        ),
        explainability=[
            ExplainabilityFactor(
                factor="Strong Fear-Related Language",
                weight=86.0,
                description="Complainant repeatedly expressed acute dread ('చాలా భయంగా ఉంది') and panic for family safety.",
                evidence_snippet="Expressions of intense fear recorded in Telugu narrative",
                indicator_group="NLP"
            ),
            ExplainabilityFactor(
                factor="Multiple Threat & Coercion References",
                weight=88.0,
                description="Explicit death threats and nocturnal stalking around residence recorded.",
                evidence_snippet="Keywords: 'చంపేస్తామని', 'బెదిరిస్తున్నారు' (Threats to kill)",
                indicator_group="NLP"
            ),
            ExplainabilityFactor(
                factor="Frequent Long Pauses & Hesitation",
                weight=74.0,
                description="Recorded 6 extended silence pauses (avg 3.2s) indicating emotional inhibition and speech blockages.",
                evidence_snippet="Prosodic hesitation markers in audio stream",
                indicator_group="Speech"
            ),
            ExplainabilityFactor(
                factor="Social Isolation & Boycott Markers",
                weight=85.0,
                description="Active social exclusion ('ఊరి నుంచి వెలివేశారు') and lack of local support network.",
                evidence_snippet="Social exclusion and community boycott verified",
                indicator_group="NLP"
            ),
            ExplainabilityFactor(
                factor="Acoustic Voice Tremor & Pitch Instability",
                weight=74.0,
                description="Pitch variance measured at 48.5 Hz with vocal tremor index of 0.74, indicating acute autonomic arousal.",
                evidence_snippet="Acoustic biometric anomaly detected",
                indicator_group="Speech"
            )
        ],
        support_recommendations=[
            SupportRecommendation(
                id="REC-1024-1",
                case_id="CASE-1024",
                service_type=SupportServiceType.COUNSELLING,
                priority="Urgent",
                status=SupportStatus.ASSIGNED,
                assigned_to="Dr. S. Anuradha (Tele-MANAS Trauma Specialist)",
                reason="Acute trauma, high fear arousal, and helplessness indicators.",
                human_confirmed=True,
                human_notes="Immediate remote psychological first aid authorized. Session scheduled for 10:30 AM.",
                reviewed_by="Officer Rajesh Kumar",
                updated_at=f"{today_str} 10:02 AM"
            ),
            SupportRecommendation(
                id="REC-1024-2",
                case_id="CASE-1024",
                service_type=SupportServiceType.LEGAL_AID,
                priority="High",
                status=SupportStatus.ASSIGNED,
                assigned_to="Adv. K. Venkatesh (District Legal Services Authority)",
                reason="Severe threat to life, illegal dispossession, and social boycott under PoA Act provisions.",
                human_confirmed=True,
                human_notes="Free legal aid counsel assigned under Sec 12 of Legal Services Authorities Act.",
                reviewed_by="Officer Rajesh Kumar",
                updated_at=f"{today_str} 10:05 AM"
            ),
            SupportRecommendation(
                id="REC-1024-3",
                case_id="CASE-1024",
                service_type=SupportServiceType.WITNESS_PROTECTION,
                priority="Urgent",
                status=SupportStatus.PENDING,
                assigned_to=None,
                reason="Night stalking around residence poses imminent risk of physical violence.",
                human_confirmed=False,
                human_notes="Forwarded to Sub-Divisional Police Officer for mobile patrol deployment.",
                reviewed_by="Officer Rajesh Kumar",
                updated_at=f"{today_str} 10:08 AM"
            )
        ],
        timeline=[
            {"time": "09:42 AM", "title": "Victim Contacted Helpline", "desc": "Incoming call received via National Atrocity Helpline IVRS / Voice Gateway.", "status": "done"},
            {"time": "09:44 AM", "title": "Consent Recorded", "desc": "Explicit telephonic consent affirmed for AI-assisted distress triage and authorized support dispatch.", "status": "done"},
            {"time": "09:45 AM", "title": "Speech Converted to Text", "desc": "Automated multilingual speech recognition processed Telugu audio stream (98.4% WER confidence).", "status": "done"},
            {"time": "09:46 AM", "title": "AI Assessment Completed", "desc": "SVI Engine computed composite Stress Vulnerability Index of 82/100 (HIGH Risk tier).", "status": "done"},
            {"time": "09:47 AM", "title": "High-Risk Indicators Detected", "desc": "Automated safety layer flagged threat, fear, isolation, and acoustic tremor signals.", "status": "done"},
            {"time": "09:49 AM", "title": "Human Reviewer Notified", "desc": "High-priority alert dispatched to Rangareddy District Nodal Officer on duty.", "status": "done"},
            {"time": "10:02 AM", "title": "Counsellor & Legal Aid Assigned", "desc": "Officer confirmed priority counselling and legal aid counsel allocation.", "status": "done"},
            {"time": "10:20 AM", "title": "Initial Follow-up Logged", "desc": "Preliminary telephonic welfare check performed; victim safely secured indoors awaiting patrol.", "status": "active"}
        ],
        critical_safety_flag=True
    )

    # Case 001: Low Risk Preset
    case_001 = CaseRecord(
        id="CASE-1001",
        case_number="NHAA-1001",
        created_at=f"{today_str} 08:15 AM",
        complainant_alias="Complainant-MH-1120",
        channel=ChannelType.PORTAL,
        language="Marathi",
        raw_text="मी शिष्यवृत्ती आणि जात प्रमाणपत्र पडతాळणीबद्दल माहिती विचारण्यासाठी संपर्क केला आहे. अर्ज प्रक्रिया काय आहे?",
        masked_narrative="Inquiry regarding caste certificate verification guidelines and post-matric scholarship timeline.",
        district="Pune",
        state="Maharashtra",
        consent_recorded=True,
        svi_score=22,
        risk_level=RiskLevel.LOW,
        confidence=0.94,
        status="Resolved",
        assigned_officer="Helpdesk Officer M. Shinde",
        speech_metrics=None,
        nlp_metrics=NLPMetrics(
            detected_language="Marathi",
            fear_score=5.0,
            anxiety_score=10.0,
            threat_intimidation_score=0.0,
            severe_distress_score=5.0,
            hopelessness_score=0.0,
            social_isolation_score=0.0,
            emotional_shock_score=0.0,
            vulnerability_score=12.0,
            self_harm_ideation=False,
            immediate_danger_detected=False,
            keywords_matched=[]
        ),
        emotion_metrics=EmotionMetrics(
            fear=0.05,
            sadness=0.05,
            anger=0.02,
            distress=0.08,
            anxiety=0.12,
            confusion=0.20,
            neutral=0.82,
            calm=0.75,
            dominant_emotion="Calm",
            confidence=0.94
        ),
        explainability=[
            ExplainabilityFactor(
                factor="Standard Procedural Query",
                weight=15.0,
                description="Interaction pertains to administrative documentation with no safety or distress keywords.",
                evidence_snippet="Administrative query terms",
                indicator_group="NLP"
            )
        ],
        support_recommendations=[
            SupportRecommendation(
                id="REC-1001-1",
                case_id="CASE-1001",
                service_type=SupportServiceType.REHABILITATION,
                priority="Standard",
                status=SupportStatus.COMPLETED,
                assigned_to="District Welfare Desk",
                reason="Standard informational guidance regarding welfare portal.",
                human_confirmed=True,
                human_notes="Information shared via SMS and portal link.",
                reviewed_by="Helpdesk Officer M. Shinde",
                updated_at=f"{today_str} 08:30 AM"
            )
        ],
        timeline=[
            {"time": "08:15 AM", "title": "Portal Query Submitted", "desc": "Online form submitted via National Portal.", "status": "done"},
            {"time": "08:16 AM", "title": "Consent Recorded", "desc": "Standard digital consent registered.", "status": "done"},
            {"time": "08:17 AM", "title": "AI Assessment: Low Risk", "desc": "SVI Score 22/100. Calm procedural query.", "status": "done"},
            {"time": "08:30 AM", "title": "Resolved", "desc": "Helpdesk dispatched scheme links.", "status": "done"}
        ],
        critical_safety_flag=False
    )

    # Case 002: Moderate Risk Preset
    case_002 = CaseRecord(
        id="CASE-1002",
        case_number="NHAA-1002",
        created_at=f"{yesterday_str} 04:30 PM",
        complainant_alias="Complainant-KA-3091",
        channel=ChannelType.CHAT,
        language="Kannada",
        raw_text=(
            "ನಮಗೆ ಪುನರ್ವಸತಿ ಪರಿಹಾರ ಇನ್ನೂ ಸಿಕ್ಕಿಲ್ಲ... ಕಳೆದ ಮೂರು ತಿಂಗಳಿಂದ ಸರ್ಕಾರಿ ಕಚೇರಿಗಳಿಗೆ ಅಲೆಯುತ್ತಿದ್ದೇವೆ. "
            "ಮನೆ ಕಳೆದುಕೊಂಡು ತುಂಬಾ ಸಂಕಷ್ಟದಲ್ಲಿದ್ದೇವೆ. ಮಕ್ಕಳಿಗೆ ಊಟಕ್ಕೂ ತೊಂದರೆಯಾಗಿದೆ... ದಯವಿಟ್ಟು ಸಹಾಯ ಮಾಡಿ."
        ),
        masked_narrative="Delayed rehabilitation grant disbursement following displacement. Expressing economic distress and severe anxiety.",
        district="Belagavi",
        state="Karnataka",
        consent_recorded=True,
        svi_score=52,
        risk_level=RiskLevel.MODERATE,
        confidence=0.86,
        status="Assigned",
        assigned_officer="Officer Suma Patil",
        speech_metrics=None,
        nlp_metrics=NLPMetrics(
            detected_language="Kannada",
            fear_score=35.0,
            anxiety_score=58.0,
            threat_intimidation_score=15.0,
            severe_distress_score=55.0,
            hopelessness_score=48.0,
            social_isolation_score=40.0,
            emotional_shock_score=30.0,
            vulnerability_score=62.0,
            self_harm_ideation=False,
            immediate_danger_detected=False,
            keywords_matched=["ಸಂಕಷ್ಟದಲ್ಲಿದ್ದೇವೆ", "ಸಹಾಯ"]
        ),
        emotion_metrics=EmotionMetrics(
            fear=0.32,
            sadness=0.68,
            anger=0.25,
            distress=0.55,
            anxiety=0.62,
            confusion=0.30,
            neutral=0.15,
            calm=0.18,
            dominant_emotion="Sadness",
            confidence=0.86
        ),
        explainability=[
            ExplainabilityFactor(
                factor="Economic Vulnerability & Displacement",
                weight=62.0,
                description="Long-term pending compensation causing substantial household distress and instability.",
                evidence_snippet="Mentions loss of shelter and food insecurity",
                indicator_group="NLP"
            ),
            ExplainabilityFactor(
                factor="Prolonged Anxiety & Exhaustion",
                weight=58.0,
                description="Repeated visits to offices without resolution leading to chronic distress.",
                evidence_snippet="Repeated administrative barriers highlighted",
                indicator_group="NLP"
            )
        ],
        support_recommendations=[
            SupportRecommendation(
                id="REC-1002-1",
                case_id="CASE-1002",
                service_type=SupportServiceType.REHABILITATION,
                priority="High",
                status=SupportStatus.ASSIGNED,
                assigned_to="District Welfare Officer Belagavi",
                reason="Pending grant clearance and immediate ration/shelter assistance.",
                human_confirmed=True,
                human_notes="Expedited review requested under rehabilitation rules.",
                reviewed_by="Officer Suma Patil",
                updated_at=f"{yesterday_str} 05:15 PM"
            ),
            SupportRecommendation(
                id="REC-1002-2",
                case_id="CASE-1002",
                service_type=SupportServiceType.COUNSELLING,
                priority="Standard",
                status=SupportStatus.PENDING,
                assigned_to=None,
                reason="Supportive counselling for family under stress.",
                human_confirmed=False,
                human_notes="Pending consent from complainant.",
                reviewed_by="Officer Suma Patil",
                updated_at=f"{yesterday_str} 05:20 PM"
            )
        ],
        timeline=[
            {"time": "04:30 PM", "title": "Chat Complaint Received", "desc": "Chatbot session initiated.", "status": "done"},
            {"time": "04:32 PM", "title": "Consent Confirmed", "desc": "Consent granted for assessment.", "status": "done"},
            {"time": "04:33 PM", "title": "SVI Assessment: 52/100", "desc": "Categorized as MODERATE risk tier.", "status": "done"},
            {"time": "05:15 PM", "title": "Welfare Officer Assigned", "desc": "File flagged for expedited compensation.", "status": "done"}
        ],
        critical_safety_flag=False
    )

    # Case 004: Critical Risk Preset
    case_004 = CaseRecord(
        id="CASE-1004",
        case_number="NHAA-1004",
        created_at=f"{today_str} 11:10 AM",
        complainant_alias="Complainant-UP-9021",
        channel=ChannelType.VOICE,
        language="Hindi",
        raw_text=(
            "सर बचाओ! हथियार लेकर 10-15 लोग अभी हमारे घर के बाहर खड़े हैं! गेट तोड़ने की कोशिश कर रहे हैं... "
            "कह रहे हैं आज रात सबको जिंदा जला देंगे! पुलिस चौकी पर फोन नहीं लग रहा... हम कमरे में बंद हैं, बचा लीजिए!"
        ),
        masked_narrative="Imminent armed mob surrounding residence, violent intrusion underway, death threats shouted. Extreme emergency.",
        district="Meerut",
        state="Uttar Pradesh",
        consent_recorded=True,
        svi_score=94,
        risk_level=RiskLevel.CRITICAL,
        confidence=0.96,
        status="Pending",
        assigned_officer="Inspector V. K. Chauhan (Quick Response Team)",
        speech_metrics=SpeechMetrics(
            speech_rate_wpm=198.0,
            pause_count=8,
            avg_pause_duration_sec=1.8,
            pitch_variance_hz=68.2,
            voice_instability_index=0.91,
            hesitation_score=85.0,
            speech_intensity_db=84.5,
            tremor_detected=True,
            distress_indicators=[
                "Extreme hyper-arousal acoustic state (> 195 WPM)",
                "Severe vocal tremor and screaming intensity (> 84 dB)",
                "Panic respiration and acoustic instability"
            ]
        ),
        nlp_metrics=NLPMetrics(
            detected_language="Hindi",
            fear_score=98.0,
            anxiety_score=96.0,
            threat_intimidation_score=98.0,
            severe_distress_score=95.0,
            hopelessness_score=80.0,
            social_isolation_score=90.0,
            emotional_shock_score=94.0,
            vulnerability_score=96.0,
            self_harm_ideation=False,
            immediate_danger_detected=True,
            keywords_matched=["बचाओ", "हथियार", "घर के बाहर", "जिंदा जला", "मार देंगे"]
        ),
        emotion_metrics=EmotionMetrics(
            fear=0.98,
            sadness=0.40,
            anger=0.72,
            distress=0.96,
            anxiety=0.95,
            confusion=0.45,
            neutral=0.01,
            calm=0.01,
            dominant_emotion="Fear",
            confidence=0.96
        ),
        explainability=[
            ExplainabilityFactor(
                factor="CRITICAL SAFETY TRIGGER",
                weight=100.0,
                description="Active armed crowd attempting forced entry. Immediate threat to life detected.",
                evidence_snippet="Keywords: 'हथियार लेकर 10-15 लोग', 'घर के बाहर खड़े हैं', 'जिंदा जला देंगे'",
                indicator_group="Safety"
            ),
            ExplainabilityFactor(
                factor="Extreme Panic & Autonomic Distress",
                weight=98.0,
                description="Vocal intensity peaked at 84.5 dB with pitch variance of 68.2 Hz (screaming/panic profile).",
                evidence_snippet="Acoustic biometric emergency indicators",
                indicator_group="Speech"
            ),
            ExplainabilityFactor(
                factor="Total Isolation from Local Emergency Response",
                weight=90.0,
                description="Complainant states unable to reach local police station, trapped inside locked room.",
                evidence_snippet="Emergency communication breakdown",
                indicator_group="NLP"
            )
        ],
        support_recommendations=[
            SupportRecommendation(
                id="REC-1004-1",
                case_id="CASE-1004",
                service_type=SupportServiceType.EMERGENCY,
                priority="Urgent",
                status=SupportStatus.ASSIGNED,
                assigned_to="District Emergency PCR / 112 Control Room",
                reason="Imminent violent attack and attempted house break-in.",
                human_confirmed=True,
                human_notes="Urgent alert dispatched to nearest patrolling vehicle (Tiger-4). ETA 4 minutes.",
                reviewed_by="Inspector V. K. Chauhan",
                updated_at=f"{today_str} 11:12 AM"
            ),
            SupportRecommendation(
                id="REC-1004-2",
                case_id="CASE-1004",
                service_type=SupportServiceType.POLICE,
                priority="Urgent",
                status=SupportStatus.ASSIGNED,
                assigned_to="Circle Officer (CO) Rural Meerut",
                reason="Special protection team dispatch required.",
                human_confirmed=True,
                human_notes="Force mobilized under DSP supervision.",
                reviewed_by="Inspector V. K. Chauhan",
                updated_at=f"{today_str} 11:14 AM"
            ),
            SupportRecommendation(
                id="REC-1004-3",
                case_id="CASE-1004",
                service_type=SupportServiceType.MEDICAL,
                priority="Urgent",
                status=SupportStatus.PENDING,
                assigned_to=None,
                reason="Standby ambulance alerted in case of assault trauma.",
                human_confirmed=False,
                human_notes="108 ambulance dispatch alerted.",
                reviewed_by="Inspector V. K. Chauhan",
                updated_at=f"{today_str} 11:15 AM"
            )
        ],
        timeline=[
            {"time": "11:10 AM", "title": "Emergency Voice Call Received", "desc": "Victim in locked room connecting to national helpline.", "status": "done"},
            {"time": "11:10 AM", "title": "Consent Verified", "desc": "Emergency verbal consent recorded.", "status": "done"},
            {"time": "11:11 AM", "title": "CRITICAL SAFETY ALERT TRIGGERED", "desc": "SVI Score 94/100. Emergency multi-agency broadcast activated.", "status": "done"},
            {"time": "11:12 AM", "title": "Police Dispatch Alerted", "desc": "PCR vehicle dispatched with siren to disperse mob.", "status": "active"}
        ],
        critical_safety_flag=True
    )

    # Additional diverse cases for realistic table view and analytics
    extra_cases = [
        CaseRecord(
            id="CASE-1005",
            case_number="NHAA-1005",
            created_at=f"{today_str} 07:45 AM",
            complainant_alias="Complainant-TN-5421",
            channel=ChannelType.VOICE,
            language="Tamil",
            raw_text="எங்கள் தெருவில் தண்ணீர் பிடிக்க விடாமல் தடுத்து மிரட்டுகிறார்கள். சாதி சொல்லி அவமானப்படுத்தினார்கள்.",
            masked_narrative="Prohibition from accessing drinking water source accompanied by caste-based verbal abuse.",
            district="Madurai",
            state="Tamil Nadu",
            consent_recorded=True,
            svi_score=71,
            risk_level=RiskLevel.HIGH,
            confidence=0.88,
            status="Under Review",
            assigned_officer="Officer K. Saravanan",
            speech_metrics=None,
            nlp_metrics=None,
            emotion_metrics=None,
            explainability=[],
            support_recommendations=[],
            timeline=[],
            critical_safety_flag=False
        ),
        CaseRecord(
            id="CASE-1006",
            case_number="NHAA-1006",
            created_at=f"{yesterday_str} 02:15 PM",
            complainant_alias="Complainant-GJ-8812",
            channel=ChannelType.IVRS,
            language="Gujarati",
            raw_text="સરપંચે અમારી જમીન પર કબજો કરવાની ધમકી આપી છે. અમે પોલીસમાં ગયા પણ કોઈ ફરિયાદ નોંધી નથી.",
            masked_narrative="Encroachment threat by local village head. Unresponsive local station reported.",
            district="Ahmedabad",
            state="Gujarat",
            consent_recorded=True,
            svi_score=68,
            risk_level=RiskLevel.HIGH,
            confidence=0.84,
            status="Pending",
            assigned_officer=None,
            speech_metrics=None,
            nlp_metrics=None,
            emotion_metrics=None,
            explainability=[],
            support_recommendations=[],
            timeline=[],
            critical_safety_flag=False
        ),
        CaseRecord(
            id="CASE-1007",
            case_number="NHAA-1007",
            created_at=f"{two_days_ago} 11:20 AM",
            complainant_alias="Complainant-WB-3341",
            channel=ChannelType.MOBILE,
            language="Bengali",
            raw_text="দোকান খুলতে দিচ্ছে না। সামাজিক বয়কট ঘোষণা করেছে। কেউ আমাদের সাথে কথা বলছে না।",
            masked_narrative="Commercial boycott preventing victim from opening small shop. Severe social ostracization.",
            district="Birbhum",
            state="West Bengal",
            consent_recorded=True,
            svi_score=76,
            risk_level=RiskLevel.HIGH,
            confidence=0.91,
            status="Assigned",
            assigned_officer="Officer Subhashish Roy",
            speech_metrics=None,
            nlp_metrics=None,
            emotion_metrics=None,
            explainability=[],
            support_recommendations=[],
            timeline=[],
            critical_safety_flag=False
        ),
        CaseRecord(
            id="CASE-1008",
            case_number="NHAA-1008",
            created_at=f"{today_str} 10:45 AM",
            complainant_alias="Complainant-OD-7711",
            channel=ChannelType.TEXT,
            language="Odia",
            raw_text="ଆମ ଜମିରେ ଫସଲ କାଟି ନେଇଗଲେ। ବିରୋଧ କଲେ ମାରିବାକୁ ଧମକ ଦେଲେ।",
            masked_narrative="Forcible harvesting of standing crops followed by threats of physical violence upon protest.",
            district="Cuttack",
            state="Odia",
            consent_recorded=True,
            svi_score=64,
            risk_level=RiskLevel.MODERATE,
            confidence=0.82,
            status="Pending",
            assigned_officer=None,
            speech_metrics=None,
            nlp_metrics=None,
            emotion_metrics=None,
            explainability=[],
            support_recommendations=[],
            timeline=[],
            critical_safety_flag=False
        ),
        CaseRecord(
            id="CASE-1009",
            case_number="NHAA-1009",
            created_at=f"{today_str} 12:05 PM",
            complainant_alias="Complainant-KL-1928",
            channel=ChannelType.UPLOAD,
            language="Malayalam",
            raw_text="തൊഴിലിടത്തിൽ ജാതി വിവേചനം നേരിടുന്നു. പരാതി നൽകിയാൽ ജോലി കളയുമെന്ന് ഭീഷണിപ്പെടുത്തുന്നു.",
            masked_narrative="Workplace caste harassment and retaliation threats against lodging institutional complaint.",
            district="Kozhikode",
            state="Kerala",
            consent_recorded=True,
            svi_score=58,
            risk_level=RiskLevel.MODERATE,
            confidence=0.85,
            status="Under Review",
            assigned_officer="Adv. Anjali Menon",
            speech_metrics=None,
            nlp_metrics=None,
            emotion_metrics=None,
            explainability=[],
            support_recommendations=[],
            timeline=[],
            critical_safety_flag=False
        ),
        CaseRecord(
            id="CASE-1010",
            case_number="NHAA-1010",
            created_at=f"{yesterday_str} 09:10 AM",
            complainant_alias="Complainant-EN-4011",
            channel=ChannelType.PORTAL,
            language="English",
            raw_text="Seeking update on the rehabilitation relief package sanctioned under PoA Act rules in 2025.",
            masked_narrative="Status inquiry on government compensation disbursement timeline.",
            district="New Delhi",
            state="Delhi",
            consent_recorded=True,
            svi_score=19,
            risk_level=RiskLevel.LOW,
            confidence=0.96,
            status="Resolved",
            assigned_officer="Officer Preeti Sen",
            speech_metrics=None,
            nlp_metrics=None,
            emotion_metrics=None,
            explainability=[],
            support_recommendations=[],
            timeline=[],
            critical_safety_flag=False
        )
    ]

    return [case_nhaa_1024, case_001, case_002, case_004] + extra_cases

def build_demo_followups() -> List[FollowUpItem]:
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    return [
        FollowUpItem(
            id="FOL-001",
            case_id="CASE-1024",
            case_number="NHAA-1024",
            category=SupportServiceType.COUNSELLING,
            scheduled_date=today_str,
            scheduled_time="03:00 PM",
            assigned_to="Dr. S. Anuradha (Tele-MANAS)",
            status="Upcoming",
            notes="Follow-up psychological stabilization session to evaluate fear and sleep disruption.",
            historical_svi=[
                {"stage": "Initial Contact", "date": f"{today_str} 09:46 AM", "svi": 82},
                {"stage": "Post Assignment", "date": f"{today_str} 10:20 AM", "svi": 75}
            ]
        ),
        FollowUpItem(
            id="FOL-002",
            case_id="CASE-1024",
            case_number="NHAA-1024",
            category=SupportServiceType.LEGAL_AID,
            scheduled_date=tomorrow_str,
            scheduled_time="11:30 AM",
            assigned_to="Adv. K. Venkatesh (DLSA)",
            status="Upcoming",
            notes="Review draft of writ petition and FIR status regarding land boundary violations.",
            historical_svi=[
                {"stage": "Initial Contact", "date": f"{today_str} 09:46 AM", "svi": 82}
            ]
        ),
        FollowUpItem(
            id="FOL-003",
            case_id="CASE-1004",
            case_number="NHAA-1004",
            category=SupportServiceType.EMERGENCY,
            scheduled_date=today_str,
            scheduled_time="01:30 PM",
            assigned_to="Inspector V. K. Chauhan",
            status="Overdue",
            notes="On-site verification of PCR patrol presence and security assessment report.",
            historical_svi=[
                {"stage": "Initial Call", "date": f"{today_str} 11:11 AM", "svi": 94}
            ]
        ),
        FollowUpItem(
            id="FOL-004",
            case_id="CASE-1002",
            case_number="NHAA-1002",
            category=SupportServiceType.REHABILITATION,
            scheduled_date=yesterday_str,
            scheduled_time="04:00 PM",
            assigned_to="Officer Suma Patil",
            status="Completed",
            notes="Meeting conducted with District Collectorate for special relief sanctions.",
            historical_svi=[
                {"stage": "Initial Chat", "date": f"{yesterday_str} 04:33 PM", "svi": 52},
                {"stage": "Welfare Review", "date": f"{yesterday_str} 06:00 PM", "svi": 38}
            ]
        )
    ]

def build_demo_notifications() -> List[NotificationItem]:
    now = datetime.now()
    return [
        NotificationItem(
            id="NOTIF-01",
            title="CRITICAL CASE REQUIRES IMMEDIATE REVIEW",
            message="Case NHAA-1004 in Meerut, UP detected armed threat with SVI 94/100.",
            severity="critical",
            timestamp="10 mins ago",
            read=False,
            case_number="NHAA-1004"
        ),
        NotificationItem(
            id="NOTIF-02",
            title="High-Risk Case Forwarded for Review",
            message="Case NHAA-1024 (Telugu Voice) scored SVI 82/100 with active threat & isolation.",
            severity="warning",
            timestamp="45 mins ago",
            read=False,
            case_number="NHAA-1024"
        ),
        NotificationItem(
            id="NOTIF-03",
            title="Follow-up Overdue Alert",
            message="Protection check for Case NHAA-1004 is overdue by 15 minutes.",
            severity="warning",
            timestamp="1 hour ago",
            read=False,
            case_number="NHAA-1004"
        ),
        NotificationItem(
            id="NOTIF-04",
            title="Counselling Session Completed",
            message="Dr. S. Anuradha logged preliminary triage for Case NHAA-1024.",
            severity="success",
            timestamp="2 hours ago",
            read=True,
            case_number="NHAA-1024"
        )
    ]

def build_demo_audit_logs() -> List[AuditLogItem]:
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    return [
        AuditLogItem(
            id="LOG-001",
            timestamp=f"{today_str} 10:21 AM",
            user_name="Officer Rajesh Kumar",
            role=UserRole.OFFICER,
            action="Viewed Case Narrative & Evidence",
            case_id="NHAA-1024",
            access_type="READ",
            ip_address="10.24.110.14",
            details="Accessed decrypted speech transcript under emergency triage authorization."
        ),
        AuditLogItem(
            id="LOG-002",
            timestamp=f"{today_str} 10:05 AM",
            user_name="Officer Rajesh Kumar",
            role=UserRole.OFFICER,
            action="Assigned Legal Aid Counsel",
            case_id="NHAA-1024",
            access_type="ASSIGN",
            ip_address="10.24.110.14",
            details="Allocated Adv. K. Venkatesh (DLSA) under Section 15A of the PoA Act."
        ),
        AuditLogItem(
            id="LOG-003",
            timestamp=f"{today_str} 10:02 AM",
            user_name="Officer Rajesh Kumar",
            role=UserRole.OFFICER,
            action="Assigned Priority Psychological Support",
            case_id="NHAA-1024",
            access_type="ASSIGN",
            ip_address="10.24.110.14",
            details="Connected to Tele-MANAS trauma specialist Dr. S. Anuradha."
        ),
        AuditLogItem(
            id="LOG-004",
            timestamp=f"{today_str} 09:44 AM",
            user_name="System Gateway",
            role=UserRole.VICTIM,
            action="Consent Recorded",
            case_id="NHAA-1024",
            access_type="WRITE",
            ip_address="49.207.19.82",
            details="Complainant affirmed explicit consent for AI speech analysis and triage."
        ),
        AuditLogItem(
            id="LOG-005",
            timestamp=f"{today_str} 09:00 AM",
            user_name="Admin Suresh Varma",
            role=UserRole.ADMIN,
            action="Updated Risk Threshold Parameters",
            case_id=None,
            access_type="WRITE",
            ip_address="10.24.100.2",
            details="Adjusted critical trigger cutoff to 85 SVI and NLP sentiment weighting."
        )
    ]
