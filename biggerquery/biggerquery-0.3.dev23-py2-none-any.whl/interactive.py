from __future__ import absolute_import

from inspect import getargspec
import hashlib
from unittest import TestCase
from unittest import main
import mock

import pandas as pd

from .configuration import DatasetConfig
from .job import Job
from .job import DEFAULT_RETRY_COUNT
from .job import DEFAULT_RETRY_PAUSE_SEC
from .utils import not_none_or_error


DEFAULT_OPERATION_NAME = '__auto'
DEFAULT_PEEK_LIMIT = 1000
DEFAULT_RUNTIME = '1970-01-01'
INLINE_COMPONENT_DATASET_ALIAS = '_inline_component_dataset'


def interactive_component(**dependencies):
    def decorator(standard_component):
        return InteractiveComponent(standard_component,
                                    {dep_name: dep.config for dep_name, dep in dependencies.items()})
    return decorator


class InteractiveDatasetManager(object):
    """Let's you run operations on a dataset, without the need of creating a component."""

    def __init__(self,
                 project_id,
                 dataset_name,
                 internal_tables=None,
                 external_tables=None,
                 extras=None):
        self.config = DatasetConfig(
            project_id=project_id,
            dataset_name=dataset_name,
            internal_tables=internal_tables,
            external_tables=external_tables,
            extras=extras)

    def write_truncate(self, table_name, sql, partitioned=True):
        method = 'write_truncate'
        return self._tmp_interactive_component_factory(
            generate_component_name(method=method, table_name=table_name, sql=sql),
            method,
            table_name,
            sql,
            partitioned=partitioned,
            operation_name=DEFAULT_OPERATION_NAME)

    def write_append(self, table_name, sql, partitioned=True):
        method = 'write_append'
        return self._tmp_interactive_component_factory(
            generate_component_name(method=method, table_name=table_name, sql=sql),
            method,
            table_name,
            sql,
            partitioned=partitioned,
            operation_name=DEFAULT_OPERATION_NAME)

    def write_tmp(self, table_name, sql):
        method = 'write_tmp'
        return self._tmp_interactive_component_factory(
            generate_component_name(method=method, table_name=table_name, sql=sql),
            method,
            table_name,
            sql,
            operation_name=DEFAULT_OPERATION_NAME)

    def collect(self, sql):
        method = 'collect'
        return self._tmp_interactive_component_factory(
            generate_component_name(method=method, table_name='', sql=sql),
            method,
            sql,
            operation_name=DEFAULT_OPERATION_NAME)

    def create_table(self, create_query):
        method = 'create_table'
        return self._tmp_interactive_component_factory(
            generate_component_name(method=method, table_name='', sql=create_query),
            method,
            create_query,
            operation_name=DEFAULT_OPERATION_NAME)

    def load_table_from_dataframe(self, table_name, df, partitioned=True):
        method = 'load_table_from_dataframe'
        return self._tmp_interactive_component_factory(
            generate_component_name(method=method, table_name=table_name, sql=''),
            method,
            table_name=table_name,
            df=df,
            partitioned=partitioned,
            operation_name=DEFAULT_OPERATION_NAME)

    def _tmp_interactive_component_factory(self, component_name, method, *args, **kwargs):
        @interactive_component(_inline_component_dataset=self)
        def tmp_component(_inline_component_dataset):
            return getattr(_inline_component_dataset, method)(*args, **kwargs)

        tmp_component._standard_component.__name__ = component_name
        return tmp_component


def generate_component_name(method, table_name, sql):
    """
    >>> generate_component_name('write_truncate', 'some_table', 'select * from another_table')
    'write_truncate_some_table_5ada1f6e843dc3c517d5eedbae557fbbdf98d6d5047272f092e7b89455826722'
    """
    component_id = hashlib.sha256()
    component_id.update(sql.encode('utf-8'))
    component_id = component_id.hexdigest()
    return '{}_{}_{}'.format(method, table_name, component_id)


class InteractiveComponent(object):
    """Let's you run the component for the specific runtime
     and peek the operation results as the pandas.DataFrame."""

    def __init__(self, standard_component, dependency_config):
        self._standard_component = standard_component
        self._dependency_config = dependency_config

    def to_job(self,
               id=None,
               retry_count=DEFAULT_RETRY_COUNT,
               retry_pause_sec=DEFAULT_RETRY_PAUSE_SEC,
               dependencies_override=None):
        _, component_callable = decorate_component_dependencies_with_operation_level_dataset_manager(self._standard_component)

        dependencies_override = dependencies_override or {}
        dependency_config = self._dependency_config.copy()
        dependency_config.update({dataset_alias: dataset.config for dataset_alias, dataset in dependencies_override.items()})

        return Job(
            component=component_callable,
            id=id,
            retry_count=retry_count,
            retry_pause_sec=retry_pause_sec,
            **dependency_config)

    def run(self, runtime=DEFAULT_RUNTIME, operation_name=None):
         _, component_callable = decorate_component_dependencies_with_operation_level_dataset_manager(
             self._standard_component, operation_name=operation_name)
         return Job(component_callable, **self._dependency_config).run(runtime)

    def peek(self, runtime, operation_name=DEFAULT_OPERATION_NAME, limit=DEFAULT_PEEK_LIMIT):
        """Returns the result of the specified operation in the form of the pandas.DataFrame, without really running the
        operation and affecting the table."""
        not_none_or_error(runtime, 'runtime')
        not_none_or_error(operation_name, 'operation_name')
        not_none_or_error(limit, 'limit')
        results_container, component_callable = decorate_component_dependencies_with_operation_level_dataset_manager(
            self._standard_component, operation_name=operation_name, peek=True, peek_limit=limit)
        Job(component_callable, **self._dependency_config).run(runtime)
        try:
            return results_container[0]
        except IndexError:
            if operation_name != DEFAULT_OPERATION_NAME:
                raise ValueError("Operation '{}' not found".format(operation_name))
            else:
                raise ValueError("You haven't specified operation_name.".format(operation_name))

    def __call__(self, **kwargs):
        _, component_callable = decorate_component_dependencies_with_operation_level_dataset_manager(self._standard_component)
        return component_callable(**kwargs)


def decorate_component_dependencies_with_operation_level_dataset_manager(
        standard_component,
        operation_name=None,
        peek=None,
        peek_limit=None):
    operation_settings = {'operation_name': operation_name, 'peek': peek, 'peek_limit': peek_limit}
    results_container = []

    def component_callable(**kwargs):
        operation_level_dataset_managers = {k: OperationLevelDatasetManager(v, **operation_settings)
                                            for k, v in kwargs.items()}

        component_return_value = standard_component(**operation_level_dataset_managers)

        for operation_level_dataset_manager in operation_level_dataset_managers.values():
            if operation_level_dataset_manager._result:
                results_container.extend(operation_level_dataset_manager._result)

        return component_return_value

    component_callable_with_proper_signature = "def reworked_function({signature}):\n    return original_func({kwargs})\n".format(
        signature=','.join([arg for arg in getargspec(standard_component).args]),
        kwargs=','.join(['{arg}={arg}'.format(arg=arg) for arg in getargspec(standard_component).args]))
    component_callable_with_proper_signature_code = compile(component_callable_with_proper_signature, "fakesource",
                                                            "exec")
    fake_globals = {}
    eval(component_callable_with_proper_signature_code, {'original_func': component_callable}, fake_globals)

    component_callable = fake_globals['reworked_function']
    component_callable.__name__ = operation_name or standard_component.__name__

    return results_container, component_callable


class OperationLevelDatasetManager(object):
    """
    Let's you run specified operation or peek a result of a specified operation.
    """

    def __init__(self, dataset_manager, peek=False, operation_name=None, peek_limit=DEFAULT_PEEK_LIMIT):
        self._dataset_manager = dataset_manager
        self._peek = peek
        self._operation_name = operation_name
        self._peek_limit = peek_limit
        self._results_container = []

    def write_truncate(self, table_name, sql, partitioned=True, custom_run_datetime=None, operation_name=None):
        return self._run_write_operation(
            operation_name=operation_name,
            method=self._dataset_manager.write_truncate,
            sql=sql,
            table_name=table_name,
            partitioned=partitioned,
            custom_run_datetime=custom_run_datetime)

    def write_append(self, table_name, sql, partitioned=True, custom_run_datetime=None, operation_name=None):
        return self._run_write_operation(
            operation_name=operation_name,
            method=self._dataset_manager.write_append,
            sql=sql,
            table_name=table_name,
            partitioned=partitioned,
            custom_run_datetime=custom_run_datetime)

    def write_tmp(self, table_name, sql, custom_run_datetime=None, operation_name=None):
        return self._run_write_operation(
            operation_name=operation_name,
            method=self._dataset_manager.write_tmp,
            sql=sql,
            table_name=table_name,
            custom_run_datetime=custom_run_datetime)

    def collect(self, sql, custom_run_datetime=None, operation_name=None):
        return self._run_write_operation(
            operation_name=operation_name,
            method=self._dataset_manager.collect,
            sql=sql,
            custom_run_datetime=custom_run_datetime)

    def create_table(self, create_query, operation_name=None):
        if self._operation_name == operation_name or self._operation_name is None:
            return self._results_container, self._dataset_manager.create_table(create_query=create_query)

    def load_table_from_dataframe(self, table_name, df, partitioned=True, custom_run_datetime=None, operation_name=None):
        if self._should_peek_operation_results(operation_name):
            return df
        elif self._should_run_operation(operation_name):
            return self._dataset_manager.load_table_from_dataframe(
                table_name=table_name,
                df=df,
                custom_run_datetime=custom_run_datetime,
                partitioned=partitioned)

    @property
    def dt(self):
        return self._dataset_manager.runtime_str

    @property
    def extras(self):
        return self._dataset_manager.extras

    @property
    def _result(self):
        return self._results_container

    @property
    def client(self):
        return self._dataset_manager.client

    def _collect_select_result_to_pandas(self, sql):
        sql = sql if 'limit' in sql.lower() else sql + '\nLIMIT {}'.format(str(self._peek_limit))
        return self._dataset_manager.collect(sql)

    def _run_write_operation(self, operation_name, method, sql, *args, **kwargs):
        if self._should_peek_operation_results(operation_name):
            result = self._collect_select_result_to_pandas(sql)
            self._results_container.append(result)
            return result
        elif self._should_run_operation(operation_name):
            return method(*args, sql=sql, **kwargs)
        else:
            return pd.DataFrame()

    def _should_peek_operation_results(self, operation_name):
        return self._operation_name == operation_name and self._peek is not None

    def _should_run_operation(self, operation_name):
        return self._operation_name == operation_name or self._operation_name is None


class OperationLevelDatasetManagerTestCase(TestCase):

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_preserve_dataset_order(self, create_dataset_manager_mock):
        # given
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, {'dependency_kwargs': kwargs})

        # given
        dataset1, dataset2, dataset3 = [
            InteractiveDatasetManager(
                project_id='project{}'.format(str(i)),
                dataset_name='dataset{}'.format(str(i)))
            for i in range(1, 4)
        ]

        @interactive_component(ds1=dataset1, ds2=dataset2, ds3=dataset3)
        def standard_component(ds2, ds1, ds3):
            # then
            self.assertEqual(ds1._dataset_manager['dependency_kwargs']['project_id'], 'project1')
            self.assertEqual(ds2._dataset_manager['dependency_kwargs']['project_id'], 'project2')
            self.assertEqual(ds3._dataset_manager['dependency_kwargs']['project_id'], 'project3')

        # when
        job = standard_component.to_job()

        # then
        job.run('2019-01-01')

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_pass_all_arguments_to_core_dataset_manager_on_run(self, create_dataset_manager_mock):
        # given
        fake_dataset_manager = mock.Mock()
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, fake_dataset_manager)

        dataset = InteractiveDatasetManager(
            project_id='project1',
            dataset_name='dataset1')

        @interactive_component(ds=dataset)
        def standard_component(ds):
            ds.write_truncate('some table', 'some sql', partitioned=False, custom_run_datetime='2019-12-12')
            ds.write_append('some table', 'some sql', partitioned=False, custom_run_datetime='2019-12-12')
            ds.write_tmp('some table', 'some sql', custom_run_datetime='2019-12-12')
            ds.collect('some sql', custom_run_datetime='2019-12-12')
            ds.create_table('some sql')
            ds.load_table_from_dataframe(
                'some table', 'some dataframe', partitioned=False, custom_run_datetime='2019-12-12')

        # when
        job = standard_component.to_job()
        job.run('2019-01-01')

        # then
        fake_dataset_manager.assert_has_calls([
            mock.call.write_truncate(
                table_name='some table', sql='some sql', partitioned=False, custom_run_datetime='2019-12-12'),
            mock.call.write_append(
                table_name='some table', sql='some sql', partitioned=False, custom_run_datetime='2019-12-12'),
            mock.call.write_tmp(
                table_name='some table', sql='some sql', custom_run_datetime='2019-12-12'),
            mock.call.collect(
                sql='some sql', custom_run_datetime='2019-12-12'),
            mock.call.create_table(create_query='some sql'),
            mock.call.load_table_from_dataframe(
                table_name='some table', df='some dataframe', partitioned=False, custom_run_datetime='2019-12-12')
        ])

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_run_specified_operation(self, create_dataset_manager_mock):
        # given
        dataset_manager_mock = mock.Mock()
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, dataset_manager_mock)

        default_dataset = InteractiveDatasetManager(
            project_id='project1',
            dataset_name='dataset1')

        @interactive_component(ds=default_dataset)
        def standard_component(ds):
            # then
            ds.write_truncate('table1', 'some sql', operation_name='operation1')
            ds.write_truncate('table2', 'some sql', operation_name='operation2')
            ds.write_truncate('table3', 'some sql', operation_name='operation3')

        # when
        standard_component.run('2019-01-01', operation_name='operation2')

        # then
        dataset_manager_mock.assert_has_calls([mock.call.write_truncate(
            table_name='table2',
            sql='some sql',
            custom_run_datetime=None,
            partitioned=True)])

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_peek_operation_results(self, create_dataset_manager_mock):
        # given
        dataset_manager_mock = mock.Mock()
        dataset_manager_mock.collect.side_effect = lambda sql, **kwargs: sql
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, dataset_manager_mock)

        default_dataset = InteractiveDatasetManager(
            project_id='project1',
            dataset_name='dataset1')

        @interactive_component(ds=default_dataset)
        def standard_component(ds):
            # then
            ds.write_truncate('table1', 'some sql', operation_name='operation1')

            ds.collect('collect sql 2', operation_name='operation2')
            ds.write_truncate('table3', 'collect sql 3', operation_name='operation3')
            ds.write_append('table4', 'collect sql 4', operation_name='operation4')
            ds.write_tmp('table5', 'collect sql 5', operation_name='operation5')

            ds.write_truncate('table3', 'some sql', operation_name='operation6')

        # expected
        self.assertEqual(
            standard_component.peek('2019-01-01', operation_name='operation2'),
            'collect sql 2\nLIMIT 1000')
        self.assertEqual(
            standard_component.peek('2019-01-01', operation_name='operation3'),
            'collect sql 3\nLIMIT 1000')
        self.assertEqual(
            standard_component.peek('2019-01-01', operation_name='operation4'),
            'collect sql 4\nLIMIT 1000')
        self.assertEqual(
            standard_component.peek('2019-01-01', operation_name='operation5'),
            'collect sql 5\nLIMIT 1000')


    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_allow_setting_peek_limit(self, create_dataset_manager_mock):
        # given
        dataset_manager_mock = mock.Mock()
        dataset_manager_mock.collect.side_effect = lambda sql, **kwargs: sql
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, dataset_manager_mock)

        default_dataset = InteractiveDatasetManager(
            project_id='project1',
            dataset_name='dataset1')

        @interactive_component(ds=default_dataset)
        def standard_component(ds):
            # then
            ds.write_truncate('table1', 'some sql', operation_name='operation1')
            ds.collect('collect sql', operation_name='operation2')
            ds.write_truncate('table3', 'some sql', operation_name='operation3')

        # when
        result = standard_component.peek('2019-01-01', operation_name='operation2', limit=1)

        # then
        self.assertEqual(result, 'collect sql\nLIMIT 1')


class InteractiveComponentToJobTestCase(TestCase):

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_pass_configuration_to_job(self, create_dataset_manager_mock):
        # given

        class DatasetManagerStub(object):
            def __init__(self, runtime_str, extras):
                self.runtime_str = runtime_str
                self.extras = extras
                self.client = 'client'

        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, DatasetManagerStub(
            kwargs.get('runtime'), kwargs.get('extras')))

        default_dataset = InteractiveDatasetManager(
            project_id='fake_project',
            dataset_name='fake_dataset',
            extras={'extra': 'param'})

        @interactive_component(ds=default_dataset)
        def standard_component(ds):
            # then
            self.assertEqual(ds.dt, '2019-01-01')
            self.assertEqual(ds.extras, {'extra': 'param'})
            self.assertEqual(ds.client, 'client')

        # when
        job = standard_component.to_job()

        # then
        self.assertEqual(job.id, 'standard_component')
        self.assertEqual(job.retry_count, DEFAULT_RETRY_COUNT)
        self.assertEqual(job.retry_pause_sec, DEFAULT_RETRY_PAUSE_SEC)
        self.assertEqual(job.dependency_configuration, {'ds': default_dataset.config})
        job.run('2019-01-01')

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_turn_component_to_job_with_redefined_dependencies(self, create_dataset_manager_mock):
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, {'dependency_kwargs': kwargs})

        # given
        default_dataset = InteractiveDatasetManager(
            project_id='default_project',
            dataset_name='default_dataset',
            internal_tables=['table1'],
            external_tables={'table': 'table1'},
            extras={'param': 'param1'})

        @interactive_component(ds1=default_dataset, ds2=default_dataset)
        def standard_component(ds1, ds2):
            # then
            self.assertEqual(ds1._dataset_manager['dependency_kwargs']['project_id'], 'default_project')
            self.assertEqual(ds1._dataset_manager['dependency_kwargs']['dataset_name'], 'default_dataset')
            self.assertEqual(ds1._dataset_manager['dependency_kwargs']['internal_tables'], ['table1'])
            self.assertEqual(ds1._dataset_manager['dependency_kwargs']['external_tables'], {'table': 'table1'})
            self.assertEqual(ds1._dataset_manager['dependency_kwargs']['extras'], {'param': 'param1'})

            self.assertEqual(ds2._dataset_manager['dependency_kwargs']['project_id'], 'modified_project')
            self.assertEqual(ds2._dataset_manager['dependency_kwargs']['dataset_name'], 'modified_dataset')
            self.assertEqual(ds2._dataset_manager['dependency_kwargs']['internal_tables'], ['table2'])
            self.assertEqual(ds2._dataset_manager['dependency_kwargs']['external_tables'], {'table': 'table2'})
            self.assertEqual(ds2._dataset_manager['dependency_kwargs']['extras'], {'param': 'param2'})

        modified_dataset = InteractiveDatasetManager(
            project_id='modified_project',
            dataset_name='modified_dataset',
            internal_tables=['table2'],
            external_tables={'table': 'table2'},
            extras={'param': 'param2'})

        # when
        job = standard_component.to_job(dependencies_override={'ds2': modified_dataset})

        # then
        job.run('2019-01-01')

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_not_mutate_dependency_configuration_when_redefining_dependencies(self, create_dataset_manager_mock):
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, {'dependency_kwargs': kwargs})

        # given
        default_dataset = InteractiveDatasetManager(
            project_id='default_project',
            dataset_name='default_dataset')

        @interactive_component(ds=default_dataset)
        def standard_component(ds):
            # then
            self.assertEqual(ds._dataset_manager['dependency_kwargs']['project_id'], 'default_project')
            self.assertEqual(ds._dataset_manager['dependency_kwargs']['dataset_name'], 'default_dataset')

        modified_dataset = InteractiveDatasetManager(
            project_id='modified_project',
            dataset_name='modified_dataset')

        # when
        standard_component.to_job(dependencies_override={'ds': modified_dataset})
        standard_component.to_job().run('2019-01-01')

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_wrap_each_dependency_into_operation_level_dataset_manager(self, create_dataset_manager_mock):
        # given
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, {'dependency_kwargs': kwargs})
        dataset1 = InteractiveDatasetManager(project_id='project1', dataset_name='someds')

        @interactive_component(ds1=dataset1)
        def fake_component(ds1):
            # then
            self.assertEqual(ds1._peek, None)
            self.assertEqual(ds1._operation_name, None)
            self.assertEqual(ds1._peek_limit, None)

        # when
        fake_component.to_job().run('2019-01-01')


class InteractiveComponentRunTestCase(TestCase):

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_wrap_each_dependency_into_operation_level_dataset_manager(self, create_dataset_manager_mock):
        # given
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, {'dependency_kwargs': kwargs})
        dataset1 = InteractiveDatasetManager(project_id='project1', dataset_name='someds')

        @interactive_component(ds1=dataset1)
        def fake_component(ds1):
            # then 1
            self.assertEqual(ds1._peek, None)
            self.assertEqual(ds1._operation_name, None)
            self.assertEqual(ds1._peek_limit, None)

        # when 1
        fake_component.run()

        @interactive_component(ds1=dataset1)
        def fake_component(ds1):
            # then 2
            self.assertEqual(ds1._peek, None)
            self.assertEqual(ds1._operation_name, 'some_operation')
            self.assertEqual(ds1._peek_limit, None)

        # when 2
        fake_component.run('2019-01-01', operation_name='some_operation')

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_pass_configuration_to_job(self, create_dataset_manager_mock):
        # given
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, {'dependency_kwargs': kwargs})
        dataset1 = InteractiveDatasetManager(
            project_id='project1',
            dataset_name='someds')

        @interactive_component(ds1=dataset1)
        def fake_component(ds1):
            # then
            self.assertEqual(ds1._dataset_manager['dependency_kwargs']['project_id'], 'project1')
            self.assertEqual(ds1._dataset_manager['dependency_kwargs']['dataset_name'], 'someds')

        # when
        fake_component.run()


class InteractiveComponentPeekTestCase(TestCase):

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_wrap_each_dependency_into_operation_level_dataset_manager(self, create_dataset_manager_mock):
        # given
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, mock.MagicMock())
        dataset = InteractiveDatasetManager(project_id='project1', dataset_name='dataset1')

        @interactive_component(ds=dataset)
        def fake_component(ds):
            # then
            self.assertEqual(ds._peek, True)
            self.assertEqual(ds._operation_name, 'some_operation')
            self.assertEqual(ds._peek_limit, 100)
            ds.write_truncate('some_table', '''some sql''', operation_name='some_operation')

        # when
        fake_component.peek('2019-01-01', operation_name='some_operation', limit=100)

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_pass_configuration_to_job(self, create_dataset_manager_mock):
        # given
        def fake_dataset_manager(kwargs):
            result = mock.Mock()
            result.configure_mock(**{
                'dependency_kwargs.return_value': kwargs
            })
            return result

        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, fake_dataset_manager(kwargs))
        dataset = InteractiveDatasetManager(
            project_id='project1',
            dataset_name='dataset1')

        @interactive_component(ds=dataset)
        def fake_component(ds):
            # then
            self.assertEqual(ds._dataset_manager.dependency_kwargs()['project_id'], 'project1')
            self.assertEqual(ds._dataset_manager.dependency_kwargs()['dataset_name'], 'dataset1')
            ds.write_truncate('some_table', '''some sql''', operation_name='some_operation')

        # when
        fake_component.peek('2019-01-01', operation_name='some_operation')

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_return_peeked_operation_result(self, create_dataset_manager_mock):
        # given
        def fake_dataset_manager(kwargs):
            result = mock.Mock()
            result.configure_mock(**{
                'collect.return_value': 'peeked_value'
            })
            return result

        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, fake_dataset_manager(kwargs))
        dataset = InteractiveDatasetManager(project_id='project1', dataset_name='dataset1')

        @interactive_component(ds=dataset)
        def fake_component(ds):
            ds.write_truncate('some_table', '''some sql''', operation_name='some_operation')

        # when
        peek_result = fake_component.peek('2019-01-01', operation_name='some_operation', limit=100)

        # then
        self.assertEqual(peek_result, 'peeked_value')

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_not_allow_peeking_with_none_argument(self, create_dataset_manager_mock):
        # given
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, mock.Mock())
        dataset = InteractiveDatasetManager(project_id='project1', dataset_name='dataset1')

        @interactive_component(ds=dataset)
        def fake_component(ds):
            pass

        # then
        with self.assertRaises(ValueError):
            # when
            fake_component.peek('2019-01-01', operation_name=None)

        # then
        with self.assertRaises(ValueError):
            # when
            fake_component.peek('2019-01-01', limit=None)

        # then
        with self.assertRaises(ValueError):
            # when
            fake_component.peek(None)

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_throw_error_when_operation_not_found(self, create_dataset_manager_mock):
        # given
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, mock.Mock())
        dataset = InteractiveDatasetManager(project_id='project1', dataset_name='dataset1')

        @interactive_component(ds=dataset)
        def fake_component(ds):
            pass

        # then
        with self.assertRaises(ValueError):
            # when
            fake_component.peek('2019-01-01', operation_name='nonexistent')


class InteractiveDatasetManagerTestCase(TestCase):

    @mock.patch('biggerquery.job.create_dataset_manager')
    def test_should_create_component_for_specified_operation(self, create_dataset_manager_mock):
        # given
        dataset_manager_mock = mock.Mock()
        create_dataset_manager_mock.side_effect = lambda **kwargs: (None, dataset_manager_mock)

        dataset = InteractiveDatasetManager(project_id='project1', dataset_name='dataset1')
        write_truncate_component = dataset.write_truncate('table', 'some sql')
        write_append_component = dataset.write_append('table', 'some sql')
        write_tmp_component = dataset.write_tmp('table', 'some sql')
        collect_component = dataset.collect('some sql')
        load_table_from_dataframe_component = dataset.load_table_from_dataframe('table', 'df')

        # when
        write_truncate_component.run()
        write_append_component.run()
        write_tmp_component.run()
        collect_component.run()
        load_table_from_dataframe_component.run()

        # then
        dataset_manager_mock.assert_has_calls([
            mock.call.write_truncate(
                table_name='table',
                sql='some sql',
                custom_run_datetime=None,
                partitioned=True),
            mock.call.write_append(
                table_name='table',
                sql='some sql',
                custom_run_datetime=None,
                partitioned=True),
            mock.call.write_tmp(
                table_name='table',
                sql='some sql',
                custom_run_datetime=None),
            mock.call.collect(
                sql='some sql',
                custom_run_datetime=None),
            mock.call.load_table_from_dataframe(
                table_name='table',
                df='df',
                custom_run_datetime=None,
                partitioned=True),
        ])


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    main()