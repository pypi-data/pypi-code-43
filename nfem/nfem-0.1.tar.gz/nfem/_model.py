from ._canvas import Canvas3D
from ._node import Node
from ._truss import Truss


class Model:
    def __init__(self):
        self._parent = None
        self._nodes = dict()
        self._elements = dict()

    def add_node(self, key, x, y, z, support=''):
        """Add a new node to the model.

        Parameters
        ----------
        key : str
            The unique identifier of the node.
        x : float
            The location of the node in x direction.
        y : float
            The location of the node in y direction.
        z : float
            The location of the node in z direction.
        support : str
            The directions in which a support permits displacements.

        Returns
        -------
        Node
            The new node.

        """
        node = Node(key, x, y, z)
        if 'x' in support:
            node.x.is_active = False
        if 'y' in support:
            node.y.is_active = False
        if 'z' in support:
            node.z.is_active = False
        self._nodes[key] = node
        return node

    def node(self, key):
        """Get a node by a given key.

        Parameters
        ----------
        key : str
            The unique identifier of the node.

        Returns
        -------
        Node
            The node with the given key.

        """
        if isinstance(key, Node):
            key = key.key
        node = self._nodes.get(key, None)
        if node is None:
            raise RuntimeError()
        return node

    def add_truss(self, key, node_a, node_b):
        """Add a new truss element to the model.

        Parameters
        ----------
        key : str
            The unique identifier of the element.
        node_a : Node or str
            The start node or the key of the node.
        node_b : Node or str
            The end node or the key of the node.

        Returns
        -------
        Truss
            The new truss element.

        """
        node_a = self.node(node_a)
        node_b = self.node(node_b)
        truss = Truss(key, node_a, node_b)
        self._elements[key] = truss
        return truss

    def show(self):
        """Shows a visualization of the model.
        """
        canvas = Canvas3D()
        for element in self._elements.values():
            element.draw(canvas)
        canvas.show()
