# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from configparser import ConfigParser, ExtendedInterpolation
from configparser import Error as ParserError

from _sadm import log
from _sadm.errors import ServiceError

class Service(ConfigParser):

	def __init__(self, cfgfn):
		super().__init__(defaults = {},
			allow_no_value = False,
			delimiters = ('=',),
			comment_prefixes = ('#',),
			strict = True,
			interpolation = ExtendedInterpolation(),
			default_section = 'default')
		self.__read(cfgfn)

	def __read(self, fn):
		log.debug("read file %s" % fn)
		try:
			super().read(fn)
		except ParserError as err:
			raise ServiceError(str(err))
