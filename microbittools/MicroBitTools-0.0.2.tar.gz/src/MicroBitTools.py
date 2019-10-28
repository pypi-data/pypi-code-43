import shutil
import os
import serial


class InternalTools:
    def yntoboolean(data="no"):
        data = data.lower()
        if data == "y":
            return True
        elif data == "n":
            return False
        else:
            return "ERROR: \nInput was not either y or n"


def export(pythonfile, dirtomoveto):
    pyfilenoext = pythonfile[:-3]
    os.system("py2hex " + pythonfile)
    print("Moving to microbit.")
    shutil.move(os.getcwd() + "\\" + pyfilenoext + ".hex", dirtomoveto)
    print("Done!")


class SerialSystem:

    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = "COM3"
    ser.open()

    microbitpath = "F:\\"

    def ReadyMicrobit(self):
        shutil.copyfile(os.getcwd() + "\\src\\" + "microbitserialsystem.hex", self.microbitpath+"SerialSystem.hex")
        shutil.copy
        print("Done!")

    def read(self):

        try:
            mbd = str(self.ser.readline())
        except serial.serialutil.SerialException:
            return {"error": "Can not find MicroBit"}
        except IndexError:
            return {"error": "Unknown error"}

        try:
            mbdf = mbd[2:]
            # mbdf = mbdf.replace(" ", "")
            mbdf = mbdf.replace("'", "")
            mbdf = mbdf.replace("\\r\\n", "")
            mbdf = mbdf.replace("\\xc2", "")
        except IndexError:
            return {"error": "Could not read!"}

        if mbdf.startswith("}"):
            mbdf = mbdf[1:]
            mbdfsplit = mbdf.split("\\xa7")
            try:
                temp = int(mbdfsplit[0])
                try:
                    brightness = int(mbdfsplit[1])
                except ValueError:
                    brightness = ""
                ButtonA = InternalTools.yntoboolean(mbdfsplit[2][2:])
                ButtonB = InternalTools.yntoboolean(mbdfsplit[3][2:])
                CmpsH = int(mbdfsplit[4])

                dicmbd = {
                    "temp": temp,
                    "brightness": brightness,
                    "Buttons": {
                        "A": ButtonA,
                        "B": ButtonB
                    },
                    "CompassHeading": CmpsH
                }

                return dicmbd
            except IndexError:
                return {"error": "Could not read!"}
        else:
            return {"error": "Could not read!"}


def test():
    print("SUCCESS")