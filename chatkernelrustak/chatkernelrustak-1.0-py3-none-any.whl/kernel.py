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

def get_last_message(host):
	try:
		response = requests.get("{}/glm".format(host)).json()
	except requests.exceptions.ConnectionError:
		os.abort()
	return response


def check_code(code):
	if len(code) == 0:
		return False
	return True if len(re.findall("\d", code)) == len(code) else False


def send(login, message, host):
	ip = socket.gethostbyname(socket.gethostname())
	response = requests.get("{}/send/{}/{}/{}".format(host, login, message, ip)).json()
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
