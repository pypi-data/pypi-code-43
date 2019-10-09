# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 08:16:38 2019

@author: Markus
"""
import serial.tools.list_ports
import serial
import threading
import numpy
import time

SamplingFrequency= ["100k", "50k", "20k", "10k", "5k", "2k", "1k",
                    "500", "200", "100", "50", "20", "10", "5", "2", "1"]

class LPM01:
    def __init__(self, comport=None, comPID=22336):
        if comport == None:
            for comp in serial.tools.list_ports.comports():
                if comp.pid == comPID:
                    comport = comp.device

        if comport == None:
            raise RuntimeError("no LPM01 device with PID %d found"%comPID)

        self.ser = serial.Serial(port=comport, baudrate=3686400, bytesize=8,
                            parity='N', stopbits=1, timeout=5.0,
                            xonxoff=0, rtscts=0)


        if self.ser.in_waiting > 0:
            self.ser.read_all()

        self.thread = None
        self._stopTimeout = 5
        self._captureData = None

        try:
            self.htcMode()
        except:
            self.reset()
            time.sleep(15)
            self.ser = serial.Serial(port=comport, baudrate=3686400, bytesize=8,
                            parity='N', stopbits=1, timeout=5.0,
                            xonxoff=0, rtscts=0)
            self.htcMode()


    def reset(self):
        self.ser.write(b"psrst\r\n")
        self.ser.close()

    def assertEqual(self, val1, val2):
        if val1 != val2:
            details = self.ser.read_all()
            if details == b"":
                details = b"<NONE>"
            raise AssertionError("%s != %s\ndetails:\n%s"%(val1, val2, details.decode()))

    def htcMode(self):
        self.ser.write(b"htc\r\n")
        rcvExpected = b'\r\nPowerShield > ack htc\r\n\r\n'
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def probe(self):
        self.ser.write(b"echo ABC\r\n")
        rcvExpected = b'\r\nPowerShield > echo ABC\r\n'
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)
        return True, "ok"

    def setVoltage(self, voltage):
        assert type(voltage) == type(1)
        assert voltage>=1800 and voltage<=3300
        self.ser.write(b"volt %dm\r\n"%voltage)
        rcvExpected = b'\r\nPowerShield > ack volt %dm\r\n\r\n'%voltage
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def setTriggerDelay(self, seconds):
        assert type(seconds) == type(1)
        assert seconds>=0 and seconds<=600
        self.ser.write(b"trigdelay %d\r\n"%seconds)
        rcvExpected = b'\r\nPowerShield > ack trigdelay %d\r\n\r\n'%seconds
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def setSamplingFrequency(self, freq):
        if type(freq) == type(1):
            freq = str(freq)
        if freq not in SamplingFrequency:
             raise RuntimeError("freq must be one of %s"%SamplingFrequency)
        self.ser.write(b"freq %b\r\n"%freq.encode())
        rcvExpected = b'\r\nPowerShield > ack freq %b\r\n\r\n'%freq.encode()
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def setAcqTime(self, acqTime):
        """Set acquisition time in seconds"""
        # assert type(voltage) == type(1)
        # assert voltage>=1800 and voltage<=3300
        acqTime = 0
        self.ser.write(b"acqtime %d\r\n"%acqTime)
        rcvExpected = b'\r\nPowerShield > ack acqtime %d\r\n\r\n'%acqTime
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def setFuncMode(self, mode):
        """Set acquisition mode"""
        self.ser.write(b"funcmode %b\r\n"%mode.encode())
        rcvExpected = b'\r\nPowerShield > ack funcmode %b\r\n\r\n'%mode.encode()
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def setBinaryFormat(self):
        self.ser.write(b"format bin_hexa\r\n")
        rcvExpected = b'\r\nPowerShield > ack format bin_hexa\r\n\r\n'
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def powerEndOnOff(self, on):
        if on==True:
            val = b"on"
        else:
            val = b"off"
        self.ser.write(b"pwrend %b\r\n"%val)
        rcvExpected = b'\r\nPowerShield > ack pwrend %b\r\n\r\n'%val
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def close(self):
        self.ser.close()

    def start(self, runTime=None):
        self.capture = True
        self.thread = threading.Thread(target = self.acqThread, args = (runTime,))
        self.thread.start()

    def stop(self):
        self.capture = False
        if self.thread != None:
            self.thread.join()

    def bin2val(self, val):
        """convert binary sample to ms current"""
        return (val&0xFFF)*16**(-((val&0xF000)>>12))

    def acqThread(self, runTime=None):
        self.setAcqTime(0)
        self.setFuncMode("optim")
        self.setBinaryFormat()

        self.ser.write(b"start\r\n")
        rcvExpected = b'\r\nPowerShield > ack start\r\n\r\n'
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

        self._captureData = b""
        self.payload = b""

        start = time.time()
        while self.capture:
            self._captureData += self.ser.read(10000)
            if runTime != None:
                if time.time() - start >= runTime:
                    self.capture = False
                    break

        if len(self._captureData) % 2 == 1:
            self._captureData = self._captureData[:-1]

        self.ser.write(b"stop\r\n")
        start = time.time()
        rcv = b""
        while True:
            rcv += self.ser.read_all()
            if b"PowerShield > Acquisition completed\r\n" in rcv:
                break
            if time.time() - start >= self._stopTimeout:
                print("stop timeout exceeded, stopping thread anyway")
                break
            
    def targetReset(self, milliSeconds):
        self.ser.write(b"targrst %dm\r\n"%milliSeconds)
        rcvExpected = b'\r\nPowerShield > ack targrst %dm\r\n\r\n'%milliSeconds
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def powerOn(self, on):
        if on == True:
            val = b"on"
        else:
            val = b"off"
        self.ser.write(b"pwr %b\r\n"%val)
        rcvExpected = b'\r\nPowerShield > ack pwr %b\r\n\r\n'%val
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def powerOn(self, on):
        if on == True:
            val = b"on"
        else:
            val = b"off"
        self.ser.write(b"pwr %b\r\n"%val)
        rcvExpected = b'\r\nPowerShield > ack pwr %b\r\n\r\n'%val
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def targetReset(self, milliSeconds):
        self.ser.write(b"targrst %dm\r\n"%milliSeconds)
        rcvExpected = b'\r\nPowerShield > ack targrst %dm\r\n\r\n'%milliSeconds
        rcv = self.ser.read(len(rcvExpected))
        self.assertEqual(rcv, rcvExpected)

    def decodeData(self):
        if self.capture == True:
            return

        if self.payload != b"":
            return self.vals

        meta = False
        firstEnd = False
        firstByte = True

        idx=0
        for data in self._captureData:
            if data >= 0xF0 and meta == False and firstByte==True:
                meta = True
            elif data == 0xFF and meta == True:
                if firstEnd == True:
                    meta = False
                    firstEnd = False
                    firstByte = True
                if firstEnd == False:
                    firstEnd = True
            elif data != 0xFF and meta == True:
                firstEnd = False
            elif meta == False:
                firstByte = not firstByte
                self.payload += bytes([data])

            idx+=1

        if len(self.payload)%2 == 1:
            self.payload = self.payload[:-1]


        numPts = int(len(self.payload)/2)

        self.vals = numpy.zeros(numPts)
        for i in range(numPts):
            value = self.payload[i*2:i*2+2]
            self.vals[i] =self.bin2val(int.from_bytes(value, "big"))

        return self.vals


if __name__ == "__main__":
    import time
    l = LPM01()

    l.probe()

    # for i in range(100):
    #     val = random.randint(1800,3300)
    #     l.setVoltage(val)
    #     print(i, val)
    l.setTriggerDelay(8)

    l.setSamplingFrequency("20k")
    l.setVoltage(3300)
#    l.powerEndOnOff(True)
#    l.start(runTime=8+5)
    l.powerOn(True)
