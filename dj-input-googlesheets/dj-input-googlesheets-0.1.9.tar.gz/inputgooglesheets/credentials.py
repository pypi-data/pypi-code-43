import pytz
import datetime
from google.auth.credentials import Credentials as BaseCredentials

class Credentials(BaseCredentials):
    def __init__(self, token_obj):
        self.token_obj = token_obj
        self.token = token_obj.access_token
        utc = pytz.timezone('UTC')
        self.expiry = token_obj.expiration().astimezone(utc).replace(tzinfo=None)

    def refresh(self, *args):
        self.token_obj.do_refresh_token()
