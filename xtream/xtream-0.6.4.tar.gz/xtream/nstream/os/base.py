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
        

    def initialize(self):
        self.runCommand(self.initcommand)

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
