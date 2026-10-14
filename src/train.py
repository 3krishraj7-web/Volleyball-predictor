import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from xgboost import XGBClassifier


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_FEATURES = os.path.join(ROOT_DIR, "data", "processed", "features.csv")
DEFAULT_MODEL = os.path.join(ROOT_DIR, "models", "best_model.joblib")


def train_models(features_path: str = DEFAULT_FEATURES,
                 model_output_path: str = DEFAULT_MODEL,
                 train_fraction: float = 0.8) -> dict:
    if not os.path.exists(features_path):
        from src.features import build_features
        df = build_features(output_path=features_path)
    else:
        df = pd.read_csv(features_path)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date").reset_index(drop=True)

    target_col = "Result"
    drop_cols = ["Date", "TeamA", "TeamB", target_col, "Year"]
    feature_cols = [c for c in df.columns if c not in drop_cols]

    years = df["Date"].dt.year.dropna().unique()
    if len(years) > 1:
        latest_year = years.max()
        train_df = df[df["Date"].dt.year < latest_year]
        test_df = df[df["Date"].dt.year == latest_year]
    else:
        split_idx = int(len(df) * train_fraction)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]

    X_train, y_train = train_df[feature_cols], train_df[target_col]
    X_test, y_test = test_df[feature_cols], test_df[target_col]

    print(f"Train: {len(X_train)} rows | Test: {len(X_test)} rows | Features: {len(feature_cols)}")

    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=42))
        ]),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1),
        "XGBoost": XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, eval_metric="logloss", random_state=42)
    }

    results = {}
    best_model_name, best_auc, best_model_obj = None, -1.0, None

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        ll = log_loss(y_test, y_prob)
        auc = roc_auc_score(y_test, y_prob)

        results[name] = {"Accuracy": acc, "Log Loss": ll, "ROC-AUC": auc}
        print(f"{name:20s} | Acc: {acc:.4f} | Log Loss: {ll:.4f} | ROC-AUC: {auc:.4f}")

        if auc > best_auc:
            best_auc, best_model_name, best_model_obj = auc, name, model

    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(best_model_obj, model_output_path)
    print(f"\nSaved {best_model_name} (ROC-AUC: {best_auc:.4f}) -> {model_output_path}")

    return {"metrics": results, "best_model": best_model_name, "best_auc": best_auc}


if __name__ == "__main__":
    train_models()
