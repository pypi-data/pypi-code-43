import inspect


class Bar:

    def worker(self, a:int, b:float, x:str='blah'):
        pass


print(inspect.getfullargspec(Bar.worker))
