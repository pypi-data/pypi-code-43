import os
import json
import sensiml.base.utility as utility


class Segmenters(object):
    """Base class for a segmenter object."""

    def __init__(self, connection, project):
        self._connection = connection
        self._project = project

    def get_segmenters(self):
        """Gets a list of all segmenters in the project.

        Returns:
            list (segmenters)
        """
        err = False
        url = "project/{0}/segmenter/".format(self._project.uuid)
        response = self._connection.request("get", url)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)
        # Populate the retrieved featurefiles
        segmenters = []

        if err is False:
            try:
                for segmenter_params in response_data:
                    segmenters.append(segmenter_params)
            except:
                pass

        return segmenters
