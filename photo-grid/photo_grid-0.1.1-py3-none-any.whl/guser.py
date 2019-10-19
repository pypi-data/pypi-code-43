import platform

class GUser():
    """
    """
    def __init__(self):
        """
        """
        self.platform = platform.system()
        self.architecture = platform.architecture()[0]
        self.release = platform.release()
        self.machine = platform.machine()
    
    def printInfo(self):
        print("GRID User's Info")
        print("----------------")
        print("Platform:      ",  self.platform)
        print("Architecture:  ",  self.architecture)
        print("Release:       ",  self.release)
        print("Machine:       ",  self.machine)
