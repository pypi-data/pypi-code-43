#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018,2019 Aljoscha Pörtner
# Copyright 2019 André Kirsch
# This file is part of SwarmRob.
#
# SwarmRob is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SwarmRob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SwarmRob.  If not, see <https://www.gnu.org/licenses/>.

import logging
from logging import handlers


class RemoteLogger(object):
    """
    Singleton class for the remote logger
    """

    def __init__(self, hostname, port, worker_uuid, swarm_uuid):
        """
            Initialization of the RemoteLogger
        :param hostname: name of the host the remote logger is running on
        :param port: port the remote logger is listening on
        """
        self.worker_uuid = worker_uuid
        self.swarm_uuid = swarm_uuid
        self.remote_logger = None
        if hostname is not None and port is not None:
            self.server_name = hostname
            self.server_port = port

            self.remote_logger = logging.getLogger(__name__)
            self.remote_logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                    '%(swarm_uuid)s %(worker_uuid)s %(asctime)s %(name)-12s %(levelname)-8s %(message)s')
            socket_handler = logging.handlers.SocketHandler(self.server_name,
                                                            self.server_port)
            socket_handler.setFormatter(formatter)
            self.remote_logger.addHandler(socket_handler)

    def debug(self, msg, *args):
        """
            Overwritten debug method of the logging module. Adds additional information like the uuid of the swarm and
            worker to the remote logging
        :param msg: Message that should be logged
        :param args: List of additional arguments
        :return:
        """
        if self.remote_logger is not None:
            self.remote_logger.debug(msg, *args, extra={'swarm_uuid': self.swarm_uuid, 'worker_uuid': self.worker_uuid})
            return True
        return False

    def error(self, msg, *args):
        """
            Overwritten error method of the logging module. Adds additional information like the uuid of the swarm and
            worker to the remote logging
        :param msg: Message that should be logged
        :param args: List of additional arguments
        :return:
        """
        if self.remote_logger is not None:
            self.remote_logger.error(msg, *args, extra={'swarm_uuid': self.swarm_uuid, 'worker_uuid': self.worker_uuid})
            return True
        return False

    def exception(self, exception, msg=""):
        """
            Overwritten exception method of the logging module. Adds additional information like the uuid of the swarm
            and worker to the remote logging
        :param exception: Thrown exception
        :param msg: Message that should be logged
        :return:
        """
        if self.remote_logger is not None:
            error_msg = msg + "\n" + exception
            self.remote_logger.error(error_msg, extra={'swarm_uuid': self.swarm_uuid, 'worker_uuid': self.worker_uuid})
            return True
        return False
