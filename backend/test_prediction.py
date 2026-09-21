import pandas as pd

from predictor import predict_station


# ============================================================
# TEST WEATHER DATA
# ============================================================

data = {
    "station_id": [1] * 15,

    "time": pd.date_range(
        "2026-01-01 00:00:00",
        periods=15,
        freq="h"
    ),

    "temp": [
        20.0, 20.2, 20.5, 20.7, 21.0,
        21.2, 21.5, 21.7, 22.0, 22.2,
        22.5, 22.7, 23.0, 23.2, 23.5
    ],

    "rhum": [
        70, 69, 68, 67, 66,
        65, 64, 63, 62, 61,
        60, 59, 58, 57, 56
    ],

    "pres": [
        1000, 1001, 1000, 1002, 1001,
        1003, 1002, 1004, 1003, 1005,
        1004, 1006, 1005, 1007, 1006
    ],

    "latitude": [25.45] * 15,
    "longitude": [81.73] * 15,
    "elevation": [97] * 15
}


df = pd.DataFrame(data)


# ============================================================
# RUN SKYGUARD
# ============================================================

print("\nPredicting with SkyGuard...")

result = predict_station(df)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n===== SKYGUARD PREDICTION =====")

for key, value in result.items():
    print(f"{key}: {value}")


print("\n===============================")
print("PREDICTION PIPELINE SUCCESSFUL")
print("===============================")