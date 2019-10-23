"""This module provide classes and functions for reading/writing ModelDirectory."""
import os
import pickle

from azureml.studio.core.io.any_directory import AnyDirectory
from azureml.studio.core.utils.yamlutils import load_yaml_file, dump_to_yaml_file
from azureml.studio.core.utils.fileutils import ensure_folder

MODEL_SPEC_FILE = 'model_spec.yaml'


class ModelDirectory(AnyDirectory):
    """A ModelDirectory could store a machine learning model described by model spec."""
    TYPE_NAME = 'ModelDirectory'

    @classmethod
    def create(cls, model_dumper=None, visualizers=None, extensions=None):
        """A ModelDirectory is initialized by a model_dumper and other meta data.

        :param model_dumper: A function to write model by calling model_dumper(save_to),
                             it should return a spec dict to describe the specifications of the model.
        :param visualizers: See AnyDirectory
        :param extensions: See AnyDirectory
        """
        meta = super().create_meta(visualizers, extensions)
        meta['model'] = MODEL_SPEC_FILE
        return cls(meta, visualizers=visualizers, model_dumper=model_dumper)

    def dump(self, save_to, meta_file_path=None):
        """Dump the model to the directory 'save_to' and dump other meta data. Params are the same as AnyDirectory."""
        spec = self.model_dumper(save_to) or {}
        dump_to_yaml_file(spec, os.path.join(save_to, self.model))
        super().dump(save_to)

    @property
    def model_spec_file(self):
        return self._meta.get('model', MODEL_SPEC_FILE)

    @classmethod
    def load(cls, load_from_dir, meta_file_path=None, model_loader=None):
        """Load the directory as a ModelDirectory.

        :param load_from_dir: See AnyDirectory
        :param meta_file_path: See AnyDirectory
        :param model_loader: A function to load the model. Todo: Load the model according to meta data.
        :return: See AnyDirectory
        """
        directory = super().load(load_from_dir, meta_file_path=meta_file_path)
        spec = load_yaml_file(os.path.join(load_from_dir, directory.model))
        if model_loader:
            directory.data = model_loader(load_from_dir, spec)
        return directory


def save_model_to_directory(save_to, model_dumper,
                            visualizers=None, extensions=None,
                            meta_file_path=None,
                            ):
    """Save a model to the specified folder 'save_to' with AnyDirectoryDirectory.dump()."""
    ModelDirectory.create(model_dumper, visualizers, extensions).dump(save_to, meta_file_path)


def load_model_from_directory(load_from_dir, meta_file_path=None, model_loader=None):
    """Load a model in the specified folder 'load_from_dir' with ModelDirectory.load()."""
    return ModelDirectory.load(load_from_dir, meta_file_path, model_loader)


def pickle_loader(load_from_dir, model_spec):
    """Load the pickle model by reading the file indicated by file_name in model_spec."""
    file_name = model_spec['file_name']
    with open(os.path.join(load_from_dir, file_name), 'rb') as fin:
        return pickle.load(fin)


def pickle_dumper(data, file_name=None):
    """Return a dumper to dump a model with pickle."""
    if not file_name:
        file_name = '_data.pkl'

    def model_dumper(save_to):
        full_path = os.path.join(save_to, file_name)
        ensure_folder(os.path.dirname(os.path.abspath(full_path)))
        with open(full_path, 'wb') as fout:
            pickle.dump(data, fout)

        model_spec = {'model_type': 'pickle', 'file_name': file_name}
        return model_spec
    return model_dumper
