

class BBSystem:

    def __init__(self):
        self.mixerMode = 0
        self.mixerModeVar = 0 #todo
        self.mixerSetpoint = 0
        self.mixerSetpointVar = '001_d_mixer001inp1'
        self.mixerFlow = 0
        self.mixerFlowVar = '001_d_mixer001inp2'
        self.mixerReturn = 0
        self.mixerReturnVar = '001_d_mixer001inp3'
        self.outsideTemperature = 0
        self.outsideTemperatureVar = '001_d_mixer001inp5'
        self.mixerPumpState = 0
        self.mixerPumpStateVar = '001_d_mixer001inp7'
        self.mixerMixerState = 0
        self.mixerMixerStateVar = '001_d_mixer001inp11'
        self.bufferTop = 0
        self.bufferTopVar = '001_d_display001inp1'
        self.bufferMidTop = 0
        self.bufferMidTopVar = '001_d_display001inp2'
        self.bufferMidBottom = 0
        self.bufferMidBottomVar = '001_d_display001inp3'
        self.bufferBottom = 0
        self.bufferMidBottomVar = '001_d_display001inp4'
        self.circulationMode = 0
        self.circulationModeVar = 0 #todo
        self.circulationFlow = 0
        self.circulationFlowVar = '001_d_display002inp1'
        self.circulationReturn = 0
        self.circulationReturnVar = '001_d_display002inp2'
        self.heatcirculationMode = 0
        self.heatcirculationModeVar = '001_d_pump001inp2'
        self.heatcirculationMaxValve = 0
        self.heatcirculationMaxValveVar = '001_d_pump001inp1'
        self.heatcirculationPumpOut = 0
        self.heatcirculationPumpOutVar = '001_d_pump001out1'
        self.heatcirculationState = 0
        self.heatcirculationStateVar = '001_d_pump001out2'
        self.heatpumpMode = 0
        self.heatpumpModeVar = '' #todo
        self.heatpumpState = 0
        self.heatpumpStateVar = '001_d_param001inp1'
        self.heatpumpHeat = 0
        self.heatpumpHeatVar = '001_d_param001inp2'
        self.heatpumpFlow = 0
        self.heatpumpFlowVar = '001_d_param001inp3'
        self.heatpumpReturn = 0
        self.heatpumpReturnVar = '001_d_param001inp4'
        self.heatpumpSetpoint = 0
        self.heatpumpSetpointVar = '001_d_param001inp5'
        self.heatpumpvalveState = 0
        self.heatpumpvalveStateVar = ''  # todo
        self.heatpumpvalveMode = 0
        self.heatpumpvalveModeVar = ''  # todo


    def update(self, json):
        #self.mixerMode = json[self.mixerModeVar]
        self.mixerSetpoint = json[self.mixerSetpointVar]
        self.mixerFlow = json[self.mixerFlowVar]
        self.mixerReturn = json[self.mixerReturnVar]
        self.outsideTemperature = json[self.outsideTemperatureVar]
        self.mixerPumpState = json[self.mixerPumpStateVar]
        self.mixerMixerState = json[self.mixerMixerStateVar]
        self.bufferTop = json[self.bufferTopVar]
        self.bufferMidTop = json[self.bufferMidTopVar]
        self.bufferMidBottom = json[self.bufferMidBottomVar]
        self.bufferBottom = json[self.bufferMidBottomVar]
        #self.circulationMode = json[self.circulationModeVar]
        self.circulationFlow = json[self.circulationFlowVar]
        self.circulationReturn = json[self.circulationReturnVar]
        self.heatcirculationMode = json[self.heatcirculationModeVar]
        self.heatcirculationMaxValve = json[self.heatcirculationMaxValveVar]
        self.heatcirculationPumpOut = json[self.heatcirculationPumpOutVar]
        self.heatcirculationState = json[self.heatcirculationStateVar]
        #self.heatpumpMode = json[self.heatpumpModeVar]
        self.heatpumpState = json[self.heatpumpStateVar]
        self.heatpumpHeat = json[self.heatpumpHeatVar]
        self.heatpumpFlow = json[self.heatpumpFlowVar]
        self.heatpumpReturn = json[self.heatpumpReturnVar]
        self.heatpumpSetpoint = json[self.heatpumpSetpointVar]
        #self.heatpumpvalveState = json[self.heatpumpvalveStateVar]
        #self.heatpumpvalveMode = json[self.heatpumpvalveModeVar]


