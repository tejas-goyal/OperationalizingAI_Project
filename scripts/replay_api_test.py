#!/usr/bin/env python3
"""
Replay saved feature rows through the /predict API.
Falls back to synthetic data if parquet file is not found.

Usage:
    python scripts/replay_api_test.py --parquet data/processed/features.parquet --n 50
    python scripts/replay_api_test.py --n 50   # uses synthetic data
"""

import argparse
import os
import random
import time
import statistics

import httpx

FEATURE_COLS = [
    "ret_mean_10s",
    "ret_std_10s",
    "ret_abs_10s",
    "tick_count_10s",
    "spread_mean_10s",
    "trade_intensity_10s",
    "ret_mean_30s",
    "ret_std_30s",
    "ret_abs_30s",
    "tick_count_30s",
    "spread_mean_30s",
    "trade_intensity_30s",
    "ret_mean_60s",
    "ret_std_60s",
    "ret_abs_60s",
    "tick_count_60s",
    "spread_mean_60s",
    "trade_intensity_60s",
    "spread_bps",
    "mid_price",
]


def generate_synthetic_row():
    """Generate a single synthetic feature row with realistic ranges."""
    return {
        "ret_mean_10s": random.gauss(0, 0.00001),
        "ret_std_10s": abs(random.gauss(0.000015, 0.000005)),
        "ret_abs_10s": abs(random.gauss(0.00001, 0.000003)),
        "tick_count_10s": random.randint(10, 50),
        "spread_mean_10s": abs(random.gauss(0.000002, 0.000001)),
        "trade_intensity_10s": random.uniform(1.0, 5.0),
        "ret_mean_30s": random.gauss(0, 0.000008),
        "ret_std_30s": abs(random.gauss(0.000018, 0.000006)),
        "ret_abs_30s": abs(random.gauss(0.000012, 0.000004)),
        "tick_count_30s": random.randint(20, 80),
        "spread_mean_30s": abs(random.gauss(0.000002, 0.000001)),
        "trade_intensity_30s": random.uniform(1.5, 4.0),
        "ret_mean_60s": random.gauss(0, 0.000006),
        "ret_std_60s": abs(random.gauss(0.000022, 0.000008)),
        "ret_abs_60s": abs(random.gauss(0.000014, 0.000005)),
        "tick_count_60s": random.randint(30, 120),
        "spread_mean_60s": abs(random.gauss(0.000002, 0.000001)),
        "trade_intensity_60s": random.uniform(1.0, 3.5),
        "spread_bps": random.uniform(0.02, 0.10),
        "mid_price": random.uniform(60000, 75000),
    }


def load_rows_from_parquet(path, n):
    """Load feature rows from parquet. Returns list of dicts."""
    import pandas as pd

    df = pd.read_parquet(path)
    df = df.head(n)

    feat_cols = [
        c
        for c in df.columns
        if c not in ["ts", "product_id", "label", "future_vol"]
        and df[c].dtype in ["float64", "float32", "int64", "int32"]
    ]

    rows = []
    for _, row in df.iterrows():
        features = {col: float(row[col]) for col in feat_cols}
        features["product_id"] = str(row.get("product_id", "BTC-USD"))
        rows.append(features)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", default=None)
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--n", type=int, default=50, help="Number of rows to replay")
    args = parser.parse_args()

    if args.parquet and os.path.exists(args.parquet):
        print(f"Loading {args.n} rows from {args.parquet} ...")
        rows = load_rows_from_parquet(args.parquet, args.n)
    else:
        if args.parquet:
            print(f"Parquet not found at {args.parquet}, using synthetic data.")
        else:
            print("No parquet specified, using synthetic data.")
        rows = [generate_synthetic_row() for _ in range(args.n)]

    latencies = []
    spikes = 0
    errors = 0

    print(f"Replaying {len(rows)} rows through {args.url}/predict ...")

    with httpx.Client() as client:
        for i, features in enumerate(rows):
            payload = {"rows": [features]}
            t0 = time.time()
            try:
                r = client.post(f"{args.url}/predict", json=payload, timeout=5.0)
                latencies.append((time.time() - t0) * 1000)
                if r.status_code == 200:
                    data = r.json()
                    for score in data.get("scores", []):
                        if score >= 0.00138:
                            spikes += 1
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                print(f"Row {i} failed: {e}")

    print("\n=== Replay Test Results ===")
    print(f"Rows replayed:   {len(rows)}")
    print(f"Successful:      {len(latencies)}")
    print(f"Errors:          {errors}")
    print(
        f"Spikes detected: {spikes}/{len(latencies)} "
        f"({100 * spikes / max(len(latencies), 1):.1f}%)"
    )
    if latencies:
        print(f"Avg latency:     {statistics.mean(latencies):.1f}ms")
        print(
            f"p95 latency:     "
            f"{sorted(latencies)[int(len(latencies) * 0.95)]:.1f}ms"
        )


if __name__ == "__main__":
    main()
