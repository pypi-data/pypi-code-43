# -*- coding: utf-8 -*-
"""
   Python client to connect to the CMS via a local or remote gRPC socket.
"""
import os
import ssl
import sys
import json
import time
import grpc
import itertools

from threading                     import Timer
from distutils.version             import StrictVersion, LooseVersion

from dgpy.safehaven.api            import api_pb2
from dgpy.safehaven.api            import api_pb2_grpc

from dgpy                          import version
from dgpy.user                     import User
from dgpy.errors                   import *
from dgpy.job                      import job_is_done
from dgpy.dvol                     import Dvol, DvolCreate, RecoverySequence
from dgpy.interceptor              import access_token_auth

from dgpy.aggregates.disk          import disk_pb2
from dgpy.aggregates.dvol          import dvol_pb2, dvol_enums_pb2
from dgpy.aggregates.site          import site_pb2
from dgpy.aggregates.cluster       import cluster_pb2
from dgpy.safehaven.cron           import cron_pb2
from dgpy.safehaven.api.types      import types_enums_pb2
from dgpy.safehaven.jobsystem      import jobsystem_pb2
from dgpy.messaging.dgcomm.message import syntropy_message_pb2
from dgpy.messaging.dgcomm.message.protocol_number import ProtoNum


class CmsClient(object):
    """
    CmsClient establishes a local or remote gRCP connection with the CMS API.

    It supports the following environment variables:
        CMS_HOST:  IP address or hostname of a remote CMS connection
        CMS_PORT:  Grpc service port at $CMS_HOST (defaults to 20081)

        CMS_TOKEN: Authentication bearer token for remote connection

        CMS_USER:  Authentication user name (takese precedence after $CMS_TOKEN)
        CMS_PASS:  Login password for $CMS_USER (only if $CMS_USER is set)
    """
    # Default CMS gRPC port
    __default_cms_port = 20081

    # Default (absolute) file path to the CMS Manager Unix Domain Socket
    __default_cms_socket_path ='/var/cms/manager.local.sock'

    def __init__(self, channel=None, token=""):
        """Initialize a new CMS gRPC connection from @channel.
        @channel: gRPC channel
        @token:   gRPC Authentication Bearer Token
        If neither channel nor token are set, figure out from environment what to do.
        """
        self._channel = channel
        if not channel and not token:
            cms_host = os.environ.get('CMS_HOST')
            token    = os.environ.get('CMS_TOKEN')
            username = os.environ.get('CMS_USER')
            password = os.environ.get('CMS_PASS')
            if not cms_host:    # Local connection
                self._channel = self.local_channel(self.__default_cms_socket_path)
            elif token:         # Token takes precedence over login
                self._channel = self.remote_channel(cms_host, cms_port=0, token=token)
            elif not username:
                raise EnvironmentError("{}() called, but CMS_USER not set".format(self.__class__.__name__))
            elif not password:
                raise EnvironmentError("{}() called, but CMS_PASS not set".format(self.__class__.__name__))
            else:               # Remote login
                self._channel, token = self.remote_login(username, password, cms_host)
        self._token = token
        self.stub = api_pb2_grpc.DgAPIStub(self._channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._channel is not None:
            self._channel.close()
        return False

    def __del__(self):
        if self._channel is not None:
            self._channel.close()

    #
    # Connection Handling
    #
    @classmethod
    def Local(cls, socket_path=None):
        """Create a local CMS connection, with the ability to override @socket_path.
           @socket_path: optional file path to the (tunneled) CMS safehaven-manager socket.
        If @socket_path is not set, it falls back to the CMS defaults for the socket path.
        """
        return cls(cls.local_channel(socket_path or cls.__default_cms_socket_path))

    @classmethod
    def Remote(cls, username, password, cms_host, cms_port=0):
        """Create an authenticated CMS client by logging in at cms_host:cms_port first.
        Arguments as in remote_login().
        """
        return cls(*cls.remote_login(username, password, cms_host, cms_port))

    @classmethod
    def RemoteFromToken(cls, token, cms_host, cms_port=0):
        """Create a remote CMS client from an existing authentication @token."""
        return cls(cls.remote_channel(cms_host, cms_port, token), token)

    @staticmethod
    def local_channel(socket_path):
        """Create a local CMS connection (via @socket_path).
        @socket_path: location of the safehaven-manager Unix domain socket on the CMS.
        """
        if not os.path.exists(socket_path):
            raise EnvironmentError("Unable to connect to the CMS via {}".format(socket_path))
        return grpc.insecure_channel('unix:{}'.format(socket_path))

    @classmethod
    @handle_exceptions
    def remote_channel(cls, cms_host, cms_port=0, token=None):
        """Return a remote TLS connection to cms_host:cms_port.

        @cms_host: IP address or hostname of the CMS to connect to
        @cms_port: service port on @cms_host (falls back to CMS_PORT or default if not set)
        @token:    optional authentication bearer token (overriden by CMS_TOKEN)

        Returns a gRPC channel to @cms_host:@cms_port.
        If @token is set, this channel is automatically authenticated for every call.
        """
        client_options = (
            ('grpc.ssl_target_name_override', version.__tls_hostname__),
            ('grpc.keepalive_time_ms', 10000),         # Timeout without read activity for keepalive ping
            ('grpc.keepalive_timeout_ms', 20000),      # Timeout expecting response after keepalive ping
            ('grpc.keepalive_permit_without_calls', 1) # Send keepalive pings when there is no RPC going on
        )

        # Environment token variables overrides argument:
        token = os.environ.get('CMS_TOKEN', token)

        # Port: CMS_PORT or default if not set
        cms_port = cms_port or int(os.environ.get('CMS_PORT') or cls.__default_cms_port)

        # Server certificate validation: the grpc library supports target_name_override for SNI,
        # but the PR mentioned in https://github.com/grpc/grpc/issues/15461 performs the certificate
        # validation after the handshake, which means it requires a valid certificate; which does not
        # help here. Hence download the server's certificate and assume it is ok if it matches the hostname.
        cert = ssl.get_server_certificate((cms_host, int(cms_port)))
        creds = grpc.ssl_channel_credentials(root_certificates=cert.encode('ascii'))
        if token:
            creds = grpc.composite_channel_credentials(creds, grpc.access_token_call_credentials(token))
        return grpc.secure_channel('{0}:{1}'.format(cms_host, cms_port), creds, client_options)

    @classmethod
    @handle_exceptions
    def remote_login(cls, username, password, cms_host, cms_port=0):
        """Create an authenticated CMS client by logging in at cms_host:cms_port first.

        @username: login username at @cms_host
        @password: login password for @username
        @cms_host: same as in remote_channel
        @cms_port: same as in remote_channel

        Returns (gRPC channel, Authentication Bearer Token) on success.

        NOTE: This method skips login/authentication if the CMS_TOKEN environment variable is set.
        """
        chan = cls.remote_channel(cms_host, cms_port)
        token = os.environ.get('CMS_TOKEN')
        if not token:
            # Perform login request to obtain Authentication Bearer Token:
            req   = api_pb2.LoginRequest(user_name=username, password=password)
            token = api_pb2_grpc.DgAPIStub(chan).Login(req).token
            chan  = grpc.intercept_channel(chan, access_token_auth(token))
        return chan, token

    # CMS Client Code versioning
    @staticmethod
    def version():
        """Return the semantic version of the Syntropy core matching this Python SDK."""
        # NB: Using LooseVersion to allow suffixes such as '-dev'
        # FIXME: our versioning currently is meaningless. Perhaps split SDK version.
        return LooseVersion(version.__version__)

    @handle_exceptions
    def legacy_command(self, proto_num, *parameters):
        """
        Sends a legacy UI_CMS command @proto_num with @parameters.
        NOTE: this is _only_ for commands, not for queries.
        Like the non-legacy commands, returns a safehaven.api.api_pb2.Response object.
        """
        return self.stub.UiCmsLegacyCommand(syntropy_message_pb2.Message(
            proto_num = proto_num.value,
            params    = map(str, parameters),
        ))

    @handle_exceptions
    def legacy_query(self, proto_num, *parameters):
        """
        Sends a legacy UI_CMS query @proto_num with @parameters.
        NOTE: this is _only_ for query, not for commands.
        On success, returns the array of (string) response parameters.
        On error, raises LegacyMessageError containing the error message.
        """
        res = self.stub.UiCmsLegacyMessage(syntropy_message_pb2.Message(
            proto_num = proto_num.value,
            params    = map(str, parameters),
        ))
        if ProtoNum(res.proto_num).IsErr():
            # The exception cause is in most cases the last member of the res.params array.
            exc = "".join(res.params[-1:]) or "E_FATAL"
            # FIXME: until #4296 is resolved, the following will not be triggered:
            if exc == "E_CMS_DVOL_DOES_NOT_EXIST":
                raise NotFoundError(exc)
            raise LegacyMessageError(exc)
        return res.params

    #
    # Computed Attributes
    #
    @property
    def sites(self):
        """Return the names of registered sites."""
        return sorted(site.name for site in self.site_list())

    @property
    def srns(self):
        """Return the Service IPs of registered SRN nodes."""
        return sorted(srn.service_ip for srn in self.node_list())

    @property
    def dvols(self):
        """Return the names of all Protection Groups (aka DVOLs)."""
        return sorted(pg.name for pg in self.dvol_list())

    @property
    def targets(self):
        """Return the list of all target names known to the CMS."""
        return sorted(tgt.vm_name for pg  in self.dvols
                                  for tgt in self.dvol_list_targets(pg))
    #
    # General Cluster API
    #
    def build_version(self):
        """Return the compile-time build version."""
        # BUILD_VERSION returns a single-element string array.
        return self.legacy_query(ProtoNum.MSG_UI_CMS_GET_BUILD_VERSION)[0]

    @handle_exceptions
    def cluster_id(self):
        """Returns the (hopefully) unique ID of this cluster."""
        return self.stub.ClusterId(cluster_pb2.ClusterIdRequest()).id

    @handle_exceptions
    def cluster_status_report(self):
        """Requests a DVOL status report from the cluster manager."""
        return self.stub.ClusterStatusReport(cluster_pb2.StatusReportRequest())

    @handle_exceptions
    def cluster_monitor_set_cron(self, cron_cluster_monitor_spec):
        """Configure the crontab(5) settings for the periodic cluster status reports:
           @cron_cluster_monitor_spec: a cron_pb2.ClusterMonitorSpec struct
        """
        return self.stub.ClusterMonSetCron(cron_cluster_monitor_spec)

    @handle_exceptions
    def cluster_monitor_get_cron(self):
        """Return the crontab(5) settings for the periodic cluster status reports."""
        return self.stub.ClusterMonGetCron(cron_pb2.GetClusterMonitorSpec())

    @handle_exceptions
    def job_list(self, max_jobs=5):
        """List up to @max_jobs last jobs"""
        return self.stub.JobList(jobsystem_pb2.JobListRequest(max_jobs=max_jobs)).jobs

    @handle_exceptions
    def job_events(self):
        """Subscribe to streaming job updates."""
        return self.stub.JobEvents(jobsystem_pb2.SubscribeJobEvent())

    @handle_exceptions
    def job_status(self, job_id):
        """Return the status of @job_id."""
        return self.stub.JobStatus(jobsystem_pb2.StatusRequest(job_id=int(job_id)))

    def wait_for_job(self, job_id, timeout=0.0, is_completed=job_is_done):
        """Await completion of @job_id, return job object at completion.
        @timeout:      timeout in (fractional) seconds
        @is_completed: optional callback that returns true if @job_id is completed
        If @timeout > 0, throw a TimeOutError if @job_id does not complete within @timeout.
        """
        try:
            jobEventIterator = self.job_events()

            # The subscription-based iterator hangs if there are no updates because
            # - the job does not exist (never started), or
            # - the job already completed (no more job updates coming in).
            # To avoid both scenarios check job status first. May throw NotFoundError.
            job = self.job_status(job_id)
            if is_completed(job):
                jobEventIterator.cancel()
                return job

            def _raiseTimeOutError():
                jobEventIterator.cancel()

            t = Timer(timeout, _raiseTimeOutError)
            if timeout > 0:
                t.start()

            for ev in jobEventIterator:
                if ev.job.job_id == int(job_id) and is_completed(ev.job):
                    t.cancel()
                    jobEventIterator.cancel()
                    return ev.job
        except grpc.RpcError as err:
            if err.cancelled():
                # If job did not report completion within timeout, try again to see if an update was missed.
                # FIXME: this is a weakness in our API (CAM-10664), a better fix is suggested in CAM-11262.
                job = self.job_status(job_id)
                if is_completed(job):
                    return job
                raise TimeOutError("Job #{0} did not report completion within {1:.1f} s".format(job_id, timeout))
            raise GrpcError("{0}: {1}".format(err.code(), err.details()))

    def cms_list(self):
        """Return the 2-element list of Active (current) and Standby CMS."""
        return self.legacy_query(ProtoNum.MSG_UI_CMS_CMS_LIST)

    def user_add(self, username, passwd):
        """Add a new user @username to the system."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_USER_CREATE, username, passwd, passwd)

    def user_del(self, username):
        """Remove user @username from the system."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_USER_DELETE, username)

    def user_set_password(self, username, passwd):
        """Set the login password for @username to @passwd."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_USER_SET_PASSWORD, username, passwd, passwd)

    def user_list(self):
        """Return the list of all CMS users."""
        return [User(*u.split()) for u in self.legacy_query(ProtoNum.MSG_UI_CMS_USER_LIST)]

    def license_list(self):
        """Return details of the currently installed software license."""
        return self.legacy_query(ProtoNum.MSG_UI_CMS_LICENSE_LIST)

    def license_add(self, key):
        """Install @key as new cluster license."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_LICENSE_ADD, key)

    #
    # Sites
    #
    @handle_exceptions
    def _site_mod(self, site_specific_creds):
        """Add a new site, using site-specific credentials in @site_specific_creds."""
        return self.stub.SiteCreateOrUpdate(site_specific_creds)

    def site_update_manual(self, site_name):
        """Create or modify a site @site_name without credentials (MANUAL site)."""
        return self._site_mod(site_pb2.SiteCredentials(name=site_name))

    def site_update_vcs(self, site_name, ip, username, password):
        """Create or modify a vmWare/VCS site, with these parameters:
           @site_name: name of the VCS site
           @ip:        IP address of the vCenter server named @vcs_name
           @username:  administrator user at @vcs_name
           @password:  login password for @username
        """
        vcs = site_pb2.VcsCreds(
            name     = site_name, # FIXME: the 'name' parameter is redundant.
            ip       = ip,
            username = username,
            password = password,
        )
        return self._site_mod(site_pb2.SiteCredentials(name=site_name, vcs=vcs))

    def site_update_clc(self, site_name, account, username, password, location):
        """Create or modify a CenturyLink Cloud site, with these parameters:
           @site-name: name of the CLC site
           @account:   which CLC (sub-)account of @user to use
           @user:      CLC portal login name
           @pass:      password for @user
           @location:  data centre location to use (e.g. CA2, VA1, ...)
        """
        clc = site_pb2.ClcCreds(
            name         = site_name, # FIXME: the 'name' parameter is redundant.
            organization = account,   # FIXME: organization is actually the (sub-)account name
            username     = username,
            password     = password,
            location     = location,
        )
        return self._site_mod(site_pb2.SiteCredentials(name=site_name, clc=clc))

    def site_update_aws(self, site_name, access_key, secret_key, region):
        """Create or modify an AWS site, with these parameters:
           @site_name:  name of the AWS site
           @access_key: API access key
           @secret_key: API secret key
           @region:     Region for the AWS deployment
        """
        aws = site_pb2.AwsCreds(
            access_key_id = access_key,
            secret_key    = secret_key,
            region        = region,
        )
        return self._site_mod(site_pb2.SiteCredentials(name=site_name, aws=aws))

    def site_update_azure(self, site_name, client_id, secret, sub_id, tenant_id, region):
        """Create or modify an Azure site, with these parameters:
           @site_name:  Name of the Azure site
           @client_id:  Client ID of the Azure App
           @secret:     Client Secret or password of the Azure App
           @sub_id:     Subscription ID of the Azure account
           @tenant_id:  Tenant ID of the Azure Active Directory
           @region:     Azure region to use for this site
        """
        azure = site_pb2.AzureCreds(
            client_id       = client_id,
            client_secret   = secret,
            subscription_id = sub_id,
            tenant_id       = tenant_id,
            region          = region,
        )
        return self._site_mod(site_pb2.SiteCredentials(name=site_name, azure=azure))

    @handle_exceptions
    def site_del(self, site_name):
        """Delete site @site_name."""
        return self.stub.SiteDelete(site_pb2.SiteDelete(name=site_name))

    @handle_exceptions
    def site_list(self):
        """Return list of all registered sites."""
        return self.stub.SiteList(site_pb2.SiteList()).sites

    @handle_exceptions
    def site_list_credentials(self, site_name):
        """Return the Cloud API credentials needed for operations at @site_name."""
        return self.stub.SiteListCredentials(site_pb2.SiteListCreds(name=site_name))

    #
    # Nodes (SRNs)
    #
    def node_add(self, name, site, ip, st_ip, lst_ip, port, password):
        """Add node @name to an existing site:
           @name:     name to use for the node
           @site:     site to add @name to
           @ip:       service IP of the node @name
           @st_ip:    storage IP of the node @name
           @lst_ip:   local (iSCSI) storage IP of the node @name
           @port:     safehaven-service port at @ip
           @password: ssh root password at @ip
        """
        return self.legacy_command(ProtoNum.MSG_UI_CMS_NODE_ADD, name, site, ip, st_ip, lst_ip, port, password)

    def node_del(self, nodeName):
        """Remove node @nodeName from inventory."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_NODE_DEL, nodeName)

    @handle_exceptions
    def node_list(self):
        """Return list of all SafeHaven Replication Nodes."""
        return self.stub.NodeList(cluster_pb2.NodeListRequest()).list

    def peer_add(self, srn1_ip, srn2_ip, srn1_pass, srn2_pass):
        """Add @srn2_ip into the peer list of @srn1_ip.
           @srn1_pass: ssh password for the root account on @srn1_ip
           @srn2_pass: ssh password for the root account on @srn2_ip
        """
        return self.legacy_command(ProtoNum.MSG_UI_CMS_ADD_PEER_SRN, srn1_ip, srn2_ip, srn1_pass, srn2_pass)

    def peer_del(self, srn1_ip, srn2_ip):
        """Remove @srn2_ip from the peer list of @srn1_ip."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_REMOVE_PEER_SRN, srn1_ip, srn2_ip)

    def peer_list(self, srnIp):
        """List the peer SRN(s) of @srnIp"""
        # The first response parameter, PARAM_LIST_PEER_SRN_SUC_IP, echos @srnIp.
        # The second parameter, PARAM_LIST_PEER_SRN_SUC_PEERS, is a ","-separated string.
        return self.legacy_query(ProtoNum.MSG_UI_CMS_LIST_PEER_SRN, srnIp)[1].split(",")

    def service_stop(self, srnIp):
        """Attempt to stop the safehaven-service on @srnIp."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_SYNTROPY_SERVICE_STOP, srnIp)

    def service_start(self, srnIp):
        """Attempt to (re)start the safehaven-service on @srnIp."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_SYNTROPY_SERVICE_START, srnIp)
    #
    # DISKs:
    #
    @handle_exceptions
    def disk_list(self, srnIp):
        """List standalone disks and LVM Volume Group pools on the SRN specified by @srnIp."""
        return self.stub.DiskList(disk_pb2.DiskList(srn_ip=srnIp))

    def disk_claim(self, srnIp, disk, pool):
        """Claim @disk to create or add to a storage @pool on @srnIp:
           @srnIp: IP address of the SRN on which to add @disk
           @disk:  single disk path (e.g. "/dev/sdd")
           @pool:  name of the (LVM) pool to release @disks from
        """
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DISK_CLAIM, srnIp, disk, pool)

    def disk_unclaim(self, srnIp, disks, pool):
        """Release @disks on @srnIp from storage @pool:
           @srnIp: IP address of the SRN on which to release disks
           @disks: '+'-separated string of disk paths (e.g. "/dev/sdd + /dev/sde")
           @pool:  name of the (LVM) pool to release @disks from
        """
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DISK_UNCLAIM, srnIp, disks, pool)
    #
    # Protection Groups (DVOLs)
    #
    def dvol_create(self, params):
        """Create a legacy PG from @args, which is a string array of length
           PARAM_CREATE_DVOL_SBD_NUM_REQ_PARAMS_SHORT (see Syntropy C code).
           Alternatively you can pass a dgpy.dvol.DvolCreate namedtuple.
        """
        return self.legacy_command(ProtoNum.MSG_UI_CMS_CREATE_DVOL, *params)

    @handle_exceptions
    def pg_create(self, pg_create_request):
        """Create a non-legacy PG from the data contained in @pg_create_request (a dvol_pb2.PgCreateRequest)."""
        return self.stub.PgCreate(pg_create_request)

    @handle_exceptions
    def dvol_list(self):
        """List all known Protection Groups (aka DVOLs)."""
        return self.stub.DvolList(cluster_pb2.DvolListRequest()).list

    @handle_exceptions
    def dvol_list_properties(self, dvolName, remote=False):
        """List the properties of @dvolName on the master or @remote site."""
        return self.stub.DvolListProperties(dvol_pb2.DvolListPropertiesRequest(name=dvolName, remote=remote))

    def dvol_list_snapshots(self, dvolName, remote=False):
        """
        List the snapshots of @dvolName on the master or @remote site.
        Returns a dictionary with the following fields:
        - index:       Snapshot Index (used internally)
        - id:          Snapshot ID (hex-encoded Unix Epoch Seconds without preceding '0x')
        - consistency: stringified aggregates/dvol/sbd/SnapshotConsistency enum literal
        - schedule:    stringified aggregates/dvol/sbd/SnapshotSchedule enum literal
        - size:        size of this snapshot in bytes
        """
        res = self.legacy_query(ProtoNum.MSG_UI_CMS_LIST_DVOL_SNAP, dvolName, ('MasterSite', 'RemoteSite')[remote])
        # Caveat: response may be empty or represented as JSON 'null' - always return proper list type.
        return (res and json.loads(res[0])['snapshots']) or []

    def dvol_list_targets(self, dvolName, remote=False):
        """
        List the targets (VMs) that are protected by @dvolName on the master or @remote site.
        Returns a list of '\t'-separated strings whose elements are
        - IQN:         the iSCSI IQN of the target, e.g. "iqn.2016-09.io.ctl:u16-CA2GRRTAWS-UB02-external"
        - VM:          the target (VM) name
        - OS Category: the Operating System type, stringified target_enums_pb2.OsCategory enum literal
        - OS Version : the Operating System version (uninterpreted string, e.g. "Red Hat 7")
        - Mirror Type: the Mirror type, stringified target_enums_pb2.TargetMirrorType enum literal
        """
        # Parameter order in response message as per dvol_sbd_list_targets_to_msg:
        columns = ('iqn', 'vm_name', 'os_category', 'os_version', 'mirror_type')
        res = self.legacy_query(ProtoNum.MSG_UI_CMS_DVOL_LIST_TARGETS, dvolName, ('MasterSite', 'RemoteSite')[remote])
        return [Dvol.Target(itertools.izip(columns, l.split('\t'))) for l in res]

    def dvol_target_delete(self, dvolName, targetIqn):
        """Remove the target identified by @targetIqn from @dvolName."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_DELETE_TARGET, dvolName, targetIqn)

    def dvol_list_pluns(self, dvolName):
        """
        List the PLUNs (attached disks) of the given @dvolName.
        Returns a list of '\t'-separated strings whose elements are
        - Name:   name of the disk (e.g. "disk-0")
        - Size:   size of the disk in bytes (unfortunately a string, due to legacy message format)
        - LUN ID: LUN number (e.g. "0")
        - ISN:    iSCSI ISN number
        - IQN:    iSCSI IQN number
        - VM:     the name of the VM that this PLUN belongs to
        """
        return self.legacy_query(ProtoNum.MSG_UI_CMS_DVOL_LIST_PLUN, dvolName)

    def dvol_plun_delete(self, plunName, dvolName, vmName):
        """Remove the disk @plunName from the @vmName of @dvolName."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DELETE_PLUN, plunName, dvolName, vmName)

    def dvol_list_recovery_plan(self, dvolName, srnIp):
        """Return the recovery plan (sequence of recovery steps) of @dvolName on @srnIp."""
        res = self.legacy_query(ProtoNum.MSG_UI_CMS_DVOL_LIST_RECOVERY_PLAN, dvolName, srnIp)
         # FIXME: crazy format - need to special-case the tab
        return RecoverySequence.from_string("\n".join(map(lambda s: s.replace('\t', ',', 1), res)))

    def dvol_create_or_update_recovery_plan(self, dvolName, srnIp, rp):
        """Set @rp as recovery plan for @dvolName on SRN @srnIp.
        @rp: '|' separated string of 12 ','-separated entries (see recovery_plan.h)
        """
        # Note: keeping PARAM_DVOL_CREATE_UPDATE_RECOVERY_PLAN_VAPP_NAME empty, since this is not used anymore.
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_CREATE_UPDATE_RECOVERY_PLAN, dvolName, srnIp, rp, "")

    def dvol_set_wan_throttle(self, dvolName, speed_in_kbsec):
        """Set the WAN replication speed on @dvolName to @speed_in_kbsec:
        - a value of 0 or 'unlimited' disables the WAN throttle,
        - any other positive number is interpreted as desired replication speed in KB/sec.
        """
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_SET_WAN_THROTTLE, dvolName, speed_in_kbsec)

    def dvol_set_snapshot_period(self, dvolName, period_in_seconds):
        """Set the periodic snapshot interval on the Legacy Protection Group @dvolName to @period_in_seconds.
           A value of 0 disables periodic checkpointing.
        """
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_SET_SNAPSHOT_PERIOD, dvolName, str(period_in_seconds))

    def dvol_delete(self, dvolName):
        """Delete the legacy Protection Group @dvolName."""
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_DELETE, dvolName)

    @handle_exceptions
    def pg_delete(self, dvolName):
        """Delete the non-legacy Protection Group @dvolName."""
        return self.stub.PgDelete(dvol_pb2.PgDeleteRequest(name=dvolName, # Always clean up resources:
                                                           terminate_instances=True, delete_snapshots=True))

    @handle_exceptions
    def pg_checkpoint_config(self, dvolName, period, scheduled=None, rp=None):
        """A complex call that does 3 things in one call:
           1) Set the snapshot period from @period,
           2) set the scheduled snapshot from @scheduled (dvol_pb2.ScheduledSnapshot),
           3) set the Azure/AWS Snapshot Retention Policy from @rp (dvol_pb2.SnapshotRetentionPolicy),
           A value of 0 disables periodic checkpointing.
        """
        return self.stub.PgCheckpointConfig(dvol_pb2.PgManageCheckpointsRequest(name = dvolName,
            snapshot_period  = period,
            scheduled        = scheduled,
            retention_policy = rp,
        ))

    def dvol_manual_snapshot(self, dvolName, vssTgts=[], stopSync=False):
        """Perform a manual checkpoint on the Legacy Protection Group @dvolName:
           @vssTargets: optional list of VSS-enabled targets,
           @stopSync:   whether to (temporarily) disable synchronisation and periodic snaphots (deprecated).
        Note that @vssTargets only makes sense on WINDOWS PGs, and is currently restricted to 1 target.
        """
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_MANUAL_SNAPSHOT, dvolName, ('false','true')[stopSync], ",".join(vssTgts))

    @handle_exceptions
    def pg_manual_checkpoint(self, dvolName, vssTgts=[]):
        """Perform a manual checkpoint on the Non-Legacy Protection Group @dvolName (analogous to dvol_manual_snapshot):
           @vssTargets: optional list of VSS-enabled targets (Windows only)
        """
        # FIXME: vssTargets should be a list, see https://github.com/CenturyLinkCloud/sh-safehaven3/issues/3972
        return self.stub.PgManualCheckpoint(dvol_pb2.PgManualCheckpointRequest(name=dvolName, vss_targets=",".join(vssTgts)))

    def dvol_test_failover(self, dvolName, snap_id, temp_size, power_on=False, isolate_network=False):
        """Create a temporary test-failover recovery image from a checkpoint
           @dvolName:        protection group to perform test-failover on
           @snap_id:         hex snapshot ID to generate temporary TFO image from
           @temp_size:       size of the temporary recovery image (big enough to avoid overflow)
           @power_on:        whether to power on the remote site after creating the image
           @isolate_network: whether to isolate the DR network on start-up
        """
        pwr_action  = str(0x00000001) if power_on else "0" # defines.h: POWER_ON_ACTION
        isolate_net = ('no', 'yes')[isolate_network]       # defines.h: NO_STR / YES_STR
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_CREATE_BACKUP_IMAGE, dvolName, snap_id, temp_size, pwr_action, isolate_net)

    def dvol_test_failover_delete(self, dvolName, temp_size, power_off=False):
        """Tear down the test-failover image on @dvolName.
           @dvolName:  name of the Dvol that has the test-failover image
           @power_off: whether to power off the remote site before deleting the image
        """
        pwr_action = str(0X00000010) if power_off else "0" # defines.h: POWER_OFF_ACTION
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_TEST_FAILOVER_DELETE_RS, dvolName, pwr_action)

    def dvol_migrate(self, dvolName, pre_power_off=False, post_power_on=False):
        """Migrate the legacy Protection Group @dvolName (swap master/remote site):
           @dvolName:      name of the PG to migrate
           @pre_power_off: whether to power off the master site before migration
           @post_power_on: whether to power on the remote site after migration
        """
        power_action = 0
        if pre_power_off:
            power_action |= 0X00000010 # defines.h: POWER_OFF_ACTION
        if post_power_on:
            power_action |= 0x00000001 # defines.h: POWER_ON_ACTION
        return self.legacy_command(ProtoNum.MSG_UI_CMS_MIGRATE_DVOL, dvolName, str(power_action))

    @handle_exceptions
    def pg_migrate(self, pg_migrate_request):
        """Migrate a non-legacy PG using @pg_migrate_request (a dvol_pb2.PgMigrateRequest)."""
        return self.stub.PgMigrate(pg_migrate_request);

    @handle_exceptions
    def pg_resize(self, pg_resize_request):
        """Resize a non-legacy PG using @pg_resize_request (a dvol_pb2.PgResizeRequest)."""
        return self.stub.PgResize(pg_resize_request);

    #
    # Ansible Commands:
    #
    def dvol_install_lra(self, dvolName, vms, ips, remote_ips, users, passwds, url):
        """Perform an automated installation of the replication agent onto VMs of @dvolName:
           @dvolName:   name of the Protection Group containing @vms
           @vms:        ','-separated list of guest VM names to install onto
           @ips:        ','-separated list of the IP addresses for each VM in @vms
           @remote_ips: ','-separated list of recovery IP addresses for each VM in @vms
           @users:      ','-separated list of Administrator users for each VM in @vms
           @passwds:    ','-separated list of login passwords, for each user in @users
           @url:        URL to download the replication-agent installer from (http://...)
        """
        # FIXME: the hard-coded '0' below refers to an unused and obsolete parameter:
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_INSTALL_LRA, dvolName, vms, ips, remote_ips, users, passwds, '0', url)

    def dvol_install_makestub(self, dvolName, vms, ips, users, passwds, url, stub_os):
        """Perform an automated installation of the makestub utility onto VMs of @dvolName:
           @dvolName:   name of the Protection Group containing @vms
           @vms:        ','-separated list of guest VM names to install onto
           @ips:        ','-separated list of the IP addresses for each VM in @vms
           @users:      ','-separated list of Administrator users for each VM in @vms
           @passwds:    ','-separated list of login passwords, for each user in @users
           @url:        download URL for MakeStub.exe (http://...)
           @stub_os:    O.S. type common to all @vms, one of 'WINDOWS' or 'LINUX'
        """
        return self.legacy_command(ProtoNum.MSG_UI_CMS_DVOL_INSTALL_MAKESTUB, dvolName, vms, ips, users, passwds, url, stub_os)

if __name__ == "__main__":
    print "Python SDK Version:", CmsClient.version()
