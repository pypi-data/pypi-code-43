from abc import ABC, abstractmethod
from typing import Dict, Any, List

from google.cloud import bigquery


class Reader(ABC):
    @abstractmethod
    def execute(self, query) -> List[Dict[str, Any]]:
        """
        Return a list of dicts of the results
        E.g. [{'col1': 213, 'col2': 234}, {'col1': 454, 'col2': 565}]
        """
        pass


class BigQueryReader(Reader):
    def __init__(self, json_credentials_path=None):
        if json_credentials_path:
            self.client = bigquery.Client.from_service_account_json(json_credentials_path=json_credentials_path)
        else:
            self.client = bigquery.Client()

    def execute(self, query) -> List[Dict[str, Any]]:
        query_job = self.client.query(query)
        return [{item[0]:item[1] for item in row.items()} for row in query_job]


