"""
tl/dr
You can modify a class's class variables before instantiating it.
"""

class MyClass:
    classvar = []

    @classmethod
    def get_vars(cls):
        return cls.classvar

    @classmethod
    def append_var(cls, value):
        cls.classvar.append(value)

    def __init__(self, value=1):
        self.vars = [var*value for var in self.get_vars()]

    def __getitem__(self, item):
        return self.vars[item]

    def __len__(self):
        return len(self.vars)

    def __repr__(self):
        return str(self.vars)


for i in range(5):
    MyClass.append_var(i)
my_object = MyClass()
print(my_object)
my_object = MyClass(2)
print(my_object)
