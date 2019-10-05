from time import sleep

from pyinnotemp import connector

bbox = connector.BBConnector()
bbox.start()

for rooms in bbox.roomList:
    print(rooms.name)
    print(rooms.getTargetTemperature())
    print(rooms.getCurrentTemperature())

sleep(20)
for rooms in bbox.roomList:
    print(rooms.name)
    print(rooms.getTargetTemperature())
    print(rooms.getCurrentTemperature())

while True:
    sleep(150)

bbox.stop()
