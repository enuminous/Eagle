# EAGLE

<!-- ENUMINOUS-NETWORK:START -->
**eNuminous network:** [All repositories](https://enuminous.github.io/EFMW/repositories.html) · [EFMW](https://enuminous.github.io/EFMW/) · [102 equations](https://github.com/enuminous/Monolithic_102_EFMW) · [165 triplets](https://enuminous.github.io/FieldSpace/) · [Zoo](https://enuminous.github.io/Tortoise/) · [Lean](https://enuminous.github.io/Aristotle-102-Monolithic-Lean/) · [Engine](https://enuminous.github.io/Archimedes-Engine/) · [Papers](https://enuminous.github.io/medium/papers-essays-index.html) · [Audit](https://github.com/enuminous/EFMW_Post156_Zoo_Audit/blob/main/portfolio/INTERLOCK_AUDIT.md)

[Repository](https://github.com/enuminous/Eagle) · This repository is linked through its source; GitHub Pages is not enabled.
<!-- ENUMINOUS-NETWORK:END -->

**Early Anomaly and Gradient Loss Estimator**

EAGLE is an EFMW-derived framework for fast-moving operational systems where the main problem is not detecting an anomaly after it appears, but identifying a deteriorating trajectory before it crosses a conventional threshold.

## Intended uses

- live operations
- queueing systems
- service reliability
- network operations
- autonomous systems
- incident response
- logistics
- production systems
- process control
- rapidly changing multi-signal environments

## Core question

> Does deterioration in state gradients provide earlier warning than snapshot anomaly detection?

## Signal path

```text
current state
→ robust anomaly score
→ first derivative
→ second derivative
→ cross-signal gradient disagreement
→ persistence
→ multiscale deterioration
→ EAGLE risk score
```

## Flat-stack repository

```text
README.md
LICENSE
CITATION.cff
pyproject.toml
requirements.txt
eagle.py
features.py
baselines.py
metrics.py
freeze.py
alert_schema.json
example_config.yaml
example_data.csv
example_run.py
test_eagle.py
MANIFEST.sha256
```

## Scientific hypothesis

> In fast operational systems, the direction and acceleration of multi-signal degradation may carry predictive information before absolute anomaly levels become extreme.

EAGLE does not assume that this hypothesis is correct.

## Baselines

Included:

- absolute z-score anomaly
- EWMA deviation
- rolling slope
- raw-feature logistic baseline
- base-rate predictor

## Primary endpoint

At matched false-alarm rates:

- sensitivity to future failure
- median lead time
- Brier score
- log loss
- AUROC
- average precision

## Installation

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python example_run.py
```

## Tests

```bash
pytest -q
```

## Minimal use

```python
import pandas as pd
from eagle import EAGLEExperiment

df = pd.read_csv("example_data.csv")

exp = EAGLEExperiment(
    time_column="time",
    failure_column="failure",
    feature_columns=["latency", "error_rate", "queue_depth", "throughput"],
    failure_horizon=20,
    horizons=(3, 7, 15),
)

print(exp.run(df))
```

## Freeze discipline

Before prospective use, freeze:

- features
- sampling interval
- failure definition
- warning horizon
- gradient equations
- multiscale horizons
- threshold-selection rule
- false-alarm budget
- baselines
- metrics
- exclusions
- seeds

Then run:

```bash
python freeze.py
```

## Negative results

If snapshot anomaly or conventional temporal baselines match or beat EAGLE, then the gradient-loss formulation has not shown incremental value.

## Status

Research software. Experimental. Not validated for safety-critical deployment.
