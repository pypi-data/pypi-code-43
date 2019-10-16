from jelm import Jelm

from .network_case_set_class import case_set, NetwokCaseTemplate


@case_set.register
class EmptyNetworks(NetwokCaseTemplate):

    def __init__(self):

        self.el1 = Jelm()
        self.el2 = Jelm()

        self.same = True


@case_set.register
class OneNodeSame(NetwokCaseTemplate):

    def __init__(self):

        self.el1 = Jelm(objects=[{'type': 'node',
                                  'id': 'n1'}])
        self.el2 = Jelm(objects=[{'type': 'node',
                                  'id': 'n1'}])

        self.same = True


@case_set.register
class OneNodeDiffAtt(NetwokCaseTemplate):

    def __init__(self):

        self.el1 = Jelm(objects=[{'type': 'node',
                                  'id': 'n1',
                                  'attributes': {'fing': True}}])
        self.el2 = Jelm(objects=[{'type': 'node',
                                  'id': 'n1'},
                                 ])

        self.same = True


@case_set.register
class OneNodeVsEmpty(NetwokCaseTemplate):

    def __init__(self):

        self.el1 = Jelm(objects=[{'type': 'node',
                                  'id': 'n1'}])
        self.el2 = Jelm()

        self.same = False


@case_set.register
class OneNodeVsTwo(NetwokCaseTemplate):

    def __init__(self):

        self.el1 = Jelm(objects=[{'type': 'node',
                                  'id': 'n1'}])

        self.el2 = Jelm(objects=[{'type': 'node',
                                  'id': 'n1'},
                                 {'type': 'node',
                                  'id': 'n2'}
                                 ])
        self.same = False


@case_set.register
class TwentyNodeSame(NetwokCaseTemplate):

    def __init__(self):
        self.el1 = Jelm(objects=[{'type': 'node',
                                  'id': 'n{}'.format(i)}
                                 for i in range(20)])

        self.el2 = Jelm(objects=[{'type': 'node',
                                  'id': 'n{}'.format(i)}
                                 for i in range(20)])
        self.same = True


@case_set.register
class TwentyNodeEdgesSame(NetwokCaseTemplate):

    def __init__(self):

        node_list1 = [{'type': 'node',
                       'id': 'n{}'.format(i)}
                      for i in range(20)]

        edge_list1 = [{'type': 'edge',
                       'source': 'n{}'.format(ns[0]),
                       'target': 'n{}'.format(ns[1])}
                      for ns in [
                          (0, 1),
                          (1, 2),
                          (4, 1),
                          (10, 8),
                          (9, 3),
                          (18, 6)
                      ]]

        self.el1 = Jelm(objects=[*node_list1,
                                 *edge_list1])

        node_list2 = [{'type': 'node',
                       'id': 'n{}'.format(i)}
                      for i in range(20)]

        edge_list2 = [{'type': 'edge',
                       'source': 'n{}'.format(ns[0]),
                       'target': 'n{}'.format(ns[1])}
                      for ns in [
                          (0, 1),
                          (1, 2),
                          (4, 1),
                          (10, 8),
                          (9, 3),
                          (18, 6)
                      ]]

        self.el2 = Jelm(objects=[*node_list2,
                                 *edge_list2])
        self.same = True


@case_set.register
class TwentyNodeEdgesSameDiffEdgeOrder(NetwokCaseTemplate):

    def __init__(self):
        node_list1 = [{'type': 'node',
                       'id': 'n{}'.format(i)}
                      for i in range(20)]

        edge_list1 = [{'type': 'edge',
                       'source': 'n{}'.format(ns[0]),
                       'target': 'n{}'.format(ns[1])}
                      for ns in [
                          (0, 1),
                          (1, 2),
                          (4, 1),
                          (10, 8),
                          (9, 3),
                          (18, 6)
                      ]]

        self.el1 = Jelm(objects=[*node_list1,
                                 *edge_list1])

        node_list2 = [{'type': 'node',
                       'id': 'n{}'.format(i)}
                      for i in range(20)]

        edge_list2 = [{'type': 'edge',
                       'source': 'n{}'.format(ns[0]),
                       'target': 'n{}'.format(ns[1])}
                      for ns in [
                          (10, 8),
                          (1, 2),
                          (0, 1),
                          (9, 3),
                          (18, 6),
                          (4, 1)
                      ]]

        self.el2 = Jelm(objects=[*node_list2,
                                 *edge_list2])
        self.same = True


@case_set.register
class TwentyNodeEdgesSameDiffEdgeAtts(NetwokCaseTemplate):

    def __init__(self):
        node_list1 = [{'type': 'node',
                       'id': 'n{}'.format(i)}
                      for i in range(20)]

        edge_list1 = [{'type': 'edge',
                       'source': 'n{}'.format(ns[0]),
                       'target': 'n{}'.format(ns[1])}
                      for ns in [
                          (0, 1),
                          (1, 2),
                          (4, 1),
                          (10, 8),
                          (9, 3),
                          (18, 6)
                      ]]

        self.el1 = Jelm(objects=[*node_list1,
                                 *edge_list1])

        node_list2 = [{'type': 'node',
                       'id': 'n{}'.format(i)}
                      for i in range(20)]

        edge_list2 = [{'type': 'edge',
                       'source': 'n{}'.format(ns[0]),
                       'target': 'n{}'.format(ns[1]),
                       'attributes': {'second': True}}
                      for ns in [
                          (10, 8),
                          (1, 2),
                          (0, 1),
                          (9, 3),
                          (18, 6),
                          (4, 1)
                      ]]

        self.el2 = Jelm(objects=[*node_list2,
                                 *edge_list2])
        self.same = False


@case_set.register
class BigNetRef(NetwokCaseTemplate):

    def __init__(self):
        node_list1 = [{'type': 'node',
                       'id': 'n{}'.format(i)}
                      for i in range(20)]

        edge_list1 = [{'type': 'edge',
                       'source': 'n{}'.format(ns[0]),
                       'target': 'n{}'.format(ns[1])}
                      for ns in [
                          (0, 1),
                          (1, 2),
                          (4, 1),
                          (10, 8),
                          (9, 3),
                          (18, 6)
                      ]]

        self.el1 = Jelm(objects=[*node_list1,
                                 *edge_list1])

        self.el2 = self.el1

        self.same = True
