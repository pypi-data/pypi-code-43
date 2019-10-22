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
# date: Wed Aug 07 14:37:55 CET 2019
'''
uplinkTunnel.py
'''
import os,sys,re,hashlib,binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import xml.etree.ElementTree as ET
import json
from .lorawan import UlUnconfFrame
if sys.version_info[0] < 3: raise Exception("Must be using Python 3")

class DevEUI_uplink():
    def __init__(self, xmlOrJson):
        self.xmlOrJson = xmlOrJson.strip()
        self.AppSKey_clear = None
        self.payload_clear = None
        if self.xmlOrJson.find('<?xml version') != -1:
            # XML document
            for elem in ET.fromstring(self.xmlOrJson):
                if   elem.tag.find('Time')!=-1:        self.Time        = elem.text
                elif elem.tag.find('DevEUI')!=-1:      self.DevEUI      = elem.text
                elif elem.tag.find('FPort')!=-1:       self.FPort       = elem.text
                elif elem.tag.find('FCntUp')!=-1:      self.FCntUp      = elem.text
                elif elem.tag.find('MType')!=-1:       self.MType       = elem.text
                elif elem.tag.find('FCntDn')!=-1:      self.FCntDn      = elem.text
                elif elem.tag.find('payload_hex')!=-1: self.payload_hex = elem.text
                elif elem.tag.find('mic_hex')!=-1:     self.mic_hex     = elem.text
                elif elem.tag.find('CustomerID')!=-1:  self.CustomerID  = elem.text
                elif elem.tag.find('AppSKey')!=-1:     self.AppSKey     = elem.text
                elif elem.tag.find('DevAddr')!=-1:     self.DevAddr     = elem.text
        else:
            # JSON document
            j = json.loads(self.xmlOrJson)['DevEUI_uplink']
            self.Time        = j['Time']
            self.DevEUI      = j['DevEUI']
            self.FPort       = str(j['FPort'])
            self.FCntUp      = str(j['FCntUp'])
            self.MType       = str(j['MType'])
            self.FCntDn      = str(j['FCntDn'])
            self.payload_hex = j['payload_hex']
            self.mic_hex     = j['mic_hex']
            self.CustomerID  = j['CustomerID']
            self.AppSKey     = j['AppSKey']
            self.DevAddr     = j['DevAddr']
    
    def decryptAppSKey(AppSKey, ASTK):
        cipher = Cipher(algorithms.AES(bytes.fromhex(ASTK)), modes.CBC(bytes.fromhex('00'*16)), backend=default_backend()).decryptor()
        clearAppSKey = cipher.update(bytes.fromhex(AppSKey)).hex()
        return clearAppSKey
        
    def decryptPayload(self, ASTK=None):
        #If ASTK is provided, it is used to decrypt AppSKey. Else, AppSKey is expected to be in clear text
        if not self.AppSKey: return self.payload_hex
        if ASTK: 
            assert(type(ASTK) is str and len(ASTK)==32)
            self.AppSKey_clear = DevEUI_uplink.decryptAppSKey(self.AppSKey, ASTK)
        else:
            self.AppSKey_clear = self.AppSKey
        self.payload_clear = UlUnconfFrame.decrypt(self.payload_hex, self.DevAddr.zfill(8), self.FCntUp.zfill(4), self.AppSKey_clear)
        return self.payload_clear
    
    def __repr__(self):
        return "{{'DevEUI_uplink': {{'Time': {0},'DevEUI': {1},'DevAddr': {2},'FPort': {3},'FCntUp': {4},'FCntDn': {5},'payload_hex': {6},'payload_ascii': {7},'AppSKey': {8} }}}}".format(self.Time, self.DevEUI, self.DevAddr, self.FPort, self.FCntUp, self.FCntDn, (self.payload_clear, self.payload_hex)[self.payload_clear is None], binascii.unhexlify((self.payload_clear, self.payload_hex)[self.payload_clear is None].encode()), (self.AppSKey_clear, self.AppSKey)[self.AppSKey_clear is None])
            
class UplinkTunnel(DevEUI_uplink):
    def __init__(self, xmlOrJson, query=None, TIAK=None):
        assert(type(xmlOrJson) is str)
        if not query: return DevEUI_uplink(xmlOrJson)
        assert(type(query) is str)
        if TIAK: assert(type(TIAK) is str and len(TIAK)==32)
        params = dict((k.strip(),v.strip()) for k,v in (i.split('=') for i in query.split('&')))
        self.query_params = 'LrnDevEui={0}&LrnFPort={1}&LrnInfos={2}&AS_ID={3}&Time={4}'.format( \
              params['LrnDevEui'], params['LrnFPort'], params['LrnInfos'], params['AS_ID'], params['Time'])
        self.Token=params['Token']
        self.xmlOrJson = xmlOrJson.strip()
        super().__init__(xmlOrJson)
        self.TIAK = TIAK.lower()
    def token(self):
        assert(self.TIAK)
        body_elements= self.CustomerID + self.DevEUI.upper() + self.FPort + self.FCntUp + self.payload_hex.lower()
        string = (body_elements + self.query_params + self.TIAK).encode('utf-8')
        m = hashlib.sha256(string)
        return m.hexdigest()
    def isTokenValid(self):
        if not (self.token() == self.Token):
            print('Computed: ' + self.token())
            print('Received: ' + self.Token)
        return (self.token() == self.Token)
    def __repr__(self):
        return self.query_params + ',\n' + self.xmlOrJson + ',\nTIAK=' + self.TIAK
    
if __name__ == '__main__':  
    assert(DevEUI_uplink.decryptAppSKey('DFE758AFD5FD4DD8A64BE063373AF6C8', '98CC5DDD614FF2DF44FD09CA9F52CDBA') == 'b0ad83c614043c76c434d460b48b90b4')
    assert(DevEUI_uplink("<?xml version='1.0' encoding='UTF-8'?><DevEUI_uplink xmlns='http://uri.actility.com/lora'><Time>2019-08-05T17:33:51.362+02:00</Time><DevEUI>0123D345666E2DBD</DevEUI><FPort>1</FPort><FCntUp>1</FCntUp><MType>2</MType><FCntDn>1</FCntDn><payload_hex>afac18845bbe3771708042</payload_hex><mic_hex>dcdcc1f5</mic_hex><Lrcid>00000127</Lrcid><LrrRSSI>-65.000000</LrrRSSI><LrrSNR>12.500000</LrrSNR><SpFact>9</SpFact><SubBand>G1</SubBand><Channel>LC3</Channel><DevLrrCnt>1</DevLrrCnt><Lrrid>C000146F</Lrrid><Late>0</Late><LrrLAT>43.640781</LrrLAT><LrrLON>7.017418</LrrLON><Lrrs><Lrr><Lrrid>C000146F</Lrrid><Chain>0</Chain><LrrRSSI>-65.000000</LrrRSSI><LrrSNR>12.500000</LrrSNR><LrrESP>-65.237602</LrrESP></Lrr></Lrrs><CustomerID>100118249</CustomerID><CustomerData>{'alr':{'pro':'LORA/Generic','ver':'1'}}</CustomerData><ModelCfg>0</ModelCfg><AppSKey>439d42627c5afe3d4d536340646621a2</AppSKey><BatteryLevel>0</BatteryLevel><BatteryTime>2019-08-05T17:33:51.362+02:00</BatteryTime><Margin>7</Margin><InstantPER>0.000000</InstantPER><MeanPER>0.000000</MeanPER><DevAddr>05947ED0</DevAddr><AckRequested>0</AckRequested><rawMacCommands>060007</rawMacCommands><TxPower>16.000000</TxPower><NbTrans>1</NbTrans></DevEUI_uplink>").decryptPayload("dbfb0939c448ff1fbf84e84d6ac8ce98") == binascii.hexlify(b"32.5C/90.5F").decode())
    
    assert(UplinkTunnel('{"DevEUI_uplink": {"Time": "2019-04-29T18:21:16.982+02:00","DevEUI": "0024AEB3C02BE1C4","FPort": "1","FCntUp": "0","MType": "2","FCntDn": "0","payload_hex": "3e8d2190","mic_hex": "8a59e259","Lrcid": "00000127","LrrRSSI": "-61.000000","LrrSNR": "7.000000","SpFact": "7","SubBand": "G1","Channel": "LC2","DevLrrCnt": "1","Lrrid": "C000146F","Late": "0","LrrLAT": "43.640781","LrrLON": "7.017418","Lrrs": {"Lrr": [{"Lrrid": "C000146F","Chain": "0","LrrRSSI": "-61.000000","LrrSNR": "7.000000","LrrESP": "-61.790096"}]},"CustomerID": "100122002","CustomerData": {"alr":{"pro":"LORA/Generic","ver":"1"}},"ModelCfg": "0","AppSKey": "f1017d39d12b342f37bfd93e88ab5468","InstantPER": "0.000000","MeanPER": "0.000000","DevAddr": "04227A7F","AckRequested": "0","rawMacCommands": "","TxPower": 14.000000,"NbTrans": 1}}', 'AS_ID=sink&LrnFPort=1&Time=2019-04-29T18:21:17.290+02:00&Token=d306f33c239a9c45d160e0cd6e4071e22a4f4b426f892a0651cf622e81369f3d&LrnDevEui=0024AEB3C02BE1C4&LrnInfos=TWA_100122002.8962.AS-1-4458785','bec499c69e9c939e413b663961636c61').isTokenValid())
    #string='1001220020024AEB3C02BE1C4103e8d2190LrnDevEui=0024AEB3C02BE1C4&LrnFPort=1&LrnInfos=TWA_100122002.8962.AS-1-4458785&AS_ID=sink&Time=2019-04-29T18:21:17.290+02:00bec499c69e9c939e413b663961636c61'
        
    sys.exit(0)