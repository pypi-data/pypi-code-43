"""
 NEURAL CONCEPT CONFIDENTIAL
 __________________
 
  [2018] Neural Concept SA-SARL, Lausanne, Switzerland
  All Rights Reserved.
 
 If you are reading this NOTICE as a result of a de-obfuscation
 or a reverse Engineering of Neural Concept’s software, you are likely
 breaking Neural Concept Shape’s End-User Licence Agreement. 
 Please contact Neural Concept Sarl without any delay.

 NOTICE:  All information contained herein is, and remains
 the property of Neural Concept and its suppliers,
 if any.  The intellectual and technical concepts contained
 herein are proprietary to Neural Concept
 and its suppliers and may be covered by European and Foreign Patents,
 patents in process, and are protected by trade secret or copyright law.
 Dissemination or usage of this information or reproduction of this material
 is strictly forbidden unless prior written permission is obtained
 from Neural Concept.
 Usage of file or code is subject to the terms and conditions defined in
 Neural Concept Shape’s End-User Licence Agreement.
""" 

import os

import requests
from ncapi_client.dataset import Dataset
from ncapi_client.job import Job
from ncapi_client.model import Model
from ncapi_client.prediction import Prediction
from ncapi_client.session import Session
from ncapi_client.trained_model import TrainedModel
from ncapi_client.training import Training
from ncapi_client.utils import map_response, ResourceList, handle_response


class Client:
    """All-in-one client for NCAPI"""

    def __init__(self, url=None, username=None, password=None, access_token=None):
        """__init__

        Args:
            url (str): url where the API is served
            username (str): username for authentication
            password (str): password for authentication
            access_token (str): JWT access token
        """

        url = url or os.environ.get("NCAPI_URL")
        username = username or os.environ.get("NCAPI_USERNAME")
        password = password or os.environ.get("NCAPI_PASSWORD")
        access_token = access_token or os.environ.get("NCAPI_ACCESS_TOKEN")
        ssl_cert = os.environ.get("NCAPI_CERT")

        self._session = requests.Session()

        self._session.verify = ssl_cert or True

        if username and password and url:
            self.url = url
            resp = self._login(username, password)
            self.access_token = resp.access_token
        elif access_token and url:
            self.url = url
            self.access_token = access_token
        else:
            raise ValueError(
                "You should specify username-password-url or access_token-url: "
                "either explicitly or through environment variables"
            )

    def __repr__(self):
        return f"Client({self.url})"

    @map_response
    def _login(self, username, password):
        payload = dict(username=username, password=password)
        return self._session.post(f"{self.url}/api/user/login", json=payload)

    @property
    def datasets(self):
        """List of datasets"""
        dataset_list = handle_response(self._session.get(f"{self.url}/api/dataset"))
        return ResourceList([Dataset(self, info["uuid"]) for info in dataset_list])

    @property
    def models(self):
        """List of models"""
        model_list = handle_response(self._session.get(f"{self.url}/api/model"))
        return ResourceList([Model(self, info["uuid"]) for info in model_list])

    @property
    def trainings(self):
        """List of trainings"""
        trainings = handle_response(self._session.get(f"{self.url}/api/training"))
        return ResourceList([Training(self, info["uuid"]) for info in trainings])

    @property
    def trained_models(self):
        """List of trained models"""
        trained_models = handle_response(
            self._session.get(f"{self.url}/api/trained_model")
        )
        return ResourceList(
            [TrainedModel(self, info["uuid"]) for info in trained_models]
        )

    @property
    def jobs(self):
        """List of jobs"""
        jobs = handle_response(self._session.get(f"{self.url}/api/jobs"))
        return ResourceList([Job(self, info["uuid"]) for info in jobs])

    @property
    def predictions(self):
        """List of predictions"""
        predictions = handle_response(self._session.get(f"{self.url}/api/prediction"))
        return ResourceList([Prediction(self, info["uuid"]) for info in predictions])

    @property
    def sessions(self):
        """List of sessions"""
        sessions = handle_response(self._session.get(f"{self.url}/api/session/list"))
        return ResourceList([Session(self, info["id"]) for info in sessions])
