"""main package module"""

from datahub.config import ApiConfig
from datahub.api import ApiClient
import pandas as pd

def get(repo_id = None, branch_id = None, table_id=None):
    """Use this function to get data from Datahub"""

    if not repo_id:
        raise ValueError('Repo id is not specified')

    config = ApiConfig()
    client = ApiClient(config.domain, config.api_key)

    datum = client.get_dataset(repo_id, branch_id, table_id) if repo_id else None
    return pd.Dataframe(datum)
    