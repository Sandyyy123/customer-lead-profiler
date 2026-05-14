"""
Customer segmentation using K-Means clustering on purchase behavior + demographics.
Reads a CRM export CSV, runs clustering, and outputs segment labels per customer.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import argparse
import json


FEATURE_COLS = [
    "order_count",
    "avg_order_value",
    "days_since_last_order",
    "email_open_rate",
    "age",
]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = set(FEATURE_COLS + ["customer_id"])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in input file: {missing}")
    return df


def preprocess(df: pd.DataFrame) -> tuple[np.ndarray, StandardScaler]:
    X = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())
    scaler = StandardScaler()
    return scaler.fit_transform(X), scaler


def find_optimal_k(X_scaled: np.ndarray, k_range: range = range(3, 8)) -> int:
    """Use silhouette score to pick the best number of clusters."""
    scores = {}
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        scores[k] = silhouette_score(X_scaled, labels)
    return max(scores, key=scores.get)


def label_segment(row: pd.Series) -> str:
    """Human-readable segment label based on cluster centroid characteristics."""
    if row["order_count"] >= 6 and row["avg_order_value"] >= 200:
        return "High-Value Loyalist"
    elif row["order_count"] >= 2 and row["days_since_last_order"] <= 90:
        return "Emerging Champion"
    elif row["order_count"] == 1:
        return "One-Time Buyer"
    elif row["days_since_last_order"] > 180:
        return "At-Risk Churner"
    else:
        return "Occasional Buyer"


def run(input_path: str, output_path: str, n_clusters: int | None = None) -> dict:
    df = load_data(input_path)
    X_scaled, _ = preprocess(df)

    k = n_clusters or find_optimal_k(X_scaled)
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    df["cluster_id"] = km.fit_predict(X_scaled)
    df["segment"] = df.apply(label_segment, axis=1)

    df.to_csv(output_path, index=False)

    summary = (
        df.groupby("segment")
        .agg(
            count=("customer_id", "count"),
            avg_orders=("order_count", "mean"),
            avg_aov=("avg_order_value", "mean"),
            avg_days_inactive=("days_since_last_order", "mean"),
        )
        .round(1)
        .to_dict(orient="index")
    )
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Segment customers from CRM export")
    parser.add_argument("--input", required=True, help="Path to customers CSV")
    parser.add_argument("--output", required=True, help="Output CSV with segment labels")
    parser.add_argument("--clusters", type=int, default=None, help="Override cluster count")
    args = parser.parse_args()
    run(args.input, args.output, args.clusters)
