#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# System
import time

# Reflection / Debugging
import inspect
import traceback

# Types
import uuid

# Message Queues
from queue import Full as queueFull

# Polycephaly
import polycephaly.functions.utilities

# Formatting
from pprint import pformat as pf

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def getQueueMessage( self, caller=None, mailboxQueue=None, **kwargs ):

		# Frame info.
		curframe	=	inspect.currentframe()
		calframe	=	inspect.getouterframes( curframe, 2 )
		logger.debug( f"{ calframe[ 0 ][ 3 ] }() called by { calframe[ 1 ][ 3 ] }()" )

		msg	=	{}

		try:

			# Locate caller in queues.
			if ( caller not in self.listQueues() ) and not mailboxQueue:
				raise KeyError( f"'{ caller }' queue doesn't exist." )
				pass # END IF

			# Current queue for caller.
			mailboxQueue	=	mailboxQueue if mailboxQueue else self.getQueue( caller )

			# Queue not empty
			if not mailboxQueue.empty():

				msg	=	mailboxQueue.get()		# Get message

				logger.debug( f"getQueueMessage( caller='{ caller }', mailboxQueue='{ pf( mailboxQueue ) }' ) received { pf( msg ) }" )

				msg	=	{
							**msg,
							**kwargs,
						}

				pass # END IF : QUEUE NOT EMPTY

			pass # END TRY

		except Exception as e:

			logger.warning( e )
			logger.warning( traceback.format_exc() )

			msg		=	{
							**{
								'sender'			:	caller,
								'recipient'			:	caller,
								'action'			:	calframe[ 0 ][ 3 ],
								'failed'			:	True,
								'body'				:	msg,
								'e'					:	e,
								'traceback'			:	traceback.format_exc(),
							},
							**kwargs,
						}

			pass # END EXCEPTION

		finally:
			return msg
			pass # END

		pass # END METHOD : Get Queue Message

	def mailman( self, caller, route=None, message=None ):
		'''
		Message should be dict if wanting to override.
		'''

		# Empty dictionary
		if not message:
			return False
			pass # END IF

		logger.debug( f"mailman( caller={ caller }, route={ route }, message={ pf( message ) } )" )

		currMatchCBs		=	self.matchFilter(
									caller=caller,
									route=route,
									message=message,
								)
		currMatchCBs_size	=	len( currMatchCBs )

		if not currMatchCBs_size:
			logger.warning( f"No filters were found for '{ caller }' to match message: { message }." )
			return False
			pass # END IF

		for i, currCB in enumerate( currMatchCBs ):

			try:
				logger.debug( f"{ caller } filter { i+1 } / { currMatchCBs_size } : { currCB.__name__ }() : running." )
				currCB( message )
				logger.debug( f"{ caller } filter { i+1 } / { currMatchCBs_size } : { currCB.__name__ }() : finished." )
				pass # END

			except Exception as e:

				logger.error( f"{ caller } filter { i+1 } / { currMatchCBs_size } : { currCB.__name__ }() : failed : { e }." )
				logger.error( traceback.format_exc() )

				pass # END

			pass # END FOR

		pass # END METHOD : Mailman

	def send( self, caller, **kwargs ):

		# Frame info.
		curframe	=	inspect.currentframe()
		calframe	=	inspect.getouterframes( curframe, 2 )

		kwargs.update({
			'sender'	:	kwargs.get( 'sender', caller ),
			'messageid'	:	str( uuid.uuid4() ),
			'time'		:	time.time(),
			'threadid'	:	kwargs.get( 'threadid', str( uuid.uuid4() ) )
		})

		q				=	None
		qName			=	None
		recipientType	=	polycephaly.functions.utilities.getType( kwargs[ 'recipient' ] ).upper()

		recipientQueue	=	polycephaly.functions.utilities.easySwitch(
								recipientType,
								None,
								STR=self.getQueue( kwargs[ 'recipient' ] ),
								QUEUE=kwargs[ 'recipient' ],
							)

		if ( kwargs[ 'sender' ].upper() == kwargs[ 'recipient' ].upper() ):

			qName	=	kwargs[ 'recipient' ]
			q		=	recipientQueue

			pass # END IF

		# Use Main to relay
		elif (

			# Sender needs Main to relay to Recipient.
			(
				kwargs[ 'recipient' ].lower() != self.nameMain
				and
				kwargs[ 'sender' ].lower() != self.nameMain
			)

			or

			# Recipient is Main.
			kwargs[ 'recipient' ].lower() == self.nameMain

		):

			qName	=	self.nameMain
			q		=	self.getQueue( self.nameMain )

			pass # END ELSE IF

		elif recipientQueue:

			if recipientType == 'STR':

				qName	=	kwargs[ 'recipient' ]

				pass # END IF

			elif recipientType == 'QUEUE':

				qName	=	'direct queue'

				pass # END ELSE

			q		=	recipientQueue

			pass # END ELSE IF

		else:

			logger.warning( f"Unable to route message: '{ kwargs[ 'sender' ] }' => '{ kwargs[ 'recipient' ] }'" )

			pass # END ELSE

		if q:

			# If applicable, add thread index
			if kwargs.get( 'threadid' ):
				kwargs.update({
					'threadindex'	:	( kwargs.get( 'threadindex', 0 ) + 1 )
				})
				pass # END IF

			# Add message to queue
			try:

				logger.debug( f"{ calframe[ 0 ][ 3 ] }() : added message to queue:\nQueue   : '{ qName }' : { q }\nCaller  : '{ caller }'\nFrom    : '{ kwargs[ 'sender' ] }'\nTo      : '{ kwargs[ 'recipient' ] }'\nMessage :\n{ pf( kwargs ) }" )

				# Add to message queue
				q.put(
					kwargs,		# Data
					True,		# Block
					5			# Timeout
				)

				pass # END TRY

			except queueFull:
				logger.error( f"Unable to add message to '{ qName }' queue due to it being full." )
				return False
				pass # END EXCEPTION

			pass # END IF

		return kwargs

		pass # END METHOD : SEND

	pass # END CLASS : Polycephaly Messenger
