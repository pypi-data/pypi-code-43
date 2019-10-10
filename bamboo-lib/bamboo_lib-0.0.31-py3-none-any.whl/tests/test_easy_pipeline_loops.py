import os

import pandas as pd
from bamboo_lib.models import Parameter, EasyPipeline, PipelineStep, LoopHelper
from bamboo_lib.steps import UnzipStep
from bamboo_lib import helpers


class GetDataStep(PipelineStep):
    def run_step(self, prev_result, params):
        return os.path.join(helpers.grab_parent_dir(__file__), "data", "food.zip")


class TransformStep1(PipelineStep):
    def run_step(self, prev_result, params):
        return pd.read_csv(prev_result)


class ExamplePipeline1(EasyPipeline):
    @staticmethod
    def parameter_list():
        return [
            Parameter("year", dtype=int),
        ]

    @staticmethod
    def steps(params):
        get_data_step = GetDataStep()
        unzip_step = UnzipStep(pattern=r"\.csv$")
        xform_step = TransformStep1()
        return [get_data_step, LoopHelper(iter_step=unzip_step, sub_steps=[xform_step])]


def test_easy_pipeline_loop_basic():
    pipeline = ExamplePipeline1()
    res = pipeline.run({"year": 2016})
    assert isinstance(res, pd.DataFrame)
    assert len(res) > 0
