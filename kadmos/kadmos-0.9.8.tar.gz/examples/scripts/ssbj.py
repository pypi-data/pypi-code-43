import copy
import logging
import os
import numpy as np

from examples.knowledgebases.ssbj.deploy import deploy_repo
from kadmos.graph import load, FundamentalProblemGraph
from kadmos.utilities.general import get_sublist, pdflatex_command_found
from ssbjkadmos.tools import scale_values, ssbj_scalers, ssbj_nonscalers

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# List of MDAO definitions that can be wrapped around the problem
mdao_definitions = ['unconverged-MDA-GS',     # 0
                    'unconverged-MDA-J',      # 1
                    'converged-MDA-GS',       # 2
                    'converged-MDA-J',        # 3
                    'unconverged-DOE-GS-CT',  # 4
                    'unconverged-DOE-J-CT',   # 5
                    'converged-DOE-GS-CT',    # 6
                    'converged-DOE-J-CT',     # 7
                    'converged-DOE-GS-LH',    # 8
                    'converged-DOE-GS-MC',    # 9
                    'MDF-GS',                 # 10
                    'MDF-J',                  # 11
                    'IDF',                    # 12
                    'CO',                     # 13
                    'BLISS-2000']             # 14

scaled = scale_values


def get_loop_items(analyze_mdao_definitions):
    """List of MDAO architecture definitions to be looped.

    :param analyze_mdao_definitions: setting with architectures to be looped
    :type analyze_mdao_definitions: Union[int, list, str]
    :return: list with MDAO architecture definitions
    :rtype: list
    """
    if isinstance(analyze_mdao_definitions, int):
        mdao_defs_loop = [mdao_definitions[analyze_mdao_definitions]]
    elif isinstance(analyze_mdao_definitions, list):
        mdao_defs_loop = [mdao_definitions[i] for i in analyze_mdao_definitions]
    elif isinstance(analyze_mdao_definitions, str):
        if analyze_mdao_definitions == 'all':
            mdao_defs_loop = mdao_definitions
        else:
            raise ValueError(
                'String value {} is not allowed for analyze_mdao_definitions.'.format(analyze_mdao_definitions))
    else:
        raise IOError('Invalid input {} provided of type {}.'.format(analyze_mdao_definitions, type(analyze_mdao_definitions)))
    return mdao_defs_loop


def add_mathematical_functions(rcg):
    """Add the mathematical functions to the repository connectivity graph.

    :param rcg: original repository connectivity graph
    :type rcg: RepositoryConnectivityGraph
    :return: enriched repository connectivity graph
    :rtype: RepositoryConnectivityGraph
    """
    # Add the objective function
    R = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/R')]
    R_label = R[0].split('/')[-1]
    f_R = '/dataSchema/scaledData/R/value'
    if scaled:
        rcg.add_mathematical_function([[R[0], R_label]],
                                      'F[R]',
                                      [[f_R, '-{}'.format(R_label), 'Python']])
    else:
        R_scaler = '/dataSchema/scaledData/R/scaler'
        R_scaler_label = 'R_scaler'
        rcg.add_mathematical_function([[R[0], R_label], [R_scaler, R_scaler_label]],
                                      'F[R]',
                                      [[f_R, '-{}/{}'.format(R_label, R_scaler_label), 'Python']])

    # Add the constraint functions
    # Collect constraint inputs
    sigmas = [node for node in rcg.find_all_nodes(category='variable') if 'sigma' in node]
    sigmas.sort()
    theta = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/Theta')]
    dpdx = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/dpdx')]
    ESF = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/ESF')]
    DT = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/DT')]
    Temp = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/Temp')]

    # Define inputs nodes and labels
    con_inputs = sigmas + theta + dpdx + ESF + DT + Temp
    input_labels = [con_input.split('/')[-1] for con_input in con_inputs]

    # Define output nodes and labels
    con_values = ['/dataSchema/scaledData/{}/value'.format(name) for name in input_labels]

    # Define mapping of the constraint functions
    function_map = {'sigmas': [0, 1, 2, 3, 4], 'Theta': [5], 'dpdx': [6], 'prop': [7, 8, 9]}

    # Add constraint functions to graph
    if scaled:
        scalers = ssbj_scalers
        con_functions = {'sigmas': ['*{}-1.09'.format(scalers['sigma1']),
                                    '*{}-1.09'.format(scalers['sigma2']),
                                    '*{}-1.09'.format(scalers['sigma3']),
                                    '*{}-1.09'.format(scalers['sigma4']),
                                    '*{}-1.09'.format(scalers['sigma5'])],
                         'Theta': ['*{}-1.04'.format(scalers['Theta'])],
                         'dpdx': ['*{}-1.04'.format(scalers['dpdx'])],
                         'prop': ['*{}-1.5'.format(scalers['ESF']),
                                  '*{}'.format(scalers['DT']),
                                  '*{}-1.02'.format(scalers['Temp'])]}
    else:
        con_functions = {'sigmas': ['-1.09']*5,
                         'Theta': ['-1.04'],
                         'dpdx': ['-1.04'],
                         'prop': ['-1.5', '', '-1.02']}

    # Add constraint functions to graph
    for f, f_idxs in function_map.items():
        f_con_inputs = get_sublist(con_inputs, f_idxs)
        f_input_labels = get_sublist(input_labels, f_idxs)
        f_con_values = get_sublist(con_values, f_idxs)
        rcg.add_mathematical_function(
            [[item[0], item[1]] for item in zip(f_con_inputs, f_input_labels)],
            'C[{}]'.format(f),
            [[item[0], '{}{}'.format(item[1], item[2]), 'Python']
             for item in zip(f_con_values, f_input_labels, con_functions[f])])

    # Add consistency constraint for lift and total weight
    if scaled:
        rcg.add_mathematical_function(
            [('/dataSchema/aircraft/other/L', 'L'), ('/dataSchema/aircraft/weight/WT', 'WT')],
            'C[LWTbalance]',
            [['/dataSchema/scaledData/LWT/value', 'L-WT', 'Python']],
            function_type='balance')
    else:
        rcg.add_mathematical_function([('/dataSchema/aircraft/other/L', 'L'),
                                       ('/dataSchema/aircraft/weight/WT', 'WT'),
                                       ('/dataSchema/scaledData/LWT/scaler', 'scaler')],
                                      'C[LWTbalance]',
                                      [['/dataSchema/scaledData/LWT/value',
                                        '(L-WT)/scaler', 'Python']],
                                      function_type='balance')
    return rcg


def run_kadmos(analyze_mdao_definitions, folder_str='ssbj', start_point='start', b2k_seed=5):
    """Run KADMOS for the list of MDAO architecture definitions.

    :param analyze_mdao_definitions: architecture definitions to be analyzed
    :type analyze_mdao_definitions: Union[list, int]
    :param folder_str: identifier for storage folder
    :type folder_str: str
    :return: nothing
    :rtype: None
    """
    # Deploy repository
    deploy_repo()

    # Get the MDA cases
    if isinstance(analyze_mdao_definitions, int):
        if analyze_mdao_definitions < 10:
            mda_cases = [analyze_mdao_definitions]
        else:
            mda_cases = []
    elif isinstance(analyze_mdao_definitions, list):
        mda_cases = [idx for idx in analyze_mdao_definitions if idx <10]
    elif isinstance(analyze_mdao_definitions, str):
        if analyze_mdao_definitions == 'all':
            mda_cases = list(range(10))
        else:
            raise IOError('String input can only be "all".')
    else:
        raise AssertionError('Value type {} not supported.'.format(type(analyze_mdao_definitions)))

    # Run the MDA cases
    if mda_cases:
        run_kadmos_mda(mda_cases, folder_str=folder_str)

    # Get the MDO cases
    if isinstance(analyze_mdao_definitions, int):
        if analyze_mdao_definitions >= 10:
            mdo_cases = [analyze_mdao_definitions]
        else:
            mdo_cases = []
    elif isinstance(analyze_mdao_definitions, list):
        mdo_cases = [idx for idx in analyze_mdao_definitions if idx >= 10]
    elif isinstance(analyze_mdao_definitions, str):
        if analyze_mdao_definitions == 'all':
            mdo_cases = list(range(10, 15))
        else:
            raise IOError('String input can only be "all".')
    else:
        raise AssertionError('Value type {} not supported.'.format(type(analyze_mdao_definitions)))

    # Run the MDO cases
    if mdo_cases:
        run_kadmos_mdo(mdo_cases, folder_str=folder_str, start_point=start_point, b2k_seed=b2k_seed)


def run_kadmos_mda(analyze_mdao_definitions, folder_str='ssbj'):
    """Run KADMOS for the MDA-based architecture definitions (MDA and DOE).

    :param analyze_mdao_definitions: MDAO architecture definitions to be analyzed
    :type analyze_mdao_definitions: list
    :param folder_str: key string for storage folders
    :type folder_str: str
    :return: files
    :rtype: None
    """

    global mdao_definitions

    # Check and analyze inputs
    mdao_defs_loop = get_loop_items(analyze_mdao_definitions)

    if scaled:
        scalers = ssbj_scalers
    else:
        scalers = ssbj_nonscalers

    compile_pdf = pdflatex_command_found()
    if not compile_pdf:
        logging.warning('Could not find command pdflatex, hence no PDFs will be compiled in the '
                        'create_dsm method.')

    # Settings for saving output files
    dsm_settings = dict(destination_folder=os.path.join(folder_str, '(X)DSM'),
                        keep_tex_file=not compile_pdf,
                        compile_pdf=compile_pdf)
    cmdows_settings = dict(file_type='cmdows',
                           destination_folder=os.path.join(folder_str, 'CMDOWS'),
                           creator='Imco van Gent',
                           version='0.1',
                           pretty_print=True,
                           integrity=False)
    kdms_settings = dict(destination_folder=os.path.join(folder_str, 'KDMS'))

    logging.info('Loading repository connectivity graph...')

    repo_dir = repo_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            '../knowledgebases', 'ssbj')
    rcg = load(os.path.join(repo_dir, '__cmdows__SSBJ.xml'),
               check_list=['consistent_root', 'invalid_leaf_elements'])
    rcg.graph['name'] = 'RCG - Tool database'
    rcg.graph['description'] = 'Repository connectivity graph of the super-sonic business jet case.'

    rcg = add_mathematical_functions(rcg)
    rcg.remove_function_nodes('C[LWTbalance]', 'DpdxAnalysis')

    # Add default values of the variables based on a reference file
    rcg.add_variable_default_values(os.path.join(repo_dir, 'SSBJ-base.xml'))

    # Define the function order
    function_order = ['StructuralAnalysis', 'AeroAnalysis', 'PropulsionAnalysis', 'PerformanceAnalysis',
                      'C[sigmas]', 'C[Theta]', 'C[dpdx]', 'C[prop]', 'F[R]']

    # Create a CMDOWS, DSM and a VISTOMS visualization of the RCG
    rcg.create_dsm(file_name='RCG', function_order=function_order, **dsm_settings)
    rcg.save('RCG', description='RCG CMDOWS file of the super-sonic business jet test case',
             **cmdows_settings)
    rcg.save('RCG', **kdms_settings)

    # Reset FPG
    logging.info('Scripting initial FPG...')
    mdao_definition_fpg = mdao_definitions[0]
    architecture_type = 'MDA'
    fpg = FundamentalProblemGraph(rcg)
    fpg.graph['name'] = 'FPG - {}'.format(architecture_type)
    fpg.graph['description'] = 'Fundamental problem graph to solve the SSBJ test case problem ' \
                               'for the architecture type: {}'.format(architecture_type)

    # Define settings of the problem formulation
    fpg.add_problem_formulation(mdao_definition_fpg, function_order)

    # Assign quantities of interest
    def mark_as_qois(g, endswith):
        g.mark_as_qois([nd for nd in g.find_all_nodes(category='variable')
                        if nd.endswith(endswith)])
    mark_as_qois(fpg, 'scaledData/R/value')
    mark_as_qois(fpg, 'scaledData/Theta/value')
    mark_as_qois(fpg, 'scaledData/dpdx/value')
    mark_as_qois(fpg, 'scaledData/ESF/value')
    mark_as_qois(fpg, 'scaledData/DT/value')
    mark_as_qois(fpg, 'scaledData/Temp/value')
    fpg.mark_as_qois([nd for nd in fpg.find_all_nodes(category='variable')
                      if 'scaledData/sigma' in nd and '/value' in nd])

    # Add WE as QOI for testing with RCE
    fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if
                      '/aircraft/weight/WE' in nd])

    # Search for problem roles
    fpg.add_function_problem_roles()

    for mdao_definition in mdao_defs_loop:
        logging.info('Scripting {}...'.format(mdao_definition))

        # If DOE, assign design variables
        scale_entry = lambda xpath, x, y, z: (xpath,
                                              x / scalers[xpath.split('/')[-1]],
                                              y / scalers[xpath.split('/')[-1]],
                                              z / scalers[xpath.split('/')[-1]])
        if 'DOE' in mdao_definition:
            des_vars = [scale_entry('/dataSchema/aircraft/geometry/tc', 0.01, 0.05, 0.09),
                        scale_entry('/dataSchema/reference/h', 30000., 45000., 60000.),
                        scale_entry('/dataSchema/reference/M', 1.4, 1.6, 1.8),
                        scale_entry('/dataSchema/aircraft/geometry/AR', 2.5, 5.5, 8.5),
                        scale_entry('/dataSchema/aircraft/geometry/Lambda', 40, 55, 70),
                        scale_entry('/dataSchema/aircraft/geometry/Sref', 500, 1000, 1500),
                        scale_entry('/dataSchema/aircraft/geometry/lambda', 0.1, 0.25, 0.4),
                        scale_entry('/dataSchema/aircraft/geometry/section', 0.75, 1.00, 1.25),
                        scale_entry('/dataSchema/aircraft/other/Cf', 0.75, 1.00, 1.25),
                        scale_entry('/dataSchema/aircraft/other/T', 0.1, 0.55, 1.00)]
            n_samples = 10
            fpg.mark_as_design_variables([ds_vr[0] for ds_vr in des_vars],
                                         lower_bounds=[ds_vr[1] for ds_vr in des_vars],
                                         nominal_values=[ds_vr[2] for ds_vr in des_vars],
                                         upper_bounds=[ds_vr[3] for ds_vr in des_vars],
                                         samples=[list(np.linspace(ds_vr[1], ds_vr[3], n_samples))
                                                  for ds_vr in des_vars] if '-CT' in mdao_definition
                                                  else None)

        # Change the problem formulation of the FPG based on the MDAO definition
        if 'DOE' in mdao_definition:
            doe_settings = dict()
            if mdao_definition.endswith('-CT'):
                doe_settings['method'] = 'Custom design table'
            elif mdao_definition.endswith('-FF'):
                doe_settings['method'] = 'Full factorial design'
                doe_settings['levels'] = 2
            elif mdao_definition.endswith('-LH'):
                doe_settings['method'] = 'Latin hypercube design'
                doe_settings['seed'] = 5
                doe_settings['runs'] = 10
            elif mdao_definition.endswith('-MC'):
                doe_settings['method'] = 'Monte Carlo design'
                doe_settings['seed'] = 9
                doe_settings['runs'] = 10
            elif mdao_definition.endswith('-BB'):
                doe_settings['method'] = 'Box-Behnken design'
                doe_settings['center_runs'] = 2
            else:
                raise AssertionError('Could not determine the doe_method.')
        else:
            doe_settings = None

        fpg.add_problem_formulation(mdao_definition, function_order,
                                    doe_settings=doe_settings)

        # Create an XDSM visualization of the strategy
        fpg.create_dsm(file_name='FPG_MDA', **dsm_settings)

        # Save output files
        fpg.save('FPG_MDA', description='FPG CMDOWS file of the SSBJ test case', **cmdows_settings)
        fpg.save('FPG_MDA', **kdms_settings)

        # Get Mdao graphs
        mdg, mpg = fpg.impose_mdao_architecture()
        mdg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
        mdg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test ' \
                                   'case optimization problem using the strategy: ' \
                                   '{}.'.format(mdao_definition)
        mpg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
        mpg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test ' \
                                   'case optimization problem using the strategy: ' \
                                   '{}.'.format(mdao_definition)

        # Create an XDSM visualization of the strategy
        mdg.create_dsm(file_name='Mdao_{}'.format(mdao_definition), mpg=mpg, **dsm_settings)

        # Save the solution strategy as CMDOWS and KDMS files
        mdg.save('Mdao_{}'.format(mdao_definition), mpg=mpg,
                 description='CMDOWS file of the SSBJ test case solution strategy',
                 **cmdows_settings)
        mdg.save('Mdao_{}'.format(mdao_definition), mpg=mpg, **kdms_settings)
        logging.info('Done!')


def run_kadmos_mdo(analyze_mdao_definitions, folder_str='ssbj', start_point='start', b2k_seed=5):
    """Run KADMOS for the MDO-based architecture definitions.

    :param analyze_mdao_definitions: MDAO architecture definitions to be analyzed
    :type analyze_mdao_definitions: list
    :param folder_str: key string for storage folders
    :type folder_str: str
    :return: files
    :rtype: None
    """

    global mdao_definitions

    # Check and analyze inputs
    mdao_defs_loop = get_loop_items(analyze_mdao_definitions)

    if scaled:
        scalers = ssbj_scalers
    else:
        scalers = ssbj_nonscalers

    compile_pdf = pdflatex_command_found()
    if not compile_pdf:
        logging.warning('Could not find command pdflatex, hence no PDFs will be compiled in the '
                        'create_dsm method.')

    # Settings for saving output files
    dsm_settings = dict(destination_folder=os.path.join(folder_str, '(X)DSM'),
                        keep_tex_file=not compile_pdf,
                        compile_pdf=compile_pdf)
    cmdows_settings = dict(file_type='cmdows',
                           destination_folder=os.path.join(folder_str, 'CMDOWS'),
                           creator='Imco van Gent',
                           version='0.1',
                           pretty_print=True,
                           integrity=False)
    kdms_settings = dict(destination_folder=os.path.join(folder_str, 'KDMS'))

    logging.info('Loading repository connectivity graph...')

    repo_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            '../knowledgebases', 'ssbj')
    rcg = load(os.path.join(repo_dir, '__cmdows__SSBJ.xml'),
               check_list=['consistent_root', 'invalid_leaf_elements'])

    logging.info('Scripting RCG...')

    # A name and a description are added to the graph
    rcg.graph['name'] = 'RCG'
    rcg.graph['description'] = 'Repository of the super-sonic business jet test case'

    rcg = add_mathematical_functions(rcg)

    # Define function order
    function_order = ['DpdxAnalysis', 'StructuralAnalysis', 'AeroAnalysis', 'PropulsionAnalysis',
                      'PerformanceAnalysis', 'C[sigmas]', 'C[Theta]', 'C[dpdx]', 'C[prop]',
                      'C[LWTbalance]', 'F[R]']

    # Create a DSM and a VISTOMS visualization of the RCG
    rcg.create_dsm('RCG', function_order=function_order, **dsm_settings)
    rcg.save('RCG', description='RCG CMDOWS file of the super-sonic business jet test case',
             **cmdows_settings)
    rcg.save('RCG', **kdms_settings)

    # Reset FPG
    logging.info('Scripting initial FPG...')
    mdao_definition_fpg = 'MDF-GS'
    architecture_type = 'MDO'
    fpg_ini = FundamentalProblemGraph(rcg)
    fpg_ini.graph['name'] = 'FPG - {}'.format(architecture_type)
    fpg_ini.graph['description'] = 'Fundamental problem graph to solve the SSBJ test case ' \
                               'problem for the architecture type: {}'.format(architecture_type)

    # Define settings of the problem formulation
    fpg_ini.add_problem_formulation(mdao_definition_fpg, function_order)

    # Assign design variables
    scale_entries = lambda xpath, x, y, z: (xpath,
                                           x / scalers[xpath.split('/')[-1]],
                                           y / scalers[xpath.split('/')[-1]],
                                           z / scalers[xpath.split('/')[-1]])
    if start_point == 'start':
        des_vars = [scale_entries('/dataSchema/aircraft/geometry/tc', 0.01, 0.05, 0.09),
                    scale_entries('/dataSchema/reference/h', 30000., 45000., 60000.),
                    scale_entries('/dataSchema/reference/M', 1.4, 1.6, 1.8),
                    scale_entries('/dataSchema/aircraft/geometry/AR', 2.475, 5.5, 7.975),
                    scale_entries('/dataSchema/aircraft/geometry/Lambda', 39.6, 55., 69.85),
                    scale_entries('/dataSchema/aircraft/geometry/Sref', 500., 1000., 1500.),
                    scale_entries('/dataSchema/aircraft/geometry/lambda', 0.1, 0.4, 0.4),
                    scale_entries('/dataSchema/aircraft/geometry/section', 0.75, 0.75, 1.25),
                    scale_entries('/dataSchema/aircraft/other/Cf', 0.75, 1.00, 1.25),
                    scale_entries('/dataSchema/aircraft/other/T', 0.09, 0.25, 0.905)]
    elif start_point == 'end':
        des_vars = [scale_entries('/dataSchema/aircraft/geometry/tc', 0.0582294675, 0.06, 0.0617705325),
                    scale_entries('/dataSchema/reference/h', 59736.9051, 59985.0, 59985.0),
                    scale_entries('/dataSchema/reference/M', 1.4, 1.4, 1.4125),
                    scale_entries('/dataSchema/aircraft/geometry/AR', 2.475, 2.475, 2.51796875),
                    scale_entries('/dataSchema/aircraft/geometry/Lambda', 69.1659386, 69.5862882, 69.7763825),
                    scale_entries('/dataSchema/aircraft/geometry/Sref', 1481.41709, 1492.72954, 1492.85441),
                    scale_entries('/dataSchema/aircraft/geometry/lambda', 0.1, 0.4, 0.4),
                    scale_entries('/dataSchema/aircraft/geometry/section', 0.75, 0.75, 1.25),
                    scale_entries('/dataSchema/aircraft/other/Cf', 0.75, 1.00, 1.25),
                    scale_entries('/dataSchema/aircraft/other/T', 0.09, 0.25, 0.905)]
    else:
        raise IOError('start_point {} does not exist'.format(start_point))

    fpg_ini.mark_as_design_variables([ds_vr[0] for ds_vr in des_vars],
                                 lower_bounds=[ds_vr[1] for ds_vr in des_vars],
                                 nominal_values=[ds_vr[2] for ds_vr in des_vars],
                                 upper_bounds=[ds_vr[3] for ds_vr in des_vars])

    # Assign objective
    fpg_ini.mark_as_objective([nd for nd in fpg_ini.find_all_nodes(category='variable') if
                               nd.endswith('/R/value')][0])

    # Assign constraints
    fpg_ini.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             ('/sigma' in nd and '/value' in nd)], '<=', 0.)
    fpg_ini.mark_as_constraint([nd for nd in rcg.find_all_nodes(category='variable') if
                            nd.endswith('/Theta/value')][0], ['>=', '<='], [-0.04, 0.])
    fpg_ini.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             nd.endswith('/dpdx/value')], '<=', 0.)  # 1.04)
    fpg_ini.mark_as_constraint([nd for nd in rcg.find_all_nodes(category='variable') if
                            nd.endswith('/ESF/value')][0], ['>=', '<='], [-1., 0.])
    fpg_ini.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             nd.endswith('/DT/value')], '<=', 0.0)
    fpg_ini.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             nd.endswith('/Temp/value')], '<=', 0.)
    fpg_ini.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             nd.endswith('/LWT/value')], '==', 0.)

    for mdao_definition in mdao_defs_loop:
        logging.info('Scripting {}...'.format(mdao_definition))
        fpg = fpg_ini.deepcopy()

        # Add valid ranges for couplings that will become design variables
        if mdao_definition in ['IDF', 'CO', 'BLISS-2000']:
            root = 'dataSchema'
            geom = '/'.join(['', root, 'aircraft', 'geometry'])
            weig = '/'.join(['', root, 'aircraft', 'weight'])
            other = '/'.join(['', root, 'aircraft', 'other'])
            ref = '/'.join(['', root, 'reference'])
            scale_entries = lambda xpath, x1, x2, x3, x4, x5: (xpath,
                                                              x1 / scalers[xpath.split('/')[-1]],
                                                              x2 / scalers[xpath.split('/')[-1]],
                                                              x3 / scalers[xpath.split('/')[-1]],
                                                              x4 / scalers[xpath.split('/')[-1]],
                                                              x5 / scalers[xpath.split('/')[-1]])
            scale_entries3 = lambda xpath, x1, x2, x3,: (xpath,
                                                        x1 / scalers[xpath.split('/')[-1]],
                                                        x2 / scalers[xpath.split('/')[-1]],
                                                        x3 / scalers[xpath.split('/')[-1]])
            if start_point == 'start':
                special_variables = [scale_entries('/'.join([other, 'D']), 1000., 15000., 0., float('inf'), 4877.52),  # TODO: Set to 2500 for CO
                                     scale_entries('/'.join([other, 'L']), 20000., 60000., 0., float('inf'), 50606.68),
                                     scale_entries3('/'.join([geom, 'Theta']), 0.96, 1.04, 1.0264),
                                     scale_entries('/'.join([weig, 'WE']), 0., 20000., 0., float('inf'), 9531.11),  # old run: ub=30000.
                                     scale_entries('/'.join([weig, 'WT']), 20000., 60000., 0., float('inf'), 50606.68),
                                     scale_entries3('/'.join([ref, 'ESF']), 0.5, 1.5, 0.75)]
            else:
                special_variables = [scale_entries('/'.join([other, 'D']), 5341.21226342, 5843.42085698, 0., float('inf'), 5625.24153468),
                                     scale_entries('/'.join([other, 'L']), 44100.2039883, 45929.0692252, 0., float('inf'), 45118.6472535),
                                     scale_entries3('/'.join([geom, 'Theta']), 1.03926133807, 1.03999999222, 1.03999999222),
                                     scale_entries('/'.join([weig, 'WE']), 9075.51289957, 9881.73848213, 0., float('inf'), 9561.45928761),# old run: ub=30000.
                                     scale_entries('/'.join([weig, 'WT']), 44100.2039883, 45929.0692252, 0., float('inf'), 45118.6472535),
                                     scale_entries3('/'.join([ref, 'ESF']), 0.707390446167, 0.764338670897, 0.741987433362)]
            if mdao_definition in ['CO']:
                special_variables.append(scale_entries3('/'.join([weig, 'WF']), 5000., 25000., 20000.))
                special_variables.append(scale_entries3('/'.join([other, 'fin']), 2., 12., 8.))  # old run: 20.
                special_variables.append(scale_entries3('/'.join([other, 'SFC']), .5, 1.5, 0.9))
            for sv in special_variables:
                vr_node = fpg.nodes[sv[0]]
                if len(sv) == 6:
                    vr_node['valid_ranges'] = {'limit_range_local': {'minimum': sv[1],
                                                                     'maximum': sv[2]}}
                    vr_node['valid_ranges'].update({'limit_range_global': {'minimum': sv[3],
                                                                           'maximum': sv[4]}})
                    fpg.nodes[sv[0]]['nominal_value'] = sv[5]
                else:
                    vr_node['valid_ranges'] = {'limit_range': {'minimum': sv[1], 'maximum': sv[2]}}
                    fpg.nodes[sv[0]]['nominal_value'] = sv[3]

        function_order2 = copy.deepcopy(function_order)
        if mdao_definition == 'BLISS-2000':
            fpg.remove_edge('AeroAnalysis', '/dataSchema/aircraft/other/dpdx')
        else:
            fpg.remove_function_nodes('DpdxAnalysis')
            function_order2.remove('DpdxAnalysis')
        if mdao_definition not in ['CO', 'BLISS-2000']:
            fpg.remove_function_nodes('C[LWTbalance]')
            function_order2.remove('C[LWTbalance]')

        # Update problem roles
        fpg.add_function_problem_roles()

        # Change the problem formulation of the FPG based on the MDAO definition
        if mdao_definition in ['CO', 'BLISS-2000']:
            fpg.graph['problem_formulation']['coupled_functions_groups'] = [['StructuralAnalysis'],
                                                                            ['AeroAnalysis'],
                                                                            ['PropulsionAnalysis']]
        fpg.add_problem_formulation(mdao_definition, function_order2,
                                    doe_settings=None if mdao_definition != 'BLISS-2000' else
                                    {'method': 'Latin hypercube design', 'seed': b2k_seed})

        # Create an XDSM visualization of the strategy
        fpg.create_dsm(file_name='FPG_MDO', **dsm_settings)

        # Save output files
        fpg.save('FPG_MDO', description='FPG CMDOWS file of the SSBJ test case', **cmdows_settings)
        fpg.save('FPG_MDO', **kdms_settings)

        # Get Mdao graphs
        mdg, mpg = fpg.impose_mdao_architecture()
        mdg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
        mdg.graph['description'] = 'Solution strategy to solve the SSBJ test case ' \
                                   'problem using the strategy: {}.'.format(mdao_definition)
        mpg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
        mpg.graph['description'] = 'Solution strategy to solve the SSBJ test case ' \
                                   'problem using the strategy: {}.'.format(mdao_definition)
        logging.info('Scripting {}...'.format(mdao_definition))

        # Create a DSM visualization of the Mdao
        mdg.create_dsm(file_name='Mdao_{}'.format(mdao_definition), mpg=mpg, **dsm_settings)

        # Save the Mdao as cmdows (and do an integrity check)
        mdg.save('Mdao_{}'.format(mdao_definition), mpg=mpg,
                 description='CMDOWS file of the SSBJ test case solution strategy',
                 **cmdows_settings)
        mdg.save('Mdao_{}'.format(mdao_definition), mpg=mpg, **kdms_settings)
    logging.info('Done!')


if __name__  == '__main__':
    # List of MDAO definitions that can be wrapped around the problem
    mdao_definitions = ['unconverged-MDA-GS',     # 0
                        'unconverged-MDA-J',      # 1
                        'converged-MDA-GS',       # 2
                        'converged-MDA-J',        # 3
                        'unconverged-DOE-GS-CT',  # 4
                        'unconverged-DOE-J-CT',   # 5
                        'converged-DOE-GS-CT',    # 6
                        'converged-DOE-J-CT',     # 7
                        'converged-DOE-GS-LH',    # 8
                        'converged-DOE-GS-MC',    # 9
                        'MDF-GS',                 # 10
                        'MDF-J',                  # 11
                        'IDF',                    # 12
                        'CO',                     # 13
                        'BLISS-2000']             # 14

    # Set options
    analyze_mdao_definitions = 'all'

    # Run KADMOS
    deploy_repo()
    run_kadmos(analyze_mdao_definitions)
