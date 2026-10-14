import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.predict import predict_matchup


def test_predict_symmetry():
    res1 = predict_matchup("Stanford", "Texas")
    res2 = predict_matchup("Texas", "Stanford")

    assert pytest.approx(res1["prob_a"] + res1["prob_b"], 1e-5) == 1.0
    assert pytest.approx(res1["prob_a"], 1e-4) == res2["prob_b"]
    assert pytest.approx(res1["prob_b"], 1e-4) == res2["prob_a"]
    assert res1["predicted_winner"] == res2["predicted_winner"]
