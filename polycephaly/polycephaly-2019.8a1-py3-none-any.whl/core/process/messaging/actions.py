#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# System
import time

# Reflection / Debugging
import inspect

# Message Queues
from queue import Empty as queueEmpty

# Polycephaly
import polycephaly.functions.threading

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def getQueueMessage( self, mailboxQueue=None, **kwargs ):
		'''
		'''

		return self.messenger.getQueueMessage( caller=self.name, mailboxQueue=mailboxQueue, **kwargs )

		pass # END METHOD : Get Queue Message

	def mailman( self, route=None, message=None ):
		'''
		'''

		self._ranMailman	=	True

		# Default use, when not being used to process messages from ROS, UDS, MQTT, et al.
		if route is None:
			route		=	self.name
			message		=	self.getQueueMessage( mailboxQueue=self.getQueue( self.name ) ) if ( message is None ) else message
			pass # END IF

		return self.messenger.mailman(
			caller=self.name,
			route=route,
			message=message,
		)

		pass # END METHOD : Mailman

	def send( self, **kwargs ):
		'''
		'''

		curframe = inspect.currentframe()
		calframe = inspect.getouterframes( curframe, 2 )

		logger.debug( f"{ self.name }.{ calframe[ 0 ][ 3 ] }() called by { self.name }.{ calframe[ 1 ][ 3 ] }() in { calframe[ 1 ][ 1 ] }" )

		return self.messenger.send( caller=self.name, **kwargs )

		pass # END METHOD : Send

	def waitForReply( self, message, **kwargs ):

		# Frame info.
		curframe	=	inspect.currentframe()
		calframe	=	inspect.getouterframes( curframe, 2 )
		logger.debug( f"{ self.name }.{ calframe[ 0 ][ 3 ] }() called by { self.name }.{ calframe[ 1 ][ 3 ] }()" )

		reply		=	None
		q			=	self.getQueue( self.name )
		end			=	time.time() + kwargs.get( 'timeout', 5 )
		ignoreLock	=	True if kwargs.get( 'ignoreLock' ) else False

		if not ignoreLock:
			self.getLocks( 'queue' ).acquire()
			pass # END IF

		messages	=	[]

		while time.time() < end:

			try:

				reply	=	self.getQueueMessage( mailboxQueue = q )
				logger.debug( f"{ self.name }.{ calframe[ 0 ][ 3 ] }() : reply for '{ self.name }' queue : { reply }" )

				# Nothing has come through yet.
				if not reply:
					time.sleep( 1 )
					continue
					pass # END IF

				# Reply found.
				elif (
					message[ 'threadid' ] == reply[ 'threadid' ]
					and
					message[ 'threadindex' ] == ( reply[ 'threadindex' ] - 1 )
				):
					logger.debug( f"{ self.name }.{ calframe[ 0 ][ 3 ] }() : reply found." )
					break
					pass # END IF

				# Save for restoring queue.
				else:
					messages.append( reply )
					pass # END ELSE

				pass # END TRY

			except queueEmpty:
				reply	=	None
				time.sleep( 1 )
				continue
				pass # END EXCEPT

			pass # END WHILE

		# Continue backing up messages from queue
		while not q.empty():
			messages.append( q.get() )
			pass # END

		# Restore queue for mailman to resume
		[ q.put( m ) for m in messages ]

		if not ignoreLock:
			self.getLocks( 'queue' ).release()
			pass # END IF

		return reply

		pass # END METHOD : Wait for reply

	def reply( self, message, **kwargs ):

		# Flip recipient and sender
		message.update({
			'recipient'	:	message.get( 'sender' ),
			'sender'	:	message.get( 'recipient' ),
			'subject'	:	kwargs.get( 'subject', 'reply' )
		})

		for k in [
			'messageid',
			'time',
		]:
			if k in message:
				del message[ k ]
				pass # END IF
			pass # END FOR

		message	=	{
						**message,
						**kwargs,
					}

		return self.messenger.send(
			caller=self.name,
			**message,
		)

		pass # END METHOD : Reply

	pass # END CLASS : Extend
