from ftw.labels.interfaces import ILabeling
from ftw.labels.interfaces import ILabelJar
from ftw.labels.interfaces import ILabelSupport
from ftw.labels.utils import make_sortable
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import implements


ANNOTATION_KEY = 'ftw.labels:labeling'


class Labeling(object):
    implements(ILabeling)
    adapts(ILabelSupport)

    def __init__(self, context):
        self.context = context
        self.jar = ILabelJar(self.context)

    def update(self, label_ids):
        jar_keys = self.jar.storage.keys()
        # removes deselected labels
        for label_id in self.storage.keys():  # use keys to avoid RuntimeError: dictionary changed size during iteration
            if label_id not in jar_keys:
                continue  # do we remove key ??
            label = self.jar.get(label_id)
            if label_id not in label_ids:
                if not label['by_user']:
                    self.storage.pop(label_id)

        # adds selected labels
        for label_id in label_ids:
            if label_id not in jar_keys:
                raise LookupError(
                    'Cannot activate label: '
                    'the label "{0}" is not in the label jar. '
                    'Following labels ids are available: {1}'.format(
                        label_id, ', '.join(jar_keys)))
            if label_id not in self.storage:
                self.storage[label_id] = PersistentList()

    def pers_update(self, label_ids, activate):
        user_id = self.user_id()
        if not user_id:
            return False
        if activate:
            for label_id in label_ids:
                if label_id not in self.storage:
                    self.storage[label_id] = PersistentList()
                if user_id not in self.storage[label_id]:
                    self.storage[label_id].append(user_id)
        else:
            for label_id in label_ids:
                if user_id in self.storage[label_id]:
                    self.storage[label_id].remove(user_id)
                if not self.storage[label_id]:
                    self.storage.pop(label_id)
        return True

    def active_labels(self):
        # selected labels
        labels = []
        for label_id in self.storage:
            try:
                label = self.jar.get(label_id)
                if label['by_user']:
                    if self.user_id() in self.storage[label_id]:
                        labels.append(label)
                else:
                    labels.append(label)
            except KeyError:
                pass
        return sorted(labels, key=lambda cls: make_sortable(cls['title']))

    def available_labels(self):
        # possible labels, marking active ones
        labels = [[], []]
        for label in self.jar.list():
            if label['by_user']:
                label['active'] = (label['label_id'] in self.storage and
                                   self.user_id() in self.storage[label['label_id']])
                labels[0].append(label)
            else:
                label['active'] = (label.get('label_id') in self.storage)
                labels[1].append(label)
        labels[0].sort(key=lambda cls: make_sortable(cls['title']))
        labels[1].sort(key=lambda cls: make_sortable(cls['title']))
        return labels

    def user_id(default=None):
        """ Return current userid """
        cur_user = api.user.get_current()
        if not cur_user:
            return default
        return cur_user.getId()

    @property
    def storage(self):
        if getattr(self, '_storage', None) is None:
            annotation = IAnnotations(self.context)
            if ANNOTATION_KEY not in annotation:
                annotation[ANNOTATION_KEY] = PersistentMapping()
            self._storage = annotation[ANNOTATION_KEY]
        return self._storage
