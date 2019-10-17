from nstream.os.base import *

class CentOSDeployer(OSBase):
    def __init__(self,osversion):
      self.osversion=osversion
      self.version=sys.version_info.major
      self.platform=platform.system()
      self.initcommand="yum update -y"


def updateCentOS():
  command="yum update -y"
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)

def centOSInstallPostgres():
  command="yum install -y postgres"
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)

def centOSInstallPythonPIP():
  command="yum install -y python3-pip"
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)

def centOSInstallGit():
  command="yum install -y git"
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)

def centOSInstallBuildPackages():
  command="yum install -y sudo pcre pcre-devel openssl-devel wget make automake gcc gcc-c++ kernel-devel"
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)

 
def centOSDownloadNginx():
  command="wget "+NGINX_SRC
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)


def centOSDownloadNginxRTMP():
  command="wget "+NGNIX_RTMP
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)

def centOSDownloadPCRE():
  command="wget "+PCRE
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)


def centOSDownloadOpenSSL():
  command="wget "+OPENSSL
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)

def centOSDownloadZLib():
  command="wget "+ZLIB
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)


def centOSCopyPython():
  command="cp /usr/bin/python3 /usr/bin/python"
  try:
    status=subprocess.call(command)
    return status
  except Exception as ex:
    print(ex)