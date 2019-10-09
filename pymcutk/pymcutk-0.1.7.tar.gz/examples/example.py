import serial
import pexpect
import sys
import time

sys.path.append("./../")

from mcutk.pserial import Serial

ser = Serial('COM20', 9600, timeout=0.1)
spawn = ser.Spawn()

spawn.logfile_read = sys.stdout
spawn.sendline("version\r\n")
spawn.expect([UBOOT_EXPERT, pexpect.TIMEOUT])
logging.info(spawn.before)
spawn.sendline("res\r\n")
spawn.expect(['Hit any key to stop autoboot:', pexpect.TIMEOUT])
time.sleep(1)
spawn.sendline("a")
spawn.expect([UBOOT_EXPERT, pexpect.TIMEOUT])
logging.info(spawn.before)
serobj.close()




spawn.write("a")


try:
    spawn.expect("welcome", timeout=3)
except:
    return

spawn.write("a")
try:
    spawn.expect("welcome", timeout=3)
except:
    return

spawn.write("a")
try:
    spawn.expect("welcome", timeout=3)
except:
    return

spawn.expect([pexpect.EOF, pexpect.TIMEOUT])
spawn.close()



