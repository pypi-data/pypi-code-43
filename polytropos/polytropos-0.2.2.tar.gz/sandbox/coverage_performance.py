import logging
import time

from polytropos.actions.consume.coverage import CoverageFile
from typing import Optional, cast

from polytropos.ontology.variable import VariableId

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

start: float = time.time()
CoverageFile.standalone("/dmz/github/analysis/etl5/schemas/",
                        "nonprofit/origin",
                        "/tmp/sample",
                        "/tmp/sample_coverage",
                        cast(VariableId, "origin_temporal_000997"),
                        None)
elapsed: float = time.time() - start
print(elapsed)
