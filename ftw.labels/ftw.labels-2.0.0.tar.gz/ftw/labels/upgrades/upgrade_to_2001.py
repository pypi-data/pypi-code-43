# -*- coding: utf-8 -*-
from ftw.labels.interfaces import ILabelJar
from ftw.labels.interfaces import ILabelJarChild
from ftw.labels.interfaces import ILabelRoot
from ftw.labels.interfaces import ILabelSupport
from ftw.labels.labeling import ILabeling
from plone import api
from zope.annotation.interfaces import IAnnotations


def upgrade_to_2001(context):
    """
        Add 'by_user' key to False in jar.
        Migrate annotation content on ILabelSupport to replace PersistentList by PersistentMapping.
    """
    # take all elements who provides ftw.labels.interfaces.ILabelRoot or ILabelJarChild
    portal_catalog = api.portal.get_tool('portal_catalog')
    brains = portal_catalog(object_provides=(ILabelRoot.__identifier__, ILabelJarChild.__identifier__))
    for brain in brains:
        jar = ILabelJar(brain.getObject())
        for key in jar.storage.keys():
            if 'by_user' not in jar.storage[key].keys():
                # give default value if not exist
                jar.storage[key]['by_user'] = False

    # take all elements who provides ftw.labels.interfaces.IlabelSupport
    brains = portal_catalog(object_provides=ILabelSupport.__identifier__)
    # Transform PersistentList in PersistentMapping
    for brain in brains:
        obj = brain.getObject()
        labeling = ILabeling(obj)
        old_values = [label for label in labeling.storage]
        annotation = IAnnotations(obj)
        del annotation['ftw.labels:labeling']
        labeling._storage = None
        labeling.update(old_values)
