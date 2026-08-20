import numpy as np
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score, average_precision_score

def future_failure_labels(failure, horizon):
    failure = np.asarray(failure, dtype=int)
    out = np.zeros_like(failure)
    n = len(failure)
    for i in range(n):
        end = min(n, i+horizon+1)
        out[i] = int(failure[i+1:end].max() if i+1 < end else 0)
    return out

def threshold_at_fpr(y, score, max_fpr=0.05):
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    neg = score[y == 0]
    if len(neg) == 0:
        return float(np.quantile(score, 0.95))
    return float(np.quantile(neg, 1-max_fpr))

def event_lead_times(failure, alerts):
    failure = np.asarray(failure, dtype=int)
    alerts = np.asarray(alerts, dtype=int)
    starts = np.where((failure == 1) & (np.r_[0, failure[:-1]] == 0))[0]
    leads = []
    for fi in starts:
        prior = np.where(alerts[:fi] == 1)[0]
        if len(prior):
            leads.append(int(fi-prior[-1]))
    return leads

def warning_metrics(failure, future_y, score, threshold):
    score = np.clip(np.asarray(score, dtype=float), 1e-9, 1-1e-9)
    future_y = np.asarray(future_y, dtype=int)
    alerts = (score >= threshold).astype(int)

    neg = future_y == 0
    pos = future_y == 1

    out = {
        "threshold": float(threshold),
        "false_alarm_rate": float(alerts[neg].mean()) if neg.any() else None,
        "sensitivity": float(alerts[pos].mean()) if pos.any() else None,
        "brier": float(brier_score_loss(future_y, score)),
        "log_loss": float(log_loss(future_y, np.c_[1-score,score], labels=[0,1])),
    }

    if len(np.unique(future_y)) > 1:
        out["roc_auc"] = float(roc_auc_score(future_y, score))
        out["average_precision"] = float(average_precision_score(future_y, score))
    else:
        out["roc_auc"] = None
        out["average_precision"] = None

    leads = event_lead_times(failure, alerts)
    out["median_event_lead_time"] = float(np.median(leads)) if leads else None
    out["events_with_prior_alert"] = len(leads)
    return out
