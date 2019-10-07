import re
import requests
from bs4 import BeautifulSoup

class API:

    def __init__(self, telnum=None, password=None, line_access_token=None):
        self.telnum = telnum
        self.password = password
        self.line_access_token = line_access_token

    def _login(self):
        s = requests.Session()
        r = s.get('https://my.softbank.jp/msb/d/webLink/doSend/MRERE0000')
        soup = BeautifulSoup(r.text, 'lxml')
        ticket = soup.find('input', type='hidden').get('value')
        payload = {
            'telnum': self.telnum,
            'password': self.password,
            'ticket': ticket
        }
        s.post('https://id.my.softbank.jp/sbid_auth/type1/2.0/login.php', data=payload)
        return s

    def get(self):
        s = self._login()
        r = s.get('https://my.softbank.jp/msb/d/webLink/doSend/MRERE0000')
        soup = BeautifulSoup(r.text, 'lxml')
        auth_token = soup.find_all('input')
        payload = {
            'mfiv': auth_token[0].get('value'),
            'mfsb': auth_token[1].get('value'),
        }
        r2 = s.post('https://re11.my.softbank.jp/resfe/top/', data=payload)
        soup2 = BeautifulSoup(r2.text, 'lxml')
        num = [float(re.findall('\d+[.]+\d\d', str(i))[0]) for i in soup2.find_all(class_='p-left-10')]
        if num == []:
            total, remain, used, rate, bf = 0.00, 0.00, 0.00, 0.00, 0.00
        else:
            total = round(num[1], 2)
            remain = round(num[1] - num[0], 2)
            used = round(num[0], 2)
            rate = round(remain / total * 100, 1)
            bf = round(num[2], 2)
        dt = {'total':str(total).ljust(4, str(0)), 'remain':str(remain).ljust(4, str(0)), 'used':str(used).ljust(4, str(0)), 'rate':str(rate).ljust(4, str(0)), 'bf':str(bf).ljust(4, str(0))}  
        return dt

    def line(self):
        dt = self.get()
        text = '\n{}GB / {}GB ({}%)'.format(dt['remain'], dt['total'], dt['rate'])
        line_notify_token = self.line_access_token
        line_notify_api = 'https://notify-api.line.me/api/notify'
        payload = {'message': text}
        headers = {'Authorization': 'Bearer ' + line_notify_token}
        line_notify = requests.post(line_notify_api, data=payload, headers=headers)
        return line_notify.status_code