# coding=utf-8
from __future__ import absolute_import, division, print_function

import functools
import os
import tempfile
from threading import Thread

import minio.error
from lostc import collection as lcc
from minio import Minio

from suanpan import api, asyncio
from suanpan import path as spath
from suanpan import runtime
from suanpan.log import logger
from suanpan.storage.objects import Storage
from suanpan.utils import pbar as spbar


class MinioStorage(Storage):
    def __init__(
        self,
        minioAccessKey=None,
        minioSecretKey=None,
        minioBucketName="suanpan",
        minioEndpoint="localhost:9000",
        minioSecure=True,
        minioDelimiter="/",
        minioTempStore=tempfile.gettempdir(),
        **kwargs
    ):
        super(MinioStorage, self).__init__(
            delimiter=minioDelimiter, tempStore=minioTempStore, **kwargs
        )

        self.bucketName = minioBucketName
        self.bucket = minioBucketName
        self.endpoint, self.secure = self._analyzeEndpoint(minioEndpoint, minioSecure)
        self.refreshAccessKey(accessKey=minioAccessKey, secretKey=minioSecretKey)

    def _analyzeEndpoint(self, endpoint, secure=False):
        httpsPrefix = "https://"
        if endpoint.startswith(httpsPrefix):
            return endpoint[len(httpsPrefix) :], True

        httpPrefix = "http://"
        if endpoint.startswith(httpPrefix):
            return endpoint[len(httpPrefix) :], False

        return endpoint, secure

    def minioRequest(self, apiName, *args, **kwargs):
        apiFunc = getattr(self.client, apiName)
        try:
            return apiFunc(*args, **kwargs)
        except minio.error.AccessDenied:
            logger.warning("Minio access denied, refreshing access key.")
            self.refreshAccessKey()
            return apiFunc(*args, **kwargs)

    def refreshAccessKey(self, accessKey=None, secretKey=None):
        if accessKey and secretKey:
            self.accessKey = accessKey
            self.secretKey = secretKey
        else:
            data = api.oss.getToken()
            self.accessKey = data["Credentials"]["AccessKeyId"]
            self.secretKey = data["Credentials"]["AccessKeySecret"]

        self.client = Minio(
            self.endpoint,
            access_key=self.accessKey,
            secret_key=self.secretKey,
            secure=self.secure,
        )
        return self.accessKey, self.secretKey

    @runtime.retry(stop_max_attempt_number=3)
    def download(self, name, path, bucket=None, ignores=None):
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        downloadFunction = (
            self.downloadFile
            if self.isFile(name, bucket=bucket)
            else self.downloadFolder
        )
        return downloadFunction(name, path, bucket=bucket, ignores=ignores)

    def downloadFolder(
        self,
        folderName,
        folderPath,
        bucket=None,
        delimiter=None,
        workers=None,
        ignores=None,
    ):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        delimiter = delimiter or self.delimiter
        storagePath = self.storageUrl(folderName, bucket=bucket)

        if folderPath in ignores:
            logger.info(
                "Ignore downloading folder: {} -> {}".format(folderPath, storagePath)
            )
            return folderPath

        downloads = {
            file: self.localPathJoin(
                folderPath, self.storageRelativePath(file, folderName)
            )
            for _, _, files in self.walk(folderName, delimiter=delimiter, bucket=bucket)
            for file in files
        }

        logger.info("Downloading folder: {} -> {}".format(storagePath, folderPath))
        # Download from minio
        _run = functools.partial(
            self.downloadFile, bucket=bucket, ignores=ignores, quiet=True
        )
        asyncio.starmap(
            _run, downloads.items(), pbar="Downloading", thread=True, workers=workers
        )
        # Remove ignores
        self.removeIgnores(folderPath, ignores=ignores)
        # Remove rest files and folders
        files = (
            self.localPathJoin(root, file)
            for root, _, files in os.walk(folderPath)
            for file in files
        )
        restFiles = [file for file in files if file not in downloads.values()]
        asyncio.map(
            spath.remove,
            restFiles,
            pbar="Removing Rest Files" if restFiles else False,
            thread=True,
        )
        spath.removeEmptyFolders(folderPath)
        logger.info("Removed empty folders in: {}".format(folderPath))
        # End
        logger.info("Downloaded folder: {} -> {}".format(storagePath, folderPath))
        return folderPath

    def downloadFile(
        self, objectName, filePath, bucket=None, ignores=None, quiet=False
    ):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        storagePath = self.storageUrl(objectName, bucket=bucket)
        fileSize = self.getStorageSize(objectName, bucket=bucket)

        if not quiet:
            logger.info("Downloading file: {} -> {}".format(storagePath, filePath))

        with spbar.one(total=fileSize, config=not quiet) as pbar:
            if filePath in ignores:
                pbar.update(fileSize)
                pbar.set_description("Ignored")
                return filePath

            objectMd5 = self.getStorageMd5(objectName, bucket=bucket)
            fileMd5 = self.getLocalMd5(filePath)
            if self.checkMd5(objectMd5, fileMd5, bucket=bucket):
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return filePath

            spath.safeMkdirsForFile(filePath)
            self.minioRequest("fget_object", bucket, objectName, filePath)

            pbar.update(fileSize)
            pbar.set_description("Downloaded")

            return filePath

    @runtime.retry(stop_max_attempt_number=3)
    def upload(self, name, path, bucket=None, ignores=None):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        uploadFunction = self.uploadFolder if os.path.isdir(path) else self.uploadFile
        return uploadFunction(name, path, bucket=bucket, ignores=ignores)

    def uploadFolder(
        self, folderName, folderPath, bucket=None, workers=None, ignores=None
    ):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        storagePath = self.storageUrl(folderName, bucket=bucket)

        if folderName in ignores:
            logger.info(
                "Ignore uploading folder: {} -> {}".format(folderName, storagePath)
            )
            return folderPath

        filePaths = (
            os.path.join(root, file)
            for root, _, files in os.walk(folderPath)
            for file in files
        )
        uploads = {
            filePath: self.storagePathJoin(
                folderName, self.localRelativePath(filePath, folderPath)
            )
            for filePath in filePaths
        }

        if not uploads:
            logger.warning("Uploading empty folder: {}".format(folderPath))
            return folderPath

        logger.info("Uploading folder: {} -> {}".format(folderPath, storagePath))
        # Upload files to oss
        uploadItems = [
            (objectName, filePath) for filePath, objectName in uploads.items()
        ]
        _run = functools.partial(
            self.uploadFile, bucket=bucket, ignores=ignores, quiet=True
        )
        asyncio.starmap(
            _run, uploadItems, pbar="Uploading", thread=True, workers=workers
        )
        # Remove rest files
        localFiles = set(
            self.localRelativePath(filePath, folderPath) for filePath in uploads.keys()
        )
        remoteFiles = set(
            self.storageRelativePath(objectName, folderName)
            for _, _, files in self.walk(folderName, bucket=bucket)
            for objectName in files
        )
        restFiles = [
            self.storagePathJoin(folderName, file) for file in remoteFiles - localFiles
        ]
        _run = functools.partial(self.remove, bucket=bucket, quiet=True)
        asyncio.map(
            _run,
            restFiles,
            pbar="Removing Rest Files" if restFiles else False,
            thread=True,
        )
        # End
        logger.info("Uploaded folder: {} -> {}".format(folderPath, storagePath))
        return folderPath

    def uploadFile(self, objectName, filePath, bucket=None, ignores=None, quiet=False):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        storagePath = self.storageUrl(objectName, bucket=bucket)
        fileSize = os.path.getsize(filePath)

        if not quiet:
            logger.info("Uploading file: {} -> {}".format(filePath, storagePath))

        with spbar.one(total=fileSize, config=not quiet) as pbar:
            if filePath in ignores:
                pbar.update(fileSize)
                pbar.set_description("Ignored")
                return filePath

            objectMd5 = self.getStorageMd5(objectName, bucket=bucket)
            fileMd5 = self.getLocalMd5(filePath)
            if self.checkMd5(objectMd5, fileMd5):
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return filePath

            self.minioRequest(
                "fput_object",
                bucket,
                objectName,
                filePath,
                progress=Progress(pbar),
                metadata={self.CONTENT_MD5: fileMd5},
            )

            pbar.set_description("Uploaded")

            return filePath

    @runtime.retry(stop_max_attempt_number=3)
    def copy(self, name, dist, bucket=None):
        bucket = bucket or self.bucket
        copyFunction = (
            self.copyFile if self.isFile(name, bucket=bucket) else self.copyFolder
        )
        return copyFunction(name, dist, bucket=bucket)

    def copyFolder(
        self, folderName, distName, bucket=None, workers=None, delimiter=None
    ):
        bucket = bucket or self.bucket
        delimiter = delimiter or self.delimiter
        folderName = self.completePath(folderName)
        distName = self.completePath(distName)
        logger.info("Copying folder: {} -> {}".format(folderName, distName))
        copyItems = [
            (file, file.replace(folderName, distName))
            for _, _, files in self.walk(folderName, delimiter=delimiter, bucket=bucket)
            for file in files
        ]
        _run = functools.partial(self.copyFile, bucket=bucket, quiet=True)
        asyncio.starmap(_run, copyItems, pbar="Copying", thread=True, workers=workers)

    def copyFile(self, objectName, distName, bucket=None, quiet=False):
        bucket = bucket or self.bucket
        fileSize = self.getStorageSize(objectName, bucket=bucket)

        if not quiet:
            logger.info(
                "Copying file: {} -> {}".format(
                    self.storageUrl(objectName, bucket=bucket),
                    self.storageUrl(distName, bucket=bucket),
                )
            )

        with spbar.one(total=fileSize, config=not quiet) as pbar:
            objectMd5 = self.getStorageMd5(objectName, bucket=bucket)
            distMd5 = self.getStorageMd5(distName, bucket=bucket)
            if self.checkMd5(objectMd5, distMd5):
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return distName

            sourcePath = self.delimiter + self.storagePathJoin(bucket, objectName)
            self.minioRequest("copy_object", bucket, distName, sourcePath)
            pbar.update(fileSize)
            return distName

    @runtime.retry(stop_max_attempt_number=3)
    def remove(self, objectName, delimiter=None, bucket=None, quiet=False):
        delimiter = delimiter or self.delimiter
        bucket = bucket or self.bucket
        removeFunc = (
            self.removeFile
            if self.isFile(objectName, bucket=bucket)
            else self.removeFolder
        )
        return removeFunc(objectName, delimiter=delimiter, bucket=bucket, quiet=quiet)

    def removeFolder(
        self, folderName, delimiter=None, bucket=None, workers=None, quiet=False
    ):
        delimiter = delimiter or self.delimiter
        bucket = bucket or self.bucket
        folderName = self.completePath(folderName)
        removes = [
            objectName
            for _, _, files in self.walk(folderName, bucket=bucket, delimiter=delimiter)
            for objectName in files
        ]
        _run = functools.partial(
            self.remove, delimiter=delimiter, bucket=bucket, quiet=True
        )
        asyncio.map(
            _run,
            removes,
            pbar="Removing" if removes and not quiet else False,
            thread=True,
            workers=workers,
        )
        return folderName

    def removeFile(
        self, objectName, delimiter=None, bucket=None, quiet=False
    ):  # pylint: disable=unused-argument
        bucket = bucket or self.bucket
        self.minioRequest("remove_object", bucket, objectName)
        if not quiet:
            storagePath = self.storageUrl(objectName, bucket=bucket)
            logger.info("Removed file: {}".format(storagePath))
        return objectName

    def walk(self, folderName, delimiter=None, bucket=None):
        bucket = bucket or self.bucket
        delimiter = delimiter or self.delimiter
        root = self.completePath(folderName, delimiter=delimiter)
        objects = self.minioRequest("list_objects_v2", bucket, prefix=root, recursive=True)
        folders, files = lcc.divide(objects, lambda obj: obj.is_dir)
        yield root, self._getObjectNames(folders), self._getObjectNames(files)

    def _listAll(self, folderName, delimiter=None, bucket=None):
        bucket = bucket or self.bucket
        delimiter = delimiter or self.delimiter
        root = self.completePath(folderName, delimiter=delimiter)
        return self.minioRequest(
            "list_objects_v2", bucket, prefix=root, recursive=False
        )

    def listAll(self, folderName, delimiter=None, bucket=None):
        return (
            obj.object_name
            for obj in self._listAll(folderName, delimiter=delimiter, bucket=bucket)
        )

    def listFolders(self, folderName, delimiter=None, bucket=None):
        return (
            obj.object_name
            for obj in self._listAll(folderName, delimiter=delimiter, bucket=bucket)
            if obj.is_dir
        )

    def listFiles(self, folderName, delimiter=None, bucket=None):
        return (
            obj.object_name
            for obj in self._listAll(folderName, delimiter=delimiter, bucket=bucket)
            if not obj.is_dir
        )

    def isFolder(self, folderName, bucket=None):
        return bool(next(self.listAll(folderName, bucket=bucket), None))

    def isFile(self, objectName, bucket=None):
        bucket = bucket or self.bucket
        try:
            self.minioRequest("stat_object", bucket, objectName)
            return True
        except Exception:
            return False

    def getStorageMd5(self, name, bucket=None):
        bucket = bucket or self.bucket
        try:
            return self.minioRequest("stat_object", bucket, name).metadata.get(
                self.CONTENT_MD5
            )
        except Exception:
            return None

    def getStorageSize(self, name, bucket=None):
        bucket = bucket or self.bucket
        return self.minioRequest("stat_object", bucket, name).size

    def storageUrl(self, path, bucket=None):
        bucket = bucket or self.bucket
        return "minio:///" + self.storagePathJoin(bucket, path)

    def _getObjectNames(self, objects):
        return (
            [obj.object_name for obj in objects]
            if isinstance(objects, (tuple, list))
            else objects.object_name
        )


class Progress(Thread):
    def __init__(self, pbar, *args, **kwargs):
        super(Progress, self).__init__(*args, **kwargs)
        self.pbar = pbar
        self.totalSize = None
        self.objectName = None

    def set_meta(self, total_length, object_name):
        self.totalSize = total_length
        self.objectName = object_name

    def update(self, size):
        self.pbar.update(size)
        self.pbar.set_description("Uploading")
