"""
Utils for file manipulations like extracting file name from path
"""
import base64
import io
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Union, Iterable, Tuple
from urllib.parse import urlencode, quote

DirectoryName = str
Directory = Tuple[DirectoryName, Iterable['FileAttachment']]


@dataclass
class FileAttachment:
    """
    Class for file abstraction
    """

    name: str
    content: bytes = field(repr=False)

    def __post_init__(self) -> None:
        """Normalize name"""
        self.name = normalize_name(self.name)

    @property
    def name_without_extension(self) -> str:
        """
        >>> FileAttachment("sample.py", b"").name_without_extension
        'sample'
        """
        return self.name.rsplit(".", 1)[0]

    @property
    def extension(self) -> str:
        """
        >>> FileAttachment("sample.py", b"").extension
        'py'
        """
        return self.name.rsplit(".", 1)[-1]

    @property
    def content_stream(self) -> io.BytesIO:
        """Return file attachment content as bytes stream"""
        return io.BytesIO(self.content)

    @property
    def content_base64(self) -> bytes:
        """Convert content to base64 binary string"""
        return base64.b64encode(self.content)

    @property
    def content_disposition(self) -> Dict[str, str]:
        """
        Convert file name to urlencoded Content-Disposition header

        >>> FileAttachment("sample.py", b"").content_disposition
        {'Content-Disposition': 'attachment; filename=sample.py'}
        >>> FileAttachment("98 - February 2019.zip", b"").content_disposition
        {'Content-Disposition': 'attachment; filename=98%20-%20February%202019.zip'}
        """
        file_name = urlencode({"filename": self.name}, quote_via=quote)
        return {"Content-Disposition": f'attachment; {file_name}'}

    @property
    def content_json(self) -> Dict:
        """Return content as dict with base64 content"""
        return {"file": self.content_base64.decode("utf-8")}

    @property
    def mimetype(self) -> str:
        """
        Guess mimetype by extension.
        """
        if self.extension == "json":
            return "application/json"
        if self.extension == "zip":
            return "application/zip"

        return "application/octet-stream"

    def save(self, path: Optional[str] = None) -> None:
        """
        Save file to disk
        """
        path = path or self.name
        with open(path, "wb") as f:
            f.write(self.content)

    @classmethod
    def load(cls, path: str) -> 'FileAttachment':
        """
        Load file from disk
        """
        assert os.path.exists(path), f'No such file: "{path}"'
        with open(path, "rb") as f:
            return FileAttachment(extract_file_name(path), f.read())

    @classmethod
    def load_from_base64(cls, base64_str: Union[str, bytes], name: str) -> 'FileAttachment':
        """
        Load file from base64 string
        """
        return FileAttachment(name, base64.b64decode(base64_str))


def extract_file_name(path: str) -> str:
    """
    Extract file name from path, works to directories too
    >>> extract_file_name("tests/test_api.py")
    'test_api.py'
    >>> extract_file_name("tests/test")
    'test'
    """
    return os.path.basename(path)


def normalize_name(raw_name: str, with_file_name_extract: bool = True) -> str:
    """
    Extract file name, remove restricted chars

    >>> normalize_name('op/"oppa".txt')
    'oppa.txt'
    >>> normalize_name('op/"oppa".txt', with_file_name_extract=False)
    'opoppa.txt'
    """
    name = extract_file_name(raw_name) if with_file_name_extract else raw_name
    for restricted in r'\/:*?"<>|':
        name = name.replace(restricted, "")
    return name


def list_dir_files(directory: str) -> Directory:
    """List directory files, return Directory"""
    paths = os.listdir(directory)
    full_paths = [os.path.join(directory, path) for path in paths]
    files = [FileAttachment.load(path) for path in full_paths if os.path.isfile(path)]
    return extract_file_name(directory), files
