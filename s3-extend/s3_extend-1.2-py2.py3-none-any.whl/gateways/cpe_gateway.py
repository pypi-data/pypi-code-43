import serial
import sys
import time

try:
    ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200,
                                                  timeout=.01)
except serial.SerialException:
    print('Connection to Circuit Playground Expressed Failed.')
    sys.exit(0)

while True:

    data = 'p\r'
    data = data.encode()

    # while not ser.inWaiting():
    #     time.sleep(.01)
    # data = ser.readline().decode()
    # print('a', data)
    # cmd = 'v\n'.encode()
    # ser.write(cmd)

    ser.write(data)
    time.sleep(1)
    data = 'n\r'
    data = data.encode()
    ser.write(data)
    time.sleep(1)
