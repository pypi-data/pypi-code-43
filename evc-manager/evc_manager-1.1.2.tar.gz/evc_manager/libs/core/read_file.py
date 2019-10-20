""" Read YAML file """


import sys
import yaml
from libs.core.log import warn
from libs.core.log import info


def read_file(source_file=None):
    """ Read YAML file and evaluate its content """

    warn('Opening file %s' % source_file)

    with open(source_file, 'r') as stream:
        try:
            #return evaluate_input(yaml.load(stream))
            # TODO: For Python 3.7:
            return evaluate_input(yaml.load(stream, Loader=yaml.FullLoader))
        except yaml.YAMLError as exc:
            info(exc)
        except ValueError as err:
            info('Error: on file %s: %s. Exiting now.' % (source_file, err))

    sys.exit(1)


def evaluate_requested_paths(requested_paths):
    """ Requested requested_paths """

    if not requested_paths:
        warn("RequestedPath needs key 'paths'")
        return False

    if 'paths' not in requested_paths:
        warn("RequestedPath needs key 'paths'")
        return False

    if not isinstance(requested_paths['paths'], list):
        warn("RequestedPath['paths'] needs to be a list")
        return False

    paths = requested_paths['paths']

    for path in paths:
        if not isinstance(path, list):
            warn("Paths is a list of non-empty lists")
            return False
        if not path:
            warn("Paths is a list of non-empty lists")
            return False

        for subpath in path:
            if isinstance(subpath, dict):
                if 'avoid' in subpath:
                    info('links to avoid: %s' % subpath['avoid'])
                if 'include' in subpath:
                    info('links to include: %s' % subpath['include'])
            elif not isinstance(subpath, str):
                warn("Provide name of the NNIs to be used")
                return False
            if not subpath:
                warn("Provide name of the NNIs to be used")
                return False

        # If we got here, we are good.

    return True


def evaluate_input(yaml_input_content):
    """ Evaluate YAML input content """
    if 'version' not in yaml_input_content:
        raise ValueError('Version not provided')

    if 'action' not in yaml_input_content:
        raise ValueError('Action not provided')

    elif yaml_input_content['action'] not in ['add', 'add_range', 'delete', 'move']:
        raise ValueError('Incorrect Action provided')

    if 'evcs' not in yaml_input_content:
        raise ValueError('EVCs not provided')

    elif not isinstance(yaml_input_content['evcs'], list):
        raise ValueError('EVCs is not a list')

    for evc in yaml_input_content['evcs']:
        if 'name' not in evc:
            raise ValueError('EVC requires a name')

        if 'unis' not in evc:
            raise ValueError('EVC requires UNIS')

        if 'requested_paths' in evc:
            if not evaluate_requested_paths(evc['requested_paths']):
                raise ValueError('RequestedPaths incorrect')

        if 'requested_paths' in evc:
            raise ValueError('Wrong Key. Must be requested_paths')

    return yaml_input_content
