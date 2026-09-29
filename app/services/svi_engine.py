from typing import Dict, Any, List, Optional
from app.models.schemas import (
    SpeechMetrics, NLPMetrics, EmotionMetrics, SVIResult,
    RiskLevel, ExplainabilityFactor, SupportServiceType, SystemConfig
)

class SVIEngineService:
    """
    Stress Vulnerability Index (SVI) Engine.
    Combines prosodic speech indicators, multilingual NLP threat/distress scores,
    and emotional arousal signals into a standardized 0-100 triage prioritization index.
    """

    @classmethod
    def calculate_svi(
        cls,
        nlp: NLPMetrics,
        emotion: EmotionMetrics,
        speech: Optional[SpeechMetrics] = None,
        config: Optional[SystemConfig] = None
    ) -> SVIResult:
        cfg = config or SystemConfig()

        # NLP Composite Component (0 - 100)
        nlp_score = (
            nlp.threat_intimidation_score * 0.35 +
            nlp.fear_score * 0.25 +
            nlp.severe_distress_score * 0.20 +
            nlp.social_isolation_score * 0.10 +
            nlp.anxiety_score * 0.10
        )

        # Emotion Composite Component (0 - 100)
        emotion_score = (
            emotion.fear * 30.0 +
            emotion.distress * 30.0 +
            emotion.anger * 20.0 +
            emotion.anxiety * 15.0 +
            emotion.sadness * 5.0
        )

        # Speech Prosodic Component (0 - 100)
        if speech:
            speech_score = (
                speech.hesitation_score * 0.35 +
                (speech.voice_instability_index * 100.0) * 0.35 +
                min(100.0, speech.pause_count * 12.0) * 0.20 +
                min(100.0, speech.pitch_variance_hz * 1.5) * 0.10
            )
            raw_svi = (
                (nlp_score * cfg.nlp_weight) +
                (speech_score * cfg.speech_weight) +
                (emotion_score * cfg.emotion_weight)
            )
        else:
            speech_score = 0.0
            # Normalize without speech channel
            nlp_w = 0.65
            emo_w = 0.35
            raw_svi = (nlp_score * nlp_w) + (emotion_score * emo_w)

        # Safety overrides: immediate danger or suicidal ideation automatically escalates
        critical_safety_alert = False
        escalation_required = False

        if nlp.immediate_danger_detected or nlp.self_harm_ideation:
            raw_svi = max(raw_svi, 88.0)
            critical_safety_alert = True
            escalation_required = True
        elif raw_svi >= cfg.threshold_high_max:
            escalation_required = True

        final_score = int(round(max(5.0, min(100.0, raw_svi))))

        # Determine Risk Level based on configurable thresholds
        if final_score <= cfg.threshold_low_max:
            risk_level = RiskLevel.LOW
        elif final_score <= cfg.threshold_mod_max:
            risk_level = RiskLevel.MODERATE
        elif final_score <= cfg.threshold_high_max:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
            critical_safety_alert = True
            escalation_required = True

        # AI Confidence & Uncertainty Modeling
        confidence = emotion.confidence
        if speech:
            confidence = min(0.95, (confidence * 0.6) + 0.35)
        
        is_uncertain = confidence < cfg.confidence_threshold
        uncertainty_note = None
        if is_uncertain:
            uncertainty_note = (
                f"Assessment confidence ({int(confidence*100)}%) is below optimal reliability threshold "
                f"({int(cfg.confidence_threshold*100)}%). Narrative length or acoustic clarity was limited. "
                "Immediate human review strongly advised."
            )

        # Explainability Factor Generation ("Why this score?")
        factors: List[ExplainabilityFactor] = []

        if nlp.threat_intimidation_score >= 40:
            factors.append(ExplainabilityFactor(
                factor="Threat & Intimidation References",
                weight=round(nlp.threat_intimidation_score, 1),
                description=f"Identified {len(nlp.keywords_matched)} explicit threat/violence or boycott markers in dialogue.",
                evidence_snippet=", ".join(nlp.keywords_matched[:3]) if nlp.keywords_matched else "Threat markers detected",
                indicator_group="NLP"
            ))

        if nlp.fear_score >= 35:
            factors.append(ExplainabilityFactor(
                factor="Strong Fear-Related Language",
                weight=round(nlp.fear_score, 1),
                description="Complainant expresses acute dread, trembling, or panic regarding their immediate situation.",
                evidence_snippet="Expressions of intense fear or helplessness recorded",
                indicator_group="NLP"
            ))

        if nlp.social_isolation_score >= 40:
            factors.append(ExplainabilityFactor(
                factor="Social Isolation & Helplessness",
                weight=round(nlp.social_isolation_score, 1),
                description="References indicate displacement, social boycott, or lack of local community/family support.",
                evidence_snippet="Lack of external support network identified",
                indicator_group="NLP"
            ))

        if speech and speech.voice_instability_index >= 0.50:
            factors.append(ExplainabilityFactor(
                factor="Acoustic Voice Tremor & Instability",
                weight=round(speech.voice_instability_index * 100, 1),
                description=f"Voice tremor index at {int(speech.voice_instability_index*100)}% with significant pitch variations ({speech.pitch_variance_hz} Hz).",
                evidence_snippet="Prosodic pitch variance indicates heightened physiological arousal",
                indicator_group="Speech"
            ))

        if speech and speech.pause_count >= 4:
            factors.append(ExplainabilityFactor(
                factor="Frequent Conversational Hesitation & Pauses",
                weight=round(min(100.0, speech.pause_count * 15.0), 1),
                description=f"Recorded {speech.pause_count} extended pauses with average duration of {speech.avg_pause_duration_sec}s.",
                evidence_snippet="Frequent narrative interruptions and hesitation patterns",
                indicator_group="Speech"
            ))

        if emotion.fear > 0.4 or emotion.distress > 0.4:
            factors.append(ExplainabilityFactor(
                factor="Elevated Emotional Distress Profile",
                weight=round(max(emotion.fear, emotion.distress) * 100, 1),
                description=f"Dominant emotion evaluated as {emotion.dominant_emotion} with distress magnitude of {int(emotion.distress*100)}%.",
                evidence_snippet=f"Dominant affective signal: {emotion.dominant_emotion}",
                indicator_group="Emotion"
            ))

        if critical_safety_alert:
            factors.insert(0, ExplainabilityFactor(
                factor="CRITICAL SAFETY TRIGGER",
                weight=100.0,
                description="Urgent physical threat, active harassment outside residence, or self-harm marker detected.",
                evidence_snippet="Requires immediate human intervention and emergency response",
                indicator_group="Safety"
            ))

        # If no severe factors, provide baseline factors
        if not factors:
            factors.append(ExplainabilityFactor(
                factor="Baseline Procedural Inquiry",
                weight=20.0,
                description="Language is informational and calm. Minimal distress indicators identified.",
                evidence_snippet="Calm informational tone",
                indicator_group="NLP"
            ))

        # Recommended Support Pathways based on detected indicators
        pathways = []
        if nlp.fear_score > 30 or emotion.distress > 0.4 or final_score >= 40:
            pathways.append(SupportServiceType.COUNSELLING)
        if nlp.threat_intimidation_score > 35 or "boycott" in str(nlp.keywords_matched).lower():
            pathways.append(SupportServiceType.LEGAL_AID)
        if speech and speech.voice_instability_index > 0.65 or final_score >= 65:
            pathways.append(SupportServiceType.MEDICAL)
        if critical_safety_alert or nlp.threat_intimidation_score > 70:
            pathways.append(SupportServiceType.POLICE)
            pathways.append(SupportServiceType.WITNESS_PROTECTION)
            pathways.append(SupportServiceType.EMERGENCY)
        if nlp.social_isolation_score > 40:
            pathways.append(SupportServiceType.REHABILITATION)

        # Deduplicate and ensure at least Counselling is present
        if not pathways:
            pathways = [SupportServiceType.COUNSELLING]

        # Calculate explicit Stress Score and Trauma Indicator Score
        speech_stress = (speech.hesitation_score * 0.4 + speech.voice_instability_index * 100 * 0.4 + min(100.0, speech.pause_count * 15.0) * 0.2) if speech else 25.0
        emo_stress = (emotion.fear * 40.0 + emotion.anxiety * 30.0 + emotion.distress * 30.0)
        nlp_stress = (nlp.fear_score * 0.5 + nlp.anxiety_score * 0.5)
        calc_stress = (speech_stress * 0.35 + emo_stress * 0.35 + nlp_stress * 0.30) if speech else (emo_stress * 0.5 + nlp_stress * 0.5)
        stress_score = int(round(max(5.0, min(100.0, calc_stress))))

        calc_trauma = (
            nlp.threat_intimidation_score * 0.40 +
            nlp.social_isolation_score * 0.25 +
            nlp.severe_distress_score * 0.20 +
            nlp.emotional_shock_score * 0.15
        )
        trauma_score = int(round(max(5.0, min(100.0, calc_trauma))))

        if critical_safety_alert or final_score >= 85:
            stress_score = max(stress_score, 88)
            trauma_score = max(trauma_score, 90)

        # Emotional State Synthesis
        if critical_safety_alert or risk_level == RiskLevel.CRITICAL:
            emotional_state = "Acute Panic & Imminent Threat Dread"
        elif risk_level == RiskLevel.HIGH:
            emotional_state = "Severe Fear, Threat Trauma & Isolation"
        elif risk_level == RiskLevel.MODERATE:
            emotional_state = "Situational Anxiety & Prolonged Distress"
        else:
            emotional_state = "Calm & Informational"

        # Risk-Specific Response Guidance
        if risk_level == RiskLevel.LOW:
            recommended_next_action = "Self-help guidance provided. Optional check-in available if distress increases."
        elif risk_level == RiskLevel.MODERATE:
            recommended_next_action = "Professional counselor consultation recommended. Supportive resources & follow-up scheduling."
        elif risk_level == RiskLevel.HIGH:
            recommended_next_action = "Immediate counselor referral initiated. Authorized officer notification dispatched for priority follow-up."
        else:
            recommended_next_action = "CRITICAL CRISIS ALERT: Emergency crisis guidance activated. Multi-agency protection referral dispatched."

        summary_text = (
            f"SVI Score of {final_score}/100 categorized as {risk_level.value} risk "
            f"(Stress Score: {stress_score}/100, Trauma Score: {trauma_score}/100). "
            f"Emotional state: {emotional_state}. "
            f"{'CRITICAL: Immediate escalation to authorized officer required.' if escalation_required else 'Authorized human review recommended for service allocation.'}"
        )

        breakdown = {
            "Stress Score": float(stress_score),
            "Trauma Indicator Score": float(trauma_score),
            "Distress Indicators": round(nlp.severe_distress_score, 1),
            "Fear Indicators": round(nlp.fear_score, 1),
            "Threat Indicators": round(nlp.threat_intimidation_score, 1),
            "Speech Hesitation": round(speech.hesitation_score if speech else 20.0, 1),
            "Emotional Intensity": round(emotion_score, 1),
            "Vulnerability Indicators": round(nlp.vulnerability_score, 1),
            "Immediate Safety Concerns": 100.0 if critical_safety_alert else 0.0
        }

        return SVIResult(
            score=final_score,
            risk_level=risk_level,
            stress_score=stress_score,
            trauma_score=trauma_score,
            emotional_state=emotional_state,
            recommended_next_action=recommended_next_action,
            confidence=round(confidence, 2),
            is_uncertain=is_uncertain,
            uncertainty_note=uncertainty_note,
            breakdown=breakdown,
            explainability_factors=factors,
            summary_text=summary_text,
            critical_safety_alert=critical_safety_alert,
            escalation_required=escalation_required,
            recommended_pathways=list(dict.fromkeys(pathways))
        )
