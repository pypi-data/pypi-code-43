#!/usr/bin/python3
#coding=utf8
import pigpio
import threading
import sys
import time

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

class CarMotor(object):
    def __init__(self, in1 = 26, in2 = 18, in3 = 7, in4 = 8):
        #4个电机引脚号,采用BCM编码
        self.Pi = pigpio.pi()
        self.In1 = in1
        self.In2 = in2
        self.In3 = in3
        self.In4 = in4

        self.Pi.set_PWM_range(self.In1, 100)#pwm范围
        self.Pi.set_PWM_range(self.In2, 100)
        self.Pi.set_PWM_range(self.In3, 100)
        self.Pi.set_PWM_range(self.In4, 100)

        self.Pi.set_PWM_frequency(self.In1, 10000)#频率10khz
        self.Pi.set_PWM_frequency(self.In2, 10000)
        self.Pi.set_PWM_frequency(self.In3, 10000)
        self.Pi.set_PWM_frequency(self.In4, 10000)

        self.Pi.set_PWM_dutycycle(self.In1, 0)#暂停pwm输出
        self.Pi.set_PWM_dutycycle(self.In2, 0)
        self.Pi.set_PWM_dutycycle(self.In3, 0)
        self.Pi.set_PWM_dutycycle(self.In4, 0)

    def SetSpeed(self, Left = 0, Right = 0):
        Left = -100  if Left < -100 else Left
        Left =  100  if Left >  100 else Left
        Right = 100  if Right > 100 else Right
        Right = -100 if Right < -100 else Right

        DutyIn1 = 0 if Left < 0 else Left
        DutyIn2 = 0 if Left > 0 else -Left
        DutyIn3 = 0 if Right < 0 else Right
        DutyIn4 = 0 if Right > 0 else -Right

        self.Pi.set_PWM_dutycycle(self.In1, DutyIn1)#开始pwm输出
        self.Pi.set_PWM_dutycycle(self.In2, DutyIn2)
        self.Pi.set_PWM_dutycycle(self.In3, DutyIn3)
        self.Pi.set_PWM_dutycycle(self.In4, DutyIn4)

if __name__ == "__main__":
        
    carmove = CarMotor()
    carmove.SetSpeed(0,0)
    #carmove.SetSpeed(100,100)
    # time.sleep(2)
    #carmove.SetSpeed(-100,100)
    # time.sleep(2)

