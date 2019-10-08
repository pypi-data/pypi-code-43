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



            self.sizer[b't1'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b't1'] = wx.StaticText(self.panel, label= 't1:', style = wx.ALIGN_CENTER)
            self.field[b't1'] = epics.wx.PVText(self.panel, pv='io_device:t1',minor_alarm = wx.Colour(5, 6, 7),auto_units = True)
            self.sizer[b't1'].Add(self.label[b't1'] , 0)
            self.sizer[b't1'].Add(self.field[b't1'] , 0)

            self.sizer[b'dt1'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b'dt1'] = wx.StaticText(self.panel, label= 'dt1:', style = wx.ALIGN_CENTER)
            self.field[b'dt1'] = epics.wx.PVFloatCtrl(self.panel, pv='io_device:dt1')
            self.sizer[b'dt1'].Add(self.label[b'dt1'] , 0)
            self.sizer[b'dt1'].Add(self.field[b'dt1'] , 0)

            self.sizer[b't2'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b't2'] = wx.StaticText(self.panel, label= 't2:', style = wx.ALIGN_CENTER)
            self.field[b't2'] = epics.wx.PVText(self.panel, pv='io_device:t2',minor_alarm = wx.Colour(5, 6, 7),auto_units = True)
            self.sizer[b't2'].Add(self.label[b't2'] , 0)
            self.sizer[b't2'].Add(self.field[b't2'] , 0)

            self.sizer[b'dt2'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b'dt2'] = wx.StaticText(self.panel, label= 'dt2:', style = wx.ALIGN_CENTER)
            self.field[b'dt2'] = epics.wx.PVFloatCtrl(self.panel, pv='io_device:dt2')
            self.sizer[b'dt2'].Add(self.label[b'dt2'] , 0)
            self.sizer[b'dt2'].Add(self.field[b'dt2'] , 0)

            main_sizer.Add(self.sizer[b't1'],0)
            main_sizer.Add(self.sizer[b'dt1'],0)
            main_sizer.Add(self.sizer[b't2'],0)
            main_sizer.Add(self.sizer[b'dt2'],0)



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
