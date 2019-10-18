"""
Utils for working with zip archives
"""
import io
from typing import Union, Iterable, Sequence
from zipfile import ZipFile

from docci.file import FileAttachment, Directory

RawZipFile = Union[str, bytes, io.BytesIO, ZipFile, FileAttachment]


def raw_to_zip(raw_zip_file: RawZipFile) -> ZipFile:
    """
    Convert path, bytes, stream, FileAttachment to ZipFile.
    """
    if isinstance(raw_zip_file, ZipFile):
        return raw_zip_file

    if isinstance(raw_zip_file, bytes):
        return ZipFile(io.BytesIO(raw_zip_file))

    if isinstance(raw_zip_file, FileAttachment):
        return ZipFile(raw_zip_file.content_stream)

    if isinstance(raw_zip_file, (str, io.BytesIO)):
        return ZipFile(raw_zip_file)


def list_zip_files(raw_zip_file: RawZipFile) -> Sequence[FileAttachment]:
    """
    List zip archive files
    """

    def zip_file_generator(zip_file: ZipFile) -> Iterable[FileAttachment]:
        for filename in zip_file.namelist():
            content = zip_file.read(filename)
            yield FileAttachment(filename, content)

    zip_file = raw_to_zip(raw_zip_file)

    return list(zip_file_generator(zip_file))


def zip_files(zip_name: str, files: Iterable[FileAttachment]) -> FileAttachment:
    """Zip files to archive with {zip_name}"""
    stream = io.BytesIO()

    with ZipFile(stream, mode="w") as zf:
        for file in files:
            zf.writestr(file.name, file.content)

    return FileAttachment(zip_name, stream.getvalue())


def zip_dirs(zip_name: str, dirs: Iterable[Directory]) -> FileAttachment:
    """Zip folders into single zip archive with {zip_name}"""
    stream = io.BytesIO()

    with ZipFile(stream, mode="w") as zf:
        for folder_name, folder_files in dirs:
            for file in folder_files:
                zf.writestr(f"{folder_name}/{file.name}", file.content)

    return FileAttachment(zip_name, stream.getvalue())
