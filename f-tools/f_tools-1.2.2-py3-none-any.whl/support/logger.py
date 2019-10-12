"""Logger object and functions"""

import coloredlogs
import logging
import sys


class Logger:
	""" Logger class
	Contains a basic logger
	"""
	def __init__(self, name='f_tools', level=logging.DEBUG):

		logging.addLevelName(25, 'NOTICE')
		logging.addLevelName(35, 'SUCCESS')

		ch = logging.StreamHandler()
		ch.setLevel(level)

		self.logger = logging.getLogger(name)
		coloredlogs.DEFAULT_LEVEL_STYLES = {
			'debug': {'color': 'white', 'faint': True},
			'info': {},
			'notice': {'color': 'magenta'},
			'success': {'color': 'green'},
			'warning': {'color': 'orange'},
			'error': {'color': 'red'},
			'critical': {'background': 'red', 'bold': True},
		}
		coloredlogs.install(level=level, logger=self.logger)

	@staticmethod
	def __format_message(msg, caller: any):
		if caller is None:
			return msg
		if hasattr(caller, 'acc_id') and hasattr(caller, 'id'):
			return f"{msg} - id: {caller.id} - acc: {caller.acc_id}"
		if hasattr(caller, 'id'):
			return f"{msg} - id: {caller.id}"
		return msg

	def debug(self, msg: str, caller: any = None, mark="*"):
		self.logger.debug(f'[{mark}] {self.__format_message(msg, caller)}')

	def info(self, msg: str, caller: any = None, mark="*"):
		self.logger.info(f'[{mark}] {self.__format_message(msg, caller)}')

	def notice(self, msg: str, caller: any = None, mark="*"):
		self.logger.log(25,f'[{mark}] {self.__format_message(msg, caller)}')

	def success(self, msg: str, caller: any = None, mark="✓"):
		self.logger.log(35, f'[{mark}] {self.__format_message(msg, caller)}')

	def warn(self, msg: str, caller: any = None, mark="!"):
		self.logger.warning(f'[{mark}] {self.__format_message(msg, caller)}')

	def error(self, msg: str, caller: any = None, mark="!"):
		self.logger.error(f'[{mark}] {self.__format_message(msg, caller)}')

	def fatal(self, msg: str, caller: any = None, mark="*"):
		self.logger.fatal(f'[{mark}] {self.__format_message(msg, caller)}')
		sys.exit(1)
