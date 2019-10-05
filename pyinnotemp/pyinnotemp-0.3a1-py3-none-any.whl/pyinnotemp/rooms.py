


class BBRooms:

    def __init__(self, name, number, targetvar, sensorvar, statusvar, setvar):
        self.name = name
        self.number = number
        self._targetvar = targetvar
        self._sensorvar = sensorvar
        self._statusvar = statusvar
        self._setvar = setvar
        self.currentTemperature = 0.0
        self.targetTemperature = 0.0


    def getTargetTemperature (self):
        return self.targetTemperature

    def getCurrentTemperature (self):
        return self.currentTemperature

    def updateCurrentTemperature (self, temp):
        self.currentTemperature = temp

    def updateTargetTemperature (self, temp):
        self.targetTemperature = temp

    def getSensorVariable (self):
        return self._sensorvar

    def getStatusVariable (self):
        return self._statusvar

    def getSetVariable (self):
        return self._setvar

    def getTargetVariable (self):
        return self._targetvar
