import signal

import oyaml as yaml
from PyQt5.QtCore import Qt
from yaml import Loader

import kamzik3
from kamzik3.snippets.snippetsWidgets import init_qt_app

app = init_qt_app()
app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

with open("conf_dummy_server.yml", "r") as configFile:
    config = yaml.load(configFile, Loader=Loader)

kamzik3.session.start_control_loops()

signal.signal(signal.SIGINT, signal.SIG_DFL)
config["session_window"].show()
app.exec_()

config["server"].close()
kamzik3.session.stop()
