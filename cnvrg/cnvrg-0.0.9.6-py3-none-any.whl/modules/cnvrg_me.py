from cnvrg.modules.base_module import CnvrgBase
from cnvrg.helpers.auth_helper import CnvrgCredentials
from cnvrg.helpers.apis_helper import update_credentials, credentials
class Cnvrg(CnvrgBase):
    def __init__(self, url="https://app.cnvrg.io", email=None, password=None):
        if email and password:
            self.credentials = CnvrgCredentials()
            self.credentials.login(email, password, api_url=url)
            update_credentials()
            return
        self.credentials = credentials

    def me(self):
        return self.credentials.username