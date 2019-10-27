import json
from datetime import datetime

import requests
import urllib3

# fix cert warnigns
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class unifiled:
    _ip = None
    _port = None
    _debug = False
    _authorization = None
    _headers = None

    def __init__(self, _ip, _port, username, password, debug=False, autologin=True):
        self._ip = _ip
        self._port = _port
        self._debug = debug
        if autologin:
            self.login(username, password)

    def debug_log(self, text):
        if self._debug:
            print('{}: {}'.format(datetime.now(), text))

    def login(self, username, password):
        self.debug_log('Logging in: {0}'.format(username))
        _json = {
            'username': username,
            'password': password
        }

        try:
            login_req = requests.post('https://' + self._ip + ':' + self._port + '/v1/login', data=_json, verify=False, timeout=5)
        except:
            raise Timeout('Connection timed out')


        if login_req.status_code == 200:
            self._authorization = login_req.json()['access_token']
            self._headers = {
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Authorization': 'Bearer ' + self._authorization,
            }
            return True
        elif login_req.status_code == 403:
            raise InvalidCredentials('Username or password is incorrect')
        else:
            raise ConnectionError('Connection error')

    def get_devices(self):
        self.debug_log('Getting devices')
        getdevices_req = requests.get('https://' + self._ip + ':' + self._port + '/v1/devices', headers=self._headers, verify=False, timeout=5)
        if getdevices_req.status_code == 200:
            return getdevices_req.json()
        else:
            raise ValueError('Could not get devices')

    def get_groups(self):
        self.debug_log('Getting groups')
        getgroups_req = requests.get('https://' + self._ip + ':' + self._port + '/v1/groups', headers=self._headers, verify=False, timeout=5)
        if getgroups_req.status_code == 200:
            return json.loads(getgroups_req.content)
        else:
            raise ValueError('Could not get groups')

    def set_device_brightness(self, id, brightness):
        self.debug_log('Setting brightness to {0} for device {1}'.format(brightness, id))
        data = '{"command":"sync","value":' + str(brightness) + '}'
        setdeviceoutput_req = requests.put('https://' + self._ip + ':' + self._port + '/v1/devices/' + str(id), data=data, headers=self._headers, verify=False, timeout=5)
        if setdeviceoutput_req.status_code == 200:
            return True
        else:
            raise ValueError('Could not set brightness')

    def set_device_output(self, id, output):
        self.debug_log('Setting output to {0} for device {1}'.format(output, id))
        data = '{"command":"config-output","value":' + str(output) + '}'
        setdeviceoutput_req = requests.put('https://' + self._ip + ':' + self._port + '/v1/devices/' + str(id), data=data, headers=self._headers, verify=False, timeout=5)
        if setdeviceoutput_req.status_code == 200:
            return True
        else:
            raise ValueError('Could not set output')

    def set_group_output(self, id, output):
        self.debug_log('Setting output to {0} for group {1}'.format(output, id))
        data = '{"command":"config-output","value":' + str(output) + '}'
        setdeviceoutput_req = requests.put('https://' + self._ip + ':' + self._port + '/v1/group/' + str(id), data=data, headers=self._headers, verify=False, timeout=5)
        if setdeviceoutput_req.status_code == 200:
            return True
        else:
            raise ValueError('Could not set output')

    def get_login_state(self):
        self.debug_log('Checking login states')
        devices = self.get_devices()
        if devices != None:
            return True
        else:
            return False

    def convert_from_255_to_100(self,value):
        self.debug_log('Converting {0} from 0-255 scale to 0-100 scale'.format(value))
        oldmin = 0
        oldmax = 255
        newmin = 0
        newmax = 100
        oldrange = (oldmax - oldmin)
        newrange = (newmax - newmin)
        convertedvalue = (((int(value) - oldmin) * newrange) / oldrange) + newmin
        return int(convertedvalue)

    def convert_from_100_to_255(self,value):
        self.debug_log('Converting {0} from 0-100 scale to 0-255 scale'.format(value))
        oldmin = 0
        oldmax = 100
        newmin = 0
        newmax = 255
        oldrange = (oldmax - oldmin)
        newrange = (newmax - newmin)
        convertedvalue = (((int(value) - oldmin) * newrange) / oldrange) + newmin
        return int(convertedvalue)

    def get_lights(self):
        lights = []
        devices = self.get_devices()
        for device in devices:
            if device['type'] == 'LED':
                lights.append(device)
        return lights

    def get_sensors(self):
        sensors = []
        devices = self.get_devices()
        for device in devices:
            if device['type'] != 'LED':
                sensors.append(device)
        return sensors

    def get_light_state(self, id):
        devices = self.get_devices()
        for device in devices:
            if device['id'] == str(id):
                if device['status']['output'] == 1:
                    return True
                else:
                    return False
        return False

    def get_light_brightness(self, id):
        devices = self.get_devices()
        for device in devices:
            if device['id'] == str(id):
                return int(device['status']['led'])
        return False

    def get_light_available(self, id):
        devices = self.get_devices()
        for device in devices:
            if device['id'] == str(id):
                if device['isOnline'] == True:
                    return True
                else:
                    return False
        return False

    #temporary compatibility functions.

    def getdevices(self):
        return self.get_devices()

    def getgroups(self):
        return self.get_groups()

    def setdevicebrightness(self, id, brightness):
        return self.set_device_brightness(id, brightness)

    def setdeviceoutput(self, id, output):
        return self.set_device_output(id, output)

    def setgroupoutput(self, id, output):
        return self.set_group_output(id, output)

    def getloginstate(self):
        return self.get_login_state()

    def convertfrom255to100(self,value):
        return self.convert_from_255_to_100(value)

    def convertfrom100to255(self,value):
        return self.convert_from_100_to_255(value)

    def getlights(self):
        return self.get_lights()

    def getsensor(self):
        return self.get_sensors()

    def getlightstate(self, id):
        return self.get_light_state(id)

    def getlightbrightness(self, id):
        return self.get_light_brightness(id)

    def getlightavailable(self, id):
        return self.get_light_available(id)
