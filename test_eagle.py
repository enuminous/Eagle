import pandas as pd
from features import build_eagle_features
from eagle import EAGLEExperiment

FEATURES = ["latency","error_rate","queue_depth","throughput"]

def test_features():
    df = pd.read_csv("example_data.csv")
    ef = build_eagle_features(df, FEATURES)
    assert len(ef) == len(df)
    assert "eagle_risk_score" in ef.columns
    assert ef["eagle_risk_score"].between(0,1).all()

def test_experiment_runs():
    df = pd.read_csv("example_data.csv")
    exp = EAGLEExperiment(
        time_column="time",
        failure_column="failure",
        feature_columns=FEATURES,
    )
    out = exp.run(df)
    assert "results" in out
    assert "eagle" in out["results"]
    assert "zscore" in out["results"]
