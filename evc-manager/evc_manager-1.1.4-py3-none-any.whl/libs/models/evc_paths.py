""" Evaluate EVC's requested paths

EvcPath has to be a list of paths and each path has to be a list of NNIs.
Paths at the beginning of the list have priority over following ones.

"""


from .nni import NNI


class EvcPath(object):
    """ EvcPath Class. Parent class of EthernetVirtualCircuit """

    def __init__(self, paths=None):
        super(EvcPath, self).__init__()
        self._paths = list()
        if paths:
            self.paths = paths

    @property
    def paths(self):
        """ Getter """
        return self._paths

    @paths.setter
    def paths(self, paths):
        """ Setter """
        self._paths = self.test_paths(paths)

    def test_paths(self, paths):
        """ Evaluate the provided requested path"""

        if not isinstance(paths, list):
            raise ValueError('Must be a list of NNIS')

        if len(paths) == 0:
            raise ValueError('Must be a list of NNIS')

        for path in paths:
            if not isinstance(path, list):
                raise ValueError('Must be a list of NNIS')

            for nni in path:

                if not isinstance(nni, NNI):
                    try:
                        return self.test_paths(self.convert_to_nnis(paths))
                    except (KeyError, ValueError, TypeError):
                        raise ValueError('Must be a list of NNIS')
        return paths

    @staticmethod
    def convert_to_nni(nni):
        """ Convert a dict to a NNI """
        link = NNI()
        link.device_a = nni['node_a']
        link.interface_a = nni['interface_a']
        link.device_z = nni['node_z']
        link.interface_z = nni['interface_z']
        link.name = nni['name']
        return link

    def convert_to_nnis(self, paths):
        """ In case a list of lists of dictionaries is provided
         convert to NNIs """
        try:
            new_paths = list()
            for path in paths:
                new_path = list()
                for nni in path:
                    new_path.append(self.convert_to_nni(nni))
                    new_paths.append(new_path)
                del new_path
            return new_paths
        except KeyError:
            raise ValueError("NNI provided has wrong format")

    def __iter__(self):
        """
        :return:
        """
        pos = 0
        while pos < len(self._paths):
            yield self._paths[pos]
            pos += 1

    def has_backup(self):
        """ Just query if requested path has a backup"""
        if len(self._paths) > 1:
            return True

    def get_path(self, path_type, full_format=False):
        """ Return path if any

        Args:
            path_type: if we will query for Primary (0) or
                Backup (1).
            full_format: True to return full path or False
                if just a string with names is desired.
        Returns:
            based on full_format
        """
        if not full_format:
            if not self.paths[path_type]:
                return 'UnSet'
            else:
                if not full_format:
                    named_path = list()
                    for path in self.paths[path_type]:
                        named_path.append(path.name)
                    return ' '.join(named_path)
                else:
                    return self.paths

    def get_primary_path(self, full_format=False, primary=0):
        """ Return primary path if any """
        return self.get_path(primary, full_format)

    def get_backup_path(self, full_format=False, backup=1):
        """ Return backup path if any """

        if len(self.paths) > 1:
            return self.get_path(backup, full_format)
        return 'None'
