from __future__ import absolute_import, division, print_function

# Imports
import json
import os
import re
import shutil
import sys
import linecache
import logging
import tempfile
from datetime import datetime

import progressbar
from six import iteritems, string_types

from kadmos.cmdows import CMDOWS

import kadmos.vistoms as vistoms

from lxml import etree

from ..utilities.xmls import get_element_details, recursively_unique_attribute, merge
from ..utilities.general import make_camel_case, get_list_entries, format_string_for_vistoms

# Settings for the logger
logger = logging.getLogger(__name__)

THEDATA_PREFIX = '			theData = '
VISTOMS_NAME = 'VISTOMS.html'
VISTOMS_TV_NAME = 'VISTOMS_XMLviewer.html'

VISTOMS_NAME_TEMP = 'VISTOMS_Static.html'
VISTOMS_TV_NAME_TEMP = 'VISTOMS_TreeViewer.html'

LOCAL_PATH_PICTURES = '/'.join(["file:static", "pictures"])
LOCAL_FILE_REFS = dict(REP__Acknowledgements__REP='/'.join([LOCAL_PATH_PICTURES, "Acknowledgements.svg"]),
                       REP__AGILE_Icon__REP='/'.join([LOCAL_PATH_PICTURES, "AGILE_Icon.png"]),
                       REP__AGILE_Logo__REP='/'.join([LOCAL_PATH_PICTURES, "AGILE_Logo.png"]),
                       REP__Contact__REP='/'.join([LOCAL_PATH_PICTURES, "Contact.svg"]),
                       REP__Home__REP='/'.join([LOCAL_PATH_PICTURES, "Home.svg"]),
                       REP__RWTH_Logo__REP='/'.join([LOCAL_PATH_PICTURES, "RWTH_Logo.svg"]),
                       REP__TUDelft_Logo__REP='/'.join([LOCAL_PATH_PICTURES, "TUDelft_Logo.svg"]),
                       REP__Tutorial__REP='/'.join([LOCAL_PATH_PICTURES, "Tutorial.svg"]),
                       REP__VISTOMS_Label__REP='/'.join([LOCAL_PATH_PICTURES, "VISTOMS_Label.svg"]),
                       REP__glyphicons_eot__REP='/'.join([LOCAL_PATH_PICTURES, "glyphicons-halflings-regular.eot"]),
                       REP__glyphicons_svg__REP='/'.join([LOCAL_PATH_PICTURES, "glyphicons-halflings-regular.svg"]),
                       REP__glyphicons_ttf__REP='/'.join([LOCAL_PATH_PICTURES, "glyphicons-halflings-regular.ttf"]),
                       REP__glyphicons_woff__REP='/'.join([LOCAL_PATH_PICTURES, "glyphicons-halflings-regular.woff"]),
                       REP__glyphicons_woff2__REP='/'.join([LOCAL_PATH_PICTURES, "glyphicons-halflings-regular.woff2"]))

ENCODING = {'encoding': 'utf-8'} if sys.version_info[0] > 2 else {}


class VistomsMixin(object):

    def vistoms_start(self, file_dir=None, mpg=None):
        """Function to open an interactive VISTOMS based on the data graph and (optionally) the MPG. If file_dir is not
        provided then the files are stored in a temp directory.

        :param file_dir: folder name or path where the graphs used in the interactive VISTOMS will be stored.
        :type file_dir: path
        :param mpg: MDAO process graph to be used in combination with the data graph.
        :type mpg: MdaoProcessGraph
        :return: interactive VISTOMS
        :rtype: file
        """

        # Logging
        logger.info('Creating the VISTOMS instance...')

        # If destination folder is given, create + use that
        if file_dir is not None:
            if os.path.isdir(file_dir):
                shutil.rmtree(file_dir)
            os.mkdir(file_dir)
            vistoms_dir = os.path.abspath(file_dir)
        # Else create temporary directory
        else:
            temp_dir = tempfile.mkdtemp()
            vistoms_dir = os.path.abspath(temp_dir)

        # Save the graph (self) in the folder
        self.save('tmp_01.kdms', destination_folder=vistoms_dir, mpg=mpg)

        # Then run interactive VISTOMS
        from kadmos.vistoms.vistoms import run_vistoms
        run_vistoms(folder=vistoms_dir)

    def vistoms_create(self, vistoms_dir, vistoms_version=None, mpg=None, function_order=None, reference_file=None,
                       compress=False, remove_after_compress=True, graph_id=None, use_png_figs=False, file_refs=None,
                       xml_file=None):
        """Function to create a new VISTOMS instance from a graph.

        :type self: KadmosGraph
        :param vistoms_dir: directory of the VISTOMS directory to be created
        :type vistoms_dir: str
        :param vistoms_version: version of the VISTOMS instance to be used (as stored in the package itself)
        :param vistoms_version: str
        :param mpg: optional MPG graph to be saved with MDG as XDSM (if None a DSM is created)
        :type mpg: MdaoProcessGraph
        :param function_order: optional function order for the diagonal of the graph (only applicable for DSMs)
        :type function_order: list
        :param reference_file: file from which reference values are extracted (either full path or file in same folder)
        :type reference_file: str
        :param compress: setting whether to compress the final VISTOMS instance folder to a zip file
        :type compress: bool
        :param remove_after_compress: setting whether to remove the original folder after compression
        :type remove_after_compress: bool
        :param graph_id: identifier of the new graph
        :type graph_id: str
        :param use_png_figs: setting whether to use the PNG figures instead of the SVG figures for local execution
        :type use_png_figs: bool
        :param file_refs: setting to provide file references manually (to use VISTOMS on a server)
        :type file_refs: dict
        :param xml_file: Name of the CMDOWS xml file
        :type xml_file: file
        :return: vistoms instance
        :rtype: VistomsMixin
        """

        # Check inputs
        self._vistoms_assertions(mpg, function_order, reference_file, vistoms_version, graph_id)

        # Logging
        logger.info('Creating the VISTOMS instance (this might take a while)...')

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        # Get absolute path of vistoms_dir
        vistoms_dir = os.path.abspath(vistoms_dir)

        # Initiate VISTOMS instance
        vistoms.copy(temp_dir, vistoms_version='Static')

        # Create dictionary for the data.json file
        data = dict(graphs=[], categories=[])

        # Add categories
        data['categories'].append({'name': 'schema', 'description': 'schema'})
        data['categories'].append({"name": "catschema_nodeLev", "description": "node levels"})
        data['categories'].append({"name": "catschema_funLev", "description": "function levels"})
        data['categories'].append({"name": "catschema_roleLev", "description": "role levels"})
        data['categories'].append({"name": "catschema_sysLev", "description": "system levels"})

        # Set default graph ID
        if graph_id is None:
            graph_id = '01'

        # Determine graph data entry
        graph_entry = self._vispack_get_graph_data_entry(graph_id, mpg=mpg, order=function_order,
                                                         reference_file=reference_file, xml_file=xml_file)

        # Put graph data entry in the data dictionary
        data['graphs'].append(graph_entry)

        data_str = json.dumps(data, default=lambda o: '<not serializable>')

        # Define string replacements based on file referencing
        if file_refs is None:
            rep = dict(LOCAL_FILE_REFS)
            if use_png_figs:
                for key, item in iteritems(rep):
                    if '.svg' in item:
                        rep[key] = item.replace('.svg', '.png')
            rep['REP__GRAPH_DATA__REP'] = data_str
        else:
            rep = file_refs
            for key, item in iteritems(LOCAL_FILE_REFS):
                if key not in rep:
                    raise AssertionError('Replacement key {} is missing in the '
                                         'file_refs.'.format(key))
            rep['REP__GRAPH_DATA__REP'] = data_str

        # Perform the text replacement
        rep = dict((re.escape(k), v) for k, v in iteritems(rep))
        pattern = re.compile("|".join(list(rep)))
        with open(os.path.join(temp_dir, VISTOMS_NAME_TEMP), "rt", **ENCODING) as fin:
            with open(os.path.join(temp_dir, VISTOMS_NAME), "wt", **ENCODING) as fout:
                for line in fin:
                    fout.write(pattern.sub(lambda m: rep[re.escape(m.group(0))], line))

        # Remove the original VISTOMS file
        os.remove(os.path.join(temp_dir, VISTOMS_NAME_TEMP))

        # Copy temp directory to file path
        # Remove previous VISTOMS directory (if present)
        try:
            shutil.rmtree(vistoms_dir)
        except OSError:
            pass
        # Place new VISTOMS folder
        shutil.copytree(temp_dir, vistoms_dir)
        # Remove temporary directory
        shutil.rmtree(temp_dir)

        if compress:
            _compress_vistoms_instance(vistoms_dir, remove_after_compress)

        # Logging
        logger.info('Successfully created the VISTOMS instance.')

        return

    def vistoms_add(self, vistoms_dir, mpg=None, function_order=None, reference_file=None, compress=False,
                    remove_after_compress=True, graph_id=None, replacement_id=None, xml_file=None, file_refs_repl=None):
        """Function to add a graph to a existing VISTOMS instance.

        :param vistoms_dir: directory of the VISTOMS directory to be used for addition
        :type vistoms_dir: str
        :param mpg: optional MPG graph to be saved with MDG as XDSM (if None a DSM is created)
        :type mpg: MdaoProcessGraph
        :param function_order: optional function order for the diagonal of the graph (only applicable for DSMs)
        :type function_order: list
        :param reference_file: file from which reference values are extracted (either full path or file in same folder)
        :type reference_file: str
        :param compress: setting whether to compress the final VISTOMS instance folder to a zip file
        :type compress: bool
        :param remove_after_compress: setting whether to remove the original folder after compression
        :type remove_after_compress: bool
        :param graph_id: indentifier of the new graph
        :type graph_id: str
        :param replacement_id: indentifier of the graph to be replaced
        :type replacement_id: str
        :param xml_file: Name of the CMDOWS xml-file
        :type xml_file: file
        :param file_refs_repl: Replacement of existing file references in the original HTML
        :type xml_file: dict
        :return: enriched vistoms instance
        :rtype: VistomsMixin

        .. hint:: In one VISTOMS instance different graphs can be shown. For example it is possible to include different
            architectures for the same problem in one VISTOMS instance.
        """

        # Check inputs
        self._vistoms_assertions(mpg, function_order, reference_file, None, graph_id)
        if replacement_id:
            if not isinstance(replacement_id, string_types):
                raise AssertionError('The attribute replacement_id should be of type str, '
                                     'now of type: {}.'.format(type(replacement_id)))
        if not os.path.exists(vistoms_dir):
            raise AssertionError('There is not a VISTOMS instance at {}.'.format(vistoms_dir))
        if not os.path.exists(os.path.join(vistoms_dir, VISTOMS_NAME)):
            raise AssertionError('{} not found in folder {}.'.format(VISTOMS_NAME, vistoms_dir))

        # Logging
        logger.info('Adding graph to the VISTOMS instance (this might take a while)...')

        # Create vistoms file name path
        vistoms_file = os.path.join(vistoms_dir, VISTOMS_NAME)

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        # Copy VISTOMS_NAME file to the temp directory
        temp_file = os.path.join(temp_dir, VISTOMS_NAME)
        shutil.copy(vistoms_file, temp_file)

        # Get the graph data and line number
        data, data_linenumber = _get_the_data(temp_file)

        if replacement_id is not None:
            # Find IDs in the current data.json
            graph_ids = [graph['id'] for graph in data['graphs']]
            if replacement_id not in graph_ids:
                raise AssertionError('Could not find replacement_id: {}. '
                                     'Available IDs: {}.'.format(replacement_id, graph_ids))
            replacement_index = graph_ids.index(replacement_id)
        if graph_id is None:
            if replacement_id is None:
                graph_id = str(len(data['graphs']) + 1).zfill(2)
                if not int(graph_id) < 100:
                    raise AssertionError('graph_id ({}) should be smaller than 100.'
                                         .format(int(graph_id)))
            else:
                graph_id = replacement_id

        # Determine graph data entry
        graph_entry = self._vispack_get_graph_data_entry(graph_id, mpg=mpg, order=function_order,
                                                         reference_file=reference_file, xml_file=xml_file)

        # Add graph_entry at the right location
        if replacement_id is None:
            data['graphs'].append(graph_entry)
        else:
            data['graphs'][replacement_index] = graph_entry

        # Replace the graph data
        data_str = json.dumps(data, default=lambda o: '<not serializable>')
        _replace_line(temp_file, data_linenumber, THEDATA_PREFIX + data_str)

        # Perform file reference replacements, if necessary
        if file_refs_repl:
            new_file_path = os.path.splitext(temp_file)[0] + '_new' + os.path.splitext(temp_file)[1]
            rep = dict((re.escape(k), v) for k, v in iteritems(file_refs_repl))
            pattern = re.compile("|".join(list(rep)))
            with open(temp_file, "rt") as fin:
                with open(new_file_path, "wt") as fout:
                    for line in fin:
                        fout.write(pattern.sub(lambda m: rep[re.escape(m.group(0))], line))
            temp_file = new_file_path

        # Copy VISTOMS_NAME to original folder
        # Remove previous VISTOMS_NAME
        try:
            os.remove(vistoms_file)
        except OSError:
            pass
        # Place new VISTOMS_NAME file
        os.rename(temp_file, vistoms_file)
        # Remove temporary directory
        shutil.rmtree(temp_dir)

        if compress:
            _compress_vistoms_instance(vistoms_dir, remove_after_compress)

        # Logging
        logger.info('Successfully added graph to the VISTOMS instance.')

        return

    def vistoms_add_json(self, mpg=None, function_order=None, graph_id=None):
        """Function to add a graph to a existing VISTOMS instance.

        In one VISTOMS instance different graphs can be shown. For example it is possible to include different
        architectures for the same problem in one VISTOMS instance.

        :param mpg: optional MPG graph to be saved with MDG as XDSM (if None a DSM is created)
        :type mpg: MdaoProcessGraph
        :param function_order: optional function order for the diagonal of the graph (only applicable for DSMs)
        :type function_order: list
        """

        # Check inputs
        self._vistoms_assertions(mpg, function_order, None, None, graph_id)

        # Logging
        logger.info('Adding graph to the VISTOMS instance (this might take a while)...')

        # if data == 'REP__GRAPH_DATA__REP':
        # Create dictionary for the data.json file
        data = dict(graphs=[], categories=[])
        # Add categories
        data['categories'].append({'name': 'schema', 'description': 'schema'})
        data['categories'].append({"name": "catschema_nodeLev", "description": "node levels"})
        data['categories'].append({"name": "catschema_funLev", "description": "function levels"})
        data['categories'].append({"name": "catschema_roleLev", "description": "role levels"})
        data['categories'].append({"name": "catschema_sysLev", "description": "system levels"})


        # Determine graph data entry
        graph_entry = self._vispack_get_graph_data_entry(graph_id, mpg=mpg, order=function_order,
                                                         reference_file=None, xml_file=None)

        # Add graph_entry at the right location
        data['graphs'].append(graph_entry)

        # Replace the graph data
        data_str = json.dumps(data, default=lambda o: '<not serializable>')

        logger.info('Successfully added graph to the VISTOMS instance.')

        return data_str

    def _vistoms_assertions(self, mpg, function_order, reference_file, vistoms_version, graph_id):
        """Function to check the inputs for the VISTOMS instance functions."""

        from kadmos.graph.graph_kadmos import KadmosGraph
        from kadmos.graph.graph_process import MdaoProcessGraph
        if not isinstance(self, KadmosGraph):
            raise AssertionError('Wrong type {} for provided graph'.format(type(self)))
        if not isinstance(mpg, MdaoProcessGraph) and mpg is not None:
            raise AssertionError('Wrong type {} for provided MPG graph.'.format(type(mpg)))
        if isinstance(self, MdaoProcessGraph):
            raise AssertionError('Wrong type {} for provided graph, did not expect an '
                                 'MdaoProcessGraph'.format(type(self)))
        if not isinstance(function_order, list) and function_order is not None:
            raise AssertionError('Unexpected function order.')
        if not isinstance(vistoms_version, string_types) and vistoms_version is not None:
            raise AssertionError('Unexpected vistoms_version.')
        if reference_file is not None:
            if not os.path.exists(reference_file):
                raise AssertionError('Could not find reference file at path: {}'
                                     .format(reference_file))
        if mpg and function_order:
            logger.warning('Both an MPG and order list are given. The FPG is used for the '
                           'determination of the order.')
        if not isinstance(graph_id, string_types) and graph_id is not None:
            raise AssertionError('graph_id is expected to be a string or None.')

    def _vispack_get_graph_data_entry(self, graph_id, mpg=None, order=None, reference_file=None, xml_file=None):
        """
        Function to make the json files required to for the VISTOMS instance.

        :type self: KadmosGraph
        :param mpg: MDO Process Graph
        :type mpg: MdaoProcessGraph
        :param order: list with the order in which the tools should be placed (only required if the FPG is not given)
        :type order: list, None
        :param reference_file: file from which reference values are extracted (either full path or file in same folder)
        :type reference_file: str
        :return: dictionary entry with all graph data
        :rtype: dict
        """

        # Start-up
        self.get_nodes_subcategory()

        coordinator_str = self.COORDINATOR_STRING

        # Check graph name and description
        if 'name' not in self.graph:
            self.add_default_name()
        if 'description' not in self.graph:
            self.add_default_description()

        # Create graph_data dictionary entry and fill in initial attributes
        graph_data_entry = dict(name=self.graph.get('name'),
                                id=graph_id,
                                description=self.graph.get('description'),
                                variableSchemes=dict())
        for attr in self.graph:
            graph_data_entry[attr] = self.graph[attr]

        # Get full_graph dictionary
        full_graph = self._get_full_graph()

        # Determine / check analysis order based on the full_graph
        if not order:
            if not mpg:
                # Get tool list and put the coordinator in the top left corner
                tool_list = list(full_graph['attributes']['tools'])
                tool_list.remove(coordinator_str)
                order = [coordinator_str] + tool_list
            else:
                # Find order based on FPG
                order = []
                for idx in range(0, mpg.number_of_nodes()):
                    node_list = mpg.find_all_nodes(attr_cond=['diagonal_position', '==', idx])
                    if len(node_list) != 1:
                        raise AssertionError('Somehow, a unique diagonal position "{}" could not '
                                             'be found in the FPG.'.format(idx))
                    order.append(node_list[0])
        else:
            order = [coordinator_str] + order
            order_differences = set(order).difference(full_graph['attributes']['tools'])
            name_differences = set(full_graph['attributes']['tools']).difference(order)
            actual_tool_names = full_graph['attributes']['tools']
            actual_tool_names.remove(coordinator_str)

            if order_differences:
                raise AssertionError('Given order of tools does not match the tool names in the '
                                     'graph. \nInvalid name(s): {}.\nActual tool names: {}'
                                     .format(', '.join(list(order_differences)),
                                             ', '.join(actual_tool_names)))
            if name_differences:
                raise AssertionError('Given order of tools misses one or more tools present in the '
                                     'graph, namely: {}.'.format(', '.join(name_differences)))

        # Get edge bundles data and tools data
        edge_bundles_list, functions_data_list = self._get_edge_bundles_and_functions_data(full_graph)
        # Write dictionary entry
        graph_data_entry['edgeBundles'] = edge_bundles_list

        # Get xdsm definition
        xdsm_dict = self._get_xdsm(order, edge_bundles_list, mpg)
        # Write dictionary entry
        graph_data_entry['xdsm'] = xdsm_dict

        # Benedikt: New schema function
        # Get variable tree based on schema
        variable_tree_dataschema = self._get_variable_tree_dataschema(full_graph, reference_file)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['schema'] = variable_tree_dataschema

        # Get variable tree based on system level categories (inputs, outputs, couplings)
        variable_tree_categorized_system_level = self._get_variable_tree_categorized_system_level(full_graph)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['catschema_sysLev'] = variable_tree_categorized_system_level

        # Node level sorting of the variables (input, shared input, shared coupling, collision, etc.)
        variable_tree_categorized_node_level = self._get_variable_tree_categorized_node_level(full_graph)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['catschema_nodeLev'] = variable_tree_categorized_node_level

        # Role level sorting of the variables (problem roles / architecture roles)
        variable_tree_categorized_role_level = self._get_variable_tree_categorized_role_level(full_graph)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['catschema_roleLev'] = variable_tree_categorized_role_level

        # Function level sorting of the variables (function inputs, function outputs)
        variable_tree_categorized_function_level = \
            self._get_variable_tree_categorized_function_level(functions_data_list)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['catschema_funLev'] = variable_tree_categorized_function_level

        graph_data_entry['organization'] = self.graph['organization']


        return graph_data_entry

    def _get_full_graph(self):
        """Method to create the full_graph dictionary. The full_graph is a dictionary with the following structure
        {node_key:[input_nodes to node_key]}

        :return: full_graph dictionary
        :rtype: dict
        """

        # Settings
        circular_cats = self.NODE_GROUP_SUBCATS['all circular variables']
        circular_coor_input_cats = get_list_entries(circular_cats, 0, 1)
        circular_coor_output_cats = get_list_entries(circular_cats, 0, 2)
        coordinator_str = self.COORDINATOR_STRING

        # Start-up
        logger.debug('Creating full_graph_data dictionary...')
        full_graph = dict(attributes=dict(tools=[], variables=[]))

        # Add coordinator to the full_graph to avoid errors later on (in case the coordinator has no inputs)
        full_graph[coordinator_str] = []
        full_graph['attributes']['tools'].append(coordinator_str)
        for edge in self.edges():
            # Check if the source is already in the dictionary (else add empty list)
            if edge[0] not in full_graph:
                # Add as output of coordinator (if node is a system input or of a certain circular variable category)
                if (self.in_degree(edge[0]) == 0 and self.nodes[edge[0]]['category'] == 'variable') or \
                                self.nodes[edge[0]]['subcategory'] in circular_coor_input_cats:
                    full_graph[edge[0]] = [coordinator_str]
                    full_graph['attributes']['tools'].append(coordinator_str)
                else:
                    full_graph[edge[0]] = []
                if self.nodes[edge[0]]['category'] == 'function':
                    full_graph['attributes']['tools'].append(edge[0])
                elif self.nodes[edge[0]]['category'] == 'variable':
                    full_graph['attributes']['variables'].append(edge[0])
                else:
                    raise NotImplementedError('Node category %s is not allowed.' % self.nodes[edge[0]]['category'])
            else:
                # Add as output of coordinator (if node is a system input or of a certain circular variable category)
                if (self.in_degree(edge[0]) == 0 and self.nodes[edge[0]]['category'] == 'variable') or \
                                self.nodes[edge[0]]['subcategory'] in circular_coor_input_cats:
                    full_graph[edge[0]].append(coordinator_str)
            # Check if the target is already in the dictionary
            if edge[1] in full_graph:
                full_graph[edge[1]].append(edge[0])
            else:
                full_graph[edge[1]] = [edge[0]]
                if self.nodes[edge[1]]['category'] == 'function':
                    full_graph['attributes']['tools'].append(edge[1])
                elif self.nodes[edge[1]]['category'] == 'variable':
                    full_graph['attributes']['variables'].append(edge[1])
                else:
                    raise NotImplementedError('Node category %s is not allow.' % self.nodes[edge[1]]['category'])
            # Check if the target is a system output (according to indegree or circularity)
            if (self.out_degree(edge[1]) == 0 and self.nodes[edge[1]]['category'] == 'variable') or \
                            self.nodes[edge[1]]['subcategory'] in circular_coor_output_cats:
                if coordinator_str in full_graph:
                    full_graph[coordinator_str].append(edge[1])
                else:
                    full_graph[coordinator_str] = [edge[1]]
                    full_graph['attributes']['tools'].append(coordinator_str)

        # Remove duplicates from the list
        full_graph['attributes']['tools'] = list(set(full_graph['attributes']['tools']))
        full_graph['attributes']['variables'] = list(set(full_graph['attributes']['variables']))
        full_graph[coordinator_str] = list(set(full_graph[coordinator_str]))

        # Add holes in the graph as source functions
        hole_functions = self.find_all_nodes(category='function', subcategory='independent')
        for hole in hole_functions:
            full_graph[hole] = []
            full_graph['attributes']['tools'].append(hole)

        # Write log output
        logger.debug('Successfully created full_graph_data dictionary.')

        return full_graph

    def _get_edge_bundles_and_functions_data(self, full_graph):
        """ Function to get the lists for edge bundles and functions data.

        :param full_graph: full_graph dictionary
        :type full_graph: dict
        :return: edge bundles and functions data lists in a single tuple
        :rtype: tuple
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        # Create empty dictionary edge_bundles
        logger.debug('Creating edge_bundles_list and tools_data_list...')
        edge_bundles = dict(attributes=dict(tools=full_graph['attributes']['tools'],
                                            variables=full_graph['attributes']['variables']))
        tools_data = dict(attributes=dict(tools=full_graph['attributes']['tools'],
                                          variables=full_graph['attributes']['variables']))

        # Setting progress bar as this process takes some time
        n_keys = len(list(full_graph))
        if logging.getLogger().getEffectiveLevel() in [logging.DEBUG, logging.INFO] and n_keys > 10000:
            n_key = 0
            logger.info('Looping through all nodes...')
            progress_bar = progressbar.ProgressBar(max_value=n_keys)
            progress_bar.start()

        for key in full_graph:
            if logging.getLogger().getEffectiveLevel() in [logging.DEBUG, logging.INFO] and n_keys > 10000:
                # noinspection PyUnboundLocalVariable
                progress_bar.update(n_key)
                n_key += 1
            if key is not 'attributes' and key is not coordinator_str:
                if self.nodes[key]['category'] == 'variable':
                    input_tools = full_graph[key]
                    # Extend tools_data with tool outputs
                    for input_tool in input_tools:
                        if input_tool not in tools_data:
                            tools_data[input_tool] = dict(name=input_tool,
                                                          input=[],
                                                          output=[key])
                        else:
                            tools_data[input_tool]['output'].append(key)
                    # Create edge_bundles
                    for tool in full_graph['attributes']['tools']:
                        if key in full_graph[tool]:
                            if tool not in edge_bundles:
                                edge_bundles[tool] = dict(name=tool, input=[],
                                                          pipeline_data=dict())
                            # Add input tools
                            edge_bundles[tool]['input'].extend(input_tools)
                            for input_tool in input_tools:
                                # Extend edge_bundles with pipeline data (variables passed between tools)
                                if input_tool not in edge_bundles[tool]['pipeline_data']:
                                    edge_bundles[tool]['pipeline_data'][input_tool] = []
                                edge_bundles[tool]['pipeline_data'][input_tool].append(key)
                    # Check if variable is also input to the coordinator
                    if key in full_graph[coordinator_str]:
                        if coordinator_str not in edge_bundles:
                            edge_bundles[coordinator_str] = dict(name=coordinator_str,
                                                                 input=[],
                                                                 pipeline_data=dict())
                        # Add input tools to coordinator
                        edge_bundles[coordinator_str]['input'].extend(input_tools)
                        for input_tool in input_tools:
                            # Extend edge_bundles with pipeline data (variables passed between tools)
                            if input_tool not in edge_bundles[coordinator_str]['pipeline_data']:
                                edge_bundles[coordinator_str]['pipeline_data'][input_tool] = []
                            edge_bundles[coordinator_str]['pipeline_data'][input_tool].append(key)
                elif not self.nodes[key]['category'] == 'function':
                    raise NotImplementedError('Node category %s is not allowed.' % self.nodes[key]['category'])
            if key is not 'attributes':
                if key is coordinator_str:
                    if key not in tools_data:
                        tools_data[key] = dict(name=key, input=full_graph[key],
                                               output=[])
                    else:
                        tools_data[key]['input'] = full_graph[key]
                elif self.nodes[key]['category'] == 'function':
                    if key not in tools_data:
                        tools_data[key] = dict(name=key, input=full_graph[key],
                                               output=[])
                    else:
                        tools_data[key]['input'] = full_graph[key]
        if logging.getLogger().getEffectiveLevel() in [logging.DEBUG, logging.INFO] and n_keys > 10000:
            # noinspection PyUnboundLocalVariable
            progress_bar.finish()
            logger.info('Successfully looped through all nodes.')

        # Remove duplicates from the list
        for key, value in iteritems(tools_data):
            if 'output' in value:
                tools_data[key]['output'] = list(set(value['output']))
        for key, value in iteritems(edge_bundles):
            if 'input' in value:
                edge_bundles[key]['input'] = list(set(value['input']))
            if 'pipeline_data' in value:
                for subkey, subvalue in iteritems(value['pipeline_data']):
                    edge_bundles[key]['pipeline_data'][subkey] = list(set(subvalue))

        # Export edge_bundles dictionary to list
        edge_bundles_list = []
        for key in edge_bundles:
            if key is not 'attributes':
                edge_bundles_list.append(edge_bundles[key])

        # Export tools_data dictionary to list
        tools_data_list = []
        for key in tools_data:
            if key is not 'attributes':
                new_dict = tools_data[key]
                new_dict['type'] = 'function'
                tools_data_list.append(new_dict)

        logger.debug('Successfully created edge_bundles_list and tools_data_list.')

        return edge_bundles_list, tools_data_list

    def _get_xdsm(self, order, edge_bundles_list, mpg):
        """ Function to get the xdsm dictionary definition for VISTOMS.

        :param order: function order
        :type order: list
        :param edge_bundles_list: data connections
        :type edge_bundles_list: list
        :param mpg: MDAO process graph
        :type mpg: MdaoProcessGraph
        :return: xdsm definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating xdsm...')
        xdsm_dict = dict(nodes=[], edges=[])

        # Add diagonal nodes
        for block in order:
            if block is not coordinator_str:
                if self.nodes[block]['category'] == 'function':
                    if 'architecture_role' in self.nodes[block]:
                        arch_role = self.nodes[block]['architecture_role']
                        if arch_role == self.ARCHITECTURE_ROLES_FUNS[0]:  # coordinator
                            block_type = 'coordinator'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[1]:  # optimizer
                            block_type = 'optimization'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[2]:  # converger
                            block_type = 'converger'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[3]:  # doe
                            block_type = 'doe'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[4]:  # UNUSED!
                            block_type = 'precouplinganalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[5]:  # uncoupled-DVD analysis
                            block_type = 'preiteratoranalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[6]:  # uncoupled-DVI analysis
                            block_type = 'postiteratoranalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[7]:  # coupled analysis
                            block_type = 'coupledanalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[8]:  # post-coupling analysis
                            block_type = 'postcouplinganalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[9]:  # surrogatemodel
                            block_type = 'surrogatemodel'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[10]:  # distributed system converger
                            block_type = 'converger'
                        else:
                            raise NotImplementedError('Architecture role %s not implemented.' % arch_role)
                    elif 'problem_role' in self.nodes[block]:
                        if self.nodes[block]['problem_role'] == self.FUNCTION_ROLES[1]:  # coupled
                            block_type = 'coupledanalysis'
                        elif self.nodes[block]['problem_role'] == self.FUNCTION_ROLES[2]:  # post-coupling
                            block_type = 'postcouplinganalysis'
                        elif self.nodes[block]['problem_role'] == self.FUNCTION_ROLES[3]:  # uncoupled-DVI
                            block_type = 'preiteratoranalysis'
                        elif self.nodes[block]['problem_role'] == self.FUNCTION_ROLES[4]:  # uncoupled-DVD
                            block_type = 'postiteratoranalysis'
                    else:
                        block_type = 'rcganalysis'
                    block_metadata = self.nodes[block]
                else:
                    raise Exception('Block category %s not supported.' % self.nodes[block]['category'])
            else:
                block_type = 'coordinator'
                block_metadata = [{'name': 'Coordinator'},
                                  {'description': 'Action block providing system inputs and collecting outputs.'},
                                  {'creator': 'Imco van Gent'}]
            # noinspection PyUnboundLocalVariable
            xdsm_dict['nodes'].append(dict(type=block_type,
                                           id=format_string_for_vistoms(block, prefix='id_'),
                                           uID=block,
                                           name=format_string_for_vistoms(block),
                                           metadata=block_metadata))

        # Add edges between blocks
        for item in edge_bundles_list:
            name_keyword = ' couplings'
            if item['name'] is coordinator_str:
                to_node_id = format_string_for_vistoms(coordinator_str, prefix='id_')
                to_node_uID = coordinator_str
                name_keyword = ' outputs'
            else:
                to_node_id = format_string_for_vistoms(item['name'], prefix='id_')
                to_node_uID = item['name']
            for from_node in item['input']:
                if from_node is coordinator_str:
                    from_node_id = format_string_for_vistoms(coordinator_str, prefix='id_')
                    from_node_uID = coordinator_str
                    name_keyword = ' inputs'
                else:
                    from_node_id = format_string_for_vistoms(from_node, prefix='id_')
                    from_node_uID = from_node
                if not to_node_id == from_node_id:  # check to avoid showing circular couplings on top of the diagonal
                    xdsm_dict['edges'].append({"to": to_node_id,
                                               "from": from_node_id,
                                               "to_uID": to_node_uID,
                                               "from_uID": from_node_uID,
                                               "name": ','.join(item['pipeline_data'][from_node]),
                                               "short_name": str(len(item['pipeline_data'][from_node])) + name_keyword})

        # Add workflow
        if mpg:
            xdsm_dict['workflow'] = mpg.get_process_list(use_d3js_node_ids=True)
        else:
            xdsm_dict['workflow'] = []

        logger.debug('Successfully created xdsm.')
        return xdsm_dict


    def _get_variable_tree_dataschema(self, full_graph, reference_file):
        """ Function to determine the variable tree based on the data schema.

        :param full_graph: dictionary with graph data
        :type full_graph: dict
        :param reference_file: file with reference values
        :type reference_file: file
        :return: variable tree definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating schema variable tree...')

        variable_tree_dataschema = []
        if reference_file:
            # Parse reference XML
            reference_xml = etree.parse(reference_file)
            # Check validity of the CPACS file
            # noinspection PyUnusedLocal
            reference_valid = recursively_unique_attribute(reference_xml)
        for key in full_graph:
            if key is not 'attributes' and key is not coordinator_str:
                if self.nodes[key]['category'] == 'variable':
                    # Determine element element value and dimension based on reference file
                    if reference_file:
                        # Check if the variable node is actually a related node
                        if 'related_to_schema_node' in self.nodes[key]:
                            xpath = self.nodes[key]['related_to_schema_node']
                        else:
                            xpath = key
                        # Get element details
                        # noinspection PyUnboundLocalVariable
                        var_value, var_dim = get_element_details(reference_xml, xpath)
                    else:
                        var_value = 'unknown'
                        var_dim = None
                        xpath = key
                    var_dict = dict(xPath=xpath, value=var_value, dimension=var_dim, type='variable')
                    variable_tree_dataschema.append(var_dict)
        logger.debug('Successfully created schema variable tree.')
        return variable_tree_dataschema

    def _get_variable_tree_categorized_system_level(self, full_graph):
        """ Function for system level sorting of the variables (inputs, outputs, couplings, holes)

        :param full_graph: dictionary with graph data
        :type full_graph: dict
        :return: variable tree definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating system level categorized variable tree...')

        variable_tree_categorized_system_level = []
        for key in full_graph:
            if key is not 'attributes' and key is not coordinator_str:
                if self.nodes[key]['category'] == 'variable':
                    in_degree = self.in_degree(key)
                    out_degree = self.out_degree(key)
                    if in_degree == 0 and out_degree > 0:
                        key = '/systemVariables/inputs' + key
                    elif in_degree > 0 and out_degree > 0:
                        key = '/systemVariables/couplings' + key
                    elif in_degree > 0 and out_degree == 0:
                        key = '/systemVariables/outputs' + key
                    else:
                        key = '/systemVariables/holes' + key
                    xpath = key
                    var_dict = dict(xPath=xpath, type='variable')
                    variable_tree_categorized_system_level.append(var_dict)
        logger.debug('Successfully created system level categorized variable tree.')
        return variable_tree_categorized_system_level

    def _get_variable_tree_categorized_node_level(self, full_graph):
        """ Function for system level sorting of the variables (inputs, outputs, couplings, holes)

        :param full_graph: dictionary with graph data
        :type full_graph: dict
        :return: variable tree definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating node level categorized variable tree...')
        variable_tree_categorized_node_level = []
        for key in full_graph:
            if key is not 'attributes' and key is not coordinator_str:
                if self.nodes[key]['category'] == 'variable':
                    subcategory = self.nodes[key]['subcategory']
                    key = '/variables/' + make_camel_case(subcategory) + key
                    xpath = key
                    var_dict = dict(xPath=xpath, type='variable')
                    variable_tree_categorized_node_level.append(var_dict)
        logger.debug('Successfully created node level categorized variable tree.')
        return variable_tree_categorized_node_level

    def _get_variable_tree_categorized_role_level(self, full_graph):
        """ Function for system level sorting of the variables (inputs, outputs, couplings, holes)

        :param full_graph: dictionary with graph data
        :type full_graph: dict
        :return: variable tree definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating role level categorized variable tree...')
        variable_tree_categorized_role_level = []
        # Create empty start tree
        key = '/variables/architectureRoles'
        xpath = key
        var_dict = dict(xPath=xpath, type='variable')
        variable_tree_categorized_role_level.append(var_dict)
        key = '/variables/problemRoles'
        xpath = key
        var_dict = dict(xPath=xpath, type='variable')
        variable_tree_categorized_role_level.append(var_dict)
        for key in full_graph:
            if key is not 'attributes' and key is not coordinator_str:
                if self.nodes[key]['category'] == 'variable':
                    if 'problem_role' in self.nodes[key]:
                        prob_role = self.nodes[key]['problem_role']
                        new_key = '/variables/problemRoles/' + make_camel_case(prob_role) + 's' + key
                        xpath = new_key
                        var_dict = dict(xPath=xpath, type='variable')
                        variable_tree_categorized_role_level.append(var_dict)
                    if 'architecture_role' in self.nodes[key]:
                        arch_role = self.nodes[key]['architecture_role']
                        new_key = '/variables/architectureRoles/' + make_camel_case(arch_role) + 's' + key
                        xpath = new_key
                        var_dict = dict(xPath=xpath, type='variable')
                        variable_tree_categorized_role_level.append(var_dict)
        logger.debug('Successfully created role level categorized variable tree.')
        return variable_tree_categorized_role_level

    def _get_variable_tree_categorized_function_level(self, function_data_list):
        """ Function for function level sorting of variables (inputs / outputs per function)

        :param function_data_list: list with function-based inputs and outputs
        :type function_data_list: list
        :return: variable tree definition
        :rtype: dict
        """

        logger.debug('Creating function level categorized variable tree...')
        variable_tree_categorized_function_level = []
        for item in function_data_list:
            name = item['name']
            inputs = item['input']
            outputs = item['output']
            for inp in inputs:
                key = '/functions/' + name + '/inputs' + inp
                xpath = key
                var_dict = dict(xPath=xpath, type='variable')
                variable_tree_categorized_function_level.append(var_dict)
            for output in outputs:
                key = '/functions/' + name + '/outputs' + output
                xpath = key
                var_dict = dict(xPath=xpath, type='variable')
                variable_tree_categorized_function_level.append(var_dict)
        logger.debug('Successfully created function level categorized variable tree...')
        return variable_tree_categorized_function_level


def vistoms_start(graphs, file_dir=None, open_vistoms=True):
    """Function to open an interactive VISTOMS based on a list of data and (optionally) process graphs. If file_dir is
     not provided then the files are stored in a temp directory.

    :param graphs: list or tuple with graphs. For pure data graphs, provide the graph object directly in the list. For
    data+process graphs, provide them as a list or tuple pair with first the data graph and then process graph.
    :type graphs: list or tuple
    :param file_dir: folder name or path where the graphs used in the interactive VISTOMS will be stored.
    :type file_dir: path
    :param mpg: MDAO process graph to be used in combination with the data graph.
    :type mpg: MdaoProcessGraph
    :return: interactive VISTOMS
    :rtype: file
    """

    # Logging
    logger.info('Creating the VISTOMS instance...')

    # Assert input
    if not isinstance(graphs, (list, tuple)):
        raise AssertionError('Input should be of type list or tuple, now: {}.'.format(type(graphs)))

    # If destination folder is given, create + use that
    if file_dir is not None:
        if os.path.isdir(file_dir):
            shutil.rmtree(file_dir)
        os.mkdir(file_dir)
        vistoms_dir = os.path.abspath(file_dir)
    # Else create temporary directory
    else:
        temp_dir = tempfile.mkdtemp()
        vistoms_dir = os.path.abspath(temp_dir)

    # Save the graphs in the folder
    for i, graph in enumerate(graphs):
        i_str = format(i+1, '02d')
        if isinstance(graph, (list, tuple)):
            graph[0].save('tmp_{}.kdms'.format(i_str), destination_folder=vistoms_dir, mpg=graph[1])
        else:
            graph.save('tmp_{}.kdms'.format(i_str), destination_folder=vistoms_dir)

    # Then run interactive VISTOMS
    from kadmos.vistoms.vistoms import run_vistoms
    run_vistoms(folder=vistoms_dir, open_vistoms=open_vistoms)


def vistoms_remove(graph_id, vistoms_dir, compress=False, remove_after_compress=True):
    """ Function to remove a graph from a VISTOMS instance.

    :param graph_id: ID of the graph to be removed
    :type graph_id: str
    :param vistoms_dir: folder of the existing VISTOMS instance
    :type vistoms_dir: str
    :param compress: setting whether to compress the final VISTOMS instance folder to a zip file
    :type compress: bool
    :param remove_after_compress: setting whether to remove the original folder after compression
    :type remove_after_compress: bool
    :return: updated VISTOMS instance
    :rtype: file
    """
    # Logging
    logger.info('Removing graph from the VISTOMS instance...')

    # Create vistoms file name path
    vistoms_file = os.path.join(vistoms_dir, VISTOMS_NAME)

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    # Copy VISTOMS_NAME file to the temp directory
    temp_file = os.path.join(temp_dir, VISTOMS_NAME)
    shutil.copy(vistoms_file, temp_file)

    # Get the graph data and line number
    data, data_linenumber = _get_the_data(temp_file)

    # Find IDs in the current graph data.json
    graph_ids = [graph['id'] for graph in data['graphs']]
    if graph_id not in graph_ids:
        raise AssertionError('Could not find graph_id: {}. Available IDs: {}.'
                             .format(graph_id, graph_ids))
    removal_index = graph_ids.index(graph_id)

    # Remove graph from the data dictionary
    data['graphs'].pop(removal_index)

    # Replace the graph data
    data_str = json.dumps(data, default=lambda o: '<not serializable>')
    _replace_line(temp_file, data_linenumber, THEDATA_PREFIX + data_str)

    # Copy VISTOMS_NAME to original folder
    # Remove previous VISTOMS_NAME
    try:
        os.remove(vistoms_file)
    except OSError:
        pass
    # Place new VISTOMS_NAME file
    os.rename(temp_file, vistoms_file)
    # Remove temporary directory
    shutil.rmtree(temp_dir)

    if compress:
        _compress_vistoms_instance(vistoms_dir, remove_after_compress)

    # Logging
    logger.info('Successfully removed graph from the VISTOMS instance.')

    return


def vistoms_get_graph_ids(vistoms_dir):
    """ Function to get a list with current graph IDs in a VISTOMS file.

    :param vistoms_dir: path to the VISTOMS folder
    :type vistoms_dir: str
    :return: list with graph IDs
    :rtype: list
    """

    # Create vistoms file name path
    vistoms_file = os.path.join(vistoms_dir, VISTOMS_NAME)

    # Get the graph data and line number
    data, data_linenumber = _get_the_data(vistoms_file)

    # Find IDs in the current graph data
    graph_ids = [graph['id'] for graph in data['graphs']]

    return graph_ids


def vistoms_get_graph_info(vistoms_dir):
    """ Function to retrieve the graph information from a VISTOMS file.

    :param vistoms_dir: path to the VISTOMS folder
    :type vistoms_dir: str
    :return: dictionary with graph info
    :rtype: dict
    """

    # Create vistoms file name path
    vistoms_file = os.path.join(vistoms_dir, VISTOMS_NAME)

    # Get the graph data and line number
    data, data_linenumber = _get_the_data(vistoms_file)

    # Find info in the current graph data
    graph_ids = [graph['id'] for graph in data['graphs']]
    graph_names = [graph['name'] for graph in data['graphs']]
    graph_descriptions = [graph['description'] for graph in data['graphs']]

    # Build dictionary
    graph_dict = dict()
    for graph_id, graph_name, graph_description in zip(graph_ids, graph_names, graph_descriptions):
        graph_dict[graph_id] = dict(name=graph_name, description=graph_description)

    return graph_dict


def get_vistoms_tree_viewer(xml_file, vistoms_dir, use_png_figs=False, file_refs=None,
                            compress=False, remove_after_compress=False):

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    # Get absolute path of vistoms_dir
    vistoms_dir = os.path.abspath(vistoms_dir)

    # Initiate VISTOMS instance
    vistoms.copy(temp_dir, vistoms_version="TreeViewer")

    # Settings
    dummy_tool_name = '__dummy__'
    dummy_cmdows_name = '__dummy__CMDOWS.xml'
    dummy_input_file_name = dummy_tool_name + '-input.xml'

    # File names
    dummy_cmdows_file = os.path.join(temp_dir, dummy_cmdows_name)
    dummy_input_file = os.path.join(temp_dir, dummy_input_file_name)

    # create dummy CMDOWS (done to get full_graph data)
    cmdows = CMDOWS()
    cmdows.add_header(creator='VISTOMS', description='CMDOWS for VISTOMS TreeViewer creation')
    cmdows.add_dc(dummy_tool_name, dummy_tool_name, 'main', 1, '1.0', dummy_tool_name)

    cmdows.save(dummy_cmdows_file, pretty_print=True)

    # rename merged_basefile as input file
    shutil.copyfile(xml_file, dummy_input_file)

    # read file as an RCG with load function
    from kadmos.graph import load
    graph = load(dummy_cmdows_file, 'cmdows', file_check_critical=False, ignore_modes=True)

    full_graph = graph._get_full_graph()

    variable_tree_dataschema = graph._get_variable_tree_dataschema(full_graph,
                                                                   reference_file=dummy_input_file)

    the_data = {"modelName": "Tree view of latest baseline file.",
                "schema": variable_tree_dataschema}
    data_str = json.dumps(the_data, default=lambda o: '<not serializable>')

    # Define string replacements based on file referencing
    if file_refs is None:
        rep = dict(LOCAL_FILE_REFS)
        if use_png_figs:
            for key, item in iteritems(rep):
                if '.svg' in item:
                    rep[key] = item.replace('.svg', '.png')
        rep['REP__GRAPH_DATA__REP'] = data_str
    else:
        rep = file_refs
        for key, item in iteritems(LOCAL_FILE_REFS):
            if not key in rep and 'glyphicons' not in key:
                raise AssertionError('Replacement key {} is missing in the file_refs.'.format(key))
        rep['REP__GRAPH_DATA__REP'] = data_str

    # Perform the text replacement
    rep = dict((re.escape(k), v) for k, v in iteritems(rep))
    pattern = re.compile("|".join(list(rep)))
    with open(os.path.join(temp_dir, VISTOMS_TV_NAME_TEMP), "rt") as fin:
        with open(os.path.join(temp_dir, VISTOMS_TV_NAME), "wt") as fout:
            for line in fin:
                fout.write(pattern.sub(lambda m: rep[re.escape(m.group(0))], line))

    # Remove the original VISTOMS file
    os.remove(os.path.join(temp_dir, VISTOMS_TV_NAME_TEMP))

    # Remove the dummy files
    os.remove(dummy_cmdows_file)
    os.remove(dummy_input_file)

    # Copy temp directory to file path
    # Remove previous VISTOMS directory (if present)
    try:
        shutil.rmtree(vistoms_dir)
    except OSError:
        pass
    # Place new VISTOMS folder
    shutil.copytree(temp_dir, vistoms_dir)
    # Remove temporary directory
    shutil.rmtree(temp_dir)

    if compress:
        _compress_vistoms_instance(vistoms_dir, remove_after_compress)


def _write_json_file(vistoms_dir, data_json):
    """ Function to write the data.json file and first remove the previous one.

    :param vistoms_dir: location of VISTOMS instance
    :type vistoms_dir: str
    :param data_json: dictionary with all graph data
    :type data_json: dict
    :return: data.json file
    :rtype: file
    """

    # Write data.json file
    dst = os.path.join(vistoms_dir, 'supportFiles', 'data.json')
    try:
        os.remove(dst)
    except OSError:
        pass
    with open(dst, 'w') as f:
        json.dump(data_json, f)


def _compress_vistoms_instance(vistoms_dir, remove_original):
    """ Function to compress the VISTOMS instance with option to remove original folder.

    :param vistoms_dir: location of VISTOMS instance
    :type vistoms_dir: str
    :param remove_original: option to
    :type remove_original:
    :return: compressed VISTOMS instance
    :rtype: file
    """

    shutil.make_archive(vistoms_dir, 'zip', vistoms_dir)
    if remove_original:
        shutil.rmtree(vistoms_dir)


def _replace_line(file_name, line_num, text):
    lines = open(file_name, 'r', **ENCODING).readlines()
    lines[line_num-1] = text + '\n'
    out = open(file_name, 'w', **ENCODING)
    out.writelines(lines)
    out.close()


def _get_the_data(vistoms_file):
    """
    Function to read the graph data dictionary from a VISTOMS html file.

    :param vistoms_file: the existing VISTOMS html file
    :type vistoms_file: str
    :return: dictionary with the graph data
    :rtype: dict
    """

    # Find the line number of the Data
    thedata_linenumber = None
    with open(vistoms_file, **ENCODING) as myFile:
        for num, line in enumerate(myFile, 1):
            if THEDATA_PREFIX in line:
                thedata_linenumber = num
    if thedata_linenumber is None:
        raise AssertionError('Could not find THEDATA_PREFIX string in the html file.')

    # Read data from the VISTOMS_NAME file
    data_line = linecache.getline(vistoms_file, thedata_linenumber)
    data_str = data_line.replace(THEDATA_PREFIX, '')
    data = json.loads(data_str)
    return data, thedata_linenumber


def retrieve_session_folder(sessions_catalog_folder, session_id, add_usage_stamp=False):
    """Function to retrieve the session folder path from a session specification file in the catalog.

    :param sessions_catalog_folder: Folder with session specification files
    :type sessions_catalog_folder: str
    :param session_id: identifier of the session
    :type session_id: str
    :param add_usage_stamp: setting on whether a refresh stamp should be added
    :type add_usage_stamp: bool
    :return: folder path with the session files
    :rtype: str
    """

    # Check if the sessions catalog folder exists
    if not os.path.exists(sessions_catalog_folder):
        raise IOError('Sessions catalog folder {} does not exist.'.format(sessions_catalog_folder))

    # If the folder exists, then check if the session_id file exists
    session_file_name = session_id + '.json'
    session_file_path = os.path.join(sessions_catalog_folder, session_file_name)
    if not os.path.isfile(session_file_path):  # Create new session file if it does not exist
        raise AssertionError('Could not find session file {} in sessions catalog folder {}.'
                             .format(session_file_name, sessions_catalog_folder))

    # If folder and file exist, then read the file
    try:
        with open(session_file_path) as f:
            session_details = json.load(f)
    except Exception as e:
        raise SystemError('Could not read the session file {} because of {}.'.format(session_file_name, e))

    # Check if folder if provided in session data
    if 'folder' not in session_details:
        raise AssertionError('Could not read folder from session file {}.'.format(session_file_name))
    else:
        session_folder = session_details['folder']

    # Optionally add usage stamp to session catalog file
    if add_usage_stamp:
        session_details['last_refresh'] = str(datetime.now())
        with open(session_file_path, 'w') as outfile:
            json.dump(session_details, outfile)

    # Make sure the session folder exists or else create it
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)

    return session_folder
