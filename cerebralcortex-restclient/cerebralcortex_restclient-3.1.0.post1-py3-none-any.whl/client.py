# Copyright (c) 2019, MD2K Center of Excellence
# - Nasir Ali <nasir.ali08@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import json
import requests


# ------------------------ USER ROUTE ------------------------#

def register_user(url: str, user_metadata: dict):
    """

    Args:
        url (str): url of user register route of CC-ApiServer. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist
        user_metadata (dict): metadata of a user
    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if user registration fails

    Examples:
        >>> from cerebralcortex_rest import register_user
        >>> register_user(url="http://localhost/api/v3/user/default/register", user_metadata={
                                  "username": "string",
                                  "password": "string",
                                  "user_role": "string",
                                  "user_metadata": {
                                    "key": "string",
                                    "value": "string"
                                  },
                                  "user_settings": {
                                    "key": "string",
                                    "value": "string"
                                  }
                                })
    """
    try:
        if not isinstance(user_metadata, dict):
            raise Exception("user_metadata object should be a dict.")
        headers = {"Accept": "application/json"}
        response = requests.post(url, json=user_metadata, headers=headers)
        return json.loads(response.content)
    except Exception as e:
        raise Exception("Login failed. " + str(e))


def login_user(url: str, username: str, password: str):
    """
    Send credentials to CC-ApiServer and Authenticate a user. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): url of login route of CC-ApiServer
        username (str): username
        password (str): password of the user

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if authentication fails

    Examples:
        >>> from cerebralcortex_rest import login_user
        >>> login_user(url="http://localhost/api/v3/user/default/login", username="demo", password="demo")

    """
    try:
        data = {"username": str(username), "password": str(password)}
        headers = {"Accept": "application/json"}
        response = requests.post(url, json=data, headers=headers)

        return json.loads(response.content)
    except Exception as e:
        raise Exception("Login failed. " + str(e))


def get_user_config(url: str, auth_token):
    """
    Get user metadata from CC-ApiServer. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): url of user-config [GET] route of CC-ApiServer
        auth_token (str): auth token of a user

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if it fails to get user configs

    Examples:
        >>> from cerebralcortex_rest import get_user_config
        >>> get_user_config(url="http://localhost/api/v3/user/default/config", auth_token="jwt-auth-tocken")

    """
    try:
        headers = {"Accept": "application/json", "Authorization": auth_token}
        response = requests.get(url, headers=headers)
        return json.loads(response.content)
    except Exception as e:
        raise Exception("Failed to get user configs. " + str(e))


# ------------------------ STREAM ROUTE ------------------------#

def register_stream(url: str, auth_token: str, stream_metadata: str):
    """
    Send stream metadata to CC-ApiServer for registration. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): url of stream-registration route of CC-ApiServer
        auth_token (str): auth token of a user
        stream_metadata (dict): metadata of the stream

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if stream registration fails

    Examples:
        >>> from cerebralcortex_rest import register_stream
        >>> register_stream(url="http://localhost/api/v3/stream/default/register", auth_token="jwt-auth-token",
                            stream_metadata={
                                          "name": "string",
                                          "description": "string",
                                          "data_descriptor": [
                                            {
                                              "name": "string",
                                              "type": "string",
                                              "attributes": [
                                                {
                                                  "key": "string",
                                                  "value": "string"
                                                }
                                              ]
                                            }
                                          ],
                                          "modules": [
                                            {
                                              "name": "string",
                                              "version": "string",
                                              "authors": [
                                                {
                                                  "developer_name": "string",
                                                  "email": "string",
                                                  "attributes": [
                                                    {
                                                      "key": "string",
                                                      "value": "string"
                                                    }
                                                  ]
                                                }
                                              ],
                                              "attributes": [
                                                {
                                                  "key": "string",
                                                  "value": "string"
                                                }
                                              ]
                                            }
                                          ]
                                        })

    """
    try:
        headers = {"Accept": "application/json", "Authorization": auth_token}
        response = requests.post(url, json=stream_metadata, headers=headers)
        return json.loads(response.content)
    except Exception as e:
        raise Exception("Stream registration failed. " + str(e))


def upload_stream_data(url: str, auth_token: str, data_file_path: str):
    """
    Upload stream data to cerebralcortex storage using CC-ApiServer. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): base url of CerebralCortex-APIServer. For example, http://localhost/
        auth_token (str): auth token of a user
        data_file_path (str): stream data file path that needs to be uploaded

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if stream data upload fails

    Examples:
        >>> from cerebralcortex_rest import upload_stream_data
        >>> upload_stream_data(url="http://localhost/api/v3/stream/default/{metadata_hash}", auth_token="jwt-aut-token")

    """
    try:
        f = open(data_file_path, "rb")
        files = {"file": (data_file_path, f)}

        headers = {"Accept": "application/json", "Authorization": auth_token}
        response = requests.put(url, files=files, headers=headers)

        return json.loads(response.content)
    except Exception as e:
        raise Exception("Stream data upload failed. " + str(e))


def get_stream_metadata(url: str, auth_token: str):
    """
    Get stream metadata from CC-ApiServer. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): url of user-config [GET] route of CC-ApiServer
        auth_token (str): auth token of a user

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if it fails to get stream metadata

    Examples:
        >>> from cerebralcortex_rest import get_stream_metadata
        >>> get_stream_metadata(url="http://localhost/api/v3/stream/metadata/default/{stream_name}", auth_token="jwt-aut-token")
    """
    try:
        headers = {"Accept": "application/json", "Authorization": auth_token}
        response = requests.get(url, headers=headers)
        return json.loads(response.content)
    except Exception as e:
        raise Exception("Failed to get stream metadata. " + str(e))


def get_stream_data(url: str, auth_token: str):
    """
    Get stream data from CC-ApiServer. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): url of user-config [GET] route of CC-ApiServer
        auth_token (str): auth token of a user

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if it fails to get stream data

    Examples:
        >>> from cerebralcortex_rest import get_stream_data
        >>> get_stream_data(url="http://localhost/api/v3/stream/data/default/{stream_name}", auth_token="jwt-aut-token")
    """
    try:
        headers = {"Accept": "application/json", "Authorization": auth_token}
        response = requests.get(url, headers=headers)
        return response
    except Exception as e:
        raise Exception("Failed to get stream metadata. " + str(e))


# ------------------------ OBJECT ROUTE ------------------------#

def get_bucket_list(url: str, auth_token: str):
    """
    Get buckets list from CC-ApiServer. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): url of object [GET] route of CC-ApiServer
        auth_token (str): auth token of a user

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if it fails to get buckets list

    Examples:
        >>> from cerebralcortex_rest import get_bucket_list
        >>> get_bucket_list(url="http://localhost/api/v3/bucket/default", auth_token="jwt-aut-token")

    """
    try:
        headers = {"Accept": "application/json", "Authorization": auth_token}
        response = requests.get(url, headers=headers)
        return json.loads(response.content)
    except Exception as e:
        raise Exception("Failed to get buckets list. " + str(e))


def get_objects_list_in_bucket(url: str, auth_token: str):
    """
    Get objects list in a bucket from CC-ApiServer. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): url of object's list [GET] route of CC-ApiServer
        auth_token (str): auth token of a user

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if it fails to get objects list in a buckets

    Examples:
        >>> from cerebralcortex_rest import get_objects_list_in_bucket
        >>> get_objects_list_in_bucket(url="http://localhost/api/v3/bucket/default/{bucket_name}", auth_token="jwt-aut-token")

    """
    try:
        headers = {"Accept": "application/json", "Authorization": auth_token}
        response = requests.get(url, headers=headers)
        return json.loads(response.content)
    except Exception as e:
        raise Exception("Failed to objects list of a bucket. " + str(e))


def get_objects_stats(url: str, auth_token: str):
    """
    Get object stats from CC-ApiServer. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): url of object's stat [GET] route of CC-ApiServer
        auth_token (str): auth token of a user

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if it fails to get object stats

    Examples:
        >>> from cerebralcortex_rest import get_objects_stats
        >>> get_objects_stats(url="http://localhost/api/v3/bucket/stats/default/{bucket_name}/{object_name}", auth_token="jwt-aut-token")
    """
    try:
        headers = {"Accept": "application/json", "Authorization": auth_token}
        response = requests.get(url, headers=headers)
        return json.loads(response.content)
    except Exception as e:
        raise Exception("Failed to object's stats. " + str(e))


def get_object(url: str, auth_token: str):
    """
    Get object stats from CC-ApiServer. "default" in url is a study_name. change it if you have created a different study_name. study_name must exist

    Args:
        url (str): url of object (download) [GET] route of CC-ApiServer
        auth_token (str): auth token of a user

    Returns:
        dict: HTTP response.content

    Raises:
        Exception: if it fails to get object

    Examples:
        >>> from cerebralcortex_rest import get_object
        >>> get_object(url="http://localhost/api/v3/bucket/default/{bucket_name}/{object_name}", auth_token="jwt-aut-token")

    """
    try:
        headers = {"Accept": "application/json", "Authorization": auth_token}
        response = requests.get(url, headers=headers)
        return json.loads(response.content)
    except Exception as e:
        raise Exception("Failed to object's stats. " + str(e))
