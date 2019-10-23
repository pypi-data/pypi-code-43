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
from watson_machine_learning_client.metanames import ModelDefinitionMetaNames, MetaNamesBase,  MetaNames
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.wml_client_error import WMLClientError
import os
import json

_DEFAULT_LIST_LENGTH = 50


class ModelDefinition(WMLResource):

    """
    Store and manage your model_definitions.
    """

    ConfigurationMetaNames = ModelDefinitionMetaNames()

    """MetaNames for model_definition creation."""

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        self._ICP = client.ICP
        self.default_space_id = client.default_space_id

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _generate_model_definition_document(self, meta_props):
        doc = {
            "metadata":
            {
               "name": "My wml_library_assert",
               "tags": ["string"],
               "asset_type": "wml_model_definition",
               "origin_country": "us",
               "rov": {
                  "mode": 0
               },
               "asset_category": "USER"
            },
            "entity": {
               "wml_model_definition": {
                   "name": "tf-model_trainings_v4_test_suite_basic",
                   "description": "Sample custom library",
                   "version": "1.0",
                   "platform": {
                      "name": "python",
                      "versions": [
                          "3.5"
                         ]
                   }
               }
            }
        }

        if self.ConfigurationMetaNames.NAME in meta_props:
            doc["metadata"]["name"] = meta_props[self.ConfigurationMetaNames.NAME] + " wml_model_definition Asset"
            doc["entity"]["wml_model_definition"]["name"] = meta_props[self.ConfigurationMetaNames.NAME]
        if self.ConfigurationMetaNames.DESCRIPTION in meta_props:
            doc["entity"]["wml_model_definition"]["description"] = meta_props[self.ConfigurationMetaNames.DESCRIPTION]
            doc["metadata"]["description"] = meta_props[self.ConfigurationMetaNames.DESCRIPTION]

        if self.ConfigurationMetaNames.VERSION in meta_props:
            doc["entity"]["wml_model_definition"]["version"] = meta_props[self.ConfigurationMetaNames.VERSION]
        if self.ConfigurationMetaNames.PLATFORM in meta_props:
            doc["entity"]["wml_model_definition"]["platform"]["name"] = meta_props[self.ConfigurationMetaNames.PLATFORM]['name']
            doc["entity"]["wml_model_definition"]["platform"]["versions"][0] = \
                meta_props[self.ConfigurationMetaNames.PLATFORM]['versions'][0]
        return doc

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store(self, model_definition, meta_props):
        """
                   Create a model_definitions.\n

                   **Parameters**

                   .. important::

                        #. **meta_props**:  meta data of the model_definition configuration. To see available meta names use:\n
                                            >>> client.model_definitions.ConfigurationMetaNames.get()

                           **type**: dict\n

                   **Output**

                   .. important::

                        **returns**: Metadata of the model_defintion created\n
                        **return type**: dict\n

                   **Example**

                    Creating a model_definition\n
        """
        ##For CP4D, check if either spce or project ID is set
        self._client._check_if_either_is_set()
        model_definition = str_type_conv(model_definition)
        self.ConfigurationMetaNames._validate(meta_props)

        metadata = {
            self.ConfigurationMetaNames.NAME: meta_props[self.ConfigurationMetaNames.NAME],
            self.ConfigurationMetaNames.VERSION: meta_props['version'],
            self.ConfigurationMetaNames.PLATFORM:
                meta_props['platform']
                if 'platform' in meta_props and meta_props['platform'] is not None
                else {
                    "name": meta_props[self.ConfigurationMetaNames.PLATFORM]['name'],
                    "versions": [meta_props[self.ConfigurationMetaNames.PLATFORM]['versions']]
                },
        }

        if self.ConfigurationMetaNames.DESCRIPTION in meta_props:
            metadata[self.ConfigurationMetaNames.DESCRIPTION] = meta_props[self.ConfigurationMetaNames.DESCRIPTION]

        if self.ConfigurationMetaNames.SPACE_UID in meta_props:
            metadata[self.ConfigurationMetaNames.SPACE_UID] = {
                "href": "/v4/spaces/" + meta_props[self.ConfigurationMetaNames.SPACE_UID]
            }
        if self._client.CAMS:
            if self._client.default_space_id is not None:
                metadata['space'] = {'href': "/v4/spaces/"+self._client.default_space_id}
            elif self._client.default_project_id is not None:
                metadata['project'] = {'href': "/v2/projects/"+self._client.default_project_id}
            else:
                raise WMLClientError("It is mandatory to set the space/project id. Use client.set.default_space(<SPACE_UID>)/client.set.default_project(<PROJECT_UID>) to proceed.")

        document = self._generate_model_definition_document(meta_props)

        model_definition_attachment_def = {
          "asset_type": "wml_model_definition",
          "name": "model_definition_attachment"
        }
        paramvalue = self._client._params()

        try:
            if not self._ICP:
                creation_response = requests.post(
                     self._href_definitions.get_model_definition_assets_href(),
                     params=paramvalue,
                     headers=self._client._get_headers(),
                     data=document,
                     verify=False)
            else:
                creation_response = requests.post(
                    self._href_definitions.get_model_definition_assets_href(),
                    params=paramvalue,
                    headers=self._client._get_headers(),
                    json=document,
                    verify=False)

            model_definition_details = self._handle_response(201, u'creating new model_definition', creation_response)
            model_definition_attachment_url = self._href_definitions.get_model_definition_assets_href() + "/" + \
                                           model_definition_details['metadata']['asset_id'] + "/attachments"

            put_header = self._client._get_headers(no_content_type=True)
            files = {'file': open(model_definition, 'rb')}
            if creation_response.status_code == 201:
                model_definition_id = model_definition_details['metadata']['asset_id']
                if not self._ICP:
                    attachment_response = requests.post(
                        model_definition_attachment_url,
                        params=paramvalue,
                        headers=self._client._get_headers(),
                        json=model_definition_attachment_def,
                        verify=False)
                else:
                    attachment_response = requests.post(
                         model_definition_attachment_url,
                         params=paramvalue,
                         headers=self._client._get_headers(),
                         json=model_definition_attachment_def,
                         verify=False)
                attachment_details = self._handle_response(201, u'creating new attachment', attachment_response)
                if attachment_response.status_code == 201:
                    attachment_id = attachment_details['attachment_id']
                    attachment_status_json = json.loads(attachment_response.content.decode("utf-8"))
                    model_definition_attachment_signed_url = attachment_status_json["url1"]
                 #   print("WML model_definition attachment url1: %s" % model_definition_attachement_signed_url)
                    model_definition_attachment_put_url = self._client.wml_credentials['url'] + model_definition_attachment_signed_url

                    if not self._ICP:
                        put_response = requests.put(model_definition_attachment_put_url,
                                                    files=files,
                                                    params=paramvalue,
                                                    headers=put_header)
                    else:

                        put_response = requests.put(model_definition_attachment_put_url,
                                                    files=files,
                                                    verify=False)
                    if put_response.status_code == 201:
                        complete_url = self._href_definitions.get_attachment_href(model_definition_id, attachment_id) \
                                       + "/complete"
                        if not self._ICP:
                            complete_response = requests.post(complete_url,
                                                              params=paramvalue,
                                                              headers=self._client._get_headers(),
                                                              verify=False)
                        else:
                            complete_response = requests.post(complete_url,
                                                              params=paramvalue,
                                                              headers=self._client._get_headers(),
                                                              verify=False)

                        if complete_response.status_code == 200:
                            return self._get_required_element_from_response(model_definition_details)
                        else:
                            self._delete(model_definition_id)
                            raise WMLClientError("Failed while creating a model_definition. Try again.")
                    else:
                        self._delete(model_definition_id)
                        raise WMLClientError("Failed while creating a model_definition. Try again.")
                else:
                    self._delete(model_definition_id)
                    raise WMLClientError("Failed while creating a model_definition. Try again.")
            else:
                raise WMLClientError("Failed while creating a model_definition. Try again.")

        except Exception as e:

            raise e


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, model_definition_uid):
        """
           Get metadata of stored model_definition.


           **Parameters**

           .. important::
                #. **model_definition_uid**: model_definition UID \n
                   **type**: str\n

           **Output**

           .. important::
                **returns**: metadata of model definition\n
                **return type**: dict
                dict (if UID is not None)\n

           **Example**

            >>> model_definition_details = client.model_definitions.get_details(model_definition_uid)

        """
        ##For CP4D, check if either spce or project ID is set
        self._client._check_if_either_is_set()
        op_name = 'getting model_definition details'
        modeldef_uid = str_type_conv(model_definition_uid)
        ModelDefinition._validate_type(modeldef_uid, u'model_definition_uid', STR_TYPE, False)

        url = self._href_definitions.get_model_definition_assets_href() + u'/' + modeldef_uid
        paramvalue = self._client._params()
        if not self._ICP:
            response_get = requests.get(
                url,
                params=self._client._params(),
                headers=self._client._get_headers()
            )
        else:
            response_get = requests.get(
                url,
                params=paramvalue,
                headers=self._client._get_headers(),
                verify=False
            )
        if response_get.status_code == 200:
            get_model_definition_details = self._handle_response(200, op_name, response_get)
            return self._get_required_element_from_response(get_model_definition_details)
        else:
            return self._handle_response(200, op_name, response_get)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def download(self, model_definition_uid, filename):
        ##For CP4D, check if either spce or project ID is set
        self._client._check_if_either_is_set()
        ModelDefinition._validate_type(model_definition_uid, u'model_definition_uid', STR_TYPE, True)
        attachment_id = self._get_attachment_id(model_definition_uid)

        if not self._ICP:
            response = requests.get(self._href_definitions.get_attachment_href(model_definition_uid, attachment_id), params=self._client._params(),
                                    headers=self._client._get_headers())
        else:
            response = requests.get(self._href_definitions.get_attachment_href(model_definition_uid, attachment_id), params=self._client._params(),
                                    headers=self._client._get_headers(), verify=False)
        if response.status_code == 200:
            attachment_signed_url = response.json()["url"]

            if not self._ICP:
                att_response = requests.get(self._wml_credentials["url"]+attachment_signed_url)
            else:
                att_response = requests.get(self._wml_credentials["url"]+attachment_signed_url,
                                            verify=False)
            if att_response.status_code != 200:
                raise WMLClientError(u'Failure during {}.'.format("downloading model_definition asset"),
                                     att_response)

            downloaded_asset = att_response.content
            try:
                with open(filename, 'wb') as f:
                    f.write(downloaded_asset)
                print(u'Successfully saved asset content to file: \'{}\''.format(filename))
                return os.getcwd() + "/" + filename
            except IOError as e:
                raise WMLClientError(u'Saving asset with artifact_url: \'{}\' failed.'.format(filename), e)
        else:
            raise WMLClientError("Failed while downloading the asset " + model_definition_uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, model_definition_uid):
        """
            Delete a stored model_definition.

            **Parameters**

            .. important::
                #. **model_definition_uid**:  Model definition UID\n
                   **type**: str\n

            **Output**

            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

            **Example**

             >>> client.model_definitions.delete(model_definition_uid)
        """
        ##For CP4D, check if either spce or project ID is set
        self._client._check_if_either_is_set()
        model_definition_uid = str_type_conv(model_definition_uid)
        ModelDefinition._validate_type(model_definition_uid, u'model_definition_uid', STR_TYPE, True)
        paramvalue = self._client._params()
        model_definition_endpoint = self._href_definitions.get_model_definition_assets_href() + "/" + model_definition_uid
        if not self._ICP:
            response_delete = requests.delete(model_definition_endpoint, params=paramvalue, headers=self._client._get_headers())
        else:
            response_delete = requests.delete(model_definition_endpoint, params=paramvalue, headers=self._client._get_headers(), verify=False)

        return self._handle_response(204, u'Model definition deletion', response_delete, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _delete(self, model_definition_uid):
        """
            Delete a stored model_definition.

            **Parameters**

            .. important::
                #. **model_definition_uid**:  Model definition UID\n
                   **type**: str\n

            **Output**

            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

            **Example**

             >>> client.model_definitions.delete(model_definition_uid)
        """
        ##For CP4D, check if either spce or project ID is set
        model_definition_uid = str_type_conv(model_definition_uid)
        ModelDefinition._validate_type(model_definition_uid, u'model_definition_uid', STR_TYPE, True)
        paramvalue = self._client._params()
        model_definition_endpoint = self._href_definitions.get_model_definition_assets_href() + "/" + model_definition_uid
        if not self._ICP:
            response_delete = requests.delete(model_definition_endpoint, params=paramvalue, headers=self._client._get_headers())
        else:
            response_delete = requests.delete(model_definition_endpoint, params=paramvalue, headers=self._client._get_headers(), verify=False)

    def _get_required_element_from_response(self, response_data):

        WMLResource._validate_type(response_data,  u'model_definition_response', dict)
        try:
            if self._client.default_space_id is not None:
                new_el = {'metadata': {'space_id': response_data['metadata']['space_id'],
                                   'guid': response_data['metadata']['asset_id'],
                                   'href': response_data['href'],
                                   'asset_type': response_data['metadata']['asset_type'],
                                   'created_at': response_data['metadata']['created_at'],
                                   'last_updated_at': response_data['metadata']['usage']['last_updated_at']
                                },
                      'entity': response_data['entity']

                      }
            elif self._client.default_project_id is not None:
                new_el = {'metadata': {'project_id': response_data['metadata']['project_id'],
                                       'guid': response_data['metadata']['asset_id'],
                                       'href': response_data['href'],
                                       'asset_type': response_data['metadata']['asset_type'],
                                       'created_at': response_data['metadata']['created_at'],
                                       'last_updated_at': response_data['metadata']['usage']['last_updated_at']
                                       },
                          'entity': response_data['entity']

                          }
            return new_el
        except Exception as e:
            raise WMLClientError("Failed to read Response from down-stream service: " + response_data)

    def _get_attachment_id(self, model_definition_uid):
        op_name = 'getting attachment id '
        url = self._href_definitions.get_model_definition_assets_href() + u'/' + model_definition_uid
        paramvalue = self._client._params()
        if not self._ICP:
            response_get = requests.get(
                url,
                headers=self._client._get_headers()
            )
        else:
            response_get = requests.get(
                url,
                params=paramvalue,
                headers=self._client._get_headers(),
                verify=False
            )
        details = self._handle_response(200, op_name, response_get)
        attachment_id = details["attachments"][0]["id"]
        return attachment_id

    def list(self, limit=None):
        """
           List stored model_definition assets. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all model_definition assets in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.model_definitions.list()
        """
        ##For CP4D, check if either spce or project ID is set
        self._client._check_if_either_is_set()
        href = self._href_definitions.get_model_definition_search_asset_href()
        if limit is None:
            data = {
                "query": "*:*"
            }
        else:
            ModelDefinition._validate_type(limit, u'limit', int, False)
            data = {
                "query": "*:*",
                "limit": limit
            }

        if not self._ICP:
            response = requests.post(href, params=self._client._params(), headers=self._client._get_headers(),json=data)
        else:
            response = requests.post(href, params=self._client._params(), headers=self._client._get_headers(),json=data, verify=False)
        self._handle_response(200, u'model_definition assets', response)
        asset_details = self._handle_response(200, u'model_definition assets', response)["results"]
        model_def_values = [
            (m[u'metadata'][u'name'], m[u'metadata'][u'asset_type'], m[u'metadata'][u'asset_id']) for
            m in asset_details]

        self._list(model_def_values, [u'NAME', u'ASSET_TYPE', u'GUID'], limit, _DEFAULT_LIST_LENGTH)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(self, model_definition_details):
        """
            Get uid of stored model.

            :param model_definition_details:  stored model_definition details
            :type model_definition_details: dict

            :returns: uid of stored model_definition
            :rtype: {str_type}

            A way you might use me is:

            >>> model_definition_uid = client.model_definitions.get_uid(model_definition_details)
        """
        ModelDefinition._validate_type(model_definition_details, u'model__definition_details', object, True)
        #ModelDefinition._validate_type_of_details(model_definition_details, MODEL_DEFINITION_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(model_definition_details, u'model_definition_details', [u'metadata', u'guid'])

    def get_href(self, model_definition_details):
        """
            Get href of stored model_definition.

            :param model_definition_details:  stored model_definition details
            :type model_definition_details: dict

            :returns: href of stored model_definition
            :rtype: {str_type}

            A way you might use me is:

            >>> model_definition_uid = client.model_definitions.get_href(model_definition_details)
        """
        ModelDefinition._validate_type(model_definition_details, u'model__definition_details', object, True)
        # ModelDefinition._validate_type_of_details(model_definition_details, MODEL_DEFINITION_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(model_definition_details, u'model_definition_details',
                                                           [u'metadata', u'href'])
