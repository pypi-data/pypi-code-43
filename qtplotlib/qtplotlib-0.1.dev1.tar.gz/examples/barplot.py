#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from qtplotlib.barplot import QBarPlot

from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = QBarPlot()
    #widget.data = (10, 20, 30, 5, 15)
    widget.data = (8, None, 7, 5, -5, 6)
    widget.data_color = ("green", None, "yellow", None, "red", "yellow")
    widget.title = "Hello"
    widget.hlines = (1, -2, 10)
    widget.ymin = -2

    widget.show()

    # The mainloop of the application. The event handling starts from this point.
    # The exec_() method has an underscore. It is because the exec is a Python keyword. And thus, exec_() was used instead.
    exit_code = app.exec_()

    # The sys.exit() method ensures a clean exit.
    # The environment will be informed, how the application ended.
    sys.exit(exit_code)
