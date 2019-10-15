# import CarConf
from ddcmaker import CarMotor
import time
carM = CarMotor.CarMotor()

class car(object):
    def right(self, step, speed=50):
        carM.SetSpeed(speed, -speed)
        # time.sleep(step)
        print("小车右转" + str(step) + "秒")
        self.stop(step)

    def left(self, step, speed=50):
        carM.SetSpeed(-speed, speed)
        # time.sleep(step)
        print("小车左转" + str(step) + "秒")
        self.stop(step)

    def forward(self, step, speed=50):
        carM.SetSpeed(speed, speed)
        # time.sleep(step)
        print("小车前进" + str(step) + "秒")
        self.stop(step)

    def stop(self, step):
        time.sleep(step)
        carM.SetSpeed(0, 0)

    def backward(self, step, speed=50):
        carM.SetSpeed(-speed, -speed)
        # time.sleep(step)
        print("小车后退" + str(step) + "秒")
        self.stop(step)


