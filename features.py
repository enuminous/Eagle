import numpy as np
import pandas as pd

EPS = 1e-8

def robust_z(s, window=15):
    s = s.astype(float)
    med = s.rolling(window, min_periods=3).median()
    mad = (s-med).abs().rolling(window, min_periods=3).median()
    return ((s-med)/(1.4826*mad+EPS)).replace([np.inf,-np.inf], np.nan).fillna(0.0)

def build_eagle_features(df, feature_columns, horizons=(3,7,15)):
    x = df[feature_columns].astype(float).copy()
    out = pd.DataFrame(index=df.index)

    zcols = []
    g1cols = []
    g2cols = []

    for c in feature_columns:
        z = f"{c}__z"
        g1 = f"{c}__g1"
        g2 = f"{c}__g2"
        out[z] = robust_z(x[c], max(horizons))
        out[g1] = x[c].diff().fillna(0.0)
        out[g2] = x[c].diff().diff().fillna(0.0)
        zcols.append(z)
        g1cols.append(g1)
        g2cols.append(g2)

    out["snapshot_anomaly"] = out[zcols].abs().mean(axis=1)
    out["gradient_magnitude"] = out[g1cols].abs().mean(axis=1)
    out["gradient_acceleration"] = out[g2cols].abs().mean(axis=1)

    # Gradient disagreement: signals no longer moving coherently.
    g1 = out[g1cols]
    out["gradient_disagreement"] = g1.std(axis=1).fillna(0.0)

    # Sign incoherence: fraction of signals moving against median direction.
    med_sign = np.sign(g1.median(axis=1))
    sign_matrix = np.sign(g1)
    disagreement = sign_matrix.ne(med_sign, axis=0).mean(axis=1)
    out["sign_incoherence"] = disagreement.fillna(0.0)

    # Loss = anomaly plus worsening gradients.
    out["gradient_loss"] = (
        out["snapshot_anomaly"].rank(pct=True)
        + out["gradient_magnitude"].rank(pct=True)
        + out["gradient_acceleration"].rank(pct=True)
        + out["gradient_disagreement"].rank(pct=True)
        + out["sign_incoherence"].rank(pct=True)
    ) / 5.0

    for h in horizons:
        out[f"loss_mean_{h}"] = out["gradient_loss"].rolling(h, min_periods=1).mean()
        out[f"loss_slope_{h}"] = out["gradient_loss"].diff().rolling(h, min_periods=1).mean()
        out[f"anomaly_mean_{h}"] = out["snapshot_anomaly"].rolling(h, min_periods=1).mean()
        out[f"disagreement_mean_{h}"] = out["gradient_disagreement"].rolling(h, min_periods=1).mean()

    components = [
        out["gradient_loss"],
        out["snapshot_anomaly"],
        out["gradient_disagreement"],
        out["gradient_acceleration"],
    ]
    for h in horizons:
        components.extend([
            out[f"loss_mean_{h}"],
            out[f"loss_slope_{h}"].clip(lower=0),
            out[f"anomaly_mean_{h}"],
            out[f"disagreement_mean_{h}"],
        ])

    ranked = pd.concat(components, axis=1).rank(pct=True)
    out["eagle_risk_score"] = ranked.mean(axis=1).fillna(0.0)

    return out.replace([np.inf,-np.inf], np.nan).fillna(0.0)
