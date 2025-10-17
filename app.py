from flask import Flask, render_template_string, make_response
from io import BytesIO
import datetime
import os

# Initialize Flask application
app = Flask(__name__)

# --- START OF EMBEDDED HTML/JAVASCRIPT FRONTEND ---
# This multiline string contains the entire client-side application (HTML, Tailwind CSS, and JavaScript with Firebase logic).
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biometric Health Monitor (Single File)</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .risk-low { border-color: #34d399; }
        .risk-medium { border-color: #fbbf24; }
        .risk-high { border-color: #f87171; }
        .tab-button.active { 
            border-bottom-width: 4px;
            border-color: #4f46e5;
            background-color: white;
            color: #4f46e5;
        }
    </style>
</head>
<body class="bg-gray-50">

    <!-- Global Alert Banner Placeholder -->
    <div id="alert-banner" class="fixed top-4 right-4 z-50 p-4 text-sm rounded-lg shadow-xl transition-opacity duration-500 opacity-0 pointer-events-none" role="alert"></div>

    <div class="min-h-screen p-4 md:p-8 max-w-7xl mx-auto">
        <header class="mb-8 flex flex-col md:flex-row justify-between items-center border-b pb-4">
            <h1 class="text-3xl font-bold text-gray-800">Biometric Health Monitor</h1>
            <div class="mt-2 md:mt-0 text-sm text-gray-500">
                User ID: <span id="user-id" class="font-mono text-xs p-1 bg-gray-200 rounded-lg select-all">Loading...</span>
            </div>
        </header>

        <main>
            <!-- Tab Navigation -->
            <nav class="flex space-x-2 border-b-2 border-gray-200 mb-8">
                <button id="tab-monitor" class="tab-button active py-3 px-6 rounded-t-xl font-semibold transition-all hover:bg-white hover:text-indigo-700">Monitor</button>
                <button id="tab-history" class="tab-button py-3 px-6 rounded-t-xl font-semibold transition-all hover:bg-white hover:text-indigo-700">History</button>
                <button id="tab-reports" class="tab-button py-3 px-6 rounded-t-xl font-semibold transition-all hover:bg-white hover:text-indigo-700">Reports</button>
            </nav>

            <!-- Tab Content -->
            <div id="tab-content" class="min-h-[400px]">
                <!-- Monitor Tab Content -->
                <div id="content-monitor" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    
                    <!-- Eye Strain Tracker -->
                    <div class="bg-white p-6 rounded-2xl shadow-xl border border-gray-100 transition duration-300">
                        <h2 class="text-2xl font-bold mb-4 text-indigo-700 flex items-center">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 mr-2 text-indigo-500" viewBox="0 0 20 20" fill="currentColor"><path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/><path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/></svg>
                            Eye Strain Tracker
                        </h2>
                        <p class="text-gray-600 mb-4 text-sm">Measures blink frequency (simulated) to assess potential <strong>visual fatigue</strong>.</p>
                        <div class="relative w-full aspect-video bg-gray-900 rounded-xl overflow-hidden mb-5 border-4 border-gray-300">
                            <video id="cameraFeed" class="w-full h-full" autoplay playsinline style="transform: scaleX(-1); display: none;"></video>
                            <div id="camera-placeholder" class="absolute inset-0 flex flex-col items-center justify-center bg-gray-800 text-gray-400 text-lg">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-2" viewBox="0 0 20 20" fill="currentColor"><path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/><path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/></svg>
                                Camera Preview Disabled
                            </div>
                            <div id="eye-risk-badge" class="absolute top-2 left-2 px-3 py-1 text-sm font-bold rounded-full shadow-lg border-2 border-white hidden"></div>
                        </div>
                        <div class="flex space-x-4">
                            <button id="btn-start-eye" class="flex-1 px-6 py-3 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-700 transition duration-150 flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline-block mr-2" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
                                Start Analysis
                            </button>
                            <button id="btn-stop-eye" class="flex-1 px-6 py-3 bg-red-600 text-white font-bold rounded-lg shadow-md hover:bg-red-700 transition duration-150 flex items-center justify-center hidden">
                                <span class="inline-block w-3 h-3 mr-2 bg-white rounded-full animate-pulse"></span>
                                Stop & Save
                            </button>
                        </div>
                        <p id="eye-status" class="mt-4 text-center text-sm font-semibold text-gray-500">Awaiting user action...</p>
                    </div>

                    <!-- Voice Fatigue Checker -->
                    <div class="bg-white p-6 rounded-2xl shadow-xl border border-gray-100 transition duration-300">
                        <h2 class="text-2xl font-bold mb-4 text-green-700 flex items-center">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 mr-2 text-green-500" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10v-3a1 1 0 00-1-1h-2a1 1 0 00-1 1v3zm0 0a1 1 0 01-1 1H8a1 1 0 01-1-1v-3h4v3zm-4-3a2 2 0 104 0V4a2 2 0 10-4 0v7z" clip-rule="evenodd"/></svg>
                            Voice Fatigue Checker
                        </h2>
                        <p class="text-gray-600 mb-4 text-sm">Analyzes vocal recordings (simulated) for pitch and volume variance for <strong>vocal strain</strong>.</p>
                        <div class="relative w-full h-40 bg-gray-100 rounded-xl flex items-center justify-center mb-5 border-4 border-gray-300">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 text-gray-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4z" clip-rule="evenodd"/><path d="M12 14l-.868-.694A2 2 0 009 13.5v-3.236a2 2 0 00-1.132-.568L7 9.5V14a5 5 0 008.204 3.541.25.25 0 01-.284.225A6.5 6.5 0 0110 18.5a6.5 6.5 0 01-5.92-.734.25.25 0 01-.284-.225A5 5 0 001 14V9.5l.2-.187a2 2 0 001.132.568V13.5a2 2 0 001.132.568L5 14v1a1 1 0 001 1h8a1 1 0 001-1v-1l.868-.694A2 2 0 0017 13.5v-3.236a2 2 0 00-1.132-.568L15 9.5V14a5 5 0 008.204 3.541.25.25 0 01-.284.225A6.5 6.5 0 0110 18.5a6.5 6.5 0 01-5.92-.734.25.25 0 01-.284-.225A5 5 0 001 14z" clip-rule="evenodd"/></svg>
                            <div id="voice-ping" class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 bg-red-500 rounded-full animate-ping opacity-75 hidden"></div>
                        </div>
                        <div class="flex space-x-4">
                            <button id="btn-start-voice" class="flex-1 px-6 py-3 bg-green-600 text-white font-bold rounded-lg shadow-md hover:bg-green-700 transition duration-150 flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline-block mr-2" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
                                Start Recording
                            </button>
                            <button id="btn-stop-voice" class="flex-1 px-6 py-3 bg-red-600 text-white font-bold rounded-lg shadow-md hover:bg-red-700 transition duration-150 flex items-center justify-center hidden">
                                <span class="inline-block w-3 h-3 mr-2 bg-white rounded-full animate-pulse"></span>
                                Stop & Save
                            </button>
                        </div>
                        <p id="voice-status" class="mt-4 text-center text-sm font-semibold text-gray-500">Awaiting user action...</p>
                    </div>
                </div>

                <!-- History Tab Content -->
                <div id="content-history" class="hidden">
                    <h2 class="text-2xl font-bold mb-6 text-gray-800">Analysis History</h2>
                    <div id="history-list" class="space-y-4">
                        <div class="text-center text-gray-500 p-8 bg-white rounded-xl shadow-inner">
                            Loading history...
                        </div>
                    </div>
                </div>

                <!-- Reports Tab Content -->
                <div id="content-reports" class="hidden">
                    <div class="bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
                        <h2 class="text-2xl font-bold mb-4 text-gray-800">Download Reports</h2>
                        <p class="text-gray-600 mb-6">
                            Generate a comprehensive <strong>PDF report</strong> containing all recorded entries and summary statistics. 
                            <strong>Note:</strong> The report is generated on the Flask backend via the <code>/download_report</code> endpoint and uses simulated data.
                        </p>
                        <a 
                            id="pdf-download-link" 
                            href="/download_report" 
                            target="_blank" 
                            class="inline-flex items-center px-8 py-3 bg-red-600 text-white font-bold rounded-xl shadow-lg hover:bg-red-700 transition duration-200 transform hover:scale-105"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5 4v3h2V4h3V2H7a2 2 0 00-2 2zm0 8H3a2 2 0 00-2 2v3a2 2 0 002 2h3v-2H5v-3zm12-4v3h-2v-3h-3V8h3a2 2 0 012 2zM9 16v-3h2v3h3v2H9a2 2 0 01-2-2z" clip-rule="evenodd"/></svg>
                            Generate & Download Report
                        </a>
                    </div>
                </div>

            </div>
        </main>
    </div>

    <!-- JavaScript and Firebase Initialization -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import { getFirestore, addDoc, onSnapshot, collection, serverTimestamp, setLogLevel } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

        // Global constants provided by the environment
        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-wellbeing-monitor';
        const firebaseConfig = (typeof __firebase_config !== 'undefined' && __firebase_config) ? JSON.parse(__firebase_config) : {};
        const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

        // --- GLOBAL STATE & REFERENCES ---
        let db;
        let auth;
        let userId = 'Loading...';
        let isAuthReady = false;
        let isTrackingEye = false;
        let isRecordingVoice = false;
        let eyeStreamRef = null;
        let voiceStreamRef = null;
        let voiceRecorderRef = null;
        let eyeIntervalRef = null;
        let voiceIntervalRef = null;
        let eyeStartTimeRef = null;
        let voiceStartTimeRef = null;
        let lastEyeScoreRef = 0;
        let historyData = [];

        // --- DOM Elements ---
        const D = (id) => document.getElementById(id);
        const userIdEl = D('user-id');
        const alertBanner = D('alert-banner');
        const contentMonitor = D('content-monitor');
        const contentHistory = D('content-history');
        const contentReports = D('content-reports');
        const tabMonitor = D('tab-monitor');
        const tabHistory = D('tab-history');
        const tabReports = D('tab-reports');
        const historyList = D('history-list');

        const cameraFeed = D('cameraFeed');
        const cameraPlaceholder = D('camera-placeholder');
        const eyeRiskBadge = D('eye-risk-badge');
        const eyeStatusEl = D('eye-status');
        const btnStartEye = D('btn-start-eye');
        const btnStopEye = D('btn-stop-eye');

        const voicePing = D('voice-ping');
        const voiceStatusEl = D('voice-status');
        const btnStartVoice = D('btn-start-voice');
        const btnStopVoice = D('btn-stop-voice');

        // --- UTILITY FUNCTIONS ---

        /**
         * Calculates risk data (level, color, suggestion) based on a score (1-5).
         */
        function getRiskData(score) {
            let level, classColor, suggestion;
            if (score >= 4.0) {
                level = 'HIGH';
                classColor = 'risk-high bg-red-100 text-red-800 border-red-400';
                suggestion = 'Immediate break recommended. Hydrate and rest your eyes/voice.';
            } else if (score >= 2.0) {
                level = 'MEDIUM';
                classColor = 'risk-medium bg-amber-100 text-amber-800 border-amber-400';
                suggestion = 'Take a short break soon. Moderate risk detected.';
            } else {
                level = 'LOW';
                classColor = 'risk-low bg-green-100 text-green-800 border-green-400';
                suggestion = 'Good to go. Continue monitoring.';
            }
            return { level, classColor, suggestion };
        }

        /**
         * Displays a temporary status alert.
         */
        function showAlert(message, type = 'success') {
            const classMap = {
                success: 'bg-green-600 text-white',
                error: 'bg-red-600 text-white',
                info: 'bg-blue-600 text-white'
            };

            alertBanner.textContent = message;
            alertBanner.className = `fixed top-4 right-4 z-50 p-4 text-sm rounded-lg shadow-xl transition-opacity duration-500 opacity-100 ${classMap[type]}`;

            setTimeout(() => {
                alertBanner.classList.remove('opacity-100');
                alertBanner.classList.add('opacity-0');
            }, 4000);
        }

        /**
         * Renders a single history item.
         */
        function renderHistoryItem(entry) {
            const isEye = entry.type === 'Eye Strain';
            const { level, classColor, suggestion } = getRiskData(entry.score);
            const timeStr = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : 'N/A';
            const duration = entry.duration_sec ? entry.duration_sec.toFixed(0) + ' seconds' : 'N/A';
            const score = entry.score.toFixed(1);

            return `
                <div class="p-5 rounded-xl shadow-lg border-2 transition duration-200 ${classColor}">
                    <div class="flex justify-between items-start mb-2">
                        <div class="font-extrabold text-xl flex items-center">
                            ${isEye ? '👀 Eye Strain' : '🎤 Voice Fatigue'}
                        </div>
                        <div class="text-sm font-medium opacity-80">${timeStr}</div>
                    </div>
                    <div class="grid grid-cols-2 gap-2 text-sm text-gray-700">
                        <p>
                            <strong class="font-semibold">Duration:</strong> ${duration}
                        </p>
                        <p>
                            <strong class="font-semibold">Risk Score (1-5):</strong>
                            <span class="font-black text-2xl ml-2">${score}</span>
                        </p>
                    </div>
                    <div class="mt-4 pt-3 border-t border-gray-300 opacity-90">
                        <p>
                            <strong class="font-bold">Risk Level:</strong> <span class="font-extrabold">${level}</span>
                        </p>
                        <p class="mt-1 text-sm">${suggestion}</p>
                    </div>
                </div>
            `;
        }

        /**
         * Renders the entire history list.
         */
        function renderHistoryList() {
            if (!isAuthReady) {
                historyList.innerHTML = `<div class="text-center text-gray-500 p-8 bg-white rounded-xl shadow-inner">Loading history...</div>`;
            } else if (historyData.length === 0) {
                historyList.innerHTML = `<div class="text-center text-gray-500 p-8 bg-white rounded-xl shadow-inner">No analysis entries recorded yet.</div>`;
            } else {
                historyList.innerHTML = historyData.map(renderHistoryItem).join('');
            }
        }

        // --- DATA SAVING FUNCTION (Firestore) ---
        async function saveEntry(type, score, duration, statusMessage) {
            if (!db || !userId) {
                showAlert("Error: Cannot save entry. Database not ready.", 'error');
                return;
            }

            const collectionRef = collection(db, `artifacts/${appId}/users/${userId}/monitor_entries`);

            try {
                const newDoc = {
                    type,
                    score: parseFloat(score.toFixed(2)),
                    duration_sec: duration,
                    message: statusMessage,
                    timestamp: serverTimestamp()
                };
                await addDoc(collectionRef, newDoc);
                showAlert(`New ${type} analysis saved successfully! Score: ${score.toFixed(1)}`);
            } catch (e) {
                console.error("Error adding document: ", e);
                showAlert("Error saving analysis. Check console.", 'error');
            }
        }

        // --- EYE TRACKER LOGIC ---

        async function startEyeTracker() {
            if (isTrackingEye) return;

            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                eyeStreamRef = stream;
                
                cameraFeed.srcObject = stream;
                cameraFeed.play();
                cameraFeed.style.display = 'block';
                cameraPlaceholder.style.display = 'none';

                isTrackingEye = true;
                eyeStatusEl.textContent = 'Analysis running... Click Stop to save.';
                eyeStatusEl.classList.add('text-red-500');
                eyeStatusEl.classList.remove('text-gray-500');
                btnStartEye.classList.add('hidden');
                btnStopEye.classList.remove('hidden');

                eyeStartTimeRef = Date.now();
                lastEyeScoreRef = 1.0;
                eyeRiskBadge.classList.remove('hidden');

                // Start continuous analysis simulation
                eyeIntervalRef = setInterval(() => {
                    const elapsedSeconds = (Date.now() - eyeStartTimeRef) / 1000;
                    
                    // Simulate score
                    const elapsedMinutes = elapsedSeconds / 60;
                    const baseRisk = Math.min(4.5, elapsedMinutes * 0.7);
                    const fluctuation = Math.random() * 0.8 - 0.4;
                    const newScore = Math.max(1.0, baseRisk + fluctuation);
                    lastEyeScoreRef = newScore;

                    const { level, classColor } = getRiskData(newScore);
                    eyeStatusEl.innerHTML = `Running: <span class="font-bold text-indigo-600">${elapsedSeconds.toFixed(0)}s</span>. Current Risk: <span class="font-bold">${level} (${newScore.toFixed(1)})</span>`;
                    eyeRiskBadge.textContent = `Risk: ${level}`;
                    eyeRiskBadge.className = `absolute top-2 left-2 px-3 py-1 text-sm font-bold rounded-full shadow-lg border-2 border-white ${classColor}`;

                }, 2000);

                showAlert("Eye Strain Tracker started. Look into the camera.", 'info');

            } catch (err) {
                console.error("Error accessing camera: ", err);
                showAlert("Failed to start camera. Check permissions and try again.", 'error');
                isTrackingEye = false;
                eyeStatusEl.textContent = 'Error accessing camera. Check console.';
            }
        }

        function stopEyeTracker() {
            if (!isTrackingEye) return;

            // Stop simulation interval
            if (eyeIntervalRef) clearInterval(eyeIntervalRef);
            
            // Stop media stream tracks
            if (eyeStreamRef) {
                eyeStreamRef.getTracks().forEach(track => track.stop());
                cameraFeed.srcObject = null;
                eyeStreamRef = null;
            }

            const duration = Math.round((Date.now() - eyeStartTimeRef) / 1000);
            const finalScore = lastEyeScoreRef;
            const { suggestion } = getRiskData(finalScore);

            saveEntry('Eye Strain', finalScore, duration, `Blink analysis over ${duration}s. ${suggestion}`);

            // Reset UI State
            isTrackingEye = false;
            cameraFeed.style.display = 'none';
            cameraPlaceholder.style.display = 'flex';
            eyeRiskBadge.classList.add('hidden');
            eyeStatusEl.textContent = `Analysis stopped. Duration: ${duration}s. Ready to start new session.`;
            eyeStatusEl.classList.remove('text-red-500');
            eyeStatusEl.classList.add('text-gray-500');
            btnStopEye.classList.add('hidden');
            btnStartEye.classList.remove('hidden');
            lastEyeScoreRef = 0;
            showAlert("Eye Strain Tracker stopped and data saved.", 'success');
        }

        // --- VOICE CHECKER LOGIC ---

        async function startVoiceChecker() {
            if (isRecordingVoice) return;
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                voiceStreamRef = stream;
                
                const recorder = new MediaRecorder(stream);
                voiceRecorderRef = recorder;
                recorder.start();

                isRecordingVoice = true;
                voiceStartTimeRef = Date.now();
                voicePing.classList.remove('hidden');
                btnStartVoice.classList.add('hidden');
                btnStopVoice.classList.remove('hidden');

                // Update duration status indefinitely
                voiceIntervalRef = setInterval(() => {
                    const duration = Math.round((Date.now() - voiceStartTimeRef) / 1000);
                    voiceStatusEl.innerHTML = `Recording: <span class="font-bold text-red-500">${duration}s</span>. Speak normally and click Stop.`;
                    voiceStatusEl.classList.add('text-red-500');
                    voiceStatusEl.classList.remove('text-gray-500');
                }, 1000);

                showAlert("Voice Fatigue Checker started. Microphone is recording.", 'info');

            } catch (err) {
                console.error("Error accessing microphone: ", err);
                showAlert("Failed to start microphone. Check permissions and try again.", 'error');
                isRecordingVoice = false;
                voiceStatusEl.textContent = 'Error accessing microphone. Check console.';
            }
        }

        function stopVoiceChecker() {
            if (!isRecordingVoice) return;

            // Stop simulation interval
            if (voiceIntervalRef) clearInterval(voiceIntervalRef);

            // Stop media stream and recorder
            if (voiceRecorderRef && voiceRecorderRef.state === 'recording') {
                voiceRecorderRef.stop();
            }
            if (voiceStreamRef) {
                voiceStreamRef.getTracks().forEach(track => track.stop());
                voiceStreamRef = null;
            }

            const duration = Math.round((Date.now() - voiceStartTimeRef) / 1000);
            
            // Simulate score based on duration
            let finalScore = 1.0;
            let statusMessage = "Simulated: Short recording, minimal vocal analysis possible.";
            
            if (duration > 90) {
                finalScore = 4.0 + Math.random() * 1.0;
                statusMessage = "Simulated: Prolonged recording (>90s) suggests high vocal strain.";
            } else if (duration > 30) {
                finalScore = 2.0 + Math.random() * 2.0;
                statusMessage = "Simulated: Moderate recording length. Potential signs of early fatigue.";
            } else {
                finalScore = 1.0 + Math.random() * 1.0;
            }
            
            const { suggestion } = getRiskData(finalScore);
            saveEntry('Voice Fatigue', finalScore, duration, `${statusMessage} (${suggestion})`);

            // Reset UI
            isRecordingVoice = false;
            voicePing.classList.add('hidden');
            voiceStatusEl.textContent = `Recording stopped. Duration: ${duration}s. Ready to start new session.`;
            voiceStatusEl.classList.remove('text-red-500');
            voiceStatusEl.classList.add('text-gray-500');
            btnStopVoice.classList.add('hidden');
            btnStartVoice.classList.remove('hidden');
            showAlert("Voice Fatigue Checker stopped and data saved.", 'success');
        }


        // --- FIREBASE INITIALIZATION & AUTH ---

        async function initFirebase() {
            if (Object.keys(firebaseConfig).length === 0) {
                console.warn("Firebase config missing. Running in mock mode.");
                userId = crypto.randomUUID();
                userIdEl.textContent = userId;
                isAuthReady = true;
                renderHistoryList();
                return;
            }

            try {
                const app = initializeApp(firebaseConfig);
                db = getFirestore(app);
                auth = getAuth(app);
                setLogLevel('Debug');

                onAuthStateChanged(auth, async (user) => {
                    if (user) {
                        userId = user.uid;
                    } else {
                        try {
                            if (initialAuthToken) {
                                await signInWithCustomToken(auth, initialAuthToken);
                            } else {
                                await signInAnonymously(auth);
                            }
                            userId = auth.currentUser.uid;
                        } catch (error) {
                            console.error("Firebase Auth Error:", error);
                            userId = crypto.randomUUID();
                        }
                    }
                    userIdEl.textContent = userId;
                    isAuthReady = true;
                    setupHistoryListener();
                });
            } catch (error) {
                console.error("Failed to initialize Firebase:", error);
                showAlert("Error initializing Firebase. Check console.", 'error');
                userId = crypto.randomUUID();
                userIdEl.textContent = userId;
                isAuthReady = true;
            }
        }
        
        // --- FIREBASE HISTORY LISTENER ---
        function setupHistoryListener() {
            if (!db || !userId || !isAuthReady) return;

            const collectionRef = collection(db, `artifacts/${appId}/users/${userId}/monitor_entries`);
            
            onSnapshot(collectionRef, (snapshot) => {
                let tempHistory = [];
                snapshot.forEach((doc) => {
                    const data = doc.data();
                    tempHistory.push({
                        id: doc.id,
                        ...data,
                        // Convert Firestore Timestamp to JS timestamp
                        timestamp: data.timestamp ? data.timestamp.toDate().getTime() : Date.now(), 
                    });
                });
                // Sort by timestamp descending (newest first)
                tempHistory.sort((a, b) => b.timestamp - a.timestamp);
                historyData = tempHistory;
                renderHistoryList();
            }, (error) => {
                console.error("Error setting up history listener: ", error);
                showAlert("Failed to load history.", 'error');
                renderHistoryList();
            });
        }


        // --- EVENT HANDLERS ---
        function changeTab(activeTabId) {
            // Hide all content and deactivate all buttons
            [contentMonitor, contentHistory, contentReports].forEach(el => el.classList.add('hidden'));
            [tabMonitor, tabHistory, tabReports].forEach(el => el.classList.remove('active'));

            // Show active content and activate button
            const activeContent = D('content-' + activeTabId);
            const activeTabButton = D('tab-' + activeTabId);
            
            if (activeContent) activeContent.classList.remove('hidden');
            if (activeTabButton) activeTabButton.classList.add('active');

            if (activeTabId === 'history') {
                renderHistoryList();
            }
            if (activeTabId === 'reports') {
                D('pdf-download-link').onclick = () => showAlert("Generating PDF using mock data from the server endpoint.", 'info');
            }
        }

        // --- INITIAL SETUP ON LOAD ---
        window.addEventListener('load', () => {
            // Setup Tab Click Listeners
            tabMonitor.addEventListener('click', () => changeTab('monitor'));
            tabHistory.addEventListener('click', () => changeTab('history'));
            tabReports.addEventListener('click', () => changeTab('reports'));

            // Setup Monitor Button Listeners
            btnStartEye.addEventListener('click', startEyeTracker);
            btnStopEye.addEventListener('click', stopEyeTracker);
            btnStartVoice.addEventListener('click', startVoiceChecker);
            btnStopVoice.addEventListener('click', stopVoiceChecker);

            initFirebase();
        });

    </script>
</body>
</html>
"""
# --- END OF EMBEDDED HTML/JAVASCRIPT FRONTEND ---


@app.route('/')
def index():
    """Renders the main HTML page containing the Biometric Health Monitor."""
    # Use render_template_string to serve the embedded HTML content
    return render_template_string(HTML_CONTENT)

@app.route('/download_report')
def download_report():
    """
    Simulates generating and serving a simple PDF report. 
    (In a real application, a library like ReportLab or FPDF would be used here.)
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"health_report_{now}.txt"
    
    # Create a simple mock report content
    report_content = f"""
    BIOMETRIC HEALTH MONITOR REPORT
    --------------------------------------
    Date Generated: {datetime.datetime.now()}
    
    This is a mock report demonstrating the Flask endpoint functionality.
    
    Analysis Summary (Mock Data):
    - Total Eye Strain Checks: 15
    - Average Eye Risk Score: 2.3 (MEDIUM)
    - Total Voice Fatigue Checks: 8
    - Average Voice Risk Score: 1.8 (LOW)
    
    Recommendation: Continue monitoring and take breaks when scores exceed 3.5.
    
    (Note: This content is simulated as client-side data cannot be accessed by Flask.)
    """
    
    # Create a response object to serve the text file as a download
    response = make_response(report_content)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/plain"
    
    return response
