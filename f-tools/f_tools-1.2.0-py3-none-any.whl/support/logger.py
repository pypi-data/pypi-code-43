"""Logger object and functions"""

import coloredlogs
import logging
import sys


class Logger:
	""" Logger class
	Contains a basic logger
	"""
	def __init__(self, name='f_tools', level=logging.DEBUG):

		ch = logging.StreamHandler()
		ch.setLevel(level)

		self.logger = logging.getLogger(name)
		coloredlogs.install(level=level, logger=self.logger)

	def debug(self, msg: str):
		self.logger.debug(f'[*] {msg}')

	def info(self, msg: str):
		self.logger.info(f'[*] {msg}')

	def success(self, msg: str):
		self.logger.info(f'[✓] {msg}')

	def warn(self, msg: str):
		self.logger.warning(f'[!] {msg}')

	def error(self, msg: str):
		self.logger.error(f'[!] {msg}')

	def fatal(self, msg: str):
		self.logger.fatal(f'[!] {msg}')
		sys.exit(1)
