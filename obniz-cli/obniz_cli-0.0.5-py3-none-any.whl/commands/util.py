import sys

import serial.tools.list_ports

def select_port():
    # シリアルポート一覧の表示および選択
    print()
    coms = serial.tools.list_ports.comports()
    portlist = [com.device for com in coms]
    if len(portlist) == 0:
        print("Error: device not found.")
        sys.exit(1)
    for i, port in enumerate(portlist):
        print(str(i) + ":", port)
    print()
    usr_input = input("Select NUMBER from above list(or if you want to cancel, input N key):")
    if usr_input in ["n", "N"]:
        print("Canceled.")
        sys.exit(0)
    elif usr_input.isdecimal() and int(usr_input) >= 0 and int(usr_input) < len(portlist):
        selected_port = portlist[int(usr_input)]
        print("Selected port", selected_port)
        return selected_port
    else:
        print("Error: Invalid input.")
        sys.exit(1)