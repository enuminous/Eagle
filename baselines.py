import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import RobustScaler

EPS = 1e-8

def zscore_score(df, feature_columns, window=15):
    parts = []
    for c in feature_columns:
        s = df[c].astype(float)
        med = s.rolling(window, min_periods=3).median()
        mad = (s-med).abs().rolling(window, min_periods=3).median()
        parts.append(((s-med)/(1.4826*mad+EPS)).abs().fillna(0.0))
    return pd.concat(parts, axis=1).mean(axis=1).rank(pct=True).to_numpy()

def ewma_score(df, feature_columns, alpha=0.25):
    parts = []
    for c in feature_columns:
        s = df[c].astype(float)
        mu = s.ewm(alpha=alpha, adjust=False).mean()
        parts.append((s-mu).abs())
    return pd.concat(parts, axis=1).mean(axis=1).fillna(0.0).rank(pct=True).to_numpy()

def slope_score(df, feature_columns, window=7):
    parts = []
    for c in feature_columns:
        parts.append(df[c].astype(float).diff().abs().rolling(window, min_periods=1).mean())
    return pd.concat(parts, axis=1).mean(axis=1).fillna(0.0).rank(pct=True).to_numpy()

class LogisticRaw:
    def __init__(self, random_state=23):
        self.scaler = RobustScaler()
        self.model = LogisticRegression(max_iter=4000, random_state=random_state)
        self.constant_ = None

    def fit(self, X, y):
        y = np.asarray(y, dtype=int)
        if len(np.unique(y)) < 2:
            self.constant_ = float(y.mean()) if len(y) else 0.0
            return self
        self.scaler.fit(X)
        self.model.fit(self.scaler.transform(X), y)
        return self

    def predict_proba(self, X):
        if self.constant_ is not None:
            return np.full(len(X), self.constant_)
        return self.model.predict_proba(self.scaler.transform(X))[:,1]
