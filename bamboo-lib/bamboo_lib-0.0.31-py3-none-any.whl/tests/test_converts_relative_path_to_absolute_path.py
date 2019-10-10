from bamboo_lib.models import Parameter, EasyPipeline, PipelineStep, LoopHelper
from bamboo_lib import helpers
from bamboo_lib.exceptions import AbsolutePathException

class CheckFileStep(PipelineStep):
    def run_step(self, prev_result, params):
        result = helpers.convert_to_absolute(params["filetstartpoint"], params["filepath"])
        return result


class ExamplePipeline(EasyPipeline):
    @staticmethod
    def parameter_list():
        return [
            Parameter("filepath", dtype=str),
            Parameter("filetstartpoint", dtype=str),
        ]

    @staticmethod
    def steps(params):
        checkfile = CheckFileStep()
        return [checkfile]


def test_conversion_to_absolute_path():
    pipeline = ExamplePipeline()
    res = pipeline.run({"filepath": "resource/candidate_mapping.csv", "filetstartpoint": "/user/desktop/test"})
    assert res == "/user/desktop/test/resource/candidate_mapping.csv"
    # when given a relative path it should raise an error
    try:
        res1 = pipeline.run({"filepath": "resource/candidate_mapping.csv", "filetstartpoint": "user/desktop/test"})
        assert False
    except AbsolutePathException:
        assert True
