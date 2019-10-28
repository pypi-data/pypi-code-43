#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Reflection / Debugging
import inspect

# Processes
import threading

# Formatting
from pprint import pformat as pf

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def addLocks( self, *args ):

		for a in args:

			self._locks[ a ]	=	threading.Lock()	# Locking queue for getQueue() and waitForReply()

			pass # END FOR

		pass # END METHOD : Add locks

	def getLocks( self, *args ):

		curframe = inspect.currentframe()
		calframe = inspect.getouterframes( curframe, 2 )

		logger.debug( f"{ self.name }.{ calframe[ 0 ][ 3 ] }( { pf( args ) } ) called by { self.name }.{ calframe[ 1 ][ 3 ] }() in { calframe[ 1 ][ 1 ] }" )

		if not args:
			return self._locks
			pass # END IF

		r	=	{ a : self._locks[ a ] for a in args }

		return next( iter( r.values() ) ) if ( len( args ) == 1 ) else r

		pass # END METHOD : Get locks

	pass # END CLASS : EXTEND
