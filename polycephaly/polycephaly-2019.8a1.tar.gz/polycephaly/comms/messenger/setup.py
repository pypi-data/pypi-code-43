#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Message Queues
from queue import Queue as queueThread
from multiprocessing import Queue as queueProcess

# Polycephaly
import polycephaly.functions.utilities

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def addQueue( self, name, queueType, **kwargs ):
		'''
		queueType is [M]ultiprocessing or [T]hreading.
		'''

		logger.debug( f"Adding message queue (type: '{ queueType }') for '{ name }'." )

		if name in self._queues:
			raise KeyError( 'Message queue already exists.' )
			pass # END IF

		queueSize	=	kwargs.get( 'size', self._defSize )

		self._queues[ name ]			=	polycephaly.functions.utilities.easySwitch(
												queueType[ 0 ].upper(),
												A=queueProcess( queueSize ),	# AsyncIO
												T=queueThread( queueSize ),		# Thread
												M=queueProcess( queueSize ),	# Multiprocessing
												P=queueProcess( queueSize ),	# Popen
											)

		return self._queues[ name ]

		pass # END METHOD : Add queue

	pass # END CLASS : Polycephaly Messenger
