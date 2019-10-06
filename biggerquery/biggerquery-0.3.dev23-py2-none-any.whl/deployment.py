from datetime import datetime
from datetime import timedelta
from unittest import TestCase
from pathlib import Path
import tempfile
import filecmp
import mock
import dateutil.parser
from zipfile import ZipFile
import os
import shutil

from .workflow import Workflow
from .job import Job


def callable_factory(job, dt_as_datetime):
    def job_callable(**kwargs):
        timestamp_name = 'ds' if not dt_as_datetime else 'ts'
        runtime = kwargs.get(timestamp_name)
        if timestamp_name == 'ts':
            runtime = dateutil.parser.parse(runtime)
            runtime = runtime.strftime("%Y-%m-%d %H:%M:%S")
        job.run(runtime)

    return job_callable


def workflow_to_dag(workflow, start_from, dag_id):
    operators = []
    for job in workflow:
        operators.append({
            'task_type': 'python_callable',
            'task_kwargs': {
                'task_id': job.id,
                'python_callable': callable_factory(job, workflow.dt_as_datetime),
                'retries': job.retry_count,
                'retry_delay': timedelta(seconds=job.retry_pause_sec),
                'provide_context': True
            }
        })

    return {
               'dag_id': dag_id,
               'default_args': {
                   'owner': 'airflow',
                   'depends_on_past': True,
                   'start_date': datetime.strptime(start_from, "%Y-%m-%d" if len(start_from) <= 10 else "%Y-%m-%d %H:%M:%S"),
                   'email_on_failure': False,
                   'email_on_retry': False
               },
               'schedule_interval': workflow.schedule_interval,
               'max_active_runs': 1
           }, operators


def build_dag_file(workflow_import_path,
                   start_from,
                   dag_id):
    dag_package_name = workflow_import_path.split('.')[0]

    return '''from airflow import models
from airflow.operators import python_operator
import biggerquery as bgq
from {workflow_import_path} import {workflow_name} as workflow

dag_args, tasks = bgq.workflow_to_dag(workflow, '{start_from}', '{dag_id}')

dag = models.DAG(**dag_args)
final_task = python_operator.PythonOperator(dag=dag, **tasks[0]['task_kwargs'])
for task in tasks[1:]:
    final_task = final_task >> python_operator.PythonOperator(dag=dag, **task['task_kwargs'])

globals()['{dag_id}'] = dag'''.format(
        dag_package=dag_package_name,
        workflow_import_path='.'.join(workflow_import_path.split('.')[:-1]),
        workflow_name=workflow_import_path.split('.')[-1],
        start_from=start_from,
        dag_id=dag_id)


def zip_dir(path, ziph, prefix_to_cut_from_filename):
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith('.pyc'):
                ziph.write(os.path.join(root, file),
                           os.path.join(root.replace(prefix_to_cut_from_filename, ''), file))


def build_dag(
        package_path,
        workflow_import_path,
        start_from,
        dag_id,
        target_dir_path):
    dag_file_name = '{}.py'.format(dag_id)
    dag_file_path = os.path.join(target_dir_path, dag_file_name)
    with open(dag_file_path, 'w') as dag_file:
        dag_file.write(build_dag_file(workflow_import_path, start_from, dag_id))

    zip_path = os.path.join(target_dir_path, '{}.zip'.format(dag_id))
    with ZipFile(zip_path, 'w') as zip:
        zip.write(dag_file_path, dag_file_name)
        zip_dir(package_path, zip, os.path.join(*package_path.split(os.sep)[:-1]))

    os.remove(dag_file_path)
    return zip_path


def build_dag_from_notebook(
        notebook_path,
        workflow_variable_name,
        start_date,
        custom_target_dir_path=None):
    cwd = custom_target_dir_path or os.getcwd()
    notebook_name = notebook_path.split(os.sep)[-1].split('.')[0]
    workflow_package = os.path.join(cwd, workflow_variable_name + '_package')
    workflow_package_init = os.path.join(workflow_package, '__init__.py')
    os.mkdir(workflow_package)
    with open(workflow_package_init, 'w') as f:
        f.write('pass')
    os.popen("jupyter nbconvert --output-dir='{output_dir_path}' --to python {notebook_path}".format(
        notebook_path=notebook_path,
        output_dir_path=cwd)).read()
    converted_notebook_name = '{}.py'.format(notebook_name)
    converted_notebook_path = os.path.join(cwd, converted_notebook_name)
    with open(converted_notebook_path, 'r') as copy_source:
        with open(os.path.join(workflow_package, converted_notebook_name), 'w') as copy_target:
            copy_target.write(''.join(copy_source.readlines()))
    result_path = build_dag(
        workflow_package,
        '.'.join([workflow_variable_name + '_package', notebook_name, workflow_variable_name]),
        start_date,
        workflow_variable_name,
        cwd)
    os.remove(converted_notebook_path)
    shutil.rmtree(workflow_package)
    return result_path


class BuildDagFromNotebook(TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.notebook_path = os.path.join(self.tmp_dir, 'notebook.ipynb')
        self.comparision_tmp_dir = tempfile.mkdtemp()
        with open(self.notebook_path, 'w') as f:
            f.write('''{
                "cells": [],
                "metadata": {},
                "nbformat": 4,
                "nbformat_minor": 2
            }''')

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_should_build_dag_from_notebook(self):
        # when
        dag_zip_path = build_dag_from_notebook(
            self.notebook_path,
            'test_workflow',
            '2019-01-01',
            self.tmp_dir)

        # then
        self.dag_is_valid(dag_zip_path, 'test_workflow')

    def dag_is_valid(self, dag_zip_path, workflow_name):
        workflow_package_name = workflow_name + '_package'
        unpacked_dag_dir_path = os.path.join(self.comparision_tmp_dir, 'unpacked_dag_dir_path')
        correct_dag_dir_path = os.path.join(self.comparision_tmp_dir, 'correct_dag_dir_path')
        workflow_package_path = os.path.join(correct_dag_dir_path, workflow_package_name)
        workflow_package_init_path = os.path.join(workflow_package_path, '__init__.py')
        workflow_file_path = os.path.join(workflow_package_path, 'notebook.py')
        dag_file_path = os.path.join(correct_dag_dir_path, 'test_workflow.py')
        os.mkdir(unpacked_dag_dir_path)
        os.mkdir(correct_dag_dir_path)
        os.mkdir(workflow_package_path)
        Path(workflow_package_init_path).touch()
        Path(workflow_file_path).touch()
        with open(dag_file_path, 'w') as f:
            f.write(build_dag_file('{}.notebook.test_workflow'.format(workflow_package_name), '2019-01-01', 'test_workflow'))

        with ZipFile(dag_zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.comparision_tmp_dir)
            self.assertTrue(filecmp.dircmp(unpacked_dag_dir_path, correct_dag_dir_path))


class BuildDagTestCase(TestCase):
    def setUp(self):
        self.tmp_dir, self.workflow_package_path, self.workflow_import_path = self.create_tmp_workflow_package_path()
        self.comparision_tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        shutil.rmtree(self.comparision_tmp_dir)

    def create_tmp_workflow_package_path(self):
        tmp_dir = tempfile.mkdtemp()
        workflow_package_path = os.path.join(tmp_dir, 'test_workflow')
        workflow_module_path = os.path.join(workflow_package_path, 'workflow_module.py')

        os.mkdir(workflow_package_path)
        Path(workflow_module_path).touch()
        return tmp_dir, workflow_package_path, 'test_workflow.workflow_module'

    def test_should_build_dag_zip(self):
        # given
        tmp_dir, workflow_package_path, workflow_import_path = self.create_tmp_workflow_package_path()

        # when
        dag_zip_path = build_dag(
            workflow_package_path,
            workflow_import_path,
            '2019-01-01',
            'dag1',
            tmp_dir)

        # then
        self.dag_is_valid(dag_zip_path, workflow_package_path)

    def dag_is_valid(self, dag_zip_path, workflow_package_path):
        with ZipFile(dag_zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.comparision_tmp_dir)
            self.assertTrue(filecmp.dircmp(workflow_package_path, self.comparision_tmp_dir))


class CallableFactoryTestCase(TestCase):
    def test_should_run_job_with_datetime_or_date_based_on_settings(self):
        # given
        job = mock.Mock()

        # when
        callable_factory(job, dt_as_datetime=False)(ds='2019-01-01')

        # then
        job.assert_has_calls([mock.call.run('2019-01-01')])

        # given
        job = mock.Mock()

        # when
        callable_factory(job, dt_as_datetime=True)(ts='2019-01-01 00:00:00')

        # then
        job.assert_has_calls([mock.call.run('2019-01-01 00:00:00')])


class WorkflowToDagTestCase(TestCase):

    @mock.patch('biggerquery.deployment.callable_factory')
    def test_should_turn_workflow_to_dag_configuration(self, callable_factory_mock):
        # given
        callable_factory_mock.side_effect = lambda job, dt_as_datetime: (job, dt_as_datetime)
        job = Job(
            id='job1',
            component=mock.Mock(),
            retry_count=100,
            retry_pause_sec=200
        )
        workflow = Workflow(definition=[job], schedule_interval='@hourly')

        # when
        dag_config, operators_config = workflow_to_dag(workflow, '2019-01-01', 'dag1')

        # then
        self.assertEqual(dag_config, {
            'dag_id': 'dag1',
            'default_args': {
                'owner': 'airflow',
                'depends_on_past': True,
                'start_date': datetime.strptime('2019-01-01', "%Y-%m-%d"),
                'email_on_failure': False,
                'email_on_retry': False
            },
            'schedule_interval': '@hourly',
            'max_active_runs': 1
        })
        self.assertEqual(len(operators_config), 1)
        self.assertEqual(operators_config[0], {
            'task_type': 'python_callable',
            'task_kwargs': {
                'task_id': 'job1',
                'python_callable': (job, False),
                'retries': 100,
                'retry_delay': timedelta(seconds=200),
                'provide_context': True
            }
        })


class BuildDagFileTestCase(TestCase):
    def test_should_build_dag_file(self):
        # when
        dag_file = build_dag_file('my.super.workflow', '2019-01-01', 'dag1')

        # then
        self.assertEqual(dag_file, '''from airflow import models
from airflow.operators import python_operator
import biggerquery as bgq
from my.super import workflow as workflow

dag_args, tasks = bgq.workflow_to_dag(workflow, '2019-01-01', 'dag1')

dag = models.DAG(**dag_args)
final_task = python_operator.PythonOperator(dag=dag, **tasks[0]['task_kwargs'])
for task in tasks[1:]:
    final_task = final_task >> python_operator.PythonOperator(dag=dag, **task['task_kwargs'])

globals()['dag1'] = dag''')