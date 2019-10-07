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


class SwarmRobException(Exception):
    """
       General Exception for all other SwarmRob related exceptions
    """
    pass


class NetworkException(SwarmRobException):
    """
        Errors related to network communication
    """
    pass


class DockerException(SwarmRobException):
    """
        Errors related to problems with the docker daemon
    """
    pass


class SwarmException(SwarmRobException):
    """
        Errors related to a swarm
    """
    pass


class CompositionException(SwarmRobException):
    """
        Errors related to the experiment definition
    """
    pass
