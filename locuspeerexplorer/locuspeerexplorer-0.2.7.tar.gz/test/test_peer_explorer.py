import os
import locuspeerexplorer.peer_explorer as pa
import pandas as pd
import locuspeerexplorer.params

dirname, filename = os.path.split(os.path.abspath(__file__))

df_data = pd.read_csv(os.path.join(dirname, "../data/processed/metrics_outcomes.csv"))

metrics = locuspeerexplorer.params.METRIC_NAMES

print(
    pa.get_distinguishing_outcomes(
        df_data, 11260, [11260, 10420, 10740, 12100], 2016, 0, metrics[0]
    )
)

print(
    pa.get_distinguishing_outcomes(
        df_data, 11260, [11260, 10420, 10740, 12100], 2016, 1, metrics[0]
    )
)

print(
    pa.get_distinguishing_outcomes(
        df_data, 11260, [11260, 10420, 10740, 12100], 2016, 2, metrics[0]
    )
)
