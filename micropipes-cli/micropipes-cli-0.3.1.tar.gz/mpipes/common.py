from argparse import ArgumentTypeError
from mpipes.common_auth import get_default_authentication, load_authentication_data, get_access_token
import certifi
from urllib3 import HTTPConnectionPool, HTTPSConnectionPool, make_headers
import json


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


def tuples(headers, data):
    rt = []
    for item in data:
        i = []
        for h in headers:
            i.append(item[h])
        rt.append(i)
    return rt


def format_response_list(resp, headers_param='*'):
    data = json.loads(resp.data.decode())
    items = data['_items']
    if len(items):
        if headers_param == '*':
            headers = list(items[0].keys())
            headers.sort()
            if 'id' in headers:
                headers.remove('id')
                headers.insert(0,'id')
        else:
            headers = headers_param.split(",")
        mask_configurations(items)
        return (headers, tuples(headers, items))
    else:
        return ([],[])

def mask_configurations(resp):
    for item in resp:
        if 'required_workers' in item:
            for wrk in item['required_workers']:
                if 'configuration' in wrk:
                    wrk['configuration'] = '**masked**'


class AuthenticatedConn:
    def __init__(self, authentication = None):
        if not authentication:
            authentication = get_default_authentication()
        auth_data = load_authentication_data(authentication)
        self.micropipes_domain = auth_data['micropipes_domain']
        self.micropipes_port = auth_data['micropipes_port']
        self.micropipes_https = auth_data['https']
        self.token = get_access_token(authentication)
        self.con = None
        self.session_cookie = None
        # self.dump_access_token()



    def create_conn(self):
        if not self.con:
            if self.micropipes_https:
                if self.micropipes_port != -1:
                    self.con = HTTPSConnectionPool(host=self.micropipes_domain, port=self.micropipes_port,
                                                   cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
                    # self.con = http.client.HTTPSConnection(self.micropipes_domain, port=self.micropipes_port)
                else:
                    self.con = HTTPSConnectionPool(host=self.micropipes_domain,
                                                   cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
                    # self.con =  http.client.HTTPSConnection(self.micropipes_domain)
            else:
                if self.micropipes_port != -1:
                    self.con = HTTPConnectionPool(host=self.micropipes_domain, port=self.micropipes_port)
                    # self.con =  http.client.HTTPConnection(self.micropipes_domain, port=self.micropipes_port)
                else:
                    self.con = HTTPConnectionPool(host=self.micropipes_domain)
                    # self.con =  http.client.HTTPConnection(self.micropipes_domain)
        return self.con

    def check_session_cookie(self, resp):
        if 'Set-Cookie' in resp.headers:
            sesk = str(resp.headers['Set-Cookie'])
            if sesk.startswith('session'):
                self.session_cookie = sesk.split(';')[0]
                # print(self.session_cookie)

    def force_session_cookie(self, headerz):
        if self.session_cookie:
            headerz['Cookie'] = self.session_cookie

    def get_request(self, path, fields = None ):
        conn = self.create_conn()
        headerz = {
            'authorization': "Bearer {}".format(self.token)
        }
        self.force_session_cookie(headerz)
        resp = conn.request("GET", url=path, body=None, headers=headerz, fields=fields)
        self.check_session_cookie(resp)
        return resp
        # return conn.getresponse()

    def post_request(self, path , payload ):
        conn = self.create_conn()
        headerz = {
            'authorization': "Bearer {}".format(self.token)
        }
        self.force_session_cookie(headerz)
        if payload:
            headerz['content-type'] = "application/json"
        resp =  conn.request("POST", url=path, body=payload, headers=headerz)
        self.check_session_cookie(resp)
        return resp

    def put_request(self, path , payload ):
        conn = self.create_conn()
        headerz = {
            'authorization': "Bearer {}".format(self.token),
        }
        self.force_session_cookie(headerz)
        if payload:
            headerz['content-type'] = "application/json"
        resp =  conn.request("PUT", url=path, body=payload, headers=headerz)
        self.check_session_cookie(resp)
        return resp


    def delete_request(self, path ):
        conn = self.create_conn()
        headerz = {
            'authorization': "Bearer {}".format(self.token),
            'Connection': 'keep-alive'
        }
        self.force_session_cookie(headerz)
        resp =  conn.request("DELETE", url=path, body=None, headers=headerz)
        self.check_session_cookie(resp)
        return resp
