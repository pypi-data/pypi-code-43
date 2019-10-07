#!/usr/bin/env python

# Python modules
from __future__ import division

# 3rd party modules
#import wx.aui as aui
import wx.lib.agw.aui as aui


class AUIManager(aui.AuiManager):
    """
    AUI Manager class
    """

    #----------------------------------------------------------------------
    def __init__(self, managed_window):
        """Constructor"""
        aui.AuiManager.__init__(self)
        self.SetManagedWindow(managed_window)