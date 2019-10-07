# Python modules
from __future__ import division

# 3rd party modules
import wx

# Our modules
import vespa.common.menu as common_menu
import vespa.common.util.config as util_common_config


class ViewIds(common_menu.IdContainer):
    # This one-off class is a container for the ids of all of the menu items
    # to which I need explicit references.
    ZERO_LINE_SHOW = common_menu.IdContainer.PLACEHOLDER

    XAXIS_SHOW = common_menu.IdContainer.PLACEHOLDER
    # FIXME PS - temporarily disabling PPM/kHz 
    # ref: http://scion.duhs.duke.edu/vespa/rfpulse/ticket/10
    # XAXIS_PPM = common_menu.IdContainer.PLACEHOLDER
    # XAXIS_KILOHERTZ = common_menu.IdContainer.PLACEHOLDER

    DATA_TYPE_REAL = common_menu.IdContainer.PLACEHOLDER
    DATA_TYPE_REAL_IMAGINARY = common_menu.IdContainer.PLACEHOLDER

    VIEW_TO_PNG = common_menu.IdContainer.PLACEHOLDER
    VIEW_TO_SVG = common_menu.IdContainer.PLACEHOLDER
    VIEW_TO_EPS = common_menu.IdContainer.PLACEHOLDER
    VIEW_TO_PDF = common_menu.IdContainer.PLACEHOLDER


# When main creates the menu bar it sets the variable below to that instance. 
# It's a convenience. It's the same as wx.GetApp().GetTopWindow().GetMenuBar(),
# but much easier to type.
bar = None


class RFPulseMenuBar(common_menu.VespaMenuBar):
    def __init__(self, main):
        common_menu.VespaMenuBar.__init__(self, main)
        
        ViewIds.init_ids()

        # _get_menu_data() is called just once, right here. 
        pulse_project, transformations, manage, view, help = _get_menu_data(main)

        # Build the top-level menus that are always present. 
        pulse_project = common_menu.create_menu(main, "&Pulse Project", pulse_project)
        transformations = common_menu.create_menu(main, "Add &Transformations", transformations)
        manage = common_menu.create_menu(main, "&Management", manage)
        view = common_menu.create_menu(main, "&View", view)
        help = common_menu.create_menu(main, "&Help", help)

        for menu in (pulse_project, transformations, manage, view, help):
            self.Append(menu, menu.label)

        ViewIds.enumerate_booleans(self.view_menu)


def _get_menu_data(main):
    # Note that wx treats the ids wx.ID_EXIT and wx.ID_ABOUT specially by 
    # moving them to their proper location on the Mac. wx will also change
    # the text of the ID_EXIT item to "Quit" as is standard under OS X. 
    # Quit is also the standard under Gnome but unfortunately wx doesn't seem
    # to change Exit --> Quit there, so our menu looks a little funny under
    # Gnome.
    
    pulseproj = (
                    ("N&ew\tCTRL+N",  main.on_new_pulse_project),
                    ("Copy &Tab to New\tCTRL+T", main.on_copy_pulse_project_tab),                     
                    ("O&pen\tCTRL+O", main.on_open_pulse_project),
                    common_menu.SEPARATOR,
                    ("R&un\tCTRL+R", main.on_run_pulse_project),
                    ("S&ave\tCTRL+S", main.on_save_pulse_project),
                    # Ctrl+Shift+S is the preferred accelerator for Save As
                    # under OS X and GTK. Microsoft doesn't provide one at
                    # all. For consistency, we'll leave off the accelerator.
                    ("Save A&s", main.on_save_as_pulse_project),
                    ("Close\tCTRL+W", main.on_close_pulse_project),
                    common_menu.SEPARATOR,
                    ("Third Party Export...", main.on_third_party_export),
                    common_menu.SEPARATOR,
                    ("Exit",          main.on_self_close, wx.ITEM_NORMAL, wx.ID_EXIT)
                )

    manage = (
                ("Manage &Pulse Projects",      main.on_manage_pulse_projects),
                ("Manage &Machine Settings Templates", main.on_manage_machine_settings_templates)
             )    

    transformations = (
                    ("Create", (
                        ("SLR",         main.on_create_slr),
                        ("Hyperbolic-Secant", main.on_create_hyperbolic_secant),
                        ("Gaussian", main.on_create_gaussian),
                        ("Randomized", main.on_create_randomized),
                        ("Import from File", main.on_create_import),
                         )),
                    common_menu.SEPARATOR,
                    ("Interpolation and Re-Scaling", main.on_ir),
                    ("Optimal Control (Non-Selective)", main.on_optimal_control_nonselective),
                )

    view = (
            ("Show Zero Line", main.on_menu_view_option, wx.ITEM_CHECK, ViewIds.ZERO_LINE_SHOW),
            ("X-Axis", (
                ("Show", main.on_menu_view_option, wx.ITEM_CHECK, ViewIds.XAXIS_SHOW),
                # FIXME PS - temporarily disabling PPM/kHz 
                # ref: http://scion.duhs.duke.edu/vespa/rfpulse/ticket/10
                # common_menu.SEPARATOR,
                # ("[mm]", main.on_menu_view_option, wx.ITEM_RADIO, ViewIds.XAXIS_PPM),
                # ("[kHz]", main.on_menu_view_option, wx.ITEM_RADIO, ViewIds.XAXIS_KILOHERTZ)
                )
            ),
            ("Data Type", (
                ("Real",            main.on_menu_view_option, wx.ITEM_RADIO, ViewIds.DATA_TYPE_REAL),
                ("Real+Imaginary",  main.on_menu_view_option, wx.ITEM_RADIO, ViewIds.DATA_TYPE_REAL_IMAGINARY))),
            common_menu.SEPARATOR,
            ("Output", (
                ("Plot to PNG", main.on_menu_view_output, wx.ITEM_NORMAL, ViewIds.VIEW_TO_PNG),
                ("Plot to SVG", main.on_menu_view_output, wx.ITEM_NORMAL, ViewIds.VIEW_TO_SVG),
                ("Plot to EPS", main.on_menu_view_output, wx.ITEM_NORMAL, ViewIds.VIEW_TO_EPS),
                ("Plot to PDF", main.on_menu_view_output, wx.ITEM_NORMAL, ViewIds.VIEW_TO_PDF)),
            )
           )

    help = [
                ("&User Manual",          main.on_user_manual),
                ("&RFPulse Help Online",  main.on_rfpulse_help_online),
                ("&Vespa Help Online",    main.on_vespa_help_online),
                ("&About", main.on_about, wx.ITEM_NORMAL, wx.ID_ABOUT),
           ]

    if util_common_config.VespaConfig().show_wx_inspector:
        help.append(common_menu.SEPARATOR)
        help.append( ("Show Inspection Tool", main.on_show_inspection_tool) )

    return (pulseproj, transformations, manage, view, help)


