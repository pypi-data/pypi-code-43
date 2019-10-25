import errno
import os
from shutil import copy2
import re

from pyus._build_utils.cuda import check_cuda_version


def whl_install(whl_path, dst_base_path, cuda_version=None):

    whl_name = whl_path.split('/')[-1]
    pkg_name_long = re.search('(^.*?)-cp', whl_name).group(1)
    pkg_name_short = re.search('^.*?-{1}[0-9]+\.[0-9]+\.[0-9]+', whl_name).group(0)

    pkg_dir = os.path.join(dst_base_path, pkg_name_long)
    link_dir = os.path.join(dst_base_path, pkg_name_short)

    # CUDA version sub directory
    cu_dir = 'cu' + check_cuda_version(cuda_version)[0].replace(".", "")

    # Complete path where to put final built distribution depending on versioning
    dst_path = os.path.join(pkg_dir, cu_dir)

    # Copy wheel
    try:
        copy2(src=os.path.join(whl_path), dst=dst_path)
    except OSError as err:
        if err.errno == errno.ENOENT:
            os.makedirs(dst_path)
            copy2(src=os.path.join(whl_path), dst=dst_path)
        else:
            raise err

    # Symlink last git revision version to short version
    try:
        os.symlink(pkg_dir, link_dir)
    except OSError as err:
        if err.errno == errno.EEXIST:
            os.remove(link_dir)
            os.symlink(pkg_dir, link_dir)
        else:
            raise err
