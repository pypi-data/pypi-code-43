from taurus.qt.qtgui.panel.taurusvalue import TaurusValue


class TaurusValueHB(TaurusValue):
    """ TaurusValue widget with Heartbeat events
    """

    def __init__(self, parent=None, designMode=False,
                 customWidgetMap=None, period=1000, attr=None):
        """ consturctor

        :param parent: parent widget
        :type parent: :class:`taurus.external.qt.Qt.QWidget`
        :param designMode: taurus design mode
        :type designMode: :obj:`bool`
        :param customWidgetMap: dictionary whose keys are device class strings
                                (see :class:`PyTango.DeviceInfo`) and
                                whose values are widget classes to be used
        :type customWidgetMap: :obj:`dict` <:obj:`str` ,
                               :class:`taurus.external.qt.Qt.QWidget` >
        :param period: heartbeat period
        :type period: :obj:`int`
        :param attr: tango device attribute name
        :type attr: :obj:`str`
        """

        TaurusValue.__init__(self, parent, designMode, customWidgetMap)
        self._attr = attr or 'position'
        self.setEventBufferPeriod(period)

    def setModel(self, model):
        """sets the widget model

        :param model: tango device name
        :type model: :obj:`str`
        """
        TaurusValue.setModel(self, model + "/" + self._attr)
