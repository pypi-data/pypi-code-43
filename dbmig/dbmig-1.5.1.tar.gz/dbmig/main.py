#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Simple tool to run SQL migration scripts against an RDBMS. dbmig upports PosgreSQL and should
be easy to adapt to any backend supported by SQLAlchemy.

dbmig runs migration scripts which transition the database from one state to another. The
migration scripts must be stored in a repository which consists of a root directory,
possibly subdivided. The scripts can be plain SQL scripts with a .sql extension or Python scripts.

SQL scripts must be named XXX_(up|down)_NAME.sql, where XXX is the revision number and NAME is
anything you want. Python scripts must be named XXX_NAME.py. For example a script named
"005_up_Create_user_table.sql" defines a transition from revision 4 to revision 5. A script
named "001_Initial_schema.py" provides both upgrade (for 0 to 1) and downgrade (from 1 to 0)
capabilities. Revision 0 represents an empty database.

Python scripts must define one or two functions named "upgrade" and "downgrade", which take at
least one positional argument: a connection object provided by SQLAlchemy. They may, but are not
required to, accept a `schema` keyword argument (either directly or through the ``**kwargs``
construct).

Scripts are always executed within a transaction: a migration from one revision to the next (or
previous) is either fully done or not at all.

The `dbmig` command is available to migrate a database from the command-line. An embeddable API
is also available through the :py:class:`MigrationHandler` class.

Before dbmig can control a database, the database must be initialized, by creating a table
named `db_version`. This table consists of a single column and a single row storing the current
revision number. Use the ``-i`` flag to `dbmig.py` or :py:meth:`MigrationHandler.initialize_db`
to initialize a database. The ``-i`` flag can be used with an already-initialized database
without errors.

It is recommended to structure directories as follows:

    /path/to/repo/000/
    /path/to/repo/000/001_up_Initial_schema.sql
    /path/to/repo/000/001_down_Initial_schema.sql
    /path/to/repo/000/002_up_Some_changes.sql
    /path/to/repo/000/002_down_Some_changes.sql
    ...
    /path/to/repo/001/
    ...

'''
from __future__ import print_function

import inspect
import imp
import logging
import re
import os
import subprocess
import sys
import threading

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ProgrammingError, DataError, DatabaseError

logger = logging.getLogger(__name__)

class MigrationHandler(object):

	mig_script_re = re.compile('^(\d+)(_up|_down|_snap)?(_.+)?(\.py|\.sql)$', re.I)

	def __init__(self, repository, dsn, schema=None, reassign_to=None):
		'''
		:param repository: repository path
		:param dsn: database DSN
		:param schema: default schema
		:param reassign_to: user who should own all objects within the current database that are owned by the user performing the migration
		'''
		self.repository = repository
		self.dsn = dsn
		self.engine = create_engine(dsn)
		self.metadata = MetaData(self.engine)
		self.db_version = Table('db_version', self.metadata, Column('version', Integer, server_default='0', default=0), schema=schema)
		self.schema = schema
		self.reassign_to = reassign_to

	def quote_ident(self, ident):
		return self.engine.dialect.identifier_preparer.quote_identifier(ident)

	def quote(self, value):
		return self.engine.dialect.identifier_preparer.quote(value)

	def get_db_repr(self):
		url = make_url(self.dsn)
		return '%s://%s:%s/%s%s' % (url.drivername, url.host or '', url.port or '', url.database, '(schema=%s)' % self.schema if self.schema else '')

	def initialize_db(self):
		'''
		Initializes a database if it is not initialized already.
		'''
		c = self.engine.connect()
		trans = c.begin()
		try:
			try:
				if self.schema:
					c.execute('select * from %s.db_version;' % self.quote_ident(self.schema))
				else:
					c.execute('select * from db_version;')
			except DatabaseError as e:
				trans.rollback()
				trans = c.begin()
				create_table = False

				if self.engine.dialect.driver == 'psycopg2':
##					logger.info('PGCode %s', e.orig.pgcode)
					if e.orig.pgcode not in ('42P01','3F000'): # Missing schema, missing table
						raise
				elif self.engine.dialect.driver == 'pysqlite':
					if e.code not in ('e3q8',):
						raise
				else:
					raise

				if self.schema:
					try:
						c.execute(text('create schema %s;' % self.quote_ident(self.schema)))
					except DatabaseError as e2:
						trans.rollback()
						trans = c.begin()
						if e2.orig.pgcode != '42P06':
							raise
					c.execute(text('set search_path to %s, public;' % self.quote_ident(self.schema)))
				self.db_version.create(bind=c)
				if self.schema:
					c.execute('insert into %s.db_version values (0);' % self.quote_ident(self.schema))
				else:
					c.execute('insert into db_version values (0);')
		except Exception:
			trans.rollback()
			raise
		else:
			trans.commit()
			logger.info('%s initialized for schema migrations', self.get_db_repr())

	def get_rev_scripts(self, up_scripts=None, down_scripts=None, snapshots=None, directory=None):
		'''
		Returns a tuple (up_scripts, down_scripts, snapshots) where each member is a dictionary mapping revision IDs to script paths.

		:param up_scripts: a pre-filled dict as returned by this method; it will be updated. Optional.
		:param down_scripts: a pre-filled dict as returned by this method; it will be updated. Optional.
		:param snapshots: a pre-filled dict as returned by this method; it will be updated. Optional.
		:param directory: a directory to search. Optional.
		'''
		up_scripts = {} if up_scripts is None else up_scripts
		down_scripts = {} if down_scripts is None else down_scripts
		snapshots = {} if snapshots is None else snapshots
		directory = directory or self.repository
		for fn in os.listdir(directory):
			full_fn = os.path.join(directory, fn)
			if os.path.isdir(full_fn):
				self.get_rev_scripts(up_scripts, down_scripts, snapshots, full_fn)
				continue
			if not os.path.isfile(full_fn):
				continue
			m = self.mig_script_re.match(fn.lower())
			if m is None:
				continue
			rev_number = int(m.group(1))
			if m.group(2) == '_up':
				up_scripts[rev_number] = full_fn
			elif m.group(2) == '_down':
				down_scripts[rev_number] = full_fn
			elif m.group(2) == '_snap':
				snapshots[rev_number] = full_fn
			elif m.group(4) == '.py':
				up_scripts[rev_number] = down_scripts[rev_number] = full_fn
		return up_scripts, down_scripts, snapshots

	def get_highest_revision_number(self):
		return max(self.get_rev_scripts()[0].keys() or [0])

	def migrate(self, target_rev=None):
		'''
		Upgrades or downgrades the schema to `target_rev`.
		'''
		up_scripts, down_scripts, snapshots = self.get_rev_scripts()
		if target_rev is None:
			if not up_scripts:
				return
			target_rev = max(up_scripts.keys())
		c = self.engine.connect()

		if self.schema:
			trans = c.begin()
			c.execute(text('set search_path to %s, public;' % self.quote_ident(self.schema)))
			trans.commit()

		trans = c.begin()
		try:
			current_rev = c.execute('select version from %sdb_version;' % (self.quote_ident(self.schema) + '.' if self.schema else '')).scalar()
			if target_rev == current_rev:
				trans.rollback()
				return
			if self.engine.dialect.name in ('postgres', 'postgresql'):
				c.execute('lock db_version in exclusive mode nowait;')
			elif self.engine.dialect.name == 'sqlite':
				pass
			else:
				raise AssertionError('Unhandled dialect %s' % self.engine.dialect.name)
			scripts = []
			from_to = []
			if current_rev == 0 and snapshots:
				# To generate snapshots use `pg_dump -F p --inserts` and delete the table db_version from the generation SQL
				try:
					snapshot_rev = max(rev for rev in snapshots.iterkeys() if rev <= target_rev)
				except ValueError:
					pass # no snapshot for a rev <= target_rev
				else:
					scripts.append(snapshots[snapshot_rev])
					current_rev = snapshot_rev
					from_to.append((0, snapshot_rev))
			if target_rev >= current_rev:
				scripts.extend(up_scripts[rev] for rev in range(current_rev+1, target_rev+1))
				from_to.extend((rev-1,rev) for rev in range(current_rev+1, target_rev+1))
			else:
				scripts.extend(down_scripts[rev] for rev in range(current_rev, target_rev, -1))
				from_to.extend((rev,rev-1)  for rev in range(current_rev, target_rev, -1))
		except Exception:
			trans.rollback()
			raise
		else:
			try:
				for (from_rev, to_rev), script_fn in zip(from_to, scripts):
##					print('%s%i -> %i' % (self.schema + ' ' if self.schema else '', from_rev, to_rev), file=sys.stderr, flush=True)
					logger.info('%s: %i -> %i', self.get_db_repr(), from_rev, to_rev)
					sub_trans = c.begin_nested()
					try:
						if script_fn.lower().endswith('.sql'):
							with open(script_fn, 'rb') as f:
								src = f.read()
							if src.strip():
								# allow empty scripts
##								c.execute(text(src.decode('utf8')).execution_options(no_parameters=True))
								c.execution_options(no_parameters=True).execute(src.decode('utf8'))
						else:
							m = imp.load_source('mig_script', script_fn)
							f_name = 'upgrade' if to_rev > from_rev else 'downgrade'
							try:
								migration_function = getattr(m, f_name)
							except AttributeError:
								raise AttributeError('Module %s has no function named %s' % (os.path.realpath(script_fn), f_name))

							# The migration function must take one positional argument, the connection object
							# It can accept some keyword arguments, but this is optional to guarantee backwards compatibility
							# At present, only the `schema` argument is passed when accepted
							kwargs = {}
							args, varargs, varkw, defaults = inspect.getargspec(migration_function)
							if varkw is not None or 'schema' in args:
								kwargs['schema'] = self.schema

							migration_function(c, **kwargs)
						c.execute('update %sdb_version set version = %i;' % (self.quote_ident(self.schema), to_rev))
					except Exception:
						sub_trans.rollback()
						raise
					else:
						sub_trans.commit()
				if self.reassign_to:
					c.execute('reassign owned by current_user to %s;' % self.quote(self.reassign_to))
			except KeyboardInterrupt:
				# Not sure that this fixes a strange bug (Ctrl+C when executing a script leads to inconsistent state)
				trans.rollback()
				raise
			finally:
				trans.commit()


class SPMigrationHandler(MigrationHandler):
	'''
	Works exactly like MigrationHandler but proxies :py:meth:`initialize_db` and :py:meth:`migrate` to
	a sub-process.

	This prevents interference between migration scripts and application code through SQLAlchemy's global state.
	Interference can happen when SQLAlchemy tries to resolve classes from strings (eg: `relationship('OtherClass')`).
	'''

	def __getstate__(self):
		return {
	        'version': 1,
	        'dsn': self.dsn,
	        'repository': self.repository,
	        'schema': self.schema
	    }

	def __setstate__(self, state):
		self.dsn = state['dsn']
		self.repository = state['repository']
		self.schema = state['schema']
		self.engine = create_engine(self.dsn)
		self.metadata = MetaData(self.engine)
		self.db_version = Table('db_version', self.metadata, Column('version', Integer, server_default='0', default=0), schema=self.schema)

	def run_in_subprocess(self, args):
		popen_args = [sys.executable, os.path.realpath(__file__)] + list(args)
		subprocess.check_call(popen_args)

	def initialize_db(self):
		args = [self.repository, '-d', self.dsn, '-i', '-N']
		if self.schema:
			args.extend(['-s', self.schema])
		self.run_in_subprocess(args)

	def migrate(self, target_rev=None):
		args = [self.repository, '-d', self.dsn]
		if self.schema:
			args.extend(['-s', self.schema])
		if target_rev is not None:
			args.extend(['-r', str(target_rev)])
		self.run_in_subprocess(args)


def main():
	import argparse
	argparser = argparse.ArgumentParser()
	argparser.add_argument('repository')
	argparser.add_argument('-d', '--dsn', help='If not supplied, the DSN is read from the MIG_DSN environment variable instead')
	argparser.add_argument('-i', '--init', action='store_true', help='Initializes the DB for versioning if it is not versioned')
	argparser.add_argument('-N', '--no-migration', action='store_true', help='Prevent migration scripts from being run (useful if you only want to initialize the database for version control)')
	argparser.add_argument('-r', '--revision', default=None, type=int, help='Target revision number')
	argparser.add_argument('-s', '--schema', default=None, help='Default schema')
	argparser.add_argument('-R', '--reassign-to', help='At the end of each transaction, issue the (PostgreSQL-specific) REASSIGN OWNED BY CURRENT_USER TO <NEW_OWNER>; command. This can be useful if you have to run migrations as a superuser.', metavar='NEW_OWNER')

	args = argparser.parse_args()

	logger.addHandler(logging.StreamHandler(sys.stderr))
	logger.setLevel(logging.INFO)

	if not args.dsn:
		args.dsn = os.environ.get('MIG_DSN')
		if not args.dsn:
			argparser.error('No -d/--dsn option not provided and the MIG_DSN environment variable is empty')

	mig_handler = MigrationHandler(args.repository, args.dsn, schema=args.schema, reassign_to=args.reassign_to)
	if args.init:
		mig_handler.initialize_db()
	if not args.no_migration:
		mig_handler.migrate(args.revision)

if __name__ == '__main__':
	main()
