from .schedule_type import ScheduleType
from algomax_common.settings import get_config
from algomax_common.terminal import FontColor

from .messages import INVALID_MODE_NAME


class UserScheduleData:
    """
    algomax scheduler configuration data
    """

    mode: ScheduleType = ScheduleType.ONCE
    schedule = {}

    def __init__(self, filename: str = None):
        """
        if filename provided: then this is a interval scheduler
        else: it runs code once
        :param filename: path of configuration file
        """
        if filename is not None:
            self.configure(filename)

    def configure(self, filename: str):
        """
        it loads the scheduler configuration from the file
        and check and set type of scheduler.
        the scheduler stops if mode type is invalid.
        :param filename: path of configuration file
        """
        config = get_config(filename)

        if config['mode'] == ScheduleType.ONCE.value:
            self.mode = ScheduleType.ONCE
        elif config['mode'] == ScheduleType.INTERVAL.value:
            self.mode = ScheduleType.INTERVAL
        else:
            print(FontColor.failed(INVALID_MODE_NAME))
            exit(0)

        self.schedule = config['schedule']

