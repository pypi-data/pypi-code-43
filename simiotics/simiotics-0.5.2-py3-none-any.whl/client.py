"""
This module defines the Simiotics client class, which encodes the higher-level semantics for
interacting with simiotics services.
"""

import os
from typing import Any, Dict, Iterator, List, Optional, Tuple

from grpc_health.v1 import health_pb2, health_pb2_grpc

from .registry import data_pb2, data_pb2_grpc
from .registry import functions_pb2, functions_pb2_grpc
from .registry.clients import data_registry_client, function_registry_client, health_client
from . import version

class Simiotics:
    """
    Python representation of the simiotics platform. It is composed of clients for each of the
    individual services that comprise the platform.

    This class does nothing more than aggregate the different services. A user may use the
    appropriate component member of a Simiotics object to realize their desired behaviour against
    the platform.
    """
    def __init__(
            self,
            data_registry: Optional[data_pb2_grpc.DataRegistryStub] = None,
            function_registry: Optional[functions_pb2_grpc.FunctionRegistryStub] = None,
            data_registry_health: Optional[health_pb2_grpc.HealthStub] = None,
            function_registry_health: Optional[health_pb2_grpc.HealthStub] = None,
        ) -> None:
        """
        Creates a Simiotics instance representing one specific configuration of backends.

        Args:
        data_registry
            Data registry client (as generated, for example, by
            registry.clients.data_registry_client)
        function_registry
            Function registry client (as generated, for example, by
            registry.clients.function_registry_client)
        data_registry_health
            Health check client that can check the health of the data registry
        function_registry_health
            Health check client that can check the health of the function registry

        Returns: None
        """
        # self.version contains just the semantic version of this Simiotics client library
        self.version = version.VERSION
        # self.client_version specifies the version string that should be passed with gRPC requests
        # made by this client library
        self.client_version = version.CLIENT_VERSION

        self.data_registry = data_registry
        self.function_registry = function_registry

        self.data_registry_health = data_registry_health
        self.function_registry_health = function_registry_health

    def health(self) -> Dict[str, Any]:
        """
        Performs a health check against the registries that this client is configured to use and
        reports the results

        Args: None

        Returns: Dictionary whose keys are service identifiers and whose values are service status
        strings
        """
        NOT_CONFIGURED = 'NOT_CONFIGURED'
        HEALTHCHECK_NOT_CONFIGURED = 'HEALTHCHECK_NOT_CONFIGURED_ON_CLIENT'
        UNKNOWN = 'UNKNOWN'
        SERVING = 'SERVING'
        NOT_SERVING = 'NOT_SERVING'

        status_map: Dict[int, str] = {
            0: UNKNOWN,
            1: SERVING,
            2: NOT_SERVING,
        }

        status = {}
        if self.data_registry is None:
            status['data'] = NOT_CONFIGURED
        elif self.data_registry_health is None:
            status['data'] = HEALTHCHECK_NOT_CONFIGURED
        else:
            request = health_pb2.HealthCheckRequest()
            response = self.data_registry_health.Check(request)
            status['data'] = status_map.get(response.status, UNKNOWN)

        if self.function_registry is None:
            status['function'] = NOT_CONFIGURED
        elif self.function_registry_health is None:
            status['function'] = HEALTHCHECK_NOT_CONFIGURED
        else:
            request = health_pb2.HealthCheckRequest()
            response = self.function_registry_health.Check(request)
            status['function'] = status_map.get(response.status, UNKNOWN)

        return status

    def list_data_sources(self, offset: int, num_items: int) -> List[data_pb2.Source]:
        """
        Lists source in a Simiotics data registry

        Args:
        offset
            Offset from which list should start
        num_items
            Number of items to list

        Returns: List of Source objects
        """
        if self.data_registry is None:
            raise UninitializedRegistryError('Client has not initialized a data registry')

        request = data_pb2.ListSourcesRequest(
            version=self.client_version,
            offset=offset,
            num_items=num_items,
        )
        response = self.data_registry.ListSources(request)

        return response.sources

    def update_data_source(self, source_id: str, message: str) -> data_pb2.Source:
        """
        Marks a source as having been updated

        Args:
        source_id
            String identifying the source you would like to mark as updated
        message
            Update message signifying the nature of the marked update

        Returns: Updated Source object
        """
        if self.data_registry is None:
            raise UninitializedRegistryError('Client has not initialized a data registry')

        request = data_pb2.UpdateSourceRequest(
            version=self.client_version,
            id=source_id,
            notes=message,
        )
        response = self.data_registry.UpdateSource(request)

        return response.source

    def get_data_source(self, source_id: str) -> data_pb2.Source:
        """
        Gets a source from a Simiotics data registry

        Args:
        source_id
            String identifying the source you would like to retrieve

        Returns: Source object
        """
        if self.data_registry is None:
            raise UninitializedRegistryError('Client has not initialized a data registry')

        request = data_pb2.GetSourceRequest(version=self.client_version, id=source_id)
        response = self.data_registry.GetSource(request)

        return response.source

    def register_data_source(
            self,
            source_type: data_pb2.Source.SourceType,
            source_id: str,
            data_access_spec: str,
            description: str = ''
        ) -> data_pb2.Source:
        """
        Registers an S3 data source against a Simiotics data registry

        Args:
        source_type
            Type of source (e.g. S3, Google Cloud Storage, files on a local filesystem, etc.)
        source_id
            String identifying the source you would like to register
        data_access_spec
            String specifying how the data in the source can be accessed - e.g. for data in an S3
            bucket, this would be a key prefix
        description
            Human-readable description of the source

        Returns: Registered Source object
        """
        if self.data_registry is None:
            raise UninitializedRegistryError('Client has not initialized a data registry')

        source = data_pb2.Source(
            id=source_id,
            source_type=source_type,
            data_access_spec=data_access_spec,
            description=description,
        )

        request = data_pb2.RegisterSourceRequest(
            version=self.client_version,
            source=source,
        )
        response = self.data_registry.RegisterSource(request)

        return response.source

    def register_data(
            self,
            samples: Iterator[Tuple[str, str, str, Dict[str, str]]],
        ) -> Iterator[data_pb2.RegisterDataResponse]:
        """
        Register samples of data under a source in a Simiotics data registry

        Args:
        samples
            Iterator over data samples that should be registered; each sample is expected to be an
            ordered 4-tuple consisting of:
            1. source ID
            2. sample ID
            3. string specification of the sample
            4. dictionary of tags to apply to that sample

        Returns: Iterator over the responses from the data registry; the response objects have the
        following members:
            1. version - Simiotics Data Registry API version
            2. response_timestamp - Time at which response was sent
            3. datum - Datum that was registered against the registry
            4. error - Boolean which is True if and only if there was an error registering the
               sample in question
            5. error_message - If error is True, this is the error message
        """
        if self.data_registry is None:
            raise UninitializedRegistryError('Client has not initialized a data registry')

        def request_iterator():
            for source_id, datum_id, sample, tags in samples:
                datum = data_pb2.Datum(
                    id=datum_id,
                    source=data_pb2.Source(id=source_id),
                    content=sample,
                    tags=tags,
                )
                request = data_pb2.RegisterDataRequest(
                    version=self.client_version,
                    datum=datum,
                )
                yield request

        responses = self.data_registry.RegisterData(request_iterator())

        return responses

    def describe_data(
            self,
            source_id: str,
            data_ids: Optional[List[str]] = None,
        ) -> Iterator[data_pb2.Datum]:
        """
        Describe data registered under a source in a Simiotics data registry

        Args:
        source_id
            String identifying the source under which the data is registered
        data_ids
            Optional IDs for the data samples you would like to restrict the description to

        Returns: Iterator over the data descriptions
        """
        if self.data_registry is None:
            raise UninitializedRegistryError('Client has not initialized a data registry')

        request = data_pb2.GetDataRequest(
            version=self.client_version,
            source_id=source_id,
        )
        if data_ids is not None:
            request.ids.extend(data_ids)

        responses = self.data_registry.GetData(request)

        return (response.datum for response in responses)

    def register_function(
            self,
            key: str,
            code: str,
            tags: Dict[str, str],
            overwrite: bool = False
        ) -> functions_pb2.RegisteredFunction:
        """
        Register a function against a Simiotics function registry
        """
        if self.function_registry is None:
            raise UninitializedRegistryError('Client has not initialized a function registry')

        function_message = functions_pb2.RegisteredFunction(key=key, code=code, tags=tags)
        request = functions_pb2.RegisterFunctionRequest(
            version=self.client_version,
            function_message=function_message,
            overwrite=overwrite,
        )
        response = self.function_registry.RegisterFunction(request)

        return response.function_message

    def list_registered_functions(
            self,
            offset: int,
            num_items: int
        ) -> List[functions_pb2.RegisteredFunction]:
        """
        Lists functions in a Simiotics function registry

        Args:
        offset
            Offset from which list should start
        num_items
            Number of items to list

        Returns: List of RegisteredFunction objects
        """
        if self.function_registry is None:
            raise UninitializedRegistryError('Client has not initialized a function registry')

        request = functions_pb2.ListRegisteredFunctionsRequest(
            version=self.client_version,
            offset=offset,
            num_items=num_items,
        )
        response = self.function_registry.ListRegisteredFunctions(request)

        return response.function_messages

    def get_registered_function(self, key: str) -> Optional[functions_pb2.RegisteredFunction]:
        """
        Gets a function_message from a Simiotics function registry

        Args:
        key
            String identifying the function you would like to retrieve

        Returns: RegisteredFunction object if the key has an associated function, else returns None
        """
        if self.function_registry is None:
            raise UninitializedRegistryError('Client has not initialized a function registry')

        request = functions_pb2.GetRegisteredFunctionRequest(version=self.client_version, key=key)
        response = self.function_registry.GetRegisteredFunction(request)
        return response.function_message

    def delete_registered_function(self, key: str) -> str:
        """
        Deletes a function_message from a Simiotics function registry

        Args:
        key
            String identifying the function you would like to delete

        Returns: Key that was deleted
        """
        if self.function_registry is None:
            raise UninitializedRegistryError('Client has not initialized a function registry')

        request = functions_pb2.DeleteRegisteredFunctionRequest(
            version=self.client_version,
            key=key
        )
        response = self.function_registry.DeleteRegisteredFunction(request)
        return response.key

class UninitializedRegistryError(Exception):
    """
    This error is raised when a caller attempts to call a Simiotics client method for which the
    relevant registries are uninitialized.
    """

def client_from_env() -> Simiotics:
    """
    Generates a Simiotics client instance using environment variables to populate its members.

    Accepts the following environment variables:
    1. SIMIOTICS_DATA_REGISTRY
    2. SIMIOTICS_FUNCTION_REGISTRY

    Args: None

    Returns: Simiotics client with specified members populated
    """
    data_registry_address = os.environ.get('SIMIOTICS_DATA_REGISTRY')
    data_registry = None
    data_registry_health = None
    if data_registry_address is not None:
        data_registry = data_registry_client(data_registry_address)
        data_registry_health = health_client(data_registry_address)

    function_registry_address = os.environ.get('SIMIOTICS_FUNCTION_REGISTRY')
    function_registry = None
    function_registry_health = None
    if function_registry_address is not None:
        function_registry = function_registry_client(function_registry_address)
        function_registry_health = health_client(function_registry_address)

    client = Simiotics(
        data_registry=data_registry,
        function_registry=function_registry,
        data_registry_health=data_registry_health,
        function_registry_health=function_registry_health,
    )

    return client
