import pandas as pd
from bamboo_lib.models import Parameter, EasyPipeline, PipelineStep
from bamboo_lib.steps import DownloadStep


class TransformStep(PipelineStep):
    def run_step(self, prev_result, params):
        return [params["year"], params["mystr"], params["mybool"]]


class ExamplePipeline(EasyPipeline):
    @staticmethod
    def parameter_list():
        return [
            Parameter("year", dtype=int, default_value=1999),
            Parameter("mystr", dtype=str, default_value="test"),
            Parameter("mybool", dtype=bool, default_value=False),

        ]

    @staticmethod
    def steps(params):
        xform_step = TransformStep()
        return [xform_step]


def test_default_parameters():
    pipeline = ExamplePipeline()
    year, mystr, mybool = pipeline.run({})
    assert year == 1999
    assert mystr is "test"
    assert mybool is False

def test_overide_parameters():
    pipeline = ExamplePipeline()
    year, mystr, mybool = pipeline.run({"year": 2001, "mystr": "pixel"})
    assert year == 2001
    assert mystr is "pixel"
    assert mybool is False
