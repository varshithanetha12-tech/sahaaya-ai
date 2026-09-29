// Audio Waveform & Speech Simulator for Sahaaya AI
window.AudioEngine = {
    isRecording: false,
    recordStartTime: null,
    recordTimerInterval: null,
    audioContext: null,
    analyser: null,
    microphoneStream: null,
    animationFrameId: null,

    startRecording: async function(canvasId, durationElId) {
        this.isRecording = true;
        this.recordStartTime = Date.now();
        const durationEl = document.getElementById(durationElId);
        const canvas = document.getElementById(canvasId);

        // Timer interval
        this.recordTimerInterval = setInterval(() => {
            if (!this.recordStartTime) return;
            const elapsedMs = Date.now() - this.recordStartTime;
            const totalSec = Math.floor(elapsedMs / 1000);
            const mins = String(Math.floor(totalSec / 60)).padStart(2, '0');
            const secs = String(totalSec % 60).padStart(2, '0');
            if (durationEl) durationEl.textContent = `${mins}:${secs}`;
        }, 1000);

        // Attempt Web Audio API microphone stream or synthetic fallback
        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                this.microphoneStream = stream;
                const AudioCtx = window.AudioContext || window.webkitAudioContext;
                this.audioContext = new AudioCtx();
                this.analyser = this.audioContext.createAnalyser();
                this.analyser.fftSize = 64;
                const source = this.audioContext.createMediaStreamSource(stream);
                source.connect(this.analyser);
                this.drawLiveWaveform(canvas);
                return;
            }
        } catch (e) {
            console.log("Microphone hardware access unavailable; falling back to simulated speech waveform:", e);
        }

        // Fallback synthetic waveform rendering
        this.drawSyntheticWaveform(canvas);
    },

    stopRecording: function() {
        this.isRecording = false;
        clearInterval(this.recordTimerInterval);
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        if (this.microphoneStream) {
            this.microphoneStream.getTracks().forEach(t => t.stop());
            this.microphoneStream = null;
        }
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
    },

    getRecordedDurationSec: function() {
        if (!this.recordStartTime) return 24.5;
        const elapsed = (Date.now() - this.recordStartTime) / 1000;
        return Math.max(5.0, Math.round(elapsed * 10) / 10);
    },

    drawLiveWaveform: function(canvas) {
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const render = () => {
            if (!this.isRecording) return;
            this.animationFrameId = requestAnimationFrame(render);
            this.analyser.getByteFrequencyData(dataArray);

            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const barWidth = (canvas.width / bufferLength) * 2.2;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                const barHeight = (dataArray[i] / 255) * canvas.height * 0.9;
                
                // Color gradient from teal to amber based on volume
                const r = Math.min(255, dataArray[i] * 1.5);
                const g = Math.max(100, 255 - dataArray[i]);
                const b = 200;

                ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
                ctx.fillRect(x, (canvas.height - barHeight) / 2, barWidth - 2, barHeight);
                x += barWidth;
            }
        };
        render();
    },

    drawSyntheticWaveform: function(canvas) {
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let step = 0;

        const render = () => {
            if (!this.isRecording) return;
            this.animationFrameId = requestAnimationFrame(render);
            step += 0.15;

            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const bars = 24;
            const barWidth = canvas.width / bars;

            for (let i = 0; i < bars; i++) {
                const amp = Math.sin(step + i * 0.5) * 0.5 + 0.5;
                const jitter = (Math.random() * 0.4) + 0.6;
                const barHeight = Math.max(6, amp * jitter * (canvas.height * 0.85));

                ctx.fillStyle = (i % 3 === 0) ? '#0d9488' : '#14b8a6';
                ctx.fillRect(i * barWidth + 2, (canvas.height - barHeight) / 2, barWidth - 4, barHeight);
            }
        };
        render();
    }
};
