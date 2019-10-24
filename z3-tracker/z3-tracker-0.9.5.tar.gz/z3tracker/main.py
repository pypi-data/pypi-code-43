'''
Location map for Zelda 3
'''

from .config import CONFIG
from . import gui

__all__ = 'main',


def main() -> None:
    '''
    Main program.
    '''

    gui.GUI = gui.guilib.GraphicalInterface()
    gui.GUI.run()
