
import ain.common.constants as constants
import re
import requests
import json

def workerNameCheck(name):
  if re.match("^[a-zA-Z0-9_-]*$", name):
    return True
  else:
    return False

def versionCheck():
  MESSAGE = {
    "jsonrpc": "2.0",
    "method": "ain_checkCliVersion",
    "params": {
      "version": constants.VERSION
    },
    "id": 1
  }
  headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
  try:
    response = requests.post(constants.TRACKER_ADDR, data=json.dumps(MESSAGE), headers=headers)
    if (response.json()['result']['result'] != 0): 
      print('[!] you have to input "sudo pip3 install --upgrade ain-worker"')
      return False
    return True
  except Exception as e:
    print("[-] tracker server error")
    print(e)
    return False