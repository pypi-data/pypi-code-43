# Copyright (c) 2010, 2013, 2015
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from sqlalchemy.orm import sessionmaker

# Import SQL-Alchemy Classes (Database Model)
from coils.foundation.alchemy import ACL, \
    AuditEntry, \
    ObjectLink, \
    ObjectInfo, \
    Team, \
    Task, \
    OGO_TASK_ACTION_ACCEPT, \
    OGO_TASK_ACTION_CREATE, \
    OGO_TASK_ACTION_REACTIVATE, \
    OGO_TASK_ACTION_ARCHIVE, \
    OGO_TASK_ACTION_REJECT, \
    OGO_TASK_ACTION_COMPLETE, \
    OGO_TASK_ACTION_COMMENT, \
    Address, \
    Telephone, \
    CompanyValue, \
    Contact, \
    Enterprise, \
    Appointment, \
    Resource, \
    Note, \
    Document, \
    Folder, \
    Project, \
    ProjectAssignment, \
    Participant, \
    CompanyAssignment, \
    ObjectProperty, \
    Route, \
    Collection, \
    CollectionAssignment, \
    Process, \
    Message, \
    CompanyInfo, \
    KVC, \
    DateInfo, \
    TaskAction, \
    CTag, \
    DocumentVersion, \
    AuthenticationToken, \
    ProcessLogEntry, \
    Lock, \
    Attachment, \
    UniversalTimeZone, \
    UTCDateTime, \
    ORMEntity, \
    ProjectInfo, \
    RouteGroup, \
    DocumentEditing

# Import core components
from log import *
from blobmanager import BLOBManager

from defaultsmanager import \
    UserDefaultsManager, \
    ServerDefaultsManager

from plist import PListParser, \
    PListWriter

from picklejar import PickleParser, \
    PickleWriter

from backend import Backend, Session
from coils.foundation.blobmanager import blob_manager_for_ds
from coils.foundation.dbfs1 import DBFS1Manager
from coils.foundation.skyfs import SkyFSManager
from coils.foundation.imap import IMAPManager

from smtp import SMTP

from tzdata import COILS_TIMEZONES

from factories import \
    LDAPConnectionFactory, \
    SQLConnectionFactory

from utility import diff_id_lists, \
    change_to_backend_usergroup, \
    fix_microsoft_text, ldap_paged_search, \
    apply_orm_hints_to_query, \
    qsearch_from_xml

from standard_xml import StandardXML

from constants import \
    OGO_ROLE_SYSTEM_ADMIN, \
    OGO_ROLE_HELPDESK, \
    OGO_ROLE_WORKFLOW_ADMIN, \
    OGO_ROLE_WORKFLOW_DEVELOPERS, \
    OGO_ROLE_DATA_MANAGER, \
    OGO_ROLE_ACCOUNT_MANAGER

from date_and_time import Parse_Value_To_UTCDateTime, Delocalize_DateTime

from exceptions import \
    InvalidCodePathException, \
    DateTimeFormatException, \
    UnknownProjectStorageMechanism

from xmlrpc import XMLRPC_callresponse, XMLRPC_faultresponse

from xmlrpc import XMLRPC_callresponse, XMLRPC_faultresponse

from messages import COILS_ERRMSG_SMTP_GAIERR2

from encoders import \
    coils_json_encode, \
    coils_yaml_encode, \
    coils_yaml_encode_to_string, \
    coils_yaml_decode
