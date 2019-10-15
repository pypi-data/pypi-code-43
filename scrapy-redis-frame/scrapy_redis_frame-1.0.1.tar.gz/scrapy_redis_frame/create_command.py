import os
import sys
import re
import click
from os.path import join, exists, abspath
import string
from shutil import ignore_patterns, move, copy2, copystat

__version__ = "1.0.0"

IGNORE = ignore_patterns('*.pyc', '.svn')
TEMPLATES_TO_RENDER = (
    ('scrapy.cfg',),
    ('${project_name}', 'settings.py.tmpl'),
    ('${project_name}', 'spiders\\example_spider.py.tmpl'),
    # ('${project_name}', 'pipelines.py.tmpl'),
    # ('${project_name}', 'middlewares.py.tmpl'),
)


def verbose_option(f):
    def callback(ctx, param, value):
        pass

    return click.option("-v", "--version", is_flag=True, expose_value=False, help="Enable verbose output",
                        callback=callback)(f)


def common_options(f):
    f = verbose_option(f)
    return f


pgk_dir = os.path.dirname(os.path.abspath(__file__))


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option('{0} from {1} (Python {2})'.format(__version__, pgk_dir, sys.version[:3]), '-V', '--version')
@common_options
def cli():
    pass


@click.command()
@click.option('-n', '--name', help="please input name", required=True)
def create_project(name):
    project_name = name
    project_dir = name

    if exists(join(project_dir, 'scrapy.cfg')):
        print('Error: scrapy.cfg already exists in %s' % abspath(project_dir))
        return
    templates_dir_1 = templates_dir()
    copytree(templates_dir_1, abspath(project_dir))
    move(join(project_dir, 'module'), join(project_dir, project_name))
    for paths in TEMPLATES_TO_RENDER:
        path = join(*paths)
        tplfile = join(project_dir,
                       string.Template(path).substitute(project_name=project_name))
        render_templatefile(tplfile, project_name=project_name,
                            ProjectName=string_camelcase(project_name))
    print("New Scrapy project '%s', using template directory '%s', "
          "created in:" % (project_name, templates_dir_1))
    print("    %s\n" % abspath(project_dir))
    print("You can start your first spider with:")
    print("    cd %s" % project_dir)
    print("    scrapy genspider example example.com")


CAMELCASE_INVALID_CHARS = re.compile(r'[^a-zA-Z\d]')


def string_camelcase(string):
    """ Convert a word  to its CamelCase version and remove invalid chars

    >>> string_camelcase('lost-pound')
    'LostPound'

    >>> string_camelcase('missing_images')
    'MissingImages'

    """
    return CAMELCASE_INVALID_CHARS.sub('', string.title())


def templates_dir():
    file_current_path = os.path.abspath(os.path.dirname(__file__))
    current_path = file_current_path[:-18]
    return join(current_path, 'scrapy_redis_frame', 'generate', 'templates', 'project')


def copytree(src, dst):
    ignore = IGNORE
    names = os.listdir(src)
    ignored_names = ignore(src, names)

    if not os.path.exists(dst):
        os.makedirs(dst)

    for name in names:
        if name in ignored_names:
            continue

        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if os.path.isdir(srcname):
            copytree(srcname, dstname)
        else:
            copy2(srcname, dstname)
    copystat(src, dst)


def render_templatefile(path, **kwargs):
    with open(path, 'rb') as fp:
        raw = fp.read().decode('utf8')

    content = string.Template(raw).substitute(**kwargs)

    render_path = path[:-len('.tmpl')] if path.endswith('.tmpl') else path
    with open(render_path, 'wb') as fp:
        fp.write(content.encode('utf8'))
    if path.endswith('.tmpl'):
        os.remove(path)


if __name__ == '__main__':
    create_project()
