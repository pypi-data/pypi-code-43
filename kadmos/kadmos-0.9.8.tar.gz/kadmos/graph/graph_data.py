from __future__ import absolute_import, division, print_function

# Imports
import itertools
import copy
import logging
import distutils.util
import numbers
import os
import re
import random

import operator as oper
from collections import OrderedDict

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from builtins import int

from lxml import etree
from networkx import NetworkXNoCycle
from six import iteritems, itervalues, string_types

from kadmos.utilities.strings import get_correctly_extended_latex_label
from ..utilities import prompting
from ..utilities import printing
from ..utilities.general import make_camel_case, unmake_camel_case, make_plural, get_list_entries, translate_dict_keys,\
    get_mdao_setup, get_group_vars
from ..utilities.testing import check
from ..utilities.plotting import AnnoteFinder
from ..utilities.xmls import Element

from kadmos.graph.graph_kadmos import KadmosGraph, _parse_check

from kadmos.graph.mixin_mdao import MdaoMixin


# Settings for the logger
logger = logging.getLogger(__name__)


class DataGraph(KadmosGraph):

    OPTIONS_FUNCTION_ORDER_METHOD = ['manual', 'minimum feedback']
    F_SAMPLES_B2k = 15  # LHS sample factor for BLISS-2000 (N_SAMPLES = F_SAMPLES*number_of_variables)

    def __init__(self, *args, **kwargs):
        super(DataGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _create_cmdows_problem_def(self):

        # Create problemDefinition
        cmdows_problem_definition = Element('problemDefinition')
        graph_problem_formulation = self.graph.get('problem_formulation')
        cmdows_problem_definition.set('uID', str(graph_problem_formulation.get('mdao_architecture')) +
                                      str(graph_problem_formulation.get('convergence_type')))

        # Create problemDefinition/problemFormulation
        cmdows_problem_formulation = cmdows_problem_definition.add('problemFormulation')
        graph_problem_formulation = self.graph.get('problem_formulation')
        cmdows_problem_formulation.add('mdaoArchitecture', graph_problem_formulation.get('mdao_architecture'))
        cmdows_problem_formulation.add('convergerType', graph_problem_formulation.get('convergence_type'))
        cmdows_executable_blocks_order = cmdows_problem_formulation.add('executableBlocksOrder')
        for index, item in enumerate(graph_problem_formulation.get('function_order')):
            # Create problemDefinition/problemFormulation/executableBlocksOrder/executableBlock
            cmdows_executable_blocks_order.add('executableBlockUID', item, attrib={'position': str(index + 1)})
        if 'coupled_functions_groups' in graph_problem_formulation:
            cmdows_executable_blocks_grouping = cmdows_problem_formulation.add('executableBlocksGrouping')
            for group in graph_problem_formulation['coupled_functions_groups']:
                cmdows_grouping = cmdows_executable_blocks_grouping.add('group')
                for exec_block in group:
                    cmdows_grouping.add('executableBlockUID', exec_block)
        cmdows_problem_formulation.add('allowUnconvergedCouplings',
                                       str(graph_problem_formulation.get('allow_unconverged_couplings')).lower())

        # Create problemDefinition/problemFormulation/doeSettings
        graph_settings = graph_problem_formulation.get('doe_settings')
        if graph_settings is not None:
            cmdows_settings = cmdows_problem_formulation.add('doeSettings')
            cmdows_settings.add('method', graph_settings.get('method'))
            cmdows_settings.add('runs', graph_settings.get('runs'))
            cmdows_settings.add('centerRuns', graph_settings.get('center_runs'))
            cmdows_settings.add('seed', graph_settings.get('seed'))
            cmdows_settings.add('levels', graph_settings.get('levels'))

        # Create problemDefinition/problemRoles
        cmdows_problem_roles = cmdows_problem_definition.add('problemRoles')
        # Create problemDefinition/problemRoles/parameters
        cmdows_parameters = cmdows_problem_roles.add('parameters')
        # Create problemDefinition/problemRoles/parameters/...
        for cmdows_parameterIndex, cmdows_parameterDef in enumerate(self.CMDOWS_ROLES_DEF):
            cmdows_parameter = cmdows_parameters.add(cmdows_parameterDef[0] + 's')
            graph_attr_cond = ['problem_role', '==', self.PROBLEM_ROLES_VARS[cmdows_parameterIndex]]
            graph_parameter = self.find_all_nodes(category='variable', attr_cond=graph_attr_cond)
            for graph_problem_role in graph_parameter:
                cmdows_problem_role = cmdows_parameter.add(cmdows_parameterDef[0])
                cmdows_problem_role.set('uID',
                                        self.PROBLEM_ROLES_VAR_SUFFIXES[cmdows_parameterIndex] +
                                        str(graph_problem_role))
                cmdows_problem_role.add('parameterUID', graph_problem_role)
                for cmdows_problem_role_attr in cmdows_parameterDef[1]:
                    if cmdows_problem_role_attr == 'samples':
                        # Create problemDefinition/problemRoles/parameters/designVariables/designVariable/samples
                        cmdows_samples = cmdows_problem_role.add('samples')
                        if self.nodes[graph_problem_role].get(cmdows_problem_role_attr) is not None:
                            for idx, itm in enumerate(self.nodes[graph_problem_role].get(cmdows_problem_role_attr)):
                                cmdows_samples.add('sample', format(itm, '.12f'), attrib={'position': str(idx + 1)})
                    elif cmdows_problem_role_attr == 'valid_ranges':
                        if 'valid_ranges' in self.nodes[graph_problem_role]:
                            cmdows_valid_ranges = cmdows_problem_role.add('validRanges')
                            for lr_type, scope in self.LIMIT_RANGE_DICT.items():
                                cmdows_valid_ranges.add('limit_range',
                                                        self.nodes[graph_problem_role]['valid_ranges'].get(lr_type),
                                                        attrib={'scope': scope} if scope else None,
                                                        camel_case_conversion=True)
                            cmdows_valid_ranges.add('list_range',
                                                    self.nodes[graph_problem_role]['valid_ranges'].get('list_range'),
                                                    camel_case_conversion=True)
                    else:
                        cmdows_problem_role.add(self.CMDOWS_ATTRIBUTE_DICT[cmdows_problem_role_attr],
                                                self.nodes[graph_problem_role].get(cmdows_problem_role_attr),
                                                camel_case_conversion=True)

        # Create problemDefinition/problemRoles/executableBlocks
        cmdows_executable_blocks = cmdows_problem_roles.add('executableBlocks')
        graph_executable_blocks = self.graph['problem_formulation']['function_ordering']
        # Create problemDefinition/problemRoles/executableBlocks/...
        for executable_block in self.FUNCTION_ROLES:
            if graph_executable_blocks.get(executable_block) is not None:
                if len(graph_executable_blocks.get(executable_block)) != 0:
                    cmdows_key = cmdows_executable_blocks.add(make_camel_case(executable_block) + 'Blocks')
                    for graph_block in graph_executable_blocks.get(executable_block):
                        cmdows_key.add(make_camel_case(executable_block) + 'Block', graph_block)

        return cmdows_problem_definition

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             LOAD METHODS                                                         #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _load_cmdows_problem_def(self, cmdows):

        graph_problem_form = {}

        cmdows_problem_formulation = cmdows.find('problemDefinition/problemFormulation')
        if cmdows_problem_formulation is not None:
            graph_problem_form['mdao_architecture'] = cmdows_problem_formulation.findtext('mdaoArchitecture')
            graph_problem_form['convergence_type'] = cmdows_problem_formulation.findtext('convergerType')
            cmdows_executable_blocks = \
                cmdows_problem_formulation.find('executableBlocksOrder').findall('executableBlockUID')
            cmdows_executable_blocks_order = [None] * len(list(cmdows_executable_blocks))
            for cmdows_executable_block in cmdows_executable_blocks:
                cmdows_executable_blocks_order[int(cmdows_executable_block.get('position')
                                                   ) - 1] = cmdows_executable_block.text
            graph_problem_form['function_order'] = cmdows_executable_blocks_order
            if cmdows_problem_formulation.find('executableBlocksGrouping') is not None:
                cmdows_function_grouping = []
                cmdows_executable_blocks_grouping = cmdows_problem_formulation.find('executableBlocksGrouping').findall('group')
                for idx, group in enumerate(cmdows_executable_blocks_grouping):
                    exec_blocks = group.findall('executableBlockUID')
                    cmdows_function_grouping.append([])
                    for exec_block in exec_blocks:
                        cmdows_function_grouping[idx].append(exec_block.text)
                if cmdows_function_grouping:
                    graph_problem_form['coupled_functions_groups'] = cmdows_function_grouping
            graph_problem_form['allow_unconverged_couplings'] = bool(distutils.util.strtobool(
                cmdows_problem_formulation.findtext('allowUnconvergedCouplings')))
            graph_problem_form['doe_settings'] = {}
            cmdows_doe_settings = cmdows_problem_formulation.find('doeSettings')
            if cmdows_doe_settings is not None:
                for cmdows_doe_setting in list(cmdows_doe_settings):
                    graph_problem_form['doe_settings'][unmake_camel_case(cmdows_doe_setting.tag
                                                                         )] = cmdows_doe_setting.text

        cmdows_problem_roles = cmdows.find('problemDefinition/problemRoles')
        if cmdows_problem_roles is not None:
            graph_problem_form['function_ordering'] = {}
            cmdows_executable_blocks = cmdows_problem_roles.find('executableBlocks')
            for role in self.FUNCTION_ROLES:
                cmdows_blocks = cmdows_executable_blocks.find(make_camel_case(role) + 'Blocks')
                if cmdows_blocks is None:
                    arr = list()
                else:
                    arr = list()
                    for cmdows_block in list(cmdows_blocks):
                        if self.nodes.get(cmdows_block.text) is None:
                            # Add node if it does not exist yet
                            self.add_node(cmdows_block.text, category='function')
                        self.nodes[cmdows_block.text]['problem_role'] = role
                        arr.append(cmdows_block.text)
                graph_problem_form['function_ordering'][role] = arr

            variable_types = [make_plural(role[0]) for role in self.CMDOWS_ROLES_DEF]
            for variable_type in variable_types:
                cmdows_variables = cmdows_problem_roles.find('parameters/' + variable_type)
                if cmdows_variables is not None:
                    for cmdows_variable in list(cmdows_variables):
                        cmdows_parameter_uid = cmdows_variable.findtext('parameterUID')
                        cmdows_suffix = '__' + re.findall(r'(?<=__).*?(?=__)', cmdows_variable.get('uID'))[0] + '__'
                        # Add problem role
                        try:
                            self.nodes[cmdows_parameter_uid]['problem_role'] = self.CMDOWS_ROLES_DICT_INV[cmdows_suffix]
                            # TODO: Find a more elegant way to handle samples and parameterUID
                            for attribute in cmdows_variable.getchildren():
                                if attribute.tag == 'samples':
                                    cmdows_samples = attribute.findall('sample')
                                    cmdows_sample_data = [None] * len(list(cmdows_samples))
                                    for cmdows_sample in cmdows_samples:
                                        cmdows_sample_data[int(cmdows_sample.get('position')) - 1] = \
                                            float(cmdows_sample.text)
                                    self.nodes[cmdows_parameter_uid]['samples'] = cmdows_sample_data
                                    cmdows_variable.remove(attribute)
                                elif attribute.tag == 'validRanges':
                                    for sub_attr in attribute.getchildren():
                                        if sub_attr.tag == 'limitRange':
                                            if sub_attr.attrib.get('scope') == 'local':
                                                sub_attr.tag = 'limitRangeLocal'
                                            elif sub_attr.attrib.get('scope') == 'global':
                                                sub_attr.tag = 'limitRangeGlobal'
                            self.nodes[cmdows_parameter_uid].update(cmdows.finddict(cmdows_variable,
                                                                                    camel_case_conversion=True))
                            del self.nodes[cmdows_parameter_uid]['parameter_u_i_d']
                        except KeyError:
                            logger.error('Could not find the node "{}" for some reason when loading the CMDOWS'
                                         .format(cmdows_parameter_uid))
                            pass

        self.graph['problem_formulation'] = graph_problem_form

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                         GRAPH-SPECIFIC METHODS                                                   #
    # ---------------------------------------------------------------------------------------------------------------- #
    def add_vnode(self, node_id, **attr_dict):
        """Method to add a variable node"""
        attr_dict['category'] = 'variable'
        if 'label' not in attr_dict:
            attr_dict['label'] = node_id.split('/')[-1]
        if 'instance' not in attr_dict:
            attr_dict['instance'] = 0
        self.add_node(node_id, attr_dict)

    def add_vnodes(self, *node_ids):
        if len(node_ids) == 1:
            if isinstance(node_ids[0], (list, tuple)):
                node_ids = node_ids[0]
        for node_id in node_ids:
            self.add_vnode(node_id)

    def connect_variable(self, vnode, input_of=(), output_of=()):
        """Connect a variable as input and/or output of multiple functions"""
        for input in input_of:
            self.add_edge(vnode, input)
        for output in output_of:
            self.add_edge(output, vnode)

    def connect_function(self, fnode, input_vars=(), output_vars=()):
        """Connect a function's inputs and/or outputs"""
        for input in input_vars:
            self.add_edge(input, fnode)
        for output in output_vars:
            self.add_edge(fnode, output)

    def mark_as_design_variable(self, node, lower_bound=None, upper_bound=None, samples=None, nominal_value=None,
                                global_lb=None, global_ub=None, ignore_outdegree=False):
        """Method to mark a single node as a design variable and add the required metadata for its definition.

        :param node: node
        :type node: str
        :param lower_bound: lower bound of design variable
        :type lower_bound: float
        :param upper_bound: upper bound of design variable
        :type upper_bound: float
        :param samples: samples of design variable
        :type samples: list
        :param nominal_value: nominal value of design variable
        :type nominal_value: float
        :param global_lb: global lower bound to be used when bounds are changed.
        :type global_lb: float
        :param global_ub: global lower bound to be used when bounds are changed.
        :type global_ub: float
        :param ignore_outdegree: option to ignore the outdegree required
        :type ignore_outdegree: bool
        :returns: graph with enriched design variable node
        """
        # Input assertions
        assert self.has_node(node), 'Node {} is not present in the graph.'.format(node)
        assert self.in_degree(node) <= 1, \
            'Node {} has to have an indegree of zero or one to be allowed as design variable.'.format(node)
        assert self.out_degree(node) > 0 or ignore_outdegree, \
            'Node {} has to have an outdegree of at least one to be a design variable.'.format(node)
        assert isinstance(lower_bound, (numbers.Number, list, type(None))), \
            'Lower bound should be a number or list of numbers.'
        assert isinstance(upper_bound, (numbers.Number, list, type(None))), \
            'Upper bound should be a number or list of numbers.'
        assert isinstance(samples, (list, type(None))), 'Samples should be a list.'

        # Mark nodes
        gnode = self.nodes[node]
        gnode['problem_role'] = self.PROBLEM_ROLES_VARS[0]
        attrb = ['valid_ranges', 'limit_range', 'limit_range_global', 'limit_range_local']
        if lower_bound is not None:
            self.add_nested_attribute(attrb[0:2] + ['minimum'], lower_bound, current_dict=gnode)
        if upper_bound is not None:
            self.add_nested_attribute(attrb[0:2] + ['maximum'], upper_bound, current_dict=gnode)
        if global_lb is not None:
            self.add_nested_attribute([attrb[0], attrb[2]] + ['minimum'], global_lb,
                                      current_dict=gnode)
        if global_ub is not None:
            self.add_nested_attribute([attrb[0], attrb[2]] + ['maximum'], global_ub,
                                      current_dict=gnode)
        if global_lb is not None or global_ub is not None:
            if 'limit_range' in gnode['valid_ranges']:
                gnode['valid_ranges'][attrb[3]] = copy.deepcopy(gnode['valid_ranges'][attrb[1]])
                del gnode['valid_ranges'][attrb[1]]
        if samples is not None:
            gnode['samples'] = samples
        if nominal_value:
            gnode['nominal_value'] = nominal_value

        return

    def mark_as_design_variables(self, nodes, lower_bounds=None, upper_bounds=None, samples=None, nominal_values=None):
        """Method to mark a list of nodes as design variable and add metadata.

        :param nodes: list of nodes present in the graph
        :type nodes: list or str
        :param lower_bounds: list of lower bound values
        :type lower_bounds: list, numbers.Number
        :param upper_bounds: list of upper bounds
        :type upper_bounds: list, numbers.Number
        :param samples: nested list of kadmos values
        :type samples: list
        :param nominal_values: list of nominal values
        :type nominal_values: list, numbers.Number
        :return: graph with enriched design variable nodes
        """

        # Input assertions
        assert isinstance(nodes, list), 'Input nodes should be a list of graph nodes. Use mark_as_design_variable for' \
                                        ' single node.'
        if isinstance(lower_bounds, numbers.Number) or lower_bounds is None:
            lower_bounds = [lower_bounds]*len(nodes)
        else:
            assert isinstance(lower_bounds, list), 'Lower bounds should be a list.'
            assert len(lower_bounds) == len(nodes), 'Number of lower bounds is not equal to the number of nodes.'
        if isinstance(upper_bounds, numbers.Number) or upper_bounds is None:
            upper_bounds = [upper_bounds]*len(nodes)
        else:
            assert isinstance(upper_bounds, list), 'Upper bounds should be a list.'
            assert len(upper_bounds) == len(nodes), 'Number of upper bounds is not equal to the number of nodes.'
        if isinstance(nominal_values, numbers.Number) or nominal_values is None:
            nominal_values = [nominal_values]*len(nodes)
        else:
            assert isinstance(nominal_values, list), 'Nominal values should be a list.'
            assert len(nominal_values) == len(nodes), 'Number of nominal values is not equal to the number of nodes.'
        if isinstance(samples, numbers.Number) or samples is None:
            samples = [samples]*len(nodes)
        else:
            assert isinstance(samples, list), 'Nominal values should be a list.'
            assert len(samples) == len(nodes), 'Number of nominal values is not equal to the number of nodes.'

        # Mark nodes
        for node, lb, ub, sm, nv in zip(nodes, lower_bounds, upper_bounds, samples, nominal_values):
            self.mark_as_design_variable(node, lower_bound=lb, upper_bound=ub, samples=sm, nominal_value=nv)

        return

    def mark_as_objective(self, node, remove_unused_outputs=False):
        """Method to mark a single node as objective.

        :param node: variable node
        :type node: str
        :param remove_unused_outputs: option to remove unused outputs
        :type remove_unused_outputs: bool
        :return: graph enriched with objective node
        """

        # Input assertions
        assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Mark node
        self.nodes[node]['problem_role'] = self.PROBLEM_ROLES_VARS[1]

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def mark_as_constraint(self, node, operator, reference_value, remove_unused_outputs=False):
        """Method to mark a node as a constraint.

        :param node: node to be marked (on the left side of the operator
        :type node: str
        :param operator: constraint operator or list of constraint operators
        :type operator: str or string list
        :param reference_value: value on the right side of the operator or list of values corresponding to the list of
                                operators
        :type reference_value: numbers.Number or list
        :param remove_unused_outputs: option to remove unused outputs
        :type remove_unused_outputs: bool
        :returns: graph with enriched constraint node
        """

        # dict of inequality operators
        operators = {'>': oper.gt,
                     '>=': oper.ge,
                     '<': oper.lt,
                     '<=': oper.le,
                     '==': oper.eq}

        # Input assertions
        assert self.has_node(node), 'Node %s not present in the graph.' % node
        if isinstance(operator, string_types):
            assert operator in operators, 'Operator has to be one of the following: %s' % list(operators)
        elif isinstance(operator, list):
            assert len(operator) == 1 or len(operator) == 2, 'Only one or two operators can be provided.'
            assert len(operator) == len(reference_value), '{} operators provided with {} reference values. Please ' \
                                                          'provide equal sized lists.'.format(len(operator),
                                                                                              len(reference_value))
            for op in operator:
                assert operators[op](1, 0) or operators[op](0, 1), 'Operator has to be one of the following: >, >=, <' \
                                                                   ' or <='
        else:
            raise AssertionError('operator input is of wrong type {}.'.format(str(type(operator))))
        assert isinstance(reference_value, (numbers.Number, list)), 'Reference value is not a number or list.'

        # check if multiple bounds are used correctly.
        if isinstance(operator, list):
            if (operators[operator[0]](0, 1) and operators[operator[1]](1, 0)) or ((operators[operator[0]](1, 0) and
                                                                                    operators[operator[1]](0, 1))):
                a = reference_value[0]
                b = reference_value[1]
                if operators[operator[1]](a, b) and operators[operator[0]](b, a):
                    pass
                else:
                    raise IOError("ERROR: x {} {} and x {} {} are not consistent as "
                                  "bounds".format(operator[0], reference_value[0], operator[1], reference_value[1]))
            else:
                raise IOError("ERROR: the combination of {} and {} as bounds is not logical. "
                              "Please correct the operators provided".format(operator[0], operator[1]))

        # Mark nodes
        self.nodes[node]['problem_role'] = self.PROBLEM_ROLES_VARS[2]
        if isinstance(operator, string_types):
            self.nodes[node]['constraint_operator'] = operator
            self.nodes[node]['reference_value'] = reference_value
        else:
            self.nodes[node]['constraint_operator'] = ';'.join(operator)
            self.nodes[node]['reference_value'] = ';'.join([str(item) for item in reference_value])
        if operator == '==':
            self.nodes[node]['constraint_type'] = 'equality'
        else:
            self.nodes[node]['constraint_type'] = 'inequality'

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def mark_as_constraints(self, nodes, operators, reference_values, remove_unused_outputs=False):
        """Method to mark multiple nodes as constraints.

        :param nodes: nodes to be marked.
        :type nodes: list
        :param operators: operators to be implemented (as list per node or as single operator for all)
        :type operators: str, list
        :param reference_values: reference values to be used (as list of values per node or as single value for all)
        :type reference_values: float, list
        :param remove_unused_outputs: option to remove unused outputs
        :type remove_unused_outputs: bool
        :return: graph with enriched constraint nodes

        Operators: '==', '>', '<', '>=' and '<='
        """

        # Input assertions
        # poss_ops = ['==', '>', '<', '>=', '<=']
        assert isinstance(nodes, list), 'Input nodes should be a list of graph nodes. Use mark_as_constraint for ' \
                                        'single node.'
        if isinstance(operators, string_types):
            operators = [operators]*len(nodes)
        else:
            assert isinstance(operators, list), 'Operators should be a list.'
            assert len(operators) == len(nodes), 'Number of operators is not equal to the number of nodes.'
        if isinstance(reference_values, numbers.Number):
            reference_values = [reference_values]*len(nodes)
        else:
            assert isinstance(reference_values, list), 'Reference values should be a list.'
            assert len(reference_values) == len(nodes), 'Number of reference values is not equal to the number of ' \
                                                        'nodes.'
        for node, op, ref in zip(nodes, operators, reference_values):
            self.mark_as_constraint(node, op, ref)

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def mark_as_qoi(self, node):
        """Function to mark a list of nodes as quantity of interest.

        :param nodes: list of nodes present in the graph
        :type nodes: list
        :param remove_unused_outputs: option to remove unused outputs
        :type remove_unused_outputs: bool
        """

        # Input assertions
        assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Mark nodes
        self.nodes[node]['problem_role'] = self.PROBLEM_ROLES_VARS[3]

        return

    def mark_as_qois(self, nodes, remove_unused_outputs=False):
        """Function to mark a list of nodes as quantity of interest.

        :param nodes: list of nodes present in the graph
        :type nodes: list
        :param remove_unused_outputs: option to remove unused outputs
        :type remove_unused_outputs: bool
        """

        # Input assertions
        assert isinstance(nodes, list)
        for node in nodes:
            assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Mark nodes
        for node in nodes:
            self.nodes[node]['problem_role'] = self.PROBLEM_ROLES_VARS[3]

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def unmark_variable(self, node):
        """Function to unmark any marked variable.

        :param node: variable node to be unmarked
        :type node: str
        :return: graph with unmarked node
        """

        # Input assertions
        assert isinstance(node, string_types)
        assert self.has_node(node), 'Node {} is not present in the graph.'.format(node)
        assert self.nodes[node]['category'] == 'variable', 'Node {} should be of category variable.'.format(node)

        # Unmark design variable
        if 'problem_role' in self.nodes[node]:
            pr = self.nodes[node]['problem_role']
            if pr == self.PROBLEM_ROLES_VARS[0]:  # design variable
                del self.nodes[node]['problem_role']
                if 'valid_ranges' in self.nodes[node]:
                    del self.nodes[node]['valid_ranges']
                if 'samples' in self.nodes[node]:
                    del self.nodes[node]['samples']
                if 'nominal_value' in self.nodes[node]:
                    del self.nodes[node]['nominal_value']
            elif pr == self.PROBLEM_ROLES_VARS[1]:  # objective
                del self.nodes[node]['problem_role']
            elif pr == self.PROBLEM_ROLES_VARS[2]:  # constraint
                del self.nodes[node]['problem_role']
                del self.nodes[node]['constraint_operator']
                del self.nodes[node]['reference_value']
            elif pr == self.PROBLEM_ROLES_VARS[3]:  # quantity of interest
                del self.nodes[node]['problem_role']
            else:
                raise AssertionError('Invalid problem role {} found on variable node {}'.format(pr, node))

    def remove_unused_outputs(self):
        """ Function to remove output nodes from an FPG which do not have a problem role.

        :return: the nodes that were removed
        :rtype: list
        """
        # TODO: Reposition this and other functions to the FPG class.
        output_nodes = self.find_all_nodes(subcategory='all outputs')
        removed_nodes = []
        for output_node in output_nodes:
            if 'problem_role' not in self.nodes[output_node]:
                self.remove_node(output_node)
                removed_nodes.append(output_node)
        return removed_nodes

    def remove_problematic_functions(self):
        """Remove functions that are independent or sinks"""
        removed_nodes = []
        for fnode in self.find_all_nodes(category='function'):
            if self.nodes[fnode]['subcategory'] in ['independent', 'sink']:
                self.remove_function_nodes(fnode)
                removed_nodes.append(fnode)
        return removed_nodes

    def remove_unused_nodes(self):
        """Iteratively remove output nodes that do not have a problem role and then remove functions that have become
        sinks or independent.

        :return: the nodes that were removed
        :rtype: list
        """
        removed_nodes = []
        nodes_were_removed = True
        while nodes_were_removed:
            n_removed_nodes1 = len(removed_nodes)
            removed_nodes.extend(self.remove_unused_outputs())
            removed_nodes.extend(self.remove_problematic_functions())
            n_removed_nodes2 = len(removed_nodes)
            nodes_were_removed = n_removed_nodes2 > n_removed_nodes1
        return removed_nodes

    @property
    def variable_nodes(self):
        """Get list with all variable nodes."""
        return [node for node in self.nodes if self.nodes[node]['category'] == 'variable']

    def get_fdg(self):
        fdg = self.deepcopy()
        for vnode in self.variable_nodes:
            sources = fdg.get_sources(vnode)
            targets = fdg.get_targets(vnode)
            for src in sources:
                for trg in targets:
                    if not fdg.has_edge(src, trg):
                        fdg.add_edge(src, trg)
            fdg.remove_node(vnode)
        return fdg

    def get_schema_root_name(self, node=None):
        if node is None:
            random_var_node = self.find_all_nodes(category='variable')[0]
            return random_var_node.split('/')[1]
        else:
            return node.split('/')[1]

    def get_related_schema_node(self, node_id):
        if 'related_to_schema_node' in self.nodes[node_id]:
            return self.nodes[node_id]['related_to_schema_node']
        else:
            return node_id

    def get_coupling_matrix(self, function_order_method='manual', node_selection=None):
        """Function to determine the role of the different functions in the FPG.

        :param function_order_method: algorithm to be used for the order in which the functions are executed.
        :type function_order_method: str
        :param node_selection: selection of nodes for which the coupling matrix will be calculated only
        :type node_selection: list
        :return: graph with enriched function node attributes and function problem role dictionary
        :rtype: FundamentalProblemGraph
        """

        # Make a copy of the graph, check it and remove all inputs and outputs
        if node_selection:
            graph = self.get_subgraph_by_function_nodes(node_selection)
        else:
            graph = self.deepcopy()
        nodes_to_remove = list()
        # TODO: Consider using the check function
        nodes_to_remove.extend(graph.find_all_nodes(subcategory='all inputs'))
        nodes_to_remove.extend(graph.find_all_nodes(subcategory='all outputs'))
        graph.remove_nodes_from(nodes_to_remove)

        # Determine and check function ordering method
        assert function_order_method in self.OPTIONS_FUNCTION_ORDER_METHOD
        if function_order_method == 'manual':
            if node_selection:
                function_order = node_selection
            else:
                assert 'function_order' in graph.graph['problem_formulation'], 'function_order must be given as ' \
                                                                               'attribute.'
                function_order = graph.graph['problem_formulation']['function_order']
        elif function_order_method == 'random':
            function_order = graph.find_all_nodes(category='function')

        # First store all the out- and in-edge variables per function
        function_var_data = dict()
        # noinspection PyUnboundLocalVariable
        for function in function_order:
            function_var_data[function] = dict(in_vars=set(), out_vars=set())
            function_var_data[function]['in_vars'] = [edge[0] for edge in graph.in_edges(function)]
            function_var_data[function]['out_vars'] = [edge[1] for edge in graph.out_edges(function)]
        # Create an empty matrix
        coupling_matrix = np.zeros((len(function_order), len(function_order)), dtype=np.int)
        # Create the coupling matrix (including circular dependencies)
        for idx1, function1 in enumerate(function_order):
            for idx2, function2 in enumerate(function_order):
                n_coupling_vars = len(set(function_var_data[function1]['out_vars']).
                                      intersection(set(function_var_data[function2]['in_vars'])))
                coupling_matrix[idx1, idx2] = n_coupling_vars

        return coupling_matrix

    def get_coupling_dictionary(self):
        """ Function to get a coupling dictionary.

        :return: coupling dictionary
        :rtype: dict

        For each function node, the dictionary indicates from which function
        nodes it gets its input and the number of variables it gets.

        * F2 ==> x1, x2 ==> F1
        * F3 ==> x3 ==> F1

        Will give: {F1: {F2: 2, F3: 1}}
        """

        coupling_dict = dict()

        # Get all function nodes and corresponding coupling matrix
        function_nodes = self.find_all_nodes(category='function')
        coupling_matrix = self.get_coupling_matrix(node_selection=function_nodes)

        # Fill in dictionary
        for idx1, function1 in enumerate(function_nodes):
            coupling_dict[function1] = dict()
            for idx2, function2 in enumerate(function_nodes):
                if coupling_matrix[idx2][idx1] != 0:
                    coupling_dict[function1][function2] = coupling_matrix[idx2][idx1]

        return coupling_dict

    def get_possible_function_order(self, method='auto', multi_start=None, check_graph=False, coupling_dict=None,
                                    node_selection=None, rcb=1.0, use_runtime_info=False):
        """ Method to find a possible function order, in the order: pre-coupling, coupled, post-coupling functions.
        If partitions have already been set, the partitions will be taken into account and the function order in each
        partition will be determined as well.

        :param method: algorithm which will be used to minimize the feedback loops
        :type method: str
        :param multi_start: start the algorithm from multiple starting points
        :type multi_start: int
        :param check_graph: check whether graph has problematic variables
        :type check_graph: bool
        :param coupling_dict: coupling dictionary of the graph
        :type coupling_dict: dict
        :param node_selection: option to get the order of only a selection of nodes instead of the entire graph
        :type node_selection: list
        :param rcb: runtime-coupling balance, relative importance between feedback and runtime while optimizing
                    function order. 1: min feedback, 0: min runtime
        :type rcb: float
        :param use_runtime_info: option to use the runtime of the disciplines while determining the function order
        :type use_runtime_info: bool
        :return Possible function order
        :rtype list
        """

        # Input assertions
        if check_graph:
            assert not self.find_all_nodes(subcategory='all problematic variables'), \
                'Graph still has problematic variables.'
        assert 0 <= rcb <= 1, 'Runtime-coupling balance should be between zero and one.'
        if use_runtime_info:
            nodes = list(node_selection) if node_selection else self.find_all_nodes(category='function')
            for node in nodes:
                assert 'performance_info' in self.nodes[node], 'Performance info missing for node {}'.format(node)
                assert 'run_time' in self.nodes[node]['performance_info'], 'Runtime missing for node {}'.format(node)

        # If zero or one node is present, the solution can be given immediately
        if node_selection is None:
            if len(self.find_all_nodes(category='function')) < 2:
                return self.find_all_nodes(category='function')
        else:
            if len(node_selection) < 2:
                return node_selection

        # Get coupling dictionary
        if not coupling_dict:
            coupling_dict = self.get_coupling_dictionary()

        # Check for partitions
        if 'problem_formulation' in self.graph and 'coupled_functions_groups' in self.graph['problem_formulation'] and \
                not node_selection:
            partitions = self.graph['problem_formulation']['coupled_functions_groups']
        else:
            partitions = None

        # Get function graph
        if node_selection:
            subgraph = self.get_subgraph_by_function_nodes(node_selection)
            function_graph = subgraph.get_function_graph()
        else:
            function_graph = self.get_function_graph()
        function_graph.remove_edges_from(function_graph.selfloop_edges())

        # Add a super node in which the coupled functions will be merged
        function_graph.add_node('super_node', category='function')
        coupled_functions = []

        if partitions:
            # Merge the nodes of the partitions into the super node
            for partition in partitions:
                for function_id in partition:
                    function_graph = nx.contracted_nodes(function_graph, 'super_node', function_id, self_loops=False)

            # Check if all coupled nodes are assigned to a partition
            if not nx.is_directed_acyclic_graph(function_graph):
                cycle = nx.find_cycle(function_graph)
                functions_in_cycle = set()
                functions_in_cycle.update(function_id for edges in cycle for function_id in edges)
                functions_in_cycle.remove('super_node')
                assert nx.is_directed_acyclic_graph(function_graph), 'Coupled functions {} should be added to a ' \
                                                                     'partition'.format(list(functions_in_cycle))
        else:
            # As long as not all coupled functions are merged into the super node:
            while not nx.is_directed_acyclic_graph(function_graph):
                # Find a cycle
                cycle = nx.find_cycle(function_graph)

                # Find the functions in the cycle
                functions_in_cycle = set()
                functions_in_cycle.update(function_id for edges in cycle for function_id in edges)
                functions_in_cycle = list(functions_in_cycle)

                # Merge the coupled functions in the super node
                for function_id in functions_in_cycle:
                    if function_id != 'super_node':
                        coupled_functions.append(function_id)
                        function_graph = nx.contracted_nodes(function_graph, 'super_node', function_id,
                                                             self_loops=False)

        # Find a topological function order
        initial_function_order = list(nx.topological_sort(function_graph))

        # Sort coupled functions to minimize feedback
        if partitions:
            coupled_functions_order = []
            for partition, nodes in enumerate(partitions):
                if len(nodes) > 1:
                    if 'local_convergers' in self.graph['problem_formulation'] and \
                            self.graph['problem_formulation']['local_convergers']:
                        nodes = self.get_possible_function_order(method, multi_start=multi_start, rcb=rcb,
                                                                 use_runtime_info=use_runtime_info,
                                                                 coupling_dict=coupling_dict,
                                                                 node_selection=list(nodes))
                    else:
                        nodes = self.minimize_feedback(list(nodes), method, multi_start=multi_start, rcb=rcb,
                                                       use_runtime_info=use_runtime_info, coupling_dict=coupling_dict)
                partitions[partition] = nodes
                coupled_functions_order.extend(nodes)
            # Make sure the function orders in the partitions are consistent with the overall function order
            self.graph['problem_formulation']['coupled_functions_groups'] = partitions
        elif coupled_functions:
            coupled_functions_order = self.minimize_feedback(coupled_functions, method, multi_start=multi_start,
                                                             rcb=rcb, use_runtime_info=use_runtime_info,
                                                             coupling_dict=coupling_dict)
        else:
            coupled_functions_order = []

        if coupled_functions_order:
            # Get pre-coupling functions and sort
            pre_coupling_functions = initial_function_order[:initial_function_order.index('super_node')]
            pre_coupling_functions_order = self.sort_nodes_for_process(pre_coupling_functions)

            # Get post-coupling functions and sort
            post_coupling_functions = initial_function_order[initial_function_order.index('super_node') + 1:]
            post_coupling_functions_order = self.sort_nodes_for_process(post_coupling_functions)

            # Get function_order
            function_order = pre_coupling_functions_order + coupled_functions_order + post_coupling_functions_order
        else:
            # If no coupled functions are present, the number of feedback is zero and the nodes need to be sorted for an
            # optimal process only
            initial_function_order.pop(initial_function_order.index('super_node'))
            function_order = self.sort_nodes_for_process(initial_function_order)

        return function_order

    def get_highest_instance(self, node):
        """
        Method to get the highest instance of a node.

        :param node: node
        :type node: str
        :return: highest instance of the node
        :rtype: int
        """
        assert 'instance' in self.nodes[node], 'node {} does not have the expected attribute "instance".'.format(node)
        highest_instance = int(self.nodes[node]['instance'])
        instance_exists = True
        while instance_exists:
            # Check for one higher instance
            check_node = node + '__i' + str(highest_instance + 1)
            if self.has_node(check_node):
                highest_instance += 1
                assert self.nodes[check_node]['instance'] == highest_instance, \
                    'instance attribute of node {} does not match node string.'.format(check_node)
            else:
                return highest_instance

    def sort_nodes_for_process(self, nodes, coupling_dict=None):
        """ Method to sort function nodes such that the correct process order is obtained. In case this function is used
        before the MDG is created, the number of feedback loops and runtime may change.

        :param nodes: function nodes to sort
        :type nodes: list
        :param coupling_dict: coupling dictionary of the graph
        :type coupling_dict: dict
        :return: nodes in sorted order
        :rtype: list
        """

        # Input assertions
        for func in nodes:
            assert func in self, "Function node {} must be present in graph.".format(func)
            assert self.nodes[func]['category'] == 'function', "Node {} is not a function node".format(func)

        # If zero or one node, return immediately
        if len(nodes) < 2:
            return nodes

        nodes_to_sort = list(nodes)
        function_order = []

        # Get couplings between nodes
        if not coupling_dict:
            coupling_dict = self.get_coupling_dictionary()

        while nodes_to_sort:
            sorted_nodes = []
            # Check for each node whether it can be sorted
            for idx, node in enumerate(nodes_to_sort):
                # If the non-sorted nodes before the node don't give input to the node, the node can be sorted
                if not set(nodes_to_sort[:idx]).intersection(coupling_dict[node]):
                    sorted_nodes.append(node)
            function_order.extend([node for node in nodes if node in sorted_nodes])
            # Delete the sorted nodes from the nodes_to_sort list
            for node in sorted_nodes:
                nodes_to_sort.pop(nodes_to_sort.index(node))

        return function_order

    def get_runtime_sequence(self, sequence, use_runtime_info=False, coupling_dict=None, get_time_line=False):
        """Function to get the runtime of a sequence of nodes. Each node starts running as soon as all its required
        input data is available.

        :param sequence: sequence of nodes
        :type sequence: list
        :param use_runtime_info: option to use the runtime of the nodes, if False the runtime for each node is set to 1
        :type use_runtime_info: bool
        :param coupling_dict: coupling dictionary of the graph
        :type coupling_dict: dict
        :param get_time_line: option to return a time line which indicates at each time step which nodes are waiting
        for input, which nodes are running and which nodes are finished
        """

        # Input assertion
        if use_runtime_info:
            for node in sequence:
                assert 'performance_info' in self.nodes[node]
                assert 'run_time' in self.nodes[node]['performance_info'], 'Run time missing for node {}'.format(node)

        # If zero nodes, return zero runtime
        if not sequence:
            if get_time_line:
                return [[0, [], [], []]]
            else:
                return 0

        # Get coupling dictionary
        if not coupling_dict:
            coupling_dict = self.get_coupling_dictionary()

        # Initialize variables
        waiting_list = dict()
        running = dict()
        finished = set()
        time_line = []
        total_runtime = 0

        # Add required input and runtime to each node in the waiting list
        for node in sequence:
            required_input = set(sequence[:sequence.index(node)]).intersection(coupling_dict[node])
            runtime = self.nodes[node]['performance_info']['run_time'] if use_runtime_info else 1
            waiting_list[node] = [required_input, runtime]

        while waiting_list or running:
            if waiting_list:
                updated_waiting_list = dict(waiting_list)
                for node in waiting_list:
                    # Check if all input data is available
                    if waiting_list[node][0].issubset(finished):
                        # If all input is known the node can be moved to the run list and deleted from the waiting list
                        running[node] = updated_waiting_list.pop(node)[1]
                waiting_list = dict(updated_waiting_list)
            # Add timestep to the time line
            if get_time_line:
                time_line.append([total_runtime, list(waiting_list), list(running), list(finished)])
            # When the running list is updated, the next time step can be determined
            time_step = min(list(running.values()))
            # Let all modules run for the time of the time step
            updated_running_list = dict(running)
            for node in running:
                updated_running_list[node] -= time_step
                # If node is finished, move it to the finished list
                if updated_running_list[node] == 0:
                    finished.add(node)
                    del updated_running_list[node]
            running = dict(updated_running_list)
            # Add the time step to the total time
            total_runtime += time_step

        if get_time_line:
            # Add final step to time line
            time_line.append([total_runtime, list(waiting_list), list(running), list(finished)])
            return time_line
        else:
            return total_runtime

    def minimize_feedback(self, nodes, method='auto', multi_start=None, get_evaluations=False, coupling_dict=None, rcb=1,
                          use_runtime_info=False):
        """Function to find the function order with minimum feedback or minimum runtime

        :param nodes: nodes for which the feedback needs to be minimized
        :type nodes: list
        :param method: algorithm used to find optimal function order
        :type method: str
        :param multi_start: start the algorithm from multiple starting points
        :type multi_start: int
        :param get_evaluations: option to get the number of evaluations needed by the algorithm as output
        :type get_evaluations: bool
        :param coupling_dict: coupling dictionary of the graph
        :type coupling_dict: dict
        :param rcb: runtime-coupling balance, relative importance between feedback and runtime while optimizing
                    function order. 1: min feedback, 0: min runtime
        :type rcb: float
        :param use_runtime_info: option to use the runtime of the disciplines while determining the function order
        :type use_runtime_info: bool
        :return function order
        :rtype list
        :return number of evaluations (optional)
        :rtype int
        """

        # Input assertions
        assert 0 <= rcb <= 1, 'Runtime-coupling balance should be between zero and one.'
        if use_runtime_info:
            for node in nodes:
                assert 'performance_info' in self.nodes[node], 'Performance info missing for node {}'.format(node)
                assert 'run_time' in self.nodes[node]['performance_info'], 'Run time missing for node {}'.format(node)

        # If zero or one node is given, the solution can be returned immediately
        if len(nodes) < 2:
            return nodes

        # Get coupling dictionary
        if not coupling_dict:
            coupling_dict = self.get_coupling_dictionary()

        # Get total number of couplings and total runtime
        total_couplings = max(sum([coupling_dict[function1][function2] for function1 in nodes for function2 in nodes if
                                   function2 in coupling_dict[function1]]), 1)
        total_time = sum([self.nodes[node]['performance_info']['run_time'] for node in nodes]) if use_runtime_info else\
            len(nodes)

        # Get random starting points for a multi-start
        if isinstance(multi_start, int):
            start_points = [[] for _ in range(multi_start)]
            for i in range(multi_start):
                random.shuffle(nodes)
                start_points[i][:] = nodes
            multi_start = start_points
        elif multi_start is None:
            multi_start = [nodes]

        best_order = list(nodes)
        min_f, min_feedback, min_time = float("inf"), float("inf"), float("inf")

        # Get sequencing method
        if method == 'auto':
            method = self._get_sequencing_method(len(nodes))

        # Start algorithm for each starting point
        n_eval = 0
        for start_point in range(len(multi_start)):
            if start_point > 0 and method in ['brute-force', 'branch-and-bound']:
                logger.warning('Multi-start is useless when using an exact algorithm to determine the function order.')
                break
            if method == 'brute-force':
                function_order, n_eval_iter = self._brute_force(nodes, coupling_dict, rcb, use_runtime_info)
            elif method == 'branch-and-bound':
                function_order, n_eval_iter = self._branch_and_bound(nodes, coupling_dict, rcb, use_runtime_info)
            elif method == 'single-swap':
                function_order, n_eval_iter = self._single_swap(multi_start[start_point], coupling_dict, rcb,
                                                                use_runtime_info)
            elif method == 'two-swap':
                function_order, n_eval_iter = self._two_swap(multi_start[start_point], coupling_dict, rcb,
                                                             use_runtime_info)
            elif method == 'hybrid-swap':
                function_order, n_eval_iter1 = self._two_swap(multi_start[start_point], coupling_dict, rcb,
                                                              use_runtime_info)
                function_order, n_eval_iter2 = self._single_swap(function_order, coupling_dict, rcb,
                                                                 use_runtime_info)
                n_eval_iter = n_eval_iter1 + n_eval_iter2
            elif method == 'genetic-algorithm':
                function_order, n_eval_iter = self._genetic_algorithm(nodes, coupling_dict, rcb, use_runtime_info)
            else:
                raise IOError('Selected method (' + method + ') is not a valid method for sequencing, supported ' +
                              'methods are: brute-force, single-swap, two-swap, hybrid-swap, branch-and-bound')

            n_eval += n_eval_iter

            # Get feedback info
            feedback, time = self.get_feedback_info(function_order, coupling_dict, use_runtime_info)

            # Remember best order found
            f = rcb*(feedback/float(total_couplings)) + (1-rcb)*(time/float(total_time))
            if (feedback == min_feedback and time < min_time) or (time == min_time and feedback < min_feedback) or \
                    (f < min_f):
                best_order, min_f, min_feedback, min_time = list(function_order), f, feedback, time

        function_order = list(best_order)

        if get_evaluations:
            return function_order, n_eval
        else:
            return function_order


    def _get_sequencing_method(self, n_nodes):
        """ Function to determine which sequencing method can best be used based on the problem characteristics

        :param nodes: node selection
        :type nodes: list
        """

        if n_nodes <= 11:
            method = 'branch-and-bound'
        elif 12 < n_nodes < 35:
            method = 'single-swap'
        elif 35 < n_nodes < 40:
            method = 'hybrid-swap'
        else:
            method = 'two-swap'

        return method

    def _brute_force(self, nodes, coupling_dict, rcb, use_runtime_info):
        """Function to find the minimum number of feedback loops using the brute-force method: try all possible
        combinations and select the best one

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :param coupling_dict: coupling dictionary of the graph
        :type coupling_dict: dict
        :param rcb: runtime-coupling balance, relative importance between feedback and runtime while optimizing
                    function order. 1: min feedback, 0: min runtime
        :type rcb: float
        :param use_runtime_info: option to use the runtime of the disciplines while determining the function order
        :type use_runtime_info: bool
        :return: function order
        :rtype: list
        """

        # Calculate the number of runs that are needed and give a warning when it exceeds a threshold
        if len(nodes) > 9:
            logger.warning(str(np.math.factorial(len(nodes))) + ' tool combinations need to be evaluated for the '
                           'brute-force method. Be aware that this can take up a considerable amount of time and '
                           'resources')

        # Get total number of couplings and total runtime
        total_couplings = max(sum([coupling_dict[function1][function2] for function1 in nodes for function2 in nodes if
                                   function2 in coupling_dict[function1]]), 1)
        total_time = sum([self.nodes[node]['performance_info']['run_time'] for node in nodes]) if use_runtime_info \
            else len(nodes)

        best_order = list(nodes)
        min_f, min_feedback, min_time = float("inf"), float("inf"), float("inf")

        # Keep track of number of evaluated function orders
        n_eval = 0

        # Get all possible combinations
        for current_order in itertools.permutations(nodes):
            n_eval += 1

            # Get feedback and runtime information of current solution
            feedback, time = self.get_feedback_info(list(current_order), coupling_dict, use_runtime_info)

            # Evaluate whether current solution is better than the best one found so far
            f = rcb * (feedback / float(total_couplings)) + (1 - rcb) * (time / float(total_time))
            if (feedback == min_feedback and time < min_time) or (time == min_time and feedback < min_feedback) or \
                    (f < min_f):
                best_order, min_f, min_feedback, min_time = list(current_order), f, feedback, time

        return best_order, n_eval

    def _single_swap(self, nodes, coupling_dict, rcb, use_runtime_info):
        """Function to find the minimum number of feedback loops using the single-swap method: improve the solution
         by searching for a better position for each node

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :param coupling_dict: coupling dictionary of the graph
        :type coupling_dict: dict
        :param rcb: runtime-coupling balance, relative importance between feedback and runtime while optimizing
                    function order. 1: min feedback, 0: min runtime
        :type rcb: float
        :param use_runtime_info: option to use the runtime of the disciplines while determining the function order
        :type use_runtime_info: bool
        :return: function order
        :rtype: list
        """

        converged = False

        # Get total number of couplings and total runtime
        total_couplings = max(sum([coupling_dict[function1][function2] for function1 in nodes for function2 in nodes if
                                   function2 in coupling_dict[function1]]), 1)
        total_time = sum([self.nodes[node]['performance_info']['run_time'] for node in nodes]) if use_runtime_info \
            else len(nodes)

        # Take the input order as start point
        best_order = list(nodes)
        min_feedback, min_time = self.get_feedback_info(nodes, coupling_dict, use_runtime_info)
        min_f = rcb*(min_feedback/float(total_couplings)) + (1-rcb)*(min_time/float(total_time))

        # Keep track of number of evaluated function orders
        n_eval = 0

        while not converged:
            new_iteration = False

            # Move each node until a better solution is found
            for idx in range(len(best_order)):
                node = best_order[idx]

                # Get feedback information for each node placement
                for position in range(len(best_order)):

                    # Skip current solution
                    if idx == len(best_order) - position - 1:
                        continue
                    # Copy current solution
                    new_order = list(best_order)
                    # Delete current node
                    new_order.pop(idx)
                    # Insert node at new position (starting from the back)
                    new_order.insert(len(best_order) - position - 1, node)
                    n_eval += 1
                    # Get feedback and runtime information of current solution
                    feedback, time = self.get_feedback_info(new_order, coupling_dict, use_runtime_info)
                    # Evaluate whether current solution is better than the best one found so far
                    f = rcb * (feedback / float(total_couplings)) + (1 - rcb) * (time / float(total_time))
                    if (feedback == min_feedback and time < min_time) or (time == min_time and feedback < min_feedback)\
                            or (f < min_f):
                        best_order, min_f, min_feedback, min_time = list(new_order), f, feedback, time
                        new_iteration = True

                    # When a better solution is found, the current iteration is stopped and a new iteration is
                    # started with the improved solution as start point
                    if new_iteration:
                        break
                if new_iteration:
                    break

            # When no improvement is found, the algorithm is terminated
            if not new_iteration:
                converged = True

        return best_order, n_eval

    def _two_swap(self, nodes, coupling_dict, rcb, use_runtime_info):
        """Function to find the minimum number of feedback loops using the two-swap method: improve the solution
        by swapping two nodes

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :param coupling_dict: coupling dictionary of the graph
        :type coupling_dict: dict
        :param rcb: runtime-coupling balance, relative importance between feedback and runtime while optimizing
                    function order. 1: min feedback, 0: min runtime
        :type rcb: float
        :param use_runtime_info: option to use the runtime of the disciplines while determining the function order
        :type use_runtime_info: bool
        :return: function order
        :rtype: list
        """

        converged = False

        # Keep track of number of evaluated function orders
        n_eval = 0

        # Get total number of couplings and total runtime
        total_couplings = max(sum([coupling_dict[function1][function2] for function1 in nodes for function2 in nodes if
                                   function2 in coupling_dict[function1]]), 1)
        total_time = sum([self.nodes[node]['performance_info']['run_time'] for node in nodes]) if use_runtime_info \
            else len(nodes)

        # Take the input order as start point
        best_order = list(nodes)
        min_feedback, min_time = self.get_feedback_info(best_order, coupling_dict, use_runtime_info)
        min_f = rcb * (min_feedback / float(total_couplings)) + (1 - rcb) * (min_time / float(total_time))

        while not converged:
            new_iteration = False

            # Swap two nodes until a better solution is found
            for i in range(len(nodes)):
                for j in range(len(nodes) - (i + 1)):

                    # Copy current solution
                    neighbor_solution = list(best_order)
                    # Swap two nodes to get a neighbor solution
                    neighbor_solution[i], neighbor_solution[-j - 1] = best_order[-j - 1], best_order[i]
                    # Get feedback information of the neighbor solution
                    n_eval += 1
                    # Get feedback and runtime information of current solution
                    feedback, time = self.get_feedback_info(neighbor_solution, coupling_dict, use_runtime_info)
                    # Evaluate whether current solution is better than the best one found so far
                    f = rcb * (feedback / float(total_couplings)) + (1 - rcb) * (time / float(total_time))
                    if (feedback == min_feedback and time < min_time) or (time == min_time and feedback < min_feedback)\
                            or (f < min_f):
                        best_order, min_f, min_feedback, min_time = list(neighbor_solution), f, feedback, time
                        new_iteration = True

                    # When a better solution is found, the current iteration is stopped and a new iteration is
                    # started with the improved solution as start point
                    if new_iteration:
                        break
                if new_iteration:
                    break

            # When no improvement is found, the algorithm is terminated
            if not new_iteration:
                converged = True

        return best_order, n_eval

    def _branch_and_bound(self, nodes, coupling_dict, rcb, use_runtime_info):
        """Function to find the minimum number of feedback loops using the branch-and-bound method: search the solution
        space in a systematic way to find the exact solution

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :param coupling_dict: coupling dictionary of the graph
        :type coupling_dict: dict
        :param rcb: runtime-coupling balance, relative importance between feedback and runtime while optimizing
                    function order. 1: min feedback, 0: min runtime
        :type rcb: float
        :param use_runtime_info: option to use the runtime of the disciplines while determining the function order
        :type use_runtime_info: bool
        :return: function order
        :rtype: list
        """

        # Imports
        from sortedcontainers import SortedList

        # Initialize variables
        active_branches = SortedList()
        n_eval = 0  # Keep track of number of evaluated function orders

        # Get total number of couplings and maximum runtime of graph
        total_couplings = max(sum([coupling_dict[function1][function2] for function1 in nodes for function2 in nodes if
                                   function2 in coupling_dict[function1]]), 1)
        total_time = sum([self.nodes[node]['performance_info']['run_time'] for node in nodes]) if use_runtime_info \
            else len(nodes)

        # Calculate lower bound for each initial branch
        if len(nodes) != 1:
            for node in nodes:
                n_eval += 1
                feedback, time = self._get_lower_bound_branch_and_bound([node], nodes, coupling_dict, use_runtime_info)
                f = rcb * (feedback / float(total_couplings)) + (1 - rcb) * (time / float(total_time))
                # Depending on the objective, the branches are sorted differently
                if rcb >= 0.5:
                    active_branches.add([f, feedback, time, len(nodes) - 1, [node]])
                else:
                    active_branches.add([f, time, feedback, len(nodes) - 1, [node]])

        while True:
            # If the sequence consists of one node, return solution immediately
            if len(nodes) == 1:
                best_branch = [nodes]
                break

            # Get the best branch and remove it from the active branches (due to the sorted list, the best branch is
            # the first branch in the list)
            best_branch = active_branches.pop(0)

            # Check whether the branch is a complete solution. If so, the best solution is found and iteration stopped
            if len(best_branch[-1]) == len(nodes):
                break

            # If branch is not a complete solution:
            # Explore branch and add children of selected branch to the list with active branches
            for node in nodes:
                if node not in best_branch[-1]:
                    new_branch = best_branch[-1] + [node]
                    n_eval += 1
                    feedback, time = self._get_lower_bound_branch_and_bound(new_branch, nodes, coupling_dict,
                                                                            use_runtime_info)
                    f = rcb * (feedback / float(total_couplings)) + (1 - rcb) * (time / float(total_time))
                    # Depending on the objective, the branches are sorted differently
                    if rcb >= 0.5:
                        active_branches.add([f, feedback, time, len(nodes) - len(new_branch), new_branch])
                    else:
                        active_branches.add([f, time, feedback, len(nodes) - len(new_branch), new_branch])

        return best_branch[-1], n_eval

    def _get_lower_bound_branch_and_bound(self, branch, nodes, coupling_dict, use_runtime_info):
        """Function to calculate the lower bound of a branch in the branch and bound algorithm.
        The lower bound for the number of feedback loops is defined as the amount of feedback loops that are guaranteed
        to occur if the current branch is placed at the beginning of the order. The lower bound for the runtime is
        defined as the runtime of the current branch.

        :param branch: the nodes in the branch
        :type branch: list
        :param nodes: the nodes that are considered in the sequencing problem
        :type nodes: list
        :param coupling_dict: coupling dictionary of the graph
        :type coupling_dict: dict
        :param use_runtime_info: option to use the runtime of the disciplines while determining the function order
        :type use_runtime_info: bool
        :return: lower bound
        :rtype: int
        """

        # Calculate the lower bound for the number of feedback loops
        n_feedback = 0
        for idx1, function1 in enumerate(branch):
            for idx2, function2 in enumerate(nodes):
                if function2 in coupling_dict[function1] and function2 not in branch[:idx1]:
                    n_feedback += coupling_dict[function1][function2]

        # Calculate the lower bound for the runtime by calculating the runtime of the branch
        run_time_branch = self.get_runtime_sequence(branch, coupling_dict=coupling_dict,
                                                    use_runtime_info=use_runtime_info)

        return n_feedback, run_time_branch

    # noinspection PyUnresolvedReferences
    def _genetic_algorithm(self, nodes, coupling_dict, rcb, use_runtime_info):

        import array

        from deap import base
        from deap import creator
        from deap import tools
        from deap import algorithms

        # Settings GA
        cxpb = 0.5
        mutpb = 0.65
        ngen = 750
        indpb = 0.02
        pop_size = 250

        # Make mapping of nodes to sequence of integers
        mapping = copy.deepcopy(nodes)

        # Get total number of couplings and maximum runtime of graph
        total_couplings = max(sum([coupling_dict[function1][function2] for function1 in nodes for function2 in nodes if
                                   function2 in coupling_dict[function1]]), 1)
        total_time = sum([self.nodes[node]['performance_info']['run_time'] for node in nodes]) if use_runtime_info \
            else len(nodes)

        # Create fitness class based on the optimization objective (= rcb value)
        creator.create('Fitness', base.Fitness, weights=(-0.99, -0.01)) if rcb in [0, 1] else \
            creator.create('Fitness', base.Fitness, weights=(-1.0,))

        # Create individual class
        creator.create('Individual', array.array, typecode='i', fitness=creator.Fitness)

        # Get toolbox
        toolbox = base.Toolbox()

        # Fill the toolbox with methods
        toolbox.register('indices', random.sample, range(len(nodes)), len(nodes))
        toolbox.register('individual', tools.initIterate, creator.Individual, toolbox.indices)
        toolbox.register('population', tools.initRepeat, list, toolbox.individual)
        toolbox.register('mate', tools.cxOrdered)
        toolbox.register('mutate', tools.mutShuffleIndexes, indpb=indpb)
        toolbox.register('select', tools.selTournament, tournsize=3)
        toolbox.register('evaluate', self._get_fitness_individual, mapping=mapping, coupling_dict=coupling_dict,
                         rcb=rcb, use_runtime_info=use_runtime_info, total_couplings=total_couplings,
                         total_time=total_time)

        population = toolbox.population(pop_size)
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)
        pop, logbook = algorithms.eaSimple(population, toolbox, cxpb, mutpb, ngen, halloffame=hof, verbose=True,
                                           stats=stats)
        n_eval = sum([logbook[generation]['nevals'] for generation in range(len(logbook))])

        # Get best results
        function_order = []
        for idx in hof[0]:
            function_order.append(mapping[idx])

        return function_order, n_eval

    def _get_fitness_individual(self, individual, mapping, coupling_dict, rcb, use_runtime_info, total_couplings,
                                total_time):
        """ Function to evaluate the fitness of an individual. Needed for the genetic algorithm
        """

        function_order = []
        for idx in individual:
            function_order.append(mapping[idx])
        feedback, time = self.get_feedback_info(function_order, coupling_dict, use_runtime_info)

        f = rcb * (feedback / float(total_couplings)) + (1 - rcb) * (time / float(total_time))

        if rcb == 1:
            return f, time
        elif rcb == 0:
            return f, feedback
        else:
            return f,

    def get_feedback_info(self, function_order, coupling_dict=None, use_runtime_info=False):
        """Function to determine the number of feedback loops and a runtime estimation for a given function order

        :param function_order: function order of the nodes
        :type function_order: list
        :param coupling_dict: coupling dictionary indicating the input/output relations between the nodes
        :type coupling_dict: dict
        :param use_runtime_info: option to take the runtime of the functions into account, else the default is set to 1
        :type use_runtime_info: bool
        :return number of feedback loops
        :rtype int
        """

        # Input assertions
        if use_runtime_info:
            for node in function_order:
                assert 'performance_info' in self.nodes[node], 'Performance info missing for node {}'.format(node)
                assert 'run_time' in self.nodes[node]['performance_info'], 'Run time missing for node {}'.format(node)

        # Get coupling dictionary
        if not coupling_dict:
            coupling_dict = self.get_coupling_dictionary()

        # Determine number of feedback loops
        n_feedback_loops = 0
        for idx1, function1 in enumerate(function_order):
            for idx2, function2 in enumerate(function_order[idx1 + 1:]):
                if function2 in coupling_dict[function1]:
                    n_feedback_loops += coupling_dict[function1][function2]

        # Calculate runtime of the sequence
        run_time = self.get_runtime_sequence(function_order, coupling_dict=coupling_dict,
                                             use_runtime_info=use_runtime_info)

        return n_feedback_loops, run_time

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          XML-HANDLING METHODS                                                    #
    # ---------------------------------------------------------------------------------------------------------------- #
    def add_variable_default_values(self, xml_file):
        """Method to add the default value of the variables based on a reference XML file containing those values.

        :param xml_file: path (absolute or local) to the XML file containing the default values
        :type xml_file: file
        :return: enriched graph with default values of the variables stored as attributes
        :rtype: self
        """
        # Check the input XML file and parse it
        assert os.path.isfile(xml_file), "Could not find the XML file {}".format(xml_file)
        _parse_check([[xml_file]])
        xml_file = etree.parse(xml_file)

        # Get all variables in the graph
        var_nodes = self.find_all_nodes(category='variable')

        # For each variable, check whether it exists in the reference XML file and add the value.
        for var_node in var_nodes:
            # Get the element in the xml_file
            els = xml_file.xpath(var_node)
            if els:
                el = els[0]
                default_value = el.text
                if default_value:
                    self.nodes[var_node]['default_value'] = default_value
        return


class RepositoryConnectivityGraph(DataGraph):

    PATHS_LIMIT = 1e4    # limit check for select_function_combination_from method
    WARNING_LIMIT = 3e6  # limit for _get_path_combinations method

    def __init__(self, *args, **kwargs):
        super(RepositoryConnectivityGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _create_cmdows_problem_def(self):

        # Create problemDefinition
        cmdows_problem_definition = Element('problemDefinition')

        return cmdows_problem_definition

    # noinspection PyPep8Naming
    def create_mathematical_problem(self, n_disciplines, coupling_density=None, n_clusters=1, cluster_strength=1,
                                    **kwargs):
        """Function to get a mathematical problem according to the variable complexity problem as described in:
        Zhang D., Song B., Wang P. and He Y. 'Performance Evaluation of MDO Architectures within a Variable
        Complexity Problem', Mathematical Problems in Engineering, 2017.

        :param n_disciplines: Number of disciplines
        :type n_disciplines: int
        :param coupling_density: percentage of couplings, 0 no couplings, 1 all possible couplings
        :type coupling_density: float
        :param n_clusters: Number of clusters within the mathematical problem
        :type n_clusters: int
        :param cluster_strength: Indicates the strength of the clustering. 0 means that a completely random problem is
        generated with no bias towards clustering at all. 1 means a complete bias towards clustering, so all couplings
        are placed within the clusters. If more couplings are required then the amount available within the clusters,
        couplings outside the clusters are made as well.
        :type cluster_strength: float
        :return enriched rcg with the mathematical problem
        :return dictionary containing the properties of the mathematical problem
        """

        # Input assertions
        assert 'B' not in kwargs if coupling_density else 'B' in kwargs, 'Either the coupling density or the ' \
                                                                         'B-matrix must be given'
        assert 1 <= n_clusters <= n_disciplines, 'Number of clusters must be in the range [1, n_disciplines]'
        assert 0 <= cluster_strength <= 1, 'Cluster strength must be a float in the range [0, 1]'
        if 'B' in kwargs:
            logger.warning('B-matrix is given to create the mathematical problem, so cluster requirements are ignored')

        mathematical_problem = dict()
        mathematical_problem['n_disciplines'] = n_disciplines

        # Create values for the random elements
        # Number of global design variables
        global_var_range = [1, 5] if 'global_var_range' not in kwargs else kwargs['global_var_range']
        n_global_var = random.randint(global_var_range[0], global_var_range[1]) if 'n_global_var' not in kwargs else \
            kwargs['n_global_var']
        mathematical_problem['n_global_var'] = n_global_var

        # Number of local design variables per discipline
        local_var_range = [1, 5] if 'local_var_range' not in kwargs else kwargs['local_var_range']
        n_local_var = [random.randint(local_var_range[0], local_var_range[1]) for _ in range(n_disciplines)] if \
            'n_local_var' not in kwargs else kwargs['n_local_var']
        mathematical_problem['n_local_var'] = n_local_var

        # Number of coupling variables per discipline
        coupling_var_range = [1, 5] if 'coupling_var_range' not in kwargs else kwargs['coupling_var_range']
        n_coupling_var = [random.randint(coupling_var_range[0], coupling_var_range[1]) for _ in range(n_disciplines)] \
            if 'n_coupling_var' not in kwargs else kwargs['n_coupling_var']
        mathematical_problem['n_coupling_var'] = n_coupling_var

        # Number of local constraints
        local_constraints_range = [1, 5] if 'local_constraints_range' not in kwargs else \
            kwargs['local_constraints_range']
        n_local_constraints = [random.randint(local_constraints_range[0], local_constraints_range[1]) for _ in
                               range(n_disciplines)] if 'n_local_constraints' not in kwargs else \
            kwargs['n_local_constraints']
        mathematical_problem['n_local_constraints'] = n_local_constraints

        # Number of global constraints
        global_constraints_range = [1, 5] if 'global_constraints_range' not in kwargs else \
            kwargs['global_constraints_range']
        n_global_constraints = random.randint(global_constraints_range[0], global_constraints_range[1]) if \
            'n_global_constraints' not in kwargs else kwargs['n_global_constraints']
        mathematical_problem['n_global_constraints'] = n_global_constraints

        # Create B-matrix: relation between the coupling variables
        if 'B' not in kwargs:
            while True:
                # Initiate matrix
                B = np.zeros((sum(n_coupling_var), sum(n_coupling_var)))

                # Calculate the number of couplings based on the coupling density
                n_couplings = int(np.ceil(((sum(n_coupling_var)*n_disciplines) - sum(n_coupling_var)) *
                                          coupling_density))

                # Determine which disciplines are in which cluster
                disciplines = list(range(n_disciplines))
                random.shuffle(disciplines)
                division = n_disciplines / float(n_clusters)
                clusters = [disciplines[int(round(division * i)):int(round(division * (i + 1)))] for i in
                            range(n_clusters)]

                # Get two lists with all possible couplings between variables and disciplines. One lists contains the
                # couplings within the clusters and one contains the couplings outside the clusters
                cluster_couplings, remaining_couplings = [], []
                for discipline1 in range(n_disciplines):
                    for discipline2 in range(n_disciplines):
                        # An output variable of a discipline cannot be an input to the same discipline
                        if discipline1 == discipline2:
                            continue
                        for coupling_var in range(n_coupling_var[discipline1]):
                            for cluster in clusters:
                                if discipline1 in cluster and discipline2 in cluster:
                                    cluster_couplings.append([discipline1, coupling_var, discipline2])
                                    break
                            if [discipline1, coupling_var, discipline2] not in cluster_couplings:
                                remaining_couplings.append([discipline1, coupling_var, discipline2])

                # Determine how many couplings need to be chosen from the ones inside the clusters and how many
                # couplings need to be chosen from the ones outside the clusters
                coupling_division = [random.uniform(0, 1) for _ in range(n_couplings)]
                percentage_cluster_couplings = len(cluster_couplings) / float(len(cluster_couplings) +
                                                                              len(remaining_couplings))
                division_criteria = percentage_cluster_couplings + ((1-percentage_cluster_couplings) *
                                                                    float(cluster_strength))

                # If the number is below the division criteria, the coupling will be part of the cluster, otherwise it
                # will be outside the cluster
                n_couplings_in_cluster = len([coupling for coupling in coupling_division if coupling <
                                              division_criteria])
                n_couplings_outside_cluster = len(coupling_division) - n_couplings_in_cluster

                # Check if there are too many couplings within or outside the clusters and change accordingly
                if n_couplings_in_cluster > len(cluster_couplings):
                    n_couplings_outside_cluster += n_couplings_in_cluster - len(cluster_couplings)
                    n_couplings_in_cluster = len(cluster_couplings)
                elif n_couplings_outside_cluster > len(remaining_couplings):
                    n_couplings_in_cluster += n_couplings_outside_cluster - len(remaining_couplings)
                    n_couplings_outside_cluster = len(remaining_couplings)

                # Choose random coupligns from all possible couplings
                couplings = random.sample(cluster_couplings, n_couplings_in_cluster) + \
                    random.sample(remaining_couplings, n_couplings_outside_cluster)

                # Fill the B-matrix with the chosen couplings
                for coupling in couplings:
                    discipline1, coupling_var, discipline2 = coupling
                    for variable in range(n_coupling_var[discipline2]):
                        B[sum(n_coupling_var[:discipline2]) + variable][
                            sum(n_coupling_var[:discipline1]) + coupling_var] = \
                            random.choice(list(range(-5, 0)) + list(range(1, 6)))  # Zero is not allowed

                # To ensure convergence the B-matrix must be diagonally dominant
                B_diag = np.sum(np.abs(B), axis=1)
                B_diag = [entry + random.randint(1, 10) for entry in B_diag]
                i, j = np.indices(B.shape)
                B[i == j] = B_diag

                # Test if the matrix is singular by calculating its rank
                rank = np.linalg.matrix_rank(B)
                singular = True if rank < min(B.shape) else False
                if not singular:
                    break
                print('B matrix is singular, new matrix is generated...')

        else:
            # Test if B matrix is singular by calculating its rank
            B = kwargs['B']
            rank = np.linalg.matrix_rank(B)
            singular = True if rank < min(B.shape) else False
            assert not singular, 'B matrix is singular'

        mathematical_problem['B-matrix'] = B

        # Create C-matrix: relation between global design variables and coupling variables
        C = np.array([[float(random.randint(-5, 5)) for _ in range(n_global_var)] for _ in
                      range(sum(n_coupling_var))]) if 'C' not in kwargs else kwargs['C']
        mathematical_problem['C-matrix'] = C

        # Create D-matrix: relation between local design variables and coupling variables
        if 'D' not in kwargs:
            D = np.zeros((sum(n_coupling_var), sum(n_local_var)))
            for discipline in range(n_disciplines):
                for local_var in range(n_local_var[discipline]):
                    for coupling_var in range(n_coupling_var[discipline]):
                        D[sum(n_coupling_var[:discipline]) + coupling_var][sum(n_local_var[:discipline]) + local_var] =\
                            random.choice(list(range(-5, 0))+list(range(1, 6)))  # Zero is not allowed
        else:
            D = kwargs['D']
        mathematical_problem['D-matrix'] = D

        # Create E-matrix: relation between global design variables and local constraints
        E = np.array([[float(random.randint(-5, 5)) for _ in range(n_global_var)] for _ in
                      range(sum(n_local_constraints))]) if 'E' not in kwargs else kwargs['E']
        mathematical_problem['E-matrix'] = E

        # Create F-matrix: relation between local design variables and local constraints
        if 'F' not in kwargs:
            F = np.zeros((sum(n_local_constraints), sum(n_local_var)))
            for discipline in range(n_disciplines):
                for local_var in range(n_local_var[discipline]):
                    for local_constraint in range(n_local_constraints[discipline]):
                        F[sum(n_local_constraints[:discipline]) +
                          local_constraint][sum(n_local_var[:discipline]) + local_var] = random.randint(-5, 5)
        else:
            F = kwargs['F']
        mathematical_problem['F-matrix'] = F

        # Create G-matrix: relation between coupling variables and local constraints
        if 'G' not in kwargs:
            G = np.zeros((sum(n_local_constraints), sum(n_coupling_var)))
            for discipline in range(n_disciplines):
                for coupling_var in range(n_coupling_var[discipline]):
                    for local_constraint in range(n_local_constraints[discipline]):
                        G[sum(n_local_constraints[:discipline]) +
                          local_constraint][sum(n_coupling_var[:discipline]) + coupling_var] = \
                            random.choice(list(range(-5, 0)) + list(range(1, 6)))  # Zero is not allowed
        else:
            G = kwargs['G']
        mathematical_problem['G-matrix'] = G

        # Create r-matrix: positive scalars used to calculate local constraint values
        r = [float(random.randint(1, 5)) for _ in range(sum(n_local_constraints))] if 'r' not in kwargs else kwargs['r']
        mathematical_problem['r-matrix'] = r

        # Create H-matrix: relation between global design variables and global constraints
        H = np.array([[float(random.randint(-5, 5)) for _ in range(n_global_var)] for _ in
                      range(n_global_constraints)]) if 'H' not in kwargs else kwargs['H']
        mathematical_problem['H-matrix'] = H

        # Create I-matrix: relation between local design variables and global constraints
        I = np.array([[float(random.randint(-5, 5)) for _ in range(sum(n_local_var))] for _ in
                      range(n_global_constraints)]) if 'I' not in kwargs else kwargs['I']
        mathematical_problem['I-matrix'] = I

        # Create J-matrix: relation between coupling variables and global constraints
        J = np.array([[float(random.randint(-5, 5)) for _ in range(sum(n_coupling_var))] for _ in
                      range(n_global_constraints)]) if 'J' not in kwargs else kwargs['J']
        mathematical_problem['J-matrix'] = J

        # Create s-matrix: positive scalars used to calculate global constraint values
        s = [float(random.randint(1, 5)) for _ in range(n_global_constraints)] if 's' not in kwargs else kwargs['s']
        mathematical_problem['s-matrix'] = s

        # Check whether problem is well-formulated
        # Check whether all coupling variables are defined
        for coupling_var in range(sum(n_coupling_var)):
            assert B[coupling_var][coupling_var] != 0, 'Diagonal of B cannot be zero'

        # Check whether output variable is not also an input variable to the same discipline
        for discipline in range(n_disciplines):
            for coupling_var in range(n_coupling_var[discipline]):
                values = B[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                           sum(n_coupling_var[:discipline]) + coupling_var]
                for index, v in enumerate(values):
                    if index != coupling_var:
                        assert v == 0, 'Output variable y{0}_{1} cannot be an input to discipline ' \
                                       'D{0}'.format(discipline + 1, coupling_var + 1)

        # Check whether local variables are not used by other disciplines
        for local_var_disc in range(n_disciplines):
            for local_var in range(n_local_var[local_var_disc]):
                for discipline in range(n_disciplines):
                    if local_var_disc != discipline:
                        values = D[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                                   sum(n_local_var[:local_var_disc]) + local_var]
                        assert all(
                            v == 0 for v in values), 'Local variable x{0}_{1} cannot be an input to discipline ' \
                                                     'D{2}, only to discipline D{0}'.format(local_var_disc + 1,
                                                                                            local_var + 1,
                                                                                            discipline + 1)
                for local_con_disc in range(n_disciplines):
                    for local_constraint in range(n_local_constraints[local_con_disc]):
                        if local_var_disc != local_con_disc:
                            assert F[sum(n_local_constraints[:local_con_disc]) + local_constraint,
                                     sum(n_local_var[:local_var_disc]) + local_var] == 0, \
                                'Local variable x{0}_{1} cannot be an input to local constraint ' \
                                'g{2}_{3}'.format(local_var_disc + 1, local_var + 1, local_con_disc + 1,
                                                  local_constraint + 1)

        # Check whether coupling variables are not used for different local constraints
        for coupling_var_disc in range(n_disciplines):
            for coupling_var in range(n_coupling_var[coupling_var_disc]):
                for local_con_disc in range(n_disciplines):
                    for local_constraint in range(n_local_constraints[local_con_disc]):
                        if coupling_var_disc != local_con_disc:
                            assert G[sum(n_local_constraints[:local_con_disc]) + local_constraint,
                                     sum(n_coupling_var[:coupling_var_disc]) + coupling_var] == 0, \
                                'Coupling variable y{0}_{1} cannot be an input to local constraint ' \
                                'g{2}_{3}'.format(coupling_var_disc + 1, coupling_var + 1, local_con_disc + 1,
                                                  local_constraint + 1)

        # All function nodes are defined
        for discipline in range(n_disciplines):  # Disciplines
            self.add_fnode('D{0}'.format(discipline + 1))
            runtime_range = kwargs['runtime_range'] if 'runtime_range' in kwargs else [1, 5]
            if runtime_range:
                run_time_node = random.randint(runtime_range[0], runtime_range[1])
                self.nodes['D{0}'.format(discipline + 1)]['performance_info'] = {'run_time': run_time_node}
                self.nodes['D{0}'.format(discipline + 1)]['sleep_time'] = run_time_node
            for local_constraint in range(n_local_constraints[discipline]):  # Local constraints
                self.add_fnode('G{0}_{1}'.format(discipline+1, local_constraint+1))
                self.nodes['G{0}_{1}'.format(discipline+1, local_constraint+1)]['performance_info'] = {'run_time': 0}
                self.nodes['G{0}_{1}'.format(discipline+1, local_constraint+1)]['sleep_time'] = 0
        self.add_fnode('F')  # Objective
        self.nodes['F']['performance_info'] = {'run_time': 0}
        self.nodes['F']['sleep_time'] = 0
        for constraint in range(n_global_constraints):  # Global constraints
            self.add_fnode('G0{0}'.format(constraint + 1))
            self.nodes['G0{0}'.format(constraint + 1)]['performance_info'] = {'run_time': 0}
            self.nodes['G0{0}'.format(constraint + 1)]['sleep_time'] = 0

        # All variable nodes are defined
        for global_var in range(n_global_var):  # Global design variables
            self.add_vnode('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                           label='x0{0}'.format(global_var + 1))
        for constraint in range(n_global_constraints):  # Global constraints
            self.add_vnode('/data_schema/global_constraints/g0{0}'.format(constraint + 1),
                           label='g0{0}'.format(constraint + 1))
        self.add_vnode('/data_schema/objective/f')
        for discipline in range(n_disciplines):
            for local_var in range(n_local_var[discipline]):  # Local design variables
                self.add_vnode('/data_schema/local_design_variables/x{0}_{1}'.format(discipline + 1, local_var + 1),
                               label='x{0}_{1}'.format(discipline + 1, local_var + 1))
            for coupling_var in range(n_coupling_var[discipline]):  # Coupling variables
                self.add_vnode('/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, coupling_var + 1),
                              label='y{0}_{1}'.format(discipline + 1, coupling_var + 1))
            for local_constraint in range(n_local_constraints[discipline]):  # Local constraints
                self.add_vnode('/data_schema/local_constraints/g{0}_{1}'.format(discipline+1, local_constraint+1),
                              label='g{0}_{1}'.format(discipline+1, local_constraint+1))

        # Edges between global variables and function nodes are defined
        for global_var in range(n_global_var):
            for discipline in range(n_disciplines):
                values = C[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]), global_var]
                if not all(v == 0 for v in values):
                    self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                                  'D{0}'.format(discipline + 1))
                for local_constraint in range(n_local_constraints[discipline]):
                    self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                                  'G{0}_{1}'.format(discipline + 1, local_constraint + 1))
            self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1), 'F')
            for constraint in range(n_global_constraints):
                self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                              'G0{0}'.format(constraint + 1))

        # Edges between local variables and function nodes are defined
        for local_var_disc in range(n_disciplines):
            for local_var in range(n_local_var[local_var_disc]):
                for discipline in range(n_disciplines):
                    values = D[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                               sum(n_local_var[:local_var_disc]) + local_var]
                    if not all(v == 0 for v in values):
                        self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1,
                                      local_var + 1), 'D{0}'.format(local_var_disc + 1))
                for local_constraint in range(n_local_constraints[local_var_disc]):
                    self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1,
                                                                                        local_var + 1),
                                  'G{0}_{1}'.format(local_var_disc + 1, local_constraint + 1))
                self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1, local_var + 1),
                              'F')
                for constraint in range(n_global_constraints):
                    self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1,
                                  local_var + 1), 'G0{0}'.format(constraint + 1))

        # Edges between coupling variables and function nodes are defined
        for coupling_var_disc in range(n_disciplines):
            for coupling_var in range(n_coupling_var[coupling_var_disc]):
                for discipline in range(n_disciplines):
                    values = B[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                               sum(n_coupling_var[:coupling_var_disc]) + coupling_var]
                    if not discipline == coupling_var_disc and not all(v == 0 for v in values):
                        self.add_edge(
                            '/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1, coupling_var + 1),
                            'D{0}'.format(discipline + 1))
                    for local_constraint in range(n_local_constraints[discipline]):
                        value = G[sum(n_local_constraints[:discipline]) + local_constraint,
                                  sum(n_coupling_var[:coupling_var_disc]) + coupling_var]
                        if value != 0:
                            self.add_edge('/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1,
                                                                                            coupling_var + 1),
                                          'G{0}_{1}'.format(discipline + 1, local_constraint + 1))
                self.add_edge('/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1, coupling_var +
                                                                                1), 'F')
                for constraint in range(n_global_constraints):
                    if J[constraint][sum(n_coupling_var[:coupling_var_disc]) + coupling_var] != 0:
                        self.add_edge(
                            '/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1, coupling_var + 1),
                            'G0{0}'.format(constraint + 1))

        # Edges between function nodes and coupling variables are defined
        for discipline in range(n_disciplines):
            for coupling_var in range(n_coupling_var[discipline]):  # Disciplines
                self.add_edge('D{0}'.format(discipline + 1),
                              '/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, coupling_var + 1))
            for local_constraint in range(n_local_constraints[discipline]):  # Local constraints
                self.add_edge('G{0}_{1}'.format(discipline + 1, local_constraint + 1),
                              '/data_schema/local_constraints/g{0}_{1}'.format(discipline + 1, local_constraint + 1))
        self.add_edge('F', '/data_schema/objective/f')  # Objective
        for constraint in range(n_global_constraints):  # Global constraints
            self.add_edge('G0{0}'.format(constraint + 1), '/data_schema/global_constraints/g0{0}'.format(constraint +
                                                                                                         1))

        # Add equations
        self.add_equation_labels(self.function_nodes, labeling_method='node_id')

        # Add discipline analysis equations
        for discipline in range(n_disciplines):
            for output_var in range(n_coupling_var[discipline]):
                equation = ""
                for global_var in range(n_global_var):
                    if C[sum(n_coupling_var[:discipline]) + output_var][global_var] != 0:
                        equation += '-{0}*x0{1}'.format(C[sum(n_coupling_var[:discipline]) + output_var][global_var],
                                                        global_var + 1)
                for local_var_disc in range(n_disciplines):
                    for local_var in range(n_local_var[local_var_disc]):
                        if D[sum(n_coupling_var[:discipline]) + output_var][
                                    sum(n_local_var[:local_var_disc]) + local_var] != 0:
                            equation += '-{0}*x{1}_{2}'.format(D[sum(n_coupling_var[:discipline]) + output_var][
                                                                sum(n_local_var[:local_var_disc]) + local_var],
                                                               local_var_disc + 1, local_var + 1)
                for coupling_var_disc in range(n_disciplines):
                    for coupling_var in range(n_coupling_var[coupling_var_disc]):
                        if B[sum(n_coupling_var[:discipline]) + output_var][sum(n_coupling_var[:coupling_var_disc]) +
                           coupling_var] != 0 and (discipline, output_var) != (coupling_var_disc, coupling_var):
                            equation += '-{0}*y{1}_{2}'.format(B[sum(n_coupling_var[:discipline]) + output_var][sum(
                                n_coupling_var[:coupling_var_disc]) + coupling_var], coupling_var_disc + 1,
                                                              coupling_var + 1)
                if B[sum(n_coupling_var[:discipline]) + output_var][sum(n_coupling_var[:discipline]) + output_var] != 1:
                    equation = '({0})/{1}'.format(equation, B[sum(n_coupling_var[:discipline]) + output_var][
                        sum(n_coupling_var[:discipline]) + output_var])
                self.add_equation(['D{0}'.format(discipline + 1),
                                  '/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, output_var + 1)],
                                  equation, 'Python')
                self.add_equation(['D{0}'.format(discipline + 1),
                                  '/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, output_var + 1)],
                                  equation, 'LaTeX')

        # Add objective function equation
        objective = ""
        for global_var in range(n_global_var):
            objective += '+x0{0}'.format(global_var + 1)
        for discipline in range(n_disciplines):
            for local_var in range(n_local_var[discipline]):
                objective += '+x{0}_{1}'.format(discipline + 1, local_var + 1)
        for discipline in range(n_disciplines):
            for coupling_var in range(n_coupling_var[discipline]):
                objective += '+y{0}_{1}'.format(discipline + 1, coupling_var + 1)
        n_variables = n_global_var + sum(n_local_var) + sum(n_coupling_var)
        self.add_equation('F', '(({0})/{1})**3'.format(objective, n_variables), 'Python')
        self.add_equation('F', '(({0})/{1})^3'.format(objective, n_variables), 'LaTeX')

        # Add global constraint function equations
        for constraint in range(n_global_constraints):
            constraint_eq = ""
            for global_var in range(n_global_var):
                constraint_eq += '+x0{0}*x0{0}'.format(global_var + 1)
                if H[constraint][global_var] != 0:
                    constraint_eq += '+{0}*x0{1}'.format(H[constraint][global_var], global_var + 1)
            for discipline in range(n_disciplines):
                for local_var in range(n_local_var[discipline]):
                    constraint_eq += '+x{0}_{1}*x{0}_{1}'.format(discipline + 1, local_var + 1)
                    if I[constraint][sum(n_local_var[:discipline]) + local_var] != 0:
                        constraint_eq += '+{0}*x{1}_{2}'.format(I[constraint][sum(n_local_var[:discipline]) +
                                                                              local_var], discipline + 1, local_var + 1)
            for discipline in range(n_disciplines):
                for coupling_var in range(n_coupling_var[discipline]):
                    if J[constraint][sum(n_coupling_var[:discipline]) + coupling_var] != 0:
                        constraint_eq += '+{0}*y{1}_{2}'.format(
                            J[constraint][sum(n_coupling_var[:discipline]) + coupling_var], discipline + 1,
                            coupling_var + 1)
            constraint_eq += '-{0}'.format(s[constraint])
            self.add_equation('G0{0}'.format(constraint + 1), constraint_eq, 'Python')
            self.add_equation('G0{0}'.format(constraint + 1), constraint_eq, 'LaTeX')

        # Add local constraint function equations
        for local_con_disc in range(n_disciplines):
            for local_constraint in range(n_local_constraints[local_con_disc]):
                constraint_eq = ""
                for global_var in range(n_global_var):
                    constraint_eq += '+x0{0}*x0{0}'.format(global_var + 1)
                    if E[sum(n_local_constraints[:local_con_disc]) + local_constraint, global_var] != 0:
                        constraint_eq += '+{0}*x0{1}'.format(E[sum(n_local_constraints[:local_con_disc]) +
                                                               local_constraint][global_var], global_var + 1)
                for local_var in range(n_local_var[local_con_disc]):
                    constraint_eq += '+x{0}_{1}*x{0}_{1}'.format(local_con_disc + 1, local_var + 1)
                    if F[sum(n_local_constraints[:local_con_disc]) + local_constraint][
                                sum(n_local_var[:local_con_disc]) + local_var] != 0:
                        constraint_eq += '+{0}*x{1}_{2}'.format(
                            F[sum(n_local_constraints[:local_con_disc]) + local_constraint][
                                sum(n_local_var[:local_con_disc]) + local_var], local_con_disc + 1, local_var + 1)
                for discipline in range(n_disciplines):
                    for coupling_var in range(n_coupling_var[discipline]):
                        if G[sum(n_local_constraints[:local_con_disc]) + local_constraint][
                                    sum(n_coupling_var[:discipline]) + coupling_var] != 0:
                            constraint_eq += '+{0}*y{1}_{2}'.format(G[sum(n_local_constraints[:local_con_disc]) +
                                                                      local_constraint][sum(n_coupling_var[:discipline])
                                                                                        + coupling_var], discipline + 1,
                                                                    coupling_var + 1)
                constraint_eq += '-{}'.format(r[sum(n_local_constraints[:local_con_disc]) + local_constraint])
                self.add_equation('G{0}_{1}'.format(local_con_disc + 1, local_constraint + 1), constraint_eq, 'Python')
                self.add_equation('G{0}_{1}'.format(local_con_disc + 1, local_constraint + 1), constraint_eq, 'LaTeX')

        # Get function order
        function_order = []
        for discipline in range(n_disciplines):
            function_order += ['D{0}'.format(discipline + 1)]
        for discipline in range(n_disciplines):
            for local_constraint in range(n_local_constraints[discipline]):
                function_order += ['G{0}_{1}'.format(discipline + 1, local_constraint + 1)]
        for constraint in range(n_global_constraints):
            function_order += ['G0{0}'.format(constraint + 1)]
        function_order += ['F']
        mathematical_problem['function_order'] = function_order

        return mathematical_problem

    # -----------------------------------------------------------------------------------------------------------------#
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # -----------------------------------------------------------------------------------------------------------------#

    def get_function_paths_by_objective(self, *args, **kwargs):
        """This function takes an arbitrary amount of objective nodes as graph sinks and returns all path combinations
        of tools.

        :param args: arbitrary amount of objective nodes
        :type args: list, str
        :param kwargs: filter options to limit possible path combinations
        :type kwargs: bool, str
        :return: all possible FPG path combinations for the provided objective nodes

        If no arguments are given, user is prompted to select objectives from the graph.

        .. hint:: The tool combinations are found using the function itertools.product() and can lead to significant
            computation times for large graphs. If this is the case, the user is prompted whether to continue or not.

        A variety of filters can be applied to the search of possible tools combinations, some of which reduce the
        computation time.

        .. note:: kwargs:

            * obj_vars_covered - ensures that all objective variables are used in tool configurations
            * ignore_funcs - ignores functions for the config
            * source - source node; if provided, must be in config
        """

        # TODO: Add filters
        # Filters:
        # include_functions - returned path combinations must include the indicated functions
        # exclude_functions - returned path combinations must exclude the indicated functions
        # min_funcs - only returns paths that have a minimum amount if functions
        # max_funcs - only returns paths that have a maximum amount of functions
        # obj_vars_covered - only returns paths where ALL objective variables are covered

        # make copy of self
        graph = copy.deepcopy(self)

        # get and check keyword arguments
        obj_vars_covered = kwargs.get('objective_variables_covered', False)  # TODO: Implement this option
        assert isinstance(obj_vars_covered, bool)

        ignore_funcs = None
        if "ignore_funcs" in kwargs:
            ignore_funcs = kwargs["ignore_funcs"]
            for func in ignore_funcs:
                assert func in self, "Function node {} must be present in graph.".format(func)

        # source = None
        # if "source" in kwargs:
        #    source = kwargs["source"]
        #    assert graph.node_is_function(source), "Source node must be a function."

        min_funcs = None
        if "min_funcs" in kwargs:
            min_funcs = kwargs["min_funcs"]
            assert isinstance(min_funcs, int)

        max_funcs = float("inf")
        if "max_funcs" in kwargs:
            max_funcs = kwargs["max_funcs"]
            assert isinstance(max_funcs, int)

        # get all function nodes in graph
        # func_nodes = graph.get_function_nodes()

        # [step 1] check if function nodes provided
        if args:
            objs = list(args)
            for arg in objs:
                assert graph.node_is_function(arg), "Provided Objective must be function."

        else:  # if not provided, ask user to select
            objs = graph.select_objectives_from_graph()

        # intermediate check that OBJ function node given
        assert objs, "No valid Objective Functions provided."
        logger.info('Function configurations are considered for objective(s): [{}]'.format(
            ', '.join(str(x) for x in objs)))

        # [Step 2]: Get OBJ function variables in graph
        obj_variables = []
        for objFunc in objs:
            for u, v in graph.in_edges(objFunc):
                obj_variables.append(u)

        # [Step 3]: Get function graph (remove all variable nodes and replace them with corresponding edges)
        if obj_vars_covered:
            # if obj_vars_covered, objective vars will be present in paths; easy to check their presence
            function_graph = graph.get_function_graph(keep_objective_variables=True)
        else:
            function_graph = graph.get_function_graph()

        # [Step 4]: get all (simple) paths to sinks
        all_simple_paths = set()  # making sure that no duplicate paths in list
        for sink in objs:
            anc_nodes = nx.ancestors(function_graph, sink)
            for anc in anc_nodes:
                if function_graph.node_is_function(anc):  # do not take objVars into account

                    # add every path to sink as frozenset
                    for path in nx.all_simple_paths(function_graph, anc, sink):  # TODO: Test for multiple sinks!
                        all_simple_paths.add(frozenset(path))

        # [Step 5]: Apply (some) filters
        # TODO: Apply some filters here

        # [Step 6]: group paths according into subsets
        path_subsets = self._group_elements_by_subset(*all_simple_paths)

        # [Step 7]: Get all combinations between all feedback tool combinations
        subsets_list = [subset for _, subset in iteritems(path_subsets)]

        # remove all paths that have ignore-functions
        if ignore_funcs:
            for subset in subsets_list:
                remove = []
                for path in subset:
                    if not ignore_funcs.isdisjoint(path):
                        remove.append(path)
                for p in remove:
                    subset.remove(p)

        all_fpg_paths = function_graph.get_path_combinations(*subsets_list, min_funcs=min_funcs, max_funcs=max_funcs)

        return all_fpg_paths

    def get_path_combinations(self, *args, **kwargs):
        """This function takes lists of subsets and generates all possible combinations between them.

        :param args: lists of subsets that will be used to find configurations
        :type args: list
        :param kwargs: see optional arguments
        :type kwargs: int
        :return: set of all unique path combinations

        This is done by using the itertools.product() function. If the amount of expected evaluations exceeds a pre-set
        minimum, the user will be asked if to continue or not; because the process can take a long time and use up many
        resources.

        .. note:: Optional arguments:

            * min_func: minimum amount of functions in each configuration
            * max_func: maximum amount of functions in each configuration
        """

        # get list of subsets
        subsets = list(args)

        # kwargs check
        # min_funcs = None
        # if "min_funcs" in kwargs:
        #     min_funcs = kwargs["min_funcs"]
        #     assert isinstance(min_funcs, int)

        max_funcs = kwargs.get('max_funcs', float("inf"))

        # append empty string to each list (to get ALL combinations; check itertools.product()) and count evaluations
        count = 1
        for subset in subsets:
            subset.append('')
            count *= len(subset)
        count -= 1

        # If many combinations are evaluated, warn user and ask if to continue
        if count > self.WARNING_LIMIT:
            logger.warning('Only ' + str(self.WARNING_LIMIT) + ' tool combinations can be evaluated with the current ' +
                           ' settings. However, ' + str(count) + ' evaluations are now selected. You can decrease ' +
                           'this number by applying filters. You could also increase the WARNING_LIMIT but be aware ' +
                           'that the process can take a considerable amount of time and resources then.')
            return list()

        # get all tool combinations using subsets
        all_path_combinations = set()

        for comb in itertools.product(*subsets):
            # combine separate lists into one for each combo
            # clean_comb = frozenset(itertools.chain.from_iterable(comb))
            clean_comb = frozenset().union(*comb)
            if len(clean_comb) > max_funcs or len(clean_comb) > max_funcs:
                continue
            # add to list if combo is not empty and does not yet exist in list
            if clean_comb and clean_comb not in all_path_combinations:
                all_path_combinations.add(clean_comb)

        return all_path_combinations

    def _get_feedback_paths(self, path, functions_only=True):
        # TODO: Add docstring

        # functions_only only passes on argument, not used in this function
        assert isinstance(functions_only, bool)

        # get feedback nodes if exist in path
        # empty strings in tpls are necessary for proper functioning
        feedback = self._get_feedback_nodes(path, functions_only=functions_only)

        # get path combinations in case feedback loops exist in path
        feedback_combis = []
        for prod in itertools.product([tuple(path)], *feedback):
            # remove all empty products
            removed_empty = (x for x in prod if x)  # remove empty strings
            # remove brackets created by product; create frozenset to make object immutable
            removed_brackets = frozenset(itertools.chain.from_iterable(removed_empty))

            # if combination is not empty and does not already exist in list, add to list
            if removed_brackets not in feedback_combis and removed_brackets:
                feedback_combis.append(removed_brackets)

        return feedback_combis

    def _get_feedback_nodes(self, main_path, functions_only=True):
        # TODO: Add docstring

        assert isinstance(functions_only, bool)
        feed_back = []  # contains feed_back nodes; each feed_back loop is in a separate list

        for main_path_idx, main_path_node in enumerate(main_path):
            search_loop = []
            start_index = -1

            if functions_only:
                if not self.node_is_function(main_path_node):
                    continue

            # iterate through edges recursively and add feed_back loops if they exist
            self._iter_out_edges(main_path_idx, main_path, main_path_node, start_index, search_loop, feed_back,
                                 functions_only)

        return feed_back

    def _iter_out_edges(self, main_path_idx, main_path, node, search_index, search_loop, feed_back,
                        functions_only=True):
        # TODO: Add docstring

        search_index += 1

        for edge in self.out_edges(node):
            if functions_only:
                if not self.node_is_function(edge[1]):
                    continue
            if edge[1] in search_loop:
                continue
            search_loop.insert(search_index, edge[1])
            if edge[1] in main_path and main_path.index(edge[1]) <= main_path_idx:
                feed_back.append(("", search_loop[:search_index]))
            elif edge[1] not in main_path:
                self._iter_out_edges(main_path_idx, main_path, edge[1], search_index, search_loop, feed_back,
                                     functions_only)

        return

    # noinspection PyMethodMayBeStatic
    def _group_elements_by_subset(self, *args):
        """This function takes arguments of type set/frozenset and groups them by subset.

        All elements that are subsets of another element are grouped together and returned in a dict with the longest
        superset as keywords.

        Example:
        >> list = [set([1]),set([1,2]),set([3]),set([0,1,2])]
        >> sub_sets = graph._group_elements_by_subset(*list)
        >> sub_sets
        >> {set([0,1,2]): [set([1]), set([1,2]),set([0,1,2])], set([3]):[set([3])]}

        :param args: arbitrary argument
        :type args: set, frozenset
        :return: dict with grouped arguments by longest subset in group
        :rtype: dict
        """

        for arg in args:
            assert isinstance(arg, (set, frozenset))
        set_list = list(args)

        sub_sets = {}
        skip = []
        for i, path in enumerate(set_list):
            if path in skip:
                continue

            set_found = False
            for comp in set_list[i + 1:]:
                if comp in skip:
                    continue

                if path == comp:
                    skip.append(comp)
                    continue

                if path.issubset(comp):
                    set_found = True

                    if comp not in sub_sets:
                        sub_sets[comp] = [comp]

                    if path in sub_sets:
                        sub_sets[comp] += sub_sets[path]
                        sub_sets.pop(path, None)
                    else:
                        sub_sets[comp].append(path)

                    skip.append(path)
                    break

                elif path.issuperset(comp):
                    set_found = True
                    skip.append(comp)

                    if path not in sub_sets:
                        sub_sets[path] = [path]
                    sub_sets[path].append(comp)

                    if comp in sub_sets:
                        sub_sets[path] += sub_sets[comp]
                        sub_sets.pop(comp, None)
                    continue

            if not set_found and path not in sub_sets:
                sub_sets[path] = []
                sub_sets[path].append(path)

        return sub_sets

    def select_function_combination_from(self, *args, **kwargs):
        """This function takes all provided workflow configurations and lists them according to their characteristics.

        :param args: workflow configurations
        :type args: list
        :param kwargs: see optional arguments
        :type kwargs: bool, str, int
        :return: sorted list of workflow configurations
        :rtype: list

        .. note:: Optional arguments:

            * 'print_combos' - option to print the combinations in a table
            * 'n_limit' - amount of combinations that will be printed in the table
            * 'sort_by' - characteristic to sort workflow configurations by
            * 'sort_by ascending' - option to sort workflow configurations by ascension
            * 'plot_combos' - option to plot the combinations in a graph

        The user can choose the workflow configuration from the list.

        A warning is given to the user if the amount of total configurations exceeds n = 1e4.
        Print limit is set to [0-20] by default.

        .. note:: sort_by must be one of ["couplings", "system_inputs", "edges", "nodes"].
        """

        # make sure arguments provided
        assert args, "At least one argument must be provided."

        # check number of arguments; prompt user to continue or not
        if len(args) > self.PATHS_LIMIT:
            msg = "More than {} workflow configurations provided; this could take a lot of time to analyze. Continue?"
            usr_sel = prompting.user_prompt_yes_no(message=msg)
            if not usr_sel:
                print("Combination selection cancelled.")
                return

        # check if all arguments are non-string iterables (list, tuple, set, frozenset,...)
        assert all([hasattr(arg, '__iter__') for arg in args]), "All arguments must be non-string iterables."

        # check KWARGS HERE
        print_combos = True
        if "print_combos" in kwargs:
            print_combos = kwargs["print_combos"]
            assert isinstance(print_combos, bool)

        # if no limit given, limit for displaying combos is set to 10
        n_limit = 21
        if "n_limit" in kwargs:
            n_limit = kwargs["n_limit"]
            assert isinstance(n_limit, int)
            assert n_limit > 0, "Argument must be positive."

        # if no sort_by argument given, it sorts combos by "holes"
        sort_by = "functions"
        if "sort_by" in kwargs:
            sort_by = kwargs["sort_by"]
            assert isinstance(sort_by, string_types)
            assert sort_by in self.GRAPH_PROPERTIES, "Argument must be in self.GRAPH_PROPERTIES."

        sort_by_ascending = False
        if "sort_by_ascending" in kwargs:
            sort_by_ascending = kwargs["sort_by_ascending"]
            assert isinstance(sort_by_ascending, bool)

        plot_combos = True
        if "plot_combos" in kwargs:
            plot_combos = kwargs["plot_combos"]
            # TODO: Add assert for type of plot, plot variables etc

        # ------------------------------------------------------------- #

        # iterate through arguments and analyze their graphs
        graph_analysis = {}
        for arg in args:
            # TODO: Implement an option to get graph data from a db instead of analyzing each subgraph (if available)
            # TODO: This saves time in large graphs!

            # initiate dict to save subgraph data to
            graph_analysis[arg] = {}

            # get subgraph in order to get fast analysis
            sub_graph = self.get_subgraph_by_function_nodes(*arg)

            # subgraph analysis
            graph_analysis[arg] = sub_graph.get_graph_properties()

        # sort configuration list
        combo_list = list(graph_analysis.items())
        sorted_combos = sorted(combo_list, key=lambda x: x[1][sort_by], reverse=not sort_by_ascending)

        if plot_combos:

            # plot
            plt_x, plt_y, annotes = [], [], []
            for k, v in iteritems(graph_analysis):
                plt_y.append(v["system_inputs"])
                plt_x.append(v["functions"])
                annotes.append(str(list(k)))

            # TODO: Automate the plotting of graphs (data, labels, etc)!
            fig, ax = plt.subplots()
            ax.scatter(plt_x, plt_y)
            af = AnnoteFinder(plt_x, plt_y, annotes, ax=ax)
            fig.canvas.mpl_connect('button_press_event', af)
            plt.xlabel('Tools')
            plt.ylabel('System Inputs')
            plt.show()

        # print configs
        if print_combos:
            print_list = []
            for combo, properties in sorted_combos:
                prop_list = [properties[prop] for prop in self.GRAPH_PROPERTIES]
                prop_list.append(list(combo))
                print_list.append(prop_list)

            hdr = self.GRAPH_PROPERTIES + ["Configuration"]
            msg = "The following tool configurations were found in the graph:"
            printing.print_in_table(print_list[:n_limit], message=msg, headers=hdr, print_indeces=True)

        # select combo for FPG
        # TODO: finish!
        # sel_mssg = "Please select a tool combination from the list above:"
        sel_list = [sorted_combo[0] for sorted_combo in sorted_combos[:n_limit]]
        # user_sel= PRO.user_prompt_select_options(*sel_list, message=sel_mssg, allow_multi=False, allow_empty=False)
        user_sel = [sel_list[0]]

        return next(iter(user_sel))

    def get_fpg_by_function_nodes(self, *args):
        """This function creates a new (FPG)-graph based on the selected function nodes.

        :param args: arbitrary amount of graph nodes
        :type args: list, str
        :return: new fpg graph
        :rtype: FundamentalProblemGraph
        """

        # TODO: Assert that nodes are function nodes

        # get subgraph from function nodes
        sub_graph = self.get_subgraph_by_function_nodes(*args)

        # create FPG from sub-graph
        fpg = nx.compose(FundamentalProblemGraph(), sub_graph)
        # TODO: Make sure that the name of the graph is changed!

        return fpg

    def get_fpg_based_on_sinks(self, list_of_sinks, name='FPG'):
        """Function to get the a Fundamental Problem Graph based on a list of sinks/required output variables.

        :param list_of_sinks: list with strings that specify the desired output
        :type list_of_sinks: list
        :param name: name of the graph to be generated
        :type name: str
        :return: Fundamental Problem Graph object
        :rtype: FundamentalProblemGraph
        """

        fpg = FundamentalProblemGraph(sinks=list_of_sinks, name=name)
        for sink in list_of_sinks:
            ancestors = nx.ancestors(self, sink)
            ancestors.add(sink)
            fpg_sink = self.subgraph(ancestors)
            fpg = nx.compose(fpg, fpg_sink)

        return fpg

    def get_fpg_based_on_list_functions(self, list_of_functions, name='FPG'):
        """Function to get a Fundamental Problem Graph based on a list of functions.

        :param list_of_functions: list with strings that specify the desired functions
        :type list_of_functions: list
        :param name: name of the graph to be generated
        :type name: str
        :return: Fundamental Problem Graph object
        :rtype: FundamentalProblemGraph
        """

        # make empty copy
        fpg = FundamentalProblemGraph(self, based_on_functions=list_of_functions, kb_path=self.graph['kb_path'],
                                      name=name)

        # build fpg by first determining the required nodes
        required_nodes = set(list_of_functions)
        for function in list_of_functions:
            for edge in fpg.out_edges(function):
                required_nodes.add(edge[1])
            for edge in fpg.in_edges(function):
                required_nodes.add(edge[0])

        for node, data in fpg.nodes(data=True):
            if node not in required_nodes:
                fpg.remove_node(node)

        return fpg

    def get_fpg_based_on_function_nodes(self, *args, **kwargs):
        """Function to get the Fundamental Problem Graph based on a list of (or a single) function.

        :param args: node names of functions of interest
        :type args: str
        :param kwargs: name: name of the graph to be generated
        :type kwargs: name: str
        :return: Fundamental Problem Graph object
        :rtype: FundamentalProblemGraph
        """

        # Input assertions
        name = kwargs.get('name', 'FPG')
        assert isinstance('name', string_types)
        list_of_functions = list(args)
        for function in list_of_functions:
            assert function in self.nodes, 'Defined function node ' + str(function) + ' does not exist in the graph.'

        # make empty copy
        fpg = FundamentalProblemGraph(self, based_on_functions=list_of_functions, name=name)

        # build FPG by first determining the required nodes
        required_nodes = set(list_of_functions)
        for function in list_of_functions:
            for edge in fpg.out_edges(function):
                required_nodes.add(edge[1])
            for edge in fpg.in_edges(function):
                required_nodes.add(edge[0])

        for node, data in fpg.nodes(data=True):
            if node not in required_nodes:
                fpg.remove_node(node)

        return fpg


class FundamentalProblemGraph(DataGraph):

    def __init__(self, *args, **kwargs):
        super(FundamentalProblemGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CHECKING METHODS                                                      #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _check_category_a(self):
        """Extended method to perform a category A check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(FundamentalProblemGraph, self)._check_category_a()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')
        var_nodes = self.find_all_nodes(category='variable')
        out_nodes = self.find_all_nodes(subcategory='all outputs')

        # Get information
        n_nodes = self.number_of_nodes()
        n_functions = len(func_nodes)
        n_variables = len(var_nodes)

        # Checks on nodes
        category_check, i = check(n_nodes != (n_functions+n_variables),
                                  'The number of total nodes does not match number of function and variable nodes.',
                                  status=category_check,
                                  category='A',
                                  i=i)
        for out_node in out_nodes:
            category_check, i_not = check('problem_role' not in self.nodes[out_node],
                                          'The attribute problem_role is missing on the output node %s.'
                                          % str(out_node),
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1
        for func_node in func_nodes:
            category_check, i_not = check('problem_role' not in self.nodes[func_node],
                                          'The attribute problem_role is missing on the function node %s.'
                                          % str(func_node),
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1

        # Return
        return category_check, i

    def _check_category_b(self):
        """Extended method to perform a category B check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(FundamentalProblemGraph, self)._check_category_b()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')

        # Checks
        category_check, i = check('problem_formulation' not in self.graph,
                                  'The problem formulation attribute is missing on the graph.',
                                  status=category_check,
                                  category='B',
                                  i=i)
        if category_check:
            category_check, i = check('mdao_architecture' not in self.graph['problem_formulation'],
                                      'The mdao_architecture attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if category_check:
                category_check, i = check(self.graph['problem_formulation']['mdao_architecture'] not in
                                          self.OPTIONS_ARCHITECTURES,
                                          'Invalid mdao_architecture attribute in the problem formulation.',
                                          status=category_check,
                                          category='B',
                                          i=i)
            category_check, i = check('convergence_type' not in self.graph['problem_formulation'],
                                      'The convergence_type attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if category_check:
                category_check, i = check(self.graph['problem_formulation']['convergence_type'] not in
                                          self.OPTIONS_CONVERGERS,
                                          'Invalid convergence_type %s in the problem formulation.'
                                          % self.graph['problem_formulation']['convergence_type'],
                                          status=category_check,
                                          category='B',
                                          i=i)
            category_check, i = check('function_order' not in self.graph['problem_formulation'],
                                      'The function_order attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if category_check:
                func_order = self.graph['problem_formulation']['function_order']
                category_check, i = check(len(func_order) != len(func_nodes),
                                          'There is a mismatch between the FPG functions and the given function_order, '
                                          + 'namely: %s.' % set(func_nodes).symmetric_difference(set(func_order)),
                                          status=category_check,
                                          category='B',
                                          i=i)
            category_check, i = check('function_ordering' not in self.graph['problem_formulation'],
                                      'The function_ordering attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if 'allow_unconverged_couplings' in self.graph['problem_formulation']:
                allow_unconverged_couplings = self.graph['problem_formulation']['allow_unconverged_couplings']
                category_check, i = check(not isinstance(allow_unconverged_couplings, bool),
                                          'The setting allow_unconverged_couplings should be of type boolean.',
                                          status=category_check,
                                          category='B',
                                          i=i)
            if self.graph['problem_formulation']['mdao_architecture'] in get_list_entries(self.OPTIONS_ARCHITECTURES, 5,
                                                                                          6):  # DOE
                category_check, i = check('doe_settings' not in self.graph['problem_formulation'],
                                          'The doe_settings attribute is missing in the problem formulation.',
                                          status=category_check,
                                          category='B',
                                          i=i)
                if category_check:
                    category_check, i = check('method' not in self.graph['problem_formulation']['doe_settings'],
                                              'The DOE method attribute is missing in the doe_settings.',
                                              status=category_check,
                                              category='B',
                                              i=i)
                    if category_check:
                        doe_method = self.graph['problem_formulation']['doe_settings']['method']
                        category_check, i = check(self.graph['problem_formulation']['doe_settings']['method'] not
                                                  in self.OPTIONS_DOE_METHODS,
                                                  'Invalid DOE method (%s) specified in the doe_settings.' % doe_method,
                                                  status=category_check,
                                                  category='B',
                                                  i=i)
                        if doe_method in get_list_entries(self.OPTIONS_DOE_METHODS, 1, 2, 4):  # LHC, Monte Carlo, Unif
                            category_check, i = check('runs' not in
                                                      self.graph['problem_formulation']['doe_settings'],
                                                      'The DOE runs attribute is missing in the doe_settings.',
                                                      status=category_check,
                                                      category='B',
                                                      i=i)
                            if category_check:
                                test = not isinstance(self.graph['problem_formulation']['doe_settings']['runs'],
                                                      int) or \
                                       self.graph['problem_formulation']['doe_settings']['runs'] < 0
                                category_check, i = check(test,
                                                          'Invalid DOE runs (%s) specified in the doe_settings.' %
                                                          self.graph['problem_formulation']['doe_settings']['runs'],
                                                          status=category_check,
                                                          category='B',
                                                          i=i)
                            category_check, i = check('seed' not in
                                                      self.graph['problem_formulation']['doe_settings'],
                                                      'The DOE seed attribute is missing in the doe_settings.',
                                                      status=category_check,
                                                      category='B',
                                                      i=i)
                            if category_check:
                                test = not isinstance(self.graph['problem_formulation']['doe_settings']['seed'],
                                                      int) or \
                                       self.graph['problem_formulation']['doe_settings']['seed'] < 0
                                category_check, i = check(test,
                                                          'Invalid DOE seed (%s) specified in the doe_settings.' %
                                                          self.graph['problem_formulation']['doe_settings']['seed'],
                                                          status=category_check,
                                                          category='B',
                                                          i=i)
                        if doe_method in get_list_entries(self.OPTIONS_DOE_METHODS, 0):  # FF
                            category_check, i = check('levels' not in
                                                      self.graph['problem_formulation']['doe_settings'],
                                                      'The DOE levels attribute is missing in the doe_settings.',
                                                      status=category_check,
                                                      category='B',
                                                      i=i)
                            if category_check:
                                test = not isinstance(self.graph['problem_formulation']['doe_settings']['levels'],
                                                      int) or \
                                       self.graph['problem_formulation']['doe_settings']['levels'] < 2
                                category_check, i = check(test,
                                                          'Invalid DOE levels (%s) specified in the doe_settings.' %
                                                          self.graph['problem_formulation']['doe_settings']['levels'],
                                                          status=category_check,
                                                          category='B',
                                                          i=i)
                        if doe_method in get_list_entries(self.OPTIONS_DOE_METHODS, 5):  # Box-Behnken
                            category_check, i = check('center_runs' not in
                                                      self.graph['problem_formulation']['doe_settings'],
                                                      'The DOE center_runs attribute is missing in the doe_settings.',
                                                      status=category_check,
                                                      category='B',
                                                      i=i)
                            if category_check:
                                test = not isinstance(self.graph['problem_formulation']['doe_settings']['center_runs'],
                                                      int) or \
                                       self.graph['problem_formulation']['doe_settings']['center_runs'] < 0
                                category_check, i = check(test,
                                                          'Invalid DOE center_runs (%s) specified in the doe_settings.' %
                                                          self.graph['problem_formulation']['doe_settings']['center_runs'],
                                                          status=category_check,
                                                          category='B',
                                                          i=i)

        # Return
        return category_check, i

    def _check_category_c(self):
        """Extended method to perform a category C check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(FundamentalProblemGraph, self)._check_category_c()

        # Get information
        mdao_arch = self.graph['problem_formulation']['mdao_architecture']
        conv_type = self.graph['problem_formulation']['convergence_type']
        allow_unconverged_couplings = self.graph['problem_formulation']['allow_unconverged_couplings']

        # Check if architecture and convergence_type match
        # -> match for converged-MDA, MDF, converged-DOE
        if mdao_arch in [self.OPTIONS_ARCHITECTURES[1], self.OPTIONS_ARCHITECTURES[3], self.OPTIONS_ARCHITECTURES[6]]:
            category_check, i = check(conv_type not in self.OPTIONS_CONVERGERS[:2],
                                      'Convergence type %s does not match with architecture %s.'
                                      % (conv_type, mdao_arch),
                                      status=category_check,
                                      category='C',
                                      i=i)
        # -> match IDF
        if mdao_arch in [self.OPTIONS_ARCHITECTURES[2]]:
            category_check, i = check(conv_type is not self.OPTIONS_CONVERGERS[2],
                                      'Convergence type %s does not match with architecture %s.'
                                      % (conv_type, mdao_arch),
                                      status=category_check,
                                      category='C',
                                      i=i)
        # -> match for unconverged-MDA, IDF, unconverged-OPT, unconverged-DOE
        # TODO: Sort out unconverged coupling mess
        # if mdao_arch in [self.OPTIONS_ARCHITECTURES[0], self.OPTIONS_ARCHITECTURES[4], self.OPTIONS_ARCHITECTURES[5]]:
        #     if allow_unconverged_couplings:
        #         category_check, i = check(conv_type is not self.OPTIONS_CONVERGERS[2],
        #                                   'Convergence type %s does not match with architecture %s. As unconverged '
        #                                   'couplings are allowed, the convergence method None has to be selected.'
        #                                   % (conv_type, mdao_arch),
        #                                   status=category_check,
        #                                   category='C',
        #                                   i=i)
        #     else:
        #         category_check, i = check(conv_type not in self.OPTIONS_CONVERGERS[:2],
        #                                   'Convergence type %s does not match with architecture %s. As unconverged '
        #                                   'couplings are not allowed, a convergence method has to be selected.'
        #                                   % (conv_type, mdao_arch),
        #                                   status=category_check,
        #                                   category='C',
        #                                   i=i)

        # For architectures using convergence, check whether this is necessary
        if category_check:
            coup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
            if mdao_arch == self.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                          conv_type == self.OPTIONS_CONVERGERS[1] else 0),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-MDA".',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch == self.OPTIONS_ARCHITECTURES[3]:  # MDF
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                          conv_type == self.OPTIONS_CONVERGERS[1] else 0),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-OPT".',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch == self.OPTIONS_ARCHITECTURES[2]:  # IDF
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=False),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-OPT".',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch == self.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                          conv_type == self.OPTIONS_CONVERGERS[1] else 0),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-DOE".',
                                          status=category_check,
                                          category='C',
                                          i=i)

        # For architectures not using convergence, check whether this is allowed
        if category_check:
            coup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
            # unconverged-MDA, unconverged-OPT, unconverged-DOE
            if mdao_arch in get_list_entries(self.OPTIONS_ARCHITECTURES, 0, 4, 5):
                if not allow_unconverged_couplings:
                    category_check, i = check(self.check_for_coupling(coup_funcs, only_feedback=True),
                                              'Inconsistent problem formulation, no feedback coupling was expected. '
                                              'Architecture should be set to something using convergence (e.g. MDF). '
                                              'Or setting allow_unconverged_couplings should be set to True.',
                                              status=category_check,
                                              category='C',
                                              i=i)
                if category_check and conv_type is not self.OPTIONS_CONVERGERS[2]:
                    category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                              conv_type == self.OPTIONS_CONVERGERS[1] else False),
                                              'Inconsistent problem formulation, expected coupling missing. '
                                              'Architecture should be unconverged variant with convergence type None.',
                                              status=category_check,
                                              category='C',
                                              i=i)

        # Check the feedforwardness of the pre-coupling functions
        if category_check:
            fun_ord = self.graph['problem_formulation']['function_ordering']
            precoup_funcs = fun_ord[self.FUNCTION_ROLES[3]] + fun_ord[self.FUNCTION_ROLES[4]]
            category_check, i = check(self.check_for_coupling(precoup_funcs, only_feedback=True),
                                      'Pre-coupling functions contain feedback variables. '
                                      'Pre-coupling functions should be adjusted.',
                                      status=category_check,
                                      category='C',
                                      i=i)

        # Check whether the necessary variables have been marked with the problem_role attribute
        if category_check:
            if mdao_arch in self.OPTIONS_ARCHITECTURES[2:5]:  # IDF, MDF, unconverged-OPT
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                category_check, i = check(len(des_var_nodes) == 0,
                                          'No design variables are specified. Use the problem_role attribute for this.',
                                          status=category_check,
                                          category='C',
                                          i=i)
                # Check the design variables connections
                for des_var_node in des_var_nodes:
                    des_var_sources = self.get_sources(des_var_node)
                    # noinspection PyUnboundLocalVariable
                    category_check, i_not = check(not set(des_var_sources).issubset(precoup_funcs),
                                                  'Design variable %s has a source after the pre-coupling functions. '
                                                  'Adjust design variables or function order to solve this.'
                                                  % des_var_node,
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
                    category_check, i_not = check(self.out_degree(des_var_node) == 0,
                                                  'Design variable %s does not have any targets. Reconsider design '
                                                  'variable selection.' % des_var_node,
                                                  status=category_check,
                                                  category='C',
                                                  i=i+1)
                i += 2
                constraint_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[2]])
                objective_node = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[1]])
                category_check, i = check(len(objective_node) != 1,
                                          '%d objective variables are specified. Only one objective node is allowed. '
                                          'Use the problem_role attribute for this.' % len(objective_node),
                                          status=category_check,
                                          category='C',
                                          i=i)
                constraint_functions = list()
                for idx, node in enumerate(objective_node + constraint_nodes):
                    category_check, i_not = check(self.in_degree(node) != 1,
                                                  'Invalid in-degree of ' + str(self.in_degree(node)) +
                                                  ', while it should be 1 of node: ' + str(node),
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
                    category_check, i_not = check(self.out_degree(node) != 0,
                                                  'Invalid out-degree of '+ str(self.out_degree(node))
                                                  + ', while it should be 0 of node: ' + str(node),
                                                  status=category_check,
                                                  category='C',
                                                  i=i+1)
                    if idx == 0:
                        objective_function = list(self.in_edges(node))[0][0]
                    elif not (list(self.in_edges(node))[0][0] in set(constraint_functions)):
                        constraint_functions.append(list(self.in_edges(node))[0][0])
                i += 2
                if category_check:
                    # Check that the objective function is unique (not also a constraint function)
                    # noinspection PyUnboundLocalVariable
                    category_check, i = check(objective_function in constraint_functions,
                                              'Objective function should be a separate function.',
                                              status=category_check,
                                              category='C',
                                              i=i)
                    optimizer_functions = [objective_function] + constraint_functions
                    # Check that all optimizer function are post-coupling functions for IDF and MDF
                    if mdao_arch in self.OPTIONS_ARCHITECTURES[2:4]:
                        func_cats = self.graph['problem_formulation']['function_ordering']
                        diff = set(optimizer_functions).difference(func_cats[self.FUNCTION_ROLES[2]])
                        coup_check = self.check_for_coupling(optimizer_functions, only_feedback=False)
                        category_check, i = check(diff,
                                                  'Not all optimizer functions are not post-coupling functions, '
                                                  'namely: %s' % diff,
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
                        category_check, i = check(coup_check,
                                                  'The optimizer functions %s are not independent of each other.'
                                                  % optimizer_functions,
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
            if mdao_arch in self.OPTIONS_ARCHITECTURES[:2] + self.OPTIONS_ARCHITECTURES[5:7]:
                # unc-MDA, con-MDA, unc-DOE, con-DOE
                # Check whether quantities of interest have been defined.
                qoi_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[3]])
                category_check, i = check(len(qoi_nodes) == 0,
                                          'No quantities of interest are specified. Use the problem_role attribute for '
                                          'this.',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch in self.OPTIONS_ARCHITECTURES[5:7]:  # unc-DOE, con-DOE
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                category_check, i = check(len(des_var_nodes) == 0,
                                          'No design variables are specified. Use the problem_role attribute for this.',
                                          status=category_check,
                                          category='C',
                                          i=i)
                if category_check:
                    # If custom table, check the samples
                    if self.graph['problem_formulation']['doe_settings']['method'] == self.OPTIONS_DOE_METHODS[3]:
                        all_samples = []
                        for des_var_node in des_var_nodes:
                            category_check, i_not = check('samples' not in self.nodes[des_var_node],
                                                          'The samples attributes is missing for design variable node'
                                                          ' %s.' % des_var_node,
                                                          status=category_check,
                                                          category='C',
                                                          i=i)
                            if category_check:
                                all_samples.append(self.nodes[des_var_node]['samples'])
                        i += 1
                        sample_lengths = [len(item) for item in all_samples]
                        # Check whether all samples have the same length
                        category_check, i = check(not sample_lengths.count(sample_lengths[0]) == len(sample_lengths),
                                                  'Not all given samples have the same length, this is mandatory.',
                                                  status=category_check,
                                                  category='C',
                                                  i=i)

        # Return
        return category_check, i

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #

    def add_function_problem_roles(self):
        """Method to determine the function problem roles of the functions in an FPG.

        :return:
        :rtype:
        """
        logger.info('Adding function problem roles...')
        # Input assertions
        if self.find_all_nodes(subcategory='all problematic variables'):
            raise AssertionError('Problem roles could not be determined. '
                                 'Graph still has problematic variables, namely: {}.'.format(
                self.find_all_nodes(subcategory='all problematic variables')
            ))

        # Define sets and coupled node label
        uncoupled_dvi = set()
        uncoupled_dvd = set()
        coupled = set()
        post_coupled = set()
        _coupled_node_str = '__coupled__'
        _des_vars_node = '__des_vars__'

        # First construct the function graph
        fgraph = self.get_fdg()  # fdg: function dependency graph

        # Get the coupled functions based on cycles
        there_are_cycles = True
        i = 0
        while there_are_cycles:
            try:
                cycles = nx.find_cycle(fgraph, orientation='original')
            except NetworkXNoCycle:
                there_are_cycles = False
            else:
                functions_to_merge = {f for cycle in cycles for f in cycle[:-1]}
                coupled.update(functions_to_merge)
                if '_coupled_node' in locals():
                    if _coupled_node in functions_to_merge:
                        coupled.remove(_coupled_node)
                    else:
                        functions_to_merge.update([_coupled_node])
                _coupled_node = _coupled_node_str + str(i)
                fgraph = fgraph.merge_functions(functions_to_merge, new_label=_coupled_node)
                i += 1

        # Get the post-coupled functions
        if coupled:
            if not nx.is_directed_acyclic_graph(fgraph):
                raise AssertionError('Graph has to be acyclic at this point to determine post-coupled functions.')
            post_coupled.update(nx.descendants(fgraph, _coupled_node))

        # Clean up the graph by removing all coupled and post-coupled functions -> pre-coupling functions are left
        fgraph.remove_nodes_from(post_coupled)
        if '_coupled_node' in locals():
            fgraph.remove_node(_coupled_node)

        # Add design variables to the graph again as a single starting node and determine descendants
        des_vars = self.find_all_nodes(category='variable',
                                       attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
        for des_var in des_vars:
            des_var_targets = self.get_targets(des_var)
            for trg in des_var_targets:
                if trg in fgraph.function_nodes:
                    if not fgraph.has_node(_des_vars_node):
                        fgraph.add_node(_des_vars_node, category='variable')
                    fgraph.add_edge(_des_vars_node, trg)
        if fgraph.has_node(_des_vars_node):
            uncoupled_dvd.update(nx.descendants(fgraph, _des_vars_node))

        # Remove the uncoupled-DVD functions from the graph
        fgraph.remove_nodes_from(uncoupled_dvd)

        # Remaining functions are uncoupled-DVI
        uncoupled_dvi.update(fgraph.function_nodes)

        # Add the function problem roles on the original graph
        f_roles = self.FUNCTION_ROLES
        g_prob_form = self.graph['problem_formulation']
        for fnode in uncoupled_dvi:
            self.nodes[fnode]['problem_role'] = f_roles[3]
        for fnode in uncoupled_dvd:
            self.nodes[fnode]['problem_role'] = f_roles[4]
        for fnode in coupled:
            self.nodes[fnode]['problem_role'] = f_roles[1]
        for fnode in post_coupled:
            self.nodes[fnode]['problem_role'] = f_roles[2]

        # TODO: Added for backward compatibility, should be removed to remove dependency on order...
        # TODO: In addition, when this is removed, the function role 'pre-coupling' can be removed.
        f_order = g_prob_form['function_order']
        g_prob_form['function_ordering'] = {f_roles[3]: [f for f in f_order if f in uncoupled_dvi],
                                            f_roles[4]: [f for f in f_order if f in uncoupled_dvd],
                                            f_roles[1]: [f for f in f_order if f in coupled],
                                            f_roles[2]: [f for f in f_order if f in post_coupled]}

        logger.info('Successfully added function problem roles...')

        return uncoupled_dvi, uncoupled_dvd, coupled, post_coupled

    def add_problem_formulation(self, mdao_definition, function_order, doe_settings=None):
        """Method to add the problem formulation.

        :param mdao_definition: MDF-GS, MDF-J, IDF, CO, BLIS-2000
        :type mdao_definition: str
        :param function_order: order or functions to be included in graph
        :type function_order: list
        :param doe_settings: doe settings of the graph
        :type doe_settings: dict
        :return: graph enriched with problem formulation
        :rtype: Fundamental ProblemGraph
        """

        # Impose the MDAO architecture
        mdao_architecture, convergence_type, allow_unconverged_couplings = get_mdao_setup(mdao_definition)

        # Define settings of the problem formulation
        if 'problem_formulation' not in self.graph:
            self.graph['problem_formulation'] = dict()
        self.graph['problem_formulation']['function_order'] = function_order
        self.graph['problem_formulation']['mdao_architecture'] = mdao_architecture
        self.graph['problem_formulation']['convergence_type'] = convergence_type
        self.graph['problem_formulation']['allow_unconverged_couplings'] = allow_unconverged_couplings

        if doe_settings:
            self.graph['problem_formulation']['doe_settings'] = pf_doe_settings = dict()
            pf_doe_settings['method'] = doe_settings['method']
            if 'seed' in doe_settings:
                pf_doe_settings['seed'] = doe_settings['seed']
            if 'runs' in doe_settings:
                pf_doe_settings['runs'] = doe_settings['runs']
            if 'center_runs' in doe_settings:
                pf_doe_settings['center_runs'] = doe_settings['center_runs']
            if 'levels' in doe_settings:
                pf_doe_settings['levels'] = doe_settings['levels']

    def partition_graph(self, n_parts, node_selection=None, use_runtime_info=False, local_convergers=False,
                        rcb_partitioning=0.0, rcb_order=1.0, coupling_dict=None, tpwgts=None):
        """Partition a graph using the Metis algorithm (http://glaros.dtc.umn.edu/gkhome/metis/metis/overview).

        :param n_parts: number of partitions requested (algorithm might provide less if the number of partitions is
        close to the number of nodes)
        :type n_parts: int
        :param node_selection: option to give the nodes that need to be included in the partitions. If none are given,
        the nodes in the partitions are selected based on the mdao architecture
        :type node_selection: list
        :param use_runtime_info: option to take the runtime information of the nodes into account when determining the
        partitions
        :type use_runtime_info: bool
        :param local_convergers: option to add local convergers to the partitions if feedback within the partition exist
        :type local_convergers: bool
        :param rcb_partitioning: runtime-coupling balance for partitioning, relative importance between cut edges and
        runtime while making the partitions. 1: min cut edges, 0: min runtime
        :type rcb_partitioning: float
        :param rcb_order: runtime-coupling balance for sequencing, relative importance between feedback and runtime
        while determining the function order within the partitions. 1: min feedback, 0: min runtime
        :type rcb_order: float
        :param coupling_dict: coupling dictionary indicating the input/output relations between the nodes
        :type coupling_dict: dict
        :param tpwgts: list of target partition weights
        :type tpwgts: list

        .. note:: partitioning can only be performed on undirected graphs. Therefore every graph input is translated
            into an undirected graph.

        """
        # TODO: Check also for metis installation?
        import metis

        # Input assertions
        if not node_selection:
            assert 'function_ordering' in self.graph['problem_formulation'], 'Function ordering is missing'
        if self.graph['problem_formulation']['convergence_type']:
            if 'Gauss-Seidel' in self.graph['problem_formulation']['convergence_type']:
                logger.warning('Partitioning does not work correctly with a Gauss-Seidel converger, use Jacobi instead')

        # Get coupling dictionary
        if not coupling_dict:
            coupling_dict = self.get_coupling_dictionary()

        # Get the nodes that need to be partitioned
        if node_selection:
            nodes_to_partition = list(node_selection)
        # For IDF, all functions in the optimizer loop are partitioned except for the objective and constraint functions
        elif self.graph['problem_formulation']['mdao_architecture'] == self.OPTIONS_ARCHITECTURES[2]:
            # Get post-design-variables, coupled and post-coupling functions
            mg_function_ordering = self.get_mg_function_ordering()
            post_des_vars = mg_function_ordering[self.FUNCTION_ROLES[4]]
            post_couplings = mg_function_ordering[self.FUNCTION_ROLES[2]]
            coupled_nodes = mg_function_ordering[self.FUNCTION_ROLES[1]]
            # Get objective and constraint functions  # TODO: Check for generic problem
            constr_obj_vars = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[2]]) + \
                self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[1]])
            constr_obj_funcs = [self.get_sources(variable)[0] for variable in constr_obj_vars]
            # Get the nodes that need to be partitioned
            nodes_to_partition = [node for node in post_des_vars if node not in constr_obj_funcs] + coupled_nodes + \
                                 [node for node in post_couplings if node not in constr_obj_funcs]
        # When a converger is present or no system architecture selected, only the coupled functions are partitioned
        else:
            function_ordering = self.graph['problem_formulation']['function_ordering']
            coupled_nodes = function_ordering[self.FUNCTION_ROLES[1]]
            nodes_to_partition = coupled_nodes

        # Check runtime and number of nodes
        if use_runtime_info:
            for node in nodes_to_partition:
                assert 'run_time' in self.nodes[node]['performance_info'], 'Run time missing for function ' \
                                                                           '{}'.format(node)

        # Get initial function graph of the nodes that need to be partitioned
        subgraph = self.get_subgraph_by_function_nodes(nodes_to_partition)
        initial_function_graph = subgraph.get_function_graph()

        # Get total number of couplings and the maximum runtime of the graph
        total_couplings = sum([coupling_dict[function1][function2] for function1 in nodes_to_partition for function2 in
                               nodes_to_partition if function2 in coupling_dict[function1]])
        total_time = sum([self.nodes[node]['performance_info']['run_time'] for node in nodes_to_partition]) if \
            use_runtime_info else len(nodes_to_partition)

        # Initialize variables
        best_partitions = []
        min_f, min_variables, min_time = float("inf"), float("inf"), float("inf")
        number_of_iterations_not_improved = 0
        function_graph = initial_function_graph.deepcopy()
        if 'problem_formulation' in self.graph and 'function_order' in self.graph['problem_formulation']:
            previous_function_order = self.graph['problem_formulation']['function_order']
        else:
            previous_function_order = nodes_to_partition

        # Calculate maximum load imbalance based on the objective
        if rcb_partitioning == 0:
            initial_ufactor = 1
        else:
            if use_runtime_info:
                runtimes = [self.nodes[node]['performance_info']['run_time'] for node in nodes_to_partition]
                lowest_runtimes = sorted(runtimes)[:n_parts - 1]
                max_runtime_part = total_time - sum(lowest_runtimes)
            else:
                max_runtime_part = total_time - (n_parts - 1)
            max_load_imbalance = max_runtime_part / (total_time / float(n_parts))
            initial_ufactor = 1 if max_load_imbalance == 1.0 else int((max_load_imbalance - 1.0) * 1000 *
                                                                      rcb_partitioning)

        # If the number of nodes equals the number of required partitions return the solution immediately
        if len(nodes_to_partition) == n_parts:
            best_partitions = [[node] for node in nodes_to_partition]
        # If the number of nodes is less than the number of required partitions return the solution immediately and give
        # a warning
        elif len(nodes_to_partition) < n_parts:
            best_partitions = [[node] for node in nodes_to_partition]
            logger.warning('Number of partitions ({0}) exceeds number of nodes ({1}). The solution for {1} partitions '
                           'will be returned'.format(n_parts, len(nodes_to_partition)))
        # If the number of partitions is one, determine the correct function order and return the solution
        # TODO: Possibly can be combined...
        elif n_parts == 1:
            if local_convergers:
                best_partitions = [self.get_possible_function_order('single-swap', node_selection=nodes_to_partition,
                                                                    rcb=rcb_order, coupling_dict=coupling_dict,
                                                                    use_runtime_info=use_runtime_info)]
            else:
                best_partitions = [self.minimize_feedback(nodes_to_partition, 'single-swap', rcb=rcb_order,
                                                          coupling_dict=coupling_dict,
                                                          use_runtime_info=use_runtime_info)]
        # Else partition the graph
        else:
            while True:
                # TODO: Next twenty lines could be a separate method -> transform_as_metis_graph()
                # Combine coupling strengths of feedforward and feedback connections between two nodes to get an
                # undirected graph with the correct edge weights
                remove_edges = []
                for edge in function_graph.edges():
                    if (edge[0], edge[1]) in remove_edges:
                        continue
                    elif (edge[1], edge[0]) in function_graph.edges():
                        function_graph.edges[edge[0], edge[1]]['coupling_strength'] += function_graph.edges[
                            edge[1], edge[0]]['coupling_strength']
                        remove_edges.append((edge[1], edge[0]))
                for edge in remove_edges:
                    function_graph.remove_edge(edge[0], edge[1])

                # Get undirected graph
                g_und = function_graph.to_undirected()

                # Add runtime to the nodes of the undirected graph for metis
                for node in g_und.nodes():
                    g_und.nodes[node]['run_time'] = g_und.nodes[node]['performance_info']['run_time'] if \
                        use_runtime_info else 1

                # Set the runtime as node weight and the coupling strength as edge weight for metis
                g_und.graph['node_weight_attr'] = 'run_time'
                g_und.graph['edge_weight_attr'] = 'coupling_strength'

                # Reset maximum load imbalance to initial value
                ufactor = initial_ufactor

                # Partition graph using metis
                # Balance factor is reduced if number of partitions is too low, until the right
                # amount of partitions is received
                while True:
                    (edgecuts, parts) = metis.part_graph(g_und, n_parts, tpwgts=tpwgts, recursive=True, ufactor=ufactor)
                    if len(set(parts)) != n_parts and ufactor != 1:
                        ufactor = 1 if ufactor < 101 else ufactor - 100
                        continue
                    else:
                        break

                # Create a list with the nodes in each partition
                partitions = []
                for part in range(n_parts):
                    # Get nodes in this partition
                    nodes = []
                    for idx, node in enumerate(g_und.nodes):
                        if parts[idx] == part:
                            nodes.extend(node.split('--') if '--' in node else [node])
                    # Get an initial guess for the function order based on the previous partitioning (in order to speed
                    # up the process)
                    nodes = [node for node in previous_function_order if node in nodes]
                    # Minimize feedback within the partition
                    if nodes:
                        if local_convergers:
                            nodes = self.get_possible_function_order('single-swap', node_selection=nodes, rcb=rcb_order,
                                                                     coupling_dict=coupling_dict,
                                                                     use_runtime_info=use_runtime_info)
                        else:
                            nodes = self.minimize_feedback(nodes, 'single-swap', rcb=rcb_order,
                                                           coupling_dict=coupling_dict,
                                                           use_runtime_info=use_runtime_info)
                    # Add nodes to the partition list
                    partitions.append(nodes)

                # Update function order for next iteration
                previous_function_order = [node for part_order in partitions for node in part_order]

                # Evaluate the properties of the partitioning
                n_variables, partition_variables, system_variables, runtime = self.get_partition_info(
                    partitions, coupling_dict=coupling_dict, use_runtime_info=use_runtime_info,
                    local_convergers=local_convergers)

                # Decide whether new solution is better than the best solution found so far
                f = rcb_partitioning * (n_variables / float(total_couplings)) + (1 - rcb_partitioning) * \
                                                                                (max(runtime) / float(total_time))
                if (n_variables == min_variables and max(runtime) < min_time) or \
                        (max(runtime) == min_time and n_variables < min_variables) or (f < min_f):
                    best_partitions, min_f, min_variables, min_time = partitions, f, n_variables, max(runtime)
                    number_of_iterations_not_improved = 0
                else:
                    number_of_iterations_not_improved += 1

                # If the third iteration does not give an improvement the iterations are stopped
                if number_of_iterations_not_improved > 2:  # TODO: make a setting of this value
                    break

                # Reset the function graph to the initial graph (without merged nodes)
                function_graph = initial_function_graph.deepcopy()

                # Merge the nodes that can be merged based on process
                for partition in partitions:
                    nodes = list(partition)
                    previous_node = []
                    for node in nodes:
                        # Check if current node can be merged with the previous node. Nodes are only merged if the
                        # resulting number of nodes is still enough to get the required number of partitions
                        prev_nodes = previous_node.split('--') if '--' in previous_node else [previous_node]
                        if previous_node and not any(prev_node in coupling_dict[node] or node in
                                                     coupling_dict[prev_node] for prev_node in prev_nodes) and \
                                len(function_graph.nodes) - 1 >= n_parts:
                            merge_nodes = [previous_node, node]
                            new_node = '--'.join(merge_nodes)
                            runtime = max(function_graph.nodes[func]['performance_info']['run_time'] for func in
                                          merge_nodes) if use_runtime_info else 1
                            function_graph.add_node(new_node, category='function')
                            for merge_node in merge_nodes:
                                function_graph = nx.contracted_nodes(function_graph, new_node, merge_node,
                                                                     self_loops=False)
                            function_graph.nodes[new_node]['performance_info'] = {'run_time': runtime}
                            previous_node = new_node
                        else:
                            previous_node = node

                # Get correct coupling strengths in case merged nodes exist in the graph
                for node1 in function_graph.nodes():
                    for node2 in function_graph.nodes():
                        coupling_strength = 0
                        source_nodes = node1.split('--') if '--' in node1 else [node1]
                        target_nodes = node2.split('--') if '--' in node2 else [node2]
                        for source in source_nodes:
                            for target in target_nodes:
                                if (source, target) in initial_function_graph.edges():
                                    coupling_strength += initial_function_graph.edges[source, target][
                                        'coupling_strength']
                        if coupling_strength != 0:
                            function_graph.edges[node1, node2]['coupling_strength'] = coupling_strength

        # Check if enough partitions are returned, if not remove empty partitions and give a warning
        best_partitions = [partition for partition in best_partitions if partition]
        if len(best_partitions) < n_parts:
            logger.warning('Metis returned {} instead of {} partitions'.format(len(best_partitions), n_parts))

        # Add local convergers if there are feedback loops in the partitions
        convergers = []
        if local_convergers:
            for part_nr, partition in enumerate(best_partitions):
                if self.check_for_coupling(partition, only_feedback=True):
                    convergers.append(part_nr)

        # Add partition id to the nodes
        for idx, partition in enumerate(best_partitions):
            for node in partition:
                self.nodes[node]['partition_id'] = idx

        # Add partition to the input graph
        if 'problem_formulation' not in self.graph:
            self.graph['problem_formulation'] = dict()
        self.graph['problem_formulation']['coupled_functions_groups'] = best_partitions
        self.graph['problem_formulation']['local_convergers'] = convergers
        self.graph['problem_formulation']['jacobi_convergence'] = []   # TODO: depricate ?
        self.graph['problem_formulation']['sequence_partitions'] = []  # TODO: depricate ?

        return

    def get_partition_info(self, partitions, coupling_dict=None, use_runtime_info=False, local_convergers=False):
        """ Function to get information about the partitions. The functions returns:

        -  Total number of connections to converge, divided in:
            -  Number of feedback connections in each partition
            -  Total number of cut edges due to the partitioning
        -  Estimation of the runtime for each partition

        :param partitions: list which indicates which nodes are in which partition
        :type partitions: list
        :param coupling_dict: coupling dictionary indicating the input/output relations between the nodes
        :type coupling_dict: dict
        :param use_runtime_info: option to take the runtime information of the nodes into account when determining the
        partitions
        :type use_runtime_info: bool
        :param local_convergers: option to add local convergers to the partitions if feedback within the partition exist
        :param local_convergers: bool
        :return total_connections: total number of connections to converge
        :return partition_variables: number of feedback connections in each partition
        :return system_variables: total number of cut edges due to the partitioning
        :return run_time_partitions: runtime estimation for each partition

        ..note:: If a converger is present in a partition, the iterations are not taken into account in the runtime
        estimation

        """

        # Get complete function order of nodes in the partitions
        function_order = [func for partition in partitions for func in partition]

        # Input assertions
        if use_runtime_info:
            for node in function_order:
                assert 'run_time' in self.nodes[node]['performance_info'], 'Run time missing for function ' \
                                                                           '{}'.format(node)

        # Get coupling dictionary
        if not coupling_dict:
            coupling_dict = self.get_coupling_dictionary()

        # For each node in the partitions check whether its input comes from the same partition, another partition or
        # neither
        system_connections = 0
        partition_connections = []
        for partition, nodes in enumerate(partitions):
            partition_feedback = 0
            for idx, target in enumerate(nodes):
                for source in coupling_dict[target]:
                    if source in nodes[idx+1:]:
                        partition_feedback += coupling_dict[target][source]
                    elif source in function_order and source not in nodes:
                        system_connections += coupling_dict[target][source]
            partition_connections.append(partition_feedback)
        total_connections = system_connections + sum(partition_connections)

        # Calculate runtime
        run_time_partitions = []
        for partition, nodes in enumerate(partitions):
            # If a local converger is present in the partition, nodes are divided in pre/post/coupled functions
            if local_convergers and self.check_for_coupling(nodes, only_feedback=True):
                pre_coupling_nodes, post_coupling_nodes = [], []
                idx1 = 0
                # Get pre-coupled nodes
                for idx1, node in enumerate(nodes):
                    if set(nodes[idx1 + 1:]).intersection(coupling_dict[node]):
                        pre_coupling_nodes = nodes[:idx1]
                        break
                # Get the nodes that provide feedback
                feedback_nodes = [node for idx, func in enumerate(nodes) for node in coupling_dict[func] if node in
                                  nodes[idx:]]
                # Get post-coupling nodes
                for idx2, node in reversed(list(enumerate(nodes[idx1:]))):
                    if node in feedback_nodes:
                        post_coupling_nodes = nodes[idx2 + 1:]
                        break
                # Get coupled nodes
                coupled_nodes = [node for node in nodes if node not in pre_coupling_nodes + post_coupling_nodes]
                # Calculate runtime (multiple runs of coupled nodes for convergence is not taken into account)
                run_time_partition = self.get_runtime_sequence(pre_coupling_nodes, coupling_dict=coupling_dict,
                                                               use_runtime_info=use_runtime_info) + \
                    self.get_runtime_sequence(coupled_nodes, coupling_dict=coupling_dict,
                                              use_runtime_info=use_runtime_info) + \
                    self.get_runtime_sequence(post_coupling_nodes, coupling_dict=coupling_dict,
                                              use_runtime_info=use_runtime_info)
            else:
                run_time_partition = self.get_runtime_sequence(nodes, coupling_dict=coupling_dict,
                                                               use_runtime_info=use_runtime_info)
            run_time_partitions.append(run_time_partition)

        return total_connections, partition_connections, system_connections, run_time_partitions

    def select_number_of_partitions(self, partition_range='pareto', node_selection=None, use_runtime_info=False,
                                    local_convergers=False, rcb_partitioning=0.0, rcb_order=1.0, coupling_dict=None,
                                    plot_solutions=False):
        """ Function to evaluate the properties of different number of partitions and to select the best one.

        :param partition_range: range of number of partitions that need to be evaluated. If set to 'pareto', a pareto
        front will be calculated.
        :type partition_range: list or str
        :param node_selection: option to give the nodes that need to be included in the partitions. If none are given,
        the nodes in the partitions are selected based on the mdao architecture
        :type node_selection: list
        :param use_runtime_info: option to take the runtime information of the nodes into account when determining the
        partitions
        :type use_runtime_info: bool
        :param local_convergers: option to add local convergers to the partitions if feedback within the partition exist
        :type local_convergers: bool
        :param rcb_partitioning: runtime-coupling balance for partitioning, relative importance between cut edges and
        runtime while making the partitions. 1: min cut edges, 0: min runtime
        :type rcb_partitioning: float
        :param rcb_order: runtime-coupling balance for sequencing, relative importance between feedback and runtime
        while determining the function order within the partitions. 1: min feedback, 0: min runtime
        :type rcb_order: float
        :param coupling_dict: coupling dictionary indicating the input/output relations between the nodes
        :type coupling_dict: dict
        :param plot_solutions: option to plot the characteristics of different number of partitions
        :type plot_solutions: bool
        """

        # Input assertions
        assert 'function_ordering' in self.graph['problem_formulation'], 'Function ordering is missing'

        # Get coupling dictionary
        if not coupling_dict:
            coupling_dict = self.get_coupling_dictionary()

        # Get the nodes that need to be partitioned
        if node_selection:
            nodes_to_partition = list(node_selection)
        # For IDF, all functions in the optimizer loop are partitioned except for the objective and constraint functions
        elif self.graph['problem_formulation']['mdao_architecture'] == self.OPTIONS_ARCHITECTURES[2]:
            # Get post-design-variables, coupled and post-coupling functions
            mg_function_ordering = self.get_mg_function_ordering()
            post_des_vars = mg_function_ordering[self.FUNCTION_ROLES[4]]
            post_couplings = mg_function_ordering[self.FUNCTION_ROLES[2]]
            coupled_nodes = mg_function_ordering[self.FUNCTION_ROLES[1]]
            # Get objective and constraint functions
            constr_obj_vars = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[2]]) + \
                self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[1]])
            constr_obj_funcs = [self.get_sources(variable)[0] for variable in constr_obj_vars]
            # Get the nodes that need to be partitioned
            nodes_to_partition = [node for node in post_des_vars if node not in constr_obj_funcs] + coupled_nodes + \
                                 [node for node in post_couplings if node not in constr_obj_funcs]
        # When a converger is present or no system architecture selected, only the coupled functions are partitioned
        else:
            function_ordering = self.graph['problem_formulation']['function_ordering']
            coupled_nodes = function_ordering[self.FUNCTION_ROLES[1]]
            nodes_to_partition = coupled_nodes

        # Check runtime
        if use_runtime_info:
            for node in nodes_to_partition:
                assert 'run_time' in self.nodes[node]['performance_info'], 'Run time missing for function ' \
                                                                           '{}'.format(node)

        # Get the partition range if a pareto front is needed
        if partition_range == 'pareto':
            pareto = True
            partition_range = range(len(nodes_to_partition) + 1)[1:]
        else:
            pareto = False

        # Initialize variables
        partition_info, partition_results = [], []

        # Partition graph
        for idx, n_partitions in enumerate(partition_range):
            graph = self.deepcopy()
            logger.info('Calculating the solution for {} partitions'.format(n_partitions))
            graph.partition_graph(n_partitions, node_selection=nodes_to_partition, coupling_dict=coupling_dict,
                                  use_runtime_info=use_runtime_info, local_convergers=local_convergers,
                                  rcb_partitioning=rcb_partitioning, rcb_order=rcb_order)
            partitions = graph.graph['problem_formulation']['coupled_functions_groups']
            local_convs = graph.graph['problem_formulation']['local_convergers']

            # Evaluate graph
            total_var, partition_variables, system_variables, runtime = graph.get_partition_info(
                partitions, use_runtime_info=use_runtime_info, coupling_dict=coupling_dict,
                local_convergers=local_convergers)

            # Get number of partitions (Metis can return less partitions in case the number of partitions is close
            # to the number of nodes in the partitions)
            n_parts = len(partitions)

            # Save partition information
            partition_info.append([idx, n_parts, partition_variables, system_variables, total_var,
                                   max(runtime)])
            partition_results.append([max(runtime), total_var, idx, partitions, local_convs])

        # If pareto front, get optimal results
        if pareto:
            # Obtain pareto front
            sorted_solutions = sorted(partition_results)
            pareto_front = [sorted_solutions[0]]
            for solution in sorted_solutions:
                if solution[1] < pareto_front[-1][1] and solution[0] != pareto_front[-1][0]:
                    pareto_front.append(solution)
            accepted_solutions = [solution[2] for solution in pareto_front]
            # Get optimal solutions
            partition_info = [result for result in partition_info if result[0] in accepted_solutions]
            partition_results = list(pareto_front)
            partition_results.reverse()
            for idx, solution in enumerate(partition_info):
                solution[0] = idx
            partition_range = [solution[1] for solution in partition_info]

        # Print partition information in table
        header = ['Option', '# partitions', '# feedback in partitions', '# system connections', 'Total # connections',
                  'Runtime']
        printing.print_in_table(partition_info, headers=header)

        # Show the options in a graph
        if plot_solutions:
            from matplotlib.ticker import MaxNLocator
            fig, ax = plt.subplots()
            plt_x, plt_y, txt = [], [], []
            for result in partition_info:
                plt_x.append(result[5])
                plt_y.append(result[4])
                txt.append(str(result[1]))
            ax.scatter(plt_x, plt_y)
            for idx in range(len(plt_x)):
                ax.annotate(txt[idx], (plt_x[idx], plt_y[idx]))
            plt.xlabel('Longest runtime')
            plt.ylabel('# variables to converge')
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            plt.show()

        # Select the number of partitions
        selmsg = 'Please select the desired option:'
        sel = prompting.user_prompt_select_options(*partition_range, message=selmsg, allow_empty=False,
                                                   allow_multi=False)
        idx = partition_range.index(int(sel[0]))

        # Add partition id to the nodes
        for part_nr, partition in enumerate(partition_results[idx][3]):
            for node in partition:
                self.nodes[node]['partition_id'] = part_nr

        # Add partition to the input graph
        self.graph['problem_formulation']['coupled_functions_groups'] = partition_results[idx][3]
        self.graph['problem_formulation']['local_convergers'] = partition_results[idx][4]
        self.graph['problem_formulation']['jacobi_convergence'] = []
        self.graph['problem_formulation']['sequence_partitions'] = []

        return

    def change_settings_distributed_convergence(self):
        """ Function to change the settings when the distributed convergence is set as architecture.

        Options:
        -  Add or remove a local converger for each partition
        -  Set the convergence method within each partition (Gauss-Seidel (default) or Jacobi)
        -  Let partitions run in sequence instead of parallel
        """
        # TODO: Depricate functions ?

        # Input assertions
        assert 'coupled_functions_groups' in self.graph['problem_formulation'], 'Graph is not yet partitioned'
        assert len(self.graph['problem_formulation']['coupled_functions_groups']) > 1, 'Graph must have at least two ' \
                                                                                       'partitions'

        # Get graph information
        partitions = self.graph['problem_formulation']['coupled_functions_groups']

        # Change the local convergers
        # Check which partitions have feedback and can have a local converger
        possible_convergers = []
        for idx, partition in enumerate(partitions):
            if not nx.is_directed_acyclic_graph(self.get_subgraph_by_function_nodes(partition)):
                possible_convergers.append(idx)

        msg = 'Please select which partitions need a local converger (options: {}):'.format(possible_convergers)
        while True:
            local_convergers = prompting.user_prompt_select_options(*range(len(partitions)), allow_empty=True,
                                                                    allow_multi=True, message=msg)
            # Check whether a valid input is given
            if all(converger in possible_convergers for converger in local_convergers):
                break
            else:
                print('Partitions {} do not contain feedback and therefore they cannot have a local ' \
                      'converger'.format(list(set(local_convergers).symmetric_difference(possible_convergers) -
                                              set(possible_convergers))))

        # Change convergence method of each partition
        msg = 'Please select which partitions must be solved using a Jacobi convergence:'
        jacobi_convergence = prompting.user_prompt_select_options(*range(len(partitions)), allow_empty=True,
                                                                  allow_multi=True, message=msg)

        # Select which partitions must be executed in sequence
        msg = 'Please select which partitions must be run in sequence (e.g. [[0, 1], [2, 3]]):'
        while True:
            valid_input = True
            sequence_partitions = prompting.user_prompt_string(allow_empty=True, message=msg)
            sequence_partitions = eval(sequence_partitions) if sequence_partitions else []
            sequence_partitions = [sequence_partitions] if not any(
                isinstance(el, list) for el in sequence_partitions) \
                else sequence_partitions
            # Do some checks to see whether a valid input is given
            if not isinstance(sequence_partitions, list) or not any(
                    isinstance(el, list) for el in sequence_partitions):
                print('Input should be a list or list of lists')
                valid_input = False
            unique_parts = set()
            n_parts = 0
            for sequence in sequence_partitions:
                for idx, element in enumerate(sequence):
                    if not isinstance(element, int):
                        print('Only integers are allowed!')
                        valid_input = False
                    if idx != 0 and sequence[idx] < sequence[idx - 1]:
                        print('Partitions must be in increasing order')
                        valid_input = False
                    if element not in range(len(partitions)):
                        print('Partition {} is not present in the graph. Existing partitions are: {}'.format(
                            element, range(len(partitions))))
                        valid_input = False
                unique_parts.update(set(sequence))
                n_parts += len(sequence)
            if not len(unique_parts) == n_parts:
                print('Each partition can only occur once in the list')
                valid_input = False
            # Ask for new input if the given input is not valid
            if not valid_input:
                continue
            break

        # Print summary of the selected options
        print('Selected options:')
        print('Local convergers:', local_convergers)
        print('Jacobi convergence:', jacobi_convergence)
        print('Sequences of partitions:', sequence_partitions)

        self.graph['problem_formulation']['local_convergers'] = local_convergers
        self.graph['problem_formulation']['jacobi_convergence'] = jacobi_convergence
        self.graph['problem_formulation']['sequence_partitions'] = sequence_partitions

        return

    def get_mg_function_ordering(self):
        """Method to determine the function ordering for MDAO graphs (FPG and MDG) based on an FPG.

        :return: function ordering dictionary
        :rtype: dict

        """
        f_roles = self.FUNCTION_ROLES
        f_order = self.graph['problem_formulation']['function_order']
        search_fun = lambda x : self.find_all_fnodes(attr_cond=['problem_role', '==', f_roles[x]])
        mg_function_ordering = {f_roles[3]: [f for f in f_order if f in search_fun(3)],
                                f_roles[4]: [f for f in f_order if f in search_fun(4)],
                                f_roles[1]: [f for f in f_order if f in search_fun(1)],
                                f_roles[2]: [f for f in f_order if f in search_fun(2)]}
        return mg_function_ordering

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CONVERSION METHODS                                                    #
    # ---------------------------------------------------------------------------------------------------------------- #

    def create_mpg(self, mg_function_ordering, name='MPG'):
        """Function to automatically create a MPG based on a FPG.

        :param mg_function_ordering: dictionary with MDAO graph function ordering
        :type mg_function_ordering: dict
        :param name: name for the MPG graph
        :type name: str
        :return: unconnected FPG (only action blocks and their diagonal position)
        :rtype: MdaoProcessGraph
        """

        from kadmos.graph.graph_process import MdaoProcessGraph
        mpg = MdaoProcessGraph(kb_path=self.graph.get('kb_path'), name=name,
                               fpg=self, mg_function_ordering=mg_function_ordering)
        mpg.graph['problem_formulation'] = self.graph['problem_formulation']

        return mpg

    def create_mdg(self, mg_function_ordering, name='MDG'):
        """Function to automatically create an MDG based on an FPG.

        :param mg_function_ordering: dictionary with MDAO graph function ordering
        :type mg_function_ordering: dict
        :param name: name for the MDG graph
        :type name: str
        :return: baseline MDG (only added additional action blocks, no changed connections)
        :rtype: MdaoDataGraph
        """

        mdg = MdaoDataGraph(self, name=name, mg_function_ordering=mg_function_ordering)

        return mdg

    def determine_scope_design_variables(self, des_vars=None, coupled_functions_groups=None, pre_coupling_functions=None,
                                         post_coupling_functions=None):
        """
        Method to determine the scope (global, local) of the design variables and to determine to which coupled
        function groups the design variable belongs.


        :param des_vars: list of design variables (if not given, it is taken from the graph)
        :type des_vars: list
        :param coupled_functions_groups: list with list of coupled function groups
        :type coupled_functions_groups: list
        :param pre_coupling_functions: list with list of pre-coupled function groups
        :type pre_coupling_functions: list
        :return: list of global design variables, list of local design variables, dictionary with dependencies
        :rtype: tuple
        """

        # Start empty lists and dictionary
        global_des_vars = []
        local_des_vars = []
        des_vars_group_idxs = dict()

        # Get and check design variables
        des_vars = self.check_and_get_design_variables(des_vars=des_vars)

        # Get and check coupled function groups
        coupled_functions_groups = \
            self.check_and_get_coupled_functions_groups(coupled_functions_groups=coupled_functions_groups)

        # Get and check pre-coupling functions
        pre_coupling_functions = \
            self.check_and_get_pre_coupling_functions(pre_coupling_functions=pre_coupling_functions)

        # Get and check post-coupling functions
        post_coupling_functions = \
            self.check_and_get_post_coupling_functions(post_coupling_functions=post_coupling_functions)

        # Determine the scope of the design variables
        for des_var in des_vars:
            linked_groups = []
            for idx, coupled_functions_group in enumerate(coupled_functions_groups):
                subgraph = self.get_subgraph_by_function_nodes(pre_coupling_functions + coupled_functions_group)
                for func in coupled_functions_group:
                    if subgraph.has_node(des_var):
                        if nx.has_path(subgraph, des_var, func):
                            linked_groups.append(idx)
                            break
                    else:
                        break
            if len(linked_groups) == 0:
                # Check if design variable can be associated with one or multiple post-coupling functions
                post_funcs = []
                subgraph = self.get_subgraph_by_function_nodes(pre_coupling_functions + post_coupling_functions)
                for post_coupling_function in post_coupling_functions:
                    if subgraph.has_node(des_var) and nx.has_path(subgraph, des_var, post_coupling_function):
                        post_funcs.append(post_coupling_function)
                # Check which of these post-coupling functions are local and to which group they belong
                local_groups = set()
                for post_func in post_funcs:
                    linked_groups_post_func = []
                    for idx, coupled_functions_group in enumerate(coupled_functions_groups):
                        subgraph = self.get_subgraph_by_function_nodes(coupled_functions_group+post_coupling_functions)
                        for func in coupled_functions_group:
                            if nx.has_path(subgraph, func, post_func):
                                linked_groups_post_func.append(idx)
                                break
                    if len(linked_groups_post_func) >= 1:
                        local_groups.update(linked_groups_post_func)
                # If the variable can only be associated to one group it is a local design variable
                if len(local_groups) == 1:
                    local_des_vars.append(des_var)
                else:
                    global_des_vars.append(des_var)
                if not post_funcs:
                    logger.warning("Design variable {} could not be associated with a coupled or post-coupling "
                                   "function.".format(des_var))
            elif len(linked_groups) == 1:
                local_des_vars.append(des_var)
            else:
                global_des_vars.append(des_var)
            des_vars_group_idxs[des_var] = linked_groups

        return global_des_vars, local_des_vars, des_vars_group_idxs

    def determine_scope_constraint_functions(self, cnstrnt_vars=None, coupled_functions_groups=None,
                                             post_coupling_functions=None, pre_coupling_functions=None):
        """Method to determine the scope (global, local) of the constraint functions based on the constraint variables
        and to determine on which coupled function groups the constraint function depends.

        :param cnstrnt_vars: (optional) constraint variables to be determined
        :type cnstrnt_vars: list
        :param coupled_functions_groups: (optional) list of lists with coupled functions groups
        :type coupled_functions_groups: list
        :param post_coupling_functions: (optional) list with post-coupling functions
        :type post_coupling_functions: list
        :return: global constraint variables and functions, local constraint variables and functions, groups indices
                 per constraint function
        :rtype: tuple
        """

        # Start empty lists and dictionary
        global_cnstrnt_vars = []
        global_cnstrnt_funcs = []
        local_cnstrnt_vars = []
        local_cnstrnt_funcs = []
        cnstrnt_vars_group_idxs = dict()
        cnstrnt_funcs_group_idxs = dict()

        # Get and check coupled function groups
        coupled_functions_groups = \
            self.check_and_get_coupled_functions_groups(coupled_functions_groups=coupled_functions_groups)

        # Get and check post-coupling functions
        post_coupling_functions = \
            self.check_and_get_post_coupling_functions(post_coupling_functions=post_coupling_functions)

        # Get and check pre-coupling functions
        pre_coupling_functions = self.check_and_get_pre_coupling_functions(pre_coupling_functions=pre_coupling_functions)

        # Associate constraint variables with the constraint functions
        cnstrnt_funcs = dict()
        for cnstrnt_var in cnstrnt_vars:
            cnstrnt_func = self.get_sources(cnstrnt_var)[0]
            if cnstrnt_func not in cnstrnt_funcs:
                cnstrnt_funcs[cnstrnt_func] = [cnstrnt_var]
            else:
                cnstrnt_funcs[cnstrnt_func].append(cnstrnt_var)

        # Determine the scope of the constraint functions
        for cnstrnt_func in cnstrnt_funcs:
            linked_groups = []
            for idx, coupled_functions_group in enumerate(coupled_functions_groups):
                subgraph = self.get_subgraph_by_function_nodes(coupled_functions_group + post_coupling_functions)
                for func in coupled_functions_group:
                    if subgraph.has_node(cnstrnt_func):
                        if nx.has_path(subgraph, func, cnstrnt_func):
                            linked_groups.append(idx)
                            break
            if len(linked_groups) == 0:
                # Check if the constraint can be associated with one or multiple pre-coupling functions
                pre_funcs = []
                subgraph = self.get_subgraph_by_function_nodes(pre_coupling_functions + post_coupling_functions)
                for pre_coupling_function in pre_coupling_functions:
                    if subgraph.has_node(cnstrnt_func) and nx.has_path(subgraph, pre_coupling_function, cnstrnt_func) and pre_coupling_function != cnstrnt_func:
                        pre_funcs.append(pre_coupling_function)
                # Check which of the pre-coupling functions are local and to which group they belong
                connected_groups = set()
                for pre_func in pre_funcs:
                    linked_groups_pre_func = []
                    for idx, coupled_functions_group in enumerate(coupled_functions_groups):
                        subgraph = self.get_subgraph_by_function_nodes(pre_coupling_functions+coupled_functions_group)
                        for func in coupled_functions_group:
                            if nx.has_path(subgraph, pre_func, func):
                                linked_groups_pre_func.append(idx)
                                break
                    if len(linked_groups_pre_func) >= 1:
                        connected_groups.update(linked_groups_pre_func)
                # If the constraint can only be associated to one group it is a local design variable
                if len(connected_groups) == 1:
                    local_cnstrnt_funcs.append(cnstrnt_func)
                    local_cnstrnt_vars.extend(cnstrnt_funcs[cnstrnt_func])
                else:
                    global_cnstrnt_funcs.append(cnstrnt_func)
                    global_cnstrnt_vars.extend(cnstrnt_funcs[cnstrnt_func])
                if not pre_funcs:
                    logger.warning("Constraint function {} could not be associated with a pre-coupling or "
                                   "coupled function.".format(cnstrnt_func))
            elif len(linked_groups) == 1:
                local_cnstrnt_funcs.append(cnstrnt_func)
                local_cnstrnt_vars.extend(cnstrnt_funcs[cnstrnt_func])
            else:
                global_cnstrnt_funcs.append(cnstrnt_func)
                global_cnstrnt_vars.extend(cnstrnt_funcs[cnstrnt_func])
            for cnstrnt_var in cnstrnt_funcs[cnstrnt_func]:
                cnstrnt_vars_group_idxs[cnstrnt_var] = linked_groups
            cnstrnt_funcs_group_idxs[cnstrnt_func] = linked_groups

        return global_cnstrnt_vars, global_cnstrnt_funcs, local_cnstrnt_vars, local_cnstrnt_funcs, \
               cnstrnt_vars_group_idxs, cnstrnt_funcs_group_idxs

    def get_group_couplings(self, coupled_functions_groups=None):
        """Method to obtain group couplings and their indices.

        :param coupled_functions_groups: (optional) list of coupled function groups
        :type coupled_functions_groups: list
        :returns: group couplings present
        :rtype: list
        :returns: index of coupled groups
        :rtype: dict
        """
        # TODO: Imco check docstring

        # Get and check coupled function groups
        coupled_functions_groups = \
            self.check_and_get_coupled_functions_groups(coupled_functions_groups=coupled_functions_groups)
        all_coupled_functions = [item for sublist in coupled_functions_groups for item in sublist]

        # Create subgraph of just the coupled functions
        subgraph = self.get_subgraph_by_function_nodes(all_coupled_functions)

        # Merge the functions of each coupled group into one
        for coupled_functions_group in coupled_functions_groups:
            if len(coupled_functions_group) > 1:
                subgraph = subgraph.merge_functions(coupled_functions_group)
                # Remove selfloops that are created due to the merge
                circular_couplings = subgraph.find_all_nodes(category='variable', subcategory='all circular variables')
                for circular_coupling in circular_couplings:
                    source_func = subgraph.get_sources(circular_coupling)[0]
                    subgraph.remove_edge(circular_coupling, source_func)
        group_couplings = subgraph.find_all_nodes(category='variable', subcategory='all couplings')

        # Determine for each group coupling to which group its determination belongs
        group_couplings_groups_idx = dict()
        for group_coupling in group_couplings:
            source_func = self.get_sources(group_coupling)[0]
            for idx, coupled_function_group in enumerate(coupled_functions_groups):
                if source_func in coupled_function_group:
                    group_couplings_groups_idx[group_coupling] = idx
                    break

        return group_couplings, group_couplings_groups_idx

    def get_sys_post_couplings(self, sys_level_post_coupled, coupled_functions_groups=None):
        """Method to obtain the system-level post-couplings functions.

        :param sys_level_post_coupled: nodes with attributed problem role 'post-coupling'
        :type sys_level_post_coupled: list
        :param coupled_functions_groups: (optional) list of coupled function groups
        :type coupled_functions_groups: list
        :returns: system-level post-coupling functions
        :rtype: list
        :returns: indices ot system-level post-coupling functions
        :rtype: dict
        """
        # TODO: Imco check docstring

        # Check system-level post-coupling functions
        for fun in sys_level_post_coupled:
            assert self.has_node(fun), 'Node {} is not present in the graph.'.format(fun)
            assert 'problem_role' in self.nodes[fun], 'Node {} does not have a problem_role assigned.'.format(fun)
            assert self.nodes[fun]['problem_role'] == self.FUNCTION_ROLES[2], \
                'Node {} is does not have problem_role {}.'.format(fun, self.FUNCTION_ROLES[2])

        # Get and check coupled function groups
        coupled_functions_groups = \
            self.check_and_get_coupled_functions_groups(coupled_functions_groups=coupled_functions_groups)
        all_coupled_functions = [item for sublist in coupled_functions_groups for item in sublist]

        # Create subgraph of just the coupled and system-level post-coupling functions
        subgraph = self.get_subgraph_by_function_nodes(all_coupled_functions+sys_level_post_coupled)

        # Merge the functions of the coupled groups into one, as well as the system-level post-coupled functions
        if len(coupled_functions_groups) > 1:
            coupled_functions_groups_flat = [item for sublist in coupled_functions_groups for item in sublist]
            subgraph = subgraph.merge_functions(coupled_functions_groups_flat)
            # Remove selfloops that are created due to the merge
            circular_couplings = subgraph.find_all_nodes(category='variable', subcategory='all circular variables')
            for circular_coupling in circular_couplings:
                source_func = subgraph.get_sources(circular_coupling)[0]
                subgraph.remove_edge(circular_coupling, source_func)
        if len(sys_level_post_coupled) > 1:
            subgraph = subgraph.merge_functions(sys_level_post_coupled)
            # Remove selfloops that are created due to the merge
            circular_couplings = subgraph.find_all_nodes(category='variable', subcategory='all circular variables')
            for circular_coupling in circular_couplings:
                source_func = subgraph.get_sources(circular_coupling)[0]
                subgraph.remove_edge(circular_coupling, source_func)
        sys_post_couplings = subgraph.find_all_nodes(category='variable', subcategory='all couplings')

        # Determine for each group coupling to which group its determination belongs
        sys_post_couplings_groups_idx = dict()
        for sys_post_coupling in sys_post_couplings:
            source_func = self.get_sources(sys_post_coupling)[0]
            for idx, coupled_function_group in enumerate(coupled_functions_groups):
                if source_func in coupled_function_group:
                    sys_post_couplings_groups_idx[sys_post_coupling] = idx
                    break

        return sys_post_couplings, sys_post_couplings_groups_idx

    def get_system_level_functions(self, global_objective_function, global_cnstrnt_functions, mg_function_ordering=None,
                                   add_system_functions_to_subsystems=True):
        """Method to obtain system level functions

        :param global_objective_function: global objective function
        :type global_objective_function: str
        :param global_cnstrnt_functions: global constraint function(s)
        :type global_cnstrnt_functions: list
        :param mg_function_ordering: MdaoGraph function ordering
        :type mg_function_ordering: dict
        :return: system level functions
        :rtype: dict
        """
        # TODO: Imco check docstring

        # Initiate dictionary
        global_functions = [global_objective_function] if global_objective_function else []
        global_functions += global_cnstrnt_functions
        system_level_function_dict = dict()
        system_level_function_dict[self.FUNCTION_ROLES[1]] = []
        system_level_function_dict[self.FUNCTION_ROLES[3]] = []
        system_level_function_dict[self.FUNCTION_ROLES[4]] = []
        system_level_function_dict[self.FUNCTION_ROLES[2]] = []

        # Get and check function groups
        if mg_function_ordering is None:
            mg_function_ordering = self.get_mg_function_ordering()
        pre_desvars = copy.deepcopy(mg_function_ordering[self.FUNCTION_ROLES[3]])
        post_desvars = copy.deepcopy(mg_function_ordering[self.FUNCTION_ROLES[4]])
        post_couplings = copy.deepcopy(mg_function_ordering[self.FUNCTION_ROLES[2]])

        # Add pre-design variables functions to the dictionary
        system_level_function_dict[self.FUNCTION_ROLES[3]] = pre_desvars

        if add_system_functions_to_subsystems:
            # Add post-design variables and post-coupling functions to the dictionary if they have a dependency to one
            # of the global functions
            # Create a subgraph
            subgraph = self.get_subgraph_by_function_nodes(post_desvars + post_couplings)
            # Check each function
            for post_desvar in post_desvars:
                for global_function in global_functions:
                    if nx.has_path(subgraph, post_desvar, global_function):
                        system_level_function_dict[self.FUNCTION_ROLES[4]].append(post_desvar)
            additional_post_couplings = []
            for post_coupling in post_couplings:
                if post_coupling not in global_functions:
                    for global_function in global_functions:
                        if nx.has_path(subgraph, post_coupling, global_function):
                            additional_post_couplings.append(post_coupling)
            # This operation is done to keep the right order of the functions
            system_level_function_dict[self.FUNCTION_ROLES[2]] = [fun for fun in post_couplings if fun in
                                                                  global_functions + additional_post_couplings]
        else:
            # Add functions to the dictionary
            system_level_function_dict[self.FUNCTION_ROLES[4]] = post_desvars
            system_level_function_dict[self.FUNCTION_ROLES[2]] = post_couplings

        return system_level_function_dict

    def get_sub_level_functions(self, local_objective_function, local_cnstrnt_funcs, coupled_functions_group,
                                mg_function_ordering=None, add_system_functions_to_subsystems=True):
        """Method to obtain subsystem level functions.

        :param local_objective_function: local objective function
        :type local_objective_function: str
        :param local_cnstrnt_funcs: local constraint function(s)
        :type local_cnstrnt_funcs: list
        :param coupled_functions_group: coupled functions
        :type coupled_functions_group: list
        :param mg_function_ordering: (optional) MdaoGraph function ordering
        :type mg_function_ordering: dict
        :return: subsystem level functions
        :rtype: dict
        """
        # TODO: Imco check docstring

        # Initiate dictionary
        local_objective_function_list = [] if local_objective_function is None else [local_objective_function]
        local_functions = local_objective_function_list + local_cnstrnt_funcs
        sub_level_function_dict = dict()
        sub_level_function_dict[self.FUNCTION_ROLES[3]] = []
        sub_level_function_dict[self.FUNCTION_ROLES[4]] = []
        sub_level_function_dict[self.FUNCTION_ROLES[1]] = []
        sub_level_function_dict[self.FUNCTION_ROLES[2]] = []

        # Evaluate coupled functions group
        # Get pre-coupled functions on subsystem level
        coupling_dict = self.get_coupling_dictionary()
        pre_coupling_idx = 0
        for idx, node in enumerate(coupled_functions_group):
            if not set(coupled_functions_group[idx + 1:]).intersection(coupling_dict[node]):
                pre_coupling_idx = idx + 1
            else:
                break
        # Get post-coupled functions on subsystem level
        post_coupling_idx = len(coupled_functions_group)
        if pre_coupling_idx != len(coupled_functions_group):
            input_functions = []
            for idx, node in enumerate(coupled_functions_group):
                input_functions.extend([node for node in coupling_dict[node] if node in coupled_functions_group[idx:]])
            for idx, node in reversed(list(enumerate(coupled_functions_group))):
                if node not in input_functions:
                    post_coupling_idx = idx
                else:
                    break
        if pre_coupling_idx == len(coupled_functions_group):
            sublevel_pre_couplings = []
            sublevel_post_couplings = copy.deepcopy(coupled_functions_group)
        else:
            sublevel_pre_couplings = coupled_functions_group[:pre_coupling_idx]
            sublevel_post_couplings = coupled_functions_group[post_coupling_idx:]

        # Get and check function groups
        if mg_function_ordering is None:
            mg_function_ordering = self.get_mg_function_ordering()
        post_desvars = copy.deepcopy(mg_function_ordering[self.FUNCTION_ROLES[4]])
        post_couplings = copy.deepcopy(mg_function_ordering[self.FUNCTION_ROLES[2]])
        additional_post_couplings = []
        additional_post_desvars = []

        if add_system_functions_to_subsystems:
            # Add local functions to the dictionary
            additional_post_couplings = list(local_functions)
            # Add post-design variables and post-coupling functions to the dictionary if they have a dependency to one
            # of the global functions
            # Create a subgraph
            subgraph = self.get_subgraph_by_function_nodes(post_desvars + coupled_functions_group + post_couplings)
            # Check each function
            for post_desvar in post_desvars:
                for local_function in local_functions:
                    if nx.has_path(subgraph, post_desvar, local_function):
                        additional_post_desvars.append(post_desvar)
            for post_coupling in post_couplings:
                if post_coupling not in local_functions:
                    for local_function in local_functions:
                        if nx.has_path(subgraph, post_coupling, local_function):
                            additional_post_couplings.append(post_coupling)

        # This operation is done to keep the right order of the functions
        sub_level_function_dict[self.FUNCTION_ROLES[4]] = [func for func in post_desvars + coupled_functions_group if
                                                           func in sublevel_pre_couplings + additional_post_desvars]
        sub_level_function_dict[self.FUNCTION_ROLES[1]] = coupled_functions_group[
                                                          pre_coupling_idx:post_coupling_idx]
        sub_level_function_dict[self.FUNCTION_ROLES[2]] = [func for func in coupled_functions_group + post_couplings if
                                                           func in sublevel_post_couplings + additional_post_couplings]

        return sub_level_function_dict

    def check_and_get_pre_coupling_functions(self, pre_coupling_functions=None):
        """Method to obtain the pre-coupled functions and check them if provided

        :param pre_coupling_functions: (optional) pre-coupled function nodes
        :type pre_coupling_functions: list
        :return: pre-coupled function nodes
        :rtype: list

        Checks whether the function is a node of the graph with the problem role 'pre-coupled'
        """

        if not pre_coupling_functions:
            fun_ord = self.graph['problem_formulation']['function_ordering']
            pre_coupling_functions = fun_ord[self.FUNCTION_ROLES[3]] + fun_ord[self.FUNCTION_ROLES[4]]
        assert isinstance(pre_coupling_functions, list), \
            'The pre_coupling_functions input should be a list.'
        for pre_coupling_function in pre_coupling_functions:
            assert self.has_node(pre_coupling_function), \
                'Function {} is not a node in the graph.'.format(pre_coupling_function)
            assert 'problem_role' in self.nodes[pre_coupling_function], \
                'Function {} does not have a problem role.'.format(pre_coupling_function)
            assert self.nodes[pre_coupling_function]['problem_role'] in [self.FUNCTION_ROLES[3], self.FUNCTION_ROLES[4]], \
                'Pre-coupled function {} lacks the problem ' \
                'role "{}/{}".'.format(pre_coupling_function, self.FUNCTION_ROLES[3], self.FUNCTION_ROLES[4])
        return pre_coupling_functions

    def check_and_get_coupled_functions_groups(self, coupled_functions_groups=None):
        """Method to obtain the coupled functions and check them if provided

        :param coupling_functions_groups: (optional) coupled function groups
        :type coupling_functions_groups: list
        :return: coupled function groups
        :rtype: list

        Checks whether the function is a node of the graph with the problem role 'coupled'
        """

        if not coupled_functions_groups:
            coupled_functions_groups = self.graph['problem_formulation']['coupled_functions_groups']
        functions_found = []
        assert len(coupled_functions_groups) > 1, 'There have to be at least two coupled functions groups.'
        for coupled_functions_group in coupled_functions_groups:
            assert isinstance(coupled_functions_group, list), \
                'The elements of the coupled_functions_groups should be lists.'
            for func in coupled_functions_group:
                assert self.has_node(func), 'Function {} is not a node in the graph.'.format(func)
                assert 'problem_role' in self.nodes[func], \
                    'Function {} does not have a problem role.'.format(func)
                # TODO: with partitions in IDF, the function can also be a uncoupled-DVD or post-coupled
                #assert self.nodes[func]['problem_role'] == self.FUNCTION_ROLES[1], \
                #    'Coupled function {} lacks the problem role "{}".'.format(func, self.FUNCTION_ROLES[1])
                assert func not in functions_found, \
                    'Coupled function {} is present multiple times in the coupled_functions_group.'.format(func)
                functions_found.append(func)
        return coupled_functions_groups

    def check_and_get_post_coupling_functions(self, post_coupling_functions=None):
        """Method to obtain the post-coupled functions and check them if provided

        :param post_coupling_functions: (optional) post-coupled function nodes
        :type post_coupling_functions: list
        :return: post-coupled function nodes
        :rtype: list

        Checks whether the function is a node of the graph with the problem role 'post-coupled'
        """

        if not post_coupling_functions:
            post_coupling_functions = self.graph['problem_formulation']['function_ordering']['post-coupling']
        assert isinstance(post_coupling_functions, list), \
            'The post_coupling_functions input should be a list.'
        for post_coupling_function in post_coupling_functions:
            assert self.has_node(post_coupling_function), \
                'Function {} is not a node in the graph.'.format(post_coupling_function)
            assert 'problem_role' in self.nodes[post_coupling_function], \
                'Function {} does not have a problem role.'.format(post_coupling_function)
            assert self.nodes[post_coupling_function]['problem_role'] == self.FUNCTION_ROLES[2], \
                'Post-coupled function {} lacks the problem ' \
                'role "{}".'.format(post_coupling_function, self.FUNCTION_ROLES[2])
        return post_coupling_functions

    def check_and_get_design_variables(self, des_vars=None):
        """Method to obtain the design variable nodes and check them if provided

        :param des_vars: (optional) design variable nodes
        :type des_vars: list
        :return: design variable nodes
        :rtype: list

        Checks whether the function is a node of the graph with the problem role 'design variable'
        """
        if des_vars:
            for des_var in des_vars:
                assert self.has_node(des_var), 'Design variable {} is not a node in the graph.'.format(des_var)
                assert 'problem_role' in self.nodes[des_var], \
                    'Design variable {} does not have a problem role.'.format(des_var)
                assert self.nodes[des_var]['problem_role'] == self.PROBLEM_ROLES_VARS[0], \
                    'Design variable {} lacks the problem role "{}".'.format(des_var, self.PROBLEM_ROLES_VARS[0])
        else:
            des_vars = self.find_all_nodes(category='variable',
                                           attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
            assert len(des_vars) > 0, 'No design variables found in the graph.'
        return des_vars

    def _analyze_distributed_system(self, des_var_nodes, objective_node, constraint_nodes, mg_function_ordering,
                                    add_system_functions_to_subsystems=True):
        """Method to analyze an FPG as a distributed system to asses local and global functions and variables.

        :param des_var_nodes: design variable nodes in the graph
        :type des_var_nodes: list
        :param objective_node: objective node in the graph
        :type objective_node: str
        :param constraint_nodes: constraint nodes in the graph
        :type constraint_nodes: list
        :param mg_function_ordering: function ordering of the MDAO graph
        :type mg_function_ordering: dict
        :return: dictionary with the system analysis results
        :rtype: dict
        """

        # Get settings from graph
        coupled_functions_groups = self.graph['problem_formulation']['coupled_functions_groups']

        # Determine coupling variables between coupled_function_groups
        group_couplings, group_couplings_groups_idx = self.get_group_couplings()
        basic_group_couplings = list(group_couplings)

        # Determine objective function based on objective value
        if objective_node:
            global_objective_function = self.get_sources(objective_node)[0]
        else:
            global_objective_function = None
        # TODO: Assert that objective function only has one output

        # Determine local and global design variables
        if des_var_nodes:
            global_des_vars, local_des_vars, des_vars_group_idxs = \
                self.determine_scope_design_variables(des_vars=des_var_nodes)
        else:
            global_des_vars, local_des_vars, des_vars_group_idxs = [], [], dict()
        # TODO: assess that each discipline group is dependent on at least one design variable (?)

        # Get global and local constraints and their functions
        if constraint_nodes:
            global_cnstrnt_vars, global_cnstrnt_funcs, local_cnstrnt_vars, local_cnstrnt_funcs, \
            cnstrnt_vars_group_idxs, cnstrnt_funcs_group_idxs = \
                self.determine_scope_constraint_functions(cnstrnt_vars=constraint_nodes)
        else:
            global_cnstrnt_vars, global_cnstrnt_funcs, local_cnstrnt_vars, local_cnstrnt_funcs, \
            cnstrnt_vars_group_idxs, cnstrnt_funcs_group_idxs = [], [], [], [], [], dict()

        # Create dictionary of pre-desvar, post-desvar, and post-coupling functions for the system optimizer
        sys_functions_dict = self.get_system_level_functions(global_objective_function, global_cnstrnt_funcs,
                                                             mg_function_ordering=mg_function_ordering,
                                                             add_system_functions_to_subsystems=
                                                             add_system_functions_to_subsystems)

        # Determine couplings between coupled groups and system-level post-coupling functions
        add_group_couplings, add_group_couplings_groups_idx = \
            self.get_sys_post_couplings(sys_functions_dict[self.FUNCTION_ROLES[2]])

        # Add additional couplings to the group_couplings
        for add_group_coupling in add_group_couplings:
            if add_group_coupling not in group_couplings:
                group_couplings.append(add_group_coupling)
                group_couplings_groups_idx[add_group_coupling] = add_group_couplings_groups_idx[add_group_coupling]

        # Create dictionaries of post-desvar, coupled, and post-coupling functions per each subgroup
        subsys_functions_dicts = []
        for idx, coupled_functions_group in enumerate(coupled_functions_groups):
            # Get the local constraint functions of the current group
            local_cnstrnt_funcs_group = []
            for cnstrnt_func, groups in iteritems(cnstrnt_funcs_group_idxs):
                if idx in groups and cnstrnt_func not in global_cnstrnt_funcs:
                    local_cnstrnt_funcs_group.append(cnstrnt_func)
            subsys_functions_dict = self.get_sub_level_functions(None, local_cnstrnt_funcs_group,
                                                                 coupled_functions_group,
                                                                 mg_function_ordering=mg_function_ordering,
                                                                 add_system_functions_to_subsystems=
                                                                 add_system_functions_to_subsystems)
            # Create dict collecting the subsystem functions dictionary
            subsys_functions_dicts.append(subsys_functions_dict)

        # Add additional couplings to the group_couplings
        for add_group_coupling in add_group_couplings:
            if add_group_coupling not in group_couplings:
                group_couplings.append(add_group_coupling)
                group_couplings_groups_idx[add_group_coupling] = add_group_couplings_groups_idx[add_group_coupling]

        # Create also list with all functions at a certain level
        functions_lists = []
        functions_list = []
        for key, item in sys_functions_dict.items():
            functions_list.extend(item)
        functions_lists.append(functions_list)
        for function_dict in subsys_functions_dicts:
            functions_list = []
            for key, item in function_dict.items():
                functions_list.extend(item)
            if len(functions_lists) == 1:
                functions_lists.append([functions_list])
            else:
                functions_lists[1].append(functions_list)

        return {'des_vars': {'global': global_des_vars, 'local': local_des_vars, 'groups': des_vars_group_idxs},
                'objective': {'global_fun': global_objective_function},
                'constraints': {'global_vars': global_cnstrnt_vars, 'local_vars': local_cnstrnt_vars,
                                'global_funs': global_cnstrnt_funcs, 'local_funs': local_cnstrnt_funcs,
                                'groups_vars': cnstrnt_vars_group_idxs, 'groups_funs': cnstrnt_funcs_group_idxs},
                'couplings': {'basic': basic_group_couplings, 'extended': group_couplings,
                              'groups': group_couplings_groups_idx},
                'functions_dicts': [sys_functions_dict, subsys_functions_dicts],
                'functions_lists': functions_lists}

    def _isolate_surrogate_models(self, sa):
        """Method to isolate surrogate models and determine where certain functions belong within a distributed
        system."""

        # For each subgroup (SM) determine which pre-desvar functions are between the group and the design variables
        # to be used for the surrogate model. Add these to the subgroup.
        n_groups = len(sa['functions_dicts'][1])
        # Get the design variables of the group
        for g in range(n_groups):
            group_uncoupled_functions = set()
            group_des_vars = [des_var for des_var, groups in sa['des_vars']['groups'].items() if g in groups]
            des_vars_funs = set()
            for g_des_var in group_des_vars:
                des_var_targets = self.get_targets(g_des_var)
                des_var_targets = [t for t in des_var_targets if self.nodes[t]['problem_role'] not in [self.FUNCTION_ROLES[1], self.FUNCTION_ROLES[2]]]
                des_vars_funs.update(des_var_targets)
            subgraph = self.get_subgraph_by_function_nodes(sa['functions_dicts'][0][self.FUNCTION_ROLES[4]]+sa['functions_lists'][1][g])
            subgraph = subgraph.merge_functions(sa['functions_lists'][1][g], new_label='__merged_node__')
            for des_vars_fun in des_vars_funs:
                simple_paths = [p for p in nx.all_simple_paths(subgraph, des_vars_fun, '__merged_node__')]
                for path in simple_paths:
                    for node in path:
                        if subgraph.nodes[node]['category'] == 'function' and node != '__merged_node__':
                            group_uncoupled_functions.add(node)
            group_postdesvar_functions = [f for f in sa['functions_dicts'][0][self.FUNCTION_ROLES[4]] if f in group_uncoupled_functions]
            sa['functions_dicts'][1][g][self.FUNCTION_ROLES[4]] = group_postdesvar_functions + sa['functions_dicts'][1][g][self.FUNCTION_ROLES[4]]

        # For extended couplings from uncoupled-DVD to post-coupling determine whether they should come from one of the
        # surrogate models.
        if sa['functions_dicts'][0][self.FUNCTION_ROLES[4]]:
            subgraph1 = self.get_subgraph_by_function_nodes(sa['functions_dicts'][0][self.FUNCTION_ROLES[4]] +
                                                            sa['functions_dicts'][0][self.FUNCTION_ROLES[2]])
            subgraph2 = subgraph1.merge_functions(sa['functions_dicts'][0][self.FUNCTION_ROLES[4]], new_label='__merged_node__')
            subgraph3 = subgraph2.merge_functions(sa['functions_dicts'][0][self.FUNCTION_ROLES[2]], new_label='__merged_node2__')
            additional_couplings = set([n[2] for n in subgraph3.get_direct_coupling_nodes(['__merged_node__', '__merged_node2__'])])
        else:
            additional_couplings = set()
            subgraph1 = None
        # First check upon which design variables the additional coupling depends
        for add_coup in additional_couplings:
            depends_on = set()
            # Check whether there is a dependency between the design variables and the additional coupling
            for des_var, gs in sa['des_vars']['groups'].items():
                if subgraph1.has_node(des_var):
                    if nx.has_path(subgraph1, des_var, add_coup):
                        depends_on.add(des_var)
            # Extract the common groups from the dependencies
            common_groups = set()
            for dependency in depends_on:
                dg = set(sa['des_vars']['groups'][dependency])
                if not common_groups:
                    common_groups.update(dg)
                else:
                    common_groups.intersection(dg)
            # Raise error if there are no common groups
            if not common_groups:
                raise NotImplementedError('An extended coupling from post-desvars functions without any common groups '
                                          'has not been implemented (yet).')  # Implement by simply keeping at system level?
            elif len(common_groups) == 1:
                # Else if there is one common group, then check if all required functions are already part of that group
                # and add them, if they are not.
                add_coup_group = list(common_groups)[0]
                add_coup_source = self.get_source(add_coup)
                group_des_vars = [des_var for des_var, groups in sa['des_vars']['groups'].items() if add_coup_group in groups]
                des_vars_funs = set()
                for g_des_var in group_des_vars:
                    des_var_targets = self.get_targets(g_des_var)
                    des_var_targets = [t for t in des_var_targets if
                                       self.nodes[t]['problem_role'] != self.FUNCTION_ROLES[1]]
                    des_vars_funs.update(des_var_targets)
                required_functions = []
                for des_vars_fun in des_vars_funs:
                    simple_paths = [p for p in nx.all_simple_paths(subgraph1, des_vars_fun, add_coup_source)]
                    for path in simple_paths:
                        for node in path:
                            if subgraph1.nodes[node]['category'] == 'function':
                                if node not in required_functions:
                                    required_functions.append(node)
                for fun in required_functions:
                    if fun not in sa['functions_dicts'][1][add_coup_group][self.FUNCTION_ROLES[4]]:
                        sa['functions_dicts'][1][add_coup_group][self.FUNCTION_ROLES[4]].append(fun)
            else:  # multiple common groups
                # If there are multiple common groups, then check if the function is already part of one of them.
                # Raise error if the function is part of multiple (not implemented, but can be)
                add_coup_source = self.get_source(add_coup)
                found_groups = set()
                for common_group in common_groups:
                    group_funs = sa['functions_dicts'][1][common_group][self.FUNCTION_ROLES[4]]
                    if add_coup_source in group_funs:
                        found_groups.add(common_group)
                if len(found_groups) > 1:
                    raise NotImplementedError('For multiple common groups the function has to be used in one of them at the moment.')
                elif len(found_groups) == 1:
                    add_coup_group = list(found_groups)[0]
                else:  # If not used in any groups yet, then just keep it at the system level
                    add_coup_group = None

            # Adjust the system analysis dictionary
            if add_coup_group is not None:
                sa['couplings']['extended'].append(add_coup)
                sa['couplings']['groups'][add_coup] = add_coup_group

        # Remove the uncoupled-DVD functions from the global level
        sublevel_uncoupled_dvds = list(itertools.chain.from_iterable([item[self.FUNCTION_ROLES[4]] for item
                                                                     in sa['functions_dicts'][1]]))
        for sublevel_uncoupled_dvd in sublevel_uncoupled_dvds:
            if sublevel_uncoupled_dvd in sa['functions_dicts'][0][self.FUNCTION_ROLES[4]]:
                sa['functions_dicts'][0][self.FUNCTION_ROLES[4]].remove(sublevel_uncoupled_dvd)

        # Create/update also list with all functions at a certain level
        # TODO: this function is a repeat of an earlier function in analyze_distributed_system
        functions_lists = []
        functions_list = []
        sys_functions_dict = sa['functions_dicts'][0]
        subsys_functions_dicts = sa['functions_dicts'][1]
        for key, item in sys_functions_dict.items():
            functions_list.extend(item)
        functions_lists.append(functions_list)
        for function_dict in subsys_functions_dicts:
            functions_list = []
            for key, item in function_dict.items():
                functions_list.extend(item)
            if len(functions_lists) == 1:
                functions_lists.append([functions_list])
            else:
                functions_lists[1].append(functions_list)
        sa['functions_lists'] = functions_lists

        return sa

    def get_objective_node(self):
        """Method to get the single (or non-existent) objective node from a graph.

        :return: objective node or None if no objective node is present
        :rtype: str, None
        """
        objective_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[1]])
        assert len(objective_nodes) <= 1, 'Multiple objective nodes found: {}'.format(objective_nodes)
        if objective_nodes:
            return objective_nodes[0]
        else:
            return None

    def get_mdg(self, name='MDG', **kwargs):
        """Create the MDAO data graph for a given FPG.

        :param name: name of the new graph
        :type name: str
        :return: MDAO data graph
        :rtype: MdaoDataGraph
        """

        # Start-up checks
        logger.info('Composing MDG...')
        assert isinstance(name, string_types)
        self.add_function_problem_roles()
        self.check(raise_error=True)

        # Make clean copy of the graph to avoid unwanted links and updates
        graph = self.deepcopy()

        # Load variables from FPG
        mdao_arch = graph.graph['problem_formulation']['mdao_architecture']
        conv_type = graph.graph['problem_formulation']['convergence_type']
        if 'allow_unconverged_couplings' in graph.graph['problem_formulation']:
            allow_unconverged_couplings = graph.graph['problem_formulation']['allow_unconverged_couplings']
        else:
            allow_unconverged_couplings = False

        # Determine special variables and functions
        des_var_nodes = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[0]])
        constraint_nodes = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[2]])
        objective_node = graph.get_objective_node()
        qoi_nodes = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[3]])

        # Get the function ordering for the FPG and assign coupling function lists accordingly.
        mg_function_ordering = graph.get_mg_function_ordering()
        coup_functions = mg_function_ordering[graph.FUNCTION_ROLES[1]]

        # Set up MDAO data graph
        mdg = graph.create_mdg(mg_function_ordering, name=name)

        # Check for partitions in monolithic architectures
        if mdao_arch in graph.OPTIONS_ARCHITECTURES[1:4] and 'coupled_functions_groups' in \
                graph.graph['problem_formulation']:
            partitions = graph.graph['problem_formulation']['coupled_functions_groups']
            system_analysis = self._analyze_distributed_system(des_var_nodes, objective_node, constraint_nodes,
                                                               mg_function_ordering,
                                                               add_system_functions_to_subsystems=False)
            distr_function_ordering = system_analysis['functions_dicts']
            mdg.graph['distr_function_ordering'] = distr_function_ordering
            sub_func_orderings = distr_function_ordering[1]
        else:
            partitions = None

        # Manipulate data graph
        if mdao_arch == graph.OPTIONS_ARCHITECTURES[0]:  # unconverged-MDA
            if allow_unconverged_couplings:
                # Manipulate the coupling variables based on the architecture
                if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                                  converger=None, include_couplings_as_final_output=False)
                elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=False,
                                                  converger=None, include_couplings_as_final_output=False)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
            if partitions:
                # Connect partitions
                # noinspection PyUnboundLocalVariable
                mdg.connect_partitions(mdao_arch, sub_func_orderings, coup_functions)
                _, sys_conv, _ = mdg.get_architecture_node_ids(mdao_arch, number_of_groups=len(partitions))
            else:
                sys_conv, sys_conv_label = graph.CONVERGER_STRING, graph.CONVERGER_LABEL
                # Connect system converger
                mdg.connect_converger(sys_conv, conv_type, coup_functions, True, label=sys_conv_label)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
            # If the system converger does not have any variables connected to it due to the local convergers, it is
            # redundant and can be removed
            if not mdg.get_sources(sys_conv) and not mdg.get_targets(sys_conv):
                mdg.remove_node(sys_conv)
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[2]:  # IDF
            if partitions:
                sys_opt = graph.SYS_PREFIX + graph.OPTIMIZER_STRING
                sys_opt_label = graph.SYS_PREFIX + graph.OPTIMIZER_LABEL
                # Connect partitions
                # noinspection PyUnboundLocalVariable
                mdg.connect_partitions(mdao_arch, sub_func_orderings, coup_functions)
            else:
                sys_opt, sys_opt_label = graph.OPTIMIZER_STRING, graph.OPTIMIZER_LABEL
                # Connect optimizer as a converger using the consistency constraint function
                mdg.connect_converger(sys_opt, graph.OPTIONS_ARCHITECTURES[2], coup_functions, True,
                                      label=sys_opt_label, conv_is_optimizer=True)
            # Connect optimizer w.r.t. design variables, objective, constraints
            # noinspection PyUnboundLocalVariable
            mdg.connect_optimizer(sys_opt, des_var_nodes, objective_node, constraint_nodes, label=sys_opt_label)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[3]:  # MDF
            if partitions:
                sys_opt = graph.SYS_PREFIX + graph.OPTIMIZER_STRING
                sys_opt_label = graph.SYS_PREFIX + graph.OPTIMIZER_LABEL
                # Connect partitions
                # noinspection PyUnboundLocalVariable
                mdg.connect_partitions(mdao_arch, sub_func_orderings, coup_functions)
                _, sys_conv, _ = mdg.get_architecture_node_ids(mdao_arch, number_of_groups=len(partitions))
            else:
                sys_opt, sys_opt_label = graph.OPTIMIZER_STRING, graph.OPTIMIZER_LABEL
                sys_conv, sys_conv_label = graph.CONVERGER_STRING, graph.CONVERGER_LABEL
                # Connect system converger
                mdg.connect_converger(sys_conv, conv_type, coup_functions, True, label=sys_conv_label)
            # Connect optimizer
            # noinspection PyUnboundLocalVariable
            mdg.connect_optimizer(sys_opt, des_var_nodes, objective_node, constraint_nodes, label=sys_opt_label)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
            # If the system converger does not have any variables connected to it due to the local convergers, it is
            # redundant and can be removed
            if not mdg.get_sources(sys_conv) and not mdg.get_targets(sys_conv):
                mdg.remove_node(sys_conv)
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[4]:  # unconverged-OPT
            opt = graph.OPTIMIZER_STRING
            if allow_unconverged_couplings:
                # Manipulate the coupling variables based on the architecture
                if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                                  converger=None, include_couplings_as_final_output=True)
                elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=False,
                                                  converger=None, include_couplings_as_final_output=True)
            # Connect optimizer
            # noinspection PyUnboundLocalVariable
            mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[5]:  # unconverged-DOE
            doe = graph.DOE_STRING
            if allow_unconverged_couplings:
                # Manipulate the coupling variables based on the architecture
                if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                                  converger=None, include_couplings_as_final_output=False)
                elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=False,
                                                  converger=None, include_couplings_as_final_output=False)
            # Connect doe block
            # noinspection PyUnboundLocalVariable
            mdg.connect_doe_block(doe, des_var_nodes, qoi_nodes)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
            doe = graph.DOE_STRING
            conv = graph.CONVERGER_STRING
            # Connect converger
            mdg.connect_converger(conv, conv_type, coup_functions, False)
            # Connect doe block
            # noinspection PyUnboundLocalVariable
            mdg.connect_doe_block(doe, des_var_nodes, qoi_nodes)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[7]:  # CO
            coupled_functions_groups = graph.graph['problem_formulation']['coupled_functions_groups']
            n_groups = len(coupled_functions_groups)
            sys_opt, sub_opts = self.get_architecture_node_ids('CO', number_of_groups=n_groups)
            sys_opt_label, sub_opts_labels = self.get_architecture_node_labels('CO', number_of_groups=n_groups)

            sa = self._analyze_distributed_system(des_var_nodes, objective_node, constraint_nodes, mg_function_ordering)

            # Determine any required function instances, add them and adjust subsys_functions_dict accordingly
            sa = mdg._split_functions(sa)

            # Keep track of the design variables and constraints for the system level
            sys_lev_des_vars = set(sa['des_vars']['global'])
            sys_lev_cnstrnts = set(sa['constraints']['global_vars'])
            J_nodes = []

            # For each discipline group, localize the group, add the consistency objective function and add the
            # sub-optimizer
            for idx, subsys_functions_dict in enumerate(sa['functions_dicts'][1]):
                # Get global and local design nodes and local constraint nodes involved in the group
                subsys_functions = [item for sublist in list(itervalues(subsys_functions_dict)) for item in sublist]
                global_des_vars_group, local_des_vars_group, local_cnstrnt_vars_group, local_group_couplings_group, \
                external_group_couplings_group = get_group_vars(sa, idx)

                # Make the groups local by introducing the right copies
                local_des_vars_copies_group, global_des_vars_copies_group, mapping_des_vars = \
                    mdg.localize_design_variables(subsys_functions, global_des_vars_group, local_des_vars_group)
                sys_lev_des_vars.update(global_des_vars_copies_group)

                external_group_couplings_copies_group, local_group_couplings_copies_group, \
                mapping_locals= mdg.localize_group_couplings(subsys_functions,
                                                             external_group_couplings_group,
                                                             local_group_couplings_group, make_copies_des_vars=True)
                sys_lev_des_vars.update(external_group_couplings_copies_group+local_group_couplings_copies_group)

                # Add the consistency objective function according to CO2
                cof_mappings = mapping_des_vars.copy()
                cof_mappings.update(mapping_locals)
                group_cof_node, group_cof_obj_node = mdg.connect_consistency_objective_function(idx, cof_mappings)
                sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[2]].append(group_cof_node)
                sa['functions_lists'][1][idx].append(group_cof_node)

                # TODO: Then (optionally) add a converger or check for the removal of feedback?
                coupled_funs = sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[1]]
                coupled_subgraph = mdg.get_subgraph_by_function_nodes(coupled_funs)
                try:
                    cycles = nx.find_cycle(coupled_subgraph)
                except NetworkXNoCycle:
                    cycles = []

                if cycles:
                    raise AssertionError('Convergence within the subgroup has not yet been implemented for CO.')

                # if feedback inside the coupled group
                # mdg.connect_converger()
                # TODO: Temp fix, make all functions into post-desvar functions (future uncoupled-DVD)
                fun_roles = self.FUNCTION_ROLES
                for node in subsys_functions:
                    if mdg.nodes[node]['problem_role'] == self.FUNCTION_ROLES[1]:  # coupled
                        mdg.nodes[node]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6]
                        mg_function_ordering[fun_roles[1]].remove(node)
                        mg_function_ordering[fun_roles[4]].append(node)
                        mdg.nodes[node]['problem_role'] = fun_roles[4]
                    elif mdg.nodes[node]['problem_role'] == fun_roles[2]:  # post-coupling
                        mdg.nodes[node]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6]
                        mg_function_ordering[fun_roles[2]].remove(node)
                        mg_function_ordering[fun_roles[4]].append(node)
                        mdg.nodes[node]['problem_role'] = fun_roles[4]

                # Add and connect the sub-level optimizer
                mdg.connect_optimizer(sub_opts[idx],
                                      local_des_vars_group+local_des_vars_copies_group,
                                      group_cof_obj_node,
                                      local_cnstrnt_vars_group,
                                      label=sub_opts_labels[idx],
                                      package='SciPy', maximum_iterations=200,
                                      convergence_tolerance=1e-6, constraint_tolerance=1e-6)
                # Mark the final consistency objective value as a constraint and add it to the system level constraints
                group_cof_obj_node_final = mdg.find_all_nodes(attr_cond=['related_to_schema_node', '==',
                                                                         group_cof_obj_node])
                assert len(group_cof_obj_node_final) == 1, 'One final value for the consistency objective value is' \
                                                           ' expected, found: {}.'.format(group_cof_obj_node_final)
                J_nodes.append(group_cof_obj_node_final[0])

            # Add combined J function
            cons_sum_fun, cons_sum_node = mdg.connect_consistencies_summation(J_nodes)
            sys_lev_cnstrnts.update([cons_sum_node])
            sa['functions_dicts'][0][mdg.FUNCTION_ROLES[2]].append(cons_sum_fun)
            sa['functions_lists'][0].append(cons_sum_fun)

            # Connect the system-level optimizer
            opt_tol = kwargs.get('opt_conv_tol', 1e-3)
            mdg.connect_optimizer(sys_opt,
                                  list(sys_lev_des_vars),
                                  objective_node,
                                  list(sys_lev_cnstrnts),
                                  label=sys_opt_label,
                                  package='pyOptSparse', maximum_iterations=200,
                                  convergence_tolerance=opt_tol, constraint_tolerance=opt_tol)

            # Temp fix: make post-coupling functions into post-desvars
            for node in sa['functions_lists'][0]:
                if mdg.nodes[node]['problem_role'] == fun_roles[1]:  # coupled
                    mdg.nodes[node]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6]
                    mg_function_ordering[fun_roles[1]].remove(node)
                    mg_function_ordering[fun_roles[4]].append(node)
                    mdg.nodes[node]['problem_role'] = fun_roles[4]
                elif mdg.nodes[node]['problem_role'] == fun_roles[2]:  # post-coupling
                    mdg.nodes[node]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6]
                    mg_function_ordering[fun_roles[2]].remove(node)
                    mg_function_ordering[fun_roles[4]].append(node)
                    mdg.nodes[node]['problem_role'] = fun_roles[4]

            # Finally, connect the coordinator
            mdg.connect_coordinator()

            # Write function_ordering to the graph
            mdg.graph['distr_function_ordering'] = sa['functions_dicts']

        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[8]:  # BLISS-2000
            coupled_functions_groups = graph.graph['problem_formulation']['coupled_functions_groups']
            n_groups = len(coupled_functions_groups)
            sys_opt, sys_conv, sys_sms, sub_does, sub_opts, sub_convs = \
                self.get_architecture_node_ids(mdao_arch, number_of_groups=n_groups)
            sys_opt_label, sys_conv_label, sys_sms_labels, sub_does_labels, sub_opts_labels, sub_convs_labels = \
                self.get_architecture_node_labels(mdao_arch, number_of_groups=n_groups)

            sa = self._analyze_distributed_system(des_var_nodes, objective_node, constraint_nodes, mg_function_ordering)

            sa = self._isolate_surrogate_models(sa)

            # Determine any required function instances, add them and adjust subsys_functions_dict accordingly
            sa = mdg._split_functions(sa)

            # Keep track of the design variables and constraints for the system level
            sys_lev_des_vars = set(sa['des_vars']['global'])
            sys_lev_cnstrnts = set(sa['constraints']['global_vars'])

            # For each discipline group, localize the group, add the consistency objective function and add the
            # sub-optimizer
            prev_local_group_couplings_copies = []
            sms_outs = []
            sms_ins = []
            weight_nodes2 = []
            sm_inps_lists = []
            doe_inps_list = []
            sa['functions_dicts'][0][self.FUNCTION_ROLES[1]].extend(sys_sms)
            fun_dict_iter = copy.deepcopy(sa['functions_dicts'][1])
            for idx, subsys_functions_dict in enumerate(fun_dict_iter):
                # Get global and local design nodes and local constraint nodes involved in the group
                subsys_functions = [item for sublist in list(itervalues(subsys_functions_dict)) for item in sublist]
                global_des_vars_group, local_des_vars_group, local_cnstrnt_vars_group, local_group_couplings_group, \
                external_group_couplings_group = get_group_vars(sa, idx)

                # Make the groups local by introducing the right copies
                local_des_vars_copies_group, global_des_vars_copies_group, mapping_des_vars = \
                    mdg.localize_design_variables(subsys_functions, global_des_vars_group, local_des_vars_group)

                external_group_couplings_copies_group, local_group_couplings_copies_group, \
                mapping_locals = mdg.localize_group_couplings(subsys_functions, external_group_couplings_group +
                                                              prev_local_group_couplings_copies,
                                                              local_group_couplings_group, instances_for_externals=True,
                                                              make_copies_des_vars=True)

                # Check for the uncoupled-DVD functions if they depend on the local design variables, if not, make them
                # uncoupled-DVI
                for func in fun_dict_iter[idx][mdg.FUNCTION_ROLES[4]]:
                    if not True in [nx.has_path(mdg, ldv, func) for ldv in local_des_vars_group]:
                        sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[4]].remove(func)
                        sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[3]].append(func)
                        mdg.nodes[func]['architecture_role'] = mdg.ARCHITECTURE_ROLES_FUNS[5]  # pre-iterator

                # Add the weighted couplings objective function according to BLISS-2000
                group_wcf_node, group_wcf_obj_node, weight_nodes = \
                    mdg.connect_weighted_couplings_objective_function(idx, [f for f in local_group_couplings_group if f in sa['couplings']['basic']])
                sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[2]].append(group_wcf_node)

                # Add and connect the sub-level optimizer
                fin_des_vars, fin_obj, _, _ = mdg.connect_optimizer(sub_opts[idx], local_des_vars_group,
                                                                    group_wcf_obj_node, local_cnstrnt_vars_group,
                                                                    label=sub_opts_labels[idx],
                                                                    maximum_iterations=30)

                # Remove final output for objective
                mdg.remove_node(fin_obj)

                # (optionally) add a converger or check for the removal of feedback?
                coupled_funs = sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[1]]
                coupled_subgraph = mdg.get_subgraph_by_function_nodes(coupled_funs)
                try:
                    cycles = nx.find_cycle(coupled_subgraph)
                except NetworkXNoCycle:
                    cycles = []

                if cycles:
                    # TODO: temp fix since coupled_functions_groups now also indicates partitions
                    del coupled_subgraph.graph['problem_formulation']['coupled_functions_groups']
                    best_order = coupled_subgraph.get_possible_function_order(method='single-swap')
                    sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[1]] = best_order
                    mdg.connect_converger(sub_convs[idx], 'Gauss-Seidel', best_order, False, label=sub_convs_labels[idx])
                else:
                    for f in sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[1]]:
                        mdg.nodes[f]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6]
                    for f in sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[2]]:
                        mdg.nodes[f]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6]

                # Add local coupling nodes as final output in the graph
                lgcg_finals = []
                for node in local_group_couplings_group:
                    if mdg.get_source(node) not in sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[3]]:
                        lgcg_final = mdg.copy_node_as(node,
                                                      mdg.ARCHITECTURE_ROLES_VARS[5],  # final output variables
                                                      add_instance_if_exists=True)
                        lgcg_finals.append(lgcg_final)
                        source = mdg.get_source(node)
                        mdg.add_edge(source, lgcg_final)
                    else:
                        lgcg_finals.append(node)

                # Add and connect the sub-level DOE
                doe_des_vars = external_group_couplings_copies_group + local_des_vars_copies_group + weight_nodes
                mdg.graph['problem_formulation']['doe_settings']['runs'] = len(doe_des_vars) * mdg.F_SAMPLES_B2k
                doe_inps, doe_outs = mdg.connect_doe_block(sub_does[idx], doe_des_vars,
                                                           lgcg_finals + fin_des_vars, label=sub_does_labels[idx],
                                                           seed_adder=idx)
                # Keep track of DOE inputs for convergence check
                doe_inps_list.extend(doe_inps)

                # Add and connect the surrogate model itself
                sm_inps = []
                for weight_node in weight_nodes:
                    weight_node2 = mdg.add_instance(weight_node)
                    sm_inps.append(weight_node2)
                    weight_nodes2.append(weight_node2)
                for node in external_group_couplings_copies_group:
                    # Check for hole node for instance = 1, otherwise add instance
                    original_node = mdg.get_first_node_instance(node)
                    if mdg.in_degree(original_node) == 0:
                        node2 = original_node
                    else:
                        node2 = mdg.add_instance(node)
                    sm_inps.append(node2)
                    mdg.mark_as_design_variable(node2, ignore_outdegree=True)
                sm_inps.extend(global_des_vars_group)
                sm_out_originals = []
                for node in lgcg_finals+fin_des_vars:
                    if 'related_to_schema_node' in mdg.nodes[node]:
                        sm_out_originals.append(mdg.nodes[node]['related_to_schema_node'])
                    else:
                        sm_out_originals.append(node)
                sm_outs = mdg.connect_surrogate_model(sys_sms[idx], doe_inps, doe_outs, sm_inps, sm_out_originals,
                                                      label=sys_sms_labels[idx],
                                                      fitting_method='ResponseSurface')
                sm_inps_lists.append(sm_inps)
                sms_ins.extend(sm_inps)
                sms_outs.extend(sm_outs)

                # List to keep track of earlier created local group couplings copies
                prev_local_group_couplings_copies.extend(local_group_couplings_copies_group)

            for idx in range(len(fun_dict_iter)):
                # Clean-up, any outputs from functions that are still unconnected, can be removed
                for func in sa['functions_lists'][1][idx]:
                    for tar in mdg.get_targets(func):
                        if mdg.out_degree(tar) == 0:
                            mdg.remove_node(tar)

            # Connect the surrogate model outputs to the system-level post-coupling functions
            sms_outs_related = [mdg.nodes[node]['related_to_schema_node'] for node in sms_outs]
            balance_nodes = {}
            for func in sa['functions_dicts'][0][self.FUNCTION_ROLES[2]]:
                sources = mdg.get_sources(func)
                mdg.nodes[func]['architecture_role'] = mdg.ARCHITECTURE_ROLES_FUNS[6]
                for source in sources:
                    rel_node = mdg.nodes[source].get('related_to_schema_node')
                    if rel_node in sms_outs_related:
                        sm_node = sms_outs[sms_outs_related.index(rel_node)]
                        # Reconnect the source to the SM node, unless it is a design variable connected to a
                        # balancing function
                        if not (mdg.nodes[source].get('problem_role') == mdg.PROBLEM_ROLES_VARS[0]
                                and mdg.nodes[func].get('function_type') == 'balance'):
                            mdg.copy_edge((source, func), (sm_node, func))
                            mdg.remove_edge(source, func)
                        else:
                            if source not in balance_nodes:
                                balance_nodes.update({source: set([func])})
                            else:
                                balance_nodes[source].add(func)

            # Create and connect the consistency constraint function
            sms_outs_couplings = [node for node in sms_outs if mdg.nodes[node]['related_to_schema_node'] in
                                  sa['couplings']['basic']]
            sms_outs_couplings_related = [mdg.nodes[node]['related_to_schema_node'] for node in sms_outs_couplings]
            sms_ins2 = [node for node in sms_ins if 'related_to_schema_node' in mdg.nodes[node]]
            sms_ins_couplings = [node for node in sms_ins2 if mdg.nodes[node]['related_to_schema_node'] in
                                 sa['couplings']['basic']]
            sms_ins_couplings_related = [mdg.nodes[node]['related_to_schema_node'] for node in sms_ins_couplings]
            ccf_mapping = dict()
            for sms_out, sms_out_related in zip(sms_outs_couplings, sms_outs_couplings_related):
                if sms_out_related in sms_ins_couplings_related:
                    map_node = sms_ins_couplings[sms_ins_couplings_related.index(sms_out_related)]
                    ccf_mapping[sms_out] = map_node
                else:
                    raise NotImplementedError('Could not find the right map node somehow...')
            ccf_node, cc_nodes = mdg.connect_consistency_constraint_function(ccf_mapping,
                                                                             architecture_role=self.ARCHITECTURE_ROLES_FUNS[6])
            sa['functions_dicts'][0][self.FUNCTION_ROLES[2]].append(ccf_node)

            # Connect a balance nodes
            for bnode, targets in balance_nodes.items():
                node_matches = [x for x in list(itervalues(ccf_mapping)) if
                                (mdg.nodes[bnode]['related_to_schema_node'] == mdg.nodes[x]['related_to_schema_node'])]
                assert len(node_matches) == 1, 'Could not match the balance node to a design variable.'
                node_match = node_matches[0]
                for trgt in targets:
                    mdg.copy_edge((bnode, trgt), (node_match, trgt))
                    mdg.remove_edge(bnode, trgt)

            # Connect the system-level optimizer
            fin_des_vars, fin_obj, _, ini_guess_nodes = mdg.connect_optimizer(sys_opt,
                                                                        list(sys_lev_des_vars)+weight_nodes2 +
                                                                        list(itervalues(ccf_mapping)),
                                                                        objective_node, list(sys_lev_cnstrnts)+cc_nodes,
                                                                        label=sys_opt_label,
                                                                        package='pyOptSparse',
                                                                        convergence_tolerance=1e-6,
                                                                        constraint_tolerance=1e-6)

            # Connect distributed system converger
            fin_sys_lev_des_vars = [node for node in fin_des_vars if
                                    mdg.nodes[node]['related_to_schema_node'] in sys_lev_des_vars]
            mdg.connect_distributed_system_converger(sys_conv, fin_des_vars + [fin_obj],
                                                     doe_inps_list + ini_guess_nodes, label=sys_conv_label)

            # Connect final objective also to coordinator
            mdg.add_edge(fin_obj, mdg.COORDINATOR_STRING)

            # Finally, connect the coordinator
            mdg.connect_coordinator(additional_inputs=fin_sys_lev_des_vars)

            # Remove hole variable nodes
            holes = mdg.find_all_nodes(category='variable', subcategory='hole')
            for hole in holes:
                mdg.remove_node(hole)

            # Write function_ordering to the graph
            mdg.graph['distr_function_ordering'] = sa['functions_dicts']

        logger.info('Composed MDG.')

        return mdg

    def impose_mdao_architecture(self):
        """Method to directly get both the MDG and MPG of an FPG.

        :return: MdaoDataGraph and MdaoProcessGraph
        :rtype: tuple
        """
        mdg = self.get_mdg()
        mpg = mdg.get_mpg()
        return mdg, mpg


class MdaoDataGraph(DataGraph, MdaoMixin):

    def __init__(self, *args, **kwargs):
        super(MdaoDataGraph, self).__init__(*args, **kwargs)
        if 'mg_function_ordering' in kwargs:
            mg_function_ordering = kwargs['mg_function_ordering']
            self._add_action_blocks_and_roles(mg_function_ordering)
            self.graph['function_ordering'] = mg_function_ordering

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CHECKING METHODS                                                      #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _check_category_a(self):
        """Extended method to perform a category A check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(MdaoDataGraph, self)._check_category_a()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')
        var_nodes = self.find_all_nodes(category='variable')

        # Get information
        n_nodes = self.number_of_nodes()
        n_functions = len(func_nodes)
        n_variables = len(var_nodes)

        # Checks on nodes
        category_check, i = check(n_nodes != (n_functions+n_variables),
                                  'The number of total nodes does not match number of function and variable nodes.',
                                  status=category_check,
                                  category='A',
                                  i=i)
        for node in var_nodes:
            category_check, i_not = check(self.in_degree(node) == 0,
                                          'The node %s has in-degree 0.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i)
            category_check, i_not = check(self.out_degree(node) == 0,
                                          'The node %s has out-degree 0.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i+1)
        i += 1
        category_check, i = check(not self.has_node(self.COORDINATOR_STRING),
                                  'The %s node is missing in the graph.' % self.COORDINATOR_STRING,
                                  status=category_check,
                                  category='A',
                                  i=i)
        for node in func_nodes:
            category_check, i_not = check('architecture_role' not in self.nodes[node],
                                          'The architecture_role attribute is missing on the node %s.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1

        # Return
        return category_check, i

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _create_cmdows_workflow_problem_def(self):

        # Create workflow/problemDefinitionUID
        cmdows_workflow_problem_def = Element('problemDefinitionUID')
        cmdows_workflow_problem_def.text = (str(self.graph['problem_formulation'].get('mdao_architecture')) +
                                            str(self.graph['problem_formulation'].get('convergence_type')))

        return cmdows_workflow_problem_def

    def _create_cmdows_architecture_elements(self):

        # Create architectureElement
        cmdows_architecture_elements = Element('architectureElements')

        # Create architectureElements/parameters
        cmdows_parameters = cmdows_architecture_elements.add('parameters')
        # Create architectureElements/parameters/instances
        # noinspection PyUnusedLocal
        cmdows_instances = cmdows_parameters.add('instances')
        # TODO: Implement this
        # Create architectureElements/parameters/...
        for architecture_roles_var in self.ARCHITECTURE_ROLES_VARS:
            cmdows_parameter = cmdows_parameters.add(make_camel_case(architecture_roles_var, make_plural_option=True))
            graph_parameter_nodes = self.find_all_nodes(attr_cond=['architecture_role', '==', architecture_roles_var])
            for graph_parameter_node in graph_parameter_nodes:
                cmdows_parameter_node = cmdows_parameter.add(make_camel_case(architecture_roles_var))
                cmdows_parameter_node.set('uID', graph_parameter_node)
                instance = int(self.nodes[graph_parameter_node].get('instance'))
                if instance > 0:
                    cmdows_parameter_node.add('relatedInstanceUID',
                                              self.get_first_node_instance(graph_parameter_node))
                else:
                    cmdows_parameter_node.add('relatedParameterUID',
                                              self.nodes[graph_parameter_node].get('related_to_schema_node'))
                cmdows_parameter_node.add('label',
                                          self.nodes[graph_parameter_node].get('label'))
                cmdows_parameter_node.add('instanceID', instance+1)
        # Create architectureElements/executableBlocks
        cmdows_executable_blocks = cmdows_architecture_elements.add('executableBlocks')
        # Create architectureElements/executableBlocks/...
        for architecture_roles_fun in self.CMDOWS_ARCHITECTURE_ROLE_SPLITTER:
            graph_nodes = self.find_all_nodes(attr_cond=['architecture_role', '==', architecture_roles_fun])
            cmdows_executable_block = cmdows_executable_blocks.add(make_camel_case(architecture_roles_fun,
                                                                                   make_plural_option=True))
            # Create architectureElements/executableBlocks/.../...
            for graph_node in graph_nodes:
                cmdows_executable_block_elem = cmdows_executable_block.add(make_camel_case(architecture_roles_fun))
                cmdows_executable_block_elem.set('uID', graph_node)
                cmdows_executable_block_elem.add('label', self.nodes[graph_node].get('label'))
                if architecture_roles_fun == 'optimizer':
                    cmdows_executable_block_elem.add('settings', self.nodes[graph_node].get('settings'),
                                                     camel_case_conversion=True)
                    graph_des_vars = [{'designVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[0] + var} for var in
                                      self.nodes[graph_node].get('design_variables')]
                    cmdows_executable_block_elem.add('designVariables', graph_des_vars)
                    graph_obj_vars = [{'objectiveVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[1] + var} for var in
                                      self.nodes[graph_node].get('objective_variable')]
                    cmdows_executable_block_elem.add('objectiveVariables', graph_obj_vars)
                    graph_con_vars = [{'constraintVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[2] + var} for var in
                                      self.nodes[graph_node].get('constraint_variables')]
                    cmdows_executable_block_elem.add('constraintVariables', graph_con_vars)
                elif architecture_roles_fun == 'doe':
                    graph_settings = self.nodes[graph_node].get('settings')
                    if graph_settings is not None:
                        cmdows_settings = cmdows_executable_block_elem.add('settings')
                        cmdows_settings.add('method', graph_settings.get('method'))
                        if graph_settings.get('runs') is not None:
                            cmdows_settings.add('runs', graph_settings.get('runs'))
                        if graph_settings.get('center_runs') is not None:
                            cmdows_settings.add('centerRuns', graph_settings.get('center_runs'))
                        if graph_settings.get('seed') is not None:
                            cmdows_settings.add('seed', graph_settings.get('seed'))
                        if graph_settings.get('levels') is not None:
                            cmdows_settings.add('levels', graph_settings.get('levels'))
                        if graph_settings.get('table') is not None:  # TODO: Temp fix, doe should have settings
                            cmdows_table = cmdows_settings.add('table')
                            for graph_row_index, graph_row in enumerate(graph_settings.get('table_order')):
                                cmdows_row = cmdows_table.add('tableRow',
                                                              attrib={'relatedParameterUID': str(graph_row)})
                                for graph_element_index, graph_element in enumerate(graph_settings.get('table')):
                                    cmdows_row.add('tableElement', str(format(float(graph_element[graph_row_index]),
                                                                              '.12f')),
                                                   attrib={'experimentID': str(graph_element_index)})
                        graph_des_vars = [{'designVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[0] + var} for var in
                                          self.nodes[graph_node].get('design_variables')]
                        cmdows_executable_block_elem.add('designVariables', graph_des_vars)
                elif architecture_roles_fun == 'surrogate model':
                    training_settings = self.nodes[graph_node].get('training')
                    if training_settings is not None:
                        cmdows_training = cmdows_executable_block_elem.add('training')
                        cmdows_training_inps = cmdows_training.add('inputs')
                        for tr_inp in self.nodes[graph_node]['training']['inputs']:
                            el_inp = cmdows_training_inps.add('input')
                            el_inp.add('parameterUID', tr_inp)
                        cmdows_training_outs = cmdows_training.add('outputs')
                        for tr_out in self.nodes[graph_node]['training']['outputs']:
                            el_out = cmdows_training_outs.add('output')
                            el_out.add('parameterUID', tr_out)
                        cmdows_training.add('settings', self.nodes[graph_node]['training']['settings'],
                                            camel_case_conversion=True)
                    prediction_settings = self.nodes[graph_node].get('prediction')
                    if prediction_settings is not None:
                        cmdows_prediction = cmdows_executable_block_elem.add('prediction')
                        cmdows_prediction_inps = cmdows_prediction.add('inputs')
                        for pr_inp in self.nodes[graph_node]['prediction']['inputs']:
                            el_inp = cmdows_prediction_inps.add('input')
                            el_inp.add('parameterUID', pr_inp)
                        cmdows_prediction_outs = cmdows_prediction.add('outputs')
                        for pr_out in self.nodes[graph_node]['prediction']['outputs']:
                            el_out = cmdows_prediction_outs.add('output')
                            el_out.add('parameterUID', pr_out)
                else:
                    cmdows_executable_block_elem.add('settings', self.nodes[graph_node].get('settings'),
                                                     camel_case_conversion=True)

        # Create architectureElements/executableBlocks/...Analyses/...
        architecture_roles_funs = np.setdiff1d(self.ARCHITECTURE_ROLES_FUNS, self.CMDOWS_ARCHITECTURE_ROLE_SPLITTER,
                                               assume_unique=True)
        for architecture_roles_fun in architecture_roles_funs:
            nodes = self.find_all_nodes(attr_cond=['architecture_role', '==', str(architecture_roles_fun)])
            cmdows_analyses = cmdows_executable_blocks.add(make_camel_case(architecture_roles_fun,
                                                                           make_plural_option=True))
            for node in nodes:
                cmdows_analysis = cmdows_analyses.add(make_camel_case(architecture_roles_fun))
                cmdows_analysis.add('relatedExecutableBlockUID', node)

        return cmdows_architecture_elements

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             LOAD METHODS                                                         #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _load_cmdows_architecture_elements(self, cmdows):

        # Create architecture element nodes
        cmdows_architecture_parameters = cmdows.find('architectureElements/parameters')
        if cmdows_architecture_parameters is not None:
            for cmdows_architecture_parameter in list(cmdows_architecture_parameters):
                for cmdows_single_architecture_parameter in list(cmdows_architecture_parameter):
                    cmdows_uid = cmdows_single_architecture_parameter.get('uID')
                    attrb = cmdows.finddict(cmdows_single_architecture_parameter, ordered=False,
                                            camel_case_conversion=True)
                    attrb = translate_dict_keys(attrb, {'related_parameter_u_i_d': 'related_to_schema_node',
                                                        'instance_id': 'instance'})
                    if 'instance' in attrb:
                        attrb['instance'] -= 1
                    self.add_node(cmdows_uid,
                                  attr_dict=attrb,
                                  category='variable',
                                  architecture_role=unmake_camel_case(cmdows_single_architecture_parameter.tag, ' '))
        cmdows_architecture_exe_blocks = cmdows.find('architectureElements/executableBlocks')
        for cmdows_architecture_exe_block in list(cmdows_architecture_exe_blocks):
            for cmdows_single_architecture_exe_block in list(cmdows_architecture_exe_block):
                cmdows_uid = cmdows_single_architecture_exe_block.get('uID')

                if cmdows_uid is not None:
                    role = unmake_camel_case(cmdows_single_architecture_exe_block.tag, ' ')
                    self.add_node(cmdows_uid,
                                  category='function',
                                  architecture_role=role,
                                  label=cmdows_single_architecture_exe_block.findasttext('label'),
                                  settings=cmdows_single_architecture_exe_block.findasttext('settings'))
                    if role == 'optimizer' or role == 'doe':
                        cmdows_des_vars = cmdows_single_architecture_exe_block.findall('designVariables/designVariable')
                        graph_des_vars = [var.findtext('designVariableUID')[10:] for var in list(cmdows_des_vars)]
                        self.nodes[cmdows_uid]['design_variables'] = graph_des_vars
                    if role == 'converger' or role == 'optimizer' or role == 'distributed system converger':
                        if 'settings' not in self.nodes[cmdows_uid] or self.nodes[cmdows_uid]['settings'] is None:
                            self.nodes[cmdows_uid]['settings'] = {}
                        if role == 'converger':
                            setting_options = OrderedDict([('linear_solver', 'linearSolver'),
                                                           ('nonlinear_solver', 'nonlinearSolver')])
                            solver_settings_options = \
                                OrderedDict([('method', 'method'),
                                             ('last_iterations_to_consider', 'lastIterationsToConsider'),
                                             ('maximum_iterations', 'maximumIterations'),
                                             ('convergence_tolerance_relative', 'convergenceToleranceRelative'),
                                             ('convergence_tolerance_absolute', 'convergenceToleranceAbsolute')])
                        elif role == 'distributed system converger':
                            setting_options = \
                                OrderedDict([('method', 'method'),
                                             ('maximum_iterations', 'maximumIterations'),
                                             ('convergence_tolerance_relative',
                                              'convergenceToleranceRelative'),
                                             ('convergence_tolerance_absolute',
                                              'convergenceToleranceAbsolute')])
                            des_var_facs_options = \
                                OrderedDict([('k_bound_reduction', 'kBoundReduction'),
                                             ('interval_increase_relative', 'intervalIncreaseRelative'),
                                             ('interval_increase_absolute', 'intervalIncreaseAbsolute'),
                                             ('interval_range_minimum', 'intervalRangeMinimum')])
                        else:
                            setting_options = \
                                OrderedDict([('package', 'package'),
                                             ('algorithm', 'algorithm'),
                                             ('maximum_iterations', 'maximumIterations'),
                                             ('apply_scaling', 'applyScaling'),
                                             ('maximum_function_evaluations', 'maximumFunctionEvaluations'),
                                             ('constraint_tolerance', 'constraintTolerance'),
                                             ('convergence_tolerance', 'convergenceTolerance')])
                        for setting_option in setting_options:
                            if setting_option == 'apply_scaling':
                                bool_options = {'true': True, 'false': False}
                                self.nodes[cmdows_uid]['settings'][setting_option] = \
                                    bool_options[cmdows_single_architecture_exe_block.findtext('settings/' +
                                                                                               setting_options
                                                                                               [setting_option])]
                            else:
                                if role == 'optimizer':
                                    self.nodes[cmdows_uid]['settings'][setting_option] = \
                                        cmdows_single_architecture_exe_block.findtext('settings/' +
                                                                                      setting_options[setting_option])
                                elif role == 'converger':
                                    self.nodes[cmdows_uid]['settings'][setting_option] = \
                                        OrderedDict((((key, cmdows_single_architecture_exe_block.findtext('settings/' +
                                             setting_options[setting_option] + '/' + solver_settings_options[key])) for
                                                      key in solver_settings_options)))
                                elif role == 'distributed system converger':
                                    self.nodes[cmdows_uid]['settings'] = \
                                        OrderedDict((((key, cmdows_single_architecture_exe_block
                                                       .findtext('settings/' + setting_options[key]))
                                                      for key in setting_options)))
                                    des_var_facs = cmdows_single_architecture_exe_block.find('settings/designVariableFactors')
                                    self.nodes[cmdows_uid]['settings']['design_variable_factors'] = \
                                        OrderedDict((((key, des_var_facs.findtext(
                                                        des_var_facs_options[key]))
                                                      for key in des_var_facs_options)))

                    if role == 'optimizer':
                        cmdows_des_vars = \
                            cmdows_single_architecture_exe_block.findall('objectiveVariables/objectiveVariable')
                        graph_des_vars = [var.findtext('objectiveVariableUID')[10:] for var in list(cmdows_des_vars)]
                        self.nodes[cmdows_uid]['objective_variable'] = graph_des_vars
                        cmdows_des_vars = \
                            cmdows_single_architecture_exe_block.findall('constraintVariables/constraintVariable')
                        graph_des_vars = [var.findtext('constraintVariableUID')[10:] for var in list(cmdows_des_vars)]
                        self.nodes[cmdows_uid]['constraint_variables'] = graph_des_vars
                    elif role == 'doe':
                        cmdows_rows = list(cmdows_single_architecture_exe_block.findall('settings/table/tableRow'))
                        graph_rows = [cmdows_row.get('relatedParameterUID') for cmdows_row in cmdows_rows]
                        graph_table = []
                        for cmdows_row in cmdows_rows:
                            def get_experiment_id(elem):
                                return float(elem.get('experimentID'))
                            elements = sorted(cmdows_row, key=get_experiment_id)
                            entry = []
                            for element in elements:
                                entry.append(format(element.findasttext(), '.12f'))
                            graph_table.append(entry)
                        graph_table = list(map(list, zip(*graph_table)))
                        if 'settings' not in self.nodes[cmdows_uid] or self.nodes[cmdows_uid]['settings'] is None:
                            self.nodes[cmdows_uid]['settings'] = {}
                        self.nodes[cmdows_uid]['settings']['table_order'] = graph_rows
                        self.nodes[cmdows_uid]['settings']['table'] = graph_table
                        self.nodes[cmdows_uid]['settings']['method'] = \
                            cmdows_single_architecture_exe_block.findtext('settings/method')
                        self.nodes[cmdows_uid]['settings']['runs'] = \
                            cmdows_single_architecture_exe_block.findtext('settings/runs')
                        self.nodes[cmdows_uid]['settings']['center_runs'] = \
                            cmdows_single_architecture_exe_block.findtext('settings/centerRuns')
                        self.nodes[cmdows_uid]['settings']['seed'] = \
                            cmdows_single_architecture_exe_block.findtext('settings/seed')
                        self.nodes[cmdows_uid]['settings']['levels'] = \
                            cmdows_single_architecture_exe_block.findtext('settings/levels')
                    elif role == 'surrogate model':
                        training_inputs = cmdows_single_architecture_exe_block.findall(
                            'training/inputs/input/parameterUID')
                        training_outputs = cmdows_single_architecture_exe_block.findall(
                            'training/outputs/output/parameterUID')
                        training_fitting_method = cmdows_single_architecture_exe_block.findtext(
                            'training/settings/fittingMethod')
                        self.nodes[cmdows_uid]['training'] = OrderedDict((('inputs', [tr_inp.text for tr_inp in training_inputs]),
                                                                          ('outputs', [tr_out.text for tr_out in training_outputs]),
                                                                          ('settings', OrderedDict((('fitting_method', training_fitting_method),)))))
                        prediction_inputs = cmdows_single_architecture_exe_block.findall('prediction/inputs/input/parameterUID')
                        prediction_outputs = cmdows_single_architecture_exe_block.findall('prediction/outputs/output/parameterUID')
                        self.nodes[cmdows_uid]['prediction'] = OrderedDict(
                            (('inputs', [pr_inp.text for pr_inp in prediction_inputs]),
                             ('outputs', [pr_out.text for pr_out in prediction_outputs])))
                else:
                    for role in self.ARCHITECTURE_ROLES_FUNS:
                        cmdows_role_name = make_camel_case(role)
                        if cmdows_single_architecture_exe_block.tag == cmdows_role_name:
                            cmdows_uid = cmdows_single_architecture_exe_block.find('relatedExecutableBlockUID').text
                            self.nodes[cmdows_uid]['architecture_role'] = role

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _add_action_blocks_and_roles(self, mg_function_ordering):
        """Method to add function blocks to the MDG based on the FPG function ordering

        :param mg_function_ordering: ordered list of functions to be added
        :type mg_function_ordering: list
        """

        # Set input settings
        mdao_arch = self.graph['problem_formulation']['mdao_architecture']

        # Add coordinator node
        assert not self.has_node(self.COORDINATOR_STRING), 'Coordinator name already in use in FPG.'
        self.add_node(self.COORDINATOR_STRING,
                      category='function',
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[0],
                      shape='8',
                      label=self.COORDINATOR_LABEL,
                      level=None)

        # Optimizer / DOE present
        if self.FUNCTION_ROLES[3] in mg_function_ordering:
            # Add pre-optimizer functions
            functions = mg_function_ordering[self.FUNCTION_ROLES[3]]
            for func in functions:
                self.nodes[func]['architecture_role'] = 'uncoupled-des-var-ind analysis'
            # Add optimizer / DOE
            if mdao_arch == self.OPTIONS_ARCHITECTURES[4]:  # unc-OPT
                assert not self.has_node(self.OPTIMIZER_STRING), 'Optimizer name already in use in FPG.'
                self.add_node(self.OPTIMIZER_STRING,
                              category='function',
                              architecture_role=self.ARCHITECTURE_ROLES_FUNS[1],
                              shape='8',
                              label=self.OPTIMIZER_LABEL,
                              settings=OrderedDict([('package', 'SciPy'),
                                                    ('algorithm', 'SLSQP'),
                                                    ('maximum_iterations', 1000),
                                                    ('maximum_function_evaluations', 1000),
                                                    ('convergence_tolerance', 1e-6),
                                                    ('constraint_tolerance', 1e-6),
                                                    ('apply_scaling', True)]))
            elif mdao_arch in self.OPTIONS_ARCHITECTURES[5:7]:  # unc-DOE, con-DOE
                assert not self.has_node(self.DOE_STRING), 'DOE name already in use in FPG.'
                self.add_node(self.DOE_STRING,
                              category='function',
                              architecture_role=self.ARCHITECTURE_ROLES_FUNS[3],  # doe
                              shape='8',
                              label=self.DOE_LABEL,
                              settings=self.graph['problem_formulation']['doe_settings'])
            # Add architecture role to post-iterator functions
            functions = mg_function_ordering[self.FUNCTION_ROLES[4]]
            for func in functions:
                self.nodes[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6]

        # Add architecture role to coupled functions
        for func in mg_function_ordering[self.FUNCTION_ROLES[1]]:
            self.nodes[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[7]

        # Add post-coupling functions
        for func in mg_function_ordering[self.FUNCTION_ROLES[2]]:
            self.nodes[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[8]

        return

    def _split_functions(self, sa):
        """
        This method splits the functions in case multiple instances are required based on the system analysis and
        updates the system analysis accordingly.

        :param sa: System analysis results for distributed systems.
        :type sa: dict
        :return: updated system analysis
        :rtype: dict
        """

        # For the functions at system level check if their output is used at the subsystem level.
        sa_fun_lists = sa['functions_lists']

        # Copy the graph for merging
        sys_funs = sa_fun_lists[0]
        sub_funs = sa_fun_lists[1]

        function_instances = dict()
        # First function instances between system level and sub-level
        for idx in range(len(sub_funs)):
            for sub_fun in sub_funs[idx]:
                if sub_fun in sys_funs:
                    function_instances[sub_fun] = {'group_idx': idx,
                                                   'serving': [fun for fun in sub_funs[idx] if
                                                               set(self.get_targets(sub_fun))
                                                                   .intersection(set(self.get_sources(fun)))]}
        # Then function instances between sub-levels
        # TODO: Now the instance creation is limited to one instance for a certain function while this could be more...
        for idx in range(len(sub_funs)-1):
            for idy in range(idx+1, len(sub_funs)):
                for sub_funx in sub_funs[idx]:
                    if sub_funx in sub_funs[idy]:
                        function_instances[sub_funx] = {'group_idx': idy,
                                                        'serving': [fun for fun in sub_funs[idy] if
                                                                   set(self.get_targets(sub_funx))
                                                                       .intersection(set(self.get_sources(fun)))]}

        for f_ins, f_det in function_instances.items():
            new_instance = self.add_function_instance(f_ins, serves=f_det['serving'])
            idx_list = sa_fun_lists[1][f_det['group_idx']].index(f_ins)
            sa_fun_lists[1][f_det['group_idx']][idx_list] = new_instance
            # TODO: this is a temporary workaround that should be fixed...
            key_term = str(self.nodes[f_ins]['architecture_role'])
            key_term = key_term.replace('iterator', 'desvars').replace('pre-coupling', 'pre-desvars')\
                .replace(' analysis', '')
            idx_dict = sa['functions_dicts'][1][f_det['group_idx']][key_term].index(f_ins)
            sa['functions_dicts'][1][f_det['group_idx']][key_term][idx_dict] = new_instance
        return sa

    def copy_node_as(self, node, architecture_role, add_instance_if_exists=False, ignore_duplicates=True):
        """Method to copy a given node for an architecture role.

        :param node: node to be copied
        :type node: str
        :param architecture_role: architecture role of the copied node
        :type architecture_role: str
        :param add_instance_if_exists: option to create another instance if copy already exists
        :type add_instance_if_exists: bool
        :param ignore_duplicates: option to ignore if the creation of an existing node is attempted
        :type ignore_duplicates: bool
        :return: modified node
        """

        assert self.has_node(node), "Node %s is not present in the graph." % node
        assert architecture_role in self.ARCHITECTURE_ROLES_VARS, "Invalid architecture role %s specified." % \
                                                                  architecture_role
        xpath_nodes = node.split('/')
        root = xpath_nodes[1]
        node_data_dict = copy.deepcopy(dict(self.nodes[node]))

        if architecture_role == self.ARCHITECTURE_ROLES_VARS[6]:  # consistency constraint variable
            new_node = '/' + root + '/architectureNodes/' + make_camel_case(architecture_role) + 's' + \
                       '/' + root + 'Copy/' + '/'.join(xpath_nodes[2:-1]) + '/gc_' + xpath_nodes[-1]
            # TODO: This needs to be fixed, now used to make RCE WF work for IDF (g_y1) instead of (y1)
        else:
            new_node = '/' + root + '/architectureNodes/' + make_camel_case(architecture_role) + 's' + \
                       '/' + root + 'Copy/' + '/'.join(xpath_nodes[2:])
        if architecture_role == self.ARCHITECTURE_ROLES_VARS[0]:  # initial guess coupling variable
            label_prefix = ''
            label_suffix = '^{c0}'
        elif architecture_role in [self.ARCHITECTURE_ROLES_VARS[1],
                                   self.ARCHITECTURE_ROLES_VARS[5]]:  # final coupling/output variable
            label_prefix = ''
            label_suffix = '^{*}'
        elif architecture_role in [self.ARCHITECTURE_ROLES_VARS[2],
                                   self.ARCHITECTURE_ROLES_VARS[9]]:  # coupling / design copy variable
            label_prefix = ''
            label_suffix = '^{c}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[3]:  # initial guess design variable
            label_prefix = ''
            label_suffix = '^{0}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[4]:  # final design variable
            label_prefix = ''
            label_suffix = '^{*}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[6]:  # consistency constraint variable
            label_prefix = 'gc_'
            label_suffix = ''
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[7]:  # doe input samples
            label_prefix = 'DOE_'
            label_suffix = '_{inp}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[8]:  # doe output samples
            label_prefix = 'DOE_'
            label_suffix = '_{out}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[10]:  # SM approximate
            label_prefix = ''
            label_suffix = '^{a}'
        else:
            raise IOError('Label extension could not be found.')

        # Determine the related schema node
        if 'related_to_schema_node' not in node_data_dict:
            node_data_dict['related_to_schema_node'] = node

        if architecture_role == self.ARCHITECTURE_ROLES_VARS[9]:
            node_data_dict.update({'problem_role': self.PROBLEM_ROLES_VARS[0]})
        else:
            if 'problem_role' in node_data_dict:
                del node_data_dict['problem_role']

        if not self.has_node(new_node):
            node_data_dict['label'] = label_prefix + get_correctly_extended_latex_label(node_data_dict['label'], label_suffix)
            node_data_dict['architecture_role'] = architecture_role
            node_data_dict['instance'] = 0
            self.add_node(new_node,
                          attr_dict=node_data_dict)
        elif self.has_node(new_node):
            if not ignore_duplicates:
                raise AssertionError('Node {} that is created as copy already exists in the graph.'.format(new_node))
            elif add_instance_if_exists:
                highest_instance = self.get_highest_instance(new_node)
                node_data_dict['instance'] = highest_instance+1
                self.copy_node_with_suffix(new_node, self.INSTANCE_SUFFIX + str(highest_instance+1),
                                           '^{i' + str(highest_instance+1) + '}',
                                           #instance=highest_instance+1,
                                           #related_to_schema_node=node,
                                           attr_dict=node_data_dict)
                new_node = new_node + self.INSTANCE_SUFFIX + str(highest_instance+1)
        return new_node

    def connect_qoi_nodes_as_input(self, nodes, function, override_with_final_outputs):
        """Method to connect a list of qoi nodes as input to a given function node.

        :param nodes: list of nodes to be connected as input
        :type nodes: list
        :param function: function to which the nodes are connected
        :type function: str
        :param override_with_final_outputs: setting on whether to override the use of final outputs
        :type override_with_final_outputs: bool
        """

        for node in nodes:
            assert self.has_node(node)
            # Check if there is a final output node as well and use that one instead.
            if override_with_final_outputs:
                schema_related_nodes = self.find_all_nodes(category='variable',
                                                           attr_cond=['related_to_schema_node', '==', node])
                for schema_related_node in schema_related_nodes:
                    if 'architecture_role' in self.nodes[schema_related_node]:
                        if self.nodes[schema_related_node]['architecture_role'] in \
                                get_list_entries(self.ARCHITECTURE_ROLES_VARS, 1, 4, 5):
                            node = schema_related_node
            self.add_edge(node, function)

        return

    def connect_consistency_objective_function(self, group_idx, ccv_mappings):
        """Method to add a consistency objective function. A consistency objective function between related values
        y_1, y_1^c, y_2 and y_2^c would be: (((y_1 - y_1^c)/y_1_scaler)^2 + ((y_2 - y_2^c)/y_2_scaler)^2)**0.5

        :param group_idx: index of the subgroup
        :type group_idx: int
        :param ccv_mappings: mapping between original inputs and copies to be made consistent.
        :type ccv_mappings: dict
        :return: the new function node and its output objective value
        :rtype: tuple
        """

        # Add the consistency constraint objective function (as generic function node, since it will be made as a
        # mathematical function)
        new_function_node = self.COF_STRING + str(group_idx) + self.COF_SUFFIX
        assert not self.has_node(new_function_node), \
            'The automatically generated function {} somehow already exists.'.format(new_function_node)
        self.add_fnode(new_function_node,
                       label=self.COF_LABEL + str(group_idx),
                       problem_role=self.FUNCTION_ROLES[4],  # post-coupling
                       architecture_role=self.ARCHITECTURE_ROLES_FUNS[6],  # post-coupling analysis
                       function_type='consistency')
        # Connect the variable inputs for the function
        var1s = sorted(ccv_mappings.keys(), reverse=True)
        for idx, var1 in enumerate(var1s):
            var2 = ccv_mappings[var1]
            eq_lab1 = 'x{}_0'.format(idx)
            eq_lab2 = 'x{}_1'.format(idx)
            eq_lab3 = 'x{}_sc'.format(idx)
            self.add_edge(var1, new_function_node, equation_label=eq_lab1)
            self.add_edge(var2, new_function_node, equation_label=eq_lab2)
            # Add the scaler variable and connect accordingly
            new_scaler_node = '/{}/scalers/{}'.format(var1.split('/')[1], '/'.join(var1.split('/')[2:]))
            if not self.has_node(new_scaler_node):
                self.add_vnode(new_scaler_node,
                               label='{}Scaler'.format(var1.split('/')[-1]))
            self.add_edge(new_scaler_node, new_function_node, equation_label=eq_lab3)
            if idx == 0:
                math_expression = '(({}-{})/{})**2'.format(eq_lab2, eq_lab1, eq_lab3)
            else:
                math_expression += '+(({}-{})/{})**2'.format(eq_lab2, eq_lab1, eq_lab3)
        # Finally, add square root around expression
        math_expression = '(' + math_expression + ')**0.5'
        # Create the output objective node of the function and connect it
        new_obj_node = '/{}/distributedArchitectures/group{}/objective'.format(self.get_schema_root_name(var1),
                                                                               group_idx)
        self.add_vnode(new_obj_node,
                       label='J'+str(group_idx),
                       problem_role=self.PROBLEM_ROLES_VARS[1])  # objective
        self.add_edge(new_function_node, new_obj_node)
        self.add_equation((new_function_node, new_obj_node), math_expression, 'Python')
        return new_function_node, new_obj_node

    def connect_weighted_couplings_objective_function(self, group_idx, couplings):
        """Method to add a weighted couplings objective function. A consistency objective function between related
         weights and couplings w_1, y_1, w_2, y_2 would be: w_1*y_1 + w_2*y_2

        :param group_idx: index of the subgroup
        :type group_idx: int
        :param couplings: couplings to be weighted
        :type couplings: list
        :return: new function node, objective output value and weight nodes
        :rtype: tuple
        """

        # Add the consistency constraint objective function (as generic function node, since it will be made as a
        # mathematical function)
        new_function_node = self.WCF_STRING + str(group_idx) + self.WCF_SUFFIX
        assert not self.has_node(new_function_node), \
            'The automatically generated function {} somehow already exists.'.format(new_function_node)
        self.add_fnode(new_function_node,
                       label=self.WCF_LABEL + str(group_idx),
                       problem_role=self.FUNCTION_ROLES[2],  # post-coupling
                       architecture_role=self.ARCHITECTURE_ROLES_FUNS[8])  # post-coupling analysis
        weight_nodes = []
        # Connect the variable inputs for the function
        for idx, var1 in enumerate(couplings):
            # Add a weight coefficient for each coupling
            xpath_var1 = var1.split('/')
            var_ref_label = xpath_var1[-1]
            root = xpath_var1[1]
            var2 = '/{}/distributedArchitectures/group{}/couplingWeights/w{}_{}'.format(root, group_idx, idx, var_ref_label)
            self.add_node(var2,
                          category='variable',
                          label=var2.split('/')[-1] + '_' + var1.split('/')[-1],
                          problem_role=self.PROBLEM_ROLES_VARS[0],
                          architecture_role=self.ARCHITECTURE_ROLES_VARS[11])
            weight_nodes.append(var2)
            # Add the scaler variable and connect accordingly
            new_scaler_node = '/{}/scalers/{}'.format(var1.split('/')[1], '/'.join(var1.split('/')[2:]))
            if not self.has_node(new_scaler_node):
                self.add_vnode(new_scaler_node,
                               label='{}Scaler'.format(var1.split('/')[-1]))
            eq_lab1 = 'y{}'.format(idx)
            eq_lab2 = 'w{}'.format(idx)
            eq_lab3 = 'y{}_sc'.format(idx)
            self.add_edge(var1, new_function_node, equation_label=eq_lab1)
            self.add_edge(var2, new_function_node, equation_label=eq_lab2)
            self.add_edge(new_scaler_node, new_function_node, equation_label=eq_lab3)
            low_bound = -2.
            upp_bound = 2.
            nom_value = 1.
            global_lb = float('-inf')
            global_ub = float('inf')
            self.mark_as_design_variable(var2, lower_bound=low_bound, upper_bound=upp_bound, nominal_value=nom_value,
                                         global_lb=global_lb, global_ub=global_ub)
            if idx == 0:
                math_expression = '{}*{}/{}'.format(eq_lab2, eq_lab1, eq_lab3)
            else:
                math_expression += '+{}*{}/{}'.format(eq_lab2, eq_lab1, eq_lab3)
        # Create the output objective node of the function and connect it
        new_obj_node = '/{}/distributedArchitectures/group{}/objective'.format(root, group_idx)
        self.add_vnode(new_obj_node,
                      label='wcf'+str(group_idx),
                      problem_role=self.PROBLEM_ROLES_VARS[1])  # objective
        self.add_edge(new_function_node, new_obj_node)
        self.add_equation((new_function_node, new_obj_node), math_expression, 'Python')
        return new_function_node, new_obj_node, weight_nodes

    def connect_consistency_constraint_function(self, ccv_mappings, architecture_role=None):
        """Method to add a consistency constraint function to an MDG.

        :param ccv_mappings: mapping between nodes that should be made consistent
        :type ccv_mappings: dict
        :return: new function node and constraint output nodes
        :rtype: tuple
        """

        # Add the consistency constraint objective function (as generic function node, since it will be made as a
        # mathematical function)
        new_function_node = '{}{}'.format(self.CONSCONS_STRING, self.CONSCONS_SUFFIX)
        assert not self.has_node(new_function_node), \
            'The automatically generated function {} somehow already exists.'.format(new_function_node)
        self.add_fnode(new_function_node,
                       label=self.CONSCONS_LABEL,
                       problem_role=self.FUNCTION_ROLES[2],  # post-coupling
                       architecture_role=self.ARCHITECTURE_ROLES_FUNS[8] if architecture_role is None else architecture_role,
                       function_type='consistency')
        # Connect the variable inputs for the function
        new_con_nodes = []
        for idx, (var1, var2) in enumerate(iteritems(ccv_mappings)):
            # Add the scaler variable and connect accordingly
            rel_var = self.get_related_schema_node(var1)
            rel_var_label = rel_var.split('/')[-1]
            new_scaler_node = '/{}/scalers/{}'.format(rel_var.split('/')[1], '/'.join(rel_var.split('/')[2:]))
            if not self.has_node(new_scaler_node):
                self.add_vnode(new_scaler_node,
                               label='{}Scaler'.format(rel_var_label))
            eq_lab1 = 'y{}_{}_0'.format(idx, rel_var_label)
            eq_lab2 = 'y{}_{}_1'.format(idx, rel_var_label)
            eq_lab3 = 'y{}_{}_sc'.format(idx, rel_var_label)
            self.add_edge(var1, new_function_node, equation_label=eq_lab1)
            self.add_edge(var2, new_function_node, equation_label=eq_lab2)
            self.add_edge(new_scaler_node, new_function_node, equation_label=eq_lab3)
            math_expression = '({}-{})/{}'.format(eq_lab2, eq_lab1, eq_lab3)
            # Create the output objective node of the function and connect it
            root = self.get_schema_root_name(var1)
            new_con_node = '/{}/mdo_data/systemLevel/consistencyConstraints/gc{}{}'.format(root, idx, rel_var_label)
            self.add_vnode(new_con_node,
                           label='gc{}_{}'.format(idx, rel_var_label),
                           problem_role=self.PROBLEM_ROLES_VARS[2])  # constraint
            self.mark_as_constraint(new_con_node, '==', 0.)
            self.add_edge(new_function_node, new_con_node)
            self.add_equation((new_function_node, new_con_node), math_expression, 'Python')
            new_con_nodes.append(new_con_node)
        return new_function_node, new_con_nodes

    def connect_consistencies_summation(self, consistency_nodes):
        """Addition of a function that sums the consistency objective values in collaborative 
        optimization at the system level."""
        summ_fun = self.COF_STRING + 'tot' + self.COF_SUFFIX
        assert not self.has_node(summ_fun), \
            'The automatically generated function {} somehow already exists.'.format(
                summ_fun)
        self.add_fnode(summ_fun,
                      label=self.COF_LABEL + 'tot',
                      problem_role=self.FUNCTION_ROLES[4],  # uncoupled-DVD
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[6],  # uncoupled-DVD
                      function_type='regular')
        # Connect the variable inputs for the function
        for idx, var in enumerate(consistency_nodes):
            eq_lab = 'J_{}'.format(idx)
            self.add_edge(var, summ_fun, equation_label=eq_lab)
            # Add the scaler variable and connect accordingly
            if idx == 0:
                math_expression = '{}**2'.format(eq_lab)
            else:
                math_expression += '+{}**2'.format(eq_lab)
        # Finally, add square root around expression
        math_expression = '(' + math_expression + ')**0.5'
        # Create the output objective node of the function and connect it
        summ_node = '/{}/distributedArchitectures/groupTot/objective'.format(
            self.get_schema_root_name(var))
        self.add_vnode(summ_node,
                      label='Jtot',
                      problem_role=self.PROBLEM_ROLES_VARS[2])  # constraint
        self.add_edge(summ_fun, summ_node)
        self.add_equation((summ_fun, summ_node), math_expression, 'Python')
        self.mark_as_constraint(summ_node, '==', 0.0)
        return summ_fun, summ_node


    def localize_design_variables(self, group_functions, global_des_vars, local_des_vars):
        """Method for distributed architecture to create instances of local and global design variables with respect to
        the subgroup.

        :param group_functions: functions that are part of the current group
        :type group_functions: list
        :param global_des_vars: global design variables of the system
        :type global_des_vars: list
        :param local_des_vars: local design variables used in the group
        :type local_des_vars: list
        :return: created copies of the design variables and their mapping
        :rtype: tuple
        """

        # Start with empty lists
        local_des_var_copies = []
        global_des_var_copies = []
        mapping = dict()
        # The global design variables get copies at the local level and are connected accordingly
        for global_des_var in global_des_vars:
            # Find the functions for which the design variable is input
            targets = self.get_targets(global_des_var)
            local_targets = [target for target in targets if target in group_functions]

            # Create a local copy of the design variable
            local_des_var_copy = self.copy_node_as(global_des_var,
                                                   self.ARCHITECTURE_ROLES_VARS[9],  # copy design variable
                                                   add_instance_if_exists=True)
            local_des_var_copies.append(local_des_var_copy)
            mapping[global_des_var] = local_des_var_copy

            for target in local_targets:
                # Connect the local copy to the targets
                self.copy_edge((global_des_var, target), (local_des_var_copy, target))

                # Remove the connection between the global design variable and the target
                self.remove_edge(global_des_var, target)
        # The local design variables get copies at the global level and are connected accordingly
        for local_des_var in local_des_vars:
            # Find the functions outside the local level for which the design variable is input
            targets = self.get_targets(local_des_var)
            external_targets = [target for target in targets if target not in group_functions]

            # Create a global copy of the design variable
            if external_targets:
                global_des_var_copy = self.copy_node_as(local_des_var,
                                                        self.ARCHITECTURE_ROLES_VARS[9],  # copy design variable
                                                        add_instance_if_exists=False)
                global_des_var_copies.append(global_des_var_copy)
                mapping[local_des_var] = global_des_var_copy

            for target in external_targets:
                # Connect the global copy to the targets
                self.copy_edge((local_des_var, target), (global_des_var_copy, target))

                # Remove the connection between the local design variable and the external target
                self.remove_edge(local_des_var, target)
        return local_des_var_copies, global_des_var_copies, mapping

    def localize_group_couplings(self, group_functions, external_couplings, local_couplings,
                                 instances_for_externals=False, make_copies_des_vars=False):
        """Method for distributed architecture to create instances of local and global coupling variables with respect
        to the subgroup.

        :param group_functions: functions that are part of the current group
        :type group_functions: list
        :param external_couplings: external couplings w.r.t. the current group
        :type external_couplings: list
        :param local_couplings: local coupling w.r.t. the current group
        :type local_couplings: list
        :param instances_for_externals: setting whether additional instances should be created for external couplings
        :type instances_for_externals: bool
        :return: created copies of the couplings and their mapping
        :rtype: tuple
        """

        # Start with empty lists
        external_couplings_copies = []
        local_couplings_copies = []
        mapping_locals = dict()
        # The external couplings should be handled with a copy at the local level
        for external_coupling in external_couplings:
            # Find the functions for which the coupling variable is input
            targets = self.get_targets(external_coupling)
            local_targets = [target for target in targets if target in group_functions]

            if local_targets:
                # Create a local copy of the external coupling
                related_node = external_coupling
                if 'architecture_role' in self.nodes[external_coupling]:
                    if self.nodes[external_coupling]['architecture_role'] == self.ARCHITECTURE_ROLES_VARS[2]:
                        related_node = self.nodes[external_coupling]['related_to_schema_node']
                external_coupling_copy = self.copy_node_as(related_node,
                                                           self.ARCHITECTURE_ROLES_VARS[9 if make_copies_des_vars else 2],  # copy design variable or coupling copy variable
                                                           add_instance_if_exists=instances_for_externals)
                external_couplings_copies.append(external_coupling_copy)

            for target in local_targets:
                # Connect the local copy to the targets
                self.copy_edge((external_coupling, target), (external_coupling_copy, target))

                # Remove the connection between the global coupling variable and the target
                self.remove_edge(external_coupling, target)

        # Local couplings should only be handled by the functions inside the group, outside, they are handled by copies
        for local_coupling in local_couplings:
            # Find the external functions for which the coupling variable is input
            targets = self.get_targets(local_coupling)
            external_targets = [target for target in targets if target not in group_functions]

            # Create a global copy of the internal coupling (if it does not exist in the graph yet)
            if external_targets:
                local_coupling_copy = self.copy_node_as(local_coupling,
                                                        self.ARCHITECTURE_ROLES_VARS[9 if make_copies_des_vars else 2],  # copy design variable or coupling copy variable
                                                        add_instance_if_exists=False)
                local_couplings_copies.append(local_coupling_copy)
                mapping_locals[local_coupling] = local_coupling_copy
            else:
                # Assess that the local_coupling_copy already exists (but has been disconnected to targets already)
                # and add its mapping.
                xpath_nodes = local_coupling.split('/')
                root = self.get_schema_root_name(local_coupling)
                local_coupling_copy = '/{}/architectureNodes/{}s/{}Copy/{}'\
                    .format(root, make_camel_case(self.ARCHITECTURE_ROLES_VARS[9 if make_copies_des_vars else 2]), root, '/'.join(xpath_nodes[2:]))
                self.assert_node_exists(local_coupling_copy)
                mapping_locals[local_coupling] = local_coupling_copy

            for target in external_targets:
                # Connect the local copy to the targets
                self.copy_edge((local_coupling, target), (local_coupling_copy, target))

                # Remove the connection between the local coupling variable and the target
                self.remove_edge(local_coupling, target)
        return external_couplings_copies, local_couplings_copies, mapping_locals

    def connect_nodes_as_output(self, nodes, function):
        """Method to connect a list of nodes as output to a function node.

        :param nodes: list of nodes to be connected as output
        :type nodes: list
        :param function: function to which the nodes are connected
        :type function: str
        """

        for node in nodes:
            assert self.has_node(node)
            self.add_edge(function, node)
        return

    def connect_coordinator(self, additional_inputs=[], additional_outputs=[]):
        """Method to automatically connect all system inputs and outputs of a graph to the coordinator node."""

        # Get system inputs and outputs
        input_nodes = self.find_all_nodes(subcategory='all inputs')
        output_nodes = self.find_all_nodes(subcategory='all outputs')

        # Connect the nodes to the coordinator
        for input_node in input_nodes+additional_outputs:
            self.add_edge(self.COORDINATOR_STRING, input_node)
        for output_node in output_nodes+additional_inputs:
            self.add_edge(output_node, self.COORDINATOR_STRING)

        return

    def connect_distributed_system_converger(self, converger, inputs, outputs, label='SYS-CONV'):
        """Method to add a convergence check in the MDG.

        :param converger: node ID of the converger block
        :type converger: str
        :param inputs: input nodes to be connected for convergence check
        :type inputs: list
        :param outputs: output nodes to be connected for convergence check
        :type outputs: list
        :param label: label for the converger block
        :type label: str
        :return: the convergence check node
        :rtype: str
        """

        # Input assertions
        # Add converger block if it's not there
        if not self.has_node(converger):
            des_var_facs = OrderedDict((('k_bound_reduction', 2.),
                                        ('interval_increase_relative', 0.25),
                                        ('interval_increase_absolute', 0.1),
                                        ('interval_range_minimum', 1e-3)))
            
            self.add_fnode(converger,
                           architecture_role=self.ARCHITECTURE_ROLES_FUNS[10],  # distr sys conv
                           label=label,
                           settings=OrderedDict((('method', 'BLISS-2000'),
                                                 ('maximum_iterations', 30),
                                                 ('convergence_tolerance_relative', 1e-3),
                                                 ('convergence_tolerance_absolute', 1e-3),
                                                 ('design_variable_factors', des_var_facs))))
        assert isinstance(inputs, list)
        self.assert_node_exists(inputs)

        # Connect the converger block
        for input in inputs:
            self.add_edge(input, converger)

        for output in outputs:
            self.add_edge(converger, output)

        return

    def connect_converger(self, converger, conv_type, coupling_functions, include_couplings_as_final_output,
                          system_converger=False, label='CONV', conv_is_optimizer=False):
        """Method to automatically connect a converger around a collection of coupled functions.

        :param converger: name of the converger to be connected
        :type converger: str
        :param conv_type: setting for the type of convergence (Jacobi, Gauss-Seidel)
        :type conv_type: str
        :param coupling_functions: list of coupled functions
        :type coupling_functions: list
        :param include_couplings_as_final_output: setting on whether coupling variables should always be added as output
        :type include_couplings_as_final_output: bool
        :param system_converger: converger is a system converger
        :type system_converger: bool
        :param label: converger label
        :type label: str
        """

        # Input assertions
        # Add converger block if it's not there
        if not self.has_node(converger):
            self.add_fnode(converger,
                           architecture_role=self.ARCHITECTURE_ROLES_FUNS[1] if conv_is_optimizer else
                           self.ARCHITECTURE_ROLES_FUNS[2],
                           label=label,
                           settings=OrderedDict((('linear_solver', OrderedDict((('method', conv_type),
                                                                                ('last_iterations_to_consider', 1),
                                                                                ('maximum_iterations', 100),
                                                                                ('convergence_tolerance_relative', 1e-6),
                                                                                ('convergence_tolerance_absolute', 1e-6)))),
                                                ('nonlinear_solver', OrderedDict((('method', conv_type),
                                                                                  ('last_iterations_to_consider', 1),
                                                                                  ('maximum_iterations', 100),
                                                                                  ('convergence_tolerance_relative', 1e-6),
                                                                                  ('convergence_tolerance_absolute', 1e-6)))
                                                 ))) if not conv_is_optimizer else
                                                                   OrderedDict([('package', 'SciPy'),
                                                                                ('algorithm', 'SLSQP'),
                                                                                ('maximum_iterations', 1000),
                                                                                ('maximum_function_evaluations', 1000),
                                                                                ('convergence_tolerance', 1e-6),
                                                                                ('constraint_tolerance', 1e-6),
                                                                                ('apply_scaling', True)]))
        assert conv_type in self.OPTIONS_CONVERGERS + [self.OPTIONS_ARCHITECTURES[2]], \
            'Invalid converger type %s specified.' % conv_type
        assert isinstance(coupling_functions, list)
        for coupling_function in coupling_functions:
            assert self.has_node(coupling_function), 'Missing coupling function %s in the graph.' % coupling_function

        # Manipulate the coupling variables based on the architecture
        if conv_type == self.OPTIONS_CONVERGERS[0]:  # Jacobi
            self.manipulate_coupling_nodes(coupling_functions, remove_feedback=True, remove_feedforward=True,
                                           converger=converger,
                                           include_couplings_as_final_output=include_couplings_as_final_output,
                                           system_converger=system_converger)
        elif conv_type == self.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
            self.manipulate_coupling_nodes(coupling_functions, remove_feedback=True, remove_feedforward=False,
                                           converger=converger,
                                           include_couplings_as_final_output=include_couplings_as_final_output,
                                           system_converger=system_converger)
        elif conv_type == self.OPTIONS_ARCHITECTURES[2]:  # IDF
            self.manipulate_coupling_nodes(coupling_functions, remove_feedback=True, remove_feedforward=True,
                                           converger=converger,
                                           include_couplings_as_final_output=include_couplings_as_final_output,
                                           system_converger=system_converger)

        return

    def connect_optimizer(self, optimizer, design_variable_nodes, objective_node, constraint_nodes, label='OPT',
                          settings=OrderedDict([('package', 'SciPy'), ('algorithm', 'SLSQP'),
                                                ('maximum_iterations', 1000), ('maximum_function_evaluations', 1000),
                                                ('convergence_tolerance', 1e-6), ('constraint_tolerance', 1e-6),
                                                ('apply_scaling', True)]), **kwargs):
        """Method to automatically connect an optimizer w.r.t. the design variables, objective, and constraints.

        :param optimizer: name of the optimizer to be connected
        :type optimizer: str
        :type design_variable_nodes: list
        :param objective_node: node used as objective by the optimizer
        :type objective_node: str
        :param constraint_nodes: list of constraint nodes
        :type constraint_nodes: list
        :param label: optimizer label
        :type label: str
        :param settings: detailed settings of the optimizer
        :type settings: OrderedDict
        :param kwargs: key-word arguments on individual optimizer settings
        :type kwargs: str or float or int or bool
        :return: enriched MDAO data graph with connected optimizer
        :rtype: MdaoDataGraph
        """

        # Input assertions
        # Add optimizer block if it's not there
        if not self.has_node(optimizer):
            self.add_fnode(optimizer,
                          architecture_role=self.ARCHITECTURE_ROLES_FUNS[1],
                          label=label,
                          settings=copy.deepcopy(settings))
        if kwargs:
            for key, value in kwargs.items():
                self.nodes[optimizer]['settings'][key] = value
        assert isinstance(design_variable_nodes, list)
        for des_var in design_variable_nodes:
            assert self.has_node(des_var), 'Design variable %s is missing in the graph.' % des_var
        assert isinstance(objective_node, string_types)
        assert self.has_node(objective_node), 'Objective node %s is missing in the graph.' % objective_node
        assert isinstance(constraint_nodes, list)
        for con_var in constraint_nodes:
            assert self.has_node(con_var), 'Constraint variable %s is missing in the graph.' % con_var

        # Add attributes to the optimizer block
        self.nodes[optimizer]['design_variables'] = dict()
        for des_var in design_variable_nodes:
            self.nodes[optimizer]['design_variables'][des_var] = dict()
            if 'upper_bound' in self.nodes[des_var]:
                self.nodes[optimizer]['design_variables'][des_var]['upper_bound'] = self.nodes[des_var]['upper_bound']
            else:
                self.nodes[optimizer]['design_variables'][des_var]['upper_bound'] = None
            if 'lower_bound' in self.nodes[des_var]:
                self.nodes[optimizer]['design_variables'][des_var]['lower_bound'] = self.nodes[des_var]['lower_bound']
            else:
                self.nodes[optimizer]['design_variables'][des_var]['lower_bound'] = None
            if 'nominal_value' in self.nodes[des_var]:
                self.nodes[optimizer]['design_variables'][des_var]['nominal_value'] = \
                    self.nodes[des_var]['nominal_value']
            else:
                self.nodes[optimizer]['design_variables'][des_var]['nominal_value'] = None
            if 'problem_role' not in self.nodes[des_var] or \
                self.nodes[des_var]['problem_role'] != self.PROBLEM_ROLES_VARS[0]:
                self.nodes[des_var]['problem_role'] = self.PROBLEM_ROLES_VARS[0]
        self.nodes[optimizer]['objective_variable'] = [objective_node]
        self.nodes[optimizer]['constraint_variables'] = dict()
        for con_var in constraint_nodes:
            self.nodes[optimizer]['constraint_variables'][con_var] = dict()
            if 'upper_bound' in self.nodes[con_var]:
                self.nodes[optimizer]['constraint_variables'][con_var]['upper_bound'] = \
                    self.nodes[con_var]['upper_bound']
            else:
                self.nodes[optimizer]['constraint_variables'][con_var]['upper_bound'] = None
            if 'lower_bound' in self.nodes[con_var]:
                self.nodes[optimizer]['constraint_variables'][con_var]['lower_bound'] = \
                    self.nodes[con_var]['lower_bound']
            else:
                self.nodes[optimizer]['constraint_variables'][con_var]['lower_bound'] = None

        # Manipulate the graph based on the architecture
        # Connect design variables to the optimizer
        pre_opt_funcs = self.graph['function_ordering'][self.FUNCTION_ROLES[3]]
        fin_des_vars = []
        ini_guess_nodes = []
        for des_var in design_variable_nodes:
            # Create initial guess design variable
            ini_guess_node = self.copy_node_as(des_var, architecture_role=self.ARCHITECTURE_ROLES_VARS[3])
            ini_guess_nodes.append(ini_guess_node)
            # If des_var comes from pre-des-var function, then reconnect (remove previous connection, connect to guess)
            des_var_sources = self.get_sources(des_var)
            if des_var_sources:
                pre_des_var_func = list(set(des_var_sources).intersection(pre_opt_funcs))[0]
                if pre_des_var_func:
                    self.remove_edge(pre_des_var_func, des_var)
                    self.add_edge(pre_des_var_func, ini_guess_node)
            # Connect initial guess design variable to optimizer
            self.add_edge(ini_guess_node, optimizer)
            # Connect design variable as output from optimizer
            self.add_edge(optimizer, des_var)
            # Create final design variable
            fin_value_node = self.copy_node_as(des_var, architecture_role=self.ARCHITECTURE_ROLES_VARS[4])
            fin_des_vars.append(fin_value_node)
            # Connect final design variable as output from optimizer
            self.add_edge(optimizer, fin_value_node)
        # Connect objective and constraint nodes to the optimizer
        fin_obj = None
        fin_cnstrnts = []
        for var in [objective_node] + constraint_nodes:
            # Connect regular variable version to optimizer
            self.add_edge(var, optimizer)
            # Create a final value copy and connect it as output of the associated functions
            fin_value_node = self.copy_node_as(var, architecture_role=self.ARCHITECTURE_ROLES_VARS[5])
            if fin_obj is None:
                fin_obj = fin_value_node
            else:
                fin_cnstrnts.append(fin_value_node)
            self.copy_edge([self.get_sources(var)[0], var], [self.get_sources(var)[0], fin_value_node])
        # If the graph contains consistency constraint variables, then connect these to the optimizer as well
        consconcs_nodes = self.find_all_nodes(category='variable',
                                              attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_VARS[6]])
        # Add consistency constraints as constraints in the graph
        for node in consconcs_nodes:
            rel_node = self.nodes[node]['related_to_schema_node']
            # Add design variables to optimizer attributes
            self.nodes[optimizer]['design_variables'][rel_node] = dict()
            # TODO: Temp fix for issue with non-existing nodes
            if rel_node in self.nodes:
                if 'upper_bound' in self.nodes[rel_node]:
                    self.nodes[optimizer]['design_variables'][rel_node]['upper_bound'] = self.nodes[rel_node]['upper_bound']
                else:
                    self.nodes[optimizer]['design_variables'][rel_node]['upper_bound'] = None
                if 'lower_bound' in self.nodes[rel_node]:
                    self.nodes[optimizer]['design_variables'][rel_node]['lower_bound'] = self.nodes[rel_node]['lower_bound']
                else:
                    self.nodes[optimizer]['design_variables'][rel_node]['lower_bound'] = None
            else:
                self.nodes[optimizer]['design_variables'][rel_node]['upper_bound'] = None
                self.nodes[optimizer]['design_variables'][rel_node]['lower_bound'] = None
            # Add constraints to optimizer attributes
            self.nodes[optimizer]['constraint_variables'][node] = dict()
            self.add_edge(node, optimizer)

        return fin_des_vars, fin_obj, fin_cnstrnts, ini_guess_nodes

    def connect_doe_block(self, doe_block, design_variable_nodes, qoi_nodes, label='DOE', **kwargs):
        """Method to automatically connect an doe_block w.r.t. the design variables, objective, and constraints.

        :param doe_block: name of the doe_block to be connected
        :type doe_block: str
        :param design_variable_nodes: list of design variables
        :type design_variable_nodes: list
        :param qoi_nodes: list of constraint nodes
        :type qoi_nodes: list
        :return: enriched MDAO data graph with connected doe_block
        :rtype: MdaoDataGraph
        """

        # Input assertions
        # Add DOE block if it's not there
        if not self.has_node(doe_block):
            self.add_fnode(doe_block,
                           architecture_role=self.ARCHITECTURE_ROLES_FUNS[3],
                           label=label,
                           settings=copy.deepcopy(self.graph['problem_formulation']['doe_settings']))
        assert isinstance(design_variable_nodes, list)
        for des_var in design_variable_nodes:
            assert self.has_node(des_var), 'Design variable %s is missing in the graph.' % des_var
        assert isinstance(qoi_nodes, list)
        for qoi_var in qoi_nodes:
            assert self.has_node(qoi_var), 'Q.O.I. variable %s is missing in the graph.' % qoi_var

        # Add attributes to the doe block
        gnodes = self.nodes
        gnodes[doe_block]['design_variables'] = doe_des_vars = dict()
        for des_var in design_variable_nodes:
            doe_des_vars[des_var] = doe_des_var = dict()
            des_var_attrbs = ['upper_bound', 'lower_bound', 'nominal_value', 'samples']
            for des_var_attrb in des_var_attrbs:
                doe_des_var[des_var_attrb] = gnodes[des_var].get(des_var_attrb)
            if 'problem_role' not in gnodes[des_var] or \
                gnodes[des_var]['problem_role'] != self.PROBLEM_ROLES_VARS[0]:
                gnodes[des_var]['problem_role'] = self.PROBLEM_ROLES_VARS[0]
        gnodes[doe_block]['quantities_of_interest'] = qoi_nodes

        # For the custom design table, add the table with values to the settings
        if 'doe_settings' in self.graph['problem_formulation']:
            doe_settings = self.graph['problem_formulation']['doe_settings']
            if 'method' in doe_settings:
                if doe_settings['method'] == 'Custom design table':
                    n_samples = len(doe_des_vars[design_variable_nodes[-1]]['samples'])
                    doe_table = []
                    for idj in range(n_samples):
                        doe_table.append([])
                        for des_var in design_variable_nodes:
                            doe_table[idj].append(gnodes[des_var]['samples'][idj])
                    doe_settings['table'] = doe_table
                    doe_settings['table_order'] = design_variable_nodes

        # Manipulate the graph based on the architecture
        # Connect design variables to the doe_block
        pre_doe_funcs = self.graph['function_ordering'][self.FUNCTION_ROLES[3]]
        inps = []
        for des_var in design_variable_nodes:
            # Create DOE input samples
            doe_input_node = self.copy_node_as(des_var, architecture_role=self.ARCHITECTURE_ROLES_VARS[7])
            inps.append(doe_input_node)
            # If des_var comes from pre-des-var function then remove this connection (DOE uses separate list of samples)
            des_var_sources = self.get_sources(des_var)
            pre_des_var_funcs = list(set(des_var_sources).intersection(pre_doe_funcs))
            if pre_des_var_funcs:
                pre_des_var_func = pre_des_var_funcs[0]
                self.remove_edge(pre_des_var_func, des_var)
                # If des_var has become a hole, remove it
                if self.node_is_hole(des_var):
                    self.add_edge(pre_des_var_func, doe_input_node)
            # Connect DOE input samples to doe_block
            self.add_edge(doe_input_node, doe_block)
            # Connect design variable as output from doe_block
            self.add_edge(doe_block, des_var)
        # Connect QOI nodes to the doe_block
        outs = []
        for var in qoi_nodes:
            # Connect regular variable version to doe_block
            self.add_edge(var, doe_block)
            # Create a DOE output samples node and connect it as output of the DOE
            doe_output_node = self.copy_node_as(var, architecture_role=self.ARCHITECTURE_ROLES_VARS[8])
            outs.append(doe_output_node)
            self.add_edge(doe_block, doe_output_node)

        return inps, outs

    def connect_surrogate_model(self, sm, train_inputs, train_outputs, sm_inputs, sm_out_originals, label=None,
                                fitting_method='Kriging'):
        """Method to connect a surrogate to the right nodes in the MDG.

        :param sm: new function node of surrogate model
        :type sm: str
        :param def_node: surrogate model definition node
        :type def_node: str
        :param sm_inputs: inputs of the surrogate model
        :type sm_inputs: list
        :param sm_out_originals: original outputs of the analysis box for which a surrogate model was created
        :type sm_out_originals: list
        :param label: label of the new function node
        :type label: str
        :return: output of the surrogate model (value approximated)
        :rtype: list
        """

        # Input assertions
        assert not self.has_node(sm), 'Node {} already exists in the graph.'.format(sm)

        # Set label
        if label is None:
            label = str(sm)

        # Add the surrogate model
        self.add_fnode(sm,
                       category='function',
                       architecture_role=self.ARCHITECTURE_ROLES_FUNS[9],  # Surrogate model
                       label=label,
                       training=OrderedDict((('inputs', train_inputs), ('outputs', train_outputs),
                                             ('settings', OrderedDict((('fitting_method', fitting_method),))))),
                       prediction=OrderedDict((('inputs', sm_inputs), ('outputs', []))))

        # Connect the surrogate model
        # Connect train data as input
        for train_input in train_inputs:
            self.add_edge(train_input, sm)
        for train_output in train_outputs:
            self.add_edge(train_output, sm)

        # Connect the model inputs
        for sm_input in sm_inputs:
            self.add_edge(sm_input, sm)

        # Connect model results as output
        node_apprs = []
        for sm_out_or in sm_out_originals:
            node_appr = self.copy_node_as(sm_out_or, self.ARCHITECTURE_ROLES_VARS[10])
            self.nodes[sm]['prediction']['outputs'].append(node_appr)
            self.add_edge(sm, node_appr)
            node_apprs.append(node_appr)

        return node_apprs

    def connect_partitions(self, mdao_arch, sub_func_orderings, coup_functions):
        """Method to connect partitions in a data graph of a monolithic architecture and add
        convergers at sub- and system level.
        """

        sys_conv_type = self.graph['problem_formulation']['convergence_type']
        partitions = self.graph['problem_formulation']['coupled_functions_groups']
        local_convergers = self.graph['problem_formulation']['local_convergers']
        jacobi_conv = self.graph['problem_formulation']['jacobi_convergence']

        sys_opt, sys_conv, sub_convs = self.get_architecture_node_ids(mdao_arch, number_of_groups=len(partitions))
        sys_opt_label, sys_conv_label, sub_convs_labels = self.get_architecture_node_labels(
            mdao_arch, number_of_groups=len(partitions))

        # Connect partitions
        for partition in range(len(partitions)):
            # Connect nodes to local converger if present, otherwise system converger or optimizer
            if partition in local_convergers:
                conv, conv_label = sub_convs[partition], sub_convs_labels[partition]
            elif mdao_arch == self.OPTIONS_ARCHITECTURES[2]:
                conv, conv_label = sys_opt, sys_opt_label
            else:
                conv, conv_label = sys_conv, sys_conv_label
            # Get convergence type
            if partition in jacobi_conv:
                conv_type = self.OPTIONS_ARCHITECTURES[2] if conv == sys_opt else self.OPTIONS_CONVERGERS[0]
            else:
                conv_type = self.OPTIONS_CONVERGERS[1]
            # Check whether optimizer needs to be connected as converger
            converger_is_optimizer = True if conv_label == sys_opt_label else False
            # Get nodes in partition
            if partition not in local_convergers and conv_type in [self.OPTIONS_CONVERGERS[0],
                                                                   self.OPTIONS_ARCHITECTURES[2]]:
                nodes = [node for func_role in sub_func_orderings[partition] for node in
                         sub_func_orderings[partition][func_role]]
            else:
                nodes = sub_func_orderings[partition]['coupled']
            # If needed add the system converger with the correct convergence type
            if conv == sys_conv and sys_conv not in self.nodes:
                self.connect_converger(conv, sys_conv_type, [], True, label=conv_label)
            # Connect nodes to (sub)system converger or system optimizer
            self.connect_converger(conv, conv_type, nodes, True, label=conv_label,
                                   conv_is_optimizer=converger_is_optimizer)
            # Change convergence tolerance of the subconverger (needed to guarantee overall convergence)
            if conv in sub_convs:
                self.nodes[conv]['settings']['linear_solver']['convergence_tolerance_relative'] = 1e-7
                self.nodes[conv]['settings']['linear_solver']['convergence_tolerance_absolute'] = 1e-7
                self.nodes[conv]['settings']['nonlinear_solver']['convergence_tolerance_relative'] = 1e-7
                self.nodes[conv]['settings']['nonlinear_solver']['convergence_tolerance_absolute'] = 1e-7

        # Connect remaining couplings to the system converger or optimizer
        if mdao_arch == self.OPTIONS_ARCHITECTURES[2]:
            conv, conv_label, conv_type = sys_opt, sys_opt_label, self.OPTIONS_ARCHITECTURES[2]
        else:
            conv, conv_label, conv_type = sys_conv, sys_conv_label, self.OPTIONS_CONVERGERS[0]
        converger_is_optimizer = True if conv == sys_opt else False
        self.connect_converger(conv, conv_type, coup_functions, True, system_converger=True, label=conv_label,
                               conv_is_optimizer=converger_is_optimizer)

        # Resolve problematic variables
        prob_var = self.find_all_nodes(subcategory='all splittable variables')
        for var in prob_var:
            sources = self.get_sources(var)
            targets = self.get_targets(var)
            function_order = []
            for converger in local_convergers:
                if sub_convs[converger] in sources:
                    function_order.extend([sub_convs[converger]])
                    function_order.extend([target for target in targets if target in partitions[converger]])
            if sys_conv in sources:
                function_order.extend([sys_conv])
                function_order.extend([target for target in targets if target not in function_order])
            if sys_opt in sources:
                function_order.extend([sys_opt])
                function_order.extend([target for target in targets if target not in function_order])
            self.split_variables(var, function_order=function_order)

        return

    def manipulate_coupling_nodes(self, func_order, remove_feedback, remove_feedforward, converger=None,
                                  include_couplings_as_final_output=False, system_converger=False):
        """Method to manipulate the coupling nodes in a data graph in order to remove unwanted feedback/feedforward.

        :param func_order: the order of the functions to be analyzed
        :type func_order: list
        :param remove_feedback: setting on whether feedback coupling should be removed
        :type remove_feedback: bool
        :param remove_feedforward: setting on whether feedforward coupling should be removed
        :type remove_feedforward: bool
        :param converger: setting on whether the couplings should be linked to a converger
        :type converger: str or None
        :param include_couplings_as_final_output: setting on whether coupling variables should always be added as output
        :type include_couplings_as_final_output: bool
        :param system_converger: converger is a system converger
        :type system_converger: bool
        """

        # Get all the relevant couplings
        if remove_feedback and remove_feedforward:
            direction = "both"
        elif remove_feedback and not remove_feedforward:
            direction = "backward"
        elif not remove_feedback and remove_feedforward:
            direction = "forward"
        else:
            raise IOError("Invalid settings on feedback and feedforward specific.")
        couplings = self.get_direct_coupling_nodes(func_order, direction=direction, print_couplings=False)

        # Manipulate the coupling nodes accordingly
        for coupling in couplings:
            if system_converger:
                assert 'coupled_functions_groups' in self.graph['problem_formulation'], 'Graph is not partitioned'
                partitions = self.graph['problem_formulation']['coupled_functions_groups']
                partition_nodes = [node for nodes in partitions for node in nodes]
                if coupling[0] in partition_nodes and coupling[1] in partition_nodes:
                    part_id_0 = [i for i in range(len(partitions)) if coupling[0] in partitions[i]][0]
                    part_id_1 = [i for i in range(len(partitions)) if coupling[1] in partitions[i]][0]
                    # Do not manipulate nodes if they are in the same partition
                    if part_id_0 == part_id_1:
                        continue
                    # Do not manipulate nodes if the partitions are solved in sequence
                    if 'sequence_partitions' in self.graph['problem_formulation']:
                        skip_coupling = False
                        for sequence in self.graph['problem_formulation']['sequence_partitions']:
                            if part_id_0 in sequence:
                                index = sequence.index(part_id_0)
                                if part_id_1 in sequence[index:]:
                                    skip_coupling = True
                        if skip_coupling:
                            continue
            # Create initial guess coupling variable node
            ini_guess_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[0])
            # If there is no converger node, then just add an initial guess of the coupled node
            if converger is None:
                # Connect initial guess as input to coupled function
                self.copy_edge((coupling[2], coupling[1]), (ini_guess_node, coupling[1]))
            # If there is a converger node, then connect it accordingly
            elif self.nodes[converger]['architecture_role'] == self.ARCHITECTURE_ROLES_FUNS[2]:
                # Connect initial guess as input to the converger
                self.add_edge(ini_guess_node, converger)
                # Create coupling copy variable (coming from converger) and connect it accordingly
                coupling_copy_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[2])
                if not self.has_edge(converger, coupling_copy_node):
                    self.add_edge(converger, coupling_copy_node)
                self.copy_edge((coupling[2], coupling[1]), (coupling_copy_node, coupling[1]))
                # Connect original coupling node to the converger
                self.add_edge(coupling[2], converger)
            # If the converger node is an optimizer (IDF), then connect it accordingly
            elif self.nodes[converger]['architecture_role'] == self.ARCHITECTURE_ROLES_FUNS[1]:
                # Connect initial guess as input to the optimizer
                self.add_edge(ini_guess_node, converger)
                # Create coupling copy variable (coming from converger/optimizer) and connect it accordingly
                coupling_copy_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[2])
                if not self.has_edge(converger, coupling_copy_node):
                    self.add_edge(converger, coupling_copy_node)
                self.copy_edge((coupling[2], coupling[1]), (coupling_copy_node, coupling[1]))
                # Create equation label
                equation_label = coupling[2].split('/')[-1]
                # Add consistency constraint function to the graph (if it's not already there)
                if not self.has_node(self.CONSCONS_STRING):
                    self.add_node(self.CONSCONS_STRING,
                                  label=self.CONSCONS_LABEL,
                                  category='function',
                                  architecture_role=self.ARCHITECTURE_ROLES_FUNS[8],
                                  function_type='consistency')
                    if 'distr_function_ordering' in self.graph:
                        self.graph['distr_function_ordering'][0][self.FUNCTION_ROLES[2]].append(self.CONSCONS_STRING)
                    if 'mg_function_ordering' in self.graph:
                        self.graph['mg_function_ordering'][self.FUNCTION_ROLES[2]].append(self.CONSCONS_STRING)
                # Connect original and copied coupling node to the consistency constraint function
                self.add_edge(coupling[2], self.CONSCONS_STRING, equation_label=equation_label)
                self.add_edge(coupling_copy_node, self.CONSCONS_STRING, equation_label=equation_label+'c')
                # Make original coupling node a design variable
                self.mark_as_design_variable(coupling[2])
                # Create consistency constraint variables for each coupling and make them output of the function
                consistency_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[6])
                self.mark_as_constraint(consistency_node, '==', 0.0)
                self.add_edge(self.CONSCONS_STRING, consistency_node)
                self.add_equation((self.CONSCONS_STRING, consistency_node), '{0}-{0}c'.format(equation_label), 'Python')
                if 'consistency_nodes' in self.nodes[self.CONSCONS_STRING]:
                    self.nodes[self.CONSCONS_STRING]['consistency_nodes'].append(consistency_node)
                else:
                    self.nodes[self.CONSCONS_STRING]['consistency_nodes'] = [consistency_node]
                # Change the role of the coupled function to post-coupled
                self.nodes[coupling[1]]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[8]
            # Remove coupling edge between coupling variable -> function
            self.remove_edge(coupling[2], coupling[1])
            # If required, create final coupling variable node and let it come from the coupled function
            if converger and ('problem_role' in self.nodes[coupling[2]] or include_couplings_as_final_output):
                final_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[1])
                self.copy_edge((coupling[0], coupling[2]), (coupling[0], final_node))
                keep_original_coupling_node = False
            elif not converger and ('problem_role' in self.nodes[coupling[2]] or include_couplings_as_final_output):
                keep_original_coupling_node = True
            else:
                keep_original_coupling_node = False
            # Remove original coupling node if it has become an output
            if self.node_is_output(coupling[2]) and not keep_original_coupling_node:
                self.remove_node(coupling[2])

        # If there is no converger node or if the converger is an optimizer (IDF), then change the coupled functions
        # to post-coupling functions or to uncoupled-DVD
        if converger is None or self.nodes[converger]['architecture_role'] == self.ARCHITECTURE_ROLES_FUNS[1] or \
                (self.graph['problem_formulation']['mdao_architecture'] == self.OPTIONS_ARCHITECTURES[2] and
                 'distr_function_ordering' in self.graph):
            if 'distr_function_ordering' in self.graph:
                distr_function_ordering = self.graph['distr_function_ordering']
                post_desvars_functions = copy.deepcopy(distr_function_ordering[0][self.FUNCTION_ROLES[4]])
                coupled_functions = copy.deepcopy(distr_function_ordering[0][self.FUNCTION_ROLES[1]])
                post_coupling_functions = copy.deepcopy(distr_function_ordering[0][self.FUNCTION_ROLES[2]])
                for partition in range(len(distr_function_ordering[1])):
                    if 'local_convergers' in self.graph['problem_formulation'] and partition not in \
                            self.graph['problem_formulation']['local_convergers']:
                        post_coupling_functions.extend(distr_function_ordering[1][partition][self.FUNCTION_ROLES[4]])
                        post_coupling_functions.extend(distr_function_ordering[1][partition][self.FUNCTION_ROLES[1]])
                    else:
                        post_desvars_functions.extend(distr_function_ordering[1][partition][self.FUNCTION_ROLES[4]])
                        coupled_functions.extend(distr_function_ordering[1][partition][self.FUNCTION_ROLES[1]])
                    post_coupling_functions.extend(distr_function_ordering[1][partition][self.FUNCTION_ROLES[2]])
                for post_desvars_function in post_desvars_functions:
                    self.nodes[post_desvars_function]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[4]
                for coupled_function in coupled_functions:
                    self.nodes[coupled_function]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[7]
                for post_coupling_function in post_coupling_functions:
                    self.nodes[post_coupling_function]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[8]
                self.graph['mg_function_ordering'][self.FUNCTION_ROLES[4]] = post_desvars_functions
                self.graph['mg_function_ordering'][self.FUNCTION_ROLES[1]] = coupled_functions
                self.graph['mg_function_ordering'][self.FUNCTION_ROLES[2]] = post_coupling_functions
            else:
                has_des_vars = bool(self.find_all_nodes(attr_cond=['problem_role', '==',
                                                                   self.PROBLEM_ROLES_VARS[0]]))
                mg_fun_ord = self.graph['mg_function_ordering']
                coupled_functions = copy.deepcopy(mg_fun_ord[self.FUNCTION_ROLES[1]])
                post_functions = copy.deepcopy(mg_fun_ord[self.FUNCTION_ROLES[2]])
                for fun in coupled_functions+post_functions:
                    self.nodes[fun]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6 if has_des_vars else 5]
                mg_fun_ord[self.FUNCTION_ROLES[1]] = []
                mg_fun_ord[self.FUNCTION_ROLES[2]] = []
                mg_fun_ord[self.FUNCTION_ROLES[4 if has_des_vars else 3]] += coupled_functions + post_functions
        return

    def create_mpg(self, name='MPG'):
        """Function to automatically create a MPG based on an MDG.

        :param name: name for the MPG graph
        :type name: str
        :return: unconnected MDG (only action blocks and their diagonal position)
        :rtype: MdaoProcessGraph
        """
        from kadmos.graph.graph_process import MdaoProcessGraph
        mpg = MdaoProcessGraph(self, name=name)
        node_list = list(mpg.nodes)
        for node in node_list:
            if 'category' not in mpg.nodes[node]:
                raise AssertionError('category attribute missing for node: {}.'.format(node))
            elif mpg.nodes[node]['category'] == 'variable':
                mpg.remove_node(node)
            elif mpg.nodes[node]['category'] not in ['variable', 'function']:
                raise AssertionError('Node {} has invalid category attribute: {}.'.format(node,
                                                                                          mpg.nodes[node]['category']))
        mpg._add_diagonal_positions()
        return mpg

    def get_mpg(self, name='MPG'):
        """Create the MDAO process graph for a given FPG.

        :param name: name of the new graph
        :type name: str
        :return: MDAO process graph
        :rtype: MdaoProcessGraph
        """

        # Start-up checks
        logger.info('Composing MPG...')
        assert isinstance(name, string_types)
        self.check(raise_error=True)

        # Make clean copy of the graph to avoid unwanted links and updates
        mdg = self.copy_as(MdaoDataGraph, as_view=True)

        # Local variables
        coor = mdg.COORDINATOR_STRING
        mdao_arch = mdg.graph['problem_formulation']['mdao_architecture']

        # Get the monolithic function ordering from the MDG and assign function lists accordingly.
        mg_function_ordering = mdg.graph['mg_function_ordering']
        pre_desvars_funcs = mg_function_ordering[mdg.FUNCTION_ROLES[3]]
        post_desvars_funcs = mg_function_ordering[mdg.FUNCTION_ROLES[4]]
        coup_functions = mdg.sort_nodes_for_process(mg_function_ordering[mdg.FUNCTION_ROLES[1]])
        post_functions = mg_function_ordering[mdg.FUNCTION_ROLES[2]]
        mg_function_ordering[mdg.FUNCTION_ROLES[1]] = list(coup_functions)
        mdg.graph['mg_function_ordering'] = mg_function_ordering

        # Check for partitions in monolithic architectures
        if mdao_arch in mdg.OPTIONS_ARCHITECTURES[1:4] and 'coupled_functions_groups' in \
                mdg.graph['problem_formulation']:
            partitions = mdg.graph['problem_formulation']['coupled_functions_groups']
            distr_function_ordering = mdg.graph['distr_function_ordering']
            pre_desvars_funcs = distr_function_ordering[0][mdg.FUNCTION_ROLES[3]]
            post_desvars_funcs = distr_function_ordering[0][mdg.FUNCTION_ROLES[4]]
            post_functions = distr_function_ordering[0][mdg.FUNCTION_ROLES[2]]
            # Update function order coupled nodes for optimal process
            for partition in range(len(partitions)):
                if partition in mdg.graph['problem_formulation']['local_convergers']:
                    distr_function_ordering[1][partition][mdg.FUNCTION_ROLES[1]] = \
                        mdg.sort_nodes_for_process(distr_function_ordering[1][partition][mdg.FUNCTION_ROLES[1]])
                else:
                    distr_function_ordering[1][partition][mdg.FUNCTION_ROLES[2]] = \
                        mdg.sort_nodes_for_process(distr_function_ordering[1][partition][mdg.FUNCTION_ROLES[4]] +
                                                   distr_function_ordering[1][partition][mdg.FUNCTION_ROLES[1]] +
                                                   distr_function_ordering[1][partition][mdg.FUNCTION_ROLES[2]])
                    distr_function_ordering[1][partition][mdg.FUNCTION_ROLES[4]] = \
                        distr_function_ordering[1][partition][mdg.FUNCTION_ROLES[1]] = []
            mdg.graph['distr_function_ordering'] = distr_function_ordering
        else:
            partitions = None

        # Set up MDAO process graph
        mpg = mdg.create_mpg(name=name)

        # Make process step of the coordinator equal to zero
        mpg.nodes[coor]['process_step'] = 0

        # Add process edges for each architecture
        if mdao_arch == mdg.OPTIONS_ARCHITECTURES[0]:  # unconverged-MDA
            sequence = [coor] + pre_desvars_funcs + coup_functions + post_functions
            mpg.add_process(sequence, 0, mdg, end_in_iterative_node=coor)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
            _, sys_conv, _ = self.get_architecture_node_ids(mdao_arch, number_of_groups=len(partitions)) if \
                partitions else ([], mdg.CONVERGER_STRING, [])
            sys_conv = [] if sys_conv not in mdg.nodes() else sys_conv
            sequence1 = [coor] + pre_desvars_funcs + [sys_conv] if sys_conv else [coor] + pre_desvars_funcs
            mpg.add_process(sequence1, 0, mdg)
            if sys_conv:
                if partitions:
                    mpg.add_process_partitions([sys_conv], partitions, [], mpg.nodes[sequence1[-1]]['process_step'], mdg,
                                               end_in_iterative_node=sys_conv)
                else:
                    sequence2 = [sys_conv] + coup_functions
                    mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg,
                                    end_in_iterative_node=sys_conv)
                if post_functions:
                    sequence3 = [sys_conv] + post_functions
                    mpg.add_process(sequence3, mpg.nodes[sys_conv]['converger_step'], mdg, end_in_iterative_node=coor)
                else:
                    mpg.connect_nested_iterators(coor, sys_conv)
            else:  # With perfect clusters, there is no system converger
                mpg.add_process_partitions(sequence1, partitions, post_functions, mpg.nodes[sequence1[0]][
                    'process_step'], mdg, end_in_iterative_node=coor)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[2]:  # IDF
            sys_opt, _, _ = self.get_architecture_node_ids(mdao_arch, number_of_groups=len(partitions)) if \
                partitions else (mdg.OPTIMIZER_STRING, [], [])
            sequence1 = [coor] + pre_desvars_funcs + [sys_opt]
            mpg.add_process(sequence1, 0, mdg)
            if partitions:
                sequence2 = [sys_opt] + post_desvars_funcs
                sequence3 = post_functions
                mpg.add_process_partitions(sequence2, partitions, sequence3, mpg.nodes[sequence1[-1]]['process_step'],
                                           mdg, end_in_iterative_node=sys_opt)
            else:
                sequence2 = [sys_opt] + post_desvars_funcs + coup_functions + post_functions
                mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=sys_opt)
            mpg.connect_nested_iterators(coor, sys_opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[3]:  # MDF
            sys_opt, sys_conv, _ = self.get_architecture_node_ids(mdao_arch, number_of_groups=len(partitions)) if \
                partitions else (mdg.OPTIMIZER_STRING, mdg.CONVERGER_STRING, [])
            sys_conv = [] if sys_conv not in mdg.nodes() else sys_conv
            sequence1 = [coor] + pre_desvars_funcs + [sys_opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [sys_opt] + post_desvars_funcs + [sys_conv] if sys_conv else [sys_opt] + post_desvars_funcs
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg)
            if sys_conv:
                if partitions:
                    mpg.add_process_partitions([sys_conv], partitions, [], mpg.nodes[sequence2[-1]]['process_step'], mdg,
                                               end_in_iterative_node=sys_conv)
                else:
                    sequence3 = [sys_conv] + coup_functions
                    mpg.add_process(sequence3, mpg.nodes[sequence2[-1]]['process_step'], mdg,
                                    end_in_iterative_node=sys_conv)
                sequence4 = [sys_conv] + post_functions
                mpg.add_process(sequence4, mpg.nodes[sys_conv]['converger_step'], mdg, end_in_iterative_node=sys_opt)
            else:  # With perfect clusters, there is no system converger
                mpg.add_process_partitions(sequence2, partitions, post_functions,
                                           mpg.nodes[sequence2[0]]['process_step'], mdg, end_in_iterative_node=sys_opt)
            mpg.connect_nested_iterators(coor, sys_opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[4]:  # unconverged-OPT
            opt = mdg.OPTIMIZER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [opt] + post_desvars_funcs + coup_functions + post_functions
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=opt)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[5]:  # unconverged-DOE
            doe = mdg.DOE_STRING
            sequence1 = [coor] + pre_desvars_funcs + [doe]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [doe] + post_desvars_funcs + coup_functions + post_functions
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=doe)
            mpg.connect_nested_iterators(coor, doe)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
            doe = mdg.DOE_STRING
            conv = mdg.CONVERGER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [doe]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [doe] + post_desvars_funcs + [conv]
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg)
            sequence3 = [conv] + coup_functions
            mpg.add_process(sequence3, mpg.nodes[sequence2[-1]]['process_step'], mdg, end_in_iterative_node=conv)
            if post_functions:
                sequence4 = [conv] + post_functions
                mpg.add_process(sequence4, mpg.nodes[conv]['converger_step'], mdg, end_in_iterative_node=doe)
            else:
                mpg.connect_nested_iterators(doe, conv)
            mpg.connect_nested_iterators(coor, doe)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[7]:  # CO
            distr_function_ordering = mdg.graph['distr_function_ordering']
            n_groups = len(distr_function_ordering[1])
            sys_opt, sub_opts = self.get_architecture_node_ids(mdao_arch, number_of_groups=n_groups)
            sequence1 = [coor] + distr_function_ordering[0][self.FUNCTION_ROLES[3]] + [sys_opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [sys_opt] + distr_function_ordering[0][self.FUNCTION_ROLES[4]] + \
                        distr_function_ordering[0][self.FUNCTION_ROLES[2]]
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=sys_opt)
            for idx, subgroup in enumerate(distr_function_ordering[1]):
                sequence3 = [sys_opt, sub_opts[idx]]
                mpg.connect_nested_iterators(sys_opt, sub_opts[idx], direction='master->slave')
                sequence4 = [sub_opts[idx]] + subgroup[self.FUNCTION_ROLES[4]] + subgroup[self.FUNCTION_ROLES[1]] + \
                             subgroup[self.FUNCTION_ROLES[2]]
                mpg.add_process(sequence4, mpg.nodes[sequence3[-1]]['process_step'], mdg,
                                end_in_iterative_node=sub_opts[idx])
                mpg.connect_nested_iterators(sys_opt, sub_opts[idx])
            mpg.connect_nested_iterators(coor, sys_opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[8]:  # BLISS-2000
            distr_function_ordering = mdg.graph['distr_function_ordering']
            n_groups = len(distr_function_ordering[1])
            sys_opt, sys_conv, _, sub_does, sub_opts, sub_convs = \
                self.get_architecture_node_ids(mdao_arch, number_of_groups=n_groups)
            sequence1 = [coor] + distr_function_ordering[0][self.FUNCTION_ROLES[3]] + [sys_conv]
            sub_does_cs = []
            for idx, subgroup in enumerate(distr_function_ordering[1]):
                if not mpg.has_node(sub_convs[idx]):
                    sequence2 = sequence1 + [sub_does[idx]] + subgroup[self.FUNCTION_ROLES[3]] + \
                                [sub_opts[idx]] + subgroup[self.FUNCTION_ROLES[4]] + subgroup[self.FUNCTION_ROLES[1]] + \
                                subgroup[self.FUNCTION_ROLES[2]]
                    mpg.add_process(sequence2, 0, mdg,
                                    end_in_iterative_node=sub_opts[idx])
                else:
                    sequence2a = sequence1 + [sub_does[idx]] + subgroup[self.FUNCTION_ROLES[3]] + \
                                 [sub_opts[idx]] + subgroup[self.FUNCTION_ROLES[4]] + [sub_convs[idx]]
                    mpg.add_process(sequence2a, 0, mdg)
                    sequence2b = [sub_convs[idx]] + subgroup[self.FUNCTION_ROLES[1]]
                    mpg.add_process(sequence2b, mpg.nodes[sequence2a[-1]]['process_step'], mdg,
                                    end_in_iterative_node=sub_convs[idx])
                    sequence2c = [sub_convs[idx]] + subgroup[self.FUNCTION_ROLES[2]]
                    mpg.add_process(sequence2c, mpg.nodes[sub_convs[idx]]['converger_step'], mdg,
                                    end_in_iterative_node=sub_opts[idx])
                mpg.connect_nested_iterators(sub_does[idx], sub_opts[idx])
                sequence3 = [sub_does[idx]] + [sys_opt]
                mpg.add_process(sequence3, mpg.nodes[sub_does[idx]]['converger_step'], mdg)
                sub_does_cs.append(mpg.nodes[sub_does[idx]]['converger_step'])
            mpg.nodes[sys_opt]['process_step'] = max(sub_does_cs) + 1
            sequence4 = [sys_opt] + distr_function_ordering[0][self.FUNCTION_ROLES[4]] + \
                        distr_function_ordering[0][self.FUNCTION_ROLES[1]] + \
                        distr_function_ordering[0][self.FUNCTION_ROLES[2]]
            mpg.add_process(sequence4, mpg.nodes[sequence3[-1]]['process_step'], mdg,
                            end_in_iterative_node=sequence4[0])
            mpg.connect_nested_iterators(sys_conv, sys_opt)
            mpg.connect_nested_iterators(coor, sys_conv)

        mpg.graph['process_hierarchy'] = mpg.get_process_hierarchy()

        logger.info('Composed MPG.')

        return mpg
