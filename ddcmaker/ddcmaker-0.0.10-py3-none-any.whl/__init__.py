'''不要随意修改类名和参数名，谁改谁背锅！！！！'''
__version__ = '0.0.10'
__metaclass__ = type
__all__ = [
    'car', 'robot'
]
'''通过固定的文件夹判断设备的种类'''

import os
import subprocess
# 设置标志值，只有作者制定升级才允许升级



if os.path.exists('/home/pi/human') == True:
    #####-------------------------------薛定谔的猫---------------------------------------
    def update():
        save_path = "/home/pi/Car/resave"
        link = "https://test-1255999742.cos.ap-chengdu.myqcloud.com/maker/installrobot.sh"
        try:
            cmd = ("sudo wget -P  {} {}".format(save_path, link))
            ref = subprocess.call(cmd, shell=True)
            if ref != 0:
                print("can't get download")
            else:
                print("finishing downloading ! ")
        except Exception as e:
            print("失败是成功之母，我们下个版本见！bye~")
    #####-------------------------------量子塌陷之前状态同时存在---------------------------------------
    from ddcmaker import robot
    from ddcmaker import showlib
    Rb = robot.robot()
    Sh = showlib.showlib()


    class Robot(object):

        @staticmethod
        def left(step=1):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Rb.left(step)

        @staticmethod
        def right(step=1):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Rb.right(step)

        @staticmethod
        def left_slide(step=1):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Rb.left_slide(step)

        @staticmethod
        def right_slide(step=1):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Rb.right_slide(step)

        @staticmethod
        def forward(step=1):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Rb.forward(step)

        @staticmethod
        def backward(step=1):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Rb.backward(step)

        @staticmethod
        def up(step=1):
            if step > 1:
                step = 1
                print("参数值超过设置上限，默认运行最大上限次数 1")
            Rb.up(step)

        @staticmethod
        def down(step=1):
            if step > 1:
                step = 1
                print("参数值超过设置上限，默认运行最大上限次数 1")
            Rb.down(step)

        @staticmethod
        def check(step=1):
            if step > 1:
                step = 1
                print("参数值超过设置上限，默认运行最大上限次数 1")
            Rb.check(step)

        # @staticmethod
        # def circle(step, radius):
        #     step = 10 if step > 10 else step
        #     Rb.circle(step, radius)

        @staticmethod
        def nod(step=1):
            if step>30:
                step=30
                print("参数值超过设置上限，默认运行最大上限次数 ",step)
            Rb.nod(step)

        @staticmethod
        def shaking_head(step=1):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Rb.shaking_head(step)

        '''虚不实真，苦切一除能，咒等等无是，咒上无是，咒明大是'''

        @staticmethod
        def hiphop():
            Sh.hiphop()

        @staticmethod
        def smallapple():
            Sh.smallapple()

        @staticmethod
        def jiangnanstyle():
            Sh.jiangnanstyle()

        @staticmethod
        def lasong():
            Sh.lasong()

        @staticmethod
        def feelgood():
            Sh.feelgood()

        '''无法兼容白色机器人，在调用时进行机器人判断'''

if os.path.exists('/home/pi/Car') == True:
    #####-------------------------------正弦波是微观世界的基本单位---------------------------------------
    def update():
        save_path = "/home/pi/Car/resave"
        link = "https://test-1255999742.cos.ap-chengdu.myqcloud.com/maker/installrobot.sh"
        try:
            cmd = ("sudo wget -P  {} {}".format(save_path, link))
            ref = subprocess.call(cmd, shell=True)
            if ref != 0:
                print("can't get download")
            else:
                print("finishing downloading ! ")
        except Exception as e:
            print("失败是成功之母，我们下个版本见！bye~")
    #####-------------------------------波粒二象性是双缝干涉发现的---------------------------------------
    from ddcmaker import car
    Ca = car.car()

    class Car(object):

        @staticmethod
        def left(step=1, speed=50):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Ca.left(step, speed)

        @staticmethod
        def right(step=1, speed=50):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Ca.right(step, speed)

        @staticmethod
        def forward(step=1, speed=50):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Ca.forward(step, speed)

        @staticmethod
        def backward(step=1, speed=50):
            if step > 30:
                step = 30
                print("参数值超过设置上限，默认运行最大上限次数 ", step)
            Ca.backward(step, speed)


