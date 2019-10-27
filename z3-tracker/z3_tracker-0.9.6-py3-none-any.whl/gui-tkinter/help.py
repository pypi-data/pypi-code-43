'''
Help window
'''

import importlib
import tkinter as tk
import tkinter.ttk as ttk

from ..config import CONFIG
common = importlib.import_module(
    '..gui-common.maps', package=__package__)
BUTTONTYPE = common.BUTTONTYPE

from .maps import make_symbol_coordinates
from . import misc

__all__ = 'HelpWindow',


class HelpWindow(tk.Toplevel):
    '''
    Help window
    '''

    def __init__(self):
        super().__init__()

        self.title('Help')
        self.frame = ttk.Frame(self)
        self.frame.grid(sticky=misc.A)
        self.widgets = []

        self.leftframe = ttk.Frame(self)
        self.leftframe.grid(column=0, row=0, sticky=misc.A)
        self.middleframe = ttk.Frame(self)
        self.middleframe.grid(column=1, row=0, sticky=misc.A)
        self.rightframe = ttk.Frame(self)
        self.rightframe.grid(column=2, row=0, sticky=misc.A)

        self._item_buttons()
        self._dungeon_buttons()
        self._entrance_buttons()
        self._map_control()

    def _item_buttons(self) -> None:
        '''
        Item colours
        '''

        widget = ttk.LabelFrame(self.leftframe, text='Item locations')
        widget.grid(column=0, row=0, sticky=tk.N+tk.E+tk.W)
        shape = -7, -7, 7, 7
        loc = make_symbol_coordinates((16, 16), shape, 1)

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=0, sticky=misc.A)
        button = canvas.create_oval(*loc)
        canvas.itemconfigure(
            button, 
            activefill=BUTTONTYPE['standard']['colours']['available']['active'],
            fill=BUTTONTYPE['standard']['colours']['available']['normal'])
        text = ttk.Label(widget, text='Available')
        text.grid(column=1, row=0, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=1, sticky=misc.A)
        button = canvas.create_oval(*loc)
        canvas.itemconfigure(
            button,
            activefill=BUTTONTYPE['standard']['colours']['indirect']['active'],
            fill=BUTTONTYPE['standard']['colours']['indirect']['normal'])
        text = ttk.Label(
            widget, text='Available, requires finishing dungeon(s)')
        text.grid(column=1, row=1, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=2, sticky=misc.A)
        button = canvas.create_oval(*loc)
        canvas.itemconfigure(
            button,
            activefill=BUTTONTYPE['standard']['colours']['maybe']['active'],
            fill=BUTTONTYPE['standard']['colours']['maybe']['normal'])
        text = ttk.Label(widget, text='Possibly available')
        text.grid(column=1, row=2, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=3, sticky=misc.A)
        button = canvas.create_oval(*loc)
        canvas.itemconfigure(
            button, 
            activefill=BUTTONTYPE['standard']['colours']['checked']['active'],
            fill=BUTTONTYPE['standard']['colours']['checked']['normal'])
        text = ttk.Label(widget, text='Already checked')
        text.grid(column=1, row=3, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=4, sticky=misc.A)
        button = canvas.create_oval(*loc)
        canvas.itemconfigure(
            button, 
            activefill=BUTTONTYPE[
                'standard']['colours']['unavailable']['active'],
            fill=BUTTONTYPE['standard']['colours']['unavailable']['normal'])
        text = ttk.Label(widget, text='Unavailable')
        text.grid(column=1, row=4, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=5, sticky=misc.A)
        button = canvas.create_oval(*loc)
        canvas.itemconfigure(
            button, 
            activefill=BUTTONTYPE['standard']['colours']['visible']['active'],
            fill=BUTTONTYPE['standard']['colours']['visible']['normal'])
        text = ttk.Label(widget, text='Unavailable, but visible')
        text.grid(column=1, row=5, sticky=tk.W)
        self.widgets.extend((canvas, widget))

    def _dungeon_buttons(self) -> None:
        '''
        Dungeon colours
        '''

        widget = ttk.LabelFrame(self.leftframe, text='Dungeon locations')
        widget.grid(column=0, row=1, sticky=tk.N+tk.E+tk.W)
        shape = -13, -13, 13, 13
        loc = make_symbol_coordinates((16, 16), shape, 1)

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=0, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['available']['normal'])
        text = ttk.Label(widget, text='Entirely available')
        text.grid(column=1, row=0, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=1, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['indirect']['normal'])
        text = ttk.Label(
            widget, text='Available, requires finishing dungeon(s)')
        text.grid(column=1, row=1, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=2, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['maybe']['normal'])
        text = ttk.Label(widget, text='Available if accessible')
        text.grid(column=1, row=2, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=3, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['checked']['normal'])
        text = ttk.Label(widget, text='Fully checked')
        text.grid(column=1, row=3, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=4, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['unavailable']['normal'])
        text = ttk.Label(widget, text='All unavailable')
        text.grid(column=1, row=4, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=5, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['visible']['normal'])
        text = ttk.Label(widget, text='Possibly or partially available')
        text.grid(column=1, row=5, sticky=tk.W)
        self.widgets.extend((canvas, widget))

    def _entrance_buttons(self):
        '''
        Entrance button colours
        '''

        widget = ttk.LabelFrame(self.middleframe, text='Entrances')
        widget.grid(column=0, row=0, sticky=tk.N)
        shape = -5, -5, 5, 5
        loc = make_symbol_coordinates((16, 16), shape, 1)

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=0, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['available']['active'],
            outline='white', width=3)
        text = ttk.Label(widget, text='Entrance leads to default location')
        text.grid(column=1, row=0, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=1, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['available']['active'],
            outline='red', width=3)
        text = ttk.Label(widget, text='Selected entrance leads here')
        text.grid(column=1, row=1, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=2, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['available']['active'],
            outline='yellow', width=3)
        text = ttk.Label(
            widget, text='This entrance leads to selected location')
        text.grid(column=1, row=2, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=3, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['available']['active'],
            outline='orange', width=3)
        text = ttk.Label(
            widget,
            text='Entrances are switched between this and selected location')
        text.grid(column=1, row=3, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=4, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['available']['active'],
            outline='blue', width=3)
        text = ttk.Label(
            widget,
            text='This entrance leads to same interior as selected one.')
        text.grid(column=1, row=4, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=5, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['available']['active'],
            outline='magenta', width=3)
        text = ttk.Label(
            widget,
            text='Combination of red and blue.')
        text.grid(column=1, row=5, sticky=tk.W)
        self.widgets.extend((canvas, widget))

        canvas = tk.Canvas(widget, height=32, width=32)
        canvas.grid(column=0, row=6, sticky=misc.A)
        button = canvas.create_rectangle(*loc)
        canvas.itemconfigure(
            button,
            fill=BUTTONTYPE['standard']['colours']['available']['active'],
            outline='cyan', width=3)
        text = ttk.Label(
            widget,
            text='Combination of yellow and blue.')
        text.grid(column=1, row=6, sticky=tk.W)
        self.widgets.extend((canvas, widget))

    def _map_control(self) -> None:
        '''
        Map controls
        '''

        widget = ttk.LabelFrame(self.rightframe, text='Entrance map control')
        widget.grid(column=0, row=0, sticky=tk.N)

        button = ttk.Label(widget, text='Left-click:')
        button.grid(column=0, row=0, sticky=misc.A)
        spacer = ttk.Label(widget, width=1)
        spacer.grid(column=1, row=0, sticky=misc.A)
        text = ttk.Label(widget, text='Mark and unmark locations as checked')
        text.grid(column=2, row=0, sticky=tk.W)

        button = ttk.Label(widget, text='Middle-click:')
        button.grid(column=0, row=1, sticky=misc.A)
        spacer = ttk.Label(widget, width=1)
        spacer.grid(column=1, row=1, sticky=misc.A)
        text = ttk.Label(widget, text='Link entrance to location')
        text.grid(column=2, row=1, sticky=tk.W)

        button = ttk.Label(widget, text='Right-click:')
        button.grid(column=0, row=2, sticky=misc.A)
        spacer = ttk.Label(widget, width=1)
        spacer.grid(column=1, row=2, sticky=misc.A)
        text = ttk.Label(widget, text='Abort linking or unlink location')
        text.grid(column=2, row=2, sticky=tk.W)

    def reset(self) -> None:
        '''
        Dummy method
        '''

        pass


def start(*args) -> tk.Toplevel:
    '''
    Open help window.

    Returns:
        tk.Toplevel: help window
    '''

    return HelpWindow()
