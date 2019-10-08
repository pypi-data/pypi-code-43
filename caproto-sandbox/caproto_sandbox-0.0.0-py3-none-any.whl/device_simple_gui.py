#!/usr/bin/env python3
#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import epics
import epics.wx
from logging import debug,warn,info,error


import wx

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

            self.sizer[b'cpu'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b'cpu'] = wx.StaticText(self.panel, label= 'CPU', style = wx.ALIGN_CENTER)
            self.field[b'cpu'] = epics.wx.PVText(self.panel, pv='simple:CPU',minor_alarm = wx.Colour(5, 6, 7),auto_units = True)
            self.sizer[b'cpu'].Add(self.label[b'cpu'] , 0)
            self.sizer[b'cpu'].Add(self.field[b'cpu'] , 0)

            self.sizer[b'memory'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b'memory'] = wx.StaticText(self.panel, label= 'Memory', style = wx.ALIGN_CENTER)
            self.field[b'memory'] = epics.wx.PVText(self.panel, pv='simple:MEMORY',minor_alarm = wx.Colour(5, 6, 7),auto_units = True)
            self.sizer[b'memory'].Add(self.label[b'memory'] , 0)
            self.sizer[b'memory'].Add(self.field[b'memory'] , 0)

            self.sizer[b'battery'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b'battery'] = wx.StaticText(self.panel, label= 'Battery', style = wx.ALIGN_CENTER)
            self.field[b'battery'] = epics.wx.PVText(self.panel, pv='simple:BATTERY',minor_alarm = wx.Colour(5, 6, 7),auto_units = True)
            self.sizer[b'battery'].Add(self.label[b'battery'] , 0)
            self.sizer[b'battery'].Add(self.field[b'battery'] , 0)

            self.sizer[b'time'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b'time'] = wx.StaticText(self.panel, label= 'Time', style = wx.ALIGN_CENTER)
            self.field[b'time'] = epics.wx.PVText(self.panel, pv='random_walk:x',minor_alarm = wx.Colour(5, 6, 7),auto_units = True)
            self.sizer[b'time'].Add(self.label[b'time'] , 0)
            self.sizer[b'time'].Add(self.field[b'time'] , 0)


            main_sizer.Add(self.sizer[b'cpu'],0)
            main_sizer.Add(self.sizer[b'memory'],0)
            main_sizer.Add(self.sizer[b'battery'],0)
            main_sizer.Add(self.sizer[b'time'],0)



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
