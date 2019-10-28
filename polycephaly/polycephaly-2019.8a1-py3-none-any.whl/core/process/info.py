#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Reflection / Debugging
import inspect

# Polycephaly
import polycephaly.functions.utilities
import polycephaly.functions.threading

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def runLevel( self, i=None ):

		curframe = inspect.currentframe()
		calframe = inspect.getouterframes( curframe, 2 )

		if i:

			# Run-level given as a string instead of an integer.
			if isinstance( i, str ):
				i	=	self.runLevels( i )
				pass # END IF

			i	=	( None if i == -1 else i )
			logger.debug( f"'{ self.name }' : changing run level from { self._runLevel } ({ self.runLevels( self._runLevel ) }) to { i } ({ self.runLevels( i ) })." )
			self._runLevel	=	i
			pass # END IF

		else:
			logger.debug( f"'{ self.name }' current run level : { self._runLevel } ({ self.runLevels( self._runLevel ) }), queried by { calframe[ 1 ][ 3 ] }()." )
			pass # END ELSE

		return self._runLevel

		pass # END METHOD : Run Level

	def runLevels( self, i=None ):

		runLevels		=	{
								-1	:	'UNSET',
								0	:	'HALT',
								1	:	'BUILDUP',
								2	:	'RUN',
								3	:	None,
								4	:	None,
								5	:	None,
								6	:	'REBOOT',
								7	:	'CLEANUP',
							}

		# Convert string to integer value
		if isinstance( i, str ):

			# Convert to uppercase for matching.
			i			=	i.upper()

			# Reverse the dictionary
			runLevels	=	polycephaly.functions.utilities.invertedDict( runLevels )

			pass # END IF

		return runLevels.get( i, None )

		pass # END METHOD : Run Levels

	def isActive( self, i=None ):

		# Optional : update active status
		if ( i == False ) ^ ( i == True ):
			logger.debug( f"'{ self.name }' : set active state to { i }." )
			self._active	=	i
			pass # END IF

		# Return active status
		return self._active

		pass # END METHOD

	def getParameter( self, name ):
		"""
		For returning core initialization parameters.
		"""

		return getattr( self, '_{}'.format( name ) )

		pass # END METHOD

	def getApp( self ):
		'''
		Returns application instance.
		'''
		return self._application if ( not polycephaly.functions.threading.isProcessForked() ) else None
		pass # END METHOD : Get Application

	def _procInfoSkel( self ):
		'''
		This is the basis for aliased methods to query the Main process for information about other processes.
		'''

		curframe = inspect.currentframe()
		calframe = inspect.getouterframes( curframe, 2 )

		# Main process
		if polycephaly.functions.threading.isApplicationMainThread():
			return getattr( self.getApp(), calframe[ 1 ][ 3 ] )()
			pass # END IF

		# Sub-process
		else:

			message		=	self.send(
								recipient	=	self.nameMain,
								subject		=	'procInfo',
								body		=	calframe[ 1 ][ 3 ],
							)

			reply		=	self.waitForReply( message, timeout=15 )

			return reply.get( 'body' )

			pass # END ELSE

		pass # END METHOD : Process Info Skeleton

	def activeSubProcesses( self ):
		return self._procInfoSkel()
		pass # END METHOD : Active Processes

	def listProcessInstances( self ):
		return self._procInfoSkel()
		pass # END METHOD : List processes

	def listRecipients( self ):
		return self._procInfoSkel()
		pass # END METHOD : List recipients

	pass # END CLASS : EXTEND
