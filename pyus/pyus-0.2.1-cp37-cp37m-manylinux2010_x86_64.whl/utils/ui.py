import os
import urllib.request
import re
from urllib.parse import urlsplit
from tqdm import tqdm
from typing import Union, List, Tuple


def copyfileobj_with_progress(
        fsrc,
        fdst,
        total: int = None,
        length: int = 16*1024
) -> None:
    """Copy data from file-like object fsrc to file-like object fdst.
    Same as `shutil.copyfileobj` with progress bar (link below):
    https://hg.python.org/cpython/file/eb09f737120b/Lib/shutil.py#l64
    :param fsrc: file-like object
    :param fdst: file-like object
    :param total:
    :param length
    :return:
    """
    bar_format = '    {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} {rate_fmt}'
    with tqdm(total=total, unit='B', unit_scale=True, bar_format=bar_format,
              ncols=60) as pbar:
        while True:
            buf = fsrc.read(length)
            if not buf:
                break
            fdst.write(buf)
            pbar.update(len(buf))


def download_file(url: str, fdst):
    """Download data from `url` to file-like object fdst.
    :param url: str
    :param fdst: file-like object
    :return:
    """
    split = urlsplit(url)
    filename = os.path.basename(split.path)

    print('Downloading {}'.format(filename))

    with urllib.request.urlopen(url) as response:
        length = response.getheader('content-length')
        if length:
            total = int(length)
            copyfileobj_with_progress(response, fdst, total=total)


def download_url_list(
        url_list: Union[List[str], Tuple[str, ...]], path: str = '.',
        check=True
) -> None:
    """Download data from `url_list` to `export_path` destination"""

    # Check number of files and total size
    if check:
        info_list = [urllib.request.urlopen(url).info() for url in url_list]
        bytes_list = [float(i['Content-Length']) for i in info_list]
        total_bytes_size = sum(bytes_list)
        # Ask to download
        check_message = (
            'You are about to download {:d} file(s) totaling {}.'
            ' Do you want to proceed ([y]/n)? '.format(
                len(url_list), sizeof_fmt(total_bytes_size)
            )
        )
        usr_in = input(check_message)
        usr_in = usr_in.lower() if usr_in else 'y'  # default: 'y'
        if usr_in.lower() != 'y':
            raise InterruptedError

    # Check if export path already exists and create if necessary
    if not os.path.exists(path):
        os.makedirs(path)

    for file_url in url_list:

        filename = os.path.basename(file_url)
        export_file_path = os.path.abspath(os.path.join(path, filename))

        if not os.path.exists(export_file_path):
            with open(export_file_path, 'wb') as export_file:
                download_file(file_url, export_file)
        else:
            print('{} already exists'.format(export_file_path))


def atoi(text):
    """Convert string to integer"""
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """Sorts in human order using list.sort(key=natural_keys)
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    """
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def sizeof_fmt(num, suffix='B', standard='SI'):
    """Humanized size modified from link below
    Link: https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size#1094933
    """
    if standard.lower() == 'si':
        unit_list = ['','K','M','G','T','P','E','Z']
        last_unit_value = 'Y'
        divisor = 1e3
    elif standard.lower() == 'iec':
        unit_list = ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']
        last_unit_value = 'Yi'
        divisor = 1024.0
    else:
        raise NotImplementedError('Unknow `standard`')

    for unit in unit_list:
        if abs(num) < 1024.0:
            return '{:3.2f} {}{}'.format(num, unit, suffix)
        num /= divisor

    return '{:.2f} {}{}'.format(num, last_unit_value, suffix)


# def check_nvidia_device():
#     try:
#         smi = subprocess.Popen(["nvidia-smi"], stdout=subprocess.PIPE)
#         # output = smi.communicate()[0]  # TODO regex on this to extract list of devices and driver version
#         return True
#     except OSError:
#         return False
#
#
# def check_nvcc():
#     try:
#         nvcc = subprocess.Popen(["nvcc","--version"], stdout=subprocess.PIPE)
#         # output = nvcc.communicate()[0]  # TODO regex on this to extract version of nvcc
#         return True
#     except OSError:
#         return False
