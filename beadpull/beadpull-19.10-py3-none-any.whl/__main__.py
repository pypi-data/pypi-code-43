import logging
import logging.config
import yaml
from sys import argv, exit
from os.path import dirname, join
from PyQt5 import QtWidgets
from beadpull.ui.window import MainWindow


def main():
    logging.config.dictConfig(
        yaml.load(
            open(join(dirname(__file__),
                      "logging.yaml"), "r"), Loader=yaml.FullLoader
        )
    )
    app = QtWidgets.QApplication(argv)
    MainWindow(dirname(__file__))
    exit(app.exec_())
