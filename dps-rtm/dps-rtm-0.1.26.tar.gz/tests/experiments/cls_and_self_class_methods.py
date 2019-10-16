

class MyClass:

    class_var = 10

    def __init__(self, value):
        self.var = value

    def multiply(self):
        print(self.class_var * self.var)

myclass = MyClass(3)
myclass.multiply()
myclass.class_var = 5
myclass.multiply()

glass = MyClass(3)
glass.multiply()
