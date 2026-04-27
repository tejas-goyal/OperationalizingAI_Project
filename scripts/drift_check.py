#!/usr/bin/env python3
"""
Automated drift detection using Evidently.
Compares current prediction data against training reference.
Can be run on a schedule (e.g., cron, GitHub Actions, or manually).

Usage:
    python scripts/drift_check.py --reference data/processed/features.parquet \
                                  --current data/recent/features.parquet \
                                  --output docs/evidently_drift_report.html
"""

import argparse
import json
import logging
import sys

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

FEATURE_COLS = [
    "ret_mean_10s", "ret_std_10s", "ret_abs_10s", "tick_count_10s",
    "spread_mean_10s", "trade_intensity_10s",
    "ret_mean_30s", "ret_std_30s", "ret_abs_30s", "tick_count_30s",
    "spread_mean_30s", "trade_intensity_30s",
    "ret_mean_60s", "ret_std_60s", "ret_abs_60s", "tick_count_60s",
    "spread_mean_60s", "trade_intensity_60s",
    "spread_bps", "mid_price",
]

DRIFT_THRESHOLD = 0.5


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    available = [c for c in FEATURE_COLS if c in df.columns]
    log.info("Loaded %d rows, %d features from %s", len(df), len(available), path)
    return df[available]


def run_drift_check(reference_path: str, current_path: str, output_path: str) -> dict:
    ref = load_data(reference_path)
    cur = load_data(current_path)

    report = Report([DataDriftPreset()])
    snapshot = report.run(reference_data=ref, current_data=cur)

    snapshot.save_html(output_path)
    log.info("HTML report saved to %s", output_path)

    results = snapshot.dump_dict()
    metrics = results.get("metrics", [])

    drifted_features = []
    total_features = 0

    for m in metrics:
        result = m.get("result", {})
        if "drift_by_columns" in result:
            for col_name, col_data in result["drift_by_columns"].items():
                total_features += 1
                if col_data.get("drift_detected", False):
                    drifted_features.append(col_name)

    drift_ratio = len(drifted_features) / max(total_features, 1)

    summary = {
        "total_features": total_features,
        "drifted_features": len(drifted_features),
        "drift_ratio": round(drift_ratio, 3),
        "drifted_feature_names": drifted_features,
        "alert": drift_ratio > DRIFT_THRESHOLD,
    }

    log.info("Drift ratio: %.1f%% (%d/%d features)",
             drift_ratio * 100, len(drifted_features), total_features)

    if summary["alert"]:
        log.warning("DRIFT ALERT: %.1f%% of features drifted (threshold: %.0f%%)",
                     drift_ratio * 100, DRIFT_THRESHOLD * 100)
        log.warning("Consider retraining the model or rolling back to baseline.")
    else:
        log.info("No drift alert. System operating within expected bounds.")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Run Evidently drift detection")
    parser.add_argument("--reference", required=True, help="Path to reference features parquet")
    parser.add_argument("--current", required=True, help="Path to current features parquet")
    parser.add_argument("--output", default="docs/evidently_drift_report.html", help="Output HTML path")
    parser.add_argument("--json-output", default=None, help="Optional: save summary as JSON")
    args = parser.parse_args()

    summary = run_drift_check(args.reference, args.current, args.output)

    if args.json_output:
        with open(args.json_output, "w") as f:
            json.dump(summary, f, indent=2)
        log.info("JSON summary saved to %s", args.json_output)

    if summary["alert"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
