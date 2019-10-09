from ..requester import Requester
from ..settings import EDTECH_SERVER_TOKEN


class EDTechRequester(Requester):
    def __init__(self, *args, **kwargs):
        super(EDTechRequester, self).__init__(*args, **kwargs)
        self.headers = {"X-Custom-Header-3School": kwargs['school_id'],
                        "X-Custom-Header-3App": "classcard",
                        "Authorization": EDTECH_SERVER_TOKEN}
