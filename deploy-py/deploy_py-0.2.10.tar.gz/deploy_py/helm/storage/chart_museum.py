import requests

import yaml

from ...logging import get_logger


class ChartMuseum:
    def __init__(self, url, name, caFile="", cache="", certFile="", keyFile="", password="", username="", verbosity=1):
        self.logger = get_logger("deploy.helm.ChartMuseum", level=verbosity)
        self.url = url
        self.name = name
        self.caFile = caFile
        self.cache = cache
        self.certFile = certFile
        self.keyFile = keyFile
        self.password = password
        self.username = username

    @classmethod
    def from_file(cls, file_path, name):
        with open(file_path) as raw_file:
            repo_file = yaml.safe_load(raw_file)
        for repo in repo_file:
            if repo["name"] == name:
                return ChartMuseum(**repo)
        raise Exception("no repo in file. REPLACE ME WITH A REAL EXCEPTION")

    def delete_url(self, chart_name, version):
        return f"{self.url}/api/charts/{chart_name}/{version}"

    def upload_url(self):
        return f"{self.url}/api/charts"

    def delete(self, chart_name: str, version: str) -> requests.Response:
        self.logger.info(f"removing previous Helm chart {chart_name}/{version}")
        resp = requests.delete(self.delete_url(chart_name, version), auth=(self.username, self.password))
        if resp.status_code == 404:
            self.logger.warn(f"chart not found; skipping delete")
        elif resp.status_code in range(400, 599):
            self.logger.warn(f"error deleting chart: {resp.json()}")
        return resp

    def upload(self, repo_name: str, file_path: str):
        with open(file_path, "rb") as chart:
            files = {"chart": chart}
            repo = self.get_repo(repo_name)
            self.logger.info(f"uploading Helm chart to {repo.url}")
            resp = requests.post(self.upload_url(), files=files, auth=(repo.username, repo.password))
            if resp.status_code not in range(200, 299):
                raise Exception(f"error uploading Helm chart: {resp.json()}")
