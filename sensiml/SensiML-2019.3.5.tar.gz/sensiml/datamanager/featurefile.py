import os
import datetime
import json
import sensiml.base.utility as utility


class FeatureFile(object):
    """Base class for a featurefile object."""

    def __init__(self, connection, project, name="", path=""):
        self._connection = connection
        self._project = project
        self.uuid = None
        self._created_at = None
        self.name = name
        self.path = path

    # Maintain campatibility with old filename attr
    @property
    def filename(self):
        """The name of the file as stored on the server

        Note:
            Filename must contain a .csv or .arff extension
        """
        return self.name

    @filename.setter
    def filename(self, value):
        self.name = value

    @property
    def created_at(self):
        """Date of the Pipeline creation"""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        self._created_at = datetime.datetime.strptime(
            value[:-6], "%Y-%m-%dT%H:%M:%S.%f"
        )

    def insert(self):
        """Calls the REST API to insert a new featurefile."""
        url = "project/{0}/featurefile/".format(self._project.uuid)
        featurefile_info = {"name": self.name}

        if not os.path.exists(self.path):
            raise OSError(
                "Cannot update featurefile because the system cannot find the file path: '{0}'. "
                "Please update the file's path attribute.".format(self.path)
            )

        response = self._connection.file_request(url, self.path, featurefile_info, "rb")
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data["uuid"]

    def update(self):
        """Calls the REST API to update the featurefile's properties on the server."""
        url = "project/{0}/featurefile/{1}/".format(self._project.uuid, self.uuid)
        featurefile_info = {"name": self.name}

        if not os.path.exists(self.path):
            raise OSError(
                "Cannot update featurefile because the system cannot find the file path: '{0}'. "
                "Please update the file's path attribute.".format(self.path)
            )

        response = self._connection.file_request(
            url, self.path, featurefile_info, "rb", method="put"
        )
        response_data, err = utility.check_server_response(response)

    def delete(self):
        """Calls the REST API and deletes the featurefile from the server."""
        url = "project/{0}/featurefile/{1}/".format(self._project.uuid, self.uuid)
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)

    def refresh(self):
        """Calls the REST API and populate the featurefile's properties from the server."""
        url = "project/{0}/featurefile/{1}/".format(self._project.uuid, self.uuid)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.name = response_data["name"]

    def data(self):
        """Calls the REST API and retrieves the featurefile's binary data.

        Returns:
            featurefile contents
        """
        url = "project/{0}/featurefile/{1}/data/".format(self._project.uuid, self.uuid)
        response = self._connection.request("get", url)
        return response.content

    def initialize_from_dict(self, dict):
        """Makes a new featurefile using the dictionary.

        Args:
            dict (dict): contains the featurefile's 'name' and 'uuid' properties
        """
        self.uuid = dict["uuid"]
        self.name = dict["name"]
        self.created_at = dict["created_at"]
