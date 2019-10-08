# -*- coding: utf-8 -*-
"""Модуль архиватора базы данных MongoDB."""

import os
import subprocess
import logging

from msbackup.backend_base import Base as BaseBackend


logger = logging.getLogger('msbackup')


def get_backend_kwargs(params):
    """Подготовка параметров для режима 'mongodb'."""
    kwargs = BaseBackend.get_common_backend_kwargs(params)
    BaseBackend.get_param(params, kwargs, 'archive_name')
    BaseBackend.get_param(params, kwargs, 'uri')
    BaseBackend.get_param(params, kwargs, 'host')
    BaseBackend.get_param(params, kwargs, 'port')
    BaseBackend.get_param(params, kwargs, 'username')
    BaseBackend.get_param(params, kwargs, 'password')
    BaseBackend.get_param(params, kwargs, 'auth_db')
    BaseBackend.get_param(params, kwargs, 'auth_mechanism')
    BaseBackend.get_param(params, kwargs, 'db')
    BaseBackend.get_param(params, kwargs, 'collection')
    BaseBackend.get_param(params, kwargs, 'parallel')
    BaseBackend.get_param(params, kwargs, 'mongodump_cmd')
    return kwargs


class MongoDB(BaseBackend):
    """Архиватор базы данных MongoDB."""

    SECTION = 'Backend-MongoDB'

    @classmethod
    def make_subparser(cls, subparsers):
        """Добавление раздела параметров командной строки для архиватора."""
        parser = subparsers.add_parser('mongodb')
        parser.set_defaults(get_backend_kwargs=get_backend_kwargs)
        parser.add_argument(
            '-n', '--name', dest='archive_name', metavar='NAME',
            help='Name of archive file without extension.',
        )
        parser.add_argument(
            '-u', '--uri', metavar='URI',
            help='URI connection string to connect to the MongoDB deployment.',
        )
        parser.add_argument(
            '-H', '--host', metavar='HOST',
            help='Resolvable hostname for the mongod to which to connect.',
        )
        parser.add_argument(
            '-p', '--port', metavar='PORT',
            help=('TCP port on which the MongoDB instance listens '
                  'for client connections.'),
        )
        parser.add_argument(
            '-U', '--username', metavar='USERNAME',
            help=('Username with which to authenticate to a MongoDB database '
                  'that uses authentication.'),
        )
        parser.add_argument(
            '-P', '--password', metavar='PASSWORD',
            help=('Password with which to authenticate to a MongoDB database '
                  'that uses authentication.'),
        )
        parser.add_argument(
            '-a', '--auth-db', metavar='AUTH_DB',
            help=('Authentication database where the specified USERNAME '
                  'has been created.'),
        )
        parser.add_argument(
            '-m', '--auth-mechanism', metavar='AUTH_MECHANISM',
            help=('Authentication mechanism the mongodump instance uses '
                  'to authenticate to the mongod or mongos.'),
        )
        parser.add_argument(
            '-d', '--db', metavar='DATABASE',
            help=('Database to backup (you cannot specify both '
                  'DATABASE and URI).'),
        )
        parser.add_argument(
            '-c', '--collection', metavar='COLLECTION',
            help='Collection to backup (all collections by default).',
        )
        parser.add_argument(
            '-j', '--parallel', type=int, metavar='NUMBER',
            help=('Number of collections mongodump should export in parallel '
                  '(default: 4).'),
        )
        parser.add_argument(
            '-C', '--mongodump-cmd', metavar='MONGODUMP_COMMAND',
            help='Command to run mongodump util.',
        )

    def __init__(self, config, *args, **kwargs):
        """Конструктор."""
        super().__init__(config, *args, **kwargs)
        # archive_name
        a_name = kwargs.get('archive_name') or config.get(
            section=self.SECTION, option='ARCHIVE_NAME', fallback=None)
        self.archive_name = os.path.basename(a_name) if a_name else None
        # --- mongodump_cmd
        cmd = [kwargs.get('mongodump_cmd') or config.get(
            section=self.SECTION,
            option='MONGODUMP_COMMAND',
            fallback='/usr/bin/mongodump',
        ), '--quiet', '--oplog', '--gzip']
        # uri
        uri = kwargs.get('uri') or config.get(
            section=self.SECTION, option='URI', fallback=None)
        if uri:
            cmd.append('--uri=%s' % uri)
        # host
        host = kwargs.get('host') or config.get(
            section=self.SECTION, option='HOST', fallback=None)
        if host:
            cmd.append('--host=%s' % host)
        # port
        port = kwargs.get('port') or config.get(
            section=self.SECTION, option='PORT', fallback=None)
        if port:
            cmd.append('--port=%s' % port)
        # username
        username = kwargs.get('username') or config.get(
            section=self.SECTION, option='USERNAME', fallback=None)
        if username:
            cmd.append('--username=%s' % username)
        # password
        password = kwargs.get('password') or config.get(
            section=self.SECTION, option='PASSWORD', fallback=None)
        if password:
            cmd.append('--password=%s' % password)
        # auth_db
        auth_db = kwargs.get('auth_db') or config.get(
            section=self.SECTION, option='AUTH_DATABASE', fallback=None)
        if auth_db:
            cmd.append('--authenticationDatabase=%s' % auth_db)
        # auth_mechanism
        auth_mechanism = kwargs.get('auth_mechanism') or config.get(
            section=self.SECTION, option='AUTH_MECHANISM', fallback=None)
        if auth_mechanism:
            cmd.append('--authenticationMechanism=%s' % auth_mechanism)
        # db
        db = kwargs.get('db') or config.get(
            section=self.SECTION, option='DATABASE', fallback=None)
        if db:
            cmd.append('--db=%s' % db)
        # collection
        collection = kwargs.get('collection') or config.get(
            section=self.SECTION, option='COLLECTION', fallback=None)
        if collection:
            cmd.append('--collection=%s' % collection)
        # parallel
        parallel = kwargs.get('parallel') or config.getint(
            section=self.SECTION, option='PARALLEL', fallback=0)
        if parallel:
            cmd.append('--numParallelCollections=%d' % parallel)
        # exclude
        if self.exclude is not None:
            for exclude in self.exclude:
                cmd.append('--excludeCollection=%s' % exclude)
        # -
        self.mongodump_cmd = cmd
        # ---
        suffix = '.gz'
        if self.encryptor is not None:
            suffix += self.encryptor.suffix
        self.suffix = suffix
        self.tmp_dir = None

    def _backup(self, sources=None, **kwargs):
        """
        Архивация баз данных MongoDB.

        :param source: Список источников для архивации.
        :type source: [str]
        :return: Количество ошибок.
        :rtype: int
        """
        name = kwargs.get('archive_name', self.archive_name)
        if name is None:
            name = os.uname().nodename
        output = self.outpath(name)
        try:
            self.archive(source=sources, output=output)
        except subprocess.CalledProcessError as ex:
            logger.error(str(ex))
            return 1
        return 0

    def _archive(self, source, output=None, **kwargs):
        """
        Упаковка списка источников в файл архива.

        :param source: Список источников для архивации.
        :type source: [str]
        :param output: Путь к файлу архива.
        :type output: str
        :return: Процесс упаковки файлов.
        :rtype: subprocess.Popen
        """
        params = self.mongodump_cmd.copy()
        logger.debug('Dump MongoDB database to "%s".', output)
        if output is None:
            params.append('--archive')
            return subprocess.Popen(
                params,
                stdout=subprocess.PIPE,
                stderr=self.stream_err,
            )
        params.append('--archive=%s' % output)
        subprocess.check_call(
            params,
            stdout=subprocess.DEVNULL,
            stderr=self.stream_err,
        )
