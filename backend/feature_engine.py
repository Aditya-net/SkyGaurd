import pandas as pd
import json
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"


# ============================================================
# LOAD EXACT V3 FEATURE ORDER
# ============================================================

with open(MODEL_DIR / "v3_features.json", "r") as f:
    FEATURE_COLUMNS_V3 = json.load(f)


# ============================================================
# CREATE V3 FEATURES
# ============================================================

def create_v3_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = [
        "station_id",
        "time",
        "temp",
        "rhum",
        "pres",
        "latitude",
        "longitude",
        "elevation"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # --------------------------------------------------------
    # Convert time and sort exactly like training
    # --------------------------------------------------------

    df["time"] = pd.to_datetime(df["time"])

    df = (
        df.sort_values(
            ["station_id", "time"]
        )
        .reset_index(drop=True)
    )

    sensors = ["temp", "rhum", "pres"]

    # ========================================================
    # 1. PREVIOUS VALUES
    # ========================================================

    for sensor in sensors:

        df[f"{sensor}_prev"] = (
            df.groupby("station_id")[sensor]
            .shift(1)
        )

    # ========================================================
    # 2. CHANGE FROM PREVIOUS OBSERVATION
    # ========================================================

    for sensor in sensors:

        df[f"{sensor}_change"] = (
            df[sensor]
            - df[f"{sensor}_prev"]
        )

    # ========================================================
    # 3. 6-HOUR ROLLING MEAN
    # ========================================================

    for sensor in sensors:

        df[f"{sensor}_rolling_mean"] = (
            df.groupby("station_id")[sensor]
            .transform(
                lambda x:
                x.rolling(
                    6,
                    min_periods=1
                ).mean()
            )
        )

    # ========================================================
    # 4. 6-HOUR ROLLING STANDARD DEVIATION
    # ========================================================

    for sensor in sensors:

        df[f"{sensor}_rolling_std"] = (
            df.groupby("station_id")[sensor]
            .transform(
                lambda x:
                x.rolling(
                    window=6,
                    min_periods=3
                ).std()
            )
        )

    # ========================================================
    # 5. CONSECUTIVE IDENTICAL READINGS
    # ========================================================

    for sensor in sensors:

        previous = (
            df.groupby("station_id")[sensor]
            .shift(1)
        )

        same = (
            df[sensor]
            .eq(previous)
            .fillna(False)
        )

        group_id = (
            (~same)
            .groupby(df["station_id"])
            .cumsum()
        )

        df[f"{sensor}_same_count"] = (
            same.astype(int)
            .groupby(
                [df["station_id"], group_id]
            )
            .cumsum()
        )

    # Match training behavior
    std_columns = [
        "temp_rolling_std",
        "rhum_rolling_std",
        "pres_rolling_std"
    ]

    df[std_columns] = (
        df[std_columns]
        .fillna(0)
    )

    # ========================================================
    # 6. V3 TEMPORAL FEATURES
    # ========================================================

    for sensor in sensors:

        # 3-hour change
        df[f"{sensor}_change_3h"] = (
            df.groupby("station_id")[sensor]
            .diff(3)
        )

        # 6-hour change
        df[f"{sensor}_change_6h"] = (
            df.groupby("station_id")[sensor]
            .diff(6)
        )

        # 12-hour change
        df[f"{sensor}_change_12h"] = (
            df.groupby("station_id")[sensor]
            .diff(12)
        )

        # 6-hour standard deviation
        df[f"{sensor}_std_6h"] = (
            df.groupby("station_id")[sensor]
            .transform(
                lambda x:
                x.rolling(
                    6,
                    min_periods=2
                ).std()
            )
        )

        # 12-hour standard deviation
        df[f"{sensor}_std_12h"] = (
            df.groupby("station_id")[sensor]
            .transform(
                lambda x:
                x.rolling(
                    12,
                    min_periods=2
                ).std()
            )
        )

        # 6-hour range
        df[f"{sensor}_range_6h"] = (
            df.groupby("station_id")[sensor]
            .transform(
                lambda x:
                x.rolling(
                    6,
                    min_periods=2
                ).max()
                -
                x.rolling(
                    6,
                    min_periods=2
                ).min()
            )
        )

        # 6-hour unique values
        df[f"{sensor}_unique_6h"] = (
            df.groupby("station_id")[sensor]
            .transform(
                lambda x:
                x.rolling(
                    6,
                    min_periods=2
                ).apply(
                    lambda y: y.nunique()
                )
            )
        )

    # ========================================================
    # 7. KEEP EXACT MODEL FEATURES
    # ========================================================

    missing_features = [
        col
        for col in FEATURE_COLUMNS_V3
        if col not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"V3 feature generation failed. "
            f"Missing: {missing_features}"
        )

    return df