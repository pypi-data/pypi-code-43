import os
import tempfile
import json
import copy

from unittest import mock

from flywheel_cli.commands.editions import _process_edition

def test_enable_lab_on_group():

    args = mock.Mock()
    args.edition = 'lab'
    args.group = 'test_group'
    # We have to set to none or the mock will return a mock instance variable
    args.project = None

    with mock.patch('flywheel_cli.commands.editions.create_flywheel_client') as mock_client:
        mock_client.return_value.get_group.return_value = {}
        _process_edition(args, True)
        mock_client.return_value.modify_group.assert_called_with(args.group, {'editions': {'lab': True}})

def test_disable_lab_on_group():

    args = mock.Mock()
    args.edition = 'lab'
    args.group = 'test_group'
    args.projects = None

    with mock.patch('flywheel_cli.commands.editions.create_flywheel_client') as mock_client:
        mock_client.return_value.get_group.return_value = {}
        _process_edition(args, False)
        mock_client.return_value.modify_group.assert_called_with(args.group, {'editions': {'lab': False}})

def test_enable_lab_on_project():

    args = mock.Mock()
    args.edition = 'lab'
    args.group = None
    args.project = 'test_project'

    with mock.patch('flywheel_cli.commands.editions.create_flywheel_client') as mock_client:
        mock_client.return_value.get_project.return_value = {}
        _process_edition(args, True)
        mock_client.return_value.modify_project.assert_called_with(args.project, {'editions': {'lab': True}})

def test_disable_lab_on_project():

    args = mock.Mock()
    args.edition = 'lab'
    args.group = None
    args.project = 'test_project'

    with mock.patch('flywheel_cli.commands.editions.create_flywheel_client') as mock_client:
        mock_client.return_value.get_project.return_value = {}
        _process_edition(args, False)
        mock_client.return_value.modify_project.assert_called_with(args.project, {'editions': {'lab': False}})

def test_enabling_new_edition_keeps_original_editions():

    args = mock.Mock()
    args.edition = 'lab'
    args.group = None
    args.project = 'test_project'

    original_editions = {'original_val': True}
    expected_editions = {'original_val': True, 'lab': True}

    with mock.patch('flywheel_cli.commands.editions.create_flywheel_client') as mock_client:
        mock_client.return_value.get_project.return_value.get.return_value = original_editions
        _process_edition(args, True)
        mock_client.return_value.modify_project.assert_called_with(args.project, {'editions': original_editions})


def test_disabling_new_edition_keeps_original_editions():

    args = mock.Mock()
    args.edition = 'lab'
    args.group = None
    args.project = 'test_project'

    original_editions = {'original_val': True}
    expected_editions = {'original_val': True, 'lab': False}

    with mock.patch('flywheel_cli.commands.editions.create_flywheel_client') as mock_client:
        mock_client.return_value.get_project.return_value.get.return_value = original_editions
        _process_edition(args, False)
        mock_client.return_value.modify_project.assert_called_with(args.project, {'editions': expected_editions})


def test_edition_invalid_edition_keeps_original_editions():

    """This should never happen as the args parser does not allow invalid values
    but just in case we have a test to validate that it keeps the org editions as they were"""
    args = mock.Mock()
    args.edition = 'DNE'
    args.group = None
    args.project = 'test_project'

    original_editions = {'original_val': True}
    expected_editions = {'original_val': True, 'DNE': True}

    with mock.patch('flywheel_cli.commands.editions.create_flywheel_client') as mock_client:
        mock_client.return_value.get_project.return_value.get.return_value = original_editions
        _process_edition(args, True)
        mock_client.return_value.modify_project.assert_called_with(args.project, {'editions': expected_editions})

