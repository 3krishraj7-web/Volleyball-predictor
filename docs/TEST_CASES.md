# Test Case Approach and Specification
## NCAA Volleyball Match Outcome Predictor

---

### 1. Test Strategy and Objectives

#### 1.1 Objectives
The primary testing objective is to verify that the prediction system satisfies all functional requirements defined in the SRS without data leakage, numerical instability, or platform incompatibilities.

#### 1.2 Test Levels
1. **Unit Testing**: Automated assertions verifying feature transformations, invariant constraints, and mathematical symmetry using `pytest`.
2. **Integration Testing**: Pipeline execution linking data loading, feature generation, model training, and disk serialization.
3. **System Testing**: Verification of the desktop GUI, automated installer scripts, and standalone executable behavior.

---

### 2. Test Case Matrix

| Test ID | Test Category | Requirement | Description | Test Inputs | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Data Ingestion | FR-1 | Load and deduplicate match dataset; parse date columns. | Default dataset path (`0.2_ewm_combined.csv`) | 36,348 rows loaded; `Date` parsed as datetime; 0 duplicates. | **PASS** |
| **TC-02** | Leakage Audit | FR-2 | Verify post-match column `S` is excluded from feature set. | `features.csv` column schema | Column `S` is not present in output features matrix. | **PASS** |
| **TC-03** | Feature Engine | FR-3 | Validate calculation of 13 differential features. | Known Team A and Team B sample metrics | `diff_<metric> == Team_A_<metric> - Team_B_<metric>` across all 13 stats. | **PASS** |
| **TC-04** | Time Split | FR-4 | Verify out-of-time chronological train/test split. | Historical dates across 2016-2019 | Train set contains only years < 2019 (27,480 rows); Test set contains year == 2019 (8,868 rows). | **PASS** |
| **TC-05** | Training | FR-5 | Train baseline and ensemble models; verify metric outputs. | 39 feature columns, target `Result` | XGBoost achieves ROC-AUC >= 0.87, Accuracy >= 78%; best model serialized to disk. | **PASS** |
| **TC-06** | Symmetry | FR-6 | Test directional symmetry when team order is flipped. | `predict_matchup("Stanford", "Texas")` vs `predict_matchup("Texas", "Stanford")` | `res1["prob_a"] == res2["prob_b"]` and predicted winner is identical. | **PASS** |
| **TC-07** | Invariant | FR-6 | Test probability sum normalisation invariant. | Pairwise match inputs | `prob_a + prob_b == 1.0` within numerical precision of `1e-5`. | **PASS** |
| **TC-08** | Auto-Save | FR-8 | Verify predictions are automatically logged to disk. | Execution of `predict.py` or batch GUI run | New record appended to `data/predictions/match_history.csv` with valid timestamp. | **PASS** |
| **TC-09** | Executable | FR-7 | Verify portable executable launches without missing dependencies. | Launch `VolleyballPredictor_Portable.exe` | Application process initializes within 5 seconds without missing DLL dialogs. | **PASS** |
| **TC-10** | Installer | FR-1 | Verify one-click dependency installer on clean system. | Execution of `install_dependencies.bat` | Virtualenv created, requirements installed, pytest suite passes with return code 0. | **PASS** |

---

### 3. Detailed Test Procedures

#### TC-06: Directional Symmetry Verification
```python
def test_predict_symmetry():
    res1 = predict_matchup("Stanford", "Texas")
    res2 = predict_matchup("Texas", "Stanford")

    assert pytest.approx(res1["prob_a"] + res1["prob_b"], 1e-5) == 1.0
    assert pytest.approx(res1["prob_a"], 1e-4) == res2["prob_b"]
    assert pytest.approx(res1["prob_b"], 1e-4) == res2["prob_a"]
    assert res1["predicted_winner"] == res2["predicted_winner"]
```
- **Execution Command**: `pytest tests/test_predict.py`
- **Result**: 1 passed in 4.24s.

#### TC-08: Automatic Logging Verification
1. Run `python src/predict.py "Stanford" "Texas"`.
2. Inspect `data/predictions/match_history.csv`.
3. Confirm that the last row contains the current timestamp, both teams, predicted win percentages, and predicted winner.

---

### 4. Requirements Traceability Matrix

| Requirement ID | Requirement Summary | Covering Test Cases |
| :--- | :--- | :--- |
| **FR-1** | Match ingestion and date parsing | TC-01, TC-10 |
| **FR-2** | Post-match leakage pruning (`S` column) | TC-02 |
| **FR-3** | 13 differential features generation | TC-03 |
| **FR-4** | Chronological train/test split | TC-04 |
| **FR-5** | Model training, benchmarking, and saving | TC-05 |
| **FR-6** | Symmetrical pairwise inference | TC-06, TC-07 |
| **FR-7** | Desktop GUI interface and standalone exe | TC-09 |
| **FR-8** | Automatic logging of predictions | TC-08 |
