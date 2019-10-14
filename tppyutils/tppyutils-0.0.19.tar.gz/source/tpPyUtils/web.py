#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utility functions related with email
"""

import email
import smtplib


class Email(object):
    """
    Base class that represents an email
    """

    def __init__(self, user=None, password=None):
        super(Email, self).__init__()

        self.user = user
        self.password = password
        self.emails_list = list()
        self.server = None

        self._setup_message()

    # region Public Functions
    def set_subject(self, subject):
        self.message['Subject'] = subject

    def add_message(self, text):
        self.message.attach(email.MIMEText(text))

    def send(self, emails_list):
        joined = email.Utils.COMMASPACE.join(emails_list)
        self.message['To'] = joined
        self._setup_server()

        if self.server:
            self.server.sendemail(self.user, emails_list, self.message.as_string())
            self.server.quit()
    # endregion

    # region Private Functions
    def _setup_message(self):
        self.message = email.MIMEMultipart.MIMEMultipart()
        self.message['From'] = self.user
        self.message['Subject'] = ''
        self.message['To'] = list()

    def _setup_server(self):
        self.server = smtplib.SMTP()
        self.server.set_debuglevel(1)
    # endregion


class Gmail(Email, object):
    def __init__(self, user=None, password=None):
        super(Gmail, self).__init__(user=user, password=password)

    # region Override Functions
    def _setup_server(self):
        super(Gmail, self)._setup_server()

        smtp_host = 'smtp.gmail.com'
        smtp_port = 587

        self.server.connect(smtp_host, smtp_port)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.user, self.password)
    # endregion


class LocalHost(Email, object):
    def __init__(self, user):
        super(LocalHost, self).__init__(user=user, password='')

    # region Override Functions
    def _setup_server(self):
        self.server = smtplib.SMTP('localhost')
    # endregion


def open_web(url):
    """
    Open given web URL in user web browser
    :param url: str
    """

    webbrowser.open(url)
