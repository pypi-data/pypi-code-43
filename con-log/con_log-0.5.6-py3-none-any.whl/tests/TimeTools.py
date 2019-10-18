from conlog import Conlog 

class Timetools:
     
    def wait(self,  s):
        console = self._conlog_.get_console()
        console.debug(r'{s=}')
        print("waiting")

    
    def retry(self,  n):
        console = self._conlog_.get_console()
        console.debug(r'{n=}')
        print("rettrun")

     
    def sleep(self, secs, minutes):
        console = self._conlog_.get_console()
        print("I am Sleeping")
        return secs+minutes
