import pandas as pd
import numpy as np

class ForecastClassificatorSingle(object):
    def classify(self, data: pd.DataFrame):
        #data["CLASSIFICATION"] = data.apply(lambda row: ForecastClassificatorSingle.get_classification(row), axis=1)
        #data["CLASSIFICATION"] = np.where(data["WITH_HISTORY"] > 0, "single_known", "single_unknown")
        data["CLASSIFICATION"] = np.where(data["AVG_UPA"].notnull(), "single_known", "single_unknown")

        return data["CLASSIFICATION"]
