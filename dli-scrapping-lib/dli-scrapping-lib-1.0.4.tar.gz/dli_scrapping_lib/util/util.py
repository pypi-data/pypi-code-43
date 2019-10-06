import os

def create_new_dir(dir_name):
    """
    Check if a directory exists, if not create and cd it.
    """
    directory = dir_name
    if not os.path.exists(directory):
        os.makedirs(directory)
    # go to that new directory
    os.chdir(directory)