import joblib
import json
import pandas as pd

from pathlib import Path

from backend.feature_engine import create_v3_features

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"


# ============================================================
# LOAD MODELS
# ============================================================

anomaly_model = joblib.load(
    MODEL_DIR / "anomaly_model_v3.joblib"
)

diagnosis_model = joblib.load(
    MODEL_DIR / "diagnosis_model.joblib"
)


# ============================================================
# LOAD CONFIG
# ============================================================

with open(MODEL_DIR / "v3_features.json", "r") as f:
    V3_FEATURES = json.load(f)

with open(MODEL_DIR / "diagnosis_features.json", "r") as f:
    DIAGNOSIS_FEATURES = json.load(f)

with open(MODEL_DIR / "config.json", "r") as f:
    CONFIG = json.load(f)


ANOMALY_THRESHOLD = CONFIG["anomaly_threshold"]


# ============================================================
# ANOMALY + DIAGNOSIS PREDICTION
# ============================================================

def predict_station(df: pd.DataFrame):

    # --------------------------------------------------------
    # Generate exact V3 features
    # --------------------------------------------------------

    feature_df = create_v3_features(df)

    # --------------------------------------------------------
    # Take latest station observation
    # --------------------------------------------------------

    latest = feature_df.iloc[-1]

    X_v3 = pd.DataFrame(
        [latest[V3_FEATURES].values],
        columns=V3_FEATURES
    )

    # --------------------------------------------------------
    # Anomaly probability
    # --------------------------------------------------------

    anomaly_probability = anomaly_model.predict_proba(
        X_v3
    )[0][1]

    # --------------------------------------------------------
    # Apply V3 threshold
    # --------------------------------------------------------

    is_anomaly = (
        anomaly_probability >= ANOMALY_THRESHOLD
    )

    result = {
        "anomaly": bool(is_anomaly),
        "anomaly_probability": float(anomaly_probability),
        "threshold": float(ANOMALY_THRESHOLD)
    }

    # --------------------------------------------------------
    # If normal, stop here
    # --------------------------------------------------------

    if not is_anomaly:

        result.update({
            "fault_sensor": None,
            "fault_type": None,
            "diagnosis_confidence": None
        })

        return result

    # ========================================================
    # DIAGNOSIS
    # ========================================================

    # Diagnosis model expects the same 42-feature structure
    X_diag = X_v3[DIAGNOSIS_FEATURES]

    diagnosis_prediction = diagnosis_model.predict(
        X_diag
    )[0]

    diagnosis_probabilities = (
        diagnosis_model.predict_proba(X_diag)[0]
    )

    diagnosis_confidence = float(
        diagnosis_probabilities.max()
    )

    # --------------------------------------------------------
    # Split class:
    # temp_spike -> temp + spike
    # --------------------------------------------------------

    fault_sensor, fault_type = (
        diagnosis_prediction.split("_", 1)
    )

    result.update({
        "fault_sensor": fault_sensor,
        "fault_type": fault_type,
        "diagnosis_confidence": diagnosis_confidence,
        "diagnosis_class": diagnosis_prediction
    })

    return result