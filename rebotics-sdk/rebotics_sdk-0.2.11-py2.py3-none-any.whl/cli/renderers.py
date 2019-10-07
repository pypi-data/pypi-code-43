import json
from datetime import datetime

import click
import pytz
from dateutil import parser as date_parser
from prettytable import PrettyTable


def extract_fields_to_render(d, max_column_length, keys_to_skip, key_prefix=None, depth=0, max_depth=1):
    fields_to_render = []

    if depth > max_depth:
        return []

    for field, value in d.items():
        if field in keys_to_skip:
            continue

        if key_prefix is not None:
            field = '{}.{}'.format(key_prefix, field)

        if not (isinstance(value, list)):
            if isinstance(value, str):
                if len(value) < max_column_length:
                    fields_to_render.append(field)
            elif isinstance(value, int) or isinstance(value, float):
                fields_to_render.append(field)
            elif value is None:
                fields_to_render.append(field)
            elif isinstance(value, dict):
                fields_to_render.extend(
                    extract_fields_to_render(value, max_column_length, keys_to_skip, key_prefix=field)
                )
    return fields_to_render


def format_full_table(results, max_column_length=30, keys_to_skip=None):
    if keys_to_skip is None:
        keys_to_skip = []

    def get_attribute(value, key, default):
        if '.' not in key:
            return value.get(key, default)

        keys = key.split('.')
        acc = value
        for k in keys:
            try:
                acc = acc.get(k, '---')
            except Exception:
                acc = default
        return acc

    if not isinstance(results, list):
        results = [results]
    table = PrettyTable()
    for i, item in enumerate(results):
        if i == 0:
            table.field_names = extract_fields_to_render(item, max_column_length, keys_to_skip)

        table.add_row([
            get_attribute(item, field, '---') for field in table.field_names
        ])
    click.echo(table)


def format_processing_action_output(processing_actions_list, format_):
    if format_ == 'json':
        click.echo(json.dumps(processing_actions_list, indent=2))
    elif format_ == 'id':
        click.echo(" ".join([str(item['id']) for item in processing_actions_list]))
    else:
        try:
            format_processing_action_table(processing_actions_list)
        except:
            format_full_table(processing_actions_list)


def format_processing_action_table(processing_actions_list):
    table = PrettyTable()
    table.field_names = ['#', 'id', 'store', 'user', 'status', 'store_planogram_id', 'aisle', 'section',
                         'created', 'last_requeue', 'last_requeue ago', 'time in queue']
    now = datetime.now(pytz.utc)
    for i, processing_action in enumerate(processing_actions_list):
        created_datetime = date_parser.parse(processing_action['created'])
        last_requeue_datetime = date_parser.parse(processing_action['last_requeue'])

        time_in_queue = now - last_requeue_datetime
        if processing_action['status'] in ['error', 'done', 'interrupted']:
            processing_start_time = processing_action.get('processing_start_time')
            processing_finish_time = processing_action.get('processing_finish_time')
            if processing_finish_time is None and processing_finish_time is None:
                time_in_queue = 'unknown'
            else:
                start_time = date_parser.parse(processing_start_time)
                finish_time = date_parser.parse(processing_finish_time)
                time_in_queue = finish_time - start_time
        table.add_row([
            i,
            processing_action['id'],
            '#{store_id}'.format(**processing_action),
            '{username}'.format(**processing_action['user']),
            processing_action['status'],
            processing_action['store_planogram_id'],
            processing_action['aisle'],
            processing_action['section'],
            created_datetime.strftime('%c'),
            last_requeue_datetime.strftime('%c'),
            str(now - last_requeue_datetime),
            str(time_in_queue),
        ])
    click.echo(table)
