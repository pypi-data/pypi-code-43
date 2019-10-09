from copy import deepcopy
from collections import defaultdict

from sage.misc.misc_c import prod

from sage.combinat.subset import Subsets
from sage.rings.integer_ring import ZZ
from sage.modules.free_module import FreeModule
from sage.functions.other import floor
from sage.graphs.graph import Graph
from sage.rings.all import Integer
from sage.arith.all import factorial
from sage.groups.perm_gps.permgroup_named import SymmetricGroup

# graphics:
from sage.repl.rich_output.pretty_print import show
from sage.plot.polygon import polygon2d
from sage.plot.text import text
from sage.plot.bezier_path import bezier_path
from sage.plot.line import line
from sage.plot.circle import circle

class StableGraph(object):
    r"""
    Stable graph.

    A stable graph is a graph (with allowed loops and multiple edges) that
    has "genus" and "marking" decorations at its vertices. It is represented
    as a list of genera of its vertices, a list of legs at each vertex and a
    list of pairs of legs forming edges.

    The markings (the legs that are not part of edges) are allowed to have
    repetitions.

    EXAMPLES:

    We create a stable graph with two vertices of genera 3,5 joined by an edge
    with a self-loop at the genus 3 vertex::

        sage: from admcycles import StableGraph
        sage: StableGraph([3,5], [[1,3,5],[2]], [(1,2),(3,5)])
        [3, 5] [[1, 3, 5], [2]] [(1, 2), (3, 5)]

    The markings can have repetitions::

         sage: StableGraph([1,0], [[1,2], [3,2]], [(1,3)])
         [1, 0] [[1, 2], [3, 2]] [(1, 3)]

    It is also possible to create graphs which are not neccesarily stable::

        sage: StableGraph([1,0], [[1], [2,3]], [(1,2)])
        [1, 0] [[1], [2, 3]] [(1, 2)]

        sage: StableGraph([0], [[1]], [])
        [0] [[1]] []

    If the input is invalid a ``ValueError`` is raised::

        sage: StableGraph([0, 0], [[1], [2], [3]], [])
        Traceback (most recent call last):
        ...
        ValueError: genera and legs must have the same length

        sage: StableGraph([0, 'hello'], [[1], [2]], [(1,2)])
        Traceback (most recent call last):
        ...
        ValueError: genera must be a list of non-negative integers

        sage: StableGraph([0, 0], [[1,2], [3]], [(3,4)])
        Traceback (most recent call last):
        ...
        ValueError: the edge (3, 4) uses invalid legs

        sage: StableGraph([0, 0], [[2,3], [2]], [(2,3)])
        Traceback (most recent call last):
        ...
        ValueError: the edge (2, 3) uses invalid legs
    """
    def __init__(self, genera, legs, edges, check=True):
        """
        INPUT:

        - ``genera`` -- (list) List of genera of the vertices of length m.

        - ``legs`` -- (list) List of length m, where ith entry is list of legs
          attached to vertex i.

        - ``edges`` -- (list) List of edges of the graph. Each edge is a 2-tuple of legs.
        """
        if check:
            if not isinstance(genera, list) or \
               not isinstance(legs, list) or \
               not isinstance(edges, list):
                   raise TypeError('genera, legs, edges must be lists')

            if len(genera) != len(legs):
                raise ValueError('genera and legs must have the same length')

            if not all(isinstance(g, (int, Integer)) and g >= 0 for g in genera):
                raise ValueError("genera must be a list of non-negative integers")

            mlegs = defaultdict(int)
            for v,l in enumerate(legs):
                if not isinstance(l, list):
                    raise ValueError("legs must be a list of lists")
                for i in l:
                    if not isinstance(i, (int, Integer)) or i <= 0:
                        raise ValueError("legs must be positive integers")
                    mlegs[i] += 1

            half_edges = []
            for e in edges:
                if not isinstance(e, tuple) or len(e) != 2:
                    raise ValueError("invalid edge {}".format(e))
                if mlegs.get(e[0], 0) != 1 or mlegs.get(e[1], 0) != 1:
                    raise ValueError("the edge {} uses invalid legs".format(e))

        self.genera = genera
        self.legs = legs
        self.edges = edges
        self.maxleg = max([max(j+[0]) for j in self.legs]) #highest leg-label that occurs

    def __repr__(self):
        return repr(self.genera)+ ' ' + repr(self.legs) + ' ' + repr(self.edges)

    def __eq__(self,other):
        r"""
        TESTS::

            sage: from admcycles import StableGraph
            sage: G1 = StableGraph([3,5], [[1,3,5],[2]], [(1,2),(3,5)])
            sage: G2 = StableGraph([3,5], [[1,3,5],[2]], [(1,2),(3,5)])
            sage: G3 = StableGraph([3,5], [[3,5,1],[2]], [(2,1),(3,5)])
            sage: G4 = StableGraph([2,2], [[1,3,5],[2]], [(1,2),(3,5)])
            sage: G5 = StableGraph([3,5], [[1,4,5],[2]], [(1,2),(4,5)])
            sage: G1 == G2
            True
            sage: G1 == G3 or G1 == G4 or G1 == G5
            False
        """
        if type(self) is not type(other):
            return False
        return self.genera == other.genera and \
               self.legs == other.legs and \
               self.edges == other.edges

    def __ne__(self, other):
        return not (self == other)

    def _graph(self):
        # TODO: it should be much faster to build this graph...
        from collections import defaultdict

        legs = defaultdict(list)

        # the multiplicity of edges is stored as integral labels
        # on the graph
        G = Graph(len(self.genera), loops=True, multiedges=False)
        for li,lj in self.edges:
            i = self.vertex(li)
            j = self.vertex(lj)
            if G.has_edge(i, j):
                G.set_edge_label(i, j, G.edge_label(i, j) + 1)
            else:
                G.add_edge(i, j, 1)

            if i < j:
                legs[i,j].append((li,lj))
            else:
                legs[j,i].append((lj,li))

        vertex_partition = defaultdict(list)
        for i, (g,l) in enumerate(zip(self.genera, self.legs)):
            l = list(self.list_markings(i))
            l.sort()
            inv = (g,) + tuple(l)
            vertex_partition[inv].append(i)

        vertex_data = sorted(vertex_partition)
        partition = [vertex_partition[k] for k in vertex_data]

        return G, vertex_data, dict(legs), partition

    def _canonical_label(self):
        G, _, _, partition = self._graph()

        # NOTE: we explicitely set algorithm='sage' since bliss got confused
        # with edge labeled graphs. See
        # https://trac.sagemath.org/ticket/28531
        H, phi = G.canonical_label(partition=partition,
                                   edge_labels=True,
                                   certificate=True,
                                   algorithm='sage')

        return (H, phi)

    # TODO: to keep consistancy with reorder_vertices and rename_legs, should
    # we do the relabeling inplace?
    # (sage graphs do not do inplace by default)
    def relabel(self, vm, lm):
        r"""
        INPUT:

        - ``vm`` - a vertex map (from the label of this graph to the new labels)

        - ``lm`` - a leg map (idem)

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([3,5], [[1,3,5,4],[2]],  [(1,2),(3,5)])
            sage: G.relabel({0:1, 1:0}, {1:3, 2:5, 3:7, 4:9, 5:15})
            [5, 3] [[5], [3, 7, 15, 9]] [(3, 5), (7, 15)]
        """
        m = len(self.genera)
        genera = [None] * m
        legs = [None] * m
        for i,(g,l) in enumerate(zip(self.genera, self.legs)):
            j = vm[i] # new label
            genera[j] = g
            legs[j] = [lm[k] for k in l]

        edges = [(lm[i], lm[j]) for i,j in self.edges]

        return StableGraph(genera, legs, edges)

    def is_isomorphic(self, other, certificate=False):
        r"""
        Test whether this stable graph is isomorphic to ``other``.

        INPUT:

        - ``certificate`` - if set to ``True`` return also a vertex mapping and
                            a legs mapping

        EXAMPLES::

            sage: from admcycles import StableGraph

            sage: G1 = StableGraph([3,5], [[1,3,5,4],[2]],  [(1,2),(3,5)])
            sage: G2 = StableGraph([3,5], [[2,3,1,4],[5]],  [(2,5),(3,1)])
            sage: G3 = StableGraph([5,3], [[5],[2,3,4,1]],  [(2,5),(3,1)])
            sage: G1.is_isomorphic(G2) and G1.is_isomorphic(G3)
            True

        Graphs with distinct markings are not isomorphic::

            sage: G4 = StableGraph([3,5], [[1,3,5,4],[2]],  [(1,2),(3,4)])
            sage: G1.is_isomorphic(G4) or G2.is_isomorphic(G4) or G3.is_isomorphic(G4)
            False

        Graph with marking multiplicities::

            sage: H1 = StableGraph([0], [[1,1]], [])
            sage: H2 = StableGraph([0], [[1,1]], [])
            sage: H1.is_isomorphic(H2)
            True

            sage: H3 = StableGraph([0,0], [[1,2,4],[1,3]], [(2,3)])
            sage: H4 = StableGraph([0,0], [[1,2],[1,3,4]], [(2,3)])
            sage: H3.is_isomorphic(H4)
            True

        TESTS::

            sage: from admcycles import StableGraph

            sage: G = StableGraph([0, 0], [[5, 8, 4, 3], [9, 2, 1]], [(8, 9)])
            sage: H = StableGraph([0, 0], [[1, 2, 6], [3, 4, 5, 7]], [(6, 7)])
            sage: G.is_isomorphic(H)
            True
            sage: ans, (vm, lm) = G.is_isomorphic(H, certificate=True)
            sage: assert ans
            sage: G.relabel(vm, lm)
            [0, 0] [[6, 2, 1], [5, 7, 4, 3]] [(7, 6)]

            sage: G = StableGraph([0, 0], [[4, 8, 2], [3, 9, 1]], [(8, 9)])
            sage: H = StableGraph([0, 0], [[1, 3, 5], [2, 4, 6]], [(5, 6)])
            sage: G.is_isomorphic(H)
            True
            sage: ans, (vm, lm) = G.is_isomorphic(H, certificate=True)
            sage: assert ans
            sage: G.relabel(vm, lm)
            [0, 0] [[3, 5, 1], [4, 6, 2]] [(6, 5)]

            sage: G = StableGraph([0, 1, 1], [[1, 3, 5], [2, 4], [6]], [(1, 2), (3, 4), (5, 6)])
            sage: H = StableGraph([1, 0, 1], [[1], [2, 3, 5], [4, 6]], [(1, 2), (3, 4), (5, 6)])
            sage: _ = G.is_isomorphic(H, certificate=True)
        """
        if type(self) != type(other):
            raise TypeError

        sG, svdat, slegs, _ = self._graph()
        oG, ovdat, olegs, _ = other._graph()

        # first compare vertex data
        if svdat != ovdat:
            return (False, None) if certificate else False

        # next, graph isomorphism
        sH, sphi = self._canonical_label()
        oH, ophi = other._canonical_label()
        if sH != oH:
            return (False, None) if certificate else False

        if certificate:
            ophi_inv = {j: i for i,j in ophi.items()}
            vertex_map = {i: ophi_inv[sphi[i]] for i in range(len(self.genera))}

            legs_map = {}
            # legs that are not part of edges are untouched
            # (slot zero in the list is the genus)
            for l in svdat:
                for i in l[1:]:
                    legs_map[i] = i

            # pair of legs that form edges have moved
            for (i,j),sl in slegs.items():
                m = sG.edge_label(i, j)
                assert len(sl) == m, (m, sl, self, other)

                ii = ophi_inv[sphi[i]]
                jj = ophi_inv[sphi[j]]
                if ii <= jj:
                    ol = olegs[ii,jj]
                else:
                    ol = [(b,a) for (a,b) in olegs[jj,ii]]
                assert len(ol) == m, (m, sl, ol, self, other)

                for (a,b),(c,d) in zip(sl,ol):
                    legs_map[a] = c
                    legs_map[b] = d

            return True, (vertex_map, legs_map)

        else:
            return True

    def vertex_automorphism_group(self, *args, **kwds):
        r"""
        Return the action of the automorphism group on the vertices.

        All arguments provided are forwarded to the method `automorphism_group`
        of Sage graphs.

        EXAMPLES::

            sage: from admcycles import StableGraph

            sage: G = StableGraph([0], [[1, 2, 3, 4, 5, 6]], [(3, 4), (5, 6)])
            sage: G.vertex_automorphism_group()
            Permutation Group with generators [()]

            sage: G = StableGraph([0, 0], [[1, 1, 2], [1, 1, 3]], [(2, 3)])
            sage: G.vertex_automorphism_group()
            Permutation Group with generators [(0,1)]
            sage: G = StableGraph([0, 0], [[4, 1, 2], [1, 3, 4]], [(3, 2)])
            sage: G.vertex_automorphism_group()
            Permutation Group with generators [(0,1)]

            sage: G = StableGraph([0, 0, 0], [[1,2], [3,4], [5,6]],
            ....:                 [(2,3),(4,5),(6,1)])
            sage: A = G.vertex_automorphism_group()
            sage: A
            Permutation Group with generators [(1,2), (0,1)]
            sage: A.cardinality()
            6

        Using extra arguments::

            sage: G.vertex_automorphism_group(algorithm='sage')
            Permutation Group with generators [(1,2), (0,1)]
            sage: G.vertex_automorphism_group(algorithm='bliss')   # optional - bliss
            Permutation Group with generators [(1,2), (0,1)]
        """
        G, _, _, partition = self._graph()
        return G.automorphism_group(partition=partition,
                                    edge_labels=True,
                                    *args, **kwds)

    def leg_automorphism_induce(self, g, A=None, check=True):
        r"""
        Given a leg automorphism ``g`` return its action on the vertices.

        Note that there is no check that the element ``g`` is a valid automorphism.

        INPUT:

        - ``g`` - a permutation acting on the legs

        - ``A`` - ambient permutation group for the result

        - ``check`` - (default ``True``) parameter forwarded to the constructor
          of the permutation group acting on vertices.

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([0, 0, 0, 0], [[1,8,9,16], [2,3,10,11], [4,5,12,13], [6,7,14,15]],
            ....:                 [(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14),(15,16)])
            sage: Averts = G.vertex_automorphism_group()
            sage: Alegs = G.leg_automorphism_group()
            sage: g = Alegs('(1,14)(2,13)(3,4)(5,10)(6,9)(7,8)(11,12)(15,16)')
            sage: assert G.leg_automorphism_induce(g) == Averts('(0,3)(1,2)')
            sage: g = Alegs('(3,11)(4,12)(5,13)(6,14)')
            sage: assert G.leg_automorphism_induce(g) == Averts('')
            sage: g = Alegs('(1,11,13,15,9,3,5,7)(2,12,14,16,10,4,6,8)')
            sage: assert G.leg_automorphism_induce(g) == Averts('(0,1,2,3)')

        TESTS::

            sage: G = StableGraph([3], [[]], [])
            sage: S = SymmetricGroup([0])
            sage: G.leg_automorphism_induce(S(''))
            ()
        """
        if A is None:
            A = SymmetricGroup(list(range(len(self.genera))))
        if len(self.genera) == 1:
            return A('')
        p = [self.vertex(g(self.legs[u][0])) for u in range(len(self.genera))]
        return A(p, check=check)

    def vertex_automorphism_lift(self, g, A=None, check=True):
        r"""
        Provide a canonical lift of vertex automorphism to leg automorphism.

        Note that there is no check that ``g`` defines a valid automorphism of
        the vertices.

        INPUT::

        - ``g`` - permutation automorphism of the vertices

        - ``A`` - an optional permutation group in which the result belongs to

        - ``check`` -- (default ``True``) parameter forwarded to the constructor
          of the permutation group

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([0, 0, 0, 0], [[1,8,9,16], [2,3,10,11], [4,5,12,13], [6,7,14,15]],
            ....:                 [(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14),(15,16)])
            sage: Averts = G.vertex_automorphism_group()
            sage: G.vertex_automorphism_lift(Averts(''))
            ()
            sage: G.vertex_automorphism_lift(Averts('(0,3)(1,2)'))
            (1,6)(2,5)(3,4)(7,8)(9,14)(10,13)(11,12)(15,16)
            sage: G.vertex_automorphism_lift(Averts('(0,1,2,3)'))
            (1,3,5,7)(2,4,6,8)(9,11,13,15)(10,12,14,16)
        """
        p = sorted(sum(self.legs, []))
        if A is None:
            A = SymmetricGroup(p)
        leg_pos = {j:i for i,j in enumerate(p)}

        G, _, edge_to_legs, partition = self._graph()

        # promote automorphisms of G as automorphisms of the stable graph
        for u,v,lab in G.edges():
            gu = g(u)
            gv = g(v)

            if u < v:
                start = edge_to_legs[u,v]
            else:
                start = [(t,s) for s,t in edge_to_legs[v,u]]

            if gu < gv:
                end = edge_to_legs[gu,gv]
            else:
                end = [(t,s) for s,t in edge_to_legs[gv,gu]]

            for (lu, lv), (glu, glv) in zip(start, end):
                p[leg_pos[lu]] = glu
                p[leg_pos[lv]] = glv

        return A(p, check=check)

    def leg_automorphism_group_vertex_stabilizer(self, *args, **kwds):
        r"""
        Return the group of automorphisms of this stable graph stabilizing the vertices.

        All arguments are forwarded to the subgroup method of the Sage symmetric group.

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([0],[[1,2,3,4,5,6,7,8]], [(1,2),(3,4),(5,6),(7,8)])
            sage: G.leg_automorphism_group_vertex_stabilizer()
            Subgroup generated by [(1,2), (1,3)(2,4), (1,3,5,7)(2,4,6,8)] of (Symmetric group of order 8! as a permutation group)

            sage: G = StableGraph([1,1],[[1,2],[3,4]], [(1,3),(2,4)])
            sage: G.leg_automorphism_group_vertex_stabilizer()
            Subgroup generated by [(1,2)(3,4)] of (Symmetric group of order 4! as a permutation group)
        """
        legs = sorted(sum(self.legs, []))
        leg_pos = {j:i for i,j in enumerate(legs)}

        G, _, edge_to_legs, partition = self._graph()

        S = SymmetricGroup(legs)
        gens = []
        for u,v,lab in G.edges():
            if lab == 1 and u != v:
                continue

            if u < v:
                multiedge = edge_to_legs[u,v]
            else:
                multiedge = edge_to_legs[v,u]

            if lab >= 2:
                (lu0, lv0) = multiedge[0]
                (lu1, lv1) = multiedge[1]
                gens.append( S.element_class([(lu0, lu1), (lv0, lv1)], S, check=False) )
                if lab >= 3:
                    gens.append( S.element_class([ tuple(x for x,y in multiedge),
                                     tuple(y for x,y in multiedge) ], S, check=False) )
            if u == v:
                (lu, lv) = multiedge[0]
                gens.append( S.element_class([ (lu, lv) ], S, check=False) )

        return S.subgroup(gens, *args, **kwds)

    def leg_automorphism_group(self, *args, **kwds):
        r"""
        Return the action of the automorphism group on the legs.

        The arguments provided to this function are forwarded to the
        constructor of the subgroup of the symmetric group.

        EXAMPLES::

            sage: from admcycles import StableGraph

        A triangle::

            sage: G = StableGraph([0, 0, 0], [[1,2], [3,4], [5,6]],
            ....:                 [(2,3),(4,5),(6,1)])
            sage: Alegs = G.leg_automorphism_group()
            sage: assert Alegs.cardinality() == G.automorphism_number()

        A vertex with four loops::

            sage: G = StableGraph([0], [[1,2,3,4,5,6,7,8]], [(1,2),(3,4),(5,6),(7,8)])
            sage: Alegs = G.leg_automorphism_group()
            sage: assert Alegs.cardinality() == G.automorphism_number()
            sage: a = Alegs.random_element()

        Using extra arguments::

            sage: G = StableGraph([0,0,0], [[6,1,7,8],[2,3,9,10],[4,5,11,12]],
            ....:       [(1,2), (3,4), (5,6), (7,8), (9,10), (11,12)])
            sage: G.leg_automorphism_group()
            Subgroup generated by [(11,12), (9,10), (7,8), (1,2)(3,6)(4,5)(7,9)(8,10), (1,6)(2,5)(3,4)(9,11)(10,12)] of (Symmetric group of order 12! as a permutation group)
            sage: G.leg_automorphism_group(canonicalize=False)
            Subgroup generated by [(1,6)(2,5)(3,4)(9,11)(10,12), (1,2)(3,6)(4,5)(7,9)(8,10), (11,12), (9,10), (7,8)] of (Symmetric group of order 12! as a permutation group)
        """
        legs = sorted(sum(self.legs, []))
        leg_pos = {j:i for i,j in enumerate(legs)}

        G, _, edge_to_legs, partition = self._graph()
        A = G.automorphism_group(partition=partition,
                                    edge_labels=True)

        # NOTE: this is too much generators. It is enough to move around the multiple
        # edges in each orbit of the vertex automorphism group.
        S = SymmetricGroup(legs)
        gens = []
        for g in self.vertex_automorphism_group().gens():
            gens.append(self.vertex_automorphism_lift(g, S))
        for g in self.leg_automorphism_group_vertex_stabilizer().gens():
            gens.append(g)

        return S.subgroup(gens, *args, **kwds)

    def automorphism_number(self):
        r"""
        Return the size of the automorphism group (acting on legs).

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([0, 2], [[1, 2, 4], [3, 5]], [(4, 5)])
            sage: G.automorphism_number()
            1

            sage: G = StableGraph([0, 0, 0], [[1,2,7,8], [3,4,9,10], [5,6,11,12]],
            ....:                 [(2,3),(4,5),(6,1),(8,9),(10,11),(12,7)])
            sage: G.automorphism_number()
            48
            sage: G.leg_automorphism_group().cardinality()
            48

            sage: G = StableGraph([0, 0], [[1, 1, 2], [1, 1, 3]], [(2, 3)])
            sage: G.automorphism_number()
            Traceback (most recent call last):
            ...
            NotImplementedError: automorphism_number not valid for repeated marking
        """
        G, _, _, _ = self._graph()
        aut = self.vertex_automorphism_group().cardinality()

        # edge automorphism
        for i,j,lab in G.edges():
            aut *= factorial(lab)
            if i == j:
                aut *= 2**lab

        # explicitly forbid marking multiplicity
        markings = self.list_markings()
        if len(markings) != len(set(markings)):
            raise NotImplementedError("automorphism_number not valid for repeated marking")

        return aut

    def g(self):
        r"""
        Return the genus of this stable graph

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([1,2],[[1,2], [3,4]], [(1,3),(2,4)])
            sage: G.g()
            4
        """
        return sum(self.genera) + len(self.edges) - len(self.genera) + ZZ.one()

    def n(self):
        r"""
        Return the number of legs of the stable graph.

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([1,2],[[1,2],[3,4,5,6]],[(1,3),(2,4)]);G.n()
            2
        """
        return len(self.list_markings())

    def numvert(self):
        return len(self.genera)

    def _graph_(self):
        r"""
        Return the Sage graph object encoding the stable graph

        This inserts a vertex with label (i,j) in the middle of the edge (i,j).
        Also inserts a vertex with label ('L',i) at the end of each leg l.

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: Gr = StableGraph([3,5],[[1,3,5,7],[2]],[(1,2),(3,5)])
            sage: SageGr = Gr._graph_()
            sage: SageGr
            Multi-graph on 5 vertices
            sage: SageGr.vertices(sort=False)   # random
            [(1, 2), 0, 1, (3, 5), ('L', 7)]
        """
        G = Graph(multiedges=True)
        for i, j in  self.edges:
            G.add_vertex((i, j))
            G.add_edge((i, j), self.vertex(i))
            G.add_edge((i, j), self.vertex(j))
        for i in self.list_markings():
            G.add_edge(('L', i), self.vertex(i))
        return G

    def dim(self,v=None):
        """
        Return dimension of moduli space at vertex v.

        If v=None, return dimension of entire stratum parametrized by graph.
        """
        if v is None:
            return sum([self.dim(v) for v in range(len(self.genera))])
        return 3 * self.genera[v] - 3 + len(self.legs[v])

    # TODO: deprecate and remove
    def invariant(self):
        r"""
        Return a graph-invariant in form of a tuple of integers or tuples

        At the moment this assumes that we only compare stable graph with same total
        g and set of markings
        currently returns sorted list of (genus,degree) for vertices

        IDEAS:

        * number of self-loops for each vertex

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: Gr = StableGraph([3,5],[[1,3,5,7],[2]],[(1,2),(3,5)])
            sage: Gr.invariant()
            ((3, 4, (7,)), (5, 1, ()))
        """
        return tuple(sorted([(self.genera[v], len(self.legs[v]), tuple(sorted(self.list_markings(v)))) for v in range(len(self.genera))]))

    def tidy_up(self):
        r"""
        Makes sure edges are in correct form and markings, maxleg is fine
        """
        for e in range(len(self.edges)):
            if self.edges[e][0] > self.edges[e][1]:
                self.edges[e] = (self.edges[e][1],self.edges[e][0])
        #TODO: sorting edges ascendingly
        self.maxleg = max([max(j+[0]) for j in self.legs])

    def vertex(self, l):
        r"""
        Return vertex number of leg l
        """
        for v in range(len(self.legs)):
            if l in self.legs[v]:
                return v
        return - ZZ.one() #self does not have leg l

    def list_markings(self,v=None):
        r"""
        Return the list of markings (non-edge legs) of self at vertex v.

        EXAMPLES::

            sage: from admcycles import StableGraph

            sage: gam = StableGraph([3,5],[[1,3,7],[2,4]],[(1,2)])
            sage: gam.list_markings(0)
            (3, 7)
            sage: gam.list_markings()
            (3, 7, 4)
        """
        if v is None:
            return tuple([j for v in range(len(self.genera)) for j in self.list_markings(v) ])
        s = set(self.legs[v])
        for e in self.edges:
            s -= set(e)
        return tuple(s)

    def leglist(self):
        r"""
        Return the list of legs
        """
        l = []
        for j in self.legs:
            l += j
        return l

    def halfedges(self):
        r"""
        Return the tuple containing all half-edges, i.e. legs belonging to an edge
        """
        s=()
        for e in self.edges:
            s=s+e
        return s

    def edges_between(self,i,j):
        r"""
        Return the list [(l1,k1),(l2,k2), ...] of edges from i to j, where l1 in i, l2 in j; for i==j return each edge only once
        """
        if i == j:
            return [e for e in self.edges if (e[0] in self.legs[i] and e[1] in self.legs[j] ) ]
        else:
            return [e for e in self.edges if (e[0] in self.legs[i] and e[1] in self.legs[j] ) ]+ [(e[1],e[0]) for e in self.edges if (e[0] in self.legs[j] and e[1] in self.legs[i] ) ]

    def forget_markings(self,markings):
        r"""
        Erase all legs in the list markings, do not check if this gives well-defined graph
        """
        for m in markings:
            self.legs[self.vertex(m)].remove(m)
        return self

    def leginversion(self,l):
        r"""
        Returns l' if l and l' form an edge, otherwise returns l
        """
        for e in self.edges:
            if e[0]==l:
                return e[1]
            if e[1]==l:
                return e[0]
        return l

    def stabilize(self):
        r"""
        Stabilize this stable graph.

        (all vertices with genus 0 have at least three markings) and returns (dicv,dicl,dich), with
         * dicv a dictionary sending new vertex numbers to the corresponding old vertex numbers
         * dicl a dictionary sending new marking names to the label of the last half-edge that they replaced during the stabilization
           this happens for instance if a g=0 vertex with marking m and half-edge l (belonging to edge (l,l')) is stabilized: l' is replaced by m, so dicl[m]=l'
         * dich a dictionary sending half-edges that vanished in the stabilization process to the last half-edge that replaced them
           this happens if a g=0 vertex with two half-edges a,b (whose corresponding half-edges are c,d) is stabilized: we obtain an edge (c,d) and a -> d, b -> d
        we assume here that a stabilization exists (all connected components have 2g-2+n>0)
        """
        markings = self.list_markings()
        stable = False
        verteximages = list(range(len(self.genera)))
        dicl = {}
        dich = {}
        while not stable:
            numvert = len(self.genera)
            count = 0
            stable = True
            while count < numvert:
                if self.genera[count] == 0 and len(self.legs[count]) == 1:
                    stable = False
                    e0 = self.legs[count][0]
                    e1 = self.leginversion(e0)
                    v1 = self.vertex(e1)
                    self.genera.pop(count)
                    verteximages.pop(count)
                    numvert -= 1
                    self.legs[v1].remove(e1)
                    self.legs.pop(count)
                    try:
                        self.edges.remove((e0,e1))
                    except:
                        self.edges.remove((e1,e0))
                elif self.genera[count] == 0 and len(self.legs[count]) == 2:
                    stable = False
                    e0 = self.legs[count][0]
                    e1 = self.legs[count][1]

                    if e1 in markings:
                        swap = e0
                        e0 = e1
                        e1 = swap

                    e1prime = self.leginversion(e1)
                    v1 = self.vertex(e1prime)
                    self.genera.pop(count)
                    verteximages.pop(count)
                    numvert -= 1

                    if e0 in markings:
                        dicl[e0] = e1prime
                        self.legs[v1].remove(e1prime)
                        self.legs[v1].append(e0)
                        self.legs.pop(count)
                        try:
                            self.edges.remove((e1,e1prime))
                        except:
                            self.edges.remove((e1prime,e1))
                    else:
                        e0prime = self.leginversion(e0)
                        v0 = self.vertex(e0prime)
                        self.legs.pop(count)
                        try:
                            self.edges.remove((e0,e0prime))
                        except:
                            self.edges.remove((e0prime,e0))
                        try:
                            self.edges.remove((e1,e1prime))
                        except:
                            self.edges.remove((e1prime,e1))
                        self.edges.append((e0prime,e1prime))

                        #update dich
                        dich[e0] = e1prime
                        dich[e1] = e0prime
                        dich.update({h:e1prime for h in dich if dich[h]==e0})
                        dich.update({h:e0prime for h in dich if dich[h]==e1})
                else:
                    count += 1
        return ({i:verteximages[i] for i in range(len(verteximages))},dicl,dich)

    def degenerations(self,v=None):
        r"""
        Return list of all possible degenerations of the graph G by adding an edge at v or splitting it into two vertices connected by an edge
        the new edge always comes last in the list of edges
        if v==None, return all degenerations at all vertices
        """
        if v==None:
            return [j for v in range(len(self.genera)) for j in self.degenerations(v) ]
        delist=[] # list of degenerated graphs

        g=self.genera[v]
        l=len(self.legs[v])

        # for positive genus: add loop to v and decrease genus
        if g > 0:
            G=deepcopy(self)
            G.degenerate_nonsep(v)
            delist.append(G)

        # now all graphs with separating edge : separate in (g1,M) and (g-g1,legs[v]-M), take note of symmetry and stability
        for g1 in range(floor(g/2)+1):
            for M in Subsets(set(self.legs[v])):
                if (g1 == 0  and len(M) < 2) or \
                   (g == g1 and l-len(M) < 2) or \
                   (2*g1 == g and l > 0 and (not self.legs[v][0] in M)):
                    continue
                G = deepcopy(self)
                G.degenerate_sep(v,g1,M)
                delist.append(G)
        return delist

    def newleg(self):
        r"""
        Create two new leg-indices that can be used to create an edge
        """
        self.maxleg += 2
        return (self.maxleg-1, self.maxleg)

    # TODO: this overlaps with relabel
    def rename_legs(self,di,shift=0):
        r"""
        Renames legs according to dictionary di, all other leg labels are shifted by shift (useful to keep half-edge labels separate from legs)
        TODO: no check that this renaming is legal, i.e. produces well-defined graph
        """
        for v in self.legs:
            for j in range(len(v)):
                v[j] = di.get(v[j],v[j]+shift)    #replace v[j] by di[v[j]] if v[j] in di and leave at v[j] otherwise
        for e in range(len(self.edges)):
            self.edges[e] = (di.get(self.edges[e][0],self.edges[e][0]+shift) ,di.get(self.edges[e][1],self.edges[e][1]+shift))
        self.tidy_up()

    def degenerate_sep(self, v, g1, M):
        r"""
        degenerate vertex v into two vertices with genera g1 and g(v)-g1 and legs M and complement
        add new edge (e[0],e[1]) such that e[0] is in new vertex v, e[1] in last vertex, which is added
        """
        g = self.genera[v]
        oldleg = self.legs[v]
        e = self.newleg()

        self.genera[v] = g1
        self.genera += [g-g1]
        self.legs[v] = list(M)+[e[0]]
        self.legs += [list(set(oldleg)-set(M))+[e[1]]]
        self.edges += [e]

    def degenerate_nonsep(self,v):
        e=self.newleg()
        self.genera[v] -= 1
        self.legs[v] += [e[0], e[1]]
        self.edges += [e]

    def contract_edge(self,e,adddata=False):
        r"""
        Contracts the edge e=(e0,e1) and returns the contracted graph
         if adddata=True, instead returns a tuple (gammatild,av,edgegraph,vnum) giving
          * the contracted graph gammatild
          * the number av of the vertex in gammatild on which previously the edge e had been attached
          * the graph edgegraph induced in self by the edge e (1-edge graph, all legs at the ends of this edge are considered as markings)
          * the numbers vnum (one or two) of the vertices to which e was attached (in the order in which they appear in edgegraph)
          * a surjective dictionary diccv sending old vertex numbers to new vertex numbers
        """
        v0 = self.vertex(e[0])
        v1 = self.vertex(e[1])
        newgraph = deepcopy(self)

        if v0 == v1:  # contracting a loop
            newgraph.genera[v0] += 1
            newgraph.legs[v0].remove(e[0])
            newgraph.legs[v0].remove(e[1])
            newgraph.edges.remove(e)

            if adddata:
                return (newgraph,v0, StableGraph([self.genera[v0]],[deepcopy(self.legs[v0])],[deepcopy(e)]),[v0],{v:v for v in range(len(self.genera))})
            else:
                return newgraph
        else:  # contracting an edge between different vertices
            if v0>v1:
                swap=v0
                v0=v1
                v1=swap
            g1 = newgraph.genera.pop(v1)
            newgraph.genera[v0]+=g1
            l1 = newgraph.legs.pop(v1)
            newgraph.legs[v0]+=l1
            newgraph.legs[v0].remove(e[0])
            newgraph.legs[v0].remove(e[1])
            newgraph.edges.remove(e)

            if adddata:
                diccv={v:v for v in range(v1)}
                diccv[v1]=v0
                diccv.update({v:v-1 for v in range(v1+1,len(self.genera)+1)})
                return (newgraph, v0, StableGraph([self.genera[v0],g1],[deepcopy(self.legs[v0]),deepcopy(self.legs[v1])],[e]), [v0,v1],diccv)
            else:
                return newgraph

    def glue_vertex(self,i,Gr,divGr={},divs={},dil={}):
        r"""
        Glues the stable graph ``Gr`` at the vertex ``i`` of this stable graph

        optional arguments: if divGr/dil are given they are supposed to be a dictionary, which will be cleared and updated with the renaming-convention to pass from leg/vertex-names in Gr to leg/vertex-names in the glued graph
        similarly, divs will be a dictionary assigning vertex numbers in the old self the corresponding number in the new self
        necessary condition:
              * every leg of i is also a leg in Gr
        every leg of Gr that is not a leg of i in self gets a new name
        """
        divGr.clear()
        divs.clear()
        dil.clear()

        # remove vertex i, legs corresponding to it and all self-edges
        selfedges_old=self.edges_between(i,i)
        self.genera.pop(i)
        legs_old=self.legs.pop(i)
        for e in selfedges_old:
            self.edges.remove(e)

        # when gluing in Gr, make sure that new legs corresponding to edges inside Gr
        # or legs in Gr which are already attached to a vertex different from i in self get a new unique label in the glued graph
        m=max(self.maxleg,Gr.maxleg)    #largest index used in either graph, new labels m+1, m+2, ...

        Gr_new=deepcopy(Gr) #here legs will be renamed before gluing in

        a=[]
        for l in Gr.legs:
            a+=l
        a=set(a)    # legs of Gr

        b=set(legs_old) # legs of self at vertex i

 #   c=[]
 #   for e in Gr.edges:
 #       c+=[e[0],e[1]]
 #   c=set(c) # legs of Gr that are in edge within Gr

        # set of legs of Gr that need to be relabeled: all legs of Gr that are not attached to vertex i in self
        e=a-b

        for l in e:
            m += 1
            dil[l] = m

        Gr_new.rename_legs(dil)

        # vertex dictionaries
        for j in range(i):
            divs[j] = j
        for j in range(i+1,len(self.genera)+1):
            divs[j] = j-1
        for j in range(len(Gr.genera)):
            divGr[j] = len(self.genera)+j

        self.genera+= Gr_new.genera
        self.legs+=Gr_new.legs
        self.edges+=Gr_new.edges

        self.tidy_up()

    # TODO: overlaps with relabel
    def reorder_vertices(self,vord):
        r"""
        Reorders vertices according to tuple given (permutation of range(len(self.genera)))
        """
        new_genera=[self.genera[j] for j in vord]
        new_legs=[self.legs[j] for j in vord]
        self.genera=new_genera
        self.legs=new_legs

    def extract_subgraph(self,vertices,outgoing_legs=None,rename=True):
        r"""
        extracts from self a subgraph induced by the list vertices
        if the list outgoing_legs is given, the markings of the subgraph are called 1,2,..,m corresponding to the elements of outgoing_legs
        in this case, all edges involving outgoing edges should be cut
        returns a triple (Gamma,dicv,dicl), where
               * Gamma is the induced subgraph
               * dicv, dicl are (surjective) dictionaries associating vertex/leg labels in self to the vertex/leg labels in Gamma
        if rename=False, do not rename any legs when extracting
        """
        attachedlegs=set([l for v in vertices for l in self.legs[v]])
        if outgoing_legs==None:
            alllegs=copy(attachedlegs)
            for (e0,e1) in self.edges:
                if e0 in alllegs and e1 in alllegs:
                    alllegs.remove(e0)
                    alllegs.remove(e1)
            outgoing_legs=list(alllegs)

        shift = len(outgoing_legs) + 1
        if rename:
            dicl={outgoing_legs[i]:i+1 for i in range(shift-1)}
        else:
            dicl={l:l for l in self.leglist()}

        genera = [self.genera[v] for v in vertices]
        legs = [[dicl.setdefault(l,l+shift) for l in self.legs[v]] for v in vertices]
        edges = [(dicl[e0],dicl[e1]) for (e0,e1) in self.edges if (e0 in attachedlegs and e1 in attachedlegs and (e0 not in outgoing_legs) and (e1 not in outgoing_legs))]
        dicv={vertices[i]:i for i in range(len(vertices))}

        return (StableGraph(genera,legs,edges),dicv,dicl)

    def boundary_pushforward(self, classes=None):
        r"""
        Computes the pushforward of a product of tautological classes (one for each vertex) under the 
        boundary gluing map for this stable graph.
        
        INPUT:
        
        - ``classes``  -- list (default: `None`); list of tautclasses, one for each vertex of the stable
          graph. The genus of the ith class is assumed to be the genus of the ith vertex, the markings
          of the ith class are supposed to be 1, ..., ni where ni is the number of legs at the ith vertex.
          Note: the jth leg at vertex i corresponds to the marking j of the ith class.
          For classes=None, place the fundamental class at each vertex.
        
        EXAMPLES::
        
            sage: from admcycles import StableGraph, psiclass, fundclass
            sage: B=StableGraph([2,1],[[4,1,2],[3,5]],[(4,5)])
            sage: Bclass=B.boundary_pushforward() # class of undecorated boundary divisor
            sage: Bclass*Bclass
            Graph :      [2, 1] [[4, 1, 2], [3, 5]] [(4, 5)]
            Polynomial : (-1)*psi_5^1 
            <BLANKLINE>
            Graph :      [2, 1] [[4, 1, 2], [3, 5]] [(4, 5)]
            Polynomial : (-1)*psi_4^1 
            sage: si1=B.boundary_pushforward([fundclass(2,3),-psiclass(2,1,2)]); si1
            Graph :      [2, 1] [[4, 1, 2], [3, 5]] [(4, 5)]
            Polynomial : (-1)*psi_5^1 
            sage: si2=B.boundary_pushforward([-psiclass(1,2,3),fundclass(1,2)]); si2
            Graph :      [2, 1] [[4, 1, 2], [3, 5]] [(4, 5)]
            Polynomial : (-1)*psi_4^1 
            sage: (Bclass*Bclass-si1-si2).simplify()
            <BLANKLINE>
              
        """
        from .admcycles import prodtautclass
        return prodtautclass(deepcopy(self),protaut=classes).pushforward()
    
    def boundary_pullback(self,other):
        r"""
        pulls back the tautclass/decstratum other to self and returns a prodtautclass with gamma=self
        """
        from .admcycles import tautclass, decstratum

        if isinstance(other,tautclass):
            from .admcycles import prodtautclass
            result=prodtautclass(self,[])
            for t in other.terms:
                result+=self.boundary_pullback(t)
            return result
        if isinstance(other,decstratum):
            # NOTE: this is using much more than just stable graphs
            # I would suggest to move it out of this class
            from .admcycles import (common_degenerations, prodtautclass,
                    onekppoly, kppoly, kappacl, psicl)
            commdeg = common_degenerations(self,other.gamma,modiso=True)
            result=prodtautclass(self,[])

            for (Gamma,dicv1,dicl1,dicv2,dicl2) in commdeg:
                numvert=len(Gamma.genera)
                # first determine edges that are covered by self and other - for excess int. terms
                legcount={l:0 for l in Gamma.leglist()}
                for l in dicl1.values():
                    legcount[l] += 1
                for l in dicl2.values():
                    legcount[l] += 1

                excesspoly=onekppoly(numvert)
                for e in Gamma.edges:
                    if legcount[e[0]] == 2:
                        excesspoly*=( (-1)*(psicl(e[0],numvert) + psicl(e[1],numvert)) )

                # partition vertices of Gamma according to where they go in self
                v1preim=[[] for v in range(len(self.genera))]
                for w in dicv1:
                    v1preim[dicv1[w]].append(w)

                graphpartition=[Gamma.extract_subgraph(v1preim[v],outgoing_legs=[dicl1[l] for l in self.legs[v]]) for v in range(len(self.genera))]

                v2preim=[[] for v in range(len(other.gamma.genera))]
                for w in dicv2:
                    v2preim[dicv2[w]].append(w)

                resultpoly=kppoly([],[])
                # now the stage is set to go through the polynomial of other term by term, pull them back according to dicv2, dicl2 and also add the excess-intersection terms
                for (kappa,psi,coeff) in other.poly:
                    # psi-classes are transferred by dicl2, but kappa-classes might be split up if dicv2 has multiple preimages of same vertex
                    # multiply everything together in a kppoly on Gamma, then split up this polynomial according to graphpartition
                    psipolydict={dicl2[l]: psi[l] for l in psi}
                    psipoly=kppoly([([[] for i in range(numvert)],psipolydict)],[1])

                    kappapoly=prod([prod([sum([kappacl(w,k+1,numvert) for w in v2preim[v] ])**kappa[v][k] for k in range(len(kappa[v]))])  for v in range(len(other.gamma.genera))])


                    resultpoly+=coeff*psipoly*kappapoly

                resultpoly*=excesspoly
                #TODO: filter for terms that vanish by dimension reasons?

                # now fiddle the terms of resultpoly apart and distribute them to graphpartition
                for (kappa,psi,coeff) in resultpoly:
                    decstratlist=[]
                    for v in range(len(self.genera)):
                        kappav=[kappa[w] for w in v1preim[v]]
                        psiv={graphpartition[v][2][l] : psi[l] for l in graphpartition[v][2] if l in psi}
                        decstratlist.append(decstratum(graphpartition[v][0],kappa=kappav,psi=psiv))
                    tempresu=prodtautclass(self,[decstratlist])
                    tempresu*=coeff
                    result+=tempresu
            return result

    def to_tautclass(self):
        r"""
        Returns pure boundary stratum associated to self; note: does not divide by automorphisms!
        """
        from .admcycles import tautclass, decstratum
        return tautclass([decstratum(deepcopy(self))])

    def _vertex_module(self):
        nv = len(self.genera)
        return FreeModule(ZZ, nv)

    def _edge_module(self):
        ne = len(self.edges)
        return FreeModule(ZZ, ne)

    # TODO: implement cache as this is used intensively in the flow code below
    # See https://gitlab.com/jo314schmitt/admcycles/issues/14
    def spanning_tree(self, root=0):
        r"""
        Return a spanning tree.

        INPUT:

        - ``root`` - optional vertex for the root of the spanning tree

        OUTPUT: a triple
        - list of triples ``(vertex ancestor, sign, edge index)`` where the
          triple at position ``i`` correspond to vertex ``i``.
        - the set of indices of extra edges not in the tree
        - vertices sorted according to their heights in the tree (first element is the root
          and the end of the list are the leaves). In other words, a topological sort of
          the vertices with respect to the spanning tree.

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([0,0,0], [[1,2],[3,4,5],[6,7]], [(1,3),(4,6),(5,7)])
            sage: G.spanning_tree()
            ([None, (0, -1, 0), (1, -1, 1)], {2}, [0, 1, 2])
            sage: G.spanning_tree(1)
            ([(1, 1, 0), None, (1, -1, 1)], {2}, [1, 0, 2])
            sage: G.spanning_tree(2)
            ([(1, 1, 0), (2, 1, 1), None], {2}, [2, 1, 0])
        """
        from collections import deque

        nv = len(self.genera)
        ne = len(self.edges)

        out_edges = [[] for _ in range(nv)]
        for i,(lu,lv) in enumerate(self.edges):
            u = self.vertex(lu)
            v = self.vertex(lv)
            out_edges[u].append((v, -1, i))
            out_edges[v].append((u, 1, i))

        ancestors = [None] * nv
        ancestors[root] = None
        unseen = [True] * nv
        unseen[root] = False
        todo = deque()
        todo.append(root)
        extra_edges = set(range(ne))
        vertices = [root]

        while todo:
            u = todo.popleft()
            for v,s,i in out_edges[u]:
                if unseen[v]:
                    ancestors[v] = (u,s,i)
                    todo.append(v)
                    unseen[v] = False
                    extra_edges.remove(i)
                    vertices.append(v)

        return ancestors, extra_edges, vertices

    def cycle_basis(self):
        r"""
        Return a basis of the cycles as vectors of length the number of edges in the graph.

        The coefficient at a given index in a vector corresponds to the edge
        of this index in the list of edges of the stable graph. The coefficient is
        +1 or -1 depending on the orientation of the edge in the cycle.

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([0,0,0], [[1,2,3], [4,5,6], [7,8]], [(1,4),(5,2),(3,7),(6,8)])
            sage: G.cycle_basis()
            [(1, 1, 0, 0), (1, 0, -1, 1)]
        """
        ne = len(self.edges)
        V = self._edge_module()

        ancestors, extra_edges, _ = self.spanning_tree()
        basis = []

        for i in extra_edges:
            vec = [0] * ne

            # contribution of the edge
            vec[i] = 1

            lu,lv = self.edges[i]
            u = self.vertex(lu)
            v = self.vertex(lv)

            # contribution of the path from root to u
            while ancestors[u] is not None:
                u, s, i = ancestors[u]
                vec[i] -= s

            # contribution of the path from v to root
            while ancestors[v] is not None:
                v, s, i = ancestors[v]
                vec[i] += s

            basis.append(V(vec))

        return basis

    def cycle_space(self):
        r"""
        Return the subspace of the edge module generated by the cycles.

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([0,0,0], [[1,2,3], [4,5,6], [7,8]], [(1,4),(5,2),(3,7),(6,8)])
            sage: C = G.cycle_space()
            sage: C
            Free module of degree 4 and rank 2 over Integer Ring
            Echelon basis matrix:
            [ 1  0 -1  1]
            [ 0  1  1 -1]
            sage: G.flow_divergence(C.random_element()).is_zero()
            True
        """
        return self._edge_module().submodule(self.cycle_basis())

    def flow_divergence(self, flow):
        r"""
        Return the divergence of the given ``flow``.

        The divergence at a given vertex is the sum of the flow on the outgoing
        edges at this vertex.

        EXAMPLES::

            sage: from admcycles import StableGraph
            sage: G = StableGraph([1,0,0], [[1,2],[3,4,5,6],[7,8]], [(1,3),(4,2),(5,8),(7,6)])
            sage: G.flow_divergence([1,1,1,1])
            (0, 0, 0)
            sage: G.flow_divergence([1,0,0,0])
            (1, -1, 0)
        """
        nv = len(self.genera)
        ne = len(self.edges)
        flow = self._edge_module()(flow)
        deriv = self._vertex_module()()
        for i, (lu, lv) in enumerate(self.edges):
            u = self.vertex(lu)
            v = self.vertex(lv)
            deriv[u] += flow[i]
            deriv[v] -= flow[i]

        return deriv

    def flow_solve(self, vertex_weights):
        r"""
        Return a solution for the flow equation with given vertex weights.

        EXAMPLES::

            sage: from admcycles import StableGraph

            sage: G = StableGraph([0,0,0], [[1,2,3], [4,5,6], [7,8]], [(1,4),(5,2),(3,7),(6,8)])
            sage: flow = G.flow_solve((-3, 2, 1))
            sage: flow
            (-2, 0, -1, 0)
            sage: G.flow_divergence(flow)
            (-3, 2, 1)
            sage: div = vector((-34, 27, 7))
            sage: flow = G.flow_solve(div)
            sage: G.flow_divergence(flow) == div
            True
            sage: C = G.cycle_space()
            sage: G.flow_divergence(flow + C.random_element()) == div
            True

            sage: G = StableGraph([0,0,0], [[1],[2,3],[4]], [(1,2),(3,4)])
            sage: G.flow_solve((-1, 0, 1))
            (-1, -1)
            sage: G.flow_divergence((-1, -1))
            (-1, 0, 1)
            sage: G.flow_solve((-1, 3, -2))
            (-1, 2)
            sage: G.flow_divergence((-1, 2))
            (-1, 3, -2)

        TESTS::

            sage: V = ZZ**4
            sage: vectors = [V((-1, 0, 0, 1)), V((-3, 1, -2, 4)), V((5, 2, -13, 6))]
            sage: G1 = StableGraph([0,0,0,0], [[1], [2,3], [4,5], [6]], [(1,2), (3,4), (5,6)])
            sage: G2 = StableGraph([0,0,0,0], [[1], [2,3], [4,5], [6]], [(1,2), (3,4), (6,5)])
            sage: G3 = StableGraph([0,0,0,0], [[1], [2,3], [4,5], [6]], [(2,1), (3,4), (6,5)])
            sage: G4 = StableGraph([0,0,0,0], [[1], [2,3], [4,5], [6]], [(1,2), (4,3), (5,6)])
            sage: for G in [G1,G2,G3,G4]:
            ....:     for v in vectors:
            ....:         flow = G.flow_solve(v)
            ....:         assert G.flow_divergence(flow) == v, (v,flow,G)

            sage: V = ZZ**6
            sage: G = StableGraph([0,0,0,0,0,0], [[1,5], [2,3], [4,6,7,10], [8,9,11,13], [14,16], [12,15]], [(1,2),(4,3),(5,6),(7,8),(9,10),(12,11),(13,14),(15,16)])
            sage: for _ in range(10):
            ....:     v0 = V.random_element()
            ....:     for u in V.basis():
            ....:         v = v0 - sum(v0) * u
            ....:         flow = G.flow_solve(v)
            ....:         assert G.flow_divergence(flow) == v, (v, flow)
        """
        # NOTE: if we compute the divergence matrix, one can also use solve_right
        # directly. It might be faster on some large instances.
        from collections import deque

        ne = len(self.edges)
        nv = len(self.genera)
        if len(vertex_weights) != nv or sum(vertex_weights) != 0:
            raise ValueError("vertex_weights must have length nv and sum up to zero")

        ancestors, _, vertices = self.spanning_tree()
        vertices.reverse()   # move leaves first and root last
        vertices.pop()       # remove the root

        new_vertex_weights = self._vertex_module()(vertex_weights)
        if new_vertex_weights is vertex_weights and vertex_weights.is_mutable():
            new_vertex_weights = vertex_weights.__copy__()
        vertex_weights = new_vertex_weights

        V = self._edge_module()
        vec = V()
        for u in vertices:
            v, s, i = ancestors[u]
            vec[i] += s * vertex_weights[u]
            vertex_weights[v] += vertex_weights[u]

        return vec

    def show(self):
        """
        Display the graph.
        """
        show(self.plot(), axes=False)

    def plot(self, vord=None, vpos=None, eheight=None):
        r"""
        Return a graphics object in which ``self`` is plotted.

        If ``vord`` is ``None``, the method uses the default vertex order.

        If ``vord`` is ``[]``, the parameter ``vord`` is used to give back the vertex order.

        EXAMPLES::

            sage: from admcycles import *
            sage: G = StableGraph([1,2],[[1,2],[3,4,5,6]],[(1,3),(2,4)])
            sage: G.plot()
            Graphics object consisting of 12 graphics primitives 

        TESTS::

            sage: from admcycles import *
            sage: G = StableGraph([1,2],[[1,2],[3,4,5,6]],[(1,3),(2,4)])
            sage: vertex_order = []
            sage: P =  G.plot(vord=vertex_order)
            sage: vertex_order
            [0, 1]
        """
        # some parameters
        mark_dx = 1       # x-distance of different markings
        mark_dy = 1       # y-distance of markings from vertices
        mark_rad = 0.2    # radius of marking-circles
        v_dxmin = 1       # minimal x-distance of two vertices
        ed_dy = 0.7       # max y-distance of different edges between same vertex-pair

        vsize = 0.4       # (half the) size of boxes representing vertices

        if not vord:
            default_vord = list(range(len(self.genera)))
            if vord is None:
                vord = default_vord
            else:
                vord += default_vord
        reord_self = deepcopy(self)
        reord_self.reorder_vertices(vord)

        if not vpos:
            default_vpos = [(0, 0)]
            for i in range(1, len(self.genera)):
                default_vpos+=[(default_vpos[i-1][0]+mark_dx*(len(reord_self.list_markings(i-1))+2 *len(reord_self.edges_between(i-1 ,i-1 ))+len(reord_self.list_markings(i))+2 *len(reord_self.edges_between(i,i)))/ZZ(2)+v_dxmin,0)]
            if vpos is None:
                vpos = default_vpos
            else:
                vpos += default_vpos

        if not eheight:
            ned={(i,j): 0  for i in range(len(reord_self.genera)) for j in range(i+1 ,len(reord_self.genera))}
            default_eheight = {}
            for e in reord_self.edges:
                ver1=reord_self.vertex(e[0])
                ver2=reord_self.vertex(e[1])
                if ver1!=ver2:
                    default_eheight[e]=abs(ver1-ver2)-1+ned[(min(ver1,ver2), max(ver1,ver2))]*ed_dy
                    ned[(min(ver1,ver2), max(ver1,ver2))]+=1

            if eheight is None:
                eheight = default_eheight
            else:
                eheight.update(default_eheight)

        # now the drawing starts
        # vertices
        vertex_graph = [polygon2d([[vpos[i][0]-vsize,vpos[i][1]-vsize],[vpos[i][0]+vsize,vpos[i][1]-vsize],[vpos[i][0]+vsize,vpos[i][1]+vsize],[vpos[i][0]-vsize,vpos[i][1]+vsize]], color='white',fill=True, edgecolor='black', thickness=1,zorder=2) + text('g='+repr(reord_self.genera[i]), vpos[i], fontsize=20 , color='black',zorder=3) for i in range(len(reord_self.genera))]

        # non-self edges
        edge_graph=[]
        for e in reord_self.edges:
            ver1=reord_self.vertex(e[0])
            ver2=reord_self.vertex(e[1])
            if ver1!=ver2:
                x=(vpos[ver1][0]+vpos[ver2][0])/ZZ(2)
                y=(vpos[ver1][1]+vpos[ver2][1])/ZZ(2)+eheight[e]
                edge_graph+=[bezier_path([[vpos[ver1], (x,y) ,vpos[ver2] ]],color='black',zorder=1)]

        marking_graph=[]

        for v in range(len(reord_self.genera)):
            se_list=reord_self.edges_between(v,v)
            m_list=reord_self.list_markings(v)
            v_x0=vpos[v][0]-(2*len(se_list)+len(m_list)-1)*mark_dx/ZZ(2)

            for e in se_list:
                edge_graph+=[bezier_path([[vpos[v], (v_x0,-mark_dy), (v_x0+mark_dx,-mark_dy) ,vpos[v] ]],zorder=1)]
                v_x0+=2*mark_dx
            for l in m_list:
                marking_graph+=[line([vpos[v],(v_x0,-mark_dy)],color='black',zorder=1)+circle((v_x0,-mark_dy),mark_rad, fill=True, facecolor='white', edgecolor='black',zorder=2)+text(repr(l),(v_x0,-mark_dy), fontsize=10, color='black',zorder=3)]
                v_x0+=mark_dx
        return sum(marking_graph) + sum(edge_graph) + sum(vertex_graph)


# Thes function is about to be deprecated. Instead use
#   - StableGraph.is_isomorphic
#   - StableGraph.automorphism_number

from sage.combinat.permutation import Permutations
import itertools

#computes union of dictionaries
def dicunion(*dicts):
    return dict(itertools.chain.from_iterable(dct.items() for dct in dicts))

def GraphIsom(G,H,check=False):
    #TODO: Insert quick hash-check if G,H can be isomorphic at all
    if (G.invariant() != H.invariant()):
        return []

    Isomlist=[]    # list of isomorphisms that will be returned
    IsoV={} # working vertex-dictionary
    IsoL={j:j for j in G.list_markings()} # working leg-dictionary

    for j in G.list_markings():
        vG=G.vertex(j)
        vH=H.vertex(j)

        # if vertices containing j have different genera or degrees in G, there is no automorphism
        # also if the markings give contradictory information where the vertices go, there is no automorphism
        if (G.genera[vG] != H.genera[vH]) or (len(G.legs[vG]) != len(H.legs[vH])) or (vG in IsoV and IsoV[vG] != vH):
            return []
        # otherwise add known association of vertices to IsoV
        IsoV[vG]=vH
    # Now vG and vH contain all information prescribed by markings, proceed to assign markingless vertices
    # Create dictionaries gdG, gdH associating to tuples (genus, degree) the indices of markingless vertices in G,H with those data
    gdG={}
    gdH={}


    for v in range(len(G.genera)):
        if v not in IsoV:
            gd=(G.genera[v],len(G.legs[v]))
            if gd in gdG:
                gdG[gd]+=[v]
            else:
                gdG[gd]=[v]
    for v in range(len(H.genera)):
        if not v in IsoV.values():
            gd=(H.genera[v],len(H.legs[v]))
            if gd in gdH:
                gdH[gd]+=[v]
            else:
                gdH[gd]=[v]


    if set(gdG) != set(gdH):
        return []

    VertIm=[]    # list (for all keys (g,d) of gdG) of lists of all possible dictionary-bijections from gdG(gd) to gdH(gd)


    for gd in gdG:
        if len(gdG[gd]) != len(gdH[gd]):
            return []
        P=Permutations(len(gdG[gd]))
        ind=list(range(len(gdG[gd])))
        VertIm+=[ [ {gdG[gd][i]:gdH[gd][p[i]-1 ] for i in ind} for p in P] ]

    # Now VertIm is a list of the form [[{0:0, 1:1},{0:1, 1:0}], [{2:2}]]
    # Iterate over all possible combinations
    for VI in itertools.product(*VertIm):
        continueloop=False
        IsoV2=dicunion(IsoV,*VI)    #IsoV2 is now complete dictionary of vertices

        LegIm=[] # list (for all (ordered) pairs of vertices of G) of lists of dictionaries associating legs of edges connecting the pair to legs in H connecting the image pair

        #TODO: possibly want quick check that now graphs are actually isomorphic

        # first look at loops of G
        for v in range(len(G.genera)):
            EdG=G.edges_between(v,v)

            EdH=H.edges_between(IsoV2[v],IsoV2[v])
            if len(EdG) != len(EdH):
                continueloop=True
                break

            LegImvv=[]

            # P gives the ways to biject from EdG to EdH, but additionally for each edge we have to decide to which of the two legs of the target edge it goes
            P=Permutations(len(EdG))
            ran=list(range(len(EdG)))
            choic=len(EdG)*[[0 ,1 ]]
            for p in P:
                for o in itertools.product(*choic):
                    #Example: EdG=[(1,2),(3,4)], EdH=[(6,7),(9,11)], p=[2,1], o=[0,1] -> {1:9, 2:11, 3:7, 4:6}
                    di=dicunion({EdG[i][0 ] : EdH[p[i]-1 ][o[i]] for i in ran},{EdG[i][1 ] : EdH[p[i]-1 ][1 -o[i]] for i in ran})
                    LegImvv+=[di]
            LegIm+=[LegImvv]
        if continueloop:
            continue

        # now look at edges from v to w
        for v in range(len(G.genera)):
            if continueloop:
                break
            for w in range(v+1 ,len(G.genera)):
                EdG=G.edges_between(v,w)
                EdH=H.edges_between(IsoV2[v],IsoV2[w])
                if len(EdG) != len(EdH):
                    continueloop=True
                    break


                LegImvw=[]

                # P gives the ways to biject from EdG to EdH
                P=Permutations(len(EdG))
                ran=list(range(len(EdG)))
                for p in P:
                    #Example: EdG=[(1,2),(3,4)], EdH=[(6,7),(9,11)], p=[2,1] -> {1:9, 2:11, 3:6, 4:7}
                    di=dicunion({EdG[i][0 ] : EdH[p[i]-1 ][0 ] for i in ran},{EdG[i][1 ] : EdH[p[i]-1 ][1 ] for i in ran})
                    LegImvw+=[di]
                LegIm+=[LegImvw]

        if continueloop:
            continue

        # if program runs to here, then IsoV2 is a bijection of vertices respecting the markings,
        # LegIm is a list of lists of dictionaries giving bijections of non-marking legs that respect
        # the map of vertices and edges; it remains to add the various elements to IsoL and return them
        Isomlist += [[IsoV2, dicunion(IsoL,*LegDics)] for LegDics in itertools.product(*LegIm)]

        if check and Isomlist:
            return Isomlist

    return Isomlist
