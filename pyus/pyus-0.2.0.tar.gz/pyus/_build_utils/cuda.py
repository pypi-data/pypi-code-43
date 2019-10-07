import subprocess
import re


def check_cuda_version(cuda_version_arg=None):
    """Check CUDA version from installation in standard location i.e. /usr/local/"""
    # TODO: add /opt as possible installation location

    cu_versions = subprocess.run(['ls', '/usr/local/'],
                                 stdout=subprocess.PIPE).stdout.decode('utf-8')
    cu_versions = re.findall(r"(cuda-{1}[0-9]+\.?[0-9]+)", cu_versions)
    cu_versions_number = [v.replace('cuda-', '') for v in cu_versions]

    # if cuda_version_arg is not None:
    if cuda_version_arg not in [None, '']:

        if re.match(r"((cuda-)?[0-9]+\.?[0-9]+)", cuda_version_arg):
            cuda_version_nb = \
            re.search(r"([0-9]+\.?[0-9]+)", cuda_version_arg)[0]

            if cuda_version_nb in cu_versions_number:
                CUDA_INCLUDE_PATH = '/usr/local/cuda-{}/include'.format(cuda_version_nb)
                CUDA_VERSION = cuda_version_nb.replace('.', '')
            else:
                raise ValueError(
                    'CUDA {} is not installed'.format(cuda_version_arg)
                )
        else:
            raise ValueError(
                "Invalid CUDA version '{}'.\n"
                "Please provide it as cuda-x.y or x.y".format(cuda_version_arg)
            )
    else:
        if len(cu_versions_number) == 0:
            raise ValueError('No CUDA installation found in /usr/local')
        elif len(cu_versions_number) == 1:
            CUDA_INCLUDE_PATH = '/usr/local/cuda-{}/include'.format(cu_versions_number[0])
            CUDA_VERSION = cu_versions_number[0].replace('.', '')
        else:
            raise ValueError(
                "Multiple CUDA installations found in /usr/local: {}\n "
                # "Use the '--cuda-version' argument to specify the desired "
                "Use the 'CUDA_VERSION' environment variable to specify the desired "
                "version of pyus".format(cu_versions)
            )

    return CUDA_VERSION, CUDA_INCLUDE_PATH
