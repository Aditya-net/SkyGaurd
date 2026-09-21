from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import joblib
import json
import pandas as pd
from pydantic import BaseModel
from typing import List

from backend.predictor import predict_station
from backend.data_store import (
    get_station_history,
    get_station_summaries,
    get_network_timeline,
    get_15day_period_summary,
)
from backend.report_generator import build_15day_pdf_report

# ============================================================
# SKYGUARD BACKEND
# ============================================================

app = FastAPI(
    title="SkyGuard Weather Station Anomaly Detection API",
    description="ML backend for weather sensor anomaly detection and fault diagnosis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/network/timeline")
def get_national_network_timeline(start_date: str = "2020-01-01", months: int = 3):
    """Return precomputed 3-month continuous national network timeline across all 20 stations."""
    timeline = get_network_timeline(start_date=start_date, months=months)
    return {"total_steps": len(timeline), "timeline": timeline}


@app.get("/report/{period_id}")
def get_15day_pdf_report(period_id: int):
    """Generate and return official binary PDF report for a 15-day period (1 to 6)."""
    if period_id < 1 or period_id > 6:
        raise HTTPException(
            status_code=400,
            detail="Period ID must be between 1 and 6 for a 90-day (3-month) dataset."
        )

    summary = get_15day_period_summary(period_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"Report summary for period {period_id} was not found."
        )

    pdf_bytes = build_15day_pdf_report(summary)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="SkyGuard_15Day_Report_Period_{period_id}.pdf"'
        }
    )


@app.get("/reports/summary")
def get_reports_summary():
    """Return overview metadata of all six 15-day period reports."""
    reports = []
    for pid in range(1, 7):
        s = get_15day_period_summary(pid)
        if s:
            reports.append({
                "period_id": pid,
                "period_label": s["period_label"],
                "start_time": s["start_time"],
                "end_time": s["end_time"],
                "total_anomalies": s["total_anomalies"],
                "anomalous_stations_count": s["anomalous_stations_count"],
                "network_health_pct": s["network_health_pct"],
                "most_affected_sensor": s["most_affected_sensor"],
                "most_common_fault": s["most_common_fault"]
            })
    return {"reports": reports}



# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

# ============================================================
# LOAD MODELS
# ============================================================

print("Loading SkyGuard models...")

anomaly_model = joblib.load(
    MODEL_DIR / "anomaly_model_v3.joblib"
)

diagnosis_model = joblib.load(
    MODEL_DIR / "diagnosis_model.joblib"
)

# ============================================================
# LOAD FEATURE CONFIGURATION
# ============================================================

with open(MODEL_DIR / "v3_features.json", "r") as f:
    v3_features = json.load(f)

with open(MODEL_DIR / "diagnosis_features.json", "r") as f:
    diagnosis_features = json.load(f)

with open(MODEL_DIR / "config.json", "r") as f:
    config = json.load(f)

ANOMALY_THRESHOLD = config["anomaly_threshold"]

print("Models loaded successfully!")
print("V3 features:", len(v3_features))
print("Diagnosis features:", len(diagnosis_features))
print("Anomaly threshold:", ANOMALY_THRESHOLD)


# ============================================================
# ROOT ENDPOINT (SERVES FRONTEND DASHBOARD)
# ============================================================

@app.get("/")
def root():
    return FileResponse(BASE_DIR / "frontend" / "index.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "anomaly_model": type(anomaly_model).__name__,
        "diagnosis_model": type(diagnosis_model).__name__,
        "v3_features": len(v3_features),
        "diagnosis_features": len(diagnosis_features),
        "anomaly_threshold": ANOMALY_THRESHOLD
    }


from typing import List, Optional, Any


class WeatherReading(BaseModel):
    station_id: Optional[Any] = 0
    time: Optional[Any] = None
    temp: Optional[float] = 0.0
    rhum: Optional[float] = 0.0
    pres: Optional[float] = 0.0
    latitude: Optional[float] = 0.0
    longitude: Optional[float] = 0.0
    elevation: Optional[float] = 0.0
    name: Optional[str] = "Station"


class PredictionRequest(BaseModel):
    readings: List[WeatherReading]


@app.post("/predict")
def predict(request: PredictionRequest):

    if not request.readings:
        raise HTTPException(
            status_code=400,
            detail="At least one weather reading is required."
        )

    df = pd.DataFrame([
        reading.model_dump()
        for reading in request.readings
    ])

    for col in ["station_id", "latitude", "longitude", "elevation", "temp", "rhum", "pres"]:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = df[col].fillna(0.0)

    result = predict_station(df)

    return result



# ============================================================
# STATION REPLAY DATA
# ============================================================

def serialize_history(history: pd.DataFrame) -> list[dict]:
    """Convert station history into JSON-safe API records."""

    records = history.copy()
    records["time"] = records["time"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return records.to_dict(orient="records")


@app.get("/stations")
def get_stations():
    """Return each replay station with its current model health."""

    stations = get_station_summaries()

    for station in stations:
        station["time"] = station["time"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        history = get_station_history(
            station["station_id"],
            limit=15,
        )

        station["prediction"] = predict_station(history)

    return {"stations": stations}


@app.get("/station/{station_id}")
def get_station(station_id: int, limit: int = 72, scenario: str | None = None):
    """Return one station's recent replay history and prediction."""

    if limit < 15 or limit > 720:
        raise HTTPException(
            status_code=400,
            detail="History limit must be between 15 and 720 readings."
        )

    history = get_station_history(station_id, limit=limit, scenario=scenario)

    if history.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Station {station_id} was not found."
        )

    latest = history.iloc[-1]

    station = {
        "station_id": int(latest["station_id"]),
        "name": latest["name"],
        "latitude": float(latest["latitude"]),
        "longitude": float(latest["longitude"]),
        "elevation": float(latest["elevation"]),
    }

    return {
        "station": station,
        "history": serialize_history(history),
        "prediction": predict_station(history),
    }


# ============================================================
# WEATHER DATA ENDPOINT
# ============================================================

@app.get("/data")
def get_weather_data(station_id: int = 42475, limit: int = 72, scenario: str | None = None):
    history = get_station_history(station_id, limit=limit, scenario=scenario)
    if history.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Station {station_id} was not found."
        )
    return serialize_history(history)


# ============================================================
# STATIC FILES MOUNT (SERVES CSS/JS/ASSETS)
# ============================================================

app.mount("/", StaticFiles(directory=BASE_DIR / "frontend", html=True), name="frontend")
