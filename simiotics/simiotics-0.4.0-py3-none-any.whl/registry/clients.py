"""
Simiotics registry clients and generators
"""

import grpc

from . import data_pb2_grpc
from . import functions_pb2_grpc

def data_registry_client(address: str = '0.0.0.0:7010') -> data_pb2_grpc.DataRegistryStub:
    """
    Creates a Data Registry gRPC client configured to communicate with a Data Registry gRPC server
    at the given address insecurely (without TLS).

    Args:
    address
        Address for the Data Registry gRPC server (default: '0.0.0.0:7010')

    Returns: DataRegistryStub that can be used to make client calls
    """
    channel = grpc.insecure_channel(address)
    stub = data_pb2_grpc.DataRegistryStub(channel)
    return stub

def function_registry_client(
        address: str = '0.0.0.0:7011'
    ) -> functions_pb2_grpc.FunctionRegistryStub:
    """
    Creates a Function Registry gRPC client configured to communicate with a Function Registry gRPC
    server at the given address insecurely (without TLS).

    Args:
    address
        Address for the Function Registry gRPC server (default: '0.0.0.0:7011')

    Returns: FunctionRegistryStub that can be used to make client calls
    """
    channel = grpc.insecure_channel(address)
    stub = functions_pb2_grpc.FunctionRegistryStub(channel)
    return stub
