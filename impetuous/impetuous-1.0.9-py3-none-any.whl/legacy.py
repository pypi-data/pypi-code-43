# TODO move this to impetuous/cli/...
from datetime import datetime, timedelta
import re

import attr
import yaml
try:
    from yaml import CSafeLoader as yaml_Loader
except ImportError:
    from yaml import SafeLoader as yaml_Loader

from impetuous.sheet import Entry, Submission, timestamp_constructor, utctz


JIRA_PATTERN = re.compile(r'\w+-\d+')


def format_comments(comments):
    if len(comments) == 1:
        return comments[0]
    else:
        return '\n'.join('- %s' % comment for comment in comments)


def load_entry(loader, node):
    source = loader.construct_mapping(node, deep=True)
    if 'covert' in source:
        del source['covert']
    source['text'] = source.pop('task')
    for key in ('start', 'end'):
        if key in source:
            source[key] = source[key].astimezone(utctz)
    if 'comments' in source:
        source['comment'] = format_comments(source.pop('comments'))
    if 'post_result' in source:
        # Very old JIRA only ...
        data = source.pop('post_result')
        # The issue id is not in the post result. Take it from the entry text.
        key = JIRA_PATTERN.match(source['text']).group()
        submission = Submission(ext='jira', key=key, result=data)
        source['submissions'] = {submission.entry_index: submission}

    if 'post_results' in source:
        submissions = []
        for ext, things in source.pop('post_results').items():
            for key, data in things.items():
                submissions.append(Submission(ext=ext, key=key, result=data))
        source['submissions'] = {s.entry_index: s for s in submissions}
    return Entry(**source)


def load_sheet(loader, node):
    mapping = loader.construct_mapping(node, deep=True)
    if 'units' in mapping:
        return mapping['units']


class v0_Loader(yaml_Loader):
    pass

v0_Loader.add_constructor(u'tag:yaml.org,2002:timestamp', timestamp_constructor)
v0_Loader.add_constructor(u'!unit', load_entry)
v0_Loader.add_constructor(u'!sheet', load_sheet)
v0_Loader.add_constructor(u'tag:yaml.org,2002:python/object:impetuous.sheet.Sheet', load_sheet)


def load_legacy_sheet(doc):
    """
    I don't know what these parameters are, doc is probably a string or
    bytes or readable file object.

    Can return anything, but should return a list of entries ...
    """
    return yaml.load(doc, Loader=v0_Loader)
