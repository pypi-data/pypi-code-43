# -*- coding: utf-8 -*-
"""
**Mapping Learning application (GUI)**


"""
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication

from maplearn.app.gui.gui import Gui
from maplearn import logger

def main():
    """
    Run the application with GUI
    """
    logger.info('maplearn Gui starting...')
    # configuration
    app = QApplication(sys.argv)
    window = QMainWindow()
    gui = Gui(window)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()