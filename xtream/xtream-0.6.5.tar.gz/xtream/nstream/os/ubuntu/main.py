from ..base import *

class UbuntuDeployer(OSBase):
    def __init__(self,osversion):
      self.osversion=osversion
      self.version=sys.version_info.major
      self.platform=platform.system()
      self.initcommand="apt-get update -y"
      self.install_prereqcommand="apt-get install build-essential wget git -y"
      self.install_dbcommand="apt-get install postgresql -y"
      self.install_nonessentialcommand="apt-get install -y docker python3-pip"