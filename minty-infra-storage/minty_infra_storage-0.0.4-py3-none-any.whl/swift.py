import os

from keystoneauth1 import session
from keystoneauth1.identity import v3
from minty import Base
from minty.exceptions import ConfigurationConflict
from minty.infrastructure.mime_utils import get_mime_type_from_handle
from swiftclient import Connection

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 1024  # 1 gigabyte


class SwiftWrapper(Base):
    """Infrastructure wrapper for file actions in OpenStack Swift

    Only uploads for now, but should support downloads, etc. in the future."""

    def __init__(
        self, filestore_config: list, container_name: str, segment_size: int
    ):
        """Initialize an infrastructure handle to work with files stored in an
        openstack-swift service.

        Default segments size is set by `DEFAULT_CHUNK_SIZE`.

        :param filestore_config: File store config params used to make the
            connection for upload.
        :type filestore_config: list
        :param container_name: The name of the container to use for file
            operations.
        :type container_name: str
        :param segment_size: The size of the segment/chunk size of the file to
            send to swift when uploading
        :type segment_size: int
        """

        self.filestore_config = filestore_config
        self.segment_size = segment_size
        self.container_name = container_name

    def upload(self, file_handle, uuid):
        """Upload file to OpenStack Swift in `segment_size` chunks.

        Reads the file handle, and uploads chunks to swift, while also
        calculating the MD5 of the file and determining its MIME type.

        :param file_handle: File-like object
        :param uuid: The uuid of the file te be handled
        :type uuid: uuid4
        :return: A dictionary of the data/metadata of the uploaded file into
            swift. Contains the keys: uuid, md5, file_size, mime_type, storage_location.
        :rtype: dict
        """
        timer = self.statsd.get_timer("file_upload")
        try:
            with timer.time("connect_to_swift"):
                connection = self._connect_to_swift(self.filestore_config[0])
        except IndexError as error:
            raise ConfigurationConflict(
                "No config found for Swift configuration"
            ) from error

        try:
            storage_location = self.filestore_config[0]["name"]
        except KeyError as error:
            raise ConfigurationConflict(
                "No name found for Swift configuration"
            ) from error

        response_dict = {}
        # For files that are smaller than 512k waitress will
        # send a BytesIO instead of a BufferedRandom handler

        mime_type = get_mime_type_from_handle(file_handle)

        with timer.time("total"):
            connection.put_object(
                container=self.container_name,
                obj=str(uuid),
                contents=file_handle,
                response_dict=response_dict,
            )

        file_handle.seek(0, os.SEEK_END)
        total_size = file_handle.tell()

        return {
            "uuid": uuid,
            "md5": response_dict["headers"]["etag"],
            "size": total_size,
            "mime_type": mime_type,
            "storage_location": storage_location,
        }

    def _connect_to_swift(self, file_store_config: dict):
        """Returns a connection to Swift based on the auth version.
        Supports V3, V2 and V1(Legacy)

        :param file_store_config: Configuration params for a file storage.
        :type file_store_config: dict
        :return: Connection V1 or V2 or V3 instance depending on the config params provided.
        :rtype: Connection
        """
        if file_store_config.get("auth") is None:
            raise ConfigurationConflict("Authentication params are missing")

        if file_store_config.get("auth_version") is None:
            raise ConfigurationConflict(
                "No auth_version specified for Swift configuration"
            )

        auth_config = {**file_store_config["auth"]}
        auth_config["timeout"] = int(auth_config.get("timeout", 60))
        auth_version = file_store_config["auth_version"]
        if auth_version == "v3":
            return self._connect_to_swift_v3(**auth_config, auth_version="3")
        elif auth_version in ["v1", "v2"]:
            # authentication version 2 and 1
            # accessing second index of string auth_version to get the version number
            auth_version = auth_version[1]
            return self._connect_to_swift_legacy_auth(
                **auth_config, auth_version=auth_version
            )
        else:
            raise ConfigurationConflict(
                f"Unsupported auth_version: '{auth_version}'"
            )

    def _connect_to_swift_v3(
        self,
        auth_url,
        username,
        password,
        auth_version=None,
        user_domain_name=None,
        project_name=None,
        project_domain_name=None,
        timeout=60,
    ) -> Connection:
        """A V3 auth type with keystone session to connect to swift.

        :param auth_url:
        :param username:
        :param password:
        :param user_domain_name:
        :param project_name:
        :param project_domain_name:
        :param timeout:
        :return  A connection Instance of V3 swift auth.
        :rtype: Connection
        """
        auth = v3.Password(
            auth_url=auth_url,
            username=username,
            password=password,
            user_domain_name=user_domain_name,
            project_name=project_name,
            project_domain_name=project_domain_name,
        )

        keystone_session = session.Session(auth=auth)

        return Connection(
            session=keystone_session,
            auth_version=auth_version,
            timeout=timeout,
        )

    def _connect_to_swift_legacy_auth(
        self,
        auth_url,
        username,
        password,
        auth_version=None,
        tenant_name=None,
        timeout=60,
    ) -> Connection:
        """Support for  auth type V1 & V2 to connect to swift.

        :param auth_url:
        :param username:
        :param password:
        :param auth_version:
        :param tenant_name:
        :param timeout:
        :return: A connection Instance of Legacy(V1) or V2 swift auth.
        :rtype: Connection
        """

        return Connection(
            authurl=auth_url,
            user=username,
            key=password,
            auth_version=auth_version,
            tenant_name=tenant_name,
            timeout=timeout,
        )


class SwiftInfrastructure(Base):
    """Infrastructure Class for OpenStack Swift connections."""

    def __call__(self, config):
        """Create a new Swift connection using the specified configuration

        :param config: The configuration params necessary to connect to a swift container.
        :return: A Swift handle for a bucket on a connection to an OpenStack server.
        :rtype: SwiftWrapper
        """

        try:
            container_name = config["storage_bucket"]
        except KeyError:
            try:
                container_name = config["instance_uuid"]
            except KeyError as k:
                raise ConfigurationConflict(
                    "No container name specified for Swift configuration"
                ) from k

        try:
            filestore_config = config["filestore"]
            if type(filestore_config) is not list:
                filestore_config = [filestore_config]
        except KeyError as error:
            raise ConfigurationConflict(
                "No file store configuration specified for openstack/swift"
            ) from error

        return SwiftWrapper(
            filestore_config=filestore_config,
            container_name=container_name,
            segment_size=int(config.get("chunk_size", DEFAULT_CHUNK_SIZE)),
        )
