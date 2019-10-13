import re
import json
import time
import os
import socket
import base64

try:
	import requests
except ModuleNotFoundError:
	print("Install dependencies: requests")
	os.abort()


code_warn = "Используйте числа в коде"

def check_server(host):
	try:
		response = requests.get("{}/check_server".format(host)).json()
	except json.decoder.JSONDecodeError:
		return False
	return response["worked"]

def get_last_message(host):
	print(host)
	try:
		response = requests.get("{}/glm".format(host)).json()
	except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
		if check_server(host):
			pass
		else:
			messagebox.showwarning("Внимание", "Хост не доступен для соединения")
			os.abort()
		return get_last_message(host)
	return response


def check_code(code):
	if len(code) == 0:
		return False
	return True if len(re.findall("\d", code)) == len(code) else False


def send(login, message, host):
	ip = socket.gethostbyname(socket.gethostname())
	try:
		response = requests.get("{}/send/{}/{}/{}".format(host, login, message, ip)).json()
	except json.decoder.JSONDecodeError:
		if check_server(host):
			print("Пиши медленнее уебан сука")
		else:
			messagebox.showwarning("Внимание", "Хост не доступен для соединения")
			os.abort()
		return False
	return response


def crypt(code, message):
	text = ""
	message = str(base64.b64encode(message.encode()))
	for x in str(message[2:-1]):
		text += str(int(ord(x))*int(code)*3) + " "
	return text


def decrypt(code, message):
	text = ""
	message = message.split()
	try:
		for x in message:
			text += str(chr(int(int(x)/int(code)/3)))
	except ValueError:
		return "(сообщение не расшифровано)"
	return base64.b64decode(eval("b\'"+text+"\'")).decode("utf-8")


def check_mess(l_id, l_mess_id):
	return True if int(l_id) > int(l_mess_id) else False

def check_login(login, l_login):
	return True if login != l_login else False

def init(login, host):
	ip = socket.gethostbyname(socket.gethostname())
	try:
		response = requests.get("{}/init/{}/{}".format(host, login, ip)).json()
	except json.decoder.JSONDecodeError:
		if check_server(host):
			pass
		else:
			messagebox.showwarning("Внимание", "Хост не доступен для соединения")
			os.abort()
		return init(login, host)
	return response

def check_new_user(host):
	try:
		response = requests.get("{}/newuser".format(host)).json()
	except json.decoder.JSONDecodeError:
		if check_server(host):
			pass
		else:
			messagebox.showwarning("Внимание", "Хост не доступен для соединения")
			os.abort()
		return check_new_user(host)
	return response
