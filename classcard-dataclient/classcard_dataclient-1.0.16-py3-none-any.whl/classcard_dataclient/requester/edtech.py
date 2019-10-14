from ..requester import Requester
from ..settings import EDTECH_SERVER_TOKEN, CLASS_CARD_SCHOOL


class EDTechRequester(Requester):
    def __init__(self, *args, **kwargs):
        super(EDTechRequester, self).__init__(*args, **kwargs)
        self.headers = {"X-Custom-Header-3School": kwargs.get('school_id', CLASS_CARD_SCHOOL),
                        "X-Custom-Header-3App": "classcard",
                        "Authorization": EDTECH_SERVER_TOKEN}
