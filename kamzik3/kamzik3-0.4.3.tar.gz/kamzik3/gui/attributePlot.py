import collections
from threading import Lock

import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from kamzik3.snippets.snippetsYaml import YamlSerializable

from kamzik3 import units
from kamzik3.constants import *

pg.setConfigOption(u'background', u'w')
pg.setConfigOption(u'foreground', u"k")


class AttributePlot(pg.PlotWidget, YamlSerializable):

    sig_repaint = pyqtSignal()

    def __init__(self, attribute, buffer_size, plot=None, parent=None, background='#fff', **kwargs):
        super().__init__(parent, background, **kwargs)
        self.current_point = 0
        self.attribute = attribute
        self.x_buffer = collections.deque([], maxlen=buffer_size)
        self.y_buffer = collections.deque([], maxlen=buffer_size)
        try:
            self.base_unit = kwargs.get("unit", attribute[UNIT])
        except TypeError:
            self.base_unit = ""

        pen1 = pg.mkPen(color=(0, 0, 255))
        pen2 = pg.mkPen(color=(0, 0, 0))
        self.value_curve = pg.PlotDataItem(self.x_buffer, self.y_buffer, pen=pen1, antialias=False, symbol=u"s",
                                           symbolSize=2, symbolPen=pen2)
        if plot is None:
            self.setLabel(u"left", kwargs.get("left_label", ""), units=self.base_unit)
            self.setLabel(u"bottom", "point")
            self.showGrid(x=True, y=True, alpha=0.1)
            self.addItem(self.value_curve)
        else:
            plot.setLabel(u"left", kwargs.get("left_label", ""), units=self.base_unit)
            plot.setLabel(u"bottom", "point")
            plot.showGrid(x=True, y=True, alpha=0.1)
            plot.addItem(self.value_curve)
        self.sig_repaint.connect(self.slot_set_data)

    def yaml_mapping(self):
        mapping = super().yaml_mapping()
        del mapping["parent"]
        return mapping

    @pyqtSlot()
    def slot_set_data(self):
        self.value_curve.setData(self.x_buffer, self.y_buffer)

    def update(self, current_point=None, current_value=None):
        if current_point is None:
            self.current_point += 1
        else:
            self.current_point = current_point
        if current_value is None:
            current_value = self.attribute.value().to(self.base_unit).m
        else:
            assert isinstance(current_value, units.Quantity)
            current_value = current_value.to(self.base_unit).m
        try:
            self.y_buffer.append(current_value)
            self.x_buffer.append(self.current_point)
        except Exception as e:
            print(e, current_point, current_value)
            return
        self.sig_repaint.emit()

    def close(self):
        self.attribute = None
        self.current_point = 0
        self.reset()
        super().close()

    def reset(self):
        self.x_buffer.clear()
        self.y_buffer.clear()
        self.value_curve.setData([], [])
