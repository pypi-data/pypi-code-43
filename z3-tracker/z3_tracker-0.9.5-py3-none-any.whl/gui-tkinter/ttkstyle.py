'''
TTK style settings
'''

import tkinter.ttk as ttk

from .config import CONFIG

__all__ = 'init',


def init() -> None:
    '''
    Initialise ttk style.
    '''

    style = ttk.Style()
    style.configure('.', font=('Arial', CONFIG['font_size']))
