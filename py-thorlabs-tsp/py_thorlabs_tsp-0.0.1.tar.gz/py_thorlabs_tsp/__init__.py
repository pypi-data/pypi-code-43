# -*- coding: utf-8 -*-
"""py_thorlabs_tsp.__init__.py

This package contains wrappers for the functions of TSP01B DLL.

This DLL allows to control Thorlabs TSP01 temperature and humidity
sensor. Requires installed TSP01 software from Thorlabs.

Was tested on Windows and TSP01 Rev.B only.

Author: Dima Pustakhod
Copyright: TU/e
"""
from .wrappers import _calibrationMessage, _close, _errorMessage, _errorQuery
from .wrappers import _findRsrc, _getExtRefVoltage, _getExtSerResist
from .wrappers import _getHumidityData, _getHumSensOffset, _getProductionDate
from .wrappers import _getRsrcInfo, _getRsrcName, _getTemperatureData
from .wrappers import _getTempSensOffset, _getThermistorExpParams, _getThermRes
from .wrappers import _identificationQuery, _init, _isServiceMode
from .wrappers import _measHumidity, _measTemperature, _reset, _revisionQuery
from .wrappers import _selfTest, _setDeviceName, _setExtRefVoltage
from .wrappers import _setExtSerResist, _setHumSensOffset, _setProductionDate
from .wrappers import _setSerialNr, _setServiceMode, _setTempSensOffset

from .thorlabs_tsp01b import ThorlabsTsp01B

from .errors import ThorlabsTsp01BException
