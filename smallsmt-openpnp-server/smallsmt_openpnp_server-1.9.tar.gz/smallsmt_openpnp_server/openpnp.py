from PyQt5.QtCore import pyqtSlot,pyqtSignal
from PyQt5.QtCore import QObject,Qt

import math

import smallsmtprotocol
import smallsmtmessanger
import openpnpmessanger
import openpnpcoords


class OpenPnp(QObject):
    UPDATE_NONE = -1
    UPDATE_VACUUM = 0

    openPnpLog = pyqtSignal([str])

    def __init__(self,smallSmtMachineConfig,serial):
        QObject.__init__(self)

        # Machine configuration
        self.machineFullConfig = smallSmtMachineConfig

        # Machine global coordinates
        self.coords = openpnpcoords.OpenPnpCoords(self.machineFullConfig)

        # Connection  to OpenPnp
        self.openpnp = openpnpmessanger.OpenPnpMessanger(self.coords)
        self.openpnp.openPnpRequest.connect(self.executeRequestProlog)

        # Connection to the SmallSmt machine
        self.smallsmt = smallsmtmessanger.SmallSmtMessanger(serial)
        self.smallsmt.messageDone.connect(self.executeRequestEpilog,Qt.QueuedConnection)
        self.smallsmt.messagePing.connect(self.executePing,Qt.QueuedConnection)

        #Ignore values sent from the machine
        self.update_read_value = self.UPDATE_NONE
        self.needle_state = 0
        self.needle_prev_value = 0
        self.pick_active = 0

    def logInfo(self,logText):
        self.openPnpLog.emit(logText)

    @pyqtSlot(str)
    def executeRequestProlog(self,command):
        if command.startswith("home("):
            self.cmd__home()
        elif command.startswith("moveTo("):
            self.cmd__moveTo(command)
        elif  command.startswith("setEnabled("):
            self.cmd__setEnabled(command)
        elif command.startswith("pick("):
            self.cmd__pick(command)
        elif command.startswith("place("):
            self.cmd__place(command)
        elif command.startswith("actuate("):
            self.cmd__actuate(command)
        elif command.startswith("actuateRead("):
            self.cmd__actuateRead(command)
        else:
            # The code comes here only in case of wrong command
            # Otherwise it is being processed in commands itself
            self.logInfo(str.format("Command unrecognized or not sent: {} ", command))
            self.openpnp.status = -1
            self.openpnp.executeResponse()

    @pyqtSlot(bool)
    def executeRequestEpilog(self, result):
        if result:
            self.openpnp.status = 0

            if self.update_read_value != self.UPDATE_NONE:

                if self.update_read_value==self.UPDATE_VACUUM:
                    try:
                        vac_read = self.smallsmt.getRetVal(self.update_read_value)
                        self.openpnp.value = float(vac_read[1])
                    except:
                        self.openpnp.value = float('NaN')
                        self.openPnpLog.emit("Vacuum reading failure")

                self.update_read_value = self.UPDATE_NONE
            else:
                self.openpnp.value = float('NaN')

        else:
            self.openpnp.status = -1
        self.openpnp.executeResponse()

    @pyqtSlot()
    def executePing(self):
        self.openpnp.executePing()


    def cmd__home(self):
        self.openPnpLog.emit("EXE: home")

        self.execute_home()


    def cmd__moveTo(self,command):

        self.openPnpLog.emit("EXE: move (" + command +")")

        cmd = openpnpcoords.OpenPnpCoordsSplitter(command)
        cmd.toMove()
        self.execute_moveTo(cmd)


    def cmd__actuate(self,command):
        self.openPnpLog.emit("EXE: actuate set (" + command + ")")

        cmd = openpnpcoords.OpenPnpCoordsSplitter(command)
        cmd.toActuatorWrite()
        self.execute_actuateSet(cmd)


    def cmd__pick(self,command):
        self.openPnpLog.emit("EXE: pick (" + command + ")")

        cmd = openpnpcoords.OpenPnpCoordsSplitter(command)
        cmd.toPickPlace()
        self.execute_pick(cmd)

    def cmd__place(self,command):
        self.openPnpLog.emit("EXE: place (" + command + ")")

        cmd = openpnpcoords.OpenPnpCoordsSplitter(command)
        cmd.toPickPlace()
        self.execute_place(cmd)



    def cmd__setEnabled(self,command):

        self.openPnpLog.emit("EXE: setEnabled (" + command + ")")

     #   self.executeRequestEpilog(1)
    #    return

        cmd = openpnpcoords.OpenPnpCoordsSplitter(command)
        cmd.toInit()

        self.execute_setEnabled(cmd)



    def cmd__actuateRead(self,command):
        self.openPnpLog.emit("EXE: actuate read (" + command + ")")

        cmd = openpnpcoords.OpenPnpCoordsSplitter(command)
        cmd.toActuatorRead()
        self.execute_actuateRead(cmd)





    def scaleStartSpeed(self,val,factor):
        result = int(math.floor(val * factor))
        if result < 1:
            result = 1
        return result

    def scaleRunSpeed(self, val, factor):
        result = int(math.floor(val * factor))
        if result < 5:
            result = 5
        return result

    def limit(self, val, min,max):
        if val < min:
            val = min
        elif val > max:
            val = max
        return math.floor(val)

    def checkOnOff(self, val):
        if val !=0:
            return 1
        else:
            return 0


    def execute_home(self):

        self.coords.Home()
        self.smallsmt.prepare()
        self.smallsmt.add({"tout": 30000, "packet": smallsmtprotocol.SmallSmtCmd__Reset("XYZ1Z2W1W2W3")})
        self.smallsmt.add({"tout": 0, "packet": smallsmtprotocol.SmallSmtCmd__SmtMode(smallsmtprotocol.SmallSmtCmd__SmtMode.MODE_BEGIN)})
        if self.smallsmt.send() != 0:
            self.executeRequestEpilog(-1)

    def execute_setEnabled(self,cmd):

        self.smallsmt.prepare()

        if cmd.cnv['value']==1:
            self.smallsmt.add({"tout": 1000, "packet": smallsmtprotocol.SmallSmtCmd__Online()})
            self.smallsmt.add({"tout":  0, "packet": smallsmtprotocol.SmallSmtCmd__SmtMode(smallsmtprotocol.SmallSmtCmd__SmtMode.MODE_BEGIN)})
        else:
            self.smallsmt.add({"tout": 0, "packet": smallsmtprotocol.SmallSmtCmd__SmtMode(smallsmtprotocol.SmallSmtCmd__SmtMode.MODE_STOP)})

        if self.smallsmt.send() != 0:
            self.executeRequestEpilog(0)




    def execute_moveTo(self,cmd):

        head_ok = 0
        stepsXYA_ok = 0

        speedFactor = cmd.cnv['speed']

        # Select speed template
        # There is global template ( no components picked) local templates ( select in feeder config )

        speedTemplate = self.machineFullConfig.machineConfig.SpeedSettings.SpeedGlobalIdle

        if self.pick_active != 0:
            speed_template_idx = -1
            if (self.pick_feeder >= 1000) and (self.pick_feeder <= 1999):
                feeder_idx = self.pick_feeder - 1000
                if len(self.machineFullConfig.machineConfig.Feder1W.Feeders) < feeder_idx:
                    speed_template_idx = self.machineFullConfig.machineConfig.Feder1W.Feeders[feeder_idx].SpeedTemplate_b
            elif  (self.pick_feeder >= 2000) and (self.pick_feeder <= 2999):
                feeder_idx = self.pick_feeder - 2000
                if len(self.machineFullConfig.machineConfig.Feder2N.Feeders) < feeder_idx:
                    speed_template_idx = self.machineFullConfig.machineConfig.Feder2N.Feeders[feeder_idx].SpeedTemplate_b
            elif (self.pick_feeder >= 2000) and (self.pick_feeder <= 2999):
                feeder_idx = self.pick_feeder - 2000
                if len(self.machineFullConfig.machineConfig.Feder3E.Feeders) < feeder_idx:
                    speed_template_idx = self.machineFullConfig.machineConfig.Feder3E.Feeders[feeder_idx].SpeedTemplate_b

            if speed_template_idx >= 0:
                if len(self.machineFullConfig.machineConfig.SpeedSettings.SpeedTemplates) > speed_template_idx:
                    speedTemplate = self.machineFullConfig.machineConfig.SpeedSettings.SpeedTemplates[speed_template_idx]


        self.coords.MoveToInit()

        # Processing global axis X
        self.coords.MoveToX(cmd.cnv['X'])
        if self.coords.X.steps_delta != 0:
            stepsXYA_ok = 1
            stepsX = self.coords.X.steps_delta
            startSpeedX = speedTemplate.AxisXY.StartSpeed_b
            runSpeedX = speedTemplate.AxisXY.RunSpeed_b
        else:
            stepsX = 0
            startSpeedX = 0
            runSpeedX = 0

        # Processing global axis Y
        self.coords.MoveToY(cmd.cnv['Y'])
        if self.coords.Y.steps_delta != 0:
            stepsXYA_ok = 1
            stepsY = self.coords.Y.steps_delta
            startSpeedY = speedTemplate.AxisXY.StartSpeed_b
            runSpeedY = speedTemplate.AxisXY.RunSpeed_b
        else:
            stepsY = 0
            startSpeedY = 0
            runSpeedY = 0


        # Default values
        stepsZ12 = 0
        startSpeedZ12 = 0
        runSpeedZ12 = 0

        stepsA1 = 0
        startSpeedA1 = 0
        runSpeedA1 = 0
        stepsA2 = 0
        startSpeedA2 = 0
        runSpeedA2 = 0
        stepsA3 = 0
        startSpeedA3 = 0
        runSpeedA3 = 0
        stepsA4 = 0
        startSpeedA4 = 0
        runSpeedA4 = 0


        if cmd.cnv['base'] == 'N1' or cmd.cnv['base'] == 'DOWN':
            head_ok = 1

            # Controlled by Z1. (shared Z1 / Z2 mechanical arangement)
            # Also Safe_Z movement uses this case
            # Note different Z direction
            self.coords.MoveToZ12(-cmd.cnv['Z'])

            if self.coords.Z12.steps_delta != 0:
                stepsZ12 = self.coords.Z12.steps_delta
                startSpeedZ12 = speedTemplate.AxisZ.StartSpeed_b
                runSpeedZ12 = speedTemplate.AxisZ.RunSpeed_b

            self.coords.MoveToC1(cmd.cnv['C'])

            if self.coords.C1.steps_delta != 0:
                stepsXYA_ok = 1
                stepsA1 = self.coords.C1.steps_delta
                startSpeedA1 = speedTemplate.AxisC.StartSpeed_b
                runSpeedA1 = speedTemplate.AxisC.RunSpeed_b


        if cmd.cnv['base'] == 'N2':
            head_ok = 1

            # Controlled by Z1. (shared Z1 / Z2 mechanical arangement)
            self.coords.MoveToZ12(-cmd.cnv['Z'])

            if self.coords.Z12.steps_delta != 0:
                stepsZ12 = self.coords.Z12.steps_delta
                startSpeedZ12 = speedTemplate.AxisZ.StartSpeed_b
                runSpeedZ12 = speedTemplate.AxisZ.RunSpeed_b


            self.coords.MoveToC2(cmd.cnv['C'])

            if self.coords.C2.steps_delta != 0:
                stepsXYA_ok = 1
                stepsA2 = self.coords.C2.steps_delta
                startSpeedA2 = speedTemplate.AxisC.StartSpeed_b
                runSpeedA2 = speedTemplate.AxisC.RunSpeed_b

        #
        #   Currently only dual axis machines supported
        #
        if cmd.cnv['base'] == 'N3' or cmd.cnv['base'] == 'N4':
            self.openPnpLog.emit("ERROR: Currently only dual axis machines supported")
            self.executeRequestEpilog(0)
            return


        if head_ok != 1:
            self.openPnpLog.emit("ERROR: Unsupported head movement")
            self.executeRequestEpilog(0)
            return



        # Prepare microcode for machine movement
        self.smallsmt.prepare()

        # If there is Z movement - execute it first
        if stepsZ12 != 0:

            packet = smallsmtprotocol.SmallSmtCmd__Move(smallsmtprotocol.SmallSmtCmd__Move.MOTOR_ZAXIS1,
                                                        stepsZ12,
                                                        self.scaleStartSpeed(startSpeedZ12,speedFactor),
                                                        self.scaleRunSpeed(runSpeedZ12,speedFactor))
            self.smallsmt.add({"tout": 5000, "packet": packet})


        if stepsXYA_ok !=0:
            # Now execute remaining X/Y and C movement
            packet = smallsmtprotocol.SmallSmtCmd__MultiMove(stepsX,
                                                         self.scaleStartSpeed(startSpeedX,speedFactor),
                                                         self.scaleRunSpeed(runSpeedX,speedFactor),
                                                         stepsY,
                                                         self.scaleStartSpeed(startSpeedY,speedFactor),
                                                         self.scaleRunSpeed(runSpeedY,speedFactor),
                                                         stepsA1,
                                                         self.scaleStartSpeed(startSpeedA1,speedFactor),
                                                         self.scaleRunSpeed(runSpeedA1,speedFactor),
                                                         stepsA2,
                                                         self.scaleStartSpeed(startSpeedA2,speedFactor),
                                                         self.scaleRunSpeed(runSpeedA2,speedFactor),
                                                         stepsA3,
                                                         self.scaleStartSpeed(startSpeedA3,speedFactor),
                                                         self.scaleRunSpeed(runSpeedA3,speedFactor),
                                                         stepsA4,
                                                         self.scaleStartSpeed(startSpeedA4,speedFactor),
                                                         self.scaleRunSpeed(runSpeedA4,speedFactor))
            self.smallsmt.add({"tout": 15000, "packet": packet})

        # Make sure we  actually have something to be sent
        if self.smallsmt.notEmpty():
            if self.smallsmt.send() != 0:
                self.executeRequestEpilog(0)
        else:
            # Nothing to do is a success
            self.executeRequestEpilog(1)

    def execute_actuateSet(self,cmd):

        # Prepare microcode for machine movement
        self.smallsmt.prepare()

        if cmd.cnv['actuator'] == 'CAM_DOWN':
            value = self.limit(float(cmd.cnv['value']),0,255)
            if value ==0:
                value = self.machineFullConfig.machineConfig.CameraLight.LightDown_b
            packet = smallsmtprotocol.SmallSmtCmd__CameraMux(smallsmtprotocol.SmallSmtCmd__CameraMux.CAM_DOWN,value)
            self.smallsmt.add({"tout": 1000, "packet": packet})
        elif cmd.cnv['actuator'] == 'CAM1_UP':
            value = self.limit(float(cmd.cnv['value']),0,255)
            if value ==0:
                value = self.machineFullConfig.machineConfig.CameraLight.LightUp1_b
            packet = smallsmtprotocol.SmallSmtCmd__CameraMux(smallsmtprotocol.SmallSmtCmd__CameraMux.CAM_UP_LEFT,value)
            self.smallsmt.add({"tout": 1000, "packet": packet})
        elif cmd.cnv['actuator'] == 'CAM2_UP':
            value = self.limit(float(cmd.cnv['value']),0,255)
            if value ==0:
                value = self.machineFullConfig.machineConfig.CameraLight.LightUp2_b
            packet = smallsmtprotocol.SmallSmtCmd__CameraMux(smallsmtprotocol.SmallSmtCmd__CameraMux.CAM_UP_RIGHT,value)
            self.smallsmt.add({"tout": 1000, "packet": packet})
        elif cmd.cnv['actuator'] == 'NEEDLE':

            new_value = self.checkOnOff(cmd.cnv['value'])

            if new_value != self.needle_state:

                # When changing state - either restore previous position ( ON->OFF)
                #                       or go to lower park position
                self.needle_state = new_value

                self.coords.MoveToInit()

                if new_value == 0:
                    self.coords.MoveToZ12(self.needle_prev_value)
                else:
                    self.needle_prev_value = self.coords.Z12.value
                    self.coords.MoveToZ12(self.machineFullConfig.machineConfig.Needle.position_f)


                if self.coords.Z12.steps_delta != 0:
                    stepsZ12 = self.coords.Z12.steps_delta
                    startSpeedZ12 = self.machineFullConfig.machineConfig.Needle.Speed.StartSpeed_b
                    runSpeedZ12 = self.machineFullConfig.machineConfig.Needle.Speed.RunSpeed_b

                    packet = smallsmtprotocol.SmallSmtCmd__Move(smallsmtprotocol.SmallSmtCmd__MoveMOTOR_ZAXIS1,
                                                                stepsZ12,
                                                                startSpeedZ12,
                                                                runSpeedZ12)
                    self.smallsmt.add({"tout": 5000, "packet": packet})


        elif cmd.cnv['actuator'] == 'FEEDER_F1W':
            self.pick_feeder = 1000 + int(round(cmd.cnv['value']))
        elif cmd.cnv['actuator'] == 'FEEDER_F2N':
            self.pick_feeder = 2000 + int(round(cmd.cnv['value']))
        elif cmd.cnv['actuator'] == 'FEEDER_F3E':
            self.pick_feeder = 3000 +int(round(cmd.cnv['value']))
        elif cmd.cnv['actuator'] == 'VALVE_VACUUM1':
            packet = smallsmtprotocol.SmallSmtCmd__Solenoid(smallsmtprotocol.SmallSmtCmd__Solenoid.PORT_VACUUM1,self.checkOnOff(cmd.cnv['value']))
            self.smallsmt.add({"tout": 1000, "packet": packet})
        elif cmd.cnv['actuator'] == 'VALVE_VACUUM2':
            packet = smallsmtprotocol.SmallSmtCmd__Solenoid(smallsmtprotocol.SmallSmtCmd__Solenoid.PORT_VACUUM1,self.checkOnOff(cmd.cnv['value']))
            self.smallsmt.add({"tout": 1000, "packet": packet})
        elif cmd.cnv['actuator'] == 'RELAY_VIBRATION':
            packet = smallsmtprotocol.SmallSmtCmd__Solenoid(smallsmtprotocol.SmallSmtCmd__Solenoid.PORT_VIBRATION,self.checkOnOff(float(cmd.cnv['value'])))
            self.smallsmt.add({"tout": 1000, "packet": packet})
        else:
            self.openPnpLog.emit("ERROR: Unsupported actuator(set)")
            self.executeRequestEpilog(0)
            return

        if self.smallsmt.notEmpty():
            # Operations to be sent
            if self.smallsmt.send() != 0:
                self.executeRequestEpilog(0)
        else:
            # Nothing to sent
            self.executeRequestEpilog(1)


    def execute_actuateRead(self, cmd):

        self.smallsmt.prepare()
        self.update_read_value = self.UPDATE_VACUUM
        if cmd.cnv['actuator'] == 'SENSOR_VACUUM1':
            packet = smallsmtprotocol.SmallSmtCmd__ReadVacum(smallsmtprotocol.SmallSmtCmd__ReadVacum.HEAD_NOZZLE1)
            self.smallsmt.add({"tout": 1000, "packet": packet})
        elif cmd.cnv['actuator'] == 'SENSOR_VACUUM2':
            packet = smallsmtprotocol.SmallSmtCmd__ReadVacum(smallsmtprotocol.SmallSmtCmd__ReadVacum.HEAD_NOZZLE2)
            self.smallsmt.add({"tout": 1000, "packet": packet})
        else:
            self.openPnpLog.emit("ERROR: Unsupported actuator(get)")
            self.executeRequestEpilog(0)
            return

        if self.smallsmt.send() != 0:
            self.executeRequestEpilog(0)


    def execute_pick(self, cmd):

        self.smallsmt.prepare()

        self.pick_active = 1

        # Turn on vacuum solenoid
        if cmd.cnv['nozzle'] == 'N1':
            packet = smallsmtprotocol.SmallSmtCmd__Solenoid(smallsmtprotocol.SmallSmtCmd__Solenoid.PORT_VACUUM1,1)
            self.smallsmt.add({"tout": 1000, "packet": packet})
        elif cmd.cnv['actuator'] == 'N2':
            packet = smallsmtprotocol.SmallSmtCmd__Solenoid(smallsmtprotocol.SmallSmtCmd__Solenoid.PORT_VACUUM2,1)
            self.smallsmt.add({"tout": 1000, "packet": packet})
        else:
            self.openPnpLog.emit("ERROR: Unsupported nozzle for pick")
            self.executeRequestEpilog(0)
            return

        if self.smallsmt.send() != 0:
            self.executeRequestEpilog(0)

    def execute_place(self, cmd):

        self.pick_active = 0

        self.smallsmt.prepare()

        # Turn off vacuum solenoid
        if cmd.cnv['nozzle'] == 'N1':
            packet = smallsmtprotocol.SmallSmtCmd__Solenoid(smallsmtprotocol.SmallSmtCmd__Solenoid.PORT_VACUUM1, 0)
            self.smallsmt.add({"tout": 0, "packet": packet})
        elif cmd.cnv['nozzle'] == 'N2':
            packet = smallsmtprotocol.SmallSmtCmd__Solenoid(smallsmtprotocol.SmallSmtCmd__Solenoid.PORT_VACUUM2, 0)
            self.smallsmt.add({"tout": 0, "packet": packet})
        else:
            self.openPnpLog.emit("ERROR: Unsupported nozzle for place")
            self.executeRequestEpilog(0)
            return

        if self.smallsmt.send() != 0:
            self.executeRequestEpilog(0)