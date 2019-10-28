#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# System
import os
import time

# Pattern matching
import glob

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

#------------------------------------------------------------ IMPORT ALL MODULES
currDir	=	os.path.dirname( __file__ )

# https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder
modules	=	glob.glob( f"{currDir}/*.py" )
__all__	=	[ os.path.basename(f)[:-3] for f in modules if os.path.isfile( f ) and not f.endswith('__init__.py') ]

# Add sub-modules
__all__	+=	[ d for d in os.listdir( currDir ) if (
				os.path.isdir( os.path.join( currDir, d ) )
				and
				os.path.isfile( os.path.join( currDir, d, '__init__.py' ) )
			) ]

from . import *
#------------------------------------------------------------/IMPORT ALL MODULES

class Extend(
	actions.Extend,
	filters.Extend,
	info.Extend,
	setup.Extend,
):

	pass # END CLASS : EXTEND
