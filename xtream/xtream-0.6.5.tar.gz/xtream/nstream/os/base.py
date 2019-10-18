import os
import sys
import platform
import sys
import os
import subprocess


class OSBase():
    def __init__(self,osversion):
        self.osversion=osversion
        self.version=sys.version_info.major
        self.platform=self.getPlatform()
        self.initcommand=None
        self.install_prereqcommand=None
        self.install_dbcommand=None
        self.install_nonessentialcommand=None

        

    def initialize(self):
        self.runCommand(self.initcommand)
        self.runCommand(self.install_prereqcommand)
        self.runCommand(self.install_dbcommand)
        self.runCommand(self.install_nonessentialcommand)

    def linux_distribution():
        try:
            return platform.linux_distribution()
        except:
            return "N/A"
            
    def getPlatform(self):
        return platform.system()

    def verbose(self,arg):
        if self.version=="3":
            print(arg)
        else:
            print(arg)

    def runCommand(self,command):
        status=os.system(command)
        return status

    def buildPackage(self):
        pass

    def dowloadPackages(self):
        downloadNginx()
        downloadNginxRTMP()
        downloadOpenSSL()
        downloadPCRE()
