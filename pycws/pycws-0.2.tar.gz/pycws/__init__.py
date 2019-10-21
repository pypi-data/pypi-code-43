# module
from __future__ import absolute_import
import requests
import json

import six.moves.urllib.parse
import logging
from pycws.utils import b64encode

logger = logging.getLogger(__name__)


def _member_by_user(url, login, pw, user):
    member_id = "__invalid_user_id__"
    members = fetch_members(url, login, pw)
    member_data = [x for x in members["members"] if x["accountName"] == user]
    if len(member_data) == 1:
        member_id = member_data[0]["memberId"]
    elif len(member_data) == 0:
        logger.warning("No user found")
    else:
        logger.warning("More than one user found. This should not be possible")
    return member_id


def _post(url, login, pw, action, data={}):
    logger.info("Posting to %s" % action)
    endpoint = six.moves.urllib.parse.urljoin(url, action)

    data.update(dict(accountName=login, credential=b64encode(pw)))
    headers = {"Content-type": "application/json",
               "Accept": "application/json"}
    response = requests.post(endpoint, data=json.dumps(data), headers=headers)
    logger.info(response.text)
    return json.loads(response.text)


def invite_member(url, login, pw, user):
    data = dict(newAccountName=user)
    return _post(url, login, pw, "members/inviteMember", data)


def create_member(url, login, pw, user, user_pw):
    data = dict(newAccountName=user, newCredential=b64encode(user_pw))
    response = _post(url, login, pw, "members/createMember", data)
    return response


def fetch_members(url, login, pw, user=None):
    data = {}

    if user is not None:
        member_id = _member_by_user(url, login, pw, user)
        data["memberId"] = member_id

    return _post(url, login, pw, "members/fetchMembers", data)


def delete_member(url, login, pw, user):
    member_id = _member_by_user(url, login, pw, user)
    data = dict(memberId=member_id)
    return _post(url, login, pw, "members/deleteMember", data)


def create_circle(url, login, pw, circle_name):
    data = dict(circleName=circle_name)
    response = _post(url, login, pw, "circles/createCircle", data)
    return response


def fetch_circles(url, login, pw):
    response = _post(url, login, pw, "circles/fetchCircles")
    return response


def get_circle_id_by_name(url, login, pw, circle_name):
    circles = fetch_circles(url, login, pw)["circles"]
    circle = [x for x in circles if x["circleName"] == circle_name]
    if len(circle) == 1:
        return circle[0]["circleId"]
    logger.error(
        'More than once circle with the same name "%s". '
        "This should not happen." % circle_name
    )
    raise Exception


def delete_circle(url, login, pw, circle_id):
    data = dict(circleId=circle_id)
    response = _post(url, login, pw, "circles/deleteCircle", data)
    return response


def add_trustee(url, login, pw, circle_id, user, trust_level="READ"):
    data = dict(circleId=circle_id, memberId=user, trustLevel=trust_level)
    response = _post(url, login, pw, "trustees/addTrustee", data)
    return response


def alter_trustee(url, login, pw, circle_name, user, trust_level="READ"):
    data = dict(circleName=circle_name, memberId=user, trustLevel=trust_level)
    response = _post(url, login, pw, "trustees/alterTrustee", data)
    return response


def remove_trustee(url, login, pw, circle_name, user):
    data = dict(circleName=circle_name, memberId=user)
    response = _post(url, login, pw, "trustees/removeTrustee", data)
    return response


def add_file(url, login, pw, circle_id, blob, uid):
    data = dict(circleId=circle_id, dataName=uid, data=b64encode(blob))
    response = _post(url, login, pw, "data/addData", data)
    return response


def fetch_file(url, login, pw, data_id):
    data = dict(dataId=data_id)
    response = _post(url, login, pw, "data/fetchData", data)
    return response


def delete_file(url, login, pw, data_id):
    data = dict(dataId=data_id)
    response = _post(url, login, pw, "data/deleteData", data)
    return response
