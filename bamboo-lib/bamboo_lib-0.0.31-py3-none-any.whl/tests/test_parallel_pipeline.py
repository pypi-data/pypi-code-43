import pytest
import os
from bamboo_lib.models import Parameter, EasyPipeline, PipelineStep, ParallelizedStep
from bamboo_lib.logger import logger


class CheckStep(PipelineStep):
    def run_step(self, prev_result, params):
        print("RESULT!!", prev_result, "\n")
        return prev_result


class MyParStep(ParallelizedStep):
    def __init__(self, ppl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ppl = ppl

    def parallel_param_list(self, _x):
        return self.ppl

    def run_step(self, _prev, params):
        logger.debug("DOWNLOAD STEP")
        # Download Cube (URL defined in conns.yaml file.)
        # This step will save the contents of the connector target
        # to a file and then pass a file path to the next step
        if "country" in params:
            return "{}-{}".format(params["country"], params["year"])
        return params["year"]


class ExamplePipeline(EasyPipeline):
    @staticmethod
    def steps(params):
        step1 = MyParStep(params["ppl"])
        step2 = CheckStep()
        return [step1, step2]


def build_pipeline():
    pp = ExamplePipeline()
    return pp


def test_parallel_pipeline_value_error():
    with pytest.raises(ValueError):
        pipeline = build_pipeline()
        pipeline.run({"ppl": {"year": 2015}})


def test_parallel_pipeline_ok_simple_dict():
    pipeline = build_pipeline()
    res = pipeline.run({"ppl": {"year": [2015, 2016]}})
    assert res == [2015, 2016]


def test_parallel_pipeline_value_xproduct_dict():
    pipeline = build_pipeline()
    res = pipeline.run({"ppl": {"year": [2015, 2016], "country": ["us", "uk"]}})
    expected_vals = set(["us-2015", "us-2016", "uk-2015", "uk-2016"])
    assert set(res) == expected_vals


def test_parallel_pipeline_value_list():
    pipeline = build_pipeline()
    res = pipeline.run({"ppl": [
        {"year": 2015, "country": "us"},
        {"year": 2016, "country": "us"},
        {"year": 2015, "country": "uk"},
        {"year": 2016, "country": "uk"}
    ]})
    expected_vals = set(["us-2015", "us-2016", "uk-2015", "uk-2016"])
    assert set(res) == expected_vals
