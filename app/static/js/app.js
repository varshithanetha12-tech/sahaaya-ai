// Main Application Logic for Sahaaya AI Platform

const App = {
    state: {
        activeTab: "landing-view",
        currentRole: "Authorized Officer",
        currentUser: null,
        cases: [],
        selectedCase: null,
        followups: [],
        resources: [],
        analytics: null,
        auditLogs: [],
        config: null,
        notifications: [],
        victimConsent: true,
        selectedLanguage: "Telugu",
        selectedChannel: "Voice Helpline",
        highContrast: false,
        fontSize: "font-size-md",
        demoWalkthroughStep: 0,
        convSessionId: null,
        convTurnIndex: 1,
        convLanguage: "Telugu",
        activeVictimSubTab: "start-assessment",
        latestAssessment: null,
        filterPriority: "ALL",
        filterReferral: "ALL",
        isConvRecording: false
    },

    init: async function() {
        console.log("Initializing Sahaaya AI Platform...");
        this.registerServiceWorker();
        this.setupPwaInstallPrompt();
        await this.loadCurrentUser();
        await this.loadNotifications();
        await this.loadConfig();
        this.setupEventListeners();
        I18N.setLanguage("English");
        
        // Auto-load cases list
        await this.fetchCases();
    },

    registerServiceWorker: function() {
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js').then((reg) => {
                    console.log('[PWA] Service Worker registered successfully with scope:', reg.scope);
                }).catch((err) => {
                    console.log('[PWA] Service Worker registration skipped:', err);
                });
            });
        }
    },

    setupPwaInstallPrompt: function() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPwaPrompt = e;
            console.log('[PWA] Install prompt captured for Add to Home Screen.');
        });
    },

    toggleMobileMenu: function() {
        const drawer = document.getElementById("mobileNavDrawer");
        if (!drawer) return;
        drawer.classList.toggle("hidden");
    },

    closeMobileMenu: function() {
        const drawer = document.getElementById("mobileNavDrawer");
        if (drawer) drawer.classList.add("hidden");
    },

    loadCurrentUser: async function() {
        try {
            const res = await fetch("/api/auth/me");
            this.state.currentUser = await res.json();
            this.state.currentRole = this.state.currentUser.role;
            const badge = document.getElementById("userRoleBadge");
            const nameEl = document.getElementById("currentUserName");
            if (badge) badge.textContent = this.state.currentRole;
            if (nameEl) nameEl.textContent = this.state.currentUser.name;
        } catch (e) {
            console.error("Failed to load user:", e);
        }
    },

    loadNotifications: async function() {
        try {
            const res = await fetch("/api/auth/notifications");
            this.state.notifications = await res.json();
            this.renderNotifications();
        } catch (e) {
            console.error("Failed to load notifications:", e);
        }
    },

    renderNotifications: function() {
        const countEl = document.getElementById("notifCount");
        const listEl = document.getElementById("notifDropdownList");
        const unread = this.state.notifications.filter(n => !n.read).length;
        if (countEl) {
            countEl.textContent = unread;
            countEl.style.display = unread > 0 ? "inline-flex" : "none";
        }
        if (listEl) {
            listEl.innerHTML = this.state.notifications.map(n => `
                <div class="p-3 border-b border-slate-100 hover:bg-slate-50 transition cursor-pointer" onclick="App.openCaseFromNotification('${n.case_number}')">
                    <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
                        <span class="font-semibold ${n.severity === 'critical' ? 'text-rose-600' : 'text-amber-600'}">${n.severity.toUpperCase()}</span>
                        <span>${n.timestamp}</span>
                    </div>
                    <div class="text-xs font-medium text-slate-800">${n.title}</div>
                    <div class="text-xs text-slate-600 mt-1">${n.message}</div>
                </div>
            `).join("");
        }
    },

    openCaseFromNotification: function(caseNumber) {
        document.getElementById("notifDropdown").classList.add("hidden");
        if (caseNumber) {
            this.viewCaseDetails(caseNumber);
        }
    },

    loadConfig: async function() {
        try {
            const res = await fetch("/api/admin/config");
            this.state.config = await res.json();
            this.updateConfigSliders();
        } catch (e) {
            console.error("Failed to load config:", e);
        }
    },

    updateConfigSliders: function() {
        if (!this.state.config) return;
        const lowEl = document.getElementById("cfgThresholdLow");
        const modEl = document.getElementById("cfgThresholdMod");
        const highEl = document.getElementById("cfgThresholdHigh");
        const nlpEl = document.getElementById("cfgNlpWeight");
        const speechEl = document.getElementById("cfgSpeechWeight");
        const emoEl = document.getElementById("cfgEmotionWeight");

        if (lowEl) lowEl.value = this.state.config.threshold_low_max;
        if (modEl) modEl.value = this.state.config.threshold_mod_max;
        if (highEl) highEl.value = this.state.config.threshold_high_max;
        if (nlpEl) nlpEl.value = this.state.config.nlp_weight;
        if (speechEl) speechEl.value = this.state.config.speech_weight;
        if (emoEl) emoEl.value = this.state.config.emotion_weight;

        // Label updates
        document.getElementById("cfgValLow").textContent = this.state.config.threshold_low_max;
        document.getElementById("cfgValMod").textContent = this.state.config.threshold_mod_max;
        document.getElementById("cfgValHigh").textContent = this.state.config.threshold_high_max;
        document.getElementById("cfgValNlp").textContent = this.state.config.nlp_weight;
        document.getElementById("cfgValSpeech").textContent = this.state.config.speech_weight;
        document.getElementById("cfgValEmo").textContent = this.state.config.emotion_weight;
    },

    switchTab: function(tabId) {
        this.state.activeTab = tabId;
        const views = [
            "landing-view", "victim-view", "officer-view", "case-details-view",
            "followups-view", "resources-view", "analytics-view", "admin-view"
        ];
        views.forEach(v => {
            const el = document.getElementById(v);
            if (el) el.classList.add("hidden");
        });

        const target = document.getElementById(tabId);
        if (target) {
            target.classList.remove("hidden");
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // Highlight header nav buttons
        document.querySelectorAll(".nav-link").forEach(btn => {
            btn.classList.remove("border-teal-600", "text-teal-700", "font-bold");
            btn.classList.add("text-slate-600");
        });
        const activeNav = document.getElementById(`nav-${tabId}`);
        if (activeNav) {
            activeNav.classList.add("border-teal-600", "text-teal-700", "font-bold");
            activeNav.classList.remove("text-slate-600");
        }

        // Trigger view-specific loaders
        if (tabId === "victim-view") this.switchVictimSubTab(this.state.activeVictimSubTab || "start-assessment");
        if (tabId === "officer-view") this.fetchCases();
        if (tabId === "followups-view") this.fetchFollowups();
        if (tabId === "resources-view") this.fetchResources();
        if (tabId === "analytics-view") this.fetchAnalytics();
        if (tabId === "admin-view") this.fetchAuditLogs();
    },

    switchRole: async function(newRole) {
        try {
            const res = await fetch("/api/auth/switch-role", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ role: newRole })
            });
            const data = await res.json();
            if (data.success) {
                this.state.currentUser = data.user;
                this.state.currentRole = data.user.role;
                document.getElementById("userRoleBadge").textContent = data.user.role;
                document.getElementById("currentUserName").textContent = data.user.name;
                this.showToast(`Switched active profile to: ${data.user.name} (${data.user.role})`, "info");
                
                if (data.user.role === "Victim/User") {
                    this.switchTab("victim-view");
                } else if (data.user.role === "Administrator") {
                    this.switchTab("admin-view");
                } else {
                    this.switchTab("officer-view");
                }
            }
        } catch (e) {
            console.error("Role switch error:", e);
        }
    },

    // ==========================================
    // VICTIM PORTAL SUB-TABS & CONVERSATIONAL ASSESSMENT
    // ==========================================
    switchVictimSubTab: function(tabName) {
        this.state.activeVictimSubTab = tabName;

        // Sub-nav buttons highlight
        document.querySelectorAll(".vsub-btn").forEach(btn => {
            btn.classList.remove("bg-teal-600", "text-white", "shadow-sm");
            btn.classList.add("bg-slate-100", "text-slate-700", "hover:bg-slate-200");
        });

        const btnIdMap = {
            "start-assessment": "vsub-start",
            "voice-assessment": "vsub-voice",
            "text-assessment": "vsub-text",
            "my-assessment": "vsub-my-assessment",
            "my-support": "vsub-my-support",
            "my-followups": "vsub-followups",
            "resources": "vsub-resources"
        };
        const activeBtn = document.getElementById(btnIdMap[tabName]);
        if (activeBtn) {
            activeBtn.classList.add("bg-teal-600", "text-white", "shadow-sm");
            activeBtn.classList.remove("bg-slate-100", "text-slate-700", "hover:bg-slate-200");
        }

        // Section elements
        const sections = [
            "conversationalAssessmentSection",
            "conversationalResultSection",
            "victimSubmissionSection",
            "victimDashboardSection",
            "victimMySupportSection",
            "victimFollowupsSection",
            "victimResourcesSection"
        ];
        sections.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.add("hidden");
        });

        if (tabName === "start-assessment") {
            const conv = document.getElementById("conversationalAssessmentSection");
            if (conv) conv.classList.remove("hidden");
            if (!this.state.convSessionId) {
                this.startConversationalAssessment();
            }
        } else if (tabName === "voice-assessment") {
            const sub = document.getElementById("victimSubmissionSection");
            if (sub) sub.classList.remove("hidden");
            this.setChannel("Voice Helpline");
        } else if (tabName === "text-assessment") {
            const sub = document.getElementById("victimSubmissionSection");
            if (sub) sub.classList.remove("hidden");
            this.setChannel("Text Complaint");
        } else if (tabName === "my-assessment") {
            const resEl = document.getElementById("conversationalResultSection");
            if (resEl) resEl.classList.remove("hidden");
            if (!this.state.latestAssessment) {
                const demoCase = this.state.cases.find(c => c.case_number === "NHAA-1024") || this.state.cases[0];
                if (demoCase) {
                    const mockAssessment = {
                        score: demoCase.svi_score,
                        risk_level: demoCase.risk_level,
                        stress_score: demoCase.stress_score || 85,
                        trauma_score: demoCase.trauma_score || 88,
                        emotional_state: demoCase.emotional_state || "Severe Fear & Threat Trauma",
                        recommended_next_action: demoCase.recommended_next_action,
                        explainability_factors: demoCase.explainability || [],
                        critical_safety_alert: demoCase.critical_safety_flag || demoCase.risk_level === "CRITICAL",
                        case_number: demoCase.case_number
                    };
                    this.state.latestAssessment = mockAssessment;
                    this.renderAssessmentResult(mockAssessment, demoCase.case_number);
                }
            } else {
                this.renderAssessmentResult(this.state.latestAssessment, this.state.latestAssessment.case_number);
            }
        } else if (tabName === "my-support") {
            const supEl = document.getElementById("victimMySupportSection");
            if (supEl) supEl.classList.remove("hidden");
        } else if (tabName === "my-followups") {
            const folEl = document.getElementById("victimFollowupsSection");
            if (folEl) folEl.classList.remove("hidden");
        } else if (tabName === "resources") {
            const recEl = document.getElementById("victimResourcesSection");
            if (recEl) recEl.classList.remove("hidden");
        }
    },

    setConvLanguage: function(lang) {
        this.state.convLanguage = lang;
        const sel = document.getElementById("convLanguageSelect");
        if (sel) sel.value = lang;
        if (this.state.convTurnIndex <= 1) {
            this.startConversationalAssessment(lang);
        }
    },

    startConversationalAssessment: async function(language, channel) {
        const lang = language || this.state.convLanguage || "Telugu";
        const ch = channel || "Voice Assessment";
        this.state.convLanguage = lang;
        this.state.convTurnIndex = 1;
        this.state.convSessionId = null;

        const sel = document.getElementById("convLanguageSelect");
        if (sel) sel.value = lang;

        const container = document.getElementById("convMessagesContainer");
        if (container) {
            container.innerHTML = `
                <div class="flex items-center space-x-2 text-xs text-teal-700 italic py-2">
                    <svg class="animate-spin h-4 w-4 text-teal-600" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                    <span>Connecting to empathetic Sahaaya conversational triage agent...</span>
                </div>
            `;
        }

        try {
            const res = await fetch(`/api/assessment/conversation/start?language=${encodeURIComponent(lang)}&channel=${encodeURIComponent(ch)}`, {
                method: "POST"
            });
            if (!res.ok) {
                throw new Error("Failed to start conversation");
            }
            const data = await res.json();
            this.state.convSessionId = data.session_id;
            this.state.convTurnIndex = data.turn_index;

            const badge = document.getElementById("convSessionBadge");
            if (badge) badge.textContent = `ID: ${data.session_id}`;

            // Reset gauges
            const turnNum = document.getElementById("convTurnNum");
            if (turnNum) turnNum.textContent = "1";
            const progPct = document.getElementById("convProgressPct");
            if (progPct) progPct.textContent = "25";
            const progFill = document.getElementById("convProgressBarFill");
            if (progFill) progFill.style.width = "25%";

            const stressEl = document.getElementById("convStressScore");
            if (stressEl) stressEl.textContent = "0 / 100";
            const stressBar = document.getElementById("convStressBar");
            if (stressBar) stressBar.style.width = "0%";

            const traumaEl = document.getElementById("convTraumaScore");
            if (traumaEl) traumaEl.textContent = "0 / 100";
            const traumaBar = document.getElementById("convTraumaBar");
            if (traumaBar) traumaBar.style.width = "0%";

            const riskBadge = document.getElementById("convRiskBadge");
            if (riskBadge) {
                riskBadge.className = "px-2.5 py-1 rounded-full text-xs font-black bg-emerald-100 text-emerald-800 border border-emerald-300";
                riskBadge.textContent = "LOW";
            }

            const emoState = document.getElementById("convEmotionalState");
            if (emoState) emoState.textContent = "Initial greeting • Active listening";

            // Render greeting message
            if (container) {
                container.innerHTML = `
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 rounded-full bg-teal-700 text-white flex items-center justify-center font-bold text-xs shadow-sm flex-shrink-0">
                            AI
                        </div>
                        <div class="bg-white border border-teal-200 text-slate-800 p-4 rounded-2xl rounded-tl-none shadow-sm max-w-xl text-xs leading-relaxed">
                            <div class="text-[10px] font-bold text-teal-700 mb-1 uppercase tracking-wider">Sahaaya Empathetic Agent (${lang})</div>
                            <div class="font-medium text-slate-800">${data.ai_response}</div>
                            <div class="text-[10px] text-slate-400 mt-2 flex items-center justify-between">
                                <span>Voice & text prosody analysis active</span>
                                <span>Just now</span>
                            </div>
                        </div>
                    </div>
                `;
            }

            const input = document.getElementById("convUserInput");
            if (input) input.value = "";
        } catch (e) {
            console.error("Conversation start error:", e);
            if (container) {
                container.innerHTML = `<div class="p-3 text-xs text-rose-600">Failed to initiate conversation. Please try again.</div>`;
            }
        }
    },

    speechRecognizer: null,
    activeMicStream: null,

    toggleConvVoice: async function() {
        this.state.isConvRecording = !this.state.isConvRecording;
        const btn = document.getElementById("convVoiceToggleBtn");
        const btnText = document.getElementById("convVoiceBtnText");
        const indicator = document.getElementById("convAudioIndicator");

        if (this.state.isConvRecording) {
            let micGranted = false;

            // 1. Microphone hardware permission handling
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    micGranted = true;
                    this.activeMicStream = stream;
                    console.log("[Audio] Microphone permission granted.");
                } catch (err) {
                    console.log("[Audio] Microphone permission denied or unavailable:", err);
                    this.showToast("Microphone access unavailable or denied. Fallback to simulated acoustic prosody active.", "warning");
                }
            } else {
                this.showToast("Microphone API not supported on this browser. Voice simulation active.", "info");
            }

            // 2. Web Speech API live voice-to-text if supported
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRec && micGranted) {
                try {
                    this.speechRecognizer = new SpeechRec();
                    this.speechRecognizer.continuous = true;
                    this.speechRecognizer.interimResults = true;
                    this.speechRecognizer.lang = this.state.convLanguage === "Telugu" ? "te-IN" : (this.state.convLanguage === "Hindi" ? "hi-IN" : "en-IN");
                    this.speechRecognizer.onresult = (evt) => {
                        let transcript = "";
                        for (let i = evt.resultIndex; i < evt.results.length; ++i) {
                            transcript += evt.results[i][0].transcript;
                        }
                        const input = document.getElementById("convUserInput");
                        if (input && transcript) {
                            input.value = transcript;
                        }
                    };
                    this.speechRecognizer.start();
                } catch (e) {
                    console.log("[SpeechRecognition] Initialization notice:", e);
                }
            }

            if (btn) {
                btn.classList.add("bg-rose-600", "text-white");
                btn.classList.remove("bg-slate-100", "text-slate-700");
            }
            if (btnText) btnText.innerHTML = `<span class="inline-block w-2.5 h-2.5 bg-white rounded-full mr-1.5 animate-ping"></span> Stop Recording (Listening...)`;
            if (indicator) indicator.classList.remove("hidden");
            this.showToast(micGranted ? "Listening via microphone..." : "Voice stream active. Acoustic prosody tracking enabled.", "info");

            const input = document.getElementById("convUserInput");
            if (input && !input.value.trim()) {
                input.value = this.state.convLanguage === "Telugu"
                    ? "నమస్కారం... మా గ్రామంలో మా కుటుంబంపై నిరంతరం బెదిరింపులు వస్తున్నాయి. రాత్రిపూట ఇంటికి వచ్చి చంపేస్తామని భయపెడుతున్నారు... తాగడానికి నీళ్లు కూడా బంద్ చేశారు... చాలా భయంగా ఉంది..."
                    : "Our family is facing continuous death threats and social boycott in our village. Night intimidation around our house. We are deeply frightened and cut off from help.";
            }
        } else {
            // Stop speech recognition and hardware stream
            if (this.speechRecognizer) {
                try { this.speechRecognizer.stop(); } catch (e) {}
                this.speechRecognizer = null;
            }
            if (this.activeMicStream) {
                try {
                    this.activeMicStream.getTracks().forEach(t => t.stop());
                } catch (e) {}
                this.activeMicStream = null;
            }

            if (btn) {
                btn.classList.remove("bg-rose-600", "text-white");
                btn.classList.add("bg-slate-100", "text-slate-700");
            }
            if (btnText) btnText.innerHTML = `🎙️ Record / Simulate Voice`;
            if (indicator) indicator.classList.add("hidden");

            const input = document.getElementById("convUserInput");
            if (input && input.value.trim()) {
                this.sendConversationMessage(input.value.trim(), true, 26.5);
            }
        }
    },

    sendConversationMessage: async function(overrideText, isAudio = false, duration = 0.0) {
        const inputEl = document.getElementById("convUserInput");
        const messageText = (overrideText !== undefined && overrideText !== null) ? overrideText : (inputEl ? inputEl.value.trim() : "");

        if (!messageText) {
            this.showToast("Please write or speak a description of your experience.", "warning");
            return;
        }

        if (!this.state.convSessionId) {
            await this.startConversationalAssessment();
        }

        const container = document.getElementById("convMessagesContainer");

        // Append user chat bubble
        if (container) {
            const userBubble = document.createElement("div");
            userBubble.className = "flex items-start justify-end space-x-3";
            userBubble.innerHTML = `
                <div class="bg-teal-700 text-white p-4 rounded-2xl rounded-tr-none shadow-sm max-w-xl text-xs leading-relaxed">
                    <div class="text-[10px] font-bold text-teal-200 mb-1 uppercase tracking-wider flex items-center justify-between">
                        <span>You (${this.state.convLanguage})</span>
                        ${isAudio ? `<span class="bg-teal-800 text-teal-100 px-1.5 py-0.5 rounded font-mono">🎙️ Spoken Audio (${duration || 26.5}s)</span>` : ''}
                    </div>
                    <div>${messageText}</div>
                    <div class="text-[10px] text-teal-300 mt-2 text-right">Delivered</div>
                </div>
                <div class="w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center font-bold text-xs shadow-sm flex-shrink-0">
                    You
                </div>
            `;
            container.appendChild(userBubble);

            // Typing indicator
            const typingInd = document.createElement("div");
            typingInd.id = "convTypingIndicator";
            typingInd.className = "flex items-center space-x-2 text-xs text-teal-700 italic py-2";
            typingInd.innerHTML = `
                <svg class="animate-spin h-4 w-4 text-teal-600" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                <span>Evaluating multi-prosodic tremor, linguistic trauma & SVI markers...</span>
            `;
            container.appendChild(typingInd);
            container.scrollTop = container.scrollHeight;
        }

        if (inputEl) inputEl.value = "";

        // Reset voice button state if it was recording
        if (this.state.isConvRecording) {
            this.state.isConvRecording = false;
            const btn = document.getElementById("convVoiceToggleBtn");
            const btnText = document.getElementById("convVoiceBtnText");
            const indicator = document.getElementById("convAudioIndicator");
            if (btn) {
                btn.classList.remove("bg-rose-600", "text-white");
                btn.classList.add("bg-slate-100", "text-slate-700");
            }
            if (btnText) btnText.innerHTML = `🎙️ Record / Simulate Voice`;
            if (indicator) indicator.classList.add("hidden");
        }

        try {
            const payload = {
                session_id: this.state.convSessionId,
                turn_index: this.state.convTurnIndex,
                user_message: messageText,
                language: this.state.convLanguage,
                channel: isAudio ? "Voice Assessment" : "Chatbot",
                audio_present: !!isAudio,
                audio_duration_sec: duration || (isAudio ? 26.5 : 0.0)
            };

            const res = await fetch("/api/assessment/conversation/turn", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const typingInd = document.getElementById("convTypingIndicator");
            if (typingInd) typingInd.remove();

            if (!res.ok) {
                const err = await res.json();
                this.showToast(err.detail || "Error evaluating turn", "error");
                return;
            }

            const data = await res.json();

            // Append AI response bubble
            if (container) {
                const aiBubble = document.createElement("div");
                aiBubble.className = "flex items-start space-x-3";
                aiBubble.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-teal-700 text-white flex items-center justify-center font-bold text-xs shadow-sm flex-shrink-0">
                        AI
                    </div>
                    <div class="bg-white border border-teal-200 text-slate-800 p-4 rounded-2xl rounded-tl-none shadow-sm max-w-xl text-xs leading-relaxed">
                        <div class="text-[10px] font-bold text-teal-700 mb-1 uppercase tracking-wider flex items-center justify-between">
                            <span>Sahaaya Empathetic Agent</span>
                            <span class="font-mono text-slate-400">Turn ${data.turn_index - 1} / 4</span>
                        </div>
                        <div class="font-medium text-slate-800">${data.ai_response}</div>
                        ${data.detected_indicators && data.detected_indicators.length > 0 ? `
                            <div class="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap items-center gap-1">
                                <span class="text-[10px] text-slate-400 mr-1">Observed Signals:</span>
                                ${data.detected_indicators.map(ind => `<span class="bg-slate-100 text-slate-700 text-[10px] font-medium px-2 py-0.5 rounded-full border border-slate-200">✓ ${ind}</span>`).join('')}
                            </div>
                        ` : ''}
                        ${data.is_complete ? `
                            <div class="mt-3 pt-2.5 border-t border-teal-100 flex items-center justify-between">
                                <span class="text-[11px] font-bold text-teal-800">✅ Assessment Synthesis Ready</span>
                                <button onclick="App.viewCompletedAssessment()" class="px-3.5 py-1.5 rounded-xl bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold transition shadow">
                                    View Full Results →
                                </button>
                            </div>
                        ` : ''}
                    </div>
                `;
                container.appendChild(aiBubble);
                container.scrollTop = container.scrollHeight;
            }

            // Update live progress and gauges
            this.state.convTurnIndex = data.turn_index;

            const turnNum = document.getElementById("convTurnNum");
            if (turnNum) turnNum.textContent = Math.min(4, data.turn_index);
            const progPct = document.getElementById("convProgressPct");
            if (progPct) progPct.textContent = data.progress_pct;
            const progFill = document.getElementById("convProgressBarFill");
            if (progFill) progFill.style.width = `${data.progress_pct}%`;

            const stressEl = document.getElementById("convStressScore");
            if (stressEl) stressEl.textContent = `${data.current_stress_score} / 100`;
            const stressBar = document.getElementById("convStressBar");
            if (stressBar) stressBar.style.width = `${data.current_stress_score}%`;

            const traumaEl = document.getElementById("convTraumaScore");
            if (traumaEl) traumaEl.textContent = `${data.current_trauma_score} / 100`;
            const traumaBar = document.getElementById("convTraumaBar");
            if (traumaBar) traumaBar.style.width = `${data.current_trauma_score}%`;

            const riskBadge = document.getElementById("convRiskBadge");
            if (riskBadge) {
                const colors = {
                    "LOW": "bg-emerald-100 text-emerald-800 border-emerald-300",
                    "MODERATE": "bg-amber-100 text-amber-800 border-amber-300",
                    "HIGH": "bg-orange-100 text-orange-800 border-orange-300",
                    "CRITICAL": "bg-rose-100 text-rose-800 border-rose-300 animate-pulse"
                };
                riskBadge.className = `px-2.5 py-1 rounded-full text-xs font-black border ${colors[data.current_risk_level] || colors["LOW"]}`;
                riskBadge.textContent = data.current_risk_level;
            }

            const emoState = document.getElementById("convEmotionalState");
            if (emoState) emoState.textContent = data.emotional_state || "Heightened affective arousal";

            // Update Emotion Pills
            const emotionPills = document.getElementById("convEmotionPills");
            if (emotionPills && data.detected_emotions) {
                const emo = data.detected_emotions;
                emotionPills.innerHTML = `
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-bold ${emo.Fear > 40 ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-slate-100 text-slate-600'}">Fear (${Math.round(emo.Fear || 0)}%)</span>
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-bold ${emo.Anxiety > 40 ? 'bg-amber-100 text-amber-800 border border-amber-300' : 'bg-slate-100 text-slate-600'}">Anxiety (${Math.round(emo.Anxiety || 0)}%)</span>
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-bold ${emo.Distress > 40 ? 'bg-purple-100 text-purple-800 border border-purple-300' : 'bg-slate-100 text-slate-600'}">Distress (${Math.round(emo.Distress || 0)}%)</span>
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-600">Sadness (${Math.round(emo.Sadness || 0)}%)</span>
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-600">Anger (${Math.round(emo.Anger || 0)}%)</span>
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-medium ${emo.Calm > 40 ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'}">Calm (${Math.round(emo.Calm || 0)}%)</span>
                `;
            }

            // If completed, record assessment and show results
            if (data.is_complete && data.final_assessment) {
                this.state.latestAssessment = data.final_assessment;
                if (data.case_number) {
                    this.state.latestAssessment.case_number = data.case_number;
                }
                this.renderAssessmentResult(data.final_assessment, data.case_number || "NHAA-1024");
                this.showToast("Assessment complete! Detailed triage synthesis generated.", "success");
                
                // Refresh cases in background
                this.fetchCases();

                setTimeout(() => {
                    this.viewCompletedAssessment();
                }, 1200);
            }
        } catch (e) {
            console.error("Conversation turn error:", e);
            const typingInd = document.getElementById("convTypingIndicator");
            if (typingInd) typingInd.remove();
            this.showToast("Failed to process conversational turn.", "error");
        }
    },

    viewCompletedAssessment: function() {
        if (!this.state.latestAssessment) return;
        this.switchVictimSubTab("my-assessment");
    },

    loadTeluguVoiceDemo: async function() {
        const teluguScenario = "నమస్కారం... మా గ్రామంలో మా కుటుంబంపై నిరంతరం బెదిరింపులు వస్తున్నాయి. భూమి పట్టా రిజిస్ట్రేషన్ తర్వాత ఊరి పెద్దలు మమ్మల్ని చంపేస్తామని రాత్రిపూట ఇంటికి వచ్చి భయపెడుతున్నారు... తాగడానికి నీళ్లు కూడా బంద్ చేశారు. మా పిల్లలు చాలా భయపడుతున్నారు... ఏం చేయాలో దిక్కులేదు...";
        this.state.convLanguage = "Telugu";
        const sel = document.getElementById("convLanguageSelect");
        if (sel) sel.value = "Telugu";

        this.showToast("Loading authentic Telugu land threat scenario with simulated speech prosody...", "info");

        if (!this.state.convSessionId || this.state.convTurnIndex > 1) {
            await this.startConversationalAssessment("Telugu", "Voice Assessment");
        }

        const input = document.getElementById("convUserInput");
        if (input) input.value = teluguScenario;

        setTimeout(() => {
            this.sendConversationMessage(teluguScenario, true, 28.5);
        }, 600);
    },

    getLatestCaseNum: function() {
        return (this.state.latestAssessment && this.state.latestAssessment.case_number) || (this.state.selectedCase && this.state.selectedCase.case_number) || "NHAA-1024";
    },

    renderAssessmentResult: function(assessment, caseNumber) {
        const caseNum = caseNumber || (assessment && assessment.case_number) || "NHAA-1024";
        const resCaseEl = document.getElementById("resCaseNumber");
        if (resCaseEl) resCaseEl.textContent = caseNum;

        // Badge styling
        const resBadge = document.getElementById("resRiskBadge");
        if (resBadge) {
            const lvl = assessment.risk_level || "HIGH";
            const colors = {
                "LOW": "bg-emerald-100 text-emerald-800 border-emerald-300",
                "MODERATE": "bg-amber-100 text-amber-800 border-amber-300",
                "HIGH": "bg-orange-100 text-orange-800 border-orange-300",
                "CRITICAL": "bg-rose-100 text-rose-800 border-rose-300 animate-pulse"
            };
            resBadge.className = `px-4 py-1.5 rounded-full text-xs font-black border ${colors[lvl] || colors["HIGH"]}`;
            resBadge.textContent = `${lvl} RISK`;
        }

        // Scores
        const stressEl = document.getElementById("resStressScore");
        if (stressEl) stressEl.textContent = `${assessment.stress_score || 85} / 100`;

        const traumaEl = document.getElementById("resTraumaScore");
        if (traumaEl) traumaEl.textContent = `${assessment.trauma_score || 88} / 100`;

        const sviEl = document.getElementById("resSviScore");
        if (sviEl) sviEl.textContent = `${assessment.score || 82} / 100`;

        const prioEl = document.getElementById("resPriority");
        if (prioEl) prioEl.textContent = assessment.critical_safety_alert ? "Urgent" : (assessment.risk_level === "HIGH" ? "Priority" : "Standard");

        // Emotional State
        const emoEl = document.getElementById("resEmotionalState");
        if (emoEl) emoEl.textContent = assessment.emotional_state || assessment.summary_text || "Heightened autonomic fear arousal with active intimidation trauma.";

        // Explainability factors
        const expList = document.getElementById("resExplainabilityList");
        if (expList && assessment.explainability_factors) {
            expList.innerHTML = assessment.explainability_factors.map(f => `
                <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                    <div class="flex items-center justify-between font-bold text-slate-800">
                        <span class="flex items-center space-x-1.5">
                            <span class="w-2 h-2 rounded-full ${f.indicator_group === 'Safety' ? 'bg-rose-500' : 'bg-teal-500'}"></span>
                            <span>${f.factor}</span>
                        </span>
                        <span class="text-teal-700 bg-teal-50 px-2 py-0.5 rounded text-[11px] font-mono">${f.weight}% Weight</span>
                    </div>
                    <div class="text-slate-600 mt-1">${f.description}</div>
                    ${f.evidence_snippet ? `<div class="mt-1.5 text-[11px] font-mono text-slate-600 bg-white p-1.5 rounded border border-slate-100">Evidence: "${f.evidence_snippet}"</div>` : ''}
                </div>
            `).join("");
        }

        // Recommended Next Action
        const actionEl = document.getElementById("resRecommendedAction");
        if (actionEl) actionEl.textContent = assessment.recommended_next_action || "Urgent human review flagged. Immediate counselor referral via Tele-MANAS (14416) and District Legal Services Authority (DLSA) defense notice advised.";

        // Feedback alert
        const fbEl = document.getElementById("resReferralFeedback");
        if (fbEl) fbEl.classList.add("hidden");
    },

    requestAssessmentReferral: function(referralType) {
        const caseNum = this.getLatestCaseNum();
        this.requestReferral(caseNum, referralType);
        const fbEl = document.getElementById("resReferralFeedback");
        const fbText = document.getElementById("resReferralFeedbackText");
        if (fbEl && fbText) {
            fbEl.classList.remove("hidden");
            fbText.textContent = `Immediate referral for [${referralType}] requested and forwarded to authorized nodal personnel for Case ${caseNum}.`;
        }
    },

    requestReferral: async function(caseNumber, referralType) {
        if (!caseNumber) {
            caseNumber = this.getLatestCaseNum();
        }

        try {
            const assigneeMap = {
                "Counselor": "Dr. S. Rao (Tele-MANAS Counselor)",
                "Legal Aid": "Adv. K. Murthy (DLSA Defense Counsel)",
                "Emergency": "District Atrocity Quick Response Unit",
                "Self-Help": "Community Welfare Coordinator"
            };

            const res = await fetch(`/api/cases/${caseNumber}/referral`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    case_number: caseNumber,
                    referral_type: referralType,
                    assignee_name: assigneeMap[referralType] || "Assigned Nodal Specialist",
                    notes: `Institutional referral initiated via Sahaaya Triage Platform`
                })
            });

            if (!res.ok) {
                throw new Error("Referral request failed");
            }

            const data = await res.json();
            this.showToast(`Referral [${referralType}] requested successfully for Case ${caseNumber}!`, "success");

            if (this.state.selectedCase && this.state.selectedCase.case_number === caseNumber) {
                this.state.selectedCase.referral_status = data.referral_status;
                const badge = document.getElementById("cdReferralStatusBadge");
                if (badge) badge.textContent = data.referral_status;
            }

            await this.fetchCases();
        } catch (e) {
            console.error("Referral request error:", e);
            this.showToast(`Failed to dispatch referral request for ${referralType}.`, "error");
        }
    },

    acknowledgeAlert: async function(caseNumber) {
        try {
            const res = await fetch(`/api/cases/${caseNumber}/alert/acknowledge`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    case_number: caseNumber,
                    acknowledged_by: this.state.currentUser ? this.state.currentUser.name : "Officer Rajesh Kumar",
                    notes: "High-risk alert verified and prioritized for triage escalation."
                })
            });

            if (!res.ok) {
                throw new Error("Alert acknowledgement failed");
            }

            const data = await res.json();
            this.showToast(`Case ${caseNumber} alert acknowledged by ${data.assigned_officer}.`, "success");

            await this.fetchCases();
            if (this.state.selectedCase && this.state.selectedCase.case_number === caseNumber) {
                await this.viewCaseDetails(caseNumber);
            }
        } catch (e) {
            console.error("Acknowledge alert error:", e);
            this.showToast("Failed to acknowledge alert.", "error");
        }
    },

    recordSupportOutcome: async function(caseNumber, received, notes) {
        try {
            const res = await fetch(`/api/cases/${caseNumber}/support-outcome`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    case_number: caseNumber,
                    support_received: !!received,
                    outcome_notes: notes || "Support verification completed.",
                    recorded_by: this.state.currentUser ? this.state.currentUser.name : "Officer Rajesh Kumar"
                })
            });

            if (!res.ok) {
                throw new Error("Support outcome recording failed");
            }

            const data = await res.json();
            this.showToast(`Support outcome recorded for ${caseNumber}. Case status: ${data.case_status}`, "success");

            await this.fetchCases();
            if (this.state.selectedCase && this.state.selectedCase.case_number === caseNumber) {
                await this.viewCaseDetails(caseNumber);
            }
        } catch (e) {
            console.error("Support outcome error:", e);
            this.showToast("Failed to record support outcome.", "error");
        }
    },

    submitSupportOutcome: function() {
        if (!this.state.selectedCase) {
            this.showToast("No active case selected.", "warning");
            return;
        }
        const received = document.getElementById("cdSupportReceivedInput") ? document.getElementById("cdSupportReceivedInput").checked : false;
        const notes = document.getElementById("cdOutcomeNotesInput") ? document.getElementById("cdOutcomeNotesInput").value.trim() : "";
        this.recordSupportOutcome(this.state.selectedCase.case_number, received, notes);
    },

    renderHighRiskAlertBanner: function() {
        const countEl = document.getElementById("highRiskAlertCount");
        const container = document.getElementById("officerAlertCardsContainer");
        if (!container) return;

        const alerts = this.state.cases.filter(c =>
            c.alert_status === "High-Risk Alert" ||
            c.risk_level === "CRITICAL" ||
            (c.risk_level === "HIGH" && c.alert_status !== "Acknowledged")
        );

        if (countEl) countEl.textContent = alerts.length;

        if (alerts.length === 0) {
            container.innerHTML = `
                <div class="col-span-full p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-900 text-xs font-semibold flex items-center space-x-2">
                    <span class="w-2.5 h-2.5 bg-emerald-500 rounded-full"></span>
                    <span>All high-risk and critical safety alerts have been reviewed and acknowledged by authorized officers.</span>
                </div>
            `;
            return;
        }

        container.innerHTML = alerts.map(c => `
            <div class="p-3.5 bg-white border border-rose-200 rounded-xl shadow-sm flex flex-col justify-between hover:border-rose-400 transition">
                <div>
                    <div class="flex items-center justify-between pb-2 border-b border-rose-100">
                        <span class="font-mono font-bold text-xs text-rose-900 flex items-center space-x-1">
                            <span class="w-2 h-2 rounded-full bg-rose-600 animate-ping"></span>
                            <span>${c.case_number}</span>
                        </span>
                        <span class="px-2 py-0.5 rounded text-[10px] font-black ${c.risk_level === 'CRITICAL' ? 'bg-rose-600 text-white' : 'bg-orange-500 text-white'}">
                            ${c.risk_level}
                        </span>
                    </div>

                    <div class="mt-2 text-xs text-slate-700">
                        <div class="font-semibold text-slate-900">${c.complainant_alias || 'Complainant'} • ${c.language}</div>
                        <div class="text-[11px] text-slate-500 mt-0.5">SVI: <strong class="text-rose-700">${c.svi_score}/100</strong> (Stress: ${c.stress_score || c.svi_score}, Trauma: ${c.trauma_score || c.svi_score})</div>
                        <div class="text-[11px] text-slate-600 mt-1 line-clamp-2">
                            <strong>Action:</strong> ${c.recommended_next_action || 'Urgent human review required.'}
                        </div>
                    </div>
                </div>

                <div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between gap-2">
                    <span class="text-[10px] font-bold ${c.referral_status && c.referral_status !== 'None' ? 'text-teal-700 bg-teal-50' : 'text-amber-700 bg-amber-50'} px-2 py-0.5 rounded">
                        ${c.referral_status || 'No Referral'}
                    </span>
                    <div class="flex items-center space-x-1.5">
                        ${c.alert_status !== 'Acknowledged' ? `
                            <button onclick="App.acknowledgeAlert('${c.case_number}')" class="px-2.5 py-1 rounded bg-rose-600 hover:bg-rose-700 text-white text-[11px] font-bold transition shadow-sm">
                                Acknowledge
                            </button>
                        ` : `
                            <span class="text-[11px] text-slate-400 font-medium">✓ Acknowledged</span>
                        `}
                        <button onclick="App.viewCaseDetails('${c.case_number}')" class="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 text-[11px] font-bold transition">
                            Review
                        </button>
                    </div>
                </div>
            </div>
        `).join("");
    },

    // ==========================================
    // VICTIM FIRST-CONTACT & CHAT PORTAL
    // ==========================================
    setVictimLanguage: function(lang) {
        this.state.selectedLanguage = lang;
        I18N.setLanguage(lang);
        const langDisplay = document.getElementById("selectedLangDisplay");
        if (langDisplay) langDisplay.textContent = lang;

        // Auto-populate empathetic demo phrase for convenience
        const sampleNarratives = {
            "Telugu": "నమస్కారం... మమ్మల్ని ఊరి నుంచి వెలివేశారు... పొలం లాక్కుంటామని కొట్టారు... రాత్రిళ్ళు ఇంటి చుట్టూ తిరుగుతూ చంపేస్తామని బెదిరిస్తున్నారు... ఎవరూ సహాయం చేయడం లేదు... పిల్లలతో కలిసి ఇంట్లో దాక్కున్నాం... చాలా భయంగా ఉంది...",
            "Hindi": "सर बचाओ! हथियार लेकर लोग हमारे घर के बाहर खड़े हैं और दरवाजा तोड़ने की कोशिश कर रहे हैं... बहुत डर लग रहा है, जिंदा नहीं छोड़ेंगे कह रहे हैं...",
            "Kannada": "ನಮಗೆ ಪುನರ್ವಸತಿ ಪರಿಹಾರ ಇನ್ನೂ ಸಿಕ್ಕಿಲ್ಲ... ಕಳೆದ ಮೂರು ತಿಂಗಳಿಂದ ಮನೆ ಕಳೆದುಕೊಂಡು ತುಂಬಾ ಸಂಕಷ್ಟದಲ್ಲಿದ್ದೇವೆ... ಮಕ್ಕಳಿಗೆ ಊಟಕ್ಕೂ ತೊಂದರೆಯಾಗಿದೆ...",
            "Tamil": "எங்கள் தெருவில் தண்ணீர் பிடிக்க விடாமல் தடுத்து மிரட்டுகிறார்கள். சாதி சொல்லி அவமானப்படுத்தினார்கள்... மிகவும் பயமாக இருக்கிறது...",
            "English": "Our family is facing continuous intimidation and death threats from dominant landlords following our land title registration. They have cut our water access and threaten to burn our home."
        };
        const input = document.getElementById("victimTextInput");
        if (input && (!input.value || input.value.trim() === "")) {
            input.value = sampleNarratives[lang] || sampleNarratives["English"];
        }
    },

    setChannel: function(channelName) {
        this.state.selectedChannel = channelName;
        document.querySelectorAll(".channel-btn").forEach(b => {
            b.classList.remove("border-teal-600", "bg-teal-50", "text-teal-900");
            b.classList.add("border-slate-200", "bg-white", "text-slate-700");
        });
        const active = document.getElementById(`chan-${channelName.replace(/\s+/g, '')}`);
        if (active) {
            active.classList.add("border-teal-600", "bg-teal-50", "text-teal-900");
            active.classList.remove("border-slate-200", "bg-white", "text-slate-700");
        }

        const voiceSection = document.getElementById("voiceRecorderContainer");
        const isVoiceChannel = ["Voice Helpline", "Voice Recording Upload", "IVRS"].includes(channelName);
        if (voiceSection) {
            if (isVoiceChannel) voiceSection.classList.remove("hidden");
            else voiceSection.classList.add("hidden");
        }
    },

    toggleRecording: async function() {
        const btn = document.getElementById("recordVoiceBtn");
        const statusEl = document.getElementById("recordingStatusText");
        
        if (!AudioEngine.isRecording) {
            await AudioEngine.startRecording("waveformCanvas", "recordDurationTimer");
            btn.classList.remove("bg-teal-600", "hover:bg-teal-700");
            btn.classList.add("bg-rose-600", "hover:bg-rose-700");
            btn.innerHTML = `<span class="inline-block w-3 h-3 bg-white rounded-sm mr-2 animate-pulse"></span> Stop Recording`;
            if (statusEl) statusEl.textContent = "Listening to acoustic prosody & hesitation markers in real-time...";
        } else {
            AudioEngine.stopRecording();
            btn.classList.add("bg-teal-600", "hover:bg-teal-700");
            btn.classList.remove("bg-rose-600", "hover:bg-rose-700");
            btn.innerHTML = `<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg> Record Voice`;
            if (statusEl) statusEl.textContent = "Voice interaction captured. Ready for multilingual stress assessment.";
            
            // Auto run assessment
            this.runInteractiveAssessment();
        }
    },

    setConsent: function(consented) {
        this.state.victimConsent = consented;
        const banner = document.getElementById("consentStatusBanner");
        const submitBtn = document.getElementById("submitCaseBtn");
        const consentModal = document.getElementById("consentModal");

        if (consentModal) consentModal.classList.add("hidden");

        if (consented) {
            if (banner) {
                banner.className = "p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center justify-between";
                banner.innerHTML = `
                    <div class="flex items-center space-x-2">
                        <span class="w-2.5 h-2.5 bg-emerald-500 rounded-full"></span>
                        <span>Consent recorded: Authorized for AI triage and support allocation.</span>
                    </div>
                    <button onclick="App.showConsentModal()" class="text-emerald-700 underline font-medium hover:text-emerald-900">Review Rights</button>
                `;
            }
            if (submitBtn) submitBtn.disabled = false;
            this.showToast("Consent registered: AI triage assessment active.", "success");
        } else {
            if (banner) {
                banner.className = "p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 flex items-center justify-between";
                banner.innerHTML = `
                    <div class="flex items-center space-x-2">
                        <span class="w-2.5 h-2.5 bg-amber-500 rounded-full"></span>
                        <span>Consent declined: AI distress analysis bypassed. Manual routing only.</span>
                    </div>
                    <button onclick="App.showConsentModal()" class="text-amber-700 underline font-medium hover:text-amber-900">Grant Consent</button>
                `;
            }
            this.showToast("Consent declined: Assessment engine will not process interaction.", "warning");
        }
    },

    showConsentModal: function() {
        const modal = document.getElementById("consentModal");
        if (modal) modal.classList.remove("hidden");
    },

    clearVictimForm: function() {
        const input = document.getElementById("victimTextInput");
        if (input) input.value = "";
        const preview = document.getElementById("sviAssessmentPreview");
        if (preview) preview.classList.add("hidden");
        AudioEngine.stopRecording();
        document.getElementById("recordDurationTimer").textContent = "00:00";
        this.showToast("Conversation cleared.", "info");
    },

    triggerEmergencySOS: function() {
        const modal = document.getElementById("emergencyAlertModal");
        if (modal) modal.classList.remove("hidden");
    },

    closeEmergencyModal: function() {
        const modal = document.getElementById("emergencyAlertModal");
        if (modal) modal.classList.add("hidden");
    },

    quickExitToSafePage: function() {
        // Instant privacy blank page escape
        window.location.href = "https://www.google.com";
    },

    runInteractiveAssessment: async function() {
        if (!this.state.victimConsent) {
            this.showToast("Consent required to run AI stress assessment.", "warning");
            this.showConsentModal();
            return;
        }

        const rawText = document.getElementById("victimTextInput").value.trim();
        if (!rawText && !AudioEngine.isRecording) {
            this.showToast("Please provide a text or voice interaction description.", "warning");
            return;
        }

        const loadingSpinner = document.getElementById("assessmentLoadingSpinner");
        if (loadingSpinner) loadingSpinner.classList.remove("hidden");

        try {
            const res = await fetch("/api/assessment/analyze-interactive", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    channel: this.state.selectedChannel,
                    language: this.state.selectedLanguage,
                    raw_text: rawText,
                    audio_present: ["Voice Helpline", "Voice Recording Upload", "IVRS"].includes(this.state.selectedChannel),
                    audio_duration_sec: AudioEngine.getRecordedDurationSec(),
                    consent_given: true,
                    district: "Rangareddy",
                    state: "Telangana"
                })
            });

            if (!res.ok) {
                const err = await res.json();
                this.showToast(err.detail || "Assessment calculation error.", "error");
                return;
            }

            const data = await res.json();
            this.renderAssessmentPreview(data);
        } catch (e) {
            console.error("Assessment error:", e);
            this.showToast("Failed to run assessment simulation.", "error");
        } finally {
            if (loadingSpinner) loadingSpinner.classList.add("hidden");
        }
    },

    renderAssessmentPreview: function(data) {
        const preview = document.getElementById("sviAssessmentPreview");
        if (!preview) return;
        preview.classList.remove("hidden");

        const svi = data.svi;
        const scoreBadge = document.getElementById("previewSviScore");
        const levelBadge = document.getElementById("previewRiskLevel");
        const summaryText = document.getElementById("previewSummaryText");
        const factorsContainer = document.getElementById("previewFactorsContainer");
        const urgentBanner = document.getElementById("previewUrgentBanner");

        if (scoreBadge) scoreBadge.textContent = `${svi.score} / 100`;

        // Color coding for risk tiers
        const colors = {
            "LOW": "bg-emerald-100 text-emerald-800 border-emerald-300",
            "MODERATE": "bg-amber-100 text-amber-800 border-amber-300",
            "HIGH": "bg-orange-100 text-orange-800 border-orange-300",
            "CRITICAL": "bg-rose-100 text-rose-800 border-rose-300 animate-pulse"
        };
        if (levelBadge) {
            levelBadge.className = `px-3 py-1 rounded-full text-xs font-bold border ${colors[svi.risk_level] || colors["LOW"]}`;
            levelBadge.textContent = svi.risk_level;
        }

        if (summaryText) summaryText.textContent = svi.summary_text;

        // Emergency state
        if (urgentBanner) {
            if (svi.critical_safety_alert || svi.risk_level === "CRITICAL") {
                urgentBanner.classList.remove("hidden");
            } else {
                urgentBanner.classList.add("hidden");
            }
        }

        // Render Explainable factors
        if (factorsContainer) {
            factorsContainer.innerHTML = svi.explainability_factors.map(f => `
                <div class="p-2.5 rounded bg-slate-50 border border-slate-200 text-xs">
                    <div class="flex items-center justify-between font-semibold text-slate-800">
                        <span>✓ ${f.factor}</span>
                        <span class="text-teal-700">${f.weight}% Weight</span>
                    </div>
                    <div class="text-slate-600 mt-1">${f.description}</div>
                    ${f.evidence_snippet ? `<div class="text-[11px] text-slate-500 italic mt-1 font-mono">Evidence: "${f.evidence_snippet}"</div>` : ''}
                </div>
            `).join("");
        }

        // Auto render mini radar chart
        AppCharts.renderEmotionRadar("previewEmotionChart", data.emotion_metrics);
    },

    submitVictimCase: async function() {
        const rawText = document.getElementById("victimTextInput").value.trim();
        if (!rawText) {
            this.showToast("Please enter or record a complaint description.", "warning");
            return;
        }

        try {
            const res = await fetch("/api/assessment/submit-case", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    channel: this.state.selectedChannel,
                    language: this.state.selectedLanguage,
                    raw_text: rawText,
                    audio_present: ["Voice Helpline", "Voice Recording Upload", "IVRS"].includes(this.state.selectedChannel),
                    audio_duration_sec: AudioEngine.getRecordedDurationSec(),
                    consent_given: true,
                    district: "Rangareddy",
                    state: "Telangana",
                    complainant_alias: "Complainant-Citizen"
                })
            });

            const data = await res.json();
            if (data.success) {
                this.showToast(`Case ${data.case.case_number} registered and forwarded for authorized human review!`, "success");
                
                // Show victim dashboard for this case
                this.renderVictimDashboard(data.case);
            }
        } catch (e) {
            console.error("Submission failed:", e);
            this.showToast("Failed to submit case.", "error");
        }
    },

    renderVictimDashboard: function(caseRecord) {
        document.getElementById("victimSubmissionSection").classList.add("hidden");
        const dash = document.getElementById("victimDashboardSection");
        if (!dash) return;
        dash.classList.remove("hidden");

        document.getElementById("vdCaseNumber").textContent = caseRecord.case_number;
        document.getElementById("vdDate").textContent = caseRecord.created_at;
        document.getElementById("vdStatus").textContent = caseRecord.status;
        document.getElementById("vdLanguage").textContent = caseRecord.language;
        document.getElementById("vdChannel").textContent = caseRecord.channel;
        document.getElementById("vdSviBadge").textContent = `SVI: ${caseRecord.svi_score}/100 (${caseRecord.risk_level})`;

        // 7-Stage Case Progress Timeline
        const timelineEl = document.getElementById("vdTimelineList");
        if (timelineEl) {
            const stages = [
                { title: "Complaint Registered", desc: "Digital intake recorded via " + caseRecord.channel, active: true },
                { title: "Initial Contact", desc: "First-contact session established", active: true },
                { title: "AI-Assisted Assessment", desc: `SVI ${caseRecord.svi_score}/100 categorized`, active: true },
                { title: "Human Review", desc: "Officer assigned for triage verification", active: caseRecord.status !== "Pending" },
                { title: "Support Assigned", desc: "Counselling or legal aid counsel dispatched", active: caseRecord.support_recommendations.some(r => r.status === "Assigned") },
                { title: "Follow-up", desc: "Scheduled safety & psychological check-in", active: false },
                { title: "Resolution", desc: "Formal resolution and case sign-off", active: false }
            ];

            timelineEl.innerHTML = stages.map((s, idx) => `
                <div class="flex items-start space-x-3 relative pb-6 last:pb-0">
                    <div class="flex flex-col items-center">
                        <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${s.active ? 'bg-teal-600 text-white shadow-sm' : 'bg-slate-200 text-slate-500'}">
                            ${idx + 1}
                        </div>
                        ${idx < stages.length - 1 ? `<div class="w-0.5 h-full ${s.active ? 'bg-teal-600' : 'bg-slate-200'} mt-1"></div>` : ''}
                    </div>
                    <div class="pt-0.5">
                        <div class="text-xs font-semibold ${s.active ? 'text-teal-900' : 'text-slate-500'}">${s.title}</div>
                        <div class="text-xs text-slate-600">${s.desc}</div>
                    </div>
                </div>
            `).join("");
        }
    },

    returnToComplaintForm: function() {
        document.getElementById("victimSubmissionSection").classList.remove("hidden");
        document.getElementById("victimDashboardSection").classList.add("hidden");
        this.clearVictimForm();
    },

    // ==========================================
    // AUTHORIZED OFFICER DASHBOARD & CASES TABLE
    // ==========================================
    fetchCases: async function() {
        const risk = document.getElementById("filterRisk") ? document.getElementById("filterRisk").value : "ALL";
        const lang = document.getElementById("filterLanguage") ? document.getElementById("filterLanguage").value : "ALL";
        const channel = document.getElementById("filterChannel") ? document.getElementById("filterChannel").value : "ALL";
        const status = document.getElementById("filterStatus") ? document.getElementById("filterStatus").value : "ALL";
        const priority = document.getElementById("filterPriority") ? document.getElementById("filterPriority").value : "ALL";
        const referral = document.getElementById("filterReferral") ? document.getElementById("filterReferral").value : "ALL";
        const search = document.getElementById("searchCasesInput") ? document.getElementById("searchCasesInput").value : "";

        this.state.filterPriority = priority;
        this.state.filterReferral = referral;

        try {
            const q = new URLSearchParams({
                risk, language: lang, channel, status, search
            });
            const res = await fetch(`/api/cases?${q.toString()}`);
            let cases = await res.json();

            // Client-side filter for Priority
            if (priority && priority !== "ALL") {
                cases = cases.filter(c => (c.priority || "Standard").toUpperCase() === priority.toUpperCase());
            }

            // Client-side filter for Referral Status
            if (referral && referral !== "ALL") {
                if (referral === "None") {
                    cases = cases.filter(c => !c.referral_status || c.referral_status === "None");
                } else {
                    cases = cases.filter(c => (c.referral_status || "").toLowerCase().includes(referral.toLowerCase()));
                }
            }

            this.state.cases = cases;
            this.renderCasesTable();
            this.updateOfficerKpis();
            this.renderHighRiskAlertBanner();

            const countEl = document.getElementById("casesCountDisplay");
            if (countEl) countEl.textContent = `${cases.length}`;
        } catch (e) {
            console.error("Failed to load cases:", e);
        }
    },

    updateOfficerKpis: function() {
        const total = this.state.cases.length;
        const high = this.state.cases.filter(c => c.risk_level === "HIGH").length;
        const crit = this.state.cases.filter(c => c.risk_level === "CRITICAL").length;
        const pending = this.state.cases.filter(c => c.status === "Pending" || c.status === "Under Review").length;

        document.getElementById("kpiTotalCases").textContent = total;
        document.getElementById("kpiHighRisk").textContent = high;
        document.getElementById("kpiCritical").textContent = crit;
        document.getElementById("kpiPendingReview").textContent = pending;
    },

    renderCasesTable: function() {
        const tbody = document.getElementById("casesTableBody");
        if (!tbody) return;

        if (this.state.cases.length === 0) {
            tbody.innerHTML = `<tr><td colspan="12" class="text-center py-8 text-sm text-slate-500">No cases match the specified triage filters.</td></tr>`;
            return;
        }

        const riskBadge = (lvl) => {
            if (lvl === "CRITICAL") return `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-300 animate-pulse">🔴 CRITICAL</span>`;
            if (lvl === "HIGH") return `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-orange-100 text-orange-800 border border-orange-300">🟠 HIGH</span>`;
            if (lvl === "MODERATE") return `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300">🟡 MODERATE</span>`;
            return `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">🟢 LOW</span>`;
        };

        const priorityBadge = (p) => {
            if (p === "Urgent") return `<span class="px-2 py-0.5 rounded text-[10px] font-black bg-rose-100 text-rose-800 border border-rose-300">🚨 Urgent</span>`;
            if (p === "Priority") return `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">⚡ Priority</span>`;
            return `<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700">Standard</span>`;
        };

        const alertBadge = (a) => {
            if (a === "High-Risk Alert") return `<span class="px-2 py-0.5 rounded text-[10px] font-black bg-rose-600 text-white animate-pulse">ALERT</span>`;
            if (a === "Acknowledged") return `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800">Ack'd</span>`;
            return `<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-500">Normal</span>`;
        };

        const referralBadge = (r) => {
            if (r && r !== "None") return `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-teal-100 text-teal-800 whitespace-nowrap">${r}</span>`;
            return `<span class="px-2 py-0.5 rounded text-[11px] text-slate-400">None</span>`;
        };

        tbody.innerHTML = this.state.cases.map(c => `
            <tr class="hover:bg-slate-50 transition border-b border-slate-100">
                <td class="py-3 px-3 text-xs font-mono font-bold text-teal-800 whitespace-nowrap">
                    ${c.case_number}
                    ${c.critical_safety_flag ? `<span class="ml-1 text-[9px] bg-rose-600 text-white px-1 py-0.5 rounded font-sans">SOS</span>` : ''}
                </td>
                <td class="py-3 px-3 text-xs text-slate-600 whitespace-nowrap">${c.created_at}</td>
                <td class="py-3 px-3 text-xs text-slate-700 font-medium whitespace-nowrap">${c.complainant_alias || 'Complainant'}</td>
                <td class="py-3 px-3 text-xs text-slate-700 font-medium whitespace-nowrap">${c.language}</td>
                <td class="py-3 px-3 text-xs text-slate-600 whitespace-nowrap">${c.channel}</td>
                <td class="py-3 px-3 text-xs font-bold ${c.svi_score >= 66 ? 'text-rose-700' : 'text-slate-800'} whitespace-nowrap">
                    ${c.svi_score} / 100
                </td>
                <td class="py-3 px-3 text-xs font-mono font-semibold text-slate-700 whitespace-nowrap">
                    <span class="text-rose-700">${c.stress_score || c.svi_score}</span> / <span class="text-purple-700">${c.trauma_score || c.svi_score}</span>
                </td>
                <td class="py-3 px-3 text-xs whitespace-nowrap">${riskBadge(c.risk_level)}</td>
                <td class="py-3 px-3 text-xs whitespace-nowrap">${priorityBadge(c.priority)}</td>
                <td class="py-3 px-3 text-xs whitespace-nowrap">${alertBadge(c.alert_status)}</td>
                <td class="py-3 px-3 text-xs">${referralBadge(c.referral_status)}</td>
                <td class="py-3 px-3 text-xs whitespace-nowrap">
                    <button onclick="App.viewCaseDetails('${c.case_number}')" class="px-2.5 py-1 rounded bg-teal-600 hover:bg-teal-700 text-white font-medium text-xs transition">
                        Review Dossier
                    </button>
                </td>
            </tr>
        `).join("");
    },

    // ==========================================
    // CASE DETAILS & DEEP TRIAGE DOSSIER
    // ==========================================
    viewCaseDetails: async function(caseNumber) {
        try {
            const res = await fetch(`/api/cases/${caseNumber}`);
            if (!res.ok) {
                this.showToast("Case not found.", "error");
                return;
            }
            this.state.selectedCase = await res.json();
            this.renderCaseDetailsView(this.state.selectedCase);
            this.switchTab("case-details-view");
        } catch (e) {
            console.error("Failed to load case details:", e);
        }
    },

    renderCaseDetailsView: function(c) {
        document.getElementById("cdCaseNumber").textContent = c.case_number;
        document.getElementById("cdDate").textContent = c.created_at;
        document.getElementById("cdLanguage").textContent = c.language;
        document.getElementById("cdChannel").textContent = c.channel;
        document.getElementById("cdDistrict").textContent = `${c.district}, ${c.state}`;
        document.getElementById("cdComplainantAlias").textContent = c.complainant_alias;
        document.getElementById("cdSviScore").textContent = `${c.svi_score} / 100`;

        // Stress / Trauma Scores
        const stressEl = document.getElementById("cdStressScore");
        if (stressEl) stressEl.textContent = `${c.stress_score || c.svi_score} / 100`;

        const traumaEl = document.getElementById("cdTraumaScore");
        if (traumaEl) traumaEl.textContent = `${c.trauma_score || c.svi_score} / 100`;

        // Emotional State
        const emoEl = document.getElementById("cdEmotionalState");
        if (emoEl) emoEl.textContent = c.emotional_state || "Severe Fear & Threat Trauma";

        // Recommended Next Action
        const actionEl = document.getElementById("cdRecommendedNextAction");
        if (actionEl) actionEl.textContent = c.recommended_next_action || "Immediate authorized review advised.";

        // Priority Badge
        const prioBadge = document.getElementById("cdPriorityBadge");
        if (prioBadge) {
            prioBadge.textContent = c.priority || "Standard";
            prioBadge.className = `px-2 py-0.5 rounded text-xs font-bold ${
                c.priority === 'Urgent' ? 'bg-rose-100 text-rose-800 border border-rose-300' :
                c.priority === 'Priority' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                'bg-slate-100 text-slate-700'
            }`;
        }

        // Alert Status Badge
        const alertBadge = document.getElementById("cdAlertStatusBadge");
        if (alertBadge) {
            alertBadge.textContent = c.alert_status || "Normal";
            alertBadge.className = `px-2 py-0.5 rounded text-xs font-bold ${
                c.alert_status === 'High-Risk Alert' ? 'bg-rose-600 text-white animate-pulse' :
                c.alert_status === 'Acknowledged' ? 'bg-blue-100 text-blue-800' :
                'bg-slate-100 text-slate-700'
            }`;
        }

        // Referral Status Badge
        const refBadge = document.getElementById("cdReferralStatusBadge");
        if (refBadge) {
            refBadge.textContent = c.referral_status || "None";
            refBadge.className = `px-2 py-0.5 rounded text-xs font-bold ${
                c.referral_status && c.referral_status !== 'None' ? 'bg-teal-100 text-teal-800 border border-teal-300' :
                'bg-slate-100 text-slate-700'
            }`;
        }

        // Support Outcome Form values
        const supportRecInput = document.getElementById("cdSupportReceivedInput");
        if (supportRecInput) supportRecInput.checked = !!c.support_received;

        const outcomeNotesInput = document.getElementById("cdOutcomeNotesInput");
        if (outcomeNotesInput) outcomeNotesInput.value = c.support_outcome_notes || "";

        const riskBadge = document.getElementById("cdRiskBadge");
        if (riskBadge) {
            riskBadge.textContent = c.risk_level;
            riskBadge.className = `px-3 py-1 rounded-full text-xs font-bold ${
                c.risk_level === 'CRITICAL' ? 'bg-rose-100 text-rose-800 border border-rose-300' :
                c.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800 border border-orange-300' :
                c.risk_level === 'MODERATE' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                'bg-emerald-100 text-emerald-800 border border-emerald-300'
            }`;
        }

        // Emergency Alert Header
        const emergencyBanner = document.getElementById("cdEmergencyBanner");
        if (emergencyBanner) {
            if (c.critical_safety_flag || c.risk_level === "CRITICAL") {
                emergencyBanner.classList.remove("hidden");
            } else {
                emergencyBanner.classList.add("hidden");
            }
        }

        // Confidence Indicator
        const confEl = document.getElementById("cdConfidenceBadge");
        if (confEl) confEl.textContent = `AI Confidence: ${Math.round(c.confidence * 100)}%`;

        // Render Charts
        if (c.emotion_metrics) {
            AppCharts.renderEmotionRadar("cdEmotionRadarChart", c.emotion_metrics);
        }
        if (c.speech_metrics) {
            AppCharts.renderSpeechMetrics("cdSpeechBarChart", c.speech_metrics);
        }

        // Render Explainable AI Cards
        const factorsContainer = document.getElementById("cdExplainabilityCards");
        if (factorsContainer) {
            factorsContainer.innerHTML = c.explainability.map(f => `
                <div class="p-3 rounded-lg border border-slate-200 bg-white shadow-sm hover:border-teal-400 transition">
                    <div class="flex items-center justify-between font-semibold text-xs text-slate-800">
                        <span class="flex items-center">
                            <span class="w-2 h-2 rounded-full mr-2 ${f.indicator_group === 'Safety' ? 'bg-rose-500' : 'bg-teal-500'}"></span>
                            ${f.factor}
                        </span>
                        <span class="text-[11px] font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">Weight: ${f.weight}%</span>
                    </div>
                    <div class="text-xs text-slate-600 mt-1.5 leading-relaxed">${f.description}</div>
                    ${f.evidence_snippet ? `
                        <div class="mt-2 text-[11px] bg-slate-50 text-slate-700 px-2.5 py-1.5 rounded font-mono border border-slate-100">
                            <strong>Evidence:</strong> "${f.evidence_snippet}"
                        </div>
                    ` : ''}
                </div>
            `).join("");
        }

        // Render Support Recommendations
        const recsContainer = document.getElementById("cdRecommendationsList");
        if (recsContainer) {
            recsContainer.innerHTML = c.support_recommendations.map(r => `
                <div class="p-4 rounded-lg border ${r.status === 'Assigned' ? 'border-teal-300 bg-teal-50/30' : 'border-slate-200 bg-white'} shadow-sm">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <span class="font-bold text-sm text-slate-800">${r.service_type}</span>
                            <span class="text-[11px] px-2 py-0.5 rounded font-medium ${r.priority === 'Urgent' ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-600'}">${r.priority}</span>
                            <span class="text-xs font-semibold ${r.status === 'Assigned' ? 'text-teal-700' : r.status === 'Rejected' ? 'text-rose-700' : 'text-amber-700'}">
                                [${r.status}]
                            </span>
                        </div>
                        <div class="flex items-center space-x-2">
                            ${r.status === 'Pending Review' ? `
                                <button onclick="App.openAssignModal('${r.id}', '${r.service_type}')" class="px-2.5 py-1 rounded bg-teal-600 hover:bg-teal-700 text-white text-xs font-medium">Assign</button>
                                <button onclick="App.rejectRecommendation('${r.id}')" class="px-2.5 py-1 rounded bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-medium">Reject</button>
                            ` : `
                                <span class="text-xs text-slate-500 italic">Confirmed by: ${r.reviewed_by || 'Officer'}</span>
                            `}
                        </div>
                    </div>
                    <div class="text-xs text-slate-600 mt-1">${r.reason}</div>
                    ${r.assigned_to ? `<div class="mt-2 text-xs font-medium text-teal-800 bg-teal-100/60 p-2 rounded">Assigned to: ${r.assigned_to} | Notes: ${r.human_notes || 'Authorized'}</div>` : ''}
                </div>
            `).join("");
        }

        // Render Chronological Timeline
        const tlContainer = document.getElementById("cdTimelineContainer");
        if (tlContainer) {
            tlContainer.innerHTML = c.timeline.map((t, idx) => `
                <div class="flex items-start space-x-3 relative pb-5 last:pb-0">
                    <div class="flex flex-col items-center">
                        <div class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${t.status === 'done' ? 'bg-teal-600 text-white' : 'bg-amber-500 text-white animate-pulse'}">
                            ${idx + 1}
                        </div>
                        ${idx < c.timeline.length - 1 ? `<div class="w-0.5 h-full bg-slate-200 mt-1"></div>` : ''}
                    </div>
                    <div>
                        <div class="text-xs font-mono text-slate-500">${t.time}</div>
                        <div class="text-xs font-bold text-slate-800">${t.title}</div>
                        <div class="text-xs text-slate-600 mt-0.5">${t.desc}</div>
                    </div>
                </div>
            `).join("");
        }
    },

    openAssignModal: function(recId, serviceType) {
        document.getElementById("assignRecId").value = recId;
        document.getElementById("assignModalServiceTitle").textContent = serviceType;
        document.getElementById("assignModal").classList.remove("hidden");
    },

    closeAssignModal: function() {
        document.getElementById("assignModal").classList.add("hidden");
    },

    confirmAssignment: async function() {
        const recId = document.getElementById("assignRecId").value;
        const assignee = document.getElementById("assigneeSelect").value;
        const notes = document.getElementById("assignNotesInput").value;

        if (!this.state.selectedCase) return;

        try {
            const res = await fetch(`/api/cases/${this.state.selectedCase.case_number}/recommendations/${recId}/action`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    action: "ASSIGN",
                    assigned_to: assignee,
                    notes: notes,
                    reviewer_name: this.state.currentUser.name
                })
            });

            const data = await res.json();
            if (data.success) {
                this.closeAssignModal();
                this.showToast(`Support service successfully assigned to: ${assignee}`, "success");
                // Reload dossier
                await this.viewCaseDetails(this.state.selectedCase.case_number);
            }
        } catch (e) {
            console.error("Assignment failed:", e);
        }
    },

    rejectRecommendation: async function(recId) {
        const reason = prompt("Please provide reason for rejecting this AI support recommendation:");
        if (reason === null) return;

        try {
            const res = await fetch(`/api/cases/${this.state.selectedCase.case_number}/recommendations/${recId}/action`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    action: "REJECT",
                    notes: reason,
                    reviewer_name: this.state.currentUser.name
                })
            });
            const data = await res.json();
            if (data.success) {
                this.showToast("Recommendation marked as Rejected with audit record.", "info");
                await this.viewCaseDetails(this.state.selectedCase.case_number);
            }
        } catch (e) {
            console.error("Rejection error:", e);
        }
    },

    triggerCaseEmergencyAction: async function(actionType) {
        if (!this.state.selectedCase) return;

        const confirmAction = confirm(`Execute simulated emergency protocol: [${actionType}] for Case ${this.state.selectedCase.case_number}?`);
        if (!confirmAction) return;

        try {
            const res = await fetch(`/api/cases/${this.state.selectedCase.case_number}/emergency-action`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ action_type: actionType })
            });

            const data = await res.json();
            if (data.success) {
                this.showToast(`Emergency alert '${actionType}' dispatched to on-duty response team!`, "success");
                await this.viewCaseDetails(this.state.selectedCase.case_number);
            }
        } catch (e) {
            console.error("Emergency dispatch error:", e);
        }
    },

    openEvidenceModal: function() {
        if (!this.state.selectedCase) return;
        const c = this.state.selectedCase;
        document.getElementById("evidenceCaseNum").textContent = c.case_number;
        document.getElementById("evidenceLanguage").textContent = c.language;
        document.getElementById("evidenceMaskedNarrative").textContent = c.masked_narrative || "No narrative available.";

        const rawContainer = document.getElementById("evidenceRawTranscript");
        // Anonymization / sensitive data masking toggle
        rawContainer.textContent = c.raw_text || "(Encrypted raw voice transcript protected under statutory privilege)";

        document.getElementById("evidenceModal").classList.remove("hidden");
    },

    closeEvidenceModal: function() {
        document.getElementById("evidenceModal").classList.add("hidden");
    },

    // ==========================================
    // FOLLOW-UP MANAGEMENT SYSTEM
    // ==========================================
    fetchFollowups: async function(status = "ALL") {
        try {
            const res = await fetch(`/api/followups?status=${status}`);
            this.state.followups = await res.json();
            this.renderFollowupsList();
        } catch (e) {
            console.error("Failed to load follow-ups:", e);
        }
    },

    renderFollowupsList: function() {
        const container = document.getElementById("followupsContainer");
        if (!container) return;

        if (this.state.followups.length === 0) {
            container.innerHTML = `<div class="text-center py-10 text-slate-500 text-xs">No follow-ups found under this status.</div>`;
            return;
        }

        container.innerHTML = this.state.followups.map(f => `
            <div class="p-4 rounded-lg border border-slate-200 bg-white shadow-sm flex flex-col md:flex-row md:items-center md:justify-between space-y-3 md:space-y-0">
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="text-xs font-mono font-bold text-teal-800">${f.case_number}</span>
                        <span class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">${f.category}</span>
                        <span class="text-xs px-2 py-0.5 rounded font-bold ${
                            f.status === 'Completed' ? 'bg-emerald-100 text-emerald-800' :
                            f.status === 'Overdue' ? 'bg-rose-100 text-rose-800 animate-pulse' :
                            'bg-blue-100 text-blue-800'
                        }">${f.status}</span>
                    </div>
                    <div class="text-xs text-slate-700 font-medium mt-1">${f.notes}</div>
                    <div class="text-[11px] text-slate-500 mt-1">Scheduled: ${f.scheduled_date} at ${f.scheduled_time} | Assigned: ${f.assigned_to}</div>
                </div>
                <div class="flex items-center space-x-2">
                    ${f.status !== 'Completed' ? `
                        <button onclick="App.markFollowupStatus('${f.id}', 'Completed')" class="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium">Mark Done</button>
                    ` : `
                        <span class="text-xs text-emerald-700 font-semibold">✓ Completed</span>
                    `}
                    <button onclick="App.viewCaseDetails('${f.case_number}')" class="px-3 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium">View Dossier</button>
                </div>
            </div>
        `).join("");

        // Render Follow-up Vulnerability Progression Chart if historical data available
        const withHistory = this.state.followups.find(f => f.historical_svi && f.historical_svi.length > 1);
        if (withHistory) {
            document.getElementById("vulnerabilityTimelineCard").classList.remove("hidden");
            document.getElementById("vulnCaseNum").textContent = withHistory.case_number;
            AppCharts.renderVulnerabilityTimeline("followupVulnerabilityChart", withHistory.historical_svi);
        }
    },

    markFollowupStatus: async function(id, newStatus) {
        try {
            const res = await fetch(`/api/followups/${id}/status?new_status=${newStatus}`, { method: "PUT" });
            const data = await res.json();
            if (data.success) {
                this.showToast(`Follow-up updated to: ${newStatus}`, "success");
                this.fetchFollowups();
            }
        } catch (e) {
            console.error("Status update error:", e);
        }
    },

    openNewFollowupModal: function() {
        const caseNumInput = document.getElementById("folModalCaseNum");
        if (caseNumInput && this.state.selectedCase) {
            caseNumInput.value = this.state.selectedCase.case_number;
        }
        document.getElementById("newFollowupModal").classList.remove("hidden");
    },

    closeNewFollowupModal: function() {
        document.getElementById("newFollowupModal").classList.add("hidden");
    },

    submitNewFollowup: async function() {
        const caseNum = document.getElementById("folModalCaseNum").value;
        const category = document.getElementById("folModalCategory").value;
        const date = document.getElementById("folModalDate").value;
        const time = document.getElementById("folModalTime").value;
        const assignee = document.getElementById("folModalAssignee").value;
        const notes = document.getElementById("folModalNotes").value;

        if (!caseNum || !date || !time) {
            this.showToast("Please provide case number, date, and time.", "warning");
            return;
        }

        try {
            const res = await fetch("/api/followups", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    case_number: caseNum,
                    category: category,
                    scheduled_date: date,
                    scheduled_time: time,
                    assigned_to: assignee,
                    notes: notes
                })
            });
            const data = await res.json();
            if (data.success) {
                this.closeNewFollowupModal();
                this.showToast("Follow-up successfully scheduled.", "success");
                this.fetchFollowups();
            }
        } catch (e) {
            console.error("Scheduling error:", e);
        }
    },

    // ==========================================
    // SUPPORT RESOURCE DIRECTORY
    // ==========================================
    fetchResources: async function() {
        const state = document.getElementById("resFilterState") ? document.getElementById("resFilterState").value : "ALL";
        const cat = document.getElementById("resFilterCategory") ? document.getElementById("resFilterCategory").value : "ALL";
        const lang = document.getElementById("resFilterLanguage") ? document.getElementById("resFilterLanguage").value : "ALL";
        const is24x7 = document.getElementById("resFilter24x7") ? document.getElementById("resFilter24x7").checked : false;

        try {
            const q = new URLSearchParams({ state, category: cat, language: lang, available_24x7: is24x7 });
            const res = await fetch(`/api/resources?${q.toString()}`);
            this.state.resources = await res.json();
            this.renderResourcesList();
        } catch (e) {
            console.error("Failed to load resources:", e);
        }
    },

    renderResourcesList: function() {
        const grid = document.getElementById("resourcesGrid");
        if (!grid) return;

        if (this.state.resources.length === 0) {
            grid.innerHTML = `<div class="col-span-full text-center py-10 text-slate-500 text-xs">No support centers match these criteria.</div>`;
            return;
        }

        grid.innerHTML = this.state.resources.map(r => `
            <div class="p-4 rounded-xl border border-slate-200 bg-white shadow-sm hover:shadow-md transition flex flex-col justify-between">
                <div>
                    <div class="flex items-start justify-between">
                        <span class="text-xs font-bold text-teal-800 bg-teal-50 px-2 py-0.5 rounded">${r.category}</span>
                        ${r.available_24x7 ? `<span class="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">24x7 ACTIVE</span>` : ''}
                    </div>
                    <div class="font-bold text-sm text-slate-900 mt-2">${r.name}</div>
                    <div class="text-xs text-slate-600 mt-1">${r.address}</div>
                    <div class="text-xs text-slate-500 mt-1">📍 ${r.district}, ${r.state}</div>
                    <div class="mt-2 text-xs font-mono font-bold text-slate-800 bg-slate-50 p-1.5 rounded">
                        📞 ${r.phone}
                    </div>
                </div>
                <div class="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                    <span>Languages: ${r.languages.slice(0, 3).join(", ")}</span>
                    <span class="text-emerald-600 font-semibold">✓ Verified</span>
                </div>
            </div>
        `).join("");
    },

    // ==========================================
    // AGGREGATE ANALYTICS & EARLY WARNING ALERTS
    // ==========================================
    fetchAnalytics: async function() {
        try {
            const res = await fetch("/api/analytics");
            this.state.analytics = await res.json();
            this.renderAnalyticsCharts();
        } catch (e) {
            console.error("Failed to load analytics:", e);
        }
    },

    renderAnalyticsCharts: function() {
        const a = this.state.analytics;
        if (!a) return;

        document.getElementById("analyticsTotalCases").textContent = a.total_cases;
        document.getElementById("analyticsAvgSvi").textContent = `${a.average_svi} / 100`;

        // Render Charts
        AppCharts.renderRiskDonut("analyticsRiskDonutChart", a.risk_distribution);
        AppCharts.renderBarDistribution("analyticsLanguageChart", a.cases_by_language, "#0d9488");
        AppCharts.renderBarDistribution("analyticsChannelChart", a.cases_by_channel, "#0284c7");
        AppCharts.renderBarDistribution("analyticsStateChart", a.cases_by_state, "#6366f1");

        // Render Early Warning Alerts
        const alertContainer = document.getElementById("earlyWarningAlertsList");
        if (alertContainer && a.early_warning_alerts) {
            alertContainer.innerHTML = a.early_warning_alerts.map(ew => `
                <div class="p-4 rounded-xl border border-amber-300 bg-amber-50/70 shadow-sm">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-amber-900 flex items-center">
                            <span class="w-2.5 h-2.5 bg-amber-500 rounded-full mr-2 animate-ping"></span>
                            ${ew.title}
                        </span>
                        <span class="text-[11px] font-mono font-semibold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">${ew.timeframe}</span>
                    </div>
                    <div class="text-xs text-amber-900 mt-2 font-medium">Location: ${ew.district}, ${ew.state} | Cluster: ${ew.sample_size}</div>
                    <div class="text-xs text-amber-800 mt-1"><strong>Actionable Signal:</strong> ${ew.recommendation}</div>
                    <div class="text-[10px] text-amber-700 italic mt-2 border-t border-amber-200 pt-1">${ew.disclaimer}</div>
                </div>
            `).join("");
        }
    },

    // ==========================================
    // ADMIN PANEL & AUDIT LOGS
    // ==========================================
    fetchAuditLogs: async function() {
        const search = document.getElementById("searchAuditInput") ? document.getElementById("searchAuditInput").value : "";
        const access = document.getElementById("filterAuditType") ? document.getElementById("filterAuditType").value : "ALL";

        try {
            const q = new URLSearchParams({ search, access_type: access });
            const res = await fetch(`/api/audit?${q.toString()}`);
            this.state.auditLogs = await res.json();
            this.renderAuditLogsTable();
            this.checkSystemHealth();
        } catch (e) {
            console.error("Failed to load audit logs:", e);
        }
    },

    renderAuditLogsTable: function() {
        const tbody = document.getElementById("auditTableBody");
        if (!tbody) return;

        tbody.innerHTML = this.state.auditLogs.map(l => `
            <tr class="hover:bg-slate-50 transition border-b border-slate-100 text-xs">
                <td class="py-2.5 px-3 font-mono text-slate-500">${l.timestamp}</td>
                <td class="py-2.5 px-3 font-medium text-slate-800">${l.user_name}</td>
                <td class="py-2.5 px-3 text-slate-600">${l.role}</td>
                <td class="py-2.5 px-3 font-semibold text-teal-800">${l.action}</td>
                <td class="py-2.5 px-3 font-mono text-slate-700">${l.case_id || 'N/A'}</td>
                <td class="py-2.5 px-3 font-mono text-slate-500">${l.access_type}</td>
                <td class="py-2.5 px-3 text-slate-600 truncate max-w-xs">${l.details}</td>
            </tr>
        `).join("");
    },

    checkSystemHealth: async function() {
        try {
            const res = await fetch("/api/admin/system-health");
            const h = await res.json();
            document.getElementById("healthStatusText").textContent = `${h.status} (Uptime: ${h.uptime})`;
            document.getElementById("healthQueueText").textContent = `${h.triage_queue_depth} Cases Pending Triage`;
        } catch (e) {
            console.error("Health check error:", e);
        }
    },

    saveAdminConfig: async function() {
        const payload = {
            threshold_low_max: parseInt(document.getElementById("cfgThresholdLow").value),
            threshold_mod_max: parseInt(document.getElementById("cfgThresholdMod").value),
            threshold_high_max: parseInt(document.getElementById("cfgThresholdHigh").value),
            speech_weight: parseFloat(document.getElementById("cfgSpeechWeight").value),
            nlp_weight: parseFloat(document.getElementById("cfgNlpWeight").value),
            emotion_weight: parseFloat(document.getElementById("cfgEmotionWeight").value),
            confidence_threshold: 0.75,
            anonymize_analytics: true,
            auto_detect_language: true
        };

        try {
            const res = await fetch("/api/admin/config", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success) {
                this.state.config = data.config;
                this.updateConfigSliders();
                this.showToast("System SVI thresholds and model weights updated & audit logged.", "success");
            }
        } catch (e) {
            console.error("Config save failed:", e);
        }
    },

    exportAuditLogsCSV: function() {
        if (!this.state.auditLogs.length) return;
        const headers = ["Timestamp", "User", "Role", "Action", "CaseID", "AccessType", "Details"];
        const rows = this.state.auditLogs.map(l => [
            `"${l.timestamp}"`,
            `"${l.user_name}"`,
            `"${l.role}"`,
            `"${l.action}"`,
            `"${l.case_id || ''}"`,
            `"${l.access_type}"`,
            `"${(l.details || '').replace(/"/g, '""')}"`
        ]);
        const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `sahaaya_audit_logs_${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        this.showToast("Audit logs exported to CSV.", "info");
    },

    // ==========================================
    // PRESENTATION DEMO MODE PRESETS
    // ==========================================
    loadDemoPreset: async function(caseNumber) {
        this.showToast(`Loading demo preset: ${caseNumber}...`, "info");
        await this.viewCaseDetails(caseNumber);
    },

    startGuidedWalkthrough: function() {
        this.state.demoWalkthroughStep = 1;
        this.nextWalkthroughStep();
    },

    nextWalkthroughStep: function() {
        const step = this.state.demoWalkthroughStep;
        if (step === 1) {
            this.switchTab("landing-view");
            this.showWalkthroughBanner(
                "Step 1: Public Intake & Landing",
                "Victims access Sahaaya AI via multiple entry points (Helpline, IVRS, Chatbot, Portal). Emphasizes privacy and consent.",
                "Proceed to Step 2: Victim Voice Contact"
            );
        } else if (step === 2) {
            this.switchTab("victim-view");
            this.setVictimLanguage("Telugu");
            this.setChannel("Voice Helpline");
            this.showWalkthroughBanner(
                "Step 2: Multilingual First Contact (Telugu Scenario)",
                "Victim provides consent and shares their narrative in Telugu. Speech prosody and hesitation markers are actively tracked.",
                "Proceed to Step 3: Run AI Assessment"
            );
        } else if (step === 3) {
            this.runInteractiveAssessment();
            this.showWalkthroughBanner(
                "Step 3: Real-Time SVI & Multimodal Assessment",
                "AI engine calculates SVI 82/100 (HIGH Risk). Extracts acoustic tremor, prosodic pauses, and threat keywords.",
                "Proceed to Step 4: Authorized Case Dossier"
            );
        } else if (step === 4) {
            this.viewCaseDetails("NHAA-1024");
            this.showWalkthroughBanner(
                "Step 4: Deep Triage & Explainable AI",
                "Authorized Officer reviews 'Why this assessment?' factor weights, emotion radar chart, and assigns human counselling & legal aid.",
                "Proceed to Step 5: Follow-up & Early Warning"
            );
        } else if (step === 5) {
            this.switchTab("analytics-view");
            this.showWalkthroughBanner(
                "Step 5: Follow-Up Intelligence & Early Warning",
                "Anonymized trend detection alerts officers of cluster patterns in Rangareddy district. Complete audit ledger maintained.",
                "Finish Walkthrough"
            );
        } else {
            this.hideWalkthroughBanner();
            this.showToast("Guided demonstration completed!", "success");
        }
        this.state.demoWalkthroughStep++;
    },

    showWalkthroughBanner: function(title, body, btnText) {
        let banner = document.getElementById("walkthroughBanner");
        if (!banner) {
            banner = document.createElement("div");
            banner.id = "walkthroughBanner";
            banner.className = "fixed bottom-5 left-1/2 transform -translate-x-1/2 z-50 bg-slate-900 text-white p-4 rounded-xl shadow-2xl border border-teal-500 max-w-xl w-full flex items-center justify-between";
            document.body.appendChild(banner);
        }
        banner.innerHTML = `
            <div>
                <div class="text-xs font-bold text-teal-400 uppercase tracking-wide">${title}</div>
                <div class="text-xs text-slate-300 mt-1 leading-snug">${body}</div>
            </div>
            <div class="ml-4 flex items-center space-x-2">
                <button onclick="App.nextWalkthroughStep()" class="px-3 py-1.5 rounded bg-teal-500 hover:bg-teal-600 text-slate-900 font-bold text-xs whitespace-nowrap">${btnText}</button>
                <button onclick="App.hideWalkthroughBanner()" class="text-slate-400 hover:text-white text-xs">✕</button>
            </div>
        `;
        banner.classList.remove("hidden");
    },

    hideWalkthroughBanner: function() {
        const banner = document.getElementById("walkthroughBanner");
        if (banner) banner.classList.add("hidden");
    },

    // ==========================================
    // ACCESSIBILITY & TOASTS
    // ==========================================
    toggleHighContrast: function() {
        this.state.highContrast = !this.state.highContrast;
        if (this.state.highContrast) {
            document.body.classList.add("high-contrast");
            this.showToast("High contrast mode enabled", "info");
        } else {
            document.body.classList.remove("high-contrast");
            this.showToast("Standard contrast restored", "info");
        }
    },

    setFontSize: function(sizeClass) {
        document.body.classList.remove("font-size-sm", "font-size-md", "font-size-lg", "font-size-xl");
        document.body.classList.add(sizeClass);
        this.state.fontSize = sizeClass;
    },

    showToast: function(msg, type = "info") {
        const toast = document.getElementById("appToast");
        if (!toast) return;
        toast.textContent = msg;
        toast.className = `fixed top-5 right-5 z-50 px-4 py-2.5 rounded-lg text-xs font-semibold shadow-xl text-white transition-all transform duration-300 ${
            type === 'success' ? 'bg-emerald-600' :
            type === 'error' ? 'bg-rose-600' :
            type === 'warning' ? 'bg-amber-600' :
            'bg-slate-800'
        }`;
        toast.classList.remove("hidden", "opacity-0", "translate-y-[-10px]");
        toast.classList.add("opacity-100", "translate-y-0");

        setTimeout(() => {
            toast.classList.add("opacity-0", "translate-y-[-10px]");
            setTimeout(() => toast.classList.add("hidden"), 300);
        }, 3500);
    },

    setupEventListeners: function() {
        // Notification bell dropdown toggle
        const bell = document.getElementById("notifBellBtn");
        if (bell) {
            bell.addEventListener("click", () => {
                document.getElementById("notifDropdown").classList.toggle("hidden");
            });
        }
    }
};

window.addEventListener("DOMContentLoaded", () => {
    App.init();
});
