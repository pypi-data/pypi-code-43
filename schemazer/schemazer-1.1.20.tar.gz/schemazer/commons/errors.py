"""
Module with errors group for fast access to error objects.
"""
from schemazer.base import SchemazerErrorGroup, SchemazerErrorBase


class RequestErrors(SchemazerErrorGroup):
    """ Simple request errors. """
    __group_name__ = 'RequestErrors'

    BadRequest = SchemazerErrorBase(
        group_name=__group_name__,
        name='BadRequest',
        description='Bad request',
    )
    NotFound = SchemazerErrorBase(
        group_name=__group_name__,
        name='NotFound',
        description='Object not found',
    )
    Undefined = SchemazerErrorBase(
        group_name=__group_name__,
        name='Undefined',
        description='Undefined error',
    )


class AccessErrors(SchemazerErrorGroup):
    """ Simple access errors. """
    __group_name__ = 'AccessErrors'

    ApiKeyInvalid = SchemazerErrorBase(
        group_name=__group_name__,
        name='ApiKeyInvalid',
        description='Invalid api key',
    )
    ApiKeyNotFound = SchemazerErrorBase(
        group_name=__group_name__,
        name='ApiKeyNotFound',
        description='Api key not found',
    )


class AuthErrors(SchemazerErrorGroup):
    """ Simple auth errors. """
    __group_name__ = 'AuthErrors'

    UserNotFound = SchemazerErrorBase(
        group_name=__group_name__,
        name='UserNotFound',
        description='User not found',
    )
    UserNotVerify = SchemazerErrorBase(
        group_name=__group_name__,
        name='UserNotVerify',
        description='User not verify',
    )
    AuthTokenExpired = SchemazerErrorBase(
        group_name=__group_name__,
        name='AuthTokenExpired',
        description='Auth token expired',
    )
