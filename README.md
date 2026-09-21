# SkyGuard – Weather Station Anomaly Detection System

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Leaflet](https://img.shields.io/badge/Map-Leaflet.js-199900?style=for-the-badge&logo=leaflet&logoColor=white)

**SkyGuard** is an advanced AI-powered National Weather Station Monitoring & Sensor Anomaly Detection System. Built with FastAPI and Scikit-Learn, SkyGuard ingests real-time weather telemetry (Temperature, Relative Humidity, Barometric Pressure) across 20 stations in India, predicts sensor anomalies in real-time, diagnoses specific hardware fault modes (e.g., Temperature Spike, Stuck Humidity Sensor, Pressure Drift), and generates automated PDF analysis reports.

---

## Key Features

- **🤖 AI-Powered Anomaly Detection & Fault Diagnosis**: Uses trained Machine Learning models (`joblib` feature ensembles) with 42 engineered rolling-window telemetry features to predict anomaly probabilities and diagnose fault modes.
- **🗺️ Official Survey of India Leaflet Map**: Interactive Leaflet map rendering all 20 active weather stations across India overlaying official Survey of India boundary GeoJSON polygons (including full Jammu & Kashmir, Ladakh, and Arunachal Pradesh).
- **📡 National Command Center Live Telemetry Stream**: Continuous live telemetry streaming across a 3-month (2,160+ hourly steps) dataset for all 20 stations simultaneously with adjustable replay speeds (1x to 50x).
- **🚨 Large Anomaly Live Inspection HUD Modal**: High-visibility real-time inspection drawer popping up upon anomaly detection, displaying station metadata, fault sensor, fault type, anomaly risk %, and diagnosis confidence.
- **📈 60fps Real-Time Sensor Trend Charts**: Dynamic Chart.js line charts tracking Temperature, Humidity, and Pressure trends over 72-hour sliding windows.
- **📄 Automated 15-Day Period PDF Reports**: Built-in ReportLab PDF generator providing automated 15-day period network analysis reports available for direct download.
- **📍 Geolocation Auto-Station Selection**: Automatically calculates distance from the operator's GPS location to recommend and select the nearest weather station on load.

---

## Directory Structure

```text
SkyGuard/
├── backend/
│   ├── app.py                  # FastAPI server, static file router & API endpoints
│   ├── data_store.py           # 3-Month telemetry dataset engine & period aggregations
│   ├── feature_engine.py       # 42-Feature rolling-window engineering processor
│   ├── predictor.py            # ML Anomaly Detection & Inverted Fault Diagnosis pipeline
│   └── report_generator.py     # ReportLab PDF report builder (15-Day period analysis)
├── frontend/
│   ├── index.html              # Main dashboard UI structure
│   ├── style.css               # Humanized Matte Charcoal design system & tokens
│   ├── script.js               # Leaflet map, telemetry stream loop & Chart.js engine
│   └── india_boundary.geojson  # Official Survey of India boundary GeoJSON layer
├── models/
│   ├── anomaly_model_v3.joblib # Trained ML Anomaly Detection model
│   ├── diagnosis_model.joblib  # Trained ML Fault Diagnosis model
│   ├── v3_features.json        # Anomaly detection feature schema
│   └── diagnosis_features.json # Fault diagnosis feature schema
├── data/                       # Telemetry data storage
└── README.md                   # Project documentation
```

---

## Architecture & Data Flow

1. **Telemetry Feed & Storage** (`data_store.py`): Serves 3 months (2,160+ timesteps) of 20-station telemetry data (Temperature, Humidity, Pressure).
2. **Feature Engineering** (`feature_engine.py`): Generates 42 rolling features including short/long rolling averages (`roll_mean_6h`, `roll_mean_24h`), standard deviations (`roll_std_6h`), rate of change (`temp_diff_1h`), and inter-sensor correlations.
3. **ML Prediction Engine** (`predictor.py`):
   - Computes **Anomaly Probability** ($P \ge 0.60 \implies \text{Anomaly Detected}$).
   - Predicts **Fault Sensor** (`TEMP_SENSOR`, `RHUM_SENSOR`, `PRES_SENSOR`).
   - Predicts **Fault Type** (`SPIKE`, `STUCK`, `DRIFT`, `OUT_OF_BOUNDS`).
   - Computes **Diagnosis Confidence Score**.
4. **Live Stream Engine** (`script.js`): Streams 20-station network updates to Leaflet map pins, dynamic Chart.js trends, and triggers the Large Anomaly HUD Card.

---

## Installation & Setup

### Prerequisites
- **Python**: Version 3.10 or higher
- **Web Browser**: Modern browser (Chrome, Firefox, Edge, Safari)

### 1. Clone & Navigate to Project Directory
```bash
git clone https://github.com/your-username/SkyGuard.git
cd SkyGuard
```

### 2. Create & Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn joblib scikit-learn pandas numpy reportlab requests
```

---

## Running the Application

Start the FastAPI backend server on `http://127.0.0.1:8000`:

```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Once started, open your web browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves root frontend dashboard (`index.html`) |
| `GET` | `/data` | Fetches latest 72 telemetry readings for selected station |
| `GET` | `/stations` | Returns list of all 20 weather stations across India |
| `GET` | `/station/{station_id}` | Station metadata & telemetry history for given station ID |
| `GET` | `/network/timeline` | Serves precomputed 3-month network telemetry timeline (2,160+ timesteps) |
| `POST` | `/predict` | Ingests sensor data payload and returns ML anomaly status & diagnosis |
| `GET` | `/report/{period_id}` | Generates and downloads PDF Analysis Report for period `1` to `6` (15 days each) |
| `GET` | `/reports/summary` | Returns summary metadata for all 6 15-day report periods |

---

## Technologies Used

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Scikit-Learn, Joblib, Pandas, NumPy, ReportLab
- **Frontend**: HTML5, Vanilla CSS3 (Matte Charcoal Design System), JavaScript (ES6+ Async/Await)
- **Mapping**: Leaflet.js, Esri Dark Canvas, Official Survey of India GeoJSON
- **Visualization**: Chart.js (Real-time dynamic line charts)

---

## License

This project is developed for Weather Station Monitoring & Anomaly Detection System requirements. All rights reserved.
