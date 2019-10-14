import os
import threading
import time
import hashlib
from blinker import signal, Signal  # type: ignore
from enum import Enum
from typing import Dict, Any, Optional, List
from requests import Response

from qmenta.core import platform, errors
from qmenta.core.upload import prepare


"""
Handles the uploading of data to QMENTA platform.
"""


class UploadError(errors.Error):
    """
    When a problem occurs while uploading.
    """
    pass


class UploadAlreadyStartedError(UploadError):
    """
    When calling upload_file() a second time and the upload is already
    in progress.
    """


class UploadAlreadyDoneError(UploadError):
    """
    When calling upload_file() a second time and the upload already finished.
    """
    pass


class FileInfo:
    """
    Specifies the metadata of a file that will be uploaded to the platform.

    Parameters
    ----------
    project_id : int
        The ID of the project to which the new file will be added
    name : str
        The name of the file in the platform. It is recommended to use the
        filename (optional)
    date_of_scan : str
        The date when the scan was made (optional)
    description : str
        A description of the data that is uploaded (optional)
    subject_name : str
        The anonymised ID of the subject (optional)
    session_id : str
        The ID of the scanning session for the subject (optional).
        If left blank, the next numerical session ID for the subject will
        automatically be assigned to the session by the platform.
    input_data_type : str
        The analysis to be used to process the data (optional).
        When left blank, the input data type will be set automatically.
        It is recommended to leave it blank, except for testing specific tools
        for processing uploaded data.
    is_result : bool
        Default value: False. Set to True if the uploaded data is the output
        of an offline analysis.
    add_to_container_id : int
        ID of the container to which this file should be added (if id > 0).
        Default value: 0. When the value is 0, the data will be added to
        a new container.
    split_data : bool
        If True, the platform will try to split the uploaded file into
        different sessions. It will be ignored when the session_id is given.
        Default value: False.
    """
    def __init__(
        self, project_id: int, name: str = '', date_of_scan: str = '',
        description: str = '', subject_name: str = '', session_id: str = '',
        input_data_type: str = '', is_result: bool = False,
        add_to_container_id: int = 0, split_data: bool = False
    ) -> None:
        self.project_id = project_id
        self.name = name
        self.date_of_scan = date_of_scan
        self.description = description
        self.subject_name = subject_name
        self.session_id = session_id

        if input_data_type:
            self.input_data_type = input_data_type
        else:
            if is_result:
                self.input_data_type = 'offline_analysis:1.0'
            else:
                self.input_data_type = 'qmenta_mri_brain_data:1.0'

        self.is_result = is_result
        self.add_to_container_id = add_to_container_id

        if session_id:
            self.split_data = False
        else:
            self.split_data = split_data

    def __repr__(self):
        return 'FileInfo({})'.format(self.__dict__)

    def __eq__(self, other):
        if not isinstance(other, FileInfo):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        if not isinstance(other, FileInfo):
            return True
        return self.__dict__ != other.__dict__


class UploadStatus(Enum):
    """
    The current stage of a SingleUpload in the uploading process.
    """
    TO_ZIP = 0
    TO_ZIP_AND_ANONYMISE = 1
    ZIPPING = 2
    TO_ANONYMISE = 3
    ANONYMISING = 4
    TO_UPLOAD = 5
    UPLOADING = 6
    TO_CLEAN = 7
    DELETING_TMP_FILES = 8
    DONE = 9
    FAILED = 10


class SingleUpload():
    """
    Class to upload a single ZIP file to the platform.
    When there is a failure in initializing the instance,
    status will be set to FAILED, and a status_message will
    be set.

    Parameters
    ----------
    auth : Auth
        The object used to authenticate to the QMENTA platform.
    path : str
        The input directory or file that will be zipped (optional),
        anonymised (optional) and uploaded.
    file_info : FileInfo
        All the metadata for the file to be stored in the platform.
    anonymise : bool
        If set, a new zip file will be created with the same name which
        contains the anonymised version of the data of the original
        zip file. The new zip file will be uploaded instead of the original
        one. Default value: True.
    upload_index : int
        This value will be passed to the 'upload-status' and 'upload-progress'
        signals. It is set by MultipleThreadedUploads and used to quickly
        identify the upload that was updated. Default value: -1.
    keep_created_files : bool
        Keep the files containing the zipped directory and anonymised data
        after the upload finished. When set to False, the ``qm-*.zip`` files
        that were created by this SingleUpload will be deleted when the upload
        if finished. Default value: True.

    Attributes
    ----------
    input_filename : str
        The file that will be anonymised (optional), and uploaded.
    upload_filename : str
        The file that will be uploaded. If anonymisation is disabled, this
        will be the same as filename. With anonymisation enabled, a new file
        will be created that contains the anonymised data.
    upload_id : str
        The upload session ID. This will be automatically generated and
        depends on the current time and the upload filename.
    chunk_size : int
        Size in bytes of each chunk. Should be expressed as a power of 2.
        Default value is 512 KB.
        It is recommended to use the default value. We expose the variable
        to speed up unit tests with tiny file sizes.
    file_size : int
        The size in bytes of the file to be uploaded. Automatically determined
        when the SingleUpload object is constructed.
    status_message : str
        In case the status becomes FAILED, status_message will contain a
        message indicating what went wrong.

    Raises
    ------
    errors.CannotReadFileError
        When the input cannot be read
    """

    # Only run a single anonymisation at once to prevent using too many
    #   computer resources, and to prevent reading/writing from/to the same
    #   file in multiple threads.
    _anon_lock: threading.Lock = threading.Lock()

    def __init__(self, auth: platform.Auth, path: str, file_info: FileInfo,
                 anonymise: bool = True, upload_index: int = -1,
                 keep_created_files: bool = True) -> None:
        self.auth = auth
        self.path = path
        self.file_info = file_info
        self.upload_index = upload_index
        self.keep_created_files = keep_created_files
        self._created_files_list: List[str] = []

        self.chunk_size: int = (2 ** 9) * 1024

        # file_size will be set in _check_type_and_size if the original file
        #   will be uploaded, or after anonymisation when anonymise == True.
        self.file_size: int = -1
        self._bytes_uploaded: int = 0

        self._status_signal: Signal = signal('upload-status')
        self._progress_signal: Signal = signal('upload-progress')

        self._status: UploadStatus
        self.upload_filename: str

        if os.path.isfile(self.path):
            self.input_filename = self.path
            if anonymise:
                self.upload_filename = ''  # to be set when anonymising
                self._status = UploadStatus.TO_ANONYMISE
            else:
                self.upload_filename = self.input_filename
                self._status = UploadStatus.TO_UPLOAD

        elif os.path.isdir(self.path):
            self.input_filename = ''  # to be set when zipping
            self.upload_filename = ''
            if anonymise:
                self._status = UploadStatus.TO_ZIP_AND_ANONYMISE
            else:
                self._status = UploadStatus.TO_ZIP
        else:
            raise errors.CannotReadFileError(
                'Cannot read input zip file or directory: {}'.format(self.path)
            )

        self.status_message: str = ''
        self.upload_id: str = ''

    def _get_upload_id(self, file_path: str) -> str:
        m = hashlib.md5()
        m.update(str(file_path).encode("utf-8"))
        return str(time.time()).replace(".", "") + "_" + m.hexdigest()

    @property
    def status(self) -> UploadStatus:
        """
        UploadStatus: The current status of the upload.
        Setting the status will trigger signal('upload-status').
        """
        return self._status

    @status.setter
    def status(self, value: UploadStatus) -> None:
        if self._status != value:
            self._status = value
            self._status_signal.send(self, upload_index=self.upload_index)

    @property
    def bytes_uploaded(self) -> int:
        """
        int: The amount of bytes that has been uploaded so far.
        When the value is updated, signal('upload-progress') is sent.
        """
        return self._bytes_uploaded

    @bytes_uploaded.setter
    def bytes_uploaded(self, value: int) -> None:
        if self._bytes_uploaded != value:
            self._bytes_uploaded = value
            self._progress_signal.send(self, upload_index=self.upload_index)

    def _add_upload_info_to_request_headers(
        self, upload_info: FileInfo, headers: Dict[str, Any] = {}
    ):
        headers["X-Mint-Name"] = upload_info.name
        headers["X-Mint-Date"] = upload_info.date_of_scan
        headers["X-Mint-Description"] = upload_info.description
        headers["X-Mint-Patient-Secret"] = upload_info.subject_name
        headers["X-Mint-SSID"] = upload_info.session_id
        headers["X-Mint-Project-Id"] = str(upload_info.project_id)
        headers["X-Mint-Split-Data"] = str(int(upload_info.split_data))

        if upload_info.input_data_type:
            headers["X-Mint-Type"] = upload_info.input_data_type

            if upload_info.is_result:
                headers["X-Mint-In-Out"] = "out"
            else:
                headers["X-Mint-In-Out"] = "in"

        if upload_info.add_to_container_id > 0:
            headers["X-Mint-Add-To"] = str(upload_info.add_to_container_id)
        return headers

    def start(self) -> None:
        """
        Check that the file was not uploaded yet, anonymise it if needed,
        and upload the (anonymised) file.
        When there is a failure in anonymising or uploading, status
        will be set to FAILED and a status_message is set.

        Raises
        ------
        UploadAlreadyDoneError
        UploadAlreadyStartedError
        prepare.FileError
        """
        if self.status in [UploadStatus.FAILED, UploadStatus.DONE]:
            raise UploadAlreadyDoneError(self.input_filename)
        elif self.status == UploadStatus.UPLOADING:
            raise UploadAlreadyStartedError(self.input_filename)

        to_zip: bool = self.status in [
            UploadStatus.TO_ZIP, UploadStatus.TO_ZIP_AND_ANONYMISE
        ]
        to_anonymise: bool = self.status in [
            UploadStatus.TO_ZIP_AND_ANONYMISE, UploadStatus.TO_ANONYMISE
        ]

        try:
            if to_zip:
                self._zip_directory()

            if to_anonymise:
                self._anonymise_zip_file()
            else:
                self.upload_filename = self.input_filename

            self.upload_id = self._get_upload_id(self.upload_filename)
            self._upload_file()

            if self._status == UploadStatus.TO_CLEAN:
                for filename in self._created_files_list:
                    self._delete_file(filename)

                self.status = UploadStatus.DONE

        except errors.Error as e:
            self.status_message = str(e)
            self.status = UploadStatus.FAILED

    def _zip_directory(self) -> None:
        """
        Zip the contents of the input directory, and updates status
        as needed.

        Raises
        ------
        prepare.FileError
        """
        assert self.status in [
            UploadStatus.TO_ZIP, UploadStatus.TO_ZIP_AND_ANONYMISE
        ]
        to_anonymise: bool = self.status == UploadStatus.TO_ZIP_AND_ANONYMISE

        with SingleUpload._anon_lock:
            self.input_filename = prepare.get_input_filename(self.path)
            self.status = UploadStatus.ZIPPING
            prepare.zip_directory(self.path, self.input_filename)
            self._created_files_list.append(self.input_filename)
            if to_anonymise:
                self.status = UploadStatus.TO_ANONYMISE
            else:
                self.status = UploadStatus.TO_UPLOAD

    def _anonymise_zip_file(self) -> None:
        """
        Anonymise the file, and updates status as needed.

        Raises
        ------
        prepare.FileError
        """
        assert self.status == UploadStatus.TO_ANONYMISE

        # Check the zip file
        prepare.get_zipfile_size(self.input_filename)

        with SingleUpload._anon_lock:
            self.upload_filename = prepare.get_anon_filename(
                self.input_filename)
            self.status = UploadStatus.ANONYMISING
            assert self.input_filename != self.upload_filename
            prepare.anonymise_zip(self.input_filename, self.upload_filename)
            self._created_files_list.append(self.upload_filename)
            self.status = UploadStatus.TO_UPLOAD

    def _upload_chunk(
        self, data: Any, range_str: str, length: int, disposition: str,
        last_chunk: bool, file_info: FileInfo
    ) -> Response:
        """
        Upload one chunk.

        Raises
        ------
        platform.ConnectionError
        """
        request_headers = {}
        request_headers["Content-Type"] = "application/zip"
        request_headers["Content-Range"] = range_str
        request_headers['Session-ID'] = str(self.upload_id)
        request_headers["Content-Length"] = str(length)
        request_headers["Content-Disposition"] = disposition

        if last_chunk:
            self._add_upload_info_to_request_headers(
                file_info, request_headers)
            request_headers["X-Requested-With"] = "XMLHttpRequest"
            request_headers["X-Mint-Filename"] = os.path.split(
                self.input_filename)[1]

        response_time: float = 300.0 if last_chunk else 30.0
        response: Response = platform.post(
            auth=self.auth,
            endpoint='upload',
            data=data,
            headers=request_headers,
            timeout=response_time
        )
        return response

    def _upload_file(self) -> Optional[Response]:
        """
        Upload the file to the QMENTA platform.
        Updates status and progress as needed.

        Returns
        -------
        The Response from the platform for the last uploaded chunk.

        Raises
        ------
        prepare.FileError
        UploadError
        platform.ConnectionError
        """
        assert self.status == UploadStatus.TO_UPLOAD

        self.file_size = prepare.get_zipfile_size(self.upload_filename)

        fname: str = os.path.split(self.upload_filename)[1]

        # TODO: The code below was copied from mintapi and needs to be
        #   cleaned up. See IF-1111.
        max_retries: int = 10
        with open(self.upload_filename, "rb") as file_object:
            chunk_num: int = 0
            retries_count: int = 0
            error_message: str = ''
            self.bytes_uploaded = 0
            response: Optional[Response] = None
            last_chunk: bool = False

            self.status = UploadStatus.UPLOADING
            while True:
                data = file_object.read(self.chunk_size)
                if not data:
                    raise UploadError(
                        "Unexpected end of file: '{}'".format(
                            self.upload_filename
                        )
                    )

                start_position: int = chunk_num * self.chunk_size
                end_position: int = start_position + self.chunk_size - 1
                bytes_to_send: int = self.chunk_size

                if end_position >= self.file_size:
                    last_chunk = True
                    end_position = self.file_size - 1
                    bytes_to_send = self.file_size - self.bytes_uploaded

                bytes_range: str = "bytes " + str(start_position) + "-" + \
                    str(end_position) + "/" + str(self.file_size)

                dispstr: str = "attachment; filename=%s" % fname

                response = self._upload_chunk(
                    data, bytes_range, bytes_to_send, dispstr,
                    last_chunk, self.file_info
                )

                if response is None:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > max_retries:
                        error_message = "HTTP Connection Problem"
                        break
                elif int(response.status_code) == 201:
                    chunk_num += 1
                    retries_count = 0
                    self.bytes_uploaded += self.chunk_size
                elif int(response.status_code) == 200:
                    self.bytes_uploaded = self.file_size
                    if self.keep_created_files:
                        self.status = UploadStatus.DONE
                    else:
                        self.status = UploadStatus.TO_CLEAN
                    break
                elif int(response.status_code) == 416:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > max_retries:
                        error_message = (
                            "Error Code: 416; "
                            "Requested Range Not Satisfiable (NGINX)")
                        break
                else:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > max_retries:
                        error_message = ("Number of retries has been reached. "
                                         "Upload process stops here !")
                        print(error_message)
                        break

        return response

    def _delete_file(self, filename: str) -> None:
        # Only delete files that were created here
        basename: str = os.path.basename(filename)
        assert basename.startswith('qm-')
        assert basename.endswith('.zip')

        os.remove(filename)
