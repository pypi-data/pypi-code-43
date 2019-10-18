import os
import shutil
import subprocess
import tempfile

import jinja2 as j2
import yaml


class PyParsingError(Exception):
    pass


class UnexpectedValue(Exception):
    pass


def make_temp_yaml_from_dict(dict_source):
    fd, path = tempfile.mkstemp(suffix='.yaml')
    with os.fdopen(fd, 'w') as tmp:
        yaml.dump(dict_source, tmp, default_flow_style=False)
    return path


def make_cfndsl_yaml(node_file, profile, render_all=False, reverse=False):
    fd, path = tempfile.mkstemp(suffix='.yaml')
    if node_file.name.endswith('.py'):
        environ = os.environ
        environ['PROFILE'] = profile
        environ['ALL'] = str(render_all)
        environ['REVERSE'] = str(reverse)
        process = subprocess.run(
            ['python', node_file.name], capture_output=True,
            env=environ)
        if process.returncode != 0:
            raise PyParsingError(
                    'Error when converting py->yaml: (%s, %s)' % (
                        process.stdout, process.stderr))
        _yml = yaml.load(process.stdout, Loader=yaml.FullLoader)
        with os.fdopen(fd, 'w') as tmp:
            yaml.dump(_yml, tmp, default_flow_style=False)
    else:
        shutil.copyfile(node_file.name, path)
    return path


def make_app_conf(yamlfile, conf):
    appconf = {} if yamlfile is None else yaml.load(
        yamlfile, Loader=yaml.FullLoader)
    appconf['nodeconf'] = conf
    return appconf


def make_base_conf(path):
    if path is None:
        raise UnexpectedValue("Path shouldn't be None")
    with open(path, 'r') as node_f:
        conf = yaml.load(node_f, Loader=yaml.FullLoader)
        return conf


def make_rendered_template(templates, template_file, conf):
    env = j2.Environment(
        loader=j2.FileSystemLoader(templates), trim_blocks=False)
    rendered_template = env.get_template(template_file).render(conf)
    return rendered_template
