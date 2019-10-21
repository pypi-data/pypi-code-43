import functools

from flask import request
from flask.wrappers import Response

from properly_util_python.dynamo_helper import EnvironmentControlledDynamoHelper
from properly_util_python.user_auth import UserAuthHelper


def authorized(role):
    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):

            user_auth_helper = UserAuthHelper(EnvironmentControlledDynamoHelper())

            unauth_response = Response(
                response="{}", status=403, mimetype="application/json"
            )

            event_object = request.environ.get("event")
            user_auth = user_auth_helper.get_user_auth_context_from_event(event_object)
            if user_auth is None:
                return unauth_response

            properly_user_id_caller = user_auth_helper.get_properly_id_from_user_auth_id(
                user_auth["auth_id"]
            )
            if properly_user_id_caller is None:
                return unauth_response

            is_in_role_flag = user_auth_helper.is_user_in_role(
                properly_user_id_caller, role
            )

            if not is_in_role_flag:
                return unauth_response

            return func(*args, **kwargs)

        return inner

    return outer
