"""Froglabs command line client."""

import os
import pprint
import signal
import traceback

import click
import pandas as pd
import xarray as xr
try:
    import matplotlib
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        # Disable GUI if not available
        matplotlib.use('agg')  # noqa
        import matplotlib.pyplot as plt
except ImportError:
    matplotlib = None

from froglabs import clients
from froglabs import exceptions
from froglabs import utils


__copyright__ = 'Copyright 2019 Froglabs, Inc.'


# Some command aliases for backward compatibility.
# Should be deprecated shortly.
class BackwardCompatibilityGroup(click.Group):

    def get_command(self, ctx, name):
        if name == 'get_weather':
            name = 'query'
        return click.Group.get_command(self, ctx, name)


@click.group(cls=BackwardCompatibilityGroup)
@click.option('--host', type=str)
@click.option('--token', type=str, help='Access token')
@click.pass_context
def cli(ctx, host, token):
    ctx.ensure_object(dict)
    ctx.obj['host'] = host
    ctx.obj['token'] = token
    ctx.obj['client'] = clients.Client(host=host, token=token)


@cli.command('create_dataset')
@click.argument('location', type=str)
@click.argument('variables', type=str)
@click.argument('input_file', type=click.Path(exists=True))
@click.pass_context
def create_dataset(ctx, location, variables, input_file):
    """Create dataset for the given location and variables from the
    given time-series file.
    """
    client = ctx.obj['client']
    variables = variables.split(',')
    response = client.create_dataset(location, variables, input_file)
    pprint.pprint(response)


@cli.command('create_training_task')
@click.argument('model')
@click.argument('dataset')
@click.option('--num-epochs', type=int, default=128)
@click.option('--batch-size', type=int, default=16)
@click.option('--window-size', type=int)
@click.option('--num-workers', type=int, default=0)
@click.option('--seed', type=int)
@click.pass_context
def create_training_task(ctx, model, dataset, num_epochs, batch_size,
                         window_size, num_workers, seed):
    """Create training task."""
    client = ctx.obj['client']
    response = client.create_training_task(
        model, dataset,
        num_epochs=num_epochs,
        batch_size=batch_size,
        window_size=window_size,
        num_workers=num_workers,
        seed=seed
    )
    pprint.pprint(response)


@cli.command('get_variables')
@click.pass_context
def get_variables(ctx):
    """Fetch supported variables."""
    client = ctx.obj['client']
    variables = client.get_variables()
    click.echo(variables.to_string())


@cli.command()
@click.argument('output_file', type=str)
# Address or bounding box
@click.argument('location', type=str)
# Comma-separated list of vars or * to select them all
@click.argument('variables', type=str, metavar='VARIABLES', required=False)
@click.argument('start_time', type=str, metavar='START_TIME', required=False)
@click.argument('end_time', type=str, metavar='END_TIME', required=False)
@click.option('--format', type=str, default='netcdf',
              help='Output format (default: netCDF)')
@click.option('--spatial_resolution', type=float, default=None)
@click.option('--space_aggregation_method', type=str, default=None)
@click.option('--time_aggregation_step', type=str, default=None)
@click.option('--time_aggregation_method', type=str, default=None)
@click.pass_context
def query(ctx, location, variables, start_time, end_time, output_file, format,
          spatial_resolution, space_aggregation_method,
          time_aggregation_step, time_aggregation_method):
    """Query weather for the given LOCATION, time period [START_TIME, END_TIME]
    and VARIABLES.

    Receives weather dataset in netCDF format and writes the result to the
    OUTPUT_FILE.

    The LOCATION can be provided in multiple ways:

    * An address, e.g. "Atlantic Ocean", "Pacific Ocean", "Black Sea".

    * A geographical point in latitude and longitude coordinate,
      measured in degrees.

    * A geographical bounding box, defined by its southwest and northeast
      points in latitude and longitude, e.g.
      "40.90888,27.4426426,46.627499,41.7775873" (Black Sea).

    Note, in case the negative number goes first, just quote the coordinates
    and add leading space, e.g.
    " -77.2844418,128.652984,59.0336872,-67.1321908" (Pacific Ocean).

    The VARIABLES is a comma-separated list of variable names,
    e.g. "sst,sss". Complete list of variables can be retrieved with
    help of get_variables command.
    """
    client = ctx.obj['client']
    now = pd.Timestamp.now('UTC')
    if format not in ('netcdf',):
        raise ValueError('Not support format: %r' % format)

    if start_time is None:
        start_time = now
    if end_time is None:
        end_time = now + pd.to_timedelta('1D')

    try:
        start_time = pd.to_datetime(start_time)
        end_time = pd.to_datetime(end_time)
    except ValueError:
        ctx.fail('Cannot parse start/end time.')
    click.echo('Time delta: %s' % (end_time - start_time,))

    if variables is not None:
        variables = variables.split(',')

    client.query(location, variables, start_time, end_time,
                 spatial_resolution=spatial_resolution,
                 space_aggregation_method=space_aggregation_method,
                 time_aggregation_step=time_aggregation_step,
                 time_aggregation_method=time_aggregation_method,
                 output=output_file, progress_bar=True)
    nbytes = os.path.getsize(output_file)
    click.echo('%r saved (%s)' % (output_file, utils.sizeof_fmt(nbytes)))


@cli.command('plot')
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(), required=True)
@click.argument('variable', type=str)
@click.option('--show', default=False, type=bool,
              help='Display the result image')
@click.option('--levels', default=None,
              help=('An optional list of levels to specify the boundaries of '
                    'the discrete colormap'))
@click.option('--draw-gridlines', default=False, type=bool,
              help='Whether to draw gridlines')
@click.option('--central-longitude', default=0, type=float)
@click.option('--central-latitude', default=0, type=float)
@click.option('--projection', default=None,
              help='PlateCarree or Orthographic')
@click.pass_context
def plot(ctx, show, variable, input_file, levels, draw_gridlines,
         central_longitude, central_latitude, projection, output_file,
         time=0):
    """Plot weather results."""
    client = ctx.obj['client']

    if levels is not None:
        levels = list(map(int, levels.split(',')))
        if len(levels) == 1:
            levels = levels[0]

    try:
        variables = client.get_variables()
        info = variables.set_index('short_name').loc[variable]
        ds = xr.load_dataset(input_file)
    except KeyError:
        click.echo('Invalid variable: %r' % variable)
        ctx.abort()
    da = ds[variable]

    # TODO(d2rk): should be done by the weather service.
    da.attrs['units'] = info['unit']

    # TODO(d2rk): do something with time and variable selection.
    da = da.isel(time=0).sortby(['longitude'])

    if projection is None:
        da.plot(levels=levels, robust=True)

        plt.title(info['name'])
        plt.tight_layout()
    else:
        try:
            import cartopy.crs as ccrs
        except ImportError:
            ccrs = None

        if not ccrs:
            click.echo('Command is not available. Please install cartopy.')
            ctx.abort()

        # See available projections:
        # https://scitools.org.uk/cartopy/docs/latest/crs/projections.html
        if projection == 'PlateCarree':
            projection = ccrs.PlateCarree()
        elif projection == 'Orthographic':
            projection = ccrs.Orthographic(central_longitude, central_latitude)
        else:
            click.echo('Unknown projection: %r' % projection, err=True)
            ctx.abort()
        ax = plt.axes(projection=projection)
        transform = ccrs.PlateCarree()
        da.plot.contourf(levels=levels, ax=ax, transform=transform)
        ax.set_global()
        ax.coastlines()
        if draw_gridlines:
            ax.gridlines()

        plt.title(info['name'])

    plt.savefig(output_file)

    if show:
        plt.show()


def main():
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo('Interrupted by user')
        return 128 + signal.SIGINT
    except exceptions.Error as e:
        click.echo(str(e), err=True)
        return 255
    except Exception:
        click.echo(traceback.format_exc(), err=True)
        return 255


# Disable plot command if matplotlib is not installed.
if matplotlib is None:
    del cli.commands['plot']
