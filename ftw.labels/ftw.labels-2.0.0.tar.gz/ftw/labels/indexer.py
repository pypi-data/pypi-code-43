from ftw.labels.interfaces import ILabelSupport
from ftw.labels.interfaces import ILabeling
from plone.indexer.decorator import indexer


@indexer(ILabelSupport)
def labels(obj):
    labeling = ILabeling(obj)
    labels = []
    for label_id in labeling.storage:
        try:
            label = labeling.jar.get(label_id)
            if label['by_user']:
                if len(labeling.storage[label_id]):
                    # if at least one user has selected the label, we add it
                    labels.append(label_id)
                    # add each combination user:label
                    for user_id in labeling.storage[label_id]:
                        labels.append('%s:%s' % (user_id, label_id))
            else:
                labels.append(label_id)
        except KeyError:
            pass
    # store something when no label. Query with 'not' in ZCatalog>=3 will retrieve it.
    if not labels:
        return ['_']
    return labels
