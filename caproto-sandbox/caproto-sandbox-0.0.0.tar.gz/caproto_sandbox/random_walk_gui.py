#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import os
#import pcaspy
#os.environ['PYEPICS_LIBCA'] = os.path.join(os.path.dirname(pcaspy.__file__), "ca.dll")

import epics
import wx
import epics.wx
from logging import debug,warn,info,error

__version__ = "0.0.0" #initial

class PanelTemplate(wx.Frame):

        title = "GUI Panel Template"

        def __init__(self):
            wx.Frame.__init__(self, None, wx.ID_ANY, title=self.title, style=wx.DEFAULT_FRAME_STYLE)
            self.panel=wx.Panel(self, -1, size = (200,75))
            self.Bind(wx.EVT_CLOSE, self.OnQuit)

            self.initialize_GUI()
            self.SetBackgroundColour(wx.Colour(255,255,255))
            self.Centre()
            self.Show()

        def OnQuit(self,event):
            """
            orderly exit of Panel if close button is pressed
            """
            self.Destroy()
            del self

        def initialize_GUI(self):
            """
            """
            sizer = wx.GridBagSizer(hgap = 5, vgap = 5)
            self.label ={}
            self.field = {}
            self.sizer = {}
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            topSizer = wx.BoxSizer(wx.VERTICAL)



            self.sizer[b'x'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b'x'] = wx.StaticText(self.panel, label= 'X value:', style = wx.ALIGN_CENTER)
            self.field[b'x'] = epics.wx.PVText(self.panel, pv='random_walk:x',minor_alarm = wx.Colour(5, 6, 7),auto_units = True)
            self.sizer[b'x'].Add(self.label[b'x'] , 0)
            self.sizer[b'x'].Add(self.field[b'x'] , 0)

            self.sizer[b't'] = wx.BoxSizer(wx.VERTICAL)
            self.label[b't'] = wx.StaticText(self.panel, label= 'Time of last update:', style = wx.ALIGN_CENTER)
            self.field[b't'] = epics.wx.PVText(self.panel, pv='random_walk:t',minor_alarm = wx.Colour(5, 6, 7),auto_units = True)
            self.sizer[b't'].Add(self.label[b't'] , 0)
            self.sizer[b't'].Add(self.field[b't'] , 0)


            main_sizer.Add(self.sizer[b'x'],0)
            main_sizer.Add(self.sizer[b't'],0)


            self.Center()
            self.Show()
            topSizer.Add(main_sizer,0)


            self.panel.SetSizer(topSizer)
            topSizer.Fit(self)
            self.Layout()
            self.panel.Layout()
            self.panel.Fit()
            self.Fit()

if __name__ == '__main__':
    from pdb import pm
    import logging
    from tempfile import gettempdir

    app = wx.App(redirect=False)
    panel = PanelTemplate()

    app.MainLoop()
