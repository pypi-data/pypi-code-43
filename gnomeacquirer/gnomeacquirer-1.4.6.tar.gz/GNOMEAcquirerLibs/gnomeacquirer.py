#!/usr/bin/python3

# import cProfile
import multiprocessing
from GNOMEAcquirerLibs.AcquisitionWindow import *

# enable this to test frozen version of the program
# setattr(sys, 'frozen', True)


def main_function():
    multiprocessing.freeze_support()

    PrintSoftwareInfo()

    app = QApplication(sys.argv)

    # make message boxes text selectable
    app.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }");

    screen = AcqusitionWindow()
    screen.showMaximized()
    screen.doAfterShown()

    app.aboutToQuit.connect(screen.cleanUp)

    sys.exit(app.exec_())

# if __name__ == '__main__':
if __name__.endswith('__main__'):  # fix because cx_freeze changes __name__
    main_function()
    # cProfile.run('main_function()',sort='tottime')
