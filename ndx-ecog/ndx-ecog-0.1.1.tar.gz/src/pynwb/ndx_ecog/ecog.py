from collections import Iterable

import numpy as np
from hdmf.utils import popargs, get_docval, docval
from pynwb import register_class
from pynwb.core import NWBContainer, MultiContainerInterface
from pynwb.file import Subject
from pynwb.base import Images


@register_class('Surface', 'ndx-ecog')
class Surface(NWBContainer):
    __nwbfields__ = ('faces', 'vertices')

    @docval({'name': 'name', 'type': str, 'doc': 'name'},
            {'name': 'vertices', 'type': Iterable, 'shape': (None, 3),
             'doc': 'vertices for surface, points in 3D space'},
            {'name': 'faces', 'type': Iterable, 'shape': (None, 3),
             'doc': 'faces for surface, indexes vertices'})
    def __init__(self, **kwargs):
        name, vertices, faces = popargs('name', 'vertices', 'faces', kwargs)
        super(Surface, self).__init__(name)
        if np.max(faces) >= len(vertices):
            raise ValueError('index of faces exceeds number vertices for {}. '
                             'Faces should be 0-indexed, not 1-indexed'.
                             format(name))
        if np.min(faces) < 0:
            raise ValueError('faces hold indices of vertices and should be non-negative')
        self.faces = faces
        self.vertices = vertices


@register_class('CorticalSurfaces', 'ndx-ecog')
class CorticalSurfaces(MultiContainerInterface):
    """
    Spike data for spike events detected in raw data
    stored in this NWBFile, or events detect at acquisition
    """

    __clsconf__ = {
        'attr': 'surfaces',
        'type': Surface,
        'add': 'add_surface',
        'get': 'get_surface',
        'create': 'create_surface'
    }

    __help = "triverts for cortical surfaces"


@register_class('ECoGSubject', 'ndx-ecog')
class ECoGSubject(Subject):

    __nwbfields__ = ({'name': 'cortical_surfaces', 'child': True},
                     {'name': 'images', 'child': True})

    @docval(*get_docval(Subject.__init__) + (
        {
            'name': 'cortical_surfaces',
            'doc': 'extension of Subject that allows adding cortical surface data',
            'type': CorticalSurfaces,
            'default': None,
        },
        {
            'name': 'images',
            'doc': "Images of subject's brain",
            'type': Images,
            'default': None
        })
            )
    def __init__(self, **kwargs):
        cortical_surfaces, images = popargs('cortical_surfaces', 'images', kwargs)
        super(ECoGSubject, self).__init__(**kwargs)
        self.cortical_surfaces = cortical_surfaces
        self.images = images
