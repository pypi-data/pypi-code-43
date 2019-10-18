import os
import ain.common.constants as constants
import docker

class Docker():

  @staticmethod
  def createContainer(image, gpu):
    try:
      print("[+] pull image.")
      client = docker.from_env()
      client.images.pull(image)
      
      print("[+] create container.")
      if gpu=="true":    
        client.containers.run(image=image,
                              command="yarn start",
                              detach=True,
                              runtime="nvidia",
                              name="ain_worker",
                              volumes={
                                  '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'ro'},
                                  constants.SHARED_PATH:{'bind': "/share", 'mode': "rw"}
                                }
                              )
      else:
        client.containers.run(image=image, command="yarn start",
                              detach=True,
                              name="ain_worker",
                              volumes={
                                  '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'ro'},
                                  constants.SHARED_PATH:{'bind': "/share", 'mode': "rw"}
                                }
                              )
        
      print("[+] started ain worker server!")
    except Exception as e:
      print("[-] failed to create container.")
      print(e)
      exit(1)

  @staticmethod
  def removeContainer(name):
    try:
      client = docker.from_env()
      constainer = client.containers.get(name)
      constainer.remove(force=True)
      
    except Exception as e:
      print("failed to remove container.")
      print(e)