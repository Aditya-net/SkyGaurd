from functools import lru_cache
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "v3_training_data.csv"

REPLAY_COLUMNS = [
    "time",
    "temp",
    "rhum",
    "pres",
    "station_id",
    "name",
    "latitude",
    "longitude",
    "elevation",
    "anomaly",
    "fault_sensor",
    "fault_type",
]


@lru_cache(maxsize=1)
def load_replay_data() -> pd.DataFrame:
    """Load the raw station data used by the dashboard replay once."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"SkyGuard replay dataset was not found: {DATA_PATH}"
        )

    df = pd.read_csv(
        DATA_PATH,
        usecols=REPLAY_COLUMNS,
        parse_dates=["time"],
    )

    missing = [
        column
        for column in REPLAY_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Replay dataset is missing required columns: {missing}"
        )

    return (
        df.sort_values(["station_id", "time"])
        .reset_index(drop=True)
    )


PRESET_SCENARIOS = {
    "pres_drift_42867": {"station_id": 42867, "start_idx": 649, "end_idx": 721},
    "temp_spike_42182": {"station_id": 42182, "start_idx": 4993, "end_idx": 5065},
    "temp_stuck_42647": {"station_id": 42647, "start_idx": 199, "end_idx": 271},
    "temp_spike_43339": {"station_id": 43339, "start_idx": 1534, "end_idx": 1606},
    "rhum_drift_42339": {"station_id": 42339, "start_idx": 5343, "end_idx": 5415},
}


def get_station_history(
    station_id: int,
    limit: int | None = None,
    scenario: str | None = None,
) -> pd.DataFrame:
    """Return one station's chronological replay history."""

    station_data = load_replay_data()

    if scenario and scenario in PRESET_SCENARIOS:
        sc_info = PRESET_SCENARIOS[scenario]
        target_st_id = sc_info["station_id"]
        st_df = station_data[station_data["station_id"] == target_st_id].sort_values("time").reset_index(drop=True)
        return st_df.iloc[sc_info["start_idx"]:sc_info["end_idx"]].copy()

    history = station_data[
        station_data["station_id"] == station_id
    ]

    if limit is not None:
        history = history.tail(limit)

    return history.copy()


def get_station_ids() -> list[int]:
    """Return the station IDs available in the replay dataset."""

    return sorted(
        load_replay_data()["station_id"]
        .drop_duplicates()
        .astype(int)
        .tolist()
    )


def get_station_summaries() -> list[dict]:
    """Return stable station metadata and each station's latest timestamp."""

    data = load_replay_data()

    latest_readings = (
        data.groupby("station_id", as_index=False)
        .tail(1)
        .sort_values("station_id")
    )

    return latest_readings[
        [
            "station_id",
            "name",
            "latitude",
            "longitude",
            "elevation",
            "time",
            "temp",
            "rhum",
            "pres",
        ]
    ].to_dict(orient="records")


@lru_cache(maxsize=1)
def get_network_timeline(start_date: str = "2020-01-01", months: int = 3) -> list[dict]:
    """Precompute 3 months of continuous hourly observations and ML status across all 20 stations."""
    from backend.feature_engine import create_v3_features
    from backend.predictor import anomaly_model, diagnosis_model, V3_FEATURES, DIAGNOSIS_FEATURES, ANOMALY_THRESHOLD

    data = load_replay_data()
    end_dt = pd.to_datetime(start_date) + pd.DateOffset(days=90)

    df_period = data[(data["time"] >= start_date) & (data["time"] <= end_dt)].sort_values(["station_id", "time"]).reset_index(drop=True)

    station_feats = []
    for st_id in df_period["station_id"].unique():
        st_df = df_period[df_period["station_id"] == st_id].reset_index(drop=True)
        if len(st_df) >= 15:
            feats = create_v3_features(st_df)
            station_feats.append(feats)

    if not station_feats:
        return []

    combined_feats = pd.concat(station_feats, ignore_index=True)

    X_v3 = combined_feats[V3_FEATURES]
    anom_probs = anomaly_model.predict_proba(X_v3)[:, 1]
    is_anom = anom_probs >= ANOMALY_THRESHOLD

    diag_preds = [""] * len(combined_feats)
    diag_confs = [0.0] * len(combined_feats)

    anom_indices = [i for i, b in enumerate(is_anom) if b]
    if anom_indices:
        X_diag = combined_feats.iloc[anom_indices][DIAGNOSIS_FEATURES]
        preds = diagnosis_model.predict(X_diag)
        confs = diagnosis_model.predict_proba(X_diag).max(axis=1)
        for k, idx_val in enumerate(anom_indices):
            diag_preds[idx_val] = preds[k]
            diag_confs[idx_val] = float(confs[k])

    combined_feats["anomaly"] = is_anom
    combined_feats["anomaly_probability"] = anom_probs
    combined_feats["diag_pred"] = diag_preds
    combined_feats["diagnosis_confidence"] = diag_confs
    combined_feats["time_str"] = combined_feats["time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    timeline = []
    for t_str, group in combined_feats.groupby("time_str"):
        st_list = []
        for _, row in group.iterrows():
            fs, ft = None, None
            if row["anomaly"] and row["diag_pred"]:
                parts = row["diag_pred"].split("_", 1)
                fs, ft = parts[0].upper(), parts[1].upper()

            st_list.append({
                "station_id": int(row["station_id"]),
                "name": str(row["name"]),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "elevation": float(row["elevation"]),
                "temp": float(row["temp"]),
                "rhum": float(row["rhum"]),
                "pres": float(row["pres"]),
                "anomaly": bool(row["anomaly"]),
                "anomaly_probability": float(round(row["anomaly_probability"], 4)),
                "fault_sensor": fs,
                "fault_type": ft,
                "diagnosis_confidence": float(round(row["diagnosis_confidence"], 4)) if row["diagnosis_confidence"] else None
            })

        timeline.append({
            "timestamp": t_str,
            "stations": st_list
        })

    return timeline


@lru_cache(maxsize=12)
def get_15day_period_summary(period_id: int) -> dict:
    """Calculate comprehensive 15-day period analytical summary for PDF report generation."""
    timeline = get_network_timeline(start_date="2020-01-01", months=3)
    
    # 90 days total divided into 6 periods of 15 days (360 hours per period)
    period_hours = 360
    start_idx = (period_id - 1) * period_hours
    end_idx = min(len(timeline), start_idx + period_hours)
    
    period_timesteps = timeline[start_idx:end_idx]
    if not period_timesteps:
        return {}

    start_time = period_timesteps[0]["timestamp"]
    end_time = period_timesteps[-1]["timestamp"]

    total_readings = 0
    anom_count = 0
    sensor_counts = {"TEMP": 0, "RHUM": 0, "PRES": 0}
    type_counts = {"DRIFT": 0, "SPIKE": 0, "STUCK": 0}

    station_stats = {}
    anom_logs = []

    for step in period_timesteps:
        ts = step["timestamp"]
        for st in step["stations"]:
            st_id = st["station_id"]
            if st_id not in station_stats:
                station_stats[st_id] = {
                    "station_id": st_id,
                    "name": st["name"],
                    "latitude": st["latitude"],
                    "longitude": st["longitude"],
                    "elevation": st["elevation"],
                    "readings_count": 0,
                    "anomaly_count": 0,
                    "temps": [],
                    "rhums": [],
                    "press": [],
                    "fault_sensors": set(),
                    "fault_types": set(),
                    "max_prob": 0.0,
                    "max_conf": 0.0
                }

            s_item = station_stats[st_id]
            s_item["readings_count"] += 1
            s_item["temps"].append(st["temp"])
            s_item["rhums"].append(st["rhum"])
            s_item["press"].append(st["pres"])
            total_readings += 1

            if st["anomaly"]:
                anom_count += 1
                s_item["anomaly_count"] += 1
                fs = st["fault_sensor"] or "UNKNOWN"
                ft = st["fault_type"] or "UNKNOWN"

                if fs in sensor_counts:
                    sensor_counts[fs] += 1
                if ft in type_counts:
                    type_counts[ft] += 1

                s_item["fault_sensors"].add(fs)
                s_item["fault_types"].add(ft)
                if st["anomaly_probability"] > s_item["max_prob"]:
                    s_item["max_prob"] = st["anomaly_probability"]
                if st["diagnosis_confidence"] and st["diagnosis_confidence"] > s_item["max_conf"]:
                    s_item["max_conf"] = st["diagnosis_confidence"]

                anom_logs.append({
                    "timestamp": ts,
                    "station_id": st_id,
                    "name": st["name"],
                    "fault_sensor": fs,
                    "fault_type": ft,
                    "probability": round(st["anomaly_probability"] * 100, 1),
                    "confidence": round(st["diagnosis_confidence"] * 100, 1) if st["diagnosis_confidence"] else 0.0
                })

    station_list = []
    anomalous_st_count = 0

    for st_id, s in station_stats.items():
        if s["anomaly_count"] > 0:
            anomalous_st_count += 1

        avg_temp = round(sum(s["temps"]) / len(s["temps"]), 1) if s["temps"] else 0.0
        avg_rhum = round(sum(s["rhums"]) / len(s["rhums"]), 1) if s["rhums"] else 0.0
        avg_pres = round(sum(s["press"]) / len(s["press"]), 1) if s["press"] else 0.0

        station_list.append({
            "station_id": st_id,
            "name": s["name"],
            "location": f"{s['latitude']:.2f}°, {s['longitude']:.2f}°",
            "elevation": f"{s['elevation']:.0f} m",
            "readings_count": s["readings_count"],
            "anomaly_count": s["anomaly_count"],
            "avg_temp": avg_temp,
            "avg_rhum": avg_rhum,
            "avg_pres": avg_pres,
            "fault_sensors": ", ".join(sorted(s["fault_sensors"])) if s["fault_sensors"] else "None",
            "fault_types": ", ".join(sorted(s["fault_types"])) if s["fault_types"] else "None",
            "max_prob": round(s["max_prob"] * 100, 1),
            "max_conf": round(s["max_conf"] * 100, 1)
        })

    most_affected_sensor = max(sensor_counts, key=sensor_counts.get) if any(sensor_counts.values()) else "None"
    most_common_fault = max(type_counts, key=type_counts.get) if any(type_counts.values()) else "None"

    normal_st_count = len(station_stats) - anomalous_st_count
    network_health_pct = round(((total_readings - anom_count) / total_readings) * 100, 1) if total_readings else 100.0

    return {
        "period_id": period_id,
        "period_label": f"Days {(period_id - 1) * 15 + 1}–{period_id * 15}",
        "start_time": start_time,
        "end_time": end_time,
        "total_stations": len(station_stats),
        "normal_stations_count": normal_st_count,
        "anomalous_stations_count": anomalous_st_count,
        "total_readings": total_readings,
        "total_anomalies": anom_count,
        "network_health_pct": network_health_pct,
        "most_affected_sensor": most_affected_sensor,
        "most_common_fault": most_common_fault,
        "sensor_counts": sensor_counts,
        "type_counts": type_counts,
        "stations": sorted(station_list, key=lambda x: x["station_id"]),
        "anomaly_logs": sorted(anom_logs, key=lambda x: x["timestamp"])[:50]  # top 50 logs for report
    }

