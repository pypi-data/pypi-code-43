# Test json api

import pycws
import base64

URL = "http://localhost:2222/cws/api/"
# URL = "http://cws.quaivecloud.com/cws/api/"

""" The admin accesses the system and prepares a user to support encryption.
To do so, a temporary certificate is generated, saved to cws and passed to the
user. The certificate serves as token so that the user is allowed to set her
initial password.
"""


def test_fetch_members():
    data = pycws.fetch_members(URL, "admin", "admin")
    assert len(data["members"]) > 0
    assert data["returnCode"] == 200


def test_invite_delete_member():

    data = pycws.fetch_members(URL, "admin", "admin", "test_user")
    assert len(data["members"]) == 0
    assert data["returnCode"] == 406

    data = pycws.invite_member(URL, "admin", "admin", "test_user")
    assert data["returnCode"] == 200

    # Now there should be one test user
    data = pycws.fetch_members(URL, "admin", "admin", "test_user")
    assert len(data["members"]) == 1
    assert data["returnCode"] == 200

    # reinvite the same user and check that we get a failure
    data = pycws.invite_member(URL, "admin", "admin", "test_user")
    assert data["returnCode"] == 595

    # Clean up again
    data = pycws.delete_member(URL, "admin", "admin", "test_user")
    assert data["returnCode"] == 200

    data = pycws.fetch_members(URL, "admin", "admin", "test_user")
    assert len(data["members"]) == 0
    assert data["returnCode"] == 406


""" A user has been informed that he can now upgrade her profile to support
encryption. To do so she has to visit her profile page, agree to the terms,
specify a password and upload her encryption certificate """


def test_store_retrieve_file():

    user_name = "test_file_user"
    user_pw = "password2"
    circle_name = "circle1"

    data = pycws.create_member(URL, "admin", "admin", user_name, user_pw)
    user_id = data.get("memberId")
    if not user_id:
        user_id = pycws._member_by_user(URL, "admin", "admin", user_name)
    # assert data["returnCode"] == 200
    # assert data.get("memberId") is not None

    data = pycws.create_circle(URL, "admin", "admin", circle_name)
    circle_id = data.get("circleId")
    if not circle_id:
        circle_id = pycws.get_circle_id_by_name(
            URL, "admin", "admin", circle_name)
    # assert data["returnCode"] == 200
    # assert circle_id is not None

    data = pycws.add_trustee(URL, "admin", "admin",
                             circle_id, user_id, "WRITE")
    # assert data["returnCode"] == 200

    # ... upload file
    blob = b"ABC"
    uid = "123"
    data = pycws.add_file(URL, "admin", "admin", circle_id, blob, uid)
    assert data["returnCode"] == 200
    file_id = data.get("dataId")

    data = pycws.fetch_file(URL, "admin", "admin", file_id)
    assert data["returnCode"] == 200
    assert data["metadata"][0]["dataId"] == file_id
    assert base64.b64decode(data["data"]) == blob

    data = pycws.delete_file(URL, "admin", "admin", file_id)
    assert data["returnCode"] == 200

    data = pycws.delete_circle(URL, "admin", "admin", circle_id)
    assert data["returnCode"] == 200

    data = pycws.delete_member(URL, "admin", "admin", user_name)
    assert data["returnCode"] == 200
