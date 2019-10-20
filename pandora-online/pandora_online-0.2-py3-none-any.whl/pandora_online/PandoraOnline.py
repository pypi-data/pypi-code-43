
import json
import requests

class PandoraOnline:
    """ This class monitored http://pro.p-on.ru and save Pandora and Pandect status """

    def __init__(self, username, password):
        """Pandora Online Constructor"""
        self.username = username
        self.password = password
        self.api_url_base = 'https://pro.p-on.ru/api'
        self.session = requests.Session()
        self.cookies = {}
        pass

    def login(self):
        """ Method from auth in pro.p-on.ru """
        api_url = self.api_url_base+'/users/login'
        headers = {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'https://pro.p-on.ru/login',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.107'
                    }
        self.session.cookies.set('lang', 'ru', path='/', domain='pro.p-on.ru')
        self.response = self.session.post(api_url, headers = headers, data = {'login':self.username,'password':self.password,'lang':'ru'},allow_redirects=True)
        self.cookies = self.response.cookies.get_dict()
        if self.response.status_code == 200 and self.cookies.get('sid'):
            return json.loads(self.response.text)
        else:
            return None

    def logout(self):
        """ Method from deauth in pro.p-on.ru """
        api_url = self.api_url_base+'/users/logout'
        headers = {'Content-Type':'application/json; charset=utf-8',
                    'Referer': 'https://pro.p-on.ru/logout',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.107'
                    }
        self.response = self.session.post(api_url, headers = headers, allow_redirects=True)
        if self.response.status_code == 200:
            self.session = None
            self.cookies = None
            return json.loads(self.response.text)
        else:
            return None


    def get_devices(self):
        """ Get all devices """
        api_url = self.api_url_base+'/devices'
        headers = {'Content-Type':'application/json; charset=utf-8',
                    'Referer': 'https://pro.p-on.ru',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.107'
                    }
        self.response = self.session.get(api_url, headers = headers)
        if self.response.status_code == 200:
            return json.loads(self.response.text)
        else:
            return None

    def iamalive(self):
        """ Some keepalive request """
        api_url = self.api_url_base+'/iamalive'
        headers = {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'https://pro.p-on.ru',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.107'
                    }
        self.response = self.session.post(api_url, headers = headers,data = {'num_click': 0})
        if self.response.status_code == 200:
            return json.loads(self.response.text)
        else:
            return None

    def get_status(self,ts = None, from_ts = None, to_ts = None):
        """ Get status from all devices """
        if(ts!= None and from_ts != None and to_ts !=None and (to_ts <= from_ts)):
            raise IOError("Please enter correct timestamps: ts - current time, from_ts - start time, to_ts - end time")
        api_url = self.api_url_base + f"/updates"
        if(ts == None):
            api_url += f"?ts=-1"
        else:
            api_url += f"?ts={ts}&from={from_ts}&to={to_ts}"
        headers = {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'https://pro.p-on.ru',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.107'
                    }
        self.response = self.session.get(api_url, headers = headers)
        if self.response.status_code == 200:
            return json.loads(self.response.text)
        else:
            return None

    def send_command(self,id=None,command=None):
        """ Send some command request """
        if(id== None or command == None):
            raise IOError("Please enter correct id device and correct command")
        api_url = self.api_url_base+'/devices/command'
        headers = {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'https://pro.p-on.ru',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.107'
                    }
        self.response = self.session.post(api_url, headers = headers,data = {'id': id,'command':command})
        if self.response.status_code == 200:
            return json.loads(self.response.text)
        else:
            return None
