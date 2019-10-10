import pandas as pd
from bamboo_lib.models import Parameter, EasyPipeline, PipelineStep
from bamboo_lib.steps import DownloadStep


class TransformStep1(PipelineStep):
    def run_step(self, prev_result, params):
        return pd.read_csv(prev_result)


class TransformStep2(PipelineStep):
    def run_step(self, prev_result, params):
        return params["year"]


class ExamplePipeline1(EasyPipeline):
    @staticmethod
    def parameter_list():
        return [
            Parameter("year", dtype=int),
        ]

    @staticmethod
    def steps(params):
        dl_step = DownloadStep(connector="sample-data", connector_path=__file__, force=params.get("force", False))
        xform_step = TransformStep1()
        return [dl_step, xform_step]


class ExamplePipeline2(EasyPipeline):
    @staticmethod
    def parameter_list():
        return [
            Parameter("year", dtype=int),
        ]

    @staticmethod
    def steps(params):
        dl_step = DownloadStep(connector="sample-data", connector_path=__file__, force=params.get("force", False))
        xform_step = TransformStep2()
        return [dl_step, xform_step]


def test_easy_pipeline_basic():
    pipeline = ExamplePipeline1()
    res = pipeline.run({"year": 2016})
    assert isinstance(res, pd.DataFrame)
    assert len(res) > 0


def test_easy_pipeline_param_passing():
    pipeline = ExamplePipeline2()
    res = pipeline.run({"year": 2016})
    assert res == 2016
