import os
def _mpath(path):
    dir_path = __file__
    dir_path = os.path.dirname(os.path.dirname(dir_path))
    return os.path.join(dir_path,path)



