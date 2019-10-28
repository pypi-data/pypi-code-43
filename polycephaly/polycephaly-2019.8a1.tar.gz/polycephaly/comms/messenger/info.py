#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def getQueues( self, *args ):

		# All
		if not len( args ):
			return self._queues
			pass # END IF

		# Select
		r	=	{}
		for qk, qv in self._queues.items():

			for a in args:

				if qk.upper() == a.upper():

					r.update({ qk : qv })

					pass # END IF

				pass # END FOR : Arguments

			pass # END FOR : Queues

		return r

		pass # END METHOD : Get queues

	def getQueue( self, name, retType='V' ):
		'''
		Name of queue.
		retType is Key or Value.  If key, will be exact match.  If value, will be actual queue.

		Singular tense of getQueues()
		'''

		currD	=	self.getQueues( name )

		return next( iter( ( currD.keys() if ( retType[ 0 ].upper() == 'K' ) else currD.values() ) ) ) if currD else None

		pass # END METHOD : Get queue

	def listQueues( self ):
		'''
		Returns name of queues.
		'''

		return list( self._queues.keys() )

		pass # END METHOD : List queues

	pass # END CLASS : Polycephaly Messenger
