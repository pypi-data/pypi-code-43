from subprocess import Popen, PIPE
from os import path
import click
from pyfiglet import Figlet
from .messages import FILE_NOT_FOUND_TEMPLATE, ALGOMAX, STOP_MESSAGE, ALGORITHM_JOB_START
from .user_schedule_data import UserScheduleData
from .scheduler import Scheduler
from algomax_common.terminal import FontColor


def do_algomax(filename: str, config: str, params: str, mode: str):
    """
    initiate and run scheduler
    :param filename: the user algorithm file i.e. algorithm.py
    :param config: broker configuration file i.e. config.json
    :param params: the user algorithm parameters file i.e. params.json
    :param mode: the scheduler configuration file i.e. mode.json
    :return:
    """
    schedule_data = UserScheduleData(mode)
    scheduler = Scheduler(schedule_data, algorithm_job, filename, config, params)
    scheduler.start()


def algorithm_job(filename: str, config: str, params: str):
    """
    this method runs the user algorithm codes
    :param filename: the user algorithm file i.e. algorithm.py
    :param config: broker configuration file i.e. config.json
    :param params: the user algorithm parameters file i.e. params.json
    """

    click.echo(FontColor.bold(ALGORITHM_JOB_START.format(Scheduler.count).center(100, '*')))
    process = Popen('python {0} {1} {2}'.format(filename, config, params), stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    process.wait()

    if stdout:
        click.echo(FontColor.info(' Output '.center(50, '-')))
        click.echo(stdout)
        click.echo(FontColor.info('-'.center(50, '-')))

    if stderr:
        click.echo(FontColor.failed(' Error '.center(50, '-')))
        click.echo(stderr)
        click.echo(FontColor.failed('-'.center(50, '-')))

    Scheduler.count += 1
    click.echo(FontColor.bold('*'.center(100, '*')))


@click.command()
@click.argument('filename')
@click.argument('config')
@click.option('-p', help='your algorithm config filename')
@click.option('-m', help='schedule filename')
def algomax(filename: str, config: str, p: str, m: str):
    """
    cli entry-point for algomax
    :param filename: the user algorithm file i.e. algorithm.py
    :param config: broker configuration file i.e. config.json
    :param p: the user algorithm parameter file i.e. params.json
    :param m: the scheduler configuration file i.e. mode.json
    """
    figlet = Figlet(font='big')
    click.echo(FontColor.bold(figlet.renderText(ALGOMAX)))
    click.echo(STOP_MESSAGE)

    if not path.exists(filename):
        click.echo(FontColor.failed(FILE_NOT_FOUND_TEMPLATE.format(filename)))
    elif not path.exists(config):
        click.echo(FontColor.failed(FILE_NOT_FOUND_TEMPLATE.format(config)))
    elif p is not None and not path.exists(p):
        click.echo(FontColor.failed(FILE_NOT_FOUND_TEMPLATE.format(p)))
    elif m is not None and not path.exists(m):
        click.echo(FontColor.failed(FILE_NOT_FOUND_TEMPLATE.format(m)))
    else:
        do_algomax(filename, config, p, m)


if __name__ == '__main__':
    algomax()
