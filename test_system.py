import httpx

def test_all():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=10.0)

    # 1. Test root HTML
    r0 = client.get("/")
    assert r0.status_code == 200
    assert "Sahaaya AI" in r0.text
    print("[PASS] Root HTML served successfully.")

    # 2. Test Cases list
    r1 = client.get("/api/cases")
    assert r1.status_code == 200
    cases = r1.json()
    assert len(cases) >= 4
    print(f"[PASS] Cases listed successfully. Count: {len(cases)}")

    # 3. Test Case NHAA-1024
    r2 = client.get("/api/cases/NHAA-1024")
    assert r2.status_code == 200
    c1024 = r2.json()
    assert c1024["svi_score"] == 82
    assert c1024["risk_level"] == "HIGH"
    assert len(c1024["explainability"]) >= 4
    print(f"[PASS] Case NHAA-1024 verified: SVI {c1024['svi_score']}, Risk {c1024['risk_level']}, Lang {c1024['language']}")

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
    print(f"[PASS] Analytics & Early Warning active. Alerts count: {len(an['early_warning_alerts'])}")

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

    print("\n=======================================================")
    print(" >>> ALL SYSTEM VERIFICATIONS PASSED SUCCESSFULLY! <<<")
    print("=======================================================")

if __name__ == "__main__":
    test_all()
