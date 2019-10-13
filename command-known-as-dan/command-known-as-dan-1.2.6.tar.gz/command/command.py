from sys import argv

commands = {}
class Command:
	def __init__(self, identifier, usage, description, commandFunction):
		self.identifier = identifier
		self.usage = usage
		self.description = description
		self.commandFunction = commandFunction

		commands[self.identifier] = self
	
	def getIdentifier(self):
		return self.identifier
	
	def getUsage(self):
		return self.usage
	
	def getDescription(self):
		return self.description

	def getFunction(self):
		return self.commandFunction
	
	def execute(self, args=[]):
		args = list(args)
		func = self.getFunction()
		func(args)

def getAllCommands():
	return commands

def getCommand(identifier):
	command_list = getAllCommands()
	try:
		return command_list[identifier]
	except:
		return None

def init(print_help=True, args=None):
	args_empty = True
	if (isinstance(args, list)):
		args = list(args)
		if (len(args) > 0):
			args_empty = False
			called_command = args[0]
			del args[0]
			fire(called_command, args)
	else:
		args = list(argv)
		if (len(args) > 1):
			args_empty = False
			called_command = args[1]
			del args[0:2]
			fire(called_command, args)
	
	if (print_help and args_empty):
		help()


def help():
	print("\nCommand List:")
	command_list = getAllCommands()
	if len(command_list) > 0:
		for identifier in command_list:
			command = command_list[identifier]
			info = "{0} {1} {2}".format(command.getIdentifier(), command.getUsage(), command.getDescription())
			print(info)
	else:
		print(" - There are no commands to display!")
	
	print() # spacing


def fire(identifier, args=[]):
	command = getCommand(identifier)
	if command != None:
		args = list(args)
		command.execute(args)
	else:
		message = "Could not find a command named '{0}'".format(identifier)
		print(message)