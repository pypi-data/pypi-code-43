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


def set_client(ServerIP="192.168.0.5",ServerPORT=502):
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
		

	elif address >= 8000 and address <= 9999 :

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



	else:

		print("ERROR: state(): address value is out of range")



def Read(read_address=-1):
	if read_address >= 8000 and read_address <= 9999 : 
		return state(read_address)
	else:
		print("ERROR: Read(): Address is out of range")




def Write(write_address=-1, write_data=0):
	
	if write_address >= 8000 and write_address <= 9999 and write_data >= 0 and write_data <= 65535:

		errorsum = 0

		while True:

			FrankaModebusTCPclient.write_single_register(write_address,write_data)

			if state(write_address) == write_data :
				break

			else :


				if errorsum > 5 :
					break
				strd = ""
				run=["~","\\","|","/"]
				for j in range(3):
					strd+="."

					for k in range(4):

						clear_print()
						print("")
						print("WARNING: Write(): Sending failed")
						print(" "+ run[k] +" Resending ("+ str(errorsum) +")"+ strd)
						time.sleep(0.15)
				errorsum = errorsum +1
				


	elif write_address < 8000 or write_address > 9999 :
		
		print("")
		print("ERROR: Write(): Sending failed")
		print("       Write(): address is out of range")
		
	elif write_data < 0 or write_data > 65535 :

		print("")
		print("ERROR: Write(): Data is out of range")
		print("       Write(): Sending failed")
	else:
		print("")
		print("ERROR: Write(): Sending failed")


def server(user_command="state", ckk="CK" ):

	if user_command == "state":
		state()
		ckk = "l"

	elif user_command == "shutdown":
		Write(9998,9999)
		time.sleep(1)

	elif user_command == "reboot":
		Write(9998,8888)
		time.sleep(1)

	elif user_command == "Y" or user_command == "y":
		ckk = "y"

	elif user_command == "N" or user_command == "n":
		ckk = "n"

	else:
		print('ERROR: server(): No command "' + user_command + '"')


	if ckk == "CK":
		
		clear_print()
		print("")
		print("[user command]: " + user_command)
		print("")
		print(" WARNING: This will shutdown or reboot the server !!")
		print("")
		print(" Please confirm the command? (y/n)")
		print("")


	elif ckk == "N" or ckk == "n":
		Write(9998,0)

	elif ckk == "Y" or ckk == "y":
		Write(9998,1)











def visual_command_Read(return_back="command"):

	if return_back == "mode" :
		return Read(9002)

	elif return_back == "command" :

		arm_mode = Read(9002)
		
		if arm_mode == 66 or arm_mode == 0:
			return "N"

		elif arm_mode == 99:
			return "ERR"

		elif arm_mode == 1:
			return "PICK_C"

		elif arm_mode == 2:
			return "PICK_S"

		elif arm_mode == 3:
			return "N"

		elif arm_mode == 4:
			return "TD"

		elif arm_mode == 5:
			return "N"

		elif arm_mode == 6:
			return "TR"

		elif arm_mode == 7:
			return "N"

		elif arm_mode == 8:
			return "N"

		elif arm_mode == 9:
			return "N"






	else:
		print('ERROR: visual_command_Read: no "' + return_back +'" to return.')

	




#def visual_wait_command():






#def mode():





#def FRANKA_STATE():







def visual_output_Write(datastr=""):

	if datastr[0:1] == "X" and datastr[4:5] == "Y" and datastr[9:10] == "Z" and datastr[13:14] == "R"  :

		try:
			x = int(datastr[1:4])
			y = int(datastr[5:9])
			z = int(datastr[10:13])
			rot = int(datastr[14:17])

			if x>=0 and x<= 999:
				Write(8003,x)
			else:
				print('ValueError: visual_output_Write: "'+ str(x) +'" X is out of range')
				return False

			if y>=-999 and y<= 999:
				Write(8004,y+1000)
			else:
				print('ValueError: visual_output_Write: "'+ str(y) +'" Y is out of range')
				return False

			if x>=0 and x<= 999:
				Write(8005,z)
			else:
				print('ValueError: visual_output_Write: "'+ str(z) +'" Z is out of range')
				return False

			if rot>=0 and rot<= 359:
				Write(8006,rot)
			else:
				print('ValueError: visual_output_Write: "'+ str(rot) +'" R is out of range')
				return False

			Write(9001,3)
			return True



		except ValueError:
			print('ValueError: visual_output_Write: "'+ datastr +'" Data ValueError')
			return False


	elif datastr[0:1] == "X" and datastr[4:5] == "Y" and datastr[8:9] == "Z" and datastr[12:13] == "R"  :

		try:
			x = int(datastr[1:4])
			y = int(datastr[5:8])
			z = int(datastr[9:12])
			rot = int(datastr[13:16])

			if x>=0 and x<= 999:
				Write(8003,x)
			else:
				print('ValueError: visual_output_Write: "'+ str(x) +'" X is out of range')
				return False

			if y>=-999 and y<= 999:
				Write(8004,y+1000)
			else:
				print('ValueError: visual_output_Write: "'+ str(y) +'" Y is out of range')
				return False

			if x>=0 and x<= 999:
				Write(8005,z)
			else:
				print('ValueError: visual_output_Write: "'+ str(z) +'" Z is out of range')
				return False

			if rot>=0 and rot<= 359:
				Write(8006,rot)
			else:
				print('ValueError: visual_output_Write: "'+ str(rot) +'" R is out of range')
				return False

			Write(9001,3)
			return True



		except ValueError:
			print('ValueError: visual_output_Write: "'+ datastr +'" Data ValueError')
			return False
		




	elif datastr[0:2] == "TD" :

		try:
			td = int(datastr[2:3])

			if td>=0 and td<= 1:
				Write(8007,td)
			else:
				print('ValueError: visual_output_Write: "'+ str(td) +'" TD is out of range')
				return False

			Write(9001,5)
			return True

		except ValueError:
			print('ValueError: visual_output_Write: "'+ datastr +'" Data ValueError')
			return False

		


	elif datastr[0:2] == "TR" :  

		try:
			tr = int(datastr[2:5])

			if tr>=0 and tr<= 359:
				Write(8008,tr)
			else:
				print('ValueError: visual_output_Write: "'+ str(tr) +'" TR is out of range')
				return False

			Write(9001,7)
			return True

		except ValueError:
			print('ValueError: visual_output_Write: "'+ datastr +'" Data ValueError')
			return False
		
	else:
		print('ERROR: visual_output_Write: "'+ datastr +'" Format error')
		return False
	








def robot_control(control_mode=66, data_X=3001, data_Y=3001, data_Z=3001):
	
	if control_mode == 1 :
		
		if data_X != 3001 :
			Write(8003, data_X)
		if data_Y != 3001 :
			Write(8004, (data_Y+1000) )
		if data_Z != 3001 :
			Write(8005, data_Z)

		Write(9008, 86)
		time.sleep(0.5)

		times = 0
		while times < 10 :
			
			if Read(9002) == 86 :

				Write(9008, 1)
				time.sleep(0.5)

			if Read(9002) == 1 :

				Write(9008, 66)
				
				break

			print("WARNING: robot_control(): Wait for Franka to respond")
			time.sleep(1) 
			times+=1

		if times >= 10 :
			print("")
			print("ERROR: robot_control(): Franka did not respond")
		
		while Read(9002) == 1:
			time.sleep(1)
			

		Write(9008, 66)

	elif control_mode == 0 :


		if data_X != 3001 :
			Write(8003, data_X)
		if data_Y != 3001 :
			Write(8004, (data_Y+1000) )
		if data_Z != 3001 :
			Write(8005, data_Z)
		Write(9008, 0)


#set_client("192.168.0.5")

#client_start()

#robot_control(1,420,0,500)
#robot_control(1,420,100,400)
#robot_control(1,420,0,600)
#Write(8002, 145)

#print(Read(8002))


#visual_output_Write("X123Y-456Z789R135")

#visual_output_Write("X420Y-230Z600R000")

#visual_output_Write("TR000")

#visual_output_Write("TD0")

#visual_output_Write("TR365")


































