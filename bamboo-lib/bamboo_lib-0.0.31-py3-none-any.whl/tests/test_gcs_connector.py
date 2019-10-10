# test_capitalize.py
import pytest
import pandas as pd
import os
from bamboo_lib.models import PipelineStep, AdvancedPipelineExecutor
from bamboo_lib.helpers import grab_connector
from bamboo_lib.steps import WildcardDownloadStep, DownloadStep


class DisplayStep(PipelineStep):
    def run_step(self, prev_result, params):
        print("RESULT:", prev_result, "\n")
        return prev_result



@pytest.fixture()
def oec_pipeline():
    source_connector = grab_connector(__file__, "gcs-oec-simple")
    http_dl_step = DownloadStep(connector=source_connector, force=True)
    show_step = DisplayStep()
    pp = AdvancedPipelineExecutor({})
    pp = pp.next(http_dl_step).next(show_step)
    return pp


@pytest.fixture()
def oec_wc_pipeline():
    source_connector = grab_connector(__file__, "gcs-oec-wildcard")
    http_dl_step = WildcardDownloadStep(connector=source_connector, force=True)
    show_step = DisplayStep()
    pp = AdvancedPipelineExecutor({})
    pp = pp.next(http_dl_step).next(show_step)
    return pp

@pytest.fixture()
def oec_wc_pipeline_params():
    source_connector = grab_connector(__file__, "gcs-oec-wildcard-param")
    http_dl_step = WildcardDownloadStep(connector=source_connector, force=True)
    show_step = DisplayStep()
    pp = AdvancedPipelineExecutor({"country_code": "bra"})
    pp = pp.next(http_dl_step).next(show_step)
    return pp

def test_oec_gcs_dl(oec_pipeline):
    res = oec_pipeline.run_pipeline()
    df = pd.read_csv(res, compression="zip")
    assert len(df) == 21324

def test_oec_gcs_wildcard_dl(oec_wc_pipeline):
    result_list = oec_wc_pipeline.run_pipeline()
    local_fp, params = result_list[0]
    assert local_fp == '/tmp/0b2a2fa50fae59eec31f4035df2de2e39a429b173a012f0b4f78cba7'
    assert params['extracted'] == '20190521'
    assert params['published'] == '20180724'

def test_oec_gcs_wildcard_dl_w_param(oec_wc_pipeline_params):
    result_list = oec_wc_pipeline_params.run_pipeline()
    assert len(result_list) >= 1
    assert result_list[0][0] == '/tmp/cac05845fa797bbe2c1906c0b599d969a666040e3f59666f59f2b338'