"""
            etl5 coverage ./schemas/ nonprofit/semantic output/entities/nonprofit/semantic \
                artifacts/coverage/actual/semantic/semantic_actual --t-group semantic_temporal_000009
"""
from typing import cast, Optional
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from polytropos.actions.consume.coverage import CoverageFile

from polytropos.ontology.context import Context
from polytropos.ontology.variable import VariableId

data_path: str = "/tmp/coverage_test"
schema_basepath: str = "/dmz/github/analysis/etl5/schemas"
schema_name: str = "nonprofit/semantic"
output_prefix: str = "/tmp/semantic_debug"
t_group: VariableId = cast(VariableId, "semantic_temporal_000009")

with Context.build("", "", input_dir=data_path, schemas_dir=schema_basepath, steppable_mode=True) as context:
    CoverageFile.standalone(context, schema_name, output_prefix, cast(Optional[VariableId], t_group),
                            cast(Optional[VariableId], None))
