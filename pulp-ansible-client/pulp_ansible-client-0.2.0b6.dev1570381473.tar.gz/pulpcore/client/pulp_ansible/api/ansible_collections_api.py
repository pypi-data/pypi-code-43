# coding: utf-8

"""
    Pulp 3 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v3
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from pulpcore.client.pulp_ansible.api_client import ApiClient
from pulpcore.client.pulp_ansible.exceptions import (
    ApiTypeError,
    ApiValueError
)


class AnsibleCollectionsApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def create(self, relative_path, **kwargs):  # noqa: E501
        """Create a collection version  # noqa: E501

        Trigger an asynchronous task to create content,optionally create new repository version.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.create(relative_path, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str relative_path: Path where the artifact is located relative to distributions base_path (required)
        :param str artifact: Artifact file representing the physical content
        :param file file: An uploaded file that should be turned into the artifact of the content unit.
        :param str repository: A URI of a repository the new content unit should be associated with.
        :param str expected_name: The expected 'name' of the Collection to be verified against the metadata during import.
        :param str expected_namespace: The expected 'namespace' of the Collection to be verified against the metadata during import.
        :param str expected_version: The expected version of the Collection to be verified against the metadata during import.
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: AsyncOperationResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.create_with_http_info(relative_path, **kwargs)  # noqa: E501

    def create_with_http_info(self, relative_path, **kwargs):  # noqa: E501
        """Create a collection version  # noqa: E501

        Trigger an asynchronous task to create content,optionally create new repository version.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.create_with_http_info(relative_path, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str relative_path: Path where the artifact is located relative to distributions base_path (required)
        :param str artifact: Artifact file representing the physical content
        :param file file: An uploaded file that should be turned into the artifact of the content unit.
        :param str repository: A URI of a repository the new content unit should be associated with.
        :param str expected_name: The expected 'name' of the Collection to be verified against the metadata during import.
        :param str expected_namespace: The expected 'namespace' of the Collection to be verified against the metadata during import.
        :param str expected_version: The expected version of the Collection to be verified against the metadata during import.
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(AsyncOperationResponse, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['relative_path', 'artifact', 'file', 'repository', 'expected_name', 'expected_namespace', 'expected_version']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method create" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'relative_path' is set
        if ('relative_path' not in local_var_params or
                local_var_params['relative_path'] is None):
            raise ApiValueError("Missing the required parameter `relative_path` when calling `create`")  # noqa: E501

        if ('relative_path' in local_var_params and
                len(local_var_params['relative_path']) < 1):
            raise ApiValueError("Invalid value for parameter `relative_path` when calling `create`, length must be greater than or equal to `1`")  # noqa: E501
        if ('expected_name' in local_var_params and
                len(local_var_params['expected_name']) < 1):
            raise ApiValueError("Invalid value for parameter `expected_name` when calling `create`, length must be greater than or equal to `1`")  # noqa: E501
        if ('expected_namespace' in local_var_params and
                len(local_var_params['expected_namespace']) < 1):
            raise ApiValueError("Invalid value for parameter `expected_namespace` when calling `create`, length must be greater than or equal to `1`")  # noqa: E501
        if ('expected_version' in local_var_params and
                len(local_var_params['expected_version']) < 1):
            raise ApiValueError("Invalid value for parameter `expected_version` when calling `create`, length must be greater than or equal to `1`")  # noqa: E501
        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}
        if 'artifact' in local_var_params:
            form_params.append(('artifact', local_var_params['artifact']))  # noqa: E501
        if 'relative_path' in local_var_params:
            form_params.append(('relative_path', local_var_params['relative_path']))  # noqa: E501
        if 'file' in local_var_params:
            local_var_files['file'] = local_var_params['file']  # noqa: E501
        if 'repository' in local_var_params:
            form_params.append(('repository', local_var_params['repository']))  # noqa: E501
        if 'expected_name' in local_var_params:
            form_params.append(('expected_name', local_var_params['expected_name']))  # noqa: E501
        if 'expected_namespace' in local_var_params:
            form_params.append(('expected_namespace', local_var_params['expected_namespace']))  # noqa: E501
        if 'expected_version' in local_var_params:
            form_params.append(('expected_version', local_var_params['expected_version']))  # noqa: E501

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['multipart/form-data', 'application/x-www-form-urlencoded'])  # noqa: E501

        # Authentication setting
        auth_settings = ['Basic']  # noqa: E501

        return self.api_client.call_api(
            '/ansible/collections/', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='AsyncOperationResponse',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)
