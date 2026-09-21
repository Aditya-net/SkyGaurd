import pandas as pd

from feature_engine import (
    create_v3_features,
    FEATURE_COLUMNS_V3
)


# ============================================================
# TEST DATA
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
# CREATE FEATURES
# ============================================================

result = create_v3_features(df)


# ============================================================
# TEST 1 — FEATURE COUNT
# ============================================================

print("\n===== TEST 1: FEATURE COUNT =====")

print("Expected:", 42)
print("Generated:", len(FEATURE_COLUMNS_V3))

assert len(FEATURE_COLUMNS_V3) == 42

print("PASS")


# ============================================================
# TEST 2 — FEATURE COLUMNS
# ============================================================

print("\n===== TEST 2: FEATURE COLUMNS =====")

missing = [
    col for col in FEATURE_COLUMNS_V3
    if col not in result.columns
]

print("Missing features:", missing)

assert len(missing) == 0

print("PASS")


# ============================================================
# TEST 3 — LATEST ROW
# ============================================================

print("\n===== TEST 3: LATEST ROW =====")

latest = result.iloc[-1]

print(latest[FEATURE_COLUMNS_V3])

print("\nPASS")


# ============================================================
# TEST 4 — DATA SHAPE
# ============================================================

print("\n===== TEST 4: DATA SHAPE =====")

print("Rows:", len(result))
print("Columns:", len(result.columns))

assert len(result.columns) >= 42

print("PASS")


print("\n================================")
print("ALL FEATURE ENGINE TESTS PASSED")
print("================================")