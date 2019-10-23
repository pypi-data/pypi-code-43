# -*- coding: utf-8 -*-
import logging

from cornice import validators
from webob.multidict import MultiDict

from oe_utils.validation import ValidationFailure

LOG = logging.getLogger(__name__)


def schema_validator(request, schema=None, deserializer=None, **kwargs):
    """
    Validate the request body against the configured schema.

    This method exists because the default cornice validators do not bind the
    request to the schema, and our schemas need it to get to the database
    session to validate database ids.
    """
    if schema is None:
        return
    try:
        # If you're using a swagger schema (as you should), then the real
        # schema to be validated is in the body child.
        body_schema = schema["body"]
    except KeyError:
        body_schema = None
    try:
        querystring_schema = schema["querystring"]
    except KeyError:
        querystring_schema = None
    if querystring_schema:
        try:
            mode = querystring_schema.get_mode(request)
        except AttributeError:
            mode = "strict"
        querystring_schema = querystring_schema.bind(request=request, mode=mode)
        validators.colander_querystring_validator(
            request, schema=querystring_schema, deserializer=deserializer, **kwargs
        )
        request.validated_querystring = request.validated

    if body_schema:
        try:
            mode = body_schema.get_mode(request)
        except AttributeError:
            mode = "strict"
        body_schema = body_schema.bind(request=request, mode=mode)
        validators.colander_body_validator(
            request, schema=body_schema, deserializer=deserializer, **kwargs
        )


def _formdata_deserializer(request):
    """
    Deserialize a requests which has their data as formdata.

    The default deserializer would take the data out of request.json unless
    the content-type is application/x-www-form-urlencoded.
    We have formdata and formdata.
    """
    cstruct = {
        "method": request.method,
        "url": request.url,
        "path": request.matchdict,
        "body": request.POST.mixed(),
    }

    for sub, attr in (
        ("querystring", "GET"),
        ("header", "headers"),
        ("cookies", "cookies"),
    ):
        data = getattr(request, attr)
        if isinstance(data, MultiDict):
            data = data.mixed()
        else:
            data = dict(data)
        cstruct[sub] = data

    return cstruct


def formdata_schema_validator(
    request, schema=None, deserializer=_formdata_deserializer, **kwargs
):
    """
    Validate a request which send their data as formdata.

    The default validator would take the data out of request.json unless
    the content-type is application/x-www-form-urlencoded.
    We have formdata use-cases. This validator will always take the data
    out of `request.POST.mixed()`
    """
    return schema_validator(request, schema=schema, deserializer=deserializer, **kwargs)


def cornice_error_handler(request):
    """
    Handle validation errors in a OE-compatible way.

    This mimics the behaviour in other applications who use manual validation
    The 2nd parameter of ValidationFailure in other applications is normally
    `colander.Invalid.asdict()`. Here we replicate this output from the errors
    given by cornice in `request.errors`.
    """
    service_name = request.current_service.name
    raise ValidationFailure(
        "Fouten bij het valideren van de {} request.".format(service_name),
        {
            error["location"] + "." + error["name"]: error["description"]
            for error in request.errors
        },
    )
