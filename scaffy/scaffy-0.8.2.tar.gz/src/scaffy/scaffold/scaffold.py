# -*- coding: utf-8 -*-
""" Scaffold implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
import os
import sys
from datetime import datetime
from os.path import join, isdir, relpath
from zipfile import ZipFile, ZipInfo


try:
    # python 3
    from io import BytesIO
    from zipfile import BadZipFile
except ImportError:
    # python 2
    from zipfile import BadZipfile as BadZipFile
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO


from six import string_types

# local imports
from scaffy.core import const
from scaffy.core import log
from scaffy.core import fs
from scaffy.core import shell


def marker_tag(marker):
    """ Create a marker tag for the given marker name. """
    return '_PELTAK-SCAFFOLD-{}_'.format(marker.upper())


class Scaffold(object):
    """ Represents the scaffold.

    All scaffold data should be contained within the scaffold file. This is a
    wrapper class around that file. It implements creating a scaffold file from
    a source directory as well as applying the scaffold to create a project.
    """
    NAME_MARKER = marker_tag('name')

    class Invalid(RuntimeError):
        """ Invalid scaffold. """
        pass

    def __init__(self, fileobj, **scaffold_config):
        self.fileobj = fileobj or BytesIO()
        self.config = scaffold_config
        self.path = None    # Only set if loaded from file or after it's written

        self.config.setdefault('line_sep', os.linesep)
        self.config.setdefault('marked_files', [])
        self.config.setdefault('created', datetime.utcnow())
        self.config.setdefault('time_format', const.TIME_FORMAT)

        if isinstance(self.created, string_types):
            created = datetime.strptime(self.created, self.time_format)
            self.config['created'] = created

    @property
    def name(self):
        """ The scaffold name. """
        return self.config['name']

    @property
    def marked_files(self):
        """ List of marked files stored in the scaffold.

        This is always a subset of .files property.
        """
        return self.config['marked_files']

    @property
    def created(self):
        """ Datetime of when the scaffold was created. """
        return self.config['created']

    @property
    def pretty_created(self):
        """ Pretty formatted creation datetime. """
        return self.created.strftime(const.TIME_FORMAT)

    @property
    def time_format(self):
        """ Time format used for date times in the scaffold config. """
        return self.config['time_format']

    @property
    def size(self):
        """ The scaffold file size. """
        start_pos = self.fileobj.tell()

        self.fileobj.seek(0, os.SEEK_END)
        size = self.fileobj.tell()
        self.fileobj.seek(start_pos, os.SEEK_SET)

        return size

    @property
    def json_config(self):
        """ Scaffold config as JSON serializable dict. """
        conf = dict(self.config)
        conf['created'] = self.created.strftime(self.time_format)
        return conf

    @property
    def files(self):
        """ List of all files in the scaffold. """
        with ZipFile(self.fileobj) as zipfile:
            return zipfile.namelist()

    @classmethod
    def create(cls, src_dir, name, exclude, markers):
        """ Create scaffold from a source directory.

        :param str src_dir:
            Path to the source directory. The contents of the directory will
            be put into the scaffold with exception to files excluded.
        :param str name:
            The name of the new scaffold. It has to be unique in the local
            store.
        :param List[str] exclude:
            A list of patterns. All files in *src_dir* that match any of those
            patters won't be included in the created scaffold
        :param Dict[str, Union[str,List[str]] markers:
            A dictionary containing markers to put into the scaffold. Markers
            are values that are scrapped from the files content and paths during
            scaffold creation and than replaced with real values once the
            scaffold is applied.
        :return Scaffold:
            A newly created scaffold.
        """
        marked_files = []

        fileobj = BytesIO()
        with ZipFile(fileobj, 'w') as zipfile:
            i = 0
            for path, arc_path in Scaffold._iter_files(
                    src_dir, markers, exclude
            ):
                if isdir(path):
                    marked = False
                    zipfile.writestr(ZipInfo(arc_path + '/'), '')
                else:
                    content, marked = Scaffold._prepare_file(path, markers)
                    zipfile.writestr(arc_path, content)

                if marked:
                    marked_files.append(arc_path)

                i += 1
                log.info("[{:4}] Adding ^35{}", i, arc_path)

        return Scaffold(fileobj, name=name, marked_files=marked_files)

    @classmethod
    def load_from_file(cls, path):
        """ Load scaffold from file.

        :param str path:
            Path to the scaffold file.
        :return:
            A `Scaffold` instance representing the scaffold file.
        """
        with open(path, 'rb') as fp:
            fileobj = BytesIO(fp.read())

        try:
            with ZipFile(fileobj) as zipfile:
                data = zipfile.read(const.CONFIG_FILE).decode('utf-8')
                scaffold_config = json.loads(data)
        except BadZipFile as ex:
            raise Scaffold.Invalid(str(ex))

        scaffold = Scaffold(fileobj, **scaffold_config)
        scaffold.path = path

        return scaffold

    def write(self, path):
        """ Write scaffold to a file under a given path.

        :param str path:
            The path where the scaffold will be written. Must be writable.
        """
        zip_path = join(path, self.name + const.FILE_EXT)

        with ZipFile(self.fileobj, 'a') as zipfile:
            zipfile.writestr(const.CONFIG_FILE, json.dumps(self.json_config))

        with open(zip_path, 'wb') as fp:
            fp.write(self.fileobj.getvalue())

        self.path = zip_path

    def apply(self, proj_name, out_path):
        """ Apply a scaffold to create a new project.

        This will create a new directory with the content being that of the
        scaffold but with all markers replaced with real values (like project
        name).

        :param str proj_name:
            The name of the new project
        :param str out_path:
            Path to the directory where the new project will be created.
            The project folder will be created within the given path.
        """
        with ZipFile(self.fileobj) as zipfile:
            scaffold_config = json.loads(zipfile.read(const.CONFIG_FILE))

            proj_path = join(out_path, proj_name)
            os.makedirs(proj_path)

            for arc_path in zipfile.namelist():
                if arc_path == const.CONFIG_FILE:
                    continue

                file_path = join(proj_path, arc_path)

                if Scaffold.NAME_MARKER in arc_path:
                    file_path = file_path.replace(Scaffold.NAME_MARKER,
                                                  proj_name)

                content = zipfile.read(arc_path)

                if arc_path in scaffold_config['marked_files']:
                    content = content.decode('utf-8')
                    content = self._render_file(content, {
                        'name': proj_name
                    })

                    with open(file_path, 'w') as fp:
                        shell.cprint("^0[ Template ] ^0^90{}^0", file_path)
                        fp.write(content)
                else:
                    if Scaffold._is_dir(zipfile, arc_path):
                        shell.cprint("^34[    Dir   ] ^90{}^0", file_path)
                        os.mkdir(file_path)
                    else:
                        shell.cprint("^90[   File   ] ^90{}^0", file_path)
                        with open(file_path, 'wb') as fp:
                            line_sep = self.config['line_sep'].encode('utf-8')
                            fp.write(content.rstrip() + line_sep)

    @staticmethod
    def _iter_files(src_dir, markers, exclude):
        for path in fs.filtered_walk(src_dir, exclude):
            arc_path = relpath(path, src_dir)
            arc_path, _ = Scaffold._prep_line(arc_path, markers)

            yield path, arc_path

    @staticmethod
    def _prepare_file(path, markers):
        is_marked = False
        try:
            with open(path) as fp:
                lines = []
                for line in fp.readlines():
                    prepped, marked = Scaffold._prep_line(line, markers)

                    if marked:
                        is_marked = True

                    lines.append(prepped)

                return ''.join(lines), is_marked

        except UnicodeDecodeError:
            with open(path, 'rb') as fp:
                return fp.read(), False

    @staticmethod
    def _prep_line(line, markers):
        """ Scrap selected values and replace them with markers

        :param str line:
            The processed line.
        :param Dict[str, List[str]] markers:
            Markers definition. The key is the marker name and the value is the
            list of strings that will be replaced with marker of the name given
            in the key.
        :return Tuple[str, bool]:
            A tuple containing the processed line and boolean flag telling
            whether any markers were injected into the line.
        """
        prepped = line
        is_marked = False

        for marker, value in markers.items():
            if isinstance(value, string_types):
                if value in line:
                    prepped = line.replace(value, marker_tag(marker))
                    is_marked = True
            else:
                # Multiple values for marker
                for item in value:
                    if item in line:
                        prepped = line.replace(item, marker_tag(marker))
                        is_marked = True

        return prepped, is_marked

    def _render_file(self, content, values):
        """ Render a file using the given values

        :param str content:
            The file content.
        :param Dict[str,List[str]] values:
            The dictionary with marker values to put into the file.
        :return str:
            The content of the rendered file with all markers replaced with
            the provided values.
        """
        lines = []

        for line in content.split(self.config['line_sep']):
            rendered = line

            for marker, value in values.items():
                tag = marker_tag(marker)
                if tag in line:
                    rendered = rendered.replace(tag, value)

            lines.append(rendered)

        return os.linesep.join(lines).rstrip() + self.config['line_sep']

    @staticmethod
    def _is_dir(zipfile, arc_path):
        """ Check if the given archive path is a directory.

        :param zipfile.ZipFile zipfile:
            A ZipFile instance that represents the archive in question.
        :param str arc_path:
            The path to the file/dir in the archive.
        :return bool:
            True if the given *arc_path* is a directory within the *zipfile*
        """
        zip_info = zipfile.getinfo(arc_path)
        if sys.version_info >= (3, 6):
            return zip_info.is_dir()
        else:
            return zip_info.filename.endswith('/')
