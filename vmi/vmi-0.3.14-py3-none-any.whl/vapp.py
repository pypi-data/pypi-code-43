from typing import Optional, List

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtWinExtras import *
import threading
import time
import os
import sys
import pathlib
import shutil

app = QApplication()
app.setOrganizationName('vmi')
app.setApplicationName('vmi')
app.setStyle(QStyleFactory.create('Fusion'))

desktopPath: str = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
appDataPath: str = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
os.makedirs(appDataPath, exist_ok=True)

_AppWindow: QWidget = None
_TaskbarButton = QWinTaskbarButton()
_Progress = _TaskbarButton.progress()


def _appinit() -> None:
    pass


_appinit()


def appexit() -> None:
    """
    退出主程序

    :return: None
    """
    shutil.rmtree(appDataPath, ignore_errors=True)
    sys.exit()


def appwindow(w: Optional[QWidget] = None) -> QWidget:
    """
    设置主程序窗口

    :param w: 主程序窗口
    :return: QWidget - 返回当前主程序窗口
    """
    if w is not None:
        global _AppWindow
        _AppWindow = w
        _TaskbarButton.setParent(w)
        _TaskbarButton.setWindow(w.windowHandle())
        _Progress.setVisible(True)
        _Progress.setRange(0, 100)
        _Progress.setValue(0)
    return _AppWindow


def appexec(w: QWidget, width: int = 1600, height: int = 900) -> int:
    """
    设置主程序窗口，居中显示，启动主程序

    :param w: 主程序窗口
    :param width: 窗口宽度
    :param height: 窗口高度
    :return: int - 主程序结束状态
    """
    appwindow(w)
    rect = QGuiApplication.screens()[0].geometry()
    rect = QRect(rect.center() - QPoint(int(width / 2), int(height / 2)), QSize(width, height))
    w.setGeometry(rect)
    w.show()
    app.exec_()


def appwait(thread: threading.Thread, progress: Optional[List[int]] = None) -> None:
    """
    执行后台线程并等待，默认在windows系统任务栏循环更新进度，设置progress=[value]可以显示真实进度

    :param thread: 后台线程
    :param progress: 进度
    :return: None
    """
    while thread.isAlive():
        if progress is None:
            value = (_Progress.value() + 5) % 100
        else:
            value = progress[0]
        _Progress.setValue(value)
        time.sleep(0.1)
    _Progress.setValue(0)


_scripts = pathlib.Path(sys.executable).parent / 'Scripts'
_lupdate = str(_scripts / 'pyside2-lupdate')
_uic = str(_scripts / 'pyside2-uic')
_rcc = str(_scripts / 'pyside2-rcc')

_pyside2 = pathlib.Path(sys.executable).parent / 'Lib/site-packages/PySide2'
_designer = str(_pyside2 / 'designer')
_linguist = str(_pyside2 / 'linguist')
_lrelease = str(_pyside2 / 'lrelease')


def app_uic(ui_dir: str = 'ui', py_dir: str = '.', prefix: str = 'Ui_') -> None:
    """
    将ui_dir目录下的所有.ui文件转换到py_dir目录下.py文件并附加前缀ui_

    :param ui_dir: 界面文件（.ui）目录
    :param py_dir: 转换后的源代码文件（.py）目录
    :param prefix: 转换后的文件名前缀
    :return: None
    """
    py_dir = pathlib.Path(py_dir)

    for ui in pathlib.Path(ui_dir).rglob('*.ui'):
        if ui.is_file():
            py = py_dir / (prefix + ui.with_suffix('.py').name)
            os.system(_uic + ' ' + str(ui) + ' -o ' + str(py) + ' -x')
            print('[uic.exe]', _uic, ui, '-o', py, '-x')


def app_lupdate(py_dir: str = '.', ts_file: str = 'zh_CN.ts') -> None:
    """
    将py_dir目录下的所有.py文件更新翻译到同目录下的.ts文件ts_file

    :param py_dir: 源代码文件（.py)目录
    :param ts_file: 转换后的翻译文件（.ts）路径
    :return: None
    """
    py_dir = pathlib.Path(py_dir)
    pys = str()

    for py in pathlib.Path(py_dir).rglob('*.py'):
        if py.is_file():
            pys += str(py) + ' '

    if len(pys) > 0:
        ts_file = py_dir / ts_file
        os.system(_lupdate + ' ' + str(pys) + ' -ts ' + str(ts_file))
        print('[lupdate.exe]', _lupdate, pys, '-ts', ts_file)


def app_lrelease(ts_file: str = './zh_CN.ts',
                 qm_file: str = 'qrc/tr/zh_CN.qm') -> None:
    """
    将可读翻译文件ts_file转换为二进制翻译文件qm_file

    :param ts_file: 可读翻译文件（.ts）
    :param qm_file: 转换后的二进制翻译文件（.qm）
    :return: None
    """
    os.system(_lrelease + ' ' + ts_file + ' -qm ' + qm_file)
    print('[lrelease.exe]', _lrelease, ts_file, '-qm', qm_file)
    os.system(_linguist + ' ' + './zh_CN.ts')


def app_rcc(rc_dir: str = 'qrc', qrc_file: str = 'vmi.qrc', py_file: str = 'vrc.py') -> None:
    """
    将rc_dir目录下的所有文件转换为.qrc资源文件qrc_file，再转换为.py文件py_file

    :param rc_dir: 资源文件目录
    :param qrc_file: 资源文件（.qrc）
    :param py_file: 转换后的源代码文件（.py）
    :return: None
    """
    rc_dir = pathlib.Path(rc_dir)
    indent = ' ' * 4
    rcs = str()

    for rc in pathlib.Path(rc_dir).rglob('*'):
        if rc.is_file():
            rc = str(rc).replace('\\', '/')
            rcs += indent * 2 + '<file>' + rc + '</file>' + '\n'

    if len(rcs) > 0:
        t = '<!DOCTYPE RCC>'
        t += '<RCC version="1.0">' + '\n'
        t += indent + '<qresource prefix="/">' + '\n'
        t += rcs
        t += indent + '</qresource>' + '\n'
        t += '</RCC>'

        with open(qrc_file, 'w') as f:
            f.write(t)

        os.system(_rcc + ' ' + qrc_file + ' -o ' + py_file)
        print('[rcc.exe]', _rcc, qrc_file, '-o', py_file)


if __name__ == '__main__':
    # app_uic()  # 更新界面.ui文件
    # app_lupdate()  # 更新翻译.ts文件
    # app_lrelease()  # 更新翻译.qm文件
    app_rcc()  # 更新.qrc文件

    # os.startfile(_designer)  # 打开界面.ui文件
