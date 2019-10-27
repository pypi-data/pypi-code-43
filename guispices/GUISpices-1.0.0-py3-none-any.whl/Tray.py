from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PySide2.QtCore import SIGNAL, QObject


class TrayIcon:
    def __init__(self, qt_application, icon_path: str, title: str, click_action=None):
        print(f'The qt_application may close when last window is closed.'
              f'To suppress, invoke qt_application.setQuitOnLastWindowClosed(False). ') \
            if qt_application.quitOnLastWindowClosed() else None
        self._app = qt_application
        self._icon_path = icon_path
        self._tray = QSystemTrayIcon(QIcon(self._icon_path), self._app)
        self._tray.activated.connect(lambda reason, *args: click_action(*args) if click_action and reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        self._feature_menu, self._menu = {}, QMenu("ToolMenuBar")
        self._tray.setContextMenu(self._menu)
        self._tray.setToolTip(title)
        self._tray.show()

    def set_icon(self, icon_path: str) -> None:
        self._tray.setIcon(QIcon(icon_path))

    def add_menu_feature(self, text: str, function: callable) -> None:
        _ = QAction(text)
        _.triggered.connect(function)
        self._feature_menu[text] = _
        self._menu.addAction(self._feature_menu[text])

    def add_separator(self) -> None:
        self._menu.addSeparator()

    def add_menu(self, menu: QMenu, menu_title: str = "") -> None:
        if menu_title:
            menu.setTitle(menu_title)
        self._menu.addMenu(menu)

    def show_tray_message(self, title: str, text: str, on_click: callable = None, icon: str = None) -> None:
        self._tray.showMessage(title, text, QIcon(icon)) if icon else self._tray.showMessage(title, text)
        if on_click:
            QObject.connect(self._tray, SIGNAL('messageClicked()'), on_click)


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication, QMessageBox
    import sys

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)


    def run_something():
        print("Icon left-clicked")


    def show_message():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setWindowTitle("MessageBox demo")
        msg.setText("This is a message box")

        msg.setInformativeText("This is additional information")
        msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()


    # Configure Tray
    tray = TrayIcon(app, "examples/icon.png", "Test Program", click_action=run_something)
    tray.add_menu_feature("Show a message box", show_message)
    tray.add_menu_feature("Change Icon", lambda: tray.set_icon("examples/icon2.png"))
    tray.add_menu_feature("Show a message from tray", lambda: tray.show_tray_message("Hello", "Hello my friend"))
    tray.add_separator()
    tray.add_menu_feature("Exit", app.exit)

    menu_ = QMenu(title="Sub Menu")
    menu_.addAction("Egg sit", lambda: sys.exit(0))
    tray.add_menu(menu_)

    tray.show_tray_message("Tray", "Tray is running", on_click=lambda: print("Hi"))

    sys.exit(app.exec_())
