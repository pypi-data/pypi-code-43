def print_qtlist(x,suojin=True,kongge=0):
	for i in x:
		if type(i)==list:
			if suojin==False:
				print_qtlist(i,suojin,kongge,)
			elif suojin==True:
				print_qtlist(i,suojin,kongge+1)
		else:
			print('\t'*kongge,end="")
			print(i)
