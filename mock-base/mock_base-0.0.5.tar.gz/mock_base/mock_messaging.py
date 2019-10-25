from . import get_mock_app, MockApp
from ._messaging.messaging import Message, Notification


def send(message: Message, dry_run=False, app: MockApp = None):
    if app is None:
        _a: MockApp = get_mock_app()
        if _a is None:
            raise Exception("default app not initialized ")
        _a.notify_listeners(message)
    else:
        _a = get_mock_app(app.name)
        if _a is None:
            raise Exception("{} app not initialized ".format(app.name))
        _a.notify_listeners(message)
