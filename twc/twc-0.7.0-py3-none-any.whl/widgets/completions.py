# Copyright (C) 2019 Michał Góral.
#
# This file is part of TWC
#
# TWC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TWC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TWC. If not, see <http://www.gnu.org/licenses/>.

import itertools

from twc.twutils import execute_command


def keywords():
    times = [
        'ascension', 'easter', 'eastermonday', 'eocw', 'eoww', 'eom', 'eoq',
        'eow', 'eoy', 'fri', 'goodfriday', 'later', 'midsommar',
        'midsommarafton', 'mon', 'pentecost', 'sat', 'socw',
        'som', 'someday', 'soq', 'sow', 'soww', 'soy', 'sun', 'thu',
        'today', 'tomorrow', 'tue', 'wed'
    ]

    completions = [
        'depends:', 'description:', 'due:', 'end:', 'entry:',
        'limit:', 'priority:', 'project:', 'recur:', 'scheduled:',
        'start:', 'status:', 'until:', 'wait:']

    for spec in ['due', 'until', 'wait']:
        completions.extend(['{}:{}'.format(spec, time) for time in times])

    return completions


def udas(tw):
    completions = []
    # add UDAs
    for uda in execute_command(tw, '_udas').verified_out():
        completions.append('{}:'.format(uda))
    return completions


def tags(tw):
    completions = set()
    for comma_sep_tags in execute_command(tw, '_unique', 'tags').verified_out():
        taglist = comma_sep_tags.split(',')
        for tag in taglist:
            completions.add('+{}'.format(tag))
    return completions


def annotations(tasks):
    if not isinstance(tasks, list):
        tasks = [tasks]

    get_annotations = (task.t['annotations'] for task in tasks)
    return set(ann['description']
               for ann in itertools.chain.from_iterable(get_annotations))


def task_add(tw):
    completions = keywords()
    completions.extend(udas(tw))
    completions.extend(tags(tw))
    completions.sort()
    return completions


def task_modify(tasks, tw):
    if not isinstance(tasks, list):
        tasks = [tasks]

    completions = keywords()
    completions.extend(udas(tw))

    get_tags = (task.t['tags'] for task in tasks)
    all_tasks_tags = set(itertools.chain.from_iterable(get_tags))

    completions.extend('-{}'.format(tag) for tag in all_tasks_tags)
    completions.extend(tags(tw))
    completions.extend(task.t['description'] for task in tasks)
    completions.sort()
    return completions
