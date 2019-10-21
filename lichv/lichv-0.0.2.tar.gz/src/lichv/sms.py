import http.client
from urllib import request
import json

class ChuanglanSMS(object):

    #余额查询的URL
    balance_get_uri = "/msg/balance/json"

    #普通短信发送的URL
    sms_send_uri = "/msg/send/json"

    """docstring for Sms"""
    def __init__(self, account, password, signal='', host='sms.253.com', port='80'):
        super(Sms, self).__init__()
        self.account = account
        self.password = password
        self.signal = signal
        self.host = host
        self.port = port

    """
    取账户余额
    """
    def get_user_balance(self):
    
        params=json.dumps({'account': self.account, 'password' : self.password})
        headers = {"Content-type": "application/json"}
        conn = http.client.HTTPConnection(self.host, port=self.port)
        conn.request('POST', self.balance_get_uri, params, headers)
        response = conn.getresponse().read()
        conn.close()
        return response

    """
    取账户余额
    """
    def send_sms(self, phone, text):
    if text.find(self.signal) == -1:
        text = '【'+self.signal+'】'+text
        params=json.dumps({'account': self.account, 'password' : self.password, 'msg': request.quote(text), 'phone':phone, 'report' : 'false'})
        headers = {"Content-type": "application/json"}
        conn = http.client.HTTPConnection(self.host, port=self.port, timeout=30)
        conn.request("POST", self.sms_send_uri, params, headers)
        response = conn.getresponse().read()
        conn.close()
        return response 


if __name__ == "__main__":
    service = ChuanglanSMS('account', 'password', '高搜易')

    result = service.send_sms("phonecode", "测试一条短信")
    print(result)

    result = service.get_user_balance()
    print(result)
