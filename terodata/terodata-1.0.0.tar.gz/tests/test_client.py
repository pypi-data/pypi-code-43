# pylint: disable=C0111 # (no docstrings)
# pylint: disable=C0413 # (allow importing local modules below sys path config)

import sys
import tempfile
import shutil
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from terodata import TeroDataClient


def test_get_datasets():
    cli = TeroDataClient()
    results = cli.get_datasets()
    assert "sentinel1" in results["datasets"]


# ====================================
# Dataset metadata
# ====================================
def test_get_dataset():
    cli = TeroDataClient()
    results = cli.get_dataset("sentinel1")
    assert results["id"] == "sentinel1"


def test_get_dataset_not_found():
    cli = TeroDataClient()
    with pytest.raises(Exception) as err:
        cli.get_dataset("foo")
    assert "DATASET_NOT_FOUND" in str(err.value)


# ====================================
# Queries
# ====================================
def test_create_query_job():
    cli = TeroDataClient()
    attrs = {
        "productType": "GRD",
        "tStart": "2018-10-01",
        "tEnd": "2018-10-05",
        "aoi": "POINT(2 41)",
    }
    results = cli.create_query_job("sentinel1", attrs)
    assert results["id"]
    assert results["attrs"]
    assert results["status"]


def test_create_query_job_dataset_not_found():
    cli = TeroDataClient()
    attrs = {
        "productType": "GRD",
        "tStart": "2018-10-01",
        "tEnd": "2018-10-05",
        "aoi": "POINT(2 41)",
    }
    with pytest.raises(Exception) as err:
        cli.create_query_job("foo", attrs)
    assert "DATASET_NOT_FOUND" in str(err.value)


def test_create_query_job_invalid_query_select():
    cli = TeroDataClient()
    attrs = {"productType": "GTRD"}
    with pytest.raises(Exception) as err:
        cli.create_query_job("sentinel1", attrs)
    assert "INVALID_QUERY" in str(err.value)


def test_create_query_job_invalid_query_date():
    cli = TeroDataClient()
    attrs = {"tStart": "foo"}
    with pytest.raises(Exception) as err:
        cli.create_query_job("sentinel1", attrs)
    assert "INVALID_QUERY" in str(err.value)


def test_create_query_job_invalid_query_date_range():
    cli = TeroDataClient()
    attrs = {"tStart": "2018-10-05", "tEnd": "2018-10-01"}
    with pytest.raises(Exception) as err:
        cli.create_query_job("sentinel1", attrs)
    assert "INVALID_QUERY" in str(err.value)


def test_create_get_cancel_query_job():
    cli = TeroDataClient()
    attrs = {"aoi": "POINT(2 41)"}
    results = cli.create_query_job("sentinel1", attrs)
    assert results["status"] == "RUNNING"
    id = results["id"]
    results = cli.get_query_job("sentinel1", id)
    assert results["status"] == "RUNNING"
    results = cli.cancel_query_job("sentinel1", id)
    assert results is None
    results = cli.get_query_job("sentinel1", id)
    assert results["status"] == "CANCELED"


def test_query():
    cli = TeroDataClient(log=False)
    attrs = {
        "productType": "GRD",
        "tStart": "2018-10-01",
        "tEnd": "2018-10-05",
        "aoi": "POINT(2 41)",
    }
    results = cli.query("sentinel1", attrs)
    assert results["id"]
    assert results["status"] == "FINISHED"
    assert results["progress"] == 100


# ====================================
# Downloads
# ====================================
def test_create_download_job():
    tmp_dir = tempfile.mkdtemp(prefix="hdaTest-")
    results = None
    try:
        cli = TeroDataClient()
        granule_ids = ["52126fdb-8eb5-4342-8515-d7c371b51069"]
        results = cli.create_download_job("sentinel1", granule_ids, output_path=tmp_dir)
        assert results["id"]
        assert results["maxSize"]
        assert results["status"]
    finally:
        if results:
            cli.cancel_download_job("sentinel1", results["id"])
        shutil.rmtree(tmp_dir)


def test_create_download_job_too_large():
    tmp_dir = tempfile.mkdtemp(prefix="hdaTest-")
    results = None
    try:
        cli = TeroDataClient()
        granule_ids = ["52126fdb-8eb5-4342-8515-d7c371b51069"]
        with pytest.raises(Exception) as err:
            results = cli.create_download_job(
                "sentinel1", granule_ids, output_path=tmp_dir, max_size=1
            )
        assert "JOB_TOO_LARGE" in str(err.value)
    finally:
        if results:
            cli.cancel_download_job("sentinel1", results["id"])
        shutil.rmtree(tmp_dir)


def test_create_download_job_granule_not_found():
    tmp_dir = tempfile.mkdtemp(prefix="hdaTest-")
    results = None
    try:
        cli = TeroDataClient()
        granule_ids = ["foo"]
        with pytest.raises(Exception) as err:
            results = cli.create_download_job(
                "sentinel1", granule_ids, output_path=tmp_dir
            )
        assert "GRANULE_NOT_FOUND" in str(err.value)
    finally:
        if results:
            cli.cancel_download_job("sentinel1", results["id"])
        shutil.rmtree(tmp_dir)


def test_create_get_cancel_download_job():
    tmp_dir = tempfile.mkdtemp(prefix="hdaTest-")
    results = None
    try:
        cli = TeroDataClient()
        granule_ids = ["52126fdb-8eb5-4342-8515-d7c371b51069"]
        results = cli.create_download_job("sentinel1", granule_ids, output_path=tmp_dir)
        assert results["status"] == "RUNNING"
        id = results["id"]
        results = cli.get_download_job("sentinel1", id)
        assert results["status"] == "RUNNING"
        results = cli.cancel_download_job("sentinel1", id)
        assert results is None
        results = cli.get_download_job("sentinel1", id)
        assert results["status"] == "CANCELED"
    finally:
        if results:
            cli.cancel_download_job("sentinel1", results["id"])
        shutil.rmtree(tmp_dir)


def test_download():
    tmp_dir = tempfile.mkdtemp(prefix="hdaTest-")

    def on_progress(id, status, progress):
        if status == "RUNNING":
            cli.cancel_download_job("sentinel1", id)

    results = None
    try:
        cli = TeroDataClient()
        granule_ids = ["52126fdb-8eb5-4342-8515-d7c371b51069"]
        with pytest.raises(Exception) as err:
            results = cli.download(
                "sentinel1", granule_ids, output_path=tmp_dir, on_progress=on_progress
            )
        assert "JOB_CANCELED" in str(err.value)
    finally:
        if results:
            cli.cancel_download_job("sentinel1", results["id"])
        shutil.rmtree(tmp_dir)
