import traceback
from classcard_dataclient.client.action import DataClient
from config import SCHOOL_NAME
from utils.loggerutils import logging

logger = logging.getLogger(__name__)


class BaseSync(object):
    def __init__(self):
        self.client = DataClient()
        code, school = self.client.get_school_by_name(SCHOOL_NAME)
        if code:
            logger.error("Error: get school info, Detail: {}".format(school))
        self.school_id = school.get("uuid")

    @NotImplementedError
    def sync(self):
        pass

    def start(self):
        try:
            self.sync()
        except (Exception,):
            logger.error("Error: sync error, Detail: {}".format(traceback.print_exc()))
