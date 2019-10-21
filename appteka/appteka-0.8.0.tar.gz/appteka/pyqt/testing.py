# appteka - helpers collection

# Copyright (C) 2018-2019 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Implementation of the tool for visual testing of widgets."""

from PyQt5 import QtWidgets
from appteka.pyqt import gui


class TestDialog(QtWidgets.QDialog):
    """Dialog for running unit tests of any widget when human tester
    answers to questions (ok or error)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__make_gui()
        self.widget = None
        self.tests = []
        self.test_num = 0

    def __make_gui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # description of test (test name)
        self.descr_layout = gui.add_sublayout(main_layout, "h")
        self.label_descr = gui.add_label("", self.descr_layout)
        self.label_descr.setWordWrap(True)

        self.widget_layout = gui.add_sublayout(main_layout, "h")

        # text
        self.assert_layout = gui.add_sublayout(main_layout, "h")
        self.label_assert = gui.add_label("", self.assert_layout)
        self.label_assert.setWordWrap(True)

        # buttons
        self.button_layout = gui.add_sublayout(main_layout, "h")
        self.button_err = gui.add_button(
            "ERROR", self.__on_button_err, self.button_layout)
        self.button_ok = gui.add_button(
            "OK", self.__on_button_ok, self.button_layout)

    def __on_button_ok(self):
        self.tests[self.test_num - 1]['result'] = "OK"
        self.__run_next_test()

    def __on_button_err(self):
        self.tests[self.test_num - 1]['result'] = "ERROR"
        self.__run_next_test()

    def set_widget(self, widget):
        """Sets widget to be tested."""
        if self.widget is not None:
            self.widget_layout.removeWidget(self.widget)
            self.widget.deleteLater()

        self.widget = gui.add_widget(widget, self.widget_layout)

    def set_text(self, value):
        """Set assertion text."""
        self.label_assert.setText(value)

    def __run_next_test(self):
        if self.test_num == len(self.tests):
            self.__report()
            self.close()
            return

        self.label_descr.setText(self.tests[self.test_num]['name'])
        self.tests[self.test_num]['func']()
        self.test_num += 1

    def run(self):
        """Run all tests."""
        self.__add_tests()

        self.show()

        if not self.tests:
            return

        self.test_num = 0
        self.__run_next_test()

    def __report(self):
        print('-----------------------------')
        print(self.__class__.__name__)
        print()
        verdict = 'PASSED'
        for test in self.tests:
            print("{}... {}".format(test['name'], test['result']))
            if test['result'] == 'ERROR':
                verdict = 'NOT PASSED'

        print('-----------------------------')
        print(verdict)
        print()

    def __add_test(self, name):
        test = {
            'func': getattr(self, name),
            'name': name,
            'result': 'ERROR',
        }
        self.tests.append(test)

    def __add_tests(self):
        for fname in dir(self):
            if fname[:5] == "test_":
                if not callable(getattr(self, fname)):
                    continue
                self.__add_test(fname)

    def disable_buttons(self):
        """Disable buttons. For example, for waiting some process
        during the test."""
        self.button_ok.setEnabled(False)
        self.button_err.setEnabled(False)

    def enable_buttons(self):
        """Enable buttons."""
        self.button_ok.setEnabled(True)
        self.button_err.setEnabled(True)
