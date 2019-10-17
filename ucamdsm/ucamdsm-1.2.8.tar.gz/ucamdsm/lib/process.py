"""Utilities for linux filesystems administration"""
import datetime
import itertools
import logging
import re
import shlex
import shutil
import subprocess
import time
from pathlib import Path

LOG = logging.getLogger(__name__)

FSTAB_CONF = '/etc/fstab'
FSTAB_BACKUP_DIR = '/etc/fstab.bkp'
MULTIPATH_CONF = '/etc/multipath.conf'
MULTIPATH_BACKUP_DIR = '/etc/multipath.bkp'
MULTIPATH_CMD = '/sbin/multipath'


class Process():

    def __init__(self):
        pass

    def run(self, command, stdin=subprocess.PIPE, stdout=subprocess.PIPE):
        """
        Runs a Shell command.

        :param command: command to run.
        :param stdin: stdin of the command execution, default: subprocess.PIPE.
        :param stdout: stdout of the command execution, default: subprocess.PIPE.
        :returns: tuple (return_code, stdout_data, stderr_data).
        """
        sub_cmds = [list(x[1]) for x in itertools.groupby(shlex.split(command), lambda x: x == '|') if not x[0]]

        processes = []
        for sub_cmd in sub_cmds:
            p = subprocess.Popen(sub_cmd, stdin=stdin, stdout=stdout)
            stdin = p.stdout
            processes.append(p)

        result = returncode = None
        num_proc = len(processes)
        for idx, proc in enumerate(processes):
            if idx == num_proc - 1:
                result = proc.communicate()
                returncode = proc.returncode
            else:
                proc.stdout.close()

        if returncode != 0:
            LOG.error("Run command: [%s] | Return Code: %s | Stdout: %s | Stderr: %s.",
                      command, returncode, result[0], result[1])
        else:
            LOG.info("Run command: [%s] | Return Code: %s | Number of words in stdout: %s | Stderr: %s.",
                     command, returncode, len(result[0].split()), result[1])

        return (returncode, result[0].decode(encoding='utf-8', errors='strict').rstrip('\n'), result[1])

    def get_hostname(self):
        """
        Gets hostname of local server.

        :returns: server's hostname or `None` for error.
        """
        cmd = 'hostname'
        result = self.run(cmd)

        return result[1] if result[0] == 0 else False

    def mountpoint_exists(self, mountpoint):
        """
        Checks if mountpoint exists.

        :param mountpoint: mountpoint to check.
        :returns: `True` if the mountpoint exists, `False` otherwise.
        """
        if not Path(mountpoint).is_dir():
            LOG.error('%s is not a directory.', mountpoint)
            return False

        cmd = f"df -h | egrep '{mountpoint}' | wc -l"
        result = self.run(cmd)

        return True if int(result[1]) == 1 else False

    def get_fsdevice_from_mountpoint(self, mountpoint):
        """
        Gets filesystem device from mountpoint.

        Example: mountpoint = /d03 --> fsdevice = /dev/mapper/vold03p1.

        :param mountpoint: the mountpoint to look for its filesystem device.
        :returns: fsdevice or `None` if fsdevice not found.
        """
        if not self.mountpoint_exists(mountpoint):
            return None

        # get mountpoint
        cmd = f"df -h | egrep '{mountpoint}' | awk '{{ print $1 }}'"
        result = self.run(cmd)

        return result[1] if result[0] == 0 else None

    def get_mpath_from_mountpoint(self, mountpoint):
        """
        Gets mpath from mountpoint.

        Example: mountpoint = /d03 --> mpath = /dev/mapper/vold03.

        :param mountpoint: the mountpoint to look for its mpath.
        :returns: mpath of mountpoint, or None if no mpath is found.
        """
        partname = self.get_fsdevice_from_mountpoint(mountpoint)

        if partname is not None:
            if partname.endswith('p1'):
                return partname[:-2]
            else:
                LOG.error('mpath of volume mounted %s cannot be found.', mountpoint)
        else:
            LOG.error('Cannot get fs device from the mountpoint %s.', mountpoint)

        return None

    def get_wwn_from_mpath(self, mpath_device):
        """
        Gets `wwn` of a mpath.

        Example: mpath = vold03p1 --> wwn = '6000d31000e3940000000000000001fd'.

        :param mpath_device: mpath device to look for its wwn.
        :returns: wwn of mpath device, `None` otherwise.
        """
        result0, result1 = self.run(f"dirname {mpath_device}"), self.run(f"basename {mpath_device}")

        if 1 in [result0[0], result1[0]]:
            LOG.error('Cannot get dirname (%s) or basename (%s) of mpath %s.', result0[1], result1[1], mpath_device)
            return None

        dirname, basename = result0[1], result1[1]

        if dirname in ['.', '/']:
            dirname = '/dev/mapper'

        mpath = f'{dirname}/{basename}'

        # issue sg_inq command
        cmd = f"/usr/bin/sg_inq -i {mpath}"
        result = self.run(cmd)

        if result[0] != 0:
            return None

        try:
            return re.search(r'\[0x.{32}\]', result[1]).group()[3:35]
        except AttributeError:
            LOG.error('WWN of mpath %s is not found in sg_inq command output.', mpath)

        return None

    def get_mpath_from_wwn(self, wwn):
        """
        Gets `mpath` of a `wwn` by looking in `multipath -ll` output.

        Example: wwn = '6000d31000e3940000000000000001fd' --> mpath = vold03.

        :param mpath: mpath to look for its wwn.
        :returns: mpath or None if mpath is not found.
        """
        if not self.is_wwn_valid(wwn):
            return None

        # show multipath config and get mpath of a wwn
        cmd = f"{MULTIPATH_CMD} -ll | grep -i '{wwn}' | awk '{{ print $1 }}'"
        result = self.run(cmd)

        return result[1] if result[0] == 0 else None

    def is_wwn_valid(self, wwn):
        """
        Checks if `wwn` is valid.

        A valid WWN should have 32 or 33 characters.

        :param wwn: the wwn to check
        :returns: `True` if wwn is valid, otherwise, `False`.
        """
        if len(wwn) not in [32, 33]:
            LOG.error('%s is invalid wwn.', wwn)
            return False
        else:
            return True

    def is_wwn_mounted(self, wwn):
        """
        Checks if a device with `wwn` is mounted.

        :param wwn: `wwn` of the device to check.
        :returns: mountpoint if the device is mounted, `None`, otherwise.
        """
        if not self.is_wwn_valid(wwn):
            return None

        alias = self.get_mpath_from_wwn(wwn)
        if alias is None:
            return None

        # check if wwn is mounted
        cmd = f"df -h | grep '/dev/mapper/{alias}p1' | awk '{{ print $6 }}'"
        result = self.run(cmd)

        if result[0] == 0:
            return None if result[1] == '' else result[1]
        else:
            return None

    def generate_devicemapper_alias(self):
        """
        Generates a new device mapper alias.

        :returns: alias name, `None` for error.
        """
        # get existing aliases in MULTIPATH_CONF
        cmd = f"grep alias {MULTIPATH_CONF} | awk '{{ print $2 }}'"
        result = self.run(cmd)
        if result[0] != 0:
            return None

        lst_aliases = result[1].split()
        alias_pattern = re.compile(r'vold\d\d')
        lst_indexes = [int(alias.replace('vold', '')) for alias in lst_aliases if alias_pattern.match(alias)]
        lst_indexes.sort()

        if len(lst_indexes) == 0:
            return 'vold01'

        new_index = lst_indexes[-1] + 1
        new_alias = f"vold{new_index:02d}"

        # make sure the new alias does not exist in lst_aliases
        assert new_alias not in lst_aliases

        return new_alias

    def is_device_valid(self, device):
        """
        Checks if device name is valid.

        A valid device name should start with '/dev/mapper/vold' and ends with 'p1'.

        :param device: device name to check.
        :returns: `True` if device name is valid, otherwise, `False`.
        """
        device_name_pattern = re.compile(r'^/dev/mapper/vold.*p1$')
        if device_name_pattern.match(device) is None:
            LOG.error('%s is not a valid device name.', device)
            return False

        return True

    def get_wwid_from_wwn(self, wwn):
        """Obtains wwid from wwn by looking at `multipath -ll` command output."""
        wwid_cmd = f"{MULTIPATH_CMD} -ll | grep -i '{wwn}' | awk '{{ print $2 }}' | sed -e 's/(//g' -e 's/)//g'"
        wwid_result = self.run(wwid_cmd)
        if wwid_result[0] != 0 or str(wwid_result[1]) == '':
            LOG.error('WWID cannot be obtained from multipath -ll. Result: %s.', wwid_result)
            return None

        return str(wwid_result[1])

    def add_multipath_alias(self, wwn):
        """
        Adds a multipath alias to MULTIPATH_CONF file.

        :param wwn: wwn to add to MULTIPATH_CONF.
        :returns: `True` for success, `False` for error.
        """
        if not self.is_wwn_valid(wwn):
            return False

        # check if wwn already exists in MULTIPATH_CONF file
        if wwn in self.read_file(MULTIPATH_CONF):
            LOG.warning('WWN %s is already in %s.', wwn, MULTIPATH_CONF)
            return False

        wwid = self.get_wwid_from_wwn(wwn)
        if wwid is None:
            return False

        # generate new alias
        alias = self.generate_devicemapper_alias()
        if alias is None:
            LOG.error('Alias for wwn %s could not be generated.', wwn)
            return False

        # backup MULTIPATH_CONF file
        if not self.backup_file(MULTIPATH_CONF, MULTIPATH_BACKUP_DIR):
            return False

        # create the multipath entry to add to MULTIPATH_CONF file
        new_multipath_entry = f"multipath {{" \
                              f"\n             wwid {wwid}" \
                              f"\n             alias {alias}" \
                              f"\n          }}" \
                              f"\n#MULTIPATH_PLACEHOLDER"

        # replace #MULTIPATH_PLACEHOLDER by new_multipath_entry in MULTIPATH_CONF file
        content = self.read_file(MULTIPATH_CONF)
        config = content.replace('#MULTIPATH_PLACEHOLDER', new_multipath_entry)
        new_config_file = open(MULTIPATH_CONF, 'w')
        new_config_file.write(config)
        new_config_file.close()

        return self.reload_multipathd()

    def remove_multipath_entry(self, wwn, alias):
        """
        Removes a multipath entry from MULTIPATH_CONF file.

        :param wwn: wwn of the multipath entry to remove.
        :param alias: alias of the multipath entry to remove
        :returns: `True` for success, `False` for error.
        """
        # backup MULTIPATH_CONF file
        if not self.backup_file(MULTIPATH_CONF, MULTIPATH_BACKUP_DIR):
            return False

        wwid = self.get_wwid_from_wwn(wwn)
        if wwid is None:
            return False

        content = self.read_file(MULTIPATH_CONF)
        regex = r"multipath\s*{\s*wwid\s+" + re.escape(wwid) + r"\s+alias\s+" + re.escape(alias) + r"\s*}\s*"
        if re.search(regex, content) is None:
            LOG.warning('Multipath entry for wwn %s and alias %s does not exist.', wwid, alias)
            return True

        new_content = re.sub(regex, '', content)
        new_config_file = open(MULTIPATH_CONF, 'w')
        new_config_file.write(new_content)
        new_config_file.close()

        return True

    def mount(self, fs):
        """
        Mounts a filesystem or mountpoint if provided.

        :returns: `True` for success, `False` for error.
        """
        cmd = f'mount {fs}'
        result = self.run(cmd)

        return True if result[0] == 0 else False

    def umount(self, fs):
        """
        Unmounts a filesystem, or mountpoint if provided.

        :returns: `True` for success, `False` for error.
        """
        cmd = f'umount {fs}'
        result = self.run(cmd)

        return True if result[0] == 0 else False

    def is_device_in_fstab(self, device):
        """
        Checks if device is in FSTAB_CONF file.

        :param device: device to check in FSTAB_CONF.
        :returns: `True` if device in FSTAB_CONF, otherwise, `False`.
        """
        if not self.is_device_valid(device):
            return False

        volname = device.split('/')[3]

        # check if a volume name exists in FSTAB_CONF
        cmd = f"cat {FSTAB_CONF} | grep -v '^#' | grep '{volname}' | wc -l"
        result = self.run(cmd)

        return True if (result[0], int(result[1])) == (0, 1) else False

    def is_string_in_file(self, string, filename):
        """
        Checks if a `string` is in `filename`.

        :param string: the string to look for in the file.
        :param file: the file to search in.
        :returns: `True` if `string` in `file`, `False`, otherwise.
        """
        if not Path(filename).exists():
            LOG.error('File %s does not exist.', filename)
            return False

        if not Path(filename).is_file():
            LOG.error('%s is not a file.', filename)
            return False

        if string not in self.read_file(filename):
            LOG.error('%s not in %s.', string, filename)
            return False

        return True

    def replace_entry_in_fstab(self, old_fs_device, new_fs_device):
        """
        Replaces entry in FSTAB_CONF file.

        :param old_fs_device: fs device to be replaced.
        :param new_fs_device: new fs device to replace old_fs_device.
        :return: `True` if task completed successfully, otherwise, `False`.
        """
        if not self.is_device_valid(old_fs_device) or not self.is_device_valid(new_fs_device):
            return False

        if not self.is_string_in_file(old_fs_device, FSTAB_CONF):
            return False

        if not self.backup_file(FSTAB_CONF, FSTAB_BACKUP_DIR):
            return False

        old_vol_name = old_fs_device.split('/')[3]
        new_vol_name = new_fs_device.split('/')[3]

        # replace old volume name with new volume name in FSTAB_CONF
        cmd = f"sed -i 's/{old_vol_name}/{new_vol_name}/' {FSTAB_CONF}"
        result = self.run(cmd)

        return True if result[0] == 0 else False

    def add_entry_in_fstab(self, fs_device, mountpoint, fstype='ext4'):
        """
        Adds `fs_device` in FSTAB_CONF file.

        :param fs_device: fs device to add.
        :param mountpoint: mountpoint of fs device.
        :param fstype: fs type of fs device.
        :returns: `True` for success, `False` for error.
        """
        if not self.is_device_valid(fs_device):
            return False

        if fstype not in ['ext3', 'ext4', 'xfs']:
            LOG.error('fstype is not supported.')
            return False

        if not self.backup_file(FSTAB_CONF, FSTAB_BACKUP_DIR):
            return False

        new_fstab_entry = f"{fs_device}\t{mountpoint}\t{fstype}\tdefaults\t1 1\n"
        with open(FSTAB_CONF, 'a') as fstab_conf_file:
            fstab_conf_file.write(new_fstab_entry)

        return True

    def remove_entry_from_fstab(self, fs_device):
        """
        Removes `fs_device` from FSTAB_CONF file.

        :param fs_device: fs device to remove.
        :returns: `True` for success, `False` for error.
        """
        if not self.is_device_valid(fs_device):
            return False

        if not self.is_string_in_file(fs_device, FSTAB_CONF):
            return False

        if not self.backup_file(FSTAB_CONF, FSTAB_BACKUP_DIR):
            return False

        content = self.read_file(FSTAB_CONF)
        regex = r"\n" + re.escape(fs_device) + r"\s+.*"
        if re.search(regex, content) is None:
            LOG.error('fstab entry for %s does not exist.', fs_device)
            return False

        new_content = re.sub(regex, '', content)
        new_config_file = open(FSTAB_CONF, 'w')
        new_config_file.write(new_content)
        new_config_file.close()

        return True

    def flush_multipath_devices(self):
        """
        Flushes multipath devices via the command `multipath -F`.

        :returns: `True` for success, `False` for error.
        """
        cmd = f'{MULTIPATH_CMD} -F'
        result = self.run(cmd)

        return True if result[0] == 0 else False

    def reload_multipathd(self):
        """
        Reloads the multipathd service.

        :returns: `True` for success, `False` for error.
        """
        cmd = 'service multipathd reload'
        result = self.run(cmd)

        time.sleep(5)

        return True if result[0] == 0 else False

    def daemon_reload(self):
        """
        Reloads systemd manager configuration

        :returns: `True` for success, `False` for error.
        """
        cmd = 'systemctl daemon-reload'
        result = self.run(cmd)

        time.sleep(5)

        return True if result[0] == 0 else False

    def get_multipath_raw_devices(self, mpath_alias):
        """
        Gets multipath raw devices of a multipath device.

        Example: mpath_alias = vold01 --> ['sdc', 'sdb'].

        :param mpath_alias: multipath device alias.
        :returns: list of multipath raw devices, `None` for error.
        """
        cmd = f"{MULTIPATH_CMD} -ll {mpath_alias} | cut -c6- | grep -E 'ready|faulty' | awk '{{ print $2 }}'"
        result = self.run(cmd)

        return result[1].split('\n') if result[0] == 0 and result[1] != '' else None

    def delete_raw_devices(self, raw_device):
        """
        Deletes a raw device.

        :param raw_device: raw device to delete.
        :returns: `True` for success, `False` for error.
        """
        with open(f'/sys/block/{raw_device}/device/delete', 'w') as outfile:
            outfile.write('1')

        return True

    def is_dir_empty(self, path):
        """
        Checks if a directory is empty.

        :param path: path of the directory to check.
        :returns: `True` if the directory, `False` otherwise.
        """
        if not Path(path).is_dir():
            LOG.error('Path %s is not a directory.', path)
            return False

        if len(list(Path(path).glob('*'))) > 0:
            LOG.error('Directory %s is not empty.', path)
            return False

        return True

    def rescan_scsibus(self):
        """
        Scans SCSI bus on local server.

        :return: `True` for success, `False` on error.
        """
        for host in Path('/sys/class/scsi_host').iterdir():
            with open(f'{host}/scan', 'w') as outfile:
                outfile.write('- - -\n')

        # wait for 20 seconds
        time.sleep(20)

        LOG.info('rescan_scsibus() succeeded.')

        # TODO we need to check if file writing succeeded
        return True

    def backup_file(self, file_, backup_dir):
        """
        Backups a file.

        Copies `file_` to `backup_dir` directory and name the new file `file.timestamp`.

        :param file_: the full path and the name of the file to back up.
        :param backup_dir: the path of the new file.
        :returns: `True` if backup task succeeded, `False`, otherwise.
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')

        if not Path(file_).exists():
            LOG.error('%s does not exist.', file_)
            return False

        if not Path(file_).is_file():
            LOG.error('%s is not a file.', file_)
            return False

        Path(backup_dir).mkdir(parents=True, exist_ok=True)

        file_basename = Path(file_).resolve().name
        destination = Path(f'{backup_dir}/{file_basename}.{timestamp}')

        try:
            result = shutil.copy(file_, destination)
        except OSError as error:
            LOG.error('File %s cannot be backed up. Error: %s', file_, error)
            return False

        if result == destination:
            LOG.info('backup_file(%s, %s) succeeded.', file_, backup_dir)
            return True
        else:
            LOG.error('backup_file(%s, %s) failed.', file_, backup_dir)
            return False

    def is_snapshot_label_valid(self, label):
        """
        Checks if snapshot label is valid.

        A snapshot label should be a string of alphanumeric characters with a length in [2, 30].

        :param label: the snapshot label to check.
        :return: `True` if the label is valid, `False` otherwise.
        """
        label_pattern = re.compile(r'^\w{2,30}$')
        if label_pattern.match(label) is None:
            LOG.error('%s is not a valid snapshot label.', label)
            return False

        return True

    def record_config_details(self):
        """
        Logs `df`, `multipath`, and `fstab` config details.
        """
        fstab_conf_content = self.read_file(FSTAB_CONF)
        multipath_conf_content = self.read_file(MULTIPATH_CONF)

        df_cmd_result = self.run('df -h')
        df_output = df_cmd_result[1]

        multipath_cmd_result = self.run('multipath -ll')
        multipath_output = multipath_cmd_result[1]

        LOG.info('Content of /etc/fstab:\n%s', fstab_conf_content)
        LOG.info('Content of /etc/multipath.conf:\n%s', multipath_conf_content)

        LOG.info('Output of df -h:\n%s', df_output)
        LOG.info('Output of multipath -ll:\n%s', multipath_output)

    def read_file(self, filename):
        """
        Reads a file.

        :param filename: the name of file to read.
        :returns: content of the file to read, or `None` on error.
        """
        content = None
        try:
            content = open(filename).read()
        except Exception as e:
            LOG.error('Cannot read %s. Error: %s', filename, e)

        return content
