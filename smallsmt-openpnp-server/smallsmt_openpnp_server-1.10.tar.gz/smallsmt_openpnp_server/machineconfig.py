import configtreeview


class CoordInfo:
    def __init__(self,cnv=1,min=0,max=0):
        self.Cnv_PulseToMm_f8 = cnv
        self.Min_f3 = min
        self.Max_f3 = max


class SpeedInfo:
    def __init__(self,start=5,stop=15):
        self.StartSpeed_b = start
        self.RunSpeed_b = stop

class MachineRange:
    def __init__(self):
        # Base coordinates
        self.X = CoordInfo(1/34.86,0,358.0)
        self.Y = CoordInfo(1/34.86,-330.0,0.0)

        # Heads
        self.Z12 = CoordInfo(1/44.52,0,15.0)
        self.Z34 = CoordInfo(1/44.52,0,15.0)
        self.C1 = CoordInfo(1/17.776)
        self.C2 = CoordInfo(1/17.776)
        self.C3 = CoordInfo(1/17.776)
        self.C4 = CoordInfo(1/17.776)

        # Feeders
        self.F1W = CoordInfo(1/34.85)
        self.F2N = CoordInfo(1/34.85)
        self.F3E = CoordInfo(1/34.85)




class FeedTemplates:
    def __init__(self,cnt):
        self.position_f = []
        for i in range(cnt):
            self.position_f.append(0)


class SpeedTemplate:
    def __init__(self):
        self.AxisXY = SpeedInfo()
        self.AxisZ = SpeedInfo()
        self.AxisC = SpeedInfo()


class SpeedTemplates:
    def __init__(self,cnt):
        self.SpeedGlobalIdle = SpeedTemplate()
        self.SpeedTemplates = []
        for i in range(cnt):
            self.SpeedTemplates.append(SpeedTemplate())


class SideFeederConfig:
    def __init__(self):
        self.Position_f = 0
        self.ControlTemplate_b = 0


class SideFeederControlConfig:
    def __init__(self):
        self.startSpeed_b = 5
        self.runSpeed_b = 15
        self.openLength_w = 3
        self.closeLength_w = 3
        self.openCloseStartSpeed_b = 5
        self.openCloseRunSpeed_b = 5
        self.feedTime_w = 5
        self.pushCount_b = 1

class SideFeedersArray:
    def __init__(self,cnt):
        self.Feeders = []
        for i in range(cnt):
            self.Feeders.append(SideFeederConfig())

class SideFeederControlConfigArray:
    def __init__(self,cnt):
        self.ControlTemplates = []
        for i in range(cnt):
            self.ControlTemplates.append(SideFeederControlConfig())

class NeedleSetup:
    def __init__(self):
        self.Speed = SpeedInfo()
        self.position_f = 10


class GlobalConfig:
    def __init__(self):
        self.Axes = MachineRange()

class CameraLightConfig:
    def __init__(self):
        self.LightDown_b = 255
        self.LightUp1_b = 255
        self.LigthUp2_b = 255


class MachineConfig:
    def __init__(self):
        self.CameraLight = CameraLightConfig()
        self.Needle = NeedleSetup()
        self.SpeedSettings = SpeedTemplates(5)
        self.FeederControl = SideFeederControlConfigArray(10)
        self.Feder1W = SideFeedersArray(32)
        self.Feder2N = SideFeedersArray(32)
        self.Feder3E = SideFeedersArray(32)
