# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import highcompress
import requests
import urllib.request
from dotmap import DotMap
import json
class Client(object):

    def __init__(self, key):
        self.auth = {'api', key}

    def request(self, api,data,path2):
        response="Compressed"
        ENDPOINT="https://www.highcompress.com/api/shrink.php"
        mime=path2[-3:]
        data={'apikey': api, 'data': data,'mime':mime}
        reponse = requests.post(ENDPOINT, data)

        data = DotMap(reponse.json())
        if data.Status=="200":
            urllib.request.urlretrieve(data.url, path2)
            response=data
        if data.Status=="500":
            response="Your key is not Valid"
        elif data.Status=="400":
            response="Your Credit is Finished Please Upgrade"

        return response

    def check_credit(self,key=""):
        return "301 left"
