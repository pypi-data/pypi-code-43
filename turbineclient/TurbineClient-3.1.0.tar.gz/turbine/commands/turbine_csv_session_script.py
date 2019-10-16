#!/usr/bin/env python
##########################################################################
# $Id: turbine_csv_session_script.py 4480 2013-12-20 23:20:21Z boverhof $
# Joshua R. Boverhof, LBNL
# See LICENSE.md for copyright notice!
#
#   $Author: boverhof $
#   $Date: 2013-12-20 15:20:21 -0800 (Fri, 20 Dec 2013) $
#   $Rev: 4480 $
#
###########################################################################
import urllib.request
import urllib.error
import csv
import sys
import os
import shutil
import json
import optparse
import sys
import os
import time
from turbine.commands.turbine_csv_script import *
from turbine.commands import add_options, post_page, get_page, get_page_by_url, get_paging, _open_config
from turbine.commands.turbine_session_script import *
from configparser import ConfigParser
import dateutil.parser
import datetime


def csv_launch(configFile, psuadeInFilename):
    """Takes a CSV file and submits all the jobs contained therein as a new session. Returns immediatly."""

    configFile.get(SECTION, 'url')
    samples = getInputsFromCSV(configFile, psuadeInFilename)
    inputsJson = writeInputsToGatewayFormat(configFile, samples)

    # create the session
    sessionid = create_session(configFile)
    print(sessionid)

    # create all the jobs in the session
    batches = len(inputsJson) / 500
    if(len(inputsJson) % 500 > 0):
        batches += 1

    print("Num batches: ", batches)

    for ii in range(0, batches):
        start = (ii)*500
        end = ((ii+1)*500)
        tmparray = inputsJson[(ii)*500:((ii+1)*500)]
        print("batch:", ii, " start:", start, " end:",
              end, " size: ", tmparray.__len__())
        createJobsResult = create_jobs(configFile, sessionid, tmparray)
        submitJobsResult = start_jobs(configFile, sessionid)

    return sessionid


def main_csv_launch(args=None):
    """Takes a CSV file and submits all the jobs contained therein as a new session. Returns immediatly."""

    op = optparse.OptionParser(usage="USAGE: %prog CSV_IN CONFIG_FILE",
                               description=main_csv_launch.__doc__)

    (options, args) = op.parse_args()
    assert(len(args) == 2)

    csvInFilename = args[0]
    configFilename = args[1]

    configFile = _open_config(configFilename)

    print(csv_launch(configFile, csvInFilename))


def write_jobs_to_csv(configFile, sessionid, csvInFilename, csvOutFilename):
    """ Gets all jobs from the session and writed them to a CSV file """

    runs = get_results(configFile, sessionid)

    # Now write the results out to PSUADE_OUT
    writeJson2CSV(configFile, runs, csvInFilename, csvOutFilename)


def main_write_jobs_to_csv(args=None):
    """ Gets all jobs from the session and writed them to a CSV file """

    op = optparse.OptionParser(usage="USAGE: %prog SESSIONID CSV_IN CSV_OUT CONFIG_FILE",
                               description=main_write_jobs_to_csv.__doc__)

    (options, args) = op.parse_args()
    assert(len(args) >= 4)

    sessionid = args[0]
    csvInFilename = args[1]
    csvOutFilename = args[2]

    configFile = _open_config(args[3])

    write_jobs_to_csv(configFile, sessionid, csvInFilename, csvOutFilename)

    print("Jobs written to", args[2])


def main_do_csv(args=None):
    """Takes a CSV file and submits all the jobs contained therein as a new session. Waits for it to return. Writes results to a new CSV file.  (To avoid overwriting the original) If a sessionId is supplied with -s, it is assumed the create and submit process has already happened, so it simple blocks waiting for results.
    """

    op = optparse.OptionParser(usage="USAGE: %prog CSV_IN CSV_OUT CONFIG_FILE",
                               description=main_do_csv.__doc__)

    (options, args) = op.parse_args()
    assert(len(args) >= 3)

    csvInFilename = args[0]
    csvOutFilename = args[1]
    configFilename = args[2]

    configFile = _open_config(configFilename)

    sessionid = options.session

    if(sessionid == None):
        sessionid = csv_launch(configFile, csvInFilename)

    print("SessionID:", sessionid)
    # loop checking that the jobs haven't finished yet
    jobsLeft = 1
    while(jobsLeft > 0):
        jobsLeft = jobs_unfinished(configFile, sessionid)
        print(jobsLeft)
        if(jobsLeft > 0):
            time.sleep(jobsLeft*5)

    # Now that the jobs are complete, get them all
    write_jobs_to_csv(configFile, sessionid, csvInFilename, csvOutFilename)
    print("Jobs written to", csvOutFilename)


main = main_list
if __name__ == "__main__":
    main()
