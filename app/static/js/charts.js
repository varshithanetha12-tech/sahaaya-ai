// Chart.js helper module for Sahaaya AI Platform
window.AppCharts = {
    instances: {},

    destroyChart: function(id) {
        if (this.instances[id]) {
            this.instances[id].destroy();
            delete this.instances[id];
        }
    },

    // 1. Emotion Radar Chart
    renderEmotionRadar: function(canvasId, emotionData) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = ['Fear', 'Distress', 'Anxiety', 'Sadness', 'Anger', 'Confusion', 'Calm', 'Neutral'];
        const values = [
            (emotionData.fear || 0) * 100,
            (emotionData.distress || 0) * 100,
            (emotionData.anxiety || 0) * 100,
            (emotionData.sadness || 0) * 100,
            (emotionData.anger || 0) * 100,
            (emotionData.confusion || 0) * 100,
            (emotionData.calm || 0) * 100,
            (emotionData.neutral || 0) * 100
        ];

        this.instances[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Arousal / Magnitude (%)',
                    data: values,
                    backgroundColor: 'rgba(239, 68, 68, 0.25)',
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    pointBackgroundColor: '#b91c1c',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#ef4444'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: '#e2e8f0' },
                        grid: { color: '#e2e8f0' },
                        pointLabels: {
                            font: { size: 11, weight: '600' },
                            color: '#334155'
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    },

    // 2. Speech Prosody Bar Chart
    renderSpeechMetrics: function(canvasId, speechData) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = ['Speech Rate (WPM)', 'Pause Count', 'Pitch Var (Hz)', 'Voice Tremor (%)', 'Hesitation (%)'];
        const values = [
            speechData ? speechData.speech_rate_wpm : 110,
            speechData ? speechData.pause_count * 10 : 20, // scaled for visualization
            speechData ? speechData.pitch_variance_hz : 25,
            speechData ? Math.round((speechData.voice_instability_index || 0.2) * 100) : 25,
            speechData ? speechData.hesitation_score : 30
        ];

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Acoustic Indicator Value',
                    data: values,
                    backgroundColor: [
                        '#0ea5e9',
                        '#f59e0b',
                        '#8b5cf6',
                        '#ef4444',
                        '#ec4899'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 200,
                        grid: { color: '#f1f5f9' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 10 } }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    },

    // 3. Analytics Risk Doughnut
    renderRiskDonut: function(canvasId, riskDist) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.instances[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Low (🟢)', 'Moderate (🟡)', 'High (🟠)', 'Critical (🔴)'],
                datasets: [{
                    data: [
                        riskDist.LOW || 0,
                        riskDist.MODERATE || 0,
                        riskDist.HIGH || 0,
                        riskDist.CRITICAL || 0
                    ],
                    backgroundColor: ['#22c55e', '#eab308', '#f97316', '#ef4444'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                }
            }
        });
    },

    // 4. Analytics Bar Chart
    renderBarDistribution: function(canvasId, dictData, barColor = '#0d9488') {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = Object.keys(dictData);
        const values = Object.values(dictData);

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: barColor,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } },
                    x: { ticks: { font: { size: 10 } } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    },

    // 5. Follow-Up Vulnerability Progression Line Chart
    renderVulnerabilityTimeline: function(canvasId, historyItems) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = historyItems.map(h => h.stage || h.date);
        const scores = historyItems.map(h => h.svi);

        this.instances[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'SVI Trauma Score Progression',
                    data: scores,
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.12)',
                    fill: true,
                    tension: 0.35,
                    pointRadius: 5,
                    pointBackgroundColor: '#0369a1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { stepSize: 20 }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
};
