from __future__ import absolute_import, division, print_function

# Imports
import math
import logging

from six import iteritems, string_types

from ..utilities.xmls import Element
from ..utilities.general import get_uid, make_float_or_keep_none

# Settings for the logger
logger = logging.getLogger(__name__)


class EquationMixin(object):

    EQUATION_LANGUAGES = ['Python']

    def _check_equation_node(self, node):
        """Method to check the validity of a node with an equation.

        This function extracts the equation labels from a equation. It then checks that the equation labels are present
        in the connected input nodes.

        :param node: graph node under consideration
        :type node: str

        :return: check result
        :rtype: bool
        """

        # TODO: Implement this method

        return False

    def _get_equation_nodes(self):
        """Retrieves a list of nodes representing a proper equation (where every output edge has an equations attribute)

        :type self: KadmosGraph

        :return: list of proper equation nodes
        :rtype: list
        """

        nodes_temp = []
        nodes = []

        # Get all nodes where at least one output edge has an equations attribute
        for out_edge in self.out_edges(data=True):
            if 'equations' in out_edge[2]:
                nodes_temp.append(out_edge[0])
        nodes_temp = list(set(nodes_temp))

        # Get all nodes where for every node every output edge has an equations attribute
        for node in nodes_temp:
            if all([len(out_edge[2].get('equations', [])) > 0 for out_edge in self.out_edges(node, data=True)]):
                nodes.append(node)

        return nodes

    def _get_equation_chars(self, language='Python'):
        """Method to obtain a list of equation operators in a specified equation language.

        :type self: KadmosGraph
        :param language: equation language under consideration
        :type language: str

        :return: list of equation operators
        :rtype: list
        """

        chars = list([' ', '+', '-', '*', '/', '^'])

        if language == 'Python':
            chars.extend(['**', '(', ')', '//', '%'])
            chars.extend(dir(math)[3:])
            chars.remove('e')

        return chars

    def add_equation_label(self, edge, labeling_method='node_label', language='Python'):
        """Method to add an equation label to a edge that can (safely) be used as reference in an equation.

        :type self: KadmosGraph
        :param edge: graph edge under consideration
        :type edge: str
        :param labeling_method: select method for automatic label string determination (node_id or node_label)
        :type labeling_method: str
        :param language: equation language used for the equation label
        :type language: str

        :return: label
        :rtype: str
        """

        # Assertions
        assert self.has_edge(edge[0], edge[1]), 'Edge %s does not exist.' % edge

        # If the label is not provided retrieve it automatically from the variable node
        node_id = edge[0] if self.node[edge[0]].get('category') == 'variable' else edge[1]
        if labeling_method == 'node_label':
            label = self.node[node_id].get('label', node_id)
        elif labeling_method == 'node_id':
            label = node_id.split('/')[-1]
            if '__i' in label:
                label = label.split('__i')[0]
        else:
            raise IOError('Invalid setting label_method.')

        # Make the label valid
        for char in self._get_equation_chars(language=language):
            label = label.replace(char, '')

        # If the language is not officially supported log this
        if language not in self.EQUATION_LANGUAGES:
            logger.info('The equation language ' + language + ' is not supported. It is assumed that the equation ' +
                        ' label ' + label + ' is valid.')

        # Attach the label to the edge
        self.adj[edge[0]][edge[1]]['equation_label'] = label

        return label

    def add_equation_labels(self, nodes, language='Python', labeling_method='node_id'):
        """Method to add equation labels automatically to all input edges connected to the specified list of nodes

        :type self: KadmosGraph
        :param nodes: list of nodes
        :type nodes: list
        :param language: equation language used for the equation label
        :type language: str
        :param labeling_method: select method for automatic label string determination (node_id or node_label)
        :type labeling_method: str

        :return: labels
        :rtype: str
        """

        # Loop
        for edge in self.in_edges(nodes):
            self.add_equation_label(edge, labeling_method=labeling_method, language=language)

        return

    def add_equation(self, edge_or_node, equation, language='Python'):
        """Method to add an equation to an output edge.

        :type self: KadmosGraph
        :param edge_or_node: graph edge or node under consideration.
        :type edge_or_node: list, str
        :param equation: equation to be added
        :type equation: str
        :param language: equation language used for the equation
        :type language: str

        :return: equation
        :rtype: str
        """

        # Check if a edge or node is given
        if not isinstance(edge_or_node, string_types):
            edge = edge_or_node
            assert self.has_edge(edge[0], edge[1]), 'Edge %s does not exist.' % edge
        else:
            node = edge_or_node
            edges = list(self.out_edges(node))
            assert len(edges) == 1, 'Node %s has several or no output edges. Please select one.' % node
            edge = edges[0]

        # If the language is not officially supported log this
        if language not in self.EQUATION_LANGUAGES:
            logger.info('The equation language ' + language + ' is not supported. It is assumed that the equation ' +
                        equation + ' is valid.')

        # Add equations attribute to the edge (if it doesn't exist already)
        if 'equations' not in self.adj[edge[0]][edge[1]]:
            self.adj[edge[0]][edge[1]]['equations'] = {}

        # Add equation to the equations attribute
        self.adj[edge[0]][edge[1]]['equations'][language] = equation

        return

    def add_mathematical_function(self, input_nodes, function_node, output_nodes, function_type='regular'):
        """Method to add mathematical function to graph

        :param input_nodes: input nodes of the mathematical function
        :type input_nodes: str, list
        :param function_node: function node of the mathematical function
        :type function_node: str
        :param output_nodes: output nodes of the mathematical function
        :type output_nodes: str, list
        :param function_type: type of function, optional (default='regular')
        :type function_type: 'regular', 'consistency' or 'balance'

        :return: mathematical function
        :rtype: str
        """

        assert not self.has_node(function_node), 'Function node {} already exists in the graph.'.format(function_node)

        self.add_fnode(function_node, label=function_node, function_type=function_type)
        for input_node in input_nodes:
            if not self.has_node(input_node[0]):
                self.add_vnode(input_node[0])
            if not self.has_edge(input_node[0], function_node):
                self.add_edge(input_node[0], function_node, equation_label=input_node[1])
            else:
                self.adj[input_node[0]][function_node]['equation_label'] = input_nodes[1]
        for output_node in output_nodes:
            if not self.has_node(output_node[0]):
                self.add_vnode(output_node[0])
            if not self.has_edge(function_node, output_node[0]):
                self.add_edge(function_node, output_node[0])
            self.add_equation((function_node, output_node[0]), output_node[1], output_node[2])

        return

    def _create_cmdows_equations(self, graph_math_funcs):
        """Method to create the CMDOWS mathematicalFunctions element

        :type self: KadmosGraph

        :return: CMDOWS mathematicalFunctions element
        :rtype: Element
        """

        # Create mathematicalFunctions
        cmdows_math_funcs = Element('mathematicalFunctions')
        cmdows_added_equations = dict()

        for graph_math_func in graph_math_funcs:
            # Create mathematicalFunctions/mathematicalFunction
            cmdows_math_func = cmdows_math_funcs.add('mathematicalFunction', uID=graph_math_func)
            cmdows_math_func.add('label', self.node[graph_math_func].get('label', graph_math_func))
            cmdows_math_func.add('functionType', self.node[graph_math_func].get('function_type'))
            cmdows_math_func.add('sleepTime', make_float_or_keep_none(self.node[graph_math_func].get('sleep_time')))

            # Create mathematicalFunctions/mathematicalFunction/inputs with children
            cmdows_inputs = cmdows_math_func.add('inputs')
            for graph_input in self.in_edges(graph_math_func, data=True):
                cmdows_input = cmdows_inputs.add('input')
                cmdows_input.add('parameterUID', graph_input[0])
                cmdows_input.add('equationLabel', graph_input[2]['equation_label'])
                cmdows_input.add('valid_ranges', graph_input[2].get('valid_ranges'), camel_case_conversion=True)

            # Create mathematicalFunctions/mathematicalFunction/outputs with children
            cmdows_outputs = cmdows_math_func.add('outputs')
            for graph_output in self.out_edges(graph_math_func, data=True):
                cmdows_output = cmdows_outputs.add('output')
                cmdows_output.add('parameterUID', graph_output[1])
                graph_equations = graph_output[2].get('equations')
                if graph_equations:
                    if graph_equations not in cmdows_added_equations.values():
                        uid = get_uid(graph_math_func + '_equation', list(cmdows_added_equations))
                        cmdows_added_equations[uid] = graph_equations
                        cmdows_equations = cmdows_output.add('equations', uID=uid)
                        for graph_equation_language, graph_equation in iteritems(graph_equations):
                            cmdows_equations.add('equation', graph_equation, language=graph_equation_language)
                    else:
                        for uid, equations in iteritems(cmdows_added_equations):
                            if equations == graph_equations:
                                break
                        # noinspection PyUnboundLocalVariable
                        cmdows_output.add('equationsUID', uid)

        return cmdows_math_funcs

    def _load_cmdows_equations(self, cmdows):
        """Method to load a CMDOWS mathematicalFunctions element

        :type self: KadmosGraph

        :param: cmdows: CMDOWS mathematicalFunctions element
        :param: cmdows: Element
        """

        for function in cmdows.findall('executableBlocks/mathematicalFunctions/mathematicalFunction'):
            self.add_node(function.get('uID'),
                          category='function',
                          shape='s',
                          label=function.findtext('label'),
                          function_type=function.findtext('functionType'),
                          sleep_time=make_float_or_keep_none(function.findtext('sleepTime')))
            for inp in function.findall('inputs/input'):
                self.add_edge(inp.findtext('parameterUID').replace("'", '"'), function.get('uID'),
                              equation_label=inp.findtext('equationLabel'),
                              valid_ranges=inp.finddict('validRanges', ordered=False, camel_case_conversion=True))
            for outp in function.findall('outputs/output'):
                if outp.find('equationsUID') is not None:
                    equations = cmdows.xpath('.//*[@uID="' + outp.find('equationsUID').text + '"]')[0]
                else:
                    equations = outp.findall('equations/equation')
                self.add_edge(function.get('uID'), outp.findtext('parameterUID').replace("'", '"'),
                              equations={eq.get('language'): eq.text for eq in equations})
