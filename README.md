# NCAA Volleyball Match Outcome Predictor

A machine learning project to predict the winner of NCAA Division I women's volleyball matches using historical box-score and rolling statistics from 2016 through 2019. 

The project includes data cleaning, leakage-free feature engineering, time-based model benchmarking, an interactive Jupyter notebook, and a standalone Windows desktop app.

---

## Results

Models were trained on matches from 2016 through 2018 (27,480 matches) and evaluated on an out-of-time holdout set consisting of the entire 2019 season (8,868 matches):

| Model | Accuracy | ROC-AUC | Log Loss | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **XGBoost** | **78.42%** | **0.8730** | **0.4444** | Best overall performance; saved as default model |
| **Random Forest** | 78.65% | 0.8724 | 0.4505 | Competitive baseline |
| **Logistic Regression** | 77.46% | 0.8417 | 0.5593 | Scaled features, linear baseline |

- **ROC-AUC (0.8730)** indicates solid class separation across thousands of collegiate matchups.
- **Log Loss (0.4444)** reflects calibrated predicted probabilities rather than overconfident classifications.

---

## Data and Modeling Approach

### 1. Leakage Prevention
In volleyball box scores, the total number of sets played (column `S`) is recorded after the match finishes (e.g., 3, 4, or 5 sets). Including this column would leak information about match competitiveness that is unknown before the match starts. Column `S` is dropped during feature engineering, and all team metrics rely strictly on rolling stats computed before game day.

### 2. Symmetrical Matchup Prediction
Tree-based models can produce slightly different probability outputs depending on whether a matchup is input as Team A vs Team B or Team B vs Team A. To eliminate presentation order bias, the prediction function evaluates both orientations and averages them:

$$P(\text{Team A wins}) = \frac{P_A(A \text{ vs } B) + (1 - P_B(B \text{ vs } A))}{2}$$

This guarantees that:
$$P(\text{Team A wins}) + P(\text{Team B wins}) = 1.0$$
regardless of which team is selected first.

### 3. Key Feature Drivers
Feature importance inspection shows the strongest predictors of match success:
1. **`diff_hit_pct` (Hitting Percentage Differential)**: Attack efficiency minus attack errors is by far the strongest single predictor of victory.
2. **`diff_assists` and `diff_kills`**: Measures transition offense and ability to convert scoring opportunities.
3. **`diff_digs`**: Floor defense to prevent opponent scoring runs.

---

## Project Structure

```text
Volleyball predictor/
├── data/
│   ├── combined/accumulated/       # Multi-season historical matches (2016-2019, 36,348 rows)
│   ├── processed/features.csv      # 39 engineered differential feature columns
│   └── predictions/                # Output folder for logged predictions
│       ├── match_history.csv       # Head-to-head prediction logs
│       └── batch_predictions_latest.csv # Batch CSV test outputs
├── dist/
│   ├── VolleyballPredictor_Portable.exe # Standalone 64-bit Windows executable (no Python required)
│   └── VolleyballPredictor_Windows_x64.zip # Portable zip package (141 MB)
├── models/
│   └── best_model.joblib           # Trained XGBoost model
├── notebooks/
│   └── volleyball_predictor.ipynb  # Jupyter notebook (data prep, training, plots, demo)
├── packaging/
│   ├── VolleyballPredictor_Portable.spec # PyInstaller build spec
│   └── installer_inno.iss          # Inno Setup installer script
├── reports/
│   └── figures/                    # Exported charts and figures
├── src/
│   ├── app.py                      # Desktop GUI application (Tkinter)
│   ├── data_loader.py              # Ingestion, date parsing, and deduplication
│   ├── features.py                 # Feature engineering and leakage cleanup
│   ├── train.py                    # Time-split training and evaluation pipeline
│   └── predict.py                  # Symmetrical prediction logic and CLI
├── tests/
│   └── test_predict.py             # Automated unit tests
├── install_dependencies.bat        # Automated environment setup script for Windows
├── run_jupyter.bat                 # One-click launcher for Jupyter notebook
├── setup_windows.bat               # Desktop shortcut installer
├── requirements.txt                # Pinned dependencies
└── README.md                       # Documentation
```

---

## Getting Started

### Option 1: Desktop Application (No Python Required)
If you want to run the app directly on a Windows laptop without installing Python:
1. Run `setup_windows.bat` to create an **NCAA Volleyball Predictor** shortcut on your Desktop, or
2. Open `dist/VolleyballPredictor_Portable.exe` directly.

The app lets you:
- Select any two of the 322 NCAA Division I teams to view win probabilities, predicted winner, and key statistical differentials.
- Upload any CSV of matches to run batch predictions and export results.

---

### Option 2: Python Setup
To run or modify the code locally:

```bash
# Clone the repository
git clone https://github.com/3krishraj7-web/Volleyball-predictor.git
cd Volleyball-predictor

# Automated setup on Windows (creates .venv, installs packages, sets up kernel):
install_dependencies.bat

# Or manual setup:
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

### Option 3: Jupyter Notebook
To run the analysis notebook:
1. Double-click `run_jupyter.bat`, or
2. Run from your terminal:
   ```bash
   jupyter notebook notebooks/volleyball_predictor.ipynb
   ```
3. Run all cells to inspect the data pipeline, model benchmark table, feature importance charts, and matchup predictions.

---

### Option 4: Command-Line Predictions
You can run predictions directly from the command line:

```bash
python src/predict.py "Stanford" "Texas"
```

Example output:
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

[Auto-Saved] Prediction logged to data/predictions/match_history.csv
```

---

## Automatic Data Saving

All predictions are automatically stored to keep workflows clean:
- **Head-to-head match predictions**: Appended to `data/predictions/match_history.csv` with a timestamp, team names, probabilities, and predicted winner.
- **Batch CSV evaluations**: Saved to `data/predictions/batch_predictions_latest.csv`.
- **Engineered dataset**: Generated by `src/features.py` into `data/processed/features.csv`.
- **Model weights**: Saved by `src/train.py` into `models/best_model.joblib`.

---

## Tests

Run the test suite using pytest:
```bash
pytest tests/
```
Tests verify probability invariants ($P_A + P_B = 1.0$) and directional symmetry ($P(A \text{ vs } B) = 1 - P(B \text{ vs } A)$).
