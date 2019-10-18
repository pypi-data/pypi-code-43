#!/usr/bin/python3
#
#
# Copyright 2016 Kirk A Jackson DBA bristoSOFT all rights reserved.  All methods,
# techniques, algorithms are confidential trade secrets under Ohio and U.S.
# Federal law owned by bristoSOFT.
#
# Kirk A Jackson dba bristoSOFT
# 4100 Executive Park Drive
# Suite 11
# Cincinnati, OH  45241
# Phone (513) 401-9114
# email jacksonkirka@bristosoft.com
#
# The trade name bristoSOFT is a registered trade name with the State of Ohio
# document No. 201607803210.
#
# Note: Testing can be done using perhaps unittest and other test that do not
# require database connection.

'''
This controller module is the main controller for bristoSOFT Contacts v. 0.1.
It is part of the model view controller software architecture and controls the
communication between the view (primarily QDialogs) and the model (primarily a
PostgreSQL 9.4+ database).
'''

# Imports
import sip  # Needed for conversion to Python types
sip.setapi('QString', 2)
import datetime
import ntpath
# import ast
import json
import os
from .secure import Security
from .bristoprint import PrintServices
import webbrowser
import requests
from requests import get # Error on ordered_dict changed in compat.py
import platform

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebKit import *
# from PyQt4.uic import *
import psycopg2
import psycopg2.pool # import pooling extension

from .bristo_exceptions import *
from .view import *
from interface import contactsmain
# import threading
# import time

__version__ = '0.1' # Version assignment

# contactsdialog = loadUiType('contacts_combo.ui')[0]
#bristocontacts = loadUiType('contacts_main.ui')[0]

# class Controller(QMainWindow,  bristocontacts):


class Controller(QMainWindow, contactsmain.Ui_bristosoftContacts):
    '''

    Controller is the Main Application window with
    all the menus, toolbars, statusbar and more. It is
    the controller in the model, view, controller software
    architecture.

    '''

    def __init__(self, parent=None):
        '''

        This initialization class method initializes
        QMainWindow and the bristocontacts.

        '''
        super(Controller, self).__init__(parent)
        self.setupUi(self)

        # Connection
        self._conn_main = None
        self._conn_main_key = 192938293829395
        self._disconnected = True
        self._connected = False
        self._conn_main_timer = 300000
        self._idle = QTimer()
        self._chgpwd = False
        self._cursor = None
        self._firstlogin = True
        self.conn_msg = None

        # Connection Pooling
        self._pool = False
        self._min_con = 2
        self._max_con = 10

        # Update
        self._db_update = False

        # Multi-Query
        self._query = 0
        self.fetch_results = []
        self.fetch_notes = []
        self.fetch_files = []
        self.fetch_calls = []
        self.fetch_appts = []
        self.fetch_groups = []
        self._MYCONTACTS = 0
        self._LASTGROUP = 0
        self._groups_dict = {}

        # Reports
        self._grprpt = None

        # Security
        self._secure = Security()


        # Users
        self._user = None
        self._passwd = None
        self._user_email = None
        self._user_webmail = None
        self._USERNM = 1
        self._USEREMAIL = 2
        self._account_expired = False
        self._xmsg = "Expired. Call 513-401-9114 or jacksonkirka@bristosoft.com."

        # SQL class globals
        self._limit = 250

        # Contacts Database constants cursor list return
        self._ITEM = 0
        self._FIRSTITEM = 0
        self._ID = 0
        self._COMPANY = 1
        self._MRMRS = 2
        self._FNAME = 3
        self._MIDDLE = 4
        self._LNAME = 5
        self._CRED = 6
        self._ADDR = 7
        self._SUITE = 8
        self._CITY = 9
        self._ST = 10
        self._POSTAL = 11
        self._OPHONE = 12
        self._CELL = 13
        self._HPHONE = 14
        self._OEMAIL = 15
        self._PEMAIL = 16
        self._OWEB = 17
        self._PWEB = 18
        self._PIC = 19
        self._FAX = 20
        self._OWNER = 21
        self._AVAIL = 22
        self._GROUP = 23

        # Groups
        self._GROUPID = 0
        self._GRPSTAMP = 1
        self._GRPNAME = 2
        self._GRPOWNER = 3
        self._GRPPWD = 4
        self._GRPDESC = 5
        self._GRPPIC = 6
        self._GRPADDR1 = 7
        self._GRPADDR2 = 8
        self._GRPCITY = 9
        self._GRPSTATE = 10
        self._GRPPOSTAL = 11
        self._GRPWEB1 = 12
        self._GRPWEB2 = 13
        self._GRPPHONE = 14
        self._GRPFAX = 15
        self._groups = False
        self._search_groups_dlg = False
        self._groupqry = False
        self._groupnm = None
        self._update_groups = False
        self._grpnm_addr = None
        self.fetch_groups_owned = None

        # Table Rows
        self._table_rows_count = 2000

        # Notes
        self._stamp = 1
        self._note = 3
        self._notes_ct = 2
        self._note_column = 1

        # Image
        self._image = QPixmap()
        self._image_bin = None
        self._image_bytea = None
        self._image_buffer = None

        # File
        self._file_bin = None
        self._file_id = 0
        self._file_stamp = 1
        self._file_ct = 2
        self._file_name = 3
        self._file_file = 4

        #Calls
        self._calls_id = 0
        self._calls_ct_id = 1
        self._calls_stamp = 2
        self._calls_phone = 3
        self._calls_in = 4
        self._calls_results = 5
        self._live_set = False

        # Search
        self._clear = False

        # Appointment
        self._appt_id = 0
        self._appt_ct_id = 1
        self._appt_stamp = 2
        self._appt_time = 3
        self._appt_complete = 4
        self._appt_purpose = 5
        self._display_appts_set = False
        self._displayed_apptsbydate = False

        # Calendar
        self._calendar_activated = False
        self._qcal_date = None

        # Messages
        self._msg_id = 0
        self._msg_uuid = 1
        self._msg_stamp = 2
        self._msg_sender = 3
        self._msg_receiver = 4
        self._msg_text = 5
        self._poll_msg_display_time = 60000
        self._poll_msg_time = 300000
        self._poll_msg_qtimer = QTimer()
        self.fetch_msg = None
        self._msg_read_uuid = None
        self._conn_mesg_key = 192938293829335

        # Stack and Dialogs
        self.bristo_stack = QStackedWidget()
        self.bristo_stack.hide()
        self.search_groups = bristoSearchGroupDlg()
        self.bristo_search = bristoContactsSearchDialog()
        self._ITEM_CONTACTS_CACHED = 0
        self._ITEM_GROUPS_CACHED = 0

        # Hide columns on calls, appointments and messages
        self.bristo_search.fileTableWidget.setColumnHidden(self._file_id,True)
        self.bristo_search.callsTableWidget.setColumnHidden(self._calls_id,  True)
        self.bristo_search.callsTableWidget.setColumnHidden(self._calls_ct_id,
            True)
        self.bristo_search.apptTableWidget.setColumnHidden(self._appt_id,  True)
        self.bristo_search.apptTableWidget.setColumnHidden(self._appt_ct_id,  True)
        self.bristo_search.apptTableWidget.setColumnHidden(self._appt_stamp,  True)
        self.bristo_search.msgTableWidget.setColumnHidden(self._msg_id,  True)
        self.bristo_search.msgTableWidget.setColumnHidden(self._msg_receiver, True)
        self.bristo_search.msgTableWidget.setColumnHidden(self._msg_uuid, True)
        self._live_set = False # Prevents Duplicate Live Widgets
        self._calendar_activated = False # User double clicked date on calendar
        self._displayed_apptsbydate = False # Appointments by date display once

        # set bristoMapper class
        self.google_com = bristoMapper()
        layout = QHBoxLayout()
        layout.addWidget(self.google_com)
        self.bristo_search.mapTabFrame.setLayout(layout)

        # set bristoMailFrame
        self.google_mail_com = bristoMailView()
        mail_layout = QHBoxLayout()
        mail_layout.addWidget(self.google_mail_com)
        self.bristo_search.emailFrame.setLayout(mail_layout)

        # Notes
        self.bristo_search.notesTableWidget.setHorizontalHeaderLabels(
            ['Time Stamp', 'Notes'])

        # Documents
        self.bristo_search.fileTableWidget.setHorizontalHeaderLabels(
            ['Id','Time Stamp', 'File Name'])

        self.active_dlg = 'search'

        # Phone Calls
        self.bristo_search.callsTableWidget.setHorizontalHeaderLabels(
            ['ID', 'CTID', 'Time Stamp', 'Phone/CID', 'IO', 'Results'])

        self.bristo_search.callsTableWidget.horizontalHeader().resizeSection(
            self._calls_stamp, 140)
        self.bristo_search.callsTableWidget.horizontalHeader().resizeSection(
            self._calls_phone, 140)
        self.bristo_search.callsTableWidget.horizontalHeader().resizeSection(
            self._calls_in, 22)

        # Appointments
        self.bristo_search.apptTableWidget.setHorizontalHeaderLabels(
            ['ID', 'CTID', 'Time Stamp', 'Date/Time', 'CO', 'Purpose'])
        self.bristo_search.apptTableWidget.horizontalHeader().resizeSection(
            self._appt_time, 150)
        self.bristo_search.apptTableWidget.horizontalHeader().resizeSection(
            self._appt_complete, 28)

        # Messages
        self.bristo_search.msgTableWidget.setHorizontalHeaderLabels(
            ['ID','UUID','Stamp','Sender','Receiver','Contact Messages'])
        self.bristo_search.msgTableWidget.horizontalHeader().resizeSection(
            self._msg_stamp, 70)
        self.bristo_search.msgTableWidget.horizontalHeader().resizeSection(
            self._msg_sender, 75)

        # Search and update Signals
        self.bristo_search.picPushButton.clicked.connect(self.update_pic)
        self.bristo_search.availabilityPushButton.clicked.connect(
            self.update_usercontact_availablity)
        self.bristo_search.notesTableWidget.cellChanged.connect(
            self.db_insert_contact_note)
        self.bristo_search.callsTableWidget.cellChanged.connect(
            self.db_insert_contact_call)
        self.bristo_search.apptTableWidget.cellChanged.connect(
            self.db_insert_update_appt)
        self.bristo_search.msgTableWidget.cellChanged.connect(
            self.db_insert_contact_msg)
        self.bristo_search.notesDetailPushButton.clicked.connect(
            self.resize_notes)
        self.bristo_search.callsDetailPushButton.clicked.connect(
            self.resize_calls)
        self.bristo_search.apptDetailPushButton.clicked.connect(
            self.resize_appts)
        self.bristo_search.msgDetailPushButton.clicked.connect(
            self.resize_msg)
        self.bristo_search.chkmsgPushButton.clicked.connect(
            self.check_messages)
        self.bristo_search.filePushButton.clicked.connect(
            self.db_insert_contact_file)
        self.bristo_search.fileTableWidget.doubleClicked.connect(
            self.get_contact_file)
        self.bristo_search.refreshMapPushButton.clicked.connect(self.refresh_map)
        self.bristo_search.browserMapPushButton.clicked.connect(self.open_url_map)
        self.bristo_search.directionsPushButton.clicked.connect(
            self.open_url_directions)
        self.bristo_search.accessGroupPushButton.clicked.connect(
            self.display_group_contacts)
        self.bristo_search.emailRefreshPushButton.clicked.connect(
            self.refresh_email)
        self.bristo_search.callsTableWidget.clicked.connect(
            self.live_call_widgets)
        self.bristo_search.apptTableWidget.clicked.connect(self.live_appt_widgets)
        self.bristo_search.calendarWidget.activated.connect(
            self.display_appts_bydate)

        # Add dialogues to the stack and stack to central widget
        self.bristo_stack.addWidget(self.bristo_search)
        self.bristo_stack.addWidget(self.search_groups)
        self.setCentralWidget(self.bristo_stack)

        # Query Progress Bar
        self._query_progressbar = QProgressBar()
        self._query_progressbar.setGeometry(30, 40, 200, 25)
        # self.contactsStatusBar.addPermanentWidget(self._query_progressbar)

        #Date and Time
        self._DATE = datetime.datetime.now()
        self._TODAY = self._DATE.strftime("%m/%d/%y %I:%M%p")

        # Next/Prev
        self._NEXT = 0
        self._PREV = 0
        self._LASTITEM = 0

        # Printing
        self._prt = PrintServices()

        # Main Signals
        self.actionAbout_Qt.triggered.connect(self.aboutqt)
        self.actionAbout_bristoSOFT_Contacts.triggered.connect(
            self.aboutbristocontacts)
        self.actionConnect.triggered.connect(self.db_connect)
        self.actionNew.triggered.connect(self.db_contact_new)
        self.actionVacuum.triggered.connect(self.db_full_vacuum)
        self.actionReIndex.triggered.connect(self.db_reindex)
        self.actionChangePassword.triggered.connect(self.chgpwddlg)
        self.action_Add_Group.triggered.connect(self.db_new_group_dlg)
        self.actionSearchGroupsDialog.triggered.connect(self.search_groups_dlg)
        self.actionDisconnect.triggered.connect(self.db_close)
        self.actionQuery.triggered.connect(self.db_contacts_fetch_flag)
        self.action_Print.triggered.connect(self.printuserscontacts)
        self.actionQuit.triggered.connect(self.close_contacts)
        self.actionFirst_Item.triggered.connect(self.db_item_fetch_first)
        self.actionPrevious_Item.triggered.connect(self.db_item_prev)
        self.actionNext_Item.triggered.connect(self.db_item_next)
        self.actionLast_Item.triggered.connect(self.db_item_fetch_last)
        self.actionSearch.triggered.connect(self.db_fetch_contact)
        self.actionUpdate.triggered.connect(self.db_update_contact)

        # Next and Previous Group
        self.menuGroups.addSeparator()
        self.menuGroups.addAction('My Contacts', self.db_my_contacts,
            QKeySequence('Home'))
        self.menuGroups.addSeparator()
        self.menuGroups.addAction('Next Group', self.db_group_next,
            QKeySequence('Ctrl+Shift+Down'))
        self.menuGroups.addAction('Prev Group', self.db_group_prev,
            QKeySequence('Ctrl+Shift+Up'))
        self.menuGroups.addSeparator()

        # Note this whole section was commented out and the main
        # screen came up for the first time.

        # Settings
        settings = QSettings()
        size = settings.value("MainWindow/Size",
                              QVariant(QSize(630, 735)))
        self.resize(size)
        position = settings.value("MainWindow/Position",
                                  QVariant(QPoint(320, 140)))
        self.move(position)
       # self.restoreState(settings.value("MainWindow/State").toByteArray())

        # Set Main Window Icon
        self.setWindowIcon(QIcon(":/icons/icons/family.ico"))

        # Set contactsStatusBar to red
        self.conn_msg = 'Welcome to bristoSOFT Contacts v. 0.1'
        self.contactsStatusBar.showMessage(self.conn_msg, 5000)
        self.contactsStatusBar.setStyleSheet("background-color: \
        rgb(230, 128, 128);")

    # About class methods
    def aboutqt(self):
        '''

        aboutqt is the standard About Qt dialog built in to QT.

        '''
        mesg = QMessageBox()
        mesg.aboutQt(self,  'About Qt')

    def aboutbristocontacts(self):
        '''

        aboutbristocontacts QMessageBox displays information about
        bristoSOFT Contacts v. 0.1.

        '''
        QMessageBox.about(self, "About bristoSOFT Contacts v. 0.1",
        """ <b>About bristoSOFT Contacts</b> v %s
        <p>Copyright &copy; 2016 bristoSOFT
        All rights reserved.
        <p>This is a PostgreSQL database contacts management system.  It is
        based on the PyQt frontend GUI.
            <p>Python %s - Qt %s - PyQt %s on %s""" % (
        __version__, platform.python_version(),
        QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def reset_timer(self):
        '''
        reset_timer resets QTimer singleShot for self._conn_main_timer amount of time.
        It stops existing timer and starts a new one.  When the time has elapsed
        it calls self.db_idle and informs the user.  Note: we must use the Qt timers
        instead of the native threading timers in python for compatibility.  This
        means greater dependency on Qt resources.
        '''

        # threading.Timer(self._conn_main_timer,  self.db_idle).start()

        # idle
        self._idle.stop()
        self._idle = QTimer() # do we need this -- Already defined
        self._idle.singleShot(self._conn_main_timer,  self.db_idle)
        self._idle.start() # start idle timer



    # class Database Methods
    def db_connect(self):
        '''

        db_connect displays the login dialog and catches the signal accept()
        from the OK button then calls self.db_login.

        '''
        self.login = bristoContactsLogin()
        self.login.show()
        self.login.accepted.connect(self.db_login_get_cred)

    def db_login_get_cred(self):

        '''
        db_login_get_cred gets credentials from login dialog then
        calls db_login.
        '''
        self._user = self.login.userNameLineEdit.text()
        self._passwd = self.login.passwordLineEdit.text()
        self.db_login()


    def db_login(self):
        '''

        db_login establishes a connection to a PostgreSQL database
        with the standard connection string.

        '''
        # Authentication
        try:
            _loc_json = get('https://ipapi.co/json')
            self._usr_loc = json.loads(_loc_json._content)
        except requests.exceptions.ConnectionError:
            self.contactsStatusBar.showMessage(
            "Connection Error! Connect to internet. Try again.", 20000)
            return
        self._usr_city = self._usr_loc['city']
        self._usr_ip = self._usr_loc['ip']
        self._usr_region = self._usr_loc['region']
        self._usr_lon = self._usr_loc['longitude']
        self._usr_ctry = self._usr_loc['country']
        self._usr_lat = self._usr_loc['latitude']
        self._usr_tz = self._usr_loc['timezone']
        self._usr_zip = self._usr_loc['postal']

        self._host = 'bristosoftcontacts'
        self._db = 'bristocontacts'

        if self._user and self._passwd:

            # Step 1 Setup connection pool
            # Note: by using the ThreadedConnectionPool class instead of
            # the PersistentConnectionPool class it is possible to have
            # more than one db connection per thread.
            
            #build connection string
            _server = " ".join(
            ["host='bristocontacts.cmuctcwvgjxh.us-east-2.rds.amazonaws.com'", 
                "dbname='bristocontacts'","sslmode='require'","port='5432'" ])
            _usr = "".join(["user=", "'", self._user, "'"])
            _pswd = "".join(['password=', "'", self._passwd, "'" ])
            con = " ".join([_server, _usr, _pswd])
            
            # Setup a threaded connection pool
            try:
                self._pool = psycopg2.pool.ThreadedConnectionPool(
                self._min_con,  self._max_con,  con)
            except psycopg2.OperationalError:
                self.incorrectcredentials()
                return

            # Step 2 Get a connection from the pool and setup main conn
            if self._pool:
                self._conn_main = self._pool.getconn(key=self._conn_main_key)
                self._connected = True # Set connection to True


            # Step 3 User database authentication
            _usr_nm_match = False
            _usr_pwd_match = False

            # Step 5 login credentials
            _usr_nm = self._user # Set Text for User Name
            _usr_pwd = self._passwd # Set Text for password

            # Step 6 Verify user name
            # If user enters incorrect user name this is not yet resolved.
            self._cursor = self._conn_main.cursor()
            self._cursor.execute("SELECT * FROM bristo_contacts_users WHERE \
            bristo_contacts_users_name = %s LIMIT %s", (
                self._user, self._limit))
            if not self._cursor.rowcount:
                self.incorrectlogin()
            else:
                _temp = self._cursor.fetchone()
                _db_usrnm = _temp[self._USERNM]


                # Need user email for availability
                self._user_email = _temp[self._USEREMAIL]


                self._cursor.close()
                if _usr_nm == _db_usrnm:
                    _usr_nm_match = True
                else:
                    _usr_nm_match = False

                # Verify user password
                self._cursor = self._conn_main.cursor()
                self._cursor.execute("SELECT bristo_contacts_users_pwd FROM \
                bristo_contacts_users WHERE bristo_contacts_users_name = %s \
                    LIMIT %s", (
                    self._user, self._limit))
                _db_usrpwdhash = self._cursor.fetchone()[0]
                _usr_pwd_match = self._secure.authenticatepwd(
                    _db_usrpwdhash,  _usr_pwd)

                if _usr_nm_match and _usr_pwd_match:

                    # Verify user account is not expired
                    self._cursor.close()
                    self._cursor = self._conn_main.cursor()
                    self._cursor.execute(
                    "SELECT bristo_contacts_users_expires FROM \
                    bristo_contacts_users WHERE bristo_contacts_users_name = %s \
                    LIMIT %s", (
                    self._user, self._limit))
                    _db_expire_date = self._cursor.fetchone()[0]
                    if _db_expire_date:
                        if self._DATE.date() > _db_expire_date:
                            self.contactsStatusBar.showMessage(
                            self._xmsg,
                            20000)
                            self._account_expired = True

                    # get user webmail link for contact filter
                    self._cursor.close()
                    self._cursor = self._conn_main.cursor()
                    self._cursor.execute("SELECT bristo_contacts_users_webmail FROM \
                    bristo_contacts_users WHERE bristo_contacts_users_name = %s \
                     LIMIT %s", (
                                         self._user, self._limit))
                    self._user_webmail_tuple = self._cursor.fetchone()
                    self._user_webmail = self._user_webmail_tuple[0]


                    if self._disconnected:
                        pass
                        #self.contactsStatusBar.removeWidget(self.conn_msg)
                    #self.conn_msg = QLabel("ssl:"+self._user + "@"+
                                            #self._host+
                                          #'/'+ self._db +'.')
                    # self.conn_msg = QLabel("")
                    if not self._account_expired:
                        self.contactsStatusBar.setStyleSheet("background-color: \
                                                         rgb(179, 255, 188);")
                    else:
                        self.contactsStatusBar.setStyleSheet("background-color: \
                                              rgb(255, 165, );")
                    if not self._chgpwd:
                        pass
                        # self.contactsStatusBar.addWidget(self.conn_msg
                    
                    # Log authentication
                    _usr_ip = self._usr_ip
                    _usr_city = self._usr_city
                    _usr_reg = self._usr_region
                    _usr_ctry = self._usr_ctry
                    _usr_zip = self._usr_zip
                    _suc = True
                    _in = True
                    _grplogin = False
                    self._cursor.execute("""INSERT INTO bristo_contacts_authlog
                            (bristo_contacts_authlog_uname,
                            bristo_contacts_authlog_in,
                            bristo_contacts_authlog_group,
                            bristo_contacts_authlog_inet,
                            bristo_contacts_authlog_city,
                            bristo_contacts_authlog_region,
                            bristo_contacts_authlog_ctry,
                            bristo_contacts_authlog_postal,
                            bristo_contacts_authlog_success)
                                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                            (_usr_nm, _in, _grplogin, _usr_ip, _usr_city,
                            _usr_reg, _usr_ctry, _usr_zip, _suc ))
                    self._conn_main.commit()
                    _tz = self._usr_tz
                    self._cursor.execute("""SET TIME ZONE %s;""", (_tz, ))
                    self.reset_timer()
                    # Initial set after user login
                    self._cursor.close()
                    self._pool.putconn(self._conn_main, key=self._conn_main_key)
                    if self._firstlogin:
                        self._firstlogin = False
                        self.msg_poll_timer()
                    self._connected = False
                    self.contactsStatusBar.showMessage(
                        self._user+'@'+self._host+'/'+ self._db+' logged in.',
                            5000)
                    self.contactsStatusBar.setStyleSheet("background-color: \
                                                          rgb(152,251,152);")
                    #self.contactsStatusBar.removeWidget(self.conn_msg)
                    #self.conn_msg = QLabel(self._user+'@'+self._host+
                                              #'/'+ self._db+'logged in.')
                    #self.contactsStatusBar.addWidget(self.conn_msg)
                    self._disconnected = True

                else:
                    self.incorrectlogin()

    def poll_messages(self):
        '''
        poll_messages checks recent messages for the current user every
        300000 milliseconds or 5 minutes.  It first queries all user
        messages and sorts them by stamp date in descending order.  Then
        it pops the top message off the stack.  This user and message
        is displayed in the status bar.
        '''
        if self._pool:
            self._conn_mesg = self._pool.getconn(key=self._conn_mesg_key)
            self._cursor_msg = self._conn_mesg.cursor()
            # query needs to be updated to select only messages insert
            # in the last 20 minutes or so.
            self._cursor_msg.execute("""SELECT * FROM (SELECT * FROM
                bristo_contacts_messages WHERE bristo_contacts_messages_receiver
                = %s ORDER BY bristo_contacts_messages_stamp DESC) AS
                recent LIMIT 1""",
                    (self._user, ))
            self.fetch_msg = self._cursor_msg.fetchone() # Get message
            if not self._cursor_msg.rowcount:
                return
            else:
                _msg_uuid = 1 # static
                _sender = 3 # static
                _msg = 5 # static
                if not self._msg_read_uuid == self.fetch_msg[_msg_uuid]:
                    self._cursor_msg.close()
                    self._pool.putconn(self._conn_mesg, key=self._conn_mesg_key)
                    self._connected = False
                    # self.contactsStatusBar.removeWidget(self.conn_msg)
                    self.contactsStatusBar.setStyleSheet("background-color: \
                                                  rgb(244, 160, 66);")
                    self.contactsStatusBar.showMessage(
                        self.fetch_msg[_sender]+': '+self.fetch_msg[_msg],
                               self._poll_msg_display_time)
                    self._msg_read_uuid = self.fetch_msg[_msg_uuid]
                    restore_status_bar = QTimer()
                    restore_status_bar.singleShot(self._poll_msg_display_time,
                                self.restore_status_bar)
                    restore_status_bar.start()

    def msg_poll_timer(self):
        '''
        msg_poll_timer starts the polling messages in messages table.
        It stops the existing timer and starts a new one.  Every time
        the time elapses it calls self.poll_messages and informs the user of
        any messages through the status bar.  Note: must use Qt timers
        for compatibility issues with other Qt modules.
        '''

        self._poll_msg_qtimer.setSingleShot(False)
        self._poll_msg_qtimer.timeout.connect(self.poll_messages)
        self._poll_msg_qtimer.start(self._poll_msg_time)
        # threading.Timer(self._poll_msg_time, self.msg_poll_timer).start()
        # self.poll_messages()


    def chgpwddlg(self):
        '''
        chngpwddlg displays the change password dialog and accepts user input
        based on accepted signal.
        '''
        if self._connected:
            self.contactsStatusBar.showMessage(
            "Please log out then change password.", 10000)
        if not self._connected and not self._user == 'guest':
            self.chgpwd = bristoContactsChgPwdDlg()
            self.chgpwd.show()
            self.chgpwd.accepted.connect(self.changepasswd)

    def changepasswd(self):
        '''
        changepwd establishes a connection to a PostgreSQL database on port
        5423 with the standard connection string then changes the password.
        '''
        _usrnm = self.chgpwd.userNameLineEdit.text()
        _oldpwd = self.chgpwd.oldPasswordLineEdit.text()
        _newpwd = self.chgpwd.newPasswordLineEdit.text()
        _reenter = self.chgpwd.reenterPasswordLineEdit.text()
        _complex = self._secure.mincomplex(_newpwd)
        self._user = _usrnm
        self._passwd = _oldpwd
        self._chgpwd = True
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
        if self._connected and _newpwd == _reenter and _complex:
            _newpwdhash = self._secure.hashpwd(_newpwd) # Hash new password
            self._cursor = self._conn_main.cursor()
            _username = self._user
            self._cursor.execute("""UPDATE bristo_contacts_users SET
            bristo_contacts_users_pwd = %s WHERE
            bristo_contacts_users_name = %s;""", (_newpwdhash, _username))
            self._conn_main.commit()
            _usrquery = " ".join(['ALTER','USER', _username,'WITH','ENCRYPTED', 
                'PASSWORD ',])
            _pwdquery = "".join(['\'', _newpwd, '\'', ';']) 
            _query = "".join([_usrquery, _pwdquery])
            self._cursor.execute(_query)
            self._conn_main.commit()
            self.contactsStatusBar.showMessage(
            "Successful.  Log out and log back in with new password.", 10000)
            self._chgpwd = False
            self._cursor.close()
            self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
        else:
            self.contactsStatusBar.setStyleSheet("background-color: \
                                              rgb(230, 128, 128);")
            self.contactsStatusBar.showMessage(
            "Disconnected, New Password didn't match or password uncomplex.", 10000)
    
    def incorrectlogin(self):

        '''
        incorrectlogin displays a message in the status bar to the user informing
        them they have not successfully logged on.  This method remains here due
        to future potential usage and is redundant with incorrectcredentials.
        '''
        # Note with new direct db login for users no connection pool is
        # availble so the attempted login cannot be logged in authlog.
        
        # Log incorrect authentication
        _usr_nm = self._user
        _usr_ip = self._usr_ip
        _usr_city = self._usr_city
        _usr_reg = self._usr_region
        _usr_ctry = self._usr_ctry
        _usr_zip = self._usr_zip
        _in = True
        _grplogin = False
        self._cursor.execute("""INSERT INTO bristo_contacts_authlog
                (bristo_contacts_authlog_uname,
                bristo_contacts_authlog_in,
                bristo_contacts_authlog_group,
                bristo_contacts_authlog_inet,
                bristo_contacts_authlog_city,
                bristo_contacts_authlog_region,
                bristo_contacts_authlog_ctry,
                bristo_contacts_authlog_postal)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s);""",
                (_usr_nm,_in, _grplogin, _usr_ip, _usr_city,
                _usr_reg, _usr_ctry, _usr_zip))
        self._conn_main.commit()
        self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
        self._connected = False
        self._disconnected = True
        #self.contactsStatusBar.setStyleSheet("background-color: \
                                              #rgb(230, 128, 128);")
        #if self._disconnected:
            #self.contactsStatusBar.removeWidget(self.conn_msg)
        _msg = 'Login incorrect, please try again.'
        self.contactsStatusBar.showMessage(_msg,  3000)



    def incorrectcredentials(self):

        '''
        incorrectcredentials displays a message in the status bar to the user informing
        them they have not successfully logged on.
        '''
        # Note with new direct db login for users no connection pool is
        # availble so the attempted login cannot be logged in authlog.
        
        _msg = 'Login credentials incorrect, please try again.'
        self.contactsStatusBar.showMessage(_msg,  3000)

    def incorrectgrouplogin(self):

        '''
        incorrectgrouplogin displays a message in the status bar to the user
        informing them they have not successfully logged into the group.
        '''
        # Log incorrect group authentication
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True # Set connection to True
            _usr_nm = self._user
            _usr_ip = self._usr_ip
            _usr_city = self._usr_city
            _usr_reg = self._usr_region
            _usr_ctry = self._usr_ctry
            _usr_zip = self._usr_zip
            _in = True
            _grplogin = True
            _grp_nm = self._groupnm
            if self._cursor.close:
                self._cursor = self._conn_main.cursor()
            self._cursor.execute("""INSERT INTO bristo_contacts_authlog
                    (bristo_contacts_authlog_uname,
                    bristo_contacts_authlog_in,
                    bristo_contacts_authlog_group,
                    bristo_contacts_authlog_grpname,
                    bristo_contacts_authlog_inet,
                    bristo_contacts_authlog_city,
                    bristo_contacts_authlog_region,
                    bristo_contacts_authlog_ctry,
                    bristo_contacts_authlog_postal)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                    (_usr_nm,_in, _grplogin, _grp_nm, _usr_ip, _usr_city,
                    _usr_reg, _usr_ctry, _usr_zip))
            self._conn_main.commit()
            self._cursor.close()
            self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
            self._connected = False
            self._disconnected = True
            #self.contactsStatusBar.setStyleSheet("background-color: \
                                                  #rgb(230, 128, 128);")
            # if self._disconnected:
                #self.contactsStatusBar.removeWidget(self.conn_msg)
            _msg = 'Group login incorrect, please try again.'
            self.contactsStatusBar.showMessage(_msg,  3000)

    def db_contact_new(self):

        '''

        db_record_new displays the new contact dialog and catches the signal accept()
        from the OK button then runs self.db_insert.

        '''
        self.reset_timer()
        self.bristo = bristoContactsDialog()
        # set contactsDialog in cetralWidget
        self.bristo_stack.addWidget(self.bristo)
        self.bristo_stack.setCurrentWidget(self.bristo)
        self.bristo_stack.show()
        self.bristo.accepted.connect(self.db_insert)


    def db_insert(self):
        '''

        db_insert inserts one new contact into the PostgreSQL database table.

        '''

        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True # Set connection
            self._cursor = self._conn_main.cursor()
            if self._connected:
                self.reset_timer()
                _company = self.bristo.companyLineEdit.text()
                _mrmrs = self.bristo.mrmrsLineEdit.text()
                _fname = self.bristo.firstNameLineEdit.text()
                _middle = self.bristo.middleNameLineEdit.text()
                _lname = self.bristo.lastNameLineEdit.text()
                _cred = self.bristo.credLineEdit.text()
                _addr = self.bristo.addressLineEdit.text()
                _suite = self.bristo.suiteLineEdit.text()
                _city = self.bristo.cityLineEdit.text()
                _st = self.bristo.stateLineEdit.text()
                _postal = self.bristo.postalLineEdit.text()
                _grp = self.bristo.copyGroupAddressLineEdit.text()
                _oph = self.bristo.officePhoneLineEdit.text()
                _cell = self.bristo.cellPhoneLineEdit.text()
                _fax = self.bristo.officeFaxLineEdit.text()
                _hph = self.bristo.homePhoneLineEdit.text()
                _oemail = self.bristo.officeEmailLineEdit.text()
                _pemail = self.bristo.personalEmailLineEdit.text()
                _oweb = self.bristo.officeWebLineEdit.text()
                _pweb = self.bristo.personalWebLineEdit.text()
                _owner = self._user
                if _grp and not _addr:
                    _grpinfo = self.db_copy_group_address(_grp)
                    _addr = _grpinfo[self._GRPADDR1]
                    _suite = _grpinfo[self._GRPADDR2]
                    _city = _grpinfo[self._GRPCITY]
                    _st = _grpinfo[self._GRPSTATE]
                    _postal = _grpinfo[self._GRPPOSTAL]

                # Check for duplicate phone numbers or emails

                self._cursor.execute("""SELECT bristo_contacts_ct_ph_office,
                        bristo_contacts_ct_email1 FROM bristo_contacts_ct WHERE
                        bristo_contacts_ct_ph_office = %s OR
                        bristo_contacts_ct_email1 = %s;""", (_oph, _oemail))
                if not self._cursor.rowcount:
                    self._cursor.execute("""INSERT INTO bristo_contacts_ct
                        (bristo_contacts_ct_co, bristo_contacts_ct_title,
                        bristo_contacts_ct_fname, bristo_contacts_ct_middle,
                        bristo_contacts_ct_lname, bristo_contacts_ct_cred,
                        bristo_contacts_ct_addr1, bristo_contacts_ct_addr2,
                        bristo_contacts_ct_city, bristo_contacts_ct_state,
                        bristo_contacts_ct_postal, bristo_contacts_ct_group,
                        bristo_contacts_ct_ph_office,bristo_contacts_ct_ph_cell,
                        bristo_contacts_ct_fax,bristo_contacts_ct_home,
                        bristo_contacts_ct_email1,bristo_contacts_ct_email2,
                        bristo_contacts_ct_web,bristo_contacts_ct_web2,
                        bristo_contacts_ct_owner)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s, %s,%s);""",
                        (_company,_mrmrs,_fname,_middle,_lname,
                        _cred, _addr, _suite,_city,_st, _postal,_grp,
                        _oph,_cell, _fax,_hph,_oemail,_pemail,_oweb,_pweb,_owner))
                    self._conn_main.commit()
                    self.contactsStatusBar.showMessage('New Contact Inserted.', 3000)
                    self._cursor.close()
                    self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                    self._connected = False
                else:
                    self.contactsStatusBar.showMessage(
                    'Duplicate email or office phone. Please Retry.', 5000)
                    self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                    self._connected = False
                    self._db_update = True
        else:
            self.connection_closed_msg()

    def db_copy_group_address(self, _group):
        '''
        db_copy_group_address accepts group name and returns the group address of
        a group into memory for access by any other caller.
        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True # Set connection
            if self._connected:
                _user = self._user
                if self._cursor.close:
                    self._cursor = self._conn_main.cursor()
                self._cursor.execute("""SELECT * FROM bristo_contacts_groups
                            WHERE bristo_contacts_groups_owner = %s AND
                            bristo_contacts_groups_group = %s;""",
                        (_user, _group))
                if not self._cursor.rowcount:
                    self.contactsStatusBar.showMessage(
                    'Group not found or user not authorized.', 5000)
                else:
                    _grpinfo = self._cursor.fetchone()
                    return _grpinfo
            self._cursor.close()
            self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
            self._connected = False

    def db_user_owns_group(self, _group):
        '''
        db_copy_group_address accepts group name and returns the group address of
        a group into memory for access by any other caller.
        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True # Set connection
        if self._connected:
            _user = self._user
            if self._cursor.close:
                self._cursor = self._conn_main.cursor()
            self._cursor.execute("""SELECT * FROM bristo_contacts_groups
                        WHERE bristo_contacts_groups_owner = %s AND
                        bristo_contacts_groups_group = %s;""",
                    (_user, _group))
            if not self._cursor.rowcount:
                return False
            else:
                return True
        self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
        self._connected = False



    def db_new_group_dlg(self):
        '''
        db_new_group_dlg opens the new group dialog box to accept information to
        create a new contacts group and then upon accept signal then calls
        db_insert_group.  Groups can be companies, departments,
        churches, non-profits, professional bodys, social groups, schools,
        restaurants, factories, distribution centers and much more.
        '''
        self.nwgrp = bristoNewGroupDlg()
        self.bristo_stack.addWidget(self.nwgrp)
        self.bristo_stack.setCurrentWidget(self.nwgrp)
        self.bristo_stack.show()
        self.nwgrp.accepted.connect(self.db_insert_group)

    def db_insert_group(self):
        '''
        db_insert_group inserts a new group entered by the user with authentication
        credentials.
        '''

        _usr = self._user
        _group = self.nwgrp.newGroupLineEdit.text()
        _pwd = self.nwgrp.passwordLineEdit.text()
        _confirm = self.nwgrp.confirmPasswordLineEdit.text()
        _desc = self.nwgrp.descTextEdit.toPlainText()
        _address = self.nwgrp.groupAddressLineEdit.text()
        _suite = self.nwgrp.groupSuiteLineEdit.text()
        _city = self.nwgrp.groupCityLineEdit.text()
        _st = self.nwgrp.groupStateLineEdit.text()
        _zip = self.nwgrp.groupPostalLineEdit.text()
        _web1 = self.nwgrp.groupOfficeWebLineEdit.text()
        _web2 = self.nwgrp.groupOtherWebLineEdit.text()
        _oph = self.nwgrp.groupOfficePhoneLineEdit.text()
        _fax = self.nwgrp.groupOfficeFaxLineEdit.text()

        if self._user == 'guest' or not _pwd:
            _pwd = 'Guest$123'
            _confirm = 'Guest$123'
        if _group:
            # Verify group name is available
            if self._pool:
                self._conn_main = self._pool.getconn(key=self._conn_main_key)
                self._connected = True

            if self._connected:
                self._cursor = self._conn_main.cursor()
                self._cursor.execute("""SELECT bristo_contacts_groups_group
                FROM bristo_contacts_groups WHERE bristo_contacts_groups_group
                 = %s;""",(_group, ))
            if not self._cursor.rowcount:
                if _pwd == _confirm:
                    _pwd_match = True
                _complex = self._secure.mincomplex(_pwd)
                if self._connected and _pwd_match and _complex:
                    self.reset_timer()
                    _hashedpwd = self._secure.hashpwd(_pwd)
                    self._cursor.execute("""INSERT INTO bristo_contacts_groups
                            (bristo_contacts_groups_owner,
                            bristo_contacts_groups_group,
                            bristo_contacts_groups_pwd,
                            bristo_contacts_groups_desc,
                            bristo_contacts_groups_addr1,
                            bristo_contacts_groups_addr2,
                            bristo_contacts_groups_city,
                            bristo_contacts_groups_state,
                            bristo_contacts_groups_postal,
                            bristo_contacts_groups_web1,
                            bristo_contacts_groups_web2,
                            bristo_contacts_groups_phone,
                            bristo_contacts_groups_fax)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                            (_usr,_group,_hashedpwd,_desc,
                            _address,_suite,_city,_st,_zip,_web1,
                            _web2, _oph,_fax ))
                    self._conn_main.commit()
                    self._cursor.close()
                    self.contactsStatusBar.showMessage('New Group Inserted.', 3000)
                    self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                    self._connected = False
                    self._db_update = True
            else:
                self.contactsStatusBar.showMessage('Group name unavailable.', 5000)
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False

    def search_groups_dlg(self):
        '''
        search_groups_dlg opens the search groups dialog to get users
        groups to view and edit.
        '''
        self.bristo_stack.setCurrentWidget(self.search_groups)
        self.bristo_stack.show()
        self._search_groups_dlg = True
        self._groupqry = False
        self._update_groups = True
        self.get_groups_owned()

    def db_fetch_groups(self):
        '''
        db_fetch_groups fetches the groups owned by the the user or
        queried by via group name and password or where the user has
        appointment for a contact in a group.
        '''
        self.reset_timer()
        _user = self._user
        _grp = self._groupnm
        if self._connected:
            self._cursor = self._conn_main.cursor()
            if not self._groupqry:
                self._cursor.execute("""SELECT DISTINCT
                bristo_contacts_groups.bristo_contacts_groups_id,
                bristo_contacts_groups.bristo_contacts_groups_stamp,
                bristo_contacts_groups.bristo_contacts_groups_group,
                bristo_contacts_groups.bristo_contacts_groups_owner,
                bristo_contacts_groups.bristo_contacts_groups_pwd,
                bristo_contacts_groups.bristo_contacts_groups_desc,
                bristo_contacts_groups.bristo_contacts_groups_pic FROM
                bristo_contacts_groups, bristo_contacts_appt, bristo_contacts_ct,
                bristo_contacts_users
                WHERE
                bristo_contacts_groups.bristo_contacts_groups_owner = %s OR
                bristo_contacts_appt.bristo_contacts_appt_owner = %s AND
                bristo_contacts_appt.bristo_contacts_appt_ct_id =
                bristo_contacts_ct.bristo_contacts_ct_id AND
                bristo_contacts_ct.bristo_contacts_ct_group =
                bristo_contacts_groups.bristo_contacts_groups_group OR
                bristo_contacts_users.bristo_contacts_users_name = %s AND
                bristo_contacts_users.bristo_contacts_users_email =
                bristo_contacts_ct.bristo_contacts_ct_email1 AND
                bristo_contacts_ct.bristo_contacts_ct_group =
                bristo_contacts_groups.bristo_contacts_groups_group LIMIT %s;""",
                (_user, _user, _user, self._limit))
                if not self._cursor.rowcount:
                    return
                self.fetch_groups.append(self._cursor.fetchall())
            if self._groupqry:
                self._cursor.execute("""SELECT * FROM bristo_contacts_groups
                    WHERE bristo_contacts_groups_group = %s
                    ORDER by bristo_contacts_groups_group LIMIT %s;""",
                (_grp, self._limit))
                self.fetch_groups.append(self._cursor.fetchall())

    def get_groups_owned(self):
        '''
        get_groups_owned returns only the groups user created and currently
        owns.
        '''
        # --------------- Performance Tuning Enhancement --------------
        # Note: Tuple out of range with Performance turning test
        # at line 1727.  Need to fix.
        #
        if self.fetch_groups_owned and not self._db_update:
            self._LASTITEM = len(self.fetch_groups_owned) - 1
            self._groups = True
            self._ITEM_CONTACTS_CACHED = self._ITEM
            self._ITEM = self._ITEM_GROUPS_CACHED - 1
            self.bristo_stack.setCurrentWidget(self.search_groups)
            return
        # --------------------------------------------------------------
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            if self._connected:
                self.reset_timer()
                _user = self._user
                self._cursor = self._conn_main.cursor()
                self._cursor.execute("""SELECT * FROM bristo_contacts_groups
                            WHERE bristo_contacts_groups_owner = %s
                            ORDER by bristo_contacts_groups_group LIMIT %s;""",
                        (_user, self._limit ))
                self.fetch_groups_owned = self._cursor.fetchall() # Gets user owned groups
                self._LASTITEM = len(self.fetch_groups_owned) - 1
                self._groups = True
                self._ITEM = self._FIRSTITEM
                self.display_data()
                self.search_groups.picPushButton.clicked.connect(
                    self.update_group_pic)
                self._search_groups_dlg = False
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
                self._db_update = False

    def db_contacts_fetch_flag(self):
        '''
        db_contacts_fetch_flag sets self._groupqry to False when the query
        button on toolbar is clicked.  It is needed to distinguish between a
        click and a program method call namely display_goup_contacts.
        '''
        # self.search_groups = None
        self._groupqry = False
        self._grprpt = None
        self.db_contacts_fetch()

    def db_contacts_fetch(self):
        '''

        db_record_fetch fetches all contacts at one time.
        self.fetch_result[0][1] is First contact, company name
        self.fetch_result is a python list returned by psycopg2 driver
        The list is then traversed in memory on the list python object.

        '''
        # --------------- Performance Tuning Enhancement --------------
        if self.fetch_results and not self._groupqry and not self._db_update:
            self._groups = False
            self._ITEM_GROUPS_CACHED = self._ITEM
            self._ITEM = self._ITEM_CONTACTS_CACHED - 1
            self._LASTITEM = len(self.fetch_results[self._query]) - 1
            self.bristo_stack.setCurrentWidget(self.bristo_search)
            return
        # --------------------------------------------------------------
        if self._pool:
            _msg = 'Please wait.  Contacts you own are being fetched....'
            self.contactsStatusBar.showMessage(_msg, 7000)
            self.reset_timer()
            self._groups = False
            _user = self._user
            _email = self._user_email
           # Fetch Data from tables --> Python lists
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            if self._connected:
                self._cursor = self._conn_main.cursor()

                if self._groupqry:
                    _group = self._groupnm
                    self._cursor.execute("""SELECT * FROM bristo_contacts_ct WHERE
                    bristo_contacts_ct_group = %s ORDER by bristo_contacts_ct_co,
                    bristo_contacts_ct_lname LIMIT %s;""",
                    (_group, self._limit ))
                if not self._groupqry:
                    self._cursor.execute("""SELECT DISTINCT
                    bristo_contacts_ct.bristo_contacts_ct_id,
                    bristo_contacts_ct.bristo_contacts_ct_co,
                    bristo_contacts_ct.bristo_contacts_ct_title,
                    bristo_contacts_ct.bristo_contacts_ct_fname,
                    bristo_contacts_ct.bristo_contacts_ct_middle,
                    bristo_contacts_ct.bristo_contacts_ct_lname,
                    bristo_contacts_ct.bristo_contacts_ct_cred,
                    bristo_contacts_ct.bristo_contacts_ct_addr1,
                    bristo_contacts_ct.bristo_contacts_ct_addr2,
                    bristo_contacts_ct.bristo_contacts_ct_city,
                    bristo_contacts_ct.bristo_contacts_ct_state,
                    bristo_contacts_ct.bristo_contacts_ct_postal,
                    bristo_contacts_ct.bristo_contacts_ct_ph_office,
                    bristo_contacts_ct.bristo_contacts_ct_ph_cell,
                    bristo_contacts_ct.bristo_contacts_ct_home,
                    bristo_contacts_ct.bristo_contacts_ct_email1,
                    bristo_contacts_ct.bristo_contacts_ct_email2,
                    bristo_contacts_ct.bristo_contacts_ct_web,
                    bristo_contacts_ct.bristo_contacts_ct_web2,
                    bristo_contacts_ct.bristo_contacts_ct_picture,
                    bristo_contacts_ct.bristo_contacts_ct_fax,
                    bristo_contacts_ct.bristo_contacts_ct_owner,
                    bristo_contacts_ct.bristo_contacts_ct_available,
                    bristo_contacts_ct.bristo_contacts_ct_group FROM
                    bristo_contacts_ct, bristo_contacts_appt WHERE
                    bristo_contacts_ct.bristo_contacts_ct_owner = %s
                    OR bristo_contacts_ct.bristo_contacts_ct_email1 = %s OR
                    bristo_contacts_appt.bristo_contacts_appt_ct_id =
                    bristo_contacts_ct.bristo_contacts_ct_id
                    AND bristo_contacts_appt.bristo_contacts_appt_owner = %s
                        ORDER by bristo_contacts_ct.bristo_contacts_ct_co,
                        bristo_contacts_ct.bristo_contacts_ct_lname LIMIT %s;""",
                        (_user, _email, _user, self._limit ))
                    if not self._cursor.rowcount:
                        self.contactsStatusBar.showMessage(
                            'No Contacts found.  Cursor over New to add one.', 5000)
                        return
                self.fetch_results.append(self._cursor.fetchall())

                # Note: When requesting group contacts there s/b no notes,
                # files, calls or appointments.

                self._cursor.execute("""SELECT * FROM bristo_contacts_notes WHERE
                    bristo_contacts_notes_owner = %s  ORDER by
                    bristo_contacts_notes_ct,
                    bristo_contacts_notes_stamp LIMIT %s""", (_user, self._limit))
                self.fetch_notes.append(self._cursor.fetchall()) # Get all notes
                self._cursor.execute("""SELECT bristo_contacts_files_id,
                    bristo_contacts_files_stamp, bristo_contacts_files_ct,
                    bristo_contacts_files_name FROM
                    bristo_contacts_files WHERE bristo_contacts_files_owner = %s
                    ORDER by bristo_contacts_files_ct,
                    bristo_contacts_files_stamp LIMIT %s""", (_user, self._limit))
                self.fetch_files.append(self._cursor.fetchall()) # Get all files
                self._cursor.execute("""SELECT * FROM bristo_contacts_calls WHERE
                    bristo_contacts_calls_owner = %s ORDER by
                    bristo_contacts_calls_ct_id,
                    bristo_contacts_calls_stamp LIMIT %s""",  (_user, self._limit))
                self.fetch_calls.append(self._cursor.fetchall()) # Get all calls
                self._cursor.execute("""SELECT * FROM bristo_contacts_appt WHERE
                     bristo_contacts_appt_owner = %s ORDER by
                        bristo_contacts_appt_ct_id,
                        bristo_contacts_appt_stamp LIMIT %s """, (_user,self._limit ))
                self.fetch_appts.append(self._cursor.fetchall()) # Get all appointments
                self.update_fetch_results()
                _msg = 'All data fetched from database.'
                self.contactsStatusBar.showMessage(_msg, 7000)
                self._cursor.close()
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
                self._db_update = False
        else:
            self.connection_closed_msg()
        self.bristo_stack.setCurrentWidget(self.bristo_search)
        self.bristo_stack.show()



    def update_fetch_results(self):
        '''

        update_fetch_results reassigns the entire contact list during an
        update.

        '''

        self._LASTITEM = len(self.fetch_results[self._query]) - 1
        self.bristo_search_dlg = False
        self._update_groups = False
        self._ITEM = self._FIRSTITEM
        self.display_data()


    def db_item_fetch_first(self):
        '''

        db_item_fetch_first fetches the first item in the results set.

        '''
        if self.fetch_results or self.fetch_groups_owned:
            self._ITEM = self._FIRSTITEM
            self.display_data()

    def db_item_fetch_last(self):
        '''

        db_item_fetch_last fetches the last item in the result set.

        '''
        if self.fetch_results or self.fetch_groups_owned:
            self._ITEM = self._LASTITEM
            self.display_data()


    def db_item_prev(self):
        '''
        db_item_prev fetches the previous item before the current item based on
        index in the python list result set.
        '''
        if not self._ITEM <= self._FIRSTITEM \
            and (self.fetch_results
            or self.fetch_groups_owned):
            self._ITEM -= 1
            self.display_data()

    def db_item_next(self):
        '''
        db_item_next fetches the next item after the current item based on
        index in the python list results set.
        '''
        if not self._ITEM >= self._LASTITEM \
            and (self.fetch_results
            or self.fetch_groups_owned):
            self._ITEM += 1
            self.display_data()

    def db_my_contacts(self):
        '''
        db_my_contacts changes the value of self._query to zero for the
        users own contacts retrieved without a group query.
        '''
        if self.fetch_results:
            self._query = self._MYCONTACTS
            self._ITEM = self._FIRSTITEM
            self._LASTITEM = len(self.fetch_results[self._query]) - 1
            self.display_data()

    def db_group_next(self):
        '''
        db_group_next fetches the next group by incrementing self._query
        index to point to the next nested in the 3d list matrix.
        '''

        if not self._query >= self._LASTGROUP and self.fetch_results:
            self._ITEM = self._FIRSTITEM
            self._query += 1
            self._LASTITEM = len(self.fetch_results[self._query]) - 1
            self.display_data()

    def db_group_prev(self):
        '''
        db_group_next fetches the previous group by incrementing self._query
        index to point to the next nested in the 3d list matrix.
        '''
        if not self._query <= self._MYCONTACTS and self.fetch_results:
            self._ITEM = self._FIRSTITEM
            self._query -= 1
            self._LASTITEM = len(self.fetch_results[self._query]) - 1
            self.display_data()

    def db_group_select(self):
        '''
        db_group_select sets self_query to group selected on group menu then
        runs self.display_data(). Note: menu does not exist until after query
        so no test for self.fetch_results need.
        '''
        self._query = self._groups_dict[self.menuGroups.sender().text()]
        self._ITEM = self._FIRSTITEM
        self._LASTITEM = len(self.fetch_results[self._query]) - 1
        self.display_data()

    def db_fetch_contact(self):
        '''

        db_fetch_contact fetches the first occurence of the company name,
        first name, or last name entered in the relevant search field.
        The database is already sorted by Company and then by Last name
        of contact.

        '''
        if self._clear is False:
            self.clear_search_fields()
            self._clear = True
        elif self.bristo_stack.currentWidget() == self.bristo_search:
            _company_qry = self.bristo_search.companyLineEdit.text()
            _lname_qry = self.bristo_search.lastNameLineEdit.text()
            _fname_qry = self.bristo_search.firstNameLineEdit.text()

            if _company_qry:
                for _company_idx in range(len(self.fetch_results[self._query])):
                    _company = self.fetch_results[self._query][_company_idx][self._COMPANY]
                    if _company_qry in _company:
                        self._ITEM = _company_idx
                        self.display_data()
                        self._clear = False
                        return
                _msg = 'Pattern not found.'
                self.contactsStatusBar.showMessage(_msg, 3000)
                self._clear = False

            elif _lname_qry:

                for _company_idx in range(len(self.fetch_results[self._query])):
                    _lname = self.fetch_results[self._query][_company_idx][self._LNAME]
                    if _lname_qry in _lname:
                        self._ITEM = _company_idx
                        self.display_data()
                        self._clear = False
                        return
                _msg = 'Pattern not found.'
                self.contactsStatusBar.showMessage(_msg, 3000)
                self._clear = False

            elif _fname_qry:

                for _company_idx in range(len(self.fetch_results[self._query])):
                    _fname = self.fetch_results[self._query][_company_idx][self._FNAME]
                    if _fname_qry in _fname:
                        self._ITEM = _company_idx
                        self.display_data()
                        self._clear = False
                        return
                _msg = 'Pattern not found.'
                self.contactsStatusBar.showMessage(_msg, 3000)
                self._clear = False

        elif self.bristo_stack.currentWidget() == self.search_groups:
            _grp_qry = self.search_groups.searchGroupLineEdit.text()

            if _grp_qry:
                for _grp_idx in range(len(self.fetch_groups_owned)):
                    _grps = self.fetch_groups_owned[_grp_idx][self._GRPNAME]
                    if _grp_qry in _grps:
                        self._ITEM = _grp_idx
                        self.display_data()
                        self._clear = False
                        return

                _msg = 'Pattern not found.'
                self.contactsStatusBar.showMessage(_msg, 3000)
                self._clear = False


    def clear_search_fields(self):

        '''
        clear_search_fields clears the search fields in the search dialog.
        '''
        if self.bristo_search:
            self.bristo_search.companyLineEdit.clear()
            self.bristo_search.firstNameLineEdit.clear()
            self.bristo_search.lastNameLineEdit.clear()

        if self.search_groups:
            self.search_groups.searchGroupLineEdit.clear()


    def db_update_contact(self):
        '''

        db_update_contact updates the currently displayed contact in the
        the database.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            if self.bristo_stack.currentWidget() == self.search_groups:
                self.db_update_group()
                return
            if self._connected:
                if self._cursor.close:
                    self._cursor = self._conn_main.cursor()
                self.reset_timer()
                _usr = self._user
                _usr_email = self._user_email
                _current_id = str(self.fetch_results[self._query][self._ITEM][self._ID])
                _company = self.bristo_search.companyLineEdit.text()
                _mrmrs = self.bristo_search.mrmrsLineEdit.text()
                _fname = self.bristo_search.firstNameLineEdit.text()
                _middle = self.bristo_search.middleNameLineEdit.text()
                _lname = self.bristo_search.lastNameLineEdit.text()
                _cred = self.bristo_search.credLineEdit.text()
                _addr = self.bristo_search.addressLineEdit.text()
                _suite = self.bristo_search.suiteLineEdit.text()
                _city = self.bristo_search.cityLineEdit.text()
                _st = self.bristo_search.stateLineEdit.text()
                _postal = self.bristo_search.postalLineEdit.text()
                _oph = self.bristo_search.officePhoneLineEdit.text()
                _cell = self.bristo_search.cellPhoneLineEdit.text()
                _fax = self.bristo_search.officeFaxLineEdit.text()
                _hph = self.bristo_search.homePhoneLineEdit.text()
                _oemail = self.bristo_search.officeEmailLineEdit.text()
                _pemail = self.bristo_search.personalEmailLineEdit.text()
                _oweb = self.bristo_search.officeWebLineEdit.text()
                _pweb = self.bristo_search.personalWebLineEdit.text()
                _gname = self.bristo_search.groupNameLineEdit.text()

                # Check if group name enter and user authorized
                if _gname:
                    _owner = self.db_user_owns_group(_gname)
                    if _owner:
                        self._cursor.execute("""UPDATE bristo_contacts_ct SET
                            (bristo_contacts_ct_co, bristo_contacts_ct_title,
                            bristo_contacts_ct_fname, bristo_contacts_ct_middle,
                            bristo_contacts_ct_lname, bristo_contacts_ct_cred,
                            bristo_contacts_ct_addr1, bristo_contacts_ct_addr2,
                            bristo_contacts_ct_city, bristo_contacts_ct_state,
                            bristo_contacts_ct_postal, bristo_contacts_ct_ph_office,
                            bristo_contacts_ct_ph_cell, bristo_contacts_ct_fax,
                            bristo_contacts_ct_home, bristo_contacts_ct_email1,
                            bristo_contacts_ct_email2, bristo_contacts_ct_web,
                            bristo_contacts_ct_web2, bristo_contacts_ct_group)
                            = (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                            %s, %s,%s,%s) WHERE bristo_contacts_ct_id = %s AND
                            bristo_contacts_ct_owner = %s OR
                            bristo_contacts_ct_id = %s AND
                            bristo_contacts_ct_email1 = %s;""",
                            (_company,_mrmrs,_fname,_middle,_lname,_cred, _addr,
                            _suite,_city,_st,_postal,_oph,_cell,_fax, _hph,_oemail,
                            _pemail,_oweb,_pweb,_gname, _current_id, _usr,
                            _current_id, _usr_email))
                        self._conn_main.commit()
                        self.contactsStatusBar.showMessage('Contact Updated.', 3000)
                        self._pool.putconn(
                            conn=self._conn_main, key=self._conn_main_key)
                        self._connected = False
                        self._db_update = True
                    elif not _owner:
                        self.contactsStatusBar.showMessage(
                        'Group nonexistent or user unauthorized. Please Retry.', 5000)
                        self._pool.putconn(
                            conn=self._conn_main, key=self._conn_main_key)
                        self._connected = False
                else:
                    self._cursor.execute("""UPDATE bristo_contacts_ct SET
                        (bristo_contacts_ct_co, bristo_contacts_ct_title,
                        bristo_contacts_ct_fname, bristo_contacts_ct_middle,
                        bristo_contacts_ct_lname, bristo_contacts_ct_cred,
                        bristo_contacts_ct_addr1, bristo_contacts_ct_addr2,
                        bristo_contacts_ct_city, bristo_contacts_ct_state,
                        bristo_contacts_ct_postal, bristo_contacts_ct_ph_office,
                        bristo_contacts_ct_ph_cell, bristo_contacts_ct_fax,
                        bristo_contacts_ct_home, bristo_contacts_ct_email1,
                        bristo_contacts_ct_email2, bristo_contacts_ct_web,
                        bristo_contacts_ct_web2) = (%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s) WHERE
                        bristo_contacts_ct_id = %s AND
                        bristo_contacts_ct_owner = %s OR
                        bristo_contacts_ct_id = %s AND
                        bristo_contacts_ct_email1 = %s;""",
                        (_company,_mrmrs,_fname,_middle,_lname,_cred, _addr,
                        _suite,_city,_st,_postal,_oph,_cell,_fax, _hph,_oemail,
                        _pemail,_oweb,_pweb, _current_id,  _usr, _current_id,
                        _usr_email))

                    self._conn_main.commit()
                    self.contactsStatusBar.showMessage('Contact Updated.', 3000)
                    self._pool.putconn(
                        conn=self._conn_main, key=self._conn_main_key)
                    self._connected = False
                    self._db_update = True
        else:
            self.connection_closed_msg()


    def db_update_group(self):
        '''
        update_group updates group information including the password.
        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            _usr = self._user
            _group = self.search_groups.searchGroupLineEdit.text()
            _pwd = self.search_groups.passwordLineEdit.text()
            _confirm = self.search_groups.confirmPasswordLineEdit.text()
            _desc = self.search_groups.descTextEdit.toPlainText()
            _address = self.search_groups.groupAddressLineEdit.text()
            _suite = self.search_groups.groupSuiteLineEdit.text()
            _city = self.search_groups.groupCityLineEdit.text()
            _st = self.search_groups.groupStateLineEdit.text()
            _zip = self.search_groups.groupPostalLineEdit.text()
            _web1 = self.search_groups.groupOfficeWebLineEdit.text()
            _web2 = self.search_groups.groupOtherWebLineEdit.text()
            _oph = self.search_groups.groupOfficePhoneLineEdit.text()
            _fax = self.search_groups.groupOfficeFaxLineEdit.text()
            if _pwd and _confirm:
                _id = self.fetch_groups_owned[self._ITEM][self._GROUPID]
                if _pwd == _confirm:
                    _pwd_match = True
                _complex = self._secure.mincomplex(_pwd)
                if self._connected and _pwd_match and _complex:
                    self.reset_timer()
                    _hashedpwd = self._secure.hashpwd(_pwd)
                    if self._cursor.closed:
                        self._cursor = self._conn_main.cursor()
                    self._cursor.execute("""UPDATE bristo_contacts_groups SET
                            (bristo_contacts_groups_group,
                                bristo_contacts_groups_pwd,
                                bristo_contacts_groups_desc,
                                bristo_contacts_groups_addr1,
                                bristo_contacts_groups_addr2,
                                bristo_contacts_groups_city,
                                bristo_contacts_groups_state,
                                bristo_contacts_groups_postal,
                                bristo_contacts_groups_web1,
                                bristo_contacts_groups_web2,
                                bristo_contacts_groups_phone,
                                bristo_contacts_groups_fax) =
                            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) WHERE
                            bristo_contacts_groups_id = %s AND
                            bristo_contacts_groups_owner = %s;""",
                            (_group,_hashedpwd,_desc,_address,
                             _suite,_city,_st,_zip,_web1,
                                _web2,_oph,_fax,_id,_usr))
                    self._conn_main.commit()
                    self._cursor.close()
                    self.contactsStatusBar.showMessage('Group Updated.', 3000)
                    self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                    self._connected = False
                    self._db_update = True
            else:
                self.contactsStatusBar.showMessage('Please enter group password.',
                    3000)
        else:
            self.connection_closed_msg()

    def update_usercontact_availablity(self):
        '''
        udate_usercontact_availability updates the users contact
        availability status if user matches the current contact.
        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
        _current_id = str(self.fetch_results[self._query][self._ITEM][self._ID])
        if self._connected and self._user_email == \
        self.fetch_results[self._query][self._ITEM][self._OEMAIL]:
                _avail = self.bristo_search.availabilityPushButton.isFlat()
                self._cursor = self._conn_main.cursor()
                self._cursor.execute("UPDATE bristo_contacts_ct SET \
                    bristo_contacts_ct_available = %s WHERE \
                    bristo_contacts_ct_id = %s",  (_avail,  _current_id))
                self._conn_main.commit()
                self._cursor.close()
                self.contactsStatusBar.showMessage('User Contact Availability Updated.', 3000)
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
        else:
            self.contactsStatusBar.showMessage('User Email must match contact email.', 5000)
            self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
            self._connected = False

    def display_data(self):
        '''

        display_data simply displays a data based on the date
        index integer value in self_ITEM.

        '''
        if not self._account_expired:
            self.block_signals()
            if not self._groups:
                self.resize_mode_zero()
                self.db_fetch_groups()
                self.display_contact()
                self.display_notes()
                self.display_files()
                self.display_calls()
                self.display_appts()
                self.display_group_in_contact()
            if self._groups:
                self.display_group()
            self.display_msg()
            self.unblock_signals()

    def display_data_not_appts(self):

        '''
        display_data_not_appts displays all info on contact without updating the
        contact appointments.  This is needed to allow appointments selected by the
        calendar date to display a contact without overwriting the calendar list
        of appointments for that day.
        '''
        if not self._account_expired:
            self.resize_mode_zero()
            self.block_signals()
            self.display_contact()
            self.display_notes()
            self.display_files()
            self.display_calls()
            self.display_group_in_contact()
            self.display_msg()
            self.unblock_signals()


    def resize_mode_zero(self):
        '''
        resize_mode_zero sets the resize mode to zero for the Table Widgets to
        zero.  There after they may be reset by clicking the resize buttons.
        '''

        self.bristo_search.notesTableWidget.verticalHeader().setSectionResizeMode(0)
        self.bristo_search.callsTableWidget.verticalHeader().setSectionResizeMode(0)
        self.bristo_search.apptTableWidget.verticalHeader().setSectionResizeMode(0)
        self.bristo_search.msgTableWidget.verticalHeader().setSectionResizeMode(0)

    def block_signals(self):
        '''
        block_signals blocks all signals during the loading of data to widgets.
        This is needed to prevent cellChanged signals from being activated during
        programatic loading of data to the widgets.
        '''

        if not self._groups:
            self.bristo_search.notesTableWidget.blockSignals(True) # block during load
            self.bristo_search.callsTableWidget.blockSignals(True)
            self.bristo_search.apptTableWidget.blockSignals(True)
            self.bristo_search.msgTableWidget.blockSignals(True)
        if self._groups:
            self.search_groups.blockSignals(True)

    def display_contact(self):
        '''
        display_contact displays contact information to the contact and address tabs.
        '''

        self.bristo_search.companyLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._COMPANY])
        self.bristo_search.mrmrsLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._MRMRS])
        self.bristo_search.firstNameLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._FNAME])
        self.bristo_search.middleNameLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._MIDDLE])
        self.bristo_search.lastNameLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._LNAME])
        self.bristo_search.credLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._CRED])
        self.bristo_search.addressLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._ADDR])
        self.bristo_search.suiteLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._SUITE])
        self.bristo_search.cityLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._CITY])
        self.bristo_search.stateLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._ST])
        self.bristo_search.postalLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._POSTAL])
        self.bristo_search.officePhoneLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._OPHONE])
        self.bristo_search.cellPhoneLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._CELL])
        self.bristo_search.officeFaxLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._FAX])
        self.bristo_search.homePhoneLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._HPHONE])
        self.bristo_search.officeEmailLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._OEMAIL])
        self.bristo_search.personalEmailLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._PEMAIL])
        self.bristo_search.officeWebLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._OWEB])
        self.bristo_search.personalWebLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._PWEB])
        self._image_bytea = self.fetch_results[self._query][self._ITEM][self._PIC]
        self.display_pic(self.bristo_search.picLabel, self._image_bytea)
        if self.fetch_results[self._query][self._ITEM][self._AVAIL]:
            self.bristo_search.availabilityPushButton.setFlat(False)
            self.bristo_search.availabilityPushButton.setStyleSheet(
            "background-color: rgb(0, 255, 0)")
        else:
            self.bristo_search.availabilityPushButton.setFlat(True)
            self.bristo_search.availabilityPushButton.setStyleSheet(
            "border: solid; background-color: rgb(255, 0, 0)")

    def display_group(self):
        '''
        display_group displays group information.
        '''
        if self.fetch_groups_owned:
            self.search_groups.descTextEdit.clear()
            self.search_groups.searchGroupLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPNAME])
            self.search_groups.descTextEdit.insertPlainText(
                self.fetch_groups_owned[self._ITEM][self._GRPDESC])
            self.search_groups.groupAddressLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPADDR1])
            self.search_groups.groupSuiteLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPADDR2])
            self.search_groups.groupCityLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPCITY])
            self.search_groups.groupStateLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPSTATE])
            self.search_groups.groupPostalLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPPOSTAL])
            self.search_groups.groupOfficeWebLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPWEB1])
            self.search_groups.groupOtherWebLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPWEB2])
            self.search_groups.groupOfficePhoneLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPPHONE])
            self.search_groups.groupOfficeFaxLineEdit.setText(
                self.fetch_groups_owned[self._ITEM][self._GRPFAX])
            self._image_bytea = self.fetch_groups_owned[self._ITEM][self._GRPPIC]
            self.display_pic(self.search_groups.newGroupLabel, self._image_bytea)

    def display_group_contacts(self):
        '''
        display_group_contacts authenticates a group login and then returns
        all contacts within a group base on group name and password without
        spaces.
        '''
        _usr = self._user 
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
        else:
            self.connection_closed_msg()
            return
        # Authenticate group
        _grp_nm = self.bristo_search.groupNameLineEdit.text()
        _pwd = self.bristo_search.groupPwdLineEdit.text()
        self._grprpt = _grp_nm
        if _grp_nm and _pwd:
            self._cursor = self._conn_main.cursor()
            
            # Update bristo_contacts_session
            self._cursor.execute("""SELECT bristo_contacts_session_username
            FROM bristo_contacts_session WHERE 
            bristo_contacts_session_username = %s;""", (_usr, ))
            if not self._cursor.rowcount:
                self._cursor.execute("""INSERT INTO bristo_contacts_session
                (bristo_contacts_session_username,
                bristo_contacts_session_grpname,
                bristo_contacts_session_grppwd)
                VALUES (%s,%s,%s);""", (_usr, _grp_nm,_pwd))
            else:
                self._cursor.execute("""UPDATE bristo_contacts_session SET
                (bristo_contacts_session_grpname, bristo_contacts_session_grppwd)
                = (%s,%s) WHERE bristo_contacts_session_username = %s;""",
                (_grp_nm,_pwd, _usr))
            
            # Set matches to False
            _grp_nm_match = False
            _grp_pwd_match = False

            # Verify group name
            # If user enters incorrect group name this is not yet resolved.
            self._cursor.execute("SELECT * FROM bristo_contacts_groups WHERE \
            bristo_contacts_groups_group = %s LIMIT %s", (
                _grp_nm, self._limit))
            if not self._cursor.rowcount:
                 self.contactsStatusBar.showMessage('Group not found.', 3000)
                 return
            else:
                _temp = self._cursor.fetchone()
                _db_grpnm = _temp[self._GRPNAME]
                self._cursor.close()
                if _grp_nm == _db_grpnm:
                    _grp_nm_match = True
                    self._groupnm = _grp_nm
                else:
                    _grp_nm_match = False

            # Verify user password
            self._cursor = self._conn_main.cursor()
            self._cursor.execute("SELECT bristo_contacts_groups_pwd FROM \
            bristo_contacts_groups WHERE bristo_contacts_groups_group = %s", (
                _grp_nm, ))
            _db_grppwdhash = self._cursor.fetchone()[0]
            _grp_pwd_match = self._secure.authenticatepwd(_db_grppwdhash,  _pwd)

            if _grp_nm_match and _grp_pwd_match:

                if self._cursor.close:
                    self._cursor = self._conn_main.cursor()
                # Log authentication
                _usr_nm = self._user
                _usr_ip = self._usr_ip
                _usr_city = self._usr_city
                _usr_reg = self._usr_region
                _usr_ctry = self._usr_ctry
                _usr_zip = self._usr_zip
                _suc = True
                _in = True
                _grplogin = True
                self._cursor.execute("""INSERT INTO bristo_contacts_authlog
                        (bristo_contacts_authlog_uname,
                        bristo_contacts_authlog_in,
                        bristo_contacts_authlog_group,
                        bristo_contacts_authlog_inet,
                        bristo_contacts_authlog_city,
                        bristo_contacts_authlog_grpname,
                        bristo_contacts_authlog_region,
                        bristo_contacts_authlog_ctry,
                        bristo_contacts_authlog_postal,
                        bristo_contacts_authlog_success)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                        (_usr_nm,_in, _grplogin, _usr_ip, _usr_city,
                        _grp_nm, _usr_reg, _usr_ctry, _usr_zip, _suc))
                self._conn_main.commit()
                self._cursor.close()
                self.bristo_search.groupNameLineEdit.clear()
                self.bristo_search.groupPwdLineEdit.clear()
                self._groupqry = True  # Key variable.
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
                if self.fetch_results:
                    self._LASTGROUP += 1
                self._query = self._LASTGROUP
                self._groups_dict[_db_grpnm] = self._query
                self.menuGroups.addAction(_db_grpnm, self.db_group_select)
                # Add group menu item for this group query
                self.db_contacts_fetch()
                self.reset_timer()
            else:
                self.incorrectgrouplogin()

    def display_notes(self):

        '''
        display_notes display notes in the notes tab.
        '''
        self.bristo_search.notesTableWidget.clearContents()
        _tblwgt_row = 0  # Changes each record
        _tblwgt_date = 0 # static
        _tblwgt_note_col = 1 # static
        for _contact_note in range(len(self.fetch_notes[self._query])):
            if self.fetch_notes[self._query][_contact_note][self._notes_ct] ==\
                    self.fetch_results[self._query][self._ITEM][self._OPHONE]:
                _date_row = self.fetch_notes[self._query][_contact_note][self._stamp].strftime(
                "%m/%d/%y %I:%M%p")
                _qwitem = QTableWidgetItem(_date_row)
                self.bristo_search.notesTableWidget.setItem(_tblwgt_row,
                    _tblwgt_date, _qwitem)
                _notes_row = self.fetch_notes[self._query][_contact_note][self._note]
                _qwitem = QTableWidgetItem(_notes_row)
                self.bristo_search.notesTableWidget.setItem(_tblwgt_row,
                    _tblwgt_note_col, _qwitem)
                _tblwgt_row += 1

    def display_files(self):

        '''
        disply_files displays files in the files tab.
        '''
        self.bristo_search.fileTableWidget.clearContents()
        _tblwgt_file_row = 0  # Changes each record
        _tblwgt_file_id = 0
        _tblwgt_date = 1 # static
        _tblwgt_filename_col = 2 # static
        for _contact_file in range(len(self.fetch_files[self._query])):
            if self.fetch_files[self._query][_contact_file][self._file_ct] ==\
                self.fetch_results[self._query][self._ITEM][self._OPHONE]:
                _id_row = str(self.fetch_files[self._query][_contact_file][self._file_id])
                _qwitem = QTableWidgetItem(_id_row)
                self.bristo_search.fileTableWidget.setItem(_tblwgt_file_row,
                    _tblwgt_file_id, _qwitem)
                _date_row = self.fetch_files[self._query][_contact_file][self._file_stamp].strftime(
                "%m/%d/%y %I:%M%p")
                _qwitem = QTableWidgetItem(_date_row)
                self.bristo_search.fileTableWidget.setItem(_tblwgt_file_row,
                    _tblwgt_date, _qwitem)
                _file_row = self.fetch_files[self._query][_contact_file][self._file_name]
                _qwitem = QTableWidgetItem(_file_row)
                self.bristo_search.fileTableWidget.setItem(_tblwgt_file_row,
                    _tblwgt_filename_col, _qwitem)
                _tblwgt_file_row += 1

    def display_calls(self):

        '''
        display calls displays telephone calls in the calls tab.
        '''
        self.bristo_search.callsTableWidget.clearContents()
        _tblwgt_calls_row = 0  # dynamic
        _tblwgt_calls_date = 2 # static
        _tblwgt_phone_col = 3  # static
        _tblwgt_in_col = 4 # static
        _tblwgt_results_col = 5 # static

        for _contact_call in range(len(self.fetch_calls[self._query])):
            if self.fetch_calls[self._query][_contact_call][self._calls_ct_id] ==\
                self.fetch_results[self._query][self._ITEM][self._ID]:
                _date_row = self.fetch_calls[self._query][_contact_call][self._calls_stamp].strftime(
                "%m/%d/%y %I:%M%p")
                _qwitem = QTableWidgetItem(_date_row)
                self.bristo_search.callsTableWidget.setItem(_tblwgt_calls_row,
                    _tblwgt_calls_date, _qwitem)
                _phone_row = self.fetch_calls[self._query][_contact_call][self._calls_phone]
                _qwitem = QTableWidgetItem(_phone_row)
                self.bristo_search.callsTableWidget.setItem(_tblwgt_calls_row,
                    _tblwgt_phone_col, _qwitem)
                _in_row = self.fetch_calls[self._query][_contact_call][self._calls_in]
                if _in_row:
                    _in_row = 'I'
                else:
                    _in_row = 'O'
                _qwitem = QTableWidgetItem(_in_row)
                self.bristo_search.callsTableWidget.setItem(_tblwgt_calls_row,
                    _tblwgt_in_col, _qwitem)
                _results_row = self.fetch_calls[self._query][_contact_call][self._calls_results]
                _qwitem = QTableWidgetItem(_results_row)
                self.bristo_search.callsTableWidget.setItem(_tblwgt_calls_row,
                    _tblwgt_results_col, _qwitem)
                _tblwgt_calls_row += 1

    def display_appts_by_date(self):

        '''
        display_appts displays appointments in the appointments tab by date.
        '''
        _tblwgt_appt_row = 0  # dynamic
        _tblwgt_id_col = 0 # static
        _tblwgt_ct_id = 1 # static
        _tblwgt_appt_date = 3 # static
        _tblwgt_complete_col = 4 #static
        _tblwgt_purpose_col = 5 # static
        self.bristo_search.apptTableWidget.clearContents()
        for _contact_appt in range(len(self.fetch_appts[self._query])):
            if (self._calendar_activated and\
                self.fetch_appts[self._query][_contact_appt][self._appt_time].date().isoformat()\
                 == self._qcal_date.toPyDate().isoformat()):
                _id_row = str(self.fetch_appts[self._query][_contact_appt][self._appt_id])
                _qwitem = QTableWidgetItem(_id_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_id_col, _qwitem)
                _ct_id_row = str(self.fetch_appts[self._query][_contact_appt][self._appt_ct_id])
                _qwitem = QTableWidgetItem(_ct_id_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_ct_id,  _qwitem)
                _date_row = self.fetch_appts[self._query][_contact_appt][self._appt_time].strftime(
                "%m/%d/%y %I:%M%p")
                _qwitem = QTableWidgetItem(_date_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_appt_date, _qwitem)
                _complete_row = self.fetch_appts[self._query][_contact_appt][self._appt_complete]
                if _complete_row:
                    _complete_row = 'C'
                else:
                    _complete_row = 'O'
                _qwitem = QTableWidgetItem(_complete_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_complete_col, _qwitem)
                _purpose_row = self.fetch_appts[self._query][_contact_appt][self._appt_purpose]
                _qwitem = QTableWidgetItem(_purpose_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_purpose_col, _qwitem)
                _tblwgt_appt_row += 1
        self._calendar_activated = False
        self._display_appts_set = False

    def display_appts(self):

        '''
        display_appts displays appointments in the appointments tab.
        '''
        _tblwgt_appt_row = 0  # dynamic
        _tblwgt_id_col = 0 # static
        _tblwgt_ct_id = 1 # static
        _tblwgt_appt_date = 3 # static
        _tblwgt_complete_col = 4 #static
        _tblwgt_purpose_col = 5 # static
        self.bristo_search.apptTableWidget.clearContents()
        for _contact_appt in range(len(self.fetch_appts[self._query])):
            if self.fetch_appts[self._query][_contact_appt][self._appt_ct_id] ==\
                self.fetch_results[self._query][self._ITEM][self._ID]:
                _id_row = str(self.fetch_appts[self._query][_contact_appt][self._appt_id])
                _qwitem = QTableWidgetItem(_id_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_id_col, _qwitem)
                _ct_id_row = str(self.fetch_appts[self._query][_contact_appt][self._appt_ct_id])
                _qwitem = QTableWidgetItem(_ct_id_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_ct_id,  _qwitem)
                _date_row = self.fetch_appts[self._query][_contact_appt][self._appt_time].strftime(
                "%m/%d/%y %I:%M%p")
                _qwitem = QTableWidgetItem(_date_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_appt_date, _qwitem)
                _complete_row = self.fetch_appts[self._query][_contact_appt][self._appt_complete]
                if _complete_row:
                    _complete_row = 'C'
                else:
                    _complete_row = 'O'
                _qwitem = QTableWidgetItem(_complete_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_complete_col, _qwitem)
                _purpose_row = self.fetch_appts[self._query][_contact_appt][self._appt_purpose]
                _qwitem = QTableWidgetItem(_purpose_row)
                self.bristo_search.apptTableWidget.setItem(_tblwgt_appt_row,
                    _tblwgt_purpose_col, _qwitem)
                _tblwgt_appt_row += 1
        self._display_appts_set = True

    def display_group_in_contact(self):
        '''
        display_group_in_contact displays group info in contact group tab.
        '''
        self.bristo_search.plainTextEdit.clear()
        self.bristo_search.groupNameLineEdit.setText(
            self.fetch_results[self._query][self._ITEM][self._GROUP])
        _grp_nm = self.fetch_results[self._query][self._ITEM][self._GROUP]
        self.bristo_search.groupLogoLabel.clear()
        self.bristo_search.groupCtLogoLabel.clear()
        _idx = 0
        if _grp_nm:
            for _idx in range(len(self.fetch_groups[self._query])):
                if _grp_nm == self.fetch_groups[self._query][_idx][self._GRPNAME]:
                    break

            if self.fetch_groups[self._query]:
                self.bristo_search.plainTextEdit.insertPlainText(
                self.fetch_groups[self._query][_idx][self._GRPDESC])
                # Get logo
                self._image_bytea1 = self.fetch_groups[self._query][_idx][self._GRPPIC]
                self.display_pic(self.bristo_search.groupLogoLabel,
                    self._image_bytea1)
                self._image_bytea2 = self.fetch_groups[self._query][_idx][self._GRPPIC]
                self.display_pic(self.bristo_search.groupCtLogoLabel, self._image_bytea2)
                _idx = 0


    def display_msg(self):

        '''
        display_msg displays a message in the status bar after update of information.
        '''
        if not self._groups:
            _msg = 'Contact, notes, files, calls '+str(self._ITEM+1)+" of "\
            +str(self._LASTITEM+1)+" and map url fetched and loaded."
            self.contactsStatusBar.showMessage(_msg, 3000)
        if self._groups:
            _msg = 'Group '+str(self._ITEM+1)+" of "\
            +str(self._LASTITEM+1)+" fetched and loaded."
            self.contactsStatusBar.showMessage(_msg, 3000)

    def unblock_signals(self):

        '''
        unblock_signals unblocks all signals after information has been loaded.
        '''
        if not self._groups:
            self.bristo_search.notesTableWidget.blockSignals(False) #unblock for update
            self.bristo_search.callsTableWidget.blockSignals(False)
            self.bristo_search.apptTableWidget.blockSignals(False)
            self.bristo_search.msgTableWidget.blockSignals(False)
        if self._groups:
             self.search_groups.blockSignals(False)


    def refresh_map(self):

        '''
        refresh_map refreshes the google map page when the user clicks the refresh
        button.
        '''
        _map_addr = self.fetch_results[self._query][self._ITEM][self._ADDR]
        _map_zip = self.fetch_results[self._query][self._ITEM][self._POSTAL]
        _google = 'https://www.google.com/maps/place/'
        _loc = _google+_map_addr+" "+_map_zip
        self.google_com.load(QUrl(_loc))

    def open_url_map(self):

        '''
        open_url_map opens the google map web page when the user clicks the browser
        button.
        '''
        _map_addr = self.fetch_results[self._query][self._ITEM][self._ADDR]
        _map_zip = self.fetch_results[self._query][self._ITEM][self._POSTAL]
        _google = 'https://www.google.com/maps/place/'
        _loc = _google+_map_addr+" "+_map_zip
        webbrowser.open(_loc)

    def refresh_email(self):

        '''
        refresh_map refreshes the google map page when the user clicks the refresh
        button.
        '''

        _email_addr_filter = self.fetch_results[self._query][self._ITEM][self._OEMAIL]
        _mail_search = self._user_webmail
        if self._calendar_activated:
            _date = self._qcal_date.toPyDate().strftime("%A %B %d, %Y")
            _loc = _mail_search + _date
        else:
            _loc = _mail_search + _email_addr_filter
        self.google_mail_com.load(QUrl(_loc))

    def db_insert_contact_note(self):

        '''
        db_insert inserts one new contact note into the PostgreSQL database table
        bristo_contacts_notes.  The serial ID, Time Date Stamp are automatically
        generated.  Only the foreign key office phone primary key for
        bristo_contacts_ct lookup value and notice itself need be entered.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True

        else:
            self.connection_closed_msg()
            return

        if self._connected:
            self._cursor = self._conn_main.cursor()
            self.reset_timer()
            _owner = self._user
            _crow = self.bristo_search.notesTableWidget.currentRow()
            _ccol = self.bristo_search.notesTableWidget.currentColumn()
            _oph = self.bristo_search.officePhoneLineEdit.text()
            _note = self.bristo_search.notesTableWidget.cellWidget(
                                                _crow,_ccol ).text()

            self._cursor.execute("""INSERT INTO bristo_contacts_notes
                    (bristo_contacts_notes_ct, bristo_contacts_notes_note,
                    bristo_contacts_notes_owner)
                    VALUES (%s,%s,%s);""", (_oph,_note,_owner))
            self._conn_main.commit()
            self.contactsStatusBar.showMessage('New Contact Note Inserted.', 3000)
            self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
            self._connected = False
            self._db_update = True


    def db_insert_contact_msg(self):

        '''
        db_insert_contact_msg inserts one new contact message into the PostgreSQL
        database table bristo_contacts_messages after contact/user availability
        has been verified.  The serial ID, Time Date Stamp, Sender and Receiver
        are automatically generated.  Only the message need be entered.

        Need to set up thread with wait time for check messages after sending.
        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self._cursor = self._conn_main.cursor()
            if self._connected:
                self.reset_timer()
                _sender = self._user
                # Get username for current contact email address
                _usr_email = self.fetch_results[self._query][self._ITEM][self._OEMAIL]
                _receiver = self.get_contact_username(_usr_email)
                _crow = self.bristo_search.msgTableWidget.currentRow()
                _ccol = self.bristo_search.msgTableWidget.currentColumn()
                _msg = self.bristo_search.msgTableWidget.cellWidget(
                                                    _crow,_ccol ).text()
                if _msg:
                    self._cursor.execute("""INSERT INTO bristo_contacts_messages
                            (bristo_contacts_messages_sender,
                            bristo_contacts_messages_receiver,
                            bristo_contacts_messages_msg)
                            VALUES (%s,%s,%s);""", (_sender,  _receiver,  _msg))
                    self._conn_main.commit()
                    self.contactsStatusBar.showMessage('Message sent.......', 4000)
                    self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                    self._connected = False
                    self._db_update = True
                else:
                    self.contactsStatusBar.showMessage('No Message to send...', 4000)
                    self._pool.putconn(conn=self._conn_main,  key=self._conn_main_key)
                    self._connected = False
        else:
            self.connection_closed_msg()

    def check_messages(self):
        '''
        check_messages displays all messages in the bristo_contacts_messages
        database table that were sent by the current user to the current contact
        and that were sent by the current contact to the current user.
        '''
        if self._pool:
            self.block_signals()
            self.reset_timer()
            # Query the database to create list of messages returned by psycopg2
            # driver from the PostgreSQL database.
            _user = self._user
            _contct_email = self.fetch_results[self._query][self._ITEM][self._OEMAIL]
            _contct_usrnm = self.get_contact_username(_contct_email)
            if _contct_usrnm and self._pool:
                self._conn_main = self._pool.getconn(key=self._conn_main_key)
                self._connected = True
                self._cursor = self._conn_main.cursor()
                self._cursor.execute("""SELECT * FROM bristo_contacts_messages WHERE
                        bristo_contacts_messages_sender = %s AND
                        bristo_contacts_messages_receiver = %s OR
                        bristo_contacts_messages_sender = %s AND
                        bristo_contacts_messages_receiver = %s
                        ORDER by bristo_contacts_messages_stamp
                        LIMIT %s;""",
                        (_user, _contct_usrnm, _contct_usrnm, _user, self._limit))
                self.fetch_msg = self._cursor.fetchall() # Get messages
                self.display_messages(self.fetch_msg) # Display messages
                self.contactsStatusBar.showMessage('Messages updated .......', 4000)
                self._cursor.close()
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
                self.unblock_signals()
            else:
                self.bristo_search.msgTableWidget.clearContents()
                self.contactsStatusBar.showMessage('User not found.....', 4000)
        else:
            self.connection_closed_msg()

    def get_contact_username(self,  _contact_email):
        '''
        get_contact_username accepts the contact email address and
        returns the contact username in bristo_contacts_users for a user
        email match.
        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self._cursor = self._conn_main.cursor()
            if self._connected:
                # Get username for current contact email address
                self._cursor.execute("""SELECT * FROM bristo_contacts_users WHERE
                bristo_contacts_users_email = %s LIMIT 1;""", (_contact_email,))
                if not self._cursor.rowcount:
                    self.contactsStatusBar.showMessage('No User Found.....', 4000)
                    self._cursor.close()
                    self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                    self._connected = False
                else:
                    _usr = self._cursor.fetchone()
                    self._cursor.close()
                    self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                    self._connected = False
                    return _usr[self._USERNM]

    def display_messages(self, _messages):
        '''
        display_messages accepts a message list returned by psycopg2 form a
        PostgreSQL database and displays these messages in the message
        table widget.
        '''
        _user = self._user
        # Display the messages in msgTableWidget and make user sent messages
        # distinct (blue or dark or highlighted) while contact sent message are
        # displayed normally.
        self.bristo_search.msgTableWidget.clearContents()
        _tblwgt_row = 0  # Changes each record
        _tblwgt_stamp = 2 # static
        _tblwgt_sender = 3 # static
        _tblwgt_msg = 5 # static
        for _msg in range(len(_messages)):

            _stamp = self.fetch_msg[_msg][_tblwgt_stamp].strftime(
            "%m/%d/%y %I:%M%p")
            _qwitem = QTableWidgetItem(_stamp)
            self.bristo_search.msgTableWidget.setItem(_tblwgt_row,
                _tblwgt_stamp, _qwitem)

            _sender = self.fetch_msg[_msg][_tblwgt_sender]
            _qwitem = QTableWidgetItem(_sender)
            self.bristo_search.msgTableWidget.setItem(_tblwgt_row,
                _tblwgt_sender, _qwitem)

            _message = self.fetch_msg[_msg][_tblwgt_msg]
            _qwitem = QTableWidgetItem(_message)
            if _sender == _user:
                _qwitem.setForeground(QColor(65,105,225))
            self.bristo_search.msgTableWidget.setItem(_tblwgt_row,
                _tblwgt_msg, _qwitem)
            _tblwgt_row += 1
        self.bristo_search.msgTableWidget.setCurrentCell(_tblwgt_row, _tblwgt_msg)

    def resize_notes(self):

        '''
        resize_notes resets the table widget resize mode to resize to contents.
        '''

        self.bristo_search.notesTableWidget.verticalHeader().setSectionResizeMode(3)
        self.bristo_search.callsTableWidget.horizontalHeader().setSectionResizeMode(3)
        

    def resize_calls(self):

        '''
        resize_calls resets the table widget resize mode to resize to contents.
        '''

        self.bristo_search.callsTableWidget.verticalHeader().setSectionResizeMode(3)
        self.bristo_search.callsTableWidget.horizontalHeader().setSectionResizeMode(3)

    def resize_appts(self):

        '''
        resize_appts resets the table widget resize mode to resize to contents.
        '''

        self.bristo_search.apptTableWidget.verticalHeader().setSectionResizeMode(3)
        self.bristo_search.apptTableWidget.horizontalHeader().setSectionResizeMode(3)

    def resize_msg(self):
        '''
        resiize_msg resets the table widget resize mode to resize to contents.
        '''
        self.bristo_search.msgTableWidget.verticalHeader().setSectionResizeMode(3)
        self.bristo_search.msgTableWidget.horizontalHeader().setSectionResizeMode(3)

    def db_insert_contact_file(self):

        '''
        db_insert_contact_file inserts one file into the PostgreSQL database table
        bristo_contacts_files.  The serial ID, Time Date Stamp are automatically
        generated.  Only the foreign key office phone primary key for
        bristo_contacts_ct lookup value, file name and file need be entered.

        '''

        _owner = self._user
        _oph = self.bristo_search.officePhoneLineEdit.text()
        fdlg = QFileDialog()
        options = fdlg.Options()
        options |= fdlg.DontUseNativeDialog     
        filenametup = fdlg.getOpenFileName(self, 'Open file',
                   "Image files (*.jpg *.gif *.png)",  options=optins)
        filename = filenametup[0]                                 # get fname 
        _fnm = self.get_path_filename(filename)             # Get name to write
        self._file_bin = open(filename, 'rb').read()        # Read > pointer
        # self._conn_main_timer = 120000                          # Need large files
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self._cursor = self._conn_main.cursor()
            if self._connected:
                self.reset_timer()
                self._cursor.execute("""INSERT INTO bristo_contacts_files
                   (bristo_contacts_files_ct, bristo_contacts_files_name,
                       bristo_contacts_files_file, bristo_contacts_files_owner)
                   VALUES (%s, %s, %s, %s); """,
                   (_oph, _fnm, psycopg2.Binary(self._file_bin), _owner))
                self._conn_main.commit()
                self.contactsStatusBar.showMessage('New contact file inserted.', 3000)
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
                self._db_update = True


    def get_contact_file(self):

        '''
        get_contact_file retrieves binary files from the database and saves them to
        the users desktop.
        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._conn_main_timer = 120000           # Need large files
            self._connected = True
            self._cursor = self._conn_main.cursor()
            if self._connected:
                self.reset_timer()
                _crow = self.bristo_search.fileTableWidget.currentRow()
                _ccol = self._file_id
                _file_id = self.bristo_search.fileTableWidget.item(
                _crow, _ccol).text()
                self._cursor.execute("SELECT * FROM\
                    bristo_contacts_files WHERE bristo_contacts_files_id = %s", (
                    _file_id,))
                _file_row = self._cursor.fetchone()
                _file_row_name = _file_row[self._file_name]
                _file = _file_row[self._file_file] # binary file
                path = os.path.join(os.path.expanduser("~"), "Desktop", _file_row_name)
                with open(path, 'wb') as f:
                    f.write(_file) # writes file to desktop
                    f.close()      # close file
                self.contactsStatusBar.showMessage(_file_row_name+' '\
                                                   +'saved on Desktop.', 3000)
                self._cursor.close()
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
                self._conn_main_timer = 300000

    def get_path_filename(self,  _path):

        '''
        get_path_filename extracts linux/windows/mac
        filenames from a path and returns them.

        >>> ctl = Controller()
        >>> _path = '/home/jacksonkirka/test.pdf'
        >>> filename0 = ctl.get_path_filename(_path)
        >>> filename0
        'test.pdf'

        '''

        head, tail = ntpath.split(_path)
        return tail

    def update_pic(self):
        '''
        update_pic opens a picture provided by the PostgreSQL database user
        and displays it then returns self._image_bin to the caller dialog.
        '''
        self._conn_main_timer = 600000
        self.reset_timer()
        fdlg = QFileDialog()
        options = fdlg.Options()
        options |= fdlg.DontUseNativeDialog        
        fnametup = fdlg.getOpenFileName(self, 'Open file',
                   "Image files (*.jpg *.gif *.png)", options=options)       # get file tuple
        fname = fnametup[0]                                 # get fname 
        self._image = QPixmap(fname)                        # Get Pixmap
        self._image_bin = open(fname, 'rb').read()          # Read > pointer
        self.bristo_search.picLabel.setPixmap(self._image)  # Display
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self._cursor = self._conn_main.cursor()
            if self._connected:
                _id = self.fetch_results[self._query][self._ITEM][self._ID]
                self._cursor = self._conn_main.cursor()
                self._cursor.execute("""UPDATE bristo_contacts_ct SET
                bristo_contacts_ct_picture = %s
                WHERE bristo_contacts_ct_id = %s;""",
                (psycopg2.Binary(self._image_bin),
                 _id ))
                self._conn_main.commit()
                self.contactsStatusBar.showMessage('Image updated.', 3000)
            self._cursor.close()
            self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
            self._connected = False
            self._conn_main_timer = 10000

    def update_group_pic(self):
        '''
        update_group pic opens a group logo provided by the PostgreSQL database
        user and displays it then returns self._image_bin to the caller dialog.
        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self._cursor = self._conn_main.cursor()
            self.reset_timer()
            fdlg = QFileDialog()
            options = fdlg.Options()
            options |= fdlg.DontUseNativeDialog    
            fnametup = fdlg.getOpenFileName(self, 'Open file',
                       "Image files (*.jpg *.gif *.png)",  options=options)       # Get Filename
            fname = fnametup[0]                                 # get fname 
            self._image = QPixmap(fname)                        # Get Pixmap
            self._image_bin = open(fname, 'rb').read()          # Read > pointer
            self.search_groups.newGroupLabel.setPixmap(self._image) # Show image
            if self._connected:
                _id = self.fetch_groups_owned[self._ITEM][self._ID]
                self._cursor = self._conn_main.cursor()
                self._cursor.execute("""UPDATE bristo_contacts_groups SET
                bristo_contacts_groups_pic = %s
                WHERE bristo_contacts_groups_id = %s;""",
                (psycopg2.Binary(self._image_bin),_id,))
                self._conn_main.commit()
                self.contactsStatusBar.showMessage('Image updated.', 3000)
                self._cursor.close()
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False


    @staticmethod
    def display_pic(_qobject, _picture):
        '''
        display_pic accepts a qobject and a buffer returned by psycopg2 database
        driver then displays pixmap on the qobject.  For future enhancements
        and addons this may have to be an instance method requiring (self,..) and
        no @staticmethod.
        '''
        p = QPixmap()               # Create QPixmap
        p.loadFromData(_picture)     # Load picture from data
        _qobject.setPixmap(p)       # Display picture on object


    def live_call_widgets(self):
        '''
        live_widgets is a bristosoft native abstract idea.  It postulates that
        resources should be allocated just in time.  This class method creates
        live widgets where they are needed at dataentry time on the fly ie
        live.  The live widgets require a boolean object for control set/not set.
        '''
        if not self._live_set:
            _crow = self.bristo_search.callsTableWidget.currentRow()
            self.live_combobox = QComboBox()
            self.bristo_search.callsTableWidget.setCellWidget(
                   _crow, self._calls_phone, self.live_combobox)
            self.live_combobox.setFrame(False)
            self.live_combobox.setEditable(True)
            self.live_combobox.addItem(self.fetch_results[self._query][self._ITEM][self._OPHONE])
            self.live_combobox.addItem(self.fetch_results[self._query][self._ITEM][self._CELL])
            self.live_combobox.addItem(self.fetch_results[self._query][self._ITEM][self._HPHONE])
            self.live_chkbox = QCheckBox()
            self.bristo_search.callsTableWidget.setCellWidget(
                   _crow, self._calls_in, self.live_chkbox)
            self._live_set = True # Prevents Dupes on selection

    def db_insert_contact_call(self):

        '''
        db_insert_contact_call inserts one new contact call into the PostgreSQL
        database table bristo_contacts_calls.  The serial ID, Time Date Stamp
        are automatically generated.  Only the phone number called, inbound or
        or outbound and results need be entered.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            if self._connected:
                self.reset_timer()
                if self._cursor.closed:
                    self._cursor = self._conn_main.cursor()
                _owner = self._user
                _id = 0
                _crow = self.bristo_search.callsTableWidget.currentRow()
                _id_ct = str(self.fetch_results[self._query][self._ITEM][_id])
                _ph = self.live_combobox.currentText()
                _in = self.live_chkbox.isChecked()
                _results = self.bristo_search.callsTableWidget.cellWidget(
                    _crow, self._calls_results).text()

                self._cursor.execute("""INSERT INTO bristo_contacts_calls
                        (bristo_contacts_calls_ct_id, bristo_contacts_calls_phone,
                        bristo_contacts_calls_type, bristo_contacts_calls_results,
                        bristo_contacts_calls_owner)
                        VALUES (%s,%s, %s, %s, %s);""", (_id_ct, _ph,
                        _in, _results, _owner))
                self._conn_main.commit()
                self._live_set = False
                self.contactsStatusBar.showMessage('New Contact Call Inserted.', 5000)
                self._cursor.close()
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
                self._db_update = True

    def appt_display_contact(self):

        _ccol = self._appt_ct_id
        _crow = self.bristo_search.apptTableWidget.currentRow()
        if self.bristo_search.apptTableWidget.item(
               _crow,  self._appt_id) is None:
                   return
        _contact_id = int(self.bristo_search.apptTableWidget.item(_crow,
            _ccol).text())
        for _index in range(len(self.fetch_results[self._query])):
            if self.fetch_results[self._query][_index][self._ID] == _contact_id:
                break
        self._ITEM = _index
        self.display_data_not_appts()


    def live_appt_widgets(self):
        '''
        live_appt_widgets displays live Date and checkbox widgets to use live.
        '''
        if not self._display_appts_set:
            self.appt_display_contact()
        if not self._live_set:
            _crow = self.bristo_search.apptTableWidget.currentRow()
            self.live_chkbox = QCheckBox()
            self.bristo_search.apptTableWidget.setCellWidget(
                   _crow, self._appt_complete, self.live_chkbox)
            if self.bristo_search.apptTableWidget.item(
               _crow,  self._appt_id) is None:
                self.live_dtimeedit = QDateTimeEdit()
                self.live_dtimeedit.setCalendarPopup(True)
                self.bristo_search.apptTableWidget.setCellWidget(
                       _crow, self._appt_time, self.live_dtimeedit)
            self._live_set = True # Prevents Dupes on selection



    def db_insert_update_appt(self):
        '''
        db_insert_update_appt calls either insert or update appointment methods
        dependent on whether the current row is empty or not.
        '''
        self.reset_timer()
        _crow = self.bristo_search.apptTableWidget.currentRow()
        if self.bristo_search.apptTableWidget.item(
                _crow,  self._appt_id) is None:
            self.db_insert_contact_appt()
        else:
            self.db_update_contact_appt()
        self._db_update = True


    def db_insert_contact_appt(self):

        '''
        db_insert_contact_appt inserts one new contact appointment into the
        PostgreSQL database table bristo_contacts_appt.  The serial ID,
        Time Date Stamp are automatically generated.  Only the date/time of
        the appointment, open or closed and purpose need be entered.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self._cursor = self._conn_main.cursor()
            if self._connected:
                _owner = self._user
                _crow = self.bristo_search.apptTableWidget.currentRow()
                _id_ct = str(self.fetch_results[self._query][self._ITEM][self._ID])
                _qtime = self.live_dtimeedit.dateTime()
                _time = _qtime.toPyDateTime()
                _closed = self.live_chkbox.isChecked()
                _purpose = self.bristo_search.apptTableWidget.cellWidget(
                    _crow, self._appt_purpose).text()

                self._cursor.execute("""INSERT INTO bristo_contacts_appt
                        (bristo_contacts_appt_ct_id, bristo_contacts_appt_time,
                        bristo_contacts_appt_complete, bristo_contacts_appt_purpose,
                        bristo_contacts_appt_owner) VALUES (%s,%s, %s, %s, %s);""",
                        (_id_ct, _time,_closed, _purpose,
                _owner))
                self._conn_main.commit()
                self._live_set = False
                self.contactsStatusBar.showMessage(
                'New Contact Appointment Inserted.', 5000)
                self._cursor.close()
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
                self._db_update = True

    def db_update_contact_appt(self):

        '''
        db_update_contact_appt updates a contact appointment in the
        PostgreSQL database table bristo_contacts_appt.  Only the
        complete/open checkbox and purpose can be updated.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self._cursor = self._conn_main.cursor()
            self.reset_timer()
            _crow = self.bristo_search.apptTableWidget.currentRow()
            _appt_id = self.bristo_search.apptTableWidget.item(
                _crow,  self._appt_id).text()
            _closed = self.live_chkbox.isChecked()
            _purpose = self.bristo_search.apptTableWidget.cellWidget(
                _crow, self._appt_purpose).text()

            self._cursor.execute("""UPDATE bristo_contacts_appt SET
                    bristo_contacts_appt_complete, bristo_contacts_appt_purpose
                    = %s,%s WHERE bristo_contacts_appt_id = %s;""", (_closed,
                    _purpose, _appt_id))
            self._conn_main.commit()
            self._live_set = False
            self.contactsStatusBar.showMessage(
            'Contact Appointment Updated.', 5000)
            self._cursor.close()
            self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
            self._connected = False

    def display_appts_bydate(self):

        '''
        display_appts_bydate accepts the date double clicked by the calendar.
        It then displays all scheduled items for that date.
        '''

        self._calendar_activated = True
        self._displayed_apptsbydate = False
        self._qcal_date = self.bristo_search.calendarWidget.selectedDate()
        self.contactsStatusBar.showMessage('Calendar date activated.', 5000)
        self.block_signals()
        self.display_appts_by_date()
        self.unblock_signals()

    @staticmethod
    def open_url(_url):
        '''

        open_url opens a web url given by the caller in the default browser of the platform contacts
        is currently running in.

        '''
        webbrowser.open(_url)
        #_opened = webbrowser.open(_url, autoraise=True)
        #if not _opened:
         #   self.contactsStatusBar.showMessage('Unable to open url requested.', 5000)

    def open_url_directions(self):
        '''
        open_url_directions accepts a from direction based on users email to match contact
        record in database using street address and zip code and also a destination address
        as the current displayed contact address.  The class method returns a url then opens
        it in the default browser as google directions.
        '''

        # query for user contact record if found build _from address
        _user_email = self._user_email
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self.reset_timer()
            if self._connected:
                if self._cursor.closed:
                    self._cursor = self._conn_main.cursor()
                self._cursor.execute("""SELECT * FROM bristo_contacts_ct
                        WHERE bristo_contacts_ct_email1 = %s LIMIT 1;""",
                        (_user_email,  ))
                _user_contact =  self._cursor.fetchone()
                if self._cursor.rowcount:
                    # _from address
                    _from_addr = _user_contact[self._ADDR]
                    _from_zip = _user_contact[self._POSTAL]
                    _from = _from_addr+" "+_from_zip
                    # _dest address
                    _dest_addr = self.fetch_results[self._query][self._ITEM][self._ADDR]
                    _dest_zip = self.fetch_results[self._query][self._ITEM][self._POSTAL]
                    _dest = _dest_addr+" "+_dest_zip

                    # build directions url
                    _google = 'https://www.google.com/maps/dir/'
                    _dir_url = _google+_from+"/"+_dest
                    self.open_url(_dir_url)
                elif not self._cursor.rowcount:
                    self.contactsStatusBar.showMessage(
                        'No contact info found for user.', 5000)
            self._cursor.close()
            self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
            self._connected = False
        else:
            self.connection_closed_msg()


    def db_full_vacuum(self):
        '''

        db_full_vacuum does a complete vacuum of the database.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self.reset_timer()
            if self._connected:
                self._cursor_admin = self._conn_admin.cursor()
                old_isolation_level = self._conn_admin.isolation_level
                self._conn_admin.set_isolation_level(0)
                self.query = "VACUUM FULL"
                self._doQuery(self.query)
                self._conn_admin.set_isolation_level(old_isolation_level)
                _msg ='Vacumming Database '+self._db+' complete.'
                self.contactsStatusBar.showMessage(_msg, 5000)
                self._cursor_admin.close()
                self._conn_admin.putconn(conn=self._conn_main, key=self._conn_main_key)
            else:
                _msg = 'Please connect to the database to vacuum.'
                self.contactsStatusBar.showMessage(_msg, 5000)


    def db_reindex(self):
        '''

        db_reindex reindexes the database bristo_contacts_ct.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            if self._connected:
                self._cursor = self._conn_main.cursor()
                old_isolation_level = self._conn_main.isolation_level
                self._conn_main.set_isolation_level(0)
                self.query = 'REINDEX DATABASE bristocontacts'
                self._doQuery(self.query)
                self._conn_main.set_isolation_level(old_isolation_level)
                _msg = 'Reindexing '+self._db+' is complete.'
                self.contactsStatusBar.showMessage(_msg,  5000)
                self._cursor.close()
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
            else:
                _msg = 'Please connect to the database to reindex.'
                self.contactsStatusBar.showMessage(_msg, 5000)

    def _doQuery(self, query):
        '''

        _doQuery performs a query with a cursor and then commits the
        transaction.  This query will be used by default unless a
        non standard query is needed.  This is an EXPERIMENTAL standardized
        SQL method to standardize SQL Queries in bristoSOFT Contacts.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            self._cursor = self._conn_main.cursor() # Get cursor for connection
            self._cursor.execute(query)             # Submit query for execution
            self._conn_main.commit()                # Commit the transaction

                                                    # Note: can't close cursor
                                                    # and need to return cursor info
                                                    # to the caller.

    def _doQueryClean(self):
        '''
        _doQueryClean closes the main cursor and puts away the connection to
        the threaded connection pool.  This is EXPERIMENTAL.
        '''

        self._cursor.close()                    # Close the cursor
        self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
        self._connected = False

    def printuserscontacts(self):
        '''
        printuserscontacts prints contacts in the current python contacts list in memory
        to the printer.  Note: In future will have boolean for print authorized yes/no on
        groups.
        '''
        if self.fetch_results:
            self._prt.print_users_contacts(
                self.fetch_results[self._query],self._grprpt)

    def db_close(self):
        '''

        db_close closing the current cursor if any and database connection.  It
        then turns the status bar red.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            if self._connected:
                if self._cursor.close:
                    self._cursor = self._conn_main.cursor()
                # Log authentication
                _usr_nm = self._user
                _grplogin = False
                _usr_ip = self._usr_ip
                _usr_city = self._usr_city
                _usr_reg = self._usr_region
                _usr_ctry = self._usr_ctry
                _usr_zip = self._usr_zip
                _suc = True
                _in = False
                _grplogin = False
                self._cursor.execute("""INSERT INTO bristo_contacts_authlog
                        (bristo_contacts_authlog_uname,
                        bristo_contacts_authlog_in,
                        bristo_contacts_authlog_group,
                        bristo_contacts_authlog_inet,
                        bristo_contacts_authlog_city,
                        bristo_contacts_authlog_region,
                        bristo_contacts_authlog_ctry,
                        bristo_contacts_authlog_postal,
                        bristo_contacts_authlog_success)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                        (_usr_nm,_in, _grplogin, _usr_ip, _usr_city,
                        _usr_reg, _usr_ctry, _usr_zip, _suc))
                self._conn_main.commit()
                self._cursor.close()
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._pool.closeall()
                self._pool = False
                self._connected = False
                self.contactsStatusBar.setStyleSheet("background-color: \
                                                      rgb(230, 128, 128);")
                self.conn_msg = self._user + ' logged out.'
                self.contactsStatusBar.showMessage(self.conn_msg)
                self._disconnected = True

    def restore_status_bar(self):
        '''
        restore_status_bar restores the status bar to red.
        '''
        if self._pool:
            self.contactsStatusBar.setStyleSheet("background-color: \
                                              rgb(152,251,152);")
        else:
            self.contactsStatusBar.setStyleSheet("background-color: \
                                              rgb(230, 128, 128);")
        #self.contactsStatusBar.showMessage(self.conn_msg)

    def db_idle(self):
        '''

        db_idle closes the current cursor if any and database connection as
        well ass the connection pool.  It then turns the status bar red.

        '''
        if self._pool:
            self._conn_main = self._pool.getconn(key=self._conn_main_key)
            self._connected = True
            if self._connected:
                if self._cursor.close:
                    self._cursor = self._conn_main.cursor()
                # Log authentication
                _usr_nm = self._user
                _usr_ip = self._usr_ip
                _usr_city = self._usr_city
                _usr_reg = self._usr_region
                _usr_ctry = self._usr_ctry
                _usr_zip = self._usr_zip
                _suc = True
                _in = False
                _grplogin = False
                self._cursor.execute("""INSERT INTO bristo_contacts_authlog
                        (bristo_contacts_authlog_uname,
                        bristo_contacts_authlog_in,
                        bristo_contacts_authlog_group,
                        bristo_contacts_authlog_inet,
                        bristo_contacts_authlog_city,
                        bristo_contacts_authlog_region,
                        bristo_contacts_authlog_ctry,
                        bristo_contacts_authlog_postal,
                        bristo_contacts_authlog_success)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                        (_usr_nm,_in, _grplogin, _usr_ip, _usr_city,
                        _usr_reg, _usr_ctry, _usr_zip, _suc))
                self._conn_main.commit()
                self._cursor.close()
                self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
                self._connected = False
                self._pool.closeall()
                self._pool = False
                self.contactsStatusBar.setStyleSheet("background-color: \
                                                      rgb(230, 128, 128);")
                # self.contactsStatusBar.removeWidget(self.conn_msg)
                self.conn_msg = self._user+'@'+self._host+\
                '/'+ self._db+' logged out due to inactivity.'
                self.contactsStatusBar.showMessage(self.conn_msg)

                # Stop the timers
                self._idle.stop()               # Stop main query timer
                self._poll_msg_qtimer.stop()    # Stop query message timer

                self._disconnected = True

    def connection_closed_msg(self):
        '''
        connection_closed_msg displays a message in the status bar that
        informs they are not logged in and to login to complete their
        query.
        '''
        self.contactsStatusBar.showMessage(
                'Connection closed.  Please login.', 5000)


    def close_contacts(self):
        '''

        close_contacts close closes the current database connection
        and closes bristoSOFT Contacts.

        '''

        # Log authentication
        if self._pool:
            try:
                _usr_nm = self._user
                _usr_ip = self._usr_ip
                _usr_city = self._usr_city
                _usr_reg = self._usr_region
                _usr_ctry = self._usr_ctry
                _usr_zip = self._usr_zip
                _suc = True
                _in = False
                _grplogin = False
                self._conn_main = self._pool.getconn(key=self._conn_main_key)
                self._connected = True
                self._cursor = self._conn_main.cursor()
                self._cursor.execute("""INSERT INTO bristo_contacts_authlog
                    (bristo_contacts_authlog_uname,
                    bristo_contacts_authlog_in,
                    bristo_contacts_authlog_group,
                    bristo_contacts_authlog_inet,
                    bristo_contacts_authlog_city,
                    bristo_contacts_authlog_region,
                    bristo_contacts_authlog_ctry,
                    bristo_contacts_authlog_postal,
                    bristo_contacts_authlog_success)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                    (_usr_nm,_in, _grplogin, _usr_ip, _usr_city,
                    _usr_reg, _usr_ctry, _usr_zip, _suc))
            except psycopg2.DatabaseError as dberror:
                self._conn_main.rollback()
                # self.contactsStatusBar.removeWidget(self.conn_msg)
                self.contactsStatusBar.setStyleSheet("background-color: \
                                              rgb(230, 128, 128);")
                _err_msg =QLabel(str(dberror))
                self.contactsStatusBar.showMessage(_err_msg)
            self._conn_main.commit()
            self._cursor.close()
            self._pool.putconn(conn=self._conn_main, key=self._conn_main_key)
            self._connected = False
            self._pool.closeall()
            self._pool = False
            # self.contactsStatusBar.removeWidget(self.conn_msg)
            self.contactsStatusBar.setStyleSheet("background-color: \
                                              rgb(230, 128, 128);")

            self.conn_msg = self._host+ '/' + self._db+'.'
            self.contactsStatusBar.showMessage(self.conn_msg)

        self.close()


