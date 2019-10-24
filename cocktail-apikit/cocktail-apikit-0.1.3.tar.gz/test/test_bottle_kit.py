import time

import jwt
import pytest
from webtest import TestApp, TestResponse

from test.conftest import app


@pytest.fixture(scope='function')
def api_client():
    client = TestApp(app)
    yield client


def build_jwt_token(**kwargs):
    return jwt.encode(
        {
            'user': 'test',
            'iss': 'MyTest-test',
            **kwargs,
        },
        key='123', algorithm='HS256'
    ).decode()


@pytest.fixture(scope='function')
def jwt_token():
    return build_jwt_token()


def test_json_response(api_client):
    result = api_client.get('/index')
    assert result.status_int == 200


def test_cors_response(api_client):
    result = api_client.get('/documents')
    print(result._headers)
    assert result.status_int == 200


def test_jwt_authentication_ok(api_client, jwt_token):
    result = api_client.get('/auth_access', headers={'authorization': f"bearer {jwt_token}"})
    assert result.status_int == 200
    assert result.text == 'OK'


def test_jwt_authentication_expired(api_client):
    token = build_jwt_token(exp=int(time.time()))
    response: TestResponse = api_client.get('/auth_access', headers={'authorization': f"bearer {token}"},
                                            expect_errors=True)
    assert response.status_int == 401


def test_jwt_authentication_wrong_issuer_fail(api_client):
    token = build_jwt_token(iss='MyTest-wrongenv')
    response: TestResponse = api_client.get('/auth_access', headers={'authorization': f"bearer {token}"},
                                            expect_errors=True)
    assert response.status_int == 401


def test_jwt_authentication_fail(api_client):
    response: TestResponse = api_client.get('/auth_access', expect_errors=True)
    assert response.status_int == 401


def test_500_error_handle(api_client):
    response: TestResponse = api_client.post('/error', expect_errors=True)
    assert response.status_int == 500
    assert 'status' in response.json
    assert 'errors' in response.json
    assert 'traceback' in response.json
