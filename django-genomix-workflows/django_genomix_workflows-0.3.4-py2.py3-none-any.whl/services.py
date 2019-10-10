# -*- coding: utf-8 -*-
import logging

import pandas
from rest_framework.exceptions import ParseError

from .models import Task, Workflow, WorkflowType

logger = logging.getLogger(__name__)


def get_or_error(classmodel, **kwargs):
    if 'label' in kwargs and not kwargs.get('label'):
        return None
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist as error:
        raise classmodel.DoesNotExist('Error: {0}. kwargs: {1}'.format(error, kwargs))


def load_tasks(filename, *args, **kwargs):
    """
    Loads Tasks into nexus
    Arguments:
        filename (str): filename of details filename
    Notes:
        file expects the following columns:
            - Task: string
            - Version: string
            - Previous: comma separated list
    """
    df = pandas.read_csv(filename, sep='\t', na_values=['NA', 'na', 'NULL', 'null', 'NONE', 'none', ''])
    df = df.where((pandas.notnull(df)), None)
    columns = df.columns

    for index, row in df.iterrows():
        label = row[columns.get_loc('Task')]
        version = row[columns.get_loc('Version')]
        previous_tasks = row[columns.get_loc('Previous')]
        previous_tasks = previous_tasks.split(',') if previous_tasks else []

        previous_tasks_list = []
        for previous_task in previous_tasks:
            previous_tasks_list.append(get_or_error(Task, label=previous_task))

        try:
            instance = Task.objects.create(label=label, version=version)
        except Exception:
            error = 'Could not create Task: {0} v{1}'.format(label, version)
            raise ParseError(detail=error, code='bad_request')

        instance.previous.add(*previous_tasks_list)
        instance.save()


def load_workflows(filename, *args, **kwargs):
    """
    Loads Tasks into nexus
    Arguments:
        filename (str): filename of details filename
    Notes:
        file expects the following columns:
            - Workflow: string
            - Version: string
            - Type: string
            - Tasks: comma separated list
    """
    df = pandas.read_csv(filename, sep='\t', na_values=['NA', 'na', 'NULL', 'null', 'NONE', 'none', ''])
    df = df.where((pandas.notnull(df)), None)
    columns = df.columns

    for index, row in df.iterrows():
        label = row[columns.get_loc('Workflow')]
        version = row[columns.get_loc('Version')]
        tasks = row[columns.get_loc('Tasks')].split(',')
        type = row[columns.get_loc('Type')]

        task_list = []
        for task in tasks:
            task_list.append(get_or_error(Task, label=task))

        if type:
            type = get_or_error(WorkflowType, label=type)

        try:
            instance = Workflow.objects.create(label=label, version=version, type=type)
        except Exception:
            error = 'Could not create Workflow: {0} v{1}'.format(label, version)
            raise ParseError(detail=error, code='bad_request')

        instance.task.add(*task_list)
        instance.save()
