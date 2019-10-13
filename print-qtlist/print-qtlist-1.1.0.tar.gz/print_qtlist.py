def print_qtlist(x,kongge):
	for i in x:
		if type(i)==list:
			print_qtlist(i,kongge+1)
		else:
			for j in range(kongge):
				print('\t',end="")
			print(i)
