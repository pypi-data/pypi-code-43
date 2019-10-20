
from __future__ import absolute_import
import apache_beam as beam
from paralelocs_beam.utils.bigquery import BigQueryUtils

__all__ = ['ParseFields']


class ParseFields(beam.PTransform):

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        self.bigquery = BigQueryUtils(schema)

    def expand(self, pcoll):
        return (pcoll | 'Parsing fields to Bigquery' >> beam.Map(self.bigquery._convert_fields_to_bigquery))
