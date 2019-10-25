class _Null():
    def __repr__(self):
        return("null")

class _Undefined():
    def __repr__(self):
        return("undefined")

class Symbol():
    def __init__(self,name):
        self.__setattr__('name',name)
    def __repr__(self):
        return(self.name)


null = _Null()
undefined = _Undefined()
true = True
false = False



