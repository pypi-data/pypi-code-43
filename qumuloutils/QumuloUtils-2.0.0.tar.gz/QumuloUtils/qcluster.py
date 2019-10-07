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
# QCluster.py
#
# This class contains all the code necessary to deal with a Qumulo Cluster;
# including Clearing the Cache, Getting the Cluster Type, Getting the Cluster IPs,
# and finding out if the Cluster is Rebuilding.


# Import python libraries

import sys
import re
import os
import arrow
import time

from contextlib import contextmanager

# Import Qumulo REST Libraries

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.lib.request as request
import qumulo.rest
from qumulo.lib.uri import UriBuilder
from qumulo.rest_client import RestClient

# Import Logger

from QumuloUtils.qlogger import Logger

#
# QCluster Class
#
# This class contains all the code necessary to deal with a Qumulo Cluster;
# including finding files based upon age, file type, and/or file size.


class QCluster (object):

    def __init__ (self, qhost, qlogin = "admin", qpasswd = "admin", qport = 8000, logger = None):

        self.logger = logger
        self.qhost = qhost
        self.qport = int (qport)
        self.qlogin = qlogin
        self.qpasswd = qpasswd
        self.connection = None
        self.credentials = None
        self.resultsdir = None
        self.saved_files = []
        self.bucket_number = 1
        self.total_dirs = 0
        self.found_dirs = 0
        self.total_files = 0
        self.found_files = 0
        self.type_sizes = []
        self.type_counts = []
        self.first_scan = True
        self.nodeinfo = None

        # Create a connection to the cluster

        try:
            self.connection = RestClient (self.qhost, self.qport)

            # Login and store credentials

            self.credentials = self.connection.login (self.qlogin, self.qpasswd)
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to login to Qumulo cluster. Error is %s', excpt)

            raise

        return

    # Clear the cache on the cluster

    def ClearCache (self):

        # We are building this "by hand" as we don't want to have
        # the users of these scripts load the internal qumulo libraries.

        method = "POST"
        uri = str (UriBuilder (path = "/v1/debug/cache/clear"))

        try:
            request.rest_request (self.connection, self.credentials, method, uri)
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Exception on clearing cache. Error is %s', excpt)

            raise

        return

    # Get some info from the cluster for logging

    def ClusterInfo (self):

        # First, get the model number from the nodes. We will store the
        # node_info structure if they need it for later.

        try:
            self.nodeinfo = self.connection.cluster.list_nodes ()
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to list_nodes in cluster. Error is %s', excpt)

            raise

        # Get the number of nodes

        node_count = len (self.nodeinfo)

        # Get the model number from the nodes. "There can be only one!"

        model = self.nodeinfo[0]['model_number']

        # Get the revision for the cluster

        try:
            versinfo = self.connection.version.version ()
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to get version from cluster. Error is %s', excpt)

            raise

        # Get the version of software from the cluster.

        version = versinfo['revision_id']

        # Get the name of the cluster

        try:
            nameinfo = self.connection.cluster.get_cluster_conf ()
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to get name of the cluster. Error is %s', excpt)

            raise

        # Get the name of the cluster

        clustername = nameinfo['cluster_name']

        return (model, version, clustername, node_count)

    # Get the connection for making "raw" calls

    def GetConnection (self):

        return self.connection

    # Find out what IP addresses are in use by the cluster.
    # We will look at both the "management" and the floating
    # IP's. If they have floating IP's, those will always
    # be used over the "management" IP's.

    def ClusterIPs (self):

        # Get the status of the network. This will return both the
        # "management" and the floating IP's. The floating IP's will
        # have an array length of 0 if there are none. So, this is easy!

        try:
            ifinfo = self.connection.network.list_interfaces ()
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to get network interfaces from cluster. Error is %s',
                                   excpt)
            raise

        try:
            netinfo = self.connection.network.list_network_status_v2 (ifinfo[0]['id'])
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to get network information from cluster. Error is %s',
                                   excpt)
            raise

        ips = []

        for info in netinfo:
            netstatus = info['network_statuses']

            if len (netstatus[0]['floating_addresses']) > 0:
                for floats in netstatus[0]['floating_addresses']:
                    ips.append (floats)
            else:
                ips.append (netstatus[0]['address'])

            # Sort the IPs and then return it

        ips.sort()

        return ips

    # Find out if the cluster is doing a rebuild. This is only allowed if
    # the benchmarker wants this (set via the configuration file). Otherwise,
    # this is an error condition.

    def ClusterRebuilding (self):

        try:
            rebuildinfo = self.connection.cluster.get_restriper_status ()
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to get restriper status from cluster. Error is %s',
                                   excpt)

            raise

        status = rebuildinfo['status']

        if status == "NOT_RUNNING":
            return False

        return True

    # Cycle through a named set of snapshots and delete the oldest greater than the limit

    def CycleSnapshot (self, snap_list, limit = None):

        # If there is a limit, then delete all older snapshots greater than the limit

        if limit is not None:
            our_limit = 1
        else:
            our_limit = limit

        # If we don't have enough snapshots to match the limit, then move on

        if len (snap_list) <= our_limit:
            return

        # Delete all snapshots greater than the limit

        num_del = len (snap_list) - our_limit
        if num_del > 0:
            for ind in range (num_del):
                snap_id = snap_list(ind)['id']

                try:
                    self.connection.snapshot.delete_snapshot (snap_id)
                except Exception, excpt:
                    self.logger.error ("Snapshot id %s was incorrectly deleted.", snap_id)

        return

    # Delete all of the old snapshots but one...

    def RemoveOldSnapshot (self, name):

        # First, get all of the snapshots that match our name

        snap_list = self.FindSnapshot (name)

        # Now, delete all of them except for the last one

        for indx in range (0, len (snap_list) - 1):
            try:
                self.connection.snapshot.delete_snapshot (snap_list[indx]["id"])
            except Exception, excpt:
                self.logger.error ("Snapshot %d was already deleted.", snap_list[indx]["id"])

        return

    # Create a new snapshot based upon the snapshot name

    def CreateSnapshot (self, name, path):

        try:
            self.connection.snapshot.create_snapshot (name = name, path = path)
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to create a snapshot. Error is %s', excpt)

        return

    # Compare two snapshots and get the delta differences

    def CompareSnapshot (self, name):

        # First, get a list of the snapshots that match our name...

        snap_list = self.FindSnapshot (name)

        # We only need the last two of them...

        created_list = []
        modified_list = []
        deleted_list = []
        compare_list = []

        if len (snap_list) >= 2:
            range_start = len (snap_list) - 2
            for indx in range (range_start, len (snap_list)):
                compare_list.append (snap_list[indx]["id"])

            # Get the differences between the two snapshots

            old_id = compare_list[0]
            young_id = compare_list[1]

            changed_list = []

            # Get all of the changes

            next_page = "first"
            while next_page is not None:
                try:
                    if next_page == "first":
                        snap_entries = self.connection.snapshot.get_snapshot_tree_diff (young_id, old_id)
                    else:
                        snap_entries = self.connection.request ("GET", snap_entries["paging"]["next"])
                except Exception, excpt:
                    self.logger.debug ("Error retrieving the snapshot diffs with old %d and young %d ids.",
                                       old_id, young_id)

                next_page = snap_entries["paging"]["next"]

                # Iterate through the list and get all of the created, modified, and deleted
            
                if len (snap_entries["entries"]) > 0:
                    (c_list, m_list, d_list) = self.__ret_snap_diffs (snap_entries["entries"])

                created_list.append (c_list)
                modified_list.append (m_list)
                deleted_list.append (d_list)

        return (created_list, modified_list, deleted_list)

    # Iterate through a snapshot differences list and get all of the created, modified, and deleted

    def __ret_snap_diffs (self, snap_diffs):

        created_list = []
        modified_list = []
        deleted_list = []

        # Find out how many entries that we have and get all of the differences

        for indx in range (len (snap_diffs)):
            if snap_diffs[indx]["op"] == "CREATE":
                created_list.append (snap_diffs[indx])
            elif snap_diffs[indx]["op"] == "MODIFY":
                modified_list.append (snap_diffs[indx])
            else:
                deleted_list.append (snap_diffs[indx])

        return (created_list, modified_list, deleted_list)

    # Find a group of snapshots based upon the snapshot name

    def FindSnapshot (self, name):

        try:
            snap_list = self.connection.snapshot.list_snapshots ()
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to list snapshots. Error is %s', excpt)
            return

        # Build a list of the snapshots that match the name

        valid_snaps = []
        snaps = snap_list["entries"]

        for snap in range (len (snaps)):
            if snaps[snap]["name"] == name:
                valid_snaps.append (snaps[snap])

        return valid_snaps

    # Create a directory

    def CreateDir (self, name, dir_path):

        try:
            self.connection.fs.create_directory (name, dir_path)
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to create directory %s in path %s. Error is %s',
                                   name, dir_path, excpt)

            raise

        return

    # Create a file...
    # You cannot write a file without first creating it.

    def CreateFile (self, name, dataBuffer):

        try:
            dirinfo = self.connection.fs.create_file (name, dataBuffer)
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to create file %s using API. Error is %s',
                                   name, excpt)

            raise

        return dirinfo['id']

    # Write a file...
    # The file must first exist before you can write into it
    # Also, the file command actually reads from a file in your filesystem
    # in order to copy the data.

    def WriteFile (self, id, procFile):

        try:
            self.connection.fs.write_file (procFile, id_=id)
        except Exception, excpt:
            if self.logger is not None:
                self.logger.error ('Unable to write api file. Error is %s', excpt)

            raise

        return

