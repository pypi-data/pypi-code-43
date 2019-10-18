from ..base import *
import platform
import sys

class WindowsDeployer(OSBase):
    def __init__(self,osversion):
      self.osversion= osversion
      self.version=sys.version_info.major
      self.platform=platform.system()
      self.initcommand="package install"
      self.install_prereqcommand="yum install -y wget automake gcc gcc-c++ kernel-devel make git "
      self.install_dbcommand="yum install -y postgresql"
      self.install_nonessentialcommand="yum install -y docker python3-pip"


    