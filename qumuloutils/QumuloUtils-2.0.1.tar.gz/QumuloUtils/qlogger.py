# Copyright (c) 2015 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# -----------------------------------------------------------------------------
# QumuloLogger.py
#
# Class that assists with logging errors to stdout, stderr, and/or a file.

# Import python libraries

import sys
import re
import os
import logging
import time
from enum import Enum

#
# Build an enumeration for the logging level

class Level (Enum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

#
# Logger Class
#
# This class deals with using the "logging" function of python. Although it could
# be called directly within any class referencing this library, it was thought that
# encapsulating it here would make it easier to deal with. Especially for those who
# have never used logging before.

class Logger (object):

    def __init__ (self, benchName = 'Logger', logLevel = Level.DEBUG):

        # Turn on logger and set level based upon "logLevel" argument

        self.logger = logging.getLogger (benchName)
        self.logger.setLevel (Level.DEBUG)
        self.logger.propagate = 1

        # Create several handlers for the logging service.
        # Set the stream handler to stderr

        logh = logging.StreamHandler ()
        logh.setLevel (logLevel)
        self.logger.addHandler (logh)

    # Change loglevel

    def setLevel (self, logLevel):

        self.logger.setLevel (logLevel)

    # Create log files

    def logFiles (self, baseDir = "/tmp", model = "NoModel", version = "noVersion"):

        resultsDir = self.__buildResultsDir (baseDir, model, version)

        infoh = logging.FileHandler (resultsDir + "/info.log")
        infoh.setLevel (Level.INFO)
        self.logger.addHandler (infoh)

        errorh = logging.FileHandler (resultsDir + "/error.log")
        errorh.setLevel (Level.ERROR)
        self.logger.addHandler (errorh)

        debugh = logging.FileHandler (resultsDir + "/debug.log")
        debugh.setLevel (Level.DEBUG)
        self.logger.addHandler (debugh)

        return resultsDir

    # Write to logging using the "info" level

    def info (self, msg, *vargs):

        self.logger.info (msg, *vargs)

    # Write to logging using the "error" level

    def error (self, msg, *vargs):

        self.logger.error (msg, *vargs)

    # Write to logging using the "debug" level

    def debug (self, msg, *vargs):

        self.logger.debug (msg, *vargs)

    # Build a results directory to store the program results. This will be
    # based upon several items: model and version of cluster, current date
    # and time.

    def __buildResultsDir (self, baseDir, model, version):

        # Get version... It is the third item in the array (2 starting from 0)

        info = version.rsplit (' ')
        versinfo = info[2]

        # Get the date and time for format it

        dateinfo = time.strftime ("%Y%m%d%H%M%S")

        # Build the results directory such:
        #
        # resultsdir / model / version / datetime

        resultsinfo = baseDir + "/" + model + "/" + versinfo + "/" + dateinfo

        # We have to make sure that the directory is created before
        # we can use it. The assumption is that the directory does
        # not exist.

        try:
            os.makedirs (resultsinfo, 0755)
        except Exception, excpt:
            self.logger.error ('Error on makedirs = %s', excpt)
            sys.exit (1)

        return resultsinfo
