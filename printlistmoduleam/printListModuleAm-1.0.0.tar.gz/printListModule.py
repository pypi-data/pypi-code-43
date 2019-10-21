#from setuptools import setup

# function to print the list. prints sublist too using recursion.
def printList(lst):
	for itm in lst:
		if (isinstance(itm, list)):
			printList(itm)
		else:
			print(itm)

# dummy code to test the printList() function
#my_list = [1, "ameer"]
#printList(my_list)
