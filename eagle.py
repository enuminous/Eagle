from dataclasses import dataclass
import numpy as np
import pandas as pd

from features import build_eagle_features
from baselines import zscore_score, ewma_score, slope_score, LogisticRaw
from metrics import future_failure_labels, threshold_at_fpr, warning_metrics

@dataclass
class EAGLEExperiment:
    time_column: str
    failure_column: str
    feature_columns: list
    failure_horizon: int = 20
    horizons: tuple = (3,7,15)
    max_false_alarm_rate: float = 0.05
    train_fraction: float = 0.60
    random_state: int = 23

    def run(self, df):
        df = df.sort_values(self.time_column).reset_index(drop=True).copy()
        cut = max(20, int(len(df)*self.train_fraction))

        failure = df[self.failure_column].astype(int).to_numpy()
        future_y = future_failure_labels(failure, self.failure_horizon)

        ef = build_eagle_features(df, self.feature_columns, self.horizons)
        eagle_score = ef["eagle_risk_score"].to_numpy()

        z = zscore_score(df, self.feature_columns, max(self.horizons))
        ewma = ewma_score(df, self.feature_columns)
        slope = slope_score(df, self.feature_columns)

        raw = df[self.feature_columns].astype(float).copy()
        for c in self.feature_columns:
            raw[f"{c}__dx"] = raw[c].diff().fillna(0.0)
            raw[f"{c}__ddx"] = raw[c].diff().diff().fillna(0.0)
        raw = raw.ffill().fillna(0.0)

        logit = LogisticRaw(self.random_state).fit(raw.iloc[:cut], future_y[:cut])
        logit_score = np.concatenate([
            logit.predict_proba(raw.iloc[:cut]),
            logit.predict_proba(raw.iloc[cut:])
        ])

        scores = {
            "eagle": eagle_score,
            "zscore": z,
            "ewma": ewma,
            "slope": slope,
            "logistic_raw": logit_score,
        }

        results = {}
        for name, score in scores.items():
            threshold = threshold_at_fpr(
                future_y[:cut],
                score[:cut],
                self.max_false_alarm_rate
            )
            results[name] = warning_metrics(
                failure[cut:],
                future_y[cut:],
                score[cut:],
                threshold
            )

        return {
            "n_total": len(df),
            "train_n": cut,
            "test_n": len(df)-cut,
            "failure_horizon": self.failure_horizon,
            "max_false_alarm_rate": self.max_false_alarm_rate,
            "results": results,
            "primary_rule": (
                "Compare sensitivity and event lead time at thresholds selected "
                "to target the same training false-alarm budget."
            )
        }
