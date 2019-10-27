# -*- coding: utf-8 -*-
"""
.. module:: custom_logger
    :synopsis: Minimalistic Custom Logger

.. moduleauthor:: DivyenduDutta

.. note::
	Tested to work only with python 2.7, not sure about python 3+

"""
import os
from os import path
import ConfigParser
from datetime import datetime
from ConfigParser import NoSectionError
from Constants import LOG_TEXT_START_END

class Logger(object):
	"""
	Custom Logger class. Dont actually need to get an instance of this class, but 
	do internally create an instance to call the :func:`__init__()` which initializes a lot of the logger variables.
	
	Currently only provides three functions for logging \n 
	1. **Method entry logging** \n
	2. **Method exit logging** \n
	3. **Normal logging** \n
	
	Both Method entry logging and Method exit logging are only *INFO* level logging by default
	
	Supports *3 levels of logging* - *INFO, ERROR, DEBUG*. These are mutually exclusive (ie not hierarchial)
	
	Supports *2 modes of logging*: \n
	1. **FILE** - Writes logs to a file in the logs folder \n
	2. **CONSOLE** - Logs to the standard output console \n
	
	**Log format - [<log level> <timestamp>] [Module name]-[Method name] <log text>**
	
	**REQUIREMENTS** \n
	1. logger.properties file  \n
	2. logs folder \n
	
	.. warning::
		logger.properties file needs to have [logger properties] at the root
	
	**SAMPLE USAGE**\n
	``from YALogger.custom_logger import Logger`` \n
	``Logger.initialize_logger(logger_prop_file_path = '.\logger.properties',log_file_path = './logs')`` \n
	``Logger.perform_method_entry_logging('foo','bar')`` \n
	``Logger.perform_method_exit_logging('foo','bar')`` \n
	``Logger.log('info', 'foo','bar','this is the log text')`` \n
	
	"""
	__instance = None
	__level = None
	__mode = None
	__current_timestamp = None
	__log_file_path = None
            
	def __new__(cls, logger_prop_file_path, log_file_path):
		"""
		Defining code in `__new__()` to make `Logger` a singleton class
		`Logger.__instance` keeps tracj of whether an instance of `Logger` exists or not. If it doesnt 
		exist then creates it otherwise returns the existing instance of `Logger`
		
		Args:
			logger_prop_file_path(str) : the path of logger.properties
			log_file_path(str) : the path of the log file
			
		Returns:
			instance of `Logger` : singleton instance of `Logger`
		"""
		if Logger.__instance is None:
			Logger.__instance = object.__new__(cls)
		return Logger.__instance
    
	def __init__(self, logger_prop_file_path, log_file_path):
		"""
		Initilaizing various `Logger` class properties: \n
		1. `Logger.__level` : the logging.level \n
		2. `Logger.__mode` : the logging mode \n 
		3. `Logger.__current_timestamp` : the current timestamp \n 
		4. `Logger.__log_file_path` : the log file path and name
		
		Args:
			logger_prop_file_path(str) : the path of logger.properties
			log_file_path(str) : the path of the log file
			
		Raises
			NoSectionError
			IOError
		"""
		if path.exists(logger_prop_file_path) == True:
			config = ConfigParser.ConfigParser()
			config.readfp(open(logger_prop_file_path))
			try:
				Logger.__level = Logger._validate_logging_level(config.get('logger properties', 'logging.level').strip())
				Logger.__mode = Logger._validate_logging_mode(config.get('logger properties', 'logging.mode').strip())
				Logger.__current_timestamp = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
				Logger.__log_file_path = log_file_path +'/log'+'_'+datetime.now().strftime("%m_%d_%Y")+'.log'
			except NoSectionError:
				raise NoSectionError('Ensure [logger properties] is present in logger.properties file')
				
		else:
			raise IOError('Not able to find/open logger.properties file in the project root')

	@staticmethod
	def _open_log_file(log_file_path):
		"""
		Opens the log file when logging.mode = FILE
		Opens in append mode
		
		Args:
			log_file_path(str) : the path of the log file
			
		Returns:
			file instance : reference to opened file
		"""
		return open(log_file_path, "a+")

	@staticmethod
	def _validate_logging_level(logging_level):
		"""
		Checks of the logging.level specified in logger.properties and validates whether it falls under the valid values
		Valid values are - 'INFO', 'ERROR' , 'DEBUG'
		
		Args:
			logging_level(str) : logging level in logger.properties
			
		Returns:
			list : logging levels from logger.properties
			
		Raises:
			ValueError
		"""
		if logging_level[-1] == ',':
			logging_level = logging_level[-1]
		logging_level_list = logging_level.split(',')
		logging_level_list = [log_level.lstrip().rstrip().upper() for log_level in logging_level_list]
		if len(logging_level_list) == 0:
			raise ValueError('Issue in logging.level. Check logging.properties file')
		
		valid_logging_levels = ['INFO', 'ERROR' , 'DEBUG']
		
		are_log_levels_valid = [log_level in valid_logging_levels for log_level in logging_level_list]
		
		if any(are_log_levels_valid):
			return logging_level_list
		else:
			raise ValueError('Not supported in logging properties. Check properties file')
			
	@staticmethod
	def _validate_logging_mode(logging_mode):
		"""
		Checks of the logging.mode specified in logger.properties and validates whether it falls under the valid values
		Valid values are - 'FILE', 'CONSOLE'
		
		Args:
			logging_mode(str) : logging mode in logger.properties
			
		Returns:
			list : logging modes from logger.properties
			
		Raises:
			ValueError
		"""
		if logging_mode[-1] == ',':
			logging_mode = logging_mode[-1]
		logging_mode_list = logging_mode.split(',')
		logging_mode_list = [log_mode.lstrip().rstrip().upper() for log_mode in logging_mode_list]
		if len(logging_mode_list) == 0:
			raise ValueError('Issue in logging.level. Check logging.properties file')
		
		valid_logging_modes = ['FILE', 'CONSOLE']
		
		are_log_modes_valid = [log_mode in valid_logging_modes for log_mode in logging_mode_list]
		
		if any(are_log_modes_valid):
			return logging_mode_list
		else:
			raise ValueError('Not supported in logging properties. Check properties file')

	@staticmethod
	def initialize_logger(logger_prop_file_path, log_file_path):
		"""
		Initializes the logger. Creates a new instance of `Logger` to call :func:`__init__()`
		
		Args:
			logger_prop_file_path(str) : the path of logger.properties
			log_file_path(str) : the path of the log file
		"""
		Logger(logger_prop_file_path, log_file_path)

	@staticmethod
	def perform_method_entry_logging(module_name, method_name):
		"""
		Call this method before entering a method
		
		Args:
			module_name(str) : module name
			method_name(str) : name of method being entered
		"""
		if 'INFO' in Logger.__level :
			log_text = (LOG_TEXT_START_END + '[ INFO \t'
				'' + Logger.__current_timestamp+ '][' + module_name + ']'
				'-[' + method_name + '] ' + 'entering...\n' + LOG_TEXT_START_END)
			if 'FILE' in Logger.__mode:
				log_file = Logger._open_log_file(Logger.__log_file_path)
				log_file.write(log_text)
				log_file.close()
			elif 'CONSOLE' in Logger.__mode:
				print(log_text)
		else:
			pass
		
	@staticmethod
	def perform_method_exit_logging(module_name, method_name):
		"""
		Call this method after exiting a method
		
		Args:
			module_name(str) : module name
			method_name(str) : name of method being entered
		"""
		if 'INFO' in Logger.__level :
			log_text = (LOG_TEXT_START_END + '[ INFO \t'
				'' + Logger.__current_timestamp+ '][' + module_name + ']'
				'-[' + method_name + '] ' + 'exiting...\n' + LOG_TEXT_START_END)
			if 'FILE' in Logger.__mode:
				log_file = Logger._open_log_file(Logger.__log_file_path)
				log_file.write(log_text)
				log_file.close()
			elif 'CONSOLE' in Logger.__mode:
				print(log_text)
		else:
			pass

	@staticmethod
	def log(log_level, module_name, method_name, log_text):
		"""
		Call this method to log text
		
		Args:
			log_level(str) : level of logging
			module_name(str) : module name
			method_name(str) : name of method being entered
			log_text(str) : text to be logged
		"""
		if log_level.upper() in Logger.__level:
			log_text = (LOG_TEXT_START_END + '[ ' + log_level +'\t'
				'' + Logger.__current_timestamp+ '][' + module_name + ']'
				'-[' + method_name + '] ' + log_text +'\n' + LOG_TEXT_START_END)
			if 'FILE' in Logger.__mode:
				log_file = Logger._open_log_file(Logger.__log_file_path)
				log_file.write(log_text)
				log_file.close()
			elif 'CONSOLE' in Logger.__mode:
				print(log_text)
		else:
			pass
