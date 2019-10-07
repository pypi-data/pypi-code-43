import subprocess

from cement import App, TestApp
from cement.utils import shell

from .job_execution import restore_original_env
from .config import ConfigManager
from .term import ColoredTerminal


def set_default_env(app: 'Tb'):
    app.config_manager = ConfigManager(app.config)
    app.src_dir = app.config.get_dict()['tb'].get('src_dir')

    theme = app.config.get_dict()['tb'].get('theme', {})

    app.term = ColoredTerminal(theme=theme)


class Tb(App):
    """Team B CLI primary application."""

    class Meta:
        label = 'tb'

    config_manager: ConfigManager = None
    term: ColoredTerminal = None
    src_dir: str = None

    @property
    def people(self):
        return self.config_manager.people

    @property
    def teams(self):
        return self.config_manager.teams

    @property
    def repositories(self):
        return self.config_manager.repositories

    @property
    def environments(self):
        return self.config_manager.environments

    @property
    def stages(self):
        return self.config_manager.stages

    def cmd(self, context: str, *cmd, **kwargs):
        self.term.command(context, " ".join(cmd))

        ret = shell.cmd(" ".join(cmd), False, env=restore_original_env(kwargs), **kwargs)
        return ret

    def cmd_callable(self, context: str, *cmd, **kwargs):
        self.term.command(context, " ".join(cmd))
        return _call, cmd, kwargs

    def captured_cmd(self, context: str, *cmd, **kwargs):
        self.term.command(context, " ".join(cmd))
        stdout, stderr, ret = shell.cmd(" ".join(cmd), True, env=restore_original_env(kwargs), **kwargs)

        return stdout, stderr, ret

    def streamed_cmd(self, context: str, *cmd, **kwargs):
        self.term.command(context, " ".join(cmd))

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             env=restore_original_env(kwargs),
                             **kwargs)
        return _read_lines(p.stdout), _read_lines(p.stderr), p.returncode


def _read_lines(std):
    while True:
        line = std.readline()
        if line != '':
            # the real code does filtering here
            yield line
        else:
            break


def _call(cmd, kwargs):
    return shell.cmd(" ".join(cmd), False, env=restore_original_env(), **kwargs)


class TbTest(Tb, TestApp):
    """A sub-class of Tb that is better suited for testing."""

    class Meta:
        label = 'tb'
