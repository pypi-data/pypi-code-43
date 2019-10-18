
class FailException(Exception):

    def __init__(self,code=None,desc=None):
        super(FailException, self).__init__() 
        self.code = code
        self.desc = desc