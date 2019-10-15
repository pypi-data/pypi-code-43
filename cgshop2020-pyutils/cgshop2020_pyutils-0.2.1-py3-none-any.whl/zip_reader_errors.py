from os import path
from zipfile import ZipFile


class ZipReaderError(Exception):
    pass


class InvalidFileName(ZipReaderError):
    def __init__(self, file_name):
        self.file_name = file_name
        super().__init__(f"The ZIP archive contains the invalid file name: '{file_name}'")


class FileTooLargeError(ZipReaderError):
    def __init__(self, file_name, file_size, file_size_limit):
        self.file_name = file_name
        self.file_size = file_size
        self.file_size_limit = file_size_limit
        super().__init__(
            f"The ZIP archive contains the file '{self.file_name}' with a size "
            f"of {self.file_size / 1_000_000} MB (only {self.file_size_limit / 1_000_000} MB allowed)!")


class NoSolutionsError(ZipReaderError):
    def __init__(self):
        super().__init__("The ZIP archive does not appear to contain any solution!")


class InvalidJSONError(ZipReaderError):
    def __init__(self, file_name, message):
        self.file_name = file_name
        super().__init__(f"The ZIP archive contains the file '{file_name}'"
                         f" which is not a valid JSON-encoded file: {message}!")


class InvalidZipError(ZipReaderError):
    def __init__(self, message):
        super().__init__(
            f"The ZIP archive is corrupted and could not be decompressed: {message}!")


class BadZipChecker:
    """
    Check if zip is bad/malicious/corrupted.
    """

    def __init__(self, file_size_limit):
        self.file_size_limit = file_size_limit

    def _is_file_name_okay(self, name):
        return name[0] != "/" and not path.isabs(name) and ".." not in name

    def _check_file_names(self, f: ZipFile):
        for n in f.namelist():
            if not self._is_file_name_okay(n):
                raise InvalidFileName(n)

    def _check_decompressed_sizes(self, f: ZipFile):
        for info in f.filelist:
            if info.file_size > self.file_size_limit:
                raise FileTooLargeError(info.filename, info.file_size,
                                        self.file_size_limit)

    def __call__(self, zip_file):
        self._check_file_names(zip_file)
