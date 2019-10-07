import json
import logging
import os
import webbrowser
from copy import copy
from multiprocessing import Pool

import click
from prettytable import PrettyTable

from .common import shell, roles, configure
from .renderers import format_processing_action_output, format_full_table
from .tasks import task_create_processing_action_for_image, upload_preview_task, \
    task_download_processing_action, task_recalculate_processing, task_cancel_processing, task_requeue_processing
from .utils import ReboticsCLIContext, pass_rebotics_context, app_dir, process_role, read_saved_role, task_runner, \
    download_file_from_dict
from ..providers import RetailerProvider, ProviderHTTPClientException
from ..utils import mkdir_p, get_filename_from_url

logger = logging.getLogger(__name__)


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']))
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='retailers.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('retailer'), help="Key to specify what retailer to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Retailer CLI tool to communicate with retailer API
    """
    process_role(ctx, role, 'retailer')
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=RetailerProvider
    )


@api.command()
@pass_rebotics_context
def version(ctx):
    """Show retailer backend version"""
    ctx.format_result(ctx.provider.version(), 100)


@api.command()
@click.option('-t', '--input_type')
@click.option('-s', '--store', type=click.INT)
@click.argument('files', nargs=-1, required=True, type=click.File('rb'))
@pass_rebotics_context
def upload_files(ctx, input_type, store, files):
    """
    Upload processing files to the retailer backend, that can be used as processing action inputs
    """
    file_ids = []
    for f_ in files:
        response = ctx.provider.processing_upload(
            store, f_, input_type
        )
        file_ids.append(response['id'])

        if ctx.verbose:
            click.echo(response)  # redirecting this output to stderr
    click.echo(' '.join(map(str, file_ids)))


REQUEUE_TYPES = {
    "facenet_kf": 'requeue_for_facenet_keyframes_key',
    "pt_multiclass": 'REQUEUE_PRICE_TAGS_DETECTION_MULTICLASS',
    "pt_heatmap": 'REQUEUE_PRICE_TAGS_DETECTION_MULTICLASS_HEATMAP',
    "pt_voting": 'REQUEUE_PRICE_TAGS_DETECTION_MULTICLASS_VOTING',
}


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-t', '--requeue-type', type=click.Choice(choices=REQUEUE_TYPES.keys()), required=False, default=None)
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def requeue(ctx, processing_ids, requeue_type, concurrency):
    """Requeue processing actions by given IDs"""
    return task_runner(ctx, task_requeue_processing, processing_ids, concurrency, requeue_type=requeue_type)


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def cancel(ctx, processing_ids, concurrency):
    """Cancel processing of the actions by given IDs"""
    return task_runner(ctx, task_cancel_processing, processing_ids, concurrency)


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def recalculate(ctx, processing_ids, concurrency):
    """Recalculate processing of the actions by given IDs"""
    return task_runner(ctx, task_recalculate_processing, processing_ids, concurrency)


@api.command()
@click.option('-t', '--input_type')
@click.option('-s', '--store', type=click.INT)
@click.option('-p', '--store-planogram', type=click.INT)
@click.option('--aisle')
@click.option('--section')
@click.option('-l', '--lens-used', is_flag=True, default=False)
@click.argument('files', nargs=-1, required=True, type=click.INT)
@pass_rebotics_context
def create_processing_action(ctx, input_type, store, store_planogram, aisle, section, lens_used, files):
    """Create processing action for store defining files by IDs"""
    response = ctx.provider.create_processing_action(
        store, files, input_type,
        store_planogram=store_planogram,
        aisle=aisle,
        section=section,
        lens_used=lens_used
    )
    if ctx.verbose:
        click.echo(response, )
    click.echo(response['id'])


@api.command()
@click.argument('actions', nargs=-1, required=True, type=click.INT)
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def download_processing_action(ctx, actions, target, concurrency):
    """Download processing actions by given IDs"""
    files_to_download = []

    pool = Pool(concurrency)
    actions_data = pool.starmap(task_download_processing_action, [(ctx, action) for action in actions])
    if ctx.verbose:
        click.echo('GET API for processing actions completed')

    for data in actions_data:
        action_id = data['id']
        processing_action_folder = os.path.join(target, 'ProcessingAction#%d' % action_id)

        mkdir_p(processing_action_folder)
        results = os.path.join(processing_action_folder, 'results')
        inputs = os.path.join(processing_action_folder, 'inputs')

        mkdir_p(results)
        mkdir_p(inputs)

        for key in ['merged_image_jpeg', 'merged_image', ]:
            files_to_download.append({
                'url': data[key],
                'filepath': os.path.join(results, get_filename_from_url(data[key])),
                'ctx': ctx,
            })

        for input_object in data.get('inputs', []):
            files_to_download.append({
                'filepath': os.path.join(inputs, get_filename_from_url(input_object['file'])),
                'url': input_object['file'],
                'ctx': ctx
            })

        with open(os.path.join(processing_action_folder, 'processing_action_%d.json' % action_id), 'w') as fout:
            json.dump(data, fout, indent=4)

        if ctx.verbose:
            click.echo('Downloading files for %s' % (action_id,))

    pool.map(download_file_from_dict, files_to_download)

    if ctx.verbose:
        click.echo('Processing download success')


@api.command()
@click.argument('actions', nargs=-1, required=True, type=click.INT)
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@click.option('--template', default="{action_id}_{i}.{ext}")
@pass_rebotics_context
def download_processing_inputs(ctx, actions, target, concurrency, template):
    """Download processing inputs from processing actions"""
    files_to_download = []

    pool = Pool(concurrency)
    actions_data = pool.starmap(task_download_processing_action, [(ctx, action) for action in actions])

    if ctx.verbose:
        click.echo('GET API for processing actions completed')

    for data in actions_data:
        for i, input_object in enumerate(data.get('inputs', [])):
            filename = get_filename_from_url(input_object['file'])
            ext = filename.split('.')[-1]
            action_id = data['id']
            files_to_download.append({
                'filepath': os.path.join(target, template.format(action_id=action_id, i=i, ext=ext)),
                'url': input_object['file'],
                'ctx': ctx
            })

    if ctx.verbose:
        click.echo("Task registraion completed")

    pool.map(download_file_from_dict, files_to_download)

    if ctx.verbose:
        click.echo('Processing inputs download success')


@api.command()
@click.option('-d', '--delete', is_flag=True)
@click.option('-c', '--concurrency', type=int, default=4)
@click.argument('path', type=click.Path(exists=True), default=os.getcwd())
@pass_rebotics_context
def upload_previews_from_folder(ctx, delete, concurrency, path):
    """
    Upload previews from file system to the server in parallel
    It has increased retries and timeout
    """
    provider = ctx.provider
    provider.retries = 5
    provider.timeout = 300
    verbose = ctx.verbose

    tasks = []
    for label in os.listdir(path):
        upc_folder = os.path.join(path, label)
        if not os.path.isdir(upc_folder):
            continue

        if verbose:
            click.echo('Reading folder: %s' % upc_folder)
        task = {
            'provider': provider,
            'images_path': [],
            'delete': delete,
            'upc': label
        }

        if label.isdigit():
            for filename in os.listdir(upc_folder):
                image_path = os.path.join(upc_folder, filename)

                if os.path.isfile(image_path):
                    task['images_path'].append(image_path)

        if task['images_path']:
            tasks.append(task)

    if verbose:
        click.echo('Number of tasks: {}'.format(len(tasks)))

    p = Pool(concurrency)
    p.map(upload_preview_task, tasks)
    click.echo('Finished')


PROCESSING_STATUSES = {
    'created': 'action created',
    'done': 'done',
    'error': 'error',
    'interrupted': 'interrupted',
    'progress': "in progress",
}


@api.command()
@click.option('-s', '--store', type=click.INT, help='Store ID')
@click.option('--status', type=click.Choice(PROCESSING_STATUSES.keys()))
@click.option('-p', '--page', type=click.INT, default=1)
@click.option('-r', '--page-size', type=click.INT, default=10)
@pass_rebotics_context
def processing_actions(ctx, store, status, page, page_size):
    """Fetches processing actions and renders them in terminal"""
    table = PrettyTable()
    table.field_names = ['#', 'id', 'store', 'user', 'status',
                         'created', 'last_requeue', 'last_requeue ago', 'time in queue']

    if ctx.verbose:
        click.echo('Getting list of processing actions')
    try:
        data = ctx.provider.processing_action_list(
            store,
            PROCESSING_STATUSES.get(status),
            page=page,
            page_size=page_size,
        )
        click.echo('Total results: %d' % len(data))
        if ctx.format != 'id':
            format_processing_action_output(data, 'id')
        format_processing_action_output(data, ctx.format)
    except ProviderHTTPClientException:
        raise click.ClickException('Failed to get list of processing actions')


@api.command()
@click.option('-t', '--token')
@click.argument('url')
@pass_rebotics_context
def set_webhook(ctx, token, url):
    """Setting webhook url for current user"""
    data = ctx.provider.set_webhook(url, token)
    click.echo('Webhook ID on server is : %d' % data['id'])


@api.command()
@click.option('-t', '--title', help='Planogram title', required=True)
@click.option('-d', '--description', help='Planogram description', default='')
@click.argument('planogram_file', type=click.File(mode='rb'))
@pass_rebotics_context
def import_planogram(ctx, planogram_file, title, description):
    """Upload planogram file to retailer instance in a very specific format"""
    try:
        ctx.provider.import_planogram(planogram_file, title, description)
    except (AssertionError, ProviderHTTPClientException) as exc:
        click.echo(exc, err=True)


@api.command()
@click.argument('planogram_assign_file', type=click.File(mode='r'))
@click.option('-d', '--deactivate', is_flag=True, help='Deactivate old planogram')
@pass_rebotics_context
def assign_planogram_through_file(ctx, planogram_assign_file, deactivate):
    """ Assign Planogram through the file """
    try:
        ctx.provider.assign_planogram(planogram_assign_file, deactivate)
    except (AssertionError, ProviderHTTPClientException) as exc:
        click.echo(exc, err=True)


@api.command()
@click.argument('braincorp_csv', type=click.File(mode='r'))
@click.option('-s', '--store', type=click.INT, help='Store ID')
@click.option('-t', '--target', default='after_processing_upload.csv')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def upload_brain_corp_images(ctx, braincorp_csv, store, target, concurrency):
    import pandas as pd
    df = pd.read_csv(braincorp_csv, header=None, names=[
        'date', 'time', 'image', 'x', 'y', 'yaw', 'type', 'count', 'note',
    ])
    pool = Pool(concurrency)

    processing_actions_ids = pool.starmap(task_create_processing_action_for_image, [
        (ctx, store, image_path) for image_path in df['image']
    ])
    df['action_id'] = processing_actions_ids
    click.echo('Processing upload completed. Please check completion using: ')
    click.echo('retailer processing-actions -s {}'.format(store))
    click.echo(df.head())
    df.to_csv(target)
    click.echo('File is written to {}'.format(target))


@api.command()
@click.argument('braincorp_csv', type=click.File(mode='r'))
@click.option('-t', '--target', default='after_processing_completed.csv')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def process_brain_corp_images(ctx, braincorp_csv, target, concurrency):
    import pandas as pd
    df = pd.read_csv(braincorp_csv)
    pool = Pool(concurrency)

    processing_actions = pool.starmap(task_download_processing_action, [
        (ctx, action_id) for action_id in df['action_id']
    ])

    def get_product_plu(action):
        if not action:
            return None
        item_upcs = map(lambda x: x['upc'], action['items'])
        return ','.join(set(item_upcs))

    identified_products = list(map(get_product_plu, processing_actions))

    df['identified_products'] = identified_products
    click.echo(df.head())
    df.to_csv(target)
    click.echo('File is written to {}'.format(target))


@api.command()
@click.argument('store_id', type=int)
@pass_rebotics_context
def store_aisles(ctx, store_id):
    """
    This API endpoint returns a list of the aisles and sections for store, accessed by id.
    Allows only GET on detail-route
    Example: get: /api/v4/store/store_planograms/<store_id>/
    """
    aisles = ctx.provider.get_store_aisles(store_id)
    # flatter results
    results = []
    for aisle in aisles:
        sections = aisle.pop('sections')
        for section in sections:
            aisle_section = copy(aisle)
            aisle_section['section'] = section
            results.append(aisle_section)
        else:
            results.append(aisle)

    format_full_table(results)


@api.command()
@pass_rebotics_context
def store_list(ctx):
    """ Return all stores related to the authenticated user"""
    results = ctx.provider.get_stores()
    format_full_table(results)


@api.command()
@click.argument('username')
@pass_rebotics_context
def user_subscriptions(ctx, username):
    """ Returns all subscriptions of the user"""
    ctx.format_result(ctx.provider.user_subscriptions(username))


@api.command()
@click.option('-s', '--store', help='Store ID')
@click.option('-a', '--aisle', help='Aisle')
@click.option('-S', '--section', help='Section')
@click.argument('username')
@pass_rebotics_context
def user_subscribe(ctx, username, store, aisle, section):
    """
    Create a subscription of the user to specific aisle and section scan updates in store alongside with AEON features
    """
    ctx.format_result(ctx.provider.user_subscriptions_create(
        username, store, aisle, section
    ))


@api.group(invoke_without_command=True)
@click.argument('processing_id', required=True, type=click.INT)
@pass_rebotics_context
@click.pass_context
def processing_action(click_context, ctx, processing_id):
    """Returns processing action by processing_id."""
    setattr(ctx, 'processing_id', processing_id)

    if click_context.invoked_subcommand is None:
        result = ctx.provider.processing_action_detail(processing_id)
        format_processing_action_output([result, ], ctx.format)


@processing_action.command(name='realogram')
@pass_rebotics_context
def processing_action_realogram(ctx):
    """Returns processing realogram by processing_id."""
    try:
        result = ctx.provider.processing_action_realogram_detail(ctx.processing_id)
        ctx.format_result(result, keys_to_skip=['banner_id'])
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        click.echo('Failed relogram: %s' % exc)


@processing_action.command(name='download')
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def processing_action_download(ctx, target, concurrency):
    """Download the processing and returns the result of this processing"""
    files_to_download = []

    data = task_download_processing_action(ctx, ctx.processing_id)
    action_id = data['id']
    processing_action_folder = os.path.join(target, 'ProcessingAction#%d' % action_id)

    mkdir_p(processing_action_folder)
    results = os.path.join(processing_action_folder, 'results')
    inputs = os.path.join(processing_action_folder, 'inputs')

    mkdir_p(results)
    mkdir_p(inputs)

    for key in ['merged_image_jpeg', 'merged_image', ]:
        files_to_download.append({
            'url': data[key],
            'filepath': os.path.join(results, get_filename_from_url(data[key])),
            'ctx': ctx,
        })

    for input_object in data.get('inputs', []):
        files_to_download.append({
            'filepath': os.path.join(inputs, get_filename_from_url(input_object['file'])),
            'url': input_object['file'],
            'ctx': ctx
        })

    with open(os.path.join(processing_action_folder, 'processing_action_%d.json' % action_id), 'w') as fout:
        json.dump(data, fout, indent=4)

    pool = Pool(concurrency)
    pool.map(download_file_from_dict, files_to_download)

    if ctx.verbose:
        click.echo('Processing download success')


@processing_action.command(name='requeue')
@click.option('-t', '--requeue-type', type=click.Choice(choices=REQUEUE_TYPES.keys()), required=False, default=None)
@pass_rebotics_context
def processing_action_requeue(ctx, requeue_type):
    """ Requeue the processing action by processing_id """
    try:
        result = ctx.provider.requeue(ctx.processing_id)
        format_processing_action_output([result, ], ctx.format)
    except ProviderHTTPClientException as exc:
        click.echo('Requeue is not allowed %s' % exc)


@processing_action.command(name='cancel')
@pass_rebotics_context
def processing_action_cancel(ctx):
    """Cancel processing calculation by processing_id"""
    try:
        result = ctx.provider.cancel(ctx.processing_id)
        format_processing_action_output([result, ], ctx.format)
    except ProviderHTTPClientException as exc:
        click.echo('Cancel is not allowed: %s' % exc)


@processing_action.command(name='recalculate')
@pass_rebotics_context
def processing_action_recalculate(ctx):
    """Recalculate processing action by processing_id"""
    try:
        result = ctx.provider.recalculate(ctx.processing_id)
        format_processing_action_output([result, ], ctx.format)
    except ProviderHTTPClientException as exc:
        click.echo('Recalculate is not allowed: %s' % exc)


@processing_action.command(name='view')
@pass_rebotics_context
def processing_action_view_in_admin(ctx):
    """View processing action in admin"""
    url = ctx.provider.build_url('/admin/processing/processingaction/{}/change/'.format(ctx.processing_id))

    if ctx.verbose:
        click.echo('Opening processing action in browser: %s' % url)
    webbrowser.open(url)


@processing_action.command(name='delete')
@pass_rebotics_context
def processing_action_delete(ctx):
    """Delete existing processing action by processing_id"""
    try:
        result = ctx.provider.processing_action_delete(ctx.processing_id)
        click.echo('Successfully deactivated processing action')
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        click.echo('Failed to deactivate: %s' % exc)


@processing_action.command(name='copy')
@pass_rebotics_context
def processing_action_copy(ctx):
    """Copy of the existing processing action by processing_id"""
    action = ctx.provider.processing_action_detail(ctx.processing_id)

    inputs_id = [i['id'] for i in action['inputs']]

    try:

        result = ctx.provider.create_processing_action(
            action['store_id'],
            files=inputs_id,
            input_type=action['input_type'],
        )
        click.echo('Successfully created processing action')
        format_processing_action_output([result, ], ctx.format)
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        click.echo('Failed to create processing action: %s' % exc)


@processing_action.command(name='notify-oos')
@click.option('-f', '--force', is_flag=True, default=False)
@pass_rebotics_context
def processing_action_notify_oss_report_ready(ctx, force):
    try:
        result = ctx.provider.send_oos_notification(ctx.processing_id, force)
        ctx.format_result(result)
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        click.echo('Failed to notify OOS report ready. %s' % exc)


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
