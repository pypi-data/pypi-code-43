import sys
from typing import List, Dict, Optional, Union

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import vmi

_SizePolicyMinimum = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
tr = QObject()
tr = tr.tr


def askOpenFile(nameFilter: str = '*',
                title: str = tr('请选择打开文件 (Please select open file)')) -> Optional[str]:
    """
    打开文件对话框

    :param nameFilter: 对话框内显示的文件名
    :param title: 对话框名称
    :return: str - 有效选择的文件名，None - 没有有效选择
    """
    s = QSettings()

    d = QFileDialog(None, title, s.value('Last' + title, defaultValue=vmi.desktopPath))
    d.setAcceptMode(QFileDialog.AcceptOpen)
    d.setFileMode(QFileDialog.ExistingFile)
    d.setViewMode(QFileDialog.Detail)
    d.setFilter(QDir.AllEntries | QDir.NoSymLinks | QDir.NoDotAndDotDot)
    d.setNameFilter(nameFilter)

    if d.exec_() != QDialog.Accepted or len(d.selectedFiles()) < 1:
        return None

    s.setValue('Last' + title, d.selectedFiles()[0])
    return d.selectedFiles()[0]


def askSaveFile(suffix: str = '', nameFilter: str = '*',
                title: str = tr('请选择保存文件 (Please select save file)')) -> Optional[str]:
    """
    保存文件对话框

    :param suffix: 默认后缀名
    :param nameFilter: 对话框内显示的文件名
    :param title: 对话框名称
    :return: str - 有效选择的文件名，None - 没有有效选择
    """
    s = QSettings()

    d = QFileDialog(None, title, s.value('Last' + title, defaultValue=vmi.desktopPath))
    d.setAcceptMode(QFileDialog.AcceptSave)
    d.setFileMode(QFileDialog.AnyFile)
    d.setViewMode(QFileDialog.Detail)
    d.setFilter(QDir.AllEntries | QDir.NoSymLinks | QDir.NoDotAndDotDot)
    d.setDefaultSuffix(suffix)
    d.setNameFilter(nameFilter)

    if nameFilter is None:
        d.setNameFilter(suffix)

    if d.exec_() != QDialog.Accepted or len(d.selectedFiles()) < 1:
        return None

    s.setValue('Last' + title, d.selectedFiles()[0])
    return d.selectedFiles()[0]


def askOpenFiles(nameFilter: str = '*',
                 title: str = tr('请选择打开文件 (Please select open files)')) -> Optional[List[str]]:
    """
    打开多个文件对话框

    :param nameFilter: 对话框内显示的文件名
    :param title: 对话框名称
    :return: List[str] - 有效选择的多个文件名，None - 没有有效选择
    """
    s = QSettings()

    d = QFileDialog(None, title, s.value('Last' + title, defaultValue=vmi.desktopPath))
    d.setAcceptMode(QFileDialog.AcceptOpen)
    d.setFileMode(QFileDialog.ExistingFiles)
    d.setViewMode(QFileDialog.Detail)
    d.setFilter(QDir.AllEntries | QDir.NoSymLinks | QDir.NoDotAndDotDot)
    d.setNameFilter(nameFilter)

    if d.exec_() != QDialog.Accepted or len(d.selectedFiles()) < 1:
        return None

    s.setValue('Last' + title, QFileInfo(d.selectedFiles()[0]).absolutePath())
    return d.selectedFiles()


def askDirectory(title: str = tr('请选择文件夹 (Please select directory)')) -> Optional[str]:
    """
    打开文件目录对话框

    :param title: 对话框名称
    :return: str - 有效选择的文件目录，None - 没有有效选择
    """
    s = QSettings()

    d = QFileDialog(None, title, s.value('Last' + title, defaultValue=vmi.desktopPath))
    d.setAcceptMode(QFileDialog.AcceptOpen)
    d.setFileMode(QFileDialog.Directory)
    d.setViewMode(QFileDialog.Detail)
    d.setFilter(QDir.AllEntries | QDir.NoSymLinks | QDir.NoDotAndDotDot)

    if d.exec_() != QDialog.Accepted or len(d.selectedFiles()) < 1:
        return None

    s.setValue('Last' + title, d.selectedFiles()[0])
    return d.selectedFiles()[0]


def _dialog_ok_cancel(widgets, title) -> QDialog:
    dialog = QDialog()
    dialog.setSizePolicy(_SizePolicyMinimum)
    dialog.setWindowTitle(title)
    dialog.setLayout(QVBoxLayout())

    button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
    button.setSizePolicy(_SizePolicyMinimum)
    button.accepted.connect(dialog.accept)
    button.rejected.connect(dialog.reject)

    for w in widgets:
        w.setParent(dialog)
        dialog.layout().addWidget(w)
    dialog.layout().addWidget(button)
    return dialog


def askSeries(series: List[vmi.SeriesData],
              title: str = tr('请选择目标系列 (Please select the target series)')) -> Optional[vmi.SeriesData]:
    """
    选择DICOM系列

    :param series: 候选的DICOM系列列表
    :param title: 对话框名称
    :return: vmi.SeriesData - 有效选择的DICOM系列，None - 没有有效选择
    """
    items = [str(i) for i in series]

    def tabCloseRequested(i):
        del items[i]
        tabs.removeTab(i)

    tabs = QTabWidget()
    tabs.setTabsClosable(True)
    tabs.setSizePolicy(_SizePolicyMinimum)
    tabs.tabCloseRequested.connect(tabCloseRequested)

    for i in items:
        label = QLabel(text=i)
        tabs.addTab(label, str(tabs.count() + 1))

    d = _dialog_ok_cancel([tabs], title)
    if d.exec_() == QDialog.Accepted:
        if 0 <= tabs.currentIndex() < len(series):
            return series[tabs.currentIndex()]
    return None


def askInt(value_min: int, value: int, value_max: int, step: Optional[int] = None, prefix: str = None,
           suffix: str = None,
           title: str = tr('输入数值 (Input value)')) -> Optional[int]:
    """
    选择整形数值

    :param value_min: 最小值
    :param value: 默认值
    :param value_max: 最大值
    :param step: 最小单位
    :param prefix: 前缀
    :param suffix: 后缀
    :param title: 对话框名称
    :return: int - 有效选择的数值，None - 没有有效选择
    """
    w = QGroupBox(prefix)
    w.setSizePolicy(_SizePolicyMinimum)
    w.setLayout(QHBoxLayout())

    spinbox = QSpinBox(w)
    spinbox.setSizePolicy(_SizePolicyMinimum)
    spinbox.setAlignment(Qt.AlignCenter)
    spinbox.setRange(value_min, value_max)
    spinbox.setValue(value)
    w.layout().addWidget(spinbox)

    if suffix is not None:
        spinbox.setSuffix(' ' + suffix)

    if step is not None:
        spinbox.setSingleStep(step)
        spinbox.setStepType(QSpinBox.DefaultStepType)
    else:
        spinbox.setStepType(QSpinBox.AdaptiveDecimalStepType)

    d = _dialog_ok_cancel([w], title)
    if d.exec_() == QDialog.Accepted:
        return spinbox.value()
    return None


def askInts(value_min: List[int], value: List[int], value_max: List[int], step: Optional[List[int]] = None,
            prefix=None, suffix=None, title=tr('输入数值 (Input value)')) -> Optional[List[int]]:
    """
    选择多个整形数值

    :param value_min: 最小值列表
    :param value: 默认值列表
    :param value_max: 最大值列表
    :param step: 最小单位列表
    :param prefix: 前缀
    :param suffix: 后缀
    :param title: 对话框名称
    :return: List[int] - 有效选择的多个数值，None - 没有有效选择
    """
    w = QGroupBox()
    w.setSizePolicy(_SizePolicyMinimum)
    w.setLayout(QHBoxLayout())

    spinbox = []
    for i in range(len(value)):
        spinbox.append(QSpinBox(w))
        spinbox[-1].setSizePolicy(_SizePolicyMinimum)
        spinbox[-1].setAlignment(Qt.AlignCenter)
        spinbox[-1].setRange(value_min[i], value_max[i])
        spinbox[-1].setValue(value[i])
        w.layout().addWidget(spinbox[-1])

        if prefix is not None:
            spinbox[-1].setPrefix(' ' + prefix[i])
        if suffix is not None:
            spinbox[-1].setSuffix(' ' + suffix[i])

        if step is not None:
            spinbox[-1].setSingleStep(step[i])
            spinbox[-1].setStepType(QSpinBox.DefaultStepType)
        else:
            spinbox[-1].setStepType(QSpinBox.AdaptiveDecimalStepType)

    d = _dialog_ok_cancel([w], title)
    if d.exec_() == QDialog.Accepted:
        return [spinbox[i].value() for i in range(len(value))]
    return None


def askFloat(value_min: float, value: float, value_max: float, decimals: int, step: Optional[float] = None,
             prefix=None, suffix=None, title: str = tr('输入数值 (Input value)')) -> Optional[float]:
    """
    选择浮点数值

    :param value_min: 最小值列表
    :param value: 默认值列表
    :param value_max: 最大值列表
    :param decimals: 小数位数
    :param step: 最小单位列表
    :param prefix: 前缀
    :param suffix: 后缀
    :param title: 对话框名称
    :return: float - 有效选择的数值，None - 没有有效选择
    """
    w = QGroupBox(prefix)
    w.setSizePolicy(_SizePolicyMinimum)
    w.setLayout(QHBoxLayout())

    spinbox = QDoubleSpinBox(w)
    spinbox.setSizePolicy(_SizePolicyMinimum)
    spinbox.setAlignment(Qt.AlignCenter)
    spinbox.setDecimals(decimals)
    spinbox.setRange(value_min, value_max)
    spinbox.setValue(value)
    w.layout().addWidget(spinbox)

    if suffix is not None:
        spinbox.setSuffix(' ' + suffix)

    if step is not None:
        spinbox.setSingleStep(step)
        spinbox.setStepType(QSpinBox.DefaultStepType)
    else:
        spinbox.setStepType(QSpinBox.AdaptiveDecimalStepType)

    d = _dialog_ok_cancel([w], title)
    if d.exec_() == QDialog.Accepted:
        return spinbox.value()
    return None


def askFloats(value_min: List[float], value: List[float], value_max: List[float], decimals: int,
              step: Optional[float] = None, prefix=None, suffix=None,
              title: str = tr('输入数值 (Input value)')) -> Optional[List[float]]:
    """
    选择多个浮点数值

    :param value_min: 最小值列表
    :param value: 默认值列表
    :param value_max: 最大值列表
    :param decimals: 小数位数
    :param step: 最小单位列表
    :param prefix: 前缀
    :param suffix: 后缀
    :param title: 对话框名称
    :return: float - 有效选择的数值，None - 没有有效选择
    """
    w = QGroupBox(prefix)
    w.setSizePolicy(_SizePolicyMinimum)
    w.setLayout(QHBoxLayout())

    spinbox = []
    for i in range(len(value)):
        spinbox.append(QDoubleSpinBox(w))
        spinbox[-1].setSizePolicy(_SizePolicyMinimum)
        spinbox[-1].setAlignment(Qt.AlignCenter)
        spinbox[-1].setDecimals(decimals)
        spinbox[-1].setRange(value_min[i], value_max[i])
        spinbox[-1].setValue(value[i])
        w.layout().addWidget(spinbox[-1])

        if suffix is not None:
            spinbox[-1].setSuffix(' ' + suffix[i])

        if step is not None:
            spinbox[-1].setSingleStep(step[i])
            spinbox[-1].setStepType(QSpinBox.DefaultStepType)
        else:
            spinbox[-1].setStepType(QSpinBox.AdaptiveDecimalStepType)

    d = _dialog_ok_cancel([w], title)
    if d.exec_() == QDialog.Accepted:
        return [spinbox[i].value() for i in range(len(value))]
    return None


def askInfo(text: str, title: str = tr('提示 (info)')) -> None:
    """
    提示对话框

    :param text: 信息文本
    :param title: 对话框名称
    :return: None
    """
    QMessageBox.information(None, title, text)


def askYesNo(text: str, title: str = tr('是否 (yes or no)')) -> bool:
    """
    询问对话框
    :param text: 信息文本
    :param title: 对话框名称
    :return: True - 选择了是，False - 选择了否
    """
    return QMessageBox.question(None, title, text) == QMessageBox.Yes


if __name__ == '__main__':
    vmi.app.setApplicationName('vmi')

    askInt(-3071, -1, 1024, prefix='CT: [-3071, 1024]', suffix='HU')
