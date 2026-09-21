# SkyGuard Presentation & Technical Approach Guide (`README2.md`)

This guide provides slide-by-slide content, technical explanations, diagrams, and key talking points for presenting the **SkyGuard Technical Approach** in pitch decks, slide presentations, and technical reviews.

---

## 📽️ Slide 1: Technical System Overview

### **SkyGuard – AI-Powered Weather Station Anomaly Detection & Sensor Fault Diagnosis**

* **Mission**: Ensure real-time reliability, sensor fault identification, and automated diagnostic reporting for national automated weather station (AWS) networks.
* **Core Capabilities**:
  * Real-time ingestion of multi-sensor telemetry (Temperature, Humidity, Pressure).
  * 42-feature rolling-window machine learning pipeline.
  * Dual-stage ML model architecture (Anomaly Detection + Fault Diagnosis).
  * Interactive Command Center UI overlaying official Survey of India cartography.
  * Automated 15-day period PDF report generation.

---

## 🏗️ Slide 2: End-to-End System Architecture

### **Data Processing & ML Pipeline Flow**

```
 ┌─────────────────────────────────────────────────────────┐
 │            20-Station Telemetry Ingestion               │
 │  (Hourly Temperature, Relative Humidity, Pressure Data)  │
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼
 ┌─────────────────────────────────────────────────────────┐
 │            42-Feature Rolling Window Engine             │
 │   • 6h / 24h Rolling Means & Standard Deviations        │
 │   • 1h First-Order Rate of Change (Derivatives)        │
 │   • Inter-Sensor Physical Correlation Metrics           │
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼
 ┌─────────────────────────────────────────────────────────┐
 │               Dual ML Pipeline Engine                   │
 │ 1. Binary Anomaly Detector (RandomForest/XGB Ensemble)  │
 │    └── Anomaly Probability P >= 0.60 Threshold          │
 │ 2. Multi-Class Fault Diagnoser                           │
 │    └── Fault Sensor (TEMP/RHUM/PRES) & Type (SPIKE/STUCK)│
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼
 ┌────────────────────────────┴────────────────────────────┐
 │                  FastAPI REST Service                   │
 │  GET /network/timeline | POST /predict | GET /report/{id}│
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼
 ┌─────────────────────────────────────────────────────────┐
 │       National Command Center Frontend Dashboard       │
 │   • Official Survey of India Leaflet Map                │
 │   • 60fps Dynamic Telemetry Streaming Loop              │
 │   • Large Anomaly Live Inspection HUD Drawer            │
 │   • Automated 15-Day Period PDF Reports (ReportLab)     │
 └─────────────────────────────────────────────────────────┘
```

---

## 📊 Slide 3: Feature Engineering Strategy (42 Features)

### **Transforming Raw Telemetry into Predictive ML Signals**

To detect subtle sensor drifts, stuck values, and unphysical spikes, raw telemetry is transformed into **42 engineered features**:

1. **Temporal Rolling Statistics**:
   * `roll_mean_6h`, `roll_mean_24h`: Captures short-term and daily baseline trends.
   * `roll_std_6h`, `roll_std_24h`: Quantifies noise variance and sudden variance drops (indicating stuck sensors).
2. **First-Order Rate of Change (Derivatives)**:
   * `temp_diff_1h`, `rhum_diff_1h`, `pres_diff_1h`: Measures hourly rate of change to isolate unphysical sensor spikes.
3. **Cross-Sensor Physical Dynamics**:
   * Evaluates expected atmospheric physics (e.g., inverse relationship between temperature spikes and relative humidity drops).
4. **Spatial Network Deviation**:
   * Compares individual station metrics against regional network medians to eliminate widespread weather events (e.g., storms vs single-sensor faults).

---

## 🧠 Slide 4: Dual-Stage Machine Learning Pipeline

### **Stage 1: Binary Anomaly Detection Model**
* **Model**: Trained Ensemble (`anomaly_model_v3.joblib`).
* **Output**: Anomaly Probability Score $P \in [0.0, 1.0]$.
* **Decision Boundary**: $P \ge 0.60 \implies \text{ANOMALY DETECTED}$.

### **Stage 2: Multi-Class Sensor Fault Diagnosis Model**
* **Model**: Multi-Class Diagnostic Classifier (`diagnosis_model.joblib`).
* **Fault Channel Localization**:
  * `TEMP_SENSOR` | `RHUM_SENSOR` | `PRES_SENSOR`
* **Fault Type Classification**:
  * ⚡ `SPIKE`: Instantaneous unphysical value jump.
  * 🔒 `STUCK`: Zero variance / frozen sensor reading over time.
  * 📉 `DRIFT`: Gradual calibration decay over 24–72 hours.
  * 🚫 `OUT_OF_BOUNDS`: Value exceeding physical meteorological boundaries.
* **Output**: Diagnosis Confidence Score (%) & Fault Mode Summary.

---

## 🗺️ Slide 5: GIS & National Command Center UI/UX

### **Real-Time Interactive Operator Dashboard**

* **Official Cartography**: Integrated Official Survey of India GeoJSON boundaries (correctly rendering J&K, Ladakh, and Arunachal Pradesh).
* **Live Telemetry Stream Loop**: Replays 2,160+ hourly steps across all 20 stations simultaneously using a dynamic `setTimeout` event loop with 1x to 50x speed controls.
* **Matte Charcoal Color Palette**: Designed for dark control room environments:
  * Matte Charcoal Panels (`#101216`, `#181b22`)
  * Solar Amber Accent (`#f59e0b` / `#fbbf24`)
  * Mineral Emerald (`#10b981` Normal)
  * Terracotta Rose (`#f43f5e` Anomaly)
* **Large Anomaly Inspection HUD Modal**: Pops up automatically on anomaly detection, pausing/lingering the feed for 6 seconds to give operators full visibility of fault details.

---

## 📄 Slide 6: Automated PDF Reporting Engine

### **Enterprise 15-Day Period Analysis Reports**

* **Technology**: Python ReportLab PDF Generation Library.
* **Functionality**:
  * Automatically aggregates telemetry data into 6 distinct 15-day observation periods across 90 days.
  * Computes period statistical metrics (Max/Min/Mean Temp, Humidity, Pressure).
  * Logs all detected sensor anomalies, root cause diagnosis, and duration.
  * Provides actionable maintenance recommendations for field engineers.
* **Access**: Available for one-click streaming download via `/report/{period_id}`.

---

## 🚀 Slide 7: Technical Highlights & Impact Summary

### **Why SkyGuard Stands Out**

1. **High Precision & Low False Positives**: 42-feature engineering isolates genuine hardware faults from severe weather events.
2. **Instant Root Cause Localization**: Pinpoints exact sensor channel (`TEMP`, `RHUM`, `PRES`) and fault mode (`SPIKE`, `STUCK`, `DRIFT`).
3. **Zero-Lag Telemetry Replay**: Dynamic 60fps streaming of 20 national stations over 2,160 hourly timesteps.
4. **Cartographic Integrity**: Fully compliant with Official Survey of India territorial borders.
5. **Production-Ready Architecture**: Decoupled FastAPI backend and lightweight vanilla JavaScript/CSS frontend.
