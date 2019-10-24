'''
Program GUI
'''

import importlib
import os
import re
import threading
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as tkmbox
import tkinter.ttk as ttk
import typing

from ..config import CONFIGDIRECTORY, CONFIG
common = importlib.import_module(
    '..gui-common.interface', package=__package__)
from .. import update
from .. import version

from . import config
from . import dark
from . import dungeons
from . import environ
from . import help
from . import items
from . import light
from . import misc
from . import ttkstyle

__all__ = 'GraphicalInterface',


class GraphicalInterface(tk.Tk):
    '''
    Main access point for everything GUI related.

    Instance variables:
        _gui_root: tkinter framework root object
        _menu: main menu
        _buttons: buttons in menu
        _tracker: world state tracker
        _windows: collection of child windows
    '''

    def __init__(self):
        '''
        Initialise GUI.
        '''

        super().__init__()
        self.call('tk', 'scaling', 1)
        ttkstyle.init()
        self._init_menu()

        self._tracker = common.world_tracker()

        self._windows = {'menu': self}

        self._restore_windows()
        self._prepare_windows()
        self.protocol('WM_DELETE_WINDOW', self.quit)

        self._start_update_check()

    def _restore_windows(self) -> None:
        '''
        Restore previously stored window layout.
        '''

        layout = common.load_window_cache()
        for window in layout:
            if window not in self._windows and window in environ.WINDOWLIST:
                self._start_window(window)
            if window in self._windows:
                self._windows[window].geometry(
                    '+{0:d}+{1:d}'.format(*layout[window]))

    def _start_window(self, identifier: str) -> None:
        '''
        Initialise a window.

        Args:
            identifier: name of window to open
        '''

        if identifier == 'quit':
            self.quit()
            return
        if identifier == 'reset':
            self.reset()
            return
        if identifier == 'save':
            self.save()
            return
        if identifier == 'load':
            self.load()
            return
        if identifier in self._windows:
            self._windows[identifier].deiconify()
            return
        self._windows[identifier] = globals()[identifier].start(self._tracker)
        if identifier == 'config':
            self._windows[identifier].dungeondisplay = self._windows['dungeons']
        self._windows[identifier].protocol(
            'WM_DELETE_WINDOW', self._windows[identifier].withdraw)

    def run(self) -> None:
        '''
        Run main GUI loop.
        '''

        self.mainloop()

    def quit(self) -> None:
        '''
        Quit program.
        '''

        common.save_window_cache(self._window_layout())
        for window in self._windows:
            if window != 'menu':
                self._windows[window].withdraw()
        self._menu.quit()

    def _prepare_windows(self) -> None:
        '''
        Preload windows without displaying them.

        I don't really want to deal with the hassle of non-existing
        windows/trackers, so I do this.
        '''

        prepwindows = []
        for window in environ.WINDOWLIST:
            if window not in self._windows:
                prepwindows.append(window)
        for window in prepwindows:
            self._start_window(window)
        for window in prepwindows:
            self._windows[window].withdraw()

    def _open_window(self, window: str) -> None:
        '''
        Open a window.

        Args:
            window: name of existing window object
            creator: window creation routine
        '''

        try:
            self._windows[window].deiconify()
        except (AttributeError, tk.TclError):
            self._start_window(window)
        self._windows[window].protocol(
            'WM_DELETE_WINDOW', self._windows[window].withdraw)

    def _window_layout(self) -> dict:
        '''
        Return current position of all windows.

        Returns:
            dict: {window name: (x, y)}
        '''

        layout = {}
        for window in self._windows:
            if self._windows[window].state() == 'withdrawn':
                continue
            try:
                self._windows[window].deiconify()
            except (AttributeError, tk.TclError):
                continue
            layout[window] = tuple(
                int(c) for c in re.match(
                    '(\d+)x(\d+)\+-?(\d+)\+-?(\d+)',
                    self._windows[window].geometry()).groups()[2:])
        return layout

    def _init_menu(self) -> None:
        '''
        Create menu buttons.
        '''

        self.title('Menu')

        self._menu = ttk.Frame(self)
        self._menu.grid(column=0, row=0, sticky=misc.A)

        self._buttons = {
            'items': self._make_button('items', (0, 0), 'Items'),
            'dungeons': self._make_button('dungeons', (1, 0), 'Dungeons'),
            'light': self._make_button('light', (0, 1), 'Light World'),
            'dark': self._make_button('dark', (1, 1), 'Dark World'),
            'config': self._make_button('config', (0, 3), 'Settings'),
            'help': self._make_button('help', (1, 3), 'Help'),
            'save': self._make_button('save', (0, 4), 'Save'),
            'load': self._make_button('load', (1, 4), 'Load'),
            'reset': self._make_button('reset', (0, 5), 'Reset'),
            'quit': self._make_button('quit', (1, 5), 'Quit'),
            }

    def _make_button(
            self, identifier: str, loc: typing.Sequence[int],
            text: str or tk.StringVar) -> ttk.Button:
        '''
        Shortcut to place buttons.

        Args:
            identifier: name of button
            loc: (column, row) of button on 2D grid
            text: text to display on button

        Returns:
            ttk.Button: created button
        '''

        button = ttk.Button(
            self._menu, command=lambda: self._start_window(identifier))
        if isinstance(text, tk.StringVar):
            button.configure(textvariable=text)
        else:
            assert isinstance(text, str)
            button.configure(text=text)
        button.grid(column=loc[0], row=loc[1], sticky=tk.N+tk.W+tk.E)
        return button

    def reset(self) -> None:
        '''
        Reset tracker windows.
        '''

        check = tkmbox.askokcancel(
            'Reset', 'This will delete all stored progress.',
            default=tkmbox.CANCEL, icon=tkmbox.WARNING)
        if not check:
            return

        for window in self._windows:
            if window not in ('menu', 'config'):
                self._windows[window].reset()

        try:
            os.remove(os.path.join(CONFIGDIRECTORY, CONFIG['autosave']))
        except FileNotFoundError:
            pass

    def save(self) -> None:
        '''
        Save tracker state to file.
        '''

        savefile = filedialog.asksaveasfilename(
            defaultextension='.json', filetypes=(('JSON', '*.json'),),
            parent=self, title='Save to file')
        if not savefile:
            return
        with open(
                os.path.join(CONFIGDIRECTORY, CONFIG['autosave']), 'r') as src:
            with open(savefile, 'w') as dst:
                dst.write(src.read())

    def load(self) -> None:
        '''
        Load save file.
        '''

        loadfile = filedialog.askopenfilename(
            defaultextension='.json', filetypes=(('JSON', '*.json'),),
            parent=self, title='Load file')
        if not loadfile:
            return
        with open(
                os.path.join(CONFIGDIRECTORY, CONFIG['autosave']), 'w') as dst:
            with open(loadfile, 'r') as src:
                dst.write(src.read())
        tkmbox.showinfo('Load file', 'Please restart z3-tracker.')
        self.quit()

    def _start_update_check(self) -> None:
        '''
        Initiate update check.
        '''

        check = threading.Thread(
            target=self._update_check, name='Update checker', daemon=True)
        check.start()

    def _update_check(self) -> None:
        '''
        Check for updates.
        '''

        update_available = update.check_update_availability()
        if update_available:
            update_text='''Update available:
- current: {0:s}
- newest: {1:s}'''.format(version.__version__, update_available)
            update_frame = ttk.Frame(self)
            update_frame.grid(column=0, row=1, sticky=misc.A)
            update_label = ttk.Label(
                update_frame, text=update_text)
            update_label.grid(sticky=misc.A)
