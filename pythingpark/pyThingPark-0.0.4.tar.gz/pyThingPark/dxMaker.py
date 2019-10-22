#!/usr/bin/env python3
#     _        _   _ _ _ _
#    / \   ___| |_(_) (_) |_ _   _
#   / _ \ / __| __| | | | __| | | |
#  / ___ \ (__| |_| | | | |_| |_| |
# /_/   \_\___|\__|_|_|_|\__|\__, |
#                            |___/
# Copyright (C) 2019 Actility, SA. All Rights Reserved.
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER
# License: Revised BSD License, see LICENSE.TXT file included in the project
# author: <raphael.apfeldorfer@actility.com>
# date: Tue September 26 09:24:48 CET 2019

import urllib.request, urllib.parse, urllib.error
import json

DxVersion = "latest"
defaultHsmGroupId = "HSM_JS-OPE.13"
log=False

class FactoryDevice:
    def __init__(self,DevEUI, JoinEUI, TkmInfo):
        assert(type(DevEUI)  is str and len(DevEUI)==16)
        assert(type(JoinEUI) is str and len(JoinEUI)==16)
        assert(type(TkmInfo) is str and len(TkmInfo)==20)
        self.deviceJson = {"deviceEUI": DevEUI, "joinEUI": JoinEUI, "tkmInfo": TkmInfo, "hsmGroupId": defaultHsmGroupId}
    def __repr__(self):
        return json.dumps(self.deviceJson)

class DxAdmin:
    URL = "https://dx-api.thingpark.com/admin/{0}/api/".format(DxVersion)
    headers= {"Accept": "application/json"}
    def __init__(self,login, password, platform="js-labs-api"):
        data = urllib.parse.urlencode((("grant_type","client_credentials"), ("client_id","{0}/{1}".format(platform,login)), ("client_secret",password))).encode('ascii')
        postRequest = urllib.request.Request(self.URL + "oauth/token", headers=self.headers)
        postRequest.add_header('Content-Type', 'application/x-www-form-urlencoded')
        postRequest.add_header('Content-Length', len(data))
        if log:
            dataHidden = data.decode('ascii')
            dataHidden = dataHidden[:dataHidden.rfind('=')+1] + '***'
            print("POST /oauth/token\n{0}".format(dataHidden))
        try: 
            resultJson = urllib.request.urlopen(postRequest, data).read()
        except urllib.error.HTTPError as error:
            print(error, error.headers)
            print("Login failed")
        except Exception as e:
            print(e)
        result = json.loads(resultJson)
        self.client_id   = result["client_id"]
        self.customer_id = result["customer_id"]
        self.bearerToken = "{0} {1}".format(result["token_type"], result["access_token"])
        self.expire      = result["expires_in"]
        
    def getBearerToken(self):
        return self.bearerToken
        
    def getTokenInfo(bearerToken):
        assert(type(bearerToken) is str)
        assert (bearerToken[:len("bearer")+1].lower() == "bearer "), "BearerToken should start with \"bearer \""
        token = bearerToken[len("bearer")+1:]
        try:
            bearerJson = urllib.request.urlopen(DxAdmin.URL + "oauth/tokeninfo?access_token={0}".format(token)).read()
        except urllib.error.HTTPError as error:
            msg = json.loads(error.read())
            print("HTTP Error {0}: {1}".format(msg["code"], msg["message"]))
            print("Verify token failed")
            return None
        return json.loads(bearerJson)

    def __repr__(self):
        return "DX connected: client_id={0}, customer_id={1}".format(self.client_id, self.customer_id)
    

class DxMaker:
    URL = "https://dx-api.thingpark.com/maker/{0}/api/".format(DxVersion)
    deviceList = {}
    headers= {"Accept": "application/json"}
    ''' Create bearer token at https://dx-api.thingpark.com/admin/$DxVersion/swagger-ui/index.html?shortUrl=tpdx-admin-api-contract.json#/ '''   
    def __init__(self,bearerToken):
        self.bearerInfo = DxAdmin.getTokenInfo(bearerToken)
        self.headers["Authorization"] = bearerToken
        if log: print(self)
    
    def request(self, path, datalen=None, method=None):
        if method:
            req = urllib.request.Request(self.URL + path, headers=self.headers, method=method)
        else:
            req = urllib.request.Request(self.URL + path, headers=self.headers)
        if datalen:
            req.add_header('Content-Type', 'application/json')
            req.add_header('Content-Length', datalen)
        return req
        
    def getFactoryDevices(self):
        '''Return all devices provisioned on JS'''
        getRequest = self.request("factoryDevices")
        resultJson = urllib.request.urlopen(getRequest).read()
        self.deviceList = json.loads(resultJson)
        if log: print("GET /factoryDevices\n{0}".format(self.deviceList))
        return self.deviceList

    def getAstKeys(self):
        '''Return all ASTK provisioned on JS'''
        getRequest = self.request("astKeys")
        resultJson = urllib.request.urlopen(getRequest).read()
        if log: print("GET /astKeys\n{0}".format(json.loads(resultJson)))
        return json.loads(resultJson)

    def postFactoryDevice(self, device):
        '''Provision new device on JS'''
        assert(type(device) is FactoryDevice)
        assert "tkmInfo" in device.deviceJson, "postFactoryDevice: tkmInfo field is mandatory (only SE is supported)"
        data = json.dumps(device.deviceJson).encode('ascii')
        if log: print("POST /factoryDevices\n{0}".format(device.deviceJson))
        try: 
            postRequest = self.request("factoryDevices", datalen=len(data))
            resultJson = urllib.request.urlopen(postRequest, data).read()
        except urllib.error.HTTPError as error:
            msg = json.loads(error.read())
            print("HTTP Error {0}: {1}".format(msg["code"], msg["message"]))
            print("Provisioning failed")
            return None
        return json.loads(resultJson)

    def deleteFactoryDevice(self, deviceEUI):
        '''Delete device on JS'''
        self.getFactoryDevices()
        deviceRef = [device['ref'] for device in self.deviceList if device['deviceEUI'].strip().lower() == deviceEUI.strip().lower()]
        assert len(deviceRef)==1, "deleteFactoryDevice: {0} not found".format(deviceEUI)
        deviceRef = deviceRef[0]
        if log: print("DELETE factoryDevices/{0} (devEUI = {1})".format(deviceRef, deviceEUI))
        try:
            deleteRequest = self.request("factoryDevices/{0}".format(deviceRef), method = 'DELETE')
            resultJson = urllib.request.urlopen(deleteRequest).read()
        except urllib.error.HTTPError as error:
            msg = json.loads(error.read())
            print("HTTP Error {0}: {1}".format(msg["code"], msg["message"]))
            print("Delete failed")
            return False
        return True
            
    def __repr__(self):
        return "DX Maker connected: client_id={0}, customer_id={1}".format(self.bearerInfo["client_id"], self.bearerInfo["customer_id"])


        
if __name__ == "__main__":
    bearerToken = "bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJTVUJTQ1JJQkVSOjEwMDAwMDA4NSJdLCJleHAiOjE1Njk4MzM4NTMsImp0aSI6ImM4ZGI4Y2RmLTcxNGYtNGE3OS1hNGZiLTI0OWYxNWVhMGIxYiIsImNsaWVudF9pZCI6ImpzLWxhYnMtYXBpL3JhcGhhZWwuYXBmZWxkb3JmZXItanMtbGFicy1zdWJAYWN0aWxpdHkuY29tIn0.KQaDUlrp6lcPJU9Gz5Re25WlHzMvIW75aef1oECCBGMOcIw9u_I7SyyZOMp1K9-AuJOY60DyfXLnVMIm_3CWaw"
    dev = FactoryDevice("0123D345666E2DBF","F03D29AC71010001","31110123D345666E2DBF")
    dx = DxMaker(bearerToken)
    dx.getFactoryDevices()
    dx.getAstKeys()
    dx.postFactoryDevice(dev)
    dx.deleteFactoryDevice(dev.deviceJson["deviceEUI"])
    dx.getFactoryDevices()
