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
from math import ceil
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.cmac import CMAC

class MalformedPacketException(Exception):
    def __init__(self, msg = ""):
        Exception.__init__(self, msg)
class DecryptionException(Exception):
    def __init__(self, msg = ""):
        Exception.__init__(self, msg)
        
def reverse_endian(hexastring):
    return "".join(reversed([hexastring[i:i+2] for i in range(0, len(hexastring), 2)]))

def xor_bytes(a,b):
    '''xor 2 bytes arrays and return hexstring format'''
    return "".join([format(ai^bi,'x') for (ai,bi) in zip(a,b)])
        
class Frame:
    MType = None
    ''' MHDR (1B) | MACPayload/JoinReq/JoinAns (var size) | MIC (4B) '''   
    def __init__(self,MHdr,MACPayload,MIC=None):
        assert(type(MHdr) is MHDR)
        assert(type(MACPayload) is str)
        self.MHDR = MHdr
        self.MACPayload = MACPayload
        self.MIC = MIC
        self.PHYPayload = MHdr.MHdr+MACPayload+(MIC if MIC else "00000000")
    
    def fromPayload(PHYPayload):
        '''Decode a LoRaWAN PHYPayload. Input: PHYPayload = big endian hexadecimal string'''
        if PHYPayload[0:2]=="0x": PHYPayload=PHYPayload[2:]
        MHdr       = PHYPayload[0:2]
        MACPayload = PHYPayload[2:-8]
        MIC        = PHYPayload[-8:]
        return Frame(MHDR.fromPayload(MHdr), MACPayload, MIC)
    
    def decode(self, AppKey=None, AppSKey=None, NwkSKey=None):
        '''Return decoded subclass'''
        try: 
            decoded = self.MHDR.MTypeClass(self.PHYPayload, encrypted=self.encrypted, AppKey=self.AppKey, AppSKey=self.AppSKey, NwkSKey=self.NwkSKey)
            return decoded
        except:
            raise MalformedPacketException("Error decoding {}".format(self.MHDR))
            
    def __repr__(self):
        '''JSON Backend Interface fields (when available)'''
        return str({"MessageType":"Undecoded frame","MACVersion":"1.0","PHYPayload":self.PHYPayload,"MHDR":self.MHDR,"MIC":self.MIC})

class UlUnconfFrame(Frame):
    MType = 2
    ''' DevAddr (4B) | FCtrl =ADR|ADRACKReq|ACK|ClassB|FOpsLen (1B) | FCnt (2B) | FOps (var size) | FPort (1B) | Payload '''   
    def __init__(self,DevAddr,ADR,ADRACKReq,ACK,ClassB,FCnt,FOps,FPort=None,Payload=None,MIC=None,NwkSKey=None):
        assert(type(DevAddr)  is str and len(DevAddr)==8 )
        assert(type(ADR)      is str and len(ADR)==1 )
        assert(type(ACK)      is str and len(ACK)==1 )
        assert(type(ClassB)   is str and len(ClassB)==1 )
        assert(type(FCnt)     is str and len(FCnt)==4 )
        assert(type(FOps)     is str and len(FOps)<=30 )
        if Payload:
            assert(type(FPort) is str and len(FPort)==2 )
            self.FPort = FPort
            self.Payload = Payload
        self.DevAddr= DevAddr
        self.ADR    = ADR
        self.ADRACKReq = ADRACKReq
        self.ACK    = ACK
        self.ClassB = ClassB
        self.FCtrl  = "{:02X}".format(int(ADR)<<7 + int(ADRACKReq)<<6 + int(ACK)<<5 + int(ClassB)<<4 + int(len(FOps)//2))
        self.FCnt   = FCnt
        self.FOps   = FOps
        frame = reverse_endian(DevAddr) + self.FCtrl + reverse_endian(FCnt) + reverse_endian(FOps) + reverse_endian(FPort) + Payload
        super().__init__(MHdr=MHDR(MHDR.LORAWAN_V1,self.MType), MACPayload=frame, MIC=MIC)
        if MIC: 
            assert(type(MIC) is str and len(MIC)==8 )
            if NwkSKey: 
                assert(type(NwkSKey) is str and len(NwkSKey)==32)
                assert(MIC==self.computeMIC(NwkSKey))
        else:
            assert(type(NwkSKey) is str and len(NwkSKey)==32)
            MIC=self.computeMIC(NwkSKey)
        self.MIC  = MIC
        
    def computeMIC(self, NwkSKey):
        assert(type(NwkSKey) is str and len(NwkSKey)==32 )              
        dir="00"
        B0 = "49"+"00"*4+dir+reverse_endian(self.DevAddr)+"0000"+reverse_endian(self.FCnt)+"00"+"{:02X}".format(len(self.PHYPayload[:-8])//2) + self.PHYPayload[:-8]
        cmac = CMAC(algorithms.AES(bytes.fromhex(NwkSKey)), backend=default_backend())
        cmac.update(bytes.fromhex(B0))
        MIC = cmac.finalize().hex()[:8]
        return MIC
        
    def fromPayload(PHYPayload):    
        '''Decode a LoRaWAN PHYPayload. Input: PHYPayload = big endian hexadecimal string'''
        if PHYPayload[0:2]=="0x": PHYPayload=PHYPayload[2:]
        frame = Frame.fromPayload(PHYPayload)
        if frame.MHDR.MType != UlUnconfFrame.MType:
            raise MalformedPacketException("Invalid UL Unconfirmed Frame (MType={} is {})".format(frame.MHDR.MType, frame.MHDR.MTypeClass.__name__))
        DevAddr  = reverse_endian(frame.MACPayload[0:8])
        FCtrl    = frame.MACPayload[8:10]
        ADR      = str((int(FCtrl[0]) >> 3) & 1)
        ADRACKReq= str((int(FCtrl[0]) >> 2) & 1)
        ACK      = str((int(FCtrl[0]) >> 1) & 1)
        ClassB   = str(int(FCtrl[0]) & 1)
        FOpsLen  = int(FCtrl[1])
        FCnt     = reverse_endian(frame.MACPayload[10:14])
        FOps     = reverse_endian(frame.MACPayload[14:14+FOpsLen])
        if len(frame.MACPayload)>2*FOpsLen:
            FPort   = frame.MACPayload[(7+FOpsLen)*2:(7+FOpsLen)*2+2]
            Payload = frame.MACPayload[(7+FOpsLen)*2+2:]
        else:   
            FPort=None
            Payload=None
        return UlUnconfFrame(DevAddr,ADR,ADRACKReq,ACK,ClassB,FCnt,FOps,FPort,Payload,frame.MIC)
        
    def decrypt(payload, DevAddr, FCnt, AppSKey):
        assert(type(DevAddr) is str and len(DevAddr)==8 )              
        assert(type(FCnt)    is str and len(FCnt)==4 )              
        assert(type(AppSKey) is str and len(AppSKey)==32 )              
        k = int(ceil(len(payload) / 16.0))
        dir="00"
        FCnt32bIdx="0000" #doesn't support 16b FCnt loopback
        S = bytes()
        for i in [j+1 for j in range(k)]:
            cipher = Cipher(algorithms.AES(bytes.fromhex(AppSKey)), modes.ECB(), backend=default_backend()).encryptor()
            Si = "01" + 4*"00" + dir + reverse_endian(DevAddr) + reverse_endian(FCnt) + FCnt32bIdx + "00" + "{:02X}".format(i)
            S += cipher.update(bytes.fromhex(Si))
        return xor_bytes(bytes.fromhex(payload + (16-len(payload)%16)*"00"), S)[:len(payload)]
        
    def encrypt(payload, DevAddr, FCnt, AppSKey):
        return UlUnconfFrame.decrypt(payload, DevAddr, FCnt, AppSKey)

    def __repr__(self):
        '''JSON Backend Interface fields (when available)'''
        return str({"MessageType":"Uplink","MACVersion":"1.0","PHYPayload":self.PHYPayload,"DevAddr":self.DevAddr,"FCtrl":self.FCtrl,"FCnt":int(self.FCnt,16),"FOps":self.FOps,"FPort":int(self.FPort,16),"Payload":self.Payload,"MIC":self.MIC})
    
class DlUnconfFrame(Frame):
    MType = 3
    def __init__(self):
        assert("TBD")

class UlConfFrame(Frame):
    MType = 4
    def __init__(self):
        assert("TBD")

class DlConfFrame(Frame):
    MType = 5
    def __init__(self):
        assert("TBD")
        
class RFU(Frame):
    MType = 6
    def __init__(self):
        assert("TBD")
        
class Proprietary(Frame):
    MType = 7
    def __init__(self):
        assert("TBD")
        
class JoinRequest(Frame):
    ''' JoinEui(8B) | DevEui(8B) | DevNonce(2B) '''
    MType = 0
    def __init__(self,JoinEUI,DevEUI,DevNonce,MIC=None,AppKey=None):
        assert(type(DevEUI)   is str and len(DevEUI)==16 )
        assert(type(JoinEUI)  is str and len(JoinEUI)==16 )
        assert(type(DevNonce) is str and len(DevNonce)==4 )
        frame = reverse_endian(JoinEUI) + reverse_endian(DevEUI) + reverse_endian(DevNonce)
        super().__init__(MHdr=MHDR(MHDR.LORAWAN_V1,self.MType), MACPayload=frame, MIC=MIC)
        self.JoinEUI  = JoinEUI
        self.DevEUI   = DevEUI
        self.DevNonce = DevNonce
        if MIC: 
            assert(type(MIC) is str and len(MIC)==8 )
            if AppKey: 
                assert(type(AppKey) is str and len(AppKey)==32)
                assert(MIC==self.computeMIC(AppKey))
        else:
            assert(type(AppKey) is str and len(AppKey)==32)
            MIC=self.computeMIC(AppKey)
        self.MIC      = MIC
    
    def fromPayload(PHYPayload):
        '''Decode a LoRaWAN PHYPayload. Input: PHYPayload = big endian hexadecimal string'''
        frame = Frame.fromPayload(PHYPayload)
        if frame.MHDR.MType != JoinRequest.MType:
            raise MalformedPacketException("Invalid join request (MType={} is {})".format(frame.MHDR.MType, frame.MHDR.MTypeClass.__name__))
        if len(frame.MACPayload)!=36: raise MalformedPacketException("Invalid join request")
        JoinEUI  = reverse_endian(frame.MACPayload[:16])
        DevEUI   = reverse_endian(frame.MACPayload[16:32])
        DevNonce = reverse_endian(frame.MACPayload[32:36])
        return JoinRequest(JoinEUI,DevEUI,DevNonce, frame.MIC)
    
    def computeMIC(self,AppKey):
        cmac = CMAC(algorithms.AES(bytes.fromhex(AppKey)), backend=default_backend())
        cmac.update(bytes.fromhex(self.PHYPayload[:-8]))
        MIC = cmac.finalize().hex()[:8]
        return MIC
    
    def __repr__(self):
        '''JSON Backend Interface fields (when available)'''
        return str({"MessageType":"JoinReq","MACVersion":"1.0","PHYPayload":self.PHYPayload,"JoinEUI":self.JoinEUI,"DevEUI":self.DevEUI,"DevNonce":self.DevNonce,"MIC":self.MIC})

class JoinAccept(Frame):
    '''  JoinNonce(3B) | NetId(3B) | DevAddr(4B) | DLSettings (1B) | RxDelay(1B) | CFList(0..16B) '''
    MType = 1
    def __init__(self,JoinNonce,NetId,DevAddr,DLSettings,RxDelay,CFList=None,MIC=None,AppKey=None):
        assert(type(JoinNonce) is str and len(JoinNonce)==6)
        assert(type(NetId)     is str and len(NetId)==6)
        assert(type(DevAddr)   is str and len(DevAddr)==8)
        assert(type(DLSettings) is str and len(DLSettings)==2)
        assert(type(RxDelay)   is str and len(RxDelay)==2)
        frame = reverse_endian(JoinNonce) + reverse_endian(NetId) + reverse_endian(DevAddr) + DLSettings + RxDelay
        self.JoinNonce  = JoinNonce 
        self.NetId      = NetId     
        self.DevAddr    = DevAddr   
        self.DLSettings = DLSettings
        self.RxDelay    = RxDelay   
        self.CFList     = CFList    
        if CFList: 
            assert(type(CFList) is str and len(CFList)<=32)
            frame += reverse_endian(CFList)
        super().__init__(MHdr=MHDR(MHDR.LORAWAN_V1,self.MType), MACPayload=frame, MIC=MIC)
        if MIC: 
            assert(type(MIC) is str and len(MIC)==8 )
            if AppKey: 
                assert(type(AppKey) is str and len(AppKey)==32)
                assert(MIC==self.computeMIC(AppKey))
        else:
            assert(type(AppKey) is str and len(AppKey)==32)
            MIC=self.computeMIC(AppKey)
        self.MIC      = MIC

    def fromPayload(PHYPayload, AppKey=None):
        frame = Frame.fromPayload(PHYPayload)
        if frame.MHDR.MType != JoinAccept.MType:
            raise MalformedPacketException("Invalid join accept (MType={} is {})".format(frame.MHDR.MType, frame.MHDR.MTypeClass.__name__))
        if len(frame.PHYPayload) == 66: 
            if AppKey: frame = JoinAccept.decrypt(frame, AppKey)
            else: raise DecryptionException("Missing AppKey to decrypt encrypted JoinAccept")
        if len(frame.MACPayload)<24 or len(frame.MACPayload)>56: 
            raise MalformedPacketException("Invalid join accept (len={}B)".format(len(frame.MACPayload)))
        JoinNonce  = reverse_endian(frame.MACPayload[:6])
        NetId      = reverse_endian(frame.MACPayload[6:12])
        DevAddr    = reverse_endian(frame.MACPayload[12:20])
        DLSettings = frame.MACPayload[20:22]
        RxDelay    = frame.MACPayload[22:24]
        if len(frame.MACPayload)>24:
            CFList = reverse_endian(frame.MACPayload[24:])
        else:
            CFList = None
        return JoinAccept(JoinNonce,NetId,DevAddr,DLSettings,RxDelay,CFList,frame.MIC)
            
    def decrypt(frame, AppKey):
        assert(type(AppKey) is str and len(AppKey)==32 )
        cipher = Cipher(algorithms.AES(bytes.fromhex(AppKey)), modes.ECB(), backend=default_backend()).encryptor()
        # Encrypt(MACPayload + MIC) to decrypt payload
        clearPayload = cipher.update(bytes.fromhex(frame.MACPayload + frame.MIC)).hex()
        # Return payload without MIC + decrypted MIC
        return Frame(MHdr=MHDR(MHDR.LORAWAN_V1,JoinAccept.MType), MACPayload=clearPayload[:-8], MIC=clearPayload[-8:]) 
    
    def encrypt(self, AppKey):
        assert(type(AppKey) is str and len(AppKey)==32 )
        cipher = Cipher(algorithms.AES(bytes.fromhex(AppKey)), modes.ECB(), backend=default_backend()).decryptor()
        # Decrypt(MACPayload + MIC) to encrypt payload
        encryptedPayload = cipher.update(bytes.fromhex(self.MACPayload + self.MIC)).hex()
        # Return encrypted frame = MHDR + encrypted payload + encrypted MIC
        return MHDR(MHDR.LORAWAN_V1,JoinAccept.MType).MHdr + encryptedPayload

    def computeMIC(self,AppKey):
        cmac = CMAC(algorithms.AES(bytes.fromhex(AppKey)), backend=default_backend())
        cmac.update(bytes.fromhex(self.PHYPayload[:-8]))
        MIC = cmac.finalize().hex()[:8]
        return MIC

    def __repr__(self):
        '''JSON Backend Interface fields (when available)'''
        return str({"MessageType":"JoinAns","MACVersion":"1.0","PHYPayload":self.PHYPayload,"JoinNonce":self.JoinNonce,"NetId":self.NetId,"DevAddr":self.DevAddr,"DLSettings":self.DLSettings,"RxDelay":self.RxDelay, "CFList": self.CFList, "MIC":self.MIC})

class MHDR:
    '''MType directly maps to decoding Class'''
    LORAWAN_V1 = 0;
    MTYPE = {JoinRequest.MType: JoinRequest,    
             JoinAccept.MType: JoinAccept, 
             UlUnconfFrame.MType: UlUnconfFrame, 
             DlUnconfFrame.MType: DlUnconfFrame,
             UlConfFrame.MType: UlConfFrame,   
             DlConfFrame.MType: DlConfFrame,
             RFU.MType: RFU,           
             Proprietary.MType: Proprietary}

    def __init__(self, Major, MType):
        assert(type(Major) is int)
        assert(MType in MHDR.MTYPE.keys())
        self.Major = Major
        self.MType = MType
        self.MTypeClass = self.MTYPE[self.MType]
        self.MHdr = "{:02X}".format((MType & 0x7) << 5 + (Major & 0x3))
        
    def fromPayload(mhdr):
        Major = int(mhdr,16) & 0x3
        if Major != MHDR.LORAWAN_V1:
            raise MalformedPacketException("Invalid major version")
        MType = (int(mhdr,16) >> 5 ) & 0x7
        return MHDR(Major, MType)
        
    def __repr__(self):
        return str(self.MTypeClass.__name__)
        
if __name__ == "__main__":
    assert(UlUnconfFrame.fromPayload("40d07e940500000001595548a403821d336ad7cd61e8d9e8").computeMIC("7f7393d88f6a87565ea0e8aae6da83e5") == '61e8d9e8')
    assert(JoinRequest.fromPayload("0x0001000171ac293df0bd2d6e6645d32301e2e2f98f810f").computeMIC("28125FFD247F3D933834B4A2862CE05D") == 'f98f810f')
    assert(JoinAccept.fromPayload("2051b239de5da07db5a8844c4714488cf116815975a04e70bf86282ed11eaa5289", "28125FFD247F3D933834B4A2862CE05D").computeMIC("28125FFD247F3D933834B4A2862CE05D") == 'a782a999')
    assert(JoinAccept.fromPayload("2051b239de5da07db5a8844c4714488cf116815975a04e70bf86282ed11eaa5289", "28125FFD247F3D933834B4A2862CE05D").encrypt("28125FFD247F3D933834B4A2862CE05D") == "2051b239de5da07db5a8844c4714488cf116815975a04e70bf86282ed11eaa5289")