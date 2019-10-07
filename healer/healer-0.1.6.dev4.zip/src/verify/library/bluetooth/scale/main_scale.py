import bluetooth

command = "fe 02 01 00 b9 35 01 8e".split()
command = bytes(map(lambda x: int(x, 16), command))
print(f"command: {command}")

scale_addr = "88:1B:99:05:5B:59"
scale_uuid = "00001101-0000-1000-8000-00805f9b34fb"

duration_limit = 2


def check_scale():
    print(f"check_scale")
    path_list = bluetooth.discover_devices(duration=duration_limit)
    for face_dict in path_list:
        if face_dict == scale_addr:
            return True
    else:
        return False


present_count = 0
present_limit = 2
present_state = False


def obtain_service():
    service_list = bluetooth.find_service(address=scale_addr, uuid=scale_uuid)
    if service_list:
        return service_list[0]
    else:
        return None


def on_connect():
    print("on_connect")
    service = obtain_service()
    print(f"    service: {service}")
    host = service["host"]
    port = service["port"]
    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    print(f"    connect to: host={host} port={port}")
    socket.connect((host, port))
    socket.settimeout(15)  # seconds
    print(f"    send command")
    socket.send(command)
    print(f"    read response")
    stream = bytearray()
    while len(stream) < 16:
#
# _bluetooth.error: (110, 'Connection timed out')
#
        packet = socket.recv(128)
        stream += packet
    print(f"stream={stream} length={len(stream)}")
    print(f"    disconnect")
    socket.close()


def on_disconnect():
    print("on_disconnect")


while True:
    has_scale = check_scale()
    if has_scale:
        present_count += 1
        if present_count > present_limit:
            present_count = present_limit
            if not present_state:
                present_state = True
                on_connect()

    else:
        present_count -= 1
        if present_count < 0:
            present_count = 0
            if present_state:
                present_state = False
                on_disconnect()

# from bluetooth import _bluetooth as _bt
# while True:
#     device_id = _bt.hci_get_route()
#     print(device_id)
#     time.sleep(1)
