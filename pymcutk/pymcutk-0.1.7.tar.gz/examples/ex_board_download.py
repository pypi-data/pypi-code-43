"""
This example show how to use mcutk.board & mcutk.debugger
to download image to board.
"""
import os
import signal
import sys
import time
import subprocess

sys.path.append("./../")

from mcutk.board import getboard
from mcutk.debugger.jlink import JLINK

# get jlink instance
jlink = JLINK.get_latest()
# set gdb path
jlink.gdbpath = "C:/MinGW/bin/gdb.exe"
# get a mcutk.board object
board = getboard("lpcxpresso54018", devicename="lpcxpresso54018", usbid="621000000")
# bind jlink debugger to frdmkl43z board
board.debugger = jlink
# register a callback that will be executed before loading image.
@board.debugger.register("before-load")
def callback(a=1, b=2):
    print a, b
    print "Callback is called"
    print "Callback end"

print board
print board.programming("C:\\Dpc\\FreeMV\\system\\app_data\\binaries\\frdmkl43z.out")[0]

