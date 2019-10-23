"""This module provide classes and functions for reading/writing AnyDirectory."""
import os
from collections import namedtuple

from azureml.studio.core.io.visualizer import Visualizer
from azureml.studio.core.utils.yamlutils import dump_to_yaml_file, load_yaml_file

_META_FILE_PATH = '_meta.yaml'


class DirectoryIOError(Exception):
    MSG_TPL = "Error occurs when saving/loading the directory '{dir_name}', root cause: '{original_error}'."

    def __init__(self, dir_name, original_error):
        super().__init__(self.MSG_TPL.format(dir_name=dir_name, original_error=original_error))


class DirectorySaveError(DirectoryIOError):
    MSG_TPL = "Error occurs when saving the directory '{dir_name}', root cause: '{original_error}'."


class DirectoryLoadError(DirectoryIOError):
    MSG_TPL = "Error occurs when loading the directory '{dir_name}', root cause: '{original_error}'."


def make_immutable_tuple(kv):
    """Make an ImmutableTuple with kv data."""
    # In python3.6 the name of the namedtuple cannot be 'tuple', in this case, when calling copy.deepcopy,
    # it will wrongly call the method __getnewargs__ of built-in tuple, then raise very strange exception.
    # This issue is fixed in python3.7.
    MutableTuple = namedtuple('MutableTuple', kv.keys())

    class ImmutableTuple(MutableTuple):
        def _replace(self, **kwargs):
            # Overwrite the _replace method in namedtuple to make sure the data is immutable.
            raise AttributeError('Attributes in ImmutableTuple is immutable.')
    return ImmutableTuple(**kv)


class AnyDirectory:
    """An AnyDirectory may store anything in the directory."""
    TYPE_NAME = 'AnyDirectory'
    # The attribute __getstate__ is used in deepcopy when calling __reduce_ex__.
    # Todo: update the design of AnyDirectory to avoid the hack here.
    RESERVED_ATTRS = {'_meta', '_attrs', '__getstate__'}

    def __init__(self, meta, **attrs):
        """Initialize the directory with meta and attributes. The keys in meta and attributes should not be overlapped.

        :param meta: The meta data that will be stored in the meta file, immutable once the directory is initialized.
        :param attrs: The attributes that won't be stored in meta.
        """
        # Use immutable_tuple to make sure the meta is immutable.
        self._meta = make_immutable_tuple(meta)
        self._attrs = attrs

    def __getattr__(self, name):
        """Overwrite __getattr__ so the attributes can be got from _meta and _attrs."""
        if name in self.RESERVED_ATTRS:
            return super().__getattribute__(name)
        if name in self._attrs:
            return self._attrs[name]
        return getattr(self._meta, name, None)

    def __setattr__(self, name, value):
        """Overwrite __setattr__ to make sure the attributes can only be set once."""
        if name in self.RESERVED_ATTRS:
            if hasattr(self, name):
                raise AttributeError(f"Attribute {name} cannot be modified.")
            super().__setattr__(name, value)
            return
        if name in self._attrs:
            raise AttributeError(f"Attribute {name} is already in attrs.")
        self._attrs[name] = value

    @classmethod
    def create_meta(cls, visualizers: list = None, extensions: dict = None):
        """Create meta data with visualizers and extensions.

        :param visualizers: Each visualizer is inherited from Visualizer and used for dumping visualization data.
        :param extensions: Any other extended data, should be able to be serialized by yaml.
        """
        meta = {
            'type': cls.TYPE_NAME,
        }

        if not visualizers:
            visualizers = []
        visualizations = []
        for visualizer in visualizers:
            if not isinstance(visualizer, Visualizer):
                raise TypeError(f"Expected type: {Visualizer.__name__}, got {visualizer.__class__.__name__}")
            visualizations.append({
                'type': visualizer.type,
                'path': visualizer.path,
            })
        if visualizations:
            meta['visualization'] = visualizations

        if not extensions:
            extensions = {}
        meta['extension'] = extensions

        return meta

    @classmethod
    def create(cls, visualizers: list = None, extensions: list = None):
        """Create an AnyDirectory instance with visualizers and extensions."""
        return AnyDirectory(cls.create_meta(visualizers, extensions), visualizers=visualizers)

    def dump(self, save_to, meta_file_path=None):
        """Dump the visualization data in the directory 'save_to' and store the yaml file for meta.

        :param save_to: The path of the directory to dump data.
        :param meta_file_path: The relative path of the meta file, use the default path if it is None.
        """
        if not meta_file_path:
            meta_file_path = _META_FILE_PATH
        if self.visualizers:
            for visualizer in self.visualizers:
                visualizer.dump(save_to)

        dump_to_yaml_file(dict(self._meta._asdict()), os.path.join(save_to, meta_file_path))

    def get_extension(self, key, default_value=None):
        return None if self.extension is None else self.extension.get(key, default_value)

    def update_extension(self, key, val, override=False):
        if not override and key in self.extension:
            raise KeyError(f"Key '{key}' already exists in extension.")
        self.extension[key] = val

    def __repr__(self):
        return f"{self.TYPE_NAME}(meta={self._meta})"

    @classmethod
    def load(cls, load_from_dir, meta_file_path=None):
        """Load the directory as an AnyDirectory instance.

        :param load_from_dir: The path of the directory to load.
        :param meta_file_path: The relative path of the meta file, use the default path if it is None.
        :return: An instance of AnyDirectory
        """
        if not meta_file_path:
            meta_file_path = _META_FILE_PATH
        if not os.path.exists(load_from_dir):
            raise FileNotFoundError(f"Not a valid load path: {load_from_dir}")
        full_meta_path = os.path.join(load_from_dir, meta_file_path)
        if not os.path.isfile(full_meta_path):
            raise FileNotFoundError(f"Meta file {full_meta_path} is not a valid file.")
        meta = load_yaml_file(full_meta_path)
        if 'extension' not in meta:
            meta['extension'] = {}
        dir_type_in_meta = meta.get('type')
        if not dir_type_in_meta:
            raise TypeError(f"Not a valid meta file, required field 'type' not found.")

        directory = cls(meta)
        if cls != AnyDirectory:
            # If the class is not AnyDirectory, make sure the type in meta is the same.
            directory.assert_type()
        # Todo: load visualizations and other data described in yaml to make sure a loaded directory can be dumped.
        return directory

    def assert_type(self):
        """Make sure the directory type is the same as the type in meta."""
        if self.TYPE_NAME != self.type:
            raise TypeError(f"Type not match, instance type='{self.TYPE_NAME}', type in meta='{self.type}'")


def has_meta(load_from_dir, meta_file_path=_META_FILE_PATH):
    meta_path = os.path.join(load_from_dir, meta_file_path)
    return os.path.exists(meta_path) and os.path.isfile(meta_path)
