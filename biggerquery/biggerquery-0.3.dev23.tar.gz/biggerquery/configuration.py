from __future__ import absolute_import

from unittest import TestCase
from unittest import main

from .gcp_defaults import DEFAULT_REGION
from .gcp_defaults import DEFAULT_MACHINE_TYPE
from .utils import unzip_file_and_save_outside_zip_as_tmp_file


class DatasetConfig(object):

    def __init__(self,
                 project_id,
                 dataset_name,
                 internal_tables=None,
                 external_tables=None,
                 extras=None,
                 dataflow_config=None):
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.internal_tables = internal_tables or []
        self.external_tables = external_tables or {}
        self.extras = extras or {}
        self.dataflow_config = dataflow_config

    def _as_dict(self, with_dataflow_config=False):
        config = {
            'project_id': self.project_id,
            'dataset_name': self.dataset_name,
            'internal_tables': self.internal_tables,
            'external_tables': self.external_tables,
            'extras': self.extras
        }
        if self.dataflow_config and with_dataflow_config:
            config.update(self.dataflow_config._as_dict)
        return config


class DataflowConfig(object):

    def __init__(self,
                 dataflow_bucket_id,
                 requirements_path,
                 region=DEFAULT_REGION,
                 machine_type=DEFAULT_MACHINE_TYPE):
        self.dataflow_bucket_id = dataflow_bucket_id
        self.requirements_path = requirements_path
        self.region = region
        self.machine_type = machine_type
        self._tmp_requirements_file = None

    @property
    def _final_requirements_path(self):
        if '.zip' in self.requirements_path:
            self._tmp_requirements_file = unzip_file_and_save_outside_zip_as_tmp_file(self.requirements_path)
            return self._tmp_requirements_file.name
        return self.requirements_path

    @property
    def _as_dict(self):
        return {
            'dataflow_bucket': self.dataflow_bucket_id,
            'machine_type': self.machine_type,
            'region': self.region,
            'requirements_file_path': self._final_requirements_path
        }


class DatasetConfigTestCase(TestCase):

    def test_should_provide_defaults(self):
        # given
        config = DatasetConfig(project_id='some.awesome.project',
                               dataset_name='some_dataset')

        # expected
        self.assertEqual(config.project_id, 'some.awesome.project')
        self.assertEqual(config.dataset_name, 'some_dataset')
        self.assertEqual(config.internal_tables, [])
        self.assertEqual(config.external_tables, {})
        self.assertEqual(config.extras, {})
        self.assertEqual(config.dataflow_config, None)

    def test_should_return_as_dict(self):
        # given
        config = DatasetConfig(project_id='some.awesome.project',
                               dataset_name='some_dataset')

        # expected
        self.assertEqual(config._as_dict(), {
            'project_id': 'some.awesome.project',
            'dataset_name': 'some_dataset',
            'internal_tables': [],
            'external_tables': {},
            'extras': {}
        })

        # given
        config = DatasetConfig(project_id='some.awesome.project',
                               dataset_name='some_dataset',
                               dataflow_config=DataflowConfig(
                                   dataflow_bucket_id='some_bucket',
                                   requirements_path='/',
                                   region='europe-west1',
                                   machine_type='standard'))

        # expected
        self.assertEqual(config._as_dict(with_dataflow_config=True), {
            'project_id': 'some.awesome.project',
            'dataset_name': 'some_dataset',
            'internal_tables': [],
            'external_tables': {},
            'extras': {},
            'dataflow_bucket': 'some_bucket',
            'machine_type': 'standard',
            'region': 'europe-west1',
            'requirements_file_path': '/'
        })


class DataflowConfigTestCase(TestCase):
    def test_should_provide_default(self):
        # given
        config = DataflowConfig(dataflow_bucket_id='some_bucket',
                                requirements_path='/')

        # expected
        self.assertEqual(config.dataflow_bucket_id, 'some_bucket')
        self.assertEqual(config.requirements_path, '/')
        self.assertEqual(config.machine_type, DEFAULT_MACHINE_TYPE)
        self.assertEqual(config.region, DEFAULT_REGION)

    def test_should_return_as_dict(self):
        # given
        config = DataflowConfig(dataflow_bucket_id='some_bucket',
                                requirements_path='/')

        # expected
        self.assertEqual(config._as_dict, {
            'dataflow_bucket': 'some_bucket',
            'machine_type': DEFAULT_MACHINE_TYPE,
            'region': DEFAULT_REGION,
            'requirements_file_path': '/'
        })


if __name__ == '__main__':
    main()