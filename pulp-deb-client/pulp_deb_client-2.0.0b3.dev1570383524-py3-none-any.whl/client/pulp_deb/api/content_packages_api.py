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

from pulpcore.client.pulp_deb.api_client import ApiClient
from pulpcore.client.pulp_deb.exceptions import (
    ApiTypeError,
    ApiValueError
)


class ContentPackagesApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def create(self, **kwargs):  # noqa: E501
        """Create a package  # noqa: E501

        Trigger an asynchronous task to create content,optionally create new repository version.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.create(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str artifact: Artifact file representing the physical content
        :param str relative_path: Path where the artifact is located relative to distributions base_path
        :param file file: An uploaded file that should be turned into the artifact of the content unit.
        :param str repository: A URI of a repository the new content unit should be associated with.
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
        return self.create_with_http_info(**kwargs)  # noqa: E501

    def create_with_http_info(self, **kwargs):  # noqa: E501
        """Create a package  # noqa: E501

        Trigger an asynchronous task to create content,optionally create new repository version.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.create_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str artifact: Artifact file representing the physical content
        :param str relative_path: Path where the artifact is located relative to distributions base_path
        :param file file: An uploaded file that should be turned into the artifact of the content unit.
        :param str repository: A URI of a repository the new content unit should be associated with.
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

        all_params = ['artifact', 'relative_path', 'file', 'repository']  # noqa: E501
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

        if ('relative_path' in local_var_params and
                len(local_var_params['relative_path']) < 1):
            raise ApiValueError("Invalid value for parameter `relative_path` when calling `create`, length must be greater than or equal to `1`")  # noqa: E501
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
            '/pulp/api/v3/content/deb/packages/', 'POST',
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

    def list(self, **kwargs):  # noqa: E501
        """List packages  # noqa: E501

        A ViewSet for Package.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.list(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str package: Filter results where package matches value
        :param str source: Filter results where source matches value
        :param str version: Filter results where version matches value
        :param str architecture: Filter results where architecture matches value
        :param str section: Filter results where section matches value
        :param str priority: Filter results where priority matches value
        :param str origin: Filter results where origin matches value
        :param str tag: Filter results where tag matches value
        :param str essential: Filter results where essential matches value
        :param str build_essential: Filter results where build_essential matches value
        :param float installed_size: Filter results where installed_size matches value
        :param str maintainer: Filter results where maintainer matches value
        :param str original_maintainer: Filter results where original_maintainer matches value
        :param str built_using: Filter results where built_using matches value
        :param str auto_built_package: Filter results where auto_built_package matches value
        :param str multi_arch: Filter results where multi_arch matches value
        :param str sha256: Filter results where sha256 matches value
        :param str repository_version: Repository Version referenced by HREF
        :param str repository_version_added: Repository Version referenced by HREF
        :param str repository_version_removed: Repository Version referenced by HREF
        :param int limit: Number of results to return per page.
        :param int offset: The initial index from which to return the results.
        :param str fields: A list of fields to include in the response.
        :param str exclude_fields: A list of fields to exclude from the response.
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: InlineResponse2004
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.list_with_http_info(**kwargs)  # noqa: E501

    def list_with_http_info(self, **kwargs):  # noqa: E501
        """List packages  # noqa: E501

        A ViewSet for Package.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.list_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str package: Filter results where package matches value
        :param str source: Filter results where source matches value
        :param str version: Filter results where version matches value
        :param str architecture: Filter results where architecture matches value
        :param str section: Filter results where section matches value
        :param str priority: Filter results where priority matches value
        :param str origin: Filter results where origin matches value
        :param str tag: Filter results where tag matches value
        :param str essential: Filter results where essential matches value
        :param str build_essential: Filter results where build_essential matches value
        :param float installed_size: Filter results where installed_size matches value
        :param str maintainer: Filter results where maintainer matches value
        :param str original_maintainer: Filter results where original_maintainer matches value
        :param str built_using: Filter results where built_using matches value
        :param str auto_built_package: Filter results where auto_built_package matches value
        :param str multi_arch: Filter results where multi_arch matches value
        :param str sha256: Filter results where sha256 matches value
        :param str repository_version: Repository Version referenced by HREF
        :param str repository_version_added: Repository Version referenced by HREF
        :param str repository_version_removed: Repository Version referenced by HREF
        :param int limit: Number of results to return per page.
        :param int offset: The initial index from which to return the results.
        :param str fields: A list of fields to include in the response.
        :param str exclude_fields: A list of fields to exclude from the response.
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(InlineResponse2004, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['package', 'source', 'version', 'architecture', 'section', 'priority', 'origin', 'tag', 'essential', 'build_essential', 'installed_size', 'maintainer', 'original_maintainer', 'built_using', 'auto_built_package', 'multi_arch', 'sha256', 'repository_version', 'repository_version_added', 'repository_version_removed', 'limit', 'offset', 'fields', 'exclude_fields']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method list" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'package' in local_var_params:
            query_params.append(('package', local_var_params['package']))  # noqa: E501
        if 'source' in local_var_params:
            query_params.append(('source', local_var_params['source']))  # noqa: E501
        if 'version' in local_var_params:
            query_params.append(('version', local_var_params['version']))  # noqa: E501
        if 'architecture' in local_var_params:
            query_params.append(('architecture', local_var_params['architecture']))  # noqa: E501
        if 'section' in local_var_params:
            query_params.append(('section', local_var_params['section']))  # noqa: E501
        if 'priority' in local_var_params:
            query_params.append(('priority', local_var_params['priority']))  # noqa: E501
        if 'origin' in local_var_params:
            query_params.append(('origin', local_var_params['origin']))  # noqa: E501
        if 'tag' in local_var_params:
            query_params.append(('tag', local_var_params['tag']))  # noqa: E501
        if 'essential' in local_var_params:
            query_params.append(('essential', local_var_params['essential']))  # noqa: E501
        if 'build_essential' in local_var_params:
            query_params.append(('build_essential', local_var_params['build_essential']))  # noqa: E501
        if 'installed_size' in local_var_params:
            query_params.append(('installed_size', local_var_params['installed_size']))  # noqa: E501
        if 'maintainer' in local_var_params:
            query_params.append(('maintainer', local_var_params['maintainer']))  # noqa: E501
        if 'original_maintainer' in local_var_params:
            query_params.append(('original_maintainer', local_var_params['original_maintainer']))  # noqa: E501
        if 'built_using' in local_var_params:
            query_params.append(('built_using', local_var_params['built_using']))  # noqa: E501
        if 'auto_built_package' in local_var_params:
            query_params.append(('auto_built_package', local_var_params['auto_built_package']))  # noqa: E501
        if 'multi_arch' in local_var_params:
            query_params.append(('multi_arch', local_var_params['multi_arch']))  # noqa: E501
        if 'sha256' in local_var_params:
            query_params.append(('sha256', local_var_params['sha256']))  # noqa: E501
        if 'repository_version' in local_var_params:
            query_params.append(('repository_version', local_var_params['repository_version']))  # noqa: E501
        if 'repository_version_added' in local_var_params:
            query_params.append(('repository_version_added', local_var_params['repository_version_added']))  # noqa: E501
        if 'repository_version_removed' in local_var_params:
            query_params.append(('repository_version_removed', local_var_params['repository_version_removed']))  # noqa: E501
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))  # noqa: E501
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))  # noqa: E501
        if 'fields' in local_var_params:
            query_params.append(('fields', local_var_params['fields']))  # noqa: E501
        if 'exclude_fields' in local_var_params:
            query_params.append(('exclude_fields', local_var_params['exclude_fields']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['Basic']  # noqa: E501

        return self.api_client.call_api(
            '/pulp/api/v3/content/deb/packages/', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='InlineResponse2004',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def read(self, package_href, **kwargs):  # noqa: E501
        """Inspect a package  # noqa: E501

        A ViewSet for Package.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.read(package_href, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str package_href: URI of Package. e.g.: /pulp/api/v3/content/deb/packages/1/ (required)
        :param str fields: A list of fields to include in the response.
        :param str exclude_fields: A list of fields to exclude from the response.
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Package
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.read_with_http_info(package_href, **kwargs)  # noqa: E501

    def read_with_http_info(self, package_href, **kwargs):  # noqa: E501
        """Inspect a package  # noqa: E501

        A ViewSet for Package.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.read_with_http_info(package_href, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str package_href: URI of Package. e.g.: /pulp/api/v3/content/deb/packages/1/ (required)
        :param str fields: A list of fields to include in the response.
        :param str exclude_fields: A list of fields to exclude from the response.
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(Package, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['package_href', 'fields', 'exclude_fields']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method read" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'package_href' is set
        if ('package_href' not in local_var_params or
                local_var_params['package_href'] is None):
            raise ApiValueError("Missing the required parameter `package_href` when calling `read`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'package_href' in local_var_params:
            path_params['package_href'] = local_var_params['package_href']  # noqa: E501

        query_params = []
        if 'fields' in local_var_params:
            query_params.append(('fields', local_var_params['fields']))  # noqa: E501
        if 'exclude_fields' in local_var_params:
            query_params.append(('exclude_fields', local_var_params['exclude_fields']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['Basic']  # noqa: E501

        return self.api_client.call_api(
            '{package_href}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Package',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)
