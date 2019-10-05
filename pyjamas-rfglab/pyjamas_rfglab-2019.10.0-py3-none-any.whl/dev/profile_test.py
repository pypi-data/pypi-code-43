import pstats, cProfile

import numpy as np
from pyjamas.pjscore import PyJAMAS
from pyjamas.rimage.rimcore import rimage
from pyjamas.rimage.rimutils import rimutils

apjs = PyJAMAS()
animage = rimage(apjs.imagedata)

cProfile.runctx("animage.livewire([329, 146], [377, 59], PyJAMAS.livewire_margin)", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()

%load_ext line_profiler
r = %lprun -r -f animage.livewire animage.livewire([329, 146], [377, 59], PyJAMAS.livewire_margin)

s = %lprun -r -f rimutils.makeGraph rimutils.makeGraph(apjs.imagedata[48:151, 329:418])

t = %lprun -r -f makeGraph makeGraph(apjs.imagedata[48:151, 329:418])

im = apjs.imagedata[48:151, 329:418]
rows = np.arange(im.shape[0])
cols = np.arange(im.shape[1])
therows, thecols = np.meshgrid(rows, cols)

therows = np.reshape(therows, therows.size)
thecols = np.reshape(thecols, thecols.size)

all_pixels = np.array([(arow, acol) for arow, acol in zip(therows, thecols)])

# Declaration of the matrix that contains pairs of neighbouring nodes and the cost associated with that edge.
# This is the fastest way to create a matrix full of infinity values.
weight_matrix = np.empty((all_pixels.shape[0], all_pixels.shape[0])) + np.inf

# Now build the matrix.
# For each pixel.
for i, coords in enumerate(all_pixels):
    isrc = rimutils.sub2ind(im.shape, np.array([coords[0]]), np.array([coords[1]]))

    # Calculate the neighbours and find their pixel ids and coordinates.
    theneighbours = rimutils._N8_(coords[0], coords[1], im.shape)
    theneighbours_ind = rimutils.sub2ind(im.shape, theneighbours[:, 0],
                                         theneighbours[:, 1])  # Convert all vertices once and use dictionary?

    weight_matrix[isrc, theneighbours_ind] = im[theneighbours[:, 0], theneighbours[:, 1]]

s = %lprun -r -f csgraph_from_dense csgraph_from_dense(weight_matrix)

import numpy
from scipy.sparse.csgraph import csgraph_from_dense
def makeGraph(im: numpy.ndarray = None):
    rows = numpy.arange(im.shape[0])
    cols = numpy.arange(im.shape[1])
    therows, thecols = numpy.meshgrid(rows, cols)

    therows = numpy.reshape(therows, therows.size)
    thecols = numpy.reshape(thecols, thecols.size)

    all_pixels = numpy.array([(arow, acol) for arow, acol in zip(therows, thecols)])

    # Find one index per pixel.
    all_pixels_ind = rimutils.sub2ind(im.shape, all_pixels[:, 0], all_pixels[:, 1])

    # Declaration of the matrix that contains pairs of neighbouring nodes and the cost associated with that edge.
    weight_matrix = numpy.full((all_pixels_ind.size, all_pixels_ind.size), numpy.inf)

    # Now build the matrix.
    # For each pixel.
    for i, coords in enumerate(all_pixels):
        # Calculate the neighbours and find their pixel ids and coordinates.
        theneighbours = _N8_(coords[0], coords[1], im.shape)
        theneighbours_ind = rimutils.sub2ind(im.shape, theneighbours[:, 0],
                                             theneighbours[:, 1])  # Convert all vertices once and use dictionary?
        isrc = rimutils.sub2ind(im.shape, numpy.array([coords[0]]), numpy.array([coords[1]]))
        # For each neighbour ...
        for j, idst in enumerate(theneighbours_ind):
            weight_matrix[isrc, idst] = im[theneighbours[j, 0], theneighbours[j, 1]]

    # And use the matrix to build the graph.
    graph_sparse = csgraph_from_dense(weight_matrix, null_value=numpy.inf)

    return graph_sparse, weight_matrix


from pyjamas.pjscore import PyJAMAS
from pyjamas.rimage.rimcore import rimage

apjs = PyJAMAS()
animage = rimage(apjs.imagedata)

%load_ext cython

%%cython -a
import numpy
from pyjamas.rimage.rimutils import rimutils
from scipy.sparse.csgraph import csgraph_from_dense
cimport numpy as cnumpy
from typing import Tuple
import cProfile

def makeGraph_cython(cnumpy.ndarray[unsigned short, ndim=2] im = None):
    rows = numpy.arange(im.shape[0])
    cols = numpy.arange(im.shape[1])
    therows, thecols = numpy.meshgrid(rows, cols)

    therows = numpy.reshape(therows, therows.size)
    thecols = numpy.reshape(thecols, thecols.size)

    all_pixels = numpy.array([(arow, acol) for arow, acol in zip(therows, thecols)])

    # Find one index per pixel.
    cdef cnumpy.ndarray[long, ndim = 1] all_pixels_ind
    all_pixels_ind = sub2ind_cython((im.shape[0], im.shape[1]), all_pixels[:, 0], all_pixels[:, 1])

    # Declaration of the matrix that contains pairs of neighbouring nodes and the cost associated with that edge.
    weight_matrix = numpy.ones((all_pixels_ind.size, all_pixels_ind.size)) * numpy.inf

    # Now build the matrix.
    # For each pixel.
    cdef cnumpy.ndarray[short, ndim = 1] theneighbours_ind, isrc
    cdef cnumpy.ndarray[short, ndim = 2] theneighbours
    cdef int i
    cdef cnumpy.ndarray[long, ndim = 1] coords
    for i, coords in enumerate(all_pixels):
        # Calculate the neighbours and find their pixel ids and coordinates.
        theneighbours = rimutils._N8_(coords[0], coords[1], (im.shape[0], im.shape[1]))
        theneighbours_ind = sub2ind_cython((im.shape[0], im.shape[1]), theneighbours[:, 0], theneighbours[:, 1])  # Convert all vertices once and use dictionary?
        isrc = sub2ind_cython((im.shape[0], im.shape[1]), numpy.array([coords[0]], dtype=numpy.short), numpy.array([coords[1]], dtype=numpy.short))
        # For each neighbour ...
        for j, idst in enumerate(theneighbours_ind):
            weight_matrix[isrc, idst] = im[theneighbours[j, 0], theneighbours[j, 1]]

    # And use the matrix to build the graph.
    graph_sparse = csgraph_from_dense(weight_matrix, null_value=numpy.inf)

    return graph_sparse, weight_matrix

%%cython -a
import numpy
from pyjamas.rimage.rimutils import rimutils
from scipy.sparse.csgraph import csgraph_from_dense
cimport numpy as cnumpy
def sub2ind_cython(cnumpy.ndarray[long, ndim=1] array_shape, cnumpy.ndarray[long, ndim=1] rows, cnumpy.ndarray[long, ndim=1] cols) -> numpy.ndarray:
    ind = rows * array_shape[1] + cols

    if type(ind) == numpy.int:
        ind = numpy.array([ind])

    bad_values = numpy.concatenate(((ind < 0).nonzero(), (ind >= numpy.prod(array_shape)).nonzero()))

    ind[bad_values] = -1

    return ind

%timeit makeGraph_cython(apjs.imagedata[80:110, 320:350])
cProfile.run('makeGraph_cython(apjs.imagedata[80:110, 320:350])', sort='time')


from pyjamas.pjscore import PyJAMAS
from pyjamas.rimage.rimutils import rimutils

apjs = PyJAMAS()

%timeit rimutils.makeGraph(apjs.imagedata[80:110, 320:350])




%timeit rimutils.sub2ind([10, 10], numpy.asarray([3, 8, 9, 1, 0, 2]), numpy.asarray([7, 5, 3, 2, 5, 9]))
%load_ext line_profiler
r = %lprun -r -f rimutils.sub2ind([10, 10], numpy.asarray([3, 8, 9, 1, 0, 2]), numpy.asarray([7, 5, 3, 2, 5, 9]))
import pprofile
def func_to_profile_rodrigo():
    prof = pprofile.Profile()
    with prof():
        rimutils.sub2ind([10, 10], numpy.asarray([3, 8, 9, 1, 0, 2]), numpy.asarray([7, 5, 3, 2, 5, 9]))
    prof.print_stats()


###############----------------------------------------------
import numpy

im = numpy.random.randint(low=0, high=255, size=(120, 120))
im = numpy.asarray([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]])

from itertools import tee

def pairwise_noncyclic(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


from __future__ import division

from networkx import DiGraph
from networkx.generators.classic import empty_graph


def makeGraphX(im: numpy.ndarray):
    """Returns the two-dimensional grid graph.

    The graph is non periodic and directed.

    The grid graph has each node connected to its eight nearest neighbors.

    Parameters
    ----------
    m, n : int or iterable container of nodes
        If an integer, nodes are from `range(n)`.
        If a container, elements become the coordinate of the nodes.

    Returns
    -------
    NetworkX graph
        The directed grid graph of the specified dimensions.

    """

    G = empty_graph(0, DiGraph())
    rows = range(im.shape[0])
    cols = range(im.shape[1])
    cols_minus1 = range(im.shape[1]-1)
    G.add_nodes_from((i, j) for i in rows for j in cols)
    G.add_weighted_edges_from(((i, j), (pi, j), im[pi, j])
                     for pi, i in pairwise_noncyclic(rows) for j in cols)
    G.add_weighted_edges_from(((pi, j), (i, j), im[i, j])
                     for pi, i in pairwise_noncyclic(rows) for j in cols)
    G.add_weighted_edges_from(((i, j), (i, pj), im[i, pj])
                     for i in rows for pj, j in pairwise_noncyclic(cols))
    G.add_weighted_edges_from(((i, pj), (i, j), im[i, j])
                     for i in rows for pj, j in pairwise_noncyclic(cols))
    G.add_weighted_edges_from(((i, j), (pi, j+1), im[pi, j+1])
                     for pi, i in pairwise_noncyclic(rows) for j in cols_minus1)
    G.add_weighted_edges_from(((pi, j+1), (i, j), im[i, j])
                     for pi, i in pairwise_noncyclic(rows) for j in cols_minus1)
    G.add_weighted_edges_from(((i, j+1), (pi, j), im[pi, j])
                     for pi, i in pairwise_noncyclic(rows) for j in cols_minus1)
    G.add_weighted_edges_from(((pi, j), (i, j+1), im[i, j+1])
                     for pi, i in pairwise_noncyclic(rows) for j in cols_minus1)

    return G
