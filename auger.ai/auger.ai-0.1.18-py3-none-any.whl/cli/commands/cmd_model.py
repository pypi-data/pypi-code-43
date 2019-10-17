import click

from auger.api.model import Model
from auger.cli.utils.context import pass_context
from auger.cli.utils.decorators import \
    error_handler, authenticated, with_project


class ModelCmd(object):

    def __init__(self, ctx):
        self.ctx = ctx

    @error_handler
    @authenticated
    @with_project(autocreate=False)
    def deploy(self, project, model_id, locally):
        Model(self.ctx, project).deploy(model_id, locally)

    @error_handler
    @authenticated
    @with_project(autocreate=False)
    def predict(self, project, filename, model_id, threshold, locally):
        Model(self.ctx, project).predict(filename, model_id, threshold, locally)


@click.group('model', short_help='Auger model management')
@pass_context
def command(ctx):
    """Auger model management"""
    ctx.setup_logger(format='')


@click.command('deploy', short_help='Deploy trained model.')
@click.argument('model-id', required=True, type=click.STRING)
@click.option('--locally', is_flag=True, default=False,
    help='Download and deploy trained model locally.')
@pass_context
def deploy(ctx, model_id, locally):
    """Deploy trained model."""
    ModelCmd(ctx).deploy(model_id, locally)

@click.command('predict', short_help='Predict with deployed model.')
@click.argument('filename', required=True, type=click.STRING)
@click.option('--threshold', '-t', default=None, type=float,
    help='Threshold.')
@click.option('--model-id', '-m', type=click.STRING, required=True,
    help='Deployed model id.')
@click.option('--locally', is_flag=True, default=False,
    help='Predict locally using Docker image to run model.')
@pass_context
def predict(ctx, filename, model_id, threshold, locally):
    """Predict with deployed model."""
    ModelCmd(ctx).predict(filename, model_id, threshold, locally)


@pass_context
def add_commands(ctx):
    command.add_command(deploy)
    command.add_command(predict)


add_commands()
