from schemazer.base import SchemazerGroup, SchemazerMethod
from schemazer.commons.errors import AuthErrors, RequestErrors
from schemazer.commons.limits import AllLimit
from schemazer.commons.parameters import AuthParameters, SystemParameters
from schemazer.commons.response_fields import TokenField


class AuthGroup(SchemazerGroup):
    __group_name__ = 'auth'

    signInEmail = SchemazerMethod(
        group_name=__group_name__,
        name='signInEmail',
        description='Sign in by email.',
        parameters=[
            AuthParameters.Email(),
            AuthParameters.Password()
        ],
        headers=[],
        cookies=[],
        systems=[SystemParameters.Apikey()],
        response=TokenField(),
        errors=[RequestErrors.BadRequest,
                AuthErrors.UserNotFound],
        limits=[AllLimit()],
        methods=['GET'],
    )
