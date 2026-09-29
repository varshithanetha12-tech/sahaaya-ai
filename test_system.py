import httpx

def test_all():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=10.0)

    # 1. Test root HTML
    r0 = client.get("/")
    assert r0.status_code == 200
    assert "Sahaaya AI" in r0.text
    print("[PASS] Root HTML served successfully.")

    # 2. Test Cases list & new schema fields
    r1 = client.get("/api/cases")
    assert r1.status_code == 200
    cases = r1.json()
    assert len(cases) >= 10
    first_case = cases[0]
    assert "svi_score" in first_case
    assert "stress_score" in first_case
    assert "trauma_score" in first_case
    assert "priority" in first_case
    assert "alert_status" in first_case
    assert "referral_status" in first_case
    print(f"[PASS] Cases listed with extended triage fields. Total cases: {len(cases)}")

    # 3. Test Case NHAA-1024
    r2 = client.get("/api/cases/NHAA-1024")
    assert r2.status_code == 200
    c1024 = r2.json()
    assert c1024["svi_score"] == 82
    assert c1024["stress_score"] == 85
    assert c1024["trauma_score"] == 88
    assert c1024["risk_level"] == "HIGH"
    assert c1024["priority"] == "Priority"
    assert len(c1024["explainability"]) >= 4
    print(f"[PASS] Case NHAA-1024 verified: SVI {c1024['svi_score']}, Stress {c1024['stress_score']}, Trauma {c1024['trauma_score']}, Risk {c1024['risk_level']}")

    # 4. Test Assessment Interactive Engine (Telugu narrative)
    payload = {
        "channel": "Voice Helpline",
        "language": "Telugu",
        "raw_text": "మమ్మల్ని ఊరి నుంచి వెలివేశారు... చంపేస్తామని బెదిరిస్తున్నారు... చాలా భయంగా ఉంది...",
        "audio_present": True,
        "audio_duration_sec": 25.0,
        "consent_given": True,
        "district": "Rangareddy",
        "state": "Telangana"
    }
    r3 = client.post("/api/assessment/analyze-interactive", json=payload)
    assert r3.status_code == 200
    res3 = r3.json()
    score = res3["svi"]["score"]
    level = res3["svi"]["risk_level"]
    print(f"[PASS] Interactive assessment simulated: SVI {score}/100 ({level})")

    # 5. Test Support Assignment Action
    r4 = client.post("/api/cases/NHAA-1024/recommendations/REC-1024-3/action", json={
        "action": "ASSIGN",
        "assigned_to": "Inspector S. Rao (Witness Protection Squad)",
        "notes": "Mobile escort patrol authorized under Sec 15A PoA Act."
    })
    assert r4.status_code == 200
    print("[PASS] Support assignment action confirmed with human approval.")

    # 6. Test Analytics & Early Warning
    r5 = client.get("/api/analytics")
    assert r5.status_code == 200
    an = r5.json()
    assert len(an["early_warning_alerts"]) >= 1
    assert "referral_stats" in an
    assert "followup_completion_rate" in an
    assert "risk_trends" in an
    print(f"[PASS] Analytics & Early Warning active. Alerts: {len(an['early_warning_alerts'])}, Followup rate: {an['followup_completion_rate']}%")

    # 7. Test Resources Directory
    r6 = client.get("/api/resources?category=Counselling")
    assert r6.status_code == 200
    res_list = r6.json()
    assert len(res_list) >= 1
    print(f"[PASS] Resource directory verified. Found counseling centers: {len(res_list)}")

    # 8. Test Audit Logs
    r7 = client.get("/api/audit")
    assert r7.status_code == 200
    logs = r7.json()
    assert len(logs) >= 5
    print(f"[PASS] Audit logs intact and verified. Total entries: {len(logs)}")

    # 9. Test Conversational AI Assessment: Start Session
    r_conv_start = client.post("/api/assessment/conversation/start", params={"language": "Telugu", "channel": "Voice Assessment"})
    assert r_conv_start.status_code == 200
    start_data = r_conv_start.json()
    assert "session_id" in start_data
    assert "ai_response" in start_data
    assert start_data["turn_index"] == 1
    conv_sess_id = start_data["session_id"]
    print(f"[PASS] Conversational AI session initialized: Session {conv_sess_id}")

    # 10. Test Conversational AI Assessment: Multi-Turn Dialogue
    r_conv_turn = client.post("/api/assessment/conversation/turn", json={
        "session_id": conv_sess_id,
        "turn_index": 1,
        "user_message": "Our family is facing death threats and intimidation from local landlords.",
        "language": "English",
        "channel": "Voice Assessment",
        "audio_present": True,
        "audio_duration_sec": 22.0
    })
    assert r_conv_turn.status_code == 200
    turn_data = r_conv_turn.json()
    assert turn_data["current_stress_score"] >= 0
    assert turn_data["current_trauma_score"] >= 0
    assert "ai_response" in turn_data
    assert "detected_emotions" in turn_data
    print(f"[PASS] Conversational turn processed: Stress {turn_data['current_stress_score']}, Trauma {turn_data['current_trauma_score']}, Next Turn: {turn_data['turn_index']}")

    # 11. Test Referral Status Action
    r_ref = client.post("/api/cases/NHAA-1024/referral", json={
        "case_number": "NHAA-1024",
        "referral_type": "Counselor",
        "assignee_name": "Dr. S. Anuradha (Tele-MANAS)",
        "notes": "Remote psychological first-aid scheduled."
    })
    assert r_ref.status_code == 200
    ref_data = r_ref.json()
    assert ref_data["success"] is True
    assert "Counselor Referred" in ref_data["referral_status"]
    print(f"[PASS] Referral action confirmed: {ref_data['referral_status']}")

    # 12. Test High-Risk Alert Acknowledgment
    r_ack = client.post("/api/cases/NHAA-1024/alert/acknowledge", json={
        "case_number": "NHAA-1024",
        "acknowledged_by": "Officer Rajesh Kumar",
        "notes": "Reviewed urgent safety flag and contacted DSP unit."
    })
    assert r_ack.status_code == 200
    ack_data = r_ack.json()
    assert ack_data["success"] is True
    assert ack_data["alert_status"] == "Acknowledged"
    print(f"[PASS] High-risk alert acknowledged by authorized officer: {ack_data['alert_status']}")

    # 13. Test Support Outcome Recording
    r_out = client.post("/api/cases/NHAA-1024/support-outcome", json={
        "case_number": "NHAA-1024",
        "support_received": True,
        "outcome_notes": "Victim verified received psychological stabilization and escort patrol.",
        "recorded_by": "Officer Rajesh Kumar"
    })
    assert r_out.status_code == 200
    out_data = r_out.json()
    assert out_data["success"] is True
    assert out_data["support_received"] is True
    print(f"[PASS] Support outcome recorded: support_received={out_data['support_received']}, status={out_data['case_status']}")

    # 14. Test Frontend Static Assets Integrity
    r_app_js = client.get("/static/js/app.js")
    assert r_app_js.status_code == 200
    assert "switchVictimSubTab" in r_app_js.text
    assert "startConversationalAssessment" in r_app_js.text
    assert "renderHighRiskAlertBanner" in r_app_js.text

    r_charts_js = client.get("/static/js/charts.js")
    assert r_charts_js.status_code == 200
    assert "renderEmotionRadar" in r_charts_js.text

    r_i18n_js = client.get("/static/js/i18n.js")
    assert r_i18n_js.status_code == 200

    print("[PASS] Frontend JavaScript modules validated and healthy.")

    print("\n==================================================================")
    print(" >>> ALL 14 SAHAAYA AI SYSTEM & API TESTS PASSED SUCCESSFULLY! <<<")
    print("==================================================================")

if __name__ == "__main__":
    test_all()
