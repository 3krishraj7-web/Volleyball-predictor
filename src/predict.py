import os
import sys
import joblib
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METRICS = [
    "Kills", "Errors", "Total Attacks", "Hit Pct", "Assists",
    "Aces", "SErr", "Digs", "RErr", "Block Solos", "Block Assists",
    "BErr", "PTS"
]


def get_latest_profile(team: str, df: pd.DataFrame) -> dict:
    m_a = df[df["TeamA"].str.lower() == team.lower()]
    m_b = df[df["TeamB"].str.lower() == team.lower()]
    la = m_a.iloc[-1] if len(m_a) else None
    lb = m_b.iloc[-1] if len(m_b) else None
    if la is None and lb is None:
        return None
    actual_name = la["TeamA"] if la is not None else lb["TeamB"]
    if lb is None or (la is not None and la["Date"] >= lb["Date"]):
        profile = {m: float(la[f"Team A {m}"]) for m in METRICS}
    else:
        profile = {m: float(lb[f"Team B {m}"]) for m in METRICS}
    return {"name": actual_name, "stats": profile}


def build_pair_features(prof_a: dict, prof_b: dict) -> pd.DataFrame:
    row = {}
    for m in METRICS:
        row[f"Team A {m}"] = prof_a[m]
    for m in METRICS:
        row[f"Team B {m}"] = prof_b[m]
    for m in METRICS:
        diff_name = f"diff_{m.lower().replace(' ', '_')}"
        row[diff_name] = prof_a[m] - prof_b[m]
    return pd.DataFrame([row])


def predict_matchup(team_a: str, team_b: str,
                    model_path: str = os.path.join(ROOT_DIR, "models", "best_model.joblib"),
                    features_path: str = os.path.join(ROOT_DIR, "data", "processed", "features.csv")) -> dict:
    df = pd.read_csv(features_path)
    df["Date"] = pd.to_datetime(df["Date"])

    p_a = get_latest_profile(team_a, df)
    p_b = get_latest_profile(team_b, df)

    if not p_a:
        raise ValueError(f"Team '{team_a}' not found in match history.")
    if not p_b:
        raise ValueError(f"Team '{team_b}' not found in match history.")

    model = joblib.load(model_path)

    # Symmetrical prediction: averages both orientations to eliminate presentation order bias
    feat_ab = build_pair_features(p_a["stats"], p_b["stats"])
    feat_ba = build_pair_features(p_b["stats"], p_a["stats"])

    p_a_forward = model.predict_proba(feat_ab)[0][1]
    p_b_reverse = model.predict_proba(feat_ba)[0][1]
    prob_a = (p_a_forward + (1.0 - p_b_reverse)) / 2.0
    prob_b = 1.0 - prob_a

    winner = p_a["name"] if prob_a >= 0.5 else p_b["name"]

    key_diffs = {
        m: p_a["stats"][m] - p_b["stats"][m]
        for m in ["Hit Pct", "Kills", "Assists", "Digs", "PTS"]
    }

    return {
        "team_a": p_a["name"],
        "team_b": p_b["name"],
        "prob_a": prob_a,
        "prob_b": prob_b,
        "predicted_winner": winner,
        "confidence": max(prob_a, prob_b),
        "key_differentials": key_diffs
    }


if __name__ == "__main__":
    t_a = sys.argv[1] if len(sys.argv) > 1 else "Stanford"
    t_b = sys.argv[2] if len(sys.argv) > 2 else "Texas"
    res = predict_matchup(t_a, t_b)
    print(f"\nMatchup: {res['team_a']} vs {res['team_b']}")
    print(f"{res['team_a']} Win Probability: {res['prob_a'] * 100:.2f}%")
    print(f"{res['team_b']} Win Probability: {res['prob_b'] * 100:.2f}%")
    print(f"Predicted Winner: {res['predicted_winner']} ({res['confidence'] * 100:.1f}% confidence)\n")
    print("Stat Differentials (Team A - Team B):")
    for stat, diff in res["key_differentials"].items():
        leader = res['team_a'] if diff > 0 else res['team_b']
        print(f"  - {stat:10s}: {diff:+.3f} (Advantage: {leader})")

    pred_dir = os.path.join(ROOT_DIR, "data", "predictions")
    os.makedirs(pred_dir, exist_ok=True)
    history_file = os.path.join(pred_dir, "match_history.csv")
    entry = pd.DataFrame([{
        "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Team A": res["team_a"],
        "Team B": res["team_b"],
        "Prob A": f"{res['prob_a'] * 100:.2f}%",
        "Prob B": f"{res['prob_b'] * 100:.2f}%",
        "Predicted Winner": res["predicted_winner"],
        "Confidence": f"{res['confidence'] * 100:.1f}%"
    }])
    entry.to_csv(history_file, mode="a", header=not os.path.exists(history_file), index=False)
    print(f"\n[Auto-Saved] Prediction logged to {history_file}")
