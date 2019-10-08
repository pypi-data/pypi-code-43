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

from .lorawan import reverse_endian as reverse_endian, JoinRequest, JoinAccept
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
log=False


class Device:
    ''' LW1.0 OTAA implementation '''
    def __init__(self, DevEUI, JoinEUI, AppKey, NS=None, JS=None):
        '''Personalization params: DevEUI, JoinEUI, AppKey'''
        assert(type(DevEUI) is str and len(DevEUI)==16)
        assert(type(JoinEUI) is str and len(JoinEUI)==16)
        assert(type(AppKey) is str and len(AppKey)==32)
        self.DevEUI  = DevEUI
        self.JoinEUI = JoinEUI
        self.AppKey  = AppKey
        self.DevNonce="0000"
        self.NS = NS
        self.JS = JS
        
    def join(self):
        '''Join network'''
        frame = JoinRequest(self.JoinEUI,self.DevEUI,self.DevNonce,AppKey=self.AppKey)
        self.DevNonce="{:04X}".format(int(self.DevNonce)+1)
        joinAnswer = self.NS.join(frame, self.JS)
        self.AppSKey, self.NwkSKey = self.deriveKeys(joinAnswer.JoinNonce, joinAnswer.NetId, frame.DevNonce)
        if log: print(frame)
        if log: print(joinAnswer)
        if log: print({"AppSKey":self.AppSKey, "NwkSKey":self.NwkSKey})
        return self.AppSKey, self.NwkSKey
        
    def deriveKeys(self, JoinNonce, NetId, DevNonce):
        '''DevNonce: BIG endian hexa string'''
        if len(DevNonce)!=4: raise MalformedPacketException("Invalid DevNonce (len={}B)".format(len(DevNonce)))     
        cipher = Cipher(algorithms.AES(bytes.fromhex(self.AppKey)), modes.ECB(), backend=default_backend()).encryptor()
        AppSKey = cipher.update(bytes.fromhex("02" + reverse_endian(JoinNonce) + reverse_endian(NetId) + reverse_endian(DevNonce) + "00"*7)).hex()
        cipher = Cipher(algorithms.AES(bytes.fromhex(self.AppKey)), modes.ECB(), backend=default_backend()).encryptor()
        NwkSKey = cipher.update(bytes.fromhex("01" + reverse_endian(JoinNonce) + reverse_endian(NetId) + reverse_endian(DevNonce) + "00"*7)).hex()
        return AppSKey, NwkSKey
        
    def setSessionKeys(self, AppSKey, NwkSKey):
        '''skip join using specific session keys'''
        self.AppSKey, self.NwkSKey = AppSKey, NwkSKey
        
    def __repr__(self):
        return str({"DevEUI":self.DevEUI, "JoinEUI":self.JoinEUI, "AppKey":self.AppKey})


class NetworkServer:
    def __init__(self, NetId, DLSettings, RxDelay, CFList):
        assert(type(NetId)     is str and len(NetId)==6)
        assert(type(DLSettings) is str and len(DLSettings)==2)
        assert(type(RxDelay)   is str and len(RxDelay)==2)
        if CFList: 
            assert(type(CFList) is str and len(CFList)<=32)
        self.NetId = NetId
        self.DLSettings = DLSettings
        self.RxDelay = RxDelay
        self.CFList = CFList
        self.DevAddr = "01234567"
        
    def join(self, joinRequest, JS):
        joinAnswer = JS.join(joinRequest, self.NetId, self.DevAddr, self.DLSettings, self.RxDelay, self.CFList)
        return joinAnswer
    
class JoinServer:
    JoinNonce="000000"
    def __init__(self, JoinEUI, AppKey):
        assert(type(JoinEUI) is str and len(JoinEUI)==16 )
        assert(type(AppKey)  is str and len(AppKey) ==32 )
        self.JoinEUI = JoinEUI
        self.AppKey = AppKey
        
    def join(self,joinRequest, NetId, DevAddr, DLSettings, RxDelay, CFList):
        self.JoinNonce="{:06X}".format(int(self.JoinNonce)+1)
        return JoinAccept(self.JoinNonce,NetId,DevAddr,DLSettings,RxDelay,CFList,MIC=None,AppKey=self.AppKey)

if __name__ == "__main__":
    #d = Device("FFFFFFAA00AC7000","FFFFFFBB00000000","037407b0a2eb121d99b2ad03b605af3a",None,None)
    #jr = JoinRequest.fromPayload("0x0000000000bbffffff0070ac00aaffffffc3f5d6de8f3e")
    #ja = JoinAccept.fromPayload("202573C61502E510C4802CEE5C076A6D9C1329A8F89689BA77BFE13F5A7CD15809",d.AppKey)
    #print(d.deriveKeys(ja.JoinNonce, ja.NetId, jr.DevNonce))
    ns=NetworkServer("000002","00","00","")
    js=JoinServer("ffffffbb00000000","037407b0a2eb121d99b2ad03b605af3a")
    d =Device("FFFFFFAA00AC7000","ffffffbb00000000","037407b0a2eb121d99b2ad03b605af3a",ns,js)
    AppSKey, NwkSKey = d.join()
    assert(AppSKey=="34298d1308374d895464262db888a70c")
    assert(NwkSKey=="26a7aa3ee479b945a3dcc865554fbbf4")