from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ChannelType(str, Enum):
    VOICE = "Voice Helpline"
    CHAT = "Chatbot"
    PORTAL = "Integrated Portal"
    MOBILE = "Mobile Application"
    IVRS = "IVRS"
    TEXT = "Text Complaint"
    UPLOAD = "Voice Recording Upload"

class UserRole(str, Enum):
    VICTIM = "Victim/User"
    COUNSELLOR = "Counsellor"
    LEGAL = "Legal Professional"
    OFFICER = "Authorized Officer"
    ADMIN = "Administrator"

class SupportServiceType(str, Enum):
    COUNSELLING = "Counselling"
    LEGAL_AID = "Legal Aid"
    MEDICAL = "Medical Assistance"
    POLICE = "Police Support"
    WITNESS_PROTECTION = "Witness Protection"
    EMERGENCY = "Emergency Support"
    REHABILITATION = "Rehabilitation & Welfare"

class SupportStatus(str, Enum):
    PENDING = "Pending Review"
    ASSIGNED = "Assigned"
    REJECTED = "Rejected"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class SpeechMetrics(BaseModel):
    speech_rate_wpm: float = 120.0
    pause_count: int = 4
    avg_pause_duration_sec: float = 1.2
    pitch_variance_hz: float = 24.5
    voice_instability_index: float = 0.35  # 0.0 to 1.0
    hesitation_score: float = 25.0         # 0 to 100
    speech_intensity_db: float = 62.0
    tremor_detected: bool = False
    distress_indicators: List[str] = []

class NLPMetrics(BaseModel):
    detected_language: str = "Telugu"
    fear_score: float = 0.0          # 0 to 100
    anxiety_score: float = 0.0
    threat_intimidation_score: float = 0.0
    severe_distress_score: float = 0.0
    hopelessness_score: float = 0.0
    social_isolation_score: float = 0.0
    emotional_shock_score: float = 0.0
    vulnerability_score: float = 0.0
    self_harm_ideation: bool = False
    immediate_danger_detected: bool = False
    keywords_matched: List[str] = []

class EmotionMetrics(BaseModel):
    fear: float = 0.0
    sadness: float = 0.0
    anger: float = 0.0
    distress: float = 0.0
    anxiety: float = 0.0
    confusion: float = 0.0
    neutral: float = 0.0
    calm: float = 0.0
    dominant_emotion: str = "Neutral"
    confidence: float = 0.85

class ExplainabilityFactor(BaseModel):
    factor: str
    weight: float
    description: str
    evidence_snippet: Optional[str] = None
    indicator_group: str  # "Speech", "NLP", "Emotion", "Safety"

class SVIResult(BaseModel):
    score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    is_uncertain: bool = False
    uncertainty_note: Optional[str] = None
    breakdown: Dict[str, float]
    explainability_factors: List[ExplainabilityFactor]
    summary_text: str
    critical_safety_alert: bool = False
    escalation_required: bool = False
    recommended_pathways: List[SupportServiceType]
    disclaimer: str = (
        "AI-assisted triage indicator. Not a medical or clinical diagnosis. "
        "All critical recommendations require authorized human professional review."
    )

class CaseCreateRequest(BaseModel):
    channel: ChannelType
    language: str
    raw_text: Optional[str] = None
    audio_present: bool = False
    audio_duration_sec: Optional[float] = None
    audio_data_base64: Optional[str] = None
    consent_given: bool = True
    district: Optional[str] = "Hyderabad"
    state: Optional[str] = "Telangana"
    complainant_alias: Optional[str] = "Complainant-Anonymous"

class SupportRecommendation(BaseModel):
    id: str
    case_id: str
    service_type: SupportServiceType
    priority: str  # "Urgent", "High", "Standard"
    status: SupportStatus = SupportStatus.PENDING
    assigned_to: Optional[str] = None
    reason: str
    human_confirmed: bool = False
    human_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    updated_at: str

class CaseRecord(BaseModel):
    id: str
    case_number: str  # e.g., NHAA-1024
    created_at: str
    complainant_alias: str
    channel: ChannelType
    language: str
    raw_text: Optional[str] = None
    district: str
    state: str
    consent_recorded: bool
    svi_score: int
    risk_level: RiskLevel
    confidence: float
    status: str  # "Pending", "Under Review", "Assigned", "Resolved"
    assigned_officer: Optional[str] = None
    speech_metrics: Optional[SpeechMetrics] = None
    nlp_metrics: Optional[NLPMetrics] = None
    emotion_metrics: Optional[EmotionMetrics] = None
    explainability: List[ExplainabilityFactor] = []
    support_recommendations: List[SupportRecommendation] = []
    timeline: List[Dict[str, Any]] = []
    critical_safety_flag: bool = False
    masked_narrative: str = ""

class FollowUpItem(BaseModel):
    id: str
    case_id: str
    case_number: str
    category: SupportServiceType
    scheduled_date: str
    scheduled_time: str
    assigned_to: str
    status: str  # "Upcoming", "Overdue", "Completed"
    notes: Optional[str] = None
    historical_svi: List[Dict[str, Any]] = []  # e.g., [{"date": "2026-09-20", "svi": 82}]

class SupportResource(BaseModel):
    id: str
    name: str
    category: SupportServiceType
    state: str
    district: str
    phone: str
    email: Optional[str] = None
    address: str
    available_24x7: bool
    languages: List[str]
    verified: bool = True
    active_capacity: str = "Available"

class NotificationItem(BaseModel):
    id: str
    title: str
    message: str
    severity: str  # "critical", "warning", "info", "success"
    timestamp: str
    read: bool = False
    case_number: Optional[str] = None

class AuditLogItem(BaseModel):
    id: str
    timestamp: str
    user_name: str
    role: UserRole
    action: str
    case_id: Optional[str] = None
    access_type: str  # "READ", "WRITE", "ASSIGN", "EXPORT", "ALERT"
    ip_address: str
    details: str

class SystemConfig(BaseModel):
    threshold_low_max: int = 35
    threshold_mod_max: int = 65
    threshold_high_max: int = 84
    speech_weight: float = 0.30
    nlp_weight: float = 0.45
    emotion_weight: float = 0.25
    confidence_threshold: float = 0.75
    anonymize_analytics: bool = True
    auto_detect_language: bool = True
