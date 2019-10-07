import os
import shlex

class Volume(object):
    def __init__(self, volumedef):
        fields = volumedef.split(':')
        self.hostpath = os.path.expanduser(fields[0])
        if not os.path.isabs(self.hostpath):
            raise ValueError('host path is not absolute for volume "{}"'.format(volumedef))
        if not os.path.exists(self.hostpath):
            raise ValueError('host path does not exist for volume "{}"'.format(volumedef))
        try:
            self.guestpath = fields[1]
        except KeyError:
            raise ValueError('invalid parameter format for volume "{}"'.format(volumedef))
        if not os.path.isabs(self.guestpath):
            raise ValueError('guest path is not absolute for volume "{}"'.format(volumedef))
        try:
            if fields[2] == 'ro':
                self.writable = False
            elif fields[2] == 'rw':
                self.writable = True
            else:
                raise ValueError('wrong R/W flag for volume "{}"'.format(volumedef))
        except KeyError:
            self.writable = True

    def volumedef(self):
        return '{}:{}:{}'.format(self.hostpath, self.guestpath, 'rw' if self.writable else 'ro')

class VolumeGroup(list):
    def __init__(self, volumedefs=None):
        if isinstance(volumedefs, str):
            volumedefs = shlex.split(volumedefs)
        if volumedefs is not None:
            for volumedef in volumedefs:
                self.append(Volume(volumedef))

    def guest_path_list(self):
        return [x.guestpath for x in self]

    def volume_def_list(self):
        return [x.volumedef() for x in self]

