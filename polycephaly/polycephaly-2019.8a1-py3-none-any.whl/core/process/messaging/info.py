#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def getQueue( self, *args, **kwargs ):
		'''
		'''

		name		=	args[ 0 ]
		ignoreLock	=	True if kwargs.get( 'ignoreLock' ) else False

		# With lock
		if name == self.name and not ignoreLock:

			with self.getLocks( 'queue' ):
				return self.messenger.getQueue( *args )
				pass # END LOCK

			pass # END IF : WITH LOCK

		# Without lock
		else:
			return self.messenger.getQueue( *args )
			pass # END ELSE

		pass # END METHOD : Get queue

	pass # END CLASS : Extend
