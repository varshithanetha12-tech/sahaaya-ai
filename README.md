# Sahaaya AI (సహాయ AI)
### Real-Time Stress & Trauma Assessment Platform for Victim-Centric Triage & Support
**Public Service Decision-Support System | Government of India Atrocity Helpline Ecosystem**

---

## 📌 Executive Overview

**Sahaaya AI** is a production-grade, victim-centric AI decision-support and triage platform designed for complainants accessing national atrocity helplines (such as Toll-Free 14566), integrated grievance portals, chatbots, IVRS, mobile applications, or digital complaint desks.

The platform standardizes the identification of immediate psychological stress, trauma, fear, anxiety, and vulnerability at first contact by computing an evidence-grounded **Stress Vulnerability Index (SVI: 0–100)** to help authorized professionals rapidly prioritize appropriate psychological, legal, and protection support.

---

## ⚖️ Key Ethical & Design Principles

1. **Non-Diagnostic Decision Support**: Sahaaya AI is **not** a clinical or medical diagnostic tool. All outputs are strictly presented as triage prioritization indicators.
2. **Human-in-the-Loop Supremacy**: AI never automatically executes final decisions. AI flags signals and recommends support pathways; authorized human professionals (Nodal Officers, Counsellors, Legal Aid Defense Counsel) confirm, assign, or reject all actions.
3. **Statutory Consent & Privacy-by-Design**: Explicit consent is required before any AI analysis is performed. Citizens retain the unconditional right to decline AI assessment without prejudice. Sensitive narrative transcripts are encrypted, PII is masked, and every access event is recorded in an HMAC-SHA256 audit ledger.
4. **AI Uncertainty Transparency**: If input clarity or narrative length is limited, the engine displays an explicit uncertainty notice (`Assessment Confidence: 68% — Insufficient evidence for reliable assessment. Human review recommended.`).
5. **Critical Safety Detection**: Immediate danger triggers (active armed mobs, nocturnal stalking, forced boycotts, suicide/self-harm ideation) activate an **URGENT HUMAN REVIEW REQUIRED** alert state for instant escalation.

---

## 🏗️ Architecture & Modules

```
                              ┌────────────────────────────────────────┐
                              │         VICTIM FIRST-CONTACT           │
                              │ Voice • Chat • Portal • IVRS • Mobile  │
                              └──────────────────┬─────────────────────┘
                                                 │ Consent Confirmed
                                                 ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                CENTRAL AI ASSESSMENT ENGINE                            │
├───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│     A. Speech Prosody         │      B. Multilingual NLP      │   C. Emotion Analysis  │
│ • Speech Rate (WPM)           │ • 10 Indian Languages         │ • Fear & Distress      │
│ • Pause Count & Duration      │ • Threat & Boycott Detection  │ • Anxiety & Sadness    │
│ • Pitch Variance (Jitter)     │ • Helplessness & Isolation    │ • Anger & Confusion    │
│ • Voice Instability (Tremor)  │ • Danger & Emergency Signals  │ • Calibrated Confidence│
└───────────────────────────────┴───────────────┬───────────────┴────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        STRESS VULNERABILITY INDEX (SVI: 0–100)                         │
│       🟢 LOW (0–35)   🟡 MODERATE (36–65)   🟠 HIGH (66–84)   🔴 CRITICAL (85–100)      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Explainable AI ("Why this assessment?"): Transparent factor decomposition & weights  │
│ • Multi-Agency Pathways: Counselling • Legal Aid • Protection • Medical • Welfare      │
└───────────────────────────────────────────────┬────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             AUTHORIZED HUMAN PROFESSIONAL                              │
│ • Review Case Dossier        • Confirm Support Services       • Longitudinal Follow-up │
│ • Inspect Masked Evidence    • Dispatch Emergency Patrol      • Early Warning Trends   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🇮🇳 Multilingual Indic Support (10 Languages + Auto-Detect)

Sahaaya AI provides native UI internationalization and NLP keyword/transliteration lexicons across 10 official languages:
- **English**
- **Telugu (తెలుగు)**
- **Hindi (हिन्दी)**
- **Tamil (தமிழ்)**
- **Kannada (ಕನ್ನಡ)**
- **Malayalam (മലയാളം)**
- **Marathi (मराठी)**
- **Bengali (বাংলা)**
- **Gujarati (ગુજરાતી)**
- **Odia (ଓଡ଼ିଆ)**
- *Auto Detect Language*

---

## 🎬 Core Demonstration Scenario (Case NHAA-1024)

The platform includes the complete synthetic demonstration scenario:
- **Case ID**: `NHAA-1024`
- **Channel**: Voice Helpline
- **Language**: Telugu (`నమస్కారం... మమ్మల్ని ఊరి నుంచి వెలివేశారు... పొలం లాక్కుంటామని కొట్టారు... రాత్రిళ్ళు ఇంటి చుట్టూ తిరుగుతూ చంపేస్తామని బెదిరిస్తున్నారు...`)
- **Acoustic Findings**: 6 extended pauses (avg 3.2s), pitch jitter at 48.5 Hz, vocal tremor index 0.74.
- **SVI Score**: **82 / 100 (HIGH Risk)**
- **Detected Indicators**: Fear (86%), Distress (79%), Threat/Intimidation (88%), Social Isolation (85%).
- **Explainability**: 5 contributing factors with evidence snippets.
- **Human Actions**: Nodal Officer assigns Tele-MANAS trauma specialist (Dr. S. Anuradha) and District Legal Services Authority defense counsel (Adv. K. Venkatesh), followed by scheduled follow-up tracking.

---

## 🚀 Running the Application

### 1. Requirements
- Python 3.10+
- Dependencies installed via `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Launch the Web Application
```bash
python run.py
```
Open your browser at: **`http://127.0.0.1:8000`**

### 3. Run Automated System Test Suite
```bash
python test_system.py
```

---

## 📱 Features & Views Walkthrough

1. **Public Landing View**: Explains the 3-phase pipeline (Listen, Assess, Support), ethical boundaries, and direct links to start support or log in.
2. **Victim First Contact & Chat Portal**:
   - Channel selector (Voice Call, Chatbot, Portal, Mobile, IVRS, Text, Audio Upload).
   - Audio recording with real-time Web Audio API waveform visualizer and duration timer.
   - Statutory consent modal and Emergency SOS quick-exit button.
   - Real-time SVI calculation preview with Emotion Radar chart.
   - Post-submission 7-stage case tracking timeline.
3. **Authorized Officer Dashboard**:
   - KPI metric cards (Total, High Risk, Critical, Pending Review, Follow-ups Today).
   - Filterable cases table (by Risk, Language, Channel, District, Status) with search.
4. **Deep Triage Case Dossier**:
   - Visual SVI gauge and AI confidence badge.
   - Interactive Chart.js Emotion Radar and Speech Prosody charts.
   - "Why this score?" Explainable AI panel.
   - AI Insight panel with restricted sensitive evidence viewer (PII masked).
   - Support recommendations with human review/assign/reject confirmation workflow.
   - 7-point chronological case timeline.
   - Immediate simulated emergency action dispatches.
5. **Follow-Up Management System**:
   - Upcoming, Overdue, and Completed follow-up queues.
   - Vulnerability Timeline line chart tracking SVI reduction over time.
6. **Support Resource Directory**:
   - Searchable directory of verified centers across India (Tele-MANAS, DLSA, Sakhi Centers, Police Nodal Cells).
7. **Analytics & Early Warning Dashboard**:
   - Aggregated charts (Risk donut, channel, language, state distributions).
   - Algorithmic cluster detection alerts (e.g. 42% threat increase in Rangareddy district).
8. **Admin Panel & Governance**:
   - Configurable SVI risk threshold sliders.
   - Model weights calibration sliders.
   - Full statutory audit ledger with search, filtering, and CSV export.
9. **Demo Mode**:
   - 4 one-click presets: Low (SVI: 22), Moderate (SVI: 52), High (NHAA-1024 SVI: 82), Critical (SVI: 94).
   - Interactive Guided Walkthrough with step-by-step presentation overlays.
