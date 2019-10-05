import json
import re
import threading
from time import sleep

import requests
from pyinnotemp.rooms import BBRooms
from pyinnotemp.system import BBSystem

class BBConnector:

    def __init__(self, username, password, hostname):
        raw_params = {'un': username, 'pw': password}
        self.session = requests.Session()
        self.roomList = []
        self.hostname = hostname
        r = self.session.post("http://" + self.hostname + "/inc/groups.read.php", data=raw_params)
        r = self.session.post("http://" + self.hostname + "/inc/roomconf.read.php")
        self._roomsraw = json.loads(r.text)
        for rooms in self._roomsraw['room']:
            attr = rooms['@attributes']
            roomno = int(re.search(r'\d+', attr['type']).group())
            raw_params_getroom = {'un': username, 'pw': password, 'room_id': str(roomno)}
            r = requests.post("http://" + self.hostname + "/inc/value.read.php", raw_params_getroom)
            jn = json.loads(r.text)
            if attr['label'] == 'Heizraum':
                self.system = BBSystem()
            else:
                setvar = list(jn.keys())[0]
                targetvar = rooms['main']['input'][0]['var']
                sensorvar = rooms['main']['input'][1]['var']
                statusvar = rooms['main']['input'][3]['var']
                self.roomList.append(BBRooms(attr['label'], roomno, targetvar, sensorvar, statusvar, setvar))
        self.lastUpdate = 0.0

    def _startUpdateThread(self):
        # Only call this function once
        self.update_thread = threading.Thread(target=self._updateLoop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def _stopUpdateThread(self):
        # Only call this function once
        self.update_thread.daemon = False
        self.update_thread.join()

    def _updateLoop(self):
        # print("Starting Update Thread")
        while True:
            self.update()
            sleep(15)

    def update(self):
        # print('Starting Update')
        r = self.session.post("http://" + self.hostname + "/inc/live_signal.read.php")
        jnresponse = json.loads(r.text)
        for room in self.roomList:
            room.updateCurrentTemperature(jnresponse[room.getSensorVariable()])
            room.updateTargetTemperature(jnresponse[room.getTargetVariable()])
        self.lastUpdate = jnresponse['sysTime']
        self.system.update(jnresponse)

    def start(self):
        # print('Starting Innotemp Service')
        self._startUpdateThread()

    def stop(self):
        self._stopUpdateThread()