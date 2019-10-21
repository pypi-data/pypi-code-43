from pacurses.constants.menu_names import MenuNames
from pacurses.gui.menus.default import DefaultMenu
from pacurses.gui.menus.help import HelpMenu
from pacurses.gui.menus.main import MainMenu
from pacurses.gui.menus.mute import MuteMenu
from pacurses.gui.menus.volume import VolumeMenu

_menu_mapping = {
    MenuNames.MAIN: MainMenu,
    MenuNames.VOLUME: VolumeMenu,
    MenuNames.MUTE: MuteMenu,
    MenuNames.DEFAULT: DefaultMenu,
    MenuNames.HELP: HelpMenu,
}


def get_menu(name):
    if name not in _menu_mapping.keys():
        raise Exception("Invalid menu name: {0}".format(name))

    return _menu_mapping[name]
