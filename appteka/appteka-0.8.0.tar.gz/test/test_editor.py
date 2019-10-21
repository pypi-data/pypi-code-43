import sys
import os

from PyQt5 import QtWidgets

sys.path.insert(0, os.path.abspath("."))
from appteka.pyqt import testing
from appteka.pyqt.codetextedit import CodeTextEdit


class TestCodeTextEdit(testing.TestDialog):
    """Tests for CodeTextEdit"""
    def __init__(self):
        super().__init__()
        self.resize(600, 600)

    def test_text(self):
        e = CodeTextEdit()
        self.set_widget(e)

        code = ""
        code += '{\n'
        code += '  "a": 1,\n'
        code += '  "b": 2\n'
        code += '}'

        e.set_text(code)
        text = ""
        text += "- Some text is printed\n"
        text += "- Lines numbered\n"
        text += "- Current line is highlighted\n"
        text += "- Font is monospace"
        self.set_text(text)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    d = TestCodeTextEdit()
    d.run()
    sys.exit(app.exec())
