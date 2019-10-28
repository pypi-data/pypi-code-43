#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# System
import signal

# Polycephaly
import polycephaly.functions.threading

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def signalsDict( self, k=None ):
		'''
		'''

		d	=	{ str( v ):int( k ) for v,k in signal.__dict__.items() if v.startswith( 'SIG' ) and not v.startswith( 'SIG_' ) }

		if isinstance( k, str ) and k.upper() in d.keys():
			return d[ k ]
			pass # END

		elif isinstance( k, int ) and k in d.values():
			fd	=	{ v:k for k,v in d.items() }
			return fd[ k ]
			pass # END

		elif k is None:
			return d
			pass # END

		else:
			return None
			pass # END

		pass # END METHOD : Signals Dictionary

	def backupSignals( self ):

		logger.debug( f'{ self.name } : backing up signals.' )

		self._signalsBak	=	{}

		# e.g. SIGINT, 2
		for sigName, sigNumber in self.signalsDict().items():

			logger.debug( f"Backing up '{ sigName }'." )
			currSignal					=	getattr( signal, sigName )		# Retrieve Signal type (e.g. Signals.SIGINT)
			self._signalsBak[ sigName ]	=	signal.getsignal( currSignal )	# Save handler (e.g. <built-in function default_int_handler>)

			pass # END FOR

		pass # END METHOD : Backup Signals

	def restoreSignals( self ):

		logger.debug( f'{ self.name } : restoring signals.' )

		if not self._signalsBak:
			logger.error( "There are no signals to restore." )
			return False
			pass # END IF

		for sigName, sigHandler in self._signalsBak.items():

			logger.debug( f"Restoring '{ sigName }'." )
			currSignal	=	getattr( signal, sigName )
			signal.signal( currSignal, sigHandler )

			pass # END FOR

		return True

		pass # END METHOD : Restore Signals

	def signalsUsed( self, i=None ):

		if i:
			self._signalsUsed	=	i
			pass # END IF

		return self._signalsUsed

		pass # END METHOD

	def signals( self, cb, *keys ):
		'''
		Bind signal to callback.
		'''

		if not polycephaly.functions.threading.isMainThreadInAPythonProcess():
			logger.warning( f"{ self.name } ( Mode={ self.getParameter( 'runtime' ).mode } ) : ignoring signals request since these actions can only be performed on the main thread of each Python process." )
			return False
			pass # END PASS

		self.signalsUsed( True )

		r					=	None

		try:

			for currKey in keys:

				currKey	=	currKey.upper()

				if (
					currKey.startswith( 'SIG' )
					and
					not currKey.startswith( 'SIG_' )
					and
					hasattr( signal, currKey )
				):

					sigNum	=	getattr( signal, currKey )
					signal.signal( sigNum, cb )

					logger.debug( f"Process '{self.name}' : bind '{ currKey }' to { cb.__name__ }()." )
					r	=	True

					pass # END IF

				pass # END FOR

			pass # END TRY

		except Exception as e:

			logger.critical( f"{self.name} : {e}" )
			r	=	False

			pass # END EXCEPTION

		finally:

			return r

			pass # END FINALLY

		pass # END METHOD : Signals

	def sigTrap( self, sigNum, currFrame ):

		self.die(
			sigNum		=	sigNum,
			currFrame	=	currFrame,
		)

		pass # END METHOD : Signal Trap

	pass # END CLASS : EXTEND
