"""main package module"""

from datahub.config import Config
from datahub.api import Client
import pandas as pd
import json

def get(repo_id = None, branch_id = None, table_id = None):
    """Use this function to get data from Datahub"""

    if not repo_id:
        raise ValueError('Repo id is not specified')

    config = Config()
    client = Client(config.domain, config.api_key)

    datum = client.get_dataset(repo_id, branch_id, table_id)
    return json.loads(json.dumps(datum.__dict__))

def upsert_commit(df = None, repo_id = None, branch_id = None, table_id=None):
    """Use this function to push a commit on Datahub"""
    if not df:
        raise ValueError('Pandas Dataframe is not passed')

    config = Config()
    client = Client(config.domain, config.api_key)

    try:
        datum_main = {}
        datum_list = []
        datum_dict = {}
        datum_dict["repo"] = "repo_id"
        datum_dict["branch"] = "branch_id"
        datum_dict["dataset"] = "dataset"
        datum_dict['txdata'] = df.to_json(orient='columns')
        datum_dict['op'] = "UPSERT"
        datum_list.append(datum_dict)
        datum_main['txdata'] = datum_list
        return client.post_commit(repo_id, branch_id, table_id, datum_main)
    except Exception as e:
        raise ValueError('Error: While upserting the data')