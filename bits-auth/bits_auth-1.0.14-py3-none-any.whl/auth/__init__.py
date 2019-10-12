# -*- coding: utf-8 -*-
"""Auth class file."""

import os
import sys

# import bits-api-python-client
mypath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(mypath, "bits-api-python-client"))

# pylama: ignore=E402


class Auth(object):
    """Auth class."""

    def __init__(self, settings, verbose=False, yes=False):
        """Initialize an Auth class instance."""
        self.settings = settings
        self.verbose = verbose
        self.yes = yes

    def accounts(
            self,
            ad=None,
            google=None,
            mongo=None,
            nis=None,
            people=None,
            slack=None,
            verbose=False,
            yes=False,
    ):
        """Connect to accounts class and all subclasses."""
        from bitsapiclient.services.accounts import Accounts
        if not ad:
            ad = self.ad()
        if not google:
            google = self.google()
        if not mongo:
            mongo = self.mongo()
        if not nis:
            nis = self.nis()
        if not people:
            people = self.people()
        if not slack:
            slack = self.slack()
        if not verbose:
            verbose = self.verbose
        if not yes:
            yes = self.yes

        return Accounts(
            ad=ad,
            google=google,
            mongo=mongo,
            nis=nis,
            people=people,
            slack=slack,
            verbose=verbose,
            yes=yes
        )

    def ad(self):
        """Connect to Active Directory LDAP."""
        from bitsapiclient.services.ad import AD
        return AD(
            self.settings['ldap_servers']['ad_ldap']['uri'],
            self.settings['ldap_servers']['ad_ldap']['bind_dn'],
            self.settings['ldap_servers']['ad_ldap']['bind_pw'],
            self.settings['ldap_servers']['ad_ldap']['base_dn'],
        )

    def angus(self):
        """Connect to Angus."""
        from bitsapiclient.services.angus import Angus
        return Angus(
            host=self.settings['angus']['host'],
            user=self.settings['angus']['user'],
            password=self.settings['angus']['pass'],
            path=self.settings['angus']['path'],
            verbose=self.verbose,
        )

    def aws(self):
        """Connect to AWS API."""
        from bitsapiclient.services.aws import AWS
        return AWS(
            auth=self,
            aws_access_key_id=self.settings['aws']['access_key_id'],
            aws_secret_access_key=self.settings['aws']['secret_access_key'],
            root_account=self.settings['aws']['root_account'],
            verbose=self.verbose,
        )

    def backupify(self):
        """Connect to Backupify API."""
        from bits.backupify import Backupify
        return Backupify(
            client_id=self.settings['backupify']['clientid'],
            client_secret=self.settings['backupify']['clientsecret'],
            verbose=self.verbose,
        )

    def bettercloud(self):
        """Connect to BetterCloud API."""
        from bitsapiclient.services.bettercloud import BetterCloud
        return BetterCloud(
            token=self.settings['bettercloud']['token'],
            verbose=self.verbose,
        )

    def bit(self):
        """Connect to BIT app."""
        from bitsapiclient.services.bit import BIT
        return BIT(
            user=self.settings['bit']['user'],
            group=self.settings['bit']['group'],
            workday_dir=self.settings['bit']['workday_dir'],
            verbose=self.verbose,
        )

    def bitsbot_cloud(self):
        """Connect to BITSbot cloud API."""
        from bitsapiclient.services.endpoints import Endpoints
        return Endpoints(
            self.settings['bitsbot']['api_host'],
            self.settings['bitsbot']['api_key']
        )

    def bitsdb_cloud(self):
        """Connect to BITSdb cloud API."""
        from bitsapiclient.services.endpoints import Endpoints
        return Endpoints(
            self.settings['bitsdb']['endpoints']['api_host'],
            self.settings['bitsdb']['endpoints']['api_key']
        )

    def bitsdb_local(self):
        """Connect to BITSdb local API."""
        from bitsapiclient.services.endpoints import Endpoints
        return Endpoints(
            self.settings['bitsdb']['local']['api_host'],
            self.settings['bitsdb']['local']['api_key']
        )

    def bitsdb_mongo(self):
        """Connect to BITSdb Mongo DB."""
        from bitsapiclient.services.bitsdb import BITSdb
        return BITSdb().MongoDb(
            mongo_uri=self.settings['mongo']['bitsdb']['uri'],
            mongo_db=self.settings['mongo']['bitsdb']['db'],
            verbose=self.verbose,
        )

    def bitsdb_update(self):
        """Connect to BITSdb Mongo DB."""
        from bitsapiclient.services.bitsdb import BITSdb
        return BITSdb().MongoDb(
            mongo_uri=self.settings['mongo']['bitsdb']['uri'],
            mongo_db=self.settings['mongo']['bitsdb']['db'],
            verbose=self.verbose,
        )

    def bitsdbapi(self):
        """Connect to BITSdb API."""
        from bitsapiclient.services.bitsdbapi import BitsdbApi
        return BitsdbApi(
            api_key=self.settings['bitsdbapi']['api_key'],
            base_url=self.settings['bitsdbapi']['base_url'],
            api=self.settings['bitsdbapi']['api'],
            version=self.settings['bitsdbapi']['version'],
            verbose=self.verbose,
        )

    def bitsdbupdate(self, auth):
        """Connect to BITSdb Update class."""
        from bitsapiclient.services.bitsdb_update import BitsdbUpdate
        return BitsdbUpdate(
            auth=auth,
            project=self.settings['datastore']['project'],
            verbose=self.verbose,
        )

    def bitstore(self):
        """Connect to currrent BITStore DB."""
        from bitsapiclient.services.bitstore import BITStore
        return BITStore(
            self.settings['mysql_servers']['bitstore']['db_host'],
            self.settings['mysql_servers']['bitstore']['db_port'],
            self.settings['mysql_servers']['bitstore']['db_user'],
            self.settings['mysql_servers']['bitstore']['db_pass'],
            self.settings['mysql_servers']['bitstore']['db']
        )

    def bitstoreapi(self):
        """Connect to BITSdb API."""
        from bitsapiclient.services.bitstoreapi import BITStoreApi
        return BITStoreApi(
            api_key=self.settings['bitstoreapi']['api_key'],
            host=self.settings['bitstoreapi']['host'],
            name=self.settings['bitstoreapi']['name'],
            sa_json_file=self.settings['google']['service_account']['json'],
            version=self.settings['bitstoreapi']['version'],
            verbose=self.verbose,
        )

    def broad_io(self):
        """Connect to currrent Broad.io DB."""
        from bitsapiclient.services.broad_io import BroadIo
        return BroadIo(
            self.settings['mysql_servers']['broad_io']['db_host'],
            self.settings['mysql_servers']['broad_io']['db_port'],
            self.settings['mysql_servers']['broad_io']['db_user'],
            self.settings['mysql_servers']['broad_io']['db_pass'],
            self.settings['mysql_servers']['broad_io']['db']
        )

    def broadaccounts(self):
        """Connect to currrent Broad Accounts."""
        from bitsapiclient.services.broadaccounts import BroadAccounts
        return BroadAccounts(
            auth=self,
            verbose=self.verbose,
        )

    def calendar(self):
        """Connect to currrent Calendar DB."""
        from bitsapiclient.services.calendar import Calendar
        return Calendar(
            server=self.settings['mysql_servers']['calendar']['db_host'],
            port=self.settings['mysql_servers']['calendar']['db_port'],
            user=self.settings['mysql_servers']['calendar']['db_user'],
            password=self.settings['mysql_servers']['calendar']['db_pass'],
            db=self.settings['mysql_servers']['calendar']['db'],
            verbose=self.verbose,
        )

    def calendar_new(self):
        """Connect to new Calendar DB."""
        from bitsapiclient.services.calendar import Calendar
        return Calendar(
            server=self.settings['mysql_servers']['calendar_new']['db_host'],
            port=self.settings['mysql_servers']['calendar_new']['db_port'],
            user=self.settings['mysql_servers']['calendar_new']['db_user'],
            password=self.settings['mysql_servers']['calendar_new']['db_pass'],
            db=self.settings['mysql_servers']['calendar_new']['db'],
            api_host=self.settings['calendar']['api_host'],
            email_from=self.settings['calendar']['email_from'],
            email_from_name=self.settings['calendar']['email_from_name'],
            email_to=self.settings['calendar']['email_to'],
            email_to_name=self.settings['calendar']['email_to_name'],
            verbose=self.verbose,
        )

    def casper(self):
        """Connect to Casper DB."""
        from bitsapiclient.services.casper import Casper
        return Casper(
            self.settings['mysql_servers']['casper']['db_host'],
            self.settings['mysql_servers']['casper']['db_port'],
            self.settings['mysql_servers']['casper']['db_user'],
            self.settings['mysql_servers']['casper']['db_pass'],
            self.settings['mysql_servers']['casper']['db']
        )

    def cloudaccounts(self):
        """Connect to Cloud Accounts API."""
        from bits.cloudaccounts import CloudAccounts
        return CloudAccounts(self.google())

    def ccure(self):
        """Connect to CCURE DB."""
        from bitsapiclient.services.ccure import CCURE
        server = '%s:%s' % (
            self.settings['mssql_servers']['ccure']['db_host'],
            self.settings['mssql_servers']['ccure']['db_port'],
        )
        return CCURE(
            server=server,
            user=self.settings['mssql_servers']['ccure']['db_user'],
            password=self.settings['mssql_servers']['ccure']['db_pass'],
            database=self.settings['mssql_servers']['ccure']['db'],
            credentials_file=self.settings['ccure']['credentials'],
            personnel_file=self.settings['ccure']['personnel'],
            new_personnel_file=self.settings['ccure']['newpersonnel'],
            photos=self.settings['ccure']['photos'],
            workday_photos=self.settings['ccure']['workday_photos'],
            verbose=self.verbose,
        )

    def ccure_dev(self):
        """Connect to CCURE dev DB."""
        from bitsapiclient.services.ccure import CCURE
        server = '%s:%s' % (
            self.settings['mssql_servers']['ccure_dev']['db_host'],
            self.settings['mssql_servers']['ccure_dev']['db_port'],
        )
        return CCURE(
            server=server,
            user=self.settings['mssql_servers']['ccure_dev']['db_user'],
            password=self.settings['mssql_servers']['ccure_dev']['db_pass'],
            database=self.settings['mssql_servers']['ccure_dev']['db'],
            credentials_file=self.settings['ccure_dev']['credentials'],
            personnel_file=self.settings['ccure_dev']['personnel'],
            new_personnel_file=self.settings['ccure_dev']['newpersonnel'],
            photos=self.settings['ccure_dev']['photos'],
            workday_photos=self.settings['ccure']['workday_photos'],
            verbose=self.verbose,
        )

    def ccure_prod(self):
        """Connect to CCURE prod DB."""
        from bitsapiclient.services.ccure import CCURE
        server = '%s:%s' % (
            self.settings['mssql_servers']['ccure_prod']['db_host'],
            self.settings['mssql_servers']['ccure_prod']['db_port'],
        )
        return CCURE(
            server=server,
            user=self.settings['mssql_servers']['ccure_prod']['db_user'],
            password=self.settings['mssql_servers']['ccure_prod']['db_pass'],
            database=self.settings['mssql_servers']['ccure_prod']['db'],
            credentials_file=self.settings['ccure_prod']['credentials'],
            personnel_file=self.settings['ccure_prod']['personnel'],
            new_personnel_file=self.settings['ccure_prod']['newpersonnel'],
            photos=self.settings['ccure_prod']['photos'],
            workday_photos=self.settings['ccure']['workday_photos'],
            verbose=self.verbose,
        )

    def datawarehouse(self, dataset):
        """Connect to data warehouse."""
        from bitsapiclient.services.datawarehouse import DataWarehouse
        return DataWarehouse(
            auth=self,
            bucket='broad-bitsdb-bigquery-import',
            project='broad-bitsdb-api',
            dataset=dataset,
            verbose=self.verbose,
        )

    def dialpad(self):
        """Connect to Dialpad API."""
        from bits.dialpad import Dialpad
        return Dialpad(
            token=self.settings['dialpad']['token'],
            verbose=self.verbose,
        )

    def disclosure(self):
        """Connect to Disclosure DB."""
        from bits.disclosure import Disclosure
        return Disclosure(
            self.settings['mongo']['disclosure']['uri'],
            self.settings['mongo']['disclosure']['db']
        )

    def disclosure_dev(self):
        """Connect to Disclosure dev DB."""
        from bits.disclosure import Disclosure
        return Disclosure(
            self.settings['mongo']['disclosure_dev']['uri'],
            self.settings['mongo']['disclosure_dev']['db']
        )

    def disclosure_prod(self):
        """Connect to Disclosure prod DB."""
        from bits.disclosure import Disclosure
        return Disclosure(
            self.settings['mongo']['disclosure_prod']['uri'],
            self.settings['mongo']['disclosure_prod']['db']
        )

    def dockerhub(self):
        """Connect to DockerHub API."""
        from bitsapiclient.services.dockerhub import DockerHub
        return DockerHub(
            self.settings['dockerhub']['username'],
            self.settings['dockerhub']['password'],
            self.settings['dockerhub']['org'],
        )

    def ecs(self):
        """Connect to the ECS API."""
        from bitsapiclient.services.ecs import ECS
        return ECS(
            username=self.settings['ecs']['username'],
            password=self.settings['ecs']['password'],
            host=self.settings['ecs']['host'],
            verbose=self.verbose,
        )

    def fox(self):
        """Connect to fox."""
        from bitsapiclient.services.fox import Fox
        return Fox(
            server=self.settings['fox']['server'],
            username=self.settings['fox']['username'],
            password=self.settings['fox']['password'],
            verbose=self.verbose,
        )

    def firehose(self):
        """Connect to Firehose."""
        from bitsapiclient.services.firehose import Firehose
        return Firehose(
            verbose=self.verbose,
        )

    def github(self, token=None):
        """Return an authenticated GitHub object."""
        from bitsapiclient.services.github import GitHub
        if not token:
            token = self.settings['github']['token']
        return GitHub(
            token=token,
            org=self.settings['github']['org'],
            owner_team=self.settings['github']['owner_team'],
            role_team=self.settings['github']['role_team'],
            verbose=self.verbose,
        )

    def google(self):
        """Connect to new Google API class."""
        settings = self.settings['google']
        from bits.google import Google
        return Google(
            api_key=settings['api_key'],
            client_scopes=settings['client_secrets']['scopes'],
            client_secrets_file=settings['client_secrets']['json'],
            credentials_file=settings['client_secrets']['credentials'],
            gsuite_licenses=settings['gsuite_licenses'],
            scopes=settings['service_account']['scopes'],
            service_account_email=settings['service_account']['email'],
            service_account_file=settings['service_account']['json'],
            subject=settings['service_account']['sub_account'],
            verbose=self.verbose,
        )

    def help(self):
        """Connect to RequestTracker DB."""
        from bitsapiclient.services.rt import RequestTracker
        return RequestTracker(
            server=self.settings['mysql_servers']['help']['db_host'],
            port=self.settings['mysql_servers']['help']['db_port'],
            user=self.settings['mysql_servers']['help']['db_user'],
            password=self.settings['mysql_servers']['help']['db_pass'],
            db=self.settings['mysql_servers']['help']['db'],
            charset='latin1',
            verbose=self.verbose,
        )

    def hosts(self):
        """Connect to Hosts App."""
        from bitsapiclient.services.hosts import Hosts
        return Hosts(
            master_host_listing=self.settings['mhl']['hosts_file'],
            lockfile=self.settings['mhl']['lock_file'],
            verbose=self.verbose,
        )

    def intranet(self):
        """Connect to Intranet DB."""
        from bitsapiclient.services.iwww import IWWW
        return IWWW(
            self.settings['mysql_servers']['intranet']['db_host'],
            self.settings['mysql_servers']['intranet']['db_port'],
            self.settings['mysql_servers']['intranet']['db_user'],
            self.settings['mysql_servers']['intranet']['db_pass'],
            self.settings['mysql_servers']['intranet']['db']
        )

    def isilon(self):
        """Connect to Isilon API."""
        from bitsapiclient.services.isilon import Isilon
        return Isilon(
            username=self.settings['isilon']['username'],
            password=self.settings['isilon']['password'],
            clusters=self.settings['isilon']['clusters'],
            verbose=self.verbose,
        )

    def jira_cloud(self):
        """Connect to JIRA cloud instance."""
        from bitsapiclient.services.jira import Jira
        return Jira(
            self.settings['jira']['cloud']['username'],
            self.settings['jira']['cloud']['password'],
            self.settings['jira']['cloud']['server'],
            verbose=self.verbose,
        )

    def jira_onprem(self):
        """Connect to JIRA onprem instance."""
        from bitsapiclient.services.jira import Jira
        return Jira(
            self.settings['jira']['onprem']['username'],
            self.settings['jira']['onprem']['password'],
            self.settings['jira']['onprem']['server'],
            verbose=self.verbose,
        )

    def jiradb(self):
        """Connect to JIRA cloud instance."""
        from bitsapiclient.services.jira import JiraDb
        return JiraDb(
            host=self.settings['postgres_servers']['jira']['db_host'],
            port=self.settings['postgres_servers']['jira']['db_port'],
            user=self.settings['postgres_servers']['jira']['db_user'],
            password=self.settings['postgres_servers']['jira']['db_pass'],
            db=self.settings['postgres_servers']['jira']['db'],
            verbose=self.verbose,
        )

    def keyserver(self):
        """Connect to Keyserver instance."""
        from bitsapiclient.services.keyserver import Keyserver
        return Keyserver(
            self.settings['keyserver']['url'],
            self.settings['keyserver']['username'],
            self.settings['keyserver']['password'],
            verbose=self.verbose,
        )

    def labinspection(self):
        """Connect to Lab Inspection DB."""
        from bitsapiclient.services.labinspection import LabInspection
        return LabInspection(
            self.settings['mysql_servers']['labinspection']['db_host'],
            self.settings['mysql_servers']['labinspection']['db_port'],
            self.settings['mysql_servers']['labinspection']['db_user'],
            self.settings['mysql_servers']['labinspection']['db_pass'],
            self.settings['mysql_servers']['labinspection']['db']
        )

    def ldap(self):
        """Connect to the LDAP class."""
        from bitsapiclient.services.ldapold import LDAP
        return LDAP(
            auth=self,
            servers=self.settings['ldap_servers'],
            verbose=self.verbose,
        )

    def ldapupdate(self):
        """Connect to the LDAPUpdate class."""
        from bits.ldap.update import LDAPUpdate
        return LDAPUpdate(
            auth=self,
            # servers=self.settings['ldap_servers'],
            settings=self.settings,
            # verbose=self.verbose,
        )

    def localmail(self):
        """Connect to the localmail LDAP class."""
        from bitsapiclient.services.localmail import Localmail
        return Localmail(
            self.settings['ldap_servers']['localmail']['uri'],
            self.settings['ldap_servers']['localmail']['bind_dn'],
            self.settings['ldap_servers']['localmail']['bind_pw'],
            self.settings['ldap_servers']['localmail']['base_dn'],
            verbose=self.verbose,
        )

    def mhl(self, people=None):
        """Connect to MHL file."""
        from bitsapiclient.services.mhl import MHL
        return MHL(
            path=self.settings['mhl']['hosts_file'],
            lockfile=self.settings['mhl']['lock_file'],
            people=people,
            verbose=self.verbose,
        )

    def mongo(self):
        """Connect to BITSdb Mongo DB."""
        from bitsapiclient.services.mongo import Mongo
        return Mongo(
            mongo_uri=self.settings['mongo']['bitsdb']['uri'],
            mongo_db=self.settings['mongo']['bitsdb']['db'],
            auth=self,
            verbose=self.verbose,
        )

    def mongo_dev(self):
        """Connect to BITSdb dev Mongo DB."""
        from bitsapiclient.services.mongo import Mongo
        return Mongo(
            self.settings['mongo']['bitsdb_dev']['uri'],
            self.settings['mongo']['bitsdb_dev']['db'],
            auth=self,
            verbose=self.verbose
        )

    def mongo_prod(self):
        """Connect to BITSdb prod Mongo DB."""
        from bitsapiclient.services.mongo import Mongo
        return Mongo(
            self.settings['mongo']['bitsdb_prod']['uri'],
            self.settings['mongo']['bitsdb_prod']['db'],
            auth=self,
            verbose=self.verbose,
        )

    def mx(self):
        """Return an MX instance."""
        from bits.mx import MX
        return MX(
            aliases_puppetdir=self.settings['mx']['aliases_puppetdir'],
            transports_puppetdir=self.settings['mx']['transports_puppetdir'],
            extension=self.settings['mx']['extension'],
            auth=self,
        )

    def netbox(self):
        """Connect to Netbox."""
        from bits.netbox import Netbox
        return Netbox(
            token=self.settings['netbox']['token'],
            url=self.settings['netbox']['url'],
            verbose=self.verbose,
        )

    def nis(self):
        """Connect to NIS."""
        from bitsapiclient.services.nis import NIS
        return NIS(
            verbose=self.verbose,
        )

    def orbitera(self):
        """Connect to Orbitera."""
        from bitsapiclient.services.orbitera import Orbitera
        return Orbitera(
            # api v1
            url=self.settings['orbitera']['url'],
            api_key=self.settings['orbitera']['api_key'],
            api_secret=self.settings['orbitera']['api_secret'],
            # api v2
            account=self.settings['orbitera']['account'],
            credentials_file=self.settings['orbitera']['credentials_file'],
            host=self.settings['orbitera']['host'],
            # verbose
            verbose=self.verbose,
        )

    def people(self):
        """Connect to People DB."""
        from bitsapiclient.services.people import PeopleDB
        return PeopleDB(
            server=self.settings['mysql_servers']['people']['db_host'],
            port=self.settings['mysql_servers']['people']['db_port'],
            user=self.settings['mysql_servers']['people']['db_user'],
            password=self.settings['mysql_servers']['people']['db_pass'],
            db=self.settings['mysql_servers']['people']['db'],
            csvs=self.settings['people']['csvs'],
            verbose=self.verbose,
        )

    def people_dev(self):
        """Connect to People dev DB."""
        from bitsapiclient.services.people import PeopleDB
        return PeopleDB(
            server=self.settings['mysql_servers']['people_dev']['db_host'],
            port=self.settings['mysql_servers']['people_dev']['db_port'],
            user=self.settings['mysql_servers']['people_dev']['db_user'],
            password=self.settings['mysql_servers']['people_dev']['db_pass'],
            db=self.settings['mysql_servers']['people_dev']['db'],
            csvs=self.settings['people']['csvs'],
            verbose=self.verbose,
        )

    def people_prod(self):
        """Connect to People prod DB."""
        from bitsapiclient.services.people import PeopleDB
        return PeopleDB(
            server=self.settings['mysql_servers']['people_prod']['db_host'],
            port=self.settings['mysql_servers']['people_prod']['db_port'],
            user=self.settings['mysql_servers']['people_prod']['db_user'],
            password=self.settings['mysql_servers']['people_prod']['db_pass'],
            db=self.settings['mysql_servers']['people_prod']['db'],
            csvs=self.settings['people']['csvs'],
            verbose=self.verbose,
        )

    def pivotaltracker(self):
        """Connect to Pivotal Tracker API."""
        from bitsapiclient.services.pivotaltracker import PivotalTracker
        return PivotalTracker(
            token=self.settings['pivotaltracker']['token'],
            verbose=self.verbose
        )

    def quay(self):
        """Connect to Quay API."""
        from bits.quay import Quay
        return Quay(
            token=self.settings['quay']['token'],
            orgname=self.settings['quay']['orgname'],
            clientid=self.settings['quay']['clientid'],
            secret=self.settings['quay']['secret'],
            role_team=self.settings['quay']['role_team'],
            verbose=self.verbose,
        )

    def redlock(self):
        """Connect to RedLock API."""
        from bitsapiclient.services.redlock import RedLock
        return RedLock(
            username=self.settings['redlock']['username'],
            password=self.settings['redlock']['password'],
            customerName=self.settings['redlock']['customerName'],
        )

    def rt(self):
        """Connect to RequestTracker DB."""
        from bitsapiclient.services.rt import RequestTracker
        return RequestTracker(
            server=self.settings['mysql_servers']['rt']['db_host'],
            port=self.settings['mysql_servers']['rt']['db_port'],
            user=self.settings['mysql_servers']['rt']['db_user'],
            password=self.settings['mysql_servers']['rt']['db_pass'],
            db=self.settings['mysql_servers']['rt']['db'],
            charset='latin1',
            verbose=self.verbose,
        )

    def sap(self):
        """Connect to SAP DB."""
        from bitsapiclient.services.sap import SAP
        server = '%s:%s' % (
            self.settings['mssql_servers']['sap']['db_host'],
            self.settings['mssql_servers']['sap']['db_port'],
        )
        return SAP(
            server=server,
            user=self.settings['mssql_servers']['sap']['db_user'],
            password=self.settings['mssql_servers']['sap']['db_pass'],
            db=self.settings['mssql_servers']['sap']['db'],
            verbose=self.verbose,
        )

    def servicenow(self):
        """Connect to ServiceNow."""
        from bitsapiclient.services.servicenow import ServiceNow
        return ServiceNow(
            base_url=self.settings['servicenow']['base_url'],
            params=self.settings['servicenow']['params'],
            user=self.settings['servicenow']['username'],
            passwd=self.settings['servicenow']['password'],
            buildings=self.settings['servicenow']['buildings'],
            verbose=self.verbose,
        )

    def shoretel(self):
        """Connect to ShoreTel DB."""
        from bitsapiclient.services.shoretel import Shoretel
        return Shoretel(
            server=self.settings['mysql_servers']['shoretel']['db_host'],
            port=self.settings['mysql_servers']['shoretel']['db_port'],
            user=self.settings['mysql_servers']['shoretel']['db_user'],
            password=self.settings['mysql_servers']['shoretel']['db_pass'],
            db=self.settings['mysql_servers']['shoretel']['db'],
            email_sender=self.settings['mysql_servers']['shoretel']['email_sender'],
            email_subject=self.settings['mysql_servers']['shoretel']['email_subject'],
            email_to=self.settings['mysql_servers']['shoretel']['email_to'],
            smtpserver=self.settings['mysql_servers']['shoretel']['smtpserver'],
            verbose=self.verbose,
        )

    def slack(self):
        """Connect to Slack API."""
        from bitsapiclient.services.slack import Slack
        return Slack(
            token=self.settings['slack']['token'],
            env=self.settings['configuration']['environment'],
            notifications=self.settings['slack']['notifications'],
        )

    def space(self):
        """Connect to Space DB."""
        from bitsapiclient.services.space import SpaceDB
        return SpaceDB(
            self.settings['mysql_servers']['space']['db_host'],
            self.settings['mysql_servers']['space']['db_port'],
            self.settings['mysql_servers']['space']['db_user'],
            self.settings['mysql_servers']['space']['db_pass'],
            self.settings['mysql_servers']['space']['db']
        )

    def space_dev(self):
        """Connect to Space dev DB."""
        from bitsapiclient.services.space import SpaceDB
        return SpaceDB(
            self.settings['mysql_servers']['space_dev']['db_host'],
            self.settings['mysql_servers']['space_dev']['db_port'],
            self.settings['mysql_servers']['space_dev']['db_user'],
            self.settings['mysql_servers']['space_dev']['db_pass'],
            self.settings['mysql_servers']['space_dev']['db']
        )

    def space_prod(self):
        """Connect to Space prod DB."""
        from bitsapiclient.services.space import SpaceDB
        return SpaceDB(
            self.settings['mysql_servers']['space_prod']['db_host'],
            self.settings['mysql_servers']['space_prod']['db_port'],
            self.settings['mysql_servers']['space_prod']['db_user'],
            self.settings['mysql_servers']['space_prod']['db_pass'],
            self.settings['mysql_servers']['space_prod']['db']
        )

    def stash(self):
        """Connect to Stash API."""
        from bitsapiclient.services.stash import Stash
        return Stash(
            self.settings['stash']['host'],
            self.settings['stash']['username'],
            self.settings['stash']['password']
        )

    def swoogo(self):
        """Connect to Swoogo API."""
        from bitsapiclient.services.swoogo import Swoogo
        return Swoogo(
            api_key=self.settings['swoogo']['api_key'],
            api_secret=self.settings['swoogo']['api_secret'],
            verbose=self.verbose,
        )

    def tableau(self):
        """Return an authenticated Tableau object."""
        from bitsapiclient.services.tableau import Tableau
        dn = self.settings['ldap_servers']['ad_ldap']['bind_dn']
        username = dn.split(',')[0].split('=')[1]
        return Tableau(
            username=r'CHARLES\%s' % (username),
            password=self.settings['ldap_servers']['ad_ldap']['bind_pw'],
            verbose=self.verbose,
        )

    def travis(self):
        """Return an authenticated Travis object."""
        from bitsapiclient.services.travis import Travis
        return Travis(
            token=self.settings['github']['token'],
            verbose=self.verbose,
        )

    def vmware(self):
        """Connect to VMWare API."""
        from bitsapiclient.services.vmware import VMWare
        return VMWare(
            username=self.settings['vmware']['username'],
            password=self.settings['vmware']['password'],
            url=self.settings['vmware']['url'],
            port=self.settings['vmware']['port'],
            verbose=self.verbose,
        )

    def welcome(self):
        """Connect to the Welcome app."""
        from bitsapiclient.services.welcome import Welcome
        return Welcome()

    def workday(self):
        """Connect to Workday API."""
        from bitsapiclient.services.workday import Workday
        return Workday(
            base_url=self.settings['workday']['base_url'],
            tenant=self.settings['workday']['tenant'],
            username=self.settings['workday']['username'],
            password=self.settings['workday']['password'],
            feed_username=self.settings['workday']['feed_username'],
            feed_password=self.settings['workday']['feed_password'],
            provisioning_username=self.settings['workday']['provisioning_username'],
            provisioning_password=self.settings['workday']['provisioning_password'],
            provisioning_url=self.settings['workday']['provisioning_url'],
            verbose=self.verbose,
        )
