from __future__ import absolute_import
from apache_beam.io.gcp.bigquery_tools import parse_table_schema_from_json
import json

__all__ = ['BigQueryUtils']

class BigQueryUtils():
    
    """
    Example
    __SCHEMA = [
                    {
                        'name':'po',
                        'type':'STRING',
                        'mode':'REQUIRED'
                    },
                    {
                        'name':'total',
                        'type':'FLOAT',
                        'mode':'REQUIRED'
                    }
                ]

    """

    def __init__(self, schema):
        self.schema = schema


    def get_schema(self):
        schema = '{"fields":' + json.dumps(self.schema) + '}'
        return parse_table_schema_from_json(schema)

    def _convert_fields_to_bigquery(self, row):
        datefields = []
        floatfields = []

        for fields in self.schema:
            if fields['type'] == 'DATETIME':
                datefields.append(fields['name'])
            elif fields['type'] == 'FLOAT':
                floatfields.append(fields['name'])
        
        for datefield in datefields:
            row[datefield] = row[datefield].strftime("%Y-%m-%d %H:%M:%S.%f")
        
        for floatfield in floatfields:
            row[floatfield] = float(row[floatfield])
    
        return row