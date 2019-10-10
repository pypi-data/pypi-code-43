from bamboo_lib.models import EasyPipeline, PipelineStep


class Step1(PipelineStep):
    def run_step(self, prev_result, params):
        return "here-it-is"


class Step2(PipelineStep):
    def run_step(self, prev_result, params):
        return "there-it-is"


class Step3(PipelineStep):
    def run_step(self, prev_result, params):
        my_results = self.get_pipeline_results_ref()
        return "{}+{}".format(my_results["result1"], my_results["result2"])


class ExamplePipeline(EasyPipeline):
    @staticmethod
    def steps(params):
        return [Step1(save_result_key="result1"), Step2(save_result_key="result2"), Step3()]


def test_easy_pipeline_basic():
    pipeline = ExamplePipeline()
    res = pipeline.run({})
    assert res == "here-it-is+there-it-is"
