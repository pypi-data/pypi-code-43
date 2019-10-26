##############################################
# The MIT License (MIT)
# Copyright (c) 2019 Kevin Walchko
# see LICENSE for full details
##############################################

from pygeckopb.msgs_pb2 import Twist, Vector, Wrench, Quaternion, Transform
from pygeckopb.msgs_pb2 import Imu, ImuInfo, LaserScan, LaserPt, NavSatFix
from pygeckopb.msgs_pb2 import Image, CameraInfo, BatteryState, Range
from pygeckopb.msgs_pb2 import Odometry, Pose, OccupancyGrid, Path


def protobufPack(msg):
    return msg.SerializeToString()


def protobufUnpack(s, cls):
    m = cls()
    m.ParseFromString(s)
    return m


__author__ = 'Kevin Walchko'
__license__ = "MIT"
__version__ = "0.0.1"
