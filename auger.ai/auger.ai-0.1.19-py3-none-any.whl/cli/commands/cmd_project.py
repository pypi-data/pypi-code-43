import click

from auger.api.project import Project
from auger.cli.utils.config import AugerConfig
from auger.cli.utils.context import pass_context
from auger.api.cloud.utils.exception import AugerException
from auger.cli.utils.decorators import error_handler, authenticated


class ProjectCmd(object):

    def __init__(self, ctx):
        self.ctx = ctx

    @error_handler
    @authenticated
    def list(self):
        count = 0
        for project in iter(Project(self.ctx).list()):
            self.ctx.log(project.get('name'))
            count += 1
        self.ctx.log('%s Project(s) listed' % str(count))

    @error_handler
    @authenticated
    def create(self, name):
        old_name, name, project = self._setup_op(name, False)
        project.create()
        if name != old_name:
            self._set_project_config(name)
        self.ctx.log('Created Project %s' % name)

    @error_handler
    @authenticated
    def delete(self, name):
        old_name, name, project = self._setup_op(name)
        project.delete()
        if name == old_name:
            self._set_project_config(None)
        self.ctx.log('Deleted Project %s' % name)

    @error_handler
    @authenticated
    def start(self, name):
        old_name, name, project = self._setup_op(name)
        if not project.is_running():
            self.ctx.log('Starting Project...')
            project.start()
            self.ctx.log('Started Project %s' % name)
        else:
            self.ctx.log('Project is already running...')

    @error_handler
    @authenticated
    def stop(self, name):
        old_name, name, project = self._setup_op(name)
        if project.is_running():
            self.ctx.log('Stopping Project...')
            project.stop()
            self.ctx.log('Stopped Project %s' % name)
        else:
            self.ctx.log('Project is not running...')

    @error_handler
    @authenticated
    def select(self, name):
        old_name, name, project = self._setup_op(name, False)
        if name != old_name:
            self._set_project_config(name)
        self.ctx.log('Selected Project %s' % name)

    def _set_project_config(self, name):
        AugerConfig(self.ctx).\
            set_project(name).\
            set_data_set(None).\
            set_experiment(None)

    def _setup_op(self, name, verify_project=True):
        old_name = self.ctx.get_config('config').get('name', None)
        if name is None:
            name = old_name
        if name is None:
            raise AugerException('Please specify Project name...')

        project = Project(self.ctx, name)

        if verify_project and not project.is_exists:
            raise AugerException('Project %s doesn\'t exists...' % name)

        return old_name, name, project

@click.group('project', short_help='Auger Cloud Projects management')
@pass_context
def command(ctx):
    """Auger Cloud Project(s) management"""
    ctx.setup_logger(format='')

@click.command(short_help='List Projects')
@pass_context
def list_cmd(ctx):
    """List Projects"""
    ProjectCmd(ctx).list()

@click.command(short_help='Create Project')
@click.argument('name', required=False, type=click.STRING)
@pass_context
def create(ctx, name):
    """Create Project"""
    ProjectCmd(ctx).create(name)

@click.command(short_help='Delete Project')
@click.argument('name', required=False, type=click.STRING)
@pass_context
def delete(ctx, name):
    """Delete Project"""
    ProjectCmd(ctx).delete(name)


@click.command(short_help='Start Project')
@click.argument('name', required=False, type=click.STRING)
@pass_context
def start(ctx, name):
    """Start Project.
       If name is not specified will start Project set in auger.yaml/name
    """
    ProjectCmd(ctx).start(name)


@click.command(short_help='Stop Project')
@click.argument('name', required=False, type=click.STRING)
@pass_context
def stop(ctx, name):
    """Stop Project.
       If name is not specified will stop Project set in auger.yaml/name
    """
    ProjectCmd(ctx).stop(name)


@click.command(short_help='Select Project')
@click.argument('name', required=True, type=click.STRING)
@pass_context
def select(ctx, name):
    """Select Project.
       Name will be set in auger.yaml/name
    """
    ProjectCmd(ctx).select(name)


@pass_context
def add_commands(ctx):
    command.add_command(list_cmd, name='list')
    command.add_command(create)
    command.add_command(delete)
    command.add_command(select)
    command.add_command(start)
    command.add_command(stop)


add_commands()
