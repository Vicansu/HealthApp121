from flask import Flask, send_file, request, Response
import csv
import io
import time # Used for simulated timestamp in CSV
from datetime import datetime

# Initialize Flask
app = Flask(__name__)

# --- Mock Data Fetching (Server-side for CSV Report Generation) ---
def fetch_mock_biometric_data():
    """Returns structured data suitable for CSV export, simulating Firestore data."""
    # Generate mock data points with varied results and timestamps
    now_ms = int(time.time() * 1000)
    return [
        {
            'timestamp': now_ms - (86400 * 1000 * 5),
            'type': 'blink',
            'rate': 9,
            'strain': 'YES',
            'vocal_duration': 'N/A',
            'vocal_strain': 'N/A'
        },
        {
            'timestamp': now_ms - (86400 * 1000 * 3) - (3600 * 1000 * 12),
            'type': 'voice',
            'rate': 'N/A',
            'strain': 'N/A',
            'vocal_duration': '3.8s',
            'vocal_strain': 'Low'
        },
        {
            'timestamp': now_ms - (86400 * 1000 * 1),
            'type': 'blink',
            'rate': 18,
            'strain': 'No',
            'vocal_duration': 'N/A',
            'vocal_strain': 'N/A'
        },
        {
            'timestamp': now_ms - (3600 * 1000 * 2),
            'type': 'voice',
            'rate': 'N/A',
            'strain': 'N/A',
            'vocal_duration': '15.5s',
            'vocal_strain': 'High (Detected)'
        }
    ]

# --- Flask Routes ---

@app.route('/')
def index():
    """Serves the complete single-file HTML/JS application."""
    # We load the entire HTML template here, including all client-side logic.
    return HTML_TEMPLATE

@app.route('/download_report')
def download_report():
    """Fetches data (mocked) and generates a CSV file for download."""
    
    data = fetch_mock_biometric_data()
    
    if not data:
        # NOTE: In a production Flask app, you'd integrate Firebase Admin SDK
        # to fetch user-specific data from Firestore here before generating.
        return "No data available to generate report.", 404

    # Create a stream for the CSV file
    si = io.StringIO()
    cw = csv.writer(si)

    # Write headers
    headers = ['Timestamp', 'Type', 'Blink Rate (b/m)', 'Eye Strain Risk', 'Vocal Test Duration', 'Vocal Strain Level']
    cw.writerow(headers)

    # Write data rows
    for entry in data:
        # Convert timestamp (ms) to readable format
        timestamp_dt = datetime.fromtimestamp(entry['timestamp'] / 1000)
        
        row = [
            timestamp_dt.strftime('%Y-%m-%d %H:%M:%S'),
            entry['type'].capitalize(),
            entry['rate'],
            entry['strain'],
            entry['vocal_duration'],
            entry['vocal_strain']
        ]
        cw.writerow(row)

    output = si.getvalue()
    
    # Return the CSV file as a downloadable response
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=biometric_report.csv"}
    )


# --- Frontend HTML/CSS/JavaScript Template (The entire client application) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Biometric Monitor</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom styles for video feed placeholder and recording pulse */
        #video-feed {
            width: 100%;
            height: 100%;
            object-fit: cover;
            background-color: #1f2937; /* Gray-900 */
        }
        .pulse-red {
            animation: pulse-red 1s infinite;
        }
        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            50% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        }
        .aspect-video {
            aspect-ratio: 16 / 9;
        }
        .main-container {
            min-height: 100vh;
        }
        /* Fade in/out for the notification banner */
        .fade-in {
            animation: fadeIn 0.5s ease-out forwards;
        }
        .fade-out {
            animation: fadeOut 0.5s ease-out forwards;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeOut { from { opacity: 1; transform: translateY(0); } to { opacity: 0; transform: translateY(-10px); } }
    </style>
</head>
<body class="bg-gray-100 font-sans antialiased">
    
    <!-- Global Notification Banner -->
    <div id="alert-banner" class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 p-4 rounded-lg shadow-2xl transition duration-300 hidden opacity-0">
        <p id="alert-message" class="font-semibold"></p>
    </div>

    <div id="app" class="flex justify-center p-4 sm:p-6">
        <div class="w-full max-w-5xl space-y-8">

            <!-- Header -->
            <header class="bg-white p-6 rounded-2xl shadow-xl border-t-4 border-indigo-600">
                <h1 class="text-4xl font-extrabold text-gray-900 mb-2">Biometric Strain Monitor</h1>
                <p class="text-gray-600 mb-4">Real-time tools for monitoring vocal and visual fatigue.</p>
                <div id="user-id-display" class="text-xs text-gray-500 p-2 bg-gray-100 rounded-lg max-w-fit">Authenticating...</div>
            </header>

            <!-- Tool Navigation -->
            <div class="flex bg-white rounded-xl shadow-md p-2 space-x-2">
                <button id="nav-tracker" class="flex-1 py-3 font-semibold rounded-xl transition-colors bg-indigo-600 text-white shadow-lg">
                    📊 Tracker Tools
                </button>
                <button id="nav-reports" class="flex-1 py-3 font-semibold rounded-xl transition-colors text-gray-700 hover:bg-gray-100">
                    📜 Reports
                </button>
            </div>

            <!-- Tracker View -->
            <section id="tracker-view" class="space-y-8">
                <!-- Tool Selection Area -->
                <div class="flex bg-white rounded-xl shadow-md p-2 space-x-2">
                    <button id="tool-blink" class="flex-1 py-3 font-semibold rounded-xl transition-colors bg-indigo-600 text-white shadow-lg">
                        👁️ Eye Strain Tracker
                    </button>
                    <button id="tool-voice" class="flex-1 py-3 font-semibold rounded-xl transition-colors text-gray-700 hover:bg-gray-100">
                        🎙️ Voice Fatigue Tester
                    </button>
                </div>
                
                <!-- Individual Tool Container -->
                <div id="tool-container">
                    <!-- Dynamic Tool Content Renders Here -->
                </div>

                <!-- Historical Entries List -->
                <div class="space-y-4">
                    <h2 class="text-3xl font-bold text-gray-800 border-b pb-2">Analysis History</h2>
                    <div id="history-list" class="space-y-4">
                        <div class="p-6 text-center text-indigo-500 font-medium bg-white rounded-xl shadow-md">Loading your history...</div>
                    </div>
                </div>
            </section>
            
            <!-- Reports View -->
            <section id="reports-view" class="space-y-6 hidden">
                <div class="p-8 bg-white rounded-2xl shadow-xl">
                    <h2 class="text-3xl font-bold text-gray-800 mb-4">Historical Data Reports</h2>
                    <p class="text-gray-600 mb-8 border-b pb-4">
                        Download a comprehensive report of all your tracked biometric data. This uses a server-side route 
                        to securely generate the CSV file.
                    </p>
                    
                    <a href="/download_report" id="download-button" class="inline-block w-full text-center py-4 px-6 bg-green-600 hover:bg-green-700 text-white text-xl font-bold rounded-xl shadow-lg transition duration-200 transform hover:scale-[1.01] active:scale-[0.99]">
                        ⬇️ Download Full Report (CSV)
                    </a>
                </div>
                <div id="report-message" class="text-center text-gray-500 italic p-6 bg-white rounded-xl shadow-md">
                    Note: The data for this download is simulated on the Flask server side for this environment.
                </div>
            </section>
        </div>
    </div>

    <!-- Firebase Client SDK -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import { getFirestore, collection, query, addDoc, serverTimestamp, onSnapshot } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

        // Global variables provided by the environment (Mandatory usage)
        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
        const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : null;
        const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

        // --- GLOBAL STATE & FIREBASE SETUP ---
        let db = null;
        let auth = null;
        let userId = null;
        let isAuthReady = false;
        let currentEntries = [];
        let loading = true;
        
        // Tool-specific states for indefinite running
        let blinkAnalysisInterval = null;
        let voiceRecordingInterval = null;
        let voiceRecordStartTime = null;
        let mediaRecorder = null;
        let voiceStream = null;
        let blinkStream = null;

        const getUserCollectionPath = (uid) => \`/artifacts/\${appId}/users/\${uid}/biometric_entries\`;
        
        // --- UTILITY FUNCTIONS ---

        function logError(message) {
            const banner = document.getElementById('alert-banner');
            const msgEl = document.getElementById('alert-message');
            
            banner.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 z-50 p-4 rounded-lg shadow-2xl bg-red-500 text-white fade-in';
            msgEl.textContent = \`ERROR: \${message}\`;
            banner.classList.remove('hidden');
            
            setTimeout(() => {
                banner.classList.add('fade-out');
                banner.classList.remove('fade-in');
            }, 5000);
        }
        
        function logMessage(message, type = 'success') {
            const banner = document.getElementById('alert-banner');
            const msgEl = document.getElementById('alert-message');
            
            let color = '';
            if (type === 'success') {
                color = 'bg-green-600 text-white';
            } else if (type === 'info') {
                color = 'bg-indigo-600 text-white';
            }

            banner.className = \`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 p-4 rounded-lg shadow-2xl \${color} fade-in\`;
            msgEl.textContent = message;
            banner.classList.remove('hidden');

            setTimeout(() => {
                banner.classList.add('fade-out');
                banner.classList.remove('fade-in');
            }, 3500);
        }

        // --- FIREBASE SETUP ---
        async function initializeFirebase() {
            if (!firebaseConfig) {
                logError("Firebase configuration is missing.");
                document.getElementById('user-id-display').textContent = 'Authentication Failed';
                isAuthReady = true;
                loading = false;
                renderHistory();
                return;
            }

            try {
                const app = initializeApp(firebaseConfig);
                db = getFirestore(app);
                auth = getAuth(app);
                
                await new Promise((resolve) => {
                    onAuthStateChanged(auth, async (user) => {
                        if (user) {
                            userId = user.uid;
                        } else {
                            if (initialAuthToken) {
                                try {
                                    const userCredential = await signInWithCustomToken(auth, initialAuthToken);
                                    userId = userCredential.user.uid;
                                } catch (e) {
                                    await signInAnonymously(auth).then(c => userId = c.user.uid);
                                }
                            } else {
                                await signInAnonymously(auth).then(c => userId = c.user.uid);
                            }
                        }
                        // Display truncated User ID for UI clarity, while using full ID for Firestore path
                        document.getElementById('user-id-display').textContent = \`User ID: \${userId.substring(0, 10)}...\`; 
                        isAuthReady = true;
                        resolve();
                    });
                });

                startDataListener();

            } catch (e) {
                console.error("Firebase Initialization Error:", e);
                logError("Failed to initialize Firebase services.");
                isAuthReady = true;
                loading = false;
                renderHistory();
            }
        }

        function startDataListener() {
            if (!db || !userId) return;

            const path = getUserCollectionPath(userId);
            const q = query(collection(db, path));

            onSnapshot(q, (snapshot) => {
                const fetchedEntries = snapshot.docs.map(doc => ({
                    id: doc.id,
                    ...doc.data()
                }));
                // Sort by timestamp in descending order (newest first) in memory
                const sortedEntries = fetchedEntries.sort((a, b) => 
                    (b.timestamp?.seconds || 0) - (a.timestamp?.seconds || 0)
                );
                
                currentEntries = sortedEntries;
                loading = false;
                renderHistory();
            }, (err) => {
                console.error("Firestore Snapshot Error:", err);
                logError("Failed to load history entries.");
                loading = false;
                renderHistory();
            });
        }
        
        // --- DATA LOGIC & UTILS ---
        
        function generateBlinkRate() {
            // Simulate a slightly higher chance of strain to make it interesting
            const rate = Math.floor(Math.random() * 40) + 5; // 5 to 44 blinks/min
            const strain = rate < 8 || rate > 30; // High strain if too low or too high
            return { rate, strain };
        }

        function analyzeVoiceStrain(durationSeconds) {
            const factor = Math.random();
            let strainLevel = 'Low';
            
            if (durationSeconds < 1) {
                strainLevel = 'Inconclusive (Too short)';
            } else if (durationSeconds > 15 && factor > 0.6) {
                // Higher chance of strain if test is long
                strainLevel = 'High (Detected)';
            } else if (factor > 0.7) {
                strainLevel = 'Medium';
            }
            
            return strainLevel;
        }

        async function logResult(entryData) {
            if (!db || !userId) {
                logError("Authentication not complete. Cannot log data.");
                return;
            }

            logMessage("Saving analysis result...", 'info');
            
            const newEntry = {
                ...entryData,
                timestamp: serverTimestamp(),
                loggedBy: userId, 
            };

            try {
                const path = getUserCollectionPath(userId);
                await addDoc(collection(db, path), newEntry);
                logMessage(\`Result logged: \${entryData.type === 'blink' ? 'Eye Strain' : 'Voice Fatigue'}\`, 'success');
            } catch (e) {
                console.error("Error adding document: ", e);
                logError("Failed to save entry. Check console.");
            }
        }

        // --- RENDERING HISTORY ---

        function renderHistory() {
            const container = document.getElementById('history-list');
            container.innerHTML = ''; // Clear existing list

            if (loading) {
                container.innerHTML = \`<div class="p-6 text-center text-indigo-500 font-medium bg-white rounded-xl shadow-md">Loading your history...</div>\`;
                return;
            }

            if (currentEntries.length === 0) {
                container.innerHTML = \`<div class="p-6 text-center text-gray-500 italic bg-white rounded-xl shadow-md">Run an analysis using the tools above to start your tracking history!</div>\`;
                return;
            }

            currentEntries.forEach(entry => {
                const isBlinkEntry = entry.type === 'blink';
                const date = entry.timestamp ? new Date(entry.timestamp.seconds * 1000) : new Date();

                const isHighRisk = isBlinkEntry ? entry.result.strain === true : entry.result.strainLevel.includes('High');
                const riskColor = isHighRisk ? 'border-red-500 bg-red-50' : 'border-green-500 bg-green-50';
                const icon = isBlinkEntry ? '👁️' : '🎙️';
                const title = isBlinkEntry ? 'Eye Strain Analysis' : 'Vocal Fatigue Test';
                const riskText = isHighRisk ? 'HIGH RISK' : 'Normal';
                const riskTextColor = isHighRisk ? 'text-red-600' : 'text-green-600';

                const detailContent = isBlinkEntry ? \`
                    <p class="text-sm text-gray-700">Blink Rate: <span class="font-semibold">\${entry.result.rate} blinks/min</span></p>
                    <p class="text-sm text-gray-700">Strain Risk: <span class="font-bold \${riskTextColor}">\${riskText}</span></p>
                \` : \`
                    <p class="text-sm text-gray-700">Duration: <span class="font-semibold">\${entry.result.durationSeconds} seconds</span></p>
                    <p class="text-sm text-gray-700">Strain Level: <span class="font-bold \${riskTextColor}">\${entry.result.strainLevel}</span></p>
                \`;

                const html = \`
                    <div class="p-5 rounded-xl shadow-md border-l-4 \${riskColor}">
                        <div class="flex items-center justify-between mb-3 border-b pb-2">
                            <div class="flex items-center space-x-3">
                                <span class="text-2xl">\${icon}</span>
                                <span class="text-xl font-bold text-gray-800">\${title}</span>
                            </div>
                            <div class="text-xs text-gray-500 font-medium">
                                \${date.toLocaleString()}
                            </div>
                        </div>
                        <div class="flex space-x-6">
                           \${detailContent}
                        </div>
                    </div>
                \`;
                container.innerHTML += html;
            });
        }
        
        // --- TOOL LOGIC: EYE STRAIN (INDEFINITE CAM) ---

        function renderEyeStrainTracker() {
            // Stop other running tool if active
            stopVoiceRecording(true); 

            const container = document.getElementById('tool-container');
            container.innerHTML = \`
                <div class="p-8 bg-white rounded-2xl shadow-xl space-y-6">
                    <h3 class="text-2xl font-bold text-gray-800 flex items-center">
                        👁️ Eye Strain Tracker
                    </h3>
                    <p class="text-gray-600 text-sm">Real-time blink analysis runs continuously until you explicitly stop it.</p>

                    <div class="relative w-full aspect-video bg-gray-900 rounded-lg overflow-hidden border-2 border-dashed border-indigo-400">
                        <video id="video-feed" autoplay playsinline></video>
                        <div id="blink-status" class="absolute top-0 left-0 w-full h-full flex flex-col items-center justify-center bg-gray-900 bg-opacity-80 text-white font-medium text-lg transition-opacity">
                            <svg class="w-10 h-10 mb-2 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.55 4.55a.5.5 0 010 .7L15 20m0-10l4.55-4.55a.5.5 0 010-.7L15 4m-6 6l-4.55 4.55a.5.5 0 000 .7L9 20m0-10l-4.55-4.55a.5.5 0 000-.7L9 4"></path></svg>
                            Camera Idle
                        </div>
                    </div>

                    <div id="blink-results" class="hidden p-4 border rounded-xl bg-indigo-50 border-indigo-300 transition-all duration-300"></div>

                    <div class="grid grid-cols-2 gap-4">
                        <button id="blink-start-btn" class="py-3 font-bold rounded-xl transition duration-200 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md">
                            Start Camera & Analysis
                        </button>
                        <button id="blink-stop-btn" disabled class="py-3 font-bold rounded-xl transition duration-200 bg-red-400 text-white cursor-not-allowed">
                            Stop Analysis
                        </button>
                    </div>

                    <button id="blink-log-btn" disabled class="w-full py-3 bg-green-500 text-white font-bold rounded-xl transition duration-200 opacity-50 cursor-not-allowed hover:bg-green-600">
                        Log Current Result to History
                    </button>
                </div>
            \`;
            
            // Attach event listeners
            document.getElementById('blink-start-btn').addEventListener('click', startBlinkAnalysis);
            document.getElementById('blink-stop-btn').addEventListener('click', stopBlinkAnalysis);
            document.getElementById('blink-log-btn').addEventListener('click', logBlinkResult);
        }
        
        async function startBlinkAnalysis() {
            if (!userId) { logError("Please wait for authentication to complete."); return; }
            if (blinkAnalysisInterval !== null) return; 

            const statusEl = document.getElementById('blink-status');
            const videoEl = document.getElementById('video-feed');
            const startBtn = document.getElementById('blink-start-btn');
            const stopBtn = document.getElementById('blink-stop-btn');
            
            statusEl.innerHTML = '<svg class="w-8 h-8 animate-spin mr-3 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> Starting Camera...';
            startBtn.disabled = true;
            
            try {
                blinkStream = await navigator.mediaDevices.getUserMedia({ video: true });
                videoEl.srcObject = blinkStream;
                statusEl.innerHTML = '<svg class="w-10 h-10 mb-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.55 4.55a.5.5 0 010 .7L15 20m0-10l4.55-4.55a.5.5 0 010-.7L15 4m-6 6l-4.55 4.55a.5.5 0 000 .7L9 20m0-10l-4.55-4.55a.5.5 0 000-.7L9 4"></path></svg> Camera Active & Analyzing';
            } catch (err) {
                console.error("Camera access failed:", err);
                statusEl.innerHTML = '<svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path></svg> Error: Camera permission denied.';
                stopBlinkAnalysis(true); 
                return;
            }

            // Update UI
            stopBtn.disabled = false;
            stopBtn.classList.remove('bg-red-400', 'cursor-not-allowed');
            stopBtn.classList.add('bg-red-600', 'hover:bg-red-700', 'pulse-red');

            // Start indefinite simulated analysis (updates every 4 seconds)
            updateBlinkAnalysis(); 
            blinkAnalysisInterval = setInterval(updateBlinkAnalysis, 4000);
            logMessage("Eye Strain Analysis started. Click 'Log' to save a result.", 'success');
        }

        function updateBlinkAnalysis() {
            const { rate, strain } = generateBlinkRate();
            const isHighRisk = strain;
            const riskColor = isHighRisk ? 'text-red-600 font-extrabold' : 'text-green-600 font-bold';
            
            const resultsEl = document.getElementById('blink-results');
            resultsEl.classList.remove('hidden');
            resultsEl.innerHTML = \`
                <p class="text-sm font-medium">
                    <span class="text-indigo-700">BLINK RATE:</span> <span class="text-xl font-bold">\${rate} / min</span>
                </p>
                <p class="text-sm font-medium">
                    <span class="text-indigo-700">STRAIN INDICATOR:</span> <span class="text-lg \${riskColor}">
                        \${isHighRisk ? ' HIGH RISK (Actively Rest)' : ' Normal (Proceed)'}
                    </span>
                </p>
            \`;

            // Store current result for logging
            document.getElementById('blink-results').dataset.currentResult = JSON.stringify({ rate, strain });
            document.getElementById('blink-log-btn').disabled = false;
            document.getElementById('blink-log-btn').classList.remove('opacity-50', 'cursor-not-allowed');
            document.getElementById('blink-log-btn').classList.add('hover:bg-green-600');
        }

        function stopBlinkAnalysis(softStop = false) {
            clearInterval(blinkAnalysisInterval);
            blinkAnalysisInterval = null;
            
            if (blinkStream) {
                blinkStream.getTracks().forEach(track => track.stop());
                blinkStream = null;
            }

            if (!softStop) {
                document.getElementById('blink-status').innerHTML = '<svg class="w-10 h-10 mb-2 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.55 4.55a.5.5 0 010 .7L15 20m0-10l4.55-4.55a.5.5 0 010-.7L15 4m-6 6l-4.55 4.55a.5.5 0 000 .7L9 20m0-10l-4.55-4.55a.5.5 0 000-.7L9 4"></path></svg> Analysis Stopped';
            }

            document.getElementById('blink-start-btn').disabled = false;
            document.getElementById('blink-stop-btn').disabled = true;
            document.getElementById('blink-stop-btn').classList.remove('bg-red-600', 'hover:bg-red-700', 'pulse-red');
            document.getElementById('blink-stop-btn').classList.add('bg-red-400', 'cursor-not-allowed');
        }

        function logBlinkResult() {
            const resultStr = document.getElementById('blink-results').dataset.currentResult;
            if (resultStr) {
                const result = JSON.parse(resultStr);
                logResult({ type: 'blink', result: result });
            }
        }
        
        // --- TOOL LOGIC: VOICE FATIGUE (INDEFINITE RECORD) ---

        function renderVoiceFatigueChecker() {
            // Stop other running tool if active
            stopBlinkAnalysis(true); 

            const container = document.getElementById('tool-container');
            container.innerHTML = \`
                <div class="p-8 bg-white rounded-2xl shadow-xl space-y-6">
                    <h3 class="text-2xl font-bold text-gray-800 flex items-center">
                        🎙️ Voice Fatigue Tester
                    </h3>
                    <p class="text-gray-600 text-sm">Records microphone audio continuously to detect changes in vocal output that indicate strain.</p>

                    <div class="flex flex-col sm:flex-row justify-between items-center p-4 border rounded-xl bg-gray-100 border-gray-300">
                        <span id="voice-status" class="font-bold text-gray-700 text-lg mb-2 sm:mb-0">Ready to Record</span>
                        <span id="voice-duration" class="text-3xl font-mono text-gray-900 bg-gray-200 px-3 py-1 rounded-lg">0.0s</span>
                    </div>

                    <div id="voice-results" class="hidden p-4 border rounded-xl bg-indigo-50 border-indigo-300 transition-all duration-300"></div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <button id="voice-start-btn" class="py-3 font-bold rounded-xl transition duration-200 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md">
                            Start Recording
                        </button>
                        <button id="voice-stop-btn" disabled class="py-3 font-bold rounded-xl transition duration-200 bg-red-400 text-white cursor-not-allowed">
                            Stop Recording
                        </button>
                    </div>

                    <button id="voice-log-btn" disabled class="w-full py-3 bg-green-500 text-white font-bold rounded-xl transition duration-200 opacity-50 cursor-not-allowed hover:bg-green-600">
                        Log Current Result to History
                    </button>
                </div>
            \`;
            
            // Attach event listeners
            document.getElementById('voice-start-btn').addEventListener('click', startVoiceRecording);
            document.getElementById('voice-stop-btn').addEventListener('click', stopVoiceRecording);
            document.getElementById('voice-log-btn').addEventListener('click', logVoiceResult);
        }

        async function startVoiceRecording() {
            if (!userId) { logError("Please wait for authentication to complete."); return; }
            if (mediaRecorder && mediaRecorder.state === 'recording') return;

            const statusEl = document.getElementById('voice-status');
            const startBtn = document.getElementById('voice-start-btn');
            const stopBtn = document.getElementById('voice-stop-btn');
            const durationEl = document.getElementById('voice-duration');
            
            statusEl.textContent = 'Starting Microphone...';
            startBtn.disabled = true;
            
            try {
                voiceStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(voiceStream);
                
                // No need to collect chunks for simulated analysis, just monitor state
                mediaRecorder.ondataavailable = (event) => { /* Ignore audio data */ };

                mediaRecorder.onstop = () => {
                    // This block executes after mediaRecorder.stop() is called
                    if (voiceStream) {
                        voiceStream.getTracks().forEach(track => track.stop());
                        voiceStream = null;
                    }

                    statusEl.textContent = 'Analyzing Vocal Strain...';
                    
                    // Final calculation and analysis
                    const finalDuration = Math.max(0, (Date.now() - voiceRecordStartTime) / 1000).toFixed(1);
                    const strainLevel = analyzeVoiceStrain(parseFloat(finalDuration));
                    
                    renderVoiceAnalysisResults(finalDuration, strainLevel);
                    statusEl.textContent = 'Analysis Complete';
                    statusEl.classList.remove('text-red-500');
                    statusEl.classList.add('text-gray-700');
                    
                    // Stop duration interval
                    clearInterval(voiceRecordingInterval);
                    voiceRecordingInterval = null;
                    voiceRecordStartTime = null;
                };

                mediaRecorder.start();
                
                // Start indefinite duration counter
                voiceRecordStartTime = Date.now();
                voiceRecordingInterval = setInterval(() => {
                    const elapsed = (Date.now() - voiceRecordStartTime) / 1000;
                    durationEl.textContent = \`${elapsed.toFixed(1)}s\`;
                }, 100);

                // Update UI
                stopBtn.disabled = false;
                stopBtn.classList.remove('bg-red-400', 'cursor-not-allowed');
                stopBtn.classList.add('bg-red-600', 'hover:bg-red-700', 'pulse-red');
                statusEl.textContent = 'Recording Voice (Test running indefinitely)';
                statusEl.classList.add('text-red-500');
                statusEl.classList.remove('text-gray-700');
                logMessage("Voice Test started. Record as long as needed.", 'success');


            } catch (err) {
                console.error("Microphone access failed:", err);
                statusEl.textContent = 'Error: Microphone permission denied.';
                stopVoiceRecording(true); 
            }
        }

        function stopVoiceRecording(softStop = false) {
            // Stop duration counter immediately
            clearInterval(voiceRecordingInterval);
            voiceRecordingInterval = null;
            
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop(); // This triggers mediaRecorder.onstop()
            } else if (voiceStream) {
                // Manual stop if recording didn't start (e.g., in error case)
                voiceStream.getTracks().forEach(track => track.stop());
                voiceStream = null;
            }

            if (!softStop) {
                document.getElementById('voice-status').textContent = 'Recording Stopped';
            }

            document.getElementById('voice-start-btn').disabled = false;
            document.getElementById('voice-stop-btn').disabled = true;
            document.getElementById('voice-stop-btn').classList.remove('bg-red-600', 'hover:bg-red-700', 'pulse-red');
            document.getElementById('voice-stop-btn').classList.add('bg-red-400', 'cursor-not-allowed');
        }

        function renderVoiceAnalysisResults(duration, strainLevel) {
            const resultsEl = document.getElementById('voice-results');
            resultsEl.classList.remove('hidden');

            const isHighRisk = strainLevel.includes('High');
            const riskColor = isHighRisk ? 'text-red-600 font-extrabold' : 'text-green-600 font-bold';

            resultsEl.innerHTML = \`
                <p class="text-sm font-medium">
                    <span class="text-indigo-700">RECORD DURATION:</span> <span class="text-xl font-bold">\${duration}s</span>
                </p>
                <p class="text-sm font-medium">
                    <span class="text-indigo-700">STRAIN LEVEL:</span> <span class="text-lg \${riskColor}">
                        \${strainLevel}
                    </span>
                </p>
            \`;
            
            // Store current result for logging
            document.getElementById('voice-results').dataset.currentResult = JSON.stringify({ durationSeconds: duration, strainLevel });
            document.getElementById('voice-log-btn').disabled = false;
            document.getElementById('voice-log-btn').classList.remove('opacity-50', 'cursor-not-allowed');
            document.getElementById('voice-log-btn').classList.add('hover:bg-green-600');
        }

        function logVoiceResult() {
            const resultStr = document.getElementById('voice-results').dataset.currentResult;
            if (resultStr) {
                const result = JSON.parse(resultStr);
                logResult({ type: 'voice', result: result });
            }
        }
        
        // --- NAVIGATION & INITIALIZATION ---

        function setToolActive(tool) {
            // Update tool selection buttons
            const blinkBtn = document.getElementById('tool-blink');
            const voiceBtn = document.getElementById('tool-voice');
            const activeClass = 'bg-indigo-600 text-white shadow-lg';
            const inactiveClass = 'text-gray-700 hover:bg-gray-100';

            if (tool === 'blink') {
                blinkBtn.classList.add(...activeClass.split(' '));
                blinkBtn.classList.remove(...inactiveClass.split(' '));
                voiceBtn.classList.remove(...activeClass.split(' '));
                voiceBtn.classList.add(...inactiveClass.split(' '));
                renderEyeStrainTracker();
            } else {
                voiceBtn.classList.add(...activeClass.split(' '));
                voiceBtn.classList.remove(...inactiveClass.split(' '));
                blinkBtn.classList.remove(...activeClass.split(' '));
                blinkBtn.classList.add(...inactiveClass.split(' '));
                renderVoiceFatigueChecker();
            }
        }
        
        function setViewActive(view) {
            const trackerView = document.getElementById('tracker-view');
            const reportsView = document.getElementById('reports-view');
            const navTracker = document.getElementById('nav-tracker');
            const navReports = document.getElementById('nav-reports');
            const activeClass = 'bg-indigo-600 text-white shadow-lg';
            const inactiveClass = 'text-gray-700 hover:bg-gray-100';
            
            // Stop any running cameras/mics when switching views
            stopBlinkAnalysis(true); 
            stopVoiceRecording(true); 

            if (view === 'tracker') {
                trackerView.classList.remove('hidden');
                reportsView.classList.add('hidden');
                navTracker.classList.add(...activeClass.split(' '));
                navTracker.classList.remove(...inactiveClass.split(' '));
                navReports.classList.remove(...activeClass.split(' '));
                navReports.classList.add(...inactiveClass.split(' '));
            } else {
                reportsView.classList.remove('hidden');
                trackerView.classList.add('hidden');
                navReports.classList.add(...activeClass.split(' '));
                navReports.classList.remove(...inactiveClass.split(' '));
                navTracker.classList.remove(...activeClass.split(' '));
                navTracker.classList.add(...inactiveClass.split(' '));
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            initializeFirebase();
            
            // Initial render
            setToolActive('blink');

            // Set up main navigation listeners
            document.getElementById('nav-tracker').addEventListener('click', () => setViewActive('tracker'));
            document.getElementById('nav-reports').addEventListener('click', () => setViewActive('reports'));

            // Set up tool navigation listeners
            document.getElementById('tool-blink').addEventListener('click', () => setToolActive('blink'));
            document.getElementById('tool-voice').addEventListener('click', () => setToolActive('voice'));
        });
        
        // Cleanup streams/intervals on navigation away from the app (simulated unmount)
        window.addEventListener('beforeunload', () => {
             stopBlinkAnalysis(true);
             stopVoiceRecording(true);
        });

    </script>
</body>
</html>
"""

if __name__ == '__main__':
    # This server is primarily for demonstration; frontend JS handles actual runtime logic.
    app.run(debug=True)
