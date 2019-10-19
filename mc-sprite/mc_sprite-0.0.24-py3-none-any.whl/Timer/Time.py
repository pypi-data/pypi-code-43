import time as pt
class Time(object):
    time=0
    deltaTime=0
    fps = 1/60
    def __init__(self):
        self.oldTime=0
        self.newTime=0
    def CalculationDeltaTime(self):
        self.oldTime=self.newTime
        self.newTime=pt.time()
        temp=self.newTime-self.oldTime
        if temp <Time.fps:
            pt.sleep(Time.fps-temp)
            self.newTime=pt.time()
        Time.deltaTime=self.newTime-self.oldTime
        if Time.deltaTime>100:
            Time.deltaTime=0
        Time.time+=Time.deltaTime
    @staticmethod
    def SetFPS(fps: int):
        if fps>0:
            Time.fps=1/fps