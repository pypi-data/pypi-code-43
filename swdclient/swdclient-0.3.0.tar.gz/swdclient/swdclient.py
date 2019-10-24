from ctypes import *
from swdclient.server_pb2 import *
import numpy as np
# from server_pb2 import *
import os

lib_path = os.path.abspath(__file__).replace("swdclient.py","libswd.so")

lib = CDLL(lib_path)


PARAM_C = [-1,-1,-1]
PARAM_T = [1,0,2]
def set_C(c):
    global PARAM_C
    PARAM_C = c

def set_T(t):
    global PARAM_T
    PARAM_T = t

class Point():
    def __init__(self,x=0,y=0,z=0):
        self.x = x;
        self.y = y;
        self.z = z;

    def to_arr(self):
        return [self.x,self.y,self.z]

    def from_arr(self,arr):
        self.x = arr[0]
        self.y = arr[1]
        self.z = arr[2]

    def h2u(self,):
        v = self.to_arr()
        arr = []
        for i in range(3):
            arr.append(v[PARAM_T[i]] * PARAM_C[i])
        self.from_arr(arr)
        # return arr

    def u2h(self):
        v = self.to_arr()
        arr = [0,0,0]
        for i in range(3):
            arr[PARAM_T[i]] = v[i] * PARAM_C[i]
        self.from_arr(arr)
        # return arr


# lib.test()

# class SwdClient:
def start(ip = "127.0.0.1",port = 21567):
    lib.start(str(ip).encode() ,port)

lib.getData.argtypes=[POINTER(c_int)]
lib.getData.restype=POINTER(c_char)

def deal_data(measurements):
    print(measurements)
    temp = Point(measurements.transform.location.x,measurements.transform.location.y,measurements.transform.location.z)
    temp.h2u()
    measurements.transform.location.x = temp.x
    measurements.transform.location.y = temp.y
    measurements.transform.location.z = temp.z

    temp = Point(measurements.transform.rotation.roll,measurements.transform.rotation.pitch,measurements.transform.rotation.yaw)
    temp.h2u()
    measurements.transform.rotation.roll = temp.x
    measurements.transform.rotation.pitch = temp.y
    measurements.transform.rotation.yaw = temp.z

    temp = Point(measurements.motionstatus.velocity.x,measurements.motionstatus.velocity.y,measurements.motionstatus.velocity.z)
    temp.h2u()
    measurements.motionstatus.velocity.x = temp.x
    measurements.motionstatus.velocity.y = temp.y
    measurements.motionstatus.velocity.z = temp.z
    temp = Point(measurements.motionstatus.accelerity.x,measurements.motionstatus.accelerity.y,measurements.motionstatus.accelerity.z)
    temp.h2u()
    measurements.motionstatus.accelerity.x = temp.x
    measurements.motionstatus.accelerity.y = temp.y
    measurements.motionstatus.accelerity.z = temp.z
    temp = Point(measurements.motionstatus.angular_velocity.x,measurements.motionstatus.angular_velocity.y,measurements.motionstatus.angular_velocity.z)
    temp.h2u()
    measurements.motionstatus.angular_velocity.x = temp.x
    measurements.motionstatus.angular_velocity.y = temp.y
    measurements.motionstatus.angular_velocity.z = temp.z


    for i in range(len(measurements.objects)):
        if measurements.objects[i].WhichOneof("object") == "pedestrian":

            temp = Point(measurements.objects[i].pedestrian.velocity.x,measurements.objects[i].pedestrian.velocity.y,measurements.objects[i].pedestrian.velocity.z)
            temp.h2u()
            measurements.objects[i].pedestrian.velocity.x = temp.x
            measurements.objects[i].pedestrian.velocity.y = temp.y
            measurements.objects[i].pedestrian.velocity.z = temp.z
            temp = Point(measurements.objects[i].pedestrian.accelerity.x,measurements.objects[i].pedestrian.accelerity.y,measurements.objects[i].pedestrian.accelerity.z)
            temp.h2u()
            measurements.objects[i].pedestrian.accelerity.x = temp.x
            measurements.objects[i].pedestrian.accelerity.y = temp.y
            measurements.objects[i].pedestrian.accelerity.z = temp.z

        elif measurements.objects[i].WhichOneof("object") == "vehicle":

            temp = Point(measurements.objects[i].vehicle.velocity.x,measurements.objects[i].vehicle.velocity.y,measurements.objects[i].vehicle.velocity.z)
            temp.h2u()
            measurements.objects[i].vehicle.velocity.x = temp.x
            measurements.objects[i].vehicle.velocity.y = temp.y
            measurements.objects[i].vehicle.velocity.z = temp.z
            temp = Point(measurements.objects[i].vehicle.accelerity.x,measurements.objects[i].vehicle.accelerity.y,measurements.objects[i].vehicle.accelerity.z)
            temp.h2u()
            measurements.objects[i].vehicle.accelerity.x = temp.x
            measurements.objects[i].vehicle.accelerity.y = temp.y
            measurements.objects[i].vehicle.accelerity.z = temp.z

        temp = Point(measurements.objects[i].transform.location.x,measurements.objects[i].transform.location.y,measurements.objects[i].transform.location.z)
        temp.h2u()
        measurements.objects[i].transform.location.x = temp.x
        measurements.objects[i].transform.location.y = temp.y
        measurements.objects[i].transform.location.z = temp.z

        temp = Point(measurements.objects[i].transform.rotation.roll,measurements.objects[i].transform.rotation.pitch,measurements.objects[i].transform.rotation.yaw)
        temp.h2u()
        measurements.objects[i].transform.rotation.roll = temp.x
        measurements.objects[i].transform.rotation.pitch = temp.y
        measurements.objects[i].transform.rotation.yaw = temp.z
    print(measurements)

def get_data():
    size = c_int(0)
    ptr = pointer(size)
    result = lib.getData(ptr)
    measurements = Measurements()
    measurements.ParseFromString(result[:size.value])

    return deal_data(measurements)

lib.sendData.argtypes=[c_float,c_float,c_float,c_bool,c_bool,c_float]
def control(throttle = 0,steer = 0,brake = 0,handBrake = False,reverse = False, speed = 0):
    lib.sendData(throttle,steer,brake,handBrake,reverse,speed)

def rotateMatrix(roll,pitch,yaw):
    a = np.deg2rad(roll)
    b = np.deg2rad(pitch)
    c = np.deg2rad(yaw)

    sa = np.sin(a)
    ca = np.cos(a)
    sb = np.sin(b)
    cb = np.cos(b)
    sc = np.sin(c)
    cc = np.cos(c)

    return np.array([
        [cb * cc, sb * sc, -sb],
        [-ca * sc + sa * sb * cc,  ca * cc + sa * sb *sc, sa * cb],
        [sa * sc + ca * sb * cc, -sa * cc + ca * sb * sc, ca * cb]
    ])

def world2body(item,matrix):
    vector = np.array([item.x,item.y,item.z])
    tmp = np.dot(matrix,vector)
    return Point(tmp[0],tmp[1],tmp[2])


def body2world(item,matrix):
    vector = np.array([item.x,item.y,item.z])
    tmp = np.dot(matrix.T,vector)
    return Point(tmp[0],tmp[1],tmp[2])

def test():
    start("192.168.30.185")
    import time
    time.sleep(2)
    set_C([1,1,1])
    set_T([0,1,2])
    get_data()
    # p = Point(1,2,3)
    # print(p.to_arr())
    # p.h2u()
    # print(p.to_arr())
    # p.u2h()
    # print(p.to_arr())
    # matrix = rotateMatrix(roll=45,pitch=30,yaw=0)
    # print(world2body(p,matrix).to_arr())
    # print()

test()