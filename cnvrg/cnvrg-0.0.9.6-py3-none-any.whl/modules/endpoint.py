from cnvrg.modules.cnvrg_job import CnvrgJob
from cnvrg.modules.project import Project
import cnvrg.helpers.string_helper as string_helper
import cnvrg.helpers.param_build_helper as param_build_helper
from cnvrg.helpers.env_helper import CURRENT_JOB_TYPE, CURRENT_JOB_ID, ENDPOINT, POOL_SIZE
from cnvrg.modules.errors import UserError
from cnvrg.helpers.url_builder_helper import url_join
import cnvrg.helpers.parallel_helper as parallel_helper
import cnvrg.helpers.apis_helper as apis_helper
import json
import time
import os
import requests


class Endpoint(CnvrgJob):
    def __init__(self, endpoint=None):
        owner, project_slug, slug = param_build_helper.parse_params(endpoint, param_build_helper.ENDPOINT)
        if not slug:
            raise UserError("Cant create an endpoint without slug")
        slug = slug or CURRENT_JOB_ID
        super(Endpoint, self).__init__(slug, ENDPOINT, Project(url_join(owner, project_slug)))
        self.__data = None


    def __base_log(self, **params):
        model_name = os.environ.get("CNVRG_MODEL_NAME", "unknown")
        log = {
            "job_id": self.job_slug,
            "job_type": self.job_type,
            "owner": self.job_owner_slug,
            "project": self.job_project_slug,
            "model": model_name,
            "event_time": time.time(),
            **params
        }
        print(json.dumps(log))

    def log_param(self, tag_name=None, tag_value=None):
        hash = {}
        hash[tag_name] = tag_value
        hash["cnvrg_tag_name"] = tag_name
        self.__base_log(**hash)

    def log_metric(self, name=None, y=None, x=None):
        hash = {}
        try:
            hash[name] = float(y)
            hash["y"] = float(y)
        except Exception as e:
            print("ERROR {}".format(e))
            exit(1)
        hash["x"] = x
        hash["cnvrg_metric_name"] = name
        self.__base_log(**hash)

    @property
    def session(self):
        return self.__session()

    @property
    def data(self):
        if self.__data:
            return self.__data
        self.__data = self.__get_endpoint()
        return self.__data

    def __get_endpoint(self):
        return apis_helper.get(self.__base_url()).get("endpoint")

    def __base_url(self):
        return url_join(
            self.project.get_base_url(), string_helper.to_snake_case(self.job_type) + "s", self.job_slug
        )

    def __session(self):
        session = requests.session()
        session.headers = {
            **apis_helper.JSON_HEADERS,
            "Cnvrg-Api-Key": self.data.get("api_key")
        }
        return session

    def predict(self, o):
        return self.session.post(self.data.get("endpoint_url"), data=json.dumps({"input_params": o})).json()

    def single_batch_predict(self, o):
        prediction = self.predict(o)
        if isinstance(o, dict):
            return {**o, **prediction}
        else:
            return {"query": o, **prediction}

    def batch_predict(self, array: list, pool_size: int=POOL_SIZE):
        return parallel_helper.safe_parallel(self.single_batch_predict, array, pool_size=pool_size, progressbar={"total": len(array), "desc": "Predicting"})