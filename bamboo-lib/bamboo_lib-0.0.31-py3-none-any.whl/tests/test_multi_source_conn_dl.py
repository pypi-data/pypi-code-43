# test_capitalize.py
import pytest
import os
import pandas as pd
from bamboo_lib.models import PipelineStep, AdvancedPipelineExecutor
from bamboo_lib.helpers import grab_connector

from bamboo_lib.steps import DownloadStep


class DisplayStep(PipelineStep):
    def run_step(self, prev_result, params):
        print("RESULT:", prev_result, "\n")
        dfs = [pd.read_json(pth, orient="records", typ='series').to_frame() for pth in prev_result]
        df = pd.concat(dfs).reset_index()
        return df


@pytest.fixture()
def pipeline():
    source_connector1 = grab_connector(__file__, "http-local")
    source_connector2 = grab_connector(__file__, "http-local-2")
    source_connector3 = grab_connector(__file__, "http-local-3")
    my_connectors = [source_connector1, source_connector2, source_connector3]
    http_multi_dl_step = DownloadStep(connector=my_connectors)
    show_step = DisplayStep()
    pp = AdvancedPipelineExecutor({})
    pp = pp.next(http_multi_dl_step).next(show_step)
    return pp


def test_dl_default_path(pipeline):
    res = pipeline.run_pipeline()
    # assert res == "/tmp/999f2fa455aff231b7daa3680efdb03abd078fa1b009e38677c42d24"
    # print(res[res.index == "id"])
    my_ids = res[res['index'] == "id"][0].values
    print("Retrieved IDs:", my_ids)
    assert len(my_ids) == 3
    assert 1 in my_ids
    assert 2 in my_ids
    assert 3 in my_ids
