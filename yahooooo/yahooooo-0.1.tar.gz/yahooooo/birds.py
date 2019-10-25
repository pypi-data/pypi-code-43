class birds:
	def __init__(self):
		self.members = ['Cuckoo', 'Sparrow', 'Eagle']
	
	def printMembers(self):
		print('printing members of the birds clasas')
		for member in self.members:
			print('\t%s' %member)