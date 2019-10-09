# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 19:12:24 2019

@author: Win10 Pro x64
"""
import socket


class BP730:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        
    def probe(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((self.ip,self.port))
        if result == 0:
            ok = True
            desc = "BP730 Port is open"
        else:
            ok = False
            desc = "BP730 Port is not open"
        sock.close()
        
        return ok, desc
        
    def printLabel(self, label):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))
        s.send(label.encode())
        s.close()