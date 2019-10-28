#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Reflection / Debugging
import traceback

# Polycephaly
import polycephaly.functions.threading

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def main( self, *args, **kwargs ):

		self._application	=	kwargs.pop( 'application' )

		logger.info( f"{ self.name }.main() started." )

		self.runLevel( 'BUILDUP' )

		logger.debug( f"{ self.name }.birth() starting." )
		self.birth()
		logger.debug( f"{ self.name }.birth() finished." )

		# Default signal binding if none were set ahead of time.
		if polycephaly.functions.threading.isMainThreadInAPythonProcess() and not self.signalsUsed():

			self.backupSignals()

			tempSignals	=	[
								'SIGHUP',	# Usually, a reload request.
								'SIGINT',	# ^C
								'SIGQUIT',	# ^\
								'SIGCONT',	# Usually, a resumed process.
								'SIGTERM',	# `kill procID` or `pkill myApp.py` and systemd's default kill signal.
								'SIGTSTP',	# ^Z
							]

			logger.critical( f"Setting signals ({ ', '.join( tempSignals ) }) to route to sigTrap()" )
			self.signals( self.sigTrap, *tempSignals )
			del tempSignals

			pass # END IF

		logger.debug( f"{ self.name }.life() starting." )

		self._currFrame		=	0
		self.runLevel( 'RUN' )

		while self.isActive():

			try:

				self.life()

				# Application forgot to run mailman() which the shutdown process relies upon.
				if not self._ranMailman:
					logger.info( f"{ self.name }.mailman() wasn't run in { self.name }.life() - now running it." )
					self.mailman()
					pass # END IF

				# Reset for next run.
				self._ranMailman	=	False

				pass # END TRY

			except Exception as e:
				logger.error( f"{ self.name }.life() experienced an error:\n{ traceback.format_exc() }" )
				pass # END EXCEPTION

			self.freqSleep()

			self._currFrame	+=	1

			if self._currFrame > self.frequency():
				self._currFrame		=	1
				pass # END IF

			pass # END WHILE ACTIVE LOOP

		logger.debug( f"{ self.name }.life() finished." )

		logger.debug( f"{ self.name }.death() starting." )

		self.runLevel( 'HALT' )
		self.joinChildThreads()
		self.death()
		self.runLevel( 'UNSET' )

		logger.debug( f"{ self.name }.death() finished." )

		logger.info( f"{ self.name }.main() stopped." )

		pass # END METHOD : Main

	pass # END CLASS : EXTEND
