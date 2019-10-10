# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Optional, Union

import requests
from robot.api import logger
from robot.utils import ConnectionCache


class RequestConnection(object):
    """
    Settings for creating connection to Couchbase via HTTP
    """

    def __init__(self, host: str, port: int, username: str, password: str, timeout: int) -> None:
        """
        Initialization.\n

        *Args:*\n
            _host_ - hostname;\n
            _port_ - port address;\n
            _username_ - username;\n
            _password_ - user password;\n
            _timeout_ - connection attempt timeout;\n

        """
        self.host = host
        self.port = port
        self.url = 'http://{host}:{port}'.format(host=host, port=port)
        self.auth = (username, password)
        self.timeout = timeout

    def close(self) -> None:
        """Close connection"""
        pass


class CouchbaseManager(object):
    """
    Library for managing Couchbase server.

    Based on:
    [ http://docs.couchbase.com/couchbase-manual-2.5/cb-rest-api/ | Using the REST API ]

    == Dependencies ==
        | robot framework | http://robotframework.org |

    == Example ==
        | *Settings* | *Value* |
        | Library    | CouchbaseManager |
        | Library    | Collections |

        | *Test Cases* | *Action* | *Argument* | *Argument* | *Argument* | *Argument* | *Argument* |
        | Simple |
        |    | Connect To Couchbase | my_host_name | 8091 | administrator | administrator | alias=couchbase |
        |    | ${overview}= | Overview |
        |    | Log Dictionary | ${overview} |
        |    | Close All Couchbase Connections |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, pool: str = 'default') -> None:
        """
        Library initialization.\n
        Robot Framework ConnectionCache() class is prepared for working with concurrent connections.

        *Args*:\n
            _pool_: name for connection pool.
        """
        self._connection: Optional[RequestConnection] = None
        self.headers: Dict[str, str] = {}
        self._cache = ConnectionCache()
        self.pool = pool

    @property
    def connection(self) -> RequestConnection:
        """Check and return connection to Couchbase server.

        *Raises:*\n
            RuntimeError: if connection to Couchbase server hasn't been created yet.

        *Returns:*\n
            Current connection to Couchbase server.
        """
        if self._connection is None:
            raise RuntimeError('There is no open connection to Couchbase server.')
        return self._connection

    def connect_to_couchbase(self, host: str, port: Union[int, str], username: str = 'administrator',
                             password: str = 'administrator', timeout: Union[int, str] = 15, alias: str = None) -> int:
        """
        Create connection to Couchbase server and set it as active connection.

        *Args:*\n
            _host_ - hostname;\n
            _port_ - port address;\n
            _username_ - username;\n
            _password_ - user password;\n
            _timeout_ - connection attempt timeout;\n
            _alias_ - connection alias;\n

        *Returns:*\n
            Index of the created connection.

        *Example:*\n
            | Connect To Couchbase | my_host_name | 8091 | administrator | administrator | alias=rmq |
        """

        port = int(port)
        timeout = int(timeout)
        logger.debug(f'Connecting using : host={host}, port={port}, username={username},'
                     f'password={password}, timeout={timeout}, alias={alias}')

        self._connection = RequestConnection(host, port, username, password, timeout)
        return self._cache.register(self.connection, alias)

    def switch_couchbase_connection(self, index_or_alias: Union[int, str]) -> int:
        """
        Switch to another existing Couchbase connection using its index or alias.\n
        Connection alias is set in keyword [#Connect To Couchbase|Connect To Couchbase], which also returns connection index.

        *Args:*\n
            _index_or_alias_ - connection index or alias;

        *Returns:*\n
            Index of the previous connection.

        *Example:*\n
            | Connect To Couchbase | my_host_name_1 | 8091 | administrator | administrator | alias=couchbase1 |
            | Connect To Couchbase | my_host_name_2 | 8091 | administrator | administrator | alias=couchbase2 |
            | Switch Couchbase Connection | couchbase1 |
            | ${overview}= | Overview |
            | Switch Couchbase Connection | couchbase2 |
            | ${overview}= | Overview |
            | Close All Couchbase Connections |
        """

        old_index = self._cache.current_index
        self._connection = self._cache.switch(index_or_alias)
        return old_index

    def disconnect_from_couchbase(self) -> None:
        """
        Close active Couchbase connection.

        *Example:*\n
            | Connect To Couchbase | my_host_name | 8091 | administrator | administrator | alias=couchbase |
            | Disconnect From Couchbase |
        """
        logger.debug(f'Close connection with : host={self.connection.host}, port={self.connection.port}')
        self.connection.close()

    def close_all_couchbase_connections(self) -> None:
        """
        Close all open Couchbase connections.\n
        You should not use [#Disconnect From Couchbase|Disconnect From Couchbase] and
        [#Close All Couchbase Connections|Close All Couchbase Connections] together.\n
        After executing this keyword connection indexes returned by opening new connections
        [#Connect To Couchbase |Connect To Couchbase] starts from 1.\n

        *Example:*\n
            | Connect To Couchbase | my_host_name | 8091 | administrator | administrator | alias=couchbase |
            | Close All Couchbase Connections |
        """

        self._connection = self._cache.close_all()

    def _prepare_request_headers(self, body: Any = None) -> Dict[str, str]:
        """
        Prepare headers for HTTP request.

        Args:*\n
            _body_: HTTP request body.\n

        *Returns:*\n
            Dictionary with HTTP request headers\n
        """
        headers = self.headers.copy()
        headers["Accept"] = "application/json"
        if body:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        return headers

    def overview(self) -> Dict[str, Any]:
        """
        Get overview info on Couchbase server.

        *Returns:*\n
            Dictionary with overview info.

        *Raises:*\n
            raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
            | ${overview}=  |  Overview |
            | Log Dictionary  |  ${overview} |
            | ${version}=  |  Get From Dictionary | ${overview}  |  implementationVersion |
            =>\n
            | ${version} = 2.2.0-821-rel-enterprise
        """
        url = f'{self.connection.url}/pools/'
        response = requests.get(url, auth=self.connection.auth, headers=self._prepare_request_headers(),
                                timeout=self.connection.timeout)
        response.raise_for_status()
        return response.json()

    def view_all_buckets(self) -> List[Dict[str, Any]]:
        """
        Retrieve information on all buckets and their operations.

        *Returns:*\n
            List with buckets information

        *Raises:*\n
            raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
            | ${buckets}=  |  View all buckets  |  default |
            | Log list  |  ${buckets} |
            =>\n
            | List length is 3 and it contains following items:
            | 0: {u'bucketType': u'membase', u'localRandomKeyUri'
            | ...
        """
        url = f'{self.connection.url}/pools/{self.pool}/buckets'
        response = requests.get(url, auth=self.connection.auth, headers=self._prepare_request_headers(),
                                timeout=self.connection.timeout)
        response.raise_for_status()
        return response.json()

    def get_names_of_all_buckets(self) -> List[str]:
        """
        Retrieve all bucket names for active pool.

        *Returns:*\n
            List with bucket names.

        *Example:*\n
            | ${names}=  |   Get names of all buckets  |  default |
            | Log list  |  ${names} |
            =>\n
            | 0: default
            | 1: ufm
            | 2: ufm_support
        """

        names = []
        data = self.view_all_buckets()
        for item in data:
            names.append(item['name'])
        return names

    def flush_bucket(self, bucket: str) -> None:
        """
        Flush specified bucket.

        *Args:*\n
            _bucket_ - bucket name;\n

        *Raises:*\n
            raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
            | Flush bucket  |  default |

        """
        url = f'{self.connection.url}/pools/{self.pool}/buckets/{bucket}/controller/doFlush'
        response = requests.post(url, auth=self.connection.auth, headers=self._prepare_request_headers(),
                                 timeout=self.connection.timeout)
        response.raise_for_status()

    def modify_bucket_parameters(self, bucket: str, **kwargs: Any) -> None:
        """
        Modify bucket parameters.

        *Args:*\n
            _bucket_ - bucket name;\n
            _**kwargs_ - bucket parameters, parameter_name=value; parameter list can be found in
                         [http://docs.couchbase.com/couchbase-manual-2.5/cb-rest-api/#modifying-bucket-parameters| Couchbase doc]

        *Raises:*\n
            raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
            | Modify bucket parameters  |  default  |  flushEnabled=1  |  ramQuotaMB=297 |
        """
        url = f'{self.connection.url}/pools/{self.pool}/buckets/{bucket}'
        response = requests.post(url, auth=self.connection.auth, data=kwargs,
                                 headers=self._prepare_request_headers(body=kwargs), timeout=self.connection.timeout)
        response.raise_for_status()
