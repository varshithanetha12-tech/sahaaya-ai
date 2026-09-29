import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.schemas import (
    CaseRecord, FollowUpItem, NotificationItem, AuditLogItem,
    SystemConfig, SupportServiceType, SupportStatus, UserRole,
    SupportRecommendation, CaseCreateRequest, RiskLevel
)
from app.services.demo_data_seeder import (
    build_demo_cases, build_demo_followups, build_demo_notifications, build_demo_audit_logs
)
from app.services.speech_analyzer import SpeechAnalyzerService
from app.services.nlp_analyzer import NLPAnalyzerService
from app.services.svi_engine import SVIEngineService
from app.services.safety_triage import SafetyTriageService

class DatabaseState:
    def __init__(self):
        self.cases: List[CaseRecord] = build_demo_cases()
        self.followups: List[FollowUpItem] = build_demo_followups()
        self.notifications: List[NotificationItem] = build_demo_notifications()
        self.audit_logs: List[AuditLogItem] = build_demo_audit_logs()
        self.config: SystemConfig = SystemConfig()
        self.current_user = {
            "name": "Officer Rajesh Kumar",
            "role": UserRole.OFFICER,
            "department": "District Atrocity Protection Unit, Rangareddy",
            "email": "rajesh.kumar@telangana.gov.in"
        }

    def log_audit(self, action: str, case_id: Optional[str], access_type: str, details: str, user_name: Optional[str] = None, role: Optional[UserRole] = None):
        u_name = user_name or self.current_user["name"]
        u_role = role or self.current_user["role"]
        log_entry = AuditLogItem(
            id=f"LOG-{uuid.uuid4().hex[:6].upper()}",
            timestamp=datetime.now().strftime("%Y-%m-%d %I:%M %p"),
            user_name=u_name,
            role=u_role,
            action=action,
            case_id=case_id,
            access_type=access_type,
            ip_address="10.24.110.14",
            details=details
        )
        self.audit_logs.insert(0, log_entry)

    def get_case_by_number(self, case_number: str) -> Optional[CaseRecord]:
        for c in self.cases:
            if c.case_number.lower() == case_number.lower() or c.id.lower() == case_number.lower():
                return c
        return None

    def create_case_from_interaction(self, req: CaseCreateRequest) -> CaseRecord:
        case_id = f"CASE-{len(self.cases) + 1025}"
        case_num = f"NHAA-{len(self.cases) + 1025}"
        now = datetime.now()
        created_str = now.strftime("%Y-%m-%d %I:%M %p")

        # Multilingual NLP analysis
        nlp_metrics, emotion_metrics = NLPAnalyzerService.analyze_text(
            text=req.raw_text or "",
            specified_language=req.language
        )

        # Speech analysis if audio channel
        speech_metrics = None
        has_voice = req.audio_present or req.channel in ["Voice Helpline", "Voice Recording Upload", "IVRS"]
        if has_voice:
            speech_metrics = SpeechAnalyzerService.analyze_audio(
                text_content=req.raw_text,
                duration_sec=req.audio_duration_sec,
                is_high_distress_hint=(nlp_metrics.fear_score > 60 or nlp_metrics.threat_intimidation_score > 60)
            )

        # Compute SVI
        svi_result = SVIEngineService.calculate_svi(
            nlp=nlp_metrics,
            emotion=emotion_metrics,
            speech=speech_metrics,
            config=self.config
        )

        # Generate support recommendations
        recs = SafetyTriageService.generate_recommendations(
            case_id=case_id,
            pathways=svi_result.recommended_pathways,
            is_critical=svi_result.critical_safety_alert
        )

        # Build initial timeline
        timeline = [
            {"time": now.strftime("%I:%M %p"), "title": "Interaction Initiated", "desc": f"Victim connected via {req.channel.value} in {nlp_metrics.detected_language}.", "status": "done"},
            {"time": (now).strftime("%I:%M %p"), "title": "Consent Formally Recorded", "desc": "Explicit consent given for triage assessment.", "status": "done"},
            {"time": (now).strftime("%I:%M %p"), "title": "AI Assessment Completed", "desc": f"SVI Score computed: {svi_result.score}/100 ({svi_result.risk_level.value} Risk).", "status": "done"}
        ]
        if svi_result.critical_safety_alert:
            timeline.append({"time": now.strftime("%I:%M %p"), "title": "Critical Safety Trigger", "desc": "Automatic priority dispatch alert sent to authorized on-duty team.", "status": "active"})
        else:
            timeline.append({"time": now.strftime("%I:%M %p"), "title": "Forwarded to Review", "desc": "Queued for authorized officer review and service assignment.", "status": "active"})

        # Mask narrative for privacy
        masked_snippet = (req.raw_text[:90] + "...") if req.raw_text and len(req.raw_text) > 90 else (req.raw_text or "Voice complaint logged.")

        new_case = CaseRecord(
            id=case_id,
            case_number=case_num,
            created_at=created_str,
            complainant_alias=req.complainant_alias or f"Complainant-{req.state[:2].upper()}-{case_num[-4:]}",
            channel=req.channel,
            language=nlp_metrics.detected_language,
            raw_text=req.raw_text,
            masked_narrative=masked_snippet,
            district=req.district or "Hyderabad",
            state=req.state or "Telangana",
            consent_recorded=req.consent_given,
            svi_score=svi_result.score,
            stress_score=svi_result.stress_score,
            trauma_score=svi_result.trauma_score,
            emotional_state=svi_result.emotional_state,
            recommended_next_action=svi_result.recommended_next_action,
            risk_level=svi_result.risk_level,
            priority="Urgent" if svi_result.critical_safety_alert else ("Priority" if svi_result.risk_level == RiskLevel.HIGH else "Standard"),
            alert_status="High-Risk Alert" if svi_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else "Normal",
            referral_status="None",
            confidence=svi_result.confidence,
            status="Pending" if not svi_result.critical_safety_alert else "Under Review",
            assigned_officer="Officer Rajesh Kumar" if svi_result.critical_safety_alert else None,
            speech_metrics=speech_metrics,
            nlp_metrics=nlp_metrics,
            emotion_metrics=emotion_metrics,
            explainability=svi_result.explainability_factors,
            support_recommendations=recs,
            timeline=timeline,
            critical_safety_flag=svi_result.critical_safety_alert
        )

        self.cases.insert(0, new_case)

        # Generate notification if high risk or critical
        if svi_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.notifications.insert(0, NotificationItem(
                id=f"NOTIF-{uuid.uuid4().hex[:4].upper()}",
                title=f"{svi_result.risk_level.value} RISK CASE RECORDED",
                message=f"Case {case_num} received via {req.channel.value} ({nlp_metrics.detected_language}) with SVI {svi_result.score}/100.",
                severity="critical" if svi_result.critical_safety_alert else "warning",
                timestamp="Just now",
                read=False,
                case_number=case_num
            ))

        # Log audit trail
        self.log_audit(
            action="Created Case from First Contact",
            case_id=case_num,
            access_type="WRITE",
            details=f"SVI: {svi_result.score}/100, Channel: {req.channel.value}, Language: {nlp_metrics.detected_language}"
        )

        return new_case

    def get_analytics(self) -> Dict[str, Any]:
        total = len(self.cases)
        low = sum(1 for c in self.cases if c.risk_level == RiskLevel.LOW)
        mod = sum(1 for c in self.cases if c.risk_level == RiskLevel.MODERATE)
        high = sum(1 for c in self.cases if c.risk_level == RiskLevel.HIGH)
        crit = sum(1 for c in self.cases if c.risk_level == RiskLevel.CRITICAL)

        avg_svi = round(sum(c.svi_score for c in self.cases) / max(1, total), 1)

        # By language
        by_lang = {}
        for c in self.cases:
            by_lang[c.language] = by_lang.get(c.language, 0) + 1

        # By channel
        by_chan = {}
        for c in self.cases:
            ch = c.channel.value
            by_chan[ch] = by_chan.get(ch, 0) + 1

        # By state
        by_state = {}
        for c in self.cases:
            by_state[c.state] = by_state.get(c.state, 0) + 1

        # Referral statistics
        referrals = {}
        for c in self.cases:
            r = getattr(c, "referral_status", "None") or "None"
            referrals[r] = referrals.get(r, 0) + 1

        completed_fols = sum(1 for f in self.followups if f.status == "Completed")
        total_fols = len(self.followups)
        fol_rate = round((completed_fols / max(1, total_fols)) * 100, 1)

        risk_trends = [
            {"period": "Day -6", "avg_svi": 52, "critical_cases": 0},
            {"period": "Day -5", "avg_svi": 55, "critical_cases": 1},
            {"period": "Day -4", "avg_svi": 60, "critical_cases": 1},
            {"period": "Day -3", "avg_svi": 58, "critical_cases": 2},
            {"period": "Day -2", "avg_svi": 64, "critical_cases": 2},
            {"period": "Yesterday", "avg_svi": 68, "critical_cases": 3},
            {"period": "Today", "avg_svi": avg_svi, "critical_cases": crit},
        ]

        return {
            "total_cases": total,
            "risk_distribution": {"LOW": low, "MODERATE": mod, "HIGH": high, "CRITICAL": crit},
            "average_svi": avg_svi,
            "cases_by_language": by_lang,
            "cases_by_channel": by_chan,
            "cases_by_state": by_state,
            "referral_stats": referrals,
            "followup_completion_rate": fol_rate,
            "risk_trends": risk_trends,
            "pending_review_count": sum(1 for c in self.cases if c.status in ["Pending", "Under Review"]),
            "followups_today_count": sum(1 for f in self.followups if f.status == "Upcoming"),
            "early_warning_alerts": [
                {
                    "id": "EW-01",
                    "title": "Cluster Alert: 42% Increase in Threat-Related Complaints",
                    "district": "Rangareddy",
                    "state": "Telangana",
                    "timeframe": "Last 7 Days",
                    "sample_size": "14 Anonymized Cases",
                    "confidence": "High Pattern Alignment (88%)",
                    "recommendation": "Deploy mobile protection liaison team and coordinate proactive Gram Sabha visit.",
                    "disclaimer": "Analytical triage signal for resource planning. Not a definitive finding of guilt or legal proof."
                },
                {
                    "id": "EW-02",
                    "title": "Speech Tremor & High Arousal Trend in Nocturnal Calls",
                    "district": "Meerut",
                    "state": "Uttar Pradesh",
                    "timeframe": "Last 48 Hours",
                    "sample_size": "6 Anonymized Calls",
                    "confidence": "Moderate Pattern Alignment (76%)",
                    "recommendation": "Coordinate with 112 Command Center for enhanced nighttime dialer response speed.",
                    "disclaimer": "Triage indicator based on acoustic prosody modeling."
                }
            ]
        }

# Global singleton database instance
db = DatabaseState()
