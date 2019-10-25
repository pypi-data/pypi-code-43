from ._firestore.mockstore import Client, MockClient
from . import _apps, MockApp, _DEFAULT_APP_NAME


def create_firestore_mock_client() -> MockClient:
    """
    creates a client not connected to the name of a MockApp
    :return:
    """
    return MockClient()


def client(app: MockApp = None) -> Client:
    """
    I set up a client client based on the name of the MockApp that passes in the "app" param
    if you don't pass me "app" I consider it default_app
    :param app:
    :return:
    """
    _app = None
    if app is None:
        _app = _apps.get(_DEFAULT_APP_NAME)
        if _app is None:
            raise ValueError("the application has not been initialized")
    else:
        _app = _apps.get(app.name)
    
        if _app.firestore is None:
            _app.set_firestore(create_firestore_mock_client())
            
        return _app.firestore

    raise Exception("....")