import requests, json, urllib3
from datetime import datetime

# TODO: Add more error handling

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
        login_req = requests.post('https://' + self._ip + ':' + self._port + '/v1/login', data=_json, verify=False, timeout=5)
        if login_req.status_code == 200:
            self._authorization = login_req.json()['access_token']
            self._headers = {
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Authorization': 'Bearer ' + self._authorization,
            }
            return True
        elif login_req.status_code == 403:
            raise ValueError('Username or password is incorrect')
        else:
            raise ValueError('Connection error')

    def getdevices(self):
        self.debug_log('Getting devices')
        getdevices_req = requests.get('https://' + self._ip + ':' + self._port + '/v1/devices', headers=self._headers, verify=False, timeout=5)
        if getdevices_req.status_code == 200:
            return getdevices_req.json()
        else:
            raise ValueError('Could not get devices')

    def getgroups(self):
        self.debug_log('Getting groups')
        getgroups_req = requests.get('https://' + self._ip + ':' + self._port + '/v1/groups', headers=self._headers, verify=False, timeout=5)
        if getgroups_req.status_code == 200:
            return json.loads(getgroups_req.content)
        else:
            raise ValueError('Could not get groups')

    def setdevicebrightness(self, id, brightness):
        self.debug_log('Setting brightness to {0} for device {1}'.format(brightness, id))
        data = '{"command":"sync","value":' + str(brightness) + '}'
        setdeviceoutput_req = requests.put('https://' + self._ip + ':' + self._port + '/v1/devices/' + str(id), data=data, headers=self._headers, verify=False, timeout=5)
        if setdeviceoutput_req.status_code == 200:
            return True
        else:
            raise ValueError('Could not set brightness')

    def setdeviceoutput(self, id, output):
        self.debug_log('Setting output to {0} for device {1}'.format(output, id))
        data = '{"command":"config-output","value":' + str(output) + '}'
        setdeviceoutput_req = requests.put('https://' + self._ip + ':' + self._port + '/v1/devices/' + str(id), data=data, headers=self._headers, verify=False, timeout=5)
        if setdeviceoutput_req.status_code == 200:
            return True
        else:
            raise ValueError('Could not set output')

    def setgroupoutput(self, id, output):
        self.debug_log('Setting output to {0} for group {1}'.format(output, id))
        data = '{"command":"config-output","value":' + str(output) + '}'
        setdeviceoutput_req = requests.put('https://' + self._ip + ':' + self._port + '/v1/group/' + str(id), data=data, headers=self._headers, verify=False, timeout=5)
        if setdeviceoutput_req.status_code == 200:
            return True
        else:
            raise ValueError('Could not set output')

    def getloginstate(self):
        self.debug_log('Checking login states')
        devices = self.getdevices()
        if devices != None:
            return True
        else:
            return False

    def convertfrom255to100(self,value):
        self.debug_log('Converting {0} from 0-255 scale to 0-100 scale'.format(value))
        oldmin = 0
        oldmax = 255
        newmin = 0
        newmax = 100
        oldrange = (oldmax - oldmin)
        newrange = (newmax - newmin)
        convertedvalue = (((int(value) - oldmin) * newrange) / oldrange) + newmin
        return int(convertedvalue)

    def convertfrom100to255(self,value):
        self.debug_log('Converting {0} from 0-100 scale to 0-255 scale'.format(value))
        oldmin = 0
        oldmax = 100
        newmin = 0
        newmax = 255
        oldrange = (oldmax - oldmin)
        newrange = (newmax - newmin)
        convertedvalue = (((int(value) - oldmin) * newrange) / oldrange) + newmin
        return int(convertedvalue)

    def getlights(self):
        lights = []
        devices = self.getdevices()
        for device in devices:
            if device['type'] == 'LED':
                lights.append(device)
        return lights

    def getlightstate(self, id):
        devices = self.getdevices()
        for device in devices:
            if device['id'] == str(id):
                if device['status']['output'] == 1:
                    return True
                else:
                    return False
        return False

    def getlightbrightness(self, id):
        devices = self.getdevices()
        for device in devices:
            if device['id'] == str(id):
                return int(device['status']['led'])
        return False

    def getlightavailable(self, id):
        devices = self.getdevices()
        for device in devices:
            if device['id'] == str(id):
                if device['isOnline'] == True:
                    return True
                else:
                    return False
        return False
