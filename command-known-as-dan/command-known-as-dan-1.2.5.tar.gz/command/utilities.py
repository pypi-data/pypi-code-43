def isArg(args, index, default=False):
	try:
		arg = args[index]
		if type(arg) == str:
			return arg
	except:
		return default