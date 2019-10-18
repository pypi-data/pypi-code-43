from __future__ import absolute_import, division, print_function

# Imports
import logging

import copy
import networkx as nx
import numpy as np

from ..utilities.general import format_string_for_vistoms
from ..utilities.testing import check
from ..utilities.xmls import Element

from kadmos.graph.graph_kadmos import KadmosGraph
from kadmos.graph.mixin_mdao import MdaoMixin


# Settings for the logger
logger = logging.getLogger(__name__)


class ProcessGraph(KadmosGraph, MdaoMixin):

    def __init__(self, *args, **kwargs):
        super(ProcessGraph, self).__init__(*args, **kwargs)

    # -------------------------------------------------------------------------------------------- #
    #                                     PRINTING METHODS                                         #
    # -------------------------------------------------------------------------------------------- #
    def inspect_process(self):
        """Method to print the MPG.

        :return: printed inspection
        """

        print('\n- - - - - - - - - - -')
        print(' PROCESS INSPECTION  ')
        print('- - - - - - - - - - -\n')
        print('\nNODES\n')
        for idx in range(0, self.number_of_nodes()):
            nodes = self.find_all_nodes(attr_cond=['diagonal_position', '==', idx])
            for node in nodes:
                print('- - - - -')
                print(node)
                print('process step: ' + str(self.nodes[node]['process_step']))
                print('diagonal pos: ' + str(self.nodes[node]['diagonal_position']))
                if 'converger_step' in self.nodes[node]:
                    print('converger step: ' + str(self.nodes[node]['converger_step']))
        print('\nEDGES\n')
        for idx in range(0, self.number_of_edges() + 1):
            for u, v, d in self.edges(data=True):
                if d['process_step'] == idx:
                    print('- - - - -')
                    print(u + ' ---> ' + v)
                    print(d['process_step'])
        print('- - - - - - - - - - -\n')


    def get_ordered_cycles(self):
        """Method to get the cycles of a process graph ordered according to process step number.

        :return: list with the cycles of a graph ordered based on PSN
        :rtype: list
        """
        cycles = list(nx.simple_cycles(self))
        min_process_steps = []
        neat_cycles = []
        for cycle in cycles:
            min_process_steps.append(self.get_lowest_psn(cycle)[0])
            neat_cycles.append(self.get_ordered_cycle(cycle))
        ordered_cycles = [x for _, x in sorted(zip(min_process_steps, neat_cycles))]
        return ordered_cycles

    def get_lowest_psn(self, cycle):
        """Method to retrieve the lowest process step number (PSN) of a list of nodes in a cycle.

        :param cycle: list with nodes on a cycle
        :type cycle: list
        :return: the minimal PSN and the index of the first element having this PSN
        :rtype: tuple
        """
        process_steps = [self.nodes[node]['process_step'] for node in cycle]
        min_process_step = min(process_steps)
        min_process_step_idx = process_steps.index(min_process_step)
        return min_process_step, min_process_step_idx

    def get_ordered_cycle(self, cycle):

        _, idx = self.get_lowest_psn(cycle)
        return cycle[idx:] + cycle[:idx]

    def get_node_text(self, node):
        """Method to determine the text of a function node (for use in a XDSM diagram).

        :param node: node
        :type node: basestring
        :return: node text for in the XDSM function box
        :rtype: basestring
        """

        # Measure to make sure a label is written
        node_label = self.nodes[node].get('label', str(node))
        assert node_label, 'Node label seems to be empty for node: %s' % node

        if 'converger_step' in self.nodes[node] and node != self.COORDINATOR_STRING:
            node_text = ('$' + str(self.nodes[node]['process_step']) + ',' + str(self.nodes[node]['converger_step']) +
                         r'\to' + str(self.nodes[node]['process_step'] + 1) +
                         r'$:\\[1pt]' + node_label)
        elif 'converger_step' in self.nodes[node] and node == self.COORDINATOR_STRING:
            node_text = ('$' + str(self.nodes[node]['process_step']) + ',' + str(self.nodes[node]['converger_step']) +
                         r'$:\\[1pt]' + node_label)
        elif 'process_step' in self.nodes[node]:
            node_text = ('$' + str(self.nodes[node]['process_step']) + r'$:\\[1pt]' + node_label)
        else:
            node_text = node_label

        return node_text

    def get_process_list(self, use_d3js_node_ids=False):
        """Method to get the xdsm workflow process list (for use in dynamic visualizations).

        :param use_d3js_node_ids: setting whether node names should be changed into node ids according to D3js notation.
        :type use_d3js_node_ids: bool
        :return: process list
        :rtype: list
        """

        # Input assertions
        assert isinstance(use_d3js_node_ids, bool)

        # Find first diagonal node
        first_nodes = self.find_all_nodes(attr_cond=['diagonal_position', '==', 0])
        assert len(first_nodes) == 1, 'Only one node per diagonal position is allowed.'
        first_node = first_nodes[0]
        assert 'converger_step' in self.nodes[first_node], 'First diagonal node should have a converger_step attribute.'
        max_step = self.nodes[first_node]['converger_step']
        process_list = []
        for step in range(0, max_step+1):
            process_list.append({'step_number': step,
                                 'process_step_blocks': [],
                                 'converger_step_blocks': [],
                                 'edges': []})
            process_step_nodes = self.find_all_nodes(attr_cond=['process_step', '==', step])
            converger_step_nodes = self.find_all_nodes(attr_cond=['converger_step', '==', step])
            if not process_step_nodes and not converger_step_nodes:
                raise IOError('Process block data missing for step %d.' % step)
            # In case of regular process steps, determine their list positions
            for step_node in process_step_nodes:
                if use_d3js_node_ids:
                    node_name = format_string_for_vistoms(step_node, prefix='id_')
                else:
                    node_name = step_node
                process_list[step]['process_step_blocks'].append(node_name)
            for step_node in converger_step_nodes:
                if use_d3js_node_ids:
                    node_name = format_string_for_vistoms(step_node, prefix='id_')
                else:
                    node_name = step_node
                process_list[step]['converger_step_blocks'].append(node_name)
            for edge in self.edges(data=True):
                if edge[2]['process_step'] == step:
                    if use_d3js_node_ids:
                        edge0_name = format_string_for_vistoms(edge[0], prefix='id_')
                        edge1_name = format_string_for_vistoms(edge[1], prefix='id_')
                    else:
                        edge0_name = edge[0]
                        edge1_name = edge[1]
                    process_list[step]['edges'].append((edge0_name, edge1_name))

        return process_list

class MdaoProcessGraph(ProcessGraph):

    ARCHITECTURE_CATS = {'all iterative blocks': ['optimizer', 'converger', 'doe'],
                         'all design variables': ['initial guess design variable', 'final design variable'],
                         'all pre-iter analyses': ['pre-coupling analysis', 'uncoupled-des-var-ind analysis']}

    def __init__(self, *args, **kwargs):
        super(MdaoProcessGraph, self).__init__(*args, **kwargs)

    # -------------------------------------------------------------------------------------------- #
    #                                   CREATE METHODS                                             #
    # -------------------------------------------------------------------------------------------- #
    def _create_cmdows_workflow_process_graph(self):
        """
        Method to add the processGraph element to a CMDOWS file.

        :return: CMDOWS processGraph element
        :rtype: Element
        """

        # Create workflow/processGraph
        cmdows_process_graph = Element('processGraph')
        cmdows_process_graph.add('name', self.graph.get('name'))

        # Create workflow/processGraph/edges
        cmdows_edges = cmdows_process_graph.add('edges')
        for u, v, w in self.edges(data=True):
            # Create workflow/dataGraph/edges/edge
            cmdows_edge = cmdows_edges.add('edge')
            cmdows_edge.add('fromExecutableBlockUID', u)
            cmdows_edge.add('toExecutableBlockUID', v)
            cmdows_edge.add('processStepNumber', w.get('process_step'))

        # Create workflow/processGraph/nodes
        cmdows_nodes = cmdows_process_graph.add('nodes')
        for n, data in self.nodes(data=True):
            # Create workflow/dataGraph/nodes/node
            cmdows_node = cmdows_nodes.add('node')
            cmdows_node.add('referenceUID', n)
            cmdows_node.add('processStepNumber', data.get('process_step'))
            cmdows_node.add('convergerStepNumber', data.get('converger_step'))
            cmdows_node.add('diagonalPosition', data.get('diagonal_position'))
            cmdows_node.add('partitionID', data.get('partition_id'))

        # Create workflow/processGraph/metadata
        cmdows_meta = cmdows_process_graph.add('metadata')
        cmdows_loop_nesting = cmdows_meta.add('loopNesting')
        cmdows_loop_nesting.add_process_hierarchy(self.graph['process_hierarchy'], self)
        return cmdows_process_graph

    # -------------------------------------------------------------------------------------------- #
    #                                  LOAD METHODS                                                #
    # -------------------------------------------------------------------------------------------- #
    def _load_cmdows_workflow_process_graph(self, cmdows, nodes):
        """
        Method to load a MPG stored in a CMDOWS workflow/processGraph element

        :param cmdows: CMDOWS file
        :type cmdows: ElementTree
        :param nodes: nodes from data graph
        :type nodes: list
        :return: enriched MPG
        :rtype: MdaoProcessGraph
        """

        cmdows_process_graph = cmdows.find('workflow/processGraph')
        cmdows_nodes = cmdows_process_graph.find('nodes')
        if cmdows_nodes is not None:
            for node in list(cmdows_nodes):
                # Get new node info
                new_attr_dict = {'process_step': node.findasttext('processStepNumber'),
                                 'diagonal_position': node.findasttext('diagonalPosition')}
                if node.findasttext('convergerStepNumber') is not None:
                    new_attr_dict['converger_step'] = node.findasttext('convergerStepNumber')
                if node.findasttext('partitionID') is not None:
                    new_attr_dict['partition_id'] = node.findasttext('partitionID')
                # Copy other node info
                attr_dict = nodes[node.findtext('referenceUID')]
                attr_dict.update(new_attr_dict)
                self.add_node(node.findtext('referenceUID'), attr_dict=attr_dict)
        cmdows_edges = cmdows_process_graph.find('edges')
        if cmdows_edges is not None:
            for edge in list(cmdows_edges):
                self.add_edge(edge.findtext('fromExecutableBlockUID'), edge.findtext('toExecutableBlockUID'),
                              attr_dict={'process_step': int(edge.findtext('processStepNumber'))})
            self.graph['process_hierarchy'] = self.get_process_hierarchy()

    # -------------------------------------------------------------------------------------------- #
    #                                 CHECKING METHODS                                             #
    # -------------------------------------------------------------------------------------------- #
    def _check_category_a(self):
        """Extended method to perform a category A check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(MdaoProcessGraph, self)._check_category_a()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')
        var_nodes = self.find_all_nodes(category='variable')

        # Get information
        n_nodes = self.number_of_nodes()
        n_functions = len(func_nodes)
        n_variables = len(var_nodes)

        # Checks on nodes
        category_check, i = check(n_variables != 0,
                                  'There are variable nodes present in the graph, namely: %s.' % str(var_nodes),
                                  status=category_check,
                                  category='A',
                                  i=i)
        category_check, i = check(n_nodes != n_functions,
                                  'The number of total nodes does not match number of function nodes.',
                                  status=category_check,
                                  category='A',
                                  i=i)
        for node in func_nodes:
            category_check, i_not = check('process_step' not in self.nodes[node],
                                          'The process_step attribute is missing on the node %s.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i)
            category_check, i_not = check('architecture_role' not in self.nodes[node],
                                          'The architecture_role attribute is missing on the node %s.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i+1)
            category_check, i_not = check(not self.has_node(self.COORDINATOR_STRING),
                                          'The %s node is missing in the graph.' % self.COORDINATOR_STRING,
                                          status=category_check,
                                          category='A',
                                          i=i+2)
        i += 3

        # Check on edges
        for u, v, d in self.edges(data=True):
            category_check, i_not = check('process_step' not in d,
                                          'The process_step attribute missing for the edge %s --> %s.' % (u, v),
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1

        # Return
        return category_check, i

    # -------------------------------------------------------------------------------------------- #
    #                                 GRAPH SPECIFIC METHODS                                       #
    # -------------------------------------------------------------------------------------------- #
    def _add_diagonal_positions(self):
        """Method to add the diagonal positions of function blocks based on the monolithic architectures

        :return: function nodes with diagonal positions
        :rtype: None
        """

        # TODO: Update this function to only one function_ordering for both monolithic and distributed architectures

        if 'distr_function_ordering' not in self.graph:
            # Get function ordering of MDAO graph and establish diagonal order list
            mg_function_ordering = self.graph['mg_function_ordering']
            diagonal_order = self.find_all_nodes(attr_cond=['architecture_role', '==',
                                                            self.ARCHITECTURE_ROLES_FUNS[0]])  # coordinator

            # Append pre-desvars functions
            if self.FUNCTION_ROLES[3] in mg_function_ordering:
                diagonal_order.extend(mg_function_ordering[self.FUNCTION_ROLES[3]])

            # Append optimizer or DOE block
            diagonal_order.extend(self.find_all_nodes(attr_cond=['architecture_role', '==',
                                                                 self.ARCHITECTURE_ROLES_FUNS[1]]))  # optimizer
            diagonal_order.extend(self.find_all_nodes(attr_cond=['architecture_role', '==',
                                                                 self.ARCHITECTURE_ROLES_FUNS[3]]))  # doe

            # Append post-desvars functions
            if self.FUNCTION_ROLES[4] in mg_function_ordering:
                diagonal_order.extend(mg_function_ordering[self.FUNCTION_ROLES[4]])

            # Append converger block
            if self.CONVERGER_STRING in self.nodes:
                diagonal_order.extend([self.CONVERGER_STRING])

            # Append coupled functions
            if self.FUNCTION_ROLES[1] in mg_function_ordering:
                # If graph is partitioned, append local convergers
                if 'coupled_functions_groups' in self.graph['problem_formulation'] and \
                                self.graph['problem_formulation']['mdao_architecture'] == 'distributed-convergence':
                    partitions = self.graph['problem_formulation']['coupled_functions_groups']
                    local_convergers = self.graph['problem_formulation']['local_convergers']
                    for partition, nodes in enumerate(partitions):
                        if partition in local_convergers:
                            diagonal_order.extend([self.CONVERGER_STRING + str(partition)])
                        diagonal_order.extend(nodes)
                else:
                    diagonal_order.extend(mg_function_ordering[self.FUNCTION_ROLES[1]])

            # Append post-coupling functions
            if self.FUNCTION_ROLES[2] in mg_function_ordering:
                diagonal_order.extend(mg_function_ordering[self.FUNCTION_ROLES[2]])

            for diag_pos, node in enumerate(diagonal_order):
                self.nodes[node]['diagonal_position'] = diag_pos
        else:
            mdao_architecture = self.graph['problem_formulation']['mdao_architecture']
            if mdao_architecture == 'BLISS-2000':
                bliss2000 = True
                co = False
                distr_conv = False
            elif mdao_architecture == 'CO':
                bliss2000 = False
                co = True
                distr_conv = False
            else:
                bliss2000 = False
                co = False
                distr_conv = True
            mg_function_ordering = self.graph['distr_function_ordering']
            syslevel_ordering = mg_function_ordering[0]
            subsyslevel_orderings = mg_function_ordering[1]
            diagonal_order = self.find_all_nodes(attr_cond=['architecture_role', '==',
                                                            self.ARCHITECTURE_ROLES_FUNS[0]])  # coordinator

            # Append system-level pre-desvars functions
            if self.FUNCTION_ROLES[3] in syslevel_ordering:
                diagonal_order.extend(syslevel_ordering[self.FUNCTION_ROLES[3]])

            # BLISS-2000: Append system-level convergence check
            if bliss2000:
                sys_conv = self.find_all_nodes(attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_FUNS[10]])
                assert len(sys_conv) == 1, '{} distributed system convergers found, one expected.'.format(len(sys_conv))
                diagonal_order.extend(sys_conv)

            # Append system level optimizer and/or DOE block
            opts = self.find_all_nodes(
                attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_FUNS[1]])  # optimizer
            if len(opts) > 1:
                sys_opt = [item for item in opts if self.SYS_PREFIX in item]
                assert len(sys_opt) == 1, '{} system optimizers found, one expected.'.format(len(sys_opt))
                opts = sys_opt
            diagonal_order.extend(opts)
            if co:
                does = self.find_all_nodes(
                    attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_FUNS[3]])  # doe
                if len(does) > 1:
                    sys_doe = [item for item in does if self.SYS_PREFIX in item]
                    assert len(sys_doe) == 1, '{} system DOE(s) found, one expected.'.format(len(sys_doe))
                    does = sys_doe
                diagonal_order.extend(does)

            # Append system-level post-desvars functions
            if self.FUNCTION_ROLES[4] in syslevel_ordering:
                diagonal_order.extend(syslevel_ordering[self.FUNCTION_ROLES[4]])

            # Append system-level converger block
            if co or distr_conv:
                convs = self.find_all_nodes(
                    attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_FUNS[2]])  # converger
                if len(convs) >= 1:
                    sys_conv = [item for item in convs if self.SYS_PREFIX in item]
                    if distr_conv and mdao_architecture not in self.OPTIONS_ARCHITECTURES[1] + \
                            self.OPTIONS_ARCHITECTURES[3]:
                        assert len(sys_conv) == 0, '{} system convergers found, none expected'.format(len(sys_conv))
                    elif distr_conv and mdao_architecture in self.OPTIONS_ARCHITECTURES[1] + \
                        self.OPTIONS_ARCHITECTURES[3]:
                        assert len(sys_conv) <= 1, '{} system convergers found, one or none expected'.format(
                            len(sys_conv))
                    else:
                        assert len(sys_conv) == 1, '{} system convergers found, one expected.'.format(len(sys_conv))
                    convs = sys_conv
                diagonal_order.extend(convs)  # converger

            # Append system-level coupled functions
            if self.FUNCTION_ROLES[1] in syslevel_ordering:
                diagonal_order.extend(syslevel_ordering[self.FUNCTION_ROLES[1]])

            # Append system-level post-coupling functions
            if bliss2000 or co:
                if self.FUNCTION_ROLES[2] in syslevel_ordering:
                    diagonal_order.extend(syslevel_ordering[self.FUNCTION_ROLES[2]])

            # Append sublevel functions here
            for idx, subsyslevel_ord in enumerate(subsyslevel_orderings):

                if not bliss2000:
                    # Append subsystem-level pre-desvars functions
                    if self.FUNCTION_ROLES[3] in subsyslevel_ord:
                        diagonal_order.extend(subsyslevel_ord[self.FUNCTION_ROLES[3]])

                # Append subsystem-level DOE block and optimizer
                does = self.find_all_nodes(
                    attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_FUNS[3]])  # doe
                if len(does) > 1:
                    sys_doe = [item for item in does if
                               self.SUBSYS_SUFFIX in item and self.SUBSYS_SUFFIX + str(idx) in item]
                    assert len(sys_doe) == 1, '{} subsystem DOEs found, one expected.'.format(len(sys_doe))
                    does = sys_doe
                diagonal_order.extend(does)

                if bliss2000:
                    # Append subsystem-level pre-desvars functions
                    if self.FUNCTION_ROLES[3] in subsyslevel_ord:
                        diagonal_order.extend(subsyslevel_ord[self.FUNCTION_ROLES[3]])

                opts = self.find_all_nodes(
                    attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_FUNS[1]])  # optimizer
                if len(opts) > 1:
                    sys_opt = [item for item in opts if
                               self.SUBSYS_SUFFIX in item and self.SUBSYS_SUFFIX + str(idx) in item]
                    assert len(sys_opt) == 1, '{} subsystem optimizers found, one expected.'.format(len(sys_opt))
                    opts = sys_opt
                    diagonal_order.extend(opts)

                # Append subsystem-level post-desvars functions
                if self.FUNCTION_ROLES[4] in subsyslevel_ord:
                    diagonal_order.extend(subsyslevel_ord[self.FUNCTION_ROLES[4]])

                # Append subsystem-level converger block
                convs = self.find_all_nodes(
                    attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_FUNS[2]])  # converger
                if len(convs) >= 1:
                    sys_conv = [item for item in convs if self.SUBSYS_PREFIX + self.CONVERGER_STRING +
                                self.SUBSYS_SUFFIX + str(idx) == item]
                    assert len(sys_conv) <= 1, '{} subsystem convergers found, max one expected'.format(len(sys_conv))
                    convs = sys_conv
                    diagonal_order.extend(convs)  # converger

                # Append subsystem-level coupled functions
                if self.FUNCTION_ROLES[1] in subsyslevel_ord:
                    diagonal_order.extend(subsyslevel_ord[self.FUNCTION_ROLES[1]])

                # Append subsystem-level post-coupling functions
                if self.FUNCTION_ROLES[2] in subsyslevel_ord:
                    diagonal_order.extend(subsyslevel_ord[self.FUNCTION_ROLES[2]])

            # Append system-level post-coupling functions
            if distr_conv:
                if self.FUNCTION_ROLES[2] in syslevel_ordering:
                    diagonal_order.extend(syslevel_ordering[self.FUNCTION_ROLES[2]])

            for diag_pos, node in enumerate(diagonal_order):
                self.nodes[node]['diagonal_position'] = diag_pos

        return

    def add_process(self, sequence, start_step, mdg, end_in_iterative_node=None):
        """Method to add a process to a list of functions.

        The sequence is assumed to be the order of the functions in the input list. The sequence is considered simple,
        since it is not analyzed for the possibility to run functions in parallel.

        :param sequence: list of functions in the required sequence
        :type sequence: list
        :param start_step: process step number for the first element in the sequence
        :type start_step: int
        :param mdg: data graph to be used for execution dependencies
        :type mdg: MdaoDataGraph
        :param end_in_iterative_node: (optional) iterative node to which the last function should go
        :type end_in_iterative_node: basestring
        """

        # Input assertions and checks
        assert isinstance(sequence, list)
        assert len(sequence) > 0, 'Sequence cannot be an empty list.'
        assert len(sequence) == len(set(sequence))
        assert isinstance(start_step, int) and start_step >= 0, 'Start step should be a positive integer.'
        if end_in_iterative_node:
            assert self.has_node(end_in_iterative_node), 'Node %s is not present in the graph' % end_in_iterative_node

        # Get data information of the graph
        coupling_dict = mdg.get_coupling_dictionary()

        # Get initial coupling matrix of the nodes in the sequence
        coupling_matrix_1 = mdg.get_coupling_matrix(node_selection=sequence)
        process_step = start_step+1

        # Deepcopy sequence
        initial_sequence = copy.deepcopy(sequence)
        sequence = copy.deepcopy(sequence)

        while sequence:
            # Determine first and second group of nodes
            nodes_1, coupling_matrix_2 = get_executable_functions(coupling_matrix_1, sequence)
            [sequence.remove(node_1) for node_1 in nodes_1]
            nodes_2, _ = get_executable_functions(coupling_matrix_2, sequence)

            # If nodes_1 contains an iterator as first element + other nodes, then split into nodes_1 and nodes_2
            if len(nodes_1) > 1 and self.nodes[nodes_1[0]]['architecture_role'] in self.ARCHITECTURE_ROLES_FUNS[:4]:
                sequence = nodes_1[1:] + sequence
                nodes_2, _ = get_executable_functions(coupling_matrix_1[1:, 1:], sequence)
                nodes_1 = [nodes_1[0]]
            # Else if iterator as last element
            elif len(nodes_1) > 1 and self.nodes[nodes_1[-1]]['architecture_role'] in self.ARCHITECTURE_ROLES_FUNS[:4]:
                nodes_2 = [nodes_1[-1]]
                nodes_1 = nodes_1[:-1]
                sequence = nodes_2 + sequence

            # If nodes_2 contains an iterator as last element, then remove that one
            if len(nodes_2) > 1 and self.nodes[nodes_2[-1]]['architecture_role'] in self.ARCHITECTURE_ROLES_FUNS[:4]:
                nodes_2 = nodes_2[:-1]

            # Coupling first and second nodes based on data links
            if nodes_2:
                for i_1, node_1 in enumerate(nodes_1):
                    if 'process_step' not in self.nodes[node_1]:
                        self.nodes[node_1]['process_step'] = process_step-1
                    for i_2, node_2 in enumerate(nodes_2):
                        if 'process_step' not in self.nodes[node_2]:
                            self.nodes[node_2]['process_step'] = process_step
                        if coupling_matrix_1[i_1, i_2+len(nodes_1)] > 0:
                            self.add_edge(node_1, node_2, process_step=process_step)

                # If first node does not have a second node link, then save these nodes for next iteration
                connected, not_connected = [], []
                for node_1 in nodes_1:
                    if not set(self.get_targets(node_1)).intersection(set(nodes_2)):
                        if self.nodes[node_1]['architecture_role'] not in self.ARCHITECTURE_ROLES_FUNS[:4] and \
                                self.nodes[nodes_2[0]]['architecture_role'] not in self.ARCHITECTURE_ROLES_FUNS[:4]:
                            not_connected.append(node_1)
                        else:
                            [self.add_edge(node_1, node_2, process_step=process_step) for node_2 in nodes_2]
                            connected.append((nodes_1 + sequence).index(node_1))
                    else:
                        connected.append((nodes_1 + sequence).index(node_1))

                # Update sequence and coupling matrix
                sequence = not_connected + sequence
                coupling_matrix_1 = np.delete(coupling_matrix_1, connected, 0)  # Remove columns of connected nodes
                coupling_matrix_1 = np.delete(coupling_matrix_1, connected, 1)  # Remove rows of connected nodes

                # Check whether for every data connection a process path between the two nodes exist
                for node_2 in nodes_2:
                    for node in reversed(initial_sequence[:initial_sequence.index(node_2)]):
                        if (node in coupling_dict[node_2] or self.nodes[node]['architecture_role'] in
                                self.ARCHITECTURE_ROLES_FUNS[:4]):
                            subgraph = self.get_kadmos_subgraph(initial_sequence)
                            if not nx.has_path(subgraph, node, node_2):
                                self.add_edge(node, node_2, process_step=self.nodes[node_2]['process_step'])
                            else:
                                # Check if the existing path is a valid path
                                path = nx.shortest_path(subgraph, node, node_2)
                                idx = 0
                                for func in path:
                                    if func in initial_sequence and initial_sequence.index(func) >= idx:
                                        idx = initial_sequence.index(func)
                                    else:
                                        self.add_edge(node, node_2, process_step=self.nodes[node_2]['process_step'])
            else:
                # End in iterative node or simply end function
                if end_in_iterative_node:
                    [self.add_edge(node_1, end_in_iterative_node, process_step=process_step) for node_1 in nodes_1]
                    if 'converger_step' not in self.nodes[end_in_iterative_node] or \
                            process_step > self.nodes[end_in_iterative_node]['converger_step']:
                        self.nodes[end_in_iterative_node]['converger_step'] = process_step
            # Increment process step
            process_step += 1

        # Check for misplaced nodes
        misplaced_nodes = []
        for node in initial_sequence:
            sources = self.get_sources(node)
            # If there isn't a source with a process step one lower than the current process step, the node is misplaced
            if sources:
                misplaced = True
                for source in sources:
                    node_step = [self.nodes[node]['process_step'], self.nodes[node]['converger_step']] if \
                        'converger_step' in self.nodes[node] else [self.nodes[node]['process_step']]
                    source_step = [self.nodes[source]['process_step'], self.nodes[source]['converger_step']] if \
                        'converger_step' in self.nodes[source] else [self.nodes[source]['process_step']]
                    if any(step+1 in node_step for step in source_step):
                        misplaced = False
                        break
                if misplaced:
                    misplaced_nodes.append(node)
        if misplaced_nodes:
            logger.warning('In the process graph determination, nodes {} do not have a proper process connection. '
                           'Sequence of functions can be improved'.format(misplaced_nodes))

        return

    def add_process_partitions(self, previous_sequence, partitions, next_sequence, start_step, mdg,
                               end_in_iterative_node=None):
        """Function to add the process in the partitions

        :param previous_sequence: previous list of functions in the required sequence
        :type previous_sequence: list
        :param partitions: process partitions to be added
        :type partitions: dict
        :param next_sequence: next list of functions in the required sequence
        :type next_sequence: list
        :param start_step: process step number for the first element in the sequence
        :type start_step: int
        :param mdg: data graph to be used for execution dependencies
        :type mdg: MdaoDataGraph
        :param end_in_iterative_node: (optional) iterative node to which the last function should go
        :type end_in_iterative_node: basestring
        :return: graph enriched with process partitioning
        :rtype: MdaoProcessGraph
        """

        # Get problem formulation
        local_convergers = self.graph['problem_formulation']['local_convergers']
        sequences_partitions = self.graph['problem_formulation']['sequence_partitions']
        sublevel_function_orderings = mdg.graph['distr_function_ordering'][1]
        mdao_arch = mdg.graph['problem_formulation']['mdao_architecture']
        _, _, sub_convs = self.get_architecture_node_ids(mdao_arch, number_of_groups=len(partitions))

        # Add process first sequence
        self.add_process(previous_sequence, start_step, mdg)
        max_process_step = self.nodes[previous_sequence[-1]]['process_step']

        # Connect partitions
        connected_partitions = []
        for part in range(len(partitions)):
            # Check if partition is already connected
            if part in connected_partitions:
                continue

            # Check if partition is the start of a sequence of partitions
            sequence_partitions = [part]
            for sequence_list in sequences_partitions:
                if sequence_list:
                    if part == sequence_list[0]:
                        sequence_partitions = sequence_list
                        break

            # Start sequence
            sequence = copy.deepcopy(previous_sequence)
            process_step = start_step

            # Connect the sequence of partitions
            for partition in sequence_partitions:
                # Check if current partition has a local converger
                if partition in local_convergers:
                    # Connect sub-level pre-coupling functions
                    sequence = sequence + sublevel_function_orderings[partition][self.FUNCTION_ROLES[4]] + \
                                [sub_convs[partition]]
                    self.add_process(sequence, process_step, mdg)
                    # Connect sub-level coupled functions to sub-level converger
                    sequence = [sub_convs[partition]] + sublevel_function_orderings[partition][self.FUNCTION_ROLES[1]]
                    self.add_process(sequence, self.nodes[sequence[0]]['process_step'], mdg,
                                     end_in_iterative_node=sub_convs[partition])
                    # Connect sub-level post-coupling functions
                    if sublevel_function_orderings[partition][self.FUNCTION_ROLES[2]]:
                        sequence = [sub_convs[partition]] + sublevel_function_orderings[partition][
                            self.FUNCTION_ROLES[2]]
                        self.add_process(sequence, self.nodes[sub_convs[partition]]['converger_step'], mdg)
                        if self.nodes[sequence[-1]]['process_step'] > max_process_step:
                            max_process_step = self.nodes[sequence[-1]]['process_step']
                    else:
                        sequence = [sub_convs[partition]]
                        if self.nodes[sub_convs[partition]]['converger_step'] > max_process_step:
                            max_process_step = self.nodes[sub_convs[partition]]['converger_step']
                    process_step = self.nodes[sub_convs[partition]]['converger_step']
                else:
                    # Connect all sub-level functions
                    sequence = sequence + sublevel_function_orderings[partition][self.FUNCTION_ROLES[4]] + \
                               sublevel_function_orderings[partition][self.FUNCTION_ROLES[1]] + \
                               sublevel_function_orderings[partition][self.FUNCTION_ROLES[2]]
                    self.add_process(sequence, process_step, mdg)
                    if self.nodes[sequence[-1]]['process_step'] > max_process_step:
                        max_process_step = self.nodes[sequence[-1]]['process_step']
                connected_partitions += [partition]

            # Connect last partition to next sequence
            if next_sequence:
                sequence = sequence + next_sequence

            # Connect final sequence and end in iterative node
            self.add_process(sequence, process_step, mdg, end_in_iterative_node=end_in_iterative_node)

        # Set correct process number for the sequence after the partitions
        if next_sequence:
            step_diff = max_process_step + 1 - self.nodes[next_sequence[0]]['process_step']
            max_process_step = self.nodes[next_sequence[0]]['process_step']
            for node in next_sequence:
                self.nodes[node]['process_step'] += step_diff
                if self.nodes[node]['process_step'] > max_process_step:
                    max_process_step = self.nodes[node]['process_step']
        if end_in_iterative_node:
            self.nodes[end_in_iterative_node]['converger_step'] = max_process_step + 1

        return

    def connect_nested_iterators(self, master, slave, direction='slave->master'):
        """Method to connect a slave iterator to a master iterator in a nested configuration.

        :param master: upper iterator node in the nested configuration
        :type master: basestring
        :param slave: lower iterator node in the nested configuration
        :type slave: basestring
        :return: graph enriched with nested iterators
        :rtype: MdaoProcessGraph

        An example is if a converger inside an optimizer in MDF needs to be linked back.
        """
        dir_options = ['slave->master', 'master->slave']
        assert direction in dir_options, 'direction options are {} and {}.'.format(dir_options[0], dir_options[1])
        assert self.has_node(master), 'Node {} not present in the graph.'.format(master)
        assert self.has_node(slave), 'Node {} not present in the graph.'.format(slave)
        if direction == 'slave->master':
            assert 'converger_step' in self.nodes[slave], 'Slave node %s needs to have a converger_step.' % slave
            self.add_edge(slave, master, process_step=self.nodes[slave]['converger_step'] + 1)
            if 'converger_step' not in self.nodes[master]:
                self.nodes[master]['converger_step'] = self.nodes[slave]['converger_step'] + 1
            else:
                if self.nodes[slave]['converger_step'] + 1 > self.nodes[master]['converger_step']:
                    self.nodes[master]['converger_step'] = self.nodes[slave]['converger_step'] + 1
        else:
            assert 'process_step' in self.nodes[master], 'Master node {} needs to have a process_step.'.format(master)
            self.add_edge(master, slave, process_step=self.nodes[master]['process_step'] + 1)
            self.nodes[slave]['process_step'] = self.nodes[master]['process_step'] + 1
        return

    def get_process_order(self, only_executable_block=True):
        """Method to receive a list with the right order of the process based on process step numbers."""
        # Find first diagonal node
        # Find the step 0 node
        start_nodes = self.find_all_nodes(attr_cond=['process_step', '==', 0])
        assert len(start_nodes) == 1, 'There can only be one start node with process step number 0.'
        first_node = start_nodes[0]
        assert 'converger_step' in self.nodes[first_node], 'Start node should have a converger_step attribute.'
        max_step = self.nodes[first_node]['converger_step']
        process_list = []
        for step in range(max_step + 1):
            process_step_nodes = self.find_all_nodes(attr_cond=['process_step', '==', step])
            updated_process_step_nodes = copy.deepcopy(process_step_nodes)
            for process_step_node in process_step_nodes:
                if self.nodes[process_step_node]['architecture_role'] in self.ARCHITECTURE_ROLES_FUNS[:4]:
                    updated_process_step_nodes.remove(process_step_node)
            process_list.extend(updated_process_step_nodes)
        return process_list

    def get_process_hierarchy(self):
        """Method to assess the hierarchy of the process based on the process lines in a ProcessGraph.

        :return: nested list with process hierarchy, e.g. [COOR, A, [OPT, [CONV, D1, D2], F1, G1, G2]]
        :rtype: list
        """
        # Find the step 0 node
        start_nodes = self.find_all_nodes(attr_cond=['process_step', '==', 0])
        assert len(start_nodes) == 1, 'There can only be one start node with process step number 0.'
        start_node = start_nodes[0]

        # Get the simple cycles in a set/list
        cycles = self.get_ordered_cycles()

        # Start process hierarchy object
        process_hierarchy = self.get_process_list_iteratively(start_node, cycles)
        return process_hierarchy

    def get_process_list_iteratively(self, cycle_node, cycles):
        """Method to obtain the process list of a collection of cycles given an iterative cycle_node. The process is
        iterative, since for every subcycle found the method is called again.

        :param cycle_node: the node that is starting and closing the cycle (e.g. coordinator, optimizer, etc.)
        :type cycle_node: str
        :param cycles: collection of cycles found in the graph
        :type cycles: list
        :return: the process list
        :rtype: list

        .. note:: Example of a process list:
            [COOR, A, [OPT, [CONV, D1, D2], F1, G1, G2]]
        """
        sub_list = [cycle_node, []]
        current_cycles = [cycle for cycle in cycles if cycle_node in cycle]
        other_cycles = [cycle for cycle in cycles if cycle_node not in cycle]
        subcycle_nodes = []
        for current_cycle in current_cycles:
            cycle_nodes = [node for node in current_cycle if node != cycle_node]
            for node in cycle_nodes:
                node_in_other_subcycles = False
                for other_cycle in other_cycles:
                    if node in other_cycle and cycle_node not in other_cycle:
                        node_in_other_subcycles = True
                # If node is in other subcycles, perform function iteratively
                # First filter out all cycles that contain the cycle_node -> filtered_cycles
                # sublist[1].append(get_process_list_iteratively(node, filtered_cycles)
                if node_in_other_subcycles:
                    if node not in subcycle_nodes:
                        filtered_cycles = list(cycles)
                        for cycle in list(filtered_cycles):
                            if cycle_node in cycle:
                                filtered_cycles.remove(cycle)
                        subcycle_nodes.append(node)
                        sub_list[1].append(self.get_process_list_iteratively(node, filtered_cycles))
                # If node is not in any other cycles, simply add to this one (at the right location based on the
                # process_step number)
                else:
                    if node not in sub_list[1]:
                        if len(sub_list[1]) == 0:  # append if list still empty
                            sub_list[1].append(node)
                        elif isinstance(sub_list[1][-1], list):  # append if last entry is a list instance
                            sub_list[1].append(node)
                        elif self.nodes[sub_list[1][-1]]['process_step'] <= self.nodes[node]['process_step']:
                            # append if last entry has equal or lower step number
                            sub_list[1].append(node)
                        else:  # insert if last entry has a higher step number
                            for i in reversed(range(len(sub_list[1]))):
                                if not isinstance(sub_list[1][i], list):
                                    if self.nodes[sub_list[1][i]]['process_step'] <= self.nodes[node]['process_step']:
                                        sub_list[1].insert(i + 1, node)
                                        break
                                    elif i == 0:
                                        sub_list[1].insert(i, node)
                                else:
                                    sub_list[1].insert(i + 1, node)
                                    break
        return sub_list


def get_executable_functions(coupling_matrix, sequence):
    """Method to determine which of the functions in the process graph are executable based on data dependencies from
    the MDG.

    :param coupling_matrix: coupling matrix of the MDG
    :type coupling_matrix: array.py
    :param sequence: sequence of functions to be analyzed
    :type sequence: list
    :return: executable functions and updated coupling matrix with removed rows and columns
    :rtype: tuple
    """

    assert len(coupling_matrix) == len(sequence), "Coupling matrix size and sequence length should match."

    # Return empty lists if the sequence is empty
    if not sequence:
        return [], []

    # Perform analysis for non-empty sequence
    upper_columns_empty = True
    functions = [sequence[0]]
    updated_coupling_matrix = coupling_matrix[1:, 1:]

    col = 1
    while upper_columns_empty and col < len(coupling_matrix):
        if sum(coupling_matrix[:col, col]) == 0:
            functions.append(sequence[col])
            updated_coupling_matrix = updated_coupling_matrix[1:, 1:]
        else:
            upper_columns_empty = False
        col += 1

    return functions, updated_coupling_matrix
