#polytropos schema catalog /dmz/github/analysis/etl5/schemas nonprofit/origin /tmp/origin_catalog.csv
import logging
from typing import TextIO

from polytropos.tools.schema.catalog import variable_catalog

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

schema_basepath: str = "/dmz/github/analysis/etl5/schemas"
schema_name: str = "nonprofit/origin"
output_file: TextIO = open("/tmp/origin.csv", "w")
variable_catalog(schema_basepath, schema_name, output_file)
