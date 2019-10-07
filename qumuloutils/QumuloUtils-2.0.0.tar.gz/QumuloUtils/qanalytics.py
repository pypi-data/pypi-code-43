# Copyright (c) 2019 Qumulo, Inc.
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
# QAnalytics.py
#
# This class contains all the code necessary to get some data analytics from a
# Qumulo cluster using the API.

# Import python libraries

import os
import sys
import glob
import time
import datetime
import multiprocessing
import Queue
import logging

# Import Qumulo Libraries

from QumuloUtils.qcluster import *
from QumuloUtils.qlogger import Logger

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')

# It is ALMOST impossible to debug spawned processes as they run in a separate context.
# The following methodology works perfectly. HOWEVER, a word of caution!!
#
# Make sure that you set your "thread" count to 1. This will work if you spawn hundreds
# of "threads", but the debugging output would be unworkable (to put it mildly).

import pdb

class ForkedPdb(pdb.Pdb):
    """A Pdb subclass that may be used
    from a forked multiprocessing child

    """
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin

# Leave the above code in permanently. It is NOT active until you place a 
# ForkedPdb().set_trace() in the code at the place you wish to start debugging.

# The following class allows us to build a counter for a value that
# works with multiprocessing

class Counter(object):
    def __init__(self, initval = 0):
        self.val = multiprocessing.Value('i', initval)
        self.lock = multiprocessing.Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def decrement(self):
        with self.lock:
            self.val.value -= 1

    def value(self):
        with self.lock:
            return self.val.value

#
# This class will handle all of the work for processes 2 thru N
# In the multiprocessing model (versus the Threading model), this is
# not supposed to be a class. I find that handling this as a class is
# far easier to debug as I can separate the functionality. However,
# this class needs to be instantiated by a function (which is the
# starting point for each process.

class WorkerProc (multiprocessing.Process):
    def __init__ (self, dir_q, callback = None, call_info = None,
                  host = None, login = None, passwd = None,
                  port = None, logger = None, count_in_q = None,
                  count_finished = None):

        super (WorkerProc, self).__init__ ()

        self.dir_q = dir_q
        self.count_in_q = count_in_q
        self.count_finished = count_finished
        self.qcluster = None
        self._callback = None
        self.proc_name = multiprocessing.current_process().name

        # The callback needs to be instantiated per thread. So, it is done here.

        if callback is not None:
            if call_info is not None:
                self._callback = callback (call_info)
            else:
                self._callback = callback ()

        # The normal logger will not work in a spawned process. So, we will
        # setup to ONLY output errors with the logger. If you set it to DEBUG,
        # then it will give you a whole lot more during any code testing.

        logger = multiprocessing.log_to_stderr ()
        logger.setLevel (logging.ERROR)
        logger.debug ("%s - Init done for Worker Process of QAnalytics.", self.proc_name)

        # This is a forked process and nothing survived. We need to re-instantiate
        # everything. Start by making a connection to the cluster.

        self.qcluster = QCluster (host, login, passwd, port, logger)
        return

    # Take a request from the queue and call the routine that will do the work

    def run (self):

        super (WorkerProc, self).run ()

        # As long as we weren't asked to stop, try to take new tasks from the queue.
        # The tasks are taken with a blocking "get", so no CPU cycles are wasted
        # while waiting. Also, "get is given a timeout, so stoprequest is always
        # checked, even if there's nothing in the queue.

        nowork_count = 0

        while True:
            try:
                entry = self.dir_q.get (True, 0.05)
                self.count_in_q.decrement ()

                self.list_dir (self.qcluster, self._callback, entry)

                self.count_finished.increment ()
                self.dir_q.task_done ()
            except Queue.Empty:

                # Let's terminate if nothing appears in the queue after 50 empty attempts
                # Since our queue empty timeout is 1/10 of a second, this should = 5 seconds

                nowork_count += 1
                if nowork_count == 50:
                    break

                continue

        # The queue has been empty for seconds. Let's leave after calling the helper
        # TearDown function.

        if self._callback is not None:
            self._callback.TearDown ()

        return

    #
    # List each entry in the directory

    def list_dir (self, rc, callback, d):

        # Get the directory entries.. If we have a "next page", then retrieve that instead.
        
        qconn = rc.GetConnection ()

        next_page = "first"
        while next_page != "":
            if next_page == "first":
                r = qconn.fs.read_directory(path=d["path"], page_size=1000)
            else:
                r = qconn.request("GET", r['paging']['next'])
            next_page = r['paging']['next']

            # Process each entry returned. If a file, then process through a "callback routine" if
            # it exists. If a directory, then put it on the queue for further processing by another
            # thread.

            for ent in r["files"]:

                # Does the callback exist? If so, then call it and pass in the file ref id

                ForkedPdb().set_trace ()

                # If this is a file, then process it...

                if ent["type"] == "FS_FILE_TYPE_FILE":

                    if callback is not None:
                        callback.process ("cfile", {"process-entry": ent})

                # If a directory, then we need to do some further processing

                if ent["type"] == "FS_FILE_TYPE_DIRECTORY" and int(ent["child_count"]) > 0:

                    # Before we put it in the queue for processing by another thread, we
                    # will add the directory entry. In order to do that, we will need to
                    # get the directory aggregates so that we have an accurate file and subdir
                    # count

                    # Now put it on the queue for processing by another thread
                    
                    self.dir_q.put ({"path": d["path"] + ent["name"] + "/"})
                    self.count_in_q.increment ()

                    # Call the callback object to process the directory entry (if it exists)

                    if callback is not None:
                        _id = ent["id"]
                        cur_dir = qconn.fs.read_dir_aggregates (id_ = _id, max_entries = 0)
                        callback.process ("cdir", {"process-entry": cur_dir, "entry": ent})

#
# QAnalytics Class
#
# This class inherits the QCluster class from QumuloUtils in order to work with a
# Qumulo Cluster API. 
#
# This class will perform either a full or partial scan of a Qumulo filesystem using
# the API in order to find certain user data patterns. It will optionally call a routine
# (callback provided by customer) that will provide additional individual file processing.

class QAnalytics (QCluster):

    def __init__ (self, qhost, qlogin = "admin", qpasswd = "admin", qport = 8000, 
                  logger = None, callback = None, elasticinfo = None, 
                  start_path = None, num_threads = None):

        super (QAnalytics, self).__init__ (qhost = qhost, qlogin = qlogin, qpasswd = qpasswd,
                                           qport = qport, logger = logger)

        self.start_path = []

        for indx in range (len (start_path)):
            self.start_path.append (start_path[indx])

            if self.start_path[indx][-1] != "/":
                self.start_path[indx] = self.start_path[indx] + "/"

                if logger is not None:
                    self.logger.debug ("File analysis on Qumulo cluster %s starting at path %s" % 
                                       (qhost, self.start_path[indx]))

        # Create Queues and Multiprocessing Pool

        if num_threads == None:
            self.num_threads = 1
        else:
            self.num_threads = num_threads

        self.dir_q = multiprocessing.JoinableQueue ()
        self.count_in_q = Counter ()
        self.count_finished = Counter ()

        # Create workers based upon number of threads
        
        if logger is not None:
            self.logger.debug ("Creating %d worker processes to help with finding the data." % 
                              (self.num_threads))

        # Get a list of all the IP's for the cluster. In order to get a fair distribution
        # for all of the threads (processes) across the nodes, we cannot trust that the
        # users have given us a cluster name that is round-robin'd in the DNS.

        IPs = self.ClusterIPs ()

        # Spawn all of the threads (processes)

        self.processes = []

        cur_ip = 0

        for i in range (self.num_threads):
            p = WorkerProc (dir_q = self.dir_q,
                            callback = callback,
                            call_info = elasticinfo,
                            host = IPs[cur_ip],
                            login = qlogin,
                            passwd = qpasswd,
                            port = qport,
                            logger = logger,
                            count_in_q = self.count_in_q,
                            count_finished = self.count_finished)
            self.processes.append (p)

            # Make sure we select the next IP

            cur_ip += 1
            if cur_ip == len (IPs) - 1:
                cur_ip = 0

        # Start all the worker procs

        for p in self.processes:
            p.start ()

        return

    # TearDown the threads (processes). This is only called if somebody hit "ctrl-C"

    def TearDown (self):

        if self.logger is not None:
            self.logger.debug ("TearDown in QAnalytics. Killing all threads.")

        for p in self.processes:
            p.terminate ()

        for p in self.processes:
            p.join ()

        return

    # Routine to do a incremental scan. This compares two snapshots and gets a list
    # of created, modified, and deleted files.

    def IncScan (self, snap_name):

        created, modified, deleted = self.CompareSnapshots (snap_name)

        return

    # Routine to do a full scan from a "start_path"

    def FullScan (self):

        # Read the aggregates from the start_path... 

        for indx in range (len (self.start_path)):
            root = self.connection.fs.read_dir_aggregates (path = self.start_path[indx], max_entries = 0)

            if self.logger is not None:
                self.logger.debug ("Directories to analyze: %12s" % 
                                   "{:,}".format(int(root["total_directories"])))
                self.logger.debug ("      Files to analyze: %12s" % 
                                   "{:,}".format(int(root["total_files"])))

                # Add this directory to a queue to process

                self.dir_q.put ({"path": self.start_path[indx]})
                self.count_in_q.increment ()

        time.sleep (1) # wait a bit for the queue to get build up.

        wait_count = 0
        while not self.dir_q.empty ():
            wait_count += 1
            if (wait_count % 50) == 0: # show status every ~5 seconds
                if self.logger is not None:
                    self.logger.debug ("Processed %s entries. Queue length: %s" % \
                                           (self.count_finished.value (), 
                                            self.count_in_q.value ()))
            time.sleep(1)

        for p in self.processes:
            p.join()

        if self.logger is not None:
            self.logger.debug ("Processed %s entries." % self.count_finished.value ())
            self.logger.debug ("Done with QAnalytics.")
