import time
import pyModbusTCP
import os
import sys
import socket
import platform

from pyModbusTCP.client import ModbusClient

global modbus_host
global modbus_port
global localhost

def clear_Print():

	if str(platform.system())=="Windows":
		os.system("cls")
	if str(platform.system())=="Linux":
		os.system("clear") 




def getMyIP():
	
	while True:
		try:
			myname = socket.getfqdn(socket.gethostname())
			get_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			get_s.connect(('8.8.8.8', 0))
			ip = ('hostname: %s, localIP: %s') % (myname, get_s.getsockname()[0])
			return get_s.getsockname()[0]

		except OSError:
			for i in range(4):
				
				strd = ""
				run=["~","\\","|","/"]
				for j in range(3):
					strd+="."

					for k in range(4):

						clear_Print()

						print("getIP() : OSError: [Errno 101] Network is unreachable")
						print(" "+ run[k] +" Connected "+ strd)
						time.sleep(0.15)


def SetClient(ServerIP="192.168.6.119",ServerPORT=502):
	global modbus_host
	global modbus_port

	modbus_host = ServerIP
	modbus_port = ServerPORT

	return modbus_host,modbus_port


def Start():
	global c
	global localhost 
	localhost = getMyIP()
	c = ModbusClient(host=modbus_host, port=modbus_port,auto_open=True, auto_close=True)

	clear_Print()
	print(" ====================================")
	print("       Franka Modbus TCP Client  ")
	print(" ====================================")
	print(" My IP: "+ localhost)
	print(" Server IP: "+ modbus_host +"   Port: "+ str(modbus_port) )
	print(" ====================================")
	print("")
	
	time.sleep(1)

	while True: 
		try:
			regs_list= c.read_holding_registers(9001, 1)
			operation = regs_list[0]
			clear_Print()
			print(" ====================================")
			print("       Franka Modbus TCP Client  ")
			print(" ====================================")
			print(" My IP: "+ localhost)
			print(" Server IP: "+ modbus_host +"   Port: "+ str(modbus_port) )
			print(" ====================================")
			print("")
			print("")
			print(" Connected...  Success")
			break
		except TypeError:
			for i in range(4):
				
				strd = ""
				run=["~","\\","|","/"]
				for j in range(3):
					strd+="."

					for k in range(4):

						clear_Print()
						print(" ====================================")
						print("       Franka Modbus TCP Client  ")
						print(" ====================================")
						print(" My IP: "+ localhost)
						print(" Server IP: "+ modbus_host +"   Port: "+ str(modbus_port) )
						print(" ====================================")
						print("")
						print("") 						
						print("  Unable to connect to Host")
						print("")
						print("Please make sure the Host's settings are correct")
						print(" "+ run[k] +" Connected "+ strd)
						time.sleep(0.15)		










        


































