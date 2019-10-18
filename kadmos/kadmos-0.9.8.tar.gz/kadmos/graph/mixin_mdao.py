from __future__ import absolute_import, division, print_function

# Imports
import logging


# Settings for the logger
from six import string_types

logger = logging.getLogger(__name__)


class MdaoMixin(object):

    def remove_node_from_diagonal(self, node):
        """Function to remove a node from the diagonal with functions.

        :type self: KadmosGraph
        :param node: node identifier
        :type node: str
        :return: graph with removed node from diagonal
        :rtype: MdaoMixin
        """

        # Input assertions
        assert isinstance(node, string_types)
        assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Get current diagonal position of the node
        diag_pos = self.node[node]['diagonal_position']

        # Remove node
        self.remove_node(node)

        # Change diagonal positions according to removed node
        for n, d in self.nodes(data=True):
            if 'diagonal_position' in d and n != node:
                if d['diagonal_position'] > diag_pos:
                    d['diagonal_position'] -= 1

    def insert_node_on_diagonal(self, node, diagonal_pos, attr_dict=None):
        """Function to insert a node on the diagonal with functions.

        :type self: KadmosGraph
        :param node: node identifier
        :type node: str
        :param diagonal_pos: integer with diagonal position (>= 0)
        :type diagonal_pos: int
        :param attr_dict: dictionary with node attributes
        :type attr_dict: dict
        :return: graph with inserted node on diagonal
        :rtype: MdaoMixin
        """

        # Input assertions
        assert isinstance(node, string_types)
        assert isinstance(diagonal_pos, int)
        assert diagonal_pos > 0
        if attr_dict is not None:
            assert isinstance(attr_dict, dict)

        # Add or overwrite diagonal position in dictionary
        if attr_dict is None:
            attr_dict = dict()
        attr_dict['diagonal_position'] = diagonal_pos

        # Add node and given attributes
        assert not self.has_node(node), 'Node %s is already present in the graph.' % node
        self.add_node(node, attr_dict)

        # Change diagonal positions according to inserted node
        for n, d in self.nodes(data=True):
            if 'diagonal_position' in d and n != node:
                if d['diagonal_position'] >= diagonal_pos:
                    d['diagonal_position'] += 1
