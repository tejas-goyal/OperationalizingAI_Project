#!/usr/bin/env python3
"""
Replay saved feature rows through the /predict API.
Validates that the API handles real feature distributions correctly.
"""
import argparse
import time
import statistics

import httpx
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", default="data/processed/features.parquet")
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--n", type=int, default=50, help="Number of rows to replay")
    args = parser.parse_args()

    df = pd.read_parquet(args.parquet)
    df = df.head(args.n)

    feat_cols = [
        c for c in df.columns
        if c not in ["ts", "product_id", "label", "future_vol"]
        and df[c].dtype in ["float64", "float32", "int64", "int32"]
    ]

    latencies = []
    spikes = 0
    errors = 0

    print(f"Replaying {len(df)} rows through {args.url}/predict ...")

    with httpx.Client() as client:
        for idx, row in df.iterrows():
            features = {col: float(row[col]) for col in feat_cols}
            features["product_id"] = str(row.get("product_id", "BTC-USD"))

            t0 = time.time()
            try:
                r = client.post(f"{args.url}/predict", json={"features": features}, timeout=5.0)
                latencies.append((time.time() - t0) * 1000)
                if r.status_code == 200:
                    data = r.json()
                    if data.get("spike_predicted"):
                        spikes += 1
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                print(f"Row {idx} failed: {e}")

    print(f"\n=== Replay Test Results ===")
    print(f"Rows replayed:   {len(df)}")
    print(f"Successful:      {len(latencies)}")
    print(f"Errors:          {errors}")
    print(f"Spikes detected: {spikes}/{len(latencies)} ({100*spikes/max(len(latencies),1):.1f}%)")
    if latencies:
        print(f"Avg latency:     {statistics.mean(latencies):.1f}ms")
        print(f"p95 latency:     {sorted(latencies)[int(len(latencies)*0.95)]:.1f}ms")


if __name__ == "__main__":
    main()
