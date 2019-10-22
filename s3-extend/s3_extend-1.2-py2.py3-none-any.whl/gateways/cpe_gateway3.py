import serial
from serial.tools import list_ports
import sys
import threading
import time

# class CpeGateway(threading.Thread):
class CpeGateway(threading.Thread):

    def __init__(self):

        self.start_time = None

        threading.Thread.__init__(self)
        self.daemon = True
        self.stop_event = threading.Event()
        try:
            self.cpe_serial = serial.Serial(port="/dev/ttyACM0", baudrate=115200,
                                                  timeout=.01)
        except serial.SerialException:
            print('Connection to Circuit Playground Expressed Failed.')
            sys.exit(0)
        except OSError:
            pass
        self.start()
        time.sleep(1)

        # get version
        cmd = 'v\r'.encode()
        self.cpe_serial.write(cmd)
        self.start_time = time.time()

        cmd = 'acc\r'.encode()
        self.cpe_serial.write(cmd)
        self.start_time = time.time()

        cmd = 'temp\r'.encode()
        self.cpe_serial.write(cmd)
        self.start_time = time.time()

        while True:
           time.sleep(.001)


    def run(self):
        """
        This method continually runs. If an incoming character is available on the serial port
        it is read and placed on the _command_deque
        @return: Never Returns
        """
        while True:
            # we can get an OSError: [Errno9] Bad file descriptor when shutting down
            # just ignore it
            try:
                if self.cpe_serial.inWaiting():
                    c = self.cpe_serial.readline().decode()
                    print(time.time() - self.start_time)

                    print(c)
                else:
                    time.sleep(.1)
            except OSError:
                pass
            # except IOError:
            #     self.stop()
            #     self.close()





CpeGateway()
