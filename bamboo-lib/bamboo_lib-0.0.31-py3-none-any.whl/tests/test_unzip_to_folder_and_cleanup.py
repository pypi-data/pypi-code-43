import os
import tempfile
from bamboo_lib.models import EasyPipeline, PipelineStep
from bamboo_lib.steps import CleanupFileStep, UnzipToFolderStep
from bamboo_lib import helpers

TARGET_DIR = os.path.join(tempfile.gettempdir(), "my-unzip-test")


class CheckStatusStep(PipelineStep):
    def run_step(self, prev_result, params):
        # assert False
        unzipped_dir_files = os.listdir(TARGET_DIR)
        assert os.path.exists(TARGET_DIR)
        assert "food1.csv" in unzipped_dir_files
        assert "food2.csv" in unzipped_dir_files
        return prev_result


class GetDataStep(PipelineStep):
    def run_step(self, prev_result, params):
        return os.path.join(helpers.grab_parent_dir(__file__), "data", "food.zip")


class ExamplePipeline(EasyPipeline):
    @staticmethod
    def steps(params):
        get_data_step = GetDataStep()
        check_unzip_status = CheckStatusStep()
        unzip_step = UnzipToFolderStep(target_folder_path=TARGET_DIR)
        cleanup_folder = CleanupFileStep(use_prev_result=True)
        return [get_data_step, unzip_step, check_unzip_status, cleanup_folder]


def test_easy_pipeline_basic():
    pipeline = ExamplePipeline()
    pipeline.run({})
    assert not os.path.exists(TARGET_DIR)
