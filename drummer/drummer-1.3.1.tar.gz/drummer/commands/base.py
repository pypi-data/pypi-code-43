# -*- coding: utf-8 -*-
from sys import exit as sys_exit
from drummer.messages import Request, StatusCode
from drummer.sockets.client import SocketClient

class BaseCommand():
    """Base command to be subclassed. """

    CLASSPATH = 'drummer/events'

    def __init__(self, config):

        # load configuration
        self.config = config

    def execute(self):
        raise NotImplementedError


class RemoteCommand(BaseCommand):
    """ Base remote command to be sublcassed. It provides socket connection test """

    def __init__(self, config):

        super().__init__(config)


    def test_socket_connection(self):

        config = self.config

        # prepare request to listener
        request = Request()
        request.set_classname('SocketTestEvent')
        request.set_classpath(self.CLASSPATH)

        try:

            # send request to listener
            sc = SocketClient(config)
            response = sc.send_request(request)

            assert response.status == StatusCode.STATUS_OK

            return True

        except:

            print('Connection test failed, maybe socket is down.')
            sys_exit()

        else:
            return
