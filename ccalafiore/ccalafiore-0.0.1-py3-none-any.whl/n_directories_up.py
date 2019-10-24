from os.path import dirname


def n_directories_up(directory, n=1):

    directory_target = directory
    while n > 0:
        # directory_target = os.path.dirname(directory_target)
        directory_target = dirname(directory_target)
        n -= 1

    return directory_target
