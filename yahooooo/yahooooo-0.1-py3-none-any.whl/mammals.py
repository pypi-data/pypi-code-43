class mammals:
	def __init__(self):
		self.members = ['Tiger', 'Elephant', 'Wild Cat']
	
	def printMembers(self):
		print('printing members of the mammal clasas')
		for member in self.members:
			print('\t%s' %member)