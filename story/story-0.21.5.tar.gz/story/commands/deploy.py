# -*- coding: utf-8 -*-
import sys
import time

from blindspin import spinner

import click

import emoji

from . import test
from .. import cli, options
from ..api import Apps, Config, Releases


@cli.cli.command()
@click.option('--message', help='Deployment message')
@click.option('--hard', is_flag=True,
              help='Pull the latest service images on deploy')
@options.app(allow_option=False)
def deploy(app, message, hard):
    """Deploy your app to Storyscript Cloud."""
    cli.user()

    payload = test.compile_app(app, False)  # Also adds a spinner.

    if payload is None:
        sys.exit(1)  # Error already printed by compile_app.

    num_stories = len(payload['stories'])
    echo_with_tick(f"Compiled {num_stories} {pluralise('story', num_stories)}")
    click.echo()

    click.echo(click.style(f'Deploying app {app}... ', bold=True), nl=False)

    with spinner():
        config = Config.get(app)
        release = Releases.create(config, payload, app, message, hard)

    url = f'https://{app}.storyscriptapp.com/'
    click.echo()
    echo_with_tick(f'Version {release["id"]} of your app'
                   ' has been queued for deployment.')
    click.echo()

    click.echo(click.style('Waiting for deployment to complete…  ',
                           bold=True), nl=False)
    with spinner():
        if Apps.maintenance(app, maintenance=None):
            click.echo()
            click.echo()
            click.echo(
                'Your app is in maintenance mode.\n'
                'Run the following to turn off it off:'
            )
            cli.print_command('story maintenance off')
            click.echo()
            click.echo(
                'Once maintenance mode is turned off, '
                'your app will be deployed immediately.'
            )
            return

        state = 'QUEUED'
        while state in ['DEPLOYING', 'QUEUED']:
            state = Releases.get(app)[0]['state']
            time.sleep(0.5)

    click.echo()
    if state == 'DEPLOYED':
        echo_with_tick(f'Configured '
                       f"{num_stories} {pluralise('story', num_stories)}")
        for s in payload['stories']:
            click.echo('  - ' + s)

        num_services = len(payload['services'])
        echo_with_tick(f'Deployed '
                       f"{num_services} {pluralise('service', num_services)}")
        for s in payload['services']:
            click.echo('  - ' + s)

        echo_with_tick(f'Created ingress route')
        echo_with_tick('Configured logging')
        echo_with_tick('Configured health checks')
        echo_with_tick('Deployment successful!')
        click.echo()
        click.echo('To see your app\'s logs, please run:\n  story logs -f')
        click.echo()
        click.echo(
            f'If your Story responds to HTTP requests, please visit:\n  {url}'
        )
    elif state == 'FAILED':
        click.echo(
            click.style('X', fg='red') + ' Deployment failed!', err=True
        )
        click.echo(
            'Please use the following command to view your app\'s logs:',
            err=True,
        )
        cli.print_command('story logs')
    elif state == 'TEMP_DEPLOYMENT_FAILURE':
        click.echo(
            click.style('X', fg='red') + ' Deployment failed!', err=True
        )
        click.echo(
            'An internal error occurred.\n'
            'The Storyscript team has been notified.\n'
            'Please visit https://status.storyscript.io/ '
            'for incident reports and updates.',
            err=True,
        )
    else:
        click.echo(
            f'An unhandled state of your app has been encountered - {state}',
            err=True,
        )
        click.echo(f'Please shoot an email to support@storyscript.io')


def echo_with_tick(message):
    click.echo(
        click.style('\b' + emoji.emojize(':heavy_check_mark:') + ' ',
                    fg='green') + message
    )


def pluralise(word, quantity):
    if quantity == 1:
        return word

    words = {
        'story': 'stories',
        'service': 'services'
    }
    return words[word]
