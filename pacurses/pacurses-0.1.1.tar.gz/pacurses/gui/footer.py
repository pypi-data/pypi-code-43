from urwid import AttrMap, Button, Divider, ExitMainLoop, GridFlow, Pile

from pacurses.constants.button_names import ButtonNames
from pacurses.constants.menu_names import MenuNames
from pacurses.constants.palette_names import PaletteNames
from pacurses.gui.status import Status


class Footer(Pile):
    def __init__(self, width, button_list, switch_menu):
        self.switch_menu = switch_menu
        divider = Divider()
        line = Divider(u"―", top=1, bottom=1)
        status = Status(width)

        buttons = []

        if ButtonNames.BACK in button_list:
            buttons.append(
                self.design_button(
                    "Back", switch_menu, user_data=MenuNames.MAIN
                )
            )

        if ButtonNames.HELP in button_list:
            buttons.append(
                self.design_button(
                    "Help", switch_menu, user_data=MenuNames.HELP
                )
            )

        if ButtonNames.CLOSE in button_list:
            buttons.append(self.design_button("Close", self.exit))

        button_grid = GridFlow(buttons, 9, 2, 0, "center")

        super(Footer, self).__init__(
            [line, status, divider, button_grid, divider]
        )
        self.button_list_index = 3

    @property
    def button_list(self):
        return self.contents[self.button_list_index][0]

    def switch_menu_wrapper(self, _, menu_name):
        self.switch_menu(menu_name)

    def exit(self, _):
        raise ExitMainLoop()

    def design_button(self, label, callback, user_data=None):
        button = Button(label, callback, user_data)
        decorated_button = AttrMap(button, PaletteNames.REVERSED, "")
        return decorated_button

    def keypress(self, size, key):
        key = super(Footer, self).keypress(size, key)

        if key and key in "hl":
            step = 1 if key == "l" else -1

            try:
                self.focus.focus_position = self.focus.focus_position + step

            except IndexError:
                pass

        else:
            return key
