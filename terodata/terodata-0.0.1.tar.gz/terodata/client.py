"""
All client requests.
"""

# pylint: disable=C0111 # (no docstrings)

import time
import requests

DEFAULT_BROKER_URL = "http://localhost:3005"
WAIT_QUERY = 3
WAIT_DOWNLOAD = 10


class TeroDataClient:
    def __init__(self, broker=DEFAULT_BROKER_URL, log=True):
        self.base_url = "%s/api" % broker
        self.log = log

    def get_datasets(self):
        url = "%s/datasets" % self.base_url
        return self._get(url)

    def get_dataset(self, dataset_id):
        url = "%s/dataset/%s" % (self.base_url, dataset_id)
        return self._get(url)

    # ====================================
    def create_query_job(self, dataset_id, attrs):
        url = "%s/dataset/%s/query" % (self.base_url, dataset_id)
        return self._post(url, attrs)

    def get_query_job(self, dataset_id, query_id):
        url = "%s/dataset/%s/query/%s" % (self.base_url, dataset_id, query_id)
        return self._get(url)

    def cancel_query_job(self, dataset_id, query_id):
        url = "%s/dataset/%s/query/%s" % (self.base_url, dataset_id, query_id)
        return self._delete(url)

    def query(self, dataset_id, attrs, on_progress=None):
        job = self.create_query_job(dataset_id, attrs)
        self._log_job_status(job, "query", on_progress)
        self._log_job_notes(job, "query", newline=True)
        self._raise_api_exception(job)
        id = job["id"]
        status = job["status"]
        while status != "FINISHED":
            time.sleep(WAIT_QUERY)
            job = self.get_query_job(dataset_id, id)
            self._log_job_status(job, "query", on_progress)
            self._raise_api_exception(job)
            status = job["status"]
            if status == "CANCELED":
                self._raise_custom_exception(
                    410, "JOB_CANCELED", "Query job has been canceled."
                )
        if self.log:
            print("")
        return job

    # ====================================
    def create_download_job(
        self, dataset_id, granule_ids, max_size=None, output_path=None
    ):
        url = "%s/dataset/%s/download" % (self.base_url, dataset_id)
        spec = {
            "granuleIds": granule_ids,
            "maxSize": max_size,
            "outputPath": output_path,
        }
        return self._post(url, spec)

    def get_download_job(self, dataset_id, download_id):
        url = "%s/dataset/%s/download/%s" % (self.base_url, dataset_id, download_id)
        return self._get(url)

    def cancel_download_job(self, dataset_id, download_id):
        url = "%s/dataset/%s/download/%s" % (self.base_url, dataset_id, download_id)
        return self._delete(url)

    def download(
        self, dataset_id, granule_ids, max_size=None, output_path=None, on_progress=None
    ):
        job = self.create_download_job(dataset_id, granule_ids, max_size, output_path)
        self._log_job_status(job, "download", on_progress)
        self._log_job_notes(job, "download", newline=True)
        self._raise_api_exception(job)
        id = job["id"]
        status = job["status"]
        while status != "FINISHED":
            time.sleep(WAIT_QUERY)
            job = self.get_download_job(dataset_id, id)
            self._log_job_status(job, "download", on_progress)
            self._raise_api_exception(job)
            status = job["status"]
            if status == "CANCELED":
                self._raise_custom_exception(
                    410, "JOB_CANCELED", "Download job has been canceled."
                )
        if self.log:
            print("")
        return job

    # ====================================
    # Helpers
    # ====================================
    def _get(self, url):
        return self._request(url)

    def _post(self, url, json):
        return self._request(url, method="post", json=json)

    def _delete(self, url):
        return self._request(url, method="delete")

    def _request(self, url, method="get", json=None):
        if method == "get":
            res = requests.get(url)
        elif method == "post":
            res = requests.post(url, json=json)
        elif method == "delete":
            res = requests.delete(url)
        if res.headers.get("content-type").startswith("application/json"):
            out = res.json()
            self._raise_api_exception(out)
            return out
        res.raise_for_status()
        return None

    def _raise_api_exception(self, res):
        if res is None:
            return
        if "_errorCode" in res:
            if self.log:
                print("")
            msg = "%s %s: %s" % (
                res["_errorHttpStatusCode"],
                res["_errorCode"],
                res["_errorDescription"],
            )
            raise Exception(msg)

    def _raise_custom_exception(self, http_status_code, code, description):
        if self.log:
            print("")
        raise Exception("%s %s: %s" % (http_status_code, code, description))

    def _log_job_status(self, job, job_type, on_progress=None):
        id = job["id"]
        status = job["status"]
        progress = job["progress"]
        if self.log:
            msg = "%s %s job %s: %s%%  " % (status, job_type, id, progress)
            print(msg, end="\r", flush=True)
        if on_progress:
            on_progress(id=id, status=status, progress=progress)

    def _log_job_notes(self, job, job_type, newline=False):
        if (not self.log) or (not "_notes" in job):
            return
        notes = job["_notes"]
        if not notes:
            return
        prefix = "\n" if newline else ""
        print("=====================================================")
        print("%sNotes from the server for %s job %s:" % (prefix, job_type, job["id"]))
        for note in notes:
            print("- %s" % note)
        print("=====================================================")
