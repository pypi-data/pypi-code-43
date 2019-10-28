#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Types
import types

# Processes
import threading

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def launchThreads( self ):
		'''
		Used for launching any methods that start with `_thread`, such as `_threadConnection` used by OpenCM and Arduino.
		'''

		# Search attributes for threads
		for sk in dir( self ):

			# Not valid
			if not ( sk.startswith( '_thread_' ) and callable( getattr( self, sk ) ) ):
				continue
				pass # END IF

			# Everything after `_thread`
			skName	=	sk[ 8: ].lower()

			args	=	[
							skName,					# Name
							getattr( self, sk ),	# Method
						]

			# This is probably a dynamically created method, such as the case of examples/threadSpinner/.
			if isinstance( getattr( self, sk ), types.FunctionType ):
				args.append( self )
				pass # END IF

			self.addChildThread( *args )

			args.clear()

			pass # END FOR

		pass # END METHOD : Launch threads

	def addChildThread( self, name, method, *args, **kwargs ):

		daemon	=	kwargs.pop( 'daemon', True )
		start	=	kwargs.pop( 'start', True )

		logger.debug( f"Setting up thread for '{ name }'." )

		self._threads.update({

			name	:	threading.Thread(
							target	=	method,
							args	=	args,
							kwargs	=	kwargs,
						),

		})

		self._threads[ name ].daemon	=	daemon

		if start:
			self._threads[ name ].start()
			pass # END IF

		pass # END METHOD : Add thread

	def removeChildThreads( self, *args ):

		for a in args:

			# Not found
			if a not in self._threads:
				logger.warning( f"Cannot remove { self.name }.{ a }, it doesn't exist." )
				pass # END IF

			# This doesn't stop the thread, you're responsible for that.
			elif (
				a in self._threads
				and
				self._threads[ a ].is_alive()
			):
				logger.error( f"Cannot remove { self.name }.{ a }, it's still active." )
				pass # END ELIF

			# Finally, a success.
			elif ( a in self._threads ):
				logger.debug( f"Removed thread '{ a }' from '{ self.name }' process." )
				del self._threads[ a ]
				pass # END ELIF

			else:
				logger.error( 'An unknown error has occurred.' )
				pass # END ELSE

			pass # END FOR

		pass # END METHOD : Remove thread entry

	def childThreadJanitor( self ):

		livingChildren	=	self.listChildThreadsLives()

		for threadName, threadAlive in livingChildren.items():

			# Thread has reached its EOL, time to remove it from the table.
			if not threadAlive:
				logger.debug( f"{ self.name }._thread_{ threadName }() is no longer alive, and is being removed from the threads table." )
				self.removeChildThreads( threadName )
				pass # END IF

			pass # END FOR

		pass # END METHOD : Child Thread Janitor

	def getChildThreads( self, *args ):

		if args:
			return { k:v for k,v in self._threads.items() if k in args }
			pass # END IF

		else:
			return self._threads
			pass # END ELSE

		pass # END METHOD : Get threads

	def listChildThreadsLives( self, *args ):
		return { threadName : self._threads[ threadName ].isAlive() for threadName in ( self._threads.keys() if not args else [ str( a ) for a in args ] ) if threadName in self._threads }
		pass # END METHOD : Is child thread alive?

	def joinChildThreads( self ):

		logger.debug( f"{ self.name }.joinChildThreads()" )

		# Attempt to join threads
		for threadName, threadAttr in self._threads.items():

			if threadAttr.is_alive():

				logger.debug( f"Attaching to { self.name }.{ threadName }() child thread and waiting for it to finish..." )
				threadAttr.join()

				pass # END IF

			pass # END FOR

		pass # END METHOD : Join children to parent process

	pass # END CLASS : EXTEND
