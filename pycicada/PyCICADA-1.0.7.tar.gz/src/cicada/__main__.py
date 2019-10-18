from cicada.gui.cicada_main_window import CicadaMainWindow
from cicada.gui.cicada_config_handler import ConfigHandler
import sys
import platform
from qtpy.QtWidgets import *
import os


app = QApplication(sys.argv)

# set the environment variable to use a specific wrapper
# it can be set to PyQt, PyQt5, PySide or PySide2 (not implemented yet)
# os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'

# dark_style_style_sheet = qdarkstyle.load_stylesheet_from_environment(is_pyqtgraph=True)
# from package qdarkstyle, modified css
my_path = os.path.abspath(os.path.dirname(__file__))
if platform.system() == "Windows":
	to_insert = os.path.join(my_path, "gui/icons/")
	to_insert = to_insert.replace("\\", "/")
else:
	to_insert = os.path.join(my_path, "gui/icons/")
	
file_name = os.path.join(my_path, "gui/cicada_qdarkstyle.css")
# with open(file_name, "w", encoding='UTF-8') as file:
#     file.write(dark_style_style_sheet)
with open(file_name, "r", encoding='UTF-8') as file:
    dark_style_cicada_style_sheet = file.read()

dark_style_cicada_style_sheet = dark_style_cicada_style_sheet.replace("icons/", to_insert)
app.setStyleSheet(dark_style_cicada_style_sheet)

config_handler = ConfigHandler()

cicada_main_window = CicadaMainWindow(config_handler=config_handler)

# putting the window at the center of the screen
# screenGeometry is an instance of Qrect
screenGeometry = QApplication.desktop().screenGeometry()
x = (screenGeometry.width() - cicada_main_window.width()) / 2
y = (screenGeometry.height() - cicada_main_window.height()) / 2
cicada_main_window.move(x, y)
cicada_main_window.show()

sys.exit(app.exec_())
