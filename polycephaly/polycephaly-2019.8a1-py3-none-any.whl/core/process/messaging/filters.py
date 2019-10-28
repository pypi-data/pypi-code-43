#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def addFilter( self, route=None, **kwargs ):
		'''
		'''

		return self.messenger.addFilter(
			caller=self.name,
			route=( route if route else self.name ),
			**kwargs
		)

		pass # END METHOD : Add Filter

	def listFilters( self, name=None, topic=None ):
		'''
		'''

		return self.messenger.listFilters(
			caller	=	name if name else self.name,
			topic	=	topic,
		)

		pass # END METHOD

	pass # END CLASS : Extend
