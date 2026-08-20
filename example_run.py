import json
import pandas as pd
from eagle import EAGLEExperiment

df = pd.read_csv("example_data.csv")

exp = EAGLEExperiment(
    time_column="time",
    failure_column="failure",
    feature_columns=["latency","error_rate","queue_depth","throughput"],
    failure_horizon=20,
    horizons=(3,7,15),
    max_false_alarm_rate=0.05,
    random_state=23,
)

result = exp.run(df)
print(json.dumps(result, indent=2))
