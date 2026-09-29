from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.schemas import SupportServiceType, SupportRecommendation, SupportStatus

class SafetyTriageService:
    """
    Critical Safety Triage and Escalation Service.
    Enforces Human-in-the-Loop decision making: AI only flags and recommends,
    while authorized human professionals confirm and assign support actions.
    """

    @classmethod
    def generate_recommendations(
        cls,
        case_id: str,
        pathways: List[SupportServiceType],
        is_critical: bool = False
    ) -> List[SupportRecommendation]:
        recs = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        priority_level = "Urgent" if is_critical else "High"

        reason_map = {
            SupportServiceType.COUNSELLING: "Elevated psychological distress, fear, and acute emotional trauma signals detected.",
            SupportServiceType.LEGAL_AID: "Coercive threats, land intimidation, social boycott, or atrocity complaint elements present.",
            SupportServiceType.MEDICAL: "Severe physiological distress indicators, trembling, shock, or potential medical urgency.",
            SupportServiceType.POLICE: "Active harassment, physical threats, or imminent safety risk reported.",
            SupportServiceType.WITNESS_PROTECTION: "Vulnerability to retaliation, community boycott, or continued coercion.",
            SupportServiceType.EMERGENCY: "Immediate danger indicators or severe vulnerability requiring rapid multi-agency dispatch.",
            SupportServiceType.REHABILITATION: "Social exclusion, economic dislocation, or displacement from residence."
        }

        for idx, pathway in enumerate(pathways):
            recs.append(SupportRecommendation(
                id=f"REC-{case_id}-{idx+1}",
                case_id=case_id,
                service_type=pathway,
                priority=priority_level if idx < 2 else "Standard",
                status=SupportStatus.PENDING,
                assigned_to=None,
                reason=reason_map.get(pathway, "AI triage detected relevant distress indicators."),
                human_confirmed=False,
                human_notes=None,
                reviewed_by=None,
                updated_at=now_str
            ))

        return recs

    @classmethod
    def simulate_emergency_action(
        cls,
        action_name: str,
        case_number: str,
        actor_name: str = "Officer-in-Charge"
    ) -> Dict[str, Any]:
        """
        Simulates instantaneous emergency notification dispatched to authorized personnel.
        """
        timestamp = datetime.now().strftime("%I:%M %p")
        return {
            "success": True,
            "action": action_name,
            "case_number": case_number,
            "dispatched_by": actor_name,
            "timestamp": timestamp,
            "status": "DISPATCHED_TO_ON_DUTY_TEAM",
            "message": f"Action '{action_name}' successfully triggered for Case {case_number}. On-duty team alerted."
        }
