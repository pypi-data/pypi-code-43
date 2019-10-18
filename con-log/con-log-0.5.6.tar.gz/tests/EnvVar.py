

class EnvVar:
    def __init__(self, xdict):
        copy = xdict if xdict else {}
        self.envcopy = copy
        

    def getVar(self, name):
        console = self._conlog_.get_console()
        console.debug("{name=} ")
        return name
    
    def setVar(self, name, val ) :
        console = self._conlog_.get_console()
        _envcopy = self.envcopy
        
        console.debug("{self.envcopy=}")
        self.envcopy["name"] = val
        console.debug("{self.envcopy=}{name=} ")
