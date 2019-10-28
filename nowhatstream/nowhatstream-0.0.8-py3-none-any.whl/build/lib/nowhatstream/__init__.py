
from flask import current_app


from .auth import ApiVideoAuth
from nowhatstream.config import configuration


class NowhatStream(object):
    def get_auth(self):
        current_app.config.update(configuration['default'])
        auth = ApiVideoAuth(current_app.config['API_VIDEO_KEY'])
