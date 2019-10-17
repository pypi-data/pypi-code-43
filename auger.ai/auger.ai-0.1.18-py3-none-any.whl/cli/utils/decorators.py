from functools import wraps
import sys

from auger.api.project import Project
from auger.api.dataset import DataSet
from auger.api.cloud.utils.exception import (
    AugerException, NotAuthenticatedException)


def error_handler(decorated):
    def wrapper(self, *args, **kwargs):
        try:
            return decorated(self, *args, **kwargs)
        except Exception as exc:
            if self.ctx.debug:
                import traceback
                traceback.print_exc()
            self.ctx.log(str(exc))
            sys.exit(1)
    return wrapper


def authenticated(decorated):
    def wrapper(self, *args, **kwargs):
        # verify avalability of auger credentials
        try:
            self.ctx.credentials.verify()
        except NotAuthenticatedException as e:
            self.ctx.log(str(e))
            sys.exit(1)
        return decorated(self, *args, **kwargs)
    return wrapper

def _get_project(self, autocreate):
    project_name = self.ctx.get_config('config').get('name', None)
    if project_name is None:
        raise AugerException(
            'Please specify project name in auger.yaml/name...')
    project = Project(self.ctx, project_name)
    project_properties = project.properties()
    if project_properties is None:
        if autocreate:
            self.ctx.log(
                'Can\'t find project %s on the Auger Cloud. '
                'Creating...' % project_name)
            project.create()
        else:
            raise AugerException('Can\'t find project %s' % project_name)
    return project

def with_project(autocreate=False):
    def decorator(decorated):
        @wraps(decorated)
        def wrapper(self, *args, **kwargs):
            project = _get_project(self, autocreate)
            return decorated(self, project, *args, **kwargs)
        return wrapper
    return decorator

def with_dataset(decorated):
    def wrapper(self, *args, **kwargs):
        project = _get_project(self, False)
        data_set_name = self.ctx.get_config('auger').get('dataset', None)
        if data_set_name is None:
            raise AugerException(
                'Please specify dataset name in auger.yaml/dataset...')
        dataset = DataSet(self.ctx, project, data_set_name)
        return decorated(self, dataset, *args, **kwargs)
    return wrapper
