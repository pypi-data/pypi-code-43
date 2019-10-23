################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
import requests
from watson_machine_learning_client.utils import SPACES_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, MEMBER_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, meta_props_str_conv, str_type_conv, get_file_from_cos
from watson_machine_learning_client.metanames import AssetsMetaNames
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.wml_client_error import  WMLClientError


_DEFAULT_LIST_LENGTH = 50


class Set(WMLResource):
    """
    Set a space_id/project_id to be used in the subsequent actions.
    """
    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        self._ICP = client.ICP

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def default_space(self, space_uid):
        """
                Set a space ID.

                **Parameters**

                .. important::
                   #. **space_uid**:  GUID of the space to be used:\n

                      **type**: str\n

                **Output**

                .. important::

                    **returns**: The space that is set here is used for subsequent requests.\n
                    **return type**: str("SUCCESS"/"FAILURE")\n

                **Example**

                 >>>  client.set.default_space(space_uid)

        """
        space_endpoint = self._href_definitions.get_space_href(space_uid)
        if not self._ICP:
            space_details = requests.get(space_endpoint, headers=self._client._get_headers())
        else:
            space_details = requests.get(space_endpoint, headers=self._client._get_headers(), verify=False)

        if space_details.status_code == 401:
            raise WMLClientError('Space with guid'+ space_uid+" does not exist.")
            return "FAILURE"
        elif space_details.status_code == 200:
            self._client.default_space_id = space_uid
            if  self._client.default_project_id is not None:
                print("Unsetting the project_id ...")
            self._client.default_project_id = None
            return "SUCCESS"
        else:
            print("Failed to set space.")
            print(space_details.text)
            return "FAILURE"

        # quick support for COS credentials instead of local path
        # TODO add error handling and cleaning (remove the file)



    ##Setting project ID
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def default_project(self, project_id):
        """
                Set a project ID.

                **Parameters**

                .. important::
                   #. **project_id**:  GUID of the project\n

                      **type**: str\n

                **Output**

                .. important::

                    **returns**: "SUCCESS"\n
                    **return type**: str\n

                **Example**

                 >>>  client.set.default_project(project_id)

        """

        self._client.default_project_id = project_id
        if self._client.default_space_id is not None:
            print("Unsetting the space_id ...")
        self._client.default_space_id = None
        return "SUCCESS"