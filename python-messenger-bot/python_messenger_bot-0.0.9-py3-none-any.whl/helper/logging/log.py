import datetime
import logging
import os

logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logging_format, level=logging.INFO)

class Log:

    def __init__(self, name, sender_psid = '0', folder_log = '', **kwargs):
        self.logger = self.prepare_logger(name, sender_psid, folder_log)

        return super().__init__(**kwargs)

    def prepare_logger(self, name, sender_psid, folder_log):
        logger = logging.getLogger(name)

        user_log = folder_log + sender_psid + '/log ' + datetime.datetime.now().strftime('%y-%b-%d %H') + '.txt'

        try:
            fh = logging.FileHandler(user_log, 'a+')
        except FileNotFoundError:
            os.makedirs(folder_log + sender_psid, exist_ok=True)
            fh = logging.FileHandler(user_log, 'a+')

        formatter = logging.Formatter(logging_format)
        fh.setFormatter(formatter)
        logger.handlers = []
        logger.addHandler(fh)

        return logger