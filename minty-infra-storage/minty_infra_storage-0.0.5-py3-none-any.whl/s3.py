import os
from uuid import UUID

import boto3
import minty.infrastructure.mime_utils as mu
from botocore.client import Config
from minty import Base
from minty.exceptions import ConfigurationConflict


class S3Wrapper(Base):
    def __init__(self, filestore_config: list, base_directory: str):
        self.filestore_config = filestore_config
        self.base_directory = base_directory

    def _select_config(self, storage_location=None):
        """Select config from the stored configs."""
        if storage_location is None:
            return self.filestore_config[0]
        for config in self.filestore_config:
            if storage_location == config["name"]:
                return config

        raise ConfigurationConflict(
            f"No configuration found for '{storage_location}'"
        )

    def _generate_attachment_disposition(self, filename: str, download: bool):
        """Generate the value of the Content-Disposition header

        https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition
        """
        if download:
            content_disposition = f'attachment; filename="{filename}"'
        else:
            content_disposition = "inline"
        return content_disposition

    def _s3_client(self, config):
        """Build an AWS S3 client object from configuration"""

        boto_config = self._generate_boto_config(config)
        boto_parameters = self._generate_boto_parameters(config)

        return boto3.session.Session().client(
            service_name="s3", config=Config(**boto_config), **boto_parameters
        )

    def _generate_boto_parameters(self, config):
        """Generate the boto parameters from the given config."""

        boto_parameters = {}
        access_key = config.get("access_id", None)
        secret_key = config.get("access_key", None)
        endpoint_url = config.get("endpoint_url", None)
        region_name = config.get("region_name", None)

        # If access id and key are not specified, boto3 will default to use
        # the EC2 IAM role, which is what we want on production.

        if all([access_key, secret_key]):
            boto_parameters["aws_access_key_id"] = access_key
            boto_parameters["aws_secret_access_key"] = secret_key

        if endpoint_url is not None:
            boto_parameters["endpoint_url"] = endpoint_url

        if region_name is not None:
            boto_parameters["region_name"] = region_name

        return boto_parameters

    def _generate_boto_config(self, config):
        """Generate the boto config from the given config."""

        signature_version = config.get("signature_version", None)
        addressing_style = config.get("addressing_style", "auto")

        boto_config = {"s3": {"addressing_style": addressing_style}}
        if signature_version is not None:
            boto_config["signature_version"] = signature_version

        return boto_config

    def _get_s3_bucket_and_key(self, config: dict, uuid: UUID) -> dict:
        """Generate `key` and `bucket` values for s3 based on the config type.

        :param config: config
        :type config: dict
        :param uuid: file_uuid
        :type uuid: UUID
        :return: dict
        :rtype: dict containing key and bucket values
        """
        if config["type"] == "s3":
            key = f"{self.base_directory}/{uuid}"
            try:
                bucket = config["bucket"]
            except KeyError as error:
                raise ConfigurationConflict(
                    "Invalid configuration for S3 found"
                ) from error
        elif config["type"] == "s3Legacy":
            key = str(uuid)
            bucket = self.base_directory
        else:
            raise ConfigurationConflict(
                "Invalid configuration for S3 found", "infra/s3/no_type"
            )
        return {"key": key, "bucket": bucket}

    def upload(self, file_handle, uuid):
        timer = self.statsd.get_timer("file_upload")
        with timer.time("s3_upload"):
            config = self._select_config()

            location_name = config["name"]
            s3_config = self._get_s3_bucket_and_key(config=config, uuid=uuid)

            response_dict = self._s3_client(config=config).put_object(
                Body=file_handle,
                Bucket=s3_config["bucket"],
                Key=s3_config["key"],
            )

        file_handle.seek(0, os.SEEK_END)
        total_size = file_handle.tell()

        return {
            "uuid": uuid,
            "md5": response_dict["ETag"][1:-1],
            "size": total_size,
            "mime_type": mu.get_mime_type_from_handle(file_handle),
            "storage_location": location_name,
        }

    def download_file(self, destination, file_uuid, storage_location: str):
        """Download a file from S3 to the file-handle `destination`

        :param destination: File handle to write the file's contents to
        :type destination: File
        :param file_uuid: UUID of the object to download
        :type file_uuid: UUID
        :param storage_location: Name of the storage configuration used to store
            this file.
        :type storage_location: str
        """
        timer = self.statsd.get_timer("file_download")
        config = self._select_config(storage_location)
        s3_config = self._get_s3_bucket_and_key(config=config, uuid=file_uuid)

        with timer.time("s3_download"):
            self._s3_client(config=config).download_fileobj(
                s3_config["bucket"], s3_config["key"], destination
            )

        return

    def get_download_url(
        self,
        uuid,
        storage_location: str,
        filename: str,
        mime_type: str,
        download: bool,
    ):
        """Generate a pre-signed download url for given file uuid."""
        timer = self.statsd.get_timer("file_download_url")
        config = self._select_config(storage_location)
        s3_config = self._get_s3_bucket_and_key(config=config, uuid=uuid)

        presigned_url_expiration = config.get("presigned_url_expiration", 3600)
        cache_control = config.get("cache_control", "private, max-age=3600")

        with timer.time("s3_download_url"):
            content_disposition = self._generate_attachment_disposition(
                filename=filename, download=download
            )
            presigned_url = self._s3_client(
                config=config
            ).generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": s3_config["bucket"],
                    "Key": s3_config["key"],
                    "ResponseContentDisposition": content_disposition,
                    "ResponseContentType": mime_type,
                    "ResponseCacheControl": cache_control,
                },
                ExpiresIn=presigned_url_expiration,
            )

        return presigned_url


class S3Infrastructure(Base):
    """Infrastructure Class for S3 Connection."""

    def __call__(self, config):
        """Create a new S3 connection using the specified configuration

        :param config: The configuration params necessary to connect to a S3 bucket.
        :return: A S3 handle for a bucket on a connection to an S3 server.
        :rtype: S3Wrapper
        """
        try:
            directory = config["storage_bucket"]
        except KeyError:
            try:
                directory = config["instance_uuid"]
            except KeyError as k:
                raise ConfigurationConflict(
                    "No instance UUID or storage bucket specified for S3 configuration"
                ) from k

        try:
            filestore_config = config["filestore"]
            if type(filestore_config) is not list:
                filestore_config = [filestore_config]
        except KeyError as error:
            raise ConfigurationConflict(
                "Invalid configuration for S3 found"
            ) from error

        return S3Wrapper(
            filestore_config=filestore_config, base_directory=directory
        )
