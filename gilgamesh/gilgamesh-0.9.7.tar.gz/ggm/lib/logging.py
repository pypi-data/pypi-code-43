"""
    Copyright (c) 2019 Contributors as noted in the AUTHORS file
    This file is part of ggm, the GILGAMESH core engine in Python.
    ggm is free software; you can redistribute it and/or modify it under
    the terms of the GNU Lesser General Public License (GPL) as published
    by the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.
    As a special exception, the Contributors give you permission to link
    this library with independent modules to produce an executable,
    regardless of the license terms of these independent modules, and to
    copy and distribute the resulting executable under terms of your choice,
    provided that you also meet, for each linked independent module, the
    terms and conditions of the license of that module. An independent
    module is a module which is not derived from or based on this library.
    If you modify this library, you must extend this exception to your
    version of the library.
    ggm is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import logging

import zmq
from zmq.log.handlers import PUBHandler

class GLog(object):
    """
        logging to resource manager
        TODO: write doc
    """
    def __init__(self, *args, **kwargs):

        self.LOG_DEST   = "ipc:///tmp/logger"

        self.glog = logging.getLogger(str(os.getpid()))
        if kwargs['verbose']:
            self.glog.setLevel(logging.DEBUG)
        else:
            self.glog.setLevel(logging.INFO)

        pub = self.context.socket(zmq.PUB)
        pub.connect(self.LOG_DEST)
        handler = PUBHandler(pub)
        #handler.root_topic = self.name

        self.glog.addHandler(handler)

        #self.glog.debug("Starting glog at {0}.".format(os.getpid()))
