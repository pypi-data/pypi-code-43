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

	def callbackEvent( self, event, *args, **kwargs ):
		'''
		Attempts to run callback at a specific event.

		Event			:	usually called by thread at a specific event such as (dis)connect or communication/device failure.
		Args & Kwargs	:	Passed through to callback.
		'''

		currCB	=	self._callbacks.get( event )

		try:

			if not currCB:
				logger.warning( f"A callback has not been registered for '{ event }' event." )
				pass # END IF

			elif callable( currCB ):
				logger.debug( f"Callback event { event }( args={ args }, kwargs={ kwargs } ) called." )
				return currCB( *args, **kwargs )
				pass # END ELIF

			else:
				logger.warning( f"Callback event { event }( args={ args }, kwargs={ kwargs } ) couldn't be called." )
				pass # END ELSE

			pass # END TRY

		except Exception as e:
			logger.critical( f"Callback event { event }( args={ args }, kwargs={ kwargs } ) experienced a critical error: '{ e }'" )
			pass # END EXCEPTION

		pass # END METHOD : callbackEvent

	def birth( self ):

		logger.debug( f'{ self.name }.{ inspect.stack()[ 0 ][ 3 ] }() - called by { inspect.stack()[ 1 ][ 3 ] }() : started.' )
		logger.debug( f'{ self.name }.{ inspect.stack()[ 0 ][ 3 ] }() : finished.' )

		pass # END METHOD : Birth

	def life( self ):

		logger.debug( f'{ self.name }.{ inspect.stack()[ 0 ][ 3 ] }() - called by { inspect.stack()[ 1 ][ 3 ] }() : started.' )

		# Check for new messages, and run appropriate callbacks.
		self.mailman()

		logger.debug( f'{ self.name }.{ inspect.stack()[ 0 ][ 3 ] }() : finished.' )

		pass # END METHOD : Life

	def death( self ):

		logger.debug( f'{ self.name }.{ inspect.stack()[ 0 ][ 3 ] }() - called by { inspect.stack()[ 1 ][ 3 ] }() : started.' )
		logger.debug( f'{ self.name }.{ inspect.stack()[ 0 ][ 3 ] }() : finished.' )

		pass # END METHOD : Death

	pass # END CLASS : EXTEND
