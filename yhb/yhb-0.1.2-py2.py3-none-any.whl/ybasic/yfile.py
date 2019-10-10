import os


def get_all_files_from_basedir(basedir):
    result = []
    for root, dirs, files in os.walk(basedir):
        for d in dirs:
            result.append(os.path.join(root, d))
    return result
