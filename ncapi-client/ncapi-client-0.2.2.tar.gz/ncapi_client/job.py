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
