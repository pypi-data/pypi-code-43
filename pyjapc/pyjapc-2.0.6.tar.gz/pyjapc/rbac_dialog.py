# -*- coding: utf-8 -*-
"""A Tk-based password entry dialog for RBAC login.

LHC LLRF acquisition & commissioning software

Copyright (c) CERN 2015

This software is distributed under the terms of the GNU General Public Licence
version 3 (GPL Version 3).

In applying this licence, CERN does not waive the privileges and immunities
granted to it by virtue of its status as an Intergovernmental Organization or
submit itself to any jurisdiction.

:Authors:
  - Helga Timko, CERN BE-RF
"""

import six

if six.PY2:
    import Tkinter as tkinter
else:
    import tkinter


class PasswordEntryDialogue(object):
    """A class to setup the password entry dialog and handle the input.

    Args:
        master  (tkinter.Tk):    Parent Tk widget
        uName   (Optional[str]): Default text for for username field
        appName (Optional[str]): Optional application name to show in dialog
                                 title bar

    Attributes:
        by_location (bool): Login should be performed by location
        username (str): Username for login
        password (str): Password for login
    """
    def __init__(self, master, uName="", appName=""):
        self.by_location = False
        self.username = None
        self.password = None
        self.master = master

        # Define pop-up frame
        frame = tkinter.Frame(self.master, padx=10, pady=10)
        if appName == "":
            self.master.title("RBAC Login")
        else:
            self.master.title("RBAC Login - {0}".format(appName))
        frame.pack(fill=tkinter.BOTH, expand=True)

        # First entry: line user name
        self.entrytext1 = tkinter.StringVar()
        self.entrytext1.set(uName)
        label1 = tkinter.Label(frame, text="User Name:")
        label1.grid(row=0, column=0, padx=5, sticky="W")
        self.entry1 = tkinter.Entry(frame, bd=2, textvariable=self.entrytext1)
        self.entry1.grid(row=0, column=1, columnspan=3, sticky="WENS", pady=5)

        # Second entry line: password
        self.entrytext2 = tkinter.StringVar()
        label2 = tkinter.Label(frame, text="Password:")
        label2.grid(row=1, column=0, padx=5, sticky="W")
        self.entry2 = tkinter.Entry(frame, bd=2, show="*",
                                    textvariable=self.entrytext2)
        self.entry2.grid(row=1, column=1, columnspan=3, sticky="WENS", pady=5)
        self.entry2.focus_set()

        # Buttons
        button1 = tkinter.Button(frame, text="Login by Location",
                                 command=self.login_by_location)
        button1.grid(row=2, column=1, pady=5, padx=2)

        button2 = tkinter.Button(frame, text="OK",
                                 command=self.login_by_password)
        button2.grid(row=2, column=2, pady=5, padx=2)

        button3 = tkinter.Button(frame, text="Cancel",
                                 command=self.master.destroy)
        button3.grid(row=2, column=3, pady=5, padx=2)

        # Action at pressing enter
        self.master.bind('<Return>', self.login_by_password)

    def login_by_password(self, *args):
        """Sets username and password and destroys the dialogue box"""
        self.by_location = False
        self.username = self.entrytext1.get()
        self.password = self.entrytext2.get()
        if self.username == "":
            self.username = None
        if self.password == "":
            self.password = None
        self.master.destroy()

    def login_by_location(self):
        """Sets by_location to True and destroys the dialogue box"""
        self.by_location = True
        self.username = None
        self.password = None
        self.master.destroy()


def getPw(uName="", appName=""):
    """Function to create a Tk widget and show the password entry dialog.

    Args:
        uName   (Optional[str]): Default text for for username field
        appName (Optional[str]): Optional application name to show in dialog
                                 title bar

    Returns:
        tuple: A tuple containing (by_location [bool], username [str],
                                   password [str])
    """
    root = tkinter.Tk()
    app = PasswordEntryDialogue(root, uName, appName)
    root.mainloop()
    return (app.by_location, app.username, app.password)
