import pytz
import datetime
from google.auth.credentials import Credentials as BaseCredentials

class Credentials(BaseCredentials):
    def __init__(self, token_obj):
        self.token_obj = token_obj
        self._update_from_token_obj()

    def _update_from_token_obj(self):
        self.token = self.token_obj.access_token
        utc = pytz.timezone('UTC')
        self.expiry = self.token_obj.expiration().astimezone(utc).replace(tzinfo=None)

    def refresh(self, *args):
        self.token_obj.do_refresh_token()
        self._update_from_token_obj()
