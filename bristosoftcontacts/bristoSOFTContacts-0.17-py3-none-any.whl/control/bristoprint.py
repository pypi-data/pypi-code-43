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

'''
This bristoprint module enables contacts to print to printers, plotters and
other devices via QPrintDialog.
'''

# Imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import *
import datetime


class PrintServices:

    '''
    The PrintServices class in contacts provides all the resources required
    for print information in contacts.
    '''
    def __init__(self, parent=None):
        '''
        This initialization class method initializes
        contacts fields.
        '''
        #Date and Time
        self._DATE = datetime.datetime.now()
        self._TODAY = self._DATE.strftime("%m/%d/%y %I:%M%p")



    def print_users_contacts(self,  _contacts, _grprpt):

        '''
        print_users_contacts prints all the contacts in memory within
        the query limit.

        _contacts - python list of contacts to print queried from db
        _grprpt - group name is group query or if null then skipped.
        '''
        _COMPANY = 1
        _FNAME = 3
        _LNAME = 5
        _CRED = 6
        _ADDR = 7
        _SUITE = 8
        _CITY = 9
        _ST = 10
        _POSTAL = 11
        _OPHONE = 12
        _OEMAIL = 15

        if len(_contacts) > 0:

            # Setup printer
            doc = ''
            bristoprint = QPrintDialog()
            if bristoprint.exec_() == QPrintDialog.Accepted:
                # begin printing to printer line by line
                qtxtedit = QTextEdit()
                qtxtedit.setFontPointSize(12.0)
                doc = 'bristoSOFT Contacts v. 0.1    ' +self._TODAY+'\n\r'
                if _grprpt:
                    doc = doc + _grprpt+'\n\r'
                for x in range(len(_contacts)):
                    if not _contacts[x][_SUITE]:
                        doc = doc + _contacts[x][_FNAME]\
                        + ' '+ _contacts[x][_LNAME]+'\n'\
                        + _contacts[x][_CRED]+'\n'\
                        + _contacts[x][_COMPANY]+'\n'\
                        + _contacts[x][_ADDR]+'\n'\
                        + _contacts[x][_CITY]\
                        + ', '+ _contacts[x][_ST]\
                        + '  '+ _contacts[x][_POSTAL]+'\n'\
                        + _contacts[x][_OPHONE]+'\n'\
                        + _contacts[x][_OEMAIL]+'\n\r'
                    else:
                        doc = doc + _contacts[x][_FNAME]\
                        + ' '+ _contacts[x][_LNAME]+'\n'\
                        + _contacts[x][_CRED]+'\n'\
                        + _contacts[x][_COMPANY]+'\n'\
                        + _contacts[x][_ADDR]+'\n'\
                        + _contacts[x][_SUITE]+'\n'\
                        + _contacts[x][_CITY]\
                        + ', '+ _contacts[x][_ST]\
                        + '  '+ _contacts[x][_POSTAL]+'\n'\
                        + _contacts[x][_OPHONE]+'\n'\
                        + _contacts[x][_OEMAIL]+'\n\r'
                qtxtedit.setText(doc)
                qtxtedit.print_(bristoprint.printer())
