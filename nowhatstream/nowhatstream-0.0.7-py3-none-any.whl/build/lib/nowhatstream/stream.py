
from .apivideo_request import BaseRequest


class Stream(BaseRequest):
    def list_all_live(self):
        return self.get('/live-streams', need_auth=True)
