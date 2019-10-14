# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import hashlib
import os
from azureml._project.ignore_file import get_project_ignore_file


class _ModuleBuilder(object):
    """Create a _ModuleBuilder

    :param context: context object
    :type context: _GraphContext
    :param module_def: module def object
    :type module_def: ModuleDef
    :param snapshot_root: folder path that contains the script and other files of module.
        Place .amlignore or .gitignore file of your module here. All paths listed
        in .amlignore or .gitignore will be excluded from snapshot and hashing.
    :type snapshot_root: str
    :param additional_hash_paths: Additional paths(other than snapshot_root) to hash when
        checking for changes to the contents of module. By default contents of the snaphsot_root
        is hashed (except filed under .amlignore or .gitignore).
    :type additional_hash_paths: list
    :param existing_snapshot_id: guid of an existing snapshot. Specify this if the module wants to
        point to an existing snapshot.
    :type existing_snapshot_id: str
    """

    def __init__(self, context, module_def, snapshot_root=None,
                 additional_hash_paths=None, existing_snapshot_id=None):
        """Initializes _ModuleBuilder."""
        self._content_path = snapshot_root
        self._additional_hash_paths = additional_hash_paths or []
        self._module_provider = context.workflow_provider.module_provider
        self._module_def = module_def
        self._existing_snapshot_id = existing_snapshot_id

    def get_fingerprint(self):
        """
        Calculate and return a deterministic unique fingerprint for the module
        :return: fingerprint
        :rtype str
        """
        fingerprint = _ModuleBuilder.calculate_hash(self._module_def, self._content_path, self._additional_hash_paths)
        return fingerprint

    def build(self):
        """
        Build the module and register it with the provider
        :return: module_id
        :rtype str
        """
        fingerprint = self.get_fingerprint()

        if self._existing_snapshot_id:
            module_id = self._module_provider.create_module(
                module_def=self._module_def, existing_snapshot_id=self._existing_snapshot_id, fingerprint=fingerprint)
        else:
            module_id = self._module_provider.create_module(
                module_def=self._module_def, content_path=self._content_path, fingerprint=fingerprint)

        return module_id

    @property
    def module_def(self):
        return self._module_def

    @staticmethod
    def _path_not_excluded(file_path, exclude_function=None):
        return (not exclude_function or
                (exclude_function and not exclude_function(os.path.normpath(file_path))))

    @staticmethod
    def _flatten_hash_paths(hash_paths, content_path=None):
        all_paths = set()

        for hash_path in hash_paths:
            if os.path.exists(hash_path):
                all_paths.add(hash_path)
            elif content_path and os.path.exists(os.path.join(content_path, hash_path)):
                all_paths.add(os.path.join(content_path, hash_path))
            else:
                raise ValueError(
                    "path not found %s. Specify absolute paths or a path relative to the `source_directory`"
                    % hash_path)

        return list(all_paths)

    @staticmethod
    def _hash_from_file_paths(hash_src):
        if len(hash_src) == 0:
            hash = "00000000000000000000000000000000"
        else:
            hasher = hashlib.md5()
            for f in hash_src:
                with open(str(f), 'rb') as afile:
                    buf = afile.read()
                    hasher.update(buf)
            hash = hasher.hexdigest()
        return hash

    @staticmethod
    def _default_content_hash_calculator(hash_paths, exclude_function=None):
        hash_src = []
        for hash_path in hash_paths:
            if os.path.isfile(hash_path):
                if _ModuleBuilder._path_not_excluded(hash_path, exclude_function):
                    hash_src.append(hash_path)
            elif os.path.isdir(hash_path):
                if _ModuleBuilder._path_not_excluded(hash_path, exclude_function):
                    for root, dirs, files in os.walk(hash_path, topdown=True):
                        hash_src.extend([os.path.join(root, name)
                                         for name in files
                                         if _ModuleBuilder._path_not_excluded(os.path.join(root, name),
                                                                              exclude_function)])
            else:
                raise ValueError("path not found %s" % hash_path)

        hash = _ModuleBuilder._hash_from_file_paths(hash_src)
        return hash

    @staticmethod
    def calculate_hash(module_def, content_path=None, hash_paths=None):
        module_hash = module_def.calculate_hash()
        hash_paths = hash_paths or []

        exclude_function = None
        if content_path:
            hash_paths.append(content_path)
            ignore_file = get_project_ignore_file(content_path)
            exclude_function = ignore_file.is_file_excluded

        if hash_paths:
            hash_paths = _ModuleBuilder._flatten_hash_paths(hash_paths, content_path)
            content_hash = _ModuleBuilder._default_content_hash_calculator(hash_paths, exclude_function)
            module_hash = module_hash + "_" + content_hash

        return module_hash
