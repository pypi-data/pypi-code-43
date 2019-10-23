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
from watson_machine_learning_client.utils import SPACES_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, MEMBER_DETAILS_TYPE,DATA_ASSETS_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, meta_props_str_conv, str_type_conv, get_file_from_cos
from watson_machine_learning_client.metanames import AssetsMetaNames
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.wml_client_error import WMLClientError, ApiRequestFailure
import os

_DEFAULT_LIST_LENGTH = 50


class Assets(WMLResource):
    """
    Store and manage your assets.
    """
    ConfigurationMetaNames = AssetsMetaNames()
    """MetaNames for Assets creation."""

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        self._ICP = client.ICP

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self,asset_uid):
        """
            Get asset details.

            **Parameters**

            .. important::
                #. **asset_details**:  Metadata of the stored asset\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: asset UID\n
                **return type**: str

            **Example**

             >>> asset_details = client.assets.get_details(asset_uid)
        """
        Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, True)


        if not self._ICP:
            response = requests.get(self._href_definitions.get_data_asset_href(asset_uid), params=self._client._params(),
                                    headers=self._client._get_headers())
        else:
            response = requests.get(self._href_definitions.get_data_asset_href(asset_uid), params=self._client._params(),
                                      headers=self._client._get_headers(), verify=False)
        if response.status_code == 200:
            return self._get_required_element_from_response(self._handle_response(200, u'get asset details', response))
        else:
            return self._handle_response(200, u'get asset details', response)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def create(self, name, file_path):
        """
                Creates a data asset and uploads content to it.

                **Parameters**

                .. important::
                   #. **name**:  Name to be given to the data asset\n

                      **type**: str\n

                   #. **file_path**:  Path to the content file to be uploaded\n

                      **type**: str\n

                **Output**

                .. important::

                    **returns**: metadata of the stored asset\n
                    **return type**: dict\n

                **Example**
                 >>> asset_details = client.assets.create(name="sample_asset",file_path="/path/to/file")
        """
        # quick support for COS credentials instead of local path
        # TODO add error handling and cleaning (remove the file)
        Assets._validate_type(name, u'name', str, True)
        Assets._validate_type(file_path, u'file_path', str, True)
        ##Step1: Create a data asset
        f = {'file': open(file_path, 'rb')}
        try:
            import mimetypes
        except Exception as e:
            raise WMLClientError(u'Module mimetypes not found.', e)
        mime_type = mimetypes.MimeTypes().guess_type(file_path)[0]
        asset_meta = {
            "metadata": {
                "name": name,
                "asset_type": "data_asset",
                "origin_country": "us",
                "asset_category": "USER"
            },
            "entity": {
                "data_asset": {
                    "mime_type": mime_type
                }
            }
        }
        #Step1  : Create an asset
        print("Creating data asset...")
        if not self._ICP:
            creation_response = requests.post(
                    self._href_definitions.get_data_assets_href(),
                    headers=self._client._get_headers(),
                    params = self._client._params(),
                    json=asset_meta
            )
        else:
            creation_response = requests.post(
                self._href_definitions.get_data_assets_href(),
                headers=self._client._get_headers(),
                json=asset_meta,
                params=self._client._params(),
                verify=False
            )


        asset_details = self._handle_response(201, u'creating new asset', creation_response)
        #Step2: Create attachment
        if creation_response.status_code == 201:
            asset_id = asset_details["metadata"]["asset_id"]
            attachment_meta = {
                    "asset_type": "data_asset",
                    "name": "attachment_"+asset_id,
                    "mime": mime_type
                }
            if not self._ICP:
                attachment_response = requests.post(
                    self._wml_credentials['url']+"/v2/assets/"+asset_id+"/attachments",
                    headers=self._client._get_headers(),
                    params=self._client._params(),
                    json=attachment_meta
                )
            else:
                attachment_response = requests.post(
                    self._wml_credentials['url']+"/v2/assets/"+asset_id+"/attachments",
                    headers=self._client._get_headers(),
                    json=attachment_meta,
                    params=self._client._params(),
                    verify=False
                )
            attachment_details = self._handle_response(201, u'creating new attachment', attachment_response)
            if attachment_response.status_code == 201:
                attachment_id = attachment_details["attachment_id"]
                attachment_url = attachment_details["url1"]
                #Step3: Put content to attachment
                if not self._ICP:
                        put_response = requests.put(
                            self._wml_credentials['url'] + attachment_url,
                            files = f
                        )
                else:
                        put_response = requests.put(
                            self._wml_credentials['url'] + attachment_url,
                            files=f,
                            verify=False
                        )
                if put_response.status_code == 201:
                    # Step4: Complete attachment
                    if not self._ICP:
                        complete_response = requests.post(
                            self._href_definitions.get_attachment_href(asset_id,attachment_id)+"/complete",
                            headers=self._client._get_headers(),
                            params = self._client._params()

                        )
                    else:
                        complete_response = requests.post(
                            self._href_definitions.get_attachment_href(asset_id,attachment_id)+"/complete",
                            headers=self._client._get_headers(),
                            params=self._client._params(),
                            verify=False
                        )
                    if complete_response.status_code == 200:
                        print("SUCCESS")
                        return self._get_required_element_from_response(asset_details)
                    else:
                        self._delete(asset_id)
                        raise WMLClientError("Failed while creating a data asset. Try again.")
                else:
                    self._delete(asset_id)
                    raise WMLClientError("Failed while creating a data asset. Try again.")
            else:
                self._delete(asset_id)
                raise WMLClientError("Failed while creating a data asset. Try again.")
        else:
            raise WMLClientError("Failed while creating a data asset. Try again.")

    def list(self,limit=None):
        """
           List stored space assets. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all assets in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.assets.list()
        """

        Assets._validate_type(limit, u'limit', int, False)
        href = self._href_definitions.get_search_asset_href()

        data = {
                "query": "*:*"
        }
        if limit is not None:
            data.update({"limit": limit})

        if not self._ICP:
            response = requests.post(href, params=self._client._params(), headers=self._client._get_headers(),json=data)
        else:
            response = requests.post(href, params=self._client._params(), headers=self._client._get_headers(),json=data, verify=False)
        self._handle_response(200, u'list assets', response)
        asset_details = self._handle_response(200, u'list assets', response)["results"]
        space_values = [
            (m[u'metadata'][u'name'], m[u'metadata'][u'asset_type'], m[u'metadata'][u'size'], m["metadata"]["asset_id"]) for
            m in asset_details]

        self._list(space_values, [u'NAME', u'ASSET_TYPE', u'SIZE',u'ASSET_ID'], None, _DEFAULT_LIST_LENGTH)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def download(self, asset_uid, filename):
        """
            Download an asset.

            **Parameters**

            .. important::
                 #. **asset_uid**:  The UID of the asset to be downloaded\n
                    **type**: str\n

                 #. **filename**:  filename to be used for the downloaded file\n
                    **type**: str\n

            **Output**

                 **returns**: Path to the downloaded asset content\n
                 **return type**: str\n

            **Example**

             >>> client.assets.download(asset_uid,"sample_asset.csv")
         """

        Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, True)
        if not self._ICP:
            asset_response = requests.get(self._href_definitions.get_data_asset_href(asset_uid), params=self._client._params(),
                                    headers=self._client._get_headers())
        else:
            asset_response = requests.get(self._href_definitions.get_data_asset_href(asset_uid), params=self._client._params(),
                                      headers=self._client._get_headers(), verify=False)
        asset_details = self._handle_response(200, u'get assets', asset_response)
        attachment_id = asset_details["attachments"][0]["id"]

        if not self._ICP:
            response = requests.get(self._href_definitions.get_attachment_href(asset_uid,attachment_id), params=self._client._params(),
                                    headers=self._client._get_headers())
        else:
            response = requests.get(self._href_definitions.get_attachment_href(asset_uid,attachment_id), params=self._client._params(),
                                      headers=self._client._get_headers(), verify=False)
        if response.status_code == 200:
            attachment_signed_url = response.json()["url"]

            if not self._ICP:
                att_response = requests.get(self._wml_credentials["url"]+attachment_signed_url)
            else:
                att_response = requests.get(self._wml_credentials["url"]+attachment_signed_url,
                                        verify=False)
                if att_response.status_code != 200:
                    raise ApiRequestFailure(u'Failure during {}.'.format("downloading asset"), att_response)

                downloaded_asset = att_response.content
                try:
                    with open(filename, 'wb') as f:
                        f.write(downloaded_asset)
                    print(u'Successfully saved asset content to file: \'{}\''.format(filename))
                    return os.getcwd() + "/" + filename
                except IOError as e:
                    raise WMLClientError(u'Saving asset with artifact_url: \'{}\' failed.'.format(filename), e)
        else:
            raise WMLClientError("Failed while downloading the asset "+ asset_uid)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(asset_details):
        """
                Get UID of stored asset.

                **Parameters**

                .. important::

                   #. **asset_details**:  Metadata of the stored asset\n
                      **type**: dict\n
                      **type**: dict\n

                **Output**

                .. important::

                    **returns**: UID of stored asset\n
                    **return type**: str\n

                **Example**


                 >>> asset_uid = client.assets.get_uid(asset_details)
        """
        Assets._validate_type(asset_details, u'asset_details', object, True)
        Assets._validate_type_of_details(asset_details, DATA_ASSETS_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(asset_details, u'data_assets_details',
                                                           [u'metadata', u'guid'])


    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_href(asset_details):
        """
            Get url of stored asset.

           **Parameters**

           .. important::
                #. **asset_details**:  stored asset details\n
                   **type**: dict\n

           **Output**

           .. important::
                **returns**: href of stored asset\n
                **return type**: str\n

           **Example**

             >>> asset_details = client.assets.get_details(asset_uid)
             >>> asset_href = client.assets.get_href(asset_details)
        """
        Assets._validate_type(asset_details, u'asset_details', object, True)
        Assets._validate_type_of_details(asset_details, DATA_ASSETS_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(asset_details, u'asset_details', [u'metadata', u'href'])


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, asset_uid):
        """
            Delete a stored asset.

            **Parameters**

            .. important::
                #. **asset_uid**:  asset UID\n
                   **type**: str\n

            **Output**

            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

            **Example**

             >>> client.assets.delete(asset_uid)
        """
        Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, True)

        if not self._ICP:
            response = requests.delete(self._href_definitions.get_asset_href(asset_uid), params=self._client._params(),
                                    headers=self._client._get_headers())
        else:
            response = requests.delete(self._href_definitions.get_asset_href(asset_uid), params=self._client._params(),
                                      headers=self._client._get_headers(), verify=False)
        if response.status_code == 200:
            return self._get_required_element_from_response(response.json())
        else:
            return self._handle_response(204, u'delete assets', response)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _delete(self, asset_uid):
        Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, True)

        if not self._ICP:
            response = requests.delete(self._href_definitions.get_asset_href(asset_uid), params=self._client._params(),
                                       headers=self._client._get_headers())
        else:
            response = requests.delete(self._href_definitions.get_asset_href(asset_uid), params=self._client._params(),
                                       headers=self._client._get_headers(), verify=False)
        # if response.status_code == 200:
        #     return self._get_required_element_from_response(response.json())
        # else:
        #     return self._handle_response(204, u'delete assets', response)


    # @docstring_parameter({'str_type': STR_TYPE_NAME})
    # def get_href(self, asset_uid):
    #     """
    #        Get metadata of stored space(s). If space UID is not specified, it returns all the spaces metadata.
    #
    #        **Parameters**
    #
    #        .. important::
    #             #. **space_uid**: Space UID (optional)\n
    #                **type**: str\n
    #             #. **limit**:  limit number of fetched records (optional)\n
    #                **type**: int\n
    #
    #        **Output**
    #
    #        .. important::
    #             **returns**: metadata of stored space(s)\n
    #             **return type**: dict
    #             dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n
    #
    #        .. note::
    #             If UID is not specified, all spaces metadata is fetched\n
    #
    #        **Example**
    #
    #         >>> space_details = client.spaces.get_details(space_uid)
    #         >>> space_details = client.spaces.get_details()
    #     """
    #
    #
    #     Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, True)
    #
    #     if not self._ICP:
    #         response = requests.get(self._href_definitions.get_data_asset_href(asset_uid), params=self._client._params(),
    #                                 headers=self._client._get_headers())
    #     else:
    #         response = requests.get(self._href_definitions.get_data_asset_href(asset_uid), params=self._client._params(),
    #                                 headers=self._client._get_headers(), verify=False)
    #     if response.status_code == 200:
    #         return response.json()["href"]
    #     else:
    #         return self._handle_response(200, u'spaces assets', response)

    def _get_required_element_from_response(self, response_data):

        WMLResource._validate_type(response_data, u'model_definition_response', dict)
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
            elif  self._client.default_project_id is not None:
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
