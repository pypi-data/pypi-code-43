import os

from cgshop2020_pyutils import InstanceReader, Instance


class InstanceDatabase:
    """
    This class allows to easily read instances from a folder if the instance files
    follow the naming convention 'instance-name.instance.json'. It allows subfolder
    but no symbolic links.
    """

    def __init__(self, path: str, cache: bool = True):
        """
        Create an InstanceDatabase that searches in a specified folder for instances.
        :param path: Path to the folder that contains the instance files (e.g. the folder
                        that contains the extracted zips). The instance files can be
                        in subfolders but have the names have to be NAME.instance.json.
        :param cache: Should the loaded instances be cached?
        """
        self._path = path
        self._cache = {}
        self._reader = InstanceReader()
        if not os.path.exists(path):
            raise ValueError(f"The folder {os.path.abspath(path)} does not exist")

    def _filename_fits_name(self, filename, name):
        if not self._filename_fits_instance_convention(filename):
            return False
        split = filename.split(".")
        return split[0] == name

    def _filename_fits_instance_convention(self, filename):
        split = filename.split(".")
        if len(split) != 3:
            return False
        return split[1] == "instance" and split[2] == "json"

    def _cache_and_return(self, instance):
        self._cache[instance.name] = instance
        return instance

    def _iterate_paths(self):
        for root, dirs, files in os.walk(self._path):
            for file in files:
                if self._filename_fits_instance_convention(file):
                    path = os.path.join(self._path, root, file)
                    yield path

    def _find_path(self, name):
        for instance_path in self._iterate_paths():
            if self._filename_fits_name(os.path.split(instance_path)[-1], name):
                return instance_path
        raise KeyError(f"Did not find a suitable file for {name} in {self._path}")

    def _extract_instance_name_from_path(self, path):
        filename = os.path.split(path)[1]
        return filename.split(".")[0]

    def __iter__(self) -> Instance:
        """
        Iterate over all instance files.
        :return: Instance objects
        """
        for instance_path in self._iterate_paths():
            instance_name = self._extract_instance_name_from_path(instance_path)
            if instance_path in self._cache:
                yield self._cache[instance_name]
            else:
                yield self._cache_and_return(self._reader.from_json(instance_path))

    def __getitem__(self, name: str) -> Instance:
        """
        Returns the instance of a specific name or throws an KeyError.
        :param name: Name of the instance.
        :return:
        """
        if name is self._cache:
            return self._cache[name]
        path = self._find_path(name)
        return self._cache_and_return(self._reader.from_json(path))
