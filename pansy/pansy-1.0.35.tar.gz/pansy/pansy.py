import sys

from .share.config import Config, ConfigAttribute
from .share.utils import import_module_or_string
from .share.log import logger
from .share import constants
from .master.master import Master


class Pansy:

    ############################## configurable begin ##############################
    name = ConfigAttribute('NAME')

    host = ConfigAttribute('HOST')
    port = ConfigAttribute('PORT')

    room_id_begin = ConfigAttribute('ROOM_ID_BEGIN')
    room_id_end = ConfigAttribute('ROOM_ID_END')

    box_class = ConfigAttribute('BOX_CLASS',
                                get_converter=import_module_or_string)
    listener_class = ConfigAttribute('LISTENER_CLASS',
                                     get_converter=import_module_or_string)

    debug = ConfigAttribute('DEBUG')

    conn_timeout = ConfigAttribute('CONN_TIMEOUT')

    stop_timeout = ConfigAttribute('STOP_TIMEOUT')

    fps = ConfigAttribute('FPS')

    ############################## configurable end   ##############################

    config = None

    master = None

    def __init__(self):
        self.config = Config(defaults=constants.DEFAULT_CONFIG)
        self.master = Master(self)

    def run(self):
        self.master.run()

    def make_proc_name(self, subtitle):
        """
        获取进程名称
        :param subtitle:
        :return:
        """
        proc_name = '[%s:%s %s] %s' % (
            constants.NAME,
            subtitle,
            self.name,
            ' '.join([sys.executable] + sys.argv)
        )

        return proc_name

