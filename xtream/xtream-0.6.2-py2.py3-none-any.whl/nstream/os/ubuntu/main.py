from ..base import *

class UbuntuDeployer(OSBase):
    def __init__(self,osversion):
      self.osversion=osversion
      self.version=sys.version_info.major
      self.platform=platform.system()
      self.initcommand="apt-get update -y"