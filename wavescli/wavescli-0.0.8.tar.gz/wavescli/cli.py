#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import yaml
import subprocess
import click


@click.group()
@click.pass_context
def main(ctx):
    WAVES_URL = os.environ.get('WAVES_URL')

    if not WAVES_URL:
        click.secho('WAVES_URL environment variable not set', fg='red')

    ctx.obj['config'] = {
        'WAVES_URL': WAVES_URL,
    }


@main.command(name='register-businesstask')
@click.argument('yaml_filepath', required=True, type=click.File('r'))
@click.pass_context
def register_businesstask(ctx, yaml_filepath):
    """
    Register the business task
    """
    definition_str = yaml_filepath.read()
    if definition_str:
        click.secho("   Publishing...", fg='green')
        new_btask = ctx.obj.client.register_businesstask(definition_str)
        click.secho(json.dumps(new_btask, indent=2, sort_keys=True), fg='yellow')


@main.command(name='start-worker')
@click.argument('yaml_filepath', required=True, type=click.File('rb'))
@click.option('--tasks', required=False, help='The path for the business task tasks.py file')
def start_worker(yaml_filepath, tasks):
    """
    Start receiving messages for current bt
    """
    definition = yaml.load(yaml_filepath, Loader=yaml.FullLoader)

    task_name = definition.get('business_task')
    task_version = definition.get('version', 'latest')
    tasks_module = definition.get('tasks_module', 'waves.btasks.app')
    if tasks:
        tasks_module = tasks
    default_queue = 'wv_{}@{}'.format(task_name, task_version)
    loglevel = 'INFO'

    concurrency = os.environ.get('CELERY_CONCURRENCY', 1)
    queue = os.environ.get('QUEUE_NAME', default_queue)
    worker_name = os.environ.get('WORKER_HOSTNAME', 'worker')

    # --detach
    cmd = 'celery -A {} worker --hostname {}@{} --loglevel={} --task-events -Ofair -c {} -Q {}'.format(
        tasks_module, task_name, worker_name, loglevel, concurrency, queue)
    click.secho("   ...Starting worker\n{}".format(cmd), fg='yellow')

    subprocess.Popen(cmd.split(' '))


@main.command(name='stop-worker')
@click.argument('yaml_filepath', required=True, type=click.File('rb'))
@click.option('--tasks', required=False, help='The path for the business task tasks.py file')
def stop_worker(yaml_filepath, tasks):
    """
    Start receiving messages for current bt
    """
    definition = yaml.load(yaml_filepath, Loader=yaml.FullLoader)
    tasks_module = definition.get('tasks_module', 'waves.btasks.app')

    if tasks:
        tasks_module = tasks

    cmd = 'celery -A {} control shutdown'.format(tasks_module)
    click.secho("   ...Stopping worker\n{}".format(cmd), fg='yellow')

    subprocess.Popen(cmd.split(' '))
