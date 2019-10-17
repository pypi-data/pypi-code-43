import logging
import re

from .connection import DSMConnection
from .process import Process

LOG = logging.getLogger(__name__)


class Task():
    """
    Reimplementation of the shell scripts on https://git.uis.cam.ac.uk/i/uis/infra/dellsc.git
    """
    def __init__(self, host, port, user, password, verify):
        self.process = Process()
        self.dsm_connection = DSMConnection(host, port, user, password, verify)

    def __enter__(self):
        self.dsm_connection.open_connection()
        return self

    def __exit__(self, tipe, value, traceback):
        self.dsm_connection.close_connection()
        self.dsm_connection = None
        self.process = None

    def get_volume_info(self, wwn=None, mountpoint=None):
        """
        Returns details of volume with WWN `wwn` or mounted on `mountpoint`.

        :param wwn: volume's `wwn`.
        :param mountpoint: `mountpoint` where the volume is mounted.
        :returns: tuple (wwn, volid, volname, volFolderName, volFolderId, scName), `None`, otherwise.
        """
        if wwn is None and mountpoint is None:
            return None

        if mountpoint is not None:
            mpath = self.process.get_mpath_from_mountpoint(mountpoint)
            if mpath is None:
                return None

            wwn = self.process.get_wwn_from_mpath(mpath)
            if wwn is None:
                return None

        # get list of volumes
        self.dsm_connection.get_volumes()

        if self.dsm_connection.volumes.get(wwn) is not None:
            volid = self.dsm_connection.volumes[wwn].get('instanceId')
            volname = self.dsm_connection.volumes[wwn].get('name')
            volFolderName = self.dsm_connection.volumes[wwn].get('volumeFolderName')
            volFolderId = self.dsm_connection.volumes[wwn].get('volumeFolderId')
            volScName = self.dsm_connection.volumes[wwn].get('scName')
        else:
            LOG.error('Cannot get volume with WWN %s.', wwn)
            return None

        return (wwn, volid, volname, volFolderName, volFolderId, volScName)

    def get_vol_wwn_from_id(self, volid):
        """
        Returns volume wwn from volume ID.

        :param volid: volume ID.
        :return: volume WWN, `None` otherwise.
        """
        self.dsm_connection.get_volumes()
        for wwn, vol_info in self.dsm_connection.volumes.items():
            if self.dsm_connection.volumes[wwn]['instanceId'] == str(volid):
                return wwn

        LOG.error('Cannot get the volume WWN from the volume ID %s.', volid)

        return None

    def generate_clone_name(self, volname):
        """
        Generates a clone name from a volume name.

        :param volname: the volume name from which to generate a clone name.
        :returns: clone name, `None`, otherwise.
        """
        # remove clone name suffix from volume name
        orig_volname = re.sub(r'_\d+$', '', volname)

        # get list of volumes starting with 'orig_volname'
        self.dsm_connection.get_volumes()
        lst = []
        for vol in self.dsm_connection.volumes.values():
            if vol['name'].startswith(orig_volname) and not vol['inRecycleBin']:
                lst.append(vol['name'])

        if len(lst) == 0:
            LOG.error('Clone name cannot be generated as no volumes is found.')
            return None

        # get indexes in the volume list
        volname_with_index = re.compile(r'.*(_\d+)$')
        volindex_lst = [int(volname_.replace(f'{orig_volname}_', ''))
                        for volname_ in lst if volname_with_index.match(volname_)]
        volindex_lst.sort()
        if len(volindex_lst) == 0:
            clone_index = 1
        else:
            clone_index = volindex_lst[-1] + 1

        return f'{orig_volname}_{clone_index}'

    def get_local_server_id(self):
        """Returns local server ID, or `None` on error."""
        hostname = self.process.get_hostname()
        server_name = hostname.split('.')[0]

        server_id = self.dsm_connection.get_server_id(server_name)
        if server_id is None:
            LOG.error('Cannot get server ID of local server %s.', server_name)

        return server_id

    def replace_volume(self, src_mountpoint, dst_mountpoint):
        """
        Clones the volume mounted on `src_mountpoint` and mount it on `dst_mountpoint`,
        the volume that was mounted on `dst_mountpoint` will be deleted.

        :param src_mountpoint: mountpoint of the volume to be cloned.
        :param dst_mountpoint: mountpoint of the clone volume.
        :return: `True` for success, `False` on error.
        """
        # check details of vols on source and destination mountpoints
        # volume details: (wwn, volid, volname, volFolderName, volFolderId, scName)
        src_vol_info = self.get_volume_info(mountpoint=src_mountpoint)
        if src_vol_info is None:
            return False

        dst_vol_info = self.get_volume_info(mountpoint=dst_mountpoint)
        if dst_vol_info is None:
            return False

        # unmount the volume to be cloned, call it "the source volume"
        if not self.process.umount(src_mountpoint):
            return False

        # create a volume snapshot from the source volume
        snapshot_id = self.dsm_connection.create_snapshot(src_vol_info[1])
        if snapshot_id is None:
            return False

        # check if the source volume is a camsis volume
        replay_profile_id = None
        self.dsm_connection.get_snapshot_profiles()
        if self.dsm_connection.rply_profiles is None:
            return False

        if 'camsis' in src_vol_info[3].lower():
            # we're sure 'camsis' replay profile exists
            replay_profile_id = self.dsm_connection.rply_profiles['camsis']['instanceId']

        # create a clone volume from the source volume
        clone_name = self.generate_clone_name(src_vol_info[2])
        view_vol_id = self.dsm_connection.create_view_volume(
            snapshot_id, replay_profile_id, clone_name, src_vol_info[4])

        # get local server id and map view volume to server
        server_id = self.get_local_server_id()
        if server_id is None:
            return False

        if not self.dsm_connection.map_volume_to_server(view_vol_id, server_id):
            return False

        # mount the source volume
        if not self.process.mount(src_mountpoint):
            return False

        # prepare to mount the view volume in place of the destination volume
        view_vol_wwn = self.get_vol_wwn_from_id(view_vol_id)
        if view_vol_wwn is None:
            return False

        # rescan scsi bus to read the new volume mapped to the server
        if not self.process.rescan_scsibus():
            return False

        # update multipath.conf
        if not self.process.add_multipath_alias(view_vol_wwn):
            return False

        dst_vol_fs_device = self.process.get_fsdevice_from_mountpoint(dst_mountpoint)
        view_vol_alias = self.process.get_mpath_from_wwn(view_vol_wwn)
        view_vol_fs_device = f'/dev/mapper/{view_vol_alias}p1'

        # unmount the destination volume and mount view volume
        if not self.process.umount(dst_mountpoint):
            return False

        if not self.process.replace_entry_in_fstab(dst_vol_fs_device, view_vol_fs_device):
            return False

        if not self.process.daemon_reload():
            return False

        if not self.process.mount(dst_mountpoint):
            return False

        # delete destination volume
        result_delete_vol = self.delete_volume(dst_vol_info[0])

        return True if result_delete_vol else False

    def delete_volume(self, wwn, recycle=True):
        """
        Deletes a volume with `wwn`.

        :param wwn: `wwn` of the volume to delete.
        :returns: `True` for success, `False` on error.
        """
        # check if volume is visible to local server
        alias = self.process.get_mpath_from_wwn(wwn)
        if alias is None:
            return False

        # check if volume exists on Dell SCs
        vol_info = self.get_volume_info(wwn)
        if vol_info is None:
            return False

        # make sure volume is mapped to local server
        vol_mappings = self.dsm_connection.get_vol_mappings(vol_info[1])
        servers = [x['server']['instanceName'] for x in vol_mappings]
        if self.process.get_hostname().split('.')[0] not in servers:
            LOG.error('Volume with ID %s is not mapped to local server.', vol_info[1])
            return False

        # make sure volume is not mounted
        if self.process.is_wwn_mounted(wwn) is not None:
            LOG.error('Volume with WWN %s is mounted on local server. Unmount it first.', wwn)
            return False

        # remove volume from fstab config file
        device_name = f'/dev/mapper/{alias}p1'
        if self.process.is_device_in_fstab(device_name):
            if not self.process.remove_entry_from_fstab(device_name):
                return False
            if not self.process.daemon_reload():
                return False
        else:
            LOG.warning('%s is not in /etc/fstab.', device_name)

        # remove (wwid, alias) entry from multipath.conf
        if not self.process.remove_multipath_entry(wwn, alias):
            return False

        # delete raw devices of multipath device alias
        raw_devices = self.process.get_multipath_raw_devices(alias)
        if raw_devices is None:
            LOG.warning('No raw devices for multipath device %s.', alias)
        else:
            result_delete_rawdevs = []
            for rawdev in raw_devices:
                result = self.process.delete_raw_devices(rawdev)
                result_delete_rawdevs.append(result)
            if False in result_delete_rawdevs:
                return False

        # reload multipathd
        if not self.process.reload_multipathd():
            return False

        # unmap the volume
        if not self.dsm_connection.unmap_volume(vol_info[1]):
            return False

        # delete the volume on DSM
        if not self.dsm_connection.delete_volume(vol_info[1], recycle=recycle):
            return False

        return True

    def clone_volume(self, volume_wwn, replay_label, target_mountpoint):
        """
        Creates a snapshot of a volume, then creates a view volume from the snapshot,
        map the view volume to local server and mount it on `target_mountpoint`.

        :param volume_wwn: wwn of volume from which to create the snapshot and the view volume.
        :param replay_label: label of the snapshot to create from volume_name.
        :param target_mounpoint: where to mount the view volume.
        :return: `True` for success, `False` on failure.
        """
        if not self.process.is_dir_empty(target_mountpoint):
            return False

        # get volume info: (wwn, volid, volname, volFolderName, volFolderId, scName)
        vol_info = self.get_volume_info(wwn=volume_wwn)
        if vol_info is None:
            return False

        # create snapshot from volume
        snapshot_id = self.dsm_connection.create_snapshot(vol_info[1])
        if snapshot_id is None:
            return False

        # create view volume
        view_volume_name = f"{vol_info[2]}_{replay_label}"
        view_volume_id = self.dsm_connection.create_view_volume(
            snapshot_id, None, view_volume_name, vol_info[4])

        # get view volume wwn
        view_volume_wwn = self.get_vol_wwn_from_id(view_volume_id)

        if view_volume_wwn is None:
            return False

        # get local server id and map view volume to server
        server_id = self.get_local_server_id()
        if server_id is None:
            return False

        if not self.dsm_connection.map_volume_to_server(view_volume_id, server_id):
            return False

        # rescan scsi bus
        if not self.process.rescan_scsibus():
            return False

        # add multipath alias of view volume wwid
        if not self.process.add_multipath_alias(view_volume_wwn):
            return False

        # update fstab file
        new_alias = self.process.get_mpath_from_wwn(view_volume_wwn)
        if new_alias is not None:
            new_fsdevice = f'/dev/mapper/{new_alias}p1'
            if not self.process.add_entry_in_fstab(new_fsdevice, target_mountpoint):
                LOG.error('%s cannot be added to /etc/fstab', new_fsdevice)
                return False
            if not self.process.daemon_reload():
                return False
        else:
            LOG.error('Alias for the view volume WWN %s does not exist.', view_volume_wwn)
            return False

        # mount target_mountpoint if it's not mounted
        # found it gets mounted after reload multipath, is it an expected behaviour?
        if not self.process.mountpoint_exists(target_mountpoint):
            if not self.process.mount(target_mountpoint):
                return False

        return True

    def create_snapshot(self, mountpoint, label, retention):
        """
        Creates a snapshot of the volume mounted on `mountpoint`.

        :param mountpoint: the mountpoint where the volume is mounted.
        :param label: snapshot label.
        :param retention: retention period of the snapshot to create, in days.
        :return: `True` for success, `False` on error.
        """
        # check if snapshot label is valid
        if not self.process.is_snapshot_label_valid(label):
            LOG.error('Snapshot label %s is not valid.', label)
            return False

        # check if the retention is between 1 and 99 days
        if not (int(retention) in range(1, 100)):
            LOG.error('Retention %s is not valid.', retention)
            return False

        # check if volume is on DSM
        vol_info = self.get_volume_info(mountpoint=mountpoint)
        if vol_info is None:
            LOG.error('No info on volume mounted on %s.', mountpoint)
            return False

        # get fsdevice. TODO: is this check really needed?
        fsdevice = self.process.get_fsdevice_from_mountpoint(mountpoint)
        if fsdevice is None:
            LOG.error('No fs device of volume mounted on %s.', mountpoint)
            return False

        # create the snapshot
        result = self.dsm_connection.create_snapshot(vol_info[1], label, int(retention)*1440)

        return False if result is None else True

    def delete_recycled_vols(self, recycled_vols_file):
        """
        Deletes the volumes listed in a file passed in argument.
        The volume must be in Recycle Bin to be deleted.

        :param recycled_vols_file: file containing the list of recycled volumes to be deleted.
        Each line in the file should contain the volume's WWN.
        The file should only contain lines in the following format:
        ('6000d31000e3940000000000000001c9', {'instanceId': '58260.165', \
            'inRecycleBin': True, 'volumeFolderPath': 'All Volumes/SB_VMWare_vols/', \
            'volumeFolderName': 'SB_VMWare_vols', 'volumeFolderId': '58260.11', \
            'status': 'Down', 'name': 'test_vol', 'scName': 'WCDC Storage Center'})
        :return: `True` if all the volumes that are in Recycle Bin are deleted, `False` otherwise.
        """
        if not self.dsm_connection.get_recycled_volumes():
            return False

        wwns = []
        with open(recycled_vols_file, 'r') as rvf:
            # extract the wwn and ignore the commented lines
            for line in rvf:
                if not line.startswith('#'):
                    rs = re.search(r"\('[A-Za-z0-9]{32}'", line)
                    if rs:
                        wwns.append(rs.group(0).replace("'", '').replace("(", ''))
                    else:
                        LOG.warning("Cannot find a valid WWN in the line starting with %s.", line[0:50])

        results = []
        for wwn in wwns:
            if self.dsm_connection.recycled_vols.get(wwn) is None:
                LOG.warning(f"Volume with WWN '{wwn}' will not be deleted as the WWN may not be valid"
                            " or the volume is not in Recycle Bin.")
            else:
                LOG.info('Volume %s will be DELETED from the Recyle Bin!', wwn)
                result_del_vol = self.dsm_connection.delete_volume(
                    self.dsm_connection.recycled_vols[wwn]['instanceId'], recycle=False)
                results.append(result_del_vol)

        return False if False in results else True
