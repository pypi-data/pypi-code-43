import urllib
import json
import uuid
import requests

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

from .files import *


def read_policies(description, filename):
    if not exists(filename):
        write_file_contents(json.dumps([]), filename)
        return []

    policies = get_file_contents(filename)
    policies = policies.replace("@type", description["@type"])
    policies_json = json.loads(policies)
    policies_json = add_id_to_policies(policies_json)
    write_file_contents(json.dumps(policies_json, indent=4), filename)
    return policies_json

def add_id_to_policies(policies):
    for policy in policies:
        if not "id" in policy:
            policy["id"] = str(uuid.uuid4())

    return policies

def gather_user_attrs_from_headers(headers):
    if "x-user-attrs" in headers:
        # user attributes header is encoded as 'application/x-www-form-urlencoded'
        x_user_attrs = urllib.parse.parse_qs(headers["x-user-attrs"])
    else:
        x_user_attrs = {}

    return {name:value.pop() for name, value in x_user_attrs.items()}

def gather_object_attrs(description):
    print("====== " + description["@id"])
    return {"swarm:ServiceType": description["@type"], "swarm:Id": description["@id"]}

def build_access_request(description, headers, method):
    user_attrs = gather_user_attrs_from_headers(headers)
    object_attrs = gather_object_attrs(description)
    operations = [restful_methods_to_operations()[method]]

    return {
        "user_attrs": user_attrs,
        "object_attrs": object_attrs,
        "context_attrs": {},
        "operations": operations,
    }

def restful_methods_to_operations():
    return {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "DELETE": "delete",
    }

def operations_to_restful_methods():
    return {
        v: k for k, v in restful_methods_to_operations().items()
    }
