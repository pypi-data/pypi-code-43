#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Reflection / Debugging
import inspect

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def __subProcInfo( self, message ):
		'''
		Queries methods in the application's side and returns them back across the wire to a process that's asking for the information.
		'''

		self.reply(
			message,
			body	=	getattr( self.getApp(), message[ 'body' ] )(),
		)

		pass # END MESSAGE CALLBACK : Sub-Process Information

	pass # END CLASS : EXTEND
