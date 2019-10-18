"""
Functions to manipulate objects on Dell Storage Manager

REST API documentation:
https://downloads.dell.com/Manuals/Common/dell-storage-manager-rest-api-cookbook-3029-wp-san_en-us.pdf
"""
import logging

from .httpclient import HttpClient

LOG = logging.getLogger(__name__)


class DSMConnection():
    """
    Storage Center API interface.

    Handles calls to Dell Storage Manager via the REST API interface.
    """
    def __init__(self, host, port, user, password, verify):
        """
        This creates a connection to Dell Storage Manager.

        :param host: IP address of the Dell Data Collector.
        :param port: Port the Data Collector is listening on.
        :param user: User account to login with.
        :param password: Password.
        :param verify: Boolean indicating whether certificate verification should be turned on or not.
        """
        self.notes = 'Created via Dell Storage Manager REST API'
        self.client = HttpClient(host, port, user, password, verify)
        self.connection_id = None

        self.scs = {}
        self.servers = {}
        self.volumes = {}
        self.volume_folders = {}
        self.replays = {}
        self.rply_profiles = {}
        self.recycled_vols = {}

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, tipe, value, traceback):
        self.close_connection()
        self.client = None

    def _check_result(self, rest_response):
        """
        Checks and logs API responses.

        :param rest_response: The result from a REST API call.
        :returns: ``True`` if success, ``False`` otherwise.
        """
        if 200 <= rest_response.status_code < 300:
            # API call was a normal success
            return True

        LOG.error('REST call result:\tCode: %s\tReason: %s\tText: %s',
                  rest_response.status_code, rest_response.reason, rest_response.text)

        return False

    def _get_json(self, blob):
        """
        Returns a dict from the JSON of a REST response.

        :param blob: The response from a REST call.
        :returns: JSON or None on error.
        """
        try:
            return blob.json()
        except AttributeError:
            LOG.error('Error invalid json: %s', blob)
        return None

    def _get_id(self, blob):
        """
        Returns the instanceId from a Dell REST object.

        :param blob: A Dell SC REST call's response.
        :returns: The instanceId from the Dell SC object or None on error.
        """
        try:
            if isinstance(blob, dict):
                return blob.get('instanceId')
        except AttributeError:
            LOG.error('Invalid API object: %s', blob)
        return None

    def open_connection(self):
        """Authenticate against Dell Storage Manager."""
        payload = {}
        response = self.client.post('ApiConnection/Login', payload)
        if not self._check_result(response):
            LOG.error('Failed to connect to Storage Manager. Response: %s.', response.text)
            return False

        try:
            # log in and set the connection ID
            apidict = self._get_json(response)
            instanceId, version = apidict['instanceId'], apidict['apiVersion']
            LOG.info('Connected to DSM. API Version: %s, Connection ID: %s' % (version, instanceId))
            self.connection_id = self._get_id(apidict)
        except Exception:
            LOG.error('Unrecognized Login Response: %s.', response.text)

    def close_connection(self):
        """Logout of Dell Storage Manager."""
        response = self.client.post('ApiConnection/Logout', {})
        result = self._check_result(response)
        LOG.info('Logout of DSM: %s.', result)

    def get_scs(self):
        """
        Gets all SCs and updates `self.scs`.

        :returns: `True` for success, `False` on error.
        """
        path = 'ApiConnection/ApiConnection/%s/StorageCenterList' % self.connection_id
        response = self.client.get(path)
        if not self._check_result(response):
            LOG.error('Failed to list Storage Centers. Response: %s', response.text)
            return False

        self.scs = {}
        stdout = self._get_json(response)
        for i in range(len(stdout)):
            self.scs[stdout[i]['name']] = {}
            self.scs[stdout[i]['name']]['instanceId'] = stdout[i]['instanceId']
            self.scs[stdout[i]['name']]['hostOrIP'] = stdout[i]['hostOrIpAddress']

        LOG.info('API call %s succeeded.', path)

        return True

    def get_volume_folders(self):
        """
        Gets volume folders in all SCs and updates `self.volume_folders`.

        :returns: `True` for success, `False` on error.
        """
        results = []
        self.volume_folders = {}

        results.append(self.get_scs())
        for sc in self.scs.values():
            sc_id = sc['instanceId']
            result = self.get_volume_folders_in_sc(sc_id)
            results.append(result)

        LOG.info('get_volume_folders() result: %s.', results)

        return False if False in results else True

    def get_volume_folders_in_sc(self, sc_id):
        """
        Gets volume folders in a given SC and updates `self.volume_folders`.

        :param sc_id: Storage Center instance ID.
        :returns: dict object containing the retrieved volume folders.
        """
        path = 'StorageCenter/StorageCenter/%s/VolumeFolderList' % sc_id
        response = self.client.get(path)
        if not self._check_result(response):
            LOG.error('Failed to get volume folders in SC %s. Response: %s', sc_id, response.text)
            return False

        stdout = self._get_json(response)
        for i in range(len(stdout)):
            self.volume_folders[stdout[i]['instanceId']] = {}
            self.volume_folders[stdout[i]['instanceId']]['name'] = stdout[i]['name']
            if stdout[i].get('parent'):
                self.volume_folders[stdout[i]['instanceId']]['parent'] = stdout[i]['parent']['instanceName']
            self.volume_folders[stdout[i]['instanceId']]['scName'] = stdout[i]['scName']

        LOG.info('API call %s succeeded.', path)

        return True

    def get_volumes(self):
        """
        Gets volumes in all SCs and updates `self.volumes`.

        :returns: `True` for success, `False` on error.
        """
        results = []
        self.volumes = {}

        results.append(self.get_scs())
        for sc in self.scs.values():
            sc_id = sc['instanceId']
            result = self.get_volumes_in_sc(sc_id)
            results.append(result)

        LOG.info('get_volumes() results %s.', results)

        return False if False in results else True

    def get_volumes_in_sc(self, sc_id):
        """
        Gets volumes in a given SC and updates `self.volumes`.

        :param sc_id: Storage Center instance ID.
        :returns: dict object containing the retrieved volumes.
        """
        path = 'StorageCenter/StorageCenter/%s/VolumeList' % sc_id
        response = self.client.get(path)
        if not self._check_result(response):
            LOG.error('Failed to get volumes in SC %s. Response: %s', sc_id, response.text)
            return False

        stdout = self._get_json(response)
        for i in range(len(stdout)):
            self.volumes[stdout[i]['deviceId']] = {}
            self.volumes[stdout[i]['deviceId']]['instanceId'] = stdout[i]['instanceId']
            self.volumes[stdout[i]['deviceId']]['inRecycleBin'] = stdout[i]['inRecycleBin']
            self.volumes[stdout[i]['deviceId']]['volumeFolderPath'] = stdout[i]['volumeFolderPath']
            self.volumes[stdout[i]['deviceId']]['volumeFolderName'] = stdout[i]['volumeFolder']['instanceName']
            self.volumes[stdout[i]['deviceId']]['volumeFolderId'] = stdout[i]['volumeFolder']['instanceId']
            self.volumes[stdout[i]['deviceId']]['status'] = stdout[i]['status']
            self.volumes[stdout[i]['deviceId']]['name'] = stdout[i]['name']
            self.volumes[stdout[i]['deviceId']]['scName'] = stdout[i]['scName']

        LOG.info('API call %s succeeded.', path)

        return True

    def get_servers(self):
        """
        Gets servers in all SCs and updates `self.servers`.

        :returns: `True` for success, `False` on error.
        """
        results = []
        self.servers = {}

        results.append(self.get_scs())
        for sc in self.scs.values():
            sc_id = sc['instanceId']
            result = self.get_servers_in_sc(sc_id)
            results.append(result)

        LOG.info('get_servers() result: %s.', results)

        return False if False in results else True

    def get_servers_in_sc(self, sc_id):
        """
        Gets servers in a given SC and updates `self.servers`.

        :param sc_id: Storage Center instance ID.
        :returns: `True` for success, `False` for error.
        """
        path = 'StorageCenter/StorageCenter/%s/ServerList' % sc_id
        response = self.client.get(path)
        if not self._check_result(response):
            LOG.error('Failed to get servers in SC %s. Response: %s.', sc_id, response.text)
            return False

        stdout = self._get_json(response)
        for i in range(len(stdout)):
            self.servers[stdout[i]['name']] = {}
            self.servers[stdout[i]['name']]['instanceId'] = stdout[i]['instanceId']
            self.servers[stdout[i]['name']]['serverFolderPath'] = stdout[i]['serverFolderPath']
            self.servers[stdout[i]['name']]['status'] = stdout[i]['status']
            self.servers[stdout[i]['name']]['operatingSystem'] = stdout[i]['operatingSystem']['instanceName']
            self.servers[stdout[i]['name']]['scName'] = stdout[i]['scName']

        LOG.info('API call %s succeeded.', path)

        return True

    def get_snapshots(self):
        """
        Gets snapshots in all SCs and updates `self.replays`.

        :param sc_id: Storage Center instance ID.
        :returns: `True` for success, `False` for error.
        """
        payload = {}
        path = 'StorageCenter/ScReplay/GetList'
        response = self.client.post(path, payload)
        if not self._check_result(response):
            LOG.error('Failed to list snapshots. Response: %s', response.text)
            return False

        self.replays = {}
        stdout = self._get_json(response)
        for i in range(len(stdout)):
            # excluding snapshots with no createVolume attributes
            if stdout[i].get('createVolume') is not None:
                self.replays[stdout[i]['createVolume']['instanceName']] = {}
                self.replays[stdout[i]['createVolume']['instanceName']]['volumeId'] = \
                    stdout[i]['createVolume']['instanceId']
                self.replays[stdout[i]['createVolume']['instanceName']]['instanceId'] = stdout[i]['instanceId']
                self.replays[stdout[i]['createVolume']['instanceName']]['description'] = stdout[i]['description']
                self.replays[stdout[i]['createVolume']['instanceName']]['scName'] = stdout[i]['scName']

        LOG.info('API call %s succeeded.', path)

        return True

    def get_snapshot_profiles(self):
        """
        Gets snapshot profiles, aka replay profiles, in all SCs and updates `self.rply_profiles`.

        :returns: `True` for success, `False` for error.
        """
        payload = {}
        path = 'StorageCenter/ScReplayProfile/GetList'
        response = self.client.post(path, payload)
        if not self._check_result(response):
            LOG.error('Failed to list reply profiles. Response: %s.', response.text)
            return False

        self.rply_profiles = {}
        stdout = self._get_json(response)
        for i in range(len(stdout)):
            self.rply_profiles[stdout[i]['instanceName']] = {}
            self.rply_profiles[stdout[i]['instanceName']]['instanceId'] = stdout[i]['instanceId']
            self.rply_profiles[stdout[i]['instanceName']]['scName'] = stdout[i]['scName']

        LOG.info('API call %s succeeded.', path)

        return True

    def create_snapshot(self, volume_id, description=None, expiration='5'):
        """
        Creates a snapshot from volume.

        :param volume: instance ID of the volume from which to create a snapshot.
        :param name: name of the snapshot to create.
        :param description: description of the snapshot.
        :param expiration: expiration time in minutes, default: 5 minutes.
        :returns: created snapshot ID, `None` on error.
        """
        payload = {}
        if description is None:
            description = 'Snapshot created via REST API'
        payload['Description'] = description
        payload['ExpireTime'] = str(expiration)

        path = '/StorageCenter/ScVolume/%s/CreateReplay' % volume_id
        response = self.client.post(path, payload)
        if not self._check_result(response):
            LOG.error('Failed to create snapshot for volume ID %s. Response: %s.', volume_id, response.text)
            return None

        stdout = self._get_json(response)

        LOG.info('API call %s succeeded.', path)

        return self._get_id(stdout)

    def create_view_volume(self, snapshot_id, replay_profile_id, volume_name, volume_folder_id):
        """
        Creates a view volume from a snapshot.

        :param snapshot_id: ID of snapshot from which to create the view volume.
        :param replay_profile_id: ID of the replay profile for the view volume.
        :param volume_name: name to assign to newly created volume.
        :param volume_folder_id: instance ID of the folder of the new volume.
        :returns: view volume ID, `None` on error.
        """
        payload = {}
        payload['Name'] = volume_name
        payload['VolumeFolder'] = volume_folder_id
        payload['Notes'] = 'View volume created via REST API'

        if replay_profile_id is not None:
            payload['ReplayProfileList'] = [replay_profile_id]

        path = 'StorageCenter/ScReplay/%s/CreateView' % snapshot_id
        response = self.client.post(path, payload)
        if not self._check_result(response):
            LOG.error('Failed to create view volume %s. Response: %s.', volume_name, response.text)
            return None

        stdout = self._get_json(response)

        LOG.info('API call %s succeeded.', path)

        return self._get_id(stdout)

    def map_volume_to_server(self, volume_id, server_id):
        """
        Maps a volume to a server.

        :param volume_id: ID of the volume to map.
        :param server_id: ID of the server to which to map the volume.
        :returns: `True` for success, `False` for error.
        """
        payload = {}
        payload['Server'] = server_id

        path = 'StorageCenter/ScVolume/%s/MapToServer' % volume_id
        response = self.client.post(path, payload)
        if not self._check_result(response):
            LOG.error('Failed to map volume ID %s to server ID %s. Response: %s.',
                      volume_id, server_id, response.text)
            return False

        LOG.info('API call %s succeeded.', path)

        return True

    def unmap_volume(self, volume_id):
        """
        Unmap a volume.

        :param volume_id: ID of the volume to unmap.
        :returns: `True` for success, `False` for error.
        """
        payload = {}

        path = 'StorageCenter/ScVolume/%s/Unmap' % volume_id
        response = self.client.post(path, payload)
        if not self._check_result(response):
            LOG.error('Failed to unmap volume with ID %s. Response: %s.', volume_id, response.text)
            return False

        LOG.info('API call %s succeeded.', path)

        return True

    def delete_volume(self, volume_id, recycle=True):
        """
        Deletes a volume.

        :param volume_id: ID of the volume to delete.
        :param recycle: If `True`, move the volume to recycle bin, otherwise, delete the volume PERMANENTLY.
        :returns: `True` for success, `False` for error.
        """
        payload = {}

        if recycle:
            path = 'StorageCenter/ScVolume/%s/Recycle' % volume_id
            response = self.client.post(path, payload)
        else:
            path = 'StorageCenter/ScVolume/%s' % volume_id
            response = self.client.delete(path)

        if not self._check_result(response):
            LOG.error('Failed to delete volume with ID %s. Response: %s.', volume_id, response.text)
            return False

        LOG.info('API call %s succeeded.', path)

        return True

    def get_vol_mappings(self, volume_id):
        """
        Gets volume mappings.

        :param volume_id: ID of volume to look for its mappings.
        :returns: mappings dict, or `False` on error.
        """
        path = 'StorageCenter/ScVolume/%s/MappingList' % volume_id
        response = self.client.get(path)
        if not self._check_result(response):
            LOG.error('Failed to get volume mappings of volume with ID %s. Response: %s.', volume_id, response.text)
            return False

        stdout = self._get_json(response)

        LOG.info('API call %s succeeded.', path)

        return stdout

    def get_recycled_volumes(self):
        """
        Gets recycled volumes and updates `self.recycled_vols`.

        :retrun: `True` for success, `False` on error.
        """
        result = self.get_volumes()
        self.recycled_vols = {}

        for wwn, vol_info in self.volumes.items():
            # we're sure 'inRecycleBin' is in self.volumes[wwn]
            if self.volumes[wwn]['inRecycleBin']:
                self.recycled_vols[wwn] = vol_info

        LOG.info('get_recycled_volumes() result %s.', result)

        return result

    def get_server_id(self, server_name):
        """
        Returns server ID from server name.

        :param server_name: the name of server to return its ID.
        :returns: server ID or `None` on failure.
        """
        self.get_servers()
        if self.servers.get(server_name) is None:
            LOG.error('Server %s not found on Dell SCs.', server_name)
            return None

        # TODO: is server name unique to use it to determine the server id confidently?
        server_id = self.servers[server_name]['instanceId']

        return server_id
