import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import joblib
import pandas as pd
from src.predict import predict_matchup, get_latest_profile, METRICS


def get_base_path() -> str:
    # PyInstaller unpack directory when frozen, otherwise project root
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class VolleyballPredictorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NCAA Volleyball Match Predictor")
        self.root.geometry("820x680")
        self.root.minsize(760, 600)

        self.base_path = get_base_path()
        self.model_path = os.path.join(self.base_path, "models", "best_model.joblib")
        self.data_path = os.path.join(self.base_path, "data", "processed", "features.csv")

        self.df_features = self._load_dataset()
        self.teams = self._extract_teams()
        self.model = joblib.load(self.model_path) if os.path.exists(self.model_path) else None

        self._setup_theme()
        self._build_ui()

    def _load_dataset(self) -> pd.DataFrame:
        if not os.path.exists(self.data_path):
            return pd.DataFrame()
        df = pd.read_csv(self.data_path)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        return df

    def _extract_teams(self) -> list:
        if self.df_features.empty:
            return []
        teams = set(self.df_features["TeamA"].dropna()).union(set(self.df_features["TeamB"].dropna()))
        return sorted(list(teams))

    def _setup_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        self.root.configure(bg="#f4f6f9")

        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#1e3a5f", foreground="#ffffff")
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10), background="#1e3a5f", foreground="#d0d7de")
        style.configure("Card.TFrame", background="#ffffff", relief="ridge")
        style.configure("Bold.TLabel", font=("Segoe UI", 10, "bold"), background="#ffffff")
        style.configure("Result.TLabel", font=("Segoe UI", 14, "bold"), background="#ffffff", foreground="#1e3a5f")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=6)

    def _build_ui(self):
        header_frame = tk.Frame(self.root, bg="#1e3a5f", pady=12)
        header_frame.pack(fill="x")

        ttk.Label(header_frame, text="NCAA Volleyball Match Predictor", style="Header.TLabel").pack()
        ttk.Label(header_frame, text="AI/ML Outcomes Engine (2016–2019 Collegiate Model)", style="SubHeader.TLabel").pack(pady=2)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=16, pady=12)

        tab_matchup = ttk.Frame(notebook)
        tab_batch = ttk.Frame(notebook)

        notebook.add(tab_matchup, text=" Head-to-Head Predictor ")
        notebook.add(tab_batch, text=" Batch CSV Testing & Evaluation ")

        self._build_matchup_tab(tab_matchup)
        self._build_batch_tab(tab_batch)

    def _build_matchup_tab(self, parent):
        top_card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        top_card.pack(fill="x", padx=8, pady=8)

        grid = tk.Frame(top_card, bg="#ffffff")
        grid.pack(fill="x")

        tk.Label(grid, text="Team A:", font=("Segoe UI", 10, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.combo_a = ttk.Combobox(grid, values=self.teams, width=28)
        self.combo_a.grid(row=0, column=1, padx=6, pady=4)
        if "Stanford" in self.teams:
            self.combo_a.set("Stanford")

        btn_swap = ttk.Button(grid, text="⇄ Swap", width=8, command=self._swap_teams)
        btn_swap.grid(row=0, column=2, padx=10, pady=4)

        tk.Label(grid, text="Team B:", font=("Segoe UI", 10, "bold"), bg="#ffffff").grid(row=0, column=3, sticky="w", padx=6, pady=4)
        self.combo_b = ttk.Combobox(grid, values=self.teams, width=28)
        self.combo_b.grid(row=0, column=4, padx=6, pady=4)
        if "Texas" in self.teams:
            self.combo_b.set("Texas")

        btn_predict = ttk.Button(top_card, text="Predict Match Outcome", style="Action.TButton", command=self._predict_matchup)
        btn_predict.pack(pady=10)

        # Prediction results card
        self.result_card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        self.result_card.pack(fill="both", expand=True, padx=8, pady=6)

        self.lbl_winner = ttk.Label(self.result_card, text="Select teams above and click Predict", style="Result.TLabel")
        self.lbl_winner.pack(anchor="center", pady=6)

        bar_frame = tk.Frame(self.result_card, bg="#ffffff")
        bar_frame.pack(fill="x", padx=20, pady=6)

        self.lbl_prob_a = tk.Label(bar_frame, text="Team A: --%", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2b5c8f")
        self.lbl_prob_a.pack(anchor="w")
        self.prog_a = ttk.Progressbar(bar_frame, length=600, mode="determinate")
        self.prog_a.pack(fill="x", pady=2)

        self.lbl_prob_b = tk.Label(bar_frame, text="Team B: --%", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#b03a2e")
        self.lbl_prob_b.pack(anchor="w", pady=(6, 0))
        self.prog_b = ttk.Progressbar(bar_frame, length=600, mode="determinate")
        self.prog_b.pack(fill="x", pady=2)

        # Stat differentials table
        tk.Label(self.result_card, text="Key Stat Differentials (Team A - Team B):", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(anchor="w", pady=(10, 4))
        self.tree_diffs = ttk.Treeview(self.result_card, columns=("Metric", "Difference", "Advantage"), show="headings", height=5)
        self.tree_diffs.heading("Metric", text="Volleyball Metric")
        self.tree_diffs.heading("Difference", text="Differential Value")
        self.tree_diffs.heading("Advantage", text="Leader")
        self.tree_diffs.column("Metric", width=220)
        self.tree_diffs.column("Difference", width=180, anchor="center")
        self.tree_diffs.column("Advantage", width=240, anchor="center")
        self.tree_diffs.pack(fill="both", expand=True)

    def _swap_teams(self):
        a, b = self.combo_a.get(), self.combo_b.get()
        self.combo_a.set(b)
        self.combo_b.set(a)
        if a and b:
            self._predict_matchup()

    def _predict_matchup(self):
        team_a = self.combo_a.get().strip()
        team_b = self.combo_b.get().strip()

        if not team_a or not team_b:
            messagebox.showwarning("Missing Teams", "Please select both Team A and Team B.")
            return
        if team_a.lower() == team_b.lower():
            messagebox.showwarning("Invalid Matchup", "Team A and Team B cannot be the same team.")
            return

        try:
            res = predict_matchup(team_a, team_b, model_path=self.model_path, features_path=self.data_path)
        except Exception as e:
            messagebox.showerror("Prediction Error", str(e))
            return

        p_a, p_b = res["prob_a"] * 100, res["prob_b"] * 100
        winner = res["predicted_winner"]
        conf = res["confidence"] * 100

        self.lbl_winner.config(text=f"Predicted Winner: {winner} ({conf:.1f}% confidence)")
        self.lbl_prob_a.config(text=f"{res['team_a']}: {p_a:.2f}%")
        self.lbl_prob_b.config(text=f"{res['team_b']}: {p_b:.2f}%")
        self.prog_a["value"] = p_a
        self.prog_b["value"] = p_b

        for row in self.tree_diffs.get_children():
            self.tree_diffs.delete(row)

        for stat, diff in res["key_differentials"].items():
            leader = res["team_a"] if diff > 0 else res["team_b"]
            sign = "+" if diff > 0 else ""
            self.tree_diffs.insert("", "end", values=(stat, f"{sign}{diff:.3f}", leader))

        # Auto-save prediction history
        pred_dir = os.path.join(self.base_path, "data", "predictions")
        os.makedirs(pred_dir, exist_ok=True)
        history_path = os.path.join(pred_dir, "match_history.csv")
        log_entry = pd.DataFrame([{
            "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Team A": res["team_a"],
            "Team B": res["team_b"],
            "Prob A": f"{p_a:.2f}%",
            "Prob B": f"{p_b:.2f}%",
            "Predicted Winner": winner,
            "Confidence": f"{conf:.1f}%"
        }])
        log_entry.to_csv(history_path, mode="a", header=not os.path.exists(history_path), index=False)

    def _build_batch_tab(self, parent):
        top_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        top_card.pack(fill="x", padx=8, pady=8)

        tk.Label(top_card, text="Evaluate Any Custom Test CSV Dataset:", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(top_card, text="CSV should contain either team names or pre-computed match features.", font=("Segoe UI", 9), bg="#ffffff", fg="#57606a").pack(anchor="w", pady=(0, 8))

        btn_box = tk.Frame(top_card, bg="#ffffff")
        btn_box.pack(fill="x")

        ttk.Button(btn_box, text="Browse CSV File...", command=self._select_batch_file).pack(side="left", padx=4)
        self.lbl_batch_file = tk.Label(btn_box, text="No file selected (Default: data/processed/features.csv)", bg="#ffffff", fg="#24292f")
        self.lbl_batch_file.pack(side="left", padx=8)

        action_box = tk.Frame(top_card, bg="#ffffff")
        action_box.pack(fill="x", pady=(10, 0))

        ttk.Button(action_box, text="Run Batch Evaluation", style="Action.TButton", command=self._run_batch_eval).pack(side="left", padx=4)
        self.btn_export = ttk.Button(action_box, text="Export Predictions to CSV", state="disabled", command=self._export_batch_results)
        self.btn_export.pack(side="left", padx=6)

        self.lbl_batch_metric = tk.Label(action_box, text="", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#1e3a5f")
        self.lbl_batch_metric.pack(side="left", padx=16)

        # Batch preview treeview
        self.batch_tree = ttk.Treeview(parent, columns=("Date", "Team A", "Team B", "Predicted", "Prob A", "Prob B", "Actual"), show="headings")
        for col in ("Date", "Team A", "Team B", "Predicted", "Prob A", "Prob B", "Actual"):
            self.batch_tree.heading(col, text=col)
            self.batch_tree.column(col, width=105, anchor="center")
        self.batch_tree.pack(fill="both", expand=True, padx=8, pady=8)

        self.batch_df = None
        self.batch_results_df = None

    def _select_batch_file(self):
        f = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if f:
            self.lbl_batch_file.config(text=os.path.basename(f))
            self.selected_batch_path = f

    def _run_batch_eval(self):
        target_path = getattr(self, "selected_batch_path", self.data_path)
        if not os.path.exists(target_path):
            messagebox.showerror("Error", f"File not found: {target_path}")
            return

        try:
            df = pd.read_csv(target_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load CSV: {e}")
            return

        drop_cols = ["Date", "TeamA", "TeamB", "Result", "Year", "S"]
        feature_cols = [c for c in df.columns if c not in drop_cols]
        expected_cols = list(self.model.feature_names_in_)

        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            messagebox.showerror("Schema Mismatch", f"CSV is missing required feature columns:\n{missing[:5]}...")
            return

        X = df[expected_cols]
        probs = self.model.predict_proba(X)
        preds = (probs[:, 1] >= 0.5).astype(int)

        res_df = df.copy()
        res_df["pred_prob_a"] = probs[:, 1]
        res_df["pred_prob_b"] = probs[:, 0]
        res_df["predicted_winner"] = [
            row["TeamA"] if p == 1 else row["TeamB"]
            for _, row, p in zip(res_df.index, res_df.to_dict("records"), preds)
        ]

        self.batch_results_df = res_df
        self.btn_export.config(state="normal")

        # Auto-save batch predictions to data/predictions/
        pred_dir = os.path.join(self.base_path, "data", "predictions")
        os.makedirs(pred_dir, exist_ok=True)
        auto_path = os.path.join(pred_dir, "batch_predictions_latest.csv")
        res_df.to_csv(auto_path, index=False)

        # Metric reporting if ground truth exists
        if "Result" in df.columns:
            acc = (df["Result"] == preds).mean() * 100
            self.lbl_batch_metric.config(text=f"Total: {len(df):,} | Accuracy: {acc:.2f}% (Saved to data/predictions/)")
        else:
            self.lbl_batch_metric.config(text=f"Predicted {len(df):,} matches (Saved to data/predictions/)")

        # Display preview in treeview
        for row in self.batch_tree.get_children():
            self.batch_tree.delete(row)

        for _, r in res_df.head(100).iterrows():
            d_val = str(r.get("Date", ""))[:10]
            act_val = str(r.get("Result", "N/A"))
            self.batch_tree.insert("", "end", values=(
                d_val,
                r.get("TeamA", ""),
                r.get("TeamB", ""),
                r.get("predicted_winner", ""),
                f"{r['pred_prob_a'] * 100:.1f}%",
                f"{r['pred_prob_b'] * 100:.1f}%",
                act_val
            ))

    def _export_batch_results(self):
        if self.batch_results_df is None or self.batch_results_df.empty:
            return
        dest = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if dest:
            self.batch_results_df.to_csv(dest, index=False)
            messagebox.showinfo("Export Successful", f"Saved {len(self.batch_results_df)} predictions to:\n{dest}")


def main():
    root = tk.Tk()
    app = VolleyballPredictorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
