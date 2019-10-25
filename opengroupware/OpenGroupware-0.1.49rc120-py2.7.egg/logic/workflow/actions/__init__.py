#
# Copyright (c) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018
#               2019
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
# THE SOFTWARE
#

from xml import OIEXSLTExtensionPoints  # not an action

from sql import \
    SelectAction, \
    ExecuteAction, \
    InsertAction, \
    UpdateAction, \
    UpsertAction
from ldap import \
    DSML1Writer, \
    SearchAction, \
    UpdateUsersFromLDAP, \
    UpdateTeamsFromPOSIXGroups, \
    FillLDAPMailRoutingAction, \
    UpdateTeamsFromRFCGroups, \
    LDAPAddAction
from flow import \
    StartAction, \
    WaitAction, \
    DelayAction, \
    CountAction, \
    QueueProcessAction, \
    NoActionAction, \
    GrantAction, \
    SetProcessPropertyAction, \
    GetProcessLogAction, \
    AbendAction, \
    ExceptionAction, \
    TransactionLoggerAction, \
    InjectMessageAction, \
    GetSequenceValue, \
    SysLogMessageAction, \
    DeleteMessageAction, \
    ChownAction, \
    SendMessageAction, \
    DeduplicateSXMLAction
from format import \
    ReadAction, \
    WriteAction, \
    TranslateAction, \
    AddColumnAction, \
    RowTemplateAction, \
    PrefixColumnAction, \
    MapAction, \
    FixMicrosoftTextAction, \
    SimpleFilter, \
    WhitespaceChunkAction, \
    IConvAction, \
    RunMapAction, \
    Base64EncodeAction, \
    SplitFilterAction, \
    GroupByAction
from xml import \
    TransformAction, \
    XPathAction, \
    AssignAction, \
    ReadJSONAction, \
    XPathMerge, \
    SetValueAction, \
    XPathTestAction, \
    WriteJSONAction, \
    StandardXMLCombine
from mail import \
    SendMailAction, \
    MailBlastAction, \
    UnsubscribeAction, \
    GetIMAPQuotaAction, \
    IMAPFetchMailAction, \
    SendMailMessagesAction, \
    StreamsFromMessagesAction
from gw import \
    GetEntityAction, \
    CreateTaskAction, \
    AcceptTaskAction, \
    TaskCommentAction, \
    CompleteTaskAction, \
    RejectTaskAction, \
    ArchiveTaskAction, \
    ContactList, \
    EnterpriseList, \
    RemoveAccountStatusAction, \
    ArchiveAccountTasksAction, \
    GetUserAccountAction, \
    RemoveAccountMembershipAction, \
    GetEntityLogAction, \
    CreateCollection, \
    ArchiveOldTasksAction, \
    RevertArchivedLoginValues, \
    CompanyListAction, \
    GetObjectPropertyAction, \
    SetObjectPropertyAction, \
    UserTaskReport, \
    ReapCollectionsAction, \
    FixTaskLastModified, \
    SetProcessTaskAction, \
    SearchEntityAction
from re import \
    FindAction, \
    TrimAction, \
    LowerCaseAction, \
    UpperCaseAction, \
    StripAction, \
    ChompTextAction
from json import CountJSONPathAction, PluckValueFromJSONAction
from doc import \
    TextToPDFAction, \
    WatermarkPDFAction, \
    PrintToLPRAction, \
    FTPPutFileAction, \
    RMLToPDFAction, \
    AppendToZIPFileAction, \
    MessageToDocumentAction, \
    XLSToXMLAction, \
    XMLToXLSAction, \
    PrintToIPPAction, \
    FolderToZIPFileAction, \
    FTPGetFileAction, \
    ExtractFileFromZIPArchive, \
    DocumentToMessageAction, \
    AttachmentToMessageAction, \
    FTPGetFilesAction, \
    FTPDeleteFileAction, \
    MessageToAttachmentAction, \
    CutPagesFromPDFAction, \
    RotatePDFPagesAction, \
    SearchDocumentsToZIPFileAction, \
    SearchDocumentsToCollectionAction, \
    CollectionToZIPFileAction, \
    SearchDocumentsForUncollectionAction, \
    MessageToZIPFileAction, \
    MessageToINBOXAction, \
    ZIPToFolderAction
from ssh import \
    SSHExecAction, \
    SSHGetFileAction, \
    SSHPutFileAction, \
    SSHGetFilesIntoZipFileAction, \
    SSHDeleteFilesAction, \
    SSHGetFolderIntoZipFileAction, \
    SSHCreateFolderAction
from misc import \
    DixieLandTrainStatusAction
from image import \
    AutoCropImageAction, \
    BackgroundImageAction, \
    ConvertImageAction
from gpg import \
    GPGEncryptAction, \
    GPGSignAction
from http import \
    HttpPutAction
from smb import \
    SMBPutFileAction, \
    SMBGetFileAction, \
    SMBPutFilesAction, \
    SMBGetFilesAction
