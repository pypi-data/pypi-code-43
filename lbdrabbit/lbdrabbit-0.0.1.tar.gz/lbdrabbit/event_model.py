# -*- coding: utf-8 -*-

import attr
import typing


@attr.s
class QueryString(object):
    pass


@attr.s
class Params(object):
    path = attr.ib(factory=dict)  # type: dict
    query_string = attr.ib(factory=QueryString)  # type: QueryString
    header = attr.ib(factory=dict)  # type: dict


@attr.s
class Context(object):
    authorizer_principal_id = attr.ib(default=None)
    api_key = attr.ib(default=None)
    api_id = attr.ib(default=None)
    resource_id = attr.ib(default=None)
    http_method = attr.ib(default=None)
    stage = attr.ib(default=None)
    caller = attr.ib(default=None)
    source_ip = attr.ib(default=None)
    user = attr.ib(default=None)
    user_agent = attr.ib(default=None)
    user_arn = attr.ib(default=None)
    request_id = attr.ib(default=None)
    cognito_authentication_provider = attr.ib(default=None)
    cognito_authentication_type = attr.ib(default=None)
    cognito_identity_id = attr.ib(default=None)
    cognito_identity_pool_id = attr.ib(default=None)


@attr.s
class Event(object):
    context = attr.ib()  # type: Context
    params = attr.ib()  # type: Params
    body = attr.ib()  # type: dict
    stage_variables = attr.ib()


@attr.s
class Response(object):
    pass


a = {
    "event": {
        "body-json": {
            "name": "Alice"
        },
        "params": {
            "path": {},
            "querystring": {
                "limit": "5"
            },
            "header": {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "auth": "allow",
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
                "Host": "npwh0mpo01.execute-api.us-east-1.amazonaws.com",
                "Postman-Token": "86ae9783-bbff-492e-a86a-5b147395a464",
                "User-Agent": "PostmanRuntime/7.15.2",
                "X-Amzn-Trace-Id": "Root=1-5d9908b5-c1d528d87a2b9890924332ac",
                "X-Forwarded-For": "138.88.94.112",
                "X-Forwarded-Port": "443",
                "X-Forwarded-Proto": "https"
            }
        },
        "stage-variables": {},
        "context": {
            "account-id": "",
            "api-id": "npwh0mpo01",
            "api-key": "",
            "authorizer-principal-id": "",
            "caller": "",
            "cognito-authentication-provider": "",
            "cognito-authentication-type": "",
            "cognito-identity-id": "",
            "cognito-identity-pool-id": "",
            "http-method": "POST",
            "stage": "dev",
            "source-ip": "138.88.94.112",
            "user": "",
            "user-agent": "PostmanRuntime/7.15.2",
            "user-arn": "",
            "request-id": "1734556b-0647-42aa-9e62-4982cb9a52cc",
            "resource-id": "gpwyfh",
            "resource-path": "/users2"
        }
    }
}
