import sys
import serial
import time
import re
from datetime import datetime
import serial.tools.list_ports

global baudrate_
global debug_

def findCom(debug = 0,  useAnyDriver = True, driver = ['FTDI','Moxa Inc.'] ):
    global debug_
    global baudrate_
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if useAnyDriver or p.manufacturer in driver:
            baudrate_ = 38400
            debug_ = debug
            try:
                with serial.Serial(p.device, baudrate_, timeout=1) as ser:
                        writeAndRead(ser, "PING", maxattemps=1)
                        return p.device
            except:
                pass
    return None

#simple get telegrams
def getData(port):
    global baudrate_
    with serial.Serial(port, baudrate_, timeout=1) as ser:
        line = writeAndRead(ser, "GETDATA") 
        stringList = line.decode('latin-1').split(":")
        return stringList[:-1]

def writeAndRead(ser, command, maxattemps = 20, ignoreError = 0):
    command = command + "\n"
    command = command.encode()
    global debug_
    if debug_ == 1:
        print("{:<6} {:<6} {:}".format(ser.name, "Write", command))
    resend = 0
    while resend<2:
        resend = resend + 1    
        ser.write(command)
        attempts = 0
        val = b''
        while attempts < maxattemps+1:
            attempts = attempts + 1
            line = ser.readline()
            val = val + line
            if val[-2:] == b'#\n':
                if debug_ == 1:
                    print("{:<6} {:<6} {:}".format(ser.name, "Read", val))
                return val[:-3]
            if val[-2:] == b'!\n':
                if val[-3:] == b'^!\n':
                    print('Recieved ^!-reply from device -> Resend:{:}'.format(command))
                    resend = 0
                    break
                if (resend<1):
                    #debug_ = 1
                    print('Recieved !-reply from device. Resend initiated.')
                    continue
                if ignoreError == 0:
                    raise RuntimeError('Recieved !-reply from device.')
                return val[:-3]    
            if val[-2:] == b'^':
                print('Recieved ^-reply from device -> Resend:{:}'.format(command))
                resend = 0
                break

        if (maxattemps>1 and resend>0):
            time.sleep(8)
    if ignoreError == 0:
        raise RuntimeError('No response from device, ' + command.decode(), ', resend = {:}'.format(resend))

if __name__ == '__main__':
    port = findCom()