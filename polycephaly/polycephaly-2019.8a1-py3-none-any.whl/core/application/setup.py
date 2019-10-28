#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Processes
import threading
import multiprocessing

# Types
import types

# Polycephaly
import polycephaly.functions.utilities

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def addProcess( self, processReference, *args, **kwargs ):
		'''

		Description

		Parameters
		----------
		processReference : :obj:`Module` or :obj:`Class`
			Can accept a Python `module` if the module contains a `Process` class, otherwise you'll need to pass the direct `class` to use.
		*args
			Variable length argument list passed directly to the sub-process.
		**kwargs
			Arbitrary keyword arguments passed directly to the sub-process.  That said, there are reserved keywords that are used by this method, and based upon `_skel` process definition in `polycephaly.core.application`:
				* **name** (:obj:`str`, optional) – Used for specifying a *friendly* name for reference by other processes.  If not set, Polycephaly will attempt to fill in a friendly name that's easily recognized.
				* **mode** (:obj:`str`, optional) – Sets the run mode for the sub-process, and defaults to `Threading`.  Options are:
					* **Threading** – If you're working with I/O related tasks, this option should suffice, and will cover nearly all of your uses.
					* **Multiprocessing** – If you're working with CPU-intensive tasks such as Machine Learning (or directly with `R.O.S. <https://www.ros.org>`_ via `Rospy <http://wiki.ros.org/rospy>`_), use this option.
					* **AsyncIO** – Not yet implemented.
					* **Popen** – Not yet implemented.
				* **autostart** (:obj:`bool`, optional) - Defaults to True, and will spin up the sub-process (via :any:`_launchAutoruns() <polycephaly.core.application.setup.Extend._launchAutoruns>`) once :any:`Application.run() <polycephaly.core.application.setup.Extend.run>` executes.
				* **depends** – Not yet implemented.
				* **frequency** (:obj:`int`, optional) – Local frequency (number of times per second that this sub-process should attempt to run the process' :any:`life() <polycephaly.core.process.events.Extend.life>` callback) that overrides what's set with :any:`globalFrequency() <polycephaly.core.application.timing.Extend.globalFrequency>` inside of :any:`Application.build() <polycephaly.core.application.events.Extend.build>`.
				* **boundShutdown** – (:obj:`bool`, optional) – Defaults to True, and dictates whether the sub-process should (forcefully) exit alongside of the Application, or be responsible for its own termination.  You'll almost always want this to be set to True, and should only override this if you're really sure.

		Returns
		-------
		bool
			True if successful, False if it can't locate the `Process` class inside of the module passed to it.

		Raises
		------
		ValueError
			Occurs when attempting to add a process with the same friendly name as one that already exists.

		'''

		# Used for initialization of a class, and then storing its object reference.
		processClass	=	None

		# Attempt to fill-in the name of the Module or Class.  e.g. processes.main = main or processes.helloWorld.Process = helloWorld
		processName		=	None

		# Obtain process name and class based upon its reference.
		for case in polycephaly.functions.utilities.switch( polycephaly.functions.utilities.getType( processReference ).upper() ):

			# Module
			if case( 'MODULE' ):
				processName		=	getattr( processReference, '__name__', '' ).split( '.' )[ -1 ]
				if hasattr( processReference, 'Process' ):
					processClass	=	getattr( processReference, 'Process' )
					pass # END IF
				else:
					logger.error( f"Unable to locate Process() class for module '{ processReference.__name__ }'. Skipping this attempt." )
					return False
					pass # END ELSE
				break # END CASE

			# Class
			if case( 'TYPE' ):
				processName		=	getattr( processReference, '__module__', '' ).split( '.' )[ -1 ]
				processClass	=	processReference
				break # END CASE

			pass # END SWITCH : type of processReference

		# e.g. procMain or if name is specified, something simple like 'main'
		processName		=	kwargs.pop( 'name', processName ).lower()

		# Reject if exist
		if processName in self._procs.objects:
			raise ValueError( "'{}' is already in use.".format( processName ) )
			pass # END IF

		# Place reserved keywords in runtime variable
		runtime	=	{}
		for k, v in self._skel.runtime.items():

			runtime[ k ]	=	kwargs.pop( k ) if ( k in kwargs ) else v
			logger.debug( f"Run-time : { processName }.{ k } = '{ runtime[ k ] }'" )

			pass # END FOR

		# Alias or direct name of run-time
		for case in polycephaly.functions.utilities.switch( runtime[ 'mode' ][ 0 ].upper() ):

			# AsyncIO
			if case( 'A' ):
				runtime[ 'mode' ]	=	'A'
				break # END CASE : AsyncIO

			# Threading
			if case( 'T' ):
				runtime[ 'mode' ]	=	'T'
				break # END CASE : Threading

			# Multiprocessing / forked process
			if case( 'M' ): pass
			if case( 'F' ):
				runtime[ 'mode' ]	=	'M'
				break # END CASE : Multiprocessing

			# Popen()-based program / external Program
			if case( 'P' ): pass
			if case( 'E' ):
				runtime[ 'mode' ]	=	'P'
				break # END CASE : Popen

			pass # END SWITCH : type of processReference

		# Create message queue for process
		self.pcm.addQueue(
			name		=	processName,
			queueType	=	runtime[ 'mode' ],
		)

		# Initialization of class, and saving it as an object.
		self._procs.objects[ processName ]	=	processClass(
													*args,
													**kwargs,
													ppill		=	self.ppill,
													messenger	=	self.pcm,
													name		=	processName,
													nameMain	=	self.name,
													runtime		=	types.SimpleNamespace( **runtime ),
													paths		=	self.paths,
												)

		return True

		pass # END METHOD : Add process

	def _setDefaultFreqs( self ):
		'''

		Used by run()

		'''

		# Set default frequency
		if not self.globalFrequency():
			logger.debug( f"Application frequency is not set.  Setting default frequency to skeleton's runtime frequency : { self._skel.runtime[ 'frequency' ] }." )
			self.globalFrequency( self._skel.runtime[ 'frequency' ] )
			pass # END IF

		# Set default for processes missing frequencies
		for currProcess in self.listProcessInstances():

			if not self.getProcess( currProcess ).frequency():

				logger.debug( f"Setting default frequency for '{ currProcess }' to '{ self.globalFrequency() }'." )
				self.getProcess( currProcess ).frequency( self.globalFrequency() )

				pass # END IF

			pass # END FOR

		pass # END METHOD : Set default frequencies

	def _createProcessInstance( self, processName ):

		if processName not in self._procs.objects:
			logger.error( f"Process '{ processName }' does not exist in the procs.objects table." )
			return False
			pass # END

		processInstance	=	self._procs.objects[ processName ]

		logger.info( f"Creating process instance: '{ processName }'" )

		# Mode: Async, Thread, or MultiProcess
		for case in polycephaly.functions.utilities.switch( processInstance.getParameter( 'runtime' ).mode ):

			if case( 'A' ):			#	 AsyncIO
				raise ValueError( "ASYNCIO ISN'T IMPLEMENTED YET." )
				break # END CASE :		/AsyncIO

			if case( 'T' ):			#	 Threading

				self._procs.threads[ processName ]	=	threading.Thread(
															target=processInstance.main,
															args=(),
															kwargs={
																'application' : self,
															},
														)

				# Main : Enable Daemon (will quit when main process quits)
				self._procs.threads[ processName ].daemon	=	processInstance.getParameter( 'runtime' ).boundShutdown
				logger.debug( f"Thread : { processName }.daemon = { self._procs.threads[ processName ].daemon }" )

				break # END CASE :		/Threading

			if case( 'M' ):			#	 Multiprocessing

				self._procs.threads[ processName ]	=	multiprocessing.Process(
															target=processInstance.main,
															args=(),
															kwargs={
																'application' : self,
															},
														)

				# Main : Enable Daemon (will quit when main process quits)
				self._procs.threads[ processName ].daemon	=	processInstance.getParameter( 'runtime' ).boundShutdown
				logger.debug( f"Multiprocessing : { processName }.daemon = { self._procs.threads[ processName ].daemon }" )

				break # END CASE :		/Multiprocessing

			if case( 'P' ):			#	 Popen
				raise ValueError( "POPEN ISN'T IMPLEMENTED YET." )
				break # END CASE :		/Popen

			# Fall-through
			if case():
				raise ValueError( 'Unknown run mode.' )
				break # END CASE

			pass # END SWITCH

		return True

		pass # END METHOD : Create Process Instance

	def _createProcessInstances( self ):
		'''

		Creates instances based on main() for each class instance.

		'''

		# Iterate processes that were added, and set each of them up.
		for processName in self._procs.objects.keys():

			# Main run is in program, and doesn't need a thread or a forked process.
			if processName.upper() == self.name.upper():
				continue
				pass # END IF

			self._createProcessInstance( processName )

			pass # END FOR : PROCESS ITERATION

		pass # END METHOD : Create process instances

	def _launchAutoruns( self ):
		'''

		Iterates over the Polycephaly processes' instantiation table for each sub-process friendly name, and then uses :any:`Application.start() <polycephaly.core.application.actions.Extend.start>` to spin each sub-process up.

		'''

		logger.debug( f"Starting auto-run processes." )

		for processName in [ k for k,v in self._procs.objects.items() if v.getParameter( 'runtime' ).autostart ]:

			logger.debug( f"Launching auto-runs : starting '{ processName }' process." )
			self.start( processName )

			pass # END FOR

		pass # END METHOD : LAUNCH AUTO-RUNS

	def _joinSubProcesses( self ):

		logger.debug( 'Application._joinSubProcesses()' )

		# Attempt to join threads
		for processName, processAttr in self._procs.threads.items():

			if not processAttr.daemon and processAttr.is_alive():

				logger.error( f"Attaching to sub-process '{ processName }' (runtime = { self._procs.objects[ processName ].getParameter( 'runtime' ) }) and waiting for it to finish..." )
				processAttr.join()

				pass # END IF

			pass # END FOR

		pass # END METHOD : Join process threads

	def run( self ):
		'''

		Used in the application launcher to setup all sub-processes and then run your Main process.

		'''

		logger.debug( 'run() initiated.' )

		# Set default frequencies for anything that's missing - also catch-up on Main process' timing.
		self._setDefaultFreqs()

		# Bind sub-process instances (thread/multiprocess) to main() method of each process.
		self._createProcessInstances()

		# Launch sub-processes
		self._launchAutoruns()

		# Launch Main process
		logger.debug( f"Starting Main process." )
		self._procs.objects[ self.name ].main(
			application		=	self,
		)

		if not self.appExit( countdown=self.threadsTimeout ):
			logger.critical( "Application shutdown experienced failure while trying to shutdown processes." )
			pass # END IF

		self._joinSubProcesses()

		logger.debug( 'run() completed.' )

		pass # END METHOD : RUN

	pass # END CLASS : EXTEND
