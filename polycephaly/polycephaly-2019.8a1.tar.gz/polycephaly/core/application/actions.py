#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# System
import time

# Polycephaly
import polycephaly.functions.utilities

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def appExit( self, countdown ):
		'''

		Used by
		:any:`Application.run() <polycephaly.core.application.setup.Extend.run>`
		to notify the user which sub-processes are still active and stalling the application's exit.

		:param countdown: Explicitly set by `threadsTimeout`.
			This sets how many seconds your application should wait on sub-processes after the Main process has stopped.
			This allows for longer tasks such as database-related processes to complete their transactions and shutdown.
		:type countdown: integer

		:return: Returns `True` if all sub-processes are shutdown.
		:rtype: bool

		'''

		processes	=	self.activeSubProcesses()

		# Everything is finished, we can exit.
		if not processes:
			return True

		# Attempt to send a stop signal to all threads.
		while processes:

			if countdown < 1:
				logger.critical( f'{ self.name } : gave up waiting.' )
				break # END IF

			# Update list of active processes
			processes	=	self.activeSubProcesses()

			# Everything is finished, we can exit.
			if not processes:
				return True
				break
				pass # END IF

			# Still waiting
			logger.warning( f"{ countdown } : { self.name } : waiting on { ', '.join( processes ) }" )

			countdown	-=	1
			time.sleep( 1 )

			pass # END WHILE

		pass # END METHOD : Application Exit

	def start( self, processName ):
		'''

		Refers to Polycephaly's processes' threads table, and is used for launching a sub-process within Polycephaly.
		If you're familiar with Python's
		`threading <https://docs.python.org/3/library/threading.html>`_
		and
		`multiprocessing <https://docs.python.org/3/library/multiprocessing.html>`_
		modules, this runs the `start()` method found in both instances.

		:param processName: the *friendly* process name that your sub-processes go by.
		:type countdown: string

		'''

		logger.debug( f"Process '{ processName }' : starting." )

		for case in polycephaly.functions.utilities.switch( self._procs.objects[ processName ].getParameter( 'runtime' ).mode ):

			if case( 'A' ):			#	 AsyncIO
				raise ValueError( "ASYNCIO ISN'T IMPLEMENTED YET." )
				break # END CASE :		/AsyncIO

			# Threading or Multiprocessing - both start the same.
			if case( 'T' ): pass	#	 Threading
			if case( 'M' ):			#	 Multiprocessing
				self._procs.threads[ processName ].start()
				break # END CASE

			if case( 'P' ):			#	 Popen
				raise ValueError( "POPEN ISN'T IMPLEMENTED YET." )
				break # END CASE :		/Popen

			# Fall-through
			if case():
				raise ValueError( 'Unknown start mode.' )
				break # END CASE

			pass # END SWITCH

		logger.debug( f"Process '{ processName }' : started." )

		pass # END METHOD : Start

	def stop( self, processName ):

		# Send a poison pill to the sub-process
		self.pcm.send(
			caller			=	self.name,
			recipient		=	processName,
			subject			=	self.ppill,
			coreApplication	=	True,			# Can be used for tracing where this came from.
		)

		# Wait for process to shutdown
		for i in range( self.threadsTimeout+1, -1, -1 ):

			if not self._procs.threads[ processName ].isAlive():
				logger.info( f"Process '{ processName }' has stopped." )
				break
				pass # END IF

			logger.info( f"Waiting { i } second{ 's' if i != 1 else '' } for '{ processName }' to stop." )

			time.sleep( 1 )
			pass # END FOR

		# Zombie!
		if ( i >= self.threadsTimeout ) and self._procs.threads[ processName ].isAlive():

			logger.warning( f"Process '{ processName }' is still alive, and did not heed Application-level request to stop." )
			return False

			pass # END IF

		# Everything is fine, delete thread entry, then re-create it so that it can be started again.
		else:

			logger.debug( f"Deleting '{ processName }' from processes' threads table." )
			del self._procs.threads[ processName ]

			logger.debug( f"Resetting '{ processName }' entry in processes' threads table." )
			self._createProcessInstance( processName )
			
			logger.debug( f"Resetting '{ processName }' active state for its next start-up." )
			self.getProcess( processName ).isActive( True )

			return True

			pass # END ELSE

		pass # END METHOD : Stop

	def restart( self, processName ):

		logger.debug( f"Restarting '{ processName }' process." )

		self.stop( processName )

		self.start( processName )

		pass # END METHOD : Restart

	pass # END CLASS : EXTEND
