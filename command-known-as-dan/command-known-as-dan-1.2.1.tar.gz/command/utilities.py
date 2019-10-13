def isArg(args, index):
	try:
		arg = args[index]
		if type(arg) == "string":
			return arg
	except:
		return False