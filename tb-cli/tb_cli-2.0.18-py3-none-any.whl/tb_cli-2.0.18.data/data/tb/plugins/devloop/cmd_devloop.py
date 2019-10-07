import os
import signal
import subprocess
import sys
import threading
import time
from collections import namedtuple
from functools import partial
from os.path import isfile
from threading import Thread, Lock

import yaml
from cement import CaughtSignal
from cement import Controller
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_CREATED, \
    EVENT_TYPE_MOVED, EVENT_TYPE_MODIFIED
from watchdog.utils import platform

from tb.arguments import repository
from tb import Tb, TbError, ColoredTerminal, restore_original_env
from .util import print_local_line

if platform.is_darwin():
    # the default mapped Observer didn't allow for watching multiple times the same directory, this one works (shrug)
    from watchdog.observers.fsevents2 import FSEventsObserver2 as Observer
else:
    from watchdog.observers import Observer

NAME = 'devloop'

EXIT_BAD_CONFIG = 101
EXIT_CLEAN_FAILED = 102
EXIT_START_FAILED = 103

Command = namedtuple('Command', ['name', 'script', 'background', 'log_prefix', 'delay'])
RunCommand = namedtuple('RunCommand', ['command', 'result'])


class DevloopController(Controller):
    class Meta:
        label = NAME
        stacked_on = 'base'
        stacked_type = 'nested'
        description = 'Runs a configured devloop, watches files and run associated commands'
        arguments = repository.arguments + [
            (['--clean', '-c'],
             dict(help='Full clean before starting', action='store_true', dest='clean')),
            (['--loop', '-l'],
             dict(help='Selects the loop to start', action='store', dest='loop'))
        ]

    def start(self):
        app: Tb = self.app
        repo_name = os.path.basename(os.path.dirname(os.getcwd()))
        loop = self.app.pargs.loop

        devloop_name, devloop_config = _devloop(app, loop)

        app.log.debug(
            "Starting {} devloop for project '{}' with configuration: {}".format(
                devloop_name, repo_name,
                devloop_config))

        clean = devloop_config.get('clean') if self.app.pargs.clean else None
        if clean:
            clean_commands = _commands(clean.get('commands', []))
            if _has_background_command(clean_commands):
                raise TbError("Clean can't have background commands.", EXIT_CLEAN_FAILED)
            if _has_failed_command(_run_commands(app, clean_commands)):
                raise TbError("Exiting since project could not be cleaned.",
                              EXIT_CLEAN_FAILED)

        start_commands = _run_commands(app, _commands(
            devloop_config.get('start', {}).get('commands', [])))
        if _has_failed_command(start_commands):
            app.term.error("Exiting since devloop could not be started.")
            _stop_commands(app, start_commands)
            raise TbError("Start failed", EXIT_START_FAILED)

        event_publisher = EventPublisher()
        watchers = [_watcher(app, event_publisher, c) for c in
                    devloop_config.get('watches', [])]

        project_watcher = ProjectWatcher(app, watchers)
        project_watcher.start()

        event_watcher = EventWatcher(app, watchers, event_publisher)

        runner = CommandRunner(app, project_watcher, event_watcher)
        runner.start()

        try:
            runner.join()
        except KeyboardInterrupt:
            pass
        except CaughtSignal:
            pass
        finally:
            project_watcher.stop()
            runner.stop()
            _stop_commands(app, start_commands)
            if 'stop' in devloop_config:
                _run_commands(app, _commands(
                    devloop_config.get('stop', {}).get('commands', [])))

            os.system('reset')

    def _default(self):
        self.start()


class EventPublisher:
    listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def fire(self, event):
        for l in self.listeners:
            l.fire(event)


class Listener:
    def __init__(self, app: Tb, event_publisher, name, commands, depends_on):
        self.app = app
        self.event_publisher = event_publisher
        self.name = name
        self.commands = commands
        self.dependsOn = depends_on
        self.event_publisher.add_listener(self)

    def start(self):
        pass

    def stop(self):
        pass

    def fire(self, event):
        if event in self.dependsOn:
            self.run()

    def run(self):
        if not _has_failed_command(_run_commands(self.app, self.commands)):
            self.event_publisher.fire(self.name)


class CommandRunner:
    scheduler_delay = .5

    def __init__(self, app: Tb, project_watcher, event_watcher):
        self.app = app
        self.project_watcher = project_watcher
        self.event_watcher = event_watcher

        self.scheduler = Thread(target=self.run)
        self.scheduler.setDaemon(True)
        self._run = True

    def start(self):
        self.scheduler.start()

    def join(self):
        self.scheduler.join()

    def stop(self):
        self._run = False

    def run(self):
        while self._run:
            has_triggered_watchers = self.project_watcher.has_triggered_watchers()
            # self.log.debug("Checking for triggered watchers: {}".format(has_triggered_watchers))
            if has_triggered_watchers:
                triggered_watchers = self.project_watcher.get_triggered_watchers()
                if triggered_watchers:
                    self.run_tasks(triggered_watchers)
            time.sleep(self.scheduler_delay)

    def run_tasks(self, watchers):
        if watchers:
            self.app.log.debug("Running watchers triggered by file changes")
            for w in watchers:
                w.run()
        fired_watchers = self.event_watcher.get_fired_watchers()
        if fired_watchers:
            self.app.log.debug("Running watchers triggered by dependencies")
            for w in fired_watchers:
                w.run()


class Watcher:
    def __init__(self, app: Tb, event_publisher, name, files, commands, depends_on):
        self.app = app
        self.event_publisher = event_publisher

        self.name = name
        self.files = files
        self.commands = commands
        self.depends_on = set(depends_on)
        self.app.log.debug("Created watcher '{}' for files: {}".format(name, files))

    def matches(self, path):
        self.app.log.debug(f"abs path: {os.path.abspath(path)}")
        watched = any(os.path.abspath(path).startswith(f) for f in self.files)
        self.app.log.debug(
            "Path {} is {} a watched file for {}.".format(path, "" if watched else " NOT",
                                                          self.name))
        return watched

    def run(self):
        if not _has_failed_command(_run_commands(self.app, self.commands)):
            self.event_publisher.fire(self.name)


class EventWatcher:
    def __init__(self, app: Tb, watchers, event_publisher):
        self.app = app
        self.watchers = watchers
        self.event_publisher = event_publisher
        self.event_publisher.add_listener(self)

        self.events = set()

    def fire(self, event):
        self.events.add(event)

    def get_fired_watchers(self):
        fired_events = self.events
        self.events = set()
        return [w for w in self.watchers if w.depends_on & fired_events]


class ProjectWatcher(PatternMatchingEventHandler):
    dirty_wait = 50
    exclude_suffixes = {"___", "~"}

    def __init__(self, app: Tb, watchers,
                 include_patterns=None,
                 exclude_patterns=None):
        if include_patterns is None:
            include_patterns = ['*']
        if exclude_patterns is None:
            exclude_patterns = ['*___', '*~', '*/.git/*', '*/.idea/*', '*/.gradle/*',
                                '*/build/*',
                                '*/.tb/*', "*.pyc", "*/__pycache__/*"]
        print(f"Watching {include_patterns} and excluding {exclude_patterns}")
        PatternMatchingEventHandler.__init__(self, patterns=include_patterns,
                                             ignore_patterns=exclude_patterns)

        self.app = app
        self.watchers = watchers

        self.dirty_time = None

        self.observer = Observer()

        self.triggered_watchers_lock = Lock()
        self.triggered_watchers = set()

    def on_any_event(self, event):
        if event.is_directory:
            # we don't care about directory (only) changes
            return

        if event.event_type not in (
        EVENT_TYPE_MOVED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED):
            return

        # check the destination path if the file was moved
        path = event.dest_path if event.event_type == EVENT_TYPE_MOVED else event.src_path

        matched_watchers = [w for w in self.watchers if w.matches(path)]

        if matched_watchers:  # we have things to do, pending
            with self.triggered_watchers_lock:
                self.triggered_watchers.update(matched_watchers)
            self.dirty_time = int(round(time.time() * 1000))

    def has_triggered_watchers(self):
        return self.dirty_time and int(
            round(time.time() * 1000)) >= self.dirty_wait + self.dirty_time

    def get_triggered_watchers(self):
        with self.triggered_watchers_lock:
            triggered_watchers = self.triggered_watchers
            self.triggered_watchers = set()
        self.dirty_time = None
        return triggered_watchers

    def start(self):
        self.observer.schedule(self, '.', recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


def _init_devloop_config(term: ColoredTerminal):
    path = "tb.yml"
    data = {}
    if isfile(path):
        with open(path, 'r') as f:
            try:
                data = yaml.load(f)
            except yaml.YAMLError as exc:
                term.error(exc)

    config = {
        "start": {
            "commands": [
                'echo "start service here"',
                {
                    "name": "watch logs",
                    "script": 'echo "Tailing logs here"',
                    "background": True
                }
            ]
        },
        "stop": {
            "commands": ['echo "Stop service here"']
        },
        "clean": {
            "commands": ['echo "Clean service files here"']
        },
        "watches": [
            {
                "name": "source file watcher",
                "commands": ['echo "Do something when the file changed here"'],
                "files": ["."]
            }
        ]
    }
    data.setdefault("devloop", {})["default"] = config

    with open(path, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

    return config


def _devloop(app: Tb, loop=None):
    devloop_configs = app.config.get_dict().get('devloop', {})

    if loop:
        name = loop
        app.log.debug("Using explicit loop configuration: {}".format(name))
        devloop_config = devloop_configs.get(name)
        if not devloop_config:
            raise TbError("Could not find '{}' devloop configuration!".format(name),
                          EXIT_BAD_CONFIG)
    else:
        name = 'default'
        app.log.debug("Looking up default loop configuration")
        devloop_config = devloop_configs.get(name)

    if not devloop_config:
        name, devloop_config = _detect_devloop(devloop_configs)
        app.log.debug(
            "No default loop configured, detected configuration {}: {}".format(name,
                                                                               devloop_config))

    if not devloop_config:
        if app.term.yesno("No devloop configuration found.  Do you want to initialize?"):
            _init_devloop_config(app.term)
            app.term.success(
                "File 'tb.yml' written with an example devloop.  Modify it and rerun")
            sys.exit(0)

    if not devloop_config:
        raise TbError("Could not find devloop configuration!", EXIT_BAD_CONFIG)

    inherit = devloop_config.get('inherit')
    if inherit:
        inherit_config = devloop_configs.get(inherit)
        if not inherit_config:
            raise TbError(
                "Devloop {} inherits {}, but the latter could not be found!".format(name,
                                                                                    inherit),
                EXIT_BAD_CONFIG)
        else:
            inherit_config.update(devloop_config)
            devloop_config = inherit_config

    return name, devloop_config


def _detect_devloop(devloop_configs):
    name = ''
    if os.path.isfile('pom.xml'):
        name += 'maven'
    elif os.path.isfile('build.gradle'):
        name += 'gradle'
    else:
        return name, None

    if os.path.isfile('docker-compose.yml'):
        name += '-' + 'docker'

    return name, devloop_configs.get(name)


def _watcher(app: Tb, event_publisher, config):
    return Watcher(app=app,
                   event_publisher=event_publisher,
                   name=config.get('name'),
                   files=_absolute_path(config.get('files', [])),
                   commands=_commands(config.get('commands', [])),
                   depends_on=config.get('dependsOn', []))


def _absolute_path(paths):
    return [os.path.abspath(p) for p in paths]


def _run_commands(app: Tb, commands, run_all=True):
    result = None
    run_commands = []
    for command in commands:
        if result is None or (isinstance(result, int) and (
                (result == 0 and run_all) or (result > 0 and not run_all))):
            run_command = _run_command(app, command)
            result = run_command.result
        else:
            app.log.debug("Not running command: {}".format(result))
            run_command = RunCommand(command, None)
        run_commands.append(run_command)

    _kill_on_control_c(result)

    app.log.debug("Ran commands: {}".format(run_commands))
    return run_commands


killing = False


def _kill_on_control_c(result):
    global killing
    if result == 130 and not killing:
        killing = True
        print("Control-C detected, shutting down")
        os.kill(os.getpid(), signal.SIGTERM)


def _run_command(app: Tb, command):
    app.log.debug("Running command: {}".format(command))
    if command.background:
        print_fn = partial(print_local_line, app.term)
        if command.log_prefix:
            def print_fn(line):
                print_local_line(app.term, '{0: <10}{1}'.format(command.log_prefix, line))

        process = BackgroundProcess(NAME, command.script.split(), print_fn, command.delay)
        process.start()
        return RunCommand(command, None)
    else:
        if ' || ' in command.script:
            commands = command.script.split(' || ')
            run_commands = _run_commands(app, _commands(commands), False)
            result = None
            for run_command in run_commands:
                if result != 0:
                    result = run_command.result
            return RunCommand(command, result)
        else:
            result = exec_cmd(NAME, *(command.script.split()))
            return RunCommand(command, result)


def _stop_commands(app: Tb, commands):
    for command in commands:
        if isinstance(command.result, BackgroundProcess):
            app.log.debug("Terminating {}".format(command))
            command.result.terminate()


def _commands(commands):
    return [_command(c) for c in commands]


def _command(command):
    if isinstance(command, str):
        return Command(name=None, script=command, background=False, delay=0,
                       log_prefix='')
    else:
        return Command(name=command.get("name"), script=command.get("script"),
                       background=command.get("background"),
                       delay=command.get("delay"), log_prefix=command.get("log_prefix"))


def _has_background_command(commands):
    return any(c.background for c in commands)


def _has_failed_command(run_commands):
    return any(isinstance(c.result, int) and c.result > 0 for c in run_commands)


class BackgroundProcess(threading.Thread):
    def __init__(self, context, cmds, output_printer, delay=0):
        threading.Thread.__init__(self)
        self.context = context
        self.cmds = cmds
        self.delay = delay
        self.process = None
        self.output_printer = output_printer

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.terminate()

    def run(self):
        if self.delay:
            time.sleep(self.delay)
        if self.output_printer:
            for line in run_process(*self.cmds):
                self.output_printer(line.decode('utf-8'))
        else:
            self.process = subprocess.Popen(self.cmds, env=restore_original_env())
            self.process.wait()

    def terminate(self):
        if self.process:
            self.process.terminate()


def run_process(*exe, **kwargs):
    """
    Run a process and return an iterator of the line output
    """
    term = ColoredTerminal(theme={})
    term.command("", " ".join(exe))

    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         env=restore_original_env(), **kwargs)
    while True:
        retcode = p.poll()  # returns None while subprocess is running
        line = p.stdout.readline()
        yield line
        if retcode is not None:
            # always kill in case the process returns 0
            _kill_on_control_c(130)
            break


def exec_cmd(context, *cmds, **kwargs):
    term = ColoredTerminal(theme={})
    term.command(context, " ".join(cmds))
    return subprocess.call(cmds,
                           env=restore_original_env(),
                           **kwargs)
