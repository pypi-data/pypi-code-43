import os

import click

from fabnodes.lib.actions import Actions
from fabnodes.lib.actions import execute_action
from fabnodes.lib import util


command_settings = {
    'ignore_unknown_options': True,
}


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@click.command(context_settings=command_settings)
@click.argument('action', type=click.Choice(Actions.to_list()))
@click.argument('node', type=click.File('rb'))
@click.option(
    '--appyaml', type=click.File('rb'),
    help='configuration for application',
    default=None)
@click.option(
    '--node-type', type=click.Choice(['node']),
    help='node type to fabricate',
    default='node')
@click.option(
    '--templates', type=click.Path('exists=True'),
    default=os.path.join(THIS_DIR, 'templates'),
    help='template directory')
@click.option('--template-file', default='cfndsl.rb.j2', help='template file')
@click.option('--profile', default='dev', help='profile to use')
def main(
        action, node, appyaml, node_type,
        templates, template_file, profile):
    path = None
    parent_path = None
    act = Actions[action.upper()]
    if True or act == Actions.TEST_FEATURE:
        try:
            parent_path = util.make_cfndsl_yaml(node, profile)
            parent_conf = util.make_base_conf(parent_path)
            for node in parent_conf['nodes']:
                path = util.make_temp_yaml_from_dict(node)
                try:
                    conf = util.make_base_conf(path)
                    tf = template_file

                    if 'template_file' in conf:
                        tf = conf['template_file']
                        del conf['template_file']
                    appconf = util.make_app_conf(appyaml, conf)
                    appconf['profile'] = profile
                    appconf['template_file'] = tf
                    rendered_template = util.make_rendered_template(
                        templates, tf, conf)

                    status, out = execute_action(
                        act, appconf, path, rendered_template)
                    for line in out:
                        click.echo(line)
                    if not status:
                        click.echo('Process failed')
                        exit(1)
                finally:
                    if path is not None:
                        os.remove(path)
        finally:
            if parent_path is not None:
                os.remove(parent_path)
        exit(0)
    try:
        path = util.make_cfndsl_yaml(node, profile)
        conf = util.make_base_conf(path)
        appconf = util.make_app_conf(appyaml, conf)
        if profile:
            appconf['profile'] = profile
        rendered_template = util.make_rendered_template(
            templates, template_file, conf)

        status, out = execute_action(act, appconf, path, rendered_template)
        for line in out:
            click.echo(line)
        if not status:
            click.echo('Process failed')
            exit(1)
    finally:
        if path is not None:
            os.remove(path)
