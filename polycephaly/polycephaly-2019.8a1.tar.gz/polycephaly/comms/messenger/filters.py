#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Types
import uuid

# Pattern matching
import re

# Formatting
from pprint import pformat as pf

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )

class Extend( object ):

	def addFilter( self, caller=None, route=None, **kwargs ):

		caller	=	self._defCaller if ( not caller and self._defCaller ) else caller
		route	=	self._defRoute if ( not route and self._defRoute ) else route
		cbName	=	None

		# Missing 2 required positional arguments: 'caller' and 'route'
		if not caller or not route:
			raise TypeError( "Missing one of required positional arguments: 'caller' or 'route'" )
			pass # END IF

		# Callback is required for a filter, but we can just skip and move on.
		if 'callback' not in kwargs:
			logger.error( "Can't add empty filter." )
			return {}
			pass # END IF

		logger.info( f"{ caller }@{ route } : Add filter : callback='{ kwargs[ 'callback' ].__name__ }' ({ kwargs.get( 'description' ) })" )
		cbName	=	kwargs[ 'callback' ].__name__

		# Core filters
		for currFilter in [
			'callback',
			'sender',
			'recipient',
			'subject',
			'body',
			'time',
		]:
			kwargs.update({ currFilter : kwargs.get( currFilter ) })
			pass # END FOR

		# Add ID to filter (or use supplied) and description.
		kwargs.update({ 'id' : kwargs.get( 'id', str( uuid.uuid4() ) ) })
		kwargs.update({ 'description' : kwargs.get( 'description', '' ) })

		# Avoid overwriting
		if ( kwargs[ 'id' ] in [ v[ 'id' ] for v in self._filters[ caller ][ route ] ] ):
			logger.error( f"Skipping filter addition ({ kwargs[ 'description' ] }), a filter with this ID already exists." )
			return {}
			pass # END

		# Requirements haven't been met
		if (
			len( [ k for k,v in kwargs.items() if k in [ 'callback' ] and not v ] )
		):
			logger.error( 'Invalid route due to missing requirements.  Skipping.' )
			return {}
			pass # END IF

		# Fall-through filter
		if not any( [ v for k, v in kwargs.items() if k not in [ 'callback', 'id', 'description', ] ] ):
			logger.info( f"Fall-through filter added: '{ kwargs[ 'id' ] }' ({ kwargs[ 'description' ] })" )
			pass # END IF

		# Successfully store filter.
		logger.info( f'{ caller }@{ route } : Successfully added filter.' )
		logger.debug( pf( kwargs ) )

		self._filters[ caller ][ route ].append( kwargs )

		return kwargs

		pass # END METHOD : Add Filter

	def matchFilter( self, caller, route, message ):

		# Callback method(s)
		r			=	[]

		# Copy dictionary to preserve original
		currFilters	=	[ d.copy() for d in self._filters[ caller ][ route ] ]

		# Build fall-throughs
		fallthroughs	=	[]
		for ft in [ i for i, c in enumerate( currFilters ) if not any( [ v for k, v in c.items() if k not in [ 'callback', 'id', 'description', ] ] ) ]:

			currFilter		=	currFilters.pop( ft )
			currFilterCB	=	currFilter.pop( 'callback' )

			if callable( currFilterCB ):
				fallthroughs.append( currFilterCB )
				pass # END IF

			elif isinstance( currFilterCB, list ):
				[ fallthroughs.append( x ) for x in currFilterCB if callable( x ) ]
				pass # END ELIF

			pass # END FOR

		for currFilter in currFilters:

			currMatch	=	False
			currMatches	=	[]

			# Remove extra
			currFilterCB		=	currFilter.pop( 'callback' )
			currFilterDesc		=	currFilter.pop( 'description', None )

			[ currFilter.pop( _ ) for _ in currFilter.copy() if ( ( _[ 0 ] == '_' ) or ( _ in [ 'id', 'callback', 'description' ] ) ) ]

			# Iterate message filter
			for filterKey, filterVal in { k:v for k,v in currFilter.items() if k[ 0 ] != '_' }.items():

				# Filter parameter isn't set
				if not filterVal:
					continue
					pass # END IF

				# Invalid filter
				if filterKey not in message:
					logger.debug( f"Filter rule ({filterKey}) doesn't match message, moving to next filter." )
					currMatches.append( False )
					break
					pass # END IF

				currMatch	=	bool(
									re.match(
										str( filterVal ),
										str( message[ filterKey ] )
									)
								)

				# Filter parameter match?
				currMatches.append( currMatch )

				pass # END FOR : message filter

			# All parameters match
			if currMatches and all( currMatches ):

				logger.debug( f"Match{ '' if ( len( currMatches ) == 1 ) else 'es' } found." )

				if callable( currFilterCB ):
					r.append( currFilterCB )
					pass # END IF

				elif isinstance( currFilterCB, list ):
					[ r.append( x ) for x in currFilterCB if callable( x ) ]
					pass # END ELIF

				pass # END IF
			else:
				logger.debug( 'No matches were found.' )
				pass # END ELSE

			currMatches.clear()

			pass # END FOR : message filters

		# No current filters, but there is fall-throughs
		if not r and fallthroughs:
			r	+=	fallthroughs
			pass # END IF

		return r

		pass # END METHOD : Match filter

	def listFilters( self, caller=None, topic=None ):

		r	=	{ k : dict( v ) for k,v in self._filters.items() }

		r	=	r.get( caller ) if caller else r

		r	=	r.get( topic ) if topic else r

		return r

		pass # END METHOD : listFilters

	pass # END CLASS : Polycephaly Messenger
