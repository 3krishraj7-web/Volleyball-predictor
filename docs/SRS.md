# Software Requirements Specification (SRS)
## NCAA Volleyball Match Outcome Predictor

---

### 1. Introduction

#### 1.1 Purpose
This document specifies the software requirements for the NCAA Volleyball Match Outcome Predictor. It defines the functional behavior, performance constraints, data handling rules, and system interfaces for both developer and end-user workflows.

#### 1.2 Scope
The system is a machine learning pipeline and desktop application that forecasts the winner and win probability of NCAA Division I women's volleyball matches. It ingests historical box scores from 2016 through 2019, generates leakage-free differential features, trains and benchmarks classification models, and serves predictions through both a graphical user interface and a command-line interface.

#### 1.3 Definitions and Acronyms
- **EWM**: Exponential Weighted Moving average, used to track team performance momentum.
- **Leakage**: The unintended introduction of post-match information into pre-match training features.
- **Symmetry**: Invariance of prediction outcomes under team order inversion.
- **SRS**: Software Requirements Specification.
- **GUI**: Graphical User Interface.

---

### 2. Overall Description

#### 2.1 Product Perspective
The system operates as a self-contained analytics tool. It consists of:
1. Core Python modules for data loading, feature engineering, model training, and inference.
2. An interactive Jupyter notebook for data exploration and reporting.
3. A Tkinter-based desktop GUI packaged into a standalone 64-bit Windows executable.
4. An automated Windows setup installer for configuring client environments.

#### 2.2 User Characteristics
- **Technical Users / Data Scientists**: Run scripts via CLI, execute notebooks, modify feature logic, or retrain models using new data.
- **Non-Technical Evaluators / Recruiters**: Run the pre-compiled portable executable or batch installer to test matchups without configuring Python.

#### 2.3 Operating Environment
- Operating System: Windows 10/11 (64-bit).
- Python Runtime: Python 3.10 to 3.14.
- Core Libraries: pandas, numpy, scikit-learn, xgboost, joblib, matplotlib, jupyter, pytest.

---

### 3. Specific System Requirements

#### 3.1 Functional Requirements

##### FR-1: Data Ingestion and Validation
- The system shall load historical match records from `data/combined/accumulated/0.2_ewm_combined.csv` or season-specific fallback paths.
- The system shall drop duplicate rows and parse match dates into standard `YYYY-MM-DD` timestamps.
- Matches must be chronologically sorted to support time-series operations.

##### FR-2: Target Leakage Prevention
- The system must explicitly drop post-match metadata, specifically total sets played (column `S`), before training feature construction.
- All team statistics must represent historical rolling metrics calculated strictly prior to match kickoff.

##### FR-3: Feature Engineering
- The system shall compute head-to-head differential statistics across 13 box-score metrics:
  `diff_<metric> = Team_A_<metric> - Team_B_<metric>`
  Metrics include: Kills, Errors, Total Attacks, Hit Pct, Assists, Aces, Service Errors, Digs, Reception Errors, Block Solos, Block Assists, Block Errors, and Points.
- The output feature matrix must be written to `data/processed/features.csv`.

##### FR-4: Chronological Holdout Splitting
- Training and evaluation splits must reflect real-world time constraints.
- Training set: Matches from seasons 2016 through 2018 (27,480 matches).
- Test set: Matches from the 2019 season (8,868 matches).
- Random k-fold cross-validation across time boundaries is prohibited to prevent temporal leakage.

##### FR-5: Model Benchmarking and Serialization
- The system shall train and compare Logistic Regression, Random Forest, and XGBoost classifiers.
- Evaluation metrics must report Accuracy, ROC-AUC, and Log Loss.
- The highest-performing model based on validation ROC-AUC must be serialized to `models/best_model.joblib`.

##### FR-6: Symmetrical Pairwise Inference
- The prediction engine must evaluate matchups in both orientations to eliminate presentation order bias:
  `P(Team A wins) = 0.5 * (P(A vs B) + (1.0 - P(B vs A)))`
- The system must guarantee that `P(Team A) + P(Team B) = 1.0`.

##### FR-7: Desktop GUI Interface
- The GUI must provide a head-to-head matchup selector supporting all 322 teams in the dataset.
- The GUI must provide a swap button that flips team selections and updates probabilities instantaneously.
- The GUI must display visual probability progress bars and a table of key stat differentials.
- The GUI must support batch CSV evaluation and allow exporting predictions to CSV.

##### FR-8: Automatic Data Logging
- Every single matchup prediction must be automatically appended to `data/predictions/match_history.csv` with timestamp, teams, win chances, and predicted winner.
- Batch evaluation results must be automatically written to `data/predictions/batch_predictions_latest.csv`.

---

### 4. Non-Functional Requirements

#### 4.1 Performance
- Single matchup inference latency must not exceed 250 milliseconds.
- Batch evaluation of 8,000 matches must complete within 2.0 seconds on standard hardware.

#### 4.2 Reliability and Invariants
- Probability outputs must strictly remain within the closed interval `[0.0, 1.0]`.
- Predictions must be deterministic for identical input feature vectors.

#### 4.3 Portability
- The portable executable must run on standard 64-bit Windows installations without external runtime dependencies.
- Repository paths must be anchored to project root to allow execution from any working directory.
