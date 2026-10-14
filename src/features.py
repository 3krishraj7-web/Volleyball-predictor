import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from src.data_loader import load_matches


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_OUTPUT = os.path.join(ROOT_DIR, "data", "processed", "features.csv")


def build_features(df: pd.DataFrame = None, output_path: str = DEFAULT_OUTPUT) -> pd.DataFrame:
    if df is None:
        df = load_matches()

    features_df = df.copy()

    drop_meta = [c for c in ["S", "Year"] if c in features_df.columns]
    if drop_meta:
        features_df = features_df.drop(columns=drop_meta)

    if "Date" in features_df.columns:
        features_df = features_df.sort_values(by="Date").reset_index(drop=True)

    metrics = [
        "Kills", "Errors", "Total Attacks", "Hit Pct", "Assists",
        "Aces", "SErr", "Digs", "RErr", "Block Solos", "Block Assists",
        "BErr", "PTS"
    ]

    for metric in metrics:
        col_a = f"Team A {metric}"
        col_b = f"Team B {metric}"
        if col_a in features_df.columns and col_b in features_df.columns:
            diff_col = f"diff_{metric.lower().replace(' ', '_')}"
            features_df[diff_col] = features_df[col_a] - features_df[col_b]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features_df.to_csv(output_path, index=False)
    print(f"Features saved: {features_df.shape} -> {output_path}")

    return features_df


if __name__ == "__main__":
    build_features()
