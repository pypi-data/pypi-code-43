from nstream.os.base import *
import platform
import sys

class WindowsDeployer(OSBase):
    def __init__(self,osversion):
      self.osversion= osversion
      self.version=sys.version_info.major
      self.platform=platform.system()
      self.initcommand="package install"


    