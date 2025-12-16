from __future__ import annotations

import json
from typing import Dict, Any

import numpy as np
import pandas as pd

from utils.io_helpers import project_path

"""
Data Analysis Script
--------------------
This script performs descriptive statistical analysis using NumPy and Pandas.

Tasks:
1. Load cleaned price data (prices.csv)
2. Compute global descriptive statistics using NumPy
3. Compute per-product statistics using Pandas groupby
4. Save results as JSON and CSV for reporting
"""

IN_CSV = project_path("data", "processed", "prices.csv")
RESULTS_DIR = project_path("results")
SUMMARY_JSON = RESULTS_DIR / "summary_stats.json"
METRICS_CSV = RESULTS_DIR / "metrics_by_product.csv"


def compute_global_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute descriptive statistics for book prices using NumPy."""
    prices = df["price"].dropna().values.astype(float)

    stats: Dict[str, Any] = {
        "count": int(prices.size),
        "mean": float(np.mean(prices)),
        "median": float(np.median(prices)),
        "std": float(np.std(prices, ddof=1)),
        "min": float(np.min(prices)),
        "max": float(np.max(prices)),
        "p25": float(np.percentile(prices, 25)),
        "p75": float(np.percentile(prices, 75)),
    }
    return stats


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------
    # 1. Load cleaned CSV
    # ---------------------------
    df = pd.read_csv(IN_CSV)

    if df.empty:
        print("[WARN] prices.csv is empty. Run clean_data.py first.")
        return

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])

    # ---------------------------
    # 2. Compute global stats
    # ---------------------------
    global_stats = compute_global_stats(df)
    print("[INFO] Global Price Statistics:")
    for k, v in global_stats.items():
        print(f"  {k}: {v}")

    # ---------------------------
    # 3. Per-product metrics
    # ---------------------------
    metrics = (
        df.groupby(["product_id", "name"])
        .agg(
            n_obs=("price", "count"),
            price_min=("price", "min"),
            price_max=("price", "max"),
            price_mean=("price", "mean"),
        )
        .reset_index()
    )

    # ---------------------------
    # 4. Save output
    # ---------------------------
    with SUMMARY_JSON.open("w", encoding="utf-8") as f:
        json.dump({"global_stats": global_stats}, f, indent=2)
    print(f"[OK] Saved summary -> {SUMMARY_JSON}")

    metrics.to_csv(METRICS_CSV, index=False)
    print(f"[OK] Saved per-product metrics -> {METRICS_CSV}")


if __name__ == "__main__":
    main()
