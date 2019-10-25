import io
import os
import yaml
import tarfile
import os.path as osp


def write_tar(tar, path, obj):
    serialized_obj = yaml.dump(
        obj, encoding='utf-8', default_flow_style=False,
        Dumper=yaml.CSafeDumper
    )
    info = tarfile.TarInfo(path)
    info.size = len(serialized_obj)
    tar.addfile(info, io.BytesIO(serialized_obj))


def save_data(fpath, _write=True, **data):
    """
    Save data in a tar:bz2 file.

    :param fpath:
        File path to save the data or stream.
    :type fpath: str | io.BytesIO

    :param data:
        Data to be saved.
    :type data: object

    :rtype:
        File path to save the data or stream.
    :rtype: str | io.BytesIO
    """
    if isinstance(fpath, str):
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with tarfile.open(mode='w:bz2', fileobj=get_fileobj(fpath)) as tar:
        for k, v in data.items():
            write_tar(tar, k, v)
    return fpath


def get_fileobj(fpath):
    if isinstance(fpath, str):
        if not osp.isfile(fpath):
            return fpath
        with open(fpath, 'rb') as f:
            return io.BytesIO(f.read())
    if isinstance(fpath, io.BytesIO):
        return fpath
    from werkzeug.datastructures import FileStorage
    if isinstance(fpath, FileStorage):
        return io.BytesIO(fpath.stream.read())


def get_filename(fpath):
    if isinstance(fpath, str):
        return os.path.basename(fpath)
    from werkzeug.datastructures import FileStorage
    if isinstance(fpath, FileStorage):
        return fpath.filename


def load_data(file):
    data = {}
    with tarfile.open(mode='r:bz2', fileobj=get_fileobj(file)) as tar:
        for member in tar.getmembers():
            with tar.extractfile(member) as f:
                data[member.name] = yaml.load(f.read(), Loader=yaml.CLoader)
    return data
