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

from ncapi_client.utils import map_response
from time import sleep


class Job:
    """Job"""

    def __init__(self, client, uuid):
        """__init__

        Args:
            client: API client object
            uuid (str): uuid or name of the dataset
        """
        self._session = client._session
        self.url = client.url
        self.uuid = uuid

    @map_response
    def delete(self):
        """Delete this job."""
        return self._session.delete(f"{self.url}/api/jobs/{self.uuid}")

    @property
    @map_response
    def info(self):
        """Get info on the conversion job."""
        return self._session.get(f"{self.url}/api/jobs/{self.uuid}")

    @map_response
    def stop(self):
        """Stop a job."""
        return self._session.post(f"{self.url}/api/jobs/{self.uuid}/stop")

    @map_response
    def restart(self):
        """Restart a job."""
        return self._session.post(f"{self.url}/api/jobs/{self.uuid}/restart")
