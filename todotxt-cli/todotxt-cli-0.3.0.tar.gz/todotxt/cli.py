#!/usr/bin/env python
# coding: utf-8
from logging import Formatter, Handler, getLogger, NOTSET, INFO, DEBUG, WARNING
import configparser
from os import mkdir
from os.path import join, isdir, isfile
from functools import update_wrapper
import sys

import six

if six.PY2:
    input = raw_input

import click
from click.types import DateTime, ParamType

from todotxt.task import TasksFile, Task, TasksWebDav
from todotxt.util import now, validPriority, validContext, validProject, validDue, addday, month, week, validRepeat

level2color = {
    0 : 'black',
    10 : 'blue',
    20 : 'green',
    30 : 'yellow',
    40 : 'red',
    50 : 'magenta',
}

class PriorityParamType(ParamType):
    name = 'priority'

    def convert(self, value, param, ctx):
        if validPriority(value):
            return value
        self.fail('invalid priority: %s is not in A-Z' % value)

    def __repr__(self):
        return 'PRIORITY'

class RepeatParamType(ParamType):
    name = 'repeat'

    def convert(self, value, param, ctx):
        if value == '0':
            return value
        if validRepeat('repeat:%s' % value):
            return value
        self.fail('invalid repeat: %s is not format ?d, ?w, ?y' % value)

    def __repr__(self):
        return 'PRIORITY'

class TaskParamType(ParamType):
    name = 'task'

    def convert(self, value, param, ctx):
        try:
            task = ctx.obj['tasks'].get_id(int(value))
            if task != None:
                return task
        except:
            pass
        self.fail('invalid task with id %s is not found' % value)
        
    def __repr__(self):
        return 'TASK'


def printTaskOneLine(task, conf={}):
    if task.done:
        click.echo(click.style('[X]', fg='green'), nl=False)
    else:
        if task.due != None:
            if task.due == now() and conf.get('Todo','ColorNow', fallback=None):
                click.echo(click.style('[ ]', fg=conf.get('Todo','ColorNow')), nl=False)
            elif task.due > now() and conf.get('Todo','ColorNext', fallback=None):
                click.echo(click.style('[ ]', fg=conf.get('Todo','ColorNext')), nl=False)
            elif now() > task.due and conf.get('Todo','ColorEarlier', fallback=None):
                click.echo(click.style('[ ]', fg=conf.get('Todo','ColorNow')), nl=False)
            else:
                click.echo('[ ]', nl=False)
        else:
            click.echo('[ ]', nl=False)
    fmt_id = ' %%%ss ' % len(conf.get('Todo','CountTask', fallback='100'))
    click.echo(fmt_id % task.id, nl=False)
    if task.priority:
        click.echo('(%s) ' % task.priority, nl=False)
    for txt in task.txt.split():
        if validDue(txt):
            if conf.get('Todo','ViewDue', fallback='true') == 'true':
                click.echo(click.style(txt, fg=conf.get('Todo', 'ColorDue', fallback='red')), nl=False)
        elif validContext(txt):
            click.echo(click.style(txt, fg=conf.get('Todo', 'ColorContext', fallback='blue')), nl=False)
        elif validProject(txt):
            click.echo(click.style(txt, fg=conf.get('Todo', 'ColorProject', fallback='magenta')), nl=False)
        else:
            click.echo(txt, nl=False)            
        click.echo(' ', nl=False)
    click.echo('', nl=True)

class ClickHandler(Handler):

    def __init__(self, level=NOTSET):
        Handler.__init__(self, level)
    
    def emit(self, record):
        click.echo(click.style(self.format(record), fg= level2color.get(record.levelno, 'white')))

# logger
logger = getLogger("todotxt")
ch = ClickHandler()
ch.setLevel(DEBUG)
formatter = Formatter("%(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

def normalize_args(f):
    def new_func(*args, **kwargs):
        if isinstance(args[0], click.core.Context):
            kwargs['tasks'] = args[0].obj['tasks']
        return f(*args, **kwargs)
    return update_wrapper(new_func, f)

@click.group(invoke_without_command=True)
@click.option('-vv', '--verbose', is_flag=True)
@click.option('-c', '--conf', type=click.File('r'))
@click.version_option('0.1.0')
@click.pass_context
def cli(ctx, verbose, conf):
    if verbose:
        logger.setLevel(DEBUG)
    if not isdir(click.get_app_dir('todocli')):
        logger.debug('create app dir %s' % click.get_app_dir('todocli'))
        mkdir(click.get_app_dir('todocli'))
    
    config = configparser.ConfigParser()
    config['Todo'] = {}
    if not conf:
        conf = join(click.get_app_dir('todocli'), 'todocli.conf')
        if isfile(conf):
            logger.debug('upload conf from %s' % conf)
            config.read(conf)
        else:
            logger.debug('not conf found in %s' % conf)
    else:
        logger.debug("upload conf from --conf")
        config.read_string(conf.read())
    if not verbose:
        logger.setLevel(config.getint('Todo','Log', fallback=40))

    if config.get('Todo','Url', fallback=None) == None:
        path = config.get('Todo','Path', fallback=join(click.get_app_dir("todocli"), 'todo.txt'))
        logger.debug("Your todo path is %s" % path)
        ctx.obj['tasks'] = TasksFile(path)
        if isfile(path):
            ctx.obj['tasks'].open()
    else:
        url = config.get('Todo','Url')
        user = config.get('Todo','User', fallback=None)
        password = config.get('Todo','Password', fallback=None)
        logger.debug("Your url todo is %s with %s/%s" % (url, user, password))
        ctx.obj['tasks'] = TasksWebDav(url, user, password)
        ctx.obj['tasks'].open()
 

    ctx.obj['config'] = config
    
    if ctx.invoked_subcommand is None:
        prettyls(ctx=ctx, tasks=ctx.obj['tasks'])

@cli.command()
@click.argument('txt', nargs=-1)
@click.pass_context
@normalize_args
def add(ctx, tasks, txt):
    """
    add task
    """
    task = Task(' '.join(txt))
    task.created = now()
    tasks.append(task)
    tasks.save()
    printTaskOneLine(task, ctx.obj['config'])


@cli.command()
@click.argument('task', nargs=1, type=TaskParamType())
@click.argument('txt', nargs=-1)
@click.pass_context
@normalize_args
def txt(ctx, tasks, task, txt):
    """
    change txt of task and save due
    """
    due = task.due
    for word in task.txt.split():
        task.remove(word)
    task.txt = ' '.join(txt)
    task.due = due
    task.completed = now()
    tasks.save()
    printTaskOneLine(task, ctx.obj['config'])



@cli.command()
@click.argument('task', nargs=1, type=TaskParamType())
@click.pass_context
@normalize_args
def rm(ctx, tasks, task):
    """
    remove task
    """
    tasks.remove(task)
    tasks.save()

@cli.command()
@click.option('--today', is_flag=True)
@click.option('--current-week', is_flag=True)
@click.option('--current-month', is_flag=True)
@click.option('--days', type=int)
@click.option('--with-done', is_flag=True)
@click.option('--only-done', is_flag=True)
@click.option('--multi-line', is_flag=True)
@click.argument('filter', nargs=-1)
@click.pass_context
@normalize_args
def ls(ctx, tasks, today, current_week, current_month, days, with_done, only_done, multi_line, filter):
    """
    list of tasks
    """
    due = None
    completed = None
    created = None
    priority = None
    id = None
    filter = list(filter)
    if current_month:
        due = "..%s" % month()
    if current_week:
        due = "..%s" % week()
    if today:
        due = "..%s" % now()
    if days:
        due = "%s..%s" % (now(), addday(now(),days)) 
    if with_done:
        done = None
    else:
        done = False
    if only_done:
        done = True
    for fil in [ fil for fil in filter if fil.startswith('created:')]:
        created = fil.split(":")[1]
        filter.remove(fil)
    for fil in [ fil for fil in filter if fil.startswith('completed:')]:
        completed = fil.split(":")[1]
        filter.remove(fil)
    for fil in [ fil for fil in filter if fil.startswith('due:')]:
        due = fil.split(":")[1]
        filter.remove(fil)
    for fil in [ fil for fil in filter if fil.startswith('priority:')]:
        priority = fil.split(":")[1]
        filter.remove(fil)
    for fil in [ fil for fil in filter if fil.startswith('id:')]:
        id = fil.split(":")[1]
        filter.remove(fil)
    if len(filter) > 0:
        txt = ' '.join(filter)
    else:
        txt=None
    lst = tasks.filter(id=id, priority=priority, due=due, done=done, completed=completed, created=created, txt=txt)
    lst.sort() 
    ctx.obj['config'].set('Todo', 'ViewDue', 'true')
    ctx.obj['config'].set('Todo', 'CountTask', (len(lst) and str(max([task.id for task in lst])) or '0'))
    for task in lst:
        printTaskOneLine(task, ctx.obj['config'])

def prettyls(ctx, tasks):
    ctx.obj['config'].set('Todo', 'ViewDue', 'false')
    ctx.obj['config'].set('Todo', 'CountTask', (len(tasks) and str(max([task.id for task in tasks])) or '0'))
    lst = tasks.filter(done=False)
    lst.sort()
    earlier = tasks.filter(done=False, due="..%s" % addday(now(), -1))
    earlier.sort()
    if len(earlier):
        ctx.obj['config'].set('Todo', 'ViewDue', 'true')
        print('Earlier:') 
        for task in earlier:
            click.echo('\t', nl=False)
            printTaskOneLine(task, ctx.obj['config'])
        click.echo('', nl=True)
    today = tasks.filter(done=False, due= now())
    today.sort()
    if len(today):
        ctx.obj['config'].set('Todo', 'ViewDue', 'false')
        print('Today:') 
        for task in today:
            click.echo('\t', nl=False)
            printTaskOneLine(task, ctx.obj['config'])
        click.echo('', nl=True)

    start = addday(now(),1)
    end = week(now())
    weekcurrent = tasks.filter(done=False, due= "%s..%s" % (start, end))
    weekcurrent.sort()
    if len(weekcurrent):
        ctx.obj['config'].set('Todo', 'ViewDue', 'true')
        print('Week:') 
        for task in weekcurrent:
            click.echo('\t', nl=False)
            printTaskOneLine(task, ctx.obj['config'])
        click.echo('', nl=True)

    start = addday(start, 1)
    end =   addday(week(start))  
    nextweek = tasks.filter(done=False, due= "%s..%s" % (start, end))
    nextweek.sort()
    if len(nextweek):
        ctx.obj['config'].set('Todo', 'ViewDue', 'true')
        print('Next week:') 
        for task in nextweek:
            click.echo('\t', nl=False)
            printTaskOneLine(task, ctx.obj['config'])
        click.echo('', nl=True)

    start = addday(start, 1)
    next = tasks.filter(done=False, due= "%s.." % start)
    next.sort()
    if len(next):
        ctx.obj['config'].set('Todo', 'ViewDue', 'true')
        print('Next:') 
        for task in next:
            click.echo('\t', nl=False)
            printTaskOneLine(task, ctx.obj['config'])
        click.echo('', nl=True)


    unplanned = [ task for task in tasks.filter(done=False) if task.due == None]
    unplanned.sort()
    if len(unplanned):
        print('Unplanned:') 
        for task in unplanned:
            click.echo('\t', nl=False)
            printTaskOneLine(task, ctx.obj['config'])
 
@cli.command()
@click.argument('task', nargs=1, type=TaskParamType())
@click.argument('words', nargs=-1)
@click.pass_context
@normalize_args
def append(ctx, tasks, task, words):
    """
    append task
    """
    task.append(' '.join(words))
    task.completed = now()
    tasks.save()
    printTaskOneLine(task, ctx.obj['config'])


@cli.command()
@click.argument('task', nargs=1, type=TaskParamType())
@click.argument('words', nargs=-1)
@click.pass_context
@normalize_args
def cancel(ctx, tasks, task, words):
    """
    cancel words in task
    """
    for word in words:
        task.remove(word)
    task.completed = now()
    tasks.save()
    printTaskOneLine(task, ctx.obj['config'])


@cli.command()
@click.argument('task', nargs=1, type=TaskParamType())
@click.pass_context
@normalize_args
def done(ctx, tasks, task):
    """
    done task
    """
    new = str(task)
    task.done = True
    task.completed = now()
    printTaskOneLine(task, ctx.obj['config'])
    if task.repeat:
        check = input('do you want repeat task for %s [Y/n]' % task.next_repeat)
        if check == "" or check in ('y','Y'):
            new = Task(new)
            new.due = new.next_repeat
            new.created = now()
            new.completed = now()
            tasks.append(new)
            printTaskOneLine(new, ctx.obj['config'])
    tasks.save()

@cli.command()
@click.argument('task', nargs=1, type=TaskParamType())
@click.pass_context
@normalize_args
def undone(ctx, tasks, task):
    """
    undone task
    """
    task.done = False
    task.completed = now()
    tasks.save()
    printTaskOneLine(task, ctx.obj['config'])


@cli.command()
@click.argument('task', nargs=1, type=TaskParamType())
@click.argument('due', nargs=1, type=DateTime(["%Y-%m-%d",]))
@click.pass_context
@normalize_args
def due(ctx, tasks, task, due):
    """
    change due of task
    """
    task.due = due.strftime("%Y-%m-%d")
    task.completed = now()
    tasks.save()
    printTaskOneLine(task, ctx.obj['config'])


@cli.command()
@click.argument('task', nargs=1, type=TaskParamType())
@click.argument('prior', nargs=1, type=PriorityParamType())
@click.pass_context
@normalize_args
def priority(ctx, tasks, task, prior):
    """
    change priority of task
    """
    task.priority = prior
    task.completed = now()
    tasks.save()
    printTaskOneLine(task, ctx.obj['config'])

@cli.command()
@click.option('--days', type=int, default=10)
@click.pass_context
@normalize_args
def prune(ctx, tasks, days):
    """
    remove task if done and today - x days >= completed
    x is 10 by default
    """
    max_completed = "..%s" % addday(now(),(-1*days) -1) 
    for task in tasks.filter(done=True, completed=max_completed):
        tasks.remove(task)
    tasks.save()



@cli.command()
@click.argument('task', nargs=1, type=TaskParamType())
@click.argument('repeat', nargs=1, type=RepeatParamType())
@click.pass_context
@normalize_args
def repeat(ctx, tasks, task, repeat):
    """
    repeat add param in task for manage repeat
    """
    task.repeat = None
    if validRepeat("repeat:%s" % repeat):
        task.repeat = repeat
    printTaskOneLine(task, ctx.obj['config'])
    tasks.save()

if __name__ == "__main__":
    cli(obj={})