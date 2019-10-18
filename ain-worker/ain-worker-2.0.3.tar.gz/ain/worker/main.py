import subprocess
import dotenv
import requests_unixsocket
import os
import ain.common.constants as constants
from ain.worker.ttyd import Ttyd
from ain.worker.docker import Docker
import ain.worker.util as util

class Worker():

  def __init__(self):
    self.ENVS = dotenv.dotenv_values(constants.ENV_FILE_PATH)
    self.session = requests_unixsocket.Session()
    self.hostTtydSocket = constants.SHARED_PATH + '/ain_worker_ttyd.sock'
    sharedPath = constants.SHARED_PATH.replace("/", '%2F')
    self.workerAddress =  'http+unix://' + sharedPath + '%2Fain_worker.sock'
    
  def start(self, optionRun):
    
    if (os.path.exists(self.hostTtydSocket)):
      print("you have to input 'sudo ain worker stop'")
      return
    
    for key in ["NAME", "LIMIT_COUNT", "PRICE", "MNEMONIC", "SERVER_IP", "GPU"]:
      if self.ENVS[key].replace(" ", "") == "" and optionRun[key] == "":
        print('[-] ' + key + '- empty')
        return

      if optionRun[key] != "":
        self.ENVS[key] = optionRun[key]
        dotenv.set_key(constants.ENV_FILE_PATH, key, optionRun[key])
        
    if optionRun["DESCRIPTION"] != "" and optionRun["DESCRIPTION"] != "empty":
      dotenv.set_key(constants.ENV_FILE_PATH, "DESCRIPTION", optionRun["DESCRIPTION"])
      
    if util.workerNameCheck(self.ENVS["NAME"]) == False:
      print("The worker name must be 10 characters or less and can be any combination of numbers, alphabets, '-' and '_' ")
      print(self.ENVS["NAME"])
      return
    
    print("[?] Do you want to start? (y/n)")
    answer = input()
    if (answer.lower() != 'y'):
      return
    
    # open provider's ttys socket 
    Ttyd.createSocket(self.hostTtydSocket)

    # open docker container for ain worker server
    Docker.createContainer(constants.IMAGE, optionRun["GPU"])


  def status(self):
    for key in self.ENVS:
      print(key + ": " + self.ENVS[key])
    
    try:
      response = self.session.get(self.workerAddress + "/info")
      ids = response.json()['id']
      if(len(ids) == 0):
        print("[+] does not exist")
        return
    except Exception as e:
      print("[-] worker server error")
      print(e)
      exit(1)

    print("[+] Status: Running")
    try:
      option = " ".join(ids)
      subprocess.run(["docker", "stats" , option])

    except Exception as e:
      print("[-] subprocess(docker) error")
      print(e)

  def stop(self):
    try:      
      response = self.session.get(self.workerAddress + "/info")
      cnt = response.json()['cnt']
      if (cnt != 0):
        print("[+] Instance count:" +str(cnt))
        
      print("[?] Do you want to stop? (y/n)")
      answer = input()
      if (answer.lower() != 'y'):
        return
    except Exception as e:
      print("[-] worker server error - info")

    try:
      response = self.session.get(self.workerAddress + "/terminate")
    except Exception as e:
      print("[-] worker server error - terminate")

    try:
      Docker.removeContainer("ain_worker")
      print('[+] succeded to remove container!')

    except Exception as e:
      print("[-] subprocess(docker) error")
      print(e)

    try:
      Ttyd.removeSocket(self.hostTtydSocket)
      Ttyd.removeSocket(constants.SHARED_PATH + "/ain_worker.sock")
      print('[+] succeded to remove ttyd socket')
    except Exception as e:
      print("[-] subprocess error(ttyd socker remove)")
      print(e)

  def log(self):
    basePath = constants.SHARED_PATH + "/log/" 
    if (os.path.exists(basePath + "log.env")):
      os.remove(basePath + "log.env")
      
    logFileName = sorted(os.listdir(basePath))
    if (len(logFileName) == 0):
      print("[+] does not exist")
      return
    
    targetFile = logFileName[-1]
    
    print("[?] do you want to see recent log?(y/n)")
    answer = input()
    if (answer == "n"):
      for i in range(len(logFileName)):
        print(str(i) + " - " + logFileName[i])
      print("[?] input number")
      number = int(input())
      targetFile = logFileName[number]
    
    try:
      path = os.path.join(basePath, targetFile)
      if (answer):
        subprocess.run(["tail", "-f" , path])
      else:
        subprocess.run(["cat", path])
    except Exception as e:
      print("[-] subprocess(log) error")
      print(e)
      
    return

  def init(self):
    for key in ["NAME", "LIMIT_COUNT", "PRICE", "MNEMONIC", "SERVER_IP", "GPU"]:
      dotenv.set_key(constants.ENV_FILE_PATH, key, "")
    dotenv.set_key(constants.ENV_FILE_PATH, "DESCRIPTION", "empty")