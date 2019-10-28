import logging
import random
import re

import requests


logger = logging.getLogger(__name__)


class SmsGate:
    '''
    https://smsc.ru/api/#menu
    '''

    __url = 'https://smsc.ru/sys/send.php'
    __digits_re = re.compile(r'\D')

    def __init__(self, login, password, sender=None, debug=False):
        self.__login = login
        self.__password = password
        self.__sender = sender
        self.__recipient = None
        self.__debug = debug

    def send(self, **kwargs):
        self.__recipient = self.__digits_re.sub('', kwargs.get('recipient', ''))
        if len(self.__recipient) != 11:
            raise 'Must define `recipient` key with 11 digits of phone number'
        if self.__recipient.startswith('8'):
            self.__recipient = '7{:s}'.format(self.__recipient[1:])
        text = kwargs.get('text', '')
        if not text:
            raise 'Must define `text` key with any unicode string'
        params = {
            'login'   : self.__login,
            'psw'     : self.__password,
            'phones'  : '+{:s}'.format(self.__recipient),
            'mes'     : text,
            'charset' : 'utf-8',
        }
        if self.__sender:
            params['sender'] = self.__sender
        if self.__debug:
            logger.info('Send SMS `{:s}` to {:s}'.format(text, self.__recipient))
        else:
            requests.get(self.__url, params=params)

    def send_random_code(self, recipient_phone, tmpl=None):
        rand = random.randrange(10000, 99999)
        self.send(
            recipient = recipient_phone,
            text = (tmpl or self.__tmpl_for_random_code()) % rand,
        )
        return rand

    def recipient(self):
        return self.__recipient

    def __tmpl_for_random_code(self):
        return 'You must type %d as checking code'
