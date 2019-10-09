import serial
import serial.tools.list_ports
import time

class M2D2Bepp:
    def __init__(self, comport=None):
        self.comport = comport
        
    def probe(self):
        ok = True
        desc = "Ok"
        self.serial = None
        if self.comport == None:
            m2d2Found = False
            for comp in serial.tools.list_ports.comports():
                try:
                    dev = serial.Serial(comp.device, baudrate=115200, timeout=1.0)
                except:
                    continue
                dev.read_all()
                dev.write(b"\r")
                time.sleep(0.1)
                rcv_complete = b''
                while True:
                    rcv = dev.read_all()
                    rcv_complete += rcv
                    if len(rcv) == 0 or len(rcv_complete) > 1000:
                        break
                dev.close()
                if rcv_complete.find(b"s: Status [Interval ms]") != -1:
                    m2d2Found = True
                    self.comport = comp.device
                    break
                    
            if m2d2Found == False:
                ok = False
                desc = "Kein M2D2Bepp Gerät gefunden"

        if ok:
            try:
                print ("Comport M2D2=", self.comport)
                self.serial = serial.Serial(self.comport, baudrate=115200, timeout=1.0)
                self.serial.close()
            except:
                ok = False
                desc = traceback.format_exc()
        
        if ok:
            v = self.getVersion()
            if v == b'Bepper Master $Revision: 1694 $ Apr 30 2019 11:09:31\nreced: v \n':
                ok = True
                desc = "M2D2Bepp mit Version %s gefunden"%v.decode()
            else:
                ok = False
                desc = "M2D2Bepp Version %s nicht freigegeben"%v.decode()
        
        return ok, desc

    def close(self):
        self.serial.close()
        
    def _getCmd(self, cmd):
        self.serial.open()
        self.serial.write(b"%s\r"%cmd)
        time.sleep(0.5)
        rv = self.serial.read_all()
        self.serial.close()
        return rv
    
    def _setCmd(self, cmd, *args):
        cmd = b"%s"%cmd
        for arg in args:
            cmd = cmd + b" " + str(arg).encode()
        cmd = cmd + b"\r"
        self.serial.open()
        self.serial.write(cmd)
        self.serial.close()
        
    def enaPurge(self):
        self._setCmd(b"p", 1)
        
    def setBeppTime(self, t):
        """set bepp time in seconds"""
        t = t*100
        self._setCmd(b"t", int(t))

    def enaBepp(self):
        self._setCmd(b"a")
        
    def getVersion(self):
        return self._getCmd(b"v")
        
    def getStatus(self):
        rv = self._getCmd(b"s")
        lst = rv.decode().split("\n")[1].split(" ")
        while '' in lst:
            lst.remove('')
        ventil = int(lst[0][1:])
        sensor = int(lst[1])
        sensorSpiele = int(lst[2])
        ventilSpiele = int(lst[3])
        waitTime = int(lst[4])
        machineState = int(lst[5])

        return ventil, sensor, sensorSpiele, ventilSpiele, waitTime, machineState

    def reset(self):
        self._getCmd(b"n")
        
        
if __name__ == "__main__":
    m2d2 = M2D2Bepp()
    m2d2.probe()
    m2d2.reset()
    m2d2.setBeppTime(3)
    m2d2.enaBepp()
    m2d2.enaPurge()