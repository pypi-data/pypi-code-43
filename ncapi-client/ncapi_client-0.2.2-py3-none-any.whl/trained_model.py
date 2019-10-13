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

from ncapi_client.utils import (
    map_response,
    handle_response,
    AttrDict,
    delete_dependent_jobs,
)
from io import BytesIO
import glob
import re
import yaml


class TrainedModel:
    """TrainedModel"""

    def __init__(self, client, uuid):
        """__init__

        Args:
            client: API client object
            uuid (str): uuid or name of the trained model
        """
        self._session = client._session
        self.url = client.url
        self.uuid = uuid
        # needed to force delete, not very nice though
        self._client = client

    @staticmethod
    def add(client, config, checkpoint, stamp=None):
        """Add a new trained model

        Args:
            config: trained model config
            checkpoint: compatible §model training checkpoint

        Returns:
            new TrainedModel
        """
        files = [
            ("checkpoint", open(path, "rb")) for path in glob.glob(f"{checkpoint}.*")
        ]
        if stamp is not None:
            with open(config) as f:
                cfg = yaml.safe_load(f)
            cfg["model"]["revision"] = stamp
            with open(config, "w") as f:
                yaml.dump(cfg, f)
        files += [("config", open(config, "rb"))]
        resp = handle_response(
            client._session.post(f"{client.url}/api/trained_model/add", files=files)
        )
        return TrainedModel(client, resp["uuid"])

    @map_response
    def delete(self, force=False):
        """delete
        Args:
            force (bool): force deletion of dependent resources (default False)
        """
        if force:
            delete_dependent_jobs(self._client, {"trained_model": self.info.uuid})
        return self._session.delete(f"{self.url}/api/trained_model/{self.uuid}")

    @property
    @map_response
    def info(self):
        """Trained model info"""
        return self._session.get(f"{self.url}/api/trained_model/{self.uuid}")

    @property
    def config(self):
        """Trained model config"""
        resp = handle_response(
            self._session.get(f"{self.url}/api/trained_model/{self.uuid}/config")
        )
        return AttrDict.convert(resp["model"])

    def download(self):
        """Download this trained model as a tar.gz archive
        
        Returns:
            BytesIO: tar.gz archive as bytes
        """
        resp = self._session.get(f"{self.url}/api/trained_model/{self.uuid}/download")
        resp.raise_for_status()
        buff = BytesIO(resp.content)
        buff.name = re.findall("filename=(.+)", resp.headers["content-disposition"])[0]
        return buff
