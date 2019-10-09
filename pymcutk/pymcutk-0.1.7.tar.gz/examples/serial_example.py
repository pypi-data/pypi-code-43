import serial
import pexpect
import sys
import time

sys.path.append("./../")

from mcutk.pserial import Serial
from mcutk.board import getboard
from mcutk.debugger.jlink import JLINK


jlinkd = JLINK.get_latest()
print jlinkd


board = getboard(
    "frdmkl43z",
    devicename="MKL43Z256xxx4",
    usbid="621000000",
    debugger_type="jlink"
    )

board.debugger = jlinkd
board.debugger.reset()

time.sleep(1)
ser = Serial('COM20', 9600, timeout=0.1)
ser.start_reader()
time.sleep(1)
ser.write("A")
time.sleep(1)
print ser.data

spawn = ser.Spawn()

interacts = [
    {
        "input": "A",
        "expect": r"Waiting for power.mode select\.\."
    },
    {
        "input": "B",
        "expect": r"Select the wake up source.*Waiting for key press\.\."
    },
    {
        "input": "T",
        "expect": r"Select the wake up timeout in seconds.*Waiting for input timeout value",
    },
    {
        "input": "1",
        "expect": r"Waiting for power.mode select.",
    },
]

# spawn.logfile_read = sys.stdout

for item in interacts:
    spawn.test_input(**item)
    time.sleep(0.2)

spawn.flush_log()
print ser.data

spawn.expect([pexpect.EOF, pexpect.TIMEOUT])
spawn.close()



