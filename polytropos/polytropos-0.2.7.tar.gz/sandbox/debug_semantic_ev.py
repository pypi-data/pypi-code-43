import os

from polytropos.ontology.schema import Schema
from polytropos.tools.qc.findall import FixtureOutcomes

actual_dir: str = os.path.join("/tmp/KhqSwztaQr/entities/nonprofit", "semantic")
basepath: str = "/dmz/github/analysis/etl5"
fixture_dir: str = os.path.join(basepath, "fixtures", "semantic")
schema_basepath: str = os.path.join(basepath, "schemas")
schema: Schema = Schema.load("nonprofit/semantic", base_path=schema_basepath)
FixtureOutcomes(schema, fixture_dir, actual_dir)

