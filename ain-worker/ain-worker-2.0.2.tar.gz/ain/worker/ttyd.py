import subprocess
from subprocess import Popen
import os
from time import sleep

class Ttyd():

  @staticmethod
  def createSocket(socketName):
    try:
      Popen(["ttyd" ,"-i" ,socketName ,"/bin/bash"],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      sleep(1)
      if (os.path.exists(socketName) == False):
        print("[-] failed to create ttyd socket.")
        exit(1)
      
    except Exception as e:
      print("[-] failed to create ttyd socket.")
      print(e)
      exit(1)
      
    print("[+] succeded to create ttyd socket.")

  @staticmethod
  def removeSocket(socketName):
    try:
      if (os.path.exists(socketName)):
        os.remove(socketName)
    except Exception as e:
      print("[-] failed to remove ttyd socket.")
      print(e)
      exit(1)