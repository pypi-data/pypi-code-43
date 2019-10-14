# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._cli.dataset.dataset_subgroup import DatasetSubGroup
from azureml._cli.cli_command import command
from azureml._cli import argument
from azureml.exceptions import UserErrorException

from azureml.core.dataset import Dataset

DATASET_NAME = argument.Argument("dataset_name", "--name", "-n", required=False,
                                 help="Name of the dataset to show")
DATASET_ID = argument.Argument("dataset_id", "--id", "-i", required=False,
                               help="ID of the dataset to show (guid)")

DEPRECATE_BY_DATASET_ID = argument.Argument("deprecate_by_dataset_id", "--deprecate-by-id",
                                            "-d", required=True,
                                            help="Dataset ID (guid) which is the intended \
                                            replacement for this Dataset.")


def _check_python():
    import sys
    current_version = sys.version_info
    if current_version[0] is 3 and current_version[1] >= 5:
        return True
    return False


@command(
    subgroup_type=DatasetSubGroup,
    command="list",
    short_description="List all datasets in the workspace")
def list_datasets_in_workspace(workspace=None, logger=None):
    if _check_python() is False:
        raise UserErrorException('The dataset command subgroup is only supported with Python 3.5 or more')
    dsets = Dataset.list(workspace)
    return list(map(lambda d: d._get_base_info_dict(), dsets))


@command(
    subgroup_type=DatasetSubGroup,
    command="show",
    short_description="Show a dataset by name or ID",
    argument_list=[
        DATASET_NAME,
        DATASET_ID
    ])
def get_dataset(
        workspace=None,
        dataset_name=None,
        dataset_id=None,
        logger=None):
    if _check_python() is False:
        raise UserErrorException('The dataset command subgroup is only supported with Python 3.5 or more')
    dset = Dataset.get(workspace, dataset_name, dataset_id)
    return dset._get_base_info_dict_show()


@command(
    subgroup_type=DatasetSubGroup,
    command="deprecate",
    short_description="Deprecate an active dataset in a workspace by another dataset",
    argument_list=[
        DATASET_NAME,
        DATASET_ID,
        DEPRECATE_BY_DATASET_ID
    ])
def deprecate_dataset(
        workspace=None,
        dataset_name=None,
        dataset_id=False,
        deprecate_by_dataset_id=None,
        logger=None):
    if _check_python() is False:
        raise UserErrorException('The dataset command subgroup is only supported with Python 3.5 or more')
    dataset = Dataset.get(workspace, dataset_name, dataset_id)
    dataset_state = dataset.state
    if dataset_state == 'deprecated':
        raise UserErrorException("Dataset '{}' ({}) is already deprecated".format(dataset.name, dataset.id))
    dataset.deprecate(deprecate_by_dataset_id)
    dataset = Dataset.get(workspace, name=dataset.name)
    if dataset.state == 'deprecated':
        logger.info("Dataset '{}' ({}) was deprecated successfully".format(dataset.name, dataset.id))
        return dataset._get_base_info_dict_show()
    else:
        logger.debug("dataset deprecate error. name: {} id: {} deprecate_by_id: {} state: {}".format(
            dataset.name, dataset.id, deprecate_by_dataset_id, dataset.state))
        raise Exception("Error, Dataset '{}' ({}) was not deprecated".format(dataset.name, dataset.id))


@command(
    subgroup_type=DatasetSubGroup,
    command="archive",
    short_description="Archive an active or deprecated dataset",
    argument_list=[
        DATASET_NAME,
        DATASET_ID
    ])
def archive_dataset(
        workspace=None,
        dataset_name=None,
        dataset_id=None,
        logger=None):
    if _check_python() is False:
        raise UserErrorException('The dataset command subgroup is only supported with Python 3.5 or more')
    dataset = Dataset.get(workspace, dataset_name, dataset_id)
    dataset_state = dataset.state
    if dataset_state == 'archived':
        raise UserErrorException("Dataset '{}' ({}) is already archived".format(dataset.name, dataset.id))
    dataset.archive()
    dataset = Dataset.get(workspace, name=dataset.name)
    if dataset.state == 'archived':
        logger.info("Dataset '{}' ({}) was archived successfully".format(dataset.name, dataset.id))
        return dataset._get_base_info_dict_show()
    else:
        logger.debug("dataset archive error. name: {} id: {} state: {}".format(
            dataset.name, dataset.id, dataset.state))
        raise Exception("Error, Dataset '{}' ({}) was not archived".format(dataset.name, dataset.id))


@command(
    subgroup_type=DatasetSubGroup,
    command="reactivate",
    short_description="Reactivate an archived or deprecated dataset",
    argument_list=[
        DATASET_NAME,
        DATASET_ID
    ])
def reactivate_dataset(
        workspace=None,
        dataset_name=None,
        dataset_id=None,
        logger=None):
    if _check_python() is False:
        raise UserErrorException('The dataset command subgroup is only supported with Python 3.5 or more')
    dataset = Dataset.get(workspace, dataset_name, dataset_id)
    dataset_state = dataset.state
    if dataset_state == 'active':
        raise UserErrorException("Dataset '{}' ({}) is already active".format(dataset.name, dataset.id))
    dataset.reactivate()
    dataset = Dataset.get(workspace, name=dataset.name)
    if dataset.state == 'active':
        logger.info("Dataset '{}' ({}) was reactivated successfully".format(dataset.name, dataset.id))
        return dataset._get_base_info_dict_show()
    else:
        logger.debug("dataset reactivate error. name: {} id: {} state: {}".format(
            dataset.name, dataset.id, dataset.state))
        raise Exception("Error, Dataset '{}' ({}) was not reactivated".format(dataset.name, dataset.id))
