# 🏐 NCAA Volleyball Match Outcome Predictor (AI/ML)

An end-to-end, production-grade Machine Learning system and standalone Windows desktop application that predicts collegiate NCAA volleyball match outcomes using 4 seasons of historical performance data (2016–2019), exponential moving statistics (EWM), and a mathematically symmetrical pairwise inference engine.

---

## 🌟 Key Features

- **Standalone Portable `.exe`**: Run instantly on any Windows laptop without installing Python or dependencies.
- **Interactive Jupyter Notebook**: Full interactive walkthrough covering exploratory data analysis (EDA), leakage-free feature engineering, model training, and feature importance charts.
- **Automatic Data Organization**: All predictions (single matchups and batch CSV tests) are automatically logged and saved into `data/predictions/`.
- **One-Click Auto-Installer**: Dedicated `install_dependencies.bat` automatically configures the Python virtual environment, dependencies, and Jupyter kernel on other Windows laptops.
- **Mathematically Symmetrical Prediction**: Eliminates presentation order bias—evaluating Team A vs. Team B or Team B vs. Team A always produces consistent, calibrated win probabilities.

---

## 🚀 Model Benchmark Results

Models were evaluated strictly on an out-of-time chronological holdout dataset (**8,868 unseen matches from the 2019 season**) after training on matches from 2016–2018 (27,480 matches):

| Model | Accuracy | ROC-AUC | Log Loss | Status |
| :--- | :---: | :---: | :---: | :--- |
| **XGBoost (Classifier)** | **78.42%** | **0.8730** | **0.4444** | **Selected Production Model** |
| **Random Forest** | **78.65%** | 0.8724 | 0.4505 | Competitive Runner-Up |
| **Logistic Regression** | 77.46% | 0.8417 | 0.5593 | Scaled Linear Baseline |

- **ROC-AUC (0.8730)**: Demonstrates strong discriminative capability in ranking winning probabilities across thousands of collegiate matchups.
- **Log Loss (0.4444)**: Confirms that probability estimates are well-calibrated confidence scores.

---

## 📁 Repository Structure

```text
├── data/
│   ├── combined/accumulated/       # 4-season historical dataset (2016–2019, 36,348 rows)
│   ├── processed/features.csv      # 39 engineered differential feature columns
│   └── predictions/                # [AUTO-SAVED] All matchup logs & batch test outputs
│       ├── match_history.csv       # Automatically logged head-to-head predictions
│       └── batch_predictions_latest.csv # Automatically saved batch test outputs
├── dist/
│   ├── VolleyballPredictor_Portable.exe # Standalone 1-file portable executable (Zero-install)
│   └── VolleyballPredictor_Windows_x64.zip # Distributable portable zip archive (141 MB)
├── models/
│   └── best_model.joblib           # Serialized production XGBoost model
├── notebooks/
│   └── volleyball_predictor.ipynb  # Interactive Jupyter notebook (EDA, training & visualizer)
├── packaging/
│   ├── VolleyballPredictor_Portable.spec # PyInstaller build specification
│   └── installer_inno.iss          # Inno Setup wizard configuration
├── reports/
│   └── figures/                    # Saved evaluation charts and figures
├── src/
│   ├── app.py                      # Desktop GUI application (Tkinter + ttk)
│   ├── data_loader.py              # Ingestion, date parsing & deduplication
│   ├── features.py                 # Leakage removal & 13 differential features
│   ├── train.py                    # Multi-season holdout benchmarking & model saver
│   └── predict.py                  # Symmetrical inference engine & CLI
├── tests/
│   └── test_predict.py             # Pytest automated test suite
├── install_dependencies.bat        # 1-click dependency installer for other Windows laptops
├── run_jupyter.bat                 # 1-click launcher for Jupyter Notebook
├── setup_windows.bat               # 1-click Desktop shortcut creator
├── requirements.txt                # Pinned reproducible Python dependencies
└── README.md                       # Complete project documentation
```

---

## ⚡ How to Run and Install

You can run this project in **4 different ways** depending on your workflow:

### Method 1: Portable Standalone Executable (No Python Required)
Best for: Demonstrating the application on any Windows machine without installing anything.
1. Navigate to the `dist/` directory.
2. Double-click:
   ```text
   dist\VolleyballPredictor_Portable.exe
   ```
3. The app launches immediately with full GUI support, bundled machine learning model, and team history.
4. *(Optional)* Run **`setup_windows.bat`** in the project root to automatically generate a desktop shortcut.

---

### Method 2: Direct Auto-Install for Other Windows Laptops
Best for: Setting up the developer environment on a fresh Windows machine with one click.
1. Ensure Python 3.10+ is installed on the laptop.
2. Double-click **`install_dependencies.bat`**.
3. The script will automatically:
   - Detect system Python (`python` or `py`).
   - Create an isolated virtual environment (`.venv`).
   - Upgrade `pip` to the latest version.
   - Install all required libraries (`pandas`, `numpy`, `scikit-learn`, `xgboost`, `jupyter`, `pytest`).
   - Register the dedicated Jupyter kernel (`Python (Volleyball Predictor)`).
   - Run verification unit tests to confirm 100% operational status.

---

### Method 3: Running from Jupyter Notebook
Best for: Exploring code, reviewing methodology, inspecting visualizations, and testing interactively.
1. Double-click **`run_jupyter.bat`** (or run `jupyter notebook notebooks/volleyball_predictor.ipynb` in terminal).
2. Your default web browser will open with the notebook loaded.
3. Select **Kernel -> Restart & Run All** to execute:
   - **Section 1**: Ingestion and validation of 36,348 matches across 2016–2019.
   - **Section 2**: Differential feature generation and leakage inspection.
   - **Section 3**: Model training and multi-metric benchmarking (Accuracy, ROC-AUC, Log Loss).
   - **Section 4**: Top 10 feature importance horizontal bar chart (XGBoost).
   - **Section 5**: Interactive symmetrical matchup prediction demo between chosen teams.

---

### Method 4: CLI Head-to-Head Prediction
Predict outcomes directly from PowerShell or Command Prompt:
```bash
# Activate virtual environment if not already activated
.\.venv\Scripts\activate

# Predict matchup between any two collegiate teams
python src/predict.py "Stanford" "Texas"
```
**Example Output:**
```text
Matchup: Stanford vs Texas
Stanford Win Probability: 56.61%
Texas Win Probability: 43.39%
Predicted Winner: Stanford (56.6% confidence)

Stat Differentials (Team A - Team B):
  - Hit Pct   : +0.016 (Advantage: Stanford)
  - Kills     : -2.783 (Advantage: Texas)
  - Assists   : -2.141 (Advantage: Texas)
  - Digs      : +4.781 (Advantage: Stanford)
  - PTS       : -6.379 (Advantage: Texas)

[Auto-Saved] Prediction logged to data\predictions\match_history.csv
```

---

## 💾 Automatic Data Saving Architecture

To ensure zero data loss during experimentation and demos, all generated outputs are automatically routed into clean repository folders:

| Data Type | Destination Path | Trigger / Behavior |
| :--- | :--- | :--- |
| **Matchup History** | [`data/predictions/match_history.csv`](file:///c:/Ai%20projects/Volleyball%20predictor/data/predictions/match_history.csv) | Auto-appends every CLI and GUI head-to-head prediction with timestamp and confidence. |
| **Batch CSV Outputs** | [`data/predictions/batch_predictions_latest.csv`](file:///c:/Ai%20projects/Volleyball%20predictor/data/predictions/batch_predictions_latest.csv) | Auto-saves whenever a batch CSV test is run in the GUI. |
| **Engineered Features**| [`data/processed/features.csv`](file:///c:/Ai%20projects/Volleyball%20predictor/data/processed/features.csv) | Auto-saved by `src/features.py` (39 differential columns). |
| **Trained ML Model** | [`models/best_model.joblib`](file:///c:/Ai%20projects/Volleyball%20predictor/models/best_model.joblib) | Auto-saved by `src/train.py` with the highest validation ROC-AUC. |

---

## 🧠 Machine Learning Methodology

### 1. Preventing Data Leakage
- **Set Count Stripping**: In NCAA match files, column `S` denotes total sets played in the match (e.g., 3, 4, or 5). Since this is only known *after* a match concludes, it is strictly pruned to prevent post-match leakage.
- **Chronological EWM**: Features use exponential moving statistics calculated strictly on preceding matches.

### 2. Symmetrical Pairwise Inference
Tree-based models can exhibit slight directional asymmetry when evaluating team order ($A \text{ vs } B$ vs. $B \text{ vs } A$). Our engine enforces mathematical symmetry:
$$P(\text{Team A}) = \frac{P_A(A \text{ vs } B) + (1 - P_B(B \text{ vs } A))}{2}, \quad P(\text{Team B}) = 1 - P(\text{Team A})$$
This guarantees identical outcome probabilities regardless of input orientation.

### 3. Key Statistical Drivers
Feature importance analysis highlights the top statistical indicators of match success:
1. **`diff_hit_pct` (Hitting Percentage Differential)**: Attacking efficiency relative to opponent error rates is the strongest predictor of victory.
2. **`diff_assists` & `diff_kills`**: Ability to execute terminal offense in transition plays.
3. **`diff_digs`**: Defensive floor coverage that prevents opponent scoring streaks.

---

## 🧪 Automated Testing

Run the test suite using `pytest`:
```bash
.\.venv\Scripts\pytest tests/
```
The test suite validates:
- Probability invariant: $P(\text{Team A}) + P(\text{Team B}) = 1.0$.
- Directional symmetry: `predict("A", "B")["prob_a"] == predict("B", "A")["prob_b"]`.

---

## ❓ Troubleshooting & FAQs for Windows

- **"Execution of scripts is disabled on this system"**:
  PowerShell by default may restrict script execution. You can run batch files (`.bat`) directly without restriction, or run in PowerShell:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
- **"Windows protected your PC" (SmartScreen prompt on portable `.exe`)**:
  Because this executable was compiled locally without a commercial EV certificate, Windows SmartScreen may show an informational prompt. Click **More Info -> Run anyway**.
- **PyCharm Environment Pointer**:
  Ensure PyCharm interpreter is set to `C:\Ai projects\Volleyball predictor\.venv\Scripts\python.exe` under **Settings -> Project -> Python Interpreter**.
