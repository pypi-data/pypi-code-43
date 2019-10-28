"""
Copyright (c) 2017, 2018, 2019 Irstea
Copyright (c) 2017, 2018, 2019 François Kneib
Copyright (c) 2017, 2018, 2019 Franck Bourrier
Copyright (c) 2017, 2018, 2019 David Toe
Copyright (c) 2017, 2018, 2019 Frédéric Berger
Copyright (c) 2017, 2018, 2019 Stéphane Lambert

This file is part of PlatRock.

PlatRock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

PlatRock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar. If not, see <http://www.gnu.org/licenses/>.
"""


#TODO :
# -globally remove all Debug.Print in PlatRock, repace by one of the three log levels.

import multiprocessing,logging,sys,os,subprocess

#Message importance levels :
INFO=logging.INFO #20
WARNING=logging.WARNING #30
ERROR=logging.ERROR #40

#Actual log level : (log messages whose importance > current_level)
current_level=0


# Get the logger corresponding to the current process PID,
# Or create one if it doesn't exist (this is the behavior of "logging.getLogger")
def get_logger():
	return logging.getLogger(str(multiprocessing.current_process().pid))	#create a logger for this thread
	
# Get or create a logger based on the process PID
# Clear its handlers
# Add a new handler
def add_logger(filename=None):
	logger = get_logger()	# get or create the logger
	logger.handlers=[]		# remove all the handlers
	if(filename==None or multiprocessing.current_process().name=='MainProcess'): handler = logging.StreamHandler()	#if the process is main (no multithreading, so no WebUI), log to console
	else: 
		if(os.path.exists(filename)): subprocess.call(["rm",filename])
		handler = logging.FileHandler(filename)									#if the process is a child, log to file
	logger.addHandler(handler)	#add the handler to the logger
	logger.propagate = False #avoid duplicate logging to the console
	logger.setLevel(current_level)
	logger.name="PlatRock-WebUI PID="+multiprocessing.current_process().name

def args_to_str(*args):
	S=""
	for arg in args:
		S+=str(arg)+" "
	return S

# Concatenate the input args, get the logger then log:
def info(*args):
	get_logger().info(args_to_str(*args))

Print=info #for retro-compatibility of the old Debug version.
	
def warning(*args):
	get_logger().warning(args_to_str(*args))

def error(*args):
	get_logger().error(args_to_str(*args))

def do_nothing(*args):
	pass

# Override the previous functions with "do_nothing" depending on the log level :
def init(level):
	global current_level
	current_level=level
	if(level>INFO):
		global info,Print
		info=do_nothing
		Print=do_nothing
	if(level>WARNING):
		global warning
		warning=do_nothing
	if(level>ERROR):
		global error
		error=do_nothing
