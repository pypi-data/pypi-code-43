

def new_method(some_class):

    def double_trouble(self):
        print(self.value * 2)

    setattr(some_class, double_trouble.__name__, double_trouble)

    return some_class


@new_method
class MyClass:
    def __init__(self, value):
        self.value = value


obj = MyClass(2)
obj.double()
