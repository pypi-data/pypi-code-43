from polytropos.ontology.schema import Schema
from polytropos.tools.qc.findall import FixtureOutcomes

schema: Schema = Schema.load("nonprofit/semantic", base_path="/dmz/github/analysis/etl5/schemas")
fixture_path: str = "/dmz/github/analysis/etl5/fixtures/semantic"
output_path: str = "/tmp/hJatWfnoXT/entities/nonprofit/semantic"
FixtureOutcomes(schema, fixture_path, output_path)