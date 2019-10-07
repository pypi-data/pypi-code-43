# Python modules
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party modules
import wx
import wx.html

# Our modules
import auto_gui.pulse_project_browser as gui_pulse_project_browser
import vespa.common.util.time_ as util_time
import vespa.common.util.xml_ as util_xml
import vespa.common.wx_gravy.util as wx_util


class DialogPulseProjectBrowser(gui_pulse_project_browser.PulseProjectBrowser):
    """Displays a dialog box that contains a list of pulse projects. 
    The list can be filtered by certain criteria and a preview of each 
    pulse project is given. The user is expected to choose a dialog 
    from the list.
    
    When the dialog closes, dialog.selected_pulse_project_id is set to 
    the id of the selected pulse project, or None if the user didn't 
    choose a pulse project.
    """
    def __init__(self, parent, db):
        self.selected_pulse_project_id = None
        
        if not parent:
            parent = wx.GetApp().GetTopWindow()

        gui_pulse_project_browser.PulseProjectBrowser.__init__(self, parent)
        
        self.db = db
        
        html_sizer = self.LabelHtml.GetContainingSizer()
        parent = self.LabelHtml.GetParent()
        self.LabelHtml.Destroy()
        
        self.html_ctrl = wx.html.HtmlWindow(parent)
        html_sizer.Add(self.html_ctrl, 1, wx.EXPAND|wx.ALIGN_TOP)
        self.html_ctrl.SetBackgroundColour(self.GetBackgroundColour())
        
        # We add the Open & Cancel buttons dynamically so that they're in the 
        # right order under OS X, GTK, Windows, etc.
        self.ButtonOpen, self.ButtonCancel = \
            wx_util.add_ok_cancel(self, self.LabelOpenCancelPlaceholder,
                                  self.on_open, ok_text="Open")

        self.populate_list()
        
        self.SetSize( (620, 400) )
        
        self.Layout()
        
        self.Center()
        
        # Under OS X & Linux, the focus is elsewhere (?) unless I manually
        # set it to the list 
        self.ListPulseProjects.SetFocus()   
        

    def on_open(self, event):
        index = self.ListPulseProjects.GetSelection()
        
        if index != wx.NOT_FOUND:
            self.selected_pulse_project_id = self.pulse_projects[index].id
        
            self.Close()        
        else:
            pass
            # On the Mac, a click on an empty listbox row doesn't generate
            # a click event but it does set the current selection to 
            # wx.NOT_FOUND (ouch). Therefore, it's possible (on the Mac,
            # at least), to get this dialog in a state where the open 
            # button is enabled but nothing is selected.
        
        
    def on_filter_change(self, event):
        self.populate_list()

        
    def on_list_click(self, event):
        index = self.ListPulseProjects.GetSelection()
        
        if index != wx.NOT_FOUND:
            pulse_project = self.pulse_projects[index]
        else:
            pulse_project = None

        self.item_selected(pulse_project)
        
        
    def on_list_double_click(self, event):
        index = self.ListPulseProjects.GetSelection()
        
        if index != wx.NOT_FOUND:
            self.selected_pulse_project_id = self.pulse_projects[index].id
        
            self.Close()        
        #else:
            # On the Mac, a click on an empty listbox row doesn't generate
            # a click event but it does set the current selection to 
            # wx.NOT_FOUND (ouch). Therefore, it's possible (on the Mac,
            # at least), to get this dialog in a state where the open 
            # button is enabled but nothing is selected.
                
        
    def item_selected(self, pulse_project=None):
        """To be called when an item is selected"""
        # Build a small HTML document using ElementTree. Using ElementTree is
        # a little more cumbersome than assembling ordinary strings, but 
        # it eliminates bugs related to improperly escaped HTML.
        html = ElementTree.Element("html")
        body = ElementTree.SubElement(html, "body")
        if pulse_project:
            # Format the created timestamp to make it easier to read
            created = pulse_project.created
            created = created.strftime(util_time.DISPLAY_TIMESTAMP_FORMAT)

            lines = ( ("Name", pulse_project.name), 
                      ("Creator", pulse_project.creator), 
                      ("Comment", pulse_project.comment), 
                      ("Is public", "%s" % pulse_project.is_public), 
                      ("Is frozen", "%s" % pulse_project.is_frozen), 
                      ("Created", created),  
                    )
                    
            for line in lines:
                description, data = line
                p = ElementTree.SubElement(body, "p")
                b = util_xml.TextSubElement(p, "b", description + ": ")
                b.tail = data

        html = ElementTree.tostring(html)
        self.html_ctrl.SetPage(html)

        # I can set the HTML control's background color during init, but
        # the control forgets that info every time I call SetPage() so I
        # have to reset it here.
        self.html_ctrl.SetBackgroundColour(self.GetBackgroundColour())

        
    def populate_list(self):
        # Clear the current selection's preview
        self.item_selected(None)
            
        self.pulse_projects = self.db.fetch_pulse_project_previews()
        
        # Populate the listbox
        names = [pulse_project.name for pulse_project in self.pulse_projects]
        self.ListPulseProjects.Set(names)

        # FIXME PS -- it'd be nice to set the background color on frozen
        # items, but that doesn't work with a regular wx.Listbox. We would
        # need to switch to a wx.ListCtrl.
        # frozen_color = wx.Colour(*common_constants.FROZEN_COLOR)
        # for i, pulse_project in enumerate(self.pulse_projects):
        #     if pulse_project.is_public or pulse_project.is_frozen:
        #         self.ListPulseProjects.SetItemBackgroundColour(i, frozen_color)
        
        self.ButtonOpen.Enable(bool(names))

        if names:
            # Select the first item
            self.ListPulseProjects.SetSelection(0)
            self.item_selected(self.pulse_projects[0])
                        
        
        
        
