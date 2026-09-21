// ============================================================
// SKYGUARD FRONTEND
// ============================================================

const API_URL = (window.location.protocol && window.location.protocol.startsWith("http")) 
    ? window.location.origin 
    : "http://127.0.0.1:8000";
async function loadWeatherData() {
    try {
        const response = await fetch(`${API_URL}/data`);

        if (!response.ok) {
            throw new Error("Failed to fetch weather data");
        }

                    const data = await response.json();

                    console.log("Weather data received from backend:", data);

                    // Replace frontend data with backend data
                    weatherReadings.length = 0;
                    weatherReadings.push(...data);
                    fullStationHistory = [...data];
                    replayIndex = Math.min(15, fullStationHistory.length);

                    // Update current sensor cards
                    displaySensorValues();

                    // Create charts using backend data
                    createSensorCharts();

                    errorMessage.classList.add("hidden");
                    predictButton.disabled = false;
                    predictButton.textContent = "Analyze Weather Data";

                    return data;

                } catch (error) {
                    console.error("Error loading weather data:", error);

                    errorMessage.textContent =
                        "Unable to load weather data. Make sure FastAPI is running.";

                    errorMessage.classList.remove("hidden");
                    predictButton.disabled = true;
                    predictButton.textContent = "Weather Data Unavailable";

                    return [];
                }
            }

            // ============================================================
            // TEST WEATHER HISTORY
            // ============================================================

            const weatherReadings = [];


            // ============================================================
            // DOM ELEMENTS
            // ============================================================

            const tempValue = document.getElementById("tempValue");
            const rhumValue = document.getElementById("rhumValue");
            const presValue = document.getElementById("presValue");

            const predictionCard =
                document.getElementById("predictionCard");

            const predictionIcon =
                document.getElementById("predictionIcon");

            const predictionStatus =
                document.getElementById("predictionStatus");

            const probability =
                document.getElementById("probability");

            const faultSensor =
                document.getElementById("faultSensor");

            const faultType =
                document.getElementById("faultType");

            const diagnosisConfidence =
                document.getElementById("diagnosisConfidence");

            const predictButton =
                document.getElementById("predictButton");

            const loading =
                document.getElementById("loading");

            const errorMessage =
                document.getElementById("errorMessage");

            const stationLabel =
                document.getElementById("stationLabel");

            const locationValue =
                document.getElementById("locationValue");

            const elevationValue =
                document.getElementById("elevationValue");

            const latestTimeValue =
                document.getElementById("latestTimeValue");

            const sensorCards =
                document.querySelectorAll(".sensor-card[data-sensor]");


            // ============================================================
            // DISPLAY CURRENT SENSOR VALUES
            // ============================================================

            function displaySensorValues() {

                const latest =
                    weatherReadings[weatherReadings.length - 1];

                if (!latest) {
                    return;
                }

                tempValue.textContent =
                    latest.temp.toFixed(1);

                rhumValue.textContent =
                    latest.rhum.toFixed(0);

                presValue.textContent =
                    latest.pres.toFixed(0);

                stationLabel.textContent =
                    `Station #${latest.station_id}`;

                locationValue.textContent =
                    `Location: ${latest.latitude.toFixed(4)}°, ${latest.longitude.toFixed(4)}°`;

                elevationValue.textContent =
                    `Elevation: ${latest.elevation.toFixed(0)} m`;

                latestTimeValue.textContent =
                    `Latest reading: ${new Date(latest.time).toLocaleString()}`;
            }


            function updateSensorHighlight(sensor) {

                sensorCards.forEach(card => {
                    card.classList.toggle(
                        "anomaly",
                        card.dataset.sensor === sensor
                    );
                });
            }


            // ============================================================
            // RUN PREDICTION
            // ============================================================

            async function analyzeWeather() {

                if (weatherReadings.length === 0) {
                    errorMessage.textContent =
                        "Weather data is still loading. Please try again in a moment.";

                    errorMessage.classList.remove("hidden");
                    return;
                }

                loading.classList.remove("hidden");
                errorMessage.classList.add("hidden");

                predictButton.disabled = true;
                predictButton.textContent = "Analyzing...";

                try {

                    const response = await fetch(
                        `${API_URL}/predict`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type": "application/json"
                            },

                            body: JSON.stringify({
                                readings: weatherReadings
                            })
                        }
                    );


                    if (!response.ok) {

                        throw new Error(
                            `API Error: ${response.status}`
                        );
                    }


                    const result =
                        await response.json();


                    displayPrediction(result);


                } catch (error) {

                    console.error(error);

                    errorMessage.textContent =
                        "Unable to connect to SkyGuard backend. " +
                        "Make sure FastAPI is running.";

                    errorMessage.classList.remove("hidden");

                } finally {

                    loading.classList.add("hidden");

                    predictButton.disabled = false;

                    predictButton.textContent =
                        "Analyze Weather Data";
                }
            }


            // ============================================================
            // ANOMALY INCIDENT REPORT SYSTEM
            // ============================================================

            let currentAnomalyReport = null;

            const downloadReportBtn = document.getElementById("downloadReportBtn");
            const reportModal = document.getElementById("reportModal");
            const reportModalBody = document.getElementById("reportModalBody");
            const closeReportBtn = document.getElementById("closeReportBtn");
            const dismissReportBtn = document.getElementById("dismissReportBtn");
            const printReportBtn = document.getElementById("printReportBtn");

            if (downloadReportBtn) {
                downloadReportBtn.addEventListener("click", openIncidentReportModal);
            }
            if (closeReportBtn) {
                closeReportBtn.addEventListener("click", closeIncidentReportModal);
            }
            if (dismissReportBtn) {
                dismissReportBtn.addEventListener("click", closeIncidentReportModal);
            }
            if (printReportBtn) {
                printReportBtn.addEventListener("click", () => window.print());
            }

            function openIncidentReportModal() {
                if (!currentAnomalyReport || !reportModal || !reportModalBody) return;

                const rep = currentAnomalyReport;
                const reportId = `INC-${Date.now().toString().slice(-6)}`;

                let maintenanceAction = "Inspect sensor transducer and wiring harness for hardware malfunction.";
                if (rep.faultType === "STUCK") {
                    maintenanceAction = `High Risk Sensor Lockup Detected: Perform immediate hard reset and hardware recalibration on ${rep.faultSensor} transducer at ${rep.stationName}.`;
                } else if (rep.faultType === "DRIFT") {
                    maintenanceAction = `Sensor Calibration Drift Detected: Re-zero and baseline calibrate ${rep.faultSensor} analog-to-digital converter unit at ${rep.stationName}.`;
                } else if (rep.faultType === "SPIKE") {
                    maintenanceAction = `Transient Spike Anomaly: Inspect surge protector, shielding, and power supply stability for ${rep.faultSensor} channel at ${rep.stationName}.`;
                }

                reportModalBody.innerHTML = `
                    <div class="report-section-block">
                        <div class="report-grid-2">
                            <div class="report-meta-item"><span>REPORT ID</span><strong>${reportId}</strong></div>
                            <div class="report-meta-item"><span>DETECTION ENGINE</span><strong>SkyGuard V3 Random Forest</strong></div>
                            <div class="report-meta-item"><span>STATION NAME</span><strong>${rep.stationName} (#${rep.stationId})</strong></div>
                            <div class="report-meta-item"><span>INCIDENT TIMESTAMP</span><strong>${rep.timestamp}</strong></div>
                            <div class="report-meta-item"><span>COORDINATES</span><strong>${rep.location}</strong></div>
                            <div class="report-meta-item"><span>ELEVATION</span><strong>${rep.elevation}</strong></div>
                        </div>
                    </div>

                    <div class="report-section-block" style="border-color: rgba(255,93,108,0.5); background: rgba(255,93,108,0.06);">
                        <h4 style="color:#ff5d6c; font-size:14px; margin-bottom:10px;">DIAGNOSTIC FAULT SUMMARY</h4>
                        <div class="report-grid-2">
                            <div class="report-meta-item"><span>ANOMALY PROBABILITY</span><strong style="color:#ff5d6c;">${rep.probability}% (Threshold: 60.0%)</strong></div>
                            <div class="report-meta-item"><span>PRIMARY FAULT SENSOR</span><strong>${rep.faultSensor}</strong></div>
                            <div class="report-meta-item"><span>FAULT CHARACTERIZATION</span><strong>${rep.faultType}</strong></div>
                            <div class="report-meta-item"><span>DIAGNOSIS CONFIDENCE</span><strong>${rep.confidence}%</strong></div>
                        </div>
                    </div>

                    <div class="report-section-block">
                        <h4 style="color:var(--accent); font-size:14px; margin-bottom:8px;">RECOMMENDED FIELD ACTION</h4>
                        <p style="color:var(--text); font-size:13px; margin:0;">${maintenanceAction}</p>
                    </div>

                    <div class="report-section-block">
                        <h4 style="color:var(--muted); font-size:13px; margin-bottom:10px;">RECENT TELEMETRY SNAPSHOT</h4>
                        <table class="report-table">
                            <thead>
                                <tr><th>Timestamp</th><th>Temp (°C)</th><th>Humidity (%)</th><th>Pressure (hPa)</th></tr>
                            </thead>
                            <tbody>
                                ${(rep.readings || []).slice(-5).map(r => `
                                    <tr>
                                        <td>${r.time || rep.timestamp}</td>
                                        <td>${r.temp !== undefined ? r.temp.toFixed(1) : '--'}</td>
                                        <td>${r.rhum !== undefined ? r.rhum.toFixed(0) : '--'}</td>
                                        <td>${r.pres !== undefined ? r.pres.toFixed(0) : '--'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;

                reportModal.classList.remove("hidden");
            }

            function closeIncidentReportModal() {
                if (reportModal) reportModal.classList.add("hidden");
            }


            // ============================================================
            // DISPLAY PREDICTION
            // ============================================================

            function displayPrediction(result) {

                const percentage =
                    (result.anomaly_probability * 100).toFixed(1);

                probability.textContent =
                    `${percentage}%`;


                if (result.anomaly) {

                    // --------------------------------------------
                    // ANOMALY
                    // --------------------------------------------

                    predictionCard.classList.remove("normal");
                    predictionCard.classList.add("anomaly");

                    predictionIcon.textContent = "!";

                    predictionStatus.textContent =
                        "ANOMALY DETECTED";


                    faultSensor.textContent =
                        result.fault_sensor
                            ? result.fault_sensor.toUpperCase()
                            : "--";


                    faultType.textContent =
                        result.fault_type
                            ? result.fault_type.toUpperCase()
                            : "--";


                    diagnosisConfidence.textContent =
                        result.diagnosis_confidence !== null
                            ? `${(
                                result.diagnosis_confidence * 100
                            ).toFixed(1)}%`
                            : "--";

                    updateSensorHighlight(result.fault_sensor);

                    // Save current anomaly report data & show Download Report button
                    currentAnomalyReport = {
                        stationId: selectedStationId || 42475,
                        stationName: stationLabel.textContent,
                        location: locationValue.textContent.replace("Location: ", ""),
                        elevation: elevationValue.textContent.replace("Elevation: ", ""),
                        timestamp: latestTimeValue.textContent.replace("Timestamp: ", "").replace("Latest reading: ", ""),
                        probability: percentage,
                        faultSensor: result.fault_sensor ? result.fault_sensor.toUpperCase() : "UNKNOWN",
                        faultType: result.fault_type ? result.fault_type.toUpperCase() : "UNKNOWN",
                        confidence: result.diagnosis_confidence ? (result.diagnosis_confidence * 100).toFixed(1) : "--",
                        readings: [...weatherReadings]
                    };

                    if (downloadReportBtn) {
                        downloadReportBtn.classList.remove("hidden");
                    }

                } else {

                    // --------------------------------------------
                    // NORMAL
                    // --------------------------------------------

                    predictionCard.classList.remove("anomaly");
                    predictionCard.classList.add("normal");

                    predictionIcon.textContent = "✓";

                    predictionStatus.textContent =
                        "SYSTEM NORMAL";


                    faultSensor.textContent = "--";

                    faultType.textContent = "--";

                    diagnosisConfidence.textContent = "--";

                    updateSensorHighlight(null);

                    if (downloadReportBtn) {
                        downloadReportBtn.classList.add("hidden");
                    }
                }
            }


            // ============================================================
            // BUTTON EVENT
            // ============================================================

            predictButton.addEventListener(
                "click",
                analyzeWeather
            );


            // ============================================================
            // SENSOR TREND CHARTS
            // ============================================================

            // ============================================================

            let temperatureChart = null;
            let humidityChart = null;
            let pressureChart = null;


            function createSensorCharts() {

                const temperatureCanvas =
                    document.getElementById("temperatureChart");

                const humidityCanvas =
                    document.getElementById("humidityChart");

                const pressureCanvas =
                    document.getElementById("pressureChart");


                if (
                    !temperatureCanvas ||
                    !humidityCanvas ||
                    !pressureCanvas
                ) {
                    console.error(
                        "SkyGuard: Chart canvas elements not found."
                    );
                    return;
                }


                // Destroy old charts before creating new ones
                if (temperatureChart) {
                    temperatureChart.destroy();
                }

                if (humidityChart) {
                    humidityChart.destroy();
                }

                if (pressureChart) {
                    pressureChart.destroy();
                }


                // Raw timestamps for exact tooltips & date tick calculations
                const rawTimestamps = weatherReadings.map(reading => reading.time || "");

                const temperatureData = weatherReadings.map(reading => reading.temp);
                const humidityData = weatherReadings.map(reading => reading.rhum);
                const pressureData = weatherReadings.map(reading => reading.pres);

                // Helper for clean 3-month date tick formatting (e.g. "Jan 1", "Jan 15")
                const xAxisConfig = {
                    ticks: {
                        color: "#8fa8c4",
                        maxTicksLimit: 8,
                        autoSkip: true,
                        callback: function(val, index) {
                            const rawLabel = this.getLabelForValue(val);
                            if (!rawLabel) return "";
                            const d = new Date(rawLabel);
                            if (isNaN(d.getTime())) return rawLabel;
                            const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                            return `${monthNames[d.getMonth()]} ${d.getDate()}`;
                        }
                    },
                    grid: { display: false }
                };

                const tooltipConfig = {
                    callbacks: {
                        title: function(items) {
                            if (!items.length) return "";
                            return `Timestamp: ${items[0].label}`;
                        }
                    }
                };

                // ========================================================
                // TEMPERATURE (°C)
                // ========================================================

                temperatureChart = new Chart(
                    temperatureCanvas,
                    {
                        type: "line",
                        data: {
                            labels: rawTimestamps,
                            datasets: [{
                                label: "Temperature (°C)",
                                data: temperatureData,
                                borderColor: "#f59e0b",
                                backgroundColor: "rgba(245, 158, 11, 0.08)",
                                tension: 0.3,
                                fill: true,
                                pointRadius: weatherReadings.length > 200 ? 0 : 2,
                                pointHoverRadius: 5
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    ...tooltipConfig,
                                    callbacks: {
                                        ...tooltipConfig.callbacks,
                                        label: (item) => `Temperature: ${item.formattedValue} °C`
                                    }
                                }
                            },
                            scales: {
                                x: xAxisConfig,
                                y: {
                                    ticks: {
                                        color: "#94a3b8",
                                        callback: (val) => `${val} °C`
                                    },
                                    grid: { color: "rgba(255,255,255,0.05)" }
                                }
                            }
                        }
                    }
                );


                // ========================================================
                // HUMIDITY (% RH)
                // ========================================================

                humidityChart = new Chart(
                    humidityCanvas,
                    {
                        type: "line",
                        data: {
                            labels: rawTimestamps,
                            datasets: [{
                                label: "Humidity (% RH)",
                                data: humidityData,
                                borderColor: "#10b981",
                                backgroundColor: "rgba(16, 185, 129, 0.08)",
                                tension: 0.3,
                                fill: true,
                                pointRadius: weatherReadings.length > 200 ? 0 : 2,
                                pointHoverRadius: 5
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    ...tooltipConfig,
                                    callbacks: {
                                        ...tooltipConfig.callbacks,
                                        label: (item) => `Humidity: ${item.formattedValue} % RH`
                                    }
                                }
                            },
                            scales: {
                                x: xAxisConfig,
                                y: {
                                    ticks: {
                                        color: "#94a3b8",
                                        callback: (val) => `${val} %`
                                    },
                                    grid: { color: "rgba(255,255,255,0.05)" }
                                }
                            }
                        }
                    }
                );


                // ========================================================
                // PRESSURE (hPa)
                // ========================================================

                pressureChart = new Chart(
                    pressureCanvas,
                    {
                        type: "line",
                        data: {
                            labels: rawTimestamps,
                            datasets: [{
                                label: "Pressure (hPa)",
                                data: pressureData,
                                borderColor: "#6366f1",
                                backgroundColor: "rgba(99, 102, 241, 0.08)",
                                tension: 0.3,
                                fill: true,
                                pointRadius: weatherReadings.length > 200 ? 0 : 2,
                                pointHoverRadius: 5
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    ...tooltipConfig,
                                    callbacks: {
                                        ...tooltipConfig.callbacks,
                                        label: (item) => `Pressure: ${item.formattedValue} hPa`
                                    }
                                }
                            },
                            scales: {
                                x: xAxisConfig,
                                y: {
                                    ticks: {
                                        color: "#94a3b8",
                                        callback: (val) => `${val} hPa`
                                    },
                                    grid: { color: "rgba(255,255,255,0.05)" }
                                }
                            }
                        }
                    }
                );


                console.log(
                    "SkyGuard: 3-Month Trend Line Charts created using",
                    weatherReadings.length,
                    "readings."
                );
            }


            // ============================================================
            // LOAD BACKEND DATA AFTER DOM IS READY
            // ============================================================

            document.addEventListener(
                "DOMContentLoaded",
                function () {
                    predictButton.disabled = true;
                    predictButton.textContent = "Loading Weather Data...";
                    loadWeatherData();
                    initIndiaMap();
                    setupReplayControls();
                }
            );


            // ============================================================
            // INDIA MAP & STATION SELECTION (PHASE 3 & PHASE 4)
            // ============================================================

            let map = null;
            let stationMarkers = {};
            let selectedStationId = null;

            async function initIndiaMap() {
                const mapContainer = document.getElementById("indiaMap");
                if (!mapContainer || typeof L === "undefined") {
                    console.error("SkyGuard: Map container or Leaflet library missing.");
                    return;
                }

                // Center map over India
                map = L.map("indiaMap", {
                    center: [22.5937, 78.9629],
                    zoom: 5,
                    zoomControl: true
                });

                // Esri Dark Gray Canvas tile layer (No API key required)
                L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
                    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
                    maxZoom: 16
                }).addTo(map);

                // Overlay official Survey of India boundary outline (Full J&K, Ladakh, Arunachal Pradesh, Northeast)
                try {
                    const geoResp = await fetch("india_boundary.geojson");
                    if (geoResp.ok) {
                        const geoData = await geoResp.json();
                        L.geoJSON(geoData, {
                            style: {
                                color: "#f59e0b",
                                weight: 1.5,
                                opacity: 0.8,
                                fill: false,
                                fillOpacity: 0
                            }
                        }).addTo(map);
                    }
                } catch (err) {
                    console.warn("India GeoJSON boundary layer warning:", err);
                }

                await loadStationsOnMap();
            }

            async function loadStationsOnMap() {
                try {
                    const response = await fetch(`${API_URL}/stations`);
                    if (!response.ok) {
                        throw new Error("Failed to fetch stations list");
                    }

                    const data = await response.json();
                    const stations = data.stations || [];

                    // Clear old markers
                    Object.values(stationMarkers).forEach(marker => map.removeLayer(marker));
                    stationMarkers = {};

                    stations.forEach(station => {
                        const isAnomaly = station.prediction && station.prediction.anomaly;
                        const statusClass = isAnomaly ? "anomaly" : "normal";
                        const statusText = isAnomaly ? "ANOMALY DETECTED" : "NORMAL";

                        // Custom divIcon marker pin
                        const iconHtml = `<div class="marker-pin ${statusClass}" id="marker-${station.station_id}"></div>`;
                        const customIcon = L.divIcon({
                            className: "custom-marker",
                            html: iconHtml,
                            iconSize: [20, 20],
                            iconAnchor: [10, 10]
                        });

                        const marker = L.marker([station.latitude, station.longitude], { icon: customIcon }).addTo(map);

                        const probPercent = station.prediction
                            ? (station.prediction.anomaly_probability * 100).toFixed(1)
                            : "--";

                        const popupContent = `
                <div class="popup-content">
                    <h4>${station.name} (#${station.station_id})</h4>
                    <p>Lat: ${station.latitude.toFixed(4)}°, Lon: ${station.longitude.toFixed(4)}°</p>
                    <p>Elevation: ${station.elevation} m</p>
                    <p>Anomaly Risk: <strong>${probPercent}%</strong></p>
                    <span class="popup-status ${statusClass}">${statusText}</span>
                    <br><small style="color:#43d9ff; margin-top:6px; display:inline-block;">Click marker to view telemetry & trends</small>
                </div>
            `;

                        marker.bindPopup(popupContent);

                        // Phase 4: Marker selection click event
                        marker.on("click", () => {
                            selectStation(station.station_id);
                        });

                        stationMarkers[station.station_id] = marker;
                    });

                    // Automatically detect user location and select nearest weather station on load
                    detectUserLocationAndSelectStation(stations);

                } catch (error) {
                    console.error("Error loading stations on map:", error);
                }
            }

            function detectUserLocationAndSelectStation(allStations) {
                if (!navigator.geolocation || !allStations || !allStations.length) return;

                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        const uLat = pos.coords.latitude;
                        const uLon = pos.coords.longitude;

                        let minDistance = Infinity;
                        let closestStation = allStations[0];

                        allStations.forEach((st) => {
                            const dist = Math.hypot(st.latitude - uLat, st.longitude - uLon);
                            if (dist < minDistance) {
                                minDistance = dist;
                                closestStation = st;
                            }
                        });

                        console.log(`SkyGuard: User location detected near ${closestStation.name} (#${closestStation.station_id})`);
                        selectStation(closestStation.station_id);
                    },
                    (err) => {
                        console.warn("User geolocation permission unavailable. Defaulting to primary station.");
                    },
                    { timeout: 4000 }
                );
            }

            async function selectStation(stationId) {
                selectedStationId = stationId;

                // Update marker highlight styles
                Object.keys(stationMarkers).forEach(id => {
                    const pin = document.getElementById(`marker-${id}`);
                    if (pin) {
                        if (parseInt(id) === stationId) {
                            pin.classList.add("selected");
                        } else {
                            pin.classList.remove("selected");
                        }
                    }
                });

                try {
                    const response = await fetch(`${API_URL}/station/${stationId}?limit=72`);
                    if (!response.ok) {
                        throw new Error(`Failed to fetch details for station ${stationId}`);
                    }

                    const data = await response.json();

                    // Update full history and reset replay index
                    fullStationHistory = data.history ? [...data.history] : [];
                    replayIndex = Math.min(15, fullStationHistory.length);
                    pauseReplay();

                    // Replace frontend readings with station history slice
                    const initialSlice = fullStationHistory.slice(0, replayIndex);
                    weatherReadings.length = 0;
                    weatherReadings.push(...initialSlice);

                    // Refresh UI components
                    displaySensorValues();
                    createSensorCharts();

                    if (data.prediction) {
                        displayPrediction(data.prediction);
                    }

                    if (replayProgressBar) {
                        replayProgressBar.style.width = "0%";
                    }

                    if (replayStatusText) {
                        const stName = data.station ? data.station.name : `Station ${stationId}`;
                        replayStatusText.textContent = `Selected ${stName} • Press Start Replay to simulate telemetry timeline`;
                    }

                } catch (error) {
                    console.error(`Error selecting station ${stationId}:`, error);
                }
            }


// ============================================================
// NATIONAL COMMAND CENTER — GLOBAL 4-MONTH NETWORK REPLAY (PHASE 5)
// ============================================================

let networkTimeline = [];
let networkReplayIndex = 0;
let replayTimer = null;
let isReplaying = false;
let latestActiveAnomalyStationId = null;

const replayStartBtn = document.getElementById("replayStartBtn");
const replayPauseBtn = document.getElementById("replayPauseBtn");
const replayResetBtn = document.getElementById("replayResetBtn");
const replaySpeedSelect = document.getElementById("replaySpeed");
const replayProgressBar = document.getElementById("replayProgress");
const replayStatusText = document.getElementById("replayStatusText");
const largeAnomalyModal = document.getElementById("largeAnomalyModal");
const largeAnomStationName = document.getElementById("largeAnomStationName");
const largeAnomFaultSensor = document.getElementById("largeAnomFaultSensor");
const largeAnomFaultType = document.getElementById("largeAnomFaultType");
const largeAnomRisk = document.getElementById("largeAnomRisk");
const largeAnomConfidence = document.getElementById("largeAnomConfidence");
const largeAnomTemp = document.getElementById("largeAnomTemp");
const largeAnomRhum = document.getElementById("largeAnomRhum");
const largeAnomPres = document.getElementById("largeAnomPres");
const largeAnomTime = document.getElementById("largeAnomTime");
const largeAnomCloseBtn = document.getElementById("largeAnomCloseBtn");
const largeAnomReportBtn = document.getElementById("largeAnomReportBtn");
const largeAnomResumeBtn = document.getElementById("largeAnomResumeBtn");

function showLargeAnomalyModal(st, timestampStr) {
    if (!largeAnomalyModal) return;

    if (largeAnomStationName) largeAnomStationName.textContent = `${st.name} (#${st.station_id})`;
    if (largeAnomFaultSensor) largeAnomFaultSensor.textContent = st.fault_sensor || st.sensor || "TEMP_SENSOR";
    if (largeAnomFaultType) largeAnomFaultType.textContent = st.fault_type || st.type || "ANOMALY_DETECTED";
    if (largeAnomRisk) largeAnomRisk.textContent = `${st.prob || (st.anomaly_probability ? (st.anomaly_probability * 100).toFixed(1) : "98.5")}%`;
    if (largeAnomConfidence) largeAnomConfidence.textContent = `${st.conf || (st.diagnosis_confidence ? (st.diagnosis_confidence * 100).toFixed(1) : "95.0")}%`;

    if (largeAnomTemp) largeAnomTemp.textContent = st.temp !== undefined ? `${st.temp.toFixed(1)} °C` : "--";
    if (largeAnomRhum) largeAnomRhum.textContent = st.rhum !== undefined ? `${st.rhum.toFixed(0)} %` : "--";
    if (largeAnomPres) largeAnomPres.textContent = st.pres !== undefined ? `${st.pres.toFixed(0)} hPa` : "--";
    if (largeAnomTime) largeAnomTime.textContent = timestampStr || "--";

    largeAnomalyModal.classList.remove("hidden");
}

function hideLargeAnomalyModal() {
    if (largeAnomalyModal) largeAnomalyModal.classList.add("hidden");
}

function setupReplayControls() {
    if (!replayStartBtn || !replayPauseBtn || !replayResetBtn) {
        return;
    }

    replayStartBtn.addEventListener("click", startReplay);
    replayPauseBtn.addEventListener("click", pauseReplay);
    replayResetBtn.addEventListener("click", resetReplay);

    if (replaySpeedSelect) {
        replaySpeedSelect.addEventListener("change", () => {
            if (isReplaying) {
                pauseReplay();
                startReplay();
            }
        });
    }

    if (largeAnomCloseBtn) {
        largeAnomCloseBtn.addEventListener("click", hideLargeAnomalyModal);
    }

    if (largeAnomResumeBtn) {
        largeAnomResumeBtn.addEventListener("click", () => {
            hideLargeAnomalyModal();
            if (!isReplaying) {
                startReplay();
            }
        });
    }

    if (largeAnomReportBtn) {
        largeAnomReportBtn.addEventListener("click", () => {
            const currentPeriodId = Math.min(6, Math.floor(networkReplayIndex / 360) + 1);
            window.open(`${API_URL}/report/${currentPeriodId}`, "_blank");
        });
    }
}

async function loadNationalNetworkTimeline() {
    if (networkTimeline.length > 0) return true;

    try {
        if (replayStatusText) {
            replayStatusText.textContent = "Loading 4-Month National Network Timeline (All 20 Stations)...";
        }

        const response = await fetch(`${API_URL}/network/timeline`);
        if (!response.ok) {
            throw new Error("Failed to load national network timeline");
        }

        const data = await response.json();
        networkTimeline = data.timeline || [];
        console.log(`Loaded ${networkTimeline.length} national network timesteps.`);
        return networkTimeline.length > 0;

    } catch (err) {
        console.error("Error loading national network timeline:", err);
        if (replayStatusText) {
            replayStatusText.textContent = "Error loading national timeline. Ensure FastAPI server is running.";
        }
        return false;
    }
}

async function startReplay() {
    const loaded = await loadNationalNetworkTimeline();
    if (!loaded) return;

    if (networkReplayIndex >= networkTimeline.length) {
        networkReplayIndex = 0;
    }

    isReplaying = true;
    if (replayStartBtn) replayStartBtn.disabled = true;
    if (replayPauseBtn) replayPauseBtn.disabled = false;

    runNetworkReplayStep();
}

function runNetworkReplayStep() {
    if (!isReplaying) return;

    if (networkReplayIndex >= networkTimeline.length) {
        pauseReplay();
        if (replayStatusText) {
            replayStatusText.textContent = "National Telemetry Feed Complete • Processed 2,868 hourly steps across all 20 stations.";
        }
        return;
    }

    const currentStep = networkTimeline[networkReplayIndex];
    const timestampStr = currentStep.timestamp;
    const stations = currentStep.stations || [];

    const activeAnomalies = [];

    // Update ALL 20 station markers on India Map simultaneously
    stations.forEach(st => {
        const isAnom = st.anomaly;
        const marker = stationMarkers[st.station_id];
        const pinElement = document.getElementById(`marker-${st.station_id}`);

        if (pinElement) {
            if (isAnom) {
                pinElement.className = `marker-pin anomaly ${st.station_id === selectedStationId ? "selected" : ""}`;
            } else {
                pinElement.className = `marker-pin normal ${st.station_id === selectedStationId ? "selected" : ""}`;
            }
        }

        if (isAnom) {
            activeAnomalies.push({
                station_id: st.station_id,
                name: st.name,
                sensor: st.fault_sensor,
                type: st.fault_type,
                prob: (st.anomaly_probability * 100).toFixed(1),
                conf: st.diagnosis_confidence ? (st.diagnosis_confidence * 100).toFixed(1) : "--",
                temp: st.temp,
                rhum: st.rhum,
                pres: st.pres,
                anomaly_probability: st.anomaly_probability,
                diagnosis_confidence: st.diagnosis_confidence,
                fault_sensor: st.fault_sensor,
                fault_type: st.fault_type
            });
        }

        // Update marker popup content with live timestamp
        if (marker) {
            const statusClass = isAnom ? "anomaly" : "normal";
            const statusText = isAnom ? "ANOMALY DETECTED" : "NORMAL";
            const probPercent = (st.anomaly_probability * 100).toFixed(1);

            const popupContent = `
                <div class="popup-content">
                    <h4>${st.name} (#${st.station_id})</h4>
                    <p>Timestamp: <strong>${timestampStr}</strong></p>
                    <p>Anomaly Risk: <strong>${probPercent}%</strong></p>
                    ${isAnom ? `<p style="color:#f43f5e; font-weight:700;">Fault: ${st.fault_sensor} ${st.fault_type} (${(st.diagnosis_confidence*100).toFixed(1)}%)</p>` : ""}
                    <span class="popup-status ${statusClass}">${statusText}</span>
                </div>
            `;
            marker.setPopupContent(popupContent);
        }

        // If this station is currently selected by user, update detailed telemetry cards & trends
        if (st.station_id === selectedStationId || (!selectedStationId && st.station_id === 42475)) {
            tempValue.textContent = st.temp.toFixed(1);
            rhumValue.textContent = st.rhum.toFixed(0);
            presValue.textContent = st.pres.toFixed(0);
            stationLabel.textContent = `${st.name} (#${st.station_id})`;
            locationValue.textContent = `Location: ${st.latitude.toFixed(4)}°, ${st.longitude.toFixed(4)}°`;
            elevationValue.textContent = `Elevation: ${st.elevation.toFixed(0)} m`;
            latestTimeValue.textContent = `Timestamp: ${timestampStr}`;

            displayPrediction({
                anomaly: st.anomaly,
                anomaly_probability: st.anomaly_probability,
                threshold: 0.6,
                fault_sensor: st.fault_sensor,
                fault_type: st.fault_type,
                diagnosis_confidence: st.diagnosis_confidence
            });

            // Update real-time weatherReadings and animate sensor trend line charts dynamically
            weatherReadings.push({
                time: timestampStr,
                temp: st.temp,
                rhum: st.rhum,
                pres: st.pres
            });
            if (weatherReadings.length > 72) {
                weatherReadings.shift();
            }
            updateSensorChartsSmooth();
        }
    });

    // Handle Anomaly Hold & Auto Map Popup Linger
    let stepDelayMs = 0;
    const speed = parseFloat(replaySpeedSelect ? replaySpeedSelect.value : 5.0) || 5.0;
    const defaultDelay = Math.max(50, 1000 / speed);

    if (activeAnomalies.length > 0) {
        const primaryAnom = activeAnomalies[0];
        latestActiveAnomalyStationId = primaryAnom.station_id;
        const marker = stationMarkers[primaryAnom.station_id];

        // Auto-open Leaflet map popup on the primary anomaly station marker so operator can read immediately
        if (marker && map) {
            marker.openPopup();
        }

        // Pop open the Large Anomaly Inspection HUD Card!
        showLargeAnomalyModal(primaryAnom, timestampStr);

        // Hold view for 6 seconds (6000ms) for comfortable reading of the Large Anomaly HUD Card
        stepDelayMs = 6000;

        if (replayStatusText) {
            replayStatusText.textContent = `Telemetry Streaming • Timestamp: ${timestampStr} • Speed: ${speed}x • Active Network Anomalies: ${activeAnomalies.length}`;
        }
    } else {
        stepDelayMs = defaultDelay;
        hideLargeAnomalyModal(); // Hide large modal overlay when network returns to normal
        if (replayStatusText) {
            replayStatusText.textContent = `Telemetry Streaming • Timestamp: ${timestampStr} • Speed: ${speed}x • Active Network Anomalies: 0`;
        }
    }

    // Update progress bar
    const percent = ((networkReplayIndex / networkTimeline.length) * 100).toFixed(1);
    if (replayProgressBar) {
        replayProgressBar.style.width = `${percent}%`;
        if (activeAnomalies.length > 0) {
            replayProgressBar.classList.add("anomaly-active");
        } else {
            replayProgressBar.classList.remove("anomaly-active");
        }
    }

    // Highlight active 15-day period report button during replay
    const currentPeriodId = Math.min(6, Math.floor(networkReplayIndex / 360) + 1);
    for (let p = 1; p <= 6; p++) {
        const btn = document.getElementById(`reportBtn${p}`);
        if (btn) {
            if (p === currentPeriodId) {
                btn.classList.add("active-period");
            } else {
                btn.classList.remove("active-period");
            }
        }
    }

    networkReplayIndex++;

    if (isReplaying) {
        replayTimer = setTimeout(runNetworkReplayStep, stepDelayMs);
    }
}

function updateSensorChartsSmooth() {
    if (!temperatureChart || !humidityChart || !pressureChart) {
        createSensorCharts();
        return;
    }

    const rawTimestamps = weatherReadings.map(r => r.time || "");
    const temperatureData = weatherReadings.map(r => r.temp);
    const humidityData = weatherReadings.map(r => r.rhum);
    const pressureData = weatherReadings.map(r => r.pres);

    temperatureChart.data.labels = rawTimestamps;
    temperatureChart.data.datasets[0].data = temperatureData;
    temperatureChart.update("none");

    humidityChart.data.labels = rawTimestamps;
    humidityChart.data.datasets[0].data = humidityData;
    humidityChart.update("none");

    pressureChart.data.labels = rawTimestamps;
    pressureChart.data.datasets[0].data = pressureData;
    pressureChart.update("none");
}

function pauseReplay() {
    if (replayTimer) {
        clearInterval(replayTimer);
        clearTimeout(replayTimer);
        replayTimer = null;
    }
    isReplaying = false;
    if (replayStartBtn) replayStartBtn.disabled = false;
    if (replayPauseBtn) replayPauseBtn.disabled = true;
    if (replayStatusText && networkReplayIndex > 0) {
        replayStatusText.textContent = `National Telemetry Stream Paused at Step ${networkReplayIndex}/${networkTimeline.length}`;
    }
}

function resetReplay() {
    pauseReplay();
    networkReplayIndex = 0;
    hideLargeAnomalyModal();
    if (replayProgressBar) replayProgressBar.style.width = "0%";
    if (replayStatusText) {
        replayStatusText.textContent = "National Telemetry Reset • Press Start Live Telemetry Feed to Stream";
    }
}

