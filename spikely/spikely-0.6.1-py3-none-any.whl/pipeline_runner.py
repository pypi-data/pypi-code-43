from PyQt5 import QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.stdout_ready)
        self.process.readyReadStandardError.connect(self.stderr_ready)
        # self.process.started.connect(lambda: p('Started!'))
        # self.process.finished.connect(lambda: p('Finished!'))

        # print 'Starting process'
        # self.process.start('python', ['speak.py'])

    def append(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        # self.output.ensureCursorVisible()

    def stdout_ready(self):
        text = str(self.process.readAllStandardOutput())
        # print text.strip()
        self.append(text)

    def stderr_ready(self):
        text = str(self.process.readAllStandardError())
        # print text.strip()
        self.append(text)


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    for arg in sys.argv:
        print(arg)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
