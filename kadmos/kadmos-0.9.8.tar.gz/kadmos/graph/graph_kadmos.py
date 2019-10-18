from __future__ import absolute_import, division, print_function

# Import packages
import copy
import filecmp
import inspect
import itertools
import json
import logging
import os
import pprint
import re
import shutil
import tempfile

from lxml import etree

import networkx as nx
import uuid
from builtins import int
from six import iteritems, string_types

from kadmos.utilities.strings import get_correctly_extended_latex_label

assert int(nx.__version__.split('.')[0]) >= 2, 'KADMOS only works with the NetworkX package of v2.0 and higher. ' \
                                               'Current version installed: {}'.format(nx.__version__)
import matplotlib.pyplot as plt

from datetime import datetime
from copy import deepcopy
from collections import OrderedDict

from kadmos.external.XDSM_writer.XDSM import XDSM
from kadmos.cmdows.cmdows import CMDOWS

from ..utilities import prompting
from ..utilities import printing
from ..utilities.general import transform_data_into_strings, transform_string_into_format, get_list_entries, \
    open_file, color_list, test_attr_cond, translate_list, zip_file, unzip_file, add_nested_dict_entry
from ..utilities.xmls import Element, parser, recursively_empty, recursively_stringify, get_uid_search_xpath
from ..utilities.testing import check

from kadmos.graph.mixin_equation import EquationMixin
from kadmos.graph.mixin_vistoms import VistomsMixin


# Settings for the logger
logger = logging.getLogger(__name__)


# Settings for the KADMOS file types and the corresponding extensions
file_types = ['cmdows', 'kdms', 'graphml', 'zipped-cmdows']
file_extensions = ['xml', 'kdms', 'graphml', 'zip']


class KadmosGraph(nx.DiGraph, EquationMixin, VistomsMixin):

    # Hardcoded values and naming convention
    OPTIONS_ARCHITECTURES = ['unconverged-MDA',          # 0
                             'converged-MDA',            # 1
                             'IDF',                      # 2
                             'MDF',                      # 3
                             'unconverged-OPT',          # 4
                             'unconverged-DOE',          # 5
                             'converged-DOE',            # 6
                             'CO',                       # 7
                             'BLISS-2000']               # 8
    OPTIONS_DOE_METHODS = ['Full factorial design',   # 0
                           'Latin hypercube design',  # 1
                           'Monte Carlo design',      # 2
                           'Custom design table',     # 3
                           'Uniform design',          # 4
                           'Box-Behnken design']      # 5
    OPTIONS_CONVERGERS = ['Jacobi', 'Gauss-Seidel', None]
    # TODO: Remove first entry
    FUNCTION_ROLES = ('UNUSED_REMOVE', 'coupled', 'post-coupling', 'uncoupled-des-var-ind', 'uncoupled-des-var-dep')
    FUNCTION_ROLES_NODESTYLES = ['PreAnalysisDVI',   # 0
                                 'CoupledAnalysis',  # 1
                                 'PostAnalysis',     # 2
                                 'PreAnalysisDVI',   # 3
                                 'PreAnalysisDVD']   # 4
    CMDOWS_VERSION = '0.9'
    CMDOWS_ATTRIBUTES = ['nominal_value', 'valid_ranges', 'constraint_type', 'constraint_operator',
                         'reference_value', 'required_equality_precision', 'samples', 'variable_type']
    CMDOWS_ATTRIBUTE_DICT = {i: j for i, j in zip(CMDOWS_ATTRIBUTES, [k for k in CMDOWS_ATTRIBUTES])}
    CMDOWS_ATTRIBUTE_DICT_INV = {i: j for j, i in iteritems(CMDOWS_ATTRIBUTE_DICT)}
    LIMIT_RANGE_DICT = {'limit_range_local': 'local',
                        'limit_range_global': 'global',
                        'limit_range': None}
    PROBLEM_ROLES_VARS = ['design variable',       # 0
                          'objective',             # 1
                          'constraint',            # 2
                          'quantity of interest']  # 3
    PROBLEM_ROLES_VAR_SUFFIXES = ['__desVar__',    # 0
                                  '__objVar__',    # 1
                                  '__conVar__',    # 2
                                  '__statVar__']   # 3
    CMDOWS_ROLES_DEF = [['designVariable', ['nominal_value', 'valid_ranges',
                                            'variable_type', 'samples']],
                        ['objectiveVariable', []],
                        ['constraintVariable', ['constraint_type', 'constraint_operator',
                                                'reference_value', 'required_equality_precision']],
                        ['stateVariable', []]]
    CMDOWS_ROLES_DICT = {i: j for i, j in zip(PROBLEM_ROLES_VARS, PROBLEM_ROLES_VAR_SUFFIXES)}
    CMDOWS_ROLES_DICT_INV = {i: j for j, i in iteritems(CMDOWS_ROLES_DICT)}
    # TODO: Combine following three lists in a dict (or object?)
    ARCHITECTURE_ROLES_VARS = ['initial guess coupling variable',  # 0
                               'final coupling variable',          # 1
                               'coupling copy variable',           # 2
                               'initial guess design variable',    # 3
                               'final design variable',            # 4
                               'final output variable',            # 5
                               'consistency constraint variable',  # 6
                               'doe input sample list',            # 7
                               'doe output sample list',           # 8
                               'copy design variable',             # 9
                               'surrogate model approximate',      # 10
                               'coupling weight']                  # 11
    ARCHITECTURE_ROLES_FUNS = ['coordinator',                      # 0
                               'optimizer',                        # 1
                               'converger',                        # 2
                               'doe',                              # 3
                               'UNUSED_REMOVE',                    # 4  # TODO: remove entry
                               'uncoupled-des-var-ind analysis',   # 5
                               'uncoupled-des-var-dep analysis',   # 6
                               'coupled analysis',                 # 7
                               'post-coupling analysis',           # 8
                               'surrogate model',                  # 9
                               'distributed system converger']     # 10
    ARCHITECTURE_ROLES_NODESTYLES = ['Coordinator',                # 0
                                     'Optimization',               # 1
                                     'Converger',                  # 2
                                     'DOE',                        # 3
                                     'PreAnalysisDVI',             # 4
                                     'PreAnalysisDVI',             # 5
                                     'PreAnalysisDVD',             # 6
                                     'CoupledAnalysis',            # 7
                                     'PostAnalysis',               # 8
                                     'Metamodel',                  # 9
                                     'Converger']                  # 10
    CMDOWS_ARCHITECTURE_ROLE_SPLITTER = get_list_entries(ARCHITECTURE_ROLES_FUNS, 0, 1, 2, 3, 9, 10)
    SYS_PREFIX = 'Sys-'
    SUBSYS_PREFIX = 'Sub-'
    SUBSYS_SUFFIX = '-'
    COORDINATOR_STRING = 'Coordinator'
    COORDINATOR_LABEL = 'COOR'
    CONVERGER_STRING = 'Converger'
    CONVERGER_LABEL = 'CONV'
    CONSCONS_STRING = 'Gc'
    CONSCONS_LABEL = 'Gc'
    CONSCONS_SUFFIX = '__'
    COF_STRING = '__J'
    COF_SUFFIX = '__'
    COF_LABEL = 'J'
    WCF_STRING = 'WCF'
    WCF_SUFFIX = '__'
    WCF_LABEL = 'WCF'
    DOE_STRING = 'DOE'
    DOE_LABEL = 'DOE'
    OPTIMIZER_STRING = 'Optimizer'
    OPTIMIZER_LABEL = 'OPT'
    SM_STRING = 'Surrogate-Model'
    SM_LABEL = 'SM'
    SMBD_STRING = 'SM-bounds'
    SMBD_LABEL = 'SMBD'
    SMB_STRING = 'SM-builder'
    SMB_LABEL = 'SMB'
    INSTANCE_SUFFIX = '__i'
    NODE_GROUP_SUBCATS = {'all variables':
                              ['hole', 'supplied input', 'supplied shared input', 'output', 'collision', 'coupling',
                               'shared coupling', 'collided coupling', 'collided shared coupling',
                               'pure circular coupling', 'shared circular coupling', 'collided circular coupling',
                               'collided shared circular coupling', 'initial guess design variable',
                               'final design variable', 'MDA coupling variable', 'initial guess MDA coupling variable',
                               'final MDA coupling variable', 'final output variable',
                               'consistency constraint variable'],
                          'all inputs':
                              ['supplied input', 'supplied shared input', 'supplied input group',
                               'supplied shared input group'],
                          'all outputs':
                              ['output', 'collision', 'output group', 'final output variable'],
                          'all couplings':
                              ['coupling', 'shared coupling', 'collided coupling', 'collided shared coupling',
                               'coupling group', 'shared coupling group', 'MDA coupling variable',
                               'initial guess MDA coupling variable', 'final MDA coupling variable'],
                          'all circular variables':
                              ['pure circular coupling', 'shared circular coupling',
                               'collided circular coupling', 'collided shared circular coupling'],
                          'all collisions':
                              ['collision', 'collided coupling', 'collided shared coupling',
                               'collided circular coupling', 'collided shared circular coupling'],
                          'all splittable variables': ['pure circular coupling',
                                                       'shared circular coupling', 'collided coupling',
                                                       'collision', 'collided circular coupling',
                                                       'collided shared coupling',
                                                       'collided shared circular coupling'],
                          'all problematic variables': ['hole', 'pure circular coupling',
                                                        'shared circular coupling', 'collided coupling',
                                                        'collision', 'collided circular coupling',
                                                        'collided shared coupling',
                                                        'collided shared circular coupling'],
                          'all problematic functions': ['independent', 'sink']
                          }

    def __init__(self, *args, **kwargs):

        # Inherit init from nx.DiGraph
        super(KadmosGraph, self).__init__(*args, **kwargs)

        # Handle knowledge base path attribute (transitive properties)
        # TODO: remove this
        if 'kb_path' in kwargs:
            self.graph['kb_path'] = kwargs['kb_path']

        # Handle name
        if 'name' in kwargs:
            self.graph['name'] = kwargs['name']

        # Init states
        self.GRAPH_IS_CONTRACTED = False

        # Hardcoded properties by which graphs are analyzed
        # related to self.get_graph_properties()
        self.GRAPH_PROPERTIES = ["functions", "nodes", "edges", "couplings", "system_inputs"]  # TODO: Add n_functions
        # Hardcoded values and naming convention
        self.NODE_CAT_TREE = {'variable': {'hole': [],
                                           'supplied input': [],
                                           'supplied shared input': [],
                                           'output': [],
                                           'collision': [],
                                           'coupling': [],
                                           'pure circular coupling': [],
                                           'shared coupling': [],
                                           'shared circular coupling': [],
                                           'collided coupling': [],
                                           'collided circular coupling': [],
                                           'collided shared coupling': [],
                                           'collided shared circular coupling': []},
                              'variable group': {'hole group': [],
                                                 'supplied input group': [],
                                                 'supplied shared input group': [],
                                                 'output group': [],
                                                 'coupling group': [],
                                                 'shared coupling group': []},
                              'function': {'independent': [],
                                           'source': [],
                                           'sink': [],
                                           'complete': []},
                              'architecture element': {'initiator': [],
                                                       'optimizer': [],
                                                       'MDA': [],
                                                       'optimizer function': [],
                                                       'MDA analysis': [],
                                                       'independent output function': [],
                                                       'initial guess design variable': [],
                                                       'final design variable': [],
                                                       'final output variable': [],
                                                       'MDA coupling variable': [],
                                                       'initial guess MDA coupling variable': [],
                                                       'final MDA coupling variable': [],
                                                       'consistency constraint variable': [],
                                                       'doe input sample list': [],  # 7
                                                       'doe output sample list': [],  # 8
                                                       'copy design variable': [],  # 9
                                                       'surrogate model approximate': [],
                                                       'coupling weight': []},
                              'RCE component': {'Input Provider': [],
                                                'XML Merger': [],
                                                'XML Loader': [],
                                                'XML PyMerger': [],
                                                'CPACS Tool': [],
                                                'Converger': [],
                                                'Optimizer': [],
                                                'Consistency constraint function': []}}

    def assert_node_exists(self, node):
        if not isinstance(node, list):
            assert self.has_node(node), 'Node {} does not exist in the graph.'.format(node)
        else:
            for n in node:
                assert self.has_node(n), 'Node {} does not exist in the graph.'.format(node)

    def assert_node_exists_not(self, node):
        assert not self.has_node(node), 'Node {} already exists in the graph.'.format(node)

    def assert_node_attribute(self, node, attrb):
        assert attrb in self.nodes[node], 'Node {} does not have the expected attribute {}.'.format(node, attrb)

    def assert_node_attribute_and_value(self, node, attrb, value):
        assert attrb in self.nodes[node], 'Node {} does not have the expected attribute {}.'.format(node, attrb)
        assert self.nodes[node][attrb] == value, 'Node {} attribute {} does not have the expected value' \
                                                 ' {}.'.format(node, attrb, value)

    def assert_node_categories(self):
        for node in self.nodes:
            if 'category' not in self.nodes[node]:
                raise KeyError('Node {} misses a category.'.format(node))

    def assert_and_get_node_attribute(self, node, attrb):
        self.assert_node_attribute(node, attrb)
        return self.nodes[node][attrb]

    def get_node_attribute(self, node, attrb):
        if self.assert_node_attribute(node, attrb):
            return self.nodes[node][attrb]
        else:
            return None

    def assert_graph_attribute(self, attrb):
        assert attrb in self.graph, 'Attribute {} is missing in the graph.'.format(attrb)

    def assert_or_add_attribute(self, attrb, val=None):
        if attrb not in self.graph:
            self.graph[attrb] = val

    def add_fnode(self, function_id, **attr_dict):
        """Add a function node"""
        attr_dict['category'] = 'function'
        if 'function_type' not in attr_dict:
            attr_dict['function_type'] = 'regular'
        if 'instance' not in attr_dict:
            attr_dict['instance'] = 0
        self.add_node(function_id, attr_dict)

    def add_fnodes(self, *function_ids):
        """Add multiple function nodes at once"""
        if len(function_ids) == 1:
            if isinstance(function_ids[0], (list, tuple)):
                function_ids = function_ids[0]
        for function_id in function_ids:
            self.add_fnode(function_id)

    def add_nested_attribute(self, attrbs, val, current_dict=None):
        assert isinstance(attrbs, (list, tuple)), 'Input attributes should be a list or tuple, now is a {}'\
            .format(type(attrbs))
        if current_dict is None:
            current_dict = self.graph
        else:
            current_dict = current_dict
        for i, attrb in enumerate(attrbs):
            if attrb not in current_dict:
                current_dict[attrb] = dict()
            if i == len(attrbs)-1:
                current_dict[attrb] = val
            else:
                if not isinstance(current_dict[attrb], dict):
                    current_dict[attrb] = dict()
                current_dict = current_dict[attrb]

    def graph_has_nested_attributes(self, *attrbs):
        """Method to test if graph has nested attributes

        :param attrbs: attributes to check for nesting in graph
        :type attrbs: str
        :return: presence of nested attribute
        :rtype: bool
        """

        if len(attrbs) == 1:
            attrbs = attrbs[0]
            if isinstance(attrbs, string_types):
                attrbs = [attrbs]
            assert isinstance(attrbs, (list, tuple)), 'Input attributes should be a list, tuple or comma-separated ' \
                                                      'arguments, now is a {}' \
                .format(type(attrbs))
        current_dict = self.graph
        for attrb in attrbs:
            if attrb in current_dict:
                current_dict = current_dict[attrb]
            else:
                return False
        return True

    def deepcopy(self):
        """Method to make a deep copy of a graph.

        :return: deepcopy of the graph
        :rtype: KadmosGraph
        """

        deep_copied_graph = copy.deepcopy(self)

        return deep_copied_graph

    def deepcopy_as(self, graph_class):
        """Method to make a deep copy of a graph and make it into another KADMOS graph class.

        :return: deepcopy of the graph
        :rtype: KadmosGraph
        """

        assert inspect.isclass(graph_class), 'graph_class input should be a class object.'

        deep_copied_graph = copy.deepcopy(self)

        # Instantiate new graph in new class
        deep_copied_graph = deep_copied_graph.change_graph_class(graph_class)

        return deep_copied_graph

    def copy_as(self, graph_class, as_view=False):
        """Method to make a copy of a graph and make it into another KADMOS graph class.

        :return: copy of the graph
        :rtype: KadmosGraph
        """

        assert inspect.isclass(graph_class), 'graph_class input should be a class object.'

        copied_graph = KadmosGraph(self.copy(as_view=as_view))

        # Instantiate new graph in new class
        copied_graph = copied_graph.change_graph_class(graph_class)

        return copied_graph

    def change_graph_class(self, graph_class):
        """Method to adjust the class of a graph.

        :return: newly classed graph.
        :rtype: graph_class
        """

        self = graph_class(self)
        return self

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CHECKING METHODS                                                      #
    # ---------------------------------------------------------------------------------------------------------------- #

    def check(self, raise_error=False):
        """Method to check the graph for validity and completeness.

        :param raise_error: determines if an error should be raised in case of an invalid graph
        :type raise_error: bool

        :return: result of the check
        :rtype: bool

        .. note:: Several checks are performed. However the method does not guarantee the validity of the graph.

        The checks are split into several categories and the methods _check_category_a, _check_category_b and
        _check_category_c are used to determine the overall validity and completeness. These sub methods are generally
        defined below and are then further refined in child classes.
        """

        # Logging
        logger.info('Checking ' + self.__class__.__name__ + '...')

        # Set check
        graph_check = True

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')
        var_nodes = self.find_all_nodes(category='variable')

        # Get information
        n_nodes = self.number_of_nodes()
        n_functions = len(func_nodes)
        n_variables = len(var_nodes)
        n_edges = self.number_of_edges()

        # Logging
        logger.info('Logging general checking info...')
        logger.info('Name: ' + str(self.graph.get('name')))
        logger.info('Number of nodes: ' + str(n_nodes))
        logger.info('Number of functions: ' + str(n_functions))
        logger.info('Number of variables: ' + str(n_variables))
        logger.info('Number of edges: ' + str(n_edges))
        logger.info('Successfully logged general checking info.')

        # Category A checks
        logger.info('Performing category A checks...')
        cat_a_check, n = self._check_category_a()
        if cat_a_check:
            logger.info('Successfully performed ' + str(n - 1) + ' category A checks.')
        else:
            graph_check = False
            logger.warning('Unsuccessfully performed category A checks.')

        # Category B checks
        if graph_check:
            logger.info('Performing category B checks...')
            cat_b_check, n = self._check_category_b()
            if cat_b_check:
                logger.info('Successfully performed ' + str(n - 1) + ' category B checks.')
            else:
                graph_check = False
                logger.warning('Unsuccessfully performed category B checks.')
        else:
            logger.info('Skipping category B checks as category A checks already yielded warnings.')

        # Category C checks (only performed if everything else is fine until now)
        if graph_check:
            logger.info('Performing category C checks...')
            cat_c_check, n = self._check_category_c()
            if cat_c_check:
                logger.info('Successfully performed ' + str(n - 1) + ' category C checks.')
            else:
                graph_check = False
                logger.warning('Unsuccessfully performed category C checks.')
        else:
            logger.info('Skipping category C checks as category A or B checks already yielded warnings.')

        # Final result
        if graph_check:
            logger.info('Successfully checked ' + self.__class__.__name__ + '.')
        else:
            logger.warning('Unsuccessfully checked ' + self.__class__.__name__ + '.')
            if raise_error:
                raise RuntimeError(
                    'Checking the graph ' + self.__class__.__name__ + ' failed. For detailed information '
                                                                      'please consult the log.')

        # Return
        return graph_check

    def _check_category_a(self):
        """Basic method to perform a category A check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check = True
        i = 1

        # General checks
        from kadmos.graph.graph_data import RepositoryConnectivityGraph
        if not isinstance(self, RepositoryConnectivityGraph):
            prob_var_nodes = self.find_all_nodes(category='variable', subcategory='all problematic variables')
            prob_fun_nodes = self.find_all_nodes(category='function', subcategory='all problematic functions')
            category_check, i = check(prob_var_nodes,
                                      'There are still problematic variable nodes in the graph, namely: %s.'
                                      % str(prob_var_nodes),
                                      status=category_check,
                                      category='A',
                                      i=i)
            category_check, i = check(prob_fun_nodes,
                                      'There are still problematic function nodes in the graph, namely: %s.'
                                      % str(prob_fun_nodes),
                                      status=category_check,
                                      category='A',
                                      i=i)

        # Equation checks
        eq_nodes_a = list(set([out_edge[0] for out_edge in self.out_edges(data=True) if 'equations' in out_edge[2]]))
        eq_nodes_b = self._get_equation_nodes()
        # TODO: Determine if this check should be critical
        category_check_na, i = check(len(eq_nodes_a) != len(eq_nodes_b),
                                     'Some nodes in the graph have output edges with and without equations. These are: '
                                     + ', '.join([node for node in eq_nodes_a if node not in eq_nodes_b]),
                                     status=category_check,
                                     category='A',
                                     i=i)

        # Return
        return category_check, i

    def _check_category_b(self):
        """Basic method to perform a category B check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check = True
        i = 1

        # Checks
        if self.graph.get('problem_formulation', {}).get('doe_settings'):
            category_check, i = check('DOE' not in self.graph['problem_formulation'].get('mdao_architecture') and
                                      'BLISS-2000' not in self.graph['problem_formulation'].get('mdao_architecture'),
                                      'DOE settings are only allowed in DOE architectures',
                                      status=category_check,
                                      category='B',
                                      i=i + 1)

        # Return
        return category_check, i

    def _check_category_c(self):
        """Basic method to perform a category C check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check = True
        i = 1

        # Return
        return category_check, i

    def check_cmdows_integrity(self, convention=True, mpg=None):
        """Method to check the integrity of the CMDOWS file that can be created with the save method.

        :param convention: option for applying a UID convention
        :type convention: bool
        :param mpg: MPG to be saved together with graph
        :type mpg: MdaoProcessGraph

        :return: check result
        :rtype: bool

        The integrity check is graph specific and thus needs to be executed for every graph before saving as CMDOWS if
        one wants to be sure that the CMDOWS file is integer. Due to its relative long runtime this check is however not
        performed automatically when using the save method.
        """

        logger.info('Performing CMDOWS integrity check...')

        # Initial Settings
        tempdir = tempfile.mkdtemp()
        timestamp = datetime.now()
        result = False

        try:
            # Check if saving and reading CMDOWS files does work properly
            # Saving
            self._save_cmdows(os.path.join(tempdir, 'testfile1.xml'),
                              description='test description',
                              creator='test author',
                              version='1.1',
                              timestamp=timestamp,
                              mpg=mpg,
                              convention=convention,
                              check=False)
            # Loading
            check_graph, check_mpg = _load_cmdows(os.path.join(tempdir, 'testfile1.xml'), False)
            # Saving
            # noinspection PyProtectedMember
            check_graph._save_cmdows(os.path.join(tempdir, 'testfile2.xml'),
                                     description='test description',
                                     creator='test author',
                                     version='1.1',
                                     timestamp=timestamp,
                                     mpg=check_mpg,
                                     convention=convention,
                                     check=False)

            # First compare files fast
            if filecmp.cmp(os.path.join(tempdir, 'testfile1.xml'), os.path.join(tempdir, 'testfile2.xml')):
                result = True
            # If fast comparison fails also try logical comparison
            # This is needed as some (dictionary) elements of the graph might not be in the correct order after loading
            else:
                logger.debug(
                    'Logical CMDOWS comparison is used for the CMDOWS integrity check instead of file wise '
                    'comparison.')
                # Parse
                test_file = etree.parse(os.path.join(tempdir, 'testfile1.xml'))
                check_file = etree.parse(os.path.join(tempdir, 'testfile2.xml'))
                # Convert
                test_list = recursively_stringify(test_file)
                check_list = recursively_stringify(check_file)
                # Check
                if test_list == check_list:
                    result = True
                else:
                    logger.warning('The following element(s) are not loaded: ' +
                                   str([x for x in test_list if x not in set(check_list)]))

        except IOError as error:
            logger.warning('An unexpected error occurred during the CMDOWS integrity check: ' + str(error))
            pass

        finally:
            shutil.rmtree(tempdir)

        # Logging and warning
        if result:
            logger.info('CMDOWS integrity check passed.')
        else:
            logger.warning('Not all elements are written to/read from the CMDOWS file. CMDOWS integrity check failed.')

        return result

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #
    def create_dsm(self, file_name, destination_folder=None, open_pdf=False, mpg=None, include_system_vars=True,
                   summarize_vars=False, function_order=None, keep_tex_file=False, abbreviate_keywords=False,
                   compile_pdf=True, colors_based_on='function_roles', pdflatex_path=None):
        """Method to create a (X)DSM PDF file

        :param file_name: name of the file to be saved
        :type file_name: str
        :param destination_folder: destination folder for the file to be saved
        :type destination_folder: str
        :param open_pdf: option for opening the created file directly
        :type open_pdf: bool
        :param mpg: optional MPG graph to be saved with MDG as XDSM (if None a DSM is created)
        :type mpg: MdaoProcessGraph
        :param include_system_vars: option for including system variables (only applicable for DSMs)
        :type include_system_vars: bool
        :param summarize_vars: option for summarizing label
        :type summarize_vars: bool
        :param function_order: optional function order for the diagonal of the graph (only applicable for DSMs)
        :type function_order: list
        :param keep_tex_file: optional argument to keep the tex file of the PDF
        :type keep_tex_file: bool
        :param abbreviate_keywords: optional argument to keep make keywords shorter (input -> inp., output -> outp.)
        :type abbreviate_keywords: bool
        :param colors_based_on: option to base the colors either on the problem role or the partitions
        :type colors_based_on: str
        :param pdflatex_path: option to add full path to pdflatex command if pdflatex is not part of the system commands
        :type colors_based_on: str or None
        """

        from kadmos.graph.graph_data import RepositoryConnectivityGraph, FundamentalProblemGraph, \
            MdaoDataGraph

        # Input assertions
        assert isinstance(open_pdf, bool)
        assert isinstance(include_system_vars, bool)
        assert isinstance(summarize_vars, bool)
        assert isinstance(function_order, list) or function_order is None
        assert isinstance(keep_tex_file, bool)
        assert keep_tex_file or compile_pdf, 'The settings do not make sense, set either keep_tex_file or compile_pdf' \
                                             ' to True, or both!'
        if colors_based_on == 'partitions':
            assert 'coupled_functions_groups' in self.graph['problem_formulation'], 'Graph is not partitioned.'
        if colors_based_on == 'function_roles':
            if isinstance(self, MdaoDataGraph):
                colors_based_on = 'architecture_roles'
            elif isinstance(self, FundamentalProblemGraph):
                colors_based_on = 'problem_roles'
            elif isinstance(self, RepositoryConnectivityGraph):
                colors_based_on = 'nothing'

        # Check if MPG is applicable
        if mpg is not None:
            if isinstance(self, RepositoryConnectivityGraph):
                logger.warning('The RCG is given with an MPG. The MPG is ignored for the creation of the DSM.')
                mpg = None
            if isinstance(self, FundamentalProblemGraph):
                logger.warning('The FPG is given with an MPG. The MPG is ignored for the creation of the DSM.')
                mpg = None

        # Get file path
        if os.path.splitext(file_name)[1].lower()[1:] == 'pdf':
            file_name = os.path.splitext(file_name)[0]
        if destination_folder is None:
            file_path = file_name
        else:
            file_path = os.path.join(destination_folder, file_name)

        # Clean copies
        logger.info('Creating the (X)DSM file ' + file_path + '.pdf...')
        graph = self.deepcopy()
        if mpg is not None:
            graph_mpg = mpg.deepcopy()

        # Check
        test = (graph.find_all_nodes(category='variable', subcategory='all problematic variables') or
                graph.find_all_nodes(category='function', subcategory='independent'))
        if test:
            logger.info('There are still problematic variables in the graph used to create the (X)DSM.')

        # Initialize (X)DSM
        dsm = XDSM()

        if mpg is None:
            # Determine the nodes on the diagonal
            assert graph.number_of_nodes() == len(graph.find_all_nodes(category='variable')) +\
                                              len(graph.find_all_nodes(category='variable group')) +\
                                              len(graph.find_all_nodes(category='function')),\
                                              'The graph has nodes in invalid categories.'
            # Check function order
            function_nodes = graph.find_all_nodes(category='function')
            if not function_order:
                if 'problem_formulation' not in graph.graph:
                    diagonal_nodes = function_nodes
                else:
                    if 'function_order' in graph.graph['problem_formulation']:
                        diagonal_nodes = graph.graph['problem_formulation']['function_order']
                        assert not set(diagonal_nodes).symmetric_difference(set(function_nodes)), \
                            'Function order of graph does not contain all function nodes, give function_order manually.'
                    else:
                        diagonal_nodes = function_nodes
            else:
                assert type(function_order) is list, 'Analysis order input has to be a list.'
                # Make sure the function nodes and the analysis order match exactly
                assert not set(function_order).difference(set(function_nodes)), \
                    'Analysis order has nodes which are not as function nodes in the graph, namely: ' + \
                    str(set(function_order).difference(set(function_nodes)))
                assert not set(function_nodes).difference(set(function_order)), \
                    'Function node(s) missing in the analysis order, namely: ' + \
                    str(set(function_nodes).difference(set(function_order)))
                diagonal_nodes = function_order

            # If parameters have to be shown, then add the 'EMPTY' pseudo node and connect it correctly
            pseudo_node = 'EMPTY'
            if include_system_vars:
                # Add pseudo-Coordinator to the diagonal_nodes
                diagonal_nodes = [pseudo_node] + diagonal_nodes
                # Now add the pseudo-Coordinator to the graph and connect the input and output parameters
                graph.add_fnode(pseudo_node, label='',
                                problem_role=graph.FUNCTION_ROLES[3],
                                architecture_role=graph.ARCHITECTURE_ROLES_FUNS[0])
                graph_inputs = graph.find_all_nodes(subcategory='all inputs')
                graph_outputs = graph.find_all_nodes(subcategory='all outputs')
                for inp in graph_inputs:
                    graph.add_edge(pseudo_node, inp)
                for output in graph_outputs:
                    graph.add_edge(output, pseudo_node)

            # Add diagonal components in order from up to down
            # Add analysis blocks
            for idx, item in enumerate(diagonal_nodes):
                node = diagonal_nodes[idx]
                node_style = graph._get_node_style(node, colors_based_on)
                node_text = graph.nodes[node].get('label', str(node))
                if '^{' in node_text:
                    node_text = node_text.replace('^{', '$^{').replace('}', '}$')
                assert node_text if node != pseudo_node else True, 'Node label is empty for node: %s' % node
                dsm.addComp(node, node_style, node_text)

        else:
            # Add diagonal components in order from up to down
            # Add analysis blocks
            for idx in range(0, graph_mpg.number_of_nodes()):
                node_list = graph_mpg.find_all_nodes(attr_cond=['diagonal_position', '==', idx])
                assert len(node_list) == 1, 'Somehow, a unique diagonal position {} could not be found in the MDG.'\
                    .format(idx)
                node = node_list[0]
                node_style = self._get_node_style(node, colors_based_on)
                # Determine node text
                node_text = graph_mpg.get_node_text(node)
                if '^{' in node_text:
                    node_text = node_text.replace('^{', '$^{').replace('}', '}$')
                dsm.addComp(node, node_style, node_text)

            # Add process chain lines to the XDSM
            for edge in graph_mpg.edges():
                # Add line between two blocks that are on the diagonal
                dsm.addChain([edge[0], edge[1]])

        # Get dimension of the (X)DSM
        if mpg is None:
            dimension = len(diagonal_nodes)
        else:
            dimension = graph_mpg.number_of_nodes()

        # Determine connected diagonal blocks and add data dependency
        for idx1 in range(0, dimension - 1):
            for idx2 in range(idx1 + 1, dimension):
                if mpg is None:
                    # Find first diagonal node
                    node1 = diagonal_nodes[idx1]
                    # Find second diagonal node
                    node2 = diagonal_nodes[idx2]
                else:
                    # Find first diagonal node
                    node1 = graph_mpg.find_all_nodes(attr_cond=['diagonal_position', '==', idx1])[0]
                    if idx1 == 0:
                        pseudo_node = node1
                    # Find second diagonal node
                    node2 = graph_mpg.find_all_nodes(attr_cond=['diagonal_position', '==', idx2])[0]

                node1_out = map((lambda x: x[1]), graph.out_edges(node1))
                node1_in = map((lambda x: x[0]), graph.in_edges(node1))
                node2_out = map((lambda x: x[1]), graph.out_edges(node2))
                node2_in = map((lambda x: x[0]), graph.in_edges(node2))

                # Determine intersection between outputs and inputs
                node_set_upp = set(node1_out).intersection(set(node2_in))
                node_set_low = set(node1_in).intersection(set(node2_out))

                # Determine data type for visualization
                if node1 == pseudo_node or node1 == self.COORDINATOR_STRING:
                    data_type = 'DataIO'
                else:
                    data_type = 'DataInter'

                # Determine string inside off-diagonal box
                if summarize_vars:
                    pl_str = 's' if len(node_set_upp) > 1 else ''
                    if node_set_upp:
                        if node1 == pseudo_node or node1 == self.COORDINATOR_STRING:
                            if abbreviate_keywords:
                                str_upp = str(len(node_set_upp)) + ' inp.'
                            else:
                                str_upp = str(len(node_set_upp)) + ' input' + pl_str
                        else:
                            if abbreviate_keywords:
                                str_upp = str(len(node_set_upp)) + ' conn.'
                            else:
                                str_upp = str(len(node_set_upp)) + ' connection' + pl_str
                    if node_set_low:
                        if node1 == pseudo_node or node1 == self.COORDINATOR_STRING:
                            if abbreviate_keywords:
                                str_low = str(len(node_set_low)) + ' outp.'
                            else:
                                str_low = str(len(node_set_low)) + ' output' + pl_str
                        else:
                            if abbreviate_keywords:
                                str_low = str(len(node_set_low)) + ' con.'
                            else:
                                str_low = str(len(node_set_low)) + ' connection' + pl_str
                else:
                    if node_set_upp:
                        str_upp = r'\\[1pt] '.join(
                            map(str, map((lambda x: '$' + graph.nodes[x]['label'] + '$'), node_set_upp)))
                    if node_set_low:
                        str_low = r'\\[1pt] '.join(
                            map(str, map((lambda x: '$' + graph.nodes[x]['label'] + '$'), node_set_low)))

                # Additional strings for XDSMs
                str_num_up = ''
                str_num_low = ''
                if node_set_upp and mpg is not None:
                    if 'process_step' in graph_mpg.nodes[node2]:
                        str_num_up = str(graph_mpg.nodes[node2]['process_step']) + ': '
                    else:
                        str_num_up = ''
                if node_set_low and mpg is not None:
                    # Check existence of process edge and add edge number if it exists
                    if 'converger_step' in graph_mpg.nodes[node1]:
                        str_num_low = (str(graph_mpg.nodes[node1]['converger_step']) + ': ')
                    elif 'process_step' in graph_mpg.nodes[node1]:
                        str_num_low = (str(graph_mpg.nodes[node1]['process_step']) + ': ')
                    else:
                        str_num_low = ''

                # Upper triangle of (X)DSM
                if node_set_upp:
                    dsm.addDep(node2, node1, data_type, (str_num_up + str_upp))

                # Lower triangle of (X)DSM
                if node_set_low:
                    dsm.addDep(node1, node2, data_type, (str_num_low + str_low))

        # Compile PDF and delete temporary files
        dsm.create(file_path, keep_tex_file, compile_pdf, pdflatex_path)

        logger.info('Successfully created the (X)DSM file ' + file_path + '.pdf.')

        # Opening the file
        if open_pdf:
            logger.info('Opening (X)DSM PDF file ' + file_path + '.pdf...')
            open_file(file_path+'.pdf')
            logger.info('Successfully opened the (X)DSM PDF file ' + file_path + '.pdf.')

        # Return
        return

    def _get_node_style(self, node, colors_based_on):
        """Method to retrieve the right node style of a given node.

        :param node: Node from graph
        :type node: str
        :param colors_based_on: setting to assess on which node property the color should be based
        :type colors_based_on: str
        :return: node_style
        :rtype: str
        """
        from kadmos.graph.graph_data import FundamentalProblemGraph, MdaoDataGraph

        if colors_based_on == 'partitions':
            if node in [node1 for nodes in self.graph['problem_formulation']['coupled_functions_groups'] for node1 in
                        nodes]:
                partitions = self.graph['problem_formulation']['coupled_functions_groups']
                part_id = [i for i in range(len(partitions)) if node in partitions[i]]
                node_style = 'EvenPartitions' if part_id[0] % 2 == 0 else 'OddPartitions'
            else:
                if isinstance(self, FundamentalProblemGraph) and 'problem_role' in self.nodes[node]:
                    role_index = self.FUNCTION_ROLES.index(self.nodes[node]['problem_role'])
                    node_style = self.FUNCTION_ROLES_NODESTYLES[role_index]
                elif isinstance(self, MdaoDataGraph) and 'architecture_role' in self.nodes[node]:
                    role_index = self.ARCHITECTURE_ROLES_FUNS.index(self.nodes[node]['architecture_role'])
                    node_style = self.ARCHITECTURE_ROLES_NODESTYLES[role_index]
                else:
                    if isinstance(self, (FundamentalProblemGraph, MdaoDataGraph)):
                        logger.warning('An invalid graph has been provided, expected role missing for: %s.' % node)
                    node_style = 'RcgAnalysis'
        elif colors_based_on == 'problem_roles':
            if 'problem_role' in self.nodes[node]:
                role_index = self.FUNCTION_ROLES.index(self.nodes[node]['problem_role'])
                node_style = self.FUNCTION_ROLES_NODESTYLES[role_index]
            else:
                logger.warning('An incomplete graph has been provided: problem_role missing for: %s.' % node)
                node_style = 'RcgAnalysis'
        elif colors_based_on == 'architecture_roles':
            if 'architecture_role' in self.nodes[node]:
                role_index = self.ARCHITECTURE_ROLES_FUNS.index(self.nodes[node]['architecture_role'])
                node_style = self.ARCHITECTURE_ROLES_NODESTYLES[role_index]
            else:
                logger.warning('An incomplete graph has been provided: architecture_role missing for: %s.' % node)
                node_style = 'RcgAnalysis'
        else:
            node_style = 'RcgAnalysis'
        return node_style

    def _create_cmdows_header(self, description, modification, creator, version, cmdows_version,
                              timestamp=datetime.now()):

        # Create header
        cmdows_header = Element('header')
        cmdows_header.add('creator', creator if creator else "unknown")
        cmdows_header.add('description', description if description else "not provided")
        cmdows_header.add('timestamp', timestamp.isoformat())
        cmdows_header.add('fileVersion', version)
        cmdows_header.add('cmdowsVersion', cmdows_version)

        # Create header/update
        cmdows_updates = cmdows_header.add('updates')

        # Create header/updates/update
        cmdows_update = cmdows_updates.add('update')
        cmdows_update.add('modification', modification)
        cmdows_update.add('creator', creator if creator else "unknown")
        cmdows_update.add('timestamp', timestamp.isoformat())
        cmdows_update.add('fileVersion', version)
        cmdows_update.add('cmdowsVersion', cmdows_version)

        # Create header/organization
        cmdows_header.add('organization', self.graph.get('organization'))

        return cmdows_header

    def _create_cmdows_executables(self):

        # Create executableBlocks
        cmdows_executable_blocks = Element('executableBlocks')
        graph_executable_blocks = self.find_all_nodes(category='function',
                                                      attr_exclude=['architecture_role',
                                                                    self.CMDOWS_ARCHITECTURE_ROLE_SPLITTER])
        graph_mathematical_functions = self._get_equation_nodes()
        graph_mathematical_functions = set(graph_executable_blocks).intersection(graph_mathematical_functions)
        graph_design_competences = set(graph_executable_blocks).difference(graph_mathematical_functions)

        # Create executableBlocks/designCompetences
        cmdows_executable_blocks.append(self._create_cmdows_competences(graph_design_competences))

        # Create executableBlocks/mathematicalFunctions
        cmdows_executable_blocks.append(self._create_cmdows_equations(graph_mathematical_functions))

        return cmdows_executable_blocks

    def _create_cmdows_competences(self, graph_design_competences):

        # Create designCompetences
        cmdows_design_competences = Element('designCompetences')
        for graph_design_competence in graph_design_competences:

            # Create designCompetences/designCompetence
            graph_design_competence_data = self.nodes[graph_design_competence]
            cmdows_design_competence = cmdows_design_competences.add('designCompetence')
            cmdows_design_competence.set('uID', graph_design_competence)
            cmdows_design_competence.add('label', graph_design_competence_data.get('label'))
            if graph_design_competence_data.get('instance', 0) is None:
                instance = 0
            else:
                instance = int(graph_design_competence_data.get('instance', 0))
            cmdows_design_competence.add('instanceID', instance+1)

            # Create designCompetences/designCompetence/inputs with children
            graph_inputs = self.in_edges(graph_design_competence, data=True)
            cmdows_inputs = cmdows_design_competence.add('inputs')
            for graph_input in graph_inputs:
                cmdows_input = cmdows_inputs.add('input')
                cmdows_input.add('parameterUID', graph_input[0])
                # TODO: Update this to also account for global/local valid_ranges
                cmdows_input.add('valid_ranges', graph_input[2].get('valid_ranges'),
                                 camel_case_conversion=True)

            # Create designCompetences/designCompetence/outputs with children
            graph_outputs = self.out_edges(graph_design_competence)
            cmdows_outputs = cmdows_design_competence.add('outputs')
            for graph_output in graph_outputs:
                cmdows_output = cmdows_outputs.add('output')
                cmdows_output.add('parameterUID', graph_output[1])

            if instance > 1:
                cmdows_design_competence.add('relatedInstanceUID',
                                             self.get_first_node_instance(cmdows_design_competence.attrib['uID']))
            else:
                cmdows_design_competence.add('ID', graph_design_competence_data.get('name'), only_add_if_valued=True)
                cmdows_design_competence.add('modeID', graph_design_competence_data.get('mode', 'main'),
                                             only_add_if_valued=True)
                cmdows_design_competence.add('version', graph_design_competence_data.get('version', '1.0'),
                                             only_add_if_valued=True)

                # Create designCompetences/designCompetence/metadata with children
                # TODO: Preferably make sure that contacts are always saved to the database?
                cmdows_metadata = cmdows_design_competence.add('metadata')
                cmdows_metadata.add('general_info', graph_design_competence_data.get('general_info'),
                                    camel_case_conversion=True)
                cmdows_metadata.add('performance_info', graph_design_competence_data.get('performance_info'),
                                    camel_case_conversion=True)
                cmdows_metadata.add('execution_info', graph_design_competence_data.get('execution_info'),
                                    camel_case_conversion=True)

                # Create designCompetences/designCompetence/projectSpecific
                cmdows_design_competence.add('projectSpecific', graph_design_competence_data.get('projectSpecific'))

        return cmdows_design_competences

    def _create_cmdows_parameters(self):

        # Create parameters
        graph_parameters = self.find_all_vnodes(attr_exclude=['architecture_role',
                                                              self.ARCHITECTURE_ROLES_VARS])
        cmdows_parameters = Element('parameters')
        for graph_parameter in graph_parameters:

            # Create parameters/parameter
            cmdows_parameter = cmdows_parameters.add('parameter')
            cmdows_parameter.set('uID', graph_parameter)
            cmdows_parameter.add('label', self.nodes[graph_parameter].get('label'))
            if self.nodes[graph_parameter].get('instance', 0) is None:
                instance = 0
            else:
                instance = int(self.nodes[graph_parameter].get('instance', 0))
            cmdows_parameter.add('instanceID', instance+1)

            if instance > 0:
                cmdows_parameter.add('relatedInstanceUID', self.get_first_node_instance(graph_parameter))
            else:
                cmdows_parameter.add('description', self.nodes[graph_parameter].get('description'),
                                     only_add_if_valued=True)
                cmdows_parameter.add('note', self.nodes[graph_parameter].get('note'), only_add_if_valued=True)
                cmdows_parameter.add('defaultValue', self.nodes[graph_parameter].get('defaultValue'), only_add_if_valued=True)
                cmdows_parameter.add('unit', self.nodes[graph_parameter].get('unit'), only_add_if_valued=True)
                cmdows_parameter.add('dataType', self.nodes[graph_parameter].get('data_type'), only_add_if_valued=True)

        # Below this line there is a workaround for missing parameters in CMDOWS files
        # TODO: This should be handled differently in future releases
        graph_params_arch = self.find_all_vnodes(attr_include=['architecture_role',
                                                               self.ARCHITECTURE_ROLES_VARS])
        already_added = set()
        for graph_param_arch in graph_params_arch:
            graph_parameter = self.nodes[graph_param_arch].get('related_to_schema_node', None)
            if graph_parameter:
                if not self.has_node(graph_parameter) and graph_parameter not in already_added:
                    cmdows_parameter = cmdows_parameters.add('parameter')
                    cmdows_parameter.set('uID', graph_parameter)
                    cmdows_parameter.add('label', graph_parameter.split('/')[-1])
                    cmdows_parameter.add('instanceID', 1)
                    cmdows_parameter.add('description', 'Dummy parameter to avoid missing UID issue.')
                    already_added.update([graph_parameter])

        return cmdows_parameters

    def _create_cmdows_workflow(self, mpg=None):

        # Create workflow
        cmdows_workflow = Element('workflow')

        # Create workflow/problemDefinitionUID
        if hasattr(self, '_create_cmdows_workflow_problem_def'):
            # noinspection PyProtectedMember
            cmdows_workflow.append(self._create_cmdows_workflow_problem_def())

        # Create workflow/dataGraph
        cmdows_data_graph = cmdows_workflow.add('dataGraph')
        cmdows_data_graph.add('name', self.graph.get('name'))

        # Create workflow/dataGraph/edges
        cmdows_edges = cmdows_data_graph.add('edges')
        for u, v, w in self.edges(data=True):
            # Create workflow/dataGraph/edges/edge
            cmdows_edge = cmdows_edges.add('edge')
            from_name = 'fromExecutableBlockUID' if self.nodes[u].get('category') == 'function' else 'fromParameterUID'
            to_name = 'toExecutableBlockUID' if self.nodes[v].get('category') == 'function' else 'toParameterUID'
            cmdows_edge.add(from_name, u)
            cmdows_edge.add(to_name, v)
        cmdows_data_graph.add('metadata')
        # TODO: Implement this (also in load function)

        # Create workflow/processGraph
        if mpg:
            # noinspection PyProtectedMember
            cmdows_workflow.append(mpg._create_cmdows_workflow_process_graph())

        return cmdows_workflow

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             LOAD METHODS                                                         #
    # ---------------------------------------------------------------------------------------------------------------- #

    def load_cmdows(self, cmdows, check_list, ignore_modes=False, keep_running=False):
        """Method to load the graph from a CMDOWS file

        :param cmdows: CMDOWS file path
        :type cmdows: str
        :param check_list: checks to be performed. See below.
        :type check_list: list
        :param ignore_modes: for determining if modes are taken into account
        :type ignore_modes: bool
        :param keep_running: for determining if errors should be raised
        :type keep_running: bool
        :return: mpg
        :rtype: MdaoProcessGraph

        .. note:: check_list options:

            * 'consistent_root': check if all in-/output files have the same root element
            * 'invalid_leaf_elements': check for leaf elements that still have child elements in other in-/output files
            * 'schemas': check if the in-/output files are consistent with the schema.

        To perform all of the checks without stopping if an error is found by the checks:

        >>> check_list = ['consistent_root', 'invalid_leaf_elements', 'schemas']
        >>> graph.load_cmdows(cmdows, check_list, keep_running=True)
        """

        # Create organization node
        self._load_cmdows_header(cmdows)

        # Create variable nodes
        self._load_cmdows_parameters(cmdows)

        # Create function nodes
        self._load_cmdows_executables(cmdows, check_list, ignore_modes=ignore_modes, keep_running=keep_running)

        # Create architecture element nodes
        if hasattr(self, '_load_cmdows_architecture_elements'):
            self._load_cmdows_architecture_elements(cmdows)

        # Create problem formulation dict (placed after creation of architecture elements for a reason!)
        if hasattr(self, '_load_cmdows_problem_def'):
            self._load_cmdows_problem_def(cmdows)

        # Create worklow nodes and edges
        mpg = self._load_cmdows_workflow(cmdows)

        return mpg

    def _load_cmdows_header(self, cmdows):

        org_dict = cmdows.finddict('header/organization')

        if org_dict is not None:
            # Fix case of single contact that is not put in a list
            if isinstance(org_dict['contacts'], OrderedDict):
                org_dict['contacts'] = [org_dict['contacts']]
            self.graph['organization'] = org_dict
        else:
            self.graph['organization'] = dict()

        return

    def _load_cmdows_executables(self, cmdows, check_list, ignore_modes=False, keep_running=False):

        self._load_cmdows_competences(cmdows, check_list, ignore_modes=ignore_modes, keep_running=keep_running)
        self._load_cmdows_equations(cmdows)

    def _load_cmdows_competences(self, cmdows, check_list=None, ignore_modes=False, keep_running=False):

        inputs_list = []
        outputs_list = []

        for function in cmdows.findall('executableBlocks/designCompetences/designCompetence'):
            if function.findtext('relatedInstanceUID'):
                related_function = cmdows.xpath(get_uid_search_xpath(function.findtext('relatedInstanceUID')))[0]
            else:
                related_function = function

            self.add_node(function.get('uID'),
                          category='function',
                          name=related_function.findtext('ID'),
                          mode=related_function.findtext('modeID'),
                          instance=int(function.findtext('instanceID'))-1,
                          version=related_function.findtext('version'),
                          label=function.findtext('label'),
                          general_info=related_function.finddict('metadata/generalInfo', ordered=False,
                                                                 camel_case_conversion=True),
                          performance_info=related_function.finddict('metadata/performanceInfo', ordered=False,
                                                                     camel_case_conversion=True),
                          execution_info=related_function.finddict('metadata/executionInfo', ordered=False,
                                                                   camel_case_conversion=True),
                          projectSpecific=related_function.finddict('projectSpecific'))

            for inp in function.findall('inputs/input'):
                self.add_edge(inp.findtext('parameterUID').replace("'", '"'), function.get('uID'),
                              valid_ranges=inp.finddict('validRanges', ordered=False, camel_case_conversion=True))

            if not function.findall('inputs/input'):
                # Determine assumed input file location (same folder as CMDOWS file)
                input_file_path = os.path.join(os.path.split(os.path.normpath(function.base))[0],
                                               function.findtext('ID') + '-input.xml').replace('file:'+os.path.sep, '')

                if os.path.isfile(input_file_path):
                    inputs_list.append([input_file_path, function])
                else:
                    logger.warning('Could not find inputs for function: ' + function.get('uID'))
                # #  #

            for output in function.findall('outputs/output'):
                self.add_edge(function.get('uID'), output.findtext('parameterUID').replace("'", '"'))

            if not function.findall('outputs/output'):
                # Determine assumed output file location (same folder as CMDOWS file)
                output_file_path = os.path.join(os.path.split(os.path.normpath(function.base))[0],
                                                function.findtext('ID') + '-output.xml').replace('file:'+os.path.sep,
                                                                                                 '')
                if os.path.isfile(output_file_path):
                    outputs_list.append([output_file_path, function])
                else:
                    logger.warning('Could not find outputs for function: ' + function.get('uID'))

        # Add inputs and outputs based on XML
        io_list = inputs_list+outputs_list

        _perform_check_list(io_list, check_list, keep_running=keep_running)

        for input_el in inputs_list:
            inputs = _read_io_xml_file(input_el[0], input_el[1].findtext('modeID'), ignore_modes=ignore_modes)
            for input in inputs['leafNodes']:
                if not self.has_node(input['xpath']):
                    self.add_node(input['xpath'],
                                  category='variable',
                                  shape='o',
                                  label=input['xpath'].split('/')[-1],
                                  instance=0)  # TODO: Extend this to pick up XML attributes for description, note, unit, data_type
                self.add_edge(input['xpath'], input_el[1].get('uID'))

        for output_el in outputs_list:
            outputs = _read_io_xml_file(output_el[0], output_el[1].findtext('modeID'), ignore_modes=ignore_modes)
            for output in outputs['leafNodes']:
                # Add new parameter if it does not exist yet
                if not self.has_node(output['xpath']):
                    self.add_node(output['xpath'],
                                  category='variable',
                                  shape='o',
                                  label=output['xpath'].split('/')[-1],
                                  instance=0)  # TODO: Extend this to pick up XML attributes for description, note, unit, data_type
                self.add_edge(output_el[1].get('uID'), output['xpath'])

        return

    def _load_cmdows_parameters(self, cmdows):

        for variable in cmdows.findall('parameters/parameter'):
            uid = variable.get('uID').replace("'", '"')

            # TODO: Adjust this to improve performance, xpath search takes too long now...
            # TODO: Handle case of having the relatedInstanceUID missing
            # if variable.findtext('relatedInstanceUID'):
            #     print variable
            #     related_variable_els = cmdows.xpath(get_uid_search_xpath(variable.findtext('relatedInstanceUID')))
            #     # If loop to catch issue when the related UID does not exist
            #     if related_variable_els:
            #         related_variable = related_variable_els[0]
            #     else:
            #         related_variable = variable
            # else:
            related_variable = variable

            # TODO: Workaround for dummy parameters
            skip_param = False
            if related_variable.findtext('description') == 'Dummy parameter to avoid missing UID issue.':
                skip_param = True

            # TODO: Workaround for reading old CMDOWS files
            instance_id = variable.findtext('instanceID')
            if instance_id is None:
                instance_id = 1
            if not skip_param:
                self.add_node(uid,
                              category='variable',
                              label=variable.findtext('label'),
                              instance=int(instance_id)-1)
                if related_variable.findtext('description') is not None:
                    self.nodes[uid]['description'] = related_variable.findtext('description')
                if related_variable.findtext('note') is not None:
                    self.nodes[uid]['note'] = related_variable.findtext('note')
                if related_variable.findtext('unit') is not None:
                    self.nodes[uid]['unit'] = related_variable.findtext('unit')
                if related_variable.findtext('dataType') is not None:
                    self.nodes[uid]['data_type'] = related_variable.findtext('dataType')
                if related_variable.findtext('defaultValue') is not None:
                    self.nodes[uid]['default_value'] = related_variable.findtext('defaultValue')

        return

    def _load_cmdows_workflow(self, cmdows):

        cmdows_data_graph = cmdows.find('workflow/dataGraph')
        if cmdows_data_graph is not None:
            self.graph['name'] = cmdows_data_graph.findtext('name')
            cmdows_edges = cmdows_data_graph.find('edges')
            if cmdows_edges is not None:
                for edge in list(cmdows_edges):
                    from_id = edge.findtext('fromExecutableBlockUID',
                                            default=edge.findtext('fromParameterUID')).replace("'", '"')
                    to_id = edge.findtext('toExecutableBlockUID',
                                          default=edge.findtext('toParameterUID')).replace("'", '"')
                    self.assert_node_exists(from_id)
                    self.assert_node_exists(to_id)
                    self.add_edge(from_id, to_id)
        else:
            logger.warning('No dataGraph element found in the CMDOWS file. Ignoring missing information.')

        cmdows_process_graph = cmdows.find('workflow/processGraph')
        if cmdows_process_graph is not None:
            from kadmos.graph.graph_process import MdaoProcessGraph
            mpg = MdaoProcessGraph(name=cmdows_process_graph.findtext('name'))
            mpg._load_cmdows_workflow_process_graph(cmdows, self.node)
        else:
            mpg = None

        return mpg

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            EXPORT METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def save(self, file_name, file_type='kdms', graph_check_critical=True, destination_folder=None, mpg=None,
             description='', creator='', version='1.0', timestamp=datetime.now(), keep_empty_elements=False,
             pretty_print=False, convention=True, integrity=False):
        """Method to save the graph.

        :param file_name: name of the file to be saved
        :type file_name: str
        :param file_type: file_type
        :type file_type: str

        :param graph_check_critical: option for raising errors in case of an invalid graph
        :type graph_check_critical: bool
        :param destination_folder: destination folder for the file to be saved
        :type destination_folder: str
        :param mpg: optional MPG graph to be saved with MDG
        :type mpg: MdaoProcessGraph

        :param description: description of the file (only applicable for the cmdows file type)
        :type description: str
        :param creator: name of the creator of the file (only applicable for the cmdows file type)
        :type creator: str
        :param version: version of the file (only applicable for the cmdows file type)
        :type version: str, float, int
        :param timestamp: timestamp to be saved in the file (only applicable for the cmdows file type)
        :type timestamp: datetime
        :param keep_empty_elements: option for keeping empty XML elements (only applicable for the cmdows file type)
        :type keep_empty_elements: bool
        :param pretty_print: option for pretty XML printing (only applicable for the cmdows file type)
        :type pretty_print: bool
        :param convention: option for applying a UID convention (only applicable for the cmdows file type)
        :type convention: bool
        :param integrity: option for doing an integrity file check (only applicable for the cmdows file type)
        :type integrity: bool

        .. note:: Different output file types are implemented for saving graphs. They are listed below:

            * kdms: the most simple file type which makes use of pickling
            * cmdows: the most versatile file type especially suited for file exchange with other tools
            * graphml: another file type especially suited for file exchange with other tools based on graphs
        """

        # Check if the file type is valid
        file_type = file_type.lower()
        if file_type not in file_types:
            raise IOError('The specified file type ' + file_type + ' is not known. '
                          'Please use one of the following file types: ' + ', '.join(file_types))

        # Check if MPG is applicable
        if mpg is not None:
            from kadmos.graph.graph_data import RepositoryConnectivityGraph, FundamentalProblemGraph
            if isinstance(self, RepositoryConnectivityGraph):
                logger.warning('The RCG is given with an MPG. The MPG is ignored for saving.')
                mpg = None
            if isinstance(self, FundamentalProblemGraph):
                logger.warning('The FPG is given with an MPG. The MPG is ignored for saving.')
                mpg = None

        # Check if the graph is valid
        check_s = self.check()
        # If MPG is provided check also this one
        if mpg is not None:
            check_s = check_s and mpg.check()
        if check_s:
            logger.info('The graph to be saved is a valid KADMOS graph.')
        else:
            validity_message = 'The graph to be saved is not a valid KADMOS graph. ' \
                               'The validity of the output file is not guaranteed.'
            if graph_check_critical:
                raise IOError(validity_message)
            else:
                logger.warning(validity_message)

        # Get file path
        file_extension = file_extensions[file_types.index(file_type)]
        if os.path.splitext(file_name)[1].lower()[1:] != file_extension:
            file_name += '.' + file_extension
        if destination_folder is None:
            file_path = file_name
        else:
            file_path = os.path.join(destination_folder, file_name)
        if mpg is not None:
            split_file_path = os.path.splitext(file_path)
            mpg_file_path = split_file_path[0] + '_mpg' + split_file_path[1]

        # Check if path exist and if not create the path
        if not os.path.exists(os.path.dirname(file_path)) and os.path.dirname(file_path) != '':
            os.makedirs(os.path.dirname(file_path))

        # Save file
        logger.info('Saving the ' + file_type.upper() + ' file ' + file_path + '...')
        if file_type in ['cmdows', 'zipped-cmdows']:
            if file_type == 'zipped-cmdows':
                temp_cmdows_file = os.path.splitext(file_path)[0] + '_' + str(uuid.uuid4()) + '.xml'
            self._save_cmdows(file_path if file_type == 'cmdows' else temp_cmdows_file,
                              description=description, creator=creator, version=version,
                              timestamp=timestamp, mpg=mpg, keep_empty_elements=keep_empty_elements,
                              pretty_print=pretty_print, convention=convention, check=True)
            if integrity:
                self.check_cmdows_integrity(convention=convention, mpg=mpg)
            if file_type == 'zipped-cmdows':
                zip_file(temp_cmdows_file,
                         destination_archive=file_path,
                         name_of_zipped_file=os.path.splitext(os.path.basename(file_path))[0] + '.xml')
                os.remove(temp_cmdows_file)
        elif file_type == 'kdms':
            self._save_kdms(file_path)
            if mpg is not None:
                # noinspection PyUnboundLocalVariable
                self._save_kdms(mpg_file_path, mpg)
        elif file_type == 'graphml':
            self._save_graphml(file_path)
            if mpg is not None:
                # noinspection PyUnboundLocalVariable
                self._save_graphml(mpg_file_path, mpg)

        # Return
        logger.info('Successfully saved the ' + file_type.upper() + ' file ' + file_path + '.')
        return

    def _save_kdms(self, file_path, graph=None):

        # Check
        if graph is None:
            graph = self

        # Write the pickled file
        nx.write_gpickle(graph, file_path)

        # Return
        return

    def _save_cmdows(self, file_path,
                     description, creator, version, timestamp=datetime.now(),
                     mpg=None,
                     keep_empty_elements=False,
                     pretty_print=False,
                     convention=True,
                     check=True):

        # Make a clean copy of the graph (to avoid shallow-copy problems)
        graph = self.deepcopy()
        if type(self).__name__ == 'RepositoryConnectivityGraph':
            modification = 'KADMOS export of a repository connectivity graph (RCG).'
        elif type(self).__name__ == 'FundamentalProblemGraph':
            modification = 'KADMOS export of a fundamental problem graph (FPG).'
        elif type(self).__name__ == 'MdaoDataGraph':
            modification = 'KADMOS export of a mdao data graph (MDG).'
            if type(mpg).__name__ != 'MdaoProcessGraph':
                raise IOError('An MPG of class MdaoProcessGraph should also be provided.')
        else:
            raise IOError('The input graph for a CMDOWS file should be of RCG, FPG or MDG class.')

        # Relabel nodes
        if convention:
            graph = copy.deepcopy(graph)
            mapping = graph.relabel_function_nodes()
            if mpg is not None:
                mpg = copy.deepcopy(mpg)
                mpg.relabel_function_nodes(mapping)
                mpg.graph['process_hierarchy'] = mpg.get_process_hierarchy()  # Needs to be updated to meet convention

        # Set basic variables and create CMDOWS element
        cmdows_version = str(graph.CMDOWS_VERSION)
        cmdows_namespace = '{%s}noNamespaceSchemaLocation' % 'http://www.w3.org/2001/XMLSchema-instance'
        cmdows_schema = 'https://bitbucket.org/imcovangent/cmdows/raw/master/schema/' + cmdows_version + '/cmdows.xsd'
        cmdows = Element('cmdows', attrib={cmdows_namespace: cmdows_schema})

        # Create header
        cmdows.append(graph._create_cmdows_header(description=description, modification=modification, creator=creator,
                                                  version=version, cmdows_version=cmdows_version, timestamp=timestamp))

        # Create executableBlocks
        cmdows.append(graph._create_cmdows_executables())

        # Create parameters
        cmdows.append(graph._create_cmdows_parameters())

        # Create problemDefinition
        if hasattr(graph, '_create_cmdows_problem_def'):
            # noinspection PyProtectedMember
            cmdows.append(graph._create_cmdows_problem_def())

        # Create workflow
        cmdows.append(graph._create_cmdows_workflow(mpg))

        # Create architectureElements
        if hasattr(graph, '_create_cmdows_architecture_elements'):
            # noinspection PyProtectedMember
            cmdows.append(graph._create_cmdows_architecture_elements())

        # Remove empty elements
        if not keep_empty_elements:
            context = etree.iterwalk(cmdows)
            for action, elem in context:
                parent = elem.getparent()
                if recursively_empty(elem):
                    parent.remove(elem)

        # Do some final simplifications and checks
        # Afterwards write the CMDOWS file
        cmdows = CMDOWS(element=cmdows)
        cmdows.simplify()
        if check:
            cmdows.check()
        cmdows.save(file_path, pretty_print=pretty_print)

        # Return
        return

    def _save_graphml(self, file_path, graph=None):

        # Set keys of dictionary entries that can be removed from the graph nodes data
        keys_to_be_removed = ['indegree', 'outdegree', 'mode', 'run_time', 'description', 'precision',
                              'standard_deviation', 'level', 'execution time']

        # Determine and assert class of the graph
        if graph is None:
            graph = self
        graph_class = str(type(graph))[8:-2].split('.')[-1]
        assert isinstance(graph, nx.DiGraph)
        g = KadmosGraph(graph)
        g.graph['kadmos_graph_type'] = graph_class

        # Transform and update graph data to make it meet graphml requirements
        transform_data_into_strings(g.graph)
        for node, data in g.nodes(data=True):
            transform_data_into_strings(data, keys_to_be_removed=keys_to_be_removed)
        for u, v, data in g.edges(data=True):
            transform_data_into_strings(data)

        # Write the graphml file
        nx.write_graphml(g, file_path)

        # Return
        return

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                              PRINTING METHODS                                                    #
    # ---------------------------------------------------------------------------------------------------------------- #

    def inspect(self):
        """Method to print an overview of the graph.

        :return: printed overview of the graph
        :rtype: str
        """

        print('\n- - - - - - - - - -')
        print(' GRAPH INSPECTION  ')
        print('- - - - - - - - - -\n')
        print('name: ' + str(self.graph['name']))
        print('number of nodes: ' + str(self.number_of_nodes()))
        print('number of functions: ' + str(len(self.find_all_nodes(category='function'))))
        print('number of variables: ' + str(len(self.find_all_nodes(category='variable'))))
        print('number of edges: ' + str(self.number_of_edges()))
        print('- - - - - - - - - -\n')

        return

    def inspect_node(self, node):
        """Method to print a node with details.

        :param node: node
        :type node: str
        :return: printed node details
        :rtype: str
        """

        pp = pprint.PrettyPrinter(indent=2)
        print('\n- - - - - - - - - - - - -')
        print(' NODE INSPECTION RESULTS ')
        print('\n- - - - - - - - - - - - -')
        print('node id:')
        print(node)
        print('\nnode indegree:')
        print(self.in_degree(node))
        print('\nnode sources:')
        pp.pprint(self.get_sources(node))
        print('\nnode outdegree:')
        print(self.out_degree(node))
        print('\nnode targets:')
        pp.pprint(self.get_targets(node))
        print('\nnode attributes:')
        pp.pprint(self.nodes[node])
        print('- - - - - - - - - - - - -\n')

    def inspect_nodes(self, list_of_nodes):
        """Method to inspect/print a list of nodes with details.

        :param list_of_nodes: node list
        :type list_of_nodes: list
        :return: printed details of nodes
        :rtype: str
        """

        assert isinstance(list_of_nodes, list)
        for node in list_of_nodes:
            assert self.has_node(node), 'Node %s does not exist in the graph.' % node
            self.inspect_node(node)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #

    def add_contact(self, name, email, uid, company=None, department=None, function=None, address=None,
                    telephone=None, country=None, roles=None):
        """Method to add a contact to the graph organization.

        :param name: name of the contact
        :type name: str
        :param email: email address of the contact
        :type email: str
        :param uid: uid of the contact
        :type uid: str
        :param company: company of which the contact is an employee, optional
        :type company: str
        :param department: department of company that the contact works at, optional
        :type department: str
        :param function: the function of the contact, optional
        :type function: str
        :param address: company address, optional
        :type address: str
        :param telephone: telephone number of the contact, optional
        :type telephone: int
        :param country: country of company, optional
        :type country: str
        :param roles: organizational role(s) of contact within the project, optional
        :type: str, list

        Optional organizational contact roles:

        * 'architect'
        * 'integrator'
        * 'collaborativeEngineer'
        * 'toolSpecialist'
        * 'customer'

        Adding a contact with one organizational role:

        >>> add_contact('Maaike de Wit', 'M.D.deWit@student.tudelft.nl', 'mddewit', company='TU Delft',
        >>>             roles='integrator')

        Adding a contact with two (or more) organizational roles:

        >>> roles = ['integrator', 'architect']
        >>> add_contact('Maaike de Wit', 'M.D.deWit@student.tudelft.nl', 'mddewit', company='TU Delft', roles=roles)

        .. note:: In case the contact uid already exists the old contact attributes are conserved and only new roles
            are added to the roles already present for that contact. To change old contact information, this has to be
            adjusted in the XML-file from which the old contact information is loaded.

        .. hint:: To add (more) roles to the existing contact, it is recommended to use the method: add_contact_roles()
        """

        already = False
        contacts = []
        organigram = {}
        contact = OrderedDict([('attrib', {'uID': uid}), ('name', name), ('email', email), ('company', company),
                               ('department', department), ('function', function), ('address', address),
                               ('telephone', telephone), ('country', country)])

        role_options = ['architect', 'integrator', 'collaborativeEngineer', 'toolSpecialist', 'customer']
        architects = []
        integrators = []
        collaborative_engineers = []
        tool_specialists = []
        customers = []

        dict = {'architect': architects, 'integrator': integrators,'collaborativeEngineer': collaborative_engineers,
                'toolSpecialist': tool_specialists,'customer': customers}

        if isinstance(roles, list):
            for role in roles:
                if role not in role_options:
                    logger.warning('Invalid role {} was provided for {}. Appropriate roles are: '
                                   '{}'.format(role, name, role_options))
                else:
                    dict[role].append({'contactUID': uid})
        elif isinstance(roles, string_types):
            role = roles
            if role not in role_options:
                logger.warning('Invalid role {} was provided for {}. Appropriate roles are: {}'.format(role, name,
                                                                                                       role_options))
            else:
                dict[role].append({'contactUID': uid})

        # Check for existing organigram
        for role in role_options:
            if self.graph_has_nested_attributes('organization', 'organigram', role+'s'):
                for contact_uid in self.graph['organization']['organigram'][role+'s']:
                    if contact_uid not in dict[role]:
                        dict[role].append(contact_uid)
                    else:
                        already = True
            if len(dict[role]) > 0:
                organigram[role+'s'] = dict[role]

        if self.graph_has_nested_attributes(['organization', 'contacts']):
            if isinstance(self.graph['organization']['contacts'], list):
                for old_contact in self.graph['organization']['contacts']:
                    contacts.append(old_contact)
                    if old_contact['attrib'] == contact['attrib']:
                        already = True
            else:
                contacts.append(self.graph['organization']['contacts'])
                if self.graph['organization']['contacts']['attrib'] == contact['attrib']:
                    already = True

            if not already:
                contacts.append(contact)
            else:
                logger.debug("{} is already defined in CMDOWS. Please use add_contact_roles() to add new roles to this"
                             " existing contact.".format(contact['attrib']))
            self.graph['organization']['contacts'] = contacts
            self.graph['organization']['organigram'] = organigram
        else:
            self.graph['organization'] = OrderedDict([('contacts', contact), ('organigram', organigram)])
        return

    def add_contact_roles(self, uid, roles):
        """Method to add roles to existing contacts

        :param uid: uid of the contact
        :type uid: str
        :param roles: organizational role(s) to be added to the existing contact
        :type roles: str, list

        Optional organizational contact roles:

        * 'architect'
        * 'integrator'
        * 'collaborativeEngineer'
        * 'toolSpecialist'
        * 'customer'

        Adding an organizational role to an existing contact:

        >>> graph.add_contact('mddewit', roles='integrator')

        Adding two (or more) organizational roles to an existing contact:

        >>> roles = ['integrator', 'architect']
        >>> graph.add_contact('mddewit', company='TU Delft', roles=roles)

        .. hint:: This method only works for existing contacts. To add a contact use the method: add_contact()
        """

        assert 'organization' in self.graph, 'There are no contacts present to add a role to.'
        assert any(uid in contact['attrib']['uID'] for contact in self.graph['organization']['contacts']),\
            '{} does not exist as a contact yet.'.format(uid)

        already = False
        duplicates = []
        organigram = {}
        role_options = ['architect', 'integrator', 'collaborativeEngineer', 'toolSpecialist', 'customer']
        architects = []
        integrators = []
        collaborative_engineers = []
        tool_specialists = []
        customers = []

        dict = {'architect': architects, 'integrator': integrators, 'collaborativeEngineer': collaborative_engineers,
                'toolSpecialist': tool_specialists, 'customer': customers}

        if isinstance(roles, list):
            for role in roles:
                if role not in role_options:
                    logger.warning('Invalid role {} was provided for {}. Approriate roles are: {}'.format(role, uid,
                                                                                                          role_options))
                else:
                    dict[role].append({'contactUID': uid})
        elif isinstance(roles, string_types):
            role = roles
            if role not in role_options:
                logger.warning('Invalid role {} was provided for {}. Appropriate roles are: {}'.format(role, uid,
                                                                                                      role_options))
            else:
                dict[role].append({'contactUID': uid})

        for role in role_options:
            if role + 's' in self.graph['organization']['organigram']:
                for contact_uid in self.graph['organization']['organigram'][role + 's']:
                    if contact_uid not in dict[role]:
                        dict[role].append(contact_uid)
                    else:
                        already = True
                        duplicates.append(role)
            if len(dict[role]) > 0:
                organigram[role + 's'] = dict[role]

        if already:
            logger.debug('{} was/were already defined as (a) role(s) for {} in CMDOWS.'.format(duplicates, uid))

        self.graph['organization']['organigram'] = organigram
        return

    def add_dc_general_info(self, dc_uid, description, status=None, creation_date=None, owner_uid=None,
                            creator_uid=None, operator_uid=None, model_definition=None):
        """Method to add general info to a design competence

        :param dc_uid: uid of the design competence
        :type dc_uid: str
        :param description: description of the design competence
        :type description: str
        :param status: status of the design competence, optional
        :type status: str
        :param creation_date: creation date of the design competence, optional
        :type creation_date: date
        :param owner_uid: uid of the owner of the design competence, optional
        :type owner_uid: str
        :param creator_uid: uid of the creator of the design competence, optional
        :type creator_uid: str
        :param operator_uid: uid of the operator of the design competence, optional
        :type operator_uid: str
        :param model_definition: model definition of the design competence, optional
        :type model_definition: str
        """

        self.nodes[dc_uid]['general_info'] = {'description': description}
        options = ['status', 'creation_date', 'owner', 'creator', 'operator', 'model_definition']
        uid_options = ['owner', 'creator', 'operator']
        dict = {'status':status, 'creation_date': creation_date, 'owner': owner_uid, 'creator': creator_uid,
                'operator': operator_uid, 'model_definition': model_definition}

        for option in options:
            if option in uid_options and dict[option]:
                self.nodes[dc_uid]['general_info'].update({option: {'contactUID': dict[option]}})
            elif dict[option]:
                self.nodes[dc_uid]['general_info'].update({option: dict[option]})
        return

    def add_dc_performance_info(self, dc_uid, precision=None, fidelity_level=None, run_time=None, verification=None):
        """Method to add performance information to a design competence

        :param dc_uid: uid of the design competence
        :type dc_uid: str
        :param precision: precision of the design competence, optional
        :type precision: float
        :param fidelity_level: the level of fidelity of the design competence, optional
        :type fidelity_level: int
        :param run_time: the run time of the design competence, optional
        :type run_time: float
        :param verification: verification method of the design competence, optional
        :type verification: dict

        At least one of the optional elements for the performance information has to be defined.

        Adding performance info with a verification:

        >>> verification = {'method': 'dummy_method', 'verifier': contact_uid, 'result': 'dummy_result',
        >>>                 'date': dateTime, 'version': dummy_version}
        >>> graph.add_dc_performance_info(dc_uid, verification=verification)
        """
        options = ['precision', 'fidelity_level', 'run_time', 'verification']
        dict = {'precision': precision, 'fidelity_level': fidelity_level, 'run_time': run_time,
                'verification': verification}
        if not precision and not fidelity_level and not run_time and not verification:
            logger.warning("At least one element of the performance info of {} must have a value".format(dc_uid))
        else:
            first = True
            for option in options:
                if dict[option]:
                    if first:
                        self.nodes[dc_uid].update({'performance_info': {option: dict[option]}})
                        first = False
                    else:
                        self.nodes[dc_uid]['performance_info'].update({option: dict[option]})
        return

    def add_dc_remote_component_info(self, dc_uid, single_or_multi_execution, job_name, remote_engineer,
                                     notification_message, data_exchange_dict=None):
        """Method to add execution information to a design competence

        :param dc_uid: uid of the design competence
        :type dc_uid: str
        :param single_or_multi_execution: execution type. Choose from 'single' or 'multiple'.
        :type single_or_multi_execution: str
        :param job_name: job name of the design competence
        :type job_name: str
        :param remote_engineer: contact uid of remote engineering of the design competence
        :type remote_engineer: str
        :param notification_message: message to notify remote_engineer
        :type notification_message: str
        :param data_exchange_dict: data exchange settings of the design competence
        :type data_exchange_dict: str

        Example use:

        >>> single_or_multi = "single"
        >>> job_name = 'job_{}'.format(fpg.nodes[node]['label'].replace(' ', ''))
        >>> notification_message = 'Hi, could you please run this tool {} for me for my {} AGILE workflow '
        >>>                        'execution. Thanks.'.format(fpg.nodes[node]['label'].replace(' ', ''), architecture)
        >>> fpg.add_dc_remote_component_info(node, single_or_multi, job_name, 'ivangent', notification_message,
        >>>                                  data_exchange_dict={'urlsite': 'some_url',
        >>>                                                      'folder': 'some_folder'})
        """
        self.nodes[dc_uid].update({'execution_info':
                                      {'remote_component_info':
                                           {'job_settings': {'single_or_multi_execution': single_or_multi_execution,
                                                              'remote_engineer': {'contact_u_i_d': remote_engineer},
                                                              'job_name': job_name,
                                                              'notification_message': notification_message}}}})
        if data_exchange_dict:
            self.nodes[dc_uid]['execution_info']['remote_component_info'].update({'data_exchange_settings':
                                                                                      data_exchange_dict})
        return

    def add_dc_licensing(self, dc_uid, license_type=None, license_specification=None, license_info=None):
        """Method to add licensing information to a design competence

        :param dc_uid: uid of the design competence
        :type dc_uid: str
        :param license_type: type of the license, optional
        :type license_type: str
        :param license_specification: specification of the license, optional
        :type license_specification: str
        :param license_info: additional info about the license, optional
        :type license_info: str
        """
        self.assert_node_exists(dc_uid)
        entries = ['license_type', 'license_specification', 'license_info']
        for entry in entries:
            if locals()[entry] is not None:
                add_nested_dict_entry(self.nodes[dc_uid], ['general_info', 'licensing', entry], locals()[entry])

    def add_dc_sources(self, dc_uid, repository_link=None, download_link=None, references=None):
        """Method to add source information to a design competence

        :param dc_uid: uid of the design competence
        :type dc_uid: str
        :param repository_link: link to the dc's repository, optional
        :type repository_link: str
        :param download_link: link to download the dc, optional
        :type download_link: str
        :param references: additional references, optional
        :type references: list
        """
        self.assert_node_exists(dc_uid)
        entries = ['repository_link', 'download_link', 'references']
        for entry in entries:
            if locals()[entry] is not None:
                add_nested_dict_entry(self.nodes[dc_uid], ['general_info', 'sources', entry], locals()[entry])
        return

    def add_dc_execution_details(self, dc_uid, operating_system=None, integration_platform=None, command=None,
                                 description=None, software_requirements=None, hardware_requirements=None,
                                 replace_for=None):
        """Method to add execution details information to a design competence

        :param dc_uid: uid of the design competence
        :type dc_uid: str
        :param operating_system: Operating system the tool is running on (e.g. Linux, Windows, MAC OS), optional
        :type operating_system: str
        :param integration_platform: Specification of the integration platform (e.g. RCE, Optimus), optional
        :type integration_platform: str
        :param command: Execution command (e.g. runTool.exe), optional
        :type command: str
        :param description: Additional infos of the execution, optional
        :type description: str
        :param software_requirements: Requirements on the software side, optional
        :type software_requirements: str
        :param hardware_requirements: Requirements on the hardware side, optional
        :type hardware_requirements: str
        :param replace_for: Index of execution details to be replaced
        :type hardware_requirements: int
        """
        self.assert_node_exists(dc_uid)
        entries = ['operating_system', 'integration_platform', 'command', 'description', 'software_requirements',
                   'hardware_requirements']

        # Create local_component_info entry
        if 'execution_info' not in self.nodes[dc_uid]:
            self.nodes[dc_uid].update({'execution_info': {'local_component_info': []}})
        if 'local_component_info' not in self.nodes[dc_uid]['execution_info']:
            self.nodes[dc_uid].update({'execution_info': {'local_component_info': []}})
        ex_det_list = self.nodes[dc_uid]['execution_info']['local_component_info']

        if replace_for is None:
            ex_det_list.append(('execution_details', dict()))
        elif replace_for > len(ex_det_list)-1:
            raise AssertionError('Could not replace execution details at "replace_for" == {}.'.format(replace_for))

        for entry in entries:
            if locals()[entry] is not None:
                ex_det_list[-1 if replace_for is None else replace_for][1][entry] = locals()[entry]
            elif replace_for is not None and entry in ex_det_list[replace_for][1]:
                del ex_det_list[replace_for][1][entry]

    def add_node(self, n, attr_dict=None, **attr):
        """Add a single node and update node attributes.

        :param n: node
        :type n: A node can be any hashable Python object except None.
        :param attr_dict: dictionary of attribute keyword arguments.
        :type attr_dict: dict
        :param attr: Set or change node attributes using attr_dict.
        :type attr: str, dict

        Examples:

        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_node(1)
        >>> G.add_node('Hello')
        >>> K3 = nx.Graph([(0, 1), (1, 2), (2, 0)])
        >>> G.add_node(K3)
        >>> G.number_of_nodes()

        Use keywords set/change node attributes:

        >>> G.add_node(1, size=10)
        >>> G.add_node(3, weight=0.4, UTM=('13S', 382871, 3972649))

        .. note::
            A hashable object is one that can be used as a key in a Python
            dictionary. This includes strings, numbers, tuples of strings
            and numbers, etc.

        .. note::
            On many platforms hashable items also include mutables such as
            NetworkX Graphs, though one should be careful that the hash
            doesn't change on mutables.
        """

        # Execute base function
        super(KadmosGraph, self).add_node(n, **attr)
        if attr_dict:
            for key in attr_dict:
                self.nodes[n][key] = attr_dict[key]

        # Set some default attributes
        if 'name' not in self.nodes[n]:
            self.nodes[n]['name'] = n
        if 'label' not in self.nodes[n]:
            self.nodes[n]['label'] = n
        if 'instance' not in self.nodes[n]:
            self.nodes[n]['instance'] = 0

    def add_edge(self, u, v, attr_dict=None, **attr):
        """Add an edge between u and v.

        :param u: node
        :type u: can be, for example, strings or numbers. Nodes must be hashable (and not None) Python objects.
        :param v: node
        :type v: see u
        :param attr_dict: keyword arguments
        :type attr_dict: str
        :param attr: edge data (or labels or objects) can be assigned using keyword arguments.
        :type attr: str

        The nodes u and v will be automatically added if they are not already in the graph.

        Adding an existing edge results in an update of the edge data.

        Edge attributes can be specified with keywords or by directly accessing the edge's attribute dictionary.
        See examples below.

        The following examples both add the edge e=(1,2) to graph G:

        >>> G = nx.Graph() # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> e = (1, 2)
        >>> G.add_edge(1, 2) # explicit two-node form
        >>> G.add_edge(*e) # single edge as tuple of two nodes

        Many NetworkX algorithms designed for weighted graphs use an edge attribute (by default 'weight') to hold a
        numerical value. Associate date to edge using keywords:

        >>> G.add_edge(1, 2, weight=3)
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)

        For non-string attribute keys, use subscript notation.

        >>> G.add_edge(1, 2)
        >>> G[1][2}.update({0: 5})
        >>> G.edges[1, 2].update({0: 5})

        """

        # Execute base function
        super(KadmosGraph, self).add_edge(u, v, **attr)
        if attr_dict:
            for key in attr_dict:
                self.adj[u][v][key] = attr_dict[key]

    def add_instance_of(self, file_path, node):
        """Method to duplicate a function with a higher instance

        :param file_path: path to CMDOWS file
        :type file_path: str
        :param node: node to get instance of
        :type node: str
        :return: new node
        :rtype: str
        """

        assert int(self.nodes[node]['instance']) == 0, 'first instance of the function has to be supplied'

        inputs_list = []
        outputs_list = []
        cmdows = etree.parse(file_path, parser).getroot()
        cmdows.clean()
        ignore_modes=False

        uid = self.add_instance(node)

        kwargs = {'name': self.nodes[node]['name'], 'mode': self.nodes[node]['mode'], 'instance': uid[-1:],
                  'version': self.nodes[node]['version'], 'label': self.nodes[node]['label'],
                  'general_info': self.nodes[node]['general_info'],
                  'performance_info': self.nodes[node]['performance_info'],
                  'execution_info': self.nodes[node]['execution_info'],
                  'projectSpecific': self.nodes[node]['projectSpecific']}

        new_node = self.copy_node_with_suffix(node, self.INSTANCE_SUFFIX + uid[-1:], '', **kwargs)

        function = cmdows.xpath(get_uid_search_xpath(node))[0]

        for inp in function.findall('inputs/input'):
            self.add_edge(inp.findtext('parameterUID').replace("'", '"'), new_node,
                          valid_ranges=inp.finddict('validRanges', ordered=False, camel_case_conversion=True))

        if not function.findall('inputs/input'):
            # Determine assumed input file location (same folder as CMDOWS file)
            input_file_path = os.path.join(os.path.split(os.path.normpath(function.base))[0],
                                           function.findtext('ID') + '-input.xml').replace('file:' + os.path.sep, '')

            if os.path.isfile(input_file_path):
                inputs_list.append(input_file_path)
            else:
                logger.warning('Could not find inputs for function: ' + function.get('uID'))

        for output in function.findall('outputs/output'):
            self.add_edge(new_node, output.findtext('parameterUID').replace("'", '"'))

        if not function.findall('outputs/output'):
            # Determine assumed output file location (same folder as CMDOWS file)
            output_file_path = os.path.join(os.path.split(os.path.normpath(function.base))[0],
                                            function.findtext('ID') + '-output.xml').replace('file:' + os.path.sep, '')
            if os.path.isfile(output_file_path):
                outputs_list.append(output_file_path)
            else:
                logger.warning('Could not find outputs for function: ' + function.get('uID'))

        # Add inputs and outputs based on XML
        for input_el in inputs_list:
            inputs = _read_io_xml_file(input_el, function.findtext('modeID'), ignore_modes=ignore_modes)
            for input in inputs['leafNodes']:
                if not self.has_node(input['xpath']):
                    self.add_node(input['xpath'],
                                  category='variable',
                                  shape='o',  # TODO: Extend this XML attributes for description, note, unit, data_type
                                  label=input['xpath'].split('/')[-1])
                self.add_edge(input['xpath'], new_node)

        for output_el in outputs_list:
            outputs = _read_io_xml_file(output_el, function.findtext('modeID'), ignore_modes=ignore_modes)
            for output in outputs['leafNodes']:
                # Add new parameter if it does not exist yet
                if not self.has_node(output['xpath']):
                    self.add_node(output['xpath'],
                                  category='variable',
                                  shape='o',
                                  label=output['xpath'].split('/')[
                                      -1])  # TODO: Extend this to pick up XML attributes for description, note, unit, data_type
                self.add_edge(new_node, output['xpath'])

        return new_node

    def has_nodes(self, nodes):
        """Function that checks whether all nodes given in a list are present in the graph.

        :param nodes: list of nodes to be checked
        :type nodes: list
        :return: boolean whether all nodes have been found
        :rtype: bool
        """

        for node in nodes:
            if not self.has_node(node):
                return False

        return True

    def node_is_function(self, node):
        """Function that checks whether a node is a function node or not.

        :param node: node in graph
        :type node: str
        :return: check result
        :rtype: bool
        """

        return self.nodes[node]["category"] == "function"

    def node_is_variable(self, node):
        """Function that checks whether a node is a variable node or not.

        :param node: node in graph
        :type node: str
        :return: check result
        :rtype: bool
        """

        return self.nodes[node]["category"] == "variable"

    def node_is_output(self, node):
        """Function that checks whether a node is a system output.

        :param node: node in graph
        :type node: str
        :return: check result
        :rtype: bool
        """

        if self.in_degree(node) > 0 and self.out_degree(node) == 0:
            return True
        else:
            return False

    def node_is_hole(self, node):
        """
        Function that checks whether a node is a hole (unconnected).

        :param node: node in graph
        :type node: str
        :return: check result
        :rtype: bool
        """

        if self.in_degree(node) == 0 and self.out_degree(node) == 0:
            return True
        else:
            return False

    def get_first_node_instance(self, node):
        """Method to obtain the first instance of a node

        :param node: node to find first instance of
        :type node: str
        :return: node of first instance
        :rtype: str
        """

        # Input assertions
        self.assert_node_exists(node)
        node_instance = self.assert_and_get_node_attribute(node, 'instance')

        if node_instance != 0:
            if self.nodes[node]['category'] == 'variable':
                return node[:-len('{}{}'.format(self.INSTANCE_SUFFIX, node_instance))]
            else:
                node_mode = self.assert_and_get_node_attribute(node, 'mode')
                node_name = self.assert_and_get_node_attribute(node, 'name')
                found_nodes = self.find_all_nodes(category='function',
                                                  attr_cond=[['name', '==', node_name],
                                                             ['instance', '==', 0],
                                                             ['mode', '==', node_mode]])
                if len(found_nodes) > 1:
                    raise AssertionError('Found multiple first node instances for node {}.'.format(node))
                elif not found_nodes:
                    raise AssertionError('Could not find first node instance for node {}.'.format(node))
                else:
                    return found_nodes[0]
        else:
            return node

    def get_same_graph_class(self, graph, copy_type='deep'):
        """
        Method to reinstantiate a given graph according to the same graph class as the self.

        :param graph: graph object to be reinstantiated
        :type graph: DiGraph
        :param copy_type: setting to have a deep or shallow copy of the graph
        :type copy_type: str
        :return: reinstantiated graph
        :rtype: KadmosGraph
        """
        assert copy_type in ['deep', 'shallow'], 'copy_type should be either "deep" or "shallow".'

        klass = self.__class__
        instance = klass(graph)
        if copy_type == 'deep':
            instance = instance.deepcopy()
        return instance

    def get_function_graph(self, keep_objective_variables=False):
        """Method for replacing variable nodes by function connections.

        :param: keep_objective_variables: if given the objective variables will remain in graph
        :type: keep_objective_variables: bool
        :return: new graph without variable nodes

        .. note::
            This function removes all variable nodes from the graph and replaces the variable connections of each function
            with function connections, such that if N(i) is a variable node, and F(i) a function node:

            F(1) => N(1) => F(2) => N(2) => F(3)

            becomes: F(1) => F(2) => F(3)
        """
        # TODO: create separate function to get coupling strength between two nodes: get_coupling_strength

        # Assertions
        assert isinstance(keep_objective_variables, bool)

        # Make copy of graph
        function_graph = self.deepcopy()

        # Iterate through nodes and get function nodes connected to each variable node
        add_edges = []
        remove_nodes = []
        remove_edges = []
        for node in function_graph.nodes:
            in_funcs = []
            out_funcs = []
            is_obj_var = False

            # Only consider variable nodes
            node_cat = function_graph.nodes[node]['category']
            if node_cat == 'variable' or node_cat == 'variable group':

                # Loop in/out edges and get all function nodes connected to variable
                for edge in function_graph.out_edges(node):
                    if function_graph.nodes[edge[1]]['category'] == 'function':
                        if keep_objective_variables:
                            if function_graph.nodes[edge[1]]["name"] == "Objective":
                                is_obj_var = True
                            else:
                                out_funcs.append(edge[1])
                                remove_edges.append(edge)
                        else:
                            out_funcs.append(edge[1])
                for edge in function_graph.in_edges(node):
                    if function_graph.nodes[edge[0]]['category'] == 'function':
                        in_funcs.append(edge[0])

                # Add all variable nodes to remove list
                if not is_obj_var:
                    remove_nodes.append(node)

            # Get all edge combinations using itertools
            if in_funcs and out_funcs:
                add_edges += [x for x in itertools.product(in_funcs, out_funcs)]

        # Remove all edges (only applies if obj vars are kept in graph)
        for edge in remove_edges:
            function_graph.remove_edge(edge[0], edge[1])

        # Remove all variable nodes
        for node in remove_nodes:
            function_graph.remove_node(node)

        # Add function edges, increase connection strength if edge exists in graph
        for edge in add_edges:
            if edge in function_graph.edges():
                function_graph[edge[0]][edge[1]]['coupling_strength'] += 1
            else:
                function_graph.add_edge(*edge, coupling_strength=1)

        return function_graph

    def get_system_inputs(self, *args, **kwargs):
        """This method checks whether there are system inputs in the graph using the function nodes provided.

        :param args: function nodes
        :type args:
        :param kwargs:
        :type kwargs:
        :return: system input nodes dictionary
        :rtype: dict

        .. note:: The function nodes should be provided in the args. If system inputs exist they are returned.
        """
        # TODO: Imco add type of args and doc of kwargs

        assert all(self.node_is_function(arg) for arg in args), "At least one node in args is not a function node."

        ignore_toolspecific = kwargs.get('ignore_toolspecific', False)
        assert isinstance(ignore_toolspecific, bool)

        system_input_nodes = {}
        for func in args:
            for u, v in self.in_edges(func):
                if not self.in_edges(u):
                    if ignore_toolspecific and "toolspecific" in u:
                        continue
                    if u not in system_input_nodes:
                        system_input_nodes[u] = [func]
                    else:
                        system_input_nodes[u].append(func)

        return system_input_nodes

    def get_graph_properties(self, *args):
        """This function retrieves the properties of a graph.

        :param: args: specific properties to be retrieved (optional)
        :return: dictionary containing the properties of the graph
        :rtype: dict

        If no argument is given, the standard list of properties GRAPH_PROPERTIES is analyzed and their values are
        returned in a dict. If arguments are given, only this list will be used as standard list of properties.
        """

        # Make sure that arguments are valid
        get_props = self.GRAPH_PROPERTIES
        if args:
            get_props = args
            for arg in args:
                assert isinstance(arg, string_types)
                assert arg in self.GRAPH_PROPERTIES, "Arguments must be pre-defined properties from GRAPH_PROPERTIES."

        # Initiate property dict and store all graph properties
        property_dict = {}

        # Get nodes and edges in graph
        if "nodes" in get_props:
            property_dict["nodes"] = len(self.nodes)
        if "edges" in get_props:
            property_dict["edges"] = len(self.edges())

        # Get system_inputs and connections in graph
        if any(prop in get_props for prop in ["system_inputs", "couplings", "functions"]):
            system_inputs = 0
            couplings = 0
            functions = 0
            for node in self.nodes:
                if self.node_is_variable(node):
                    if self.in_degree(node) < 1:
                        system_inputs += 1  # system inputs are counted by nodes
                    elif self.out_degree(node) > 0:  # since at least one in_degree, if out_degree then coupling
                        couplings += (self.in_degree(node) * self.out_degree(node))  # couplings are counted by edges
                elif self.node_is_function(node):
                    functions += 1

            if "system_inputs" in get_props:
                property_dict["system_inputs"] = system_inputs
            if "couplings" in get_props:
                property_dict["couplings"] = couplings
            if "functions" in get_props:
                property_dict["functions"] = functions

        return property_dict

    def get_number_of_couplings(self, node):
        """This function returns the number of couplings of a node in the graph.

        :param node: input node
        :return: number of couplings for the input node
        :rtype: int
        """

        assert node in self, "The specified node is not present in graph."

        couplings = 0
        for u, v in self.out_edges(node):
            couplings += self.out_degree(v)
        for u, v in self.in_edges(node):
            couplings += self.in_degree(u)

        return couplings

    def get_direct_coupling_nodes(self, *args, **kwargs):
        """This method returns the direct couplings between two nodes in a graph.

        :param args: nodes to be checked for couplings; at least two must be provided
        :type args: str, list
        :param kwargs: print_couplings: option for printing all couplings with coupling direction and node (optional)
        :type kwargs: print_couplings: bool
        :param kwargs: direction: set only coupling in certain direction (optional)
        :type kwargs: direction: str
        :return: couplings: list of tuples containing the coupled nodes and the coupling node
        :rtype: list

        This method is specifically written (and tested) with function nodes in mind. Direct coupling is defined as
        coupling with between two nodes through a third node.

        In this function, each combination between the provided arguments is tested for couplings (in pairs). First,
        the two nodes in each pair are checked for common neighbors. If they do, the edges of the common neighbors are
        iterated to determine whether the node-pair is connected to each other, or only the neighbor. The direction of
        the coupling is also checked.

        Example:

        * The connection: F1 => N1 => F2
        * Leads to: [(F1, F2, N1)]
        """

        # Assert that every argument is string, and node in graph
        if isinstance(args[0], list):
            assert len(args) == 1, "Only one list of functions can be provided."
            args = args[0]
        else:
            assert len(args) > 1, "At least two arguments must be provided."
        for arg in args:
            assert isinstance(arg, string_types), "Every argument must be a string_type."
            assert arg in self.node, "All arguments must be nodes in graph."

        # Set print_couplings variable
        print_couplings = kwargs.get('print_couplings', False)
        assert isinstance(print_couplings, bool), "print_couplings must be of type bool"

        # Set only coupling in certain direction
        direction = kwargs.get('direction', 'both')
        assert direction in ["both", "forward", "backward"], "Invalid direction provided."

        # Get list of all neighbors of each argument node, save in dict
        arg_neighbors = {}
        for arg in args:
            arg_neighbors[arg] = list(nx.all_neighbors(self, arg))

        # Get argument pair combinations
        arg_pairs = list(itertools.combinations(args, 2))

        # Iterate through pairs of nodes, check for neighbors, iterate through edges of common neighbor
        couplings = []
        for pair in arg_pairs:

            # Get all shared neighbors between node pair
            shared_nodes = set(arg_neighbors[pair[0]]).intersection(arg_neighbors[pair[1]])

            # If shared neighbors found, iterate their edges
            if shared_nodes:

                # Iterate each shared neighbor
                for node in shared_nodes:

                    # Iterate each edge and check if a member of the node pair is found in edge, start with in-edges
                    for in_edge in self.in_edges(node):
                        func = in_edge[0]
                        if func in pair:  # If member found, check if other pair member is in any of the out-edges
                            coupled_func = pair[1] if func == pair[0] else pair[0]  # Get the other node-pair-member
                            if any(coupled_func in out_edge[1] for out_edge in self.out_edges(node)):
                                couplings.append((func, coupled_func, node))
                                break

                    # Repeat the above algorithm, but switch edge analysis to get
                    # coupling direction (first out, then in-edges)
                    for out_edge in self.out_edges(node):
                        func = out_edge[0]
                        if func in pair:
                            coupled_func = pair[1] if func == pair[0] else pair[0]
                            if any(coupled_func in in_edge[1] for in_edge in self.in_edges(node)):
                                couplings.append((coupled_func, func, node))
                                break

            else:
                continue

        # Filter the found couplings according to direction setting
        valid_couplings = []
        if direction == "forward":
            for idx, analysis in enumerate(args):
                analysis_checklist = args[idx + 1:]
                valid_couplings.extend([coupling for coupling in couplings if
                                        (coupling[0] == analysis and coupling[1] in analysis_checklist)])
            couplings = valid_couplings
        elif direction == "backward":
            for idx, analysis in enumerate(reversed(args)):
                analysis_checklist = args[::-1][idx + 1:]
                valid_couplings.extend([coupling for coupling in couplings if
                                        (coupling[0] == analysis and coupling[1] in analysis_checklist)])
            couplings = valid_couplings

        # Print results
        if print_couplings:
            print('\n- - - - - -')
            print(' COUPLINGS ')
            print('- - - - - -\n')
            if not couplings:
                print("No direct couplings found between provided nodes.")
            else:
                print("The following couplings were found between provided nodes ({} total): ".format(len(couplings)))
                for couplingTpl in couplings:
                    print("{} >> {} | {}".format(couplingTpl[0], couplingTpl[1], couplingTpl[2]))
            print('- - - - - -\n')

        return couplings

    def get_nodes_based_on_strings(self, *args, **kwargs):
        """This function enables the user to search graph nodes for specific strings.

        :param args: strings that graph nodes being searched for
        :type args: str
        :param kwargs: include_all: If include_all is set to True, all matching nodes are added to returned list
        :type kwargs: include_all: bool
        :return: matching nodes that user selected (all if include_all is True)

        Each provided string will be searched for, and if multiple node are found for each string, the user will be able
        to select the ones desired. The other matched nodes are disregarded.
        """

        # Check if all found nodes should be included or not
        include_all = kwargs.get('include_all', False)
        assert isinstance(include_all, bool)

        # Set up pattern for bracket search; compile before loop for better performance
        bracket_pattern = re.compile('\[.*?\]')

        # Ensure that each arg is string; set up matching nodes dict
        matched_nodes = {}  # collect nodes that match strings in dict
        brackets_in_arg = {}  # dict to check whether brackets should be removed or not from Node string for search
        arg_list = []
        for arg in args:
            assert isinstance(arg, string_types)
            matched_nodes[arg] = []  # collect all matching nodes in list
            brackets_in_arg[arg] = bool(bracket_pattern.search(arg))  # True if bracket in string, otherwise False
            arg_list.append(arg)

        # Loop though nodes and check if string argument matches node
        for node in self.nodes:

            # Check all args match that node
            for arg in arg_list:

                # Check if brackets are given in string argument
                check_node_string = node
                if not brackets_in_arg[arg]:  # remove brackets from node if not brackets in argument
                    check_node_string = bracket_pattern.sub("", node)

                # Add node to matched_nodes if argument string matches
                if arg in check_node_string:
                        matched_nodes[arg].append(node)

        selected_nodes = []

        # If not all nodes should be included
        if not include_all:

            # Prompt user to choose nodes
            for arg in matched_nodes:
                if len(matched_nodes[arg]) > 1:

                    # Check if user wants to include or nodes or not
                    user_prompt = "Multiple nodes found for '{}'. Would you like to include all " \
                                  "matching nodes?".format(arg)
                    user_select = prompting.user_prompt_yes_no(message=user_prompt)

                    if user_select == 1:
                        # If user wants to include all nodes, skip to next
                        selected_nodes += matched_nodes[arg]
                    else:
                        # Print nodes found for arg string
                        mssg = "The following nodes were found for {}: ".format(arg)
                        printing.print_indexed_list(message=mssg, *matched_nodes[arg])

                        # Select nodes from list
                        select_nodes_prompt = "Please select the nodes you would like to include for {} (separate " \
                                              "selection by space):".format(arg)
                        user_sel = prompting.user_prompt_select_options(message=select_nodes_prompt,
                                                                        *matched_nodes[arg])
                        selected_nodes += user_sel
                elif len(matched_nodes[arg]) > 0:
                    selected_nodes += matched_nodes[arg]
                else:
                    logger.warning("Could not find any nodes matching {}.".format(arg))

        # If all nodes included
        else:

            # Add all matched nodes to returned list
            for arg in matched_nodes:
                selected_nodes += matched_nodes[arg]

        return selected_nodes

    def get_subgraph_by_function_nodes(self, *args, **kwargs):
        """This function retrieves a subgraph from the original graph only containing the argument nodes.

        :param args: arbitrary amount of graph nodes
        :type args: list, str
        :param kwargs: copy_type: type of copy (clean or deep)
        :type kwargs: copy_type: str
        :return: sub-graph only containing nodes provided as arguments, and their edges

        .. note:: All arguments must be found in the graph.
        """

        # handle the fact that the *args could also be a list or tuple directly
        if len(args) == 1 and (isinstance(args[0], tuple) or isinstance(args[0], list)):
            args = list(args[0])

        # get copy_type
        copy_type = kwargs.get('copy_type', 'deep')
        assert copy_type in ['deep', 'shallow'], 'copy_type should be either "deep" or "shallow".'

        # check if all arguments are nodes in graph
        for arg in args:
            assert arg in self, "Argument {} is not a node in graph".format(arg)

        # get sub-nodes and sub-edges
        sub_nodes = []
        for arg in args:
            sub_nodes.append(arg)
            sub_nodes += nx.all_neighbors(self, arg)

        # create subgraph from nodes
        subgraph = self.get_kadmos_subgraph(sub_nodes, copy_type=copy_type)

        return subgraph

    def get_source(self, node):
        """Function to determine the single source of a given node. Throws error if node has multiple sources.

        :param node: node for which source should be found
        :type node: str
        :return: source
        :rtype: str
        """

        self.assert_node_exists(node)
        sources = [edge[0] for edge in self.in_edges(node)]
        if len(sources) > 1:
            raise AssertionError('Node has multiple sources, use get_sources() method instead.')
        elif len(sources) == 1:
            return sources[0]
        else:
            return None

    def get_sources(self, node):
        """Function to determine the sources of a given node.

        :param node: node for which sources should be found
        :type node: str
        :return: list with sources
        :rtype: list
        """

        assert self.has_node(node), 'Node not present in the graph.'
        sources = [edge[0] for edge in self.in_edges(node)]

        return sources

    def get_target(self, node):
        """Function to determine the single target of a given node. Throws error if node has multiple targets.

        :param node: node for which target should be found
        :type node: str
        :return: target
        :rtype: str
        """

        self.assert_node_exists(node)
        targets = [edge[1] for edge in self.out_edges(node)]
        if len(targets) > 1:
            raise AssertionError('Node has multiple targets, use get_targets() method instead.')
        elif len(targets) == 1:
            return targets[0]
        else:
            return None

    def get_targets(self, node):
        """Function to determine the targets of a given node.

        :param node: node for which targets should be found
        :type node: str
        :return: list with targets
        :rtype: list
        """

        assert self.has_node(node), 'Node {} not present in the graph.'.format(node)
        targets = [edge[1] for edge in self.out_edges(node)]

        return targets

    def get_kadmos_subgraph(self, nodes, copy_type='deep'):

        assert copy_type in ['deep', 'shallow'], 'copy_type should be either "deep" or "shallow".'

        subgraph = self.subgraph(nodes)

        return self.get_same_graph_class(subgraph)

    def get_contracted_graph(self, contraction_level):
        """This function contracts the nodes of a graph to the provided contraction level.

        :param contraction_level: from 0 (highest level) to X (lowest level existing in XML schema)
        :type contraction_level: int
        :return: contracted_graph: graph with contracted nodes

        The contraction level refers to the xpath-level, which represents the position of the descendant with respect
        to its predecessors. The example below represents a level 3 node, with "cpacs" being at level zero.

        /cpacs/aircraft/wings/wing

        --cpacs

        ----aircraft

        --------wings

        ------------wing

        .. note::
            All nodes above the contraction level are removed from the graph and replaced by a "variable group" node, which
            groups the removed nodes in a node at contraction level. This allows for a "de-cluttering" of the graph, with
            the graph connections still being represented.
        """

        # check input
        assert (contraction_level >= 0) & isinstance(contraction_level, int), \
            "Contraction level should be non-negative integer."

        # create clean copy of graph
        contracted_graph = self.copy()

        logger.info('Contracting graph... ')

        # get function nodes in graph
        func_nodes = contracted_graph.function_nodes

        # iterate over function nodes, check all their incoming and outgoing edges for nodes above contraction level
        added_edges = []
        remove_nodes = []

        for func_node in func_nodes:

            for in_out in ['input', 'output']:
                if in_out == "input":  # edges have different format for incoming and outgoing nodes
                    func_edges = contracted_graph.in_edges(func_node)
                    var_idx = 0
                else:
                    func_edges = contracted_graph.out_edges(func_node)
                    var_idx = 1

                # iterate through function edges and check all its nodes
                for edge in func_edges:

                    var_node = edge[var_idx]
                    n_count = var_node.count('/')  # may also refer to "level" in graph node
                    if n_count - 1 > contraction_level:
                        remove_nodes.append(var_node)
                        split_xpath = var_node.split('/')[1:]  # remove first entry (this is empty since string starts
                        # with '/'
                        required_node = '/' + '/'.join(split_xpath[0:contraction_level + 1])  # Create xpath for group
                        # node

                        # add new node with "variable group" attributes
                        contracted_graph.add_node(required_node,
                                                  shape='d',
                                                  category='variable group',
                                                  label=split_xpath[contraction_level],
                                                  level=contraction_level)

                        # ensure that function node and newly added node are connected
                        add_edge = [func_node]
                        add_edge.insert(var_idx, required_node)
                        add_edge = tuple(add_edge)
                        if add_edge in added_edges:  # if edge already in graph
                            contracted_graph[add_edge[0]][add_edge[1]]['coupling_strength'] += 1
                        else:
                            contracted_graph.add_edge(*add_edge, coupling_strength=1)
                        added_edges.append(add_edge)

        # remove nodes in list
        remove_nodes_set = set(remove_nodes)  # ensure that items unique
        for node in remove_nodes_set:
            contracted_graph.remove_node(node)

        logger.info("Successfully contracted graph. {} nodes were contracted.".format(len(remove_nodes_set)))

        # set graph_is_contracted to True, so that user can be warned before graph operations etc
        contracted_graph.GRAPH_IS_CONTRACTED = True

        return contracted_graph

    @property
    def function_nodes(self):
        """Get list with all function nodes."""
        return [node for node in self.nodes if self.nodes[node]['category'] == 'function']

    def get_nodes_indegree(self):
        """Function to get the indegree of all the graph nodes and store them in a dictionary.

        :return: dictionary with node name key and indegree integer value.
        :rtype: dict
        """

        nid_dict = dict(list(self.in_degree()))
        return nid_dict

    def get_nodes_outdegree(self):
        """Function to get the outdegree of all the graph nodes and store them in a dictionary.

        :return: dictionary with node name key and outdegree integer value.
        :rtype: dict
        """

        nod_dict = dict(list(self.out_degree()))
        return nod_dict

    def get_nodes_subcategory(self):
        """Method to analyse all nodes and to update the subcategory attributes of the nodes."""

        for node in self.nodes:
            self.get_node_subcategory(node)

        return

    def get_node_subcategory(self, node):
        """Method to analyse a node and to update the subcategory attribute of the node.

        :param node: node in the graph
        :type node: str
        :return: subcategory of the node
        :rtype: str

        The following table illustrates how the subcategory is determined based on the category, indegree and outdegree:

        +-------------------+-----------------------------------+----------+-----------+
        | NODE CATEGORY     | SUBCATEGORY                       | INDEGREE | OUTDEGREE |
        +===================+===================================+==========+===========+
        | variable          | hole                              | 0        | 0         |
        |                   +-----------------------------------+----------+-----------+
        |                   | supplied input                    | 0        | 1         |
        |                   +-----------------------------------+----------+-----------+
        |                   | supplied shared input             | 0        | >1        |
        |                   +-----------------------------------+----------+-----------+
        |                   | output                            | 1        | 0         |
        |                   +-----------------------------------+----------+-----------+
        |                   | collision                         | >1       | 0         |
        |                   +-----------------------------------+----------+-----------+
        |                   | coupling                          |          |           |
        |                   | or                                | 1        | 1         |
        |                   | pure circular coupling            |          |           |
        |                   +-----------------------------------+----------+-----------+
        |                   | shared coupling                   |          |           |
        |                   | or                                | 1        | >1        |
        |                   | shared circular coupling          |          |           |
        |                   +-----------------------------------+----------+-----------+
        |                   | collided coupling                 |          |           |
        |                   | or                                | >1       | 1         |
        |                   | collided circular coupling        |          |           |
        |                   +-----------------------------------+----------+-----------+
        |                   | collided shared coupling          |          |           |
        |                   | or                                | >1       | >1        |
        |                   | collided shared circular coupling |          |           |
        +-------------------+-----------------------------------+----------+-----------+
        | function          | independent                       | 0        | 0         |
        |                   +-----------------------------------+----------+-----------+
        |                   | source                            | 0        | >0        |
        |                   +-----------------------------------+----------+-----------+
        |                   | sink                              | >0       | 0         |
        |                   +-----------------------------------+----------+-----------+
        |                   | complete                          | >0       | >0        |
        +-------------------+-----------------------------------+----------+-----------+
        """

        # Check node
        assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Get node indegree and outdegree
        idx = self.in_degree(node)
        od = self.out_degree(node)

        # Get node data
        data = self.nodes[node]

        # Analyse node and set subcategory
        if 'category' not in data:
            raise AssertionError('Category is missing on node {} with data {}.'.format(node, data))

        if data['category'] == 'variable':
            if idx == 0 and od == 0:
                data['subcategory'] = 'hole'
            elif idx == 0 and od == 1:
                data['subcategory'] = 'supplied input'
            elif idx == 0 and od > 1:
                data['subcategory'] = 'supplied shared input'
            elif idx == 1 and od == 0:
                data['subcategory'] = 'output'
            elif idx > 1 and od == 0:
                data['subcategory'] = 'collision'
            elif idx == 1 and od == 1:
                in_function = list(self.in_edges(node))[0][0]
                if in_function == list(self.out_edges(node))[0][1]:
                    data['subcategory'] = 'pure circular coupling'
                    data['circularity_info'] = dict()
                    data['circularity_info']['level'] = 1
                    data['circularity_info']['circular_functions'] = [in_function]
                else:
                    data['subcategory'] = 'coupling'
            elif idx == 1 and od > 1:
                in_function = list(self.in_edges(node))[0][0]
                if in_function in [edge[1] for edge in self.out_edges(node)]:
                    data['subcategory'] = 'shared circular coupling'
                    data['circularity_info'] = dict()
                    data['circularity_info']['level'] = 1
                    data['circularity_info']['circular_functions'] = [in_function]
                else:
                    data['subcategory'] = 'shared coupling'
            elif idx > 1 and od == 1:
                out_function = list(self.out_edges(node))[0][1]
                if out_function in [edge[0] for edge in self.in_edges(node)]:
                    data['subcategory'] = 'collided circular coupling'
                    data['circularity_info'] = dict()
                    data['circularity_info']['level'] = 1
                    data['circularity_info']['circular_functions'] = [out_function]
                else:
                    data['subcategory'] = 'collided coupling'
            elif idx > 1 and od > 1:
                in_nodes = [edge[0] for edge in self.in_edges(node)]
                out_nodes = [edge[1] for edge in self.out_edges(node)]
                common_nodes = set(in_nodes).intersection(set(out_nodes))
                if common_nodes:
                    data['subcategory'] = 'collided shared circular coupling'
                    data['circularity_info'] = dict()
                    data['circularity_info']['level'] = len(common_nodes)
                    data['circularity_info']['circular_functions'] = list(common_nodes)
                else:
                    data['subcategory'] = 'collided shared coupling'
            else:
                raise NotImplementedError('Variable subcategory could not be determined based on combination of '
                                          'indegree {} and outdegree {}.'.format(idx, od))
        if data['category'] == 'variable group':
            if idx == 0 and od == 0:
                data['subcategory'] = 'hole group'
            elif idx == 0 and od == 1:
                data['subcategory'] = 'supplied input group'
            elif idx == 0 and od > 1:
                data['subcategory'] = 'supplied shared input group'
            elif idx > 0 and od == 0:
                data['subcategory'] = 'output group'
            elif idx > 0 and od == 1:
                data['subcategory'] = 'coupling group'
            elif idx > 0 and od > 1:
                data['subcategory'] = 'shared coupling group'
            else:
                raise NotImplementedError('Group variable subcategory could not be determined based on combination '
                                          'of indegree {} and outdegree {}.'.format(idx, od))
        if data['category'] == 'function':
            if idx == 0 and od == 0:
                data['subcategory'] = 'independent'
            elif idx == 0 and od > 0:
                data['subcategory'] = 'source'
            elif idx > 0 and od == 0:
                data['subcategory'] = 'sink'
            elif idx > 0 and od > 0:
                data['subcategory'] = 'complete'
            else:
                raise NotImplementedError('Function subcategory could not be determined based on combination of '
                                          'indegree {} and outdegree {}.'.format(idx, od))

        return data['subcategory']

    def get_categorized_nodes(self, print_in_log=False):
        """Function that returns a dictionary with graph nodes grouped according to category and subcategory.

        :param print_in_log: option for printing the categories
        :type print_in_log: bool
        :return: dictionary with analysis results
        :rtype: dict
        """
        # TODO: Speedup this function if possible (deepcopy is fast, the rest is slow)

        self.get_nodes_subcategory()
        result = deepcopy(self.NODE_CAT_TREE)

        for node, data in self.nodes(data=True):
            for key1 in result:
                if data['category'] == key1:
                    for key2 in result[key1]:
                        if data['subcategory'] == key2:
                            result[key1][key2].append(node)
                        else:
                            NotImplementedError('Unsupported node subcategory found.')
                else:
                    NotImplementedError('Unsupported node category found.')

        if print_in_log:
            print('\n- - - - - - - - -')
            print(' NODE CATEGORIES ')
            print('- - - - - - - - -\n')
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(result)
            print('- - - - - - - - -\n')

        return result

    def get_node_attributes(self, node, attr_list, print_in_log=False):
        """Function to get and print certain attributes of a node from the graph.

        :param node: node name
        :type node: str
        :param attr_list: list with attributes to be pulled
        :type attr_list: list
        :param print_in_log: option for printing to log
        :type print_in_log: bool
        :return: dictionary with node attributes
        :rtype: dict
        """

        node_attr = dict()

        if not isinstance(attr_list, list) and attr_list != 'all':
            attr_list = [attr_list]

        if attr_list == 'all':
            node_attr = self.nodes[node]
            if print_in_log:
                for key in self.nodes[node]:
                    print('        ' + key + ': ' + str(self.nodes[node][key]))
        elif isinstance(attr_list, list):
            for key in attr_list:
                # check if key is part of the attributes
                if key in self.nodes[node]:
                    node_attr[key] = self.nodes[node][key]
                    if print_in_log:
                        print('        ' + key + ': ' + str(self.nodes[node][key]))
                else:
                    if print_in_log:
                        print('        ' + key + ': attribute not defined for this node')

        return node_attr

    def get_function_metadata(self, node):
        """Function to get the node metadata in a list (used in the dynamic visualization package).

        :param node: function node to collect the metadata for.
        :type node: str
        :return: list with metadata
        :rtype: list
        """

        # Input assertions
        assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Settings
        preferred_data = ['name', 'mode', 'description', 'creator', 'version',
                          'problem role', 'architecture role',
                          'run_time', 'precision', 'standard_deviation']
        special_data = ['subgraph', 'contraction']
        ignored_data = ['level', 'category', 'subcategory', 'shape', 'label']

        # Gather data
        metadata = []
        node_data = dict(self.nodes[node])

        # First loop over preferred data
        for item in preferred_data:
            if item in node_data:
                metadata.append({item: node_data[item]})

        # Add remaining data
        for key, value in iteritems(node_data):
            if key not in preferred_data + special_data + ignored_data:
                metadata.append({key: value})

        # Loop over special data
        for item in special_data:
            if item in node_data:
                if item == special_data[0]:  # subgraph
                    metadata.append({item: str(type(node_data[item]))})
                elif item == special_data[1]:  # contraction
                    metadata.append({'CONTRACTION_DATA': ''})
                    contract_data = node_data[item]
                    idx = 0
                    for key, value in iteritems(contract_data):
                        idx += 1
                        metadata.append({'CONTRACTED_FUNCTION': idx})
                        for item2 in preferred_data:
                            if item2 in contract_data[key]:
                                metadata.append({item2: contract_data[key][item2]})
                        for key2, value2 in iteritems(contract_data[key]):
                            if key2 not in preferred_data+special_data+ignored_data:
                                metadata.append({key2: value2})

        return metadata

    def get_adjacency_matrix(self, print_in_log=True):
        """Function to determine the adjacency matrix of a graph.

        :param print_in_log: option for printing the results
        :type print_in_log: bool
        :return: different methods of storing the same adjacency matrix in one dictionary
        :rtype: dict
        """

        if print_in_log:
            print('\n- - - - - - - - - -')
            print(' ADJACENCY MATRIX  ')
            print('- - - - - - - - - -\n')
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(nx.convert.to_dict_of_dicts(self, edge_data=1))
            print('- - - - - - - - - -\n')

        return {'dict of dicts': nx.convert.to_dict_of_dicts(self, edge_data=1),
                'SciPy sparse matrix': nx.adjacency_matrix(self)}

    def get_architecture_node_ids(self, mdao_architecture, number_of_groups=None):
        """Method to get the IDs of architecture nodes specific for a certain MDAO architecture.

        :param mdao_architecture: specified architecture (CO, BLISS-2000, etc)
        :type mdao_architecture: str
        :param number_of_groups: number of subgroups in distributed architectures
        :type number_of_groups: int, None
        :return: node IDs
        :rtype: tuple
        """

        if mdao_architecture in self.OPTIONS_ARCHITECTURES[1:4]:  # Distributed convergence of monolithic architectures
            assert number_of_groups is not None, \
                'number_of_groups should be specified for this architecture ({}).'.format(mdao_architecture)
            assert number_of_groups > 0, 'number_of_groups should be larger than 0.'
            sys_opt = '{}{}'.format(self.SYS_PREFIX, self.OPTIMIZER_STRING)
            sys_conv = '{}{}'.format(self.SYS_PREFIX, self.CONVERGER_STRING)
            sub_convs = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.CONVERGER_STRING, self.SUBSYS_SUFFIX, item) for
                        item in range(number_of_groups)]
            return sys_opt, sys_conv, sub_convs
        elif mdao_architecture == self.OPTIONS_ARCHITECTURES[7]:  # CO
            assert number_of_groups is not None, \
                'number_of_groups should be specified for this architecture ({}).'.format(mdao_architecture)
            assert number_of_groups > 0, 'number_of_groups should be larger than 0.'
            sys_opt = '{}{}'.format(self.SYS_PREFIX, self.OPTIMIZER_STRING)
            sub_opts = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.OPTIMIZER_STRING, self.SUBSYS_SUFFIX, item) for
                        item in range(number_of_groups)]
            return sys_opt, sub_opts
        elif mdao_architecture == self.OPTIONS_ARCHITECTURES[8]:  # BLISS-2000
            assert number_of_groups is not None, \
                'number_of_groups should be specified for this architecture ({}).'.format(mdao_architecture)
            assert number_of_groups > 0, 'number_of_groups should be larger than 0.'
            sys_opt = '{}{}'.format(self.SYS_PREFIX, self.OPTIMIZER_STRING)
            sys_conv = '{}{}'.format(self.SYS_PREFIX, self.CONVERGER_STRING)
            sys_sms = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.SM_STRING, self.SUBSYS_SUFFIX, item) for
                       item in range(number_of_groups)]
            sub_does = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.DOE_STRING, self.SUBSYS_SUFFIX, item) for
                        item in range(number_of_groups)]
            sub_opts = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.OPTIMIZER_STRING, self.SUBSYS_SUFFIX, item) for
                        item in range(number_of_groups)]
            sub_convs = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.CONVERGER_STRING, self.SUBSYS_SUFFIX, item) for
                        item in range(number_of_groups)]
            return sys_opt, sys_conv, sys_sms, sub_does, sub_opts, sub_convs

    def get_architecture_node_labels(self, mdao_architecture, number_of_groups=None):
        """Method to get the labels of architecture nodes specific for a certain MDAO architecture.

        :param mdao_architecture: specified architecture (CO, BLISS-2000, etc)
        :type mdao_architecture: str
        :param number_of_groups: number of subgroups in distributed architectures
        :type number_of_groups: int, None
        :return: node labels
        :rtype: tuple
        """

        if mdao_architecture in self.OPTIONS_ARCHITECTURES[1:4]:  # Distributed convergence of monolithic architectures
            assert number_of_groups is not None, \
                'number_of_groups should be specified for this architecture ({}).'.format(mdao_architecture)
            assert number_of_groups > 0, 'number_of_groups should be larger than 0.'
            sys_opt_label = '{}{}'.format(self.SYS_PREFIX, self.OPTIMIZER_LABEL)
            sys_conv_label = '{}{}'.format(self.SYS_PREFIX, self.CONVERGER_LABEL)
            sub_convs_labels = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.CONVERGER_LABEL, self.SUBSYS_SUFFIX, item)
                               for item in range(number_of_groups)]
            return sys_opt_label, sys_conv_label, sub_convs_labels
        elif mdao_architecture == self.OPTIONS_ARCHITECTURES[7]:  # CO
            assert number_of_groups is not None, \
                'number_of_groups should be specified for this architecture ({}).'.format(mdao_architecture)
            assert number_of_groups > 0, 'number_of_groups should be larger than 0.'
            sys_opt_label = '{}{}'.format(self.SYS_PREFIX, self.OPTIMIZER_LABEL)
            sub_opts_labels = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.OPTIMIZER_LABEL, self.SUBSYS_SUFFIX, item)
                               for item in range(number_of_groups)]
            return sys_opt_label, sub_opts_labels
        elif mdao_architecture == self.OPTIONS_ARCHITECTURES[8]:  # BLISS-2000
            assert number_of_groups is not None, \
                'number_of_groups should be specified for this architecture ({}).'.format(mdao_architecture)
            assert number_of_groups > 0, 'number_of_groups should be larger than 0.'
            sys_opt_label = '{}{}'.format(self.SYS_PREFIX, self.OPTIMIZER_LABEL)
            sys_conv_label = '{}{}'.format(self.SYS_PREFIX, self.CONVERGER_LABEL)
            sys_sms_labels = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.SM_LABEL, self.SUBSYS_SUFFIX, item)
                             for item in range(number_of_groups)]
            sub_does_labels = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.DOE_LABEL, self.SUBSYS_SUFFIX, item) for
                               item in range(number_of_groups)]
            sub_opts_labels = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.OPTIMIZER_LABEL, self.SUBSYS_SUFFIX, item)
                               for item in range(number_of_groups)]
            sub_convs_labels = ['{}{}{}{}'.format(self.SUBSYS_PREFIX, self.CONVERGER_LABEL, self.SUBSYS_SUFFIX, item)
                               for item in range(number_of_groups)]
            return sys_opt_label, sys_conv_label, sys_sms_labels, sub_does_labels, sub_opts_labels, sub_convs_labels

    def add_objective_function_by_nodes(self, *args, **kwargs):
        """This function adds objective functions to the graph using lists of variable nodes.

        :param args: list of nodes (list elements must be strings)
        :type args: list
        :param kwargs: list of nodes (list elements must be strings)
        :type kwargs: list
        :return: list of Objective Functions added to Graph
        :rtype: list

        Each list produces a separate objective function node in the graph. If the list if passed as a keyword argument,
        the keyword is taken as the name of the objective function node. Otherwise, a standard name will be given to the
        node. Each objective function node has one output variable, and takes the nodes given in the argument list as
        input nodes.

        If the provided nodes do not exist in the graph, a warning is given to the user on whether to continue the
        addition of the objective function to the graph using valid nodes.

        Example:

        >>> unnamed_function = list(>>list of graph nodes<<)
        >>> named_obj_fcn = list(>>list of graph nodes<<)
        >>> MyGraph.add_objective_function_by_nodes(unnamed_function, My_obj_fcn_name = named_obj_fcn)

        The added objective function nodes can be queried by the attribute:

        >>> Graph.nodes[node]["name"] == "Objective"
        """

        standard_func_name = "OBJECTIVE"
        obj_node = "f"

        # initiate objective function list of tuples (functionName, ListOfNodes)
        obj_fun_list = list()
        obj_funcs_added = list()

        # ensure that args are lists, add to obj_fun_list as tuples
        for arg in args:
            assert isinstance(arg, list)
            obj_fun_list.append(("", arg))

        # ensure that kwargs are lists, add to obj_fun_list as tuples
        for kwarg in kwargs:
            assert isinstance(kwargs[kwarg], list)
            obj_fun_list.append((kwarg, kwargs[kwarg]))

        # assert that all elements are strings
        for obj_fun_tpl in obj_fun_list:
            for elem in obj_fun_tpl[1]:
                assert isinstance(elem, string_types)

        # loop
        for obj_fun_tpl in obj_fun_list:
            name_idx = 1
            obj_func_name = standard_func_name
            output_node = obj_node

            # check OBJ fun name, if not, add function
            if obj_fun_tpl[0]:  # if function name provided
                obj_func_name = obj_fun_tpl[0]
                name_indexed = False

                # check if name exists in graph, and if it does, add index
                while True:
                    if obj_func_name in self:
                        obj_func_name = "{}[{}]".format(obj_fun_tpl[0], name_idx)
                        name_idx += 1
                        name_indexed = True
                    else:
                        break  # return given (indexed) name

                # define output node
                output_node = "{}[{}]".format(obj_node, obj_func_name)

                # give warning to user, replace obj func name
                if name_indexed:
                    logger.warning("Node {} already exists in graph. Objective function is added to graph "
                                   "as {}.".format(obj_fun_tpl[0], obj_func_name))
                obj_fun_tpl = (obj_func_name, obj_fun_tpl[1])

            else:
                # check if standard name exists in graph, and if yes, add index; return only when name unique
                while True:
                    if obj_func_name in self or any(obj_func_name == tpl[0] for tpl in obj_fun_list):
                        obj_func_name = "{}[{}]".format(standard_func_name, name_idx)
                        output_node = "{}[{}]".format(obj_node, name_idx)
                        name_idx += 1
                    else:
                        break  # return standard (indexed) name

                # replace name in func list
                obj_fun_tpl = (obj_func_name, obj_fun_tpl[1])

            # loop over elements in list and check whether they exist in graph
            invalid_nodes = []
            for element in obj_fun_tpl[1]:

                # make sure node is in graph and in category "variable"
                if element not in self or not self.nodes[element]["category"] == "variable":
                    invalid_nodes.append(element)

            # remove invalid elements from list
            obj_fun_tpl = (obj_func_name, [elem for elem in obj_fun_tpl[1] if elem not in invalid_nodes])

            # if all provided elements invalid, continue with next obj function
            if not obj_fun_tpl[1]:
                logger.warning("No valid nodes were found for objective function '{}'; it is therefore not added to "
                               "graph.".format(obj_fun_tpl[0]))
                continue

            # if any invalid nodes found, inform user and ask if continue or not
            if invalid_nodes:

                # print invalid nodes
                user_prompt = "The following nodes either do not exist in graph, or are not variable nodes, and can " \
                              "therefore not be used for an objective function: "
                print(user_prompt)
                for node in invalid_nodes:
                    print(node)

                # ask if continue; if not, continue with next obj fcn
                ask_continue = "Would you like to continue adding objective function '{}' using the valid " \
                               "nodes?".format(obj_func_name)
                user_sel = prompting.user_prompt_yes_no(message=ask_continue)
                if not user_sel:
                    print("Objective function {} not added to graph.".format(obj_func_name))
                    continue

            # add function and output nodes to graph
            self.add_node(obj_fun_tpl[0],
                          shape='s',
                          category='function',
                          label=obj_func_name,
                          name="Objective",
                          level=None)
            self.add_node(output_node,
                          shape='o',
                          category='variable',
                          label=output_node,
                          level=None,
                          execution_time=1)

            # add edge tuples to graph
            edge_tpls = [(element, obj_fun_tpl[0]) for element in obj_fun_tpl[1]]
            edge_tpls.append((obj_fun_tpl[0], output_node))
            self.add_edges_from(edge_tpls, coupling_strength=1)

            obj_funcs_added.append(obj_func_name)

        logger.info("Objective function(s) [{}] added to graph.".format(', '.join(obj_funcs_added)))

        return obj_funcs_added

    def select_objectives_from_graph(self, *args):
        """This functions lets the user select one or more objective functions from the graph.

        :param args: objective functions to choose from
        :type args: str
        :return: list of objective functions
        :rtype: list

        .. note:: Only functions can be selected as objectives. If no arguments are provided, user is prompted to select
            an objective from all functions in graph.
        """

        # check if arguments provided
        func_nodes = []
        for arg in args:
            assert self.node_is_function(arg), "Provided node must be function."
            func_nodes.append(arg)

        # if no objectives, get list of functions in graph
        if not func_nodes:
            for node in self.nodes:
                if self.node_is_function(node):
                    func_nodes.append(node)

        # get number of input/output nodes, store in selection list
        sel_list = []
        for func in func_nodes:
            indeg = self.in_degree(func)
            outdeg = self.out_degree(func)
            couplings = self.get_number_of_couplings(func)
            sel_list.append([indeg, outdeg, couplings, func])

        # sort list according to # of outputs
        sel_list.sort(key=lambda x: x[1])

        # prompt user to select objective
        msg = "The following function nodes were found in graph:"
        printing.print_in_table(sel_list, headers=["Inputs", "Outputs", "Couplings", "Function"], message=msg,
                                print_indeces=True)
        selmsg = "Please select objective(s):"
        indx_list = range(len(sel_list))
        sel = prompting.user_prompt_select_options(*indx_list, message=selmsg, allow_multi=True, allow_empty=False)
        # sel = [3]
        #  TODO: Add DEMO

        # get objectives
        objs = [sel_list[idx][-1] for idx in sel]

        return objs

    def node_is_objective_function(self, node):
        """This function checks whether the provided node is a objective function.

        :param node: graph node to be tested
        :type node: str
        :return: check result
        :rtype: bool

        This function checks whether the provided node:
            1. exists in graph
            2. has name-attribute "Objective"
            3. has an out-degree of 1
            4. has an outgoing node with an out-degree of zero

        .. note:: Only if all checks are satisfied, is the node a valid objective function node.
        """
        # TODO: This may not be a good approach (see condition 4 above)

        if self.node_is_function(node):
            if node in self:
                name_check = self.nodes[node]['name'] == 'Objective'  # TODO: Fix this
                out_deg_check = self.out_degree(node) == 1
                try:
                    out_node = list(self.out_edges(node))[0][1]
                    out_node_check = self.out_degree(out_node) == 0
                except IndexError:
                    out_node_check = False

                if name_check and out_deg_check and out_node_check:
                    return True

        return False

    def merge_function_nodes_based_on_modes(self, merge_funcs=None):
        """This class method merges all execution modes of the same function into a single node.

        :param merge_funcs: List of tuple of functions to merge. If empty (default), all functions are merged.
        :type merge_funcs: list, tuple
        :return: merged graph

        Mainly used for illustration purposes since information on the execution modes gets lost. Functions must be
        present in graph.
        """

        # TODO: What if empty list is given?

        if merge_funcs is not None:
            assert isinstance(merge_funcs, (tuple, list))

        m_graph = KadmosGraph(self)
        func_nodes = {}

        # get function nodes and corresponding data, add to dict
        for node, data in m_graph.nodes(data=True):
            if data["category"] == "function":
                func_nodes[node] = data

        # make sure that the provided function names are present in graph
        func_names = set([func_nodes[f]["name"] for f in func_nodes])
        if any(merge_funcs):
            for func in merge_funcs:
                assert func in func_names, "The provided function '{}' to be merged could not be found in the used " \
                                           "graph.".format(func)
        else:
            merge_funcs = list(func_names)

        # add "super"-function to graph by merging function modes into new "super"-node
        for super_func in merge_funcs:

            if super_func in m_graph:  # check if that "super"-function already exists
                func_node = m_graph.nodes.get(super_func)
                func_keys = [k for k in func_node]
                for key in func_keys:
                    if key in ["mode", "runtime", "precision", "fidelity"]:
                        func_node.pop(key, None)

            else:  # make attributes uniform (no mode-info available when modes are merged!)
                m_graph.add_node(super_func,
                                 shape='s',
                                 category='function',
                                 label=super_func,
                                 level=None,
                                 name=super_func)

                # merge modes into "super"-function
                for merge_node in func_nodes:
                    if func_nodes[merge_node]['name'] == super_func:
                        m_graph = nx.contracted_nodes(m_graph, super_func, merge_node, self_loops=True)

        return m_graph

    def add_instance(self, node, instance=None):
        """Method to change the instance of a node

        :param node: node to change the instance of
        :type node: str
        :param instance: new instance, optional (default=None)
        :type instance: int

        In case the default is used the instance added is the highest current instance + 1.
        """

        assert 'instance' in self.nodes[node], 'Node {} misses attribute "instance".'.format(node)
        node_instance = self.nodes[node]['instance']
        if instance is None:
            highest_instance = self.get_highest_instance(node)
            new_instance = highest_instance+1
        else:
            new_instance = instance
        if int(node_instance) > 1:
            original_node = node[:-len(self.INSTANCE_SUFFIX + str(node_instance))]
        else:
            original_node = node

        node_data_dict = copy.deepcopy(self.nodes[node])
        cleaned_data_dict = copy.deepcopy(node_data_dict)
        del cleaned_data_dict['instance']

        # Determine the related schema node
        if 'related_to_schema_node' in node_data_dict:
            related_schema_node = node_data_dict['related_to_schema_node']
            del cleaned_data_dict['related_to_schema_node']
        else:
            related_schema_node = node

        self.copy_node_with_suffix(original_node, self.INSTANCE_SUFFIX + str(new_instance),
                                   '^{i' + str(new_instance) + '}',
                                   instance=new_instance, related_to_schema_node=related_schema_node,
                                   attr_dict=cleaned_data_dict)
        return '{}{}{}'.format(original_node, self.INSTANCE_SUFFIX, new_instance)

    def add_function_instance(self, node, serves, instance=None):
        """Method to change the instance of a node

        :param node: node to change the instance of
        :type node: str
        :param serves: list of nodes for which the new instances should provide inputs
        :type serves: list
        :param instance: new instance, optional (default=None)
        :type instance: int

        In case the default is used the instance added is the highest current instance + 1.
        """

        assert 'instance' in self.nodes[node], 'Node {} misses attribute "instance".'.format(node)
        node_instance = self.nodes[node]['instance']
        if instance is None:
            highest_instance = self.get_highest_instance(node)
            new_instance = highest_instance+1
        else:
            new_instance = instance
        if int(node_instance) > 1:
            original_node = node[:-len(self.INSTANCE_SUFFIX + str(node_instance))]
        else:
            original_node = node

        node_data_dict = dict(self.nodes[node])
        del node_data_dict['instance']
        del node_data_dict['label']

        new_node = self.copy_node_with_suffix(original_node, self.INSTANCE_SUFFIX + str(new_instance),
                                              '^{i' + str(new_instance) + '}',
                                              instance=new_instance, attr_dict=node_data_dict)

        # Connect inputs of original function also to new instance
        for input in self.get_sources(node):
            self.copy_edge((input, node), (input, new_node))

        # Reconnect edges based on the served nodes
        output_mapping = dict()
        for output in self.get_targets(node):
            for fun in serves:
                if output in self.get_sources(fun):
                    if output not in output_mapping:
                        output_mapping[output] = [fun]
                    else:
                        output_mapping[output].append(fun)

        for output, funs in output_mapping.items():
            new_output = self.add_instance(output)
            for fun in funs:
                self.copy_edge((node, output), (new_node, new_output))
                self.copy_edge((output, fun), (new_output, fun))
                self.remove_edge(output, fun)

        return new_node

    def copy_edge(self, old_edge, new_edge):
        """Method to copy an edge so that attributes of the old edge are maintained.

        :param old_edge: edge to be copied
        :type old_edge: tuple
        :param new_edge: edge to be created
        :type new_edge: tuple
        :return: created edge
        :rtype: tuple
        """
        assert self.has_edge(old_edge[0], old_edge[1]), 'Edge {} does not exist in the graph.'.format(old_edge)
        attrb_old_edge = dict(self.adj[old_edge[0]][old_edge[1]])
        self.add_edge(new_edge[0], new_edge[1])
        for key in attrb_old_edge:
            self.adj[new_edge[0]][new_edge[1]][key] = attrb_old_edge[key]
        return new_edge

    def copy_node_with_suffix(self, node, suffix, label_extension, attr_dict=None, **kwargs):
        """Method to simply copy a node and its attributes by creating a new node with a suffix.

        :param node: node to be copied
        :type node: str
        :param suffix: suffix to be added to the node ID
        :type suffix: str
        :param label_extension: extension for labels
        :type label_extension: str
        :param kwargs: keyword arguments will be added as node attributes
        :type kwargs: dict, int
        :return: new node and enriched graph
        :rtype: str
        """

        assert self.has_node(node), 'Node %s is not present in the graph.' % node
        assert isinstance(suffix, string_types)
        assert len(suffix) > 0, 'Suffix string should be larger than zero length.'

        new_node = node + suffix
        node_data_dict = copy.deepcopy(self.nodes[node])

        # determine the related schema node
        if 'related_to_schema_node' in self.nodes[node]:
            related_schema_node = self.nodes[node]['related_to_schema_node']
        else:
            related_schema_node = node

        # add the node
        if not self.has_node(new_node):
            self.add_node(new_node,
                          category=node_data_dict['category'],
                          related_to_schema_node=related_schema_node,
                          label=get_correctly_extended_latex_label(node_data_dict['label'], label_extension),
                          attr_dict=attr_dict)
        if 'architecture_role' in node_data_dict:
            self.nodes[new_node]['architecture_role'] = node_data_dict['architecture_role']
        if kwargs:
            for key, item in iteritems(kwargs):
                if key != 'related_to_schema_node':
                    self.nodes[new_node][key] = item

        return new_node

    def relabel_function_nodes(self, mapping=None):
        """Method to relabel all function nodes so that they meet the minimum CMDOWS convention

        :param mapping: application of mapping required, optional (default=None)
        :type mapping: None, bool
        :returns: relabeled graph

        CMDOWS convention:

        * Minimum information: ID
        * Maximum information: ID[modeID][instanceID][version]

        .. note:: modeID, instanceID and version are only provided if there is a function with the same ID that requires
            this specification to differentiate between the functions.

        Example:

        Design competences (full information):

        #. Aerodynamics[A][1][v1]
        #. Aerodynamics[A][2][v1]
        #. Aerodynamics[B][1][v1]
        #. Structures[A][1][v1]
        #. Structures[A}[1][v2]
        #. Propulsion[A][1][v2]

        Design competences relabeled:

        #. Aerodynamics[A][1]
        #. Aerodynamics[A][2]
        #. Aerodynamics[B][1]
        #. Structure[v1]
        #. Structure[v2]
        #. Propulsion
        """

        # Determine nodes to be renamed
        executable_blocks = self.find_all_fnodes(attr_exclude=['architecture_role',
                                                               self.CMDOWS_ARCHITECTURE_ROLE_SPLITTER])
        design_competences = set(executable_blocks).difference(self._get_equation_nodes())

        # Make the mapping
        if mapping is None:
            mapping = {}
            labels = []
            ids = []
            modes = []
            instances = []
            versions = []
            ids_set = set()
            multiples = set()
            ids_dict = {}
            des_comps = []

            for design_competence in design_competences:
                id = self.nodes[design_competence].get('name', design_competence)
                mode = self.nodes[design_competence].get('mode', 'main')
                instance = str(self.nodes[design_competence].get('instance', 0))
                version = self.nodes[design_competence].get('version', '1.0')
                mapping[design_competence] = '{}[{}][{}][{}]'.format(id, mode, instance, version)
                des_comps.append(design_competence)
                labels.append([id])
                ids.append(id)
                modes.append(mode)
                instances.append(instance)
                versions.append(version)
                ids_set.add(id)

            # check if there are IDs that are used multiple times
            if len(ids_set) < len(ids):
                # create a dictionary with index locations of all design competences
                for i in range(len(ids)):
                    if ids[i] in ids_dict:
                        if isinstance(ids_dict[ids[i]], int):
                            ids_dict[ids[i]] = [ids_dict[ids[i]], i]
                        else:
                            update = []
                            for index in ids_dict[ids[i]]:
                                update.append(index)
                            update.append(i)
                            ids_dict[ids[i]] = update
                        multiples.add(ids[i])
                    else:
                        ids_dict[ids[i]] = i
                # for the IDs that are used multiple times determine if there is a difference in mode/instance/version
                for multiple in multiples:
                    indices = ids_dict[multiple]
                    modes_set = set()
                    instances_set = set()
                    versions_set = set()
                    for index in indices:
                        modes_set.add(modes[index])
                        instances_set.add(instances[index])
                        versions_set.add(versions[index])
                    for index in indices:
                        if len(modes_set) > 1:
                            labels[index].append(modes[index])
                        if len(instances_set) > 1:
                            labels[index].append(instances[index])
                        if len(versions_set) > 1:
                            labels[index].append(versions[index])

            # create mapping using the correct labeling
            for i in range(len(des_comps)):
                label = labels[i][0]
                for j in range(1, len(labels[i])):
                    label += '['+labels[i][j]+']'
                mapping[des_comps[i]] = label

        # Do the relabeling
        nx.relabel_nodes(self, mapping, copy=False)

        # Do more relabeling
        if 'problem_formulation' in self.graph:
            if 'mg_function_ordering' in self.graph:
                for group in self.graph['mg_function_ordering']:
                    self.graph['mg_function_ordering'][group] = translate_list(self.graph['mg_function_ordering']
                                                                               [group], mapping)
            if 'function_order' in self.graph['problem_formulation']:
                 self.graph['problem_formulation']['function_order'] = \
                     translate_list(self.graph['problem_formulation']['function_order'], mapping)
            if 'function_ordering' in self.graph['problem_formulation']:
                for group in self.graph['problem_formulation']['function_ordering']:
                    self.graph['problem_formulation']['function_ordering'][group] = \
                        translate_list(self.graph['problem_formulation']['function_ordering'][group], mapping)

        return mapping

    def remove_function_nodes(self, *args):
        """Function that removes a function node

        :param args: function node id(s)
        :type args: str, list
        :return: graph with nodes removed
        :rtype: KadmosGraph

        .. attention:: Also the input and output variables that only have links to this specific function node are
            deleted. A simple remove_node of a function node might lead to unconnected variables in the graph.
        """

        # Input assertions
        if len(args) == 1 and isinstance(args[0], list):
            args = args[0]
        for arg in args:
            assert isinstance(arg, string_types), 'Argument %s is not of type str.' % arg
            assert self.has_node(arg), 'Node "' + str(arg) + '" is not present in the graph.'
            assert self.node_is_function(arg), \
                'Node "' + str(arg) + '" is not of category function (but ' + self.nodes[arg]['category'] + ').'

        # Remove functions including input and output variables (if allowed)
        for node in args:
            # Determine outgoing edges of the function and remove possible edges and nodes
            for out_edge in copy.deepcopy(self.out_edges(node)):
                self.remove_edge(out_edge[0], out_edge[1])
                # Check if variable has been set free
                if self.in_degree(out_edge[1]) == 0 and self.out_degree(out_edge[1]) == 0:
                    self.remove_node(out_edge[1])
            # Determine incoming edges of the function and remove possible edges and nodes
            for in_edge in copy.deepcopy(self.in_edges(node)):
                self.remove_edge(in_edge[0], in_edge[1])
                # Check if variable has been set free
                if self.in_degree(in_edge[0]) == 0 and self.out_degree(in_edge[0]) == 0:
                    self.remove_node(in_edge[0])
            # Finally, remove the function node itself
            self.remove_node(node)
            # Remove the function node also from the function order
            if 'problem_formulation' in self.graph:
                if 'function_order' in self.graph['problem_formulation']:
                    if node in self.graph['problem_formulation']['function_order']:
                        self.graph['problem_formulation']['function_order'].remove(node)

    def merge_parallel_functions(self, *args, **kwargs):
        """Function to merge a list of functions

        :param args: functions to be merged
        :type args: node_ids
        :param kwargs: new_label to specify new node label manually (optional)
        :type kwargs: dict
        :return: graph with merged functions
        :rtype: KadmosGraph
        """

        # Handle the fact that the *args could also be a list or tuple directly
        if len(args) == 1 and (isinstance(args[0], tuple) or isinstance(args[0], list)):
            args = list(args[0])

        # Input assertions
        assert len(args) > 1, 'More than 1 input argument is required.'
        for arg in args:
            assert isinstance(arg, string_types)

        # Get subgraph of functions and their (variable) neighbours
        subgraph = self.get_subgraph_by_function_nodes(args)

        # Check whether the functions are really parallel
        coupling_nodes = subgraph.find_all_nodes(subcategory='all couplings')
        collided_nodes = subgraph.find_all_nodes(subcategory='all collisions')

        if not coupling_nodes and not collided_nodes:
            # Check or create new node label
            if 'new_label' in kwargs:
                assert isinstance(kwargs['new_label'], string_types)
                new_label = kwargs['new_label']
            else:
                new_label = '-'.join(args) + '--par'

            # Make clean copy of the graph
            new_graph = self.deepcopy()
            graph_class = self.__class__

            # Add new node to graph
            assert not new_graph.has_node(new_label), 'New node label not allowed. Node already present in the graph.'
            new_graph.add_node(new_label, category='function', shape='s', level=None, label=new_label, name=new_label,
                               description='Merged function of parallel functions "' + ','.join(args) + '".',
                               subgraph=subgraph)
            for function_id in args:
                new_graph = nx.contracted_nodes(new_graph, new_label, function_id)
            new_graph = graph_class(new_graph)
            return new_graph
        else:
            if coupling_nodes and collided_nodes:
                raise AssertionError('The subgraph contains coupling nodes %s and collided nodes %s.'
                                     % (coupling_nodes, collided_nodes))
            elif coupling_nodes:
                raise AssertionError('The subgraph contains coupling nodes %s.' % coupling_nodes)
            elif collided_nodes:
                raise AssertionError('The subgraph contains collided nodes %s.' % collided_nodes)

    def merge_functions(self, *args, **kwargs):
        """Function to merge a collection of functions.

        :param args: functions to be merged
        :type args: node_ids
        :param kwargs: new_label to specify new node label manually (optional)
        :type kwargs: dict
        :return: graph with merged function
        :rtype: KadmosGraph
        """

        # Handle the fact that the *args could also be a list or tuple directly
        if len(args) == 1 and isinstance(args[0], (tuple, list, set)):
            args = list(args[0])

        # Input assertions
        for arg in args:
            assert isinstance(arg, string_types)

        # Get subgraph of functions and their (variable) neighbours
        subgraph = self.get_subgraph_by_function_nodes(args)

        # Check or create new node label
        if 'new_label' in kwargs:
            assert isinstance(kwargs['new_label'], string_types)
            new_label = kwargs['new_label']
        else:
            new_label = '-'.join(args) + '--merged'

        # Make clean copy of the graph
        new_graph = self.deepcopy()
        graph_class = self.__class__

        # Add new node to graph
        assert not new_graph.has_node(new_label), 'New node label not allowed. Node already present in the graph.'
        new_graph.add_fnode(new_label, label=new_label, name=new_label,
                            description='Merged function of functions "' + ','.join(args) + '".',
                            subgraph=subgraph, merge_info={'merge_type': 'generic', 'merge_order': list(args)})
        for function_id in args:
            new_graph = nx.contracted_nodes(new_graph, new_label, function_id)
        # For any coupling nodes in the subgraph, remove the incoming edge to the merged node
        new_graph = graph_class(new_graph)

        # Remove a potential cyclic edge on new node
        if new_graph.has_edge(new_label, new_label):
            new_graph.remove_edge(new_label, new_label)

        return new_graph

    def merge_sequential_functions(self, *args, **kwargs):
        """Function to merge a collection of functions.

        :param args: functions to be merged in the given sequence
        :type args: node_ids
        :param kwargs: new_label to specify new node label manually (optional)
        :type kwargs: str
        :return: graph with merged functions
        :rtype: KadmosGraph

        .. attention:: It is assumed that the merged functions are actually executed in the sequence in which they are
            given to this function.
        """

        # Handle the fact that the *args could also be a list or tuple directly
        if len(args) == 1 and (isinstance(args[0], tuple) or isinstance(args[0], list)):
            args = list(args[0])

        # Input assertions
        assert len(args) > 1, 'More than 1 input is required for this function.'
        for arg in args:
            assert isinstance(arg, string_types)

        # Get subgraph of functions and their (variable) neighbours
        subgraph = self.get_subgraph_by_function_nodes(args)

        # Check whether the sequence of functions is valid and whether the subgraph is unproblematic
        feedback_coupling = subgraph.check_for_coupling(function_order=args, only_feedback=True)
        collided_nodes_subgraph = subgraph.find_all_nodes(subcategory='all collisions')

        # Check that any coupling nodes in the subgraph are not collided (so not also determined by something else),
        # then these coupling nodes are only outputs of the merged graph.
        all_coupling_nodes = subgraph.find_all_nodes(subcategory='coupling') + \
            subgraph.find_all_nodes(subcategory='shared coupling')
        collided_coupling_nodes = False
        for coupling_node in all_coupling_nodes:
            if self.in_degree(coupling_node) > 1:
                collided_coupling_node = coupling_node
                collided_coupling_nodes = True
                break

        if not feedback_coupling and not collided_nodes_subgraph and not collided_coupling_nodes:
            # Check or create new node label
            if 'new_label' in kwargs:
                assert isinstance(kwargs['new_label'], string_types)
                new_label = kwargs['new_label']
            else:
                new_label = '-'.join(args)

            # Make clean copy of the graph
            new_graph = self.deepcopy()
            graph_class = self.__class__

            # Add new node to graph
            assert not new_graph.has_node(new_label), 'New node label not allowed. Node already present in the graph.'
            new_graph.add_fnode(new_label, level=None, label=new_label, name=new_label,
                               description='Merged function of sequential functions "' + ','.join(args) + '".',
                               subgraph=subgraph, merge_info={'merge_type': 'sequential', 'merge_order': list(args)})
            for function_id in args:
                new_graph = nx.contracted_nodes(new_graph, new_label, function_id)
            # For any coupling nodes in the subgraph, remove the incoming edge to the merged node
            for coupling_node in all_coupling_nodes:
                new_graph.remove_edge(coupling_node, new_label)
                # If the couplings can be removed, then do so
                if 'remove_internal_couplings' in kwargs:
                    if kwargs['remove_internal_couplings']:
                        new_graph.remove_node(coupling_node)
            new_graph = graph_class(new_graph)
            return new_graph
        else:
            if feedback_coupling:
                raise AssertionError('The subgraph contains feedback coupling. This is not allowed for merging.')
            if collided_nodes_subgraph:
                raise AssertionError('The subgraph contains collided nodes. This is not allowed for merging.')
            if collided_coupling_nodes:
                # noinspection PyUnboundLocalVariable
                raise AssertionError('Coupling node in subgraph %s is still collided in full graph. '
                                     'Remove collision before merging.' % collided_coupling_node)

    def merge_function_modes(self, *args, **kwargs):
        """Function to contract certain modes of the same function.

        :param args: function (first arg) and then followed by modes to be contracted.
        :type args: str
        :param kwargs: new_label to specify new node label manually (optional)
        :type kwargs: dict or str
        :return: contracted graph
        :rtype: KadmosGraph
        """

        # Handle the fact that the *args could also be a list or tuple directly
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            args = args[0]

        # Input assertions
        assert len(args) > 1, 'At least two arguments are required for a function mode merge.'
        for arg in args:
            assert isinstance(arg, string_types)
        # Create function-mode strings and check them
        function_nodes = list()
        if 'ignore_function_id' in kwargs:
            assert isinstance(kwargs['ignore_function_id'], bool), 'ignore_function_id should be of type Boolean.'
            ignore_function_id = kwargs['ignore_function_id']
        else:
            ignore_function_id = False
        function_name_prev = None
        for idx, arg in enumerate(args):
            node_name = arg
            function_name = self.nodes[node_name]['name']
            function_nodes.append(node_name)
            self.assert_node_exists(node_name)
            self.assert_node_attribute_and_value(node_name, 'category', 'function')
            if not ignore_function_id:
                if function_name_prev is not None:
                    assert function_name == function_name_prev, 'Nodes {} and {} do not have the same function ' \
                                                                'names.'.format(node_name, node_name_prev)
                    function_name_prev = function_name
                    node_name_prev = node_name
                else:
                    function_name_prev = function_name
        # Check or create new node label
        if 'new_label' in kwargs:
            assert isinstance(kwargs['new_label'], string_types)
            new_label = kwargs['new_label']
        else:
            new_label = '{}-merged[{}modes]'.format(self.nodes[args[0]]['name'], str(len(args)))

        # Get the subgraph of function modes and neighbouring functions
        subgraph = self.get_subgraph_by_function_nodes(function_nodes)

        # Check if no collisions are present in the subgraph
        collided_nodes = subgraph.find_all_nodes(subcategory='all collisions')

        if not collided_nodes:
            # Make clean copy of the graphs
            new_graph = self.deepcopy()
            graph_class = self.__class__

            # Add new node to graph
            assert not new_graph.has_node(new_label), 'New node label not allowed. Node already present in the graph.'
            modes = [self.nodes[arg]['mode'] for arg in args]
            new_graph.add_node(new_label, category='function', level=None, label=new_label, name=function_name,
                               description='Contracted function of function "' + function_name + '" combining ' +
                                           str(len(modes)) + ' modes (' + ','.join(modes) + ')', mode=';'.join(modes),
                               subgraph=subgraph)
            for function_mode in function_nodes:
                new_graph = nx.contracted_nodes(new_graph, new_label, function_mode)
            new_graph = graph_class(new_graph)
            return new_graph
        else:
            raise AssertionError('The subgraph contains collided nodes %s.' % collided_nodes)

    # noinspection PyUnboundLocalVariable
    def split_variables(self, *args, **kwargs):
        """Method to split a problematic variable node into multiple separate valid nodes.

        :param args: problematic node in the graph
        :type args: str, list
        :param kwargs:
        :type kwargs:
        :return: graph with split variables
        :rtype: KadmosGraph

        The following variables are considered problematic and will be handled by this function:

        * pure circular coupling
        * shared circular coupling
        * collided coupling
        * collision
        * collided circular coupling
        * collided shared coupling
        * collided shared circular coupling

        The following table shows an example situation for each of the different problematic variables:

        +----------------------+------------------------+----------------+---------------------------------------+
        | PROBLEMATIC VARIABLE | SITUATION              | FUNCTION ORDER | RESOLVED AS                           |
        +======================+========================+================+=======================================+
        | pure circular        | x1 <=> F1              | n.a.           | x1/variableInstance1 => F1 =>         |
        | coupling             |                        |                | x1/variableInstance2                  |
        +----------------------+------------------------+----------------+---------------------------------------+
        | shared circular      | F1 <=> x1 => F2, F3    | n.a.           | x1/variableInstance1 => F1 =>         |
        | coupling             |                        |                |  x1/variableInstance2 => F2, F3, etc. |
        +----------------------+------------------------+----------------+---------------------------------------+
        | collided (shared)    | F1, F3 => x1 => F2, F4 | F1, F2, F3, F4 | F1 => x1/variableInstance1 => F2      |
        | coupling             |                        |                +---------------------------------------+
        |                      |                        |                | F3 => x1/variableInstance2 => F4      |
        +----------------------+------------------------+----------------+---------------------------------------+
        | collision            | F1, F2 => x1           | F1, F2         | F1 => x1/variableInstance1            |
        |                      |                        |                +---------------------------------------+
        |                      |                        |                | F2 => x1/variableInstance2            |
        +----------------------+------------------------+----------------+---------------------------------------+
        | collided circular    | F1 <=> x1 <= F2, F3    | n.a.           | x1/variableInstance1 => F1 =>         |
        | coupling             |                        |                | x1/variableInstance2                  |
        |                      |                        |                +---------------------------------------+
        |                      |                        |                | F2 => x1/variableInstance3            |
        |                      |                        |                +---------------------------------------+
        |                      |                        |                | F3 => x1/variableInstance4            |
        +----------------------+------------------------+----------------+---------------------------------------+
        | collided shared      | F3, F5 <=> x1 <= F2    | F1, F2, F3, F4,| x1/variableInstance1 => F2 => (..)    |
        | circular coupling    | x1 => F1, F4, F6       | F5, F6         +---------------------------------------+
        |                      |                        |                | x1/variableInstance2 => F1, F3 => (..)|
        |                      |                        |                +---------------------------------------+
        |                      |                        |                | x1/variableInstance3 => F4, F5 => (..)|
        |                      |                        |                +---------------------------------------+
        |                      |                        |                | x1/variableInstance4 => F6            |
        +----------------------+------------------------+----------------+---------------------------------------+

        """
        #TODO Imco add kwargs documentation

        # Input assertions
        if len(args) == 0:
            raise IOError('At least one input argument is required.')
        if len(args) == 1:
            assert isinstance(args[0], string_types) or isinstance(args[0], list)
            if isinstance(args[0], string_types):
                nodes = [args[0]]
            elif isinstance(args[0], list):
                nodes = args[0]
        if len(args) > 1:
            nodes = []
            for arg in args:
                assert isinstance(arg, string_types)
                nodes.append(arg)

        logger.info('Splitting problematic variables...')

        # Get relevant categories
        relevant_node_subcats = self.NODE_GROUP_SUBCATS['all splittable variables']
        function_order_required_cats = relevant_node_subcats[2:7]

        # Loop through the provided nodes
        for idx, node in enumerate(nodes):

            # Get subcat
            subcat = self.get_node_subcategory(node)

            # Check subcategory
            assert subcat in relevant_node_subcats, 'Node %s is not a problematic variable.' % node

            # Get functions for which the node is also output (except the circular function)
            source_funcs = self.get_sources(node)

            # Get functions for which the node is an input
            target_funcs = self.get_targets(node)

            # Get function order
            if 'function_order' in kwargs:
                function_order = kwargs['function_order']
            elif subcat in function_order_required_cats:
                assert 'function_order' in self.graph['problem_formulation'], \
                    'Function order should be formulated in order to split this problematic node.'
                function_order = self.graph['problem_formulation']['function_order']
            else:
                new_targets = list(target_funcs)
                new_targets.remove(source_funcs[0])
                function_order = source_funcs + new_targets

            # Assert that the function order given matches with the sources and targets
            assert set(source_funcs).issubset(function_order), \
                'Some node sources {} are missing in the function order {}.'.format(source_funcs, function_order)
            assert set(target_funcs).issubset(function_order), \
                'Some node targets {} are missing in the function order {}.'.format(target_funcs, function_order)

            # Create a temporary new node with instance 1
            idx = 1
            new_node = self.copy_node_with_suffix(node, self.INSTANCE_SUFFIX + str(idx), '^{vi' + str(idx) + '}',
                                                  instance=idx, related_to_schema_node=node)
            for func in function_order:
                if func in target_funcs:
                    self.copy_edge((node, func), (new_node, func))
                    self.remove_edge(node, func)
                if func in source_funcs:
                    if idx == 1 and func not in target_funcs:
                        idx += 1
                    else:
                        if idx == 1:
                            idx += 1
                        new_node = self.copy_node_with_suffix(node, '__i'+str(idx), '^{vi'+str(idx)+'}',
                                                              instance=idx, related_to_schema_node=node)
                        idx += 1
                    self.copy_edge((func, node), (func, new_node))
                    self.remove_edge(func, node)

            # Remove the original node
            assert self.in_degree(node) == 0 and self.out_degree(node) == 0, \
                'Problematic node is still connected somehow.'
            self.remove_node(node)

            # Relabel node with instance=0
            # TODO: This should be done more elegantly
            nx.relabel_nodes(self, {node + self.INSTANCE_SUFFIX + str(1): node}, copy=False)

        # Log some info about the splitted nodes
        log_max_nodes = 20
        log_nodes = log_max_nodes if len(nodes) >= log_max_nodes else len(nodes)
        logger.info('Successfully splitted ' + str(len(nodes)) + ' problematic variables.')
        if nodes:
            logger.info('The first ' + str(log_nodes) + ' splitted problematic variables are: ' +
                        (', '.join(nodes[0:log_nodes])))

        return

    def make_all_variables_valid(self):
        """Method to analyze all variables in a graph and make any problematic variables valid.

        :return: graph with problematic variables removed.

        Problematic variable are holes and splittables. Splittable variables are split and holes will simply be removed.
        """

        # First fix the splittable variables
        splittables = self.find_all_nodes(subcategory='all splittable variables')
        if splittables:
            self.split_variables(splittables)

        # Then find hole variables and remove them
        holes = self.find_all_nodes(category='variable', subcategory='hole')
        if holes:
            logger.info('Removing hole nodes...')
            self.remove_nodes_from(holes)
            logger.info('Successfully removed ' + str(len(holes)) + ' hole nodes.')
            logger.info('The removed hole nodes were: ' + (', '.join(holes)))

        return

    def disconnect_problematic_variables_from(self, function, disconnect_collided_targets=True,
                                              disconnect_shared_sources=True, ignore_list=[]):
        """Method to automatically disconnect certain problematic variables with respect to a given function.

        :param function: function around which problematic variables are disconnected
        :type function: str
        :param disconnect_collided_targets: setting to disconnect collided targets
        :type disconnect_collided_targets: bool
        :param disconnect_shared_sources: setting to disconnect shared sources
        :type disconnect_shared_sources: bool
        :param ignore_list: setting to ignore certain nodes
        :type ignore_list: list

        If given as setting (disconnect_collided_targets=True) then the collided targets will be disconnected from this
        function. Also, if given as setting (disconnect_shared_sources=True), shared sources are also disconnected.
        """

        # Input assertions
        assert self.has_node(function), 'Node {} not present in the graph.'.format(function)
        assert self.nodes[function]['category'] == 'function', \
            'Node {} should be of category function.'.format(function)
        assert isinstance(disconnect_collided_targets, bool)
        assert isinstance(disconnect_shared_sources, bool)
        assert isinstance(ignore_list, list)

        # Get all target variables of the function
        target_nodes = self.get_targets(function) if disconnect_collided_targets else []
        source_nodes = self.get_sources(function) if disconnect_shared_sources else []

        # Clean up target and source nodes by running ignore list
        for item in ignore_list:
            if item in target_nodes:
                target_nodes.remove(item)
            if item in source_nodes:
                source_nodes.remove(item)

        # Add node subcategories
        self.get_nodes_subcategory()

        # Disconnect if required
        for target_node in target_nodes:
            if self.nodes[target_node]['subcategory'] in \
                    self.NODE_GROUP_SUBCATS['all problematic variables'][3:8]:  # all collided subcategories
                self.remove_edge(function, target_node)
        for source_node in source_nodes:
            if self.nodes[source_node]['subcategory'] in \
                    get_list_entries(self.NODE_GROUP_SUBCATS['all problematic variables'], 2, 6, 7):  # all shared
                #  subcategories
                self.remove_edge(source_node, function)

        return

    def check_for_coupling(self, function_order, only_feedback=False, raise_error_if_true=False):
        """Function to check for the presence of coupling in a graph for a list of analyses in a given analysis order.

        :param function_order: list with node names of functions
        :type function_order: list
        :param only_feedback: Boolean on whether to check for feedback coupling only (this is useful for Gauss-Seidel)
        :type only_feedback: bool
        :param raise_error_if_true: Boolean on whether to raise an error if coupling exists
        :type raise_error_if_true: bool
        :return: Boolean value on whether coupling exists
        :rtype: bool

        .. note:: only the functions in the function_order list are checked for feedback.
        """

        # Set coupling initially to False.
        coupling = False
        # Make cleancopy of function_order.
        function_order = list(function_order)
        for idx, analysis in enumerate(function_order):
            in_edges = self.in_edges(analysis)
            if only_feedback:
                analysis_checklist = function_order[idx + 1:]
            else:
                analysis_checklist = function_order
                analysis_checklist.remove(analysis)

            for edge in in_edges:
                # Determine the input variable of the analysis
                in_node = edge[0]
                if self.in_degree(in_node) > 0:
                    # Check if the node is coupled to a any critical analyses (forward and feedback, or feedback).
                    # Get all the functions that are coupled as incoming edges to the node.
                    coupled_functions = map((lambda x: x[0]), self.in_edges(in_node))
                    if set(coupled_functions).intersection(set(analysis_checklist)):
                        coupling = True
                        if raise_error_if_true:
                            raise AssertionError('Invalid coupling is present for variable %s.' % in_node)
                        break
                else:
                    continue
            if coupling:
                break

        return coupling

    def count_function_nodes(self):
        """This function counts the amount function nodes that are present in the graph.

        :return: amount of function nodes counted in graph
        :rtype: int
        """

        return len(self.find_all_nodes(category='function'))

    def find_all_nodes(self, category='all', subcategory='all', attr_cond=None, attr_include=None, attr_exclude=None,
                       xpath_include=None, xpath_exclude=None, print_in_log=False, print_attributes='all'):
        """Advanced search function to get nodes and their properties.

        :param category: category of the node (you can specify multiple in a list), see note for allowed values.
        :type category: str
        :param subcategory: subcategory of the node (you can specify multiple in a list), see note for allowed values.
        :type subcategory: str
        :param attr_cond: conditional on the node attribute value (e.g. ['execution time','>',200])
        :type attr_cond: list
        :param attr_include: attributes to exclusively include in search
        :type attr_include: list
        :param attr_exclude: attributes to exclude from search
        :type attr_exclude: list
        :param xpath_include: xpaths to exclusively include in search
        :type xpath_include: list
        :param xpath_exclude: xpaths to exclude from search
        :type xpath_exclude: list
        :param print_in_log: parameter to set printing in log on or off
        :type print_in_log: bool
        :param print_attributes: attributes that should be printed in the log
        :type print_attributes: str or list
        :return: list of all nodes that meet the search criteria
        :rtype: list

        .. note:: The following categories are allowed:

            * all
            * variable
            * variable group
            * function
            * architecture element
            * RCE component

        .. note:: The following subcategories are allowed:

            GROUPS:

            * all
            * all variables
            * all inputs
            * all outputs
            * all couplings
            * all circular variables
            * all PSG blocks
            * all iterative blocks
            * all design variables


            VARIABLES:

            * hole
            * supplied input
            * supplied shared input
            * output
            * collision
            * coupling
            * pure circular coupling
            * shared coupling
            * shared circular coupling
            * collided coupling
            * collided circular coupling
            * collided shared coupling
            * collided shared circular coupling


            FUNCTIONS:

            * independent
            * source
            * sink
            * complete


            ARCHITECTURE ELEMENTS:

            Action blocks:

            * optimizer
            * MDA
            * optimizer function
            * MDA analysis
            * independent output function


            Parameters:

            * initial guess design variable
            * final design variable
            * final output variable
            * MDA coupling variable
            * initial guess MDA coupling variable
            * final MDA coupling variable
            * consistency constraint variable


            RCE COMPONENTS:

            * Input Provider
            * XML Merger
            * XML PyMerger
            * CPACS Tool
            * Converger
            * Optimizer
            * Consistency constraint function

        Example usage:
        Just get all nodes of a graph in a list:

        >>> all_nodes = self.find_all_nodes()

        Get all input nodes in a list and print them in the log as well:

        >>> all_nodes = self.find_all_nodes(category='all', subcategory='all inputs', print_in_log=True)

        Get all input nodes with a certain attribute value:

        >>> all_nodes = self.find_all_nodes(category='all', subcategory='all inputs',
        >>>                                 attr_cond=['execution time', '>', 5], print_in_log=True)

        Get all nodes with any of the listed attribute values:

        >>> all_nodes = self.find_all_nodes(category='all', subcategory='all',
        >>>                                 attr_include=[['problem_role', ['constraint', 'objective']],
        >>>                                               ['instance', 0]])
        """
        # TODO: Update docstring

        # Assert inputs
        possible_categories = ['all'] + list(self.NODE_CAT_TREE)
        possible_subcategories = ['all'] + list(self.NODE_GROUP_SUBCATS) + \
                                 [item for sublist in
                                  [list(self.NODE_CAT_TREE[key]) for key in list(self.NODE_CAT_TREE)]
                                  for item in sublist]
        assert isinstance(self, type(nx.DiGraph()))
        assert isinstance(category, string_types)
        assert isinstance(subcategory, string_types)
        assert isinstance(attr_cond, type(None)) or isinstance(attr_cond, list)
        assert isinstance(attr_include, type(None)) or isinstance(attr_include, list)
        assert isinstance(attr_exclude, type(None)) or isinstance(attr_exclude, list)
        assert isinstance(xpath_include, type(None)) or isinstance(xpath_include, list)
        assert isinstance(xpath_exclude, type(None)) or isinstance(xpath_exclude, list)
        assert isinstance(print_in_log, bool)
        assert isinstance(print_attributes, string_types) or isinstance(print_attributes, list)
        if isinstance(attr_cond, type(None)):
            pass
        elif isinstance(attr_cond[0], string_types):
            assert len(attr_cond) == 3, "Attribute condition needs to be a list with three entries."
        else:
            assert isinstance(attr_cond[0][0], string_types), "Attribute condition can only handle one nesting level."
            for attr in attr_cond:
                assert len(attr) == 3, "Attribute conditions need to be nested lists with three entries."
        if isinstance(attr_include, type(None)):
            pass
        elif isinstance(attr_include[0], string_types):
            assert len(attr_include) == 2, "Attribute included needs to be a list with the attribute" \
                                             " and (a list of) the desired value(s)."
        else:
            assert isinstance(attr_include[0][0], string_types), "Attributes included can only handle one nesting level."
            for attr in attr_include:
                assert len(attr) == 2, "Attributes included need to be nested lists with the attribute and " \
                                       "(a list of) desired value(s)."
        if isinstance(attr_exclude, type(None)):
            pass
        elif isinstance(attr_exclude[0], string_types):
            assert len(attr_exclude) == 2, "Attribute excluded needs to be a list with the attribute" \
                                             " and (a list of) the desired value(s)."
        else:
            assert isinstance(attr_exclude[0][0], string_types), "Attributes excluded can only handle one nesting level."
            for attr in attr_exclude:
                assert len(attr) == 2, "Attributes excluded need to be nested lists with the attribute" \
                                       " and (a list of) desired value(s)."
        assert len({category}.intersection(possible_categories)) != 0, \
            "Specified category '%s' does not exist. Please choose from %s." % (category, str(possible_categories))
        assert len({subcategory}.intersection(possible_subcategories)) != 0, \
            "Specified subcategory '%s' does not exist. Please choose from %s." % (subcategory,
                                                                                   str(possible_subcategories))

        # Categorize nodes
        cat_nodes = self.get_categorized_nodes(print_in_log=False)
        all_nodes = list()

        if print_in_log:
            print('')
            print('\n- - - - - - - -')
            print('   NODE SEARCH   ')
            print('- - - - - - - -\n')
            print('category: ' + str(category))
            print('subcategory: ' + str(subcategory))
            print('attribute condition: ' + str(attr_cond))
            print('print_attributes: ' + str(print_attributes))
            print('- - - - - - - -\n')

        # Handle special subcategories
        if subcategory in list(self.NODE_GROUP_SUBCATS):
            subcategory = self.NODE_GROUP_SUBCATS[subcategory]

        if not isinstance(category, list) and category != 'all':
            category = [category]

        if not isinstance(subcategory, list) and subcategory != 'all':
            subcategory = [subcategory]

        for key1 in cat_nodes:
            # check if current key is in the category (list) given
            if {key1}.intersection(set(category)) or category == 'all':
                if print_in_log:
                    print('category: ' + key1 + '\n')
                for key2 in cat_nodes[key1]:
                    # check if current key is in the subcategory (list) given
                    if {key2}.intersection(set(subcategory)) or subcategory == 'all':
                        if print_in_log:
                            print('    subcategory: ' + key2 + '\n')
                        if len(cat_nodes[key1][key2]) == 0:
                            if print_in_log:
                                print('        no nodes present in this subcategory')
                        else:
                            for item in cat_nodes[key1][key2]:
                                # Determine if the node has a valid attribute value to be added
                                if attr_cond is None:
                                    eval_node = True
                                elif isinstance(attr_cond[0], string_types):
                                    if attr_cond[0] in self.nodes[item]:
                                        if test_attr_cond(self.nodes[item][attr_cond[0]], attr_cond[1], attr_cond[2]):
                                            eval_node = True
                                        else:
                                            eval_node = False
                                    else:
                                        eval_node = False
                                else:
                                    eval_node = True
                                    for attr in attr_cond:
                                        if attr[0] in self.nodes[item]:
                                            if test_attr_cond(self.nodes[item][attr[0]], attr[1], attr[2]) and \
                                                    eval_node:
                                                eval_node = True
                                            else:
                                                eval_node = False
                                        else:
                                            eval_node = False
                                # noinspection PyUnboundLocalVariable
                                if eval_node:
                                    if print_in_log:
                                        print('        node: ' + str(item))
                                        self.get_node_attributes(item, print_attributes, print_in_log=print_in_log)
                                        print('')
                                    all_nodes.append(item)
                        if print_in_log:
                            print('')

        # include all nodes (from selection) that have any of the specified attributes.
        if attr_include:
            filtered = set()
            if isinstance(attr_include, type(None)):
                pass
            elif isinstance(attr_include[0], string_types):
                for node in all_nodes:
                    if self.nodes[node].get(attr_include[0]):
                        if self.nodes[node][attr_include[0]] in attr_include[1]:
                            filtered.add(node)
            else:
                for attr in attr_include:
                    for node in all_nodes:
                        if self.nodes[node].get(attr[0]):
                            if self.nodes[node][attr[0]] in attr[1]:
                                filtered.add(node)
            filtered = list(filtered)
            all_nodes = filtered

        # include all nodes (from selection) that have none of the specified attributes.
        if attr_exclude:
            filtered = list()
            if isinstance(attr_exclude, type(None)):
                pass
            elif isinstance(attr_exclude[0], string_types):
                for node in all_nodes:
                    choice = True
                    if self.nodes[node].get(attr_exclude[0]):
                        if self.nodes[node][attr_exclude[0]] in attr_exclude[1]:
                            choice = False
                    if choice:
                        filtered.append(node)
            else:
                for attr in attr_exclude:
                    for node in all_nodes:
                        choice = True
                        if self.nodes[node].get(attr[0]):
                            if self.nodes[node][attr[0]] in attr[1]:
                                choice = False
                        if choice:
                            filtered.append(node)
            all_nodes = filtered

        if xpath_include:
            filtered = list()
            for xpath in xpath_include:
                path = xpath.split('/')
                for node in all_nodes:
                    node_path = self.nodes[node]['name'].split('/')
                    for el in range(len(path)):
                        choice = False
                        if node_path[el] == path[el]:
                            choice = True
                        if not choice:
                            break
                    if choice:
                        filtered.append(node)
            all_nodes = filtered

        if xpath_exclude:
            filtered = list()
            for xpath in xpath_exclude:
                path = xpath.split('/')
                for node in all_nodes:
                    node_path = self.nodes[node]['name'].split('/')
                    for el in range(len(path)):
                        choice = True
                        if node_path[el] == path[el]:
                            choice = False
                        if choice:
                            break
                    if choice:
                        filtered.append(node)
            all_nodes = filtered

        return all_nodes

    def find_all_fnodes(self, **kwargs):
        return self.find_all_nodes(category='function', **kwargs)

    def find_all_vnodes(self, **kwargs):
        return self.find_all_nodes(category='variable', **kwargs)

    def add_default_name(self):
        """Method to add a default name attribute to a graph

        :return: graph with default attribute name
        :rtype: KadmosGraph
        """

        self.graph['name'] = str(type(self))[8:-2]

    def add_default_description(self):
        """Method to add a default description attribute to a graph

        :return: graph with default attribute description
        :rtype: KadmosGraph
        """

        self.graph['description'] = 'A graph of type: ' + str(type(self))[8:-2] + '.'

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                           VISUALIZATION FUNCTIONS                                                #
    # ---------------------------------------------------------------------------------------------------------------- #

    def print_graph(self, use_pretty_print=False):
        """Function to print the full graph.

        :param use_pretty_print: Boolean on whether to use pretty print for node and edge attributes
        :type use_pretty_print: bool
        """

        graph = self.copy(as_view=True)
        print('\n- - - - - - - - -')
        print(' GRAPH PRINT-OUT ')
        print('- - - - - - - - -\n')

        print('GRAPH ATTRIBUTES\n----------------')
        if use_pretty_print:
            print(json.dumps(graph.graph, indent=1, sort_keys=True))
        else:
            print(graph.graph)

        print('\nNODES\n(' + str(graph.number_of_nodes()) + ')\n-----')
        for node, data in graph.nodes(data=True):
            print(node)
            if use_pretty_print:
                if 'subgraph' in data:
                    del data['subgraph']  # TODO: Change to name / string of subgraph?
                print(json.dumps(data, indent=1, sort_keys=True))
            else:
                print(data)
            print('- - -')

        print('\nDIRECTED EDGES (SOURCE -> TARGET)\n(' + str(graph.number_of_edges()) + ')\n-----')
        for edge in graph.edges(data=True):
            print(edge[0])
            print(edge[1])
            if use_pretty_print:
                print(json.dumps(edge[2], indent=1, sort_keys=True))
            else:
                print(edge[2])
            print('- - -')

        print('- - - - - - - - -\n')
        return

    def plot_graph(self, fig_num=1, color_setting='default', positioning='circular', save_as=None, show_now=True,
                   title=None, edge_label=False):
        """Function to plot a graph.

        :param fig_num: figure number
        :type fig_num: int
        :param color_setting: choose from 'default', 'sinks', 'categories', 'partitions'
        :type color_setting: str
        :param positioning: choose from 'circular', 'spring'
        :type positioning: str
        :param save_as: save plot as figure file
        :type save_as: bool
        :param show_now: Boolean whether to plot directly (pausing the execution until the plot is closed), or not.
        :type show_now: bool
        :param title: title of the graph
        :type title: str
        :param edge_label: edge attribute that will be shown for each edge in graph
        :type edge_label: str
        :return: window with plot

        .. hint:: if the plot window is not showing, you need to add matplotlib.pyplot.show() at the end of your code
        """

        # Create node labels
        node_labels = {}
        for node, data in self.nodes(data=True):
            node_labels[node] = self.nodes[node]['label']

        # Create figure
        f = plt.figure(num=fig_num, figsize=(min(len(node_labels)/3, 50), min(len(node_labels)/3, 50)))

        # Create edge labels
        if edge_label:
            edge_labels = {}
            assert isinstance(edge_label, string_types)
            for edge in self.edges(data=True):
                edge_tple = (edge[0], edge[1])
                if edge_label in edge[2]:  # if attribute found, add string
                    edge_labels[edge_tple] = edge[2][edge_label]
                else:  # if attribute not found, add empty string
                    edge_labels[edge_tple] = ''

        # Define node sizes
        node_sizes = {'variable': max(10000/len(node_labels), 100),
                      'variable group': max(20000/len(node_labels), 100),
                      'function': max(30000/len(node_labels), 100),
                      'architecture element': max(30000/len(node_labels), 100)}

        # Need to create a layout when doing separate calls to draw nodes and edges
        if positioning == 'circular':
            pos = nx.circular_layout(self)
        elif positioning == 'spring':
            pos = nx.spring_layout(self)

        # Define node shapes
        node_shapes = {'variable': 'o',
                       'variable group': 's',
                       'function': 'd',
                       'architecture element': '8'}

        # Dynamic node shape, color, and size creation
        if color_setting == 'default':

            node_cate = set((category[1]["category"] for category in self.nodes(data=True)))

            # Get all distinct node classes according to the node shape attribute
            node_colors = {'variable': '#FFEBCD',
                           'variable group': '#00BFFF',
                           'function': '#FFD700',
                           'architecture element': '#66FF99'}  # Based on html hex string colors
            legend_names = {'variable': 'variable',
                            'variable group': 'variable group',
                            'function': 'function',
                            'architecture element': 'architecture element'}

            for category in node_cate:
                # Filter and draw the subset of nodes with the same symbol in the positions that are now known through
                # the use of the layout.
                nx.draw_networkx_nodes(self, pos,  with_labels=False,
                                       nodelist=[s_node[0] for s_node in
                                                 filter(lambda x: x[1]["category"] == category, self.nodes(data=True))],
                                       node_shape=node_shapes[category],
                                       node_color=node_colors[category],
                                       node_size=node_sizes[category])

        elif color_setting == 'sinks':
            # Get sink list from graph
            sink_list = self.graph['sinks']
            if type(sink_list) is not list:
                sink_list = [sink_list]

            # Specify node colors
            node_colors = {'non-sink': '#DCDCDC',
                           'sink': '#90EE90'}  # Based on html hex string colors
            legend_names = {'non-sink': 'linked',
                            'sink': 'sink'}
            # Get all distinct node classes according to the node shape attribute
            node_cate = set((category[1]["category"] for category in self.nodes(data=True)))

            for category in node_cate:
                nodelist = [s_node[0] for s_node in
                            filter(lambda x: x[1]["category"] == category, self.nodes(data=True))]
                node_color = []
                for entry in nodelist:
                    sink_found = False
                    for sl_entry in sink_list:
                        if sl_entry == entry:
                            sink_found = True
                    if sink_found:
                        node_color.append(node_colors['sink'])
                    else:
                        node_color.append(node_colors['non-sink'])

                # Filter and draw the subset of nodes with the same symbol in the positions that are now known through
                # the use of the layout.
                nx.draw_networkx_nodes(self, pos,
                                       node_shape=node_shapes[category], with_labels=False,
                                       nodelist=nodelist,
                                       node_color=node_color,
                                       node_size=node_sizes[category])

        elif color_setting == 'categories':
            # Group graph nodes
            self.get_nodes_subcategory()
            grouped_nodes = self.get_categorized_nodes()

            # Specify node colors
            node_colors = {'accepted': '#90EE90',  # green
                           'couplings': '#87CEFA',  # blue
                           'problematic': '#FFA500',  # orange
                           'wrong': '#FF4500'}  # red
            legend_names = {'accepted': 'accepted',
                            'couplings': 'couplings',
                            'problematic': 'problematic',
                            'wrong': 'wrong'}
            # Get all distinct node classes according to the node shape attribute
            node_cate = set((category[1]["category"] for category in self.nodes(data=True)))
            for category in node_cate:
                nodelist = [s_node[0] for s_node in
                            filter(lambda x: x[1]["category"] == category, self.nodes(data=True))]
                node_color = []
                for node in nodelist:
                    if node in grouped_nodes['variable']['hole'] or \
                            node in grouped_nodes['variable']['collision'] or \
                            node in grouped_nodes['variable']['collided coupling'] or \
                            node in grouped_nodes['variable']['collided shared coupling'] or \
                            node in grouped_nodes['variable group']['hole group'] or \
                            node in grouped_nodes['variable group']['hole group'] or \
                            node in grouped_nodes['function']['independent']: node_color.append(node_colors['wrong'])
                    elif node in grouped_nodes['function']['source'] or \
                            node in grouped_nodes['function']['sink']:
                        node_color.append(node_colors['problematic'])
                    elif node in grouped_nodes['variable']['supplied input'] or \
                            node in grouped_nodes['variable']['supplied shared input'] or \
                            node in grouped_nodes['variable']['output'] or \
                            node in grouped_nodes['variable group']['supplied input group'] or \
                            node in grouped_nodes['variable group']['supplied shared input group'] or \
                            node in grouped_nodes['variable group']['output group'] or \
                            node in grouped_nodes['function']['complete']: node_color.append(node_colors['accepted'])
                    elif node in grouped_nodes['variable']['coupling'] or \
                            node in grouped_nodes['variable']['shared coupling'] or \
                            node in grouped_nodes['variable group']['coupling group'] or \
                            node in grouped_nodes['variable group']['shared coupling group']:
                        node_color.append(node_colors['couplings'])
                    else:
                        raise AttributeError('Node not found in node grouping dictionary.')
                # Draw the subset of nodes with the same symbol in the positions that are now known through the
                # use of the layout.
                nx.draw_networkx_nodes(self, pos,
                                       node_shape=node_shapes[category], with_labels=False,
                                       nodelist=nodelist,
                                       node_color=node_color,
                                       node_size=node_sizes[category])

        elif color_setting == 'partitions':
            # Check if partition has been performed
            # node_colors = []
            for node, data in self.nodes(data=True):
                if ('part_color' not in data) or ('part_id' not in data):
                    raise IOError('Input graph has not been partitioned (node attributes are missing).')

            # Get all distinct node classes according to the node shape attribute
            node_cate = set((category[1]["category"] for category in self.nodes(data=True)))
            color_set = set()
            for category in node_cate:
                nodelist = [s_node[0] for s_node in
                            filter(lambda x: x[1]["category"] == category, self.nodes(data=True))]
                node_color = []
                for node in nodelist:
                    node_color.append(self.nodes[node]['part_color'])
                    color_set.add(self.nodes[node]['part_color'])
                # Draw the subset of nodes with the same symbol in the positions that are now known through the
                # use of the layout.
                nx.draw_networkx_nodes(self, pos,
                                       node_shape=node_shapes[category], with_labels=False,
                                       nodelist=nodelist,
                                       node_color=node_color,
                                       node_size=node_sizes[category])
            # Create the legend data
            n_part_colors = len(color_set)
            node_colors = dict()
            legend_names = dict()
            for i in range(0, n_part_colors):
                node_colors[i] = color_list()[i]
                legend_names[i] = 'partition ' + str(i + 1)
        else:
            raise IOError("Invalid color_setting (%s) specified." % color_setting)

        ax = f.add_subplot(1, 1, 1)
        for category in node_colors:
            ax.plot([0], [0], color=node_colors[category], label=legend_names[category])

        nx.draw_networkx_edges(self, pos, arrows=True, ax=ax, width=0.5, arrowstyle='->',
                               nodesize=node_sizes['function'])
        if len(node_labels) < 100:
            nx.draw_networkx_labels(self, pos, node_labels, fontsize=10, ax=ax)
            if edge_label:
                # noinspection PyUnboundLocalVariable
                nx.draw_networkx_edge_labels(self, pos, edge_labels, label_pos=0.35)
        plt.legend()

        if title:
            assert type(title) == str
            plt.title(title)
        elif hasattr(self, 'name'):
            plt.title('graph name: ' + str(self.name))

        plt.axis('off')

        if save_as:
            plt.savefig(save_as + '.png')

        if show_now:
            plt.show()
        else:
            plt.show(block=False)

    def plot_adjacency_matrix(self, fig_num=1, fig_size=(7, 7), show_now=True):
        """Draw the adjacency matrix in a plot window.

        :param fig_num: figure number
        :param fig_size: figure size
        :param show_now: Boolean whether to plot directly (pausing the execution until the plot is closed), or not.
        """
        # Get adjacency matrix in right format
        adjacency_matrix = self.get_adjacency_matrix()['SciPy sparse matrix'].toarray().astype('float')

        # Set diagonal values to 0.5
        for i in range(0, len(adjacency_matrix)):
            adjacency_matrix[i, i] = 0.5

        # Plot adjacency matrix in toned-down black and white
        plt.figure(num=fig_num, figsize=fig_size)  # in inches
        plt.imshow(adjacency_matrix,
                   cmap="Greys",
                   interpolation="nearest")

        if show_now:
            plt.show()
        else:
            plt.show(block=False)

        return


# noinspection PyUnboundLocalVariable
def load(file_name, file_type=None, check_list=None, file_check_critical=True, source_folder=None, ignore_modes=False,
         keep_running=False):
    """Function to load a KadmosGraph from a file.

    Different input file types are implemented. They are listed in the following.
    kdms: the most simple file type which makes use of pickling
    cmdows: the most versatile file type especially suited for file exchange with other tools
    graphml: another file type especially suited for file exchange with other tools based on graphs

    :param file_name: name of the file which contains the graph
    :type file_name: str
    :param file_type: file_type
    :type file_type: str

    :param file_check_critical: option for raising errors in case of an invalid graph
    :type file_check_critical: bool
    :param source_folder: source folder which contains the input file
    :type source_folder: str
    :param check_list: list with checks to be performed on in case of CMDOWS file with in- and output XML files.
    check options:
    'consistent_root': to check XML input/output files have the same, single root element.
    'invalid_leaf_elements': to check XML input/output files for invalid leaf elements.
    'schemas': to check XML input/output files against a schema file (XSD) in case of CMDOWS file in combination
    with in- and output XML files.
    :type check_list: list
    :param ignore_modes: for determining if modes are taken into account
    :type ignore_modes: bool
    :param keep_running: for determining if errors should be raised
    :type keep_running: bool
    :return: graph loaded from file
    :rtype: KadmosGraph
    """

    # Try to detect the file type automatically
    if file_type is None:
        if file_name.lower().endswith(tuple(file_extensions)):
            file_type = file_types[file_extensions.index(os.path.splitext(file_name)[1].lower()[1:])]
        else:
            raise IOError('The file type of ' + file_name + ' could not be detected automatically. '
                          'Please provide it with the file_type input argument.')

    # Check if the file type is valid
    file_type = file_type.lower()
    if file_type not in file_types:
        raise IOError('The specified file type ' + file_type + ' is not known. '
                      'Please use one of the following file types: ' + ', '.join(file_types))

    # Get path to file
    if source_folder is None:
        file_path = file_name
    else:
        file_path = os.path.join(source_folder, file_name)

    # Load file
    # TODO: Load also header info and/or metadata of files
    logger.info('Loading the ' + file_type.upper() + ' file ' + file_path + '...')
    if file_type in ['cmdows', 'zipped-cmdows']:
        graph, mpg = _load_cmdows(file_path, check_list, ignore_modes=ignore_modes, keep_running=keep_running)
    elif file_type == 'kdms':
        graph = _load_kdms(file_path)
    elif file_type == 'graphml':
        graph = _load_graphml(file_path)

    # Set mpg to none if not defined
    try:
        mpg
    except NameError:
        mpg = None

    # Check if the loaded graph is valid
    if graph.check():
        logger.info('The graph generated from the loaded file is a valid KADMOS graph.')
    else:
        validity_message = 'The graph generated from the loaded file is not a valid KADMOS graph.'
        if file_check_critical:
            raise IOError(validity_message)
        else:
            logger.warning(validity_message)

    # Return
    logger.info('Successfully loaded the ' + file_type.upper() + ' file ' + file_path + '.')
    if mpg is None:
        return graph
    else:
        return graph, mpg


def check_database(file_name, source_folder=None, check_list=None, keep_running=False):
    """Method to check the XML-files inside the database for parse errors, inconsistent roots, invalid leaf elements
    and schema inconsistencies.

    :param file_name: name of the cmdows file.
    :type file_name: str
    :param source_folder: source folder which contains the input file
    :type source_folder: str
    :param check_list: list with checks to be performed on in case of CMDOWS file with in-/output XML files.
    :type check_list: list
    :param keep_running: for determining if errors should be raised
    :type keep_running: bool
    :return: graph loaded from file
    :rtype: KadmosGraph

    Check_list options:

    * 'consistent_root': to check XML input/output files have the same, single root element.
    * 'invalid_leaf_elements': to check XML input/output files for invalid leaf elements.
    * 'schemas': to check XML input/output files against a schema file (XSD) in case of CMDOWS file in combination
    with in- and output XML files.

    """

    # Try to detect the file type automatically
    if file_name.lower().endswith(tuple(file_extensions)):
        file_type = file_types[file_extensions.index(os.path.splitext(file_name)[1].lower()[1:])]
    else:
        raise IOError('The file type of ' + file_name + ' could not be detected automatically. '
                                                        'Please provide it with the file_type input argument.')

    # Check if the file type is valid
    file_type = file_type.lower()
    if file_type == 'cmdows':
        pass
    else:
        raise IOError('The specified file type ' + file_type + ' cannot be checked. Please use the file type: cmdows.')

    # Get path to file
    if source_folder is None:
        file_path = file_name
    else:
        file_path = os.path.join(source_folder, file_name)

    cmdows = CMDOWS(file_path=file_path)
    if not cmdows.check():
        logger.warning('The CMDOWS file ' + file_path + ' has some flaws. You may use a previous version of KADMOS to'
                                                        ' ensure proper loading of the CMDOWS file.')

    # Parse
    cmdows = etree.parse(file_path, parser).getroot()

    # Clean
    cmdows.clean()

    inputs_list = []
    outputs_list = []

    for function in cmdows.findall('executableBlocks/designCompetences/designCompetence'):
        if not function.findall('inputs/input'):
            # Determine assumed input file location (same folder as CMDOWS file)
            input_file_path = os.path.join(os.path.split(os.path.normpath(function.base))[0],
                                           function.findtext('ID') + '-input.xml').replace('file:' + os.path.sep, '')
        if os.path.isfile(input_file_path):
            inputs_list.append([input_file_path, function])
        else:
            logger.warning('Could not find inputs for function: ' + function.get('uID'))

        if not function.findall('inputs/input'):
            # Determine assumed input file location (same folder as CMDOWS file)
            output_file_path = os.path.join(os.path.split(os.path.normpath(function.base))[0],
                                            function.findtext('ID') + '-output.xml').replace('file:' + os.path.sep, '')
        if os.path.isfile(input_file_path):
            outputs_list.append([output_file_path, function])
        else:
            logger.warning('Could not find outputs for function: ' + function.get('uID'))

    io_list = inputs_list + outputs_list

    _perform_check_list(io_list, check_list, keep_running=keep_running)

    return


def _perform_check_list(io_list, check_list, keep_running=False):

    root_check = False
    leaf_check = False
    xsd_check = False
    # Check which checks need to be performed
    if check_list:
        checks_detected = 0
        if 'consistent_root' in check_list:
            root_check = True
            checks_detected += 1
        if 'invalid_leaf_elements' in check_list:
            leaf_check = True
            checks_detected += 1
        if 'schemas' in check_list:
            xsd_check = True
            checks_detected += 1
        # Check if checks were added correctly
        if checks_detected is not len(check_list):
            logger.warning("Invalid check_list element input detected. Valid options: 'consistent_root',"
                           " 'invalid_leaf_elements' or 'schemas'")

    _parse_check(io_list)

    # Check consistency of root
    if root_check:
        _check_roots(io_list, keep_running=keep_running)

    # Check for invalid leaf elements
    if leaf_check:
        leafs = _get_leafs(io_list)
        _check_leafs(io_list, leafs, keep_running=keep_running)

    # Check file against XSD schema
    if xsd_check and io_list:
        logger.info('Checking for invalidities w.r.t. schema...')
        schema_path = _get_data_schema(os.path.split(io_list[0][0])[0])
        for item in io_list:
            _validate_file_against_schema(item[0], schema_path, keep_running=keep_running)

    return


def _load_kdms(file_path):

    # Parse
    graph = nx.read_gpickle(file_path)

    # Return
    return graph


def _load_graphml(file_path):

    # Parse
    nx_graph = nx.read_graphml(file_path)
    kadmos_graph = KadmosGraph(nx_graph, kb_path=nx_graph.graph['kb_path'])

    # Change class of the graph according to graphml class attribute
    from kadmos.graph.graph_data import MdaoDataGraph
    from kadmos.graph.graph_process import MdaoProcessGraph
    if kadmos_graph.graph['kadmos_graph_type'] == 'MdaoDataGraph':
        graph = MdaoDataGraph(kadmos_graph)
    elif kadmos_graph.graph['kadmos_graph_type'] == 'MdaoProcessGraph':
        graph = MdaoProcessGraph(kadmos_graph)
    else:
        raise AttributeError('Invalid KADMOS graph type attribute (kadmos_graph_type) in the GRAPHML file.')

    # Post-process graph to make it into a valid KADMOS graph again
    transform_string_into_format(graph.graph, keys_to_be_removed=['edge_default', 'node_default', 'kadmos_graph_type'])
    for node, data in graph.nodes(data=True):
        transform_string_into_format(data)
    for u, v, data in graph.edges(data=True):
        transform_string_into_format(data)

    # Return
    return graph


# noinspection PyUnboundLocalVariable
def _load_cmdows(file_path, check_list=None, ignore_modes=False, keep_running=False):

    from kadmos.graph.graph_data import RepositoryConnectivityGraph, FundamentalProblemGraph, \
        MdaoDataGraph

    # If zipped-CMDOWS is provided, then unzip it!
    if os.path.splitext(file_path)[1] == '.zip':
        file_path = unzip_file(file_path)

    # Check CMDOWS
    cmdows = CMDOWS(file_path=file_path)
    if not cmdows.check():
        logger.warning('The CMDOWS file ' + file_path + ' has some flaws. You may use a previous version of KADMOS to'
                       ' ensure proper loading of the CMDOWS file.')

    # Parse
    cmdows = etree.parse(file_path, parser).getroot()

    # Clean
    cmdows.clean()

    # Determine the class for the graph based on elements in the CMDOWS file
    rcg = cmdows.findall('header') and cmdows.findall('executableBlocks')
    fpg = rcg and cmdows.findall('problemDefinition')
    mdg = fpg and cmdows.findall('workflow') and cmdows.findall('architectureElements')
    if mdg:
        graph = MdaoDataGraph()
    elif fpg:
        graph = FundamentalProblemGraph()
    elif rcg:
        graph = RepositoryConnectivityGraph()
    else:
        raise IOError('The CMDOWS file ' + file_path + ' is missing basic elements and cannot be loaded.')

    # Load the graph (and MPG in case this one is provided)
    mpg = graph.load_cmdows(cmdows, check_list, ignore_modes=ignore_modes, keep_running=keep_running)

    # Clean up graph
    try:
        graph.remove_node(None)
        mpg.remove_node(None)
    except nx.exception.NetworkXError:
        pass

    # Return graph
    if isinstance(graph, MdaoDataGraph):
        return graph, mpg
    else:
        return graph, None


def _read_io_xml_file(file_path, mode, ignore_modes=False):

    # Check input
    assert os.path.isfile(file_path), 'File {} does not exist.'.format(file_path)
    assert isinstance(mode, string_types), 'Mode should be an instance of string.'

    # Initiate data dictionary
    dataDict = {"leafNodes": [], "completeNodeSet": [], "leafNodeSet": []}

    # if XML file is empty, return empty dict, else parse file
    if os.stat(file_path).st_size == 0:  # check size of file
        return dataDict
    else:
        tree = etree.parse(file_path, parser)

    # remove comments from tree
    comments = tree.xpath("//comment()")
    for c in comments:
        p = c.getparent()
        p.remove(c)

    # iterate through tree and add data to dict, only touch leaf nodes
    leafNodesList = []
    completeNodeList = []
    for el in tree.iter():
        data = {}
        path = tree.getpath(el)
        if path == '/*':
            raise NotImplementedError('The given XML file {} seems to contain namespaces, '
                                      'this is not supported by KADMOS.'.format(os.path.split(file_path)[1]))

        # add uids to xpath
        path = _add_attributes_to_xpath(path, el)

        # append path to list of all nodes
        completeNodeList.append(path)

        if not el.getchildren():  # if leaf node

            if _check_execution_mode_for_element(el, tree, file_path, mode, ignore_modes=ignore_modes):

                # append path to list of leaf nodes
                leafNodesList.append(path)

                # add element data to function dict
                data['xpath'] = path
                data['tag'] = el.tag
                data['attributes'] = el.attrib
                data['value'] = el.text if el.text else ''

                # remove whitespace from start/end of string, or add None
                if el.text is not None:
                    data['value'] = el.text.strip()
                else:
                    data['value'] = el.text  # adding None if empty

                # add element data to data dict
                dataDict['leafNodes'].append(data)

    # add complete list of input/output nodes (for convenience, performance later on)
    dataDict["leafNodeSet"] = set(leafNodesList)

    # add list of ALL nodes to dictionary
    dataDict["completeNodeSet"] = set(completeNodeList)

    # check if toolspecific nodes found in file
    if any("toolspecific" in node for node in dataDict["leafNodeSet"]):
        logger.warning("'toolspecific' nodes found in {}".format(os.path.split(file_path)[1]))

    return dataDict


def _add_attributes_to_xpath(xpath, element):
    """
    This function adds element attributes to the corresponding elements in the xpath. The ancestors of the element that
    belongs to the xpath are iterated and checked for attributes. If one is found, it is added to the
    approriate place in the xpath. If xpath contains indices in elements that have no defined UID, the indices
    are kept.


    :param xpath: xpath of xml-element
    :type str
    :param element: lxml-element
    :return: uid_xpath
    :rtype str
    """

    # Define bracket pattern once
    bracket_pattern = re.compile('\[.*?\]')

    # get elements in xpath and reverse list for easier operation with ancestors
    path_elems = xpath.split('/')[1:]
    rev_path_elems = list(reversed(path_elems))

    # if element has attributes, add it to xpath element
    if element.attrib:

        clean_elem = False
        if 'uID' in element.attrib:
            # remove existing index-bracket, if present; add uid to element
            cleanElem = bracket_pattern.sub("", rev_path_elems[0])
            clean_elem = True
            rev_path_elems[0] = '{}[@uID="{}"]'.format(cleanElem, element.get('uID'))
        for attr in sorted(element.attrib):
            if attr == 'mapType':
                continue
            if attr != 'uID':
                if not clean_elem:
                    rev_path_elems[0] = bracket_pattern.sub("", rev_path_elems[0])
                # Add remaining attributes to the element
                rev_path_elems[0] += '[@{0}="{1}"]'.format(attr, element.get(attr))

    # loop through ancestors, check for attributes
    for idx, anc in enumerate(element.iterancestors()):

        # if uid attribute present, add to appropriate element
        if anc.attrib:
            clean_elem = False
            if 'uID' in anc.attrib:
                # remove any existing index-brackets; add uid to element
                cleanElem = bracket_pattern.sub("", rev_path_elems[idx+1])
                clean_elem = True
                rev_path_elems[idx+1] = '{}[@uID="{}"]'.format(cleanElem, anc.get('uID'))
            for attr in sorted(anc.attrib):
                if attr == 'mapType':
                    continue
                if attr != 'uID':
                    if not clean_elem:
                        rev_path_elems[idx+1] = bracket_pattern.sub("", rev_path_elems[idx + 1])
                    # Add remaining attributes to the element
                    rev_path_elems[idx+1] += '[@{}="{}"]'.format(attr, anc.get(attr))

    # join elements to uid-xpath
    uid_xpath = "/" + "/".join(reversed(rev_path_elems))

    return uid_xpath


def _check_execution_mode_for_element(element, tree, file, req_mode, ignore_modes=False):
    """
    (PRIVATE) This function retrieves the modes attribute of the child node or of its ancestors. If multiple modes
    are defined in its ancestry, a warning is given and only the lowest modes definition is returned. Ancestry is
    checked for 'modes' attributes regardless of whether it is present in it leaf-node or not.
    Once the modes are retrieved, they are checked for validity (present in info-file) and "negativity" (mode
    attributes can either be positive or negative). NOTE: If no modes are given in a leaf-node, this node is applied
    to ALL function modes.

    :param element: xml element, leaf-node
    :param tree: element tree of the current element
    :param file: file that is currently analyzed
    :param req_mode: required mode for the element
    :return: execModes: string containing all function modes applied to this element
    """
    if ignore_modes:
        return True
    else:
        # get element xpath
        elementPath = tree.getpath(element)
        # get function modes from info file and assert that they are unique
        execModes = ''  # NOTE: if no modes indicated, all modes are applied to node
        modesFound = False

        # if 'modes' key present and has characters
        if 'modes' in element.attrib and re.search("[^\s]", element.attrib['modes']):
            assert isinstance(element.attrib['modes'], string_types), "If provided, modes-attribute of element {} in " \
                                                                    "{} must be of type string.".format(elementPath,
                                                                                                        file)
            execModes = element.attrib['modes']
            modesFound = True

        for anc in element.iterancestors():
            if 'modes' in anc.attrib and re.search("[^\s]", anc.attrib['modes']):
                if not modesFound:
                    modesFound = True
                    execModes = anc.attrib['modes']
                else:
                    logger.warning("Multiple 'modes' attributes found in ancestry of element {} in {}; lowest one is "
                                   "applied.".format(elementPath, file))
                    break

        negModesList = []
        modesList = []
        if re.search("[^\s]", execModes):  # if contains any characters
            # get all modes
            modesList = execModes.split()

            # check if modes negative (all either negative or positive)
            negPattern = "^-"
            if any(re.search(negPattern, mode) for mode in modesList):
                assert all(re.search(negPattern, mode) for mode in modesList), \
                    "Either all or none of the 'modes'-attributes of element {} in {} must be " \
                    "negative!".format(elementPath, file)
                negModesList = [mode[1:] for mode in modesList]
                modesList = []

        # check if the mode is the required mode
        if req_mode in modesList or not modesList:
            if req_mode not in negModesList:
                return True
            else:
                return False
        else:
            return False


def _get_data_schema(kb_dir):
    """
    (PRIVATE) This function retrieves the data schema (.xsd) file from the KB folder and stores filename in instance.
    :return:  data_schema_path
    """
    schema_pattern = "(.xsd)$"

    # Determine name of XML Schema file
    xsd_schema_found = False
    for file_name in os.listdir(kb_dir):
        if os.path.isfile(os.path.join(kb_dir, file_name)):
            match = re.search(schema_pattern, file_name)
            if match and not xsd_schema_found:
                data_schema = file_name
                xsd_schema_found = True
            elif match and xsd_schema_found:
                raise IOError('Multiple XML Schemas (.xsd files) found in the knowledge base ({}). '
                              'Only one .xsd file is allowed per knowledge base.'.format(os.path.split(kb_dir)[1]))
    if not xsd_schema_found:
        raise IOError('No XML Schemas (.xsd files) found in the knowledge base ({}). '
                      'One .xsd file is required per knowledge base.'.format(os.path.split(kb_dir)[1]))
    else:
        logger.info("   XML Schema '{}' found.".format(data_schema))

    return os.path.join(kb_dir, data_schema)


def _validate_file_against_schema(file_path, schema_path, keep_running=False):
    """
    (PRIVATE) Check the read-write XML file in the knowledge base against the XML Schema.
    Argument is list/tuple of nodes to ignore in validation. Root node can not be ignored.

    :rtype: Error
    """
    # Parse the XML file
    tree = etree.parse(file_path)

    # Parse the XML Schema
    xmlschema_doc = etree.parse(schema_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    # Perform file validation
    validated = xmlschema.validate(tree)
    if validated:
        logger.info('   The XML file {} has been validated against the schema {}.'.format(os.path.split(file_path)[1],
                    os.path.split(schema_path)[1]))
    else:
        logger.debug('   Schema validation errors:')
        for error in xmlschema.error_log:
            logger.debug('ERROR ON LINE {} in file {}: {}'.format(error.line, os.path.split(file_path)[1],
                                                                  error.message.encode("utf-8")))
        if not keep_running:
            raise AssertionError('The provided file {} is not valid w.r.t. the schema {} (set logger to debug for '
                                 'additional info).'.format(os.path.split(file_path)[1], os.path.split(schema_path)[1]))
    return


def _check_roots(io_list, keep_running=False):
    """This function checks if there are inconsistent roots in the XML input and output files.

    :rtype: Warning
    """

    logger.info('Checking for inconsistent roots...')

    first_file = True
    for entry in io_list:
        file_path = entry[0]
        file_name = os.path.split(file_path)[1]
        if os.path.isfile(file_path):
            tree = etree.parse(file_path, parser)
            current_root = tree.getroot()
            if not first_file:
                # Give warning if root is inconsistent
                if current_root.tag != previous_root.tag:
                    logger.debug('Inconsistent root of element found in XML file {}'.format(file_name))
                    logger.debug('Inconsistent root: {}'.format(current_root.tag))
                    logger.debug('Inconsistent w.r.t. standard root: {}'.format(previous_root.tag))
                    if not keep_running:
                        raise IOError('Inconsistent root in file {} (root found: {}, expected root: {})'
                                      .format(file_name, current_root.tag, previous_root.tag))
            previous_root = current_root
            first_file = False
    return


def _get_leafs(io_list):
    """
    This function generates a list of unique leaf elements with findable path, path and file_name.
    :return: leafs
    """
    logger.info('Obtaining leaf elements...')
    leafs = set()
    for entry in io_list:
        file_path = entry[0]
        file_name = os.path.split(file_path)[1]
        if os.path.isfile(file_path):
            tree = etree.parse(file_path, parser)
            for el in tree.iter():
                if not el.getchildren():
                    path_list = []
                    child = el
                    while child.getparent() is not None:
                        parent = child.getparent()
                        path_list.append(child.tag)
                        child = parent
                    path_list = reversed(path_list)
                    first = True
                    path = '//'
                    for part in path_list:
                        if first:
                            path += str(part)
                            first = False
                        else:
                            path += '/'+str(part)
                    leafs.add((path, tree.getpath(el), file_name))
    leafs = list(leafs)
    return leafs


def _check_leafs(io_list, leafs, keep_running=False):
    """
    This function checks if there are elements in other files with the same element that still have child elements.
    :rtype: Warning
    """
    logger.info('Checking for invalid leaf elements...')
    for entry in io_list:
        file_path = entry[0]
        file_name = os.path.split(file_path)[1]
        logger.info('   {} (file: {}/{}).'.format(file_name, io_list.index(entry)+1, len(io_list)))
        if os.path.isfile(file_path):
            tree = etree.parse(file_path, parser)
            for leaf in leafs:
                el = tree.find(leaf[0])
                if el is not None:
                    if el.getchildren():
                        path = tree.getpath(el.getchildren()[0])
                        logger.debug('Invalid leaf element found in XML file {}'.format(leaf[2]))
                        logger.debug('Invalid leaf element path {}'.format(leaf[1]))
                        logger.debug('Reason for invalidity: longer path {} found in file {}'.format(path, file_name))
                        leafs.remove(leaf)
                        if not keep_running:
                            raise AssertionError('Invalid leaf element found in XML file {}\n'.format(leaf[2]) +
                                                 'Invalid leaf element path {}\n'.format(leaf[1]) +
                                                 'Reason for invalidity: longer path {} found in file {}'.format(path, file_name))
    return


def _parse_check(io_list):
    logger.info('Checking for parsing errors...')
    for entry in io_list:
        # TODO: Check what is happening here and why...
        file_path=entry[0]
        if os.path.isfile(file_path):
            tree = _try_parsing(file_path)
    return


def _try_parsing(file_path, keep_running=False):
    try:
        tree = etree.parse(file_path, parser)
    except etree.XMLSyntaxError as e:
        logger.debug('Could not parse XML file {}. Check file structure.'.format(os.path.split(file_path)[1]))
        logger.debug('To avoid parser errors, use an XML editor to build and adjust files.')
        logger.warning('ERROR: {}'.format(e))
        raise IOError('Could not parse XML file {}. Check file structure. Parsing error: {}'.format(os.path.split(file_path)[1], e))
    return tree

