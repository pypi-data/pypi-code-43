#!/usr/bin/python3

"""
simple_plotter - simple 2d curve plotting front-end and numpy/matplotlib code generator
Copyright (C) 2018, 2019  Thies Hecker

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QFileDialog, QGridLayout, \
    QVBoxLayout, QWidget, QHBoxLayout, QGroupBox, QDialog, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from simple_plotter.code_generator import *
import faulthandler
faulthandler.enable()
import warnings
import pkg_resources
from setuptools_scm import get_version
from . import name


def check_valid_input(input_value):
    """Checks if an input value corresponds to a valid value - i.e. not None, "", "None",..."""

    if input_value is None or input_value == "" or input_value == "None":
        valid = False
    else:
        valid = True

    return valid


class GUI(QMainWindow):

    def __init__(self, data_handler, version):
        self.version = version
        self.ConstList = []
        self.xpos = []
        self.ypos = []
        self.data_handler = data_handler
        self.projectfile = 'project1.json'

        super().__init__()
        self.initUI()

    def initUI(self):
        """initialize the GUI elements
        """

        main_layout = QVBoxLayout()

        # hbox for action buttons
        group_actions = QGroupBox("Actions")
        layout_actions = QHBoxLayout()
        layout_actions.setSpacing(10)

        plotButton = QPushButton('Plot', self)
        saveButton = QPushButton('Save', self)
        loadButton = QPushButton('Load', self)
        exportButton = QPushButton('Export code', self)

        plotButton.clicked.connect(self.plotButClicked)
        saveButton.clicked.connect(self.saveButClicked)
        loadButton.clicked.connect(self.loadButClicked)
        exportButton.clicked.connect(self.exportButClicked)

        layout_actions.addWidget(plotButton)
        layout_actions.addWidget(saveButton)
        layout_actions.addWidget(loadButton)
        layout_actions.addWidget(exportButton)

        group_actions.setLayout(layout_actions)
        main_layout.addWidget(group_actions)

        # hbox for equation definition
        group_eq = QGroupBox("Equation")
        layout_eq = QHBoxLayout()
        layout_eq.setSpacing(10)

        self.leFormula = QLineEdit(self.data_handler.formula.equation, self)
        lblEq = QLabel('=', self)
        self.lefunctionName = QLineEdit(self.data_handler.formula.function_name, self)
        lblUnit = QLabel('Unit:', self)
        self.leFuncUnit = QLineEdit(self.data_handler.formula.function_unit, self)

        layout_eq.addWidget(self.lefunctionName, 0)
        layout_eq.addWidget(lblEq)
        layout_eq.addWidget(self.leFormula, 3)
        layout_eq.addWidget(lblUnit)
        layout_eq.addWidget(self.leFuncUnit)

        group_eq.setLayout(layout_eq)

        main_layout.addWidget(group_eq)

        # variable definition
        var_const_group = QGroupBox("Variable settings")

        layout_vardef = QGridLayout()
        layout_vardef.setSpacing(10)

        lblvarName = QLabel('Var. name:', self)
        layout_vardef.addWidget(lblvarName, 0, 0)

        self.levarName = QLineEdit(str(self.data_handler.formula.var_name), self)
        layout_vardef.addWidget(self.levarName, 1, 0)

        lblStartVal = QLabel('min:', self)
        layout_vardef.addWidget(lblStartVal, 0, 1)
        self.leStartVal = QLineEdit(str(self.data_handler.plot_data.start_val), self)
        layout_vardef.addWidget(self.leStartVal, 1, 1)

        lblEndVal = QLabel('max:', self)
        layout_vardef.addWidget(lblEndVal, 0, 2)
        self.leEndVal = QLineEdit(str(self.data_handler.plot_data.end_val), self)
        layout_vardef.addWidget(self.leEndVal, 1, 2)

        lblNoPts = QLabel('Data points:', self)
        self.leNoPts = QLineEdit(str(self.data_handler.plot_data.no_pts), self)
        layout_vardef.addWidget(lblNoPts, 0, 3)
        layout_vardef.addWidget(self.leNoPts, 1, 3)

        lblVarUnit = QLabel('Unit:', self)
        self.leVarUnit = QLineEdit(str(self.data_handler.formula.var_unit), self)
        layout_vardef.addWidget(lblVarUnit, 0, 4)
        layout_vardef.addWidget(self.leVarUnit, 1, 4)

        var_const_group.setLayout(layout_vardef)
        main_layout.addWidget(var_const_group)

        # constants
        group_constants = QGroupBox("Constants")
        layout_constants = QGridLayout()
        layout_constants.setSpacing(10)

        self.const_table = QTableWidget(0, 4)
        self.const_table.setHorizontalHeaderLabels(["Const. name", "Value", "Unit", "Comment"])
        addConstButton = QPushButton('Add', self)
        removeConstButton = QPushButton('Remove', self)

        layout_constants.addWidget(self.const_table, 1, 0, 5, 3)
        layout_constants.addWidget(addConstButton, 0, 0)
        layout_constants.addWidget(removeConstButton, 0, 1)
        layout_constants.setRowStretch(1, 1)

        addConstButton.clicked.connect(self.addConstClicked)
        removeConstButton.clicked.connect(self.removeConstClicked)

        group_constants.setLayout(layout_constants)

        main_layout.addWidget(group_constants)

        # curve set constants
        group_sets = QGroupBox("Curve set parameters")
        layout_sets = QGridLayout()

        lblsetvarName = QLabel('Curve set\nconstant:', self)
        self.lesetvarName = QLineEdit(str(self.data_handler.formula.set_var_name), self)
        lblsetStartVal = QLabel('min:', self)
        self.lesetStartVal = QLineEdit(str(self.data_handler.formula.set_min_val), self)
        lblsetEndVal = QLabel('max:', self)
        self.lesetEndVal = QLineEdit(str(self.data_handler.formula.set_max_val), self)
        lblsetNoPts = QLabel('No. of\ncurve sets:', self)
        self.lesetNoPts = QLineEdit(str(self.data_handler.formula.no_sets), self)
        lblsetUnit = QLabel('Unit:', self)
        self.leSetUnit = QLineEdit(str(self.data_handler.formula.set_var_unit), self)
        lblSetListValues = QLabel('Explicit set const. values:', self)
        self.leSetConstValues = QLineEdit(str(self.data_handler.formula.explicit_set_values), self)

        layout_sets.addWidget(lblsetvarName, 0, 0)
        layout_sets.addWidget(self.lesetvarName, 1, 0)
        layout_sets.addWidget(lblsetStartVal, 0, 1)
        layout_sets.addWidget(self.lesetStartVal, 1, 1)
        layout_sets.addWidget(lblsetEndVal, 0, 2)
        layout_sets.addWidget(self.lesetEndVal, 1, 2)
        layout_sets.addWidget(lblsetNoPts, 0, 3)
        layout_sets.addWidget(self.lesetNoPts, 1, 3)
        layout_sets.addWidget(lblsetUnit, 0, 4)
        layout_sets.addWidget(self.leSetUnit, 1, 4)
        layout_sets.addWidget(lblSetListValues, 2, 0)
        layout_sets.addWidget(self.leSetConstValues, 2, 1, 1, 5)

        self.leSetConstValues.textChanged.connect(self.explicit_set_const_values_changed)

        group_sets.setLayout(layout_sets)
        main_layout.addWidget(group_sets)

        # toggle buttons for plotting config
        group_plotconf = QGroupBox("Plot settings")
        layout_plotconf = QGridLayout()
        layout_plotconf.setSpacing(10)

        self.xscaleToggle = QPushButton('x = log', self)
        self.xscaleToggle.setCheckable(True)

        self.yscaleToggle = QPushButton('y = log', self)
        self.yscaleToggle.setCheckable(True)

        self.xySwapToggle = QPushButton('Swap XY', self)
        self.xySwapToggle.setCheckable(True)

        self.csvExpToggle = QPushButton('Add csv\nexp. code', self)
        self.csvExpToggle.setCheckable(True)

        self.gridToggle = QPushButton('Show\ngrid', self)
        self.gridToggle.setCheckable(True)

        lbl_ymin = QLabel('y min./max.:', self)
        self.le_ymin = QLineEdit(str(self.data_handler.plot_data.y_min), self)
        # lbl_ymax = QLabel('y max.:', self)
        self.le_ymax = QLineEdit(str(self.data_handler.plot_data.y_max), self)

        lbl_plot_title = QLabel('Plot title:')
        self.le_plot_title = QLineEdit(self.data_handler.plot_data.plot_title, self)

        layout_plotconf.addWidget(self.xscaleToggle, 0, 0)
        layout_plotconf.addWidget(self.yscaleToggle, 0, 1)
        layout_plotconf.addWidget(self.xySwapToggle, 0, 2)
        layout_plotconf.addWidget(self.gridToggle, 0, 3)
        layout_plotconf.addWidget(self.csvExpToggle, 0, 4)
        layout_plotconf.addWidget(lbl_ymin, 1, 0)
        layout_plotconf.addWidget(self.le_ymin, 1, 1)
        # layout_plotconf.addWidget(lbl_ymax, 1, 2)
        layout_plotconf.addWidget(self.le_ymax, 1, 2)
        layout_plotconf.addWidget(lbl_plot_title, 2, 0)
        layout_plotconf.addWidget(self.le_plot_title, 2, 1, 1, 3)

        group_plotconf.setLayout(layout_plotconf)
        main_layout.addWidget(group_plotconf)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        # self.setLayout(main_layout)

        # menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        action_load = fileMenu.addAction('&Load')
        action_save = fileMenu.addAction('&Save')
        action_export = fileMenu.addAction('&Export')
        action_quit = fileMenu.addAction('&Quit')
        runMenu = menubar.addMenu('&Run')
        action_plot = runMenu.addAction('&Plot')

        aboutMenu = menubar.addMenu('&?')
        action_help = aboutMenu.addAction('&Help')
        action_about = aboutMenu.addAction('&About')

        action_load.triggered.connect(self.loadButClicked)
        action_save.triggered.connect(self.saveButClicked)
        action_export.triggered.connect(self.exportButClicked)
        action_quit.triggered.connect(self.close)
        action_plot.triggered.connect(self.plotButClicked)
        action_about.triggered.connect(self.launch_about)
        action_help.triggered.connect(self.show_help_link)

        self.setWindowTitle('simple_plotter ' + self.version)
        self.setGeometry(0, 20, 640, 480)

        self.show()

    def refreshGUI(self):
        """
        resets and freshes text fields in GUI (retrieves data from data_handler)
        """
        self.leStartVal.setText(str(self.data_handler.plot_data.start_val))
        self.leEndVal.setText(str(self.data_handler.plot_data.end_val))
        self.leFormula.setText(self.data_handler.formula.equation)
        self.lefunctionName.setText(self.data_handler.formula.function_name)
        self.leFuncUnit.setText(self.data_handler.formula.function_unit)
        self.leNoPts.setText(str(self.data_handler.plot_data.no_pts))
        self.levarName.setText(self.data_handler.formula.var_name)
        self.leVarUnit.setText(self.data_handler.formula.var_unit)
        self.lesetStartVal.setText(str(self.data_handler.formula.set_min_val))
        self.lesetEndVal.setText(str(self.data_handler.formula.set_max_val))
        self.lesetNoPts.setText(str(self.data_handler.formula.no_sets))
        self.lesetvarName.setText(self.data_handler.formula.set_var_name)
        self.leSetUnit.setText(self.data_handler.formula.set_var_unit)
        self.leSetConstValues.setText(self.data_handler.formula.explicit_set_values)
        self.xscaleToggle.setChecked(self.data_handler.plot_data.x_log)
        self.yscaleToggle.setChecked(self.data_handler.plot_data.y_log)
        self.xySwapToggle.setChecked(self.data_handler.plot_data.swap_xy)
        self.gridToggle.setChecked(self.data_handler.plot_data.grid)
        self.csvExpToggle.setChecked(self.data_handler.export_csv)
        self.le_ymin.setText(str(self.data_handler.plot_data.y_min))
        self.le_ymax.setText(str(self.data_handler.plot_data.y_max))
        self.le_plot_title.setText(str(self.data_handler.plot_data.plot_title))

        # delete constants table
        for row in range(self.const_table.rowCount()):
            self.const_table.removeRow(row)

        # new write constants from constants dictionary into table
        for i, constant in enumerate(self.data_handler.formula.constants):
            self.const_table.insertRow(self.const_table.rowCount())
            for j in range(self.const_table.columnCount()):
                key = self.const_table.horizontalHeaderItem(j).text()
                item = QTableWidgetItem(self.data_handler.formula.constants[i][key])
                self.const_table.setItem(i, j, item)

    def saveButClicked(self):
        """
        Opens the file dialog and saves the project
        """
        self.readGUIInputs()
        filename, _ = QFileDialog.getSaveFileName(self, 'Save file')

        if filename not in ['', None]:
            self.projectfile = filename
            self.data_handler.save_project(filename)

    def loadButClicked(self):
        """
        Opens the file dialog on loads a project
        """
        filename, _ = QFileDialog.getOpenFileName(self, 'Open file')

        if filename not in ['', None]:
            self.projectfile = filename
            self.data_handler.load_project(filename)
            self.refreshGUI()

    def exportButClicked(self):
        """
        Opens the file dialog and exports the plotting source code
        """
        self.readGUIInputs()
        filename, _ = QFileDialog.getSaveFileName(self, 'Export file')

        if filename not in ['', None]:
            self.data_handler.write_py_file(filename)

    def addConstClicked(self):
        """
        adds new constant and GUI elements for it
        """
        self.const_table.insertRow(self.const_table.rowCount())

    def removeConstClicked(self):
        """"removes the selected row in the constants table"""

        self.const_table.removeRow(self.const_table.currentRow())

    def explicit_set_const_values_changed(self):
        """Greys out start, end, step values when explicit defined"""

        if check_valid_input(self.leSetConstValues.text()):
            self.lesetStartVal.setDisabled(True)
            self.lesetEndVal.setDisabled(True)
            self.lesetNoPts.setDisabled(True)
        else:
            self.lesetStartVal.setDisabled(False)
            self.lesetEndVal.setDisabled(False)
            self.lesetNoPts.setDisabled(False)

    def readGUIInputs(self):
        """
        reads the constants, start-endval and formula from GUI
        """
        constants = []
        for i in range(self.const_table.rowCount()):
            item_dict = {}
            for j in range(self.const_table.columnCount()):
                try:
                    # print(self.const_table.horizontalHeaderItem(j).text(), "=", self.const_table.item(i, j).text())
                    item_dict[self.const_table.horizontalHeaderItem(j).text()] = self.const_table.item(i, j).text()
                except AttributeError:
                    # print(self.const_table.horizontalHeaderItem(j).text(), "= None")
                    item_dict[self.const_table.horizontalHeaderItem(j).text()] = None
            print(item_dict)
            constants.append(item_dict)

        self.data_handler.formula.constants = constants
        self.data_handler.plot_data.start_val = self.leStartVal.text()
        self.data_handler.plot_data.end_val = self.leEndVal.text()
        self.data_handler.formula.equation = self.leFormula.text()
        self.data_handler.formula.function_name = self.lefunctionName.text()
        self.data_handler.formula.function_unit = self.leFuncUnit.text()
        self.data_handler.plot_data.no_pts = self.leNoPts.text()
        self.data_handler.formula.var_name = self.levarName.text()
        self.data_handler.formula.var_unit = self.leVarUnit.text()
        self.data_handler.formula.set_min_val = self.lesetStartVal.text()
        self.data_handler.formula.set_max_val = self.lesetEndVal.text()
        self.data_handler.formula.no_sets = self.lesetNoPts.text()
        self.data_handler.formula.set_var_name = self.lesetvarName.text()
        self.data_handler.formula.set_var_unit = self.leSetUnit.text()
        self.data_handler.formula.explicit_set_values = self.leSetConstValues.text()
        self.data_handler.plot_data.x_log = self.xscaleToggle.isChecked()
        self.data_handler.plot_data.y_log = self.yscaleToggle.isChecked()
        self.data_handler.plot_data.swap_xy = self.xySwapToggle.isChecked()
        self.data_handler.export_csv = self.csvExpToggle.isChecked()
        self.data_handler.plot_data.grid = self.gridToggle.isChecked()
        self.data_handler.plot_data.y_min = self.le_ymin.text()
        self.data_handler.plot_data.y_max = self.le_ymax.text()
        self.data_handler.plot_data.plot_title = self.le_plot_title.text()

    def plotButClicked(self):
        """
        read GUI inputs and plot graph
        """
        self.readGUIInputs()
        error_code = self.data_handler.plot()

        if error_code == 1:
            QMessageBox.critical(self, "Invalid defintion in constants",
                                 "Constants need to have at least name and value defined."
                                 "\nPlease remove incomplete constant defintions.")

    def launch_about(self):
        """Launches a message box with the about message"""

        about = AboutWindow(self)

    def show_help_link(self):
        """Shows a message box with the link to the documentation page"""

        url = "https://simple-plotter.readthedocs.io/en/stable/"
        helpbox = QMessageBox()
        helpbox.setTextFormat(Qt.RichText)
        helpbox.about(self, "Help", "<p> Please visit the documentation page:</p>"
                                    "<a href='{}'>"
                                    "{}</a>".format(url,  url))


class AboutWindow(QDialog):

    def __init__(self, *args, **kwargs):
        """About window with copyright and licence info"""

        super(AboutWindow, self).__init__(*args, **kwargs)

        self.layout = QGridLayout()

        lblInfo = QLabel("simple_plotter {}\n\n" \
                         "minimalistic plotting front-end and python code generator\n\n" \
                         "Copyright (c) 2018-2019 Thies Hecker\n".format(version))
        lblInfo.setAlignment(Qt.AlignCenter)
        self.btLicence = QPushButton("Licence")
        self.btOkay = QPushButton("Okay")

        self.layout.addWidget(lblInfo, 0, 0, 3, 2)
        self.layout.addWidget(self.btLicence, 3, 0)
        self.layout.addWidget(self.btOkay, 3, 1)

        self.btLicence.clicked.connect(self.show_licence)
        self.btOkay.clicked.connect(self.close)

        self.setWindowTitle("About")
        self.setLayout(self.layout)

        self.show()

    def show_licence(self):
        """Shows a message box with the licence info"""

        gplv3 = "This program is free software: you can redistribute it and/or modify it under the terms of the " \
                "GNU General Public License as published by the Free Software Foundation, either version 3 of the " \
                "License, or (at your option) any later version.\nThis program is distributed in the hope that it " \
                "will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or " \
                "FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n" \
                "You should have received a copy of the GNU General Public License along with this program. " \
                "If not, see <https://www.gnu.org/licenses/>."

        QMessageBox.about(self, "Licence info", gplv3)


if __name__ == '__main__':
    # get version string
    try:
        version = get_version(root='.', relative_to=__file__)  # version from source code repo
    except LookupError:
        version = pkg_resources.get_distribution(name).version  # if this is an installed package
    app = QApplication(sys.argv)
    formula1 = Formula()
    plot_data1 = PlotData()
    data_handler1 = DataHandler(formula1, plot_data1)
    gui1 = GUI(data_handler1, version)
    sys.exit(app.exec_())
