from __future__ import absolute_import


import os
import runpy
import mock

import tempfile
import imp
from types import ModuleType
from inspect import getargspec
from inspect import getmodule
from unittest import TestCase
from unittest import main

from .utils import secure_create_dataflow_manager_import
from .dataset_manager import create_dataset_manager
create_dataflow_manager = secure_create_dataflow_manager_import()

from .utils import unzip_file_and_save_outside_zip_as_tmp_file
from .utils import AutoDeletedTmpFile
from .configuration import DatasetConfig
from .configuration import DataflowConfig

DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_PAUSE_SEC = 60


class Job(object):
    def __init__(self,
                 component,
                 id=None,
                 retry_count=DEFAULT_RETRY_COUNT,
                 retry_pause_sec=DEFAULT_RETRY_PAUSE_SEC,
                 **dependency_configuration):
        self.id = id or component.__name__
        self.component = component
        self.dependency_configuration = dependency_configuration
        self.retry_count = retry_count
        self.retry_pause_sec = retry_pause_sec

    def __call__(self, runtime):
        return self.run(runtime)

    def run(self, runtime):
        return self._run_component(self._build_dependencies(runtime))

    def _build_dependencies(self, runtime):
        return {
            dependency_name: self._build_dependency(
                dependency_config=self._find_config(dependency_name),
                runtime=runtime)
            for dependency_name in self._component_dependencies
        }

    def _run_component(self, dependencies):
        if not self._is_dataflow_job:
            return self.component(**dependencies)
        else:
            return self._run_beam_component(dependencies)

    def _run_beam_component(self, dependencies):
        component_file_path = os.path.abspath(getmodule(self.component).__file__)
        return runpy.run_path(
            path_name=unzip_file_and_save_outside_zip_as_tmp_file(component_file_path, suffix='.py').name
                if '.zip' in component_file_path else component_file_path,
            init_globals={'dependencies': dependencies},
            run_name='__main__')

    @property
    def _component_dependencies(self):
        return [dependency_name for dependency_name in getargspec(self._component).args]

    @property
    def _component(self):
        return self.component if not self._is_dataflow_job else self.component.run

    @property
    def _is_dataflow_job(self):
        return isinstance(self.component, ModuleType)

    def _find_config(self, target_dependency_name):
        for dependency_name, config in self.dependency_configuration.items():
            if dependency_name == target_dependency_name:
                return config
        raise ValueError("Can't find config for dependency: " + target_dependency_name)

    def _build_dependency(self, dependency_config, runtime):
        if self._is_dataflow_job:
            return create_dataflow_manager(runtime=runtime,
                **dependency_config._as_dict(with_dataflow_config=True))
        _, dataset_manager = create_dataset_manager(runtime=runtime,
            **dependency_config._as_dict())
        return dataset_manager


class JobTestCase(TestCase):

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_run_bigquery_component(self, create_dataset_manager_mock):

        # given
        create_dataset_manager_mock.side_effect = lambda **kwargs: (kwargs, kwargs)

        def test_component(bigquery_dependency1, bigquery_dependency2):

            # then
            self.assertEqual(bigquery_dependency2, {
                'project_id': 'some-project-id-2',
                'dataset_name': 'some-dataset-2',
                'internal_tables': ['some_internal_table'],
                'external_tables': {'some_external_table': 'some.external.table'},
                'extras': {'extra_param': 'some-extra-param'},
                'runtime': '2019-01-01'
            })

            # and
            self.assertEqual(bigquery_dependency1, {
                'project_id': 'some-project-id',
                'dataset_name': 'some-dataset',
                'internal_tables': ['some_internal_table'],
                'external_tables': {'some_external_table': 'some.external.table'},
                'extras': {'extra_param': 'some-extra-param'},
                'runtime': '2019-01-01'
            })

        job = Job(component=test_component,
                  bigquery_dependency1=DatasetConfig(
                      project_id='some-project-id',
                      dataset_name='some-dataset',
                      internal_tables=['some_internal_table'],
                      external_tables={'some_external_table': 'some.external.table'},
                      extras={'extra_param': 'some-extra-param'}),
                  bigquery_dependency2=DatasetConfig(
                      project_id='some-project-id-2',
                      dataset_name='some-dataset-2',
                      dataflow_config=DataflowConfig(
                          dataflow_bucket_id='dataflow-bucket-id',
                          requirements_path='/requirements.txt',
                          region='europe-west',
                          machine_type='standard'
                      ),
                      internal_tables=['some_internal_table'],
                      external_tables={'some_external_table': 'some.external.table'},
                      extras={'extra_param': 'some-extra-param'}))

        # when
        job('2019-01-01')

    @mock.patch('biggerquery.job.create_dataflow_manager')
    def test_should_run_beam_component(self, create_dataflow_manager_mock):

        # given
        tmp_beam_component = self.setup_temporary_beam_component()

        create_dataflow_manager_mock.side_effect = lambda **kwargs: kwargs

        job = Job(component=tmp_beam_component,
                  dependency_beam_manager=DatasetConfig(
                      project_id='some_project_id',
                      dataset_name='some_dataset',
                      dataflow_config=DataflowConfig(
                          dataflow_bucket_id='dataflow_bucket',
                          requirements_path='/requirements.txt',
                          region='europe-west',
                          machine_type='standard'
                      ),
                      internal_tables=['some_internal_table'],
                      external_tables={'some_external_table': 'some.external.table'},
                      extras={'extra_param': 'some-extra-param', 'test_case': self}))

        # when
        job('2019-01-01')

    def setup_temporary_beam_component(self):
        tmp_module = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
        tmp_module.write(b'''
def run(dependency_beam_manager):
    dependency_beam_manager['extras']['test_case'].assertEqual(dependency_beam_manager, {
        'project_id': 'some_project_id',
        'dataset_name': 'some_dataset',
        'internal_tables': ['some_internal_table'],
        'external_tables': {'some_external_table': 'some.external.table'},
        'extras': {'extra_param': 'some-extra-param', 'test_case': dependency_beam_manager['extras']['test_case']},
        'requirements_file_path': '/requirements.txt',
        'dataflow_bucket': 'dataflow_bucket',
        'region': 'europe-west',
        'machine_type': 'standard',
        'runtime': '2019-01-01'
    })

if __name__ == '__main__':
    run(**globals()['dependencies'])''')
        tmp_module.close()
        self._tmp_module_file = AutoDeletedTmpFile(tmp_module)
        return imp.load_source(tmp_module.name.split('/')[0], tmp_module.name)


if __name__ == '__main__':
    main()