import sys
import bluetooth

command = "fe 02 01 00 b9 35 01 8e".split()
command = bytes(map(lambda x: int(x, 16), command))
print(f"command: {command}")

# sys.exit()

print(f"bluetooth.SERIAL_PORT_PROFILE {bluetooth.SERIAL_PORT_PROFILE}")
print(f"bluetooth.SERIAL_PORT_CLASS   {bluetooth.SERIAL_PORT_CLASS}")

"""
88:1B:99:05:5B:59 Electronic Scale
"""

# nearby_devices = bluetooth.discover_devices(lookup_names=True)
# print(f"found devices: {len(nearby_devices)}")
# for addr, name in nearby_devices:
#     print(f"{addr} {name}")

print(f"find_service")

service_list = bluetooth.find_service()

if len(service_list) > 0:
    print(f"found service_list: {len(service_list)} ")
    print("")
else:
    print("no service_list found")

for service in service_list:
    print("Service Name: %s" % service["name"])
    print("    Host:        %s" % service["host"])
    print("    Description: %s" % service["description"])
    print("    Provided By: %s" % service["provider"])
    print("    Protocol:    %s" % service["protocol"])
    print("    channel/PSM: %s" % service["port"])
    print("    service classes: %s " % service["service-classes"])
    print("    profiles:    %s " % service["profiles"])
    print("    service id:  %s " % service["service-id"])
    print("")

print(f"find_service")

address = "88:1B:99:05:5B:59"
scale_uuid = "00001101-0000-1000-8000-00805f9b34fb"

match_list = bluetooth.find_service(address=address, uuid=scale_uuid)

if not match_list:
    print(f"Missing scale device")
    sys.exit()

match = match_list[0]
host = match["host"]
port = match["port"]
name = match["name"]

print(f"connecting to: host={host} port={port} name={name}")

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

sock.connect((host, port))

print(f"connected to sock: {sock}")

# sock.send('0x01 ')
sock.send(command)

print(f"sock.send")

while True:
    data = sock.recv(16)
    if data:
        print(f"sock.recv={data}")
    else:
        break

sock.close()
