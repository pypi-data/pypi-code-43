import click
from auger.api.dataset import DataSet
from auger.cli.utils.config import AugerConfig
from auger.cli.utils.context import pass_context
from auger.cli.utils.decorators import \
    error_handler, authenticated, with_project


class DataSetCmd(object):

    def __init__(self, ctx):
        self.ctx = ctx

    @error_handler
    @authenticated
    @with_project(autocreate=False)
    def list(self, project):
        count = 0
        selected = self.ctx.get_config('auger').get('dataset', None)
        for dataset in iter(DataSet(self.ctx, project).list()):
            self.ctx.log(
                ('[%s] ' % ('x' if selected == dataset.get('name') else ' ')) +
                dataset.get('name')
            )
            count += 1
        self.ctx.log('%s DataSet(s) listed' % str(count))

    @error_handler
    @authenticated
    @with_project(autocreate=True)
    def create(self, project, source):
        if source is None:
            source = self.ctx.get_config('config').get('source', None)
        dataset = DataSet(self.ctx, project).create(source)
        AugerConfig(self.ctx).set_data_set(dataset.name, source)
        self.ctx.log('Created DataSet %s' % dataset.name)

    @error_handler
    @authenticated
    @with_project(autocreate=False)
    def delete(self, project, name):
        if name is None:
            name = self.ctx.get_config('auger').get('dataset', None)
        DataSet(self.ctx, project, name).delete()
        if name == self.ctx.get_config('auger').get('dataset', None):
            AugerConfig(self.ctx).set_data_set(None).set_experiment(None)
        self.ctx.log('Deleted dataset %s' % name)

    @error_handler
    def select(self, name):
        old_name = self.ctx.get_config('auger').get('dataset', None)
        if name != old_name:
            AugerConfig(self.ctx).set_data_set(name, '').set_experiment(None)
        self.ctx.log('Selected DataSet %s' % name)

    @error_handler
    @authenticated
    @with_project(autocreate=False)
    def download(self, project, name, path_to_download):
        if name is None:
            name = self.ctx.get_config('auger').get('dataset', None)
        file_name = DataSet(self.ctx, project, name).download(path_to_download)
        self.ctx.log('Downloaded dataset %s to %s' % (name, file_name))


@click.group('dataset', short_help='Auger Cloud dataset(s) management')
@pass_context
def command(ctx):
    """Auger Cloud data sets management"""
    ctx.setup_logger(format='')


@click.command(short_help='List data sets on Auger Cloud')
@pass_context
def list_cmd(ctx):
    """List Auger remote datasets"""
    DataSetCmd(ctx).list()


@click.command(short_help='Create data set on the Auger Cloud')
@click.argument('source', required=False, type=click.STRING)
@pass_context
def create(ctx, source):
    """Create data set on the Auger Cloud.
       If source is not specified, auger.yaml/source
       will be used instead.
    """
    DataSetCmd(ctx).create(source)


@click.command(short_help='Delete data set on the Auger Cloud')
@click.argument('name', required=False, type=click.STRING)
@pass_context
def delete(ctx, name):
    """Delete data set on the Auger Cloud
       If name is not specified, auger.yaml/dataset
       will be used instead.
    """
    DataSetCmd(ctx).delete(name)


@click.command(short_help='Select Data Set')
@click.argument('name', required=True, type=click.STRING)
@pass_context
def select(ctx, name):
    """Select data set.
       Name will be set in auger.yaml/dataset
    """
    DataSetCmd(ctx).select(name)

@click.command(short_help='Downloads source data form Data Set on the Auger Cloud')
@click.argument('path_to_download', required=True, type=click.STRING)
@click.option('--dataset', '-ds', type=click.STRING, required=False,
    help='Data Set name to download.')
@pass_context
def download(ctx, dataset, path_to_download):
    """Downloads source data form Data Set on the Auger Cloud.
       If Data Set name is not specified, auger.yaml/dataset
       will be used instead.
    """
    DataSetCmd(ctx).download(dataset, path_to_download)


@pass_context
def add_commands(ctx):
    command.add_command(list_cmd, name='list')
    command.add_command(create)
    command.add_command(delete)
    command.add_command(select)
    command.add_command(download)


add_commands()
