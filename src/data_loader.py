import os
import pandas as pd


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_matches(file_path: str = None) -> pd.DataFrame:
    if file_path is None:
        candidates = [
            os.path.join(ROOT_DIR, "data", "combined", "accumulated", "0.2_ewm_combined.csv"),
            os.path.join(ROOT_DIR, "data", "raw", "ncaa", "2019", "accumulated", "0.2_ewm.csv"),
            os.path.join(ROOT_DIR, "data", "processed", "2019", "accumulated", "0.2_ewm.csv"),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                file_path = candidate
                break
        if file_path is None:
            raise FileNotFoundError(f"Matches file not found in: {candidates}")

    df = pd.read_csv(file_path).drop_duplicates()

    if "Date" in df.columns:
        date_str = df["Date"].astype(str).str.zfill(8)
        df["Date"] = pd.to_datetime(date_str, format="%m%d%Y", errors="coerce")
        df = df.sort_values(by="Date").reset_index(drop=True)

    return df


if __name__ == "__main__":
    matches = load_matches()
    print(f"Loaded: {matches.shape}")
    print(matches.head(3))
