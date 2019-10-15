import os.path as path
from distutils.dir_util import copy_tree
from quixote import get_context


def copy(directory: str):
    """
    Fetch the delivery by copying it from a directory on the local machine

    :param directory:       the directory containing the deliveries

    The structure of ``directory`` must be like so:
    directory/
    └── 123/
        └── file1.txt
        └── file2.png
    └── 124/
        └── file1.txt
        └── file2.png

    where 123 and 124 are group IDs.

    The following entries must be provided in the context:
    - group_id:         the ID of the target group, as integer
    """
    group_id = get_context()["group_id"]
    delivery_path = get_context()["delivery_path"]
    copy_tree(path.join(directory, str(group_id)), delivery_path)
