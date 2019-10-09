from PyVoice.MyDict import MyDict, DictProperty
from abc import ABC, abstractmethod
import json
from flask import Response
from random import randint


class VoicePlatformABC(ABC):

    def __init__(self, request_data_json):
        print('request_data_json: ', request_data_json)
        self._session_id = None
        self._result = None
        self._parameters = None
        self._action = None
        self._message = ''
        self._message_dict = None
        self._max_msg_length = 600

        self._greetings = ('Alrighty.',
                           'Okie Dokie.',
                           'Ok.')

        self._questions = (
            'What would you like me to do next?',
            'So what next?'
        )

        self._parameters = {}

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    def add_message(self, message):
        self._message += message

    @property
    def parameters(self):
        return self._parameters

    @property
    def action(self):
        return self._action

    @property
    def session_id(self):
        return self._session_id

    @property
    def decorated_message(self):

        print('message: ', self._message)

        random_greeting = randint(0, len(self._greetings) - 1)
        random_question = randint(0, len(self._questions) - 1)

        print('greeting: ', self._greetings[random_greeting])

        print('message length: ', len(self._message))
        print('max limit: ', self._max_msg_length)

        if len(self._message) > self._max_msg_length:
            return self._message[:self._max_msg_length-50] \
                   + '. This message is way too big so I had to truncate it!!! ' + self._questions[random_question]
        else:
            return self._greetings[random_greeting] + ' ' + self._message + ' ' + self._questions[random_question]

    @property
    def response(self):

        output_json = json.dumps(self.output)
        print('output_json: ', output_json)

        resp = Response(output_json.encode('utf-8'), status=200, mimetype='application/json')
        resp.headers['encoding'] = 'utf-8'

        return resp

    @property
    @abstractmethod
    def output(self):
        return NotImplementedError('Not implemented')
