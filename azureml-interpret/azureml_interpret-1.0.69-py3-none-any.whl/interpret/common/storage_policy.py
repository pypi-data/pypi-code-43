# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines storage policy."""

from azureml.interpret.common.constants import History


def storage_policy(block_size=None, max_num_blocks=None, **kwargs):
    """Set of parameters for defining the storage policy on explanations.

    :param block_size: The size of each block for the summary stored in artifacts storage.
    :type block_size: int
    :param max_num_blocks: The maximum number of blocks to store.
    :type max_num_blocks: int
    :rtype: dict
    :return: The arguments for the storage policy
    """
    kwargs[History.BLOCK_SIZE] = block_size
    kwargs[History.MAX_NUM_BLOCKS] = max_num_blocks
    return kwargs
