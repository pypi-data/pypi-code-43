def print_qtlist(x):
	if type(x)!=list:
		print(x)	
	else:
		for y in x:
			print_qtlist(y)