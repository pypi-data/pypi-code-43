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

	def build( self ):

		logger.debug( f'{ self.name }.{ inspect.stack()[ 0 ][ 3 ] }() - called by { inspect.stack()[ 1 ][ 3 ] }() : started.' )
		logger.debug( f'{ self.name }.{ inspect.stack()[ 0 ][ 3 ] }() : finished.' )

		pass # END METHOD : Build

	pass # END CLASS : EXTEND
