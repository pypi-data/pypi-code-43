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

'''TaskWarrior utilities'''

import shlex
import functools
import subprocess
from collections import OrderedDict, deque
import attr

from twc.task import Task
from twc.utils import eprint
from twc.locale import tr


class IndexedOrderedDict:
    def __init__(self, iterable):
        self._od = OrderedDict()
        self._indices = {}

        for i, (key, val) in enumerate(iterable):
            self._od[key] = val
            self._indices.setdefault(key, i)

    def data(self):
        return self._od

    def index(self, key):
        return self._indices[key]

    def get(self, key, default=None):
        return self._od.get(key, default)

    def __getitem__(self, key):
        return self._od[key]

    def __delitem__(self, key):
        del self._od[key]
        del self._indices[key]

    def __len__(self):
        return len(self._od)


@attr.s
class TWProcess:
    stdout = attr.ib()
    stderr = attr.ib()
    retcode = attr.ib()
    args = attr.ib()

    @classmethod
    def execute(cls, tw, args):
        stdout, stderr, retcode = tw.execute_command(
            args,
            return_all=True,
            allow_failure=False)
        return cls(stdout, stderr, retcode, args)

    @classmethod
    def execute_no_capture(cls, args):
        '''Executes raw task command, without tasklib, but also without
        capturing stdout and stderr.'''
        cmd = ['task'] + args
        ep = subprocess.run(cmd)
        return cls(None, None, ep.returncode, args)

    @property
    def successful(self):
        return self.retcode == 0

    @property
    def stderr_no_overrides(self):
        '''Returns stderr without informations about tasklib's configuration
        overrides which, hopefully, should give us bare failure reason.'''
        forbidden_starts = ('TASKRC override', 'Configuration override')
        stderr = []
        for msg in self.stderr:
            if not any(msg.startswith(st) for st in forbidden_starts):
                stderr.append(msg)
        return stderr

    def verified_out(self):
        '''Gracefully handles errors: reports an error and returns an empty list
        instead of the one created from stdout.'''
        if self.report_failure():
            return []
        return self.stdout

    def report_failure(self):
        if not self.successful:
            eprint(tr('Command failed: {}'.format(' '.join(self.args))))
            return True
        return False


class TaskComparer:
    '''Class which can be used as a key in all Python sort methods for sorting
    TaskWarrior lists of task dictionaries. It compares tasks by applying a
    complex TaskWarrior-compatible sort conditions.'''
    def __init__(self, task, cmp):
        self.task = task
        self.cmp = cmp

    def __lt__(self, other):
        for attrname, rev in self.cmp:
            sp = self.task.t[attrname]
            op = other.task.t[attrname]

            if sp is None and op is None:
                continue
            if sp is None:
                return True ^ rev
            if op is None:
                return False ^ rev
            if sp == op:
                continue
            return (sp < op) ^ rev

        # we're here because all checked attributes are equal
        return False


def _process_sort_string(sort_string):
    '''Returns a list of tuples: (sort condition, reverse sort)'''
    cmp = []
    for attrname in sort_string.split(','):
        attrname = attrname.strip()
        rev = False

        if attrname.endswith('+'):
            attrname = attrname[:-1]
        elif attrname.endswith('-'):
            attrname = attrname[:-1]
            rev = True

        cmp.append((attrname, rev))
    return cmp


def to_filter(flt):
    if isinstance(flt, list):
        return [t['uuid'] for t in flt]
    if isinstance(flt, Task):
        return [flt['uuid']]
    if isinstance(flt, str):
        return [flt]
    return []


def execute_command(tw, subcommand, args=None, flt=None):
    full_cmd = to_filter(flt)
    full_cmd.append(subcommand)

    if args:
        if isinstance(args, str):
            full_cmd.extend(shlex.split(args, posix=False))
        else:
            full_cmd.extend(args)

    return TWProcess.execute(tw, full_cmd)


def edit_tasks(flt, taskrc):
    '''Runs task edit for given filter, which results in TaskWarrior starting
    text editor for filtered tasks. This is a separate command because
    tasklib's execute_command() eats stdout of running command.'''
    args = ['rc:{}'.format(taskrc)] + to_filter(flt) + ['edit']
    return TWProcess.execute_no_capture(args)


def filter_tasks(filter_string, tw):
    '''Returns a list of tasks filtered by a given TW-compatible string'''
    if filter_string:
        tasks = tw.tasks.filter(filter_string)
    else:
        tasks = tw.tasks.all()

    return [Task(t) for t in tasks]


def sort_tasks(tasks, sort_string):
    '''Sorts a list of tasks (in-place) according to a complex TW-compatible
    sort string.'''
    if not sort_string:
        return

    cmp = _process_sort_string(sort_string)
    comparer = functools.partial(TaskComparer, cmp=cmp)
    tasks.sort(key=comparer)


def group_tasks(tasks):
    '''Groups tasks by creating parent-child relationship. This allows creating
    subtasks even if TaskWarrior doesn't natively supports that.

    Tasks are grouped by their `depends` field: parent tasks depend on
    children. Children are stable: their original relative order is
    preserved.'''
    grouped = IndexedOrderedDict([(task['uuid'], task) for task in tasks])

    def index(uuid):
        try:
            return grouped.index(uuid)
        except KeyError:
            return len(grouped)

    for task in tasks:
        uuidgen = (dt['uuid'] for dt in task.t['depends'])
        uuids = sorted(uuidgen, key=index)
        for uuid in uuids:
            dep = grouped.get(uuid)
            if dep:
                task.add_child(dep)
                del grouped[uuid]

    return grouped.data()


def dfs(tasks):
    '''Depth-first-search walk through tasks grouped by group_tasks()'''
    stack = deque(tasks)
    while stack:
        task = stack.popleft()
        yield task
        stack.extendleft(reversed(task.children))
