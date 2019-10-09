from typing import Dict, Any

import pandas as pd


class DataFrame:

    def __new__(self, data: Dict[str, Any]) -> pd.DataFrame:
        if isinstance(data, dict):
            return pd.DataFrame(data, index=[0])
        else:
            raise NotImplementedError()