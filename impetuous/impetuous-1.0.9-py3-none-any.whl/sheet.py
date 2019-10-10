""" TODO rename this to models.py or something boring like that
"""

import datetime
import logging
import math
import os
import random
import re
import warnings
from uuid import UUID

import attr
import dateutil.parser
import yaml

from impetuous.serialization import UUID_PATTERN

logger = logging.getLogger(__name__)

utctz = datetime.timezone.utc
localtz = dateutil.tz.tzlocal()

not_loaded = type('not_loaded', (object,), {})()


def utcnow():
    if 'IM_NOW' in os.environ:
        dt = dateutil.parser.parse(os.environ['IM_NOW'])
        if dt.tzinfo is None:
            dt.replace(tzinfo=localtz)
        return dt.astimezone(datetime.timezone.utc)
    else:
        return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


class EntryNotFoundError(RuntimeError):  # TODO remove this
    pass


class ValidationError(Exception):

    def __init__(self, message, params=None):
        if params is None:
            params = {}
            super().__init__(message)
        else:
            super().__init__(message.format(**params))
        self.message = message
        self.params = params


@attr.s(cmp=True)
class Entry(object):
    id = attr.ib(default=None)
    rev = attr.ib(default=None)
    text = attr.ib(default='')
    comment = attr.ib(default='')
    start = attr.ib(default=None)
    end = attr.ib(default=None)
    submissions = attr.ib(default=attr.Factory(dict))

    @end.validator
    @start.validator
    def has_timezone(self, attribute, value):
        if value is None or value is not_loaded:
            pass
        elif value.tzinfo is None:
            raise ValueError("%s requires a timezone aware datetime, not %r" % (attribute.name, value))

    @classmethod
    def joker(cls, id=not_loaded, rev=not_loaded, text=not_loaded, comment=not_loaded, start=not_loaded, end=not_loaded, submissions=not_loaded):
        return cls(id=id, rev=rev, text=text, comment=comment, start=start, end=end, submissions=submissions)

    @classmethod
    def new(cls):
        return cls(id=None, rev=None, text='', comment='', start=None, end=None, submissions={})

    def __contains__(self, other):
        return (
                (other.end is not None and other.start <= self.start < other.end)
                or (self.end is not None and self.start <= other.start < self.end)
                )

    @property
    def duration(self):
        assert self.start is not not_loaded
        assert self.end is not not_loaded
        if self.end is None:
            end = utcnow()
        else:
            end = self.end
        return end - self.start

    @property
    def duration_in_minutes(self):
        """ Return duration in minutes as integer. Rounds randomly. :)
        """
        minutes_spent = self.duration.total_seconds() / 60
        if minutes_spent % 1 <= random.random():
            return math.floor(minutes_spent)
        else:
            return math.ceil(minutes_spent)


@attr.s(cmp=True)
class Submission(object):
    id = attr.ib(default=None)
    rev = attr.ib(default=None)
    entry = attr.ib(default=None)
    ext = attr.ib(default=None)
    key = attr.ib(default=None)
    result = attr.ib(default=None)

    @classmethod
    def joker(cls, id=not_loaded, rev=not_loaded, entry=not_loaded, ext=not_loaded, key=not_loaded, result=not_loaded):
        return cls(id=id, rev=rev, entry=entry, ext=ext, key=key, result=result)

    @property
    def entry_index(self):
        assert self.ext is not not_loaded  # assert double negation
        assert self.key is not not_loaded  # is not not readable...
        return self.ext, self.key


def load_cli_entry_from_yaml(loader, node):
    args = loader.construct_mapping(node, deep=True)
    if 'covert' in args:
        del args['covert']
    args['text'] = args.pop('task')
    for key in ('start', 'end'):
        if key in args:
            args[key] = args[key].astimezone(utctz)
    if 'submissions' in args:
        args['submissions'] = {s.entry_index: s for s in args['submissions']}
    return Entry(**args)


# I think this stuff is used by im_edit, should probably live in impetuous/cli/
# somewhere TODO

def load_cli_submission_from_yaml(loader, node):
    args = loader.construct_mapping(node, deep=True)
    return Submission(**args)


# http://stackoverflow.com/a/13295663
def timestamp_constructor(loader, node):
    return dateutil.parser.parse(node.value)


def load_UUID(loader, node):
    return UUID(loader.construct_scalar(node))


class cli_yaml_Loader(yaml.SafeLoader):
    pass

cli_yaml_Loader.add_constructor(u'tag:yaml.org,2002:timestamp', timestamp_constructor)
cli_yaml_Loader.add_constructor('!uuid', load_UUID)
cli_yaml_Loader.add_constructor(u'!entry', load_cli_entry_from_yaml)
cli_yaml_Loader.add_constructor(u'!submission', load_cli_submission_from_yaml)
cli_yaml_Loader.add_implicit_resolver('!uuid', UUID_PATTERN, None)


def dump_cli_entry_as_yaml(dumper, entry):
    as_dict = {
        'id': entry.id,
        'rev': entry.rev,
        'start': entry.start.astimezone(localtz),
        'task': entry.text,
    }
    if entry.end is not None:
        as_dict['end'] = entry.end.astimezone(localtz)
    if entry.submissions:
        as_dict['submissions'] = list(entry.submissions.values())
    if entry.comment:
        as_dict['comment'] = entry.comment
    return dumper.represent_mapping(u'!entry', as_dict)


def dump_cli_submission_as_yaml(dumper, result):
    return dumper.represent_mapping(u'!submission', attr.asdict(result))


def dump_UUID(dumper, uuid):
    return dumper.represent_scalar('!uuid', str(uuid))


class cli_yaml_Dumper(yaml.SafeDumper):
    pass

cli_yaml_Dumper.add_representer(UUID, dump_UUID)
cli_yaml_Dumper.add_representer(Entry, dump_cli_entry_as_yaml)
cli_yaml_Dumper.add_representer(Submission, dump_cli_submission_as_yaml)
