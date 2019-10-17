class A:
	def __init__(self,a=None,b=None):
		self.a=a
		self.b=b
	def update(self,**kwargs):
		for key in kwargs.keys():
			if key in self.__dict__:
				setattr(self,key,kwargs[key])
a=A(1,2)
print(a.a,a.b)
a.update(a=3,b=4)
print(a.a,a.b)
