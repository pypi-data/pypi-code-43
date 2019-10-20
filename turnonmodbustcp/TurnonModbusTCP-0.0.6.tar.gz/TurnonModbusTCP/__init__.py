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
global FrankaModebusTCPclient


def clear_print():

	if str(platform.system())=="Windows":
		os.system("cls")
	if str(platform.system())=="Linux":
		os.system("clear") 




def get_my_IP():
	
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

						clear_print()

						print("getIP() : OSError: [Errno 101] Network is unreachable")
						print(" "+ run[k] +" Connected "+ strd)
						time.sleep(0.15)


def set_client(ServerIP="192.168.6.119",ServerPORT=502):
	global modbus_host
	global modbus_port

	modbus_host = ServerIP
	modbus_port = ServerPORT

	return modbus_host,modbus_port


def client_start():
	global FrankaModebusTCPclient
	global localhost 
	localhost = get_my_IP()
	FrankaModebusTCPclient = ModbusClient(host=modbus_host, port=modbus_port,auto_open=True, auto_close=True)

	clear_print()
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
			regs_list= FrankaModebusTCPclient.read_holding_registers(9001, 1)
			operation = regs_list[0]
			clear_print()
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

						clear_print()
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




def state(address=-403, ID=-1):
	
	if address == -403 and ID == -1 :
		
		while True:

			try:
				data_list8 = FrankaModebusTCPclient.read_holding_registers(8001, 8)
				data_list9 = FrankaModebusTCPclient.read_holding_registers(9001, 8)
				data = data_list8[0]
				data = data_list9[0]
				print("")
				print("")
				print("--------------------------")
				print("   Franka Modbus state")
				print("--------------------------")
				print(" 8001: " + str(data_list8[0]) + "	" + " 9001: " + str(data_list9[0]))
				print(" 8002: " + str(data_list8[1]) + "	" + " 9002: " + str(data_list9[1]))
				print(" 8003: " + str(data_list8[2]) + "	" + " 9003: " + str(data_list9[2]))
				print(" 8004: " + str(data_list8[3]) + "	" + " 9004: " + str(data_list9[3]))
				print(" 8005: " + str(data_list8[4]) + "	" + " 9005: " + str(data_list9[4]))
				print(" 8006: " + str(data_list8[5]) + "	" + " 9006: " + str(data_list9[5]))
				print(" 8007: " + str(data_list8[6]) + "	" + " 9007: " + str(data_list9[6]))
				print(" 8008: " + str(data_list8[7]) + "	" + " 9008: " + str(data_list9[7]))
				print("")
				print("")
				return True
				break

			except TypeError:
				print("ERROR: state(): Connection to modbus server failed")
				return False
		

	elif address >= 8001 and address <= 8008 :

		if ID == -1 :

			while True:

				try:
					data_list = FrankaModebusTCPclient.read_holding_registers(address, 1)
					data = data_list[0]
					return data
					break

				except TypeError:
					print("ERROR: state(): Connection to modbus server failed")
					time.sleep(1)

		elif ID >= 1 and ID <= 16 :
			
			while True:

				try:
					data_list = FrankaModebusTCPclient.read_holding_registers(address, 1)
					data = data_list[0]
					fillBinData = '{:016b}'.format(data)
					data_bin = (str(fillBinData))[::-1]
					ID_data = bool(int(data_bin[ID-1:ID]))
					return ID_data
					break

				except TypeError:
					print("ERROR: state(): Connection to modbus server failed")
					time.sleep(1)
		
		
		else :
			print("ERROR: state(): ID value is out of range (1~16)")


	elif address >= 9001 and address <= 9008 :
		
		if ID == -1 :

			while True:

				try:
					data_list = FrankaModebusTCPclient.read_holding_registers(address, 1)
					data = data_list[0]
					return data
					break

				except TypeError:
					print("ERROR: state(): Connection to modbus server failed")
					time.sleep(1)

		elif ID >= 1 and ID <= 16 :
			
			while True:

				try:
					data_list = FrankaModebusTCPclient.read_holding_registers(address, 1)
					data = data_list[0]
					fillBinData = '{:016b}'.format(data)
					data_bin = (str(fillBinData))[::-1]
					ID_data = bool(int(data_bin[ID-1:ID]))
					return ID_data
					break

				except TypeError:
					print("ERROR: state(): Connection to modbus server failed")
					time.sleep(1)



	else:

		print("ERROR: state(): address value is out of range")




#def mode():





#def FRANKA_STATE():





#def visual_command_Read():





#def visual_wait_command():





#def visual_output_Write():





set_client()
client_start()

state()




        






































