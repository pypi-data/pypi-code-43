# Python modules
from __future__ import division

# 3rd party modules
import wx

# Our modules
import auto_gui.view_pulse_project as view_pulse_project
import dialog_referrers


class DialogViewPulseProject(view_pulse_project.MyDialog):
    """Displays the dialog for viewing a pulse_project in HTML"""
    def __init__(self, parent, pulse_project):
        if not parent:
            parent = wx.GetApp().GetTopWindow()

        view_pulse_project.MyDialog.__init__(self, parent) 
        
        self.pulse_project = pulse_project

        html_sizer = self.LabelHtmlPlaceholder.GetContainingSizer()
        parent = self.LabelHtmlPlaceholder.GetParent()
        self.LabelHtmlPlaceholder.Destroy()
        
        self.html_ctrl = wx.html.HtmlWindow(parent)
        
        html_sizer.Add(self.html_ctrl, 1, wx.EXPAND|wx.ALIGN_TOP)

        self.html_ctrl.SetPage(pulse_project.as_html())
        
        self.SetTitle("View Pulse Project %s" % pulse_project.name)

        self.SetSize( (500, 600) )

        self.Layout()

        self.Center()


    def on_show_referrers(self, event):
        dialog = dialog_referrers.DialogReferrers(self, self.pulse_project)
        dialog.ShowModal()
