import os

from azureml.studio.core.io.any_directory import AnyDirectory
from azureml.studio.common.io.pickle_utils import read_with_pickle_from_file


class TransformDirectory(AnyDirectory):
    TYPE_NAME = 'TransformationDirectory'

    @classmethod
    def create(cls, file_path=None, visualizers=None, extensions=None):
        meta = cls.create_meta(visualizers, extensions)
        meta['file_path'] = file_path
        return cls(meta, visualizers=visualizers)

    @classmethod
    def load(cls, load_from_dir, meta_file_path=None):
        directory = super().load(load_from_dir, meta_file_path)
        directory.data = read_with_pickle_from_file(os.path.join(load_from_dir, directory.file_path))
        return directory


def save_transform_to_directory(save_to, file_path, meta_file_path=None,
                                **kwarg,
                                ):
    TransformDirectory.create(file_path=file_path, **kwarg).dump(save_to, meta_file_path)


def load_transform_from_directory(load_from_dir):
    return TransformDirectory.load(load_from_dir)
