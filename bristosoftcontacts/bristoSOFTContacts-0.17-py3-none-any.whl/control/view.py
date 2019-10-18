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
'''
view.py module creates the interface objects by multiple inheritance while
leveraging Qt Designer tools to deliver a world class GUI experience.  This
view.py module is imported by the controller.py.
'''

# Imports
from PyQt5.QtGui import *
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.uic import *
from interface import contacts
from interface import login
from interface import search
from interface import changepwd
from interface import newgroup
from interface import searchgroup



class bristoContactsLogin(QDialog, login.Ui_loginDialog):
    '''

    bristoContactsLogin is the login dialog used to login
    to a PostgreSQL database.  It captures the test needed
    to build the PostgreSQL connection string.

    '''
    def __init__(self,  parent=None):
        '''

        This initialization class method initializes
        QDialog and bristoContactsLogin.

        '''
        super(bristoContactsLogin,  self).__init__(parent)
        self.setupUi(self)

class bristoContactsDialog(QDialog,  contacts.Ui_contactsDialog):
    '''

    bristoContactsDialog provides a GUI interface for building
    the database INSERT query.

    '''
    def __init__(self,  parent=None):
        '''

        This initialization class method initializes
        QDialog and bristoContactsDialog.

        '''
        super(bristoContactsDialog,  self).__init__(parent)
        self.setupUi(self)

class bristoContactsSearchDialog(
    QDialog,  search.Ui_contactsSearchDialog):
    '''

    bristoContactsSearchDialog is the a dialog for traversing
    the contacts database.

    '''
    def __init__(self,  parent=None):
        '''

        This initialization class method initializes
        QDialog and bristoContactsSearchDialog.

        '''
        super(bristoContactsSearchDialog,  self).__init__(parent)
        self.setupUi(self)

class bristoContactsChgPwdDlg(
    QDialog,  changepwd.Ui_changepwdDialog):
    '''

    bristoContactsChgPwdDlg is the a dialog changing the user password.

    '''
    def __init__(self,  parent=None):
        '''

        This initialization class method initializes
        QDialog and bristoContactsChgPwdDlg.

        '''
        super(bristoContactsChgPwdDlg,  self).__init__(parent)
        self.setupUi(self)

class bristoNewGroupDlg(QDialog,  newgroup.Ui_newGroupDialog):
    '''

    bristoNewGroupDlg is the a dialog for adding new groups.

    '''
    def __init__(self,  parent=None):
        '''

        This initialization class method initializes
        QDialog and bristoNewGroupDlg.

        '''
        super(bristoNewGroupDlg,  self).__init__(parent)
        self.setupUi(self)

class bristoSearchGroupDlg(
    QDialog,  searchgroup.Ui_searchGroupDialog):
    '''

    bristoSearchGroupDlg is the a dialog for navigating groups.

    '''
    def __init__(self,  parent=None):
        '''

        This initialization class method initializes
        QDialog and bristoSearchGroupDlg.

        '''
        super(bristoSearchGroupDlg,  self).__init__(parent)
        self.setupUi(self)

class bristoMapper(QWebView):

    '''
    bristoMapper is a webview of the address provided in a contact.
    '''
    def __init__(self, parent=None):
        super(bristoMapper, self).__init__(parent)

class bristoMailView(QWebView):
    '''
    bristoMailView is a webview of the users web mail service filtered for the
    current contact.
    '''
    def __init__(self,  parent=None):
        super(bristoMailView,  self).__init__(parent)
        self.setZoomFactor(.75)
