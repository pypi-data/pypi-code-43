import serial
import time
import struct

class VitalSign:
	port = ""
	def __init__(self,port):
		self.port = port
		print("***vital init***")
		
	def vital_test(self):
		print("------vital Sign ---- ok:" + self.port)
