import os
import logging
import atexit
from friendlypics.file_object import FileObj


class ManifestFile(object):
    """Interface for manipulating a friendlypics manifest file"""
    def __init__(self, file_name):
        """
        Args:
            file_name (str): path to the manifest file to parse
        """
        self._log = logging.getLogger(__name__)
        self._file_name = os.path.abspath(file_name)
        self._data = self._parse()

        # Register our save method with the Python runtime to ensure the
        # manifest files always get updated and written to disk
        atexit.register(self._save)

    @property
    def path(self):
        """str: path to the manifest file managed by this object"""
        return os.path.split(self._file_name)[0]

    def _parse(self):
        """dict: Parses the manifest file"""
        retval = dict()

        # If the specified manifest file doesn't exist yet,
        # assume we need to create a new file with an empty dataset
        if not os.path.exists(self._file_name):
            return retval

        with open(self._file_name, "r") as file_handle:
            manifest_version = file_handle.readline().strip()
            if manifest_version != "1.0":
                raise Exception(
                    f"Unsupported manifest version '{manifest_version}' for "
                    f"file {self._file_name}"
                )
            for cur_line in file_handle.readlines():
                if not cur_line.strip():
                    continue
                parts = cur_line.strip().split("\t")
                retval[parts[0]] = parts[1]
        return retval

    def _save(self):
        """Saves the state of the class to the manifest file"""
        self._log.info(f"Saving manifest file {self._file_name}.")
        with open(self._file_name, "w") as file_handle:
            file_handle.write("1.0\n")
            for cur_chksum, cur_file in self._data.items():
                file_handle.write(f"{cur_chksum}\t{cur_file}\n")

    def add_entry(self, file):
        """Adds a new entry to the manifest

        Args:
            file (FileObj): file to reference in the manifest
        """
        self._data[file.checksum] = file.filename

    def find_matches(self, file):
        """Locates any files defined in this manifest that match a source file

        Args:
            file (FileObj): file to locate

        Returns:
            list:
                0 or more files that match either the checksum or the file
                name of the source file. Typically returns 0, 1 or 2 matches. 0
                if there are no similar files in the manifest. 1 if there is
                a file with the same name and/or the same checksum as the source
                file. 2 if there is both a file with the same file name but
                a different checksum AND a file with the same checksum but a
                different filename.
        """
        retval = list()

        for cur_hash, cur_file in self._data.items():
            if cur_file == file.filename or cur_hash == file.checksum:
                retval.append(FileObj(os.path.join(self.path, cur_file)))
        return retval

    def contains(self, file):
        """Checks to see whether a file exists in this manifest

        Args:
            file (FileObj): file to locate

        Returns:
            bool:
                True if there is any file with a matching checksum file to
                the source file tracked by this manifest file, False if not
        """

        retval = file.checksum in self._data
        if retval and file.filename != self._data[file.checksum]:
            self._log.warning(
                f"It appears as though the source file {file.path} has been "
                f"renamed to {self._data[file.checksum]} in the target folder "
                f"{self.path}"
            )
        return retval


if __name__ == "__main__":  # pragma: no cover
    pass
