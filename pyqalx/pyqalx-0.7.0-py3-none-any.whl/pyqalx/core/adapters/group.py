from pyqalx.core.adapters.adapter import QalxUnpackableAdapter
from pyqalx.core.entities import Group, Set


class QalxGroup(QalxUnpackableAdapter):
    _entity_class = Group
    child_entity_class = Set

    def add(self, sets, meta=None, **kwargs):
        """
        When adding a `Group` ensure that the sets posted to the api are in
        the format {<key>: pyqalx.entities.Set}

        :param sets: A dictionary of Sets to create on the group
        :type sets: dict
        :param meta: A dictionary of metadata to store
        :type meta: dict
        :return: A newly created `Group` instance
        """
        return super(QalxGroup, self).add(sets=sets,
                                          meta=meta,
                                          **kwargs)
