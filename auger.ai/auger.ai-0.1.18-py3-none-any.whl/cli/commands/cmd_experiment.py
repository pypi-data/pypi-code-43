import click

from auger.api.experiment import Experiment
from auger.cli.utils.config import AugerConfig
from auger.cli.utils.context import pass_context
from auger.cli.utils.formatter import print_table
from auger.cli.utils.decorators import \
    error_handler, authenticated, with_dataset
from auger.api.cloud.utils.exception import AugerException



class ExperimentCmd(object):

    def __init__(self, ctx):
        self.ctx = ctx

    @error_handler
    @authenticated
    @with_dataset
    def list(self, dataset):
        count = 0
        for exp in iter(Experiment(self.ctx, dataset).list()):
            self.ctx.log(exp.get('name'))
            count += 1
        self.ctx.log('%s Experiment(s) listed' % str(count))

    @error_handler
    @authenticated
    @with_dataset
    def start(self, dataset):
        experiment_name = \
            self.ctx.get_config('auger').get('experiment/name', None)
        eperiment_name, session_id = \
            Experiment(self.ctx, dataset, experiment_name).start()
        AugerConfig(self.ctx).set_experiment(eperiment_name, session_id)

    @error_handler
    @authenticated
    @with_dataset
    def stop(self, dataset):
        name = self.ctx.get_config('auger').get('experiment/name', None)
        if name is None:
            raise AugerException('Please specify Experiment name...')
        if Experiment(self.ctx, dataset, name).stop():
            self.ctx.log('Search is stopped...')
        else:
            self.ctx.log('Search is not running. Stop is ignored.')

    @error_handler
    @authenticated
    @with_dataset
    def leaderboard(self, dataset, run_id):
        name = self.ctx.get_config('auger').get('experiment/name', None)
        if name is None:
            raise AugerException('Please specify Experiment name...')
        leaderboard, status = Experiment(
            self.ctx, dataset, name).leaderboard(run_id)
        if leaderboard is None:
            raise AugerException('No leaderboard was found...')
        print_table(self.ctx.log, leaderboard[::-1])
        messages = {
            'preprocess': 'Search is preprocessing data for traing...',
            'started': 'Search is in progress...',
            'completed': 'Search is completed.',
            'interrupted': 'Search was interrupted.'
        }
        message = messages.get(status, None)
        if message:
            self.ctx.log(message)
        else:
            self.ctx.log('Search status is %s' % status)

    @error_handler
    @authenticated
    @with_dataset
    def history(self, dataset):
        name = self.ctx.get_config('auger').get('experiment/name', None)
        if name is None:
            raise AugerException('Please specify Experiment name...')
        for exp_run in iter(Experiment(self.ctx, dataset, name).history()):
            self.ctx.log("run id: {}, start time: {}, status: {}".format(
                exp_run.get('id'),
                exp_run.get('model_settings').get('start_time'),
                exp_run.get('status')))


@click.group('experiment', short_help='Auger experiment management')
@pass_context
def command(ctx):
    """Auger experiment management"""
    ctx.setup_logger(format='')


@click.command(short_help='List Experiments for selected DataSet')
@pass_context
def list_cmd(ctx):
    """List Experiments for selected DataSet"""
    ExperimentCmd(ctx).list()


@click.command(short_help='Start Experiment')
@pass_context
def start(ctx):
    """Start Experiment.
       If Experiment is not selected, new Experiment will be created.
    """
    ExperimentCmd(ctx).start()


@click.command(short_help='Stop Experiment')
@pass_context
def stop(ctx):
    """Stop Experiment"""
    ExperimentCmd(ctx).stop()


@click.command(short_help='Show Experiment leaderboard')
@click.argument('run-id', required=False, type=click.STRING)
@pass_context
def leaderboard(ctx, run_id):
    """Show Experiment leaderboard for specified run id.
       If run id is not provided, latest experiment run
       leaderboard will be shown.
    """
    ExperimentCmd(ctx).leaderboard(run_id)

@click.command(short_help='Show Experiment history')
@pass_context
def history(ctx):
    """Show Experiment history"""
    ExperimentCmd(ctx).history()


@pass_context
def add_commands(ctx):
    command.add_command(list_cmd, name='list')
    command.add_command(start)
    command.add_command(stop)
    command.add_command(leaderboard)
    command.add_command(history)


add_commands()
